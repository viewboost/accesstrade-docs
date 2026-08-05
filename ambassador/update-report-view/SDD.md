# Tách view được tính thưởng và view vượt ngân sách — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tách số lượt xem thành phần được tính thưởng và phần bị loại do event vượt ngân sách, ở ba nơi: kỳ đối soát, menu thống kê admin, và trang cá nhân của ambassador.

**Architecture:** Thêm field mới song song với field cũ, không đổi ngữ nghĩa gì đang có. Tầng aggregate chỉ cung cấp hai bộ số; tầng API quyết định trừ hay không. Bốn khối logic thuần được tách thành module có test: builder nhánh aggregate, bộ tính số hiển thị, builder bản ghi đối soát, và builder thống kê theo nguồn.

**Tech Stack:** Go 1.x, MongoDB (mongo-go-driver), Echo. Frontend React + TypeScript + Ant Design ProTable, umi.

## Global Constraints

- Không đổi ngữ nghĩa và không xoá bất kỳ field nào đang tồn tại **trong database**. Field mới luôn thêm song song.
- Giá trị trả về ở response và ở file export **được phép** trừ đi phần vượt ngân sách — đó chính là bản sửa, không phải lỗi. Cụ thể áp dụng cho Task 4, Task 6, Task 7.
- Hai thay đổi hành vi **có chủ đích, nằm trong phạm vi**, không được coi là vượt phạm vi khi review:
  1. Task 3 — guard loại content có toàn bộ lượt xem trong kỳ đều vượt ngân sách ra khỏi kỳ đối soát.
  2. Task 8 — `View.Pending` của hai nguồn youtube và youtubeShort lấy từ số lượt xem thay vì số bình luận, khử lỗi chép nhầm có sẵn.
- Không chạm vào đường ghi phần thưởng. Cấm sửa `GetEventRewardStatisticAllByContentIDs`, `GetStatisticContentIsRewardInDay`, và mọi thứ trong `processRewardForSchema`.
- Mọi tổng tiền phải giữ nguyên giá trị sau thay đổi.
- Trước khi backfill, mọi màn hình phải hiển thị y hệt hiện tại. Không có trạng thái trung gian sai.
- Module thuần không được nhận `context.Context`, không gọi DAO, không đọc thời gian hệ thống.
- Test dùng khuôn của `backend/internal/service/budget_split_test.go`: hàm thuần, không DB, dùng sẵn `assertInt64` và `assertFloat64` nếu cùng package.
- Quy ước bucket của `event_reward.status` trong tên field Go lệch một nấc và **giữ nguyên**: slot `Pending` ứng với status `waiting_approved`, slot `Completed` ứng với status `pending`, slot `Cashback` ứng với status `completed`.
- Tất cả lệnh chạy từ thư mục `backend/` trừ khi ghi rõ khác.
- Commit sau mỗi task, không gộp.

---

## File Structure

**Tạo mới — backend**

| File | Trách nhiệm |
|---|---|
| `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder.go` | M1: sinh nhánh `$sum` có điều kiện cho `$group` |
| `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder_test.go` | Test M1 |
| `backend/internal/util/viewstat/viewstat.go` | M2: tính số lượt xem hiển thị từ tổng và phần vượt ngân sách |
| `backend/internal/util/viewstat/viewstat_test.go` | Test M2 |
| `backend/pkg/admin/service/reconciliation_content_item.go` | M3: dựng phần content của dòng đối soát, và quyết định bỏ qua |
| `backend/pkg/admin/service/reconciliation_content_item_test.go` | Test M3 |
| `backend/internal/service/analytic_view_statistic.go` | M4: ánh xạ báo cáo aggregate sang hai nhánh view của analytic |
| `backend/internal/service/user_event_source_statistic.go` | M5: dựng thống kê cho một nguồn |
| `backend/internal/service/user_event_source_statistic_test.go` | Test M5 |

**Sửa — backend**

| File | Việc |
|---|---|
| `internal/model/mg/event_analytic_daily.go` | thêm `ViewExceedBudget` |
| `internal/model/mg/user_event.go` | thêm `ViewExceedBudget` vào `UserContentStatistic` |
| `internal/model/mg/reconciliation_item.go` | thêm hai field int64 |
| `internal/module/database/mongodb/aggregate_pipeline/event_reward.go` | thêm nhánh cho ba pipeline |
| `internal/module/database/mongodb/aggregate_pipeline/event_analytic_daily.go` | thêm bốn nhánh đọc |
| `internal/service/event.go` | dùng M4 và M5 ở ba hàm cập nhật |
| `pkg/admin/service/reconciliation_processing.go` | dùng M3 |
| `pkg/admin/service/reconciliation.go` | map field mới ra response |
| `pkg/admin/service/event.go` | trừ ở converter thống kê |
| `pkg/admin/service/export_reconciliation.go` | thêm cột |
| `pkg/admin/service/export_event_analytic.go` | trừ và thêm cột |
| `pkg/admin/model/response/reconciliation.go` | thêm hai key |
| `pkg/admin/model/response/event.go` | thêm nhóm `viewExceedBudget` |
| `pkg/public/model/response/event.go` | expose `bpe` |
| `pkg/public/service/event.go` | gán `bpe` |

**Sửa — frontend**

| File | Việc |
|---|---|
| `admin/src/pages/reconciliation/detail/.../content/components/table.tsx` | đổi cột, thêm cột |
| `admin/src/pages/reconciliation/detail/.../content/components/info-modal.tsx` | thêm dòng |
| `admin/src/pages/reconciliation/detail/.../content/type.d.ts` | thêm hai key |
| `admin/src/pages/event-statistic/index.tsx` | thêm dòng thống kê |
| `admin/src/locales/vi-VN.ts` | nhãn mới |
| `<app>/src/pages/home/components/statistic/table.tsx` × 14 | thêm cột, sửa nhãn, sửa sorter |
| `<app>/src/interfaces/*` × 14 | thêm `viewExceedBudget` |
| `frontend/src/pages/home/components/budget-alert/index.tsx` | dọn chuỗi placeholder |

---

## Task 1: M1 — Builder nhánh aggregate

Ba pipeline sắp nhận thêm khoảng mười lăm nhánh `$cond`. File `event_reward.go` đã có bảy mươi hai nhánh chép tay và dài 1010 dòng. Builder này khử việc chép tay đó.

**Files:**
- Create: `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder.go`
- Test: `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder_test.go`

**Interfaces:**
- Consumes: không
- Produces:
  - `type BudgetFilter int` với ba hằng `BudgetAny`, `BudgetRewarded`, `BudgetExceeded`
  - `func SumWhere(field, status string, budget BudgetFilter) bson.M`
  - `func SumTransfer(field string, budget BudgetFilter) bson.M`

- [ ] **Step 1: Viết test thất bại**

Tạo `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder_test.go`:

```go
package aggregatepipeline

import (
	"reflect"
	"testing"

	"go.mongodb.org/mongo-driver/bson"
)

func TestSumWhere_NoFilter(t *testing.T) {
	got := SumWhere("$statistic.totalView", "", BudgetAny)
	want := bson.M{"$sum": "$statistic.totalView"}
	assertBson(t, "no filter", want, got)
}

func TestSumWhere_StatusOnly(t *testing.T) {
	got := SumWhere("$statistic.totalView", "pending", BudgetAny)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$eq": []interface{}{"$status", "pending"}},
		"$statistic.totalView",
		0,
	}}}
	assertBson(t, "status only", want, got)
}

func TestSumWhere_BudgetExceededOnly(t *testing.T) {
	got := SumWhere("$cash", "", BudgetExceeded)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$eq": []interface{}{"$isBudgetExceeded", true}},
		"$cash",
		0,
	}}}
	assertBson(t, "exceeded only", want, got)
}

func TestSumWhere_StatusAndRewarded(t *testing.T) {
	got := SumWhere("$statistic.totalView", "pending", BudgetRewarded)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$and": []bson.M{
			{"$eq": []interface{}{"$status", "pending"}},
			{"$ne": []interface{}{"$isBudgetExceeded", true}},
		}},
		"$statistic.totalView",
		0,
	}}}
	assertBson(t, "status and rewarded", want, got)
}

func TestSumWhere_StatusAndExceeded(t *testing.T) {
	got := SumWhere("$statistic.totalView", "completed", BudgetExceeded)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$and": []bson.M{
			{"$eq": []interface{}{"$status", "completed"}},
			{"$eq": []interface{}{"$isBudgetExceeded", true}},
		}},
		"$statistic.totalView",
		0,
	}}}
	assertBson(t, "status and exceeded", want, got)
}

func TestSumTransfer_Rewarded(t *testing.T) {
	got := SumTransfer("$statistic.totalView", BudgetRewarded)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$and": []bson.M{
			{"$eq": []interface{}{"$isTransfer", true}},
			{"$ne": []interface{}{"$isBudgetExceeded", true}},
		}},
		"$statistic.totalView",
		0,
	}}}
	assertBson(t, "transfer rewarded", want, got)
}

func TestSumTransfer_Any(t *testing.T) {
	got := SumTransfer("$cash", BudgetAny)
	want := bson.M{"$sum": bson.M{"$cond": []interface{}{
		bson.M{"$eq": []interface{}{"$isTransfer", true}},
		"$cash",
		0,
	}}}
	assertBson(t, "transfer any", want, got)
}

func assertBson(t *testing.T, name string, expected, actual bson.M) {
	t.Helper()
	if !reflect.DeepEqual(expected, actual) {
		t.Errorf("%s:\n expected %#v\n got      %#v", name, expected, actual)
	}
}
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `go test ./internal/module/database/mongodb/aggregate_pipeline/ -run TestSum -v`
Expected: FAIL, báo `undefined: SumWhere`

- [ ] **Step 3: Viết implementation tối thiểu**

Tạo `backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder.go`:

```go
package aggregatepipeline

import (
	"go.mongodb.org/mongo-driver/bson"
)

// BudgetFilter chọn nhóm document theo cờ isBudgetExceeded của event_reward.
type BudgetFilter int

const (
	// BudgetAny không lọc theo ngân sách.
	BudgetAny BudgetFilter = iota
	// BudgetRewarded chỉ lấy document sinh ra tiền thưởng.
	// Dùng $ne nên document cũ chưa có field isBudgetExceeded cũng được tính vào đây.
	BudgetRewarded
	// BudgetExceeded chỉ lấy document bị loại do event vượt ngân sách.
	BudgetExceeded
)

func budgetCond(budget BudgetFilter) (bson.M, bool) {
	switch budget {
	case BudgetRewarded:
		return bson.M{"$ne": []interface{}{"$isBudgetExceeded", true}}, true
	case BudgetExceeded:
		return bson.M{"$eq": []interface{}{"$isBudgetExceeded", true}}, true
	default:
		return nil, false
	}
}

func sumOf(field string, conds []bson.M) bson.M {
	if len(conds) == 0 {
		return bson.M{"$sum": field}
	}
	var match interface{} = conds[0]
	if len(conds) > 1 {
		match = bson.M{"$and": conds}
	}
	return bson.M{"$sum": bson.M{"$cond": []interface{}{match, field, 0}}}
}

// SumWhere sinh một nhánh $sum cho $group, lọc theo status của event_reward
// và theo cờ vượt ngân sách.
//
// field là đường dẫn cần cộng, ví dụ "$statistic.totalView" hoặc "$cash".
// status rỗng nghĩa là không lọc theo status.
func SumWhere(field, status string, budget BudgetFilter) bson.M {
	conds := make([]bson.M, 0, 2)
	if status != "" {
		conds = append(conds, bson.M{"$eq": []interface{}{"$status", status}})
	}
	if c, ok := budgetCond(budget); ok {
		conds = append(conds, c)
	}
	return sumOf(field, conds)
}

// SumTransfer sinh nhánh $sum lọc theo cờ isTransfer thay vì status.
func SumTransfer(field string, budget BudgetFilter) bson.M {
	conds := []bson.M{{"$eq": []interface{}{"$isTransfer", true}}}
	if c, ok := budgetCond(budget); ok {
		conds = append(conds, c)
	}
	return sumOf(field, conds)
}
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `go test ./internal/module/database/mongodb/aggregate_pipeline/ -run TestSum -v`
Expected: PASS, 7 test

- [ ] **Step 5: Commit**

```bash
git add backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder.go \
        backend/internal/module/database/mongodb/aggregate_pipeline/sum_builder_test.go
git commit -m "feat(aggregate): them builder nhanh sum co dieu kien theo status va ngan sach"
```

---

## Task 2: M2 — Bộ tính số lượt xem hiển thị

Đây là nơi tập trung mọi phép trừ dễ sai. Tách thành hàm thuần để test độc lập.

**Files:**
- Create: `backend/internal/util/viewstat/viewstat.go`
- Test: `backend/internal/util/viewstat/viewstat_test.go`

**Interfaces:**
- Consumes: không
- Produces:
  - `func Rewarded(total, exceeded float64) float64`
  - `type TableRow struct { Total, Rewarded, NotRewarded, Waiting float64 }`
  - `func SourceTable(viewCompleted, viewCashback, exceedCashback, exceedCompleted float64) TableRow`

- [ ] **Step 1: Viết test thất bại**

Tạo `backend/internal/util/viewstat/viewstat_test.go`:

```go
package viewstat

import "testing"

func TestRewarded_KhongVuotNganSach(t *testing.T) {
	assertFloat64(t, "rewarded", 1000, Rewarded(1000, 0))
}

func TestRewarded_VuotMotPhan(t *testing.T) {
	assertFloat64(t, "rewarded", 600, Rewarded(1000, 400))
}

func TestRewarded_VuotToanBo(t *testing.T) {
	assertFloat64(t, "rewarded", 0, Rewarded(1000, 1000))
}

func TestRewarded_DuLieuKhongNhatQuan_KepVeKhong(t *testing.T) {
	// exceeded lớn hơn total chỉ xảy ra khi dữ liệu lệch; không được trả số âm
	assertFloat64(t, "rewarded", 0, Rewarded(500, 900))
}

func TestSourceTable_KhongVuotNganSach(t *testing.T) {
	got := SourceTable(10000, 6000, 0, 0)
	assertFloat64(t, "total", 10000, got.Total)
	assertFloat64(t, "rewarded", 6000, got.Rewarded)
	assertFloat64(t, "notRewarded", 0, got.NotRewarded)
	assertFloat64(t, "waiting", 4000, got.Waiting)
}

func TestSourceTable_VuotNganSachCaHaiTrangThai(t *testing.T) {
	// 10000 view content đã duyệt
	// 6000 view đã đối soát, trong đó 800 vượt ngân sách
	// 500 view đang chờ đối soát nhưng đã vượt ngân sách
	got := SourceTable(10000, 6000, 800, 500)
	assertFloat64(t, "total", 10000, got.Total)
	assertFloat64(t, "rewarded", 5200, got.Rewarded)
	assertFloat64(t, "notRewarded", 1300, got.NotRewarded)
	assertFloat64(t, "waiting", 3500, got.Waiting)
}

func TestSourceTable_BonCotCongLaiBangTong(t *testing.T) {
	got := SourceTable(10000, 6000, 800, 500)
	sum := got.Rewarded + got.NotRewarded + got.Waiting
	assertFloat64(t, "tong ba cot", got.Total, sum)
}

func TestSourceTable_DuLieuChuaBackfill(t *testing.T) {
	// viewExceedBudget toàn 0 thì kết quả phải giống hệt hành vi hiện tại
	got := SourceTable(10000, 6000, 0, 0)
	assertFloat64(t, "rewarded", 6000, got.Rewarded)
	assertFloat64(t, "waiting", 4000, got.Waiting)
}

func TestSourceTable_HaiNguonLech_WaitingKepVeKhong(t *testing.T) {
	// cashback (event_reward) vượt completed (content) — có thể xảy ra do lệch nguồn
	got := SourceTable(1000, 1500, 0, 0)
	assertFloat64(t, "waiting", 0, got.Waiting)
}

func assertFloat64(t *testing.T, name string, expected, actual float64) {
	t.Helper()
	if expected != actual {
		t.Errorf("%s: expected %f, got %f", name, expected, actual)
	}
}
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `go test ./internal/util/viewstat/ -v`
Expected: FAIL, báo `undefined: Rewarded`

- [ ] **Step 3: Viết implementation tối thiểu**

Tạo `backend/internal/util/viewstat/viewstat.go`:

```go
// Package viewstat tính các con số lượt xem dùng để hiển thị, từ tổng lượt xem
// và phần lượt xem không sinh tiền thưởng do event vượt ngân sách.
package viewstat

func clampZero(v float64) float64 {
	if v < 0 {
		return 0
	}
	return v
}

// Rewarded trả về phần lượt xem có sinh tiền thưởng trong một bucket.
// total là tổng của bucket, exceeded là phần vượt ngân sách nằm bên trong nó.
// Kết quả không bao giờ âm.
func Rewarded(total, exceeded float64) float64 {
	return clampZero(total - exceeded)
}

// TableRow là bốn con số của một dòng trong bảng thống kê theo nguồn
// trên trang cá nhân của ambassador.
type TableRow struct {
	Total       float64 // lượt xem của content đã duyệt
	Rewarded    float64 // đã đối soát và có tiền
	NotRewarded float64 // không được tính thưởng do vượt ngân sách
	Waiting     float64 // còn lại, sẽ được xét ở kỳ sau
}

// SourceTable tính bốn cột cho một nguồn.
//
// viewCompleted lấy từ collection content: lượt xem của content đã duyệt.
// viewCashback lấy từ event_reward: lượt xem của phần thưởng đã đối soát.
// exceedCashback là phần vượt ngân sách nằm trong viewCashback.
// exceedCompleted là phần vượt ngân sách của phần thưởng đang chờ đối soát.
//
// Lưu ý viewCompleted và exceedCompleted KHÔNG cùng hệ đo: cái đầu đếm theo
// trạng thái của content, cái sau theo trạng thái của phần thưởng.
func SourceTable(viewCompleted, viewCashback, exceedCashback, exceedCompleted float64) TableRow {
	rewarded := Rewarded(viewCashback, exceedCashback)
	notRewarded := exceedCashback + exceedCompleted
	return TableRow{
		Total:       viewCompleted,
		Rewarded:    rewarded,
		NotRewarded: notRewarded,
		Waiting:     clampZero(viewCompleted - rewarded - notRewarded),
	}
}
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `go test ./internal/util/viewstat/ -v`
Expected: PASS, 9 test

- [ ] **Step 5: Commit**

```bash
git add backend/internal/util/viewstat/
git commit -m "feat(viewstat): them bo tinh luot xem duoc tinh thuong"
```

---

## Task 3: Kỳ đối soát — model, pipeline, và M3

**Files:**
- Modify: `backend/internal/model/mg/reconciliation_item.go:32-48`
- Modify: `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go:11-24` (struct) và `:32-128` (pipeline)
- Create: `backend/pkg/admin/service/reconciliation_content_item.go`
- Modify: `backend/pkg/admin/service/reconciliation_processing.go:178-235`
- Test: `backend/pkg/admin/service/reconciliation_content_item_test.go`

**Interfaces:**
- Consumes: `aggregatepipeline.SumWhere`, `aggregatepipeline.BudgetRewarded`, `aggregatepipeline.BudgetExceeded` từ Task 1
- Produces:
  - `modelmg.ReconciliationItemContent.TotalViewPendingRewarded int64`
  - `modelmg.ReconciliationItemContent.TotalViewPendingExceeded int64`
  - `aggregatepipeline.TotalCashRewardByContent.TotalViewPendingRewarded float64`
  - `aggregatepipeline.TotalCashRewardByContent.TotalViewPendingExceeded float64`
  - `func shouldSkipReconciliationContent(item aggregatepipeline.TotalCashRewardByContent) bool`
  - `func buildReconciliationItemContent(item aggregatepipeline.TotalCashRewardByContent, content *modelmg.ContentRaw) *modelmg.ReconciliationItemContent`

- [ ] **Step 1: Thêm field vào model**

Trong `backend/internal/model/mg/reconciliation_item.go`, thêm vào struct `ReconciliationItemContent`, ngay dưới `TotalViewPending`:

```go
	// TotalViewPendingRewarded và TotalViewPendingExceeded là hai phần của
	// TotalViewPending. Bất biến: Rewarded + Exceeded == TotalViewPending.
	// Rewarded nhân với CashPerView bằng đúng TotalCashPending.
	TotalViewPendingRewarded int64 `json:"totalViewPendingRewarded" bson:"totalViewPendingRewarded"`
	TotalViewPendingExceeded int64 `json:"totalViewPendingExceeded" bson:"totalViewPendingExceeded"`
```

- [ ] **Step 2: Thêm field vào struct aggregate**

Trong `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go`, thêm vào `TotalCashRewardByContent`, dưới `TotalViewPending`:

```go
	TotalViewPendingRewarded float64 `json:"totalViewPendingRewarded" bson:"totalViewPendingRewarded"`
	TotalViewPendingExceeded float64 `json:"totalViewPendingExceeded" bson:"totalViewPendingExceeded"`
```

- [ ] **Step 3: Thêm hai nhánh vào pipeline**

Trong cùng file, trong `$group` của `GetTotalCashRewardByContent`, thêm ngay sau nhánh `"totalViewPending"`. Không sửa nhánh nào đang có:

```go
				"totalViewPendingRewarded": SumWhere("$statistic.totalView", constants.StatusPending, BudgetRewarded),
				"totalViewPendingExceeded": SumWhere("$statistic.totalView", constants.StatusPending, BudgetExceeded),
```

- [ ] **Step 4: Viết test thất bại cho M3**

Tạo `backend/pkg/admin/service/reconciliation_content_item_test.go`:

```go
package adminservice

import (
	"testing"

	aggregatepipeline "viewboost/internal/module/database/mongodb/aggregate_pipeline"
	modelmg "viewboost/internal/model/mg"
)

func sampleContent() *modelmg.ContentRaw {
	c := new(modelmg.ContentRaw)
	c.Statistic.Like.Total = 300
	c.Statistic.Comment.Total = 200
	return c
}

func TestShouldSkip_KhongCoViewChoDoiSoat(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{}
	if !shouldSkipReconciliationContent(item) {
		t.Error("phai bo qua khi khong co view cho doi soat")
	}
}

func TestShouldSkip_ToanBoVuotNganSach(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{
		TotalViewPending:         500,
		TotalViewPendingRewarded: 0,
		TotalViewPendingExceeded: 500,
	}
	if !shouldSkipReconciliationContent(item) {
		t.Error("phai bo qua content ma toan bo view deu vuot ngan sach")
	}
}

func TestShouldSkip_CoViewDuocTinhThuong(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{
		TotalViewPending:         500,
		TotalViewPendingRewarded: 100,
		TotalViewPendingExceeded: 400,
	}
	if shouldSkipReconciliationContent(item) {
		t.Error("khong duoc bo qua khi con view duoc tinh thuong")
	}
}

func TestBuildItemContent_BatBienHaiPhanCongBangTong(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{
		TotalViewPending:         1000,
		TotalViewPendingRewarded: 600,
		TotalViewPendingExceeded: 400,
		TotalView:                1500,
	}
	got := buildReconciliationItemContent(item, sampleContent())
	if got.TotalViewPendingRewarded+got.TotalViewPendingExceeded != got.TotalViewPending {
		t.Errorf("bat bien sai: %d + %d != %d",
			got.TotalViewPendingRewarded, got.TotalViewPendingExceeded, got.TotalViewPending)
	}
}

func TestBuildItemContent_ViewDuocTinhThuongKhopTien(t *testing.T) {
	const cashPerView = 200.0
	item := aggregatepipeline.TotalCashRewardByContent{
		TotalViewPending:         1000,
		TotalViewPendingRewarded: 600,
		TotalViewPendingExceeded: 400,
		TotalCashPending:         600 * cashPerView,
		TotalView:                1500,
	}
	got := buildReconciliationItemContent(item, sampleContent())
	want := float64(got.TotalViewPendingRewarded) * cashPerView
	if got.TotalCashPending != want {
		t.Errorf("tien khong khop view: expected %f, got %f", want, got.TotalCashPending)
	}
}

func TestBuildItemContent_GiuNguyenCacFieldCu(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{
		TotalViewPending:         1000,
		TotalViewPendingRewarded: 600,
		TotalViewPendingExceeded: 400,
		TotalViewCompleted:       200,
		TotalViewRejected:        100,
		TotalView:                1500,
	}
	got := buildReconciliationItemContent(item, sampleContent())
	if got.TotalViewPending != 1000 {
		t.Errorf("TotalViewPending phai giu nguyen la tong: got %d", got.TotalViewPending)
	}
	if got.TotalViewBegin != 300 {
		t.Errorf("TotalViewBegin = rejected + completed: expected 300, got %d", got.TotalViewBegin)
	}
	if got.TotalViewEnd != 1500 {
		t.Errorf("TotalViewEnd = tong tran: expected 1500, got %d", got.TotalViewEnd)
	}
}

func TestBuildItemContent_EngagementKhongChiaChoKhong(t *testing.T) {
	item := aggregatepipeline.TotalCashRewardByContent{TotalView: 0}
	got := buildReconciliationItemContent(item, sampleContent())
	if got.Engagement != 0 {
		t.Errorf("expected 0, got %f", got.Engagement)
	}
}
```

- [ ] **Step 5: Chạy test để xác nhận thất bại**

Run: `go test ./pkg/admin/service/ -run 'TestShouldSkip|TestBuildItemContent' -v`
Expected: FAIL, báo `undefined: shouldSkipReconciliationContent`

- [ ] **Step 6: Viết M3**

Tạo `backend/pkg/admin/service/reconciliation_content_item.go`:

```go
package adminservice

import (
	"math"

	modelmg "viewboost/internal/model/mg"
	aggregatepipeline "viewboost/internal/module/database/mongodb/aggregate_pipeline"
)

// shouldSkipReconciliationContent quyết định một dòng aggregate có được đưa
// vào kỳ đối soát hay không.
//
// Content mà toàn bộ lượt xem chờ đối soát đều vượt ngân sách sẽ bị loại, vì
// kỳ này không chi đồng nào cho nó.
func shouldSkipReconciliationContent(item aggregatepipeline.TotalCashRewardByContent) bool {
	return item.TotalViewPendingRewarded == 0
}

// buildReconciliationItemContent dựng phần content của một dòng đối soát từ
// kết quả aggregate và thông tin content.
//
// Mọi field đang có giữ nguyên ý nghĩa. Hai field mới là hai phần của
// TotalViewPending.
func buildReconciliationItemContent(
	item aggregatepipeline.TotalCashRewardByContent,
	content *modelmg.ContentRaw,
) *modelmg.ReconciliationItemContent {
	c := &modelmg.ReconciliationItemContent{
		ID:                       item.ID.Content,
		Schema:                   item.ID.Schema,
		Engagement:               0,
		TotalLike:                int64(content.Statistic.Like.Total),
		TotalComment:             int64(content.Statistic.Comment.Total),
		TotalViewBegin:           int64(item.TotalViewRejected + item.TotalViewCompleted),
		TotalViewPending:         int64(item.TotalViewPending),
		TotalViewPendingRewarded: int64(item.TotalViewPendingRewarded),
		TotalViewPendingExceeded: int64(item.TotalViewPendingExceeded),
		TotalViewCompleted:       int64(item.TotalViewCompleted),
		TotalViewRejected:        int64(item.TotalViewRejected),
		TotalViewEnd:             int64(item.TotalView),
		TotalCashPending:         item.TotalCashPending,
		TotalCashCompleted:       item.TotalCashCompleted,
		TotalCashRejected:        item.TotalCashRejected,
	}
	if c.TotalViewEnd > 0 {
		engagement := (content.Statistic.Like.Total + content.Statistic.Comment.Total) / item.TotalView
		c.Engagement = math.Round(engagement*10000) / 10000
	}
	return c
}
```

- [ ] **Step 7: Chạy test để xác nhận pass**

Run: `go test ./pkg/admin/service/ -run 'TestShouldSkip|TestBuildItemContent' -v`
Expected: PASS, 7 test

- [ ] **Step 8: Nối M3 vào ProcessingContent**

Trong `backend/pkg/admin/service/reconciliation_processing.go`, thay thân vòng lặp từ dòng 192 tới 230. Thay:

```go
		if item.TotalViewPending == 0 {
			fmt.Println("Not view pending")
			continue
		}
```

bằng:

```go
		if shouldSkipReconciliationContent(item) {
			fmt.Println("Not rewarded view pending")
			continue
		}
```

Rồi thay toàn bộ khối `Content: &modelmg.ReconciliationItemContent{...}` bằng `Content: buildReconciliationItemContent(item, content),` và xoá khối `if p.Content.TotalViewEnd > 0 { ... }` phía dưới, vì `buildReconciliationItemContent` đã tính `Engagement`.

Kết quả phần dựng payload:

```go
		p := &modelmg.ReconciliationItemRaw{
			ID:             modelmg.NewAppID(),
			Reconciliation: rc.ID,
			Type:           constants.ReconciliationItemTypeContent,
			User:           item.ID.User,
			TotalCash:      item.TotalCashPending,
			SearchString:   content.SearchString,
			Content:        buildReconciliationItemContent(item, content),
			Status:         constants.StatusPending,
			FirstAt:        item.FirstAt,
			LastAt:         item.LastAt,
			CreatedAt:      time.Now(),
			UpdatedAt:      time.Now(),
		}
		payloads = append(payloads, p)
```

Nếu `math` không còn được dùng ở file này thì xoá import.

- [ ] **Step 9: Build và chạy toàn bộ test**

Run: `go build ./... && go test ./pkg/admin/service/ ./internal/... -count=1`
Expected: build sạch, test pass

- [ ] **Step 10: Commit**

```bash
git add backend/internal/model/mg/reconciliation_item.go \
        backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go \
        backend/pkg/admin/service/reconciliation_content_item.go \
        backend/pkg/admin/service/reconciliation_content_item_test.go \
        backend/pkg/admin/service/reconciliation_processing.go
git commit -m "feat(reconciliation): tach view cho doi soat thanh phan duoc thuong va phan vuot ngan sach"
```

---

## Task 4: Kỳ đối soát — response, export, giao diện admin

**Files:**
- Modify: `backend/pkg/admin/model/response/reconciliation.go:42-60`
- Modify: `backend/pkg/admin/service/reconciliation.go:206-229`
- Modify: `backend/pkg/admin/service/export_reconciliation.go:91-99` và `:280-289`
- Modify: `admin/src/pages/reconciliation/detail/components/tabs/content/type.d.ts:39-43`
- Modify: `admin/src/pages/reconciliation/detail/components/tabs/content/components/table.tsx:64-73`
- Modify: `admin/src/pages/reconciliation/detail/components/tabs/content/components/info-modal.tsx:17-33`
- Modify: `admin/src/locales/vi-VN.ts`

**Interfaces:**
- Consumes: `TotalViewPendingRewarded`, `TotalViewPendingExceeded` từ Task 3
- Produces: hai key JSON `viewPendingRewarded` và `viewPendingExceeded` trong `ReconciliationContentItem`

- [ ] **Step 1: Thêm hai key vào response DTO**

Trong `backend/pkg/admin/model/response/reconciliation.go`, thêm vào `ReconciliationContentItem` ngay dưới `ViewPending`:

```go
	ViewPendingRewarded int64 `json:"viewPendingRewarded"`
	ViewPendingExceeded int64 `json:"viewPendingExceeded"`
```

- [ ] **Step 2: Map hai key ở service**

Trong `backend/pkg/admin/service/reconciliation.go`, trong khối dựng `response.ReconciliationContentItem`, thêm ngay dưới `ViewPending`:

```go
				ViewPendingRewarded: rc.Content.TotalViewPendingRewarded,
				ViewPendingExceeded: rc.Content.TotalViewPendingExceeded,
```

- [ ] **Step 3: Build backend**

Run: `go build ./...`
Expected: build sạch

- [ ] **Step 4: Thêm cột vào file Excel đối soát**

Trong `backend/pkg/admin/service/export_reconciliation.go`, ở danh sách header quanh dòng 91-99, thêm một cột ngay sau cột "Số view chờ đối soát trong kỳ":

```go
		"Số view không được tính thưởng",
```

Ở phần điền giá trị quanh dòng 280-289, đổi giá trị của cột "Số view chờ đối soát trong kỳ" từ `item.Content.TotalViewPending` sang `item.Content.TotalViewPendingRewarded`, rồi thêm ngay sau nó:

```go
		item.Content.TotalViewPendingExceeded,
```

Giữ đúng thứ tự giữa header và giá trị.

- [ ] **Step 5: Build và commit phần backend**

Run: `go build ./...`
Expected: build sạch

```bash
git add backend/pkg/admin/model/response/reconciliation.go \
        backend/pkg/admin/service/reconciliation.go \
        backend/pkg/admin/service/export_reconciliation.go
git commit -m "feat(reconciliation): tra ve va export so view khong duoc tinh thuong"
```

- [ ] **Step 6: Thêm nhãn tiếng Việt**

Trong `admin/src/locales/vi-VN.ts`, thêm hai khoá mới cạnh các khoá view hiện có:

```ts
  'label.viewReconciliationPendingRewarded': 'Lượt xem chờ đối soát',
  'label.viewNotRewarded': 'Lượt xem không được tính thưởng',
```

Nếu file dùng cấu trúc khoá lồng nhau thì đặt theo đúng cấu trúc đang có.

- [ ] **Step 7: Thêm hai key vào type**

Trong `admin/src/pages/reconciliation/detail/components/tabs/content/type.d.ts`, thêm dưới `viewPending`:

```ts
    viewPendingRewarded: number;
    viewPendingExceeded: number;
```

- [ ] **Step 8: Đổi cột và thêm cột trong bảng**

Trong `admin/src/pages/reconciliation/detail/components/tabs/content/components/table.tsx`, thay khối cột `viewPending` bằng hai khối:

```tsx
    {
      title: intl.formatMessage({ id: key.label.viewReconciliationPendingRewarded }),
      width: 120,
      dataIndex: ['viewPendingRewarded'],
      renderText: (value: number) => format.number(value),
    },
    {
      title: intl.formatMessage({ id: key.label.viewNotRewarded }),
      width: 140,
      dataIndex: ['viewPendingExceeded'],
      renderText: (value: number) => format.number(value),
    },
```

Nếu `key.label` là object hằng thì bổ sung hai khoá tương ứng vào đó trước.

- [ ] **Step 9: Thêm dòng vào modal chi tiết**

Trong `admin/src/pages/reconciliation/detail/components/tabs/content/components/info-modal.tsx`, trong mảng `[key.label.view]`, thay phần tử `'label.pending'` và thêm một phần tử mới ngay sau nó:

```tsx
          {
            _id: 'label.pendingRewarded',
            name: format.number(valueEdit.viewPendingRewarded),
          },
          {
            _id: 'label.viewNotRewarded',
            name: format.number(valueEdit.viewPendingExceeded),
          },
```

Thêm khoá `'label.pendingRewarded': 'Chờ đối soát'` vào `admin/src/locales/vi-VN.ts` nếu chưa có.

- [ ] **Step 10: Kiểm tra kiểu và build admin**

Run: `cd admin && npx tsc --noEmit`
Expected: không có lỗi kiểu

- [ ] **Step 11: Commit**

```bash
git add admin/src/locales/vi-VN.ts \
        admin/src/pages/reconciliation/detail/components/tabs/content/
git commit -m "feat(admin): hien thi cot view khong duoc tinh thuong trong ky doi soat"
```

---

## Task 5: Analytic — model, pipeline nguồn, và M4

**Files:**
- Modify: `backend/internal/model/mg/event_analytic_daily.go:28-32`
- Modify: `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go:130-160` (struct) và `:241-310` (pipeline)
- Create: `backend/internal/service/analytic_view_statistic.go`
- Modify: `backend/internal/service/event.go:505-521` và `:769-775`

**Interfaces:**
- Consumes: `SumWhere`, `SumTransfer`, `BudgetExceeded` từ Task 1
- Produces:
  - `modelmg.EventAnalyticDailyStatistic.ViewExceedBudget CommonStatisticContent`
  - `aggregatepipeline.StatisticRewardReport` thêm sáu field `TotalViewExceed*`
  - `func buildAnalyticViewStatistic(r aggregatepipeline.StatisticRewardReport) (view, viewExceed modelmg.CommonStatisticContent)`

- [ ] **Step 1: Thêm field vào model analytic**

Trong `backend/internal/model/mg/event_analytic_daily.go`, thêm vào `EventAnalyticDailyStatistic` ngay dưới `View`:

```go
	// ViewExceedBudget là phần lượt xem KHÔNG sinh tiền thưởng vì event vượt
	// ngân sách. Là tập con của View, cùng quy ước bucket với View.
	// Nguồn: event_reward, các document có isBudgetExceeded = true.
	ViewExceedBudget CommonStatisticContent `json:"viewExceedBudget" bson:"viewExceedBudget"`
```

`UserEventAnalyticDailyRaw.Statistic` dùng chung struct này nên không phải sửa gì thêm.

- [ ] **Step 2: Thêm field vào struct báo cáo aggregate**

Trong `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go`, thêm vào `StatisticRewardReport`, ngay dưới nhóm view hiện có:

```go
	TotalViewExceed            float64 `json:"totalViewExceed" bson:"totalViewExceed"`
	TotalViewExceedPending     float64 `json:"totalViewExceedPending" bson:"totalViewExceedPending"`
	TotalViewExceedCompleted   float64 `json:"totalViewExceedCompleted" bson:"totalViewExceedCompleted"`
	TotalViewExceedRejected    float64 `json:"totalViewExceedRejected" bson:"totalViewExceedRejected"`
	TotalViewExceedCashback    float64 `json:"totalViewExceedCashback" bson:"totalViewExceedCashback"`
	TotalViewExceedTransferred float64 `json:"totalViewExceedTransferred" bson:"totalViewExceedTransferred"`
```

- [ ] **Step 3: Thêm sáu nhánh vào GetStatisticRewardReport**

Trong `$group` của `GetStatisticRewardReport`, thêm ngay sau nhánh `"totalViewNoRejected"`. Không sửa nhánh nào đang có:

```go
				// View vượt ngân sách — tập con của các nhánh view phía trên
				"totalViewExceed":            SumWhere("$statistic.totalView", "", BudgetExceeded),
				"totalViewExceedPending":     SumWhere("$statistic.totalView", constants.StatusWaitingApproved, BudgetExceeded),
				"totalViewExceedCompleted":   SumWhere("$statistic.totalView", constants.StatusPending, BudgetExceeded),
				"totalViewExceedRejected":    SumWhere("$statistic.totalView", constants.StatusRejected, BudgetExceeded),
				"totalViewExceedCashback":    SumWhere("$statistic.totalView", constants.StatusCompleted, BudgetExceeded),
				"totalViewExceedTransferred": SumTransfer("$statistic.totalView", BudgetExceeded),
```

- [ ] **Step 4: Viết M4**

Tạo `backend/internal/service/analytic_view_statistic.go`:

```go
package internalservice

import (
	modelmg "viewboost/internal/model/mg"
	aggregatepipeline "viewboost/internal/module/database/mongodb/aggregate_pipeline"
)

// buildAnalyticViewStatistic dựng hai nhánh view của analytic từ báo cáo
// aggregate: nhánh tổng giữ nguyên ý nghĩa cũ, nhánh vượt ngân sách là tập
// con của nó.
//
// Dùng chung cho cả event_analytic_daily và user_event_analytic_daily để hai
// collection không thể lệch nhau.
func buildAnalyticViewStatistic(
	r aggregatepipeline.StatisticRewardReport,
) (view, viewExceed modelmg.CommonStatisticContent) {
	view = modelmg.CommonStatisticContent{
		Total:     r.TotalView,
		Pending:   r.TotalViewPending,
		Rejected:  r.TotalViewRejected,
		Completed: r.TotalViewCompleted,
		Cashback:  r.TotalViewCashback,
		Transfer:  r.TotalViewTransferred,
	}
	viewExceed = modelmg.CommonStatisticContent{
		Total:     r.TotalViewExceed,
		Pending:   r.TotalViewExceedPending,
		Rejected:  r.TotalViewExceedRejected,
		Completed: r.TotalViewExceedCompleted,
		Cashback:  r.TotalViewExceedCashback,
		Transfer:  r.TotalViewExceedTransferred,
	}
	return view, viewExceed
}
```

- [ ] **Step 5: Dùng M4 ở UpdateAnalyticUserEventDaily**

Trong `backend/internal/service/event.go`, trong `UpdateAnalyticUserEventDaily` quanh dòng 505-521, thay khối `View: modelmg.CommonStatisticContent{...}` trong `statistic`. Trước khi dựng `statistic`, thêm:

```go
	viewStat, viewExceedStat := buildAnalyticViewStatistic(rewardAnalytics)
```

rồi trong literal `statistic`, thay dòng `View: ...{...},` bằng:

```go
		View:             viewStat,
		ViewExceedBudget: viewExceedStat,
```

- [ ] **Step 6: Dùng M4 ở UpdateAnalyticEventDaily**

Làm y hệt Step 5 cho `UpdateAnalyticEventDaily` quanh dòng 769-775. Tên biến kết quả aggregate ở hàm này cũng là `rewardAnalytics`.

- [ ] **Step 7: Build và chạy test**

Run: `go build ./... && go test ./internal/... -count=1`
Expected: build sạch, test pass

- [ ] **Step 8: Commit**

```bash
git add backend/internal/model/mg/event_analytic_daily.go \
        backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go \
        backend/internal/service/analytic_view_statistic.go \
        backend/internal/service/event.go
git commit -m "feat(analytic): ghi nhanh view vuot ngan sach vao hai collection analytic"
```

---

## Task 6: Menu thống kê admin — pipeline đọc, response, giao diện

**Files:**
- Modify: `backend/internal/module/database/mongodb/aggregate_pipeline/event_analytic_daily.go:25-41` (struct `EventStatistic`), `:48-61` (struct `EventChart`), `:111-160` (pipeline)
- Modify: `backend/pkg/admin/model/response/event.go:75-100`
- Modify: `backend/pkg/admin/service/event.go:965-990`
- Modify: `admin/src/pages/event-statistic/index.tsx:94-110`
- Modify: `admin/src/locales/vi-VN.ts`

**Interfaces:**
- Consumes: `event_analytic_daily.statistic.viewExceedBudget` từ Task 5, `viewstat.Rewarded` từ Task 2
- Produces:
  - `aggregatepipeline.EventStatistic` thêm bốn field `TotalViewExceed*`
  - `response.EventStatisticResponse.ViewExceedBudget EventStatistic[int64]`

- [ ] **Step 1: Thêm bốn field vào hai struct**

Trong `backend/internal/module/database/mongodb/aggregate_pipeline/event_analytic_daily.go`, thêm vào **cả hai** struct `EventStatistic` và `EventChart[T]`, ngay dưới `TotalViewTransfer`:

```go
	TotalViewExceedPending  int64 `json:"totalViewExceedPending" bson:"totalViewExceedPending"`
	TotalViewExceedApproved int64 `json:"totalViewExceedApproved" bson:"totalViewExceedApproved"`
	TotalViewExceedCashback int64 `json:"totalViewExceedCashback" bson:"totalViewExceedCashback"`
	TotalViewExceedTransfer int64 `json:"totalViewExceedTransfer" bson:"totalViewExceedTransfer"`
```

- [ ] **Step 2: Thêm bốn nhánh vào GetEventStatistic**

Trong `$group` của `GetEventStatistic`, thêm ngay sau `"totalViewTransfer"`. Không dùng `$subtract` ở tầng này — pipeline chỉ cung cấp, tầng API mới trừ:

```go
				"totalViewExceedPending": bson.M{
					"$sum": "$statistic.viewExceedBudget.pending",
				},
				"totalViewExceedApproved": bson.M{
					"$sum": "$statistic.viewExceedBudget.completed",
				},
				"totalViewExceedCashback": bson.M{
					"$sum": "$statistic.viewExceedBudget.cashback",
				},
				"totalViewExceedTransfer": bson.M{
					"$sum": "$statistic.viewExceedBudget.transfer",
				},
```

Document cũ chưa có field này thì `$sum` trả 0, nên không cần `$ifNull`.

- [ ] **Step 3: Thêm nhóm mới vào response DTO**

Trong `backend/pkg/admin/model/response/event.go`, thêm vào `EventStatisticResponse` giữa `View` và `Cash`:

```go
	ViewExceedBudget EventStatistic[int64] `json:"viewExceedBudget"`
```

Dùng lại generic đang có, không định nghĩa type mới.

- [ ] **Step 4: Trừ ở converter**

Trong `backend/pkg/admin/service/event.go`, trong `convertStatisticRepsonse`, thay khối `View:` và thêm khối mới. Thêm import `"viewboost/internal/util/viewstat"`:

```go
		View: response.EventStatistic[int64]{
			Pending:  int64(viewstat.Rewarded(float64(r.TotalViewPending), float64(r.TotalViewExceedPending))),
			Approved: int64(viewstat.Rewarded(float64(r.TotalViewApproved), float64(r.TotalViewExceedApproved))),
			Cashback: int64(viewstat.Rewarded(float64(r.TotalViewCashback), float64(r.TotalViewExceedCashback))),
			Transfer: int64(viewstat.Rewarded(float64(r.TotalViewTransfer), float64(r.TotalViewExceedTransfer))),
		},
		ViewExceedBudget: response.EventStatistic[int64]{
			Pending:  r.TotalViewExceedPending,
			Approved: r.TotalViewExceedApproved,
			Cashback: r.TotalViewExceedCashback,
			Transfer: r.TotalViewExceedTransfer,
		},
```

Hai biểu đồ ở `getDailyChart` và hàm biểu đồ tháng **không** trừ — giữ nguyên, không sửa gì.

- [ ] **Step 5: Build**

Run: `go build ./...`
Expected: build sạch

- [ ] **Step 6: Commit phần backend**

```bash
git add backend/internal/module/database/mongodb/aggregate_pipeline/event_analytic_daily.go \
        backend/pkg/admin/model/response/event.go \
        backend/pkg/admin/service/event.go
git commit -m "feat(admin): menu thong ke tra ve view da tru phan vuot ngan sach"
```

- [ ] **Step 7: Thêm nhãn**

Trong `admin/src/locales/vi-VN.ts`, thêm:

```ts
  'label.viewExceedBudget': 'Không được tính thưởng',
```

- [ ] **Step 8: Thêm dòng vào nhóm thống kê**

Trong `admin/src/pages/event-statistic/index.tsx`, mảng `view` quanh dòng 94-110 đang có bốn phần tử. Thêm phần tử thứ năm vào cuối mảng, trước dấu `];`:

```tsx
        {
          _id: 'label.viewExceedBudget',
          name: format.number(statistic.viewExceedBudget.cashback),
        },
```

Bốn phần tử đang có giữ nguyên — chúng tự hiển thị số đã trừ vì backend đã trừ ở Step 4. Chỉ thêm dòng cho bucket `cashback` vì đó là dòng đứng cạnh số tiền đã chi thực tế; ba bucket còn lại của `viewExceedBudget` vẫn có trong payload nếu sau này cần.

- [ ] **Step 9: Kiểm tra kiểu**

Run: `cd admin && npx tsc --noEmit`
Expected: không có lỗi kiểu

- [ ] **Step 10: Commit**

```bash
git add admin/src/locales/vi-VN.ts admin/src/pages/event-statistic/index.tsx
git commit -m "feat(admin): hien thi dong view khong duoc tinh thuong o menu thong ke"
```

---

## Task 7: Hai file Excel báo cáo event

**Files:**
- Modify: `backend/pkg/admin/service/export_event_analytic.go:122-160` và `:232-270`

**Interfaces:**
- Consumes: `EventStatistic.TotalViewExceed*` từ Task 6, `viewstat.Rewarded` từ Task 2
- Produces: không

- [ ] **Step 1: Trừ và thêm cột ở export theo ngày**

Trong `backend/pkg/admin/service/export_event_analytic.go`, ở phần export theo ngày quanh dòng 148-151, đổi bốn giá trị view sang bản đã trừ và thêm bốn cột mới. Thêm import `"viewboost/internal/util/viewstat"`:

```go
		int64(viewstat.Rewarded(float64(d.TotalViewPending), float64(d.TotalViewExceedPending))),
		int64(viewstat.Rewarded(float64(d.TotalViewApproved), float64(d.TotalViewExceedApproved))),
		int64(viewstat.Rewarded(float64(d.TotalViewCashback), float64(d.TotalViewExceedCashback))),
		int64(viewstat.Rewarded(float64(d.TotalViewTransfer), float64(d.TotalViewExceedTransfer))),
		d.TotalViewExceedPending,
		d.TotalViewExceedApproved,
		d.TotalViewExceedCashback,
		d.TotalViewExceedTransfer,
```

Tên biến dòng dữ liệu có thể khác `d`; giữ đúng tên đang dùng trong file.

- [ ] **Step 2: Thêm header tương ứng**

Ở danh sách header của export theo ngày, thêm bốn cột ngay sau bốn cột view hiện có:

```go
		"Không tính thưởng - chờ duyệt",
		"Không tính thưởng - đã duyệt",
		"Không tính thưởng - đã đối soát",
		"Không tính thưởng - đã thanh toán",
```

- [ ] **Step 3: Làm y hệt cho export theo tháng**

Lặp lại Step 1 và Step 2 cho phần export theo tháng quanh dòng 232-270.

- [ ] **Step 4: Build**

Run: `go build ./...`
Expected: build sạch

- [ ] **Step 5: Commit**

```bash
git add backend/pkg/admin/service/export_event_analytic.go
git commit -m "feat(export): tach view khong duoc tinh thuong trong bao cao event"
```

---

## Task 8: Trang cá nhân — pipeline, M5, và refactor thống kê theo nguồn

Hàm `UpdateStatisticUserEvent` dài 636 dòng với mười khối gần giống hệt nhau. Câu lệnh ghi đè nguyên khối object thống kê, nên quên gán một nguồn nghĩa là **xoá** dữ liệu của nguồn đó. Task này gộp mười khối thành một hàm.

**Files:**
- Modify: `backend/internal/model/mg/user_event.go:164-170`
- Modify: `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go:808-960`
- Create: `backend/internal/service/user_event_source_statistic.go`
- Modify: `backend/internal/service/event.go:1125-1500`
- Test: `backend/internal/service/user_event_source_statistic_test.go`

**Interfaces:**
- Consumes: `SumWhere`, `SumTransfer`, `BudgetExceeded` từ Task 1
- Produces:
  - `modelmg.UserContentStatistic.ViewExceedBudget CommonStatisticContent`
  - `aggregatepipeline.StatisticContentBySource` thêm bốn field `TotalViewExceed*`
  - `func buildSourceStatistic(c aggregatepipeline.StatisticContentSourceByEventAndUser, r aggregatepipeline.StatisticContentBySource) modelmg.UserContentStatistic`

- [ ] **Step 1: Thêm field vào model**

Trong `backend/internal/model/mg/user_event.go`, thêm vào `UserContentStatistic` ngay dưới `View`:

```go
	// ViewExceedBudget là phần lượt xem không sinh tiền thưởng vì event vượt
	// ngân sách. Toàn bộ đến từ event_reward.
	//
	// CẢNH BÁO: khác với View trong cùng struct. View trộn hai nguồn —
	// Total/Pending/Rejected/Completed lấy từ collection content, chỉ
	// Cashback/Transfer lấy từ event_reward. Vì vậy slot Completed ở đây
	// (phần thưởng đang chờ đối soát) KHÔNG cùng hệ đo với View.Completed
	// (content đã duyệt). Chỉ Cashback và Transfer so sánh trực tiếp được.
	ViewExceedBudget CommonStatisticContent `json:"viewExceedBudget" bson:"viewExceedBudget"`
```

- [ ] **Step 2: Thêm field vào struct aggregate theo nguồn**

Trong `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go`, thêm vào `StatisticContentBySource`:

```go
	TotalViewExceedCompleted   int64 `json:"totalViewExceedCompleted" bson:"totalViewExceedCompleted"`
	TotalViewExceedWaiting     int64 `json:"totalViewExceedWaiting" bson:"totalViewExceedWaiting"`
	TotalViewExceedPending     int64 `json:"totalViewExceedPending" bson:"totalViewExceedPending"`
	TotalViewExceedRejected    int64 `json:"totalViewExceedRejected" bson:"totalViewExceedRejected"`
	TotalViewExceedTransferred int64 `json:"totalViewExceedTransferred" bson:"totalViewExceedTransferred"`
```

- [ ] **Step 3: Thêm năm nhánh vào GetStatisticContentBySource**

Trong `$group` của `GetStatisticContentBySource`, thêm sau các nhánh hiện có. Không sửa nhánh nào đang có:

```go
				"totalViewExceedCompleted":   SumWhere("$statistic.totalView", constants.StatusCompleted, BudgetExceeded),
				"totalViewExceedWaiting":     SumWhere("$statistic.totalView", constants.StatusWaitingApproved, BudgetExceeded),
				"totalViewExceedPending":     SumWhere("$statistic.totalView", constants.StatusPending, BudgetExceeded),
				"totalViewExceedRejected":    SumWhere("$statistic.totalView", constants.StatusRejected, BudgetExceeded),
				"totalViewExceedTransferred": SumTransfer("$statistic.totalView", BudgetExceeded),
```

- [ ] **Step 4: Viết test thất bại cho M5**

Tạo `backend/internal/service/user_event_source_statistic_test.go`:

```go
package internalservice

import (
	"testing"

	aggregatepipeline "viewboost/internal/module/database/mongodb/aggregate_pipeline"
)

func sampleContentStats() aggregatepipeline.StatisticContentSourceByEventAndUser {
	return aggregatepipeline.StatisticContentSourceByEventAndUser{
		TotalView:          10000,
		TotalViewCompleted: 8000,
		TotalViewPending:   1500,
		TotalViewRejected:  500,

		TotalLike:          300,
		TotalLikeCompleted: 250,
		TotalLikePending:   40,
		TotalLikeRejected:  10,

		TotalComment:          200,
		TotalCommentCompleted: 170,
		TotalCommentPending:   20,
		TotalCommentRejected:  10,
	}
}

func sampleRewardStats() aggregatepipeline.StatisticContentBySource {
	return aggregatepipeline.StatisticContentBySource{
		TotalViewCompleted:      6000,
		TotalViewWaitingApprove: 900,
		TotalViewPending:        1000,
		TotalViewRejected:       100,
		TotalViewTransferred:    5000,

		TotalViewCash:               1200000,
		TotalViewCashWaitingApprove: 180000,
		TotalViewCashPending:        200000,
		TotalViewCashRejected:       20000,
		TotalViewCashCompleted:      1200000,
		TotalViewCashTransferred:    1000000,

		TotalViewExceedCompleted:   800,
		TotalViewExceedPending:     500,
		TotalViewExceedTransferred: 700,
	}
}

func TestBuildSourceStatistic_ViewLayTuContent(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	assertFloat64(t, "View.Total", 10000, got.View.Total)
	assertFloat64(t, "View.Completed", 8000, got.View.Completed)
	assertFloat64(t, "View.Rejected", 500, got.View.Rejected)
}

func TestBuildSourceStatistic_ViewPendingLayTuViewChuKhongPhaiComment(t *testing.T) {
	// chan hoi quy cho loi chep nham o nhanh youtube truoc day
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	assertFloat64(t, "View.Pending", 1500, got.View.Pending)
}

func TestBuildSourceStatistic_CashbackVaTransferLayTuReward(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	assertFloat64(t, "View.Cashback", 6000, got.View.Cashback)
	assertFloat64(t, "View.Transfer", 5000, got.View.Transfer)
}

func TestBuildSourceStatistic_GanDuNhanhVuotNganSach(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	assertFloat64(t, "ViewExceedBudget.Cashback", 800, got.ViewExceedBudget.Cashback)
	assertFloat64(t, "ViewExceedBudget.Completed", 500, got.ViewExceedBudget.Completed)
	assertFloat64(t, "ViewExceedBudget.Transfer", 700, got.ViewExceedBudget.Transfer)
}

func TestBuildSourceStatistic_ExceedKhongVuotQuaCashback(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	if got.ViewExceedBudget.Cashback > got.View.Cashback {
		t.Errorf("ViewExceedBudget.Cashback (%f) khong duoc lon hon View.Cashback (%f)",
			got.ViewExceedBudget.Cashback, got.View.Cashback)
	}
}

func TestBuildSourceStatistic_CashTotalTruWaiting(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	assertFloat64(t, "Cash.Total", 1200000-180000, got.Cash.Total)
	assertFloat64(t, "Cash.Waiting", 180000, got.Cash.Waiting)
}

func TestBuildSourceStatistic_DuLieuChuaBackfill(t *testing.T) {
	r := sampleRewardStats()
	r.TotalViewExceedCompleted = 0
	r.TotalViewExceedPending = 0
	r.TotalViewExceedTransferred = 0
	got := buildSourceStatistic(sampleContentStats(), r)
	assertFloat64(t, "ViewExceedBudget.Cashback", 0, got.ViewExceedBudget.Cashback)
	assertFloat64(t, "View.Cashback", 6000, got.View.Cashback)
}

func TestBuildSourceStatistic_ExceedTotalBangTongCacBucket(t *testing.T) {
	got := buildSourceStatistic(sampleContentStats(), sampleRewardStats())
	want := got.ViewExceedBudget.Pending +
		got.ViewExceedBudget.Rejected +
		got.ViewExceedBudget.Completed +
		got.ViewExceedBudget.Cashback
	assertFloat64(t, "ViewExceedBudget.Total", want, got.ViewExceedBudget.Total)
}
```

Ghi chú: `assertFloat64` đã tồn tại trong package `internalservice` ở `budget_split_test.go`, dùng lại, không định nghĩa mới.

- [ ] **Step 5: Chạy test để xác nhận thất bại**

Run: `go test ./internal/service/ -run TestBuildSourceStatistic -v`
Expected: FAIL, báo `undefined: buildSourceStatistic`

- [ ] **Step 6: Viết M5**

Tạo `backend/internal/service/user_event_source_statistic.go`:

```go
package internalservice

import (
	modelmg "viewboost/internal/model/mg"
	aggregatepipeline "viewboost/internal/module/database/mongodb/aggregate_pipeline"
)

// buildSourceStatistic dựng thống kê của một nguồn nội dung cho user_event.
//
// c đến từ collection content: lượt xem, lượt thích, bình luận theo trạng thái
// của chính content.
// r đến từ collection event_reward: lượt xem và tiền theo trạng thái của phần
// thưởng.
//
// Hàm này thay cho mười khối chép tay trước đây. Vì câu lệnh ghi đè nguyên
// khối object thống kê, thiếu một nguồn nghĩa là xoá dữ liệu của nguồn đó —
// dùng chung một hàm để chuyện đó không xảy ra.
func buildSourceStatistic(
	c aggregatepipeline.StatisticContentSourceByEventAndUser,
	r aggregatepipeline.StatisticContentBySource,
) modelmg.UserContentStatistic {
	s := modelmg.UserContentStatistic{
		View: modelmg.CommonStatisticContent{
			Total:     float64(c.TotalView),
			Pending:   float64(c.TotalViewPending),
			Rejected:  float64(c.TotalViewRejected),
			Completed: float64(c.TotalViewCompleted),
			Cashback:  float64(r.TotalViewCompleted),
			Transfer:  float64(r.TotalViewTransferred),
		},
		ViewExceedBudget: modelmg.CommonStatisticContent{
			Pending:   float64(r.TotalViewExceedWaiting),
			Rejected:  float64(r.TotalViewExceedRejected),
			Completed: float64(r.TotalViewExceedPending),
			Cashback:  float64(r.TotalViewExceedCompleted),
			Transfer:  float64(r.TotalViewExceedTransferred),
		},
		Like: modelmg.CommonStatisticContent{
			Total:     float64(c.TotalLike),
			Pending:   float64(c.TotalLikePending),
			Rejected:  float64(c.TotalLikeRejected),
			Completed: float64(c.TotalLikeCompleted),
		},
		Comment: modelmg.CommonStatisticContent{
			Total:     float64(c.TotalComment),
			Pending:   float64(c.TotalCommentPending),
			Rejected:  float64(c.TotalCommentRejected),
			Completed: float64(c.TotalCommentCompleted),
		},
		Cash: modelmg.CommonStatisticContent{
			Total:     r.TotalViewCash - r.TotalViewCashWaitingApprove,
			Waiting:   r.TotalViewCashWaitingApprove,
			Pending:   r.TotalViewCashPending,
			Rejected:  r.TotalViewCashRejected,
			Completed: r.TotalViewCashCompleted,
			Cashback:  r.TotalViewCashCompleted,
			Transfer:  r.TotalViewCashTransferred,
		},
	}
	s.ViewExceedBudget.Total = s.ViewExceedBudget.Pending +
		s.ViewExceedBudget.Rejected +
		s.ViewExceedBudget.Completed +
		s.ViewExceedBudget.Cashback
	s.Point = s.GetPoint()
	return s
}
```

- [ ] **Step 7: Chạy test để xác nhận pass**

Run: `go test ./internal/service/ -run TestBuildSourceStatistic -v`
Expected: PASS, 8 test

- [ ] **Step 8: Thay mười khối trong UpdateStatisticUserEvent**

Trong `backend/internal/service/event.go`, xoá mười khối dựng `modelmg.UserContentStatistic{...}` cùng mười dòng `X.Point = X.GetPoint()` (từ khoảng dòng 1125 tới 1462), thay bằng mười lời gọi:

```go
	youtube := buildSourceStatistic(contentYoutubeStats, statisticYoutubeView)
	youtubeShort := buildSourceStatistic(contentYoutubeShortStats, statisticYoutubeShortView)
	tiktok := buildSourceStatistic(contentTiktokStats, statisticTiktokView)
	facebook := buildSourceStatistic(contentFacebookStats, statisticFacebookView)
	facebookReel := buildSourceStatistic(contentFacebookReelStats, statisticFacebookReelsView)
	facebookPost := buildSourceStatistic(contentFacebookPostStats, statisticFacebookPostView)
	instagram := buildSourceStatistic(contentInstagramStats, statisticInstagramView)
	instagramReel := buildSourceStatistic(contentInstagramReelStats, statisticInstagramReelsView)
	threads := buildSourceStatistic(contentThreadStats, statisticThreadsView)
	shopeeVideo := buildSourceStatistic(contentShopeeStats, statisticShopeeVideoView)
```

Giữ nguyên tên mười biến kết quả vì literal `statistic` phía dưới đang dùng chúng. Đối chiếu tên biến nguồn với phần khai báo ở đầu hàm quanh dòng 887-910 để ghép đúng cặp.

- [ ] **Step 9: Kiểm tra không sót nguồn nào**

Run: `grep -c "buildSourceStatistic(" internal/service/event.go`
Expected: `10`

Run: `grep -c "modelmg.UserContentStatistic{" internal/service/event.go`
Expected: `0`

- [ ] **Step 10: Build và chạy toàn bộ test**

Run: `go build ./... && go test ./internal/... ./pkg/... -count=1`
Expected: build sạch, test pass

- [ ] **Step 11: Commit**

```bash
git add backend/internal/model/mg/user_event.go \
        backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go \
        backend/internal/service/user_event_source_statistic.go \
        backend/internal/service/user_event_source_statistic_test.go \
        backend/internal/service/event.go
git commit -m "refactor(user-event): gop 10 khoi thong ke theo nguon thanh mot ham va them nhanh vuot ngan sach"
```

---

## Task 9: Trang cá nhân — bảng thống kê ở 14 ứng dụng

Bảng không có package dùng chung. Mười bốn file, bốn biến thể khác nhau ở nhãn cột và bản đồ nguồn. Hàm `getData()` giống hệt nhau ở cả mười bốn bản.

Task này làm luôn hai lỗi có sẵn: nhãn cột trùng nhãn tiền, và ba cột đều sắp xếp theo cùng một giá trị.

**Files:**
- Modify: `frontend/src/pages/home/components/statistic/table.tsx` và bản tương ứng ở `anker`, `mbbank`, `turborg`, `flamingo`, `vnpay`, `yody`, `tpbank`, `vng`, `vpbank`, `wildrift`, `parasola`, `lusso`, `hdbank`
- Modify: interface `userEventStatistic` trong `src/interfaces/` của cả 14 ứng dụng

**Interfaces:**
- Consumes: `userEventStatistic[source].viewExceedBudget` từ Task 8
- Produces: không

- [ ] **Step 1: Liệt kê chính xác 14 file**

Run: `ls -1 */src/pages/home/components/statistic/table.tsx`
Expected: 14 đường dẫn. Ghi lại danh sách, dùng cho các step sau.

- [ ] **Step 2: Thêm field vào interface**

Trong mỗi ứng dụng, tìm interface mô tả thống kê theo nguồn:

Run: `grep -rln "cashback" <app>/src/interfaces/`

Thêm vào cạnh `view`:

```ts
  viewExceedBudget: {
    total: number;
    waiting: number;
    pending: number;
    rejected: number;
    completed: number;
    cashback: number;
    transfer: number;
  };
```

- [ ] **Step 3: Sửa getData trong bản `frontend`**

Trong `frontend/src/pages/home/components/statistic/table.tsx`, trong `getData()`, thay phần dựng mỗi dòng. Giá trị hiện tại của `cashCompleted` và `cashPending` là số lượt xem chứ không phải tiền, đổi tên cho đúng:

```ts
      const stat = userEventStatistic?.[key];
      const view = stat?.view;
      const exceed = stat?.viewExceedBudget;

      const total = view?.completed ?? 0;
      const exceedCashback = exceed?.cashback ?? 0;
      const exceedPending = exceed?.completed ?? 0;

      const rewarded = Math.max((view?.cashback ?? 0) - exceedCashback, 0);
      const notRewarded = exceedCashback + exceedPending;
      const waiting = Math.max(total - rewarded - notRewarded, 0);

      return {
        name,
        view: total,
        viewRewarded: rewarded,
        viewNotRewarded: notRewarded,
        viewWaiting: waiting,
      };
```

Lưu ý `exceed.completed` là lượt xem của phần thưởng đang **chờ đối soát**, không phải content đã duyệt. Đây là quy ước bucket lệch một nấc có sẵn của codebase.

- [ ] **Step 4: Sửa định nghĩa cột trong bản `frontend`**

Thay ba cột sau cột "Nguồn" bằng bốn cột. Sửa luôn sorter cho từng cột và làm rõ nhãn là lượt xem:

```tsx
    {
      title: 'Lượt xem',
      dataIndex: 'view',
      sorter: (a, b) => a.view - b.view,
      render: (value: number) => formatter.numberNew(value),
    },
    {
      title: 'Lượt xem đã đối soát',
      dataIndex: 'viewRewarded',
      sorter: (a, b) => a.viewRewarded - b.viewRewarded,
      render: (value: number) => formatter.numberNew(value),
    },
    {
      title: 'Lượt xem không được tính thưởng',
      dataIndex: 'viewNotRewarded',
      sorter: (a, b) => a.viewNotRewarded - b.viewNotRewarded,
      render: (value: number) => formatter.numberNew(value),
    },
    {
      title: 'Lượt xem chờ đối soát',
      dataIndex: 'viewWaiting',
      sorter: (a, b) => a.viewWaiting - b.viewWaiting,
      render: (value: number) => formatter.numberNew(value),
    },
```

Giữ nguyên các thuộc tính khác của từng cột như `align`, `width`, `className` nếu bản gốc có.

- [ ] **Step 5: Áp cho 13 ứng dụng còn lại**

Áp cùng thay đổi. Ba điểm khác biệt giữa các biến thể, giữ nguyên theo từng bản:

- Bản dùng nhãn tiếng Anh thì đổi tiêu đề thành `Views`, `Settled views`, `Views not rewarded`, `Views pending settlement`.
- Bản có `className="bg-transparent"` thì giữ nguyên thuộc tính đó.
- Bản có thêm `facebook_post` trong bản đồ nguồn thì giữ nguyên bản đồ đó.

- [ ] **Step 6: Kiểm tra kiểu từng ứng dụng**

Run cho mỗi ứng dụng: `cd <app> && npx tsc --noEmit`
Expected: không có lỗi kiểu

- [ ] **Step 7: Kiểm tra không sót bản nào**

Run: `grep -L "viewNotRewarded" */src/pages/home/components/statistic/table.tsx`
Expected: không in ra file nào

- [ ] **Step 8: Commit**

```bash
git add */src/pages/home/components/statistic/table.tsx */src/interfaces/
git commit -m "feat(web): them cot luot xem khong duoc tinh thuong va sua sorter o 14 ung dung"
```

---

## Task 10: Expose ngân sách event và dọn chuỗi placeholder

`BudgetAlert` và nhãn "Ngân sách tối đa" đọc `matchedEvent.bpe`, nhưng response không hề có field này nên hai khối đó **chưa bao giờ hiển thị**. Khi ambassador nhìn thấy cột "không được tính thưởng", banner ngân sách chính là thứ giải thích nguyên nhân.

**Files:**
- Modify: `backend/pkg/public/model/response/event.go:33-66`
- Modify: `backend/pkg/public/service/event.go` (nơi dựng `EventBriefResponse` trong `GetList`)
- Modify: `frontend/src/pages/home/components/budget-alert/index.tsx:44`

**Interfaces:**
- Consumes: `modelmg.EventRaw.Bpe`
- Produces: key `bpe` trong `EventBriefResponse`

- [ ] **Step 1: Xác định hình dạng dữ liệu ngân sách mà giao diện cần**

Run: `sed -n '70,85p' frontend/src/pages/home/components/logged-in-view/index.tsx`
Expected: thấy các field được đọc là `total`, `used`, `remain`, `usedPercent`

Run: `grep -n "BudgetInfo" -A 12 backend/internal/model/mg/event.go`
Expected: thấy struct và hàm `GetTotal()`

- [ ] **Step 2: Thêm field vào response**

Trong `backend/pkg/public/model/response/event.go`, thêm vào `EventBriefResponse` cạnh `Bpc`:

```go
	Bpe *modelmg.BudgetInfo `json:"bpe,omitempty"`
```

Nếu `BudgetInfo` chưa có sẵn `usedPercent` dưới dạng field JSON thì bổ sung một struct response nhỏ trong cùng file, với đúng bốn khoá `total`, `used`, `remain`, `usedPercent`, và tính `usedPercent` khi dựng response.

- [ ] **Step 3: Gán khi dựng response**

Trong `backend/pkg/public/service/event.go`, ở hàm `GetList` nơi dựng từng `EventBriefResponse`, gán `Bpe` từ `event.Bpe`.

- [ ] **Step 4: Build**

Run: `go build ./...`
Expected: build sạch

- [ ] **Step 5: Kiểm tra bằng tay**

Gọi `GET /events` với một event có đặt ngân sách và xác nhận payload có khoá `bpe` với bốn số. Xác nhận banner và nhãn "Ngân sách tối đa" hiển thị trên trang cá nhân.

- [ ] **Step 6: Dọn chuỗi placeholder**

Trong `frontend/src/pages/home/components/budget-alert/index.tsx` quanh dòng 44, `subText` đang lẫn ghi chú nội bộ và sẽ render ra giao diện. Thay bằng câu hoàn chỉnh, ví dụ:

```tsx
subText: 'Ngân sách chiến dịch đã dùng hết. Lượt xem phát sinh thêm sẽ không được tính thưởng.'
```

Áp cho các ứng dụng khác có cùng component nếu chúng cũng chứa chuỗi lỗi.

- [ ] **Step 7: Commit**

```bash
git add backend/pkg/public/model/response/event.go \
        backend/pkg/public/service/event.go \
        frontend/src/pages/home/components/budget-alert/index.tsx
git commit -m "fix(web): expose bpe de canh bao ngan sach hoat dong tro lai"
```

---

## Task 11: Backfill và đối chiếu dữ liệu thật

Trước task này, mọi field mới đều bằng 0 nên giao diện hiển thị y hệt trước thay đổi. Task này làm số bắt đầu đúng.

**Files:** không sửa file nào. Đây là task vận hành và xác minh.

**Interfaces:**
- Consumes: toàn bộ thay đổi từ Task 1 tới Task 10
- Produces: không

- [ ] **Step 1: Xác minh dữ liệu nguồn có tồn tại**

Chạy trên MongoDB, thay `<eventId>` bằng một event đã từng vượt ngân sách:

```js
db.event_reward.aggregate([
  { $match: { event: ObjectId("<eventId>"), type: "by_statistic" } },
  { $group: {
      _id: { status: "$status", exceeded: { $eq: ["$isBudgetExceeded", true] } },
      docs: { $sum: 1 },
      totalView: { $sum: "$statistic.totalView" },
      totalCash: { $sum: "$cash" }
  } }
])
```

Expected: có ít nhất một nhóm `exceeded: true` với `totalView > 0` và `totalCash == 0`.

- [ ] **Step 2: Chạy kỳ đối soát thử trên môi trường staging**

Tạo một kỳ đối soát cho event đó, chuyển sang trạng thái xử lý, rồi kiểm tra bất biến trên các item vừa sinh:

```js
db.reconciliation_item.find({ reconciliation: ObjectId("<recId>"), type: "content" })
  .forEach(function (d) {
    var c = d.content;
    if (c.totalViewPendingRewarded + c.totalViewPendingExceeded !== c.totalViewPending) {
      print("SAI BAT BIEN: " + d._id);
    }
  })
```

Expected: không in ra dòng nào.

- [ ] **Step 3: Đối chiếu view với tiền trên một dòng cụ thể**

Chọn một item có `totalViewPendingExceeded > 0`, lấy `cashPerView` của schema tương ứng, và xác nhận `totalViewPendingRewarded * cashPerView == totalCashPending`.

- [ ] **Step 4: Backfill hai collection analytic**

Chạy job cập nhật analytic theo ngày cho khoảng thời gian cần thiết. Điểm vào: hàm lặp theo ngày `UpdateAnalyticOldEventDaily` cho `event_analytic_daily` và `UpdateUserEventAnalyticDaily` cho `user_event_analytic_daily`. Nếu hệ thống đã có endpoint admin kích hoạt các job này thì dùng endpoint đó thay vì viết script mới.

- [ ] **Step 5: Xác minh analytic đã có field mới**

```js
db.event_analytic_daily.findOne({ "statistic.viewExceedBudget.cashback": { $gt: 0 } })
```

Expected: trả về một document.

- [ ] **Step 6: Đối chiếu menu thống kê admin**

Mở menu thống kê với khoảng ngày đã backfill. Xác nhận với mỗi trạng thái, giá trị hiển thị mới cộng với giá trị "không được tính thưởng" bằng đúng giá trị hiển thị trước khi thay đổi. Ghi lại số cũ trước khi deploy để so.

- [ ] **Step 7: Backfill thống kê user-event nếu cần**

Với event đang chạy thì không cần: hàm cập nhật được gọi realtime sau mỗi lần tính thưởng cộng năm điểm chạy định kỳ. Chỉ chạy tay cho những cặp ambassador-event đã ngừng phát sinh phần thưởng.

Xác minh:

```js
db.user_event.findOne({ "statistic.youtube.viewExceedBudget.cashback": { $gt: 0 } })
```

- [ ] **Step 8: Đối chiếu trang cá nhân**

Mở trang cá nhân của một ambassador thuộc event đã vượt ngân sách. Xác nhận ba cột "đã đối soát", "không được tính thưởng" và "chờ đối soát" cộng lại bằng cột "lượt xem".

- [ ] **Step 9: Hồi quy đường ghi phần thưởng**

Chạy lại luồng tính thưởng trên dữ liệu staging và xác nhận collection `event_reward` không thay đổi. So sánh số document và tổng `cash` trước và sau.

Expected: giống hệt nhau. Không thay đổi nào trong plan này được phép chạm vào đường ghi.

- [ ] **Step 10: Kiểm tra tổng tiền không đổi**

Với cùng một khoảng ngày, xác nhận cả bốn giá trị của nhóm `cash` trong menu thống kê giống hệt trước khi deploy.

---

## Ghi chú triển khai

Thứ tự deploy an toàn: backend trước, khi đó mọi field mới bằng 0 và giao diện hiển thị y hệt hôm nay. Chạy backfill sau. Deploy frontend cuối cùng. Không bước nào cần cửa sổ bảo trì.

Nếu phải quay lui, chỉ cần revert frontend là giao diện trở về trạng thái cũ; các field mới trong database vô hại vì không consumer nào đọc.

## Ngoài phạm vi plan này

Đã rà và xác nhận có lệch nhưng không sửa: file Excel danh sách ambassador theo partner; thẻ tổng lượt xem trên dashboard admin; hai tab thống kê của ambassador ngoài trang cá nhân; số lượt thích và bình luận cũng phồng theo cùng cơ chế; phép đếm số bản ghi phần thưởng phồng gấp đôi nhưng chưa consumer nào đọc.

Chỉ số tương tác trong kỳ đối soát sai theo hai cách độc lập: tử số lấy từ collection content nên không bị chặn theo mốc thời gian của kỳ, mẫu số lấy từ phần thưởng thì bị chặn và còn phồng. Sửa nó là đổi ngữ nghĩa field đang có.

View vượt ngân sách bị khoá vĩnh viễn sau khi kỳ đối soát chạy: mọi bản ghi phần thưởng chờ xử lý đều chuyển sang hoàn tất, kể cả bản ghi vượt ngân sách, nên phép trừ chống trả thưởng trùng coi như chúng đã xong. Nếu event được nạp thêm ngân sách sau đó thì số view kia không có đường nào để được trả. Cần một phiên thiết kế riêng.
