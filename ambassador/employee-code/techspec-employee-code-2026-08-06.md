# Technical Specification: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 1.1
**Status:** Draft
**PRD:** [prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md) v1.4
**Repo:** `AT-Core/ambassador`

---

## 1. Tổng quan

Tài liệu này mô tả cách hiện thực hoá PRD v1.4. Mỗi mục ánh xạ trực tiếp tới FR trong PRD.

### Nguyên tắc bám theo

1. **Không phát minh pattern mới.** Mọi thứ đều có tiền lệ trong repo: `PartnerOpts` cho feature flag, `Segment`/`UserSegment` cho phân nhóm, `EligibilityInterface` cho điều kiện tham gia, `ModalCompleteRegistration` cho modal sau đăng nhập.
2. **Backend dùng chung, frontend chỉ Parasola.** Chi phí thêm cho backend gần bằng 0; phần tốn công là FE và chỉ làm một folder.
3. **Không đụng 12 folder partner còn lại.** Có bước kiểm tra diff trước khi merge.

### Bốn ràng buộc kỹ thuật tuyệt đối

| # | Ràng buộc | Vì sao |
|---|---|---|
| 1 | `confirm-is-staff` **không bao giờ ghi** `isJoined` / `joinedAt` | `isJoined` là điều kiện xác định user thuộc partner nào (`internal/service/user.go:226`). Ghi nhầm → thổi phồng số creator của Parasola |
| 2 | **Không đụng** `UserPartnerRaw.Code` | Trường này đang là referral code (`migration.go:1109 UserPartnerReferralCode`) |
| 3 | Chiếm mã bằng **một** `findOneAndUpdate` | Hai user nhập cùng lúc chỉ một người thắng |
| 4 | Ba bước ghi nằm trong **một transaction** | Ghi vào 3 collection; lỗi giữa chừng phải rollback sạch |

---

## 2. Thay đổi Model

### 2.1 `UserPartnerRaw`

`backend/internal/model/mg/user_partner.go`

```go
type UserPartnerRaw struct {
	// ... các trường hiện có, GIỮ NGUYÊN
	// Code vẫn là referral code — KHÔNG dùng cho mã nhân viên

	// StatusStaff: "employee" | "not_employee" | "not_verify". Rỗng = chưa hỏi.
	StatusStaff string `bson:"statusStaff,omitempty" json:"statusStaff,omitempty"`
	// StaffCode là mã nhân viên đã xác nhận thành công (đã chuẩn hoá TRIM+UPPER).
	StaffCode string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`
	// StaffCodeAt là thời điểm xác nhận.
	StaffCodeAt time.Time `bson:"staffCodeAt,omitempty" json:"staffCodeAt,omitempty"`

	// StaffPromptDismissedAt/Count phục vụ giới hạn số lần hỏi lại (FR-008).
	StaffPromptDismissedAt  time.Time `bson:"staffPromptDismissedAt,omitempty" json:"-"`
	StaffPromptDismissCount int       `bson:"staffPromptDismissCount,omitempty" json:"-"`
}
```

### 2.2 `ManageCodeRaw` — file mới

`backend/internal/model/mg/manage_code.go`

```go
package modelmg

import (
	"time"
	databasemongodb "viewboost/internal/module/database/mongodb"
)

type ManageCodeDAO interface {
	GetShare() databasemongodb.IDatabase
}

// ManageCodeRaw là một mã nhân viên hợp lệ do Admin import theo partner.
type ManageCodeRaw struct {
	ID      AppID  `bson:"_id" json:"_id"`
	Partner AppID  `bson:"partner" json:"partner"`
	Type    string `bson:"type" json:"type"` // constants.ManageCodeApplyForEmployee
	Code    string `bson:"code" json:"code"` // đã chuẩn hoá TRIM + UPPERCASE

	// Group là tên nhóm lấy từ cột "group" của file import (phòng ban/khu vực).
	// Segment là segment tương ứng, tạo tự động khi import.
	Group   string `bson:"group,omitempty" json:"group,omitempty"`
	Segment AppID  `bson:"segment,omitempty" json:"segment,omitempty"`

	// ImportBatchID gom các mã cùng một lần import, phục vụ xoá theo lô.
	ImportBatchID AppID `bson:"importBatchId,omitempty" json:"importBatchId,omitempty"`

	IsUsed bool      `bson:"isUsed" json:"isUsed"`
	UsedBy AppID     `bson:"usedBy,omitempty" json:"usedBy,omitempty"`
	UsedAt time.Time `bson:"usedAt,omitempty" json:"usedAt,omitempty"`

	CreatedBy AppID     `bson:"createdBy" json:"createdBy"`
	CreatedAt time.Time `bson:"createdAt" json:"createdAt"`
	UpdatedAt time.Time `bson:"updatedAt" json:"updatedAt"`
}

func (m *ManageCodeRaw) DbModelName() string {
	return databasemongodb.CollectionManageCode
}
```

### 2.3 `PartnerOpts`

`backend/internal/model/mg/partner.go`

```go
type PartnerOpts struct {
	AllowResubmitRejectedContent bool `bson:"allowResubmitRejectedContent,omitempty" json:"allowResubmitRejectedContent"`

	// EnableStaffCode bật luồng nhập mã nhân viên cho partner này.
	// Mặc định false — 13 partner hiện tại không đổi hành vi.
	EnableStaffCode bool `bson:"enableStaffCode,omitempty" json:"enableStaffCode"`
	// RequireStaffCodeValidation bắt buộc mã phải tồn tại trong manage-codes.
	// Tắt = chấp nhận mọi mã đúng format (khi partner chưa kịp gửi danh sách).
	RequireStaffCodeValidation bool `bson:"requireStaffCodeValidation,omitempty" json:"requireStaffCodeValidation"`
}
```

### 2.4 `ParticipationRequirements`

`backend/internal/model/mg/event.go`

```go
type ParticipationRequirements struct {
	// ... các trường hiện có

	// StaffRequired: chỉ nhân viên đã xác nhận mới tham gia được.
	StaffRequired bool `bson:"staffRequired,omitempty" json:"staffRequired"`
	// AllowedSegments: giới hạn theo nhóm. Rỗng = không giới hạn.
	// Kết hợp với StaffRequired theo quan hệ AND.
	AllowedSegments []AppID `bson:"allowedSegments,omitempty" json:"allowedSegments,omitempty"`
}
```

### 2.5 Constants — file mới

`backend/internal/constants/staff_code.go`

```go
package constants

const (
	StatusStaffNotVerify   = "not_verify"
	StatusStaffIsEmployee  = "employee"
	StatusStaffNotEmployee = "not_employee"

	ManageCodeApplyForEmployee = "apply_for_employee"

	// Giới hạn hỏi lại khi user đóng modal (FR-008)
	StaffPromptMaxDismiss   = 3
	StaffPromptCooldownDays = 7

	// Rate limit (FR-007)
	StaffCodeMaxFailPerUser = 5
	StaffCodeMaxFailPerIP   = 20
	StaffCodeFailWindow     = 10 * time.Minute
	StaffCodeLockDuration   = 30 * time.Minute
)

// IsStaff là quy tắc canonical DUY NHẤT để phân loại nhân viên.
// Mọi giá trị mơ hồ (rỗng, not_verify) đều KHÔNG tính là nhân viên,
// để số liệu nhân viên không bao giờ bị thổi phồng do dữ liệu bẩn.
// Giữ đồng bộ với parasola/src/utils/staff.ts
func IsStaff(statusStaff string) bool {
	return statusStaff == StatusStaffIsEmployee
}

var staffCodePattern = regexp.MustCompile(`^[A-Z0-9_-]{6,32}$`)

// NormalizeStaffCode chuẩn hoá mã ở BACKEND, không tin FE.
func NormalizeStaffCode(code string) string {
	return strings.ToUpper(strings.TrimSpace(code))
}

func IsValidStaffCodeFormat(code string) bool {
	return staffCodePattern.MatchString(code)
}
```

---

## 3. Database

### 3.1 Collection mới

`backend/internal/module/database/mongodb/collection.go`

```go
CollectionManageCode = "manage-codes"
```

### 3.2 DAO

`backend/internal/module/database/mongodb/dao/manage_code.go` — copy nguyên pattern của `dao/user_segment.go`.

### 3.3 Index

`backend/internal/module/database/mongodb/index.go`

Hàm `newIndex()` hiện tại **không hỗ trợ unique** (`index.go:352`, chỉ dựng `bsonx.Doc` với `Int32(1)`). Cần thêm helper:

```go
func (i indexDatabase) newUniqueIndex(key ...string) mongo.IndexModel {
	m := i.newIndex(key...)
	m.Options = options.Index().SetUnique(true)
	return m
}
```

Rồi đăng ký:

```go
// manage-codes
{
	indexes := []mongo.IndexModel{
		i.newUniqueIndex("partner", "code"),  // chống trùng mã trong cùng partner
		i.newIndex("partner", "isUsed"),      // filter danh sách
		i.newIndex("usedBy"),                 // tra ngược từ user
		i.newIndex("importBatchId"),          // xoá theo lô
	}
	i.process(db.Collection(CollectionManageCode), indexes)
}
```

Bổ sung index cho `user-partners` phục vụ filter và thống kê:

```go
// user partner — thêm vào block đã có
i.newIndex("partner", "statusStaff"),
```

### 3.4 Migration

**Không cần migration dữ liệu.** Mọi field mới đều `omitempty`; bản ghi cũ đọc ra `statusStaff = ""`, và `IsStaff("")` trả `false` — đúng ngữ nghĩa "chưa xác nhận, tính là người ngoài".

Việc duy nhất cần làm khi release: bật cờ cho Parasola.

```js
db.getCollection('partners').updateOne(
  { slug: 'parasola' },
  { $set: {
      'options.enableStaffCode': true,
      'options.requireStaffCodeValidation': true
  }}
)
```

---

## 4. Backend — Public API

### 4.1 `GET /users/me` — bổ sung khối `staffStatus` (FR-005)

`backend/pkg/public/service/user.go` — `GetMe` (`:1770`)

Không tạo endpoint riêng cho luồng chính: endpoint riêng bắt **mọi** người dùng tốn thêm một round-trip mỗi lần mở app, kể cả người đã trả lời từ lâu.

```go
type StaffStatusResponse struct {
	IsFeatureEnabled     bool   `json:"isFeatureEnabled"`
	ShouldAskStaffStatus bool   `json:"shouldAskStaffStatus"`
	StatusStaff          string `json:"statusStaff"`
	CanEdit              bool   `json:"canEdit"`
}
```

```go
func buildStaffStatus(partner *modelmg.PartnerRaw, up *modelmg.UserPartnerRaw) *StaffStatusResponse {
	// Partner chưa bật → trả sớm, KHÔNG phát sinh truy vấn nào thêm
	if partner.Options == nil || !partner.Options.EnableStaffCode {
		return &StaffStatusResponse{IsFeatureEnabled: false}
	}
	res := &StaffStatusResponse{IsFeatureEnabled: true, CanEdit: true}
	if up == nil || up.ID.IsZero() {
		res.ShouldAskStaffStatus = true
		res.StatusStaff = constants.StatusStaffNotVerify
		return res
	}
	res.StatusStaff = up.StatusStaff

	// Đã chốt lựa chọn → thôi hỏi
	if up.StatusStaff == constants.StatusStaffIsEmployee ||
		up.StatusStaff == constants.StatusStaffNotEmployee {
		// user KHÔNG tự gỡ được nhãn nhân viên (FR-009)
		res.CanEdit = up.StatusStaff != constants.StatusStaffIsEmployee
		return res
	}

	// Giới hạn hỏi lại
	if up.StaffPromptDismissCount >= constants.StaffPromptMaxDismiss {
		return res
	}
	if !up.StaffPromptDismissedAt.IsZero() &&
		time.Since(up.StaffPromptDismissedAt) < constants.StaffPromptCooldownDays*24*time.Hour {
		return res
	}
	res.ShouldAskStaffStatus = true
	return res
}
```

Vẫn giữ `GET /partners/:id/staff-status` trả đúng struct trên, dùng khi FE cần đọc lại sau xác nhận mà không muốn tải lại toàn bộ `users/me`.

### 4.2 `POST /users/confirm-is-staff` (FR-006)

**Router** — `backend/pkg/public/router/user.go`
```go
g.POST("/confirm-is-staff", h.ConfirmIsStaff, v.ConfirmIsStaff, a.RequiredLogin, m.StaffCodeRateLimit())
```

**Request** — `backend/pkg/public/model/request/user.go`
```go
type ConfirmIsStaffBody struct {
	Partner string `json:"partner"`
	IsStaff bool   `json:"isStaff"`
	Code    string `json:"code"`
}

func (b ConfirmIsStaffBody) Validate() error {
	return validation.ValidateStruct(&b,
		validation.Field(&b.Partner,
			validation.Required.Error(locale.CommonKeyPartnerIsRequired),
			is.MongoID.Error(locale.CommonKeyIDMongoInvalid)),
		// Code KHÔNG validate ở đây vì phụ thuộc IsStaff — validate trong service
	)
}
```

**Service** — `backend/pkg/public/service/user.go`

```go
func (u *userImpl) ConfirmIsStaff(ctx context.Context, userId modelmg.AppID, body request.ConfirmIsStaffBody) error {
	user, partner, err := u.loadUserAndPartnerForStaff(ctx, userId, body.Partner)
	if err != nil {
		return err
	}
	if partner.Options == nil || !partner.Options.EnableStaffCode {
		return errors.New(locale.StaffCodeKeyFeatureDisabled)
	}

	// ---- Nhánh KHÔNG phải nhân viên: không đụng gì tới mã ----
	if !body.IsStaff {
		if err := u.writeStaffStatus(ctx, userId, partner.ID,
			constants.StatusStaffNotEmployee, ""); err != nil {
			return err
		}
		go audit.LogStaffStatusChanged(userId, partner.ID, constants.StatusStaffNotEmployee, "")
		return nil
	}

	// ---- Nhánh LÀ nhân viên ----
	code := constants.NormalizeStaffCode(body.Code)
	if code == "" {
		return errors.New(locale.StaffCodeKeyRequired)
	}
	if !constants.IsValidStaffCodeFormat(code) {
		u.recordStaffCodeFailure(ctx, userId, code)
		return errors.New(locale.StaffCodeKeyInvalid)
	}

	// Ba bước ghi vào 3 collection — gói trong MỘT transaction.
	// Lỗi bất kỳ bước nào ⇒ rollback sạch, mã trở về chưa dùng.
	err = databasemongodb.TransactionDatabase().WithTransaction(ctx,
		func(sc mongo.SessionContext) error {
			var claimed *modelmg.ManageCodeRaw
			if partner.Options.RequireStaffCodeValidation {
				claimed, err = u.claimStaffCode(sc, partner.ID, code, userId)
				if err != nil {
					return err
				}
			}
			if err := u.writeStaffStatus(sc, userId, partner.ID,
				constants.StatusStaffIsEmployee, code); err != nil {
				return err
			}
			if claimed != nil && !claimed.Segment.IsZero() {
				return u.upsertUserSegment(sc, userId, claimed.Segment)
			}
			return nil
		})
	if err != nil {
		u.recordStaffCodeFailure(ctx, userId, code)
		return err
	}

	// Ghi log SAU khi commit, bất đồng bộ — lỗi log không được làm hỏng nghiệp vụ
	go audit.LogStaffStatusChanged(userId, partner.ID, constants.StatusStaffIsEmployee, code)
	return nil
}
```

**Lưu ý khi implement:** mọi lệnh DB bên trong closure phải truyền `sc` (`mongo.SessionContext`), không phải `ctx` gốc. Truyền nhầm `ctx` thì lệnh đó nằm ngoài transaction và không được rollback — đây là lỗi phổ biến và rất khó phát hiện vì luồng happy path vẫn chạy đúng.

#### `writeStaffStatus` — hàm ghi DUY NHẤT được phép chạm `user-partners`

Đây là điểm chặn ràng buộc #1 và #2. Mọi thứ khác trong luồng này đều **không** được `UpdateOne` lên `user-partners`.

```go
// writeStaffStatus upsert trạng thái nhân viên vào user-partners.
//
// CẢNH BÁO: KHÔNG BAO GIỜ ghi isJoined/joinedAt ở đây.
// isJoined là điều kiện xác định user thuộc partner nào
// (internal/service/user.go:226) và chỉ được set khi user THỰC SỰ tham gia
// (internal/service/user.go:491). Ghi ở đây sẽ khiến người chỉ mới bấm
// "Tôi không phải nhân viên" bị tính là creator của partner.
//
// Cũng KHÔNG được ghi trường `code` — đó là referral code.
func (u *userImpl) writeStaffStatus(
	ctx context.Context, userId, partnerId modelmg.AppID, status, code string,
) error {
	set := bson.M{
		"statusStaff": status,
		"updatedAt":   time.Now(),
	}
	if status == constants.StatusStaffIsEmployee {
		set["staffCode"] = code
		set["staffCodeAt"] = time.Now()
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

#### `claimStaffCode` — chiếm mã atomic

```go
// claimStaffCode chiếm mã bằng MỘT thao tác findOneAndUpdate.
// Hai user nhập cùng lúc: chỉ một người match filter {isUsed:false}.
func (u *userImpl) claimStaffCode(
	ctx context.Context, partnerId modelmg.AppID, code string, userId modelmg.AppID,
) (*modelmg.ManageCodeRaw, error) {
	var claimed modelmg.ManageCodeRaw
	err := daomongodb.ManageCodeDAO().GetShare().
		Collection(new(modelmg.ManageCodeRaw)).
		FindOneAndUpdate(ctx,
			bson.M{
				"partner": partnerId,
				"code":    code,
				"type":    constants.ManageCodeApplyForEmployee,
				"isUsed":  false,
			},
			bson.M{"$set": bson.M{
				"isUsed": true, "usedBy": userId,
				"usedAt": time.Now(), "updatedAt": time.Now(),
			}},
			options.FindOneAndUpdate().SetReturnDocument(options.After),
		).Decode(&claimed)

	if err == nil {
		return &claimed, nil
	}
	if err != mongo.ErrNoDocuments {
		return nil, errors.New(locale.CommonKeyErrorWhenHandle)
	}

	// Không match: phân biệt "không tồn tại" vs "đã dùng" bằng 1 truy vấn đọc
	exists := new(modelmg.ManageCodeRaw)
	_ = daomongodb.ManageCodeDAO().GetShare().FindOne(ctx, exists, bson.M{
		"partner": partnerId, "code": code,
		"type": constants.ManageCodeApplyForEmployee,
	})
	if exists.ID.IsZero() {
		return nil, errors.New(locale.StaffCodeKeyInvalid)
	}
	return nil, errors.New(locale.StaffCodeKeyAlreadyUsed)
}
```

**Vì sao dùng transaction:** repo đã có helper `WithTransaction` (`internal/module/database/mongodb/transaction.go`) với `writeconcern.WMajority()` + `readconcern.Snapshot()`, đang chạy thật ở luồng rút tiền (`internal/service/withdraw.go:131`). Transaction đòi replica set, nên hạ tầng có sẵn — không cần xác minh thêm, và không cần viết cơ chế bù trừ thủ công.

### 4.3 Rate limit middleware (FR-007)

`backend/internal/echo/middleware/staff_code_rate_limit.go` — file mới

Dùng Redis (đã có sẵn trong repo cho cache), khoá theo cả user và IP:

```
staff_code_fail:user:<userId>   TTL 10 phút
staff_code_fail:ip:<ip>         TTL 10 phút
staff_code_lock:user:<userId>   TTL 30 phút
```

- Middleware kiểm tra khoá `lock` trước khi vào handler → có thì trả lỗi kèm số phút còn lại
- Service gọi `recordStaffCodeFailure()` **chỉ khi nhập sai**; nhập đúng không tăng bộ đếm
- Vượt ngưỡng → đặt khoá `lock`

**Dùng chung cho mọi đường nhập mã** — cả `confirm-is-staff` lẫn đường sửa từ trang Hồ sơ (FR-009), cùng một khoá theo user. Nếu tách bộ đếm thì đó là cửa dò mã thứ hai.

---

## 5. Backend — Admin API

### 5.1 Router

`backend/pkg/admin/router/manage_code.go` — file mới, đăng ký trong `router.go` cạnh `segment(adminGroup)`.

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
	g.DELETE("/batch/:id", h.DeleteBatch, c.ParamID)
	g.GET("/export", h.Export, v.GetList)
}
```

| Endpoint | Ghi chú |
|---|---|
| `GET /manage-codes` | filter `partner`, `code`, `group`, `isUsed`, `keyword` |
| `POST /manage-codes` | `{partner, code, group?}` |
| `DELETE /manage-codes/:id` | từ chối nếu `isUsed` |
| `POST /manage-codes/import-excel` | form `partner`, `dryRun` (bool), file |
| `DELETE /manage-codes/batch/:id` | xoá mã **chưa dùng** của một `importBatchId` |
| `GET /manage-codes/export` | xuất Excel |

Mọi handler kiểm tra `s.Staff.IsAllowPartner(partnerID)` theo pattern có sẵn.

### 5.2 Import Excel (FR-004)

`backend/pkg/admin/service/manage_code.go`

**Đọc theo tên cột, không theo vị trí.** T-Fluencer đọc `xlsx:"0"` — file đúng tên nhưng sai thứ tự cột sẽ import nhầm dữ liệu im lặng.

```go
// Bước 1: đọc dòng header, dựng map tên cột → chỉ số
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

**Thuật toán xử lý mỗi dòng:**

```
code := NormalizeStaffCode(cell[codeCol])
rỗng / sai format → ghi vào errors[], sang dòng kế

group := trim(cell[groupCol])  (nếu có cột)
segmentId := resolveSegment(partnerId, group)   // cache trong RAM theo lô

existing := findOne({partner, code})

existing == nil:
    → thêm vào danh sách insert (kèm importBatchId)

existing != nil && existing.Group == group:
    → skipped++

existing != nil && existing.Group != group:
    → cập nhật {group, segment} của mã
    → nếu existing.IsUsed:
          gỡ user-segments {user: existing.UsedBy, segment: existing.Segment}
          thêm user-segments {user: existing.UsedBy, segment: segmentId}
    → groupUpdated++
```

`resolveSegment` tra `segments` theo `{partner, name}`; chưa có thì tạo mới, cache lại trong map để nhiều dòng cùng nhóm không tạo trùng.

**Dry-run:** chạy toàn bộ logic trên nhưng gom kết quả vào struct và `return` trước mọi lệnh ghi — kể cả tạo segment.

**Kết quả:**
```go
type ImportResult struct {
	ImportBatchID   string        `json:"importBatchId"`
	Total           int           `json:"total"`
	Inserted        int           `json:"inserted"`
	GroupUpdated    int           `json:"groupUpdated"`
	Skipped         int           `json:"skipped"`
	SegmentsCreated []string      `json:"segmentsCreated"`
	Errors          []ImportError `json:"errors"` // {row, code, reason}
}
```

### 5.3 `user-partners` — trả thêm trường và filter (FR-013)

`backend/pkg/admin/service/user_partner.go`

- Response bổ sung `statusStaff`, `staffCode`, `segments[]` (lookup từ `user-segments`)
- Filter `statusStaff` (map thẳng vào `cond`), `segments` (`$in` qua `user-segments`)
- Endpoint sửa trạng thái (FR-009): `PUT /user-partners/:id/staff-status` body `{statusStaff, reason}`
  - Gỡ nhãn nhân viên ⇒ nhả mã (`isUsed:false`, unset `usedBy`/`usedAt`) + gỡ khỏi segment
  - `reason` bắt buộc, ghi audit

---

## 6. Backend — Eligibility (FR-011)

`backend/pkg/public/service/eligibility.go`

Cắm vào `CalculateEligibility` đã có, **không** thêm nhánh kiểm tra song song trong `content.go` như T-Fluencer.

```go
type EligibilityChecks struct {
	// ... các trường hiện có
	IsStaff        bool `json:"isStaff"`
	InAllowedGroup bool `json:"inAllowedGroup"`
}

type ParticipationRequirementsVO struct {
	// ... các trường hiện có
	StaffRequired    bool     `json:"staffRequired"`
	AllowedSegments  []string `json:"allowedSegments,omitempty"`
	AllowedGroupNames []string `json:"allowedGroupNames,omitempty"` // để FE hiện tên nhóm
}
```

Trong `CalculateEligibility`, sau bước tải user:

```go
// Chỉ truy vấn khi event thực sự dùng điều kiện này
if req.StaffRequired || len(req.AllowedSegments) > 0 {
	up := new(modelmg.UserPartnerRaw)
	_ = daomongodb.UserPartnerDAO().GetShare().FindOne(ctx, up,
		bson.M{"user": userId, "partner": event.Partner})

	if req.StaffRequired {
		result.Checks.IsStaff = constants.IsStaff(up.StatusStaff)
		if !result.Checks.IsStaff {
			result.Eligible = false
			result.FailReasons = append(result.FailReasons, "staffRequired")
		}
	}
	if len(req.AllowedSegments) > 0 {
		total := daomongodb.UserSegmentDAO().GetShare().CountByCondition(ctx,
			new(modelmg.UserSegmentRaw),
			bson.M{"user": userId, "segment": bson.M{"$in": req.AllowedSegments}})
		result.Checks.InAllowedGroup = total > 0
		if total == 0 {
			result.Eligible = false
			result.FailReasons = append(result.FailReasons, "notInAllowedGroup")
		}
	}
}
```

Quan hệ **AND**: bật cả hai thì phải thoả cả hai. Nhân viên có mã không kèm `group` sẽ không thuộc segment nào → bị chặn khỏi event giới hạn nhóm. Đây là hành vi đúng thiết kế; admin UI phải cảnh báo (mục 9.3).

---

## 7. Backend — Thống kê theo nhóm (FR-014)

`backend/internal/module/database/mongodb/aggregate_pipeline/staff_breakdown.go` — file mới

```go
// GetStaffBreakdownBySegment tách số liệu theo nhóm nhân viên.
//
// Phân loại theo statusStaff TẠI THỜI ĐIỂM CHẠY, không snapshot theo thời điểm
// đăng bài (PRD FR-014 phương án A). Số liệu kỳ cũ có thể đổi khi có nhân viên
// xác nhận muộn — mọi bảng và export PHẢI in ghi chú này.
func GetStaffBreakdownBySegment(cond bson.M) []bson.M {
	return []bson.M{
		{"$match": cond},
		// user-partners → statusStaff
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
		// user-segments → nhóm
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

**Quy tắc trình bày** (khớp PRD):
- `guest = total − staff`, không cộng dồn từng loại — mọi giá trị mơ hồ rơi vào "Ngoài", số nhân viên không bao giờ bị thổi phồng
- Nhân viên không có segment → gom vào dòng "Chưa phân nhóm"
- Số liệu loại trừ bài đã huỷ
- Ghi chú bắt buộc trên bảng và export: *"Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo."*

Cân nhắc cache Redis 5 phút nếu đo thấy vượt 3 giây với 10.000 user.

---

## 8. Audit

Dùng `internal/model/mg/audit.go` sẵn có. Bốn loại sự kiện:

| Action | Payload |
|---|---|
| `staff_status_changed` | user, partner, from → to, code, ip |
| `staff_code_failed` | user, partner, code đã thử, ip |
| `staff_status_changed_by_admin` | admin, user, from → to, **reason** |
| `staff_code_imported` | admin, partner, batchId, total/inserted/updated/skipped, filename |

Ghi bất đồng bộ (`go audit.Log...`) **sau khi transaction commit** — lỗi ghi log không được làm hỏng nghiệp vụ, và không được ghi log cho giao dịch đã rollback.

**Không cần job đối soát mã mồ côi.** Transaction ở mục 4.2 đảm bảo không thể tồn tại mã bị chiếm mà chủ không có nhãn.

---

## 9. Frontend — Admin

### 9.1 Trang `/manage-code` — mới

`admin/src/pages/manage-code/` theo pattern các trang hiện có:

```
index.tsx
model.ts
type.d.ts
components/
  filter.tsx        partner / code / group / isUsed / keyword
  table.tsx         Mã | Partner | Nhóm | Đã dùng | Người dùng | Ngày dùng | Ngày tạo
  create-modal.tsx  {partner, code, group?}
  import-modal.tsx  Dragger + checkbox "Xem trước" + bảng kết quả
```

`import-modal.tsx` phải hiển thị kết quả dạng bảng, **liệt kê từng dòng lỗi kèm số dòng**. Sau dry-run có nút "Import thật".

Thêm menu vào `admin/src/locales/*/menu.ts` và service `admin/src/services/manage-code.ts`.

### 9.2 Partner modal — 2 toggle (FR-010)

`admin/src/pages/partner/components/modal.tsx` — section "Cấu hình nhân viên", dùng `RcSwitchFormNew` như 2 toggle BXH đã có. Toggle `requireStaffCodeValidation` disable khi `enableStaffCode` tắt.

### 9.3 Event modal — điều kiện tham gia (FR-011)

`admin/src/pages/event/components/modal.tsx` — trong section điều kiện tham gia đã có:
- `RcSwitchFormNew` cho `participationRequirements.staffRequired`
- `RcFormSelectNew mode="multiple"` cho `allowedSegments`, chỉ load segment của partner đang chọn

**Cảnh báo bắt buộc** khi chọn segment mà partner còn mã chưa gán nhóm:

> ⚠️ Partner này còn {n} mã nhân viên chưa gán nhóm. Những nhân viên dùng các mã đó sẽ không tham gia được chiến dịch này.

Lấy `n` từ `GET /manage-codes?partner=X&hasGroup=false&countOnly=true`.

### 9.4 `user-partner` — cột, filter, sửa trạng thái (FR-013, FR-009)

`admin/src/pages/user-partner/`:
- `table.tsx`: 3 cột `Nhân viên` | `Mã nhân viên` | `Nhóm`, rỗng hiện `—`
- `filter.tsx`: select `statusStaff`, multi-select `segment`
- `modal-edit.tsx`: thêm mục sửa trạng thái nhân viên, **bắt buộc nhập lý do**

### 9.5 Thống kê (FR-014)

`admin/src/pages/event-statistic/` — tab mới. Bảng phân cấp: dòng tổng "Nhân viên" → các nhóm con → dòng "Chưa phân nhóm" → dòng tổng "Ngoài". Nút export.

---

## 10. Frontend — Parasola

**Chỉ làm trong `parasola/`.** `frontend/` và 12 folder partner còn lại không đụng tới.

### 10.1 Điểm cắm — dùng lại pattern có sẵn

`parasola/src/components/layout/main/header/index.tsx` đã làm đúng cơ chế này cho màn đồng ý điều khoản (`:82-84`):

```
initApp gọi users/me → user state update
  → useEffect [user] kiểm tra user.privacyAccepted === false
  → bung ModalCompleteRegistration
```

Modal mã nhân viên đi theo **đúng cơ chế đó**, đặt cạnh trong cùng file:

```tsx
// Điều khoản có độ ưu tiên cao hơn — không hiện chồng 2 modal
useEffect(() => {
  if (!user) return;
  if (user.privacyAccepted === false) return;          // để modal điều khoản chạy trước
  if (user.staffStatus?.shouldAskStaffStatus) {
    setVisibleModalStaffCode(true);
  }
}, [user]);
```

### 10.2 Component modal

`parasola/src/components/layout/main/header/components/modal-staff-code.tsx` — mới

Dùng `AppModal` sẵn có. **Khác** `ModalCompleteRegistration` ở chỗ modal này **đóng được** (`closeButton` mặc định) — điều khoản là nghĩa vụ pháp lý, khai báo nhân viên thì không.

```tsx
const [isStaff, setIsStaff] = useState<boolean | null>(null);
const [code, setCode] = useState('');

// Chuẩn hoá NGAY khi gõ, để giá trị hiển thị = giá trị gửi lên.
// T-Fluencer hiện hoa nhưng gửi nguyên bản → DB lưu khác cái user thấy.
const onCodeChange = (v: string) => setCode(v.toUpperCase().trim());

const canSubmit = isStaff === false || (isStaff === true && code.length > 0);

const onDismiss = () => {
  dispatch({ type: 'mainState/dismissStaffPrompt' });  // tăng dismissCount
  onClose();
};
```

- Chọn "Tôi không phải" → `confirm-is-staff {isStaff:false}` ngay, đóng modal
- Chọn "Tôi là nhân viên" → hiện ô mã, nút Xác nhận khoá tới khi có mã
- Lỗi backend hiện dưới ô mã, **không** đóng modal

### 10.3 Model và API

`parasola/src/models/main.ts` — thêm state `visibleModalStaffCode` và các effect `confirmIsStaff`, `dismissStaffPrompt`, `getStaffStatus`.

`parasola/src/configs/api.ts`:
```ts
confirmIsStaff: (): IApi => ({ url: '/users/confirm-is-staff', method: methods.post }),
getStaffStatus: (id: string): IApi => ({ url: `/partners/${id}/staff-status`, method: methods.get }),
```

`parasola/src/utils/staff.ts` — mirror của `constants.IsStaff`, kèm comment yêu cầu giữ đồng bộ với Go.

### 10.4 Trang Hồ sơ (FR-009)

`parasola/src/pages/account/` — mục "Thông tin nhân viên":
- `not_employee` / chưa xác nhận → cho nhập mã, đổi sang "là nhân viên"
- `employee` → hiện mã (che một phần) + hướng dẫn liên hệ hỗ trợ, **không cho tự gỡ**

### 10.5 Thông báo từ chối (FR-012)

Component dùng chung, đọc `failReasons` từ `CalculateEligibility`:

| `failReasons` | Tiêu đề | Hành động |
|---|---|---|
| `staffRequired` + chưa xác nhận | Chiến dịch dành riêng cho nhân viên | **Nhập mã ngay** → mở modal 10.2 |
| `staffRequired` + đã xác nhận không phải | Chiến dịch dành riêng cho nhân viên | **Khám phá thêm** |
| `notInAllowedGroup` | Chiến dịch dành cho nhóm khác | **Khám phá thêm** |

---

## 11. Locale

`backend/internal/locale/staff_code.go` + `properties/{vi,en}/staff_code.properties` — file mới.

**Không tái sử dụng** `ReferralKeyCodeInvalid` như T-Fluencer — sai ngữ cảnh.

| Key | VI | EN |
|---|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeKeyAlreadyUsed` | Mã này đã được sử dụng bởi tài khoản khác | This code has already been used |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |
| `staffCodeKeyTooManyAttempts` | Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau {n} phút | Too many failed attempts. Try again in {n} minutes |
| `manageCodeKeyMissingCodeColumn` | File thiếu cột "code" | Missing "code" column |
| `manageCodeKeyAlreadyUsed` | Mã đã được sử dụng, không thể xoá | Code already used, cannot delete |
| `eventKeyStaffRequired` | Chiến dịch này chỉ dành cho nhân viên | This campaign is for employees only |
| `eventKeyNotInAllowedGroup` | Bạn không thuộc nhóm được tham gia chiến dịch này | You are not in an eligible group |

---

## 12. Ánh xạ FR → file

| FR | Backend | Frontend |
|---|---|---|
| FR-001 | `model/mg/user_partner.go`, `constants/staff_code.go` | — |
| FR-002 | `model/mg/manage_code.go`, `mongodb/{collection,index}.go`, `dao/manage_code.go` | — |
| FR-003 | `pkg/admin/{router,handler,service}/manage_code.go` | `admin/src/pages/manage-code/` |
| FR-004 | `pkg/admin/service/manage_code.go` (ImportExcel) | `admin/.../import-modal.tsx` |
| FR-005 | `pkg/public/service/user.go` (GetMe), `service/partner.go` | `parasola/src/models/main.ts` |
| FR-006 | `pkg/public/service/user.go` (ConfirmIsStaff) | — |
| FR-007 | `internal/echo/middleware/staff_code_rate_limit.go` | — |
| FR-008 | — | `parasola/.../modal-staff-code.tsx`, `header/index.tsx` |
| FR-009 | `pkg/admin/service/user_partner.go` | `parasola/src/pages/account/`, `admin/.../modal-edit.tsx` |
| FR-010 | `model/mg/partner.go` | `admin/src/pages/partner/components/modal.tsx` |
| FR-011 | `model/mg/event.go`, `pkg/public/service/eligibility.go` | `admin/src/pages/event/components/modal.tsx` |
| FR-012 | — | `parasola/` component thông báo |
| FR-013 | `pkg/admin/service/user_partner.go` | `admin/src/pages/user-partner/` |
| FR-014 | `aggregate_pipeline/staff_breakdown.go` | `admin/src/pages/event-statistic/` |
| FR-015 | `pkg/admin/service/export_*.go` | — |
| FR-016 | `audit` (4 loại sự kiện) | — |

---

## 13. Thứ tự triển khai

Ba nhóm đầu chạy song song được; nhóm 4 phụ thuộc nhóm 1.

**Nhóm 1 — Nền tảng** (chặn các nhóm sau)
1. Model + constants + collection + index + DAO (FR-001, FR-002)
2. `PartnerOpts` + toggle admin (FR-010)
3. Locale (mục 11)

**Nhóm 2 — Quản lý mã**
4. Admin CRUD `manage-codes` (FR-003)
5. Import Excel kèm nhóm + dry-run + xoá theo lô (FR-004)
6. Trang admin `/manage-code` (FR-003, FR-004)

**Nhóm 3 — Luồng người dùng**
7. `staffStatus` trong `users/me` + endpoint riêng (FR-005)
8. `confirm-is-staff` + `writeStaffStatus` + `claimStaffCode` (FR-006)
9. Rate limit middleware (FR-007)
10. Modal Parasola + model + api (FR-008)
11. Trang Hồ sơ + sửa từ admin (FR-009)

**Nhóm 4 — Campaign và báo cáo**
12. `ParticipationRequirements` + eligibility (FR-011)
13. Admin event UI + cảnh báo mã chưa gán nhóm (FR-011)
14. Thông báo từ chối trên Parasola (FR-012)
15. Cột + filter `user-partner` (FR-013)
16. Aggregate + tab thống kê (FR-014)
17. Export (FR-015)
18. Audit (FR-016)

---

## 14. Test plan

### 14.1 Unit test bắt buộc

| Test | Khẳng định |
|---|---|
| `TestWriteStaffStatus_NeverTouchesIsJoined` | Bắt câu update, khẳng định **không** chứa `isJoined`, `joinedAt`, `code` |
| `TestWriteStaffStatus_UpsertCreatesMinimalDoc` | User chưa có bản ghi → tạo mới chỉ với `user`, `partner`, `createdAt`, `statusStaff` |
| `TestClaimStaffCode_Concurrent` | 10 goroutine cùng chiếm 1 mã → đúng 1 thành công, 9 nhận `AlreadyUsed` |
| `TestClaimStaffCode_DistinguishErrors` | Mã không tồn tại → `Invalid`; mã đã dùng → `AlreadyUsed` |
| `TestConfirmIsStaff_ReleasesCodeOnWriteFailure` | Mock lỗi ở `writeStaffStatus` → mã trở về `isUsed:false`, `usedBy` bị unset |
| `TestNormalizeStaffCode` | ` prs8f2a1c ` → `PRS8F2A1C` |
| `TestIsValidStaffCodeFormat` | Từ chối < 6 ký tự, ký tự lạ, chuỗi rỗng |
| `TestIsStaff_AmbiguousIsGuest` | `""`, `"not_verify"`, `"NOT_EMPLOYEE"` đều trả `false` |
| `TestImportExcel_ReadsByColumnName` | File đảo thứ tự cột vẫn đọc đúng |
| `TestImportExcel_UpdatesGroupForUsedCode` | Mã đã dùng đổi nhóm → `user-segments` của `usedBy` được đồng bộ |
| `TestImportExcel_DryRunWritesNothing` | Dry-run → không tạo mã, không tạo segment |
| `TestEligibility_StaffAndSegmentAreAND` | Bật cả hai, thoả một → không đủ điều kiện |

### 14.2 Kịch bản tích hợp

1. **Happy path nhân viên** — import mã kèm nhóm → user nhập → có nhãn + vào segment + mã `isUsed` + có audit
2. **Happy path người ngoài** — bấm "Tôi không phải" → `statusStaff = not_employee`, **không** xuất hiện trong danh sách creator của partner (kiểm tra `isJoined` không bị set)
3. **Chia sẻ mã** — A dùng mã X thành công → B dùng mã X → `AlreadyUsed`
4. **Dò mã** — sai 3 lần ở modal + 3 lần ở trang Hồ sơ → bị khoá (chứng minh dùng chung bộ đếm)
5. **Chuyển bộ phận** — import lại với nhóm mới → user chuyển segment, thống kê phản ánh ngay
6. **Bỏ qua modal** — đóng 3 lần → hết hỏi, vẫn khai được từ Hồ sơ
7. **Gate campaign** — nhân viên nhóm A vào event giới hạn nhóm B → bị chặn với lý do đúng
8. **Nhân viên không nhóm** — mã không có `group` → bị chặn khỏi event có `allowedSegments`, admin đã được cảnh báo trước
9. **Gỡ nhãn** — admin gỡ → mã nhả ra, dùng lại được, user rời segment
10. **Cách ly partner** — bật cho Parasola, kiểm tra 12 partner khác không thấy modal và API từ chối

### 14.3 Kiểm tra trước khi merge

```bash
# 12 folder partner còn lại KHÔNG được có thay đổi nào
git diff --name-only develop... -- anker/ flamingo/ hdbank/ lusso/ mbbank/ \
  tpbank/ turborg/ vng/ vnpay/ vpbank/ wildrift/ yody/ frontend/
# → phải rỗng

# Không có chỗ nào so sánh statusStaff trực tiếp ngoài constants
grep -rn '"employee"' backend/ --include="*.go" | grep -v constants/staff_code.go
# → chỉ được xuất hiện trong aggregate pipeline (có comment giải thích)
```

---

## 15. Rollout và rollback

### Thứ tự release

1. Deploy backend + admin (cờ mặc định `false` → **không ai thấy gì**)
2. Ops import mã cho Parasola qua dry-run trước, kiểm tra kết quả, rồi import thật
3. Deploy `parasola/`
4. Bật `enableStaffCode` + `requireStaffCodeValidation` cho riêng Parasola
5. Theo dõi 48 giờ: tỉ lệ nhập thành công/thất bại, số lần chạm rate limit, số creator mới của Parasola

### Rollback

Tắt `options.enableStaffCode` của Parasola. Modal biến mất, API từ chối, **dữ liệu đã có giữ nguyên** không bị xoá. Không cần rollback code.

### Theo dõi sau release

| Chỉ số | Ngưỡng cảnh báo |
|---|---|
| Tỉ lệ nhập mã thất bại | > 30% → mã phát sai hoặc file import thiếu |
| Số user chạm rate limit / ngày | > 10 → nghi có dò mã |
| Lỗi transaction khi xác nhận | > 0 → xem log, có thể do truyền nhầm ctx thay vì SessionContext |
| Số creator mới của Parasola | tăng bất thường → **nghi `isJoined` bị ghi nhầm** |

---

## 16. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Ghi nhầm `isJoined` → thổi phồng số creator | **Cao** | Một hàm ghi duy nhất có comment cảnh báo + unit test bắt câu update + theo dõi số creator sau release |
| Truyền nhầm `ctx` thay `SessionContext` trong transaction | Trung bình | Lệnh nằm ngoài transaction, happy path vẫn đúng nên khó phát hiện — có test mô phỏng lỗi giữa chừng |
| Parasola phát mã tuần tự → dò được | Trung bình | Thống nhất yêu cầu entropy **trước khi** phát mã (PRD FR-007) |
| Import nhầm file 5.000 dòng | Trung bình | Dry-run bắt buộc + xoá theo `importBatchId` |
| Thống kê kỳ cũ đổi số | Thấp | Đã chọn phương án A có ý thức, in ghi chú trên mọi bảng/export |
| Rò rỉ sang partner khác | Thấp | Cờ mặc định `false` + kiểm tra diff trước merge + kịch bản test 10 |
| Aggregate thống kê chậm | Thấp | Index `{partner, statusStaff}`; cache Redis 5 phút nếu vượt 3 giây |

---

## 17. Câu hỏi cần chốt trước khi code

1. **Parasola chia nhóm theo tiêu chí gì, và đã có sẵn dữ liệu nhóm theo mã chưa?** Câu duy nhất còn có thể làm đổi phạm vi — không có cột nhóm thì FR-014 chỉ chạy được ở mức nhị phân. Cần hỏi trước khi Parasola phát mã.
2. **Xử lý nhân viên nghỉ việc?** Chưa có thu hồi hàng loạt; quy mô nhỏ nên tạm gỡ tay qua FR-009.

---

## 18. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Đổi từ bù trừ sang Mongo transaction (mục 4.2), bỏ job cron đối soát; chốt format mã theo T-Fluencers; nới mốc hiệu năng theo quy mô nhân viên nhỏ |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | Tech spec đầu tiên, bám PRD v1.3 |
