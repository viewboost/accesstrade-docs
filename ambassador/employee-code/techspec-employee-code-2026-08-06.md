# Technical Specification: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 3.2 — bản chốt
**Status:** Final
**PRD:** [prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md) v3.2
**Repo:** `AT-Core/ambassador`

---

## 1. Tổng quan

Tài liệu này mô tả cách hiện thực hoá PRD v3.2. Thuật ngữ dùng theo mục 0 của PRD.

### Nguyên tắc

**Port luồng T-Fluencers sang Ambassador.** Phần lớn công việc là chuyển code từ `Viewboost-2025/techcombank` sang `AT-Core/ambassador`, không thiết kế lại.

Chỉ viết mới ở hai chỗ:
1. Năm ràng buộc bắt buộc do kiến trúc Ambassador (mục 1.2)
2. `applyType: staff_code` cho segment tự động (T-Fluencers chỉ có `referral_code`) + thống kê theo nhóm

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
| Segment tự động | `internal/model/mg/segment.go` (`Type`, `ConditionForAutomatic`) + `internal/service/segment.go` (`CheckUserInSegmentWithReferralCode`) | port nguyên, **thêm** `applyType: staff_code` |
| Aggregate thống kê | `aggregate_pipeline/creator_analytics.go` — `GetCreatorKPIsByStaffBreakdown` | **viết mới**, thêm chiều nhóm |

### 1.2 Năm ràng buộc bắt buộc

| # | Ràng buộc | Vì sao |
|---|---|---|
| 1 | Mã lưu ở `staffCode`, **không** dùng `UserPartnerRaw.Code` | `Code` ở Ambassador là referral code (`migration.go:1109`) |
| 2 | `confirm-is-staff` **không bao giờ ghi** `isJoined`/`joinedAt` | `isJoined` xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi thực sự tham gia (`:491`). T-Fluencers gán cứng `IsJoined: true` — bê sang sẽ làm sai lệch tăng số creator Parasola |
| 3 | Bật/tắt bằng `PartnerOpts`, không dùng ENV | Ambassador có 13 partner |
| 4 | Gate nhân viên đặt **độc lập, trước** `Eligibility().JoinEvent()` | `JoinEvent` (`eligibility.go:216`) thoát sớm nếu đã join, và `CalculateEligibility` (`:64`) fail-open khi `Enabled=false`. Nhét gate vào đó = campaign mở 3 ngày rồi bật `applyForStaff` thì 500 người ngoài đã join vẫn nộp bài được tới hết campaign |
| 5 | Mọi truy vấn `user-segments` kèm `partner` | Bảng thiếu tenant discriminator; thống kê sẽ gán nhầm nhóm và lộ tên nhóm partner khác |

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
	ApplyForStaff            bool              `bson:"applyForStaff,omitempty" json:"applyForStaff"`
	StaffCodes               []string          `bson:"staffCodes,omitempty" json:"staffCodes,omitempty"`
	ApplyForSegments         []AppID           `bson:"applyForSegments,omitempty" json:"-"`
	ApplyForSegmentsResponse []IDAndNameString `bson:"applyForSegmentsResponse,omitempty" json:"applyForSegmentsResponse,omitempty"`
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

**Nhưng có 2 script dữ liệu phải chạy** (FR-002b và FR-015):

```js
// 1. Backfill partner cho user-segments (FR-002b) — TRƯỚC khi làm FR-005/FR-013
db.getCollection('user-segments').find({ partner: { $exists: false } }).forEach(function (us) {
  var seg = db.getCollection('segments').findOne({ _id: us.segment });
  if (seg && seg.partner) {
    db.getCollection('user-segments').updateOne({ _id: us._id }, { $set: { partner: seg.partner } });
  }
});

// 2. Đánh dấu user Parasola hiện có là "không phải nhân viên" (FR-015)
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

Port `ConfirmIsStaff` (`pkg/public/service/user.go:177`). Hai thay đổi: quy tắc ghi ở 4.3, và bước gán segment ở cuối.

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

	// Gán segment tự động — port cơ chế T-Fluencers (mục 4.6)
	if body.IsStaff {
		_ = internalservice.Segment{}.CheckUserInSegmentWithStaffCode(ctx, userId, partner.ID, code)
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

Việc gán segment **không** làm ở đây — nằm trọn trong `CheckUserInSegmentWithStaffCode` (mục 4.6), đúng khuôn T-Fluencers.

### 4.4 Gate nộp bài

Port `pkg/public/service/content.go:114-146`, giữ nguyên thứ tự kiểm tra:

```go
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
	// 3. Giới hạn theo nhóm
	if len(event.Options.ApplyForSegments) > 0 {
		total := daomongodb.UserSegmentDAO().GetShare().CountByCondition(ctx,
			new(modelmg.UserSegmentRaw),
			bson.M{"user": userId, "segment": bson.M{"$in": event.Options.ApplyForSegments}})
		if total == 0 {
			return errors.New(locale.EventKeyNotApplySegment)
		}
	}
}
```

### 4.5 `POST /events/:id/input-code-join-event`

Port `InputCodeJoinEvent` (`pkg/public/service/event.go:53`) nguyên vẹn. Cần `UserEventOpts` ở mục 2.3.

Cờ `isRequireCode` trên event list (`event.go:515`) và event detail (`event.go:1074`) port theo nguồn.

### 4.6 Segment tự động theo mã nhân viên

Port cơ chế sẵn có của T-Fluencers, thêm một `applyType`.

**Model** — `internal/model/mg/segment.go`, Ambassador hiện chưa có 2 field này:

```go
type SegmentRaw struct {
	// ... các trường hiện có
	Type                  string             `bson:"type" json:"type"` // manual | automatic
	ConditionForAutomatic *SegmentConditions `bson:"conditionForAutomatic,omitempty" json:"conditionForAutomatic,omitempty"`
}

type SegmentConditions struct {
	ApplyType     string   `bson:"applyType" json:"applyType"`
	ReferralCodes []string `bson:"referralCodes,omitempty" json:"referralCodes,omitempty"`
	StaffCodes    []string `bson:"staffCodes,omitempty" json:"staffCodes,omitempty"` // THÊM MỚI
}
```

`internal/model/mg/user_segment.go` — bổ sung `Note string` (T-Fluencers có, Ambassador chưa).

**Constants** — `internal/constants/segments.go`:
```go
const (
	SegmentTypeManual    = "manual"
	SegmentTypeAutomatic = "automatic"
)
const (
	SegmentApplyTypeReferralCode = "referral_code" // như T-Fluencers
	SegmentApplyTypeStaffCode    = "staff_code"    // THÊM MỚI
)
```

**Service** — `internal/service/segment.go`, viết theo đúng khuôn `CheckUserInSegmentWithReferralCode`:

```go
// CheckUserInSegmentWithStaffCode thêm user vào mọi segment tự động có cấu hình
// mã nhân viên này. Khuôn giống hệt CheckUserInSegmentWithReferralCode của
// T-Fluencers, chỉ khác applyType và trường chứa danh sách mã.
func (s Segment) CheckUserInSegmentWithStaffCode(
	ctx context.Context, userID, partnerID modelmg.AppID, staffCode string,
) error {
	data := make([]*modelmg.SegmentRaw, 0)
	_ = daomongodb.SegmentDAO().GetShare().Find(ctx, new(modelmg.SegmentRaw), bson.M{
		"type":                             constants.SegmentTypeAutomatic,
		"conditionForAutomatic.applyType":  constants.SegmentApplyTypeStaffCode,
		"conditionForAutomatic.staffCodes": staffCode,
		"partner":                          partnerID, // chỉ segment của partner này
	})(&data)
	if len(data) == 0 {
		return nil
	}

	payloads := make([]interface{}, 0)
	for _, segment := range data {
		userSegment := new(modelmg.UserSegmentRaw)
		_ = daomongodb.UserSegmentDAO().GetShare().FindOne(ctx, userSegment,
			bson.M{"user": userID, "segment": segment.ID})
		if userSegment.ID.IsZero() { // idempotent
			payloads = append(payloads, &modelmg.UserSegmentRaw{
				ID:        modelmg.NewAppID(),
				User:      userID,
				Segment:   segment.ID,
				Note:      "Automatic add to segment by staff code",
				CreatedAt: time.Now(),
				CreatedBy: userID,
			})
		}
	}
	if len(payloads) > 0 {
		_ = daomongodb.UserSegmentDAO().GetShare().InsertMany(ctx,
			new(modelmg.UserSegmentRaw), payloads)
	}
	return nil
}
```

Khác nguồn một điểm: lọc thêm `partner` để mã của partner này không kéo user vào segment của partner khác. T-Fluencers một partner nên không cần.

**Index:** `{type: 1, "conditionForAutomatic.applyType": 1, "conditionForAutomatic.staffCodes": 1}`

**Tương thích ngược:** segment hiện có của Ambassador không có `type` → truy vấn `type: "automatic"` không khớp → hành vi cũ giữ nguyên. Khi hiển thị, `type` rỗng coi như `manual`.

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

### 5.2 Import Excel

Port nguyên của T-Fluencers. **File chỉ một cột là mã.**

```go
// pkg/admin/model/request/manage_code.go
type ManageCodeXLSX struct {
	Code string `xlsx:"0" json:"code"`
}
```

```
Mỗi dòng (bỏ dòng 0 là header):
  code := NormalizeStaffCode(readStruct.Code)
  rỗng → ghi vào errors[], sang dòng kế

  existing := findOne({partner, code})
  existing != nil → skipped++
  existing == nil → thêm vào danh sách insert

Cuối cùng: InsertMany
```

Không có cột nhóm. Phân nhóm làm ở mục 4.6 bằng segment tự động, đúng cách T-Fluencers làm với mã giới thiệu.

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
- Response bổ sung `statusStaff`, `staffCode`, `segments[]` (lookup từ `user-segments`)
- Filter `statusStaff` (map thẳng vào `cond`), `segments` (`$in` qua `user-segments`)

### 5.4 Segment — hỗ trợ `type` và chặn xoá khi đang được dùng

`pkg/admin/service/segment.go`:
- Create/Update nhận thêm `type` và `conditionForAutomatic{applyType, staffCodes}`
- **Delete**: từ chối nếu segment còn được `events.options.applyForSegments` tham chiếu (NFR-002)

```go
total := daomongodb.EventDAO().GetShare().CountByCondition(ctx, new(modelmg.EventRaw),
    bson.M{"options.applyForSegments": segmentId})
if total > 0 {
    return errors.New(locale.SegmentKeyInUseByEvent)
}
```

Bỏ qua bước này thì event trỏ tới segment đã xoá → điều kiện `applyForSegments` không khớp ai, chiến dịch âm thầm chặn toàn bộ người tham gia.

---

## 6. Backend — Thống kê theo nhóm

`aggregate_pipeline/staff_breakdown.go` — file mới. T-Fluencers có `GetCreatorKPIsByStaffBreakdown` nhưng chỉ tách nhị phân staff/guest; bản này thêm chiều nhóm.

### 6.1 Vì sao không dùng một pipeline `$lookup`

Cách hiển nhiên là `$lookup` `user-partners` và `user-segments` vào từng bản ghi analytics. **Không làm vậy**, vì hai lý do:

1. `user-event-analytic-daily` có **một document cho mỗi user × event × ngày** — lookup theo từng document là lặp lại cùng một phép tra cứu hàng nghìn lần cho cùng một user.
2. `$lookup` `user-segments` không lọc được đúng "nhóm nhân viên" nếu chỉ join theo `user`: user còn nằm trong segment thủ công và segment `referral_code` cho mục đích khác. Lấy `$arrayElemAt [..., 0]` sẽ gán bừa một segment bất kỳ.

Tập nhân viên của một partner chỉ vài trăm người (NFR-003). Nên: lấy tập nhân viên và bản đồ nhóm bằng hai truy vấn nhỏ, gộp trong Go.

### 6.2 Bốn bước

**Bước 1 — tập nhân viên của partner**

```go
// user-partners: {partner, statusStaff: employee} → set[userId]
// Chỉ so sánh qua constants.IsStaff, không so chuỗi trực tiếp.
```

**Bước 2 — bản đồ user → nhóm**

```go
// a. segments nhân viên của partner (thường vài chục bản ghi)
bson.M{
    "partner":                         partnerId,
    "type":                            constants.SegmentTypeAutomatic,
    "conditionForAutomatic.applyType": constants.SegmentApplyTypeStaffCode,
}
// → []{segmentId, name}

// b. user-segments của đúng các segment đó, chỉ trong tập nhân viên
[]bson.M{
    {"$match": bson.M{
        "user":    bson.M{"$in": staffIds},
        "segment": bson.M{"$in": staffSegmentIds},
    }},
    {"$group": bson.M{"_id": "$user", "segments": bson.M{"$addToSet": "$segment"}}},
}
```

Quy tắc gán nhóm — theo PRD FR-013:

| Số segment nhân viên user thuộc | Xếp vào |
|---|---|
| 0 | `Chưa phân nhóm` |
| 1 | segment đó |
| ≥ 2 | `Thuộc nhiều nhóm` |

Mỗi user rơi vào **đúng một** dòng ⇒ tổng các dòng con luôn bằng dòng tổng "Nhân viên".

**Bước 3 — số liệu theo user**

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

**Bước 4 — gộp trong Go**

```
với mỗi user có số liệu:
    isStaff  = staffIds.has(user)
    groupKey = isStaff ? groupOf(user) : "guest"
    cộng dồn vào dòng groupKey: view, cash, content
    Số người   += 1
    Đã tham gia += 1 nếu totalContent > 0

Tổng — Nhân viên = cộng các dòng nhóm
Tổng — Ngoài     = Tổng toàn bộ − Tổng nhân viên   (không cộng dồn từng loại)
```

### 6.3 Quy tắc trình bày

Giữ quy ước T-Fluencers: `guest = total − staff`, không cộng dồn từng loại. Thêm hai dòng riêng `Thuộc nhiều nhóm` và `Chưa phân nhóm`. Mọi bảng và file export in ghi chú *"Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo."*

---

## 7. Locale

`internal/locale/staff_code.go` + `properties/{vi,en}/staff_code.properties`.

**Không tái sử dụng** `ReferralKeyCodeInvalid` như T-Fluencers — sai ngữ cảnh.

| Key | VI | EN |
|---|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |
| `manageCodeKeyAlreadyUsed` | Mã đã được sử dụng, không thể xoá | Code already used, cannot delete |
| `manageCodeKeyEmptyFile` | File không có dữ liệu để import | No data to import |
| `segmentKeyInUseByEvent` | Nhóm đang được chiến dịch sử dụng, không thể xoá | Segment is in use by an event |
| `eventKeyApplyOnlyStaff` | Chương trình này chỉ áp dụng cho nhân viên của công ty | This program only applies to employees |
| `eventKeyRequiredCode` | Bạn cần nhập mã để tham gia chương trình này | You need a code to join this program |
| `eventKeyStaffCodeInvalid` | Mã tham gia chương trình không hợp lệ | Invalid program code |
| `eventKeyNotApplySegment` | Bạn không đủ điều kiện tham gia chương trình này | You are not eligible for this program |

---

## 8. Frontend — Admin

| Trang | Nội dung |
|---|---|
| `admin/src/pages/manage-code/` | Port từ T-Fluencers: `index.tsx`, `model.ts`, `type.d.ts`, `components/{filter,table,create-modal,import-modal}.tsx`. `import-modal` hiển thị bảng kết quả liệt kê từng dòng lỗi |
| `admin/src/pages/segment/components/modal.tsx` | +select `type` (manual/automatic), +select `applyType`, +ô nhập danh sách mã `mode="tags"` — port từ T-Fluencers |
| `admin/src/pages/partner/components/modal.tsx` | 2 toggle `enableStaffCode` / `requireStaffCodeValidation`, dùng `RcSwitchFormNew` như 2 toggle BXH đã có |
| `admin/src/pages/event/components/modal.tsx` | Switch `applyForStaff`; select `mode="tags"` cho `staffCodes` với `tokenSeparators={[',', ' ', '\n']}`; select nhiều `applyForSegments` — port nguyên từ T-Fluencers |
| `admin/src/pages/user-partner/` | +3 cột (Nhân viên / Mã nhân viên / Nhóm), +2 filter |
| `admin/src/pages/event-statistic/` | Tab thống kê theo nhóm |

Thêm menu vào `admin/src/locales/*/menu.ts` và service `admin/src/services/manage-code.ts`.

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
| FR-003 Admin CRUD mã | `pkg/admin/{router,handler,service}/manage_code.go` | `admin/src/pages/manage-code/` |
| FR-004 Import mã | `pkg/admin/service/manage_code.go` (ImportExcel) | `admin/.../import-modal.tsx` |
| FR-005 Segment tự động | `model/mg/{segment,user_segment}.go`, `constants/segments.go`, `internal/service/segment.go`, `pkg/admin/service/segment.go` | `admin/src/pages/segment/components/modal.tsx` |
| FR-006 API `status-employee` | `pkg/public/{router,handler,service}/partner.go` | `parasola/src/models/main.ts` |
| FR-007 API `confirm-is-staff` | `pkg/public/{router,handler,service}/user.go` | — |
| FR-008 Modal xác nhận | — | `parasola/.../modal-staff-code.tsx`, `header/index.tsx` |
| FR-009 Chiến dịch cho nhân viên | `model/mg/{event,user_event}.go`, `pkg/public/service/{content,event}.go` | `admin/src/pages/event/components/modal.tsx` |
| FR-010 Modal từ chối | — | `parasola/.../modal-not-employee.tsx` |
| FR-011 Tenant toggle | `model/mg/partner.go` | `admin/src/pages/partner/components/modal.tsx` |
| FR-012 Cột + filter admin | `pkg/admin/service/user_partner.go` | `admin/src/pages/user-partner/` |
| FR-013 Thống kê theo nhóm | `aggregate_pipeline/staff_breakdown.go` | `admin/src/pages/event-statistic/` |
| FR-014 Export | `pkg/admin/service/export_*.go` | — |

---

## 11. Thứ tự triển khai

**Nhóm 0 — Tiền đề** (chặn Nhóm 2b và Nhóm 4)
0. **`user-segments` thêm `partner` + `note`, backfill từ `segments.partner`, `Delete` kiểm `IsAllowPartner` (FR-002b)** — làm trước, sửa sau thì FR-005 và FR-013 phải viết lại

**Nhóm 1 — Nền tảng** (chặn các nhóm sau)
1. Model + constants + collection + index + DAO (FR-001, FR-002)
2. `PartnerOpts` + toggle admin (FR-011)
3. Locale

**Nhóm 2 — Quản lý mã**
4. Admin CRUD `manage-codes` (FR-003)
5. Import Excel (FR-004)
6. Trang admin `/manage-code` (FR-003, FR-004)

**Nhóm 3 — Phân nhóm** (chặn nhóm 6)
7. `SegmentRaw.Type` + `ConditionForAutomatic` + `UserSegmentRaw.Note` (FR-005)
8. `CheckUserInSegmentWithStaffCode` + chặn xoá segment đang dùng (FR-005)
9. Admin UI segment: `type`, `applyType`, danh sách mã (FR-005)

**Nhóm 4 — Luồng người dùng**
10. `status-employee` (FR-006)
11. `confirm-is-staff` + `writeStaffStatus` (FR-007)
12. Modal Parasola + model + api (FR-008)

**Nhóm 5 — Chiến dịch**
13. `EventOpts` + `UserEventOpts` + gate ở `content.go` (FR-009)
14. `input-code-join-event` + cờ `isRequireCode` (FR-009)
15. Admin event UI (FR-009)
16. `modal-not-employee` (FR-010)

**Nhóm 6 — Báo cáo**
17. Cột + filter `user-partner` (FR-012)
18. Aggregate + tab thống kê (FR-013)
19. Export (FR-014)

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
| `TestUpsertUserSegment_Idempotent` | Gọi 3 lần → chỉ 1 bản ghi `user-segments` |
| `TestImportExcel_NormalizesAndSkipsExisting` | File 1 cột: mã được TRIM + UPPERCASE; mã đã có bị skip và đếm vào `Skipped`; dòng trống vào `Errors` kèm số dòng |
| `TestCheckUserInSegmentWithStaffCode` | Mã thuộc 2 segment → user vào cả 2; gọi lại lần nữa không tạo bản ghi trùng |
| `TestSegmentAutomatic_PartnerIsolation` | Mã của partner A không kéo user vào segment của partner B |
| `TestSegmentWithoutType_BehavesAsManual` | Segment cũ không có `type` → không bị gán tự động |
| `TestSegmentDelete_BlockedWhenEventReferences` | Segment còn trong `events.options.applyForSegments` → xoá bị từ chối |
| `TestContentGate_ThreeConditions` | `applyForStaff`, `staffCodes`, `applyForSegments` chặn đúng, độc lập và kết hợp |
| `TestStaffBreakdown_MultiSegmentCountedOnce` | User thuộc 2 segment nhân viên → nằm ở dòng "Thuộc nhiều nhóm", tổng các dòng con = tổng nhân viên |
| `TestStaffBreakdown_IgnoresNonStaffSegments` | User trong segment `manual` hoặc `referral_code` → không bị tính là nhóm nhân viên |

### 12.2 Kịch bản tích hợp

1. **Nhân viên** — import mã (file 1 cột) → tạo segment `automatic`/`staff_code` chứa mã đó → nhập mã → `statusStaff = employee` + tự vào segment
2. **Người ngoài** — chọn "Tôi không thuộc Parasola" + nhập mã → `not_employee`, **không** xuất hiện trong danh sách creator của partner (kiểm tra `isJoined` không bị set)
3. **Mã dùng chung** — 3 người cùng nhập một mã, cả 3 thành công, `manage-codes.isUsed` vẫn `false`
4. **Modal blocking** — không đóng được bằng X, ESC, click ngoài; phải chọn mới qua
5. **Gate `applyForStaff`** — người ngoài vào event chỉ-nhân-viên → modal từ chối
6. **Gate `staffCodes`** — chưa nhập mã event → chặn; nhập đúng → qua
7. **Gate `applyForSegments`** — nhân viên nhóm A vào event giới hạn nhóm B → chặn
8. **Thống kê** — tổng các nhóm con = tổng nhân viên; nhân viên + ngoài = tổng hệ thống
9. **Cách ly partner** — bật cho Parasola, 12 partner khác không thấy modal, API từ chối

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
| Dòng "Chưa phân nhóm" trong thống kê | Còn cao sau khi Ops đã cấu hình xong segment → có mã chưa được đưa vào segment nào |
| Dòng "Thuộc nhiều nhóm" | > 0 → cấu hình segment bị chồng lấn, một mã đang nằm ở nhiều nhóm |

---

## 14. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Ghi nhầm `isJoined` → sai lệch tăng số creator | **Cao** | Một hàm ghi duy nhất có comment cảnh báo + unit test bắt câu update + theo dõi số creator sau release |
| Mã lộ ra ngoài Parasola | Trung bình | Chấp nhận theo mô hình T-Fluencers (mã dùng chung). Xử lý khi xảy ra: xoá mã, phát mã mới |
| Ops quên cấu hình segment cho một số mã | Trung bình | Nhân viên dùng mã đó rơi vào dòng "Chưa phân nhóm"; sửa được bất cứ lúc nào bằng cách thêm mã vào segment (không phải import lại) |
| Rò rỉ sang partner khác | Thấp | Cờ mặc định `false` + kiểm tra diff trước merge + kịch bản test 9 |
| Import sai file | Thấp | Đọc theo tên cột + báo cáo từng dòng lỗi; mã chưa dùng xoá được từ admin |

---

## 15. Câu hỏi cần chốt trước khi code

_(Không còn.)_

Việc cần trước khi Ops cấu hình: Parasola gửi danh sách mã kèm thông tin mã nào thuộc nhóm nào, để Ops tạo segment tự động tương ứng. Đây là thao tác vận hành, không ảnh hưởng thiết kế — và sửa lại được bất cứ lúc nào mà không cần import lại mã.

---

## 16. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| **3.2** | 2026-08-07 | Nguyễn Đăng Định | Đồng bộ PRD v3.2. Thêm ràng buộc #4 (gate đặt độc lập trước `JoinEvent`) và #5 (mọi query `user-segments` kèm `partner`). Thêm Nhóm 0 tiền đề (FR-002b) vào thứ tự triển khai và Nhóm 5 phát hành (backfill FR-015) |
| **3.1** | 2026-08-06 | Nguyễn Đăng Định | Soát với code Ambassador theo PRD v3.1. **Mục 6 viết lại:** pipeline cũ dùng `netContent`/`netView`/`netCash` — không tồn tại trong repo (thật ra là `statistic.view.total` / `statistic.cash.total` của `EventAnalyticDailyStatistic`), không nêu collection nguồn, `$lookup` không lọc segment nhân viên và `$arrayElemAt[...,0]` gán bừa một nhóm. Thay bằng 4 bước: tập nhân viên → bản đồ nhóm → số liệu → gộp trong Go; số bài đếm từ `contents`. **Mục 5.4 mới:** chặn xoá segment đang được event tham chiếu. **Mục 10, 11: đánh số lại FR** cho khớp PRD (bản cũ lệch một bậc từ FR-006 và lặp FR-005). Dọn tàn dư bản 1.x: bỏ `upsertUserSegment` không ai gọi, bỏ key locale `manageCodeKeyMissingCodeColumn` và test đọc-theo-tên-cột (import chỉ 1 cột), sửa kịch bản "import kèm nhóm", đổi ngưỡng theo dõi sau release |
| 3.0 | 2026-08-06 | Nguyễn Đăng Định | **Bản chốt theo PRD v3.0.** Phân nhóm chuyển sang segment tự động port từ T-Fluencers (mục 4.6, `applyType: staff_code`); `manage-codes` trở về đúng cấu trúc nguồn, import file 1 cột. Status: Final |
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | Viết lại theo PRD v2.0 — bám T-Fluencers. Bỏ transaction, claim atomic, rate limit middleware, audit trail, cron đối soát, dry-run, xoá theo lô. Thêm bảng đối chiếu file nguồn ↔ file đích để port |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ theo mục 0 của PRD |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Đổi từ bù trừ sang Mongo transaction, bỏ job cron |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | Tech spec đầu tiên |
