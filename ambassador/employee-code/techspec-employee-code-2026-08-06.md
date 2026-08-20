# Technical Specification: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06 (cập nhật 2026-08-17)
**Author:** Nguyễn Đăng Định
**Version:** 5.1 — đồng bộ với code sau đợt QA
**Status:** Final
**PRD:** [prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md) v5.1
**Repo:** `AT-Core/ambassador`

---

## 1. Tổng quan

Tài liệu này mô tả cách hiện thực hoá PRD v5.1. Thuật ngữ dùng theo mục 0 của PRD.

> **v5.0 — bỏ phân nhóm bằng segment.** Mục 4.6, 5.4, 5.5 và chiều nhóm ở mục 6 đã gỡ; `applyForSegments` không còn trong `EventOpts`; không backfill `partner` cho `user-segments`. Lý do đầy đủ ở FR-006 của PRD.

### Nguyên tắc

**Port luồng T-Fluencers sang Ambassador.** Phần lớn công việc là chuyển code từ `Viewboost-2025/techcombank` sang `AT-Core/ambassador`, không thiết kế lại.

Chỉ viết mới ở hai chỗ:
1. Năm ràng buộc bắt buộc do kiến trúc Ambassador (mục 1.2)
2. Tenant toggle theo partner thay ENV, và đường sửa lại trạng thái nhân viên (FR-010)

### 1.1 Bảng đối chiếu file nguồn ↔ file đích

| Chức năng | T-Fluencers | Ambassador |
|---|---|---|
| Model mã | `internal/model/mg/manage_code.go` | **như nguồn, không thêm field nào** |
| Constants | `internal/constants/staff.go` | `internal/constants/staff_code.go` |
| Admin CRUD mã | `pkg/admin/{router,handler,service}/manage_code.go` | như nguồn |
| Admin UI mã | `admin/src/pages/manage-code/` | như nguồn |
| API xác nhận | `pkg/public/service/user.go` — `ConfirmIsStaff` | như nguồn, **trừ** quy tắc ghi ở mục 4.3 |
| API cờ hiển thị modal | `pkg/public/service/partner.go` — `GetStatusEmployee` | như nguồn, thêm kiểm tra `PartnerOpts` |
| Gate nộp bài | `pkg/public/service/content.go:114-146` | như nguồn |
| Mã theo event | `pkg/public/service/event.go` — `InputCodeJoinEvent` | như nguồn |
| Modal nhập mã | `frontend/src/components/layout/main/header/components/modal-tcb-employee.tsx` | `parasola/src/.../modal-staff-code.tsx` |
| Modal từ chối | `frontend/.../modal-not-employee.tsx` | `parasola/.../modal-not-employee.tsx` |
| Aggregate thống kê | `aggregate_pipeline/creator_analytics.go` — `GetCreatorKPIsByStaffBreakdown` | **viết mới**, nhị phân nhân viên / ngoài |

### 1.2 Năm ràng buộc bắt buộc

| # | Ràng buộc | Vì sao |
|---|---|---|
| 1 | Mã lưu ở `staffCode`, **không** dùng `UserPartnerRaw.Code` | `Code` ở Ambassador là referral code (`migration.go:1109`) |
| 2 | `confirm-is-staff` **không bao giờ ghi** `isJoined`/`joinedAt` | `isJoined` xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi thực sự tham gia (`:491`). T-Fluencers gán cứng `IsJoined: true` — bê sang sẽ làm sai lệch tăng số creator Parasola |
| 3 | Bật/tắt bằng `PartnerOpts`, không dùng ENV | Ambassador có 13 partner |
| 4 | Gate nhân viên đặt **độc lập, trước** `Eligibility().JoinEvent()` | `JoinEvent` (`eligibility.go:216`) thoát sớm nếu đã join, và `CalculateEligibility` (`:64`) fail-open khi `Enabled=false`. Nhét gate vào đó = campaign mở 3 ngày rồi bật `applyForStaff` thì 500 người ngoài đã join vẫn nộp bài được tới hết campaign |
| 5 | `UserSegment.Delete` kiểm `IsAllowPartner` như `Add` | Đang xoá theo `_id` trần nên admin partner A xoá được thành viên nhóm của partner B |

---

## 2. Thay đổi Model

### 2.1 `UserPartnerRaw`

```go
// backend/internal/model/mg/user_partner.go
type UserPartnerRaw struct {
	// ... các trường hiện có, GIỮ NGUYÊN
	// Code vẫn là referral code — KHÔNG dùng cho mã nhân viên

	StatusStaff string `bson:"statusStaff,omitempty" json:"statusStaff,omitempty"`
	StaffCode   string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`
}
```

### 2.2 `ManageCodeRaw` — file mới

```go
// backend/internal/model/mg/manage_code.go
package modelmg

type ManageCodeDAO interface {
	GetShare() databasemongodb.IDatabase
}

type ManageCodeRaw struct {
	ID      AppID  `bson:"_id" json:"_id"`
	Partner AppID  `bson:"partner" json:"partner"`
	Type    string `bson:"type" json:"type"`
	Code    string `bson:"code" json:"code"`

	// IsUsed/UsedBy/UsedAt giữ đúng ngữ nghĩa T-Fluencers: chỉ script migration
	// ghi, luồng người dùng KHÔNG ghi. Một mã dùng được cho nhiều người.
	IsUsed bool      `bson:"isUsed" json:"isUsed"`
	UsedBy AppID     `bson:"usedBy,omitempty" json:"usedBy,omitempty"`
	UsedAt time.Time `bson:"usedAt,omitempty" json:"usedAt,omitempty"`

	CreatedAt time.Time `bson:"createdAt" json:"createdAt"`
	UpdatedAt time.Time `bson:"updatedAt" json:"updatedAt"`
}

func (m *ManageCodeRaw) DbModelName() string {
	return databasemongodb.CollectionManageCode
}
```

### 2.3 `UserEventRaw` — bổ sung `Options`

Ambassador hiện thiếu field này, cần thêm để port `InputCodeJoinEvent`:

```go
// backend/internal/model/mg/user_event.go
type UserEventOpts struct {
	CodeInput      string `bson:"codeInput" json:"codeInput"`
	StatusEmployee string `bson:"statusEmployee" json:"statusEmployee"`
}

type UserEventRaw struct {
	// ... các trường hiện có
	Options *UserEventOpts `bson:"options,omitempty" json:"options,omitempty"`
}
```

### 2.4 `PartnerOpts` và `EventOpts`

```go
// partner.go
type PartnerOpts struct {
	AllowResubmitRejectedContent bool `bson:"allowResubmitRejectedContent,omitempty" json:"allowResubmitRejectedContent"`
	EnableStaffCode              bool `bson:"enableStaffCode,omitempty" json:"enableStaffCode"`
	RequireStaffCodeValidation   bool `bson:"requireStaffCodeValidation,omitempty" json:"requireStaffCodeValidation"`
}

// event.go
type EventOpts struct {
	// ... các trường hiện có
	ApplyForStaff bool     `bson:"applyForStaff,omitempty" json:"applyForStaff"`
	StaffCodes    []string `bson:"staffCodes,omitempty" json:"staffCodes,omitempty"`
}
```

### 2.5 Constants — file mới

```go
// backend/internal/constants/staff_code.go
package constants

const (
	StatusStaffNotVerify   = "not_verify"
	StatusStaffIsEmployee  = "employee"
	StatusStaffNotEmployee = "not_employee"

	ManageCodeApplyForEmployee = "apply_for_employee"
)

// IsStaff là quy tắc canonical DUY NHẤT để phân loại nhân viên.
// Mọi giá trị mơ hồ (rỗng, not_verify) đều KHÔNG tính là nhân viên,
// để số liệu nhân viên không bị sai lệch tăng do dữ liệu không hợp lệ.
// Giữ đồng bộ với parasola/src/utils/staff.ts
func IsStaff(statusStaff string) bool {
	return statusStaff == StatusStaffIsEmployee
}

// NormalizeStaffCode chuẩn hoá mã ở BACKEND, không tin FE.
// T-Fluencers hiển thị mã viết hoa ở FE nhưng gửi nguyên bản, dẫn tới giá trị
// lưu khác giá trị user thấy. Ambassador chuẩn hoá ở đây.
func NormalizeStaffCode(code string) string {
	return strings.ToUpper(strings.TrimSpace(code))
}
```

---

## 3. Database

```go
// module/database/mongodb/collection.go
CollectionManageCode = "manage-codes"
```

`dao/manage_code.go` — copy pattern của `dao/user_segment.go`.

**Index** (`module/database/mongodb/index.go`):
```go
// manage-codes
{
	indexes := []mongo.IndexModel{
		i.newIndex("partner", "code"),   // tra cứu khi xác nhận
		i.newIndex("partner", "isUsed"), // filter danh sách admin
	}
	i.process(db.Collection(CollectionManageCode), indexes)
}

// user partner — thêm vào block đã có
i.newIndex("partner", "statusStaff"),
```

**Migration schema: không cần.** Field mới đều `omitempty`; bản ghi cũ đọc ra `statusStaff = ""` và `IsStaff("")` trả `false` — đúng ngữ nghĩa "chưa xác nhận, tính là người ngoài".

**Nhưng có 1 script dữ liệu phải chạy** (FR-017):

```js
// Đánh dấu user Parasola hiện có là "không phải nhân viên" (FR-017)
//    TRƯỚC khi bật options.enableStaffCode, nếu không toàn bộ creator
//    đang hoạt động sẽ bị modal blocking chặn ở lần vào tiếp theo.
db.getCollection('user-partners').updateMany(
  { partner: <parasolaId>, statusStaff: { $exists: false } },
  { $set: { statusStaff: 'not_employee', updatedAt: new Date() } }
);
```

Việc duy nhất khi release — bật cờ cho Parasola:
```js
db.getCollection('partners').updateOne(
  { slug: 'parasola' },
  { $set: { 'options.enableStaffCode': true, 'options.requireStaffCodeValidation': true } }
)
```

---

## 4. Backend — Public API

### 4.1 `GET /partners/:id/status-employee`

Port `GetStatusEmployee` (`pkg/public/service/partner.go:256`), thêm một bước kiểm tra cờ partner:

```go
func (p partnerImpl) GetStatusEmployee(ctx context.Context, id, userId modelmg.AppID) *response.StatusEmployeeResponse {
	var (
		partner     = new(modelmg.PartnerRaw)
		userPartner = new(modelmg.UserPartnerRaw)
		res         = &response.StatusEmployeeResponse{IsOpenInputStaffCode: true}
	)
	_ = daomongodb.PartnerDAO().GetShare().FindById(ctx, partner, id)
	// KHÁC T-Fluencers: cờ theo partner thay vì ENV toàn cục
	if partner.Options == nil || !partner.Options.EnableStaffCode {
		res.IsOpenInputStaffCode = false
		return res
	}

	_ = daomongodb.UserPartnerDAO().GetShare().FindOne(ctx, userPartner,
		bson.M{"user": userId, "partner": id})
	if userPartner.ID.IsZero() {
		return res
	}
	if userPartner.StatusStaff == constants.StatusStaffIsEmployee ||
		userPartner.StatusStaff == constants.StatusStaffNotEmployee {
		res.IsOpenInputStaffCode = false
	}
	return res
}
```

### 4.2 `POST /users/confirm-is-staff`

Port `ConfirmIsStaff` (`pkg/public/service/user.go:177`). Thay đổi duy nhất: quy tắc ghi ở 4.3.

```go
func (u *userImpl) ConfirmIsStaff(ctx context.Context, userId modelmg.AppID, body request.ConfirmIsStaffBody) error {
	var (
		user    = new(modelmg.UserRaw)
		partner = new(modelmg.PartnerRaw)
		status  = constants.StatusStaffIsEmployee
	)
	if !body.IsStaff {
		status = constants.StatusStaffNotEmployee
	}

	_ = daomongodb.UserDAO().GetShare().FindById(ctx, user, userId)
	if user.ID.IsZero() {
		return errors.New(locale.UserKeyNotFound)
	}
	if user.Banned {
		return errors.New(locale.UserKeyNotActive)
	}

	_ = daomongodb.PartnerDAO().GetShare().FindOne(ctx, partner,
		bson.M{"_id": util.GetAppIDFromHex(body.Partner)})
	if partner.ID.IsZero() {
		return errors.New(locale.PartnerKeyNotFound)
	}
	if partner.Options == nil || !partner.Options.EnableStaffCode {
		return errors.New(locale.StaffCodeKeyFeatureDisabled)
	}

	code := constants.NormalizeStaffCode(body.Code)
	manageCode := new(modelmg.ManageCodeRaw)
	_ = manageCode // chỉ dùng để validate, không lấy nhóm từ đây

	if body.IsStaff {
		if code == "" {
			return errors.New(locale.StaffCodeKeyRequired)
		}
		// KHÁC T-Fluencers: cờ theo partner thay vì ENV
		if partner.Options.RequireStaffCodeValidation {
			_ = daomongodb.ManageCodeDAO().GetShare().FindOne(ctx, manageCode, bson.M{
				"partner": partner.ID,
				"code":    code,
				"type":    constants.ManageCodeApplyForEmployee,
			})
			if manageCode.ID.IsZero() {
				return errors.New(locale.StaffCodeKeyInvalid)
			}
		}
	}

	if err := u.writeStaffStatus(ctx, userId, partner.ID, status, code); err != nil {
		return err
	}

	// v5.0: không còn bước gán nhóm ở đây
	if body.IsStaff {
	}
	return nil
}
```

**Không lọc `isUsed: false`, không ghi `isUsed`** — giữ đúng hành vi T-Fluencers: một mã dùng được cho nhiều người.

### 4.3 `writeStaffStatus` — hàm ghi duy nhất chạm `user-partners`

Đây là chỗ thực thi ràng buộc #2. Mọi thứ khác trong luồng này **không** được `UpdateOne` lên `user-partners`.

```go
// writeStaffStatus upsert trạng thái nhân viên vào user-partners.
//
// CẢNH BÁO: KHÔNG BAO GIỜ ghi isJoined/joinedAt ở đây.
// T-Fluencers tạo bản ghi mới với IsJoined: true, JoinedAt: now
// (pkg/public/service/user.go — ConfirmIsStaff). Ambassador KHÔNG làm vậy:
// isJoined là điều kiện xác định user thuộc partner nào
// (internal/service/user.go:226) và chỉ được set khi user THỰC SỰ tham gia
// (internal/service/user.go:491). Ghi ở đây sẽ khiến người chỉ mới bấm
// "Tôi không thuộc Parasola" bị tính là creator của partner.
//
// Cũng KHÔNG được ghi trường `code` — đó là referral code.
func (u *userImpl) writeStaffStatus(
	ctx context.Context, userId, partnerId modelmg.AppID, status, code string,
) error {
	set := bson.M{"statusStaff": status, "updatedAt": time.Now()}
	if status == constants.StatusStaffIsEmployee {
		set["staffCode"] = code
	}

	opts := options.Update().SetUpsert(true)
	return daomongodb.UserPartnerDAO().GetShare().UpdateOne(ctx,
		new(modelmg.UserPartnerRaw),
		bson.M{"user": userId, "partner": partnerId},
		bson.M{
			"$set": set,
			"$setOnInsert": bson.M{
				"_id":       modelmg.NewAppID(),
				"user":      userId,
				"partner":   partnerId,
				"createdAt": time.Now(),
			},
		}, opts)
}

```

Hàm này là toàn bộ phần ghi của luồng xác nhận — không còn bước gán nhóm nào phía sau (v5.0).

### 4.4 Gate nộp bài

Port `pkg/public/service/content.go:114-146` của T-Fluencers, giữ nguyên thứ tự kiểm tra.

> ⚠️ **Hai điều kiện đặt sai chỗ là hỏng, đọc kỹ:**
>
> **(a) Ambassador chưa có biến `userPartner` trong `content.go`.** T-Fluencers load ở `content.go:105`; Ambassador thì không — grep ra rỗng. Phải tự thêm bước load, nếu không đoạn dưới không compile. Biến `event` thì đã có sẵn (`content.go:95`, `:107`).
>
> **(b) Khối này đặt TRƯỚC lời gọi `Eligibility().JoinEvent()` ở `content.go:123`, không nhét vào trong.** `JoinEvent` thoát sớm khi user đã join (`eligibility.go:216`) và `CalculateEligibility` fail-open khi `Enabled=false` (`:64`) — nhét vào đó là gate mất tác dụng với mọi người đã join trước.

```go
// BƯỚC THÊM: Ambassador chưa có sẵn biến này
userPartner := new(modelmg.UserPartnerRaw)
_ = daomongodb.UserPartnerDAO().GetShare().FindOne(ctx, userPartner,
	bson.M{"user": userId, "partner": event.Partner})

if event.Options != nil {
	// 1. Chỉ dành cho nhân viên
	if event.Options.ApplyForStaff {
		if userPartner.ID.IsZero() || !constants.IsStaff(userPartner.StatusStaff) {
			return errors.New(locale.EventKeyApplyOnlyStaff)
		}
	}
	// 2. Mã riêng của event
	if len(event.Options.StaffCodes) > 0 {
		userEvent := new(modelmg.UserEventRaw)
		_ = daomongodb.UserEventDAO().GetShare().FindOne(ctx, userEvent,
			bson.M{"user": userId, "event": event.ID})
		if userEvent.Options == nil ||
			!funk.Contains(event.Options.StaffCodes, userEvent.Options.CodeInput) {
			return errors.New(locale.EventKeyRequiredCode)
		}
	}
}
```

### 4.5 `POST /events/:id/input-code-join-event`

Port `InputCodeJoinEvent` (`pkg/public/service/event.go:53`) nguyên vẹn. Cần `UserEventOpts` ở mục 2.3.

Cờ `isRequireCode` trên event list (`event.go:515`) và event detail (`event.go:1074`) port theo nguồn.

### 4.6 ~~Segment tự động theo mã nhân viên~~ — GỠ Ở v5.0

Bản 4.x mô tả `CheckUserInSegmentWithStaffCode` trong `internal/service/segment.go`, cùng `SegmentConditions`, `constants/segments.go` và hai field `Type` / `ConditionForAutomatic` trên `SegmentRaw`. Toàn bộ đã gỡ theo FR-006 của PRD v5.0: luồng xác nhận nhân viên chỉ ghi `user-partners`, không đụng `segments` / `user-segments`.

---

## 5. Backend — Admin API

### 5.1 Router

`pkg/admin/router/manage_code.go`, đăng ký trong `router.go` cạnh `segment(adminGroup)`:

```go
func manageCode(e *echo.Group) {
	var (
		a = routeauth.Auth()
		g = e.Group("/manage-codes", a.RequiredLogin, a.IsAdmin)
		h = handler.ManageCode()
		v = routevalidation.ManageCode()
		c = routevalidation.Common()
	)
	g.GET("", h.GetList, v.GetList)
	g.POST("", h.Create, v.Create)
	g.DELETE("/:id", h.Delete, c.ParamID)
	g.POST("/import-excel", h.ImportExcel, v.ImportExcel, echocustom.UploadSingle())
}
```

Mọi handler kiểm tra `s.Staff.IsAllowPartner(partnerID)`.

**`GetList` phân trang trong bộ nhớ, `page` 0-based.** Không dùng được `GetFindOptsUsingPage` vì phải đối soát `isUsed` động với `user-partners` rồi mới lọc, nên phải cắt lát bằng tay sau khi đã lọc:

```go
page := query.Page          // 0-based, ĐÚNG quy ước repo
if page < 0 { page = 0 }
limit := query.Limit
if limit < 1 { limit = 20 } // khớp initState của model FE
start := page * limit
```

Chỗ này rất dễ viết nhầm thành 1-based (`if page < 1 { page = 1 }` rồi `start := (page-1)*limit`). Hậu quả: FE gửi `page=0` bị kẹp lên 1 → `start=0`, `page=1` cũng ra `start=0` — **trang 1 và trang 2 trả cùng dữ liệu**, mọi trang sau lệch một nhịp, và với tổng 62 thì hai bản ghi cuối không bao giờ xem được. Quy ước repo là 0-based: `GetFindOptsUsingPage` dùng `SetSkip(Page * Limit)` và mọi màn admin gửi `page: current - 1`.

### 5.2 Import Excel / CSV

Port của T-Fluencers, mở rộng cho CSV. **File chỉ một cột là mã.**

```go
// pkg/admin/model/request/manage_code.go
type ManageCodeXLSX struct {
	Code string `xlsx:"0" json:"code"`
}
```

**Hai hàm đọc, chọn theo đuôi file.** `readManageCodeRows` phân nhánh `.csv` → `readManageCodeRowsCSV`, còn lại → `readManageCodeRowsXLSX`. Cần cả CSV vì modal cho chọn `.csv` và nút "Tải file mẫu" phát ra đúng một file `.csv`: chỉ dùng `xlsx.OpenFile` thì tải mẫu về rồi nộp lại chính nó cũng báo lỗi, mà thông báo lại chung chung nên không ai đoán ra vì sao. **Không nhận `.xls`** — `tealeg/xlsx` không mở được BIFF cũ.

Hai chi tiết bắt buộc ở nhánh CSV: `reader.FieldsPerRecord = -1` (file thật hay có dòng trống hoặc thừa dấu phẩy ở cuối, để mặc định thì cả file hỏng chỉ vì một dòng lệch cột), và cắt BOM `﻿` ở ô đầu tiên (Excel ghi ra, không cắt thì mã đầu file không bao giờ khớp).

**Cắt đuôi rỗng ngay sau khi đọc**, trước khi vào vòng lặp:

```go
// Chỉ cắt ở ĐUÔI. Dòng trống giữa vùng dữ liệu vẫn phải báo — đó thường là
// Ops xoá nhầm một ô và cần biết mã nào rơi.
func trimTrailingEmptyRows(rows []manageCodeRow) []manageCodeRow {
	end := len(rows)
	for end > 0 {
		last := rows[end-1]
		if last.Err != "" || strings.TrimSpace(last.Code) != "" {
			break
		}
		end--
	}
	return rows[:end]
}
```

Không có bước này thì file 20 mã do Excel xuất ra vẫn cho `Total` vài trăm và bảng lỗi đầy dòng `"Dòng trống"` — Excel coi mọi ô đã từng chạm tới là "có dòng". Lưu ý điều kiện `last.Err != ""`: dòng **đọc hỏng** ở cuối file không phải dòng rỗng, nó có mặt thật và phải được báo.

```
Mỗi dòng (bỏ dòng 0 là header, sau khi đã cắt đuôi rỗng):
  code := NormalizeStaffCode(r.Code)
  total++

  r.Err != ""     → errors[] {row, "", "Không đọc được dòng"}, skipped++
  code == ""      → errors[] {row, "", "Dòng trống"},          skipped++
  seen[code]      → errors[] {row, code, "Trùng trong file"},  skipped++

  existing := findOne({partner, code})
  existing != nil → errors[] {row, code, "Mã đã tồn tại"},     skipped++
  existing == nil → thêm vào danh sách insert

Cuối cùng: InsertMany
```

Không có cột nhóm — v5.0 không phân nhóm (FR-006).

**Sửa một bug của T-Fluencers:** `ImportExcel` bên đó kiểm tra `len(newCodes) == 0` hai lần liên tiếp, nhánh `CommonKeyAllCodesAlreadyExist` là code chết. Ambassador bỏ nhánh thừa.

```go
type ImportResult struct {
	Total    int           `json:"total"`
	Inserted int           `json:"inserted"`
	Skipped  int           `json:"skipped"`
	Errors   []ImportError `json:"errors"` // {row, code, reason}
}
```

### 5.3 `user-partners` — trả thêm field và filter

`pkg/admin/service/user_partner.go`:
- Response bổ sung `statusStaff`, `staffCode`
- Filter `statusStaff` (map thẳng vào `cond`), multi-select nên dùng `$in`

### 5.4–5.5 ~~Segment: `type`, chặn xoá khi đang dùng, nút "Áp dụng lại"~~ — GỠ Ở v5.0

Không còn. Chỉ giữ một sửa đổi trên `user_segment.go`: `Delete` yêu cầu `segmentId`, kiểm `IsAllowPartner` như `Add`, và ràng buộc `segment` vào điều kiện xoá (FR-003 rút gọn).

### 5.6 Sửa lại trạng thái nhân viên (FR-010)

**Gán mã ở đường admin phải validate như luồng public.** `UpdateStaffStatus` ghi `staffCode` nên cũng phải chạy đúng bộ luật của `pkg/public/service/staff_code.go`: đối chiếu `manage-codes` khi `partner.Options.RequireStaffCodeValidation`, và chặn mã đã thuộc tài khoản khác ở **cả hai tầng** (`manage-codes.isUsed/usedBy` và `user-partners.staffCode` của user khác). Tầng thứ hai không phụ thuộc cờ — mã có thể chưa kịp đánh dấu `isUsed`.

**`Reason` bắt buộc và phải ghi audit.** Kiểm trên chuỗi đã TRIM bằng `validation.By`, vì `validation.Required` chỉ bắt chuỗi rỗng nên một dấu cách lách qua được. Ghi vết bằng `internalservice.Audit().CreatePayload/CreateAudits` với `fromStatus`/`toStatus` và `fromStaffCode`/`toStaffCode`. Lỗi ghi audit **không** trả về lỗi cho caller: bản ghi trạng thái đã cập nhật xong.


Không cần endpoint mới cho phía user — `confirm-is-staff` đã cho ghi đè (mục 4.2). Chỉ cần thêm lối vào.

**Phía Parasola** — `parasola/src/pages/account/`, mục "Thông tin nhân viên":

| Trạng thái hiện tại | Hiển thị |
|---|---|
| `not_employee` hoặc rỗng | Ô nhập mã + nút "Xác nhận là nhân viên" → gọi `confirm-is-staff {isStaff: true, code}` |
| `employee` | Hiện mã đã dùng, **không có nút gỡ**, kèm dòng "Cần thay đổi, vui lòng liên hệ hỗ trợ" |

Một chiều `not_employee → employee`, tránh trò bật tắt để lách gate campaign.

**Phía Admin** — `pkg/admin/service/user_partner.go`:

```
PUT /user-partners/:id/staff-status     { statusStaff, reason }
```

- Đổi được sang bất kỳ trạng thái nào
- `reason` **bắt buộc**, độ dài tối thiểu 10 ký tự
- Gỡ nhãn (`employee` → khác) ⇒ xoá luôn `staffCode` đã ghi, tránh để lại dữ liệu mồ côi

UI: nút "Sửa trạng thái nhân viên" trong `admin/src/pages/user-partner/components/modal-edit.tsx`.

---

## 6. Backend — Thống kê nhân viên / ngoài

`aggregate_pipeline/staff_breakdown.go` — file mới, giữ đúng cách tách nhị phân staff/guest của `GetCreatorKPIsByStaffBreakdown` bên T-Fluencers. **Không có chiều nhóm** (FR-006 đã gỡ).

### 6.1 Vì sao không dùng một pipeline `$lookup`

Cách hiển nhiên là `$lookup` `user-partners` vào từng bản ghi analytics. **Không làm vậy**: `user-event-analytic-daily` có **một document cho mỗi user × event × ngày**, lookup theo từng document là lặp lại cùng một phép tra cứu hàng nghìn lần cho cùng một user.

Tập nhân viên của một partner chỉ vài trăm người (NFR-003). Nên: lấy tập nhân viên bằng một truy vấn nhỏ rồi gộp trong Go.

### 6.2 Ba bước

**Bước 1 — tập nhân viên của partner**

```go
// user-partners: {partner, statusStaff: employee} → set[userId]
// Chỉ so sánh qua constants.IsStaff, không so chuỗi trực tiếp.
```

**Bước 2 — số liệu theo user**

Lượt xem và chi phí lấy từ `user-event-analytic-daily`. Tên field theo `EventAnalyticDailyStatistic` của Ambassador (`model/mg/event_analytic_daily.go`) — **không** phải `netView`/`netCash` của T-Fluencers:

```go
func GetStaffKPIsByUser(cond bson.M) []bson.M {
	return []bson.M{
		{"$match": cond}, // {partner, event?, date: {$gte, $lte}}
		{"$group": bson.M{
			"_id":       "$user",
			"totalView": bson.M{"$sum": "$statistic.view.total"},
			"totalCash": bson.M{"$sum": "$statistic.cash.total"},
		}},
	}
}
```

Số bài đếm từ `contents` — collection analytics không giữ số lượng bài:

```go
func GetContentCountByUser(cond bson.M) []bson.M {
	return []bson.M{
		// cond: {partner, event?, createdAt: {$gte, $lte},
		//        status: {"$ne": constants.StatusCancelled}}
		{"$match": cond},
		{"$group": bson.M{"_id": "$user", "totalContent": bson.M{"$sum": 1}}},
	}
}
```

Loại trừ đúng `StatusCancelled` — theo câu chữ PRD FR-013 "không tính bài đã bị huỷ". Bài `rejected` **vẫn được đếm**; nếu nghiệp vụ muốn loại luôn thì sửa PRD trước, không sửa lệch ở đây.

**Bước 3 — gộp trong Go**

```
với mỗi user có số liệu:
    isStaff = staffIds.has(user)
    cộng dồn vào dòng "Nhân viên" nếu isStaff: view, cash, content
    Số người    += 1
    Đã tham gia += 1 nếu totalContent > 0

Tổng — Ngoài = Tổng toàn bộ − Tổng nhân viên   (trừ, không cộng dồn từng loại)
```

### 6.3 Quy tắc trình bày

Giữ quy ước T-Fluencers: `guest = total − staff`, không cộng dồn từng loại. **Hai dòng tổng** dựng từ `StaffStatisticRow`; dưới đó là **bảng chi tiết từng người** (`StaffItemResponse`) gồm creator đã xác nhận là nhân viên và creator đã được gán mã nhưng chưa xác nhận. Ghi chú *"Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo"* in trên màn hình.

Thứ tự cột bảng chi tiết: **Creator** → Mã nhân viên → Trạng thái → Số bài → Lượt xem → Chi phí.

### 6.4 File xuất CSV

Dựng ở FE (`components/staff-statistic-export.ts`), không thêm endpoint — dữ liệu bảng đã nằm sẵn trong model.

**Một bảng phẳng, dòng 1 là tiêu đề.** Không chèn khối ngữ cảnh hay tổng quan lên đầu: chúng đẩy tiêu đề bảng xuống giữa file nên Excel/Sheets không lọc và sắp xếp được nếu chưa xoá tay mấy dòng đầu. Ngữ cảnh nằm ở tên file `thong-ke-nhan-vien-{đối-tác}-{từ}-{đến}.csv`.

```
User ID | Tên Creator | Hashtag | Mã nhân viên | Nhân viên | Số video | Tổng lượt xem | Phí quảng cáo
```

`Hashtag` lấy từ `UserRaw.Hashtag`, cần bổ sung vào `StaffItemResponse` (service đã load sẵn `userMap` nên không phát sinh truy vấn). Giá trị lưu **sẵn cả dấu `#`** — Parasola cho creator copy thẳng chuỗi này dán vào bài, và hàm kiểm nội dung ở `internal/service/content.go` cũng so trực tiếp — nên ghi nguyên, không thêm bớt.

Cột `Nhân viên` ghi nhãn tiếng Việt qua `staffStatusLabel`, dùng chung đúng chữ với màn "Creator theo đối tác" để hai màn không gọi cùng một trạng thái bằng hai tên.

**Hai bẫy CSV bắt buộc xử lý:** BOM `﻿` đầu file (không có thì Excel đọc UTF-8 thành tiếng Việt vỡ) và chèn nháy đơn trước ô chữ mở đầu bằng `=` `+` `-` `@` (Excel/Sheets coi là công thức; số điện thoại `+8498...` sẽ thành `#NAME?`).

> **Đã cân nhắc rồi bỏ:** cột `Tổng lượt thích`. Dữ liệu lấy được từ `$statistic.like.total` ngay trong collection pipeline đang đọc, nhưng giữ nó buộc mọi bản ghi phân tích gánh thêm một phép `$sum` chỉ để phục vụ một cột không ai đọc.

---

## 7. Locale

`internal/locale/staff_code.go` + `properties/{vi,en}/staff_code.properties`.

**Không tái sử dụng** `ReferralKeyCodeInvalid` như T-Fluencers — sai ngữ cảnh.

| Key | VI | EN |
|---|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeKeyCodeAlreadyUsed` | Mã nhân viên này đã được tài khoản khác sử dụng | This employee code is already used by another account |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |
| `manageCodeKeyAlreadyUsed` | Mã đã được sử dụng, không thể xoá | Code already used, cannot delete |
| `manageCodeKeyEmptyFile` | File không có dữ liệu để import | No data to import |
| `eventKeyApplyOnlyStaff` | Chương trình này chỉ áp dụng cho nhân viên của công ty | This program only applies to employees |
| `eventKeyRequiredCode` | Bạn cần nhập mã để tham gia chương trình này | You need a code to join this program |
| `eventKeyStaffCodeInvalid` | Mã tham gia chương trình không hợp lệ | Invalid program code |

---

## 8. Frontend — Admin

| Trang | Nội dung |
|---|---|
| `admin/src/pages/manage-code/` | Port từ T-Fluencers: `index.tsx`, `model.ts`, `type.d.ts`, `components/{filter,table,create-modal,import-modal}.tsx`. `import-modal` hiển thị bảng kết quả liệt kê từng dòng lỗi |
| `admin/src/pages/partner/components/modal.tsx` | 2 toggle `enableStaffCode` / `requireStaffCodeValidation`, dùng `RcSwitchFormNew` như 2 toggle BXH đã có |
| `admin/src/pages/event/components/modal.tsx` | Switch `applyForStaff`; select `mode="tags"` cho `staffCodes` với `tokenSeparators={[',', ' ', '\n']}` và prop `tooltip` (không dùng khối `Alert`) |
| `admin/src/pages/user-partner/` | +2 cột (Nhân viên / Mã nhân viên), +1 filter `statusStaff` |
| `admin/src/pages/event-statistic/` | Khối thống kê nhân viên / ngoài, bảng chi tiết, và `components/staff-statistic-export.ts` dựng CSV |

Thêm menu vào `admin/src/locales/*/menu.ts` và service `admin/src/services/manage-code.ts`.

#### Ba điểm dễ sai ở tầng FE

**`RcFormSelectNew` phải có prop `tooltip` pass-through cho `Form.Item`.** Component dùng chung này vốn không khai `tooltip`. Trước khi thêm, **grep xem nhánh khác đã thêm chưa** — đã từng có hai nhánh cùng bổ sung prop này ở hai vị trí khác nhau trong file, git gộp cả hai mà không báo conflict, và build vỡ ở babel với `Identifier 'tooltip' has already been declared`. Mỗi nhánh đứng riêng đều build được nên chỉ lộ ra sau khi merge.

**Phân trang bảng gom sẵn dữ liệu: khai `pageSize`, đừng khai `showSizeChanger`.** `GetPagination` dùng chung đã mặc định tắt ô đổi số dòng cho toàn bộ bảng của dự án; khai lại `true` là lệch chuẩn chung. Bảng thống kê nhân viên dùng 20 dòng/trang.

**Modal import phải dọn trạng thái theo cả hai chiều.** `importResult` sống trong model nên đóng modal rồi mở lại vẫn thấy báo cáo lần trước; và sau mỗi lần import phải gỡ file khỏi ô chọn để không nộp lại nhầm chính file vừa import.

---

## 9. Frontend — Parasola

**Chỉ làm trong `parasola/`.**

### 9.1 Điểm cắm

`parasola/src/components/layout/main/header/index.tsx` đã có cơ chế này cho màn đồng ý điều khoản (`:82-84`):

```
initApp gọi users/me → user state update
  → useEffect [user] kiểm tra user.privacyAccepted === false
  → hiển thị ModalCompleteRegistration
```

Modal mã nhân viên đi theo đúng cơ chế đó:

```tsx
// Điều khoản có độ ưu tiên cao hơn — không hiển thị chồng 2 modal
useEffect(() => {
  if (!user) return;
  if (user.privacyAccepted === false) return;
  dispatch({ type: 'mainState/checkPartnerEmployeeStatus',
             payload: { partnerId: partnerDetail?._id } });
}, [user]);
```

Effect `checkPartnerEmployeeStatus` gọi `GET /partners/:id/status-employee`; `isOpenInputStaffCode = true` thì bật `visibleModalStaffCode` — port từ `frontend/src/models/main.ts:374`.

### 9.2 `modal-staff-code.tsx`

Port `modal-tcb-employee.tsx`. Giữ nguyên:
- `onClose={() => {}}`, `keyboard={false}`, `hideFooter`, không nút Hủy
- Hai thẻ chọn, **cả hai nhánh đều hiện ô mã**
- `disabled={isStaff === null || !code.trim()}`
- Hai bước: chọn → màn xác nhận (khung cảnh báo, tóm tắt lựa chọn + mã) → Confirm
- Copy: lựa chọn được ghi nhận cố định

**Sửa một lỗi hiển thị của T-Fluencers:** bản gốc `value={employeeCode?.toUpperCase()}` nhưng gửi `code: employeeCode.trim()` — user thấy `ABC123`, DB lưu `abc123`. Ambassador chuẩn hoá khi gõ:

```tsx
const onCodeChange = (v: string) => setCode(v.toUpperCase().trim());
```

Backend vẫn chuẩn hoá lại bằng `NormalizeStaffCode` — không tin FE.

### 9.3 `modal-not-employee.tsx`

Port nguyên. Modal này **đóng được**, 2 nút "Đã hiểu" / "Khám phá thêm".

### 9.4 Model, API, utils

```ts
// parasola/src/configs/api.ts
confirmIsStaff: (): IApi => ({ url: '/users/confirm-is-staff', method: methods.post }),
checkEmployeeStatus: (id: string): IApi => ({ url: `/partners/${id}/status-employee`, method: methods.get }),
inputCodeJoinEvent: (id: string): IApi => ({ url: `/events/${id}/input-code-join-event`, method: methods.post }),
```

`parasola/src/utils/staff.ts` — mirror `constants.IsStaff` kèm comment giữ đồng bộ với Go.

---

## 10. Ánh xạ FR → file

| FR | Backend | Frontend |
|---|---|---|
| FR-001 Trạng thái nhân viên | `model/mg/user_partner.go`, `constants/staff_code.go` | `parasola/src/utils/staff.ts` |
| FR-002 Collection `manage-codes` | `model/mg/manage_code.go`, `mongodb/{collection,index}.go`, `dao/` | — |
| **FR-003 Vá quyền xoá thành viên nhóm** | `pkg/admin/service/user_segment.go` | — |
| FR-004 Admin CRUD mã | `pkg/admin/{router,handler,service}/manage_code.go` | `admin/src/pages/manage-code/` |
| FR-005 Import mã | `pkg/admin/service/manage_code.go` (ImportExcel) | `admin/.../import-modal.tsx` |
| ~~FR-006 Segment tự động~~ | **Gỡ ở v5.0** | — |
| FR-007 API `status-employee` | `pkg/public/{router,handler,service}/partner.go` | `parasola/src/models/main.ts` |
| FR-008 API `confirm-is-staff` | `pkg/public/{router,handler,service}/user.go` | — |
| FR-009 Modal xác nhận | — | `parasola/.../modal-staff-code.tsx`, `header/index.tsx` |
| **FR-010 Sửa lại trạng thái** | `pkg/admin/service/user_partner.go` | `parasola/src/pages/account/`, `admin/.../user-partner/` |
| FR-011 Chiến dịch cho nhân viên | `model/mg/{event,user_event}.go`, `pkg/public/service/{content,event}.go` | `admin/src/pages/event/components/modal.tsx` |
| FR-012 Modal từ chối | — | `parasola/.../modal-not-employee.tsx` |
| FR-013 Tenant toggle | `model/mg/partner.go` | `admin/src/pages/partner/components/modal.tsx` |
| FR-014 Cột + filter admin | `pkg/admin/service/user_partner.go` | `admin/src/pages/user-partner/` |
| FR-015 Thống kê nhân viên / ngoài | `aggregate_pipeline/staff_breakdown.go` | `admin/src/pages/event-statistic/` |
| FR-016 Export | `pkg/admin/service/export_*.go` | — |
| **FR-017 Backfill trước khi bật cờ** | script Mongo (mục 3) | — |

---

## 11. Thứ tự triển khai

Đánh số FR theo PRD v5.0.

**Nhóm 0 — Vá quyền** (độc lập, làm lúc nào cũng được)
1. `UserSegment.Delete` kiểm `IsAllowPartner` như `Add` — **FR-003**

**Nhóm 1 — Nền tảng** (chặn các nhóm sau)
2. Model + constants + collection + index + DAO — **FR-001, FR-002**
3. `PartnerOpts` + toggle admin — **FR-013**
4. Locale (chỉ tiếng Việt)

**Nhóm 2 — Quản lý mã**
5. Admin CRUD `manage-codes`, bắt buộc partner tường minh — **FR-004**
6. Import Excel 1 cột — **FR-005**
7. Trang admin `/manage-code` — **FR-004, FR-005**

~~**Nhóm 3 — Phân nhóm**~~ — gỡ ở v5.0 (FR-006)

**Nhóm 4 — Luồng người dùng**
8. `status-employee` — **FR-007**
9. `confirm-is-staff` + `writeStaffStatus` — **FR-008**
10. Modal Parasola + model + api — **FR-009**
11. Sửa lại trạng thái: mục Hồ sơ (Parasola) + `PUT /user-partners/:id/staff-status` (admin), mục 5.6 — **FR-010**

**Nhóm 5 — Chiến dịch**
12. `EventOpts` + `UserEventOpts` + gate ở `content.go` (**nhớ load `userPartner`, đặt trước `JoinEvent`**) — **FR-011**
13. `input-code-join-event` + cờ `isRequireCode` — **FR-011**
14. Admin event UI — **FR-011**
15. `modal-not-employee` — **FR-012**

**Nhóm 6 — Báo cáo**
16. Cột + filter `user-partner` (filter multi-select) — **FR-014**
17. Aggregate + khối thống kê nhân viên / ngoài — **FR-015**
18. Export — **FR-016**

**Nhóm 7 — Phát hành**
19. Backfill `statusStaff = not_employee` cho user Parasola hiện có — **FR-017**
    **Chạy trước khi bật `enableStaffCode`.** Không làm thì toàn bộ creator đang hoạt động bị modal blocking chặn.

---

## 12. Test plan

### 12.1 Unit test bắt buộc

| Test | Khẳng định |
|---|---|
| `TestWriteStaffStatus_NeverTouchesIsJoined` | Bắt câu update, khẳng định **không** chứa `isJoined`, `joinedAt`, `code` |
| `TestWriteStaffStatus_UpsertCreatesMinimalDoc` | User chưa có bản ghi → tạo mới chỉ với `user`, `partner`, `createdAt`, `statusStaff` |
| `TestConfirmIsStaff_DoesNotWriteIsUsed` | Sau khi xác nhận, `manage-codes` giữ nguyên `isUsed: false` |
| `TestConfirmIsStaff_MultiUserSameCode` | 3 user cùng nhập một mã → cả 3 thành công |
| `TestNormalizeStaffCode` | ` prs_a3f91b2c ` → `PRS_A3F91B2C` |
| `TestIsStaff_AmbiguousIsGuest` | `""`, `"not_verify"`, `"NOT_EMPLOYEE"` đều trả `false` |
| `TestImportExcel_NormalizesAndSkipsExisting` | File 1 cột: mã được TRIM + UPPERCASE; mã đã có bị skip và đếm vào `Skipped`; dòng trống vào `Errors` kèm số dòng |
| `TestContentGate_TwoConditions` | `applyForStaff` và `staffCodes` chặn đúng, độc lập và kết hợp |
| `TestUserSegmentDelete_PartnerIsolation` | Admin partner A xoá thành viên nhóm của partner B → bị từ chối |

### 12.2 Kịch bản tích hợp

1. **Nhân viên** — import mã (file 1 cột) → nhập mã → `statusStaff = employee`
2. **Người ngoài** — chọn "Tôi không thuộc Parasola" + nhập mã → `not_employee`, **không** xuất hiện trong danh sách creator của partner (kiểm tra `isJoined` không bị set)
3. **Mã dùng chung** — 3 người cùng nhập một mã, cả 3 thành công, `manage-codes.isUsed` vẫn `false`
4. **Modal blocking** — không đóng được bằng X, ESC, click ngoài; phải chọn mới qua
5. **Gate `applyForStaff`** — người ngoài vào event chỉ-nhân-viên → modal từ chối
6. **Gate `staffCodes`** — chưa nhập mã event → chặn; nhập đúng → qua
7. **Thống kê** — nhân viên + ngoài = tổng hệ thống
8. **Cách ly partner** — bật cho Parasola, 12 partner khác không thấy modal, API từ chối

### 12.3 Kiểm tra trước khi merge

```bash
# 12 folder partner còn lại KHÔNG được có thay đổi nào
git diff --name-only develop... -- anker/ flamingo/ hdbank/ lusso/ mbbank/ \
  tpbank/ turborg/ vng/ vnpay/ vpbank/ wildrift/ yody/ frontend/
# → phải rỗng

# Không so sánh statusStaff trực tiếp ngoài constants
grep -rn '"employee"' backend/ --include="*.go" | grep -v constants/staff_code.go
# → chỉ được xuất hiện trong aggregate pipeline (có comment giải thích)
```

---

## 13. Rollout

1. Deploy backend + admin (cờ mặc định `false` → không ai thấy gì)
2. Ops import mã cho Parasola, kiểm tra danh sách trên `/manage-code`
3. Deploy `parasola/`
4. Bật `enableStaffCode` + `requireStaffCodeValidation` cho riêng Parasola
5. Theo dõi 48 giờ

**Rollback:** tắt `options.enableStaffCode` của Parasola. Modal biến mất, API từ chối, dữ liệu đã có giữ nguyên. Không cần rollback code.

**Theo dõi sau release:**

| Chỉ số | Ngưỡng cảnh báo |
|---|---|
| Tỉ lệ nhập mã thất bại | > 30% → mã phát sai hoặc file import thiếu |
| Số creator mới của Parasola | tăng bất thường → **nghi `isJoined` bị ghi nhầm** |

---

## 14. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Ghi nhầm `isJoined` → sai lệch tăng số creator | **Cao** | Một hàm ghi duy nhất có comment cảnh báo + unit test bắt câu update + theo dõi số creator sau release |
| Mã lộ ra ngoài Parasola | Trung bình | Chấp nhận theo mô hình T-Fluencers (mã dùng chung). Xử lý khi xảy ra: xoá mã, phát mã mới |
| Ops import thiếu mã | Trung bình | Nhân viên dùng mã thiếu sẽ bị báo "Mã nhân viên không hợp lệ"; import bổ sung là xong, không phải làm lại từ đầu |
| Rò rỉ sang partner khác | Thấp | Cờ mặc định `false` + kiểm tra diff trước merge + kịch bản test 9 |
| Import sai file | Thấp | Đọc theo tên cột + báo cáo từng dòng lỗi; mã chưa dùng xoá được từ admin |

---

## 15. Câu hỏi cần chốt trước khi code

_(Không còn.)_

Việc cần trước khi Ops cấu hình: Parasola gửi danh sách mã nhân viên. Đây là thao tác vận hành, không ảnh hưởng thiết kế.

---

## 16. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| **5.1** | 2026-08-17 | **Đồng bộ với code sau đợt QA.**<br>**5.1:** `GetList` phân trang trong bộ nhớ, chốt `page` 0-based và `limit` mặc định 20, kèm mô tả hậu quả khi viết nhầm 1-based.<br>**5.2:** đổi tên mục thành Import Excel/CSV — hai hàm đọc theo đuôi file, `FieldsPerRecord = -1`, cắt BOM, thêm `trimTrailingEmptyRows` và bảng bốn loại `reason`.<br>**6.3:** bổ sung bảng chi tiết từng người và thứ tự cột Creator đứng đầu.<br>**6.4 (mới):** đặc tả file xuất CSV — bảng phẳng 8 cột, nguồn `Hashtag`, nhãn trạng thái tiếng Việt, hai bẫy BOM và ô mở đầu bằng `=+-@`; ghi lại lý do bỏ `Tổng lượt thích`.<br>**7:** thêm key `staffCodeKeyCodeAlreadyUsed`.<br>**8:** ghi ba điểm dễ sai ở FE — `tooltip` pass-through cho `RcFormSelectNew` (đã có lần hai nhánh cùng thêm gây vỡ build), không khai lại `showSizeChanger`, dọn trạng thái modal import hai chiều |
| **5.0** | 2026-08-14 | Nguyễn Đăng Định | Đồng bộ PRD v5.0 — **bỏ phân nhóm bằng segment**. Gỡ mục 4.6 (`CheckUserInSegmentWithStaffCode`, `SegmentConditions`, `constants/segments.go`), mục 5.4–5.5 (`type`/`applyType`, chặn xoá segment đang dùng, `ResyncStaffSegment`). `EventOpts` còn `applyForStaff` + `staffCodes`; gate ở 4.4 còn hai điều kiện. Mục 3 bỏ script backfill `partner` cho `user-segments`. Mục 6 viết lại theo nhị phân nhân viên / ngoài, còn ba bước. Ràng buộc #5 đổi từ "mọi query kèm partner" thành "vá quyền `UserSegment.Delete`". Mục 7 bỏ 2 key locale, mục 8/10/11/12 bỏ hạng mục segment |
| **4.1** | 2026-08-10 | Nguyễn Đăng Định | Soát chéo với PRD v4.0 và bịt 3 lỗ. **Mục 11 (thứ tự triển khai) toàn bộ đang dùng đánh số FR cũ**, lệch một bậc từ FR-003 — dev đọc sẽ làm nhầm việc; viết lại theo đúng 17 FR, bổ sung FR-010 và FR-017 vốn bị bỏ sót. **Thêm mục 5.5** — hàm `ResyncStaffSegment` cho nút "Áp dụng lại" (FR-006): revision v4.0 ghi là đã bổ sung nhưng thực tế chưa có dòng nào. **Thêm mục 5.6** — sửa lại trạng thái nhân viên (FR-010): trước đó chỉ có tên trong bảng ánh xạ, không có hướng dẫn triển khai |
| **4.0** | 2026-08-07 | Nguyễn Đăng Định | Đồng bộ PRD v4.0. **Sửa lỗi code không compile ở mục 4.4:** `content.go` của Ambassador chưa load `userPartner` (khác T-Fluencers có ở `content.go:105`) — phải thêm bước `UserPartnerDAO().FindOne` trước khối gate. Bổ sung hàm "Áp dụng lại" segment. Đánh số FR lại theo PRD (FR-002b → FR-003, backfill → FR-017) |
| **3.2** | 2026-08-07 | Nguyễn Đăng Định | Đồng bộ PRD v3.2. Thêm ràng buộc #4 (gate đặt độc lập trước `JoinEvent`) và #5 (mọi query `user-segments` kèm `partner`). Thêm Nhóm 0 tiền đề (FR-002b) vào thứ tự triển khai và Nhóm 5 phát hành (backfill FR-015) |
| **3.1** | 2026-08-06 | Nguyễn Đăng Định | Soát với code Ambassador theo PRD v3.1. **Mục 6 viết lại:** pipeline cũ dùng `netContent`/`netView`/`netCash` — không tồn tại trong repo (thật ra là `statistic.view.total` / `statistic.cash.total` của `EventAnalyticDailyStatistic`), không nêu collection nguồn, `$lookup` không lọc segment nhân viên và `$arrayElemAt[...,0]` gán bừa một nhóm. Thay bằng 4 bước: tập nhân viên → bản đồ nhóm → số liệu → gộp trong Go; số bài đếm từ `contents`. **Mục 5.4 mới:** chặn xoá segment đang được event tham chiếu. **Mục 10, 11: đánh số lại FR** cho khớp PRD (bản cũ lệch một bậc từ FR-006 và lặp FR-005). Dọn tàn dư bản 1.x: bỏ `upsertUserSegment` không ai gọi, bỏ key locale `manageCodeKeyMissingCodeColumn` và test đọc-theo-tên-cột (import chỉ 1 cột), sửa kịch bản "import kèm nhóm", đổi ngưỡng theo dõi sau release |
| 3.0 | 2026-08-06 | Nguyễn Đăng Định | **Bản chốt theo PRD v3.0.** Phân nhóm chuyển sang segment tự động port từ T-Fluencers (mục 4.6, `applyType: staff_code`); `manage-codes` trở về đúng cấu trúc nguồn, import file 1 cột. Status: Final |
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | Viết lại theo PRD v2.0 — bám T-Fluencers. Bỏ transaction, claim atomic, rate limit middleware, audit trail, cron đối soát, dry-run, xoá theo lô. Thêm bảng đối chiếu file nguồn ↔ file đích để port |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ theo mục 0 của PRD |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Đổi từ bù trừ sang Mongo transaction, bỏ job cron |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | Tech spec đầu tiên |
