# Technical Specification: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 2.0
**Status:** Draft
**PRD:** [prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md) v2.0
**Repo:** `AT-Core/ambassador`

---

## 1. Tổng quan

Tài liệu này mô tả cách hiện thực hoá PRD v2.0. Thuật ngữ dùng theo mục 0 của PRD.

### Nguyên tắc

**Port luồng T-Fluencers sang Ambassador.** Phần lớn công việc là chuyển code từ `Viewboost-2025/techcombank` sang `AT-Core/ambassador`, không thiết kế lại.

Chỉ viết mới ở hai chỗ:
1. Ba khác biệt bắt buộc do kiến trúc Ambassador (mục 1.2)
2. Cột `group` + gán `Segment` + thống kê theo nhóm — T-Fluencers không có

### 1.1 Bảng đối chiếu file nguồn ↔ file đích

| Chức năng | T-Fluencers | Ambassador |
|---|---|---|
| Model mã | `internal/model/mg/manage_code.go` | như nguồn, **thêm** `Group`, `Segment` |
| Constants | `internal/constants/staff.go` | `internal/constants/staff_code.go` |
| Admin CRUD mã | `pkg/admin/{router,handler,service}/manage_code.go` | như nguồn |
| Admin UI mã | `admin/src/pages/manage-code/` | như nguồn, thêm cột Nhóm |
| API xác nhận | `pkg/public/service/user.go` — `ConfirmIsStaff` | như nguồn, **trừ** quy tắc ghi ở mục 4.3 |
| API cờ hiển thị modal | `pkg/public/service/partner.go` — `GetStatusEmployee` | như nguồn, thêm kiểm tra `PartnerOpts` |
| Gate nộp bài | `pkg/public/service/content.go:114-146` | như nguồn |
| Mã theo event | `pkg/public/service/event.go` — `InputCodeJoinEvent` | như nguồn |
| Modal nhập mã | `frontend/src/components/layout/main/header/components/modal-tcb-employee.tsx` | `parasola/src/.../modal-staff-code.tsx` |
| Modal từ chối | `frontend/.../modal-not-employee.tsx` | `parasola/.../modal-not-employee.tsx` |
| Aggregate thống kê | `aggregate_pipeline/creator_analytics.go` — `GetCreatorKPIsByStaffBreakdown` | **viết mới**, thêm chiều nhóm |

### 1.2 Ba khác biệt bắt buộc

| # | Ràng buộc | Vì sao |
|---|---|---|
| 1 | Mã lưu ở `staffCode`, **không** dùng `UserPartnerRaw.Code` | `Code` ở Ambassador là referral code (`migration.go:1109`) |
| 2 | `confirm-is-staff` **không bao giờ ghi** `isJoined`/`joinedAt` | `isJoined` xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi thực sự tham gia (`:491`). T-Fluencers gán cứng `IsJoined: true` — bê sang sẽ làm sai lệch tăng số creator Parasola |
| 3 | Bật/tắt bằng `PartnerOpts`, không dùng ENV | Ambassador có 13 partner |

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

	// Group/Segment: THÊM MỚI so với T-Fluencers, phục vụ thống kê theo nhóm.
	Group   string `bson:"group,omitempty" json:"group,omitempty"`
	Segment AppID  `bson:"segment,omitempty" json:"segment,omitempty"`

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

**Migration dữ liệu: không cần.** Field mới đều `omitempty`; bản ghi cũ đọc ra `statusStaff = ""` và `IsStaff("")` trả `false` — đúng ngữ nghĩa "chưa xác nhận, tính là người ngoài".

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

	// THÊM MỚI so với T-Fluencers: gán vào segment theo nhóm của mã
	if body.IsStaff && !manageCode.Segment.IsZero() {
		_ = u.upsertUserSegment(ctx, userId, manageCode.Segment)
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

// upsertUserSegment idempotent — nhập lại cùng mã không tạo bản ghi trùng.
func (u *userImpl) upsertUserSegment(ctx context.Context, userId, segmentId modelmg.AppID) error {
	opts := options.Update().SetUpsert(true)
	return daomongodb.UserSegmentDAO().GetShare().UpdateOne(ctx,
		new(modelmg.UserSegmentRaw),
		bson.M{"user": userId, "segment": segmentId},
		bson.M{"$setOnInsert": bson.M{
			"_id": modelmg.NewAppID(), "user": userId,
			"segment": segmentId, "createdAt": time.Now(),
		}}, opts)
}
```

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

### 5.2 Import Excel — khác T-Fluencers ở 2 điểm

**Điểm 1 — đọc theo tên cột.** T-Fluencers dùng `ManageCodeXLSX{ Code string \`xlsx:"0"\` }`, đọc theo vị trí; file đúng tên nhưng sai thứ tự cột sẽ import sai dữ liệu mà không phát sinh cảnh báo.

```go
headerIdx := map[string]int{}
for i, cell := range sheet.Rows[0].Cells {
	headerIdx[strings.ToLower(strings.TrimSpace(cell.String()))] = i
}
codeCol, ok := headerIdx["code"]
if !ok {
	return nil, errors.New(locale.ManageCodeKeyMissingCodeColumn) // từ chối TOÀN BỘ
}
groupCol, hasGroup := headerIdx["group"]
```

**Điểm 2 — cột `group` và tạo segment.**

```
Mỗi dòng:
  code := NormalizeStaffCode(cell[codeCol])
  rỗng → ghi vào errors[], sang dòng kế

  group := trim(cell[groupCol])                   (nếu có cột)
  segmentId := resolveSegment(partnerId, group)   // cache trong RAM theo lô

  existing := findOne({partner, code})
  existing != nil → skipped++                     (như T-Fluencers)
  existing == nil → thêm vào danh sách insert kèm {group, segment}
```

`resolveSegment` tra `segments` theo `{partner, name}`; chưa có thì tạo mới và cache lại để nhiều dòng cùng nhóm không tạo trùng segment.

```go
type ImportResult struct {
	Total           int           `json:"total"`
	Inserted        int           `json:"inserted"`
	Skipped         int           `json:"skipped"`
	SegmentsCreated []string      `json:"segmentsCreated"`
	Errors          []ImportError `json:"errors"` // {row, code, reason}
}
```

### 5.3 `user-partners` — trả thêm field và filter

`pkg/admin/service/user_partner.go`:
- Response bổ sung `statusStaff`, `staffCode`, `segments[]` (lookup từ `user-segments`)
- Filter `statusStaff` (map thẳng vào `cond`), `segments` (`$in` qua `user-segments`)

---

## 6. Backend — Thống kê theo nhóm

`aggregate_pipeline/staff_breakdown.go` — file mới. T-Fluencers có `GetCreatorKPIsByStaffBreakdown` nhưng chỉ tách nhị phân; bản này thêm chiều nhóm.

```go
// GetStaffBreakdownBySegment tách số liệu theo nhóm nhân viên.
//
// Phân loại theo statusStaff TẠI THỜI ĐIỂM CHẠY, không snapshot theo thời điểm
// đăng bài. Số liệu kỳ cũ có thể đổi khi có nhân viên xác nhận muộn — mọi bảng
// và export PHẢI in ghi chú này. Đây cũng là hành vi của T-Fluencers.
func GetStaffBreakdownBySegment(cond bson.M) []bson.M {
	return []bson.M{
		{"$match": cond},
		{"$lookup": bson.M{
			"from": "user-partners",
			"let":  bson.M{"uid": "$user", "pid": "$partner"},
			"pipeline": []bson.M{{"$match": bson.M{"$expr": bson.M{"$and": []bson.M{
				{"$eq": []interface{}{"$user", "$$uid"}},
				{"$eq": []interface{}{"$partner", "$$pid"}},
			}}}}},
			"as": "up",
		}},
		{"$addFields": bson.M{
			"isStaff": bson.M{"$eq": []interface{}{
				bson.M{"$arrayElemAt": []interface{}{"$up.statusStaff", 0}}, "employee",
			}},
		}},
		{"$lookup": bson.M{
			"from": "user-segments", "localField": "user",
			"foreignField": "user", "as": "us",
		}},
		{"$addFields": bson.M{
			"segmentId": bson.M{"$arrayElemAt": []interface{}{"$us.segment", 0}},
		}},
		{"$group": bson.M{
			"_id":     bson.M{"isStaff": "$isStaff", "segment": "$segmentId"},
			"users":   bson.M{"$addToSet": "$user"},
			"content": bson.M{"$sum": "$netContent"},
			"view":    bson.M{"$sum": "$netView"},
			"cash":    bson.M{"$sum": "$netCash"},
		}},
	}
}
```

**Quy tắc trình bày** (giữ quy ước T-Fluencers): `guest = total − staff`, không cộng dồn từng loại; nhân viên không có segment gom vào "Chưa phân nhóm"; loại trừ bài đã huỷ.

---

## 7. Locale

`internal/locale/staff_code.go` + `properties/{vi,en}/staff_code.properties`.

**Không tái sử dụng** `ReferralKeyCodeInvalid` như T-Fluencers — sai ngữ cảnh.

| Key | VI | EN |
|---|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |
| `manageCodeKeyMissingCodeColumn` | File thiếu cột "code" | Missing "code" column |
| `manageCodeKeyAlreadyUsed` | Mã đã được sử dụng, không thể xoá | Code already used, cannot delete |
| `eventKeyApplyOnlyStaff` | Chương trình này chỉ áp dụng cho nhân viên của công ty | This program only applies to employees |
| `eventKeyRequiredCode` | Bạn cần nhập mã để tham gia chương trình này | You need a code to join this program |
| `eventKeyStaffCodeInvalid` | Mã tham gia chương trình không hợp lệ | Invalid program code |
| `eventKeyNotApplySegment` | Bạn không đủ điều kiện tham gia chương trình này | You are not eligible for this program |

---

## 8. Frontend — Admin

| Trang | Nội dung |
|---|---|
| `admin/src/pages/manage-code/` | Port từ T-Fluencers: `index.tsx`, `model.ts`, `type.d.ts`, `components/{filter,table,create-modal,import-modal}.tsx`. Thêm cột **Nhóm** và filter `group`. `import-modal` hiển thị bảng kết quả liệt kê từng dòng lỗi |
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
| FR-001 | `model/mg/user_partner.go`, `constants/staff_code.go` | `parasola/src/utils/staff.ts` |
| FR-002 | `model/mg/manage_code.go`, `mongodb/{collection,index}.go`, `dao/` | — |
| FR-003 | `pkg/admin/{router,handler,service}/manage_code.go` | `admin/src/pages/manage-code/` |
| FR-004 | `pkg/admin/service/manage_code.go` (ImportExcel) | `admin/.../import-modal.tsx` |
| FR-005 | `pkg/public/service/partner.go` | `parasola/src/models/main.ts` |
| FR-006 | `pkg/public/service/user.go` | — |
| FR-007 | — | `parasola/.../modal-staff-code.tsx`, `header/index.tsx` |
| FR-008 | `model/mg/{event,user_event}.go`, `pkg/public/service/{content,event}.go` | `admin/src/pages/event/components/modal.tsx` |
| FR-009 | — | `parasola/.../modal-not-employee.tsx` |
| FR-010 | `model/mg/partner.go` | `admin/src/pages/partner/components/modal.tsx` |
| FR-011 | `pkg/admin/service/user_partner.go` | `admin/src/pages/user-partner/` |
| FR-012 | `aggregate_pipeline/staff_breakdown.go` | `admin/src/pages/event-statistic/` |
| FR-013 | `pkg/admin/service/export_*.go` | — |

---

## 11. Thứ tự triển khai

**Nhóm 1 — Nền tảng** (chặn các nhóm sau)
1. Model + constants + collection + index + DAO (FR-001, FR-002)
2. `PartnerOpts` + toggle admin (FR-010)
3. Locale

**Nhóm 2 — Quản lý mã**
4. Admin CRUD `manage-codes` (FR-003)
5. Import Excel kèm cột `group` (FR-004)
6. Trang admin `/manage-code` (FR-003, FR-004)

**Nhóm 3 — Luồng người dùng**
7. `status-employee` (FR-005)
8. `confirm-is-staff` + `writeStaffStatus` + `upsertUserSegment` (FR-006)
9. Modal Parasola + model + api (FR-007)

**Nhóm 4 — Chiến dịch và báo cáo**
10. `EventOpts` + `UserEventOpts` + gate ở `content.go` (FR-008)
11. `input-code-join-event` + cờ `isRequireCode` (FR-008)
12. Admin event UI (FR-008)
13. `modal-not-employee` (FR-009)
14. Cột + filter `user-partner` (FR-011)
15. Aggregate + tab thống kê (FR-012)
16. Export (FR-013)

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
| `TestImportExcel_ReadsByColumnName` | File đảo thứ tự cột vẫn đọc đúng |
| `TestImportExcel_CreatesSegmentOncePerGroup` | 50 dòng cùng nhóm → tạo đúng 1 segment |
| `TestContentGate_ThreeConditions` | `applyForStaff`, `staffCodes`, `applyForSegments` chặn đúng, độc lập và kết hợp |

### 12.2 Kịch bản tích hợp

1. **Nhân viên** — import mã kèm nhóm → nhập mã → `statusStaff = employee` + vào segment
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
| Số nhân viên chưa vào segment nào | > 0 → file import thiếu cột `group` |

---

## 14. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Ghi nhầm `isJoined` → sai lệch tăng số creator | **Cao** | Một hàm ghi duy nhất có comment cảnh báo + unit test bắt câu update + theo dõi số creator sau release |
| Mã lộ ra ngoài Parasola | Trung bình | Chấp nhận theo mô hình T-Fluencers (mã dùng chung). Xử lý khi xảy ra: xoá mã, phát mã mới |
| Parasola không gửi cột `group` | Trung bình | Hỏi trước khi họ phát mã; nếu không có thì FR-012 chỉ ra bảng nhị phân |
| Rò rỉ sang partner khác | Thấp | Cờ mặc định `false` + kiểm tra diff trước merge + kịch bản test 9 |
| Import sai file | Thấp | Đọc theo tên cột + báo cáo từng dòng lỗi; mã chưa dùng xoá được từ admin |

---

## 15. Câu hỏi cần chốt trước khi code

1. **Parasola chia nhóm theo tiêu chí gì, và đã có sẵn dữ liệu nhóm theo mã chưa?** Không có cột `group` thì FR-012 chỉ ra được bảng nhị phân.
2. **Có đặt mã theo nhóm luôn không** (`PRS_MIENBAC`)? Với mô hình mã dùng chung thì cách này bỏ được cột `group` và Ops chuẩn bị nhẹ hơn hẳn.

---

## 16. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | Viết lại theo PRD v2.0 — bám T-Fluencers. Bỏ transaction, claim atomic, rate limit middleware, audit trail, cron đối soát, dry-run, xoá theo lô. Thêm bảng đối chiếu file nguồn ↔ file đích để port |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ theo mục 0 của PRD |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Đổi từ bù trừ sang Mongo transaction, bỏ job cron |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | Tech spec đầu tiên |
