# Dossier tham chiếu — Luồng mã nhân viên T-Fluencer (Techcombank)

**Ngày:** 05/08/2026
**Mục đích:** Đầu vào cho PRD + Techspec "Luồng nhập mã nhân viên trên Ambassador"
**Repo tham chiếu:** `Viewboost-2025/techcombank` (backend Go, frontend Umi, admin Umi, dashboard Next.js)
**Repo đích:** `AT-Core/ambassador`

---

## 1. Kiến trúc — 3 lớp độc lập

T-Fluencer không có "một luồng nhập mã" mà có **3 lớp tách rời**, dùng nguồn dữ liệu khác nhau:

| Lớp | Mục đích | Nguồn dữ liệu | Phạm vi |
|---|---|---|---|
| **A. Định danh nhân viên** | Đánh dấu user là CBNV của partner | `user-partners.statusStaff` + `.code` | Theo partner, 1 lần/đời |
| **B. Gate campaign** | Giới hạn ai được nộp bài vào event | `events.options.{applyForStaff, staffCodes, applyForSegments}` | Theo từng event |
| **C. Thống kê** | Tách số liệu CBNV vs bên ngoài | Aggregate từ `user-partners.statusStaff` | Dashboard analytics |

Lưu ý: Lớp B có **nguồn mã thứ hai** (`events.options.staffCodes`) hoàn toàn tách khỏi `manage-codes` của Lớp A → đây là nợ kỹ thuật, không nên bê nguyên sang Ambassador.

---

## 2. Lớp A — Định danh nhân viên cấp partner

### 2.1 Model

```go
// internal/model/mg/user_partner.go
StatusStaff string `bson:"statusStaff"` // "employee" | "not_employee" | "not_verify"
Code        string `bson:"code"`         // mã NV user nhập khi confirm

// internal/model/mg/manage_code.go — bảng mã hợp lệ
type ManageCodeRaw struct {
    ID        AppID
    Partner   AppID
    Type      string    // constants.ManageCodeApplyForEmployee = "apply_for_employee"
    Code      string
    IsUsed    bool
    UsedBy    AppID
    UsedAt    time.Time
    CreatedAt, UpdatedAt time.Time
}
```

Hằng số canonical — `internal/constants/staff.go`:
```go
StatusStaffNotIdentify = "not_verify"
StatusStaffIsEmployee  = "employee"
StatusStaffNotEmployee = "not_employee"

func IsStaff(statusStaff string) bool { return statusStaff == StatusStaffIsEmployee }
```
Mirror ở FE dashboard: `dashboard/src/lib/staff.ts` (`STAFF_STATUS`, `isStaff()`, `staffGroup()`), có comment "Keep in sync with backend".

### 2.2 API

| Method | Endpoint | Auth | Chức năng |
|---|---|---|---|
| POST | `/users/confirm-is-staff` | Login | Xác nhận là NV, body `{partner, isStaff, code}` |
| GET | `/partners/:id/status-employee` | Login | Trả `{isOpenInputStaffCode: bool}` — cờ bung modal |
| GET/POST/DELETE | `/manage-codes` | Admin | CRUD mã |
| POST | `/manage-codes/import-excel` | Admin | Import Excel (form field `partner` + file) |

### 2.3 Logic `ConfirmIsStaff` (`pkg/public/service/user.go:177`)

1. Load user → lỗi nếu không tồn tại / bị ban
2. Load partner theo `body.Partner` → lỗi nếu không tồn tại
3. Nếu `isStaff = true`:
   - `code == ""` → lỗi `ReferralKeyCodeInvalid`
   - Nếu ENV `IS_VALIDATE_STAFF_CODE_EXISTS = true` → tìm trong `manage-codes` theo `{partner, code, type: apply_for_employee}`; không thấy → lỗi `ReferralKeyCodeInvalid`
4. Upsert `user-partners`: set `code` + `statusStaff` (`employee` / `not_employee`)

**Điểm cần sửa khi port sang Ambassador:**
- Không set `isUsed/usedBy/usedAt` → **một mã dùng lại vô hạn**, nhiều user share chung 1 mã. Ba trường này có trong model nhưng chỉ được set ở đường **migration** (`pkg/admin/service/migration.go:581`), không set ở đường live.
- Nhánh `isStaff = false` vẫn ghi `code` vào DB dù không validate gì.
- Không có audit trail (ai đổi, đổi lúc nào).

### 2.4 Gate hiện modal — `GetStatusEmployee` (`pkg/public/service/partner.go:256`)

```go
res = {IsOpenInputStaffCode: true}          // mặc định: bung modal
userPartner = findOne({user, partner})
if userPartner rỗng            → return true   // chưa join partner vẫn bung
if statusStaff ∈ {employee, not_employee} → false  // đã chọn rồi thì thôi
// statusStaff = "not_verify" hoặc rỗng → vẫn true
```

### 2.5 FE — modal chặn (`frontend/src/components/layout/main/header/components/modal-tcb-employee.tsx`)

Trigger: sau khi `getMe` thành công và có `partnerDetail._id` → dispatch `checkPartnerEmployeeStatus` → nếu `isOpenInputStaffCode` thì `visibleModalTcbEmployee = true` (`src/models/main.ts:129, 374`).

Đặc điểm UX:
- **Chặn cứng**: `onClose={() => {}}`, `keyboard={false}`, `hideFooter`, không nút Hủy — comment trong code: *"Cancel button removed - user must make a selection"*
- 2 thẻ chọn: "Tôi là nhân viên Techcombank" / "Tôi không thuộc Techcombank"
- **Cả 2 nhánh đều bắt buộc nhập mã**: `disabled={isTcbEmployee === null || !employeeCode.trim()}`. Nhánh không phải NV placeholder là *"Nhập mã được cấp"*
- 2 bước: chọn + nhập mã → màn xác nhận (cảnh báo vàng, tóm tắt lựa chọn + mã) → Confirm
- Hiển thị mã tự viết hoa (`value={employeeCode?.toUpperCase()}`) nhưng **gửi lên nguyên bản** (`code: employeeCode.trim()`) → lệch giữa cái user thấy và cái lưu DB
- Copy khẳng định: *"Lựa chọn này sẽ được ghi nhận cố định sau khi đăng ký và không thể thay đổi"*
- Payload gửi kèm `event: eventHome._id` nhưng BE `ConfirmIsStaffBody` **không dùng** field này

### 2.6 Admin UI — `admin/src/pages/manage-code/`

`index.tsx`, `model.ts`, `type.d.ts`, `components/{table, filter-less, create-modal, import-modal, modal}.tsx`

- Bảng: Partner | Code | isUsed | usedBy | usedAt | createdAt
- Filter: `partner`, `code`, `isUsed`
- Create: `{partner, code}` — chặn trùng theo `{partner, code}`
- Import: Dragger 1 file, **Excel 1 cột duy nhất là Code** (`ManageCodeXLSX{ Code string \`xlsx:"0"\` }`), bỏ dòng header, skip mã đã tồn tại, insert phần còn lại; `newCodes` rỗng → lỗi "không có dữ liệu để import"
- Partner tự điền nếu admin đang gắn với 1 partner
- Delete: chặn nếu `isUsed = true`
- Phân quyền: `s.Staff.IsAllowPartner(partnerID)` trên mọi thao tác

Bug nhỏ trong `ImportExcel`: kiểm tra `len(newCodes) == 0` hai lần liên tiếp, nhánh `CommonKeyAllCodesAlreadyExist` không bao giờ chạy.

---

## 3. Lớp B — Campaign dành riêng cho nhân viên

### 3.1 Model — `EventOpts`

```go
ApplyForStaff            bool              `bson:"applyForStaff,omitempty"`
ApplyForSegments         []AppID           `bson:"applyForSegments,omitempty"`
ApplyForSegmentsResponse []IDAndNameString `bson:"applyForSegmentsResponse,omitempty"`
StaffCodes               []string          `bson:"staffCodes,omitempty"`
```

```go
// user_event.go
type UserEventOpts struct {
    CodeInput      string `bson:"codeInput"`
    StatusEmployee string `bson:"statusEmployee"`
}
```

### 3.2 Điểm chặn khi nộp bài — `pkg/public/service/content.go:114-146`

Thứ tự kiểm tra:
1. `ApplyForStaff` → `userPartner.StatusStaff != employee` ⇒ lỗi `EventKeyApplyOnlyStaff`
2. `len(StaffCodes) > 0` → `userEvent.Options.CodeInput` không nằm trong `StaffCodes` ⇒ lỗi `EventKeyRequiredCode`
3. `len(ApplyForSegments) > 0` → đếm `user-segments` của user giao với danh sách ⇒ 0 thì lỗi `EventKeyNotApplySegment`

### 3.3 Nhập mã theo event — `POST /events/:id/input-code-join-event`

`InputCodeJoinEvent` (`pkg/public/service/event.go:53`):
- Event không tồn tại / không `IsValid()` ⇒ lỗi
- `Options == nil` hoặc `len(StaffCodes) == 0` ⇒ **return nil (no-op)**
- Mã không nằm trong `StaffCodes` ⇒ lỗi `EventKeyStaffCodeInvalid`
- Upsert `user-events` với `Options{CodeInput, StatusEmployee: "employee"}`

Đáng lưu ý: hàm này gán `StatusEmployee = employee` vào `user-events` **không hề kiểm tra** `user-partners.statusStaff` → trạng thái NV cấp event và cấp partner có thể mâu thuẫn nhau.

### 3.4 Cờ ra FE

- Event list (`event.go:515`): `IsRequireCode = len(Options.StaffCodes) > 0` — **không xét user đã nhập mã chưa**
- Event detail (`event.go:1074`): `IsRequireCode = true` chỉ khi user **chưa** có `CodeInput` hợp lệ
- Event detail (`event.go:1117`): nếu user không thuộc `ApplyForSegments` ⇒ `IsCanSummit = false`
- Event detail response trả `Options.ApplyForStaff` để FE hiện modal từ chối

FE: `modal-not-employee.tsx` — *"Thử thách này dành riêng cho nhân viên Techcombank"*, 2 nút "Đã hiểu" / "Khám phá thêm" (về trang chủ). Modal này **đóng được** (khác modal Lớp A).

### 3.5 Admin UI event (`admin/src/pages/event/components/modal.tsx`)

- `RcSwitchFormNew` cho `options.applyForStaff` (label i18n `onlyStaff`)
- `RcFormSelectNew mode="tags"` cho `options.staffCodes`, `tokenSeparators={[',', ' ', '\n']}` — Ops dán cả danh sách
- Select segment → map `applyForSegmentsResponse` → `applyForSegments`
- Có hàm `toBool` coerce vì form trả `'true'`/`'false'` dạng chuỗi

---

## 4. Lớp C — Thống kê CBNV vs bên ngoài

### 4.1 Backend

`aggregate_pipeline/creator_analytics.go`:
- `GetCreatorKPIsByStaffBreakdown(cond)` — `$lookup` `user-partners` với điều kiện `statusStaff = "employee"`, gán `statusStaff` theo `$size(staffPartner) > 0`, rồi `$sum` có điều kiện ra: `total/staff/guest` × `count/videos/views/cash`; cột `guest` = `total - staff`
- `GetCreatorsWithValidPostsCountByStaff` — tách số creator có bài hợp lệ
- Comment trong code ghi rõ đã fix bug lookup `user-partners` nhận nhầm row khi user thuộc nhiều partner

`internal/service/dashboard_analytics.go`: `TotalStaff`, `TotalStaffVideos`, `TotalStaffViews`, `TotalStaffCash` (`:95-104`, `:1497-1539`)

### 4.2 Dashboard (Next.js)

- `components/widgets/staff-badge.tsx` — badge Briefcase (đỏ) / User (xám), có `iconOnly`
- `components/filters/creator-filter.tsx` — `CreatorFilterMode = 'all' | 'staff' | 'guest' | 'custom'`, tác động toàn dashboard
- `components/tables/creator-columns.tsx` — cột "Nhóm" có sort + filter
- Breakdown inline trên 4 KPI card tab Influencer

### 4.3 Giới hạn quan trọng

**Chỉ nhị phân staff/guest.** Không có phân nhóm phòng ban / chi nhánh / khối. `Segment` bên TCB chỉ dùng để **gate campaign**, không dùng để breakdown thống kê. Yêu cầu Ambassador ghi rõ *"thống kê kết quả theo nhóm nhân viên"* ⇒ **phần này T-Fluencer chưa có, phải thiết kế mới.**

PRD tham chiếu: `accesstrade-docs/t-fluencers/dashboard-wiki-and-techcomer/prd.md` (360 dòng) — cấu trúc tốt để bám: Executive Summary → Business Objectives → Success Metrics → Personas → Scope in/out → FR đánh số + Must/Should/Could.

---

## 5. Thông điệp lỗi (VI/EN)

| Key | VI | EN |
|---|---|---|
| `eventKeyApplyOnlyStaff` | Xin lỗi, chương trình này chỉ áp dụng cho nhân viên của công ty! | Sorry, this program only applies to employees of the company! |
| `eventKeyRequiredCode` | Bạn cần nhập mã để có thể tham gia chương trình này! | You need to enter a code to participate in this program! |
| `eventKeyStaffCodeInvalid` | Mã để tham gia chương trình không hợp lệ! | Staff code invalid! |
| `eventKeyNotApplySegment` | Bạn không đủ điều kiện để tham gia chương trình này! | You do not meet the conditions to participate in this program! |
| `commonKeyCodeIsExisted` | Code đã tồn tại trong hệ thống! | Code is existed! |
| `commonKeyCodeAlreadyUsed` | Mã đã được sử dụng! | Code already used! |

`ReferralKeyCodeInvalid` bị tái sử dụng cho lỗi mã nhân viên — sai ngữ nghĩa, nên tách key riêng khi port.

---

## 6. Hiển thị dữ liệu NV cho Ops

- Admin `pages/user-partner/components/table.tsx:104` + `pages/influencer-management/components/table.tsx:159` — cột `statusStaff` qua `renderStaffStatus()`
- Export Excel/CSV hồ sơ: 2 cột "Nhân viên" (Có/Không) + "Mã nhân viên" — nguồn ưu tiên `UserPartnerRaw.Code`, fallback `UserRaw.StaffCode` (`export_user_social.go`)
- PRD: `accesstrade-docs/t-fluencers/prd-employee-code-profile.md`

Có **2 nguồn mã** ở TCB: `UserPartnerRaw.Code` (user tự nhập — nguồn chính) và `UserRaw.StaffCode` (chỉ khi admin tạo user thủ công — hầu như rỗng).

---

## 7. Migration/backfill

`pkg/admin/service/migration.go:~520-612` — import Excel `{userCode, hashtag, code}`:
1. Tìm user theo `userCode`
2. **Đối chiếu hashtag** (trim + lowercase) — sai thì skip
3. Set `manage-codes.{isUsed, usedBy, usedAt}`
4. Set `user-partners.{code, statusStaff: employee}`
5. In tổng kết `Total / Inserted / Updated / Skipped`

Đây là đường **duy nhất** ở TCB có set `isUsed`.

---

## 8. Đối chiếu năng lực Ambassador

| Thành phần | T-Fluencer | Ambassador | Ghi chú |
|---|---|---|---|
| `user-partners.statusStaff` | ✅ | ❌ | Comment cố ý bỏ tại `partner_creator_config.go:23` |
| `user-partners.code` | mã NV | ⚠️ **đã chiếm** | Dùng làm referral code (`migration.go:1109 UserPartnerReferralCode`) → phải thêm field mới |
| `manage-codes` + admin CRUD/import | ✅ | ❌ | Dựng mới toàn bộ |
| `confirm-is-staff`, `status-employee` | ✅ | ❌ | Dựng mới |
| Modal nhập mã (FE user) | ✅ | ❌ | Ambassador có **13 folder partner FE** riêng (anker, flamingo, hdbank, lusso, mbbank, parasola, tpbank, turborg, vng, vnpay, vpbank, wildrift, yody) + `frontend` chung |
| `Segment` + `UserSegment` | ✅ | ✅ **đã có** | BE model + `POST /user-segments/import-excel` + admin `pages/segment/` |
| `UserEvent` | ✅ có `Options` | ⚠️ có model, **thiếu `Options`** | Chỉ cần thêm nếu làm mã theo event |
| `EventOpts.applyForStaff/staffCodes/applyForSegments` | ✅ | ❌ | Ambassador `EventOpts` hiện chỉ có maxContentPerDay, applyForSources, hashtags, leaderboardPeriod, opsHub* |
| `ParticipationRequirements` | ❌ | ✅ **đã có** | enabled/email/phone/facebook + minFollowers/minAccountAge — chỗ cắm tự nhiên cho điều kiện "chỉ NV" |
| Feature flag theo partner | ENV toàn cục | ✅ `PartnerOpts` | Ambassador đã có pattern tenant-level toggle (`AllowResubmitRejectedContent`) — **tốt hơn ENV của TCB** |
| Thống kê staff/guest | ✅ | ❌ | Ambassador chưa có dashboard analytics tương đương |

### Kết luận kỹ thuật

Ambassador **không port 1-1 được**. Ba khác biệt kiến trúc bắt buộc phải xử lý:

1. `user-partners.code` đã bị referral code chiếm ⇒ field mã NV phải đặt tên khác (vd `staffCode`).
2. TCB bật/tắt bằng ENV toàn cục; Ambassador đa tenant thật (13 partner) ⇒ phải dùng `PartnerOpts` thay ENV.
3. Ambassador đã có `Segment`/`UserSegment` + `ParticipationRequirements` sẵn ⇒ tái dùng được thay vì bê `staffCodes` và nhánh gate riêng của TCB.

### Những chỗ **không nên** copy từ T-Fluencer

| Vấn đề ở TCB | Đề xuất cho Ambassador |
|---|---|
| Không set `isUsed/usedBy/usedAt` khi confirm ⇒ mã share vô hạn | Set ngay trong luồng confirm, hoặc chốt rõ chính sách "1 mã n người" |
| Người **không phải** NV cũng bắt buộc nhập mã | Chỉ bắt nhập mã ở nhánh "là nhân viên" |
| 2 nguồn mã tách rời (`manage-codes` vs `events.options.staffCodes`) | Một nguồn duy nhất |
| `input-code-join-event` set `statusEmployee` không đối chiếu cấp partner | Bỏ, hoặc đồng bộ 1 chiều |
| Tái dùng key lỗi `ReferralKeyCodeInvalid` cho mã NV | Tách key riêng |
| FE hiện mã viết hoa nhưng gửi nguyên bản | Chuẩn hoá (uppercase + trim) ở **backend** |
| `IsRequireCode` ở list không xét user đã nhập | Thống nhất logic list và detail |
| Không có audit trail | Ghi log thay đổi trạng thái NV |
| Chọn 1 lần vĩnh viễn, không có đường sửa | Cần đường Ops sửa khi user nhập nhầm |

---

## 9. Câu hỏi còn treo

1. Entry point trên Ambassador: modal chặn sau login như TCB, hay trang Hồ sơ, hay just-in-time khi tham gia campaign?
2. Chính sách mã: 1 mã 1 người hay dùng chung? Có cho sửa sau khi xác nhận không?
3. "Thống kê theo nhóm nhân viên" lấy nhóm từ đâu — TCB chưa có phần này?
4. Phạm vi campaign riêng cho NV ở phase 1: `applyForStaff`, hay kèm cả giới hạn theo nhóm?
5. Partner nào rollout trước? Có cần chạy đồng thời 13 FE folder không?
6. Docs lưu ở `AT-Core/accesstrade-core/tree/release/docs` (theo yêu cầu) hay `viewboost/accesstrade-docs` (nơi mọi PRD hiện hành đang nằm)?
