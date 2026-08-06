# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 3.0 — bản chốt
**Project Level:** Level 2
**Status:** Final
**Phạm vi:** **Chỉ partner Parasola.** 12 partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD cho tính năng cho phép **nhân viên Parasola** tự xác nhận danh tính nội bộ trên Ambassador bằng mã do Parasola cấp.

### Nguyên tắc của bản chốt

**Bám sát T-Fluencers.** T-Fluencers đã chạy production và được nghiệm thu nên lấy làm chuẩn. Mọi cơ chế đều port từ đó, kể cả phần phân nhóm.

Chỉ khác T-Fluencers ở đúng **ba điểm bắt buộc** do Ambassador khác kiến trúc (mục 2.2). Ngoài ba điểm đó, không thêm bất kỳ cơ chế nào không có ở T-Fluencers.

**Related Documents:**
- T-Fluencers Handbook: https://handbook.diso.vn/wiki/admin/nhan-vien/03-quan-ly-ma-nhan-vien
- T-Fluencers SRS: https://handbook.diso.vn/srs/admin-portal/14-code
- Dossier phân tích code T-Fluencers: [tf-reference-employee-code-flow.md](./tf-reference-employee-code-flow.md)
- Tech spec: [techspec-employee-code-2026-08-06.md](./techspec-employee-code-2026-08-06.md)

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`: `employee` \| `not_employee` \| `not_verify`. Rỗng = chưa khai, phân loại như `not_verify` |
| **Mã nhân viên** | Bản ghi trong `manage-codes`, do Admin import theo partner. **Một mã dùng được cho nhiều người** — theo mô hình T-Fluencers |
| **Segment thủ công** | Segment mà Admin gán user vào bằng tay hoặc import danh sách userId (`type: manual`) |
| **Segment tự động** | Segment có điều kiện; user thoả điều kiện thì hệ thống tự thêm vào (`type: automatic`). T-Fluencers đã có, áp cho mã giới thiệu |
| **`applyType`** | Loại điều kiện của segment tự động. T-Fluencers có `referral_code`; PRD này thêm `staff_code` |
| **Tenant-level feature toggle** | Cờ bật/tắt theo từng partner, lưu trong `PartnerOpts`. Khác ENV vốn có phạm vi toàn service |
| **Silent failure** | Lỗi xảy ra nhưng hệ thống vẫn báo thành công |
| **Idempotent** | Thực hiện nhiều lần cho cùng kết quả như một lần |

---

## 1. Executive Summary

Parasola muốn phân biệt **nhân viên nội bộ** với creator bên ngoài trên Ambassador, để chạy chiến dịch riêng cho nội bộ và báo cáo tách bạch đóng góp của hai nhóm.

Ambassador hiện chưa có gì cho việc này: `UserPartnerRaw` không có trường trạng thái nhân viên (có comment xác nhận cố ý bỏ tại `partner_creator_config.go:23`), không có bảng mã nhân viên, không có API xác nhận.

**Giải pháp — port luồng T-Fluencers:**

```
Parasola cấp mã cho nhân viên (kênh nội bộ)
  → Admin import danh sách mã vào Ambassador
  → Nhân viên nhập mã trên web
  → Hệ thống ghi trạng thái nhân viên + tự đưa vào nhóm tương ứng
  → Dùng để chặn campaign nội bộ và tách số liệu báo cáo
```

**Về phân nhóm:** T-Fluencers đã có sẵn cơ chế **segment tự động** — segment cấu hình một danh sách mã, ai nhập mã trong danh sách thì tự vào segment đó (`internal/service/segment.go` — `CheckUserInSegmentWithReferralCode`, gọi từ `pkg/public/service/referral.go:75`). Hiện áp cho **mã giới thiệu**. PRD này port nguyên cơ chế đó và thêm một `applyType` mới cho **mã nhân viên**.

Nhờ vậy phần "thống kê theo nhóm nhân viên" — thứ T-Fluencers chưa làm — được giải quyết bằng chính cơ chế sẵn có của T-Fluencers, không phát sinh khái niệm mới.

**Phạm vi:** backend và admin xây theo hướng dùng chung (bật/tắt bằng cờ), nhưng phase này **chỉ bật cho Parasola và chỉ làm frontend cho `parasola/`**.

---

## 2. Bối cảnh

### 2.1 Hiện trạng Ambassador

| Thành phần | Ambassador | T-Fluencers |
|---|---|---|
| `UserPartnerRaw.statusStaff` | ❌ Không có | ✅ |
| `UserPartnerRaw.code` | ⚠️ **Đã bị chiếm** làm referral code (`migration.go:1109`) | Dùng cho mã nhân viên |
| Collection `manage-codes` | ❌ Không có | ✅ |
| API `confirm-is-staff`, `status-employee` | ❌ Không có | ✅ |
| `Segment` + `UserSegment` cơ bản | ✅ Có | ✅ |
| `SegmentRaw.Type` + `ConditionForAutomatic` | ❌ **Không có** | ✅ Có, `applyType: referral_code` |
| `UserSegmentRaw.Note` | ❌ Không có | ✅ |
| `EventOpts.applyForStaff` / `staffCodes` / `applyForSegments` | ❌ Không có | ✅ |
| `UserEventRaw.Options` | ❌ Không có | ✅ |
| `PartnerOpts` (tenant toggle) | ✅ Có pattern (`AllowResubmitRejectedContent`) | Dùng ENV |

### 2.2 Ba khác biệt bắt buộc

Chỉ ba chỗ **không thể** làm giống T-Fluencers, do Ambassador khác kiến trúc:

| # | T-Fluencers | Ambassador phải làm | Lý do |
|---|---|---|---|
| 1 | Mã nhân viên lưu ở `UserPartnerRaw.Code` | Lưu ở field mới `staffCode` | `Code` ở Ambassador đã là referral code |
| 2 | Tạo `UserPartnerRaw` với `IsJoined: true, JoinedAt: now` | **Không được ghi** `isJoined`/`joinedAt` | `isJoined` ở Ambassador là điều kiện xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi user thực sự tham gia (`:491`). Ghi ở đây sẽ làm sai lệch tăng số creator của Parasola |
| 3 | Bật/tắt bằng ENV `IS_VALIDATE_STAFF_CODE_EXISTS` | Bật/tắt bằng `PartnerOpts` | Ambassador có 13 partner; ENV toàn service nghĩa là bật cho Parasola là bật cho cả 12 partner kia |

**Ngoài ba điểm trên, mọi hành vi khác giữ nguyên như T-Fluencers.**

### 2.3 Những gì KHÔNG thêm vào

Đã cân nhắc và **loại bỏ** khỏi bản chốt, vì T-Fluencers không có:

- Ràng buộc một mã một người (`isUsed` enforcement), claim atomic, Mongo transaction
- Rate limit, validate format mã
- Audit trail
- Job đối soát dữ liệu
- Dry-run và xoá theo lô khi import
- Giới hạn số lần hiển thị modal
- Cho phép sửa lại trạng thái sau khi đã xác nhận
- Cột `group` trong file import mã

---

## 3. User Personas

**P1. Nhân viên Parasola** — được cấp mã qua kênh nội bộ. Nhập mã một lần khi đăng nhập.

**P2. Creator bên ngoài trên Parasola** — chiếm đa số người dùng.

**P3. Admin/Ops AccessTrade** — nhận file mã từ Parasola, import, tạo segment theo nhóm, theo dõi danh sách.

**P4. Marketing Parasola** — cấu hình chiến dịch chỉ dành cho nhân viên hoặc cho nhóm cụ thể, xem báo cáo theo nhóm.

**P5. Người dùng của 12 partner còn lại** — **không được thấy bất kỳ thay đổi nào.** Đây là ràng buộc, không phải mục tiêu.

---

## 4. Functional Requirements

### FR-001: Trạng thái nhân viên trên `UserPartnerRaw`

**Priority:** Must Have

```go
// backend/internal/model/mg/user_partner.go
StatusStaff string `bson:"statusStaff,omitempty" json:"statusStaff,omitempty"`
StaffCode   string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`
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

Đặt tên `staffCode` — Khác biệt bắt buộc #1.

**Acceptance Criteria:**
- [ ] 2 field `omitempty`, bản ghi cũ không bị ảnh hưởng
- [ ] `constants.IsStaff()` là nơi duy nhất định nghĩa quy tắc
- [ ] Có mirror `isStaff()` phía FE kèm comment yêu cầu giữ đồng bộ
- [ ] `UserPartnerRaw.Code` (referral) không bị đụng

---

### FR-002: Collection `manage-codes`

**Priority:** Must Have

Port nguyên cấu trúc T-Fluencers, **không thêm field nào**.

```go
// backend/internal/model/mg/manage_code.go — mới
type ManageCodeRaw struct {
    ID        AppID     `bson:"_id"`
    Partner   AppID     `bson:"partner"`
    Type      string    `bson:"type"`        // constants.ManageCodeApplyForEmployee
    Code      string    `bson:"code"`
    IsUsed    bool      `bson:"isUsed"`
    UsedBy    AppID     `bson:"usedBy,omitempty"`
    UsedAt    time.Time `bson:"usedAt,omitempty"`
    CreatedAt time.Time `bson:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt"`
}
```

**`isUsed`/`usedBy`/`usedAt` giữ đúng ngữ nghĩa T-Fluencers:** chỉ script migration ghi, luồng người dùng **không** ghi. Nghĩa là **một mã dùng được cho nhiều người**.

Hệ quả cần biết: mã hiển thị `isUsed: false` kể cả khi đã có người dùng; không truy được ai đã dùng mã nào từ `manage-codes`. Muốn biết ai là nhân viên thì tra `user-partners.statusStaff`.

**Index:** `{partner, code}`, `{partner, isUsed}`

**Acceptance Criteria:**
- [ ] Tạo mã trùng trong cùng partner → báo lỗi (kiểm tra ở tầng service như T-Fluencers)
- [ ] Luồng `confirm-is-staff` **không** ghi `isUsed`/`usedBy`/`usedAt`

---

### FR-003: Admin — CRUD mã nhân viên

**Priority:** Must Have

Port trang `/manage-code` từ `admin/src/pages/manage-code/` của T-Fluencers.

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/manage-codes` | Danh sách, filter `partner`, `code`, `isUsed` |
| `POST` | `/manage-codes` | Tạo lẻ `{partner, code}` |
| `DELETE` | `/manage-codes/:id` | Xoá — từ chối nếu `isUsed = true` |
| `POST` | `/manage-codes/import-excel` | Import hàng loạt (FR-004) |

**Bảng:** Mã \| Partner \| Đã dùng \| Người dùng \| Ngày dùng \| Ngày tạo

Mọi thao tác qua kiểm tra quyền partner theo pattern `IsAllowPartner` sẵn có.

**Acceptance Criteria:**
- [ ] CRUD hoạt động, chặn trùng mã trong cùng partner
- [ ] Xoá mã đã dùng → từ chối kèm thông báo

---

### FR-004: Import mã hàng loạt

**Priority:** Must Have

Port nguyên của T-Fluencers. **File Excel chỉ một cột là mã.**

| `code` |
|---|
| `PRS_A3F91B2C` |
| `PRS_7D0E4A88` |

**Xử lý:** bỏ dòng header → chuẩn hoá TRIM + UPPERCASE → mã đã tồn tại thì skip → insert phần còn lại.

Không có cột nhóm. Việc phân nhóm làm ở FR-005 bằng segment tự động, đúng như cách T-Fluencers làm với mã giới thiệu.

**Acceptance Criteria:**
- [ ] Import file 1 cột hoạt động, báo số dòng thành công / bị skip
- [ ] Mã được chuẩn hoá TRIM + UPPERCASE trước khi lưu

---

### FR-005: Segment tự động theo mã nhân viên

**Priority:** Must Have

**Đây là cách phân nhóm nhân viên.** Port cơ chế segment tự động sẵn có của T-Fluencers, thêm một `applyType` mới.

#### Cơ chế hiện có ở T-Fluencers

```go
// internal/model/mg/segment.go
Type                  string             // "manual" | "automatic"
ConditionForAutomatic *SegmentConditions

type SegmentConditions struct {
    ApplyType     string   // "referral_code"
    ReferralCodes []string
}
```

```go
// internal/service/segment.go — gọi từ pkg/public/service/referral.go:75
CheckUserInSegmentWithReferralCode(ctx, userID, referralCode)
// → tìm mọi segment automatic chứa mã này → thêm user vào
// → UserSegmentRaw.Note = "Automatic add to segment by referral code"
```

#### Áp cho mã nhân viên

Ambassador port toàn bộ cấu trúc trên, thêm:

```go
// backend/internal/constants/segments.go
SegmentTypeManual    = "manual"
SegmentTypeAutomatic = "automatic"

SegmentApplyTypeReferralCode = "referral_code"   // như T-Fluencers
SegmentApplyTypeStaffCode    = "staff_code"      // THÊM MỚI

// SegmentConditions — thêm một danh sách mã song song với ReferralCodes
type SegmentConditions struct {
    ApplyType     string   `bson:"applyType"`
    ReferralCodes []string `bson:"referralCodes,omitempty"`
    StaffCodes    []string `bson:"staffCodes,omitempty"`
}
```

Bổ sung `UserSegmentRaw.Note` (T-Fluencers có, Ambassador chưa).

#### Ops dùng thế nào

```
1. Import toàn bộ mã nhân viên qua FR-004
2. Tạo segment "Nhóm Miền Bắc"
     type = automatic
     applyType = staff_code
     staffCodes = [PRS_A3F91B2C, PRS_7D0E4A88, ...]
3. Nhân viên nhập mã → tự vào đúng segment
```

Sửa nhóm về sau chỉ cần sửa danh sách mã trong segment, không phải import lại file.

**Admin UI** (`admin/src/pages/segment/components/modal.tsx`): thêm select `type`, select `applyType`, và ô nhập danh sách mã dạng `mode="tags"` — port từ T-Fluencers.

**Acceptance Criteria:**
- [ ] Tạo được segment `automatic` với `applyType = staff_code`
- [ ] Nhân viên nhập mã thuộc segment → tự xuất hiện trong segment đó
- [ ] Một mã nằm trong nhiều segment → user vào tất cả
- [ ] Idempotent — nhập lại cùng mã không tạo bản ghi trùng
- [ ] `Note` ghi rõ nguồn gán tự động
- [ ] Segment `manual` giữ nguyên hành vi cũ, không bị ảnh hưởng

---

### FR-006: API kiểm tra trạng thái nhân viên

**Priority:** Must Have

Port nguyên endpoint và response của T-Fluencers.

```
GET /partners/:id/status-employee        (yêu cầu đăng nhập)
→ { "isOpenInputStaffCode": true }
```

**Logic:**
```
partner chưa bật tính năng             → false     ← khác T-Fluencers (Khác biệt #3)
chưa có bản ghi user-partners          → true
statusStaff ∈ {employee, not_employee} → false
còn lại (rỗng / not_verify)            → true
```

**Acceptance Criteria:**
- [ ] Partner tắt tính năng → luôn `false`
- [ ] Đã chọn rồi → `false`
- [ ] Chưa join partner → `true`

---

### FR-007: API xác nhận nhân viên

**Priority:** Must Have

```
POST /users/confirm-is-staff        { partner, isStaff, code }
```

**Luồng xử lý** — port T-Fluencers:
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
5. Nếu isStaff = true → CheckUserInSegmentWithStaffCode(userId, code)   ← FR-005
```

Bước 5 gọi cơ chế FR-005, đúng như T-Fluencers gọi `CheckUserInSegmentWithReferralCode` sau khi user nhập mã giới thiệu.

**Không ghi** `isUsed`/`usedBy`/`usedAt` — giữ hành vi T-Fluencers.

#### ⚠️ Quy tắc ghi `user-partners`

T-Fluencers tạo bản ghi mới với `IsJoined: true, JoinedAt: time.Now()`. **Ambassador không được làm vậy** — Khác biệt bắt buộc #2.

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
- [ ] User chưa từng tham gia Parasola, bấm "Tôi không thuộc Parasola" → không bị tính vào danh sách creator của partner
- [ ] `UserPartnerRaw.Code` không bị thay đổi
- [ ] Xác nhận thành công → user vào đúng các segment cấu hình theo mã đó
- [ ] Ba user cùng nhập một mã → cả ba thành công

---

### FR-008: Modal xác nhận trên Frontend Parasola

**Priority:** Must Have

**Port nguyên UX của T-Fluencers** (`modal-tcb-employee.tsx`). Chỉ làm trong `parasola/`.

**Điểm cắm:** `parasola/src/components/layout/main/header/index.tsx` đã có sẵn cơ chế này cho màn đồng ý điều khoản — `initApp` gọi `users/me` → `useEffect [user]` kiểm tra `privacyAccepted === false` → hiển thị `ModalCompleteRegistration`. Modal mã nhân viên đi theo đúng cơ chế đó, dùng chung `AppModal`.

Thứ tự ưu tiên: **modal điều khoản trước, modal nhân viên sau** — không hiển thị chồng.

**Hành vi — giống T-Fluencers:**
- Modal **blocking**: `onClose={() => {}}`, `keyboard={false}`, `hideFooter`, không nút Hủy
- Hai lựa chọn: "Tôi là nhân viên Parasola" / "Tôi không thuộc Parasola"
- **Cả hai nhánh đều bắt buộc nhập mã**, nút Xác nhận khoá tới khi có mã
- Hai bước: chọn + nhập mã → màn xác nhận tóm tắt → Confirm
- Lựa chọn ghi nhận cố định, không tự thay đổi được
- Lỗi từ backend hiển thị dưới ô mã, không đóng modal

**Sửa một lỗi hiển thị của T-Fluencers:** bản gốc hiển thị mã viết hoa (`value={employeeCode?.toUpperCase()}`) nhưng gửi lên nguyên bản (`code: employeeCode.trim()`) — user thấy `ABC123`, DB lưu `abc123`. Ambassador chuẩn hoá để giá trị lưu khớp giá trị hiển thị.

**Phạm vi triển khai:**

| Folder | Làm gì |
|---|---|
| `parasola/` | ✅ Toàn bộ FR-008, FR-010 |
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

### FR-009: Chiến dịch dành riêng cho nhân viên

**Priority:** Must Have

Port đủ **cả ba cơ chế** của T-Fluencers vào `EventOpts`:

```go
ApplyForStaff    bool     `bson:"applyForStaff,omitempty"`
StaffCodes       []string `bson:"staffCodes,omitempty"`
ApplyForSegments []AppID  `bson:"applyForSegments,omitempty"`
```

**Điểm chặn khi nộp bài** — thứ tự như T-Fluencers (`content.go:114-146`):

| Điều kiện | Kiểm tra | Lỗi |
|---|---|---|
| `ApplyForStaff` | `user-partners.statusStaff == "employee"` | Chương trình này chỉ áp dụng cho nhân viên của công ty |
| `StaffCodes` | `user-events.options.codeInput` nằm trong danh sách | Bạn cần nhập mã để tham gia chương trình này |
| `ApplyForSegments` | đếm `user-segments` giao với danh sách > 0 | Bạn không đủ điều kiện tham gia chương trình này |

**Mã riêng theo event:** `POST /events/:id/input-code-join-event` → upsert `user-events.options {codeInput, statusEmployee}`.

`UserEventRaw` của Ambassador hiện **thiếu** `Options` — cần bổ sung:
```go
type UserEventOpts struct {
    CodeInput      string `bson:"codeInput" json:"codeInput"`
    StatusEmployee string `bson:"statusEmployee" json:"statusEmployee"`
}
```

**Cờ ra FE:** `isRequireCode` trên event list và event detail, logic như T-Fluencers.

**Admin UI** (`admin/src/pages/event/components/modal.tsx`): switch `applyForStaff`; select `mode="tags"` cho `staffCodes`; select nhiều cho `applyForSegments`.

**Acceptance Criteria:**
- [ ] Ba điều kiện hoạt động độc lập và kết hợp được
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] Chỉ chọn được segment thuộc partner của event

---

### FR-010: Thông báo khi không đủ điều kiện

**Priority:** Must Have

Port `modal-not-employee.tsx` của T-Fluencers.

| Trường hợp | Tiêu đề | Hành động |
|---|---|---|
| Không phải nhân viên, vào event `applyForStaff` | Thử thách này dành riêng cho nhân viên Parasola | **Đã hiểu** / **Khám phá thêm** |
| Không thuộc nhóm được phép | Bạn không đủ điều kiện tham gia chương trình này | **Đã hiểu** / **Khám phá thêm** |

Modal này **đóng được** — khác modal FR-008. Giống T-Fluencers.

**Acceptance Criteria:**
- [ ] Modal đóng được, "Khám phá thêm" điều hướng về trang chủ
- [ ] Có VI và EN

---

### FR-011: Bật/tắt theo từng partner

**Priority:** Must Have

Thay ENV của T-Fluencers bằng `PartnerOpts` — Khác biệt bắt buộc #3.

```go
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

### FR-012: Admin — hiển thị và lọc theo nhân viên/nhóm

**Priority:** Must Have

Bổ sung vào `admin/src/pages/user-partner/`:

**Cột mới:** `Nhân viên` (Có/Không) \| `Mã nhân viên` \| `Nhóm`
**Filter mới:** `statusStaff` (Tất cả / Nhân viên / Không phải / Chưa xác nhận), `segment` (chọn nhiều)

**Acceptance Criteria:**
- [ ] Ba cột hiển thị đúng, giá trị rỗng hiện `—`
- [ ] Filter hoạt động độc lập và kết hợp với filter sẵn có

---

### FR-013: Thống kê theo nhóm nhân viên

**Priority:** Must Have

T-Fluencers có `GetCreatorKPIsByStaffBreakdown` nhưng chỉ tách nhị phân staff/guest. Bản này giữ nguyên quy tắc tính của T-Fluencers, thêm chiều nhóm lấy từ segment (FR-005).

**Vị trí:** tab mới trong `admin/src/pages/event-statistic/`.

| Nhóm | Số người | Đã tham gia | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|
| **Tổng — Nhân viên** | 210 | 168 | 1.180 | 3,1tr | 190tr |
| ├ Nhóm Miền Bắc | 85 | 72 | 520 | 1,4tr | 82tr |
| ├ Nhóm Miền Nam | 78 | 61 | 410 | 1,1tr | 68tr |
| ├ Khối Vận hành | 35 | 28 | 200 | 0,5tr | 33tr |
| └ Chưa phân nhóm | 12 | 7 | 50 | 0,1tr | 7tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9,3tr | 650tr |

**Quy tắc tính** — giữ nguyên quy ước T-Fluencers:
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên, không cộng dồn từng loại
- Không tính bài đã bị huỷ
- Nhân viên chưa thuộc segment nào gom vào "Chưa phân nhóm"

**Phân loại theo trạng thái hiện tại, không snapshot.** Nhân viên xác nhận muộn thì số liệu kỳ cũ thay đổi theo. Đây cũng là hành vi T-Fluencers; khác ở chỗ Ambassador **in ghi chú rõ** trên bảng và export:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo.*

**Acceptance Criteria:**
- [ ] Tổng các nhóm con = dòng tổng "Nhân viên"
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] Có ghi chú "không bao gồm bài đã huỷ" và ghi chú phân loại theo trạng thái hiện tại
- [ ] Tải xong dưới 3 giây

---

### FR-014: Xuất dữ liệu

**Priority:** Should Have

Bổ sung 3 cột `Nhân viên` \| `Mã nhân viên` \| `Nhóm` vào file export hồ sơ/creator hiện có; thêm nút export cho bảng FR-013.

Nguồn dữ liệu như T-Fluencers: ưu tiên `UserPartnerRaw.StaffCode`, fallback `UserRaw.StaffCode` nếu có.

**Acceptance Criteria:**
- [ ] Excel và CSV đều có 3 cột mới
- [ ] Cột "Nhân viên" xuất "Có"/"Không"

---

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
- Mọi field mới `omitempty`, không cần migration dữ liệu
- `EnableStaffCode` mặc định `false` — 13 partner hiện tại không đổi hành vi
- Segment hiện có không có `Type` → coi như `manual`, hành vi không đổi
- Không đụng `UserPartnerRaw.Code`

### NFR-002: Data Integrity
- Luồng `confirm-is-staff` không bao giờ ghi `isJoined`/`joinedAt`/`code`
- Gán segment tự động là idempotent
- Xoá segment bị từ chối khi còn được `events.options.applyForSegments` tham chiếu

### NFR-003: Performance
- Quy mô nhân viên Parasola nhỏ. Các mốc dưới đây chỉ để chặn thiết kế sai kiểu N+1, không phải bài toán tải thật. **Không tối ưu sớm.**
- Import 1.000 mã < 10 giây
- Thống kê FR-013 < 3 giây

### NFR-004: i18n
- Chuỗi mới có cả VI và EN
- Tên segment lấy nguyên do Ops đặt, không dịch

---

## 6. Epics

| Epic | FR | Nội dung |
|---|---|---|
| **EPIC-001** Nền tảng | FR-001, 002, 011 | Model, constants, collection, index, tenant toggle |
| **EPIC-002** Quản lý mã | FR-003, 004 | Admin CRUD + import |
| **EPIC-003** Phân nhóm | FR-005 | Segment tự động theo mã nhân viên |
| **EPIC-004** Luồng người dùng | FR-006, 007, 008 | API + modal Parasola |
| **EPIC-005** Chiến dịch | FR-009, 010 | Ba cơ chế gate + modal từ chối |
| **EPIC-006** Báo cáo | FR-012, 013, 014 | Cột, filter, thống kê theo nhóm, export |

---

## 7. Kiến trúc

### Luồng dữ liệu

```
Parasola phát mã cho nhân viên (kênh nội bộ)
        │
        ▼
Admin import Excel 1 cột  →  manage-codes {partner, type, code}
Admin tạo segment automatic → segments {type, applyType: staff_code, staffCodes[]}
        │
        ▼
Nhân viên nhập mã  →  POST /users/confirm-is-staff
        ├──► user-partners  {statusStaff, staffCode}
        └──► CheckUserInSegmentWithStaffCode → user-segments {user, segment, note}
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
            ├─ thành công → ghi statusStaff + staffCode → tự vào segment
            └─ mã sai     → hiển thị lỗi dưới ô mã, giữ modal
```

---

## 8. Implementation Scope

### Thay đổi cần làm

| Vùng | File | Nội dung |
|---|---|---|
| **Model** | `model/mg/user_partner.go` | +2 field |
| **Model** | `model/mg/manage_code.go` | File mới |
| **Model** | `model/mg/segment.go` | +`Type`, +`ConditionForAutomatic` |
| **Model** | `model/mg/user_segment.go` | +`Note` |
| **Model** | `model/mg/user_event.go` | +`Options` |
| **Model** | `model/mg/partner.go` | +2 field trong `PartnerOpts` |
| **Model** | `model/mg/event.go` | +3 field trong `EventOpts` |
| **Constants** | `constants/staff_code.go`, `constants/segments.go` | File mới |
| **DAO** | `module/database/mongodb/` | `ManageCodeDAO` + collection + index |
| **Service** | `internal/service/segment.go` | `CheckUserInSegmentWithStaffCode` |
| **Public API** | `pkg/public/{router,handler,service}/user.go` | `confirm-is-staff` |
| **Public API** | `pkg/public/{router,handler,service}/partner.go` | `status-employee` |
| **Public API** | `pkg/public/{router,handler,service}/event.go` | `input-code-join-event` |
| **Public API** | `pkg/public/service/content.go` | 3 điểm chặn khi nộp bài |
| **Admin API** | `pkg/admin/{router,handler,service}/manage_code.go` | File mới |
| **Admin API** | `pkg/admin/service/segment.go` | Hỗ trợ `type` + `conditionForAutomatic` |
| **Admin API** | `pkg/admin/service/user_partner.go` | Trả thêm field + filter |
| **Export** | `pkg/admin/service/export_*.go` | +3 cột |
| **Thống kê** | `aggregate_pipeline/` | Pipeline breakdown theo nhóm |
| **Locale** | `internal/locale/staff_code.go` + `properties/{vi,en}/` | Key mới |
| **Admin UI** | `admin/src/pages/manage-code/` | Trang mới |
| **Admin UI** | `admin/src/pages/segment/components/modal.tsx` | +type, +applyType, +danh sách mã |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | +2 toggle |
| **Admin UI** | `admin/src/pages/event/components/modal.tsx` | +1 switch, +2 select |
| **Admin UI** | `admin/src/pages/user-partner/` | +3 cột, +2 filter |
| **Admin UI** | `admin/src/pages/event-statistic/` | Tab thống kê theo nhóm |
| **Frontend** | `parasola/src/.../header/index.tsx` | Trigger modal |
| **Frontend** | `parasola/src/.../modal-staff-code.tsx`, `modal-not-employee.tsx` | Component mới |
| **Frontend** | `parasola/src/models/main.ts`, `configs/api.ts`, `utils/staff.ts` | State, endpoint, mirror `isStaff` |

### KHÔNG làm

- **Không đụng `frontend/` và 12 folder partner còn lại** (`anker`, `flamingo`, `hdbank`, `lusso`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `vpbank`, `wildrift`, `yody`)
- Không bật cờ cho partner nào ngoài Parasola
- Không dùng lại `UserPartnerRaw.Code`
- Không ghi `isJoined`/`joinedAt` trong luồng xác nhận
- Không dùng ENV toàn cục
- Không thêm cột nhóm vào file import mã
- Không thêm ràng buộc một-mã-một-người, rate limit, audit trail, transaction
- Không dựng dashboard analytics riêng — bổ sung vào trang admin đã có
- Không đụng logic tính thưởng, xếp hạng, duyệt nội dung
- Không tự sinh mã — Parasola cấp, Admin import

---

## 9. Assumptions

1. Parasola phát mã cho nhân viên qua kênh nội bộ; Ambassador không gửi mã
2. Parasola cung cấp được danh sách mã, và cho biết mã nào thuộc nhóm nào để Ops cấu hình segment
3. Trạng thái nhân viên gắn theo partner, không phải toàn hệ thống
4. `parasola/` tiếp tục dùng Umi + dva; modal mới bám pattern `ModalCompleteRegistration` sẵn có

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
| Có nơi để nhân viên nhập mã | FR-006, FR-007, FR-008 |
| Có thống kê kết quả theo nhóm nhân viên | FR-005, FR-012, FR-013, FR-014 |
| Có campaign dành riêng cho nhân viên | FR-009, FR-010 |
| Import nhân viên để về sau còn phân loại | FR-002, FR-003, FR-004, FR-005 |

| Priority | FR |
|---|---|
| **Must Have** (13) | FR-001 → FR-013 |
| **Should Have** (1) | FR-014 |

---

## 12. Resolved Questions

1. **Có bám theo T-Fluencers không?** → **Có.** T-Fluencers đã chạy production và được nghiệm thu; lấy làm chuẩn. Chỉ khác ở 3 điểm bắt buộc do kiến trúc (mục 2.2).

2. **Một mã dùng được cho mấy người?** → **Nhiều người**, như T-Fluencers. Luồng xác nhận không ghi `isUsed`.

3. **Modal có chặn không?** → **Có**, blocking. Cả hai nhánh đều nhập mã. Lựa chọn cố định.

4. **Có port `staffCodes` theo event không?** → **Có**, đủ cả ba cơ chế.

5. **Phân nhóm nhân viên bằng cách nào?** → **Segment tự động, port từ T-Fluencers.** T-Fluencers đã có `type: automatic` + `applyType: referral_code` (`internal/service/segment.go`, gọi từ `referral.go:75`). Ambassador thêm `applyType: staff_code` và gọi tương tự sau `confirm-is-staff`. **Không** thêm cột `group` vào file import — đó là cơ chế tự nghĩ, đã loại bỏ.

6. **Format mã?** → Theo quy ước T-Fluencers: `PRS_<8 hex ngẫu nhiên viết hoa>`, ví dụ `PRS_A3F91B2C`. Sinh bằng `f"PRS_{secrets.token_hex(4).upper()}"` như Handbook hướng dẫn.

7. **Bật/tắt bằng gì?** → `PartnerOpts` thay ENV. Bắt buộc, vì Ambassador có 13 partner.

8. **Tên trường mã?** → `staffCode`, vì `UserPartnerRaw.Code` đã là referral code.

---

## 13. Open Questions

_(Không còn — đã chốt toàn bộ.)_

Việc cần làm trước khi Ops cấu hình: Parasola gửi danh sách mã **kèm thông tin mã nào thuộc nhóm nào**, để Ops tạo segment tương ứng. Đây là thao tác vận hành, không ảnh hưởng thiết kế.

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| **3.0** | 2026-08-06 | Nguyễn Đăng Định | **Bản chốt.** Phân nhóm chuyển sang **segment tự động port từ T-Fluencers** (`applyType: staff_code`) thay cho cột `group` trong file import — cột `group` là cơ chế tự nghĩ, đã loại bỏ. `manage-codes` trở về đúng cấu trúc T-Fluencers. Bổ sung `SegmentRaw.Type`, `ConditionForAutomatic`, `UserSegmentRaw.Note` (T-Fluencers có, Ambassador chưa). 13 FR → 14 FR. Status: Final |
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | Viết lại theo hướng bám T-Fluencers, bỏ các thay đổi tự đề xuất ở v1.x |
| 1.6 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.5 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ kỹ thuật, bổ sung mục 0 |
| 1.4 | 2026-08-06 | Nguyễn Đăng Định | Chốt 3 câu hỏi treo |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Soát nhất quán sau đợt vá v1.2 |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Vá 12 lỗ hổng phát hiện khi review flow |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Thu hẹp phạm vi về chỉ Parasola |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | PRD đầu tiên |
