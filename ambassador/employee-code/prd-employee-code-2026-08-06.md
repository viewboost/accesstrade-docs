# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 2.0
**Project Level:** Level 2
**Status:** Draft
**Phạm vi:** **Chỉ partner Parasola.** 12 partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD cho tính năng cho phép **nhân viên Parasola** tự xác nhận danh tính nội bộ trên Ambassador bằng mã do Parasola cấp.

**Nguyên tắc của bản này: bám sát luồng T-Fluencers đang chạy production.** T-Fluencers đã vận hành thực tế và được nghiệm thu, nên lấy làm chuẩn. Chỉ thiết kế mới ở hai trường hợp:

1. **Ambassador khác kiến trúc nên không thể làm giống** (mục "Khác biệt bắt buộc")
2. **T-Fluencers không có phần đó** — cụ thể là thống kê theo nhóm nhân viên (mục FR-004, FR-012)

**Related Documents:**
- T-Fluencers Handbook: https://handbook.diso.vn/wiki/admin/nhan-vien/03-quan-ly-ma-nhan-vien
- T-Fluencers SRS: https://handbook.diso.vn/srs/admin-portal/14-code
- Dossier phân tích code T-Fluencers: [tf-reference-employee-code-flow.md](./tf-reference-employee-code-flow.md)

**Điểm cắm trong repo `AT-Core/ambassador`:**
- `backend/internal/model/mg/user_partner.go`, `partner.go`, `event.go`, `segment.go`, `user_segment.go`
- `backend/pkg/public/service/{user,partner,content}.go`
- `backend/pkg/admin/router/user_segment.go` — `POST /user-segments/import-excel` đã có
- `admin/src/pages/{user-partner,segment,event,partner}/`
- `parasola/src/components/layout/main/header/index.tsx` — điểm hiển thị modal

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`: `employee` \| `not_employee` \| `not_verify`. Rỗng = chưa khai, phân loại như `not_verify` |
| **Mã nhân viên** | Bản ghi trong `manage-codes`, do Admin import theo partner. Một mã dùng được cho nhiều người (theo mô hình T-Fluencers) |
| **Nhóm** | Đơn vị phân loại nhân viên (phòng ban / khu vực). Biểu diễn bằng `Segment` sẵn có của Ambassador |
| **Tenant-level feature toggle** | Cờ bật/tắt tính năng theo từng partner, lưu trong `PartnerOpts`. Khác ENV vốn có phạm vi toàn service |
| **Silent failure** | Lỗi xảy ra nhưng hệ thống vẫn báo thành công |
| **Idempotent** | Thực hiện nhiều lần cho cùng kết quả như một lần |

---

## 1. Executive Summary

Parasola muốn phân biệt **nhân viên nội bộ** với creator bên ngoài trên Ambassador, để chạy chiến dịch riêng cho nội bộ và báo cáo tách bạch đóng góp của hai nhóm.

Ambassador hiện **chưa có gì** cho việc này: `UserPartnerRaw` không có trường trạng thái nhân viên (có comment xác nhận cố ý bỏ tại `partner_creator_config.go:23`), không có bảng mã nhân viên, không có API xác nhận.

**Giải pháp:** port luồng T-Fluencers sang Ambassador. Parasola cấp mã cho nhân viên qua kênh nội bộ → Admin import danh sách mã → Nhân viên nhập mã trên web → Hệ thống đối chiếu và ghi trạng thái nhân viên. Trạng thái này dùng để chặn campaign nội bộ và tách số liệu báo cáo.

**Phần thêm mới so với T-Fluencers:** file import có thêm cột `group`, dùng để gán nhân viên vào `Segment`. Đây là điều kiện tiên quyết cho yêu cầu *"thống kê kết quả theo nhóm nhân viên"* — T-Fluencers chỉ tách nhị phân nhân viên/người ngoài, không có dữ liệu nhóm.

**Phạm vi:** backend và admin xây theo hướng dùng chung (bật/tắt bằng cờ), nhưng phase này **chỉ bật cho Parasola và chỉ làm frontend cho `parasola/`**.

---

## 2. Bối cảnh

### Hiện trạng Ambassador

| Thành phần | Trạng thái |
|---|---|
| `UserPartnerRaw.statusStaff` | ❌ Không có |
| `UserPartnerRaw.code` | ⚠️ **Đã bị chiếm** làm referral code (`migration.go:1109`) |
| Collection `manage-codes` | ❌ Không có |
| API xác nhận nhân viên | ❌ Không có |
| `Segment` + `UserSegment` + import Excel | ✅ **Đã có đủ** (BE + admin UI) |
| `EventOpts` | ⚠️ Có, nhưng thiếu `applyForStaff` / `staffCodes` / `applyForSegments` |
| `PartnerOpts` (tenant-level toggle) | ✅ **Đã có** pattern (`AllowResubmitRejectedContent`) |

### Khác biệt bắt buộc so với T-Fluencers

Ba chỗ **không thể** làm giống, do Ambassador khác kiến trúc:

| # | T-Fluencers | Ambassador phải làm | Lý do |
|---|---|---|---|
| 1 | Mã nhân viên lưu ở `UserPartnerRaw.Code` | Lưu ở field mới `staffCode` | `Code` ở Ambassador đã là referral code |
| 2 | Tạo `UserPartnerRaw` với `IsJoined: true, JoinedAt: now` | **Không được ghi** `isJoined`/`joinedAt` | `isJoined` ở Ambassador là điều kiện xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi user thực sự tham gia (`:491`). Ghi ở đây sẽ làm sai lệch tăng số creator của Parasola |
| 3 | Bật/tắt bằng ENV `IS_VALIDATE_STAFF_CODE_EXISTS` | Bật/tắt bằng `PartnerOpts` | Ambassador có 13 partner; ENV toàn service nghĩa là bật cho Parasola là bật cho cả 12 partner kia |

Ngoài ba điểm trên, mọi hành vi khác **giữ nguyên như T-Fluencers**.

---

## 3. User Personas

**P1. Nhân viên Parasola** — được cấp mã qua kênh nội bộ. Nhập mã một lần khi đăng nhập.

**P2. Creator bên ngoài trên Parasola** — chiếm đa số người dùng.

**P3. Admin/Ops AccessTrade** — nhận file mã từ Parasola, import, theo dõi danh sách mã.

**P4. Marketing Parasola** — cấu hình chiến dịch chỉ dành cho nhân viên hoặc cho nhóm cụ thể, xem báo cáo theo nhóm.

**P5. Người dùng của 12 partner còn lại** — **không được thấy bất kỳ thay đổi nào.** Đây là ràng buộc, không phải mục tiêu.

---

## 4. Functional Requirements

### FR-001: Trạng thái nhân viên trên `UserPartnerRaw`

**Priority:** Must Have

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/user_partner.go — UserPartnerRaw
StatusStaff string `bson:"statusStaff,omitempty" json:"statusStaff,omitempty"` // "employee" | "not_employee" | "not_verify"
StaffCode   string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`     // mã nhân viên user đã nhập
```

```go
// backend/internal/constants/staff_code.go — mới
const (
    StatusStaffNotVerify   = "not_verify"
    StatusStaffIsEmployee  = "employee"
    StatusStaffNotEmployee = "not_employee"
    ManageCodeApplyForEmployee = "apply_for_employee"
)

// IsStaff là quy tắc canonical duy nhất để phân loại nhân viên.
// Mọi giá trị mơ hồ (rỗng, not_verify) đều KHÔNG tính là nhân viên,
// để số liệu nhân viên không bị sai lệch tăng do dữ liệu không hợp lệ.
// Giữ đồng bộ với parasola/src/utils/staff.ts
func IsStaff(statusStaff string) bool { return statusStaff == StatusStaffIsEmployee }
```

Đặt tên `staffCode` thay vì `code` — xem Khác biệt bắt buộc #1.

**Acceptance Criteria:**
- [ ] 2 field `omitempty`, bản ghi cũ không bị ảnh hưởng
- [ ] `constants.IsStaff()` là nơi duy nhất định nghĩa quy tắc, không nơi nào so sánh chuỗi trực tiếp
- [ ] Có mirror `isStaff()` phía FE kèm comment yêu cầu giữ đồng bộ
- [ ] `UserPartnerRaw.Code` (referral) không bị đụng

---

### FR-002: Collection `manage-codes`

**Priority:** Must Have

Giữ nguyên cấu trúc của T-Fluencers, thêm 2 field phục vụ phân nhóm.

```go
// backend/internal/model/mg/manage_code.go — mới
type ManageCodeRaw struct {
    ID      AppID  `bson:"_id"`
    Partner AppID  `bson:"partner"`
    Type    string `bson:"type"`  // constants.ManageCodeApplyForEmployee
    Code    string `bson:"code"`

    // THÊM MỚI so với T-Fluencers — phục vụ thống kê theo nhóm (FR-004, FR-012)
    Group   string `bson:"group,omitempty"`   // tên nhóm từ cột "group" của file import
    Segment AppID  `bson:"segment,omitempty"` // segment tương ứng, tạo tự động khi import

    IsUsed    bool      `bson:"isUsed"`
    UsedBy    AppID     `bson:"usedBy,omitempty"`
    UsedAt    time.Time `bson:"usedAt,omitempty"`
    CreatedAt time.Time `bson:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt"`
}
```

**Ba trường `isUsed`/`usedBy`/`usedAt` giữ đúng ngữ nghĩa T-Fluencers:** chỉ được ghi bởi script migration/backfill, **không** ghi ở luồng người dùng nhập mã. Nghĩa là **một mã dùng được cho nhiều người** — đây là hành vi của T-Fluencers và được giữ nguyên.

Hệ quả cần biết: mã hiển thị `isUsed: false` kể cả khi đã có người dùng; không truy được ai đã dùng mã nào từ phía `manage-codes`. Muốn biết ai là nhân viên thì tra `user-partners.statusStaff`.

**Index:**
```
{ partner: 1, code: 1 }   — tra cứu khi xác nhận
{ partner: 1, isUsed: 1 } — filter danh sách admin
```

**Acceptance Criteria:**
- [ ] Tạo mã trùng trong cùng partner → báo lỗi (kiểm tra ở tầng service như T-Fluencers)
- [ ] `Group` optional — partner chưa phân nhóm vẫn dùng được
- [ ] Luồng `confirm-is-staff` **không** ghi `isUsed`/`usedBy`/`usedAt`

---

### FR-003: Admin — CRUD mã nhân viên

**Priority:** Must Have

Trang `/manage-code`, port từ `admin/src/pages/manage-code/` của T-Fluencers.

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/manage-codes` | Danh sách, filter `partner`, `code`, `group`, `isUsed` |
| `POST` | `/manage-codes` | Tạo lẻ `{partner, code, group?}` |
| `DELETE` | `/manage-codes/:id` | Xoá — từ chối nếu `isUsed = true` |
| `POST` | `/manage-codes/import-excel` | Import hàng loạt (FR-004) |

**Bảng:** Mã \| Partner \| Nhóm \| Đã dùng \| Người dùng \| Ngày dùng \| Ngày tạo

Mọi thao tác qua kiểm tra quyền partner theo pattern `IsAllowPartner` sẵn có.

**Acceptance Criteria:**
- [ ] CRUD hoạt động, chặn trùng mã trong cùng partner
- [ ] Xoá mã đã dùng → từ chối kèm thông báo
- [ ] Filter `group` hoạt động (cột mới)

---

### FR-004: Import mã hàng loạt kèm nhóm

**Priority:** Must Have

**Đây là phần thêm mới so với T-Fluencers.** File import của T-Fluencers chỉ có một cột mã, nên không có dữ liệu nhóm — và đó là lý do T-Fluencers không làm được thống kê theo nhóm. Ambassador cần cột `group`.

**Format file:**

| `code` (bắt buộc) | `group` (tuỳ chọn) |
|---|---|
| `PRS_A3F91B2C` | `Nhóm Miền Bắc` |
| `PRS_7D0E4A88` | `Nhóm Miền Bắc` |
| `PRS_C15B9F30` | `Khối Vận hành` |

**Xử lý:**
1. Đọc header **theo tên cột** (`code`, `group`) — T-Fluencers đọc theo vị trí (`xlsx:"0"`), file sai thứ tự cột sẽ silent failure
2. Chuẩn hoá `code`: TRIM + UPPERCASE
3. Với mỗi `group` chưa có: tạo `SegmentRaw{Name: group, Partner: partnerId}`; đã có thì tái dùng
4. Gán `ManageCodeRaw.Segment`
5. Mã đã tồn tại → skip (như T-Fluencers), ghi lại số dòng
6. Insert phần còn lại

**Kết quả trả về:**
```json
{ "total": 200, "inserted": 187, "skipped": 13,
  "segmentsCreated": ["Nhóm Miền Bắc", "Khối Vận hành"],
  "errors": [{ "row": 45, "code": "", "reason": "Mã trống" }] }
```

**Acceptance Criteria:**
- [ ] Đọc theo **tên cột**, không theo vị trí
- [ ] File thiếu cột `code` → từ chối toàn bộ, không import một phần
- [ ] Cột `group` trống → mã vẫn import được, không gán segment
- [ ] Segment mới tạo đúng partner, không tạo trùng khi nhiều dòng cùng nhóm
- [ ] Báo cáo liệt kê từng dòng lỗi kèm số dòng

---

### FR-005: API kiểm tra trạng thái nhân viên

**Priority:** Must Have

Giữ nguyên endpoint và response của T-Fluencers.

```
GET /partners/:id/status-employee        (yêu cầu đăng nhập)
→ { "isOpenInputStaffCode": true }
```

**Logic:**
```
partner chưa bật tính năng             → false
chưa có bản ghi user-partners          → true
statusStaff ∈ {employee, not_employee} → false
còn lại (rỗng / not_verify)            → true
```

Chỉ khác T-Fluencers ở dòng đầu — kiểm tra `PartnerOpts.EnableStaffCode` (Khác biệt bắt buộc #3).

**Acceptance Criteria:**
- [ ] Partner tắt tính năng → luôn `false`
- [ ] Đã chọn rồi → `false`
- [ ] Chưa join partner → `true`

---

### FR-006: API xác nhận nhân viên

**Priority:** Must Have

```
POST /users/confirm-is-staff        { partner, isStaff, code }
```

**Luồng xử lý** — giữ nguyên T-Fluencers:
```
1. Load user      → không tồn tại / bị ban ⇒ lỗi
2. Load partner   → không tồn tại ⇒ lỗi
                  → chưa bật EnableStaffCode ⇒ lỗi
3. Nếu isStaff = true:
     code rỗng ⇒ lỗi
     nếu partner bật RequireStaffCodeValidation:
         tìm manage-codes {partner, code, type}
         không thấy ⇒ lỗi "Mã không hợp lệ"
4. Upsert user-partners: statusStaff + staffCode
5. Nếu mã có Segment → upsert user-segments {user, segment}   ← phần mới, phục vụ FR-012
```

Bước 5 là phần thêm cho phân nhóm. Idempotent — nhập lại cùng mã không tạo bản ghi trùng.

**Không ghi** `isUsed`/`usedBy`/`usedAt` — giữ đúng hành vi T-Fluencers (xem FR-002).

#### ⚠️ Quy tắc ghi `user-partners`

T-Fluencers tạo bản ghi mới với `IsJoined: true, JoinedAt: time.Now()`. **Ambassador không được làm vậy** — xem Khác biệt bắt buộc #2.

Thao tác ghi duy nhất được phép:
```go
opts := options.Update().SetUpsert(true)
UserPartnerDAO().UpdateOne(ctx, ..., bson.M{"user": userId, "partner": partnerId}, bson.M{
    "$set": bson.M{
        "statusStaff": status,
        "staffCode":   code,        // bỏ qua khi isStaff = false
        "updatedAt":   time.Now(),
    },
    "$setOnInsert": bson.M{
        "_id": modelmg.NewAppID(), "user": userId, "partner": partnerId,
        "createdAt": time.Now(),
    },
}, opts)
```

**Cấm tuyệt đối:** `isJoined`, `joinedAt`, `code` (referral), `statistic`, `contentStatistic`.

**Thông báo lỗi** — dùng key riêng, không tái sử dụng key referral như T-Fluencers:

| Key | VI | EN |
|---|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |

**Acceptance Criteria:**
- [ ] **`isJoined`/`joinedAt` không xuất hiện trong bất kỳ câu ghi nào** — có test khẳng định
- [ ] User chưa từng tham gia Parasola, bấm "Tôi không phải nhân viên" → không bị tính vào danh sách creator của partner
- [ ] `UserPartnerRaw.Code` không bị thay đổi
- [ ] Xác nhận thành công + mã có nhóm → user xuất hiện trong segment tương ứng
- [ ] Nhập lại cùng mã → không tạo bản ghi `user-segments` trùng

---

### FR-007: Modal xác nhận trên Frontend Parasola

**Priority:** Must Have

**Port nguyên UX của T-Fluencers** (`modal-tcb-employee.tsx`). Chỉ làm trong `parasola/`.

**Điểm cắm:** `parasola/src/components/layout/main/header/index.tsx` đã có sẵn cơ chế này cho màn đồng ý điều khoản — `initApp` gọi `users/me` → `useEffect [user]` kiểm tra `privacyAccepted === false` → hiển thị `ModalCompleteRegistration`. Modal mã nhân viên đi theo đúng cơ chế đó, dùng chung component `AppModal`.

Thứ tự ưu tiên khi cả hai cùng thoả điều kiện: **modal điều khoản trước, modal nhân viên sau** — không hiển thị chồng.

**Hành vi — giống T-Fluencers:**
- Modal **blocking**: `onClose={() => {}}`, `keyboard={false}`, `hideFooter`, không nút Hủy
- Hai lựa chọn: "Tôi là nhân viên Parasola" / "Tôi không thuộc Parasola"
- **Cả hai nhánh đều bắt buộc nhập mã**, nút Xác nhận khoá tới khi có mã
- Hai bước: chọn + nhập mã → màn xác nhận tóm tắt → Confirm
- Lựa chọn ghi nhận cố định, không tự thay đổi được
- Lỗi từ backend hiển thị dưới ô mã, không đóng modal

**Sửa một lỗi hiển thị của T-Fluencers:** bản TCB hiển thị mã viết hoa (`value={employeeCode?.toUpperCase()}`) nhưng gửi lên nguyên bản (`code: employeeCode.trim()`) — user thấy `ABC123`, DB lưu `abc123`. Ambassador chuẩn hoá ở backend để giá trị lưu luôn khớp giá trị hiển thị.

**Phạm vi triển khai:**

| Folder | Làm gì |
|---|---|
| `parasola/` | ✅ Toàn bộ FR-007, FR-009 |
| `frontend/` và 12 folder partner còn lại | ❌ **Không đụng tới** |

**Acceptance Criteria:**
- [ ] Modal không đóng được bằng X, ESC hay click ra ngoài
- [ ] Cả hai nhánh đều yêu cầu nhập mã
- [ ] Hai bước, có màn xác nhận trước khi gửi
- [ ] Giá trị lưu trong DB khớp giá trị user thấy
- [ ] Partner tắt tính năng → modal không xuất hiện
- [ ] Không hiển thị chồng với `ModalCompleteRegistration`
- [ ] **12 folder partner còn lại không có thay đổi nào trong diff**

---

### FR-008: Chiến dịch dành riêng cho nhân viên

**Priority:** Must Have

Port đủ **cả ba cơ chế** của T-Fluencers vào `EventOpts`:

```go
// backend/internal/model/mg/event.go — EventOpts
ApplyForStaff    bool     `bson:"applyForStaff,omitempty" json:"applyForStaff"`
StaffCodes       []string `bson:"staffCodes,omitempty" json:"staffCodes,omitempty"`
ApplyForSegments []AppID  `bson:"applyForSegments,omitempty" json:"applyForSegments,omitempty"`
```

**Điểm chặn khi nộp bài** — thứ tự kiểm tra như T-Fluencers (`content.go:114-146`):

| Điều kiện | Kiểm tra | Lỗi |
|---|---|---|
| `ApplyForStaff` | `user-partners.statusStaff == "employee"` | Chương trình này chỉ áp dụng cho nhân viên của công ty |
| `StaffCodes` | `user-events.options.codeInput` nằm trong danh sách | Bạn cần nhập mã để tham gia chương trình này |
| `ApplyForSegments` | đếm `user-segments` giao với danh sách > 0 | Bạn không đủ điều kiện tham gia chương trình này |

**Mã riêng theo event:**
```
POST /events/:id/input-code-join-event   { code }
→ upsert user-events.options { codeInput, statusEmployee }
```

`UserEventRaw` của Ambassador hiện **thiếu** field `Options` — cần bổ sung:
```go
type UserEventOpts struct {
    CodeInput      string `bson:"codeInput" json:"codeInput"`
    StatusEmployee string `bson:"statusEmployee" json:"statusEmployee"`
}
```

**Cờ ra FE:** `isRequireCode` trên event list và event detail, logic như T-Fluencers.

**Admin UI** (`admin/src/pages/event/components/modal.tsx`):
- Switch `applyForStaff`
- Select `mode="tags"` cho `staffCodes`, `tokenSeparators={[',', ' ', '\n']}`
- Select nhiều cho `applyForSegments`, chỉ liệt kê segment của partner đang chọn

**Acceptance Criteria:**
- [ ] Ba điều kiện hoạt động độc lập và kết hợp được
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] Chỉ chọn được segment thuộc partner của event
- [ ] Thông báo lỗi đúng từng trường hợp, có VI và EN

---

### FR-009: Thông báo khi không đủ điều kiện

**Priority:** Must Have

Port `modal-not-employee.tsx` của T-Fluencers.

| Trường hợp | Tiêu đề | Hành động |
|---|---|---|
| Không phải nhân viên, vào event `applyForStaff` | Thử thách này dành riêng cho nhân viên Parasola | **Đã hiểu** / **Khám phá thêm** |
| Không thuộc nhóm được phép | Bạn không đủ điều kiện tham gia chương trình này | **Đã hiểu** / **Khám phá thêm** |

Modal này **đóng được** — khác modal FR-007. Giống T-Fluencers.

**Acceptance Criteria:**
- [ ] Modal đóng được, "Khám phá thêm" điều hướng về trang chủ
- [ ] Có VI và EN

---

### FR-010: Bật/tắt theo từng partner

**Priority:** Must Have

Thay ENV của T-Fluencers bằng `PartnerOpts` — xem Khác biệt bắt buộc #3.

```go
// backend/internal/model/mg/partner.go — PartnerOpts
// EnableStaffCode bật luồng nhập mã nhân viên cho partner này.
EnableStaffCode bool `bson:"enableStaffCode,omitempty" json:"enableStaffCode"`
// RequireStaffCodeValidation tương đương ENV IS_VALIDATE_STAFF_CODE_EXISTS
// của T-Fluencers, nhưng phạm vi theo partner.
RequireStaffCodeValidation bool `bson:"requireStaffCodeValidation,omitempty" json:"requireStaffCodeValidation"`
```

**UI:** 2 toggle trong section "Cấu hình nhân viên" của `admin/src/pages/partner/components/modal.tsx`, theo pattern 2 toggle BXH đã có.

**Acceptance Criteria:**
- [ ] Mặc định cả 2 = `false` — 13 partner hiện tại không đổi hành vi
- [ ] **Chỉ Parasola được bật khi release**
- [ ] Tắt `EnableStaffCode` → modal biến mất, API từ chối, dữ liệu đã có giữ nguyên

---

### FR-011: Admin — hiển thị và lọc theo nhân viên/nhóm

**Priority:** Must Have

Bổ sung vào `admin/src/pages/user-partner/`:

**Cột mới:** `Nhân viên` (Có/Không) \| `Mã nhân viên` \| `Nhóm`
**Filter mới:** `statusStaff` (Tất cả / Nhân viên / Không phải / Chưa xác nhận), `segment` (chọn nhiều)

**Acceptance Criteria:**
- [ ] Ba cột hiển thị đúng, giá trị rỗng hiện `—`
- [ ] Filter hoạt động độc lập và kết hợp với filter sẵn có

---

### FR-012: Thống kê theo nhóm nhân viên

**Priority:** Must Have

**T-Fluencers không có phần này.** Dashboard T-Fluencers chỉ tách nhị phân staff/guest (`GetCreatorKPIsByStaffBreakdown`) vì file import mã chỉ một cột, không có dữ liệu nhóm. Yêu cầu gốc của Ambassador ghi rõ *"Có thống kê kết quả theo nhóm nhân viên"* nên phần này thiết kế mới.

**Vị trí:** tab mới trong `admin/src/pages/event-statistic/`.

| Nhóm | Số người | Đã tham gia | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|
| **Tổng — Nhân viên** | 210 | 168 | 1.180 | 3,1tr | 190tr |
| ├ Nhóm Miền Bắc | 85 | 72 | 520 | 1,4tr | 82tr |
| ├ Nhóm Miền Nam | 78 | 61 | 410 | 1,1tr | 68tr |
| ├ Khối Vận hành | 35 | 28 | 200 | 0,5tr | 33tr |
| └ Chưa phân nhóm | 12 | 7 | 50 | 0,1tr | 7tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9,3tr | 650tr |

**Quy tắc tính** — giữ nguyên quy ước của T-Fluencers:
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên, không cộng dồn từng loại
- Không tính bài đã bị huỷ
- Nhân viên chưa được gán nhóm gom vào dòng "Chưa phân nhóm"

**Phân loại theo trạng thái hiện tại, không snapshot.** Nhân viên xác nhận muộn thì số liệu kỳ cũ sẽ thay đổi theo. Đây cũng là hành vi của T-Fluencers; khác ở chỗ Ambassador **in ghi chú rõ** trên bảng và export:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo.*

**Acceptance Criteria:**
- [ ] Tổng các nhóm con = dòng tổng "Nhân viên"
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] Có ghi chú "không bao gồm bài đã huỷ" và ghi chú phân loại theo trạng thái hiện tại
- [ ] Tải xong dưới 3 giây

---

### FR-013: Xuất dữ liệu

**Priority:** Should Have

Bổ sung 3 cột `Nhân viên` \| `Mã nhân viên` \| `Nhóm` vào file export hồ sơ/creator hiện có; thêm nút export cho bảng FR-012.

Nguồn dữ liệu như T-Fluencers: ưu tiên `UserPartnerRaw.StaffCode`, fallback `UserRaw.StaffCode` nếu có.

**Acceptance Criteria:**
- [ ] Excel và CSV đều có 3 cột mới
- [ ] Cột "Nhân viên" xuất "Có"/"Không"

---

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
- Mọi field mới `omitempty`, không cần migration dữ liệu
- `EnableStaffCode` mặc định `false` — 13 partner hiện tại không đổi hành vi
- Không đụng `UserPartnerRaw.Code`

### NFR-002: Data Integrity
- Luồng `confirm-is-staff` không bao giờ ghi `isJoined`/`joinedAt`/`code`
- Upsert `user-segments` idempotent
- Xoá segment bị từ chối khi còn được `manage-codes.segment` hoặc `events.options.applyForSegments` tham chiếu

### NFR-003: Performance
- Quy mô nhân viên Parasola nhỏ. Các mốc dưới đây chỉ để chặn thiết kế sai kiểu N+1, không phải bài toán tải thật. **Không tối ưu sớm.**
- Import 1.000 mã < 10 giây
- Thống kê FR-012 < 3 giây

### NFR-004: i18n
- Chuỗi mới có cả VI và EN
- Tên nhóm lấy nguyên từ file import, không dịch

---

## 6. Epics

| Epic | FR | Nội dung |
|---|---|---|
| **EPIC-001** Nền tảng | FR-001, 002, 010 | Model, constants, collection, index, tenant toggle |
| **EPIC-002** Quản lý mã | FR-003, 004 | Admin CRUD + import kèm nhóm |
| **EPIC-003** Luồng người dùng | FR-005, 006, 007 | API + modal Parasola |
| **EPIC-004** Chiến dịch | FR-008, 009 | Ba cơ chế gate + modal từ chối |
| **EPIC-005** Báo cáo | FR-011, 012, 013 | Cột, filter, thống kê theo nhóm, export |

---

## 7. Kiến trúc

### Luồng dữ liệu

```
Parasola phát mã cho nhân viên (kênh nội bộ)
        │
        ▼
Admin import Excel (code | group)
        ├──► manage-codes  {partner, type, code, group, segment}
        └──► segments      tạo tự động theo cột group
        │
        ▼
Nhân viên nhập mã  →  POST /users/confirm-is-staff
        ├──► user-partners  {statusStaff, staffCode}
        └──► user-segments  {user, segment}      ← phần thêm mới
        │
   ┌────┴───────────────┬────────────────────┐
   ▼                    ▼                    ▼
Gate chiến dịch      Thống kê            Hiển thị/Export
content.go           theo nhóm           admin user-partner
```

### Luồng xác nhận

```
Đăng nhập → users/me → có partnerDetail
  → GET /partners/:id/status-employee
  → isOpenInputStaffCode = false → kết thúc
  → true → hiển thị modal blocking
       Bước 1: chọn nhánh + nhập mã (cả hai nhánh đều bắt buộc)
       Bước 2: màn xác nhận → Confirm
       → POST /users/confirm-is-staff
            ├─ thành công → ghi statusStaff + staffCode + segment
            └─ mã sai     → hiển thị lỗi dưới ô mã, giữ modal
```

---

## 8. Implementation Scope

### Thay đổi cần làm

| Vùng | File | Nội dung |
|---|---|---|
| **Model** | `model/mg/user_partner.go` | +2 field |
| **Model** | `model/mg/manage_code.go` | File mới |
| **Model** | `model/mg/user_event.go` | +`Options` (`UserEventOpts`) |
| **Model** | `model/mg/partner.go` | +2 field trong `PartnerOpts` |
| **Model** | `model/mg/event.go` | +3 field trong `EventOpts` |
| **Constants** | `constants/staff_code.go` | File mới |
| **DAO** | `module/database/mongodb/` | `ManageCodeDAO` + collection + index |
| **Public API** | `pkg/public/{router,handler,service}/user.go` | `confirm-is-staff` |
| **Public API** | `pkg/public/{router,handler,service}/partner.go` | `status-employee` |
| **Public API** | `pkg/public/{router,handler,service}/event.go` | `input-code-join-event` |
| **Public API** | `pkg/public/service/content.go` | 3 điểm chặn khi nộp bài |
| **Admin API** | `pkg/admin/{router,handler,service}/manage_code.go` | File mới |
| **Admin API** | `pkg/admin/service/user_partner.go` | Trả thêm field + filter |
| **Export** | `pkg/admin/service/export_*.go` | +3 cột |
| **Thống kê** | `aggregate_pipeline/` | Pipeline breakdown theo nhóm |
| **Locale** | `internal/locale/staff_code.go` + `properties/{vi,en}/` | Key mới, không tái dùng key referral |
| **Admin UI** | `admin/src/pages/manage-code/` | Trang mới |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | +2 toggle |
| **Admin UI** | `admin/src/pages/event/components/modal.tsx` | +1 switch, +2 select |
| **Admin UI** | `admin/src/pages/user-partner/` | +3 cột, +2 filter |
| **Admin UI** | `admin/src/pages/event-statistic/` | Tab thống kê theo nhóm |
| **Frontend** | `parasola/src/components/layout/main/header/index.tsx` | Trigger modal |
| **Frontend** | `parasola/src/components/layout/main/header/components/modal-staff-code.tsx` | Component mới |
| **Frontend** | `parasola/src/components/.../modal-not-employee.tsx` | Component mới |
| **Frontend** | `parasola/src/models/main.ts`, `configs/api.ts`, `utils/staff.ts` | State, endpoint, mirror `isStaff` |

### KHÔNG làm

- **Không đụng `frontend/` và 12 folder partner còn lại** (`anker`, `flamingo`, `hdbank`, `lusso`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `vpbank`, `wildrift`, `yody`)
- Không bật cờ cho partner nào ngoài Parasola
- Không dùng lại `UserPartnerRaw.Code`
- Không ghi `isJoined`/`joinedAt` trong luồng xác nhận
- Không dùng ENV toàn cục
- Không dựng dashboard analytics riêng — bổ sung vào trang admin đã có
- Không đụng logic tính thưởng, xếp hạng, duyệt nội dung
- Không tự sinh mã — Parasola cấp, Admin import

---

## 9. Assumptions

1. Parasola phát mã cho nhân viên qua kênh nội bộ; Ambassador không gửi mã
2. Parasola cung cấp được file danh sách mã, kèm cột nhóm nếu muốn thống kê theo nhóm
3. Trạng thái nhân viên gắn theo partner, không phải toàn hệ thống
4. Tên nhóm trong file import là duy nhất trong phạm vi một partner
5. `parasola/` tiếp tục dùng Umi + dva; modal mới bám pattern `ModalCompleteRegistration` sẵn có

---

## 10. Out of Scope

- Triển khai cho 12 partner còn lại — chỉ cần bật cờ + làm frontend folder tương ứng
- Tích hợp SSO / HR API của Parasola
- Tự sinh mã hàng loạt trong hệ thống
- Hạn dùng cho mã, thu hồi mã hàng loạt
- Phân cấp nhóm nhiều tầng — phase 1 chỉ một tầng
- Snapshot trạng thái nhân viên theo từng bài đăng
- Phân quyền xem thống kê theo nhóm — admin partner thấy toàn bộ

---

## 11. Traceability Matrix

| Yêu cầu gốc | FR đáp ứng |
|---|---|
| Có nơi để nhân viên nhập mã | FR-005, FR-006, FR-007 |
| Có thống kê kết quả theo nhóm nhân viên | FR-004, FR-011, FR-012, FR-013 |
| Có campaign dành riêng cho nhân viên | FR-008, FR-009 |
| Import nhân viên để về sau còn phân loại | FR-002, FR-003, FR-004 |

| Priority | FR |
|---|---|
| **Must Have** (12) | FR-001 → FR-012 |
| **Should Have** (1) | FR-013 |

---

## 12. Resolved Questions

1. **Có bám theo T-Fluencers không?** → **Có.** T-Fluencers đã chạy production và được nghiệm thu; lấy làm chuẩn. Chỉ thiết kế mới ở chỗ Ambassador khác kiến trúc (3 điểm ở mục 2) và chỗ T-Fluencers không có (thống kê theo nhóm).

2. **Một mã dùng được cho mấy người?** → **Nhiều người**, như T-Fluencers. Luồng xác nhận không ghi `isUsed`.

3. **Modal có chặn không?** → **Có**, blocking như T-Fluencers. Cả hai nhánh đều nhập mã. Lựa chọn cố định.

4. **Có port `staffCodes` theo event không?** → **Có**, đủ cả ba cơ chế của T-Fluencers.

5. **Format mã?** → Theo quy ước T-Fluencers: `PRS_<8 hex ngẫu nhiên viết hoa>`, ví dụ `PRS_A3F91B2C`.

6. **Bật/tắt bằng gì?** → `PartnerOpts` thay ENV. Bắt buộc, vì Ambassador có 13 partner.

7. **Tên trường mã?** → `staffCode`, vì `UserPartnerRaw.Code` đã là referral code.

8. **Nhóm nhân viên lấy từ đâu?** → Cột `group` trong file import, tự tạo và gán `Segment`. Phần thêm mới vì T-Fluencers không có.

---

## 13. Open Questions

1. **Parasola có sẵn dữ liệu nhóm cho từng mã chưa, và chia nhóm theo tiêu chí gì?** Nếu không có cột nhóm, FR-012 chỉ ra được bảng nhị phân nhân viên/người ngoài — tức là một trong ba mục tiêu gốc không đạt. Cần hỏi trước khi Parasola phát mã, vì cột nhóm phải có ngay từ file import đầu tiên.

2. **Với mô hình một mã dùng chung, có nên đặt mã theo nhóm luôn không?** Ví dụ `PRS_MIENBAC`, `PRS_VANHANH` — mỗi nhóm một mã, gửi vào nhóm chat tương ứng. Cách này bỏ được cột `group` trong file import và Ops chuẩn bị nhẹ hơn hẳn. Đánh đổi: mã dễ đoán hơn.

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | **Viết lại theo hướng bám T-Fluencers.** Bỏ các thay đổi tự đề xuất ở v1.x: single-use code + claim atomic + transaction, rate limit, audit trail, dry-run + xoá theo lô, giới hạn số lần hiển thị modal, modal đóng được, chỉ nhánh nhân viên nhập mã, sửa lại trạng thái sau khi xác nhận, bỏ `staffCodes` theo event. Giữ đúng 3 khác biệt bắt buộc do kiến trúc Ambassador (`staffCode`, không ghi `isJoined`, `PartnerOpts` thay ENV) và phần T-Fluencers không có (cột `group` + thống kê theo nhóm). 16 FR → 13 FR |
| 1.6 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.5 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ kỹ thuật, bổ sung mục 0 |
| 1.4 | 2026-08-06 | Nguyễn Đăng Định | Chốt 3 câu hỏi treo: transaction, format mã, quy mô |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Soát nhất quán sau đợt vá v1.2 |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Vá 12 lỗ hổng phát hiện khi review flow |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Thu hẹp phạm vi về chỉ Parasola |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | PRD đầu tiên |
