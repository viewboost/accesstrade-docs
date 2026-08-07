# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06 (cập nhật 2026-08-07)
**Author:** Nguyễn Đăng Định
**Reviewer:** Vinh Nguyễn — [review-feedback-2026-08-07.md](./review-feedback-2026-08-07.md)
**Version:** 4.0 — bản chốt
**Project Level:** Level 2
**Status:** Final
**Phạm vi:** **Chỉ partner Parasola.** 12 partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD cho tính năng cho phép **nhân viên Parasola** tự xác nhận danh tính nội bộ trên Ambassador bằng mã do Parasola cấp, phục vụ ba mục tiêu gốc: có nơi nhập mã, có thống kê theo nhóm nhân viên, có chiến dịch dành riêng cho nhân viên.

### Nguyên tắc

**Bám sát T-Fluencers.** Bản đó đã chạy production và được nghiệm thu nên lấy làm chuẩn. Mọi cơ chế port từ đó.

Chỉ đi khác ở ba loại tình huống, mỗi chỗ đều ghi rõ lý do tại chỗ:
1. **Bắt buộc** — Ambassador khác kiến trúc, không thể làm giống (mục 2.2)
2. **T-Fluencers không có** — phải thiết kế mới (phân nhóm, thống kê theo nhóm)
3. **Sửa lỗi đã kiểm chứng trên code T-Fluencers** — liệt kê ở mục 2.3

**Related Documents:**
- Review: [review-feedback-2026-08-07.md](./review-feedback-2026-08-07.md)
- Dossier phân tích code T-Fluencers: [tf-reference-employee-code-flow.md](./tf-reference-employee-code-flow.md)
- Tech spec: [techspec-employee-code-2026-08-06.md](./techspec-employee-code-2026-08-06.md)
- T-Fluencers Handbook (wiki, đã verify có nội dung): https://handbook.diso.vn/wiki/admin/nhan-vien/03-quan-ly-ma-nhan-vien
- ~~SRS `/srs/admin-portal/14-code`~~ — **không dùng làm căn cứ**: mô tả mã gán theo `Ref (Event)` và trạng thái `USED`, không khớp code thật

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`: `employee` \| `not_employee` \| `not_verify`. Rỗng = chưa khai, phân loại như `not_verify` |
| **Mã nhân viên** | Bản ghi trong `manage-codes`, Admin import theo partner. **Một mã dùng được cho nhiều người** — theo mô hình T-Fluencers |
| **Segment thủ công** | Admin gán user vào bằng tay hoặc import danh sách userId (`type: manual`) |
| **Segment tự động** | Segment có điều kiện, user thoả thì hệ thống tự thêm vào (`type: automatic`) |
| **`applyType`** | Loại điều kiện của segment tự động. T-Fluencers có `referral_code`; PRD này thêm `staff_code` |
| **Tenant-level feature toggle** | Cờ bật/tắt theo từng partner, lưu trong `PartnerOpts` |
| **Silent failure** | Lỗi xảy ra nhưng hệ thống vẫn báo thành công |
| **Idempotent** | Thực hiện nhiều lần cho cùng kết quả như một lần |

---

## 1. Executive Summary

Parasola muốn phân biệt nhân viên nội bộ với creator bên ngoài, để chạy chiến dịch riêng cho nội bộ và báo cáo tách bạch hai nhóm.

Ambassador hiện chưa có gì cho việc này: `UserPartnerRaw` không có trường trạng thái nhân viên (`partner_creator_config.go:23` có comment xác nhận cố ý bỏ), không có bảng mã, không có API xác nhận.

```
Parasola cấp mã cho nhân viên (kênh nội bộ)
  → Admin import danh sách mã
  → Admin tạo segment tự động, gán danh sách mã của từng nhóm
  → Nhân viên nhập mã trên web
  → Hệ thống ghi trạng thái + tự đưa vào nhóm
  → Dùng để chặn campaign nội bộ và tách số liệu báo cáo
```

**Về phân nhóm:** T-Fluencers có sẵn cơ chế **segment tự động** — cấu hình một danh sách mã, ai nhập mã trong danh sách thì tự vào segment (`internal/service/segment.go`, gọi từ `referral.go:75`). Hiện áp cho mã giới thiệu. PRD này port nguyên và thêm `applyType: staff_code`.

**Phạm vi:** backend và admin xây dùng chung (bật/tắt bằng cờ), phase này **chỉ bật cho Parasola, chỉ làm frontend `parasola/`**.

---

## 2. Bối cảnh

### 2.1 Hiện trạng Ambassador — đã verify từng dòng

| Thành phần | Ambassador | Bằng chứng |
|---|---|---|
| `UserPartnerRaw.statusStaff` | ❌ Không có | `user_partner.go` |
| `UserPartnerRaw.Code` | ⚠️ **Là referral code** | `migration.go:1155` ghi `"code": r.Code` từ `ReferralRaw` |
| Collection `manage-codes` | ❌ Không có | — |
| API `confirm-is-staff`, `status-employee` | ❌ Không có | — |
| `Segment` + `UserSegment` cơ bản | ✅ Có | — |
| `SegmentRaw.Type`, `.ConditionForAutomatic` | ❌ Không có | verify từng field |
| `UserSegmentRaw.Note`, `.Partner` | ❌ Không có | verify từng field |
| `UserEventRaw.Options` | ❌ Không có | verify |
| `EventOpts.applyForStaff` / `staffCodes` / `applyForSegments` | ❌ Không có | verify |
| `PartnerOpts` (tenant toggle) | ✅ Có pattern | `AllowResubmitRejectedContent` |
| Gate người tham gia khi nộp bài | ❌ **Không có gì** | `content.go` chỉ chặn theo nguồn, thời gian, link, trùng bài |
| Ngôn ngữ | **Chỉ tiếng Việt** | `parasola/` và `admin/` chỉ có `vi-VN.ts`, không có `en-US` |

### 2.2 Ba khác biệt bắt buộc do kiến trúc

| # | T-Fluencers | Ambassador phải làm | Lý do (đã verify) |
|---|---|---|---|
| 1 | Mã lưu ở `UserPartnerRaw.Code` | Lưu ở field mới `staffCode` | `Code` đã là referral code |
| 2 | Tạo `UserPartnerRaw` với `IsJoined: true` | **Không được ghi** `isJoined`/`joinedAt` | `isJoined` là điều kiện xác định user thuộc partner nào (`internal/service/user.go:226`), chỉ set khi thực sự tham gia (`:491`). Ghi ở đây làm sai lệch tăng số creator Parasola |
| 3 | ENV `IS_VALIDATE_STAFF_CODE_EXISTS` | `PartnerOpts` | Ambassador có 13 partner; ENV toàn service = bật cho Parasola là bật cho cả 12 partner kia |

### 2.3 Ba lỗi của T-Fluencers — sửa, không port

Đều đã verify trên code, không phải suy đoán:

| Lỗi | Bằng chứng | Ambassador làm gì |
|---|---|---|
| Gate campaign chỉ chạy lúc join, và fail-open | Ambassador `eligibility.go:216` thoát sớm nếu đã join; `:64` trả `Eligible=true` khi `Enabled=false` | Gate đặt **độc lập, trước** `JoinEvent`, chạy mỗi lần nộp bài (FR-011) |
| FE hiện mã viết hoa nhưng gửi nguyên bản | `modal-tcb-employee.tsx` — `value={...toUpperCase()}` vs `code: employeeCode.trim()` | Chuẩn hoá ở **backend** (FR-008) |
| Tái dùng key lỗi `ReferralKeyCodeInvalid` cho mã nhân viên | `user.go` vùng `ConfirmIsStaff` | Key riêng (FR-008) |

### 2.4 Những gì KHÔNG thêm vào

Đã cân nhắc, loại bỏ vì T-Fluencers không có:

- Ràng buộc một mã một người (`isUsed` enforcement), claim atomic, Mongo transaction
- Rate limit, validate format mã
- Audit trail
- Job đối soát dữ liệu
- Dry-run và xoá theo lô khi import
- Giới hạn số lần hiển thị modal
- Cột `group` trong file import mã

---

## 3. User Personas

**P1. Nhân viên Parasola** — được cấp mã qua kênh nội bộ, nhập một lần khi đăng nhập.
**P2. Creator bên ngoài trên Parasola** — chiếm đa số người dùng.
**P3. Admin/Ops AccessTrade** — nhận file mã, import, tạo segment theo nhóm.
**P4. Marketing Parasola** — cấu hình chiến dịch nội bộ, xem báo cáo theo nhóm.
**P5. Người dùng 12 partner còn lại** — **không được thấy bất kỳ thay đổi nào.** Ràng buộc, không phải mục tiêu.

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

**AC:**
- [ ] 2 field `omitempty`, bản ghi cũ không bị ảnh hưởng
- [ ] `constants.IsStaff()` là nơi duy nhất định nghĩa quy tắc
- [ ] Có mirror `isStaff()` phía FE kèm comment giữ đồng bộ
- [ ] `UserPartnerRaw.Code` (referral) không bị đụng

---

### FR-002: Collection `manage-codes`

**Priority:** Must Have

Port nguyên cấu trúc T-Fluencers, không thêm field.

```go
type ManageCodeRaw struct {
    ID        AppID     `bson:"_id"`
    Partner   AppID     `bson:"partner"`
    Type      string    `bson:"type"`   // ManageCodeApplyForEmployee
    Code      string    `bson:"code"`
    IsUsed    bool      `bson:"isUsed"`
    UsedBy    AppID     `bson:"usedBy,omitempty"`
    UsedAt    time.Time `bson:"usedAt,omitempty"`
    CreatedAt time.Time `bson:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt"`
}
```

**Một mã dùng được cho nhiều người.** `isUsed`/`usedBy`/`usedAt` chỉ do script migration ghi, luồng người dùng **không** ghi — giữ đúng T-Fluencers.

> ⚠️ **Hệ quả phải biết:** mã luôn hiển thị `isUsed: false` kể cả khi đã có người dùng. Điều kiện *"từ chối xoá nếu `isUsed = true`"* ở FR-004 vì vậy **không bao giờ kích hoạt** — T-Fluencers cũng có đúng dòng chết này (`manage_code.go:99`). Giữ cho parity, nhưng **không được coi là cơ chế bảo vệ**. Muốn biết ai đang dùng mã thì tra `user-partners.staffCode`.

**Index:** `{partner, code}`, `{partner, isUsed}`

**AC:**
- [ ] Tạo mã trùng trong cùng partner → báo lỗi ở tầng service
- [ ] Luồng `confirm-is-staff` không ghi `isUsed`/`usedBy`/`usedAt`

---

### FR-003: `user-segments` phải mang `partner`

**Priority:** Must Have — **prerequisite của FR-006 và FR-015, làm TRƯỚC**

**Vấn đề.** `UserSegmentRaw` hiện là `{User, Segment, CreatedAt, CreatedBy}` — không có `partner`. `SegmentRaw.Partner` có nhưng `omitempty`, tồn tại segment global cũ. Toàn bộ phân nhóm và thống kê cưỡi lên bảng này.

| Hệ quả | Chi tiết |
|---|---|
| Báo cáo gán nhầm nhóm, lộ tên nhóm partner khác | Một người vừa là NV Parasola vừa nằm trong segment marketing của partner khác → thống kê Parasola gán họ vào nhóm partner kia |
| Admin partner khác xoá được nhóm NV Parasola | `pkg/admin/service/user_segment.go:123` — `DeleteMany` theo `{_id:{$in}}`, **không gọi `IsAllowPartner`** trong khi `Add` cùng file thì có |

Ambassador ở pool model (shared DB, tenant discriminator): mọi bảng tenant-scoped phải mang tenant id, filter fail-closed ở tầng dưới — không dựa vào kỷ luật viết query.

```go
// backend/internal/model/mg/user_segment.go
Partner AppID  `bson:"partner,omitempty" json:"partner,omitempty"`
Note    string `bson:"note,omitempty" json:"note,omitempty"`   // dùng ở FR-006
```

Backfill `partner` từ `segments.partner` cho bản ghi hiện có.

**AC:**
- [ ] `user-segments` có `partner`, backfill xong trước khi làm FR-006
- [ ] **Mọi truy vấn / `$lookup` trên `user-segments` đều kèm điều kiện partner** — không ngoại lệ
- [ ] `UserSegment.Delete` kiểm `IsAllowPartner` như `Add`
- [ ] Admin partner A không xoá được bản ghi của partner B
- [ ] Thống kê FR-015 không bao giờ hiện tên segment của partner khác

---

### FR-004: Admin — CRUD mã nhân viên

**Priority:** Must Have

Port trang `/manage-code` từ T-Fluencers.

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/manage-codes` | Danh sách, filter `partner`, `code`, `isUsed` |
| `POST` | `/manage-codes` | Tạo lẻ `{partner, code}` |
| `DELETE` | `/manage-codes/:id` | Xoá — từ chối nếu `isUsed = true` (xem cảnh báo FR-002) |
| `POST` | `/manage-codes/import-excel` | Import hàng loạt (FR-005) |

**Bảng:** Mã \| Partner \| Đã dùng \| Người dùng \| Ngày dùng \| Ngày tạo

**Bắt buộc chọn partner tường minh.** `StaffRaw.Partner` đơn trị (`staff.go:38`) và `IsPermissionAllPartner()` trả `true` khi `Partner` rỗng (`:92`) — admin chưa gắn partner tự thành super-admin xuyên tenant. Với dữ liệu nhân sự thì mặc định đó sai hướng:
- Trang `/manage-code` **không có chế độ "tất cả partner"**
- Import/xoá yêu cầu `partner` trong request, không suy từ session

**AC:**
- [ ] CRUD hoạt động, chặn trùng mã trong cùng partner
- [ ] Admin có `Partner` rỗng **không** xem được mã của mọi partner

---

### FR-005: Import mã hàng loạt

**Priority:** Must Have

Port nguyên T-Fluencers. **File Excel một cột.**

| `code` |
|---|
| `PRS_A3F91B2C` |
| `PRS_7D0E4A88` |

Xử lý: bỏ dòng header → chuẩn hoá TRIM + UPPERCASE → mã đã tồn tại thì skip → insert phần còn lại. Không có cột nhóm; phân nhóm làm ở FR-006.

**Sửa một bug của T-Fluencers:** `ImportExcel` bên đó kiểm `len(newCodes) == 0` hai lần liên tiếp, nhánh thứ hai là code chết. Bỏ nhánh thừa.

**AC:**
- [ ] Import file 1 cột hoạt động, báo số dòng thành công / bị skip
- [ ] Mã chuẩn hoá TRIM + UPPERCASE trước khi lưu

---

### FR-006: Segment tự động theo mã nhân viên

**Priority:** Must Have

Đây là cách phân nhóm. Port cơ chế segment tự động sẵn có của T-Fluencers, thêm một `applyType`.

#### Cơ chế nguồn

```go
// T-Fluencers — internal/model/mg/segment.go
Type                  string             // "manual" | "automatic"
ConditionForAutomatic *SegmentConditions

type SegmentConditions struct {
    ApplyType     string   // "referral_code"
    ReferralCodes []string
}
```
`CheckUserInSegmentWithReferralCode` (`internal/service/segment.go`) gọi từ `referral.go:75` — tìm mọi segment automatic chứa mã, thêm user vào, `Note = "Automatic add to segment by referral code"`.

#### Áp cho mã nhân viên

```go
// backend/internal/constants/segments.go
SegmentTypeManual    = "manual"
SegmentTypeAutomatic = "automatic"

SegmentApplyTypeReferralCode = "referral_code"   // như T-Fluencers
SegmentApplyTypeStaffCode    = "staff_code"      // THÊM MỚI

type SegmentConditions struct {
    ApplyType     string   `bson:"applyType"`
    ReferralCodes []string `bson:"referralCodes,omitempty"`
    StaffCodes    []string `bson:"staffCodes,omitempty"`   // THÊM MỚI
}
```

Segment sinh từ luồng này mang `source: "staff_import"`.

#### Ops dùng thế nào

```
1. Import toàn bộ mã (FR-005)
2. Tạo segment "Nhóm Miền Bắc": type = automatic, applyType = staff_code,
   staffCodes = [PRS_A3F91B2C, PRS_7D0E4A88, ...]
3. Nhân viên nhập mã → tự vào đúng segment
```

#### Segment nhân viên là org unit, không phải audience marketing

| | Segment marketing | Segment nhân viên |
|---|---|---|
| Ai định nghĩa | Marketer, tự do | Sinh từ danh sách mã |
| Dùng để | Lọc, gửi thông báo | **Gate quyền tham gia** |
| Sửa thành viên | Thoải mái | **Không cho thêm/xoá tay** |

Segment `source: "staff_import"` **không cho admin thêm/xoá thành viên thủ công**. Nếu cho, một người có quyền admin đưa user vào *"Nhóm Miền Bắc"* là user đó qua gate campaign nhân viên **dù chưa từng nhập mã** — gate gác tiền không được tin vào bảng ai cũng ghi được.

#### Nút "Áp dụng lại" — bắt buộc

`CheckUserInSegmentWithStaffCode` chỉ chạy **lúc user nhập mã**. Ops sửa danh sách mã trong segment sau đó thì **người đã xác nhận không tự chuyển nhóm**.

T-Fluencers không gặp đau này vì họ không dùng segment cho nhân viên — cơ chế tự động của họ gắn với mã giới thiệu, gán một lần là xong. Ambassador đặt phân nhóm nhân viên lên đó nên phát sinh nhu cầu đồng bộ. **Đây là hệ quả của lựa chọn thiết kế trong PRD này, không phải thiếu sót kế thừa — nên phải tự giải.**

Nút **"Áp dụng lại"** trên màn segment: quét toàn bộ `user-partners` của partner có `staffCode` nằm trong `staffCodes` của segment, thêm ai còn thiếu, gỡ ai không còn thuộc. Chạy đồng bộ, hiện số lượng thêm/gỡ.

Không có nút này thì Parasola tái cơ cấu một lần là thống kê sai vĩnh viễn.

**Admin UI** (`admin/src/pages/segment/components/modal.tsx`): select `type`, select `applyType`, ô nhập danh sách mã `mode="tags"`, nút "Áp dụng lại" (chỉ hiện với segment `automatic`).

**AC:**
- [ ] Tạo được segment `automatic` với `applyType = staff_code`
- [ ] Nhân viên nhập mã thuộc segment → tự xuất hiện trong segment đó
- [ ] Một mã nằm trong nhiều segment → user vào tất cả
- [ ] Idempotent — nhập lại cùng mã không tạo bản ghi trùng
- [ ] Thêm tay user vào segment `staff_import` → **bị từ chối**
- [ ] Ops thêm mã vào segment rồi bấm "Áp dụng lại" → **người đã xác nhận trước đó được thêm vào**
- [ ] Ops gỡ mã khỏi segment rồi "Áp dụng lại" → người dùng mã đó bị gỡ khỏi segment
- [ ] Segment `manual` giữ nguyên hành vi cũ

---

### FR-007: API kiểm tra trạng thái nhân viên

**Priority:** Must Have

```
GET /partners/:id/status-employee        (yêu cầu đăng nhập)
→ { "isOpenInputStaffCode": true }
```

```
partner chưa bật tính năng             → false     ← khác T-Fluencers (Khác biệt #3)
chưa có bản ghi user-partners          → true
statusStaff ∈ {employee, not_employee} → false
còn lại (rỗng / not_verify)            → true
```

**AC:**
- [ ] Partner tắt tính năng → luôn `false`
- [ ] Đã chọn rồi → `false`
- [ ] Chưa join partner → `true`

---

### FR-008: API xác nhận nhân viên

**Priority:** Must Have

```
POST /users/confirm-is-staff        { partner, isStaff, code }
```

```
1. Load user      → không tồn tại / bị ban ⇒ lỗi
2. Load partner   → không tồn tại ⇒ lỗi
                  → chưa bật EnableStaffCode ⇒ lỗi
3. Nếu isStaff = true:
     code rỗng ⇒ lỗi
     nếu partner bật RequireStaffCodeValidation:
         tìm manage-codes {partner, code, type}
         không thấy ⇒ lỗi "Mã nhân viên không hợp lệ"
4. Upsert user-partners: statusStaff + staffCode
5. Nếu isStaff = true → CheckUserInSegmentWithStaffCode(userId, partnerId, code)
```

**Chuẩn hoá mã ở backend** (`TRIM` + `UPPERCASE`), không tin FE. T-Fluencers chuẩn hoá ở FE nhưng gửi nguyên bản nên giá trị lưu khác giá trị user thấy.

**Không ghi** `isUsed`/`usedBy`/`usedAt`.

#### Gọi lại khi đã xác nhận: cho phép ghi đè

T-Fluencers **không chặn** — hàm không đọc `statusStaff` hiện tại, chỉ upsert đè lên. Ambassador giữ nguyên hành vi đó, và ghi rõ ra đây vì nó là nền tảng của FR-010.

#### ⚠️ Quy tắc ghi `user-partners`

T-Fluencers tạo bản ghi mới với `IsJoined: true, JoinedAt: time.Now()`. **Ambassador không được làm vậy** — Khác biệt bắt buộc #2.

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

**Thông báo lỗi** — key riêng, không tái dùng key referral như T-Fluencers. **Chỉ tiếng Việt** (Ambassador không có `en-US`):

| Key | Nội dung |
|---|---|
| `staffCodeKeyRequired` | Vui lòng nhập mã nhân viên |
| `staffCodeKeyInvalid` | Mã nhân viên không hợp lệ |
| `staffCodeKeyFeatureDisabled` | Tính năng chưa được bật cho đối tác này |

**AC:**
- [ ] **`isJoined`/`joinedAt` không xuất hiện trong bất kỳ câu ghi nào** — có test khẳng định
- [ ] User bấm "Tôi không thuộc Parasola" → **không** bị tính vào danh sách creator của partner
- [ ] `UserPartnerRaw.Code` không bị thay đổi
- [ ] Xác nhận thành công → user vào đúng các segment cấu hình theo mã
- [ ] Ba user cùng nhập một mã → cả ba thành công
- [ ] Gõ `prs_a3f91b2c` → lưu `PRS_A3F91B2C`
- [ ] Gọi lại API khi đã xác nhận → ghi đè, không lỗi

---

### FR-009: Modal xác nhận trên Frontend Parasola

**Priority:** Must Have

Port UX của T-Fluencers (`modal-tcb-employee.tsx`). Chỉ làm trong `parasola/`.

**Điểm cắm:** `parasola/src/components/layout/main/header/index.tsx:82-84` đã có sẵn cơ chế này cho màn đồng ý điều khoản — `initApp` gọi `users/me` → `useEffect [user]` kiểm `privacyAccepted === false` → hiện `ModalCompleteRegistration`. Modal mã nhân viên đi theo đúng cơ chế đó, dùng chung `AppModal`.

Thứ tự ưu tiên: **modal điều khoản trước, modal nhân viên sau** — không hiện chồng.

**Hành vi — giống T-Fluencers:**
- Modal **blocking**: `closeButton={false}`, `keyboard={false}`, `hideFooter`
- Hai lựa chọn: "Tôi là nhân viên Parasola" / "Tôi không thuộc Parasola"
- Hai bước: chọn → màn xác nhận tóm tắt → Confirm
- Lỗi backend hiện dưới ô mã, không đóng modal

#### Một khác biệt có chủ ý: chỉ nhánh nhân viên mới nhập mã

T-Fluencers khoá nút Xác nhận ở cả hai nhánh: `disabled={isTcbEmployee === null || !employeeCode.trim()}`. Người chọn *"Tôi không thuộc Techcombank"* vẫn phải gõ một mã họ không được cấp.

Điều này **không chặn họ** — nhánh `isStaff=false` ở backend không validate mã, gõ ký tự nào cũng qua. Nhưng hệ quả:
- Dữ liệu rác vào `user-partners.staffCode`
- Dòng hướng dẫn *"nhập mã bạn được cấp trước đó"* nói sai với người chưa từng được cấp

Chi phí bỏ: một dòng `disabled={isStaff === null || (isStaff === true && !code.trim())}`. Đây là **khác biệt duy nhất về UX so với T-Fluencers**, và là đánh đổi sạch dữ liệu lấy parity.

#### Bố cục — bám component sẵn có

```
┌──────────────────────────────────────────────┐
│  [logo]  Bạn có phải nhân viên Parasola?     │   ← không có nút X
├──────────────────────────────────────────────┤
│  Parasola có những chiến dịch dành riêng     │
│  cho nhân viên nội bộ.                       │
│                                              │
│  ┌────────────────┐  ┌────────────────┐      │
│  │ ☐ Tôi là nhân  │  │ ☐ Tôi không    │      │
│  │   viên Parasola│  │   thuộc Parasola│     │
│  └────────────────┘  └────────────────┘      │
│                                              │
│  [ chỉ hiện khi chọn thẻ trái ]              │
│  Mã nhân viên                                │
│  ┌────────────────────────────────────┐      │
│  │ Nhập mã được cấp                   │      │
│  └────────────────────────────────────┘      │
│              [   Xác nhận   ]                │
└──────────────────────────────────────────────┘
```

Bước 2 giữ khung cảnh báo vàng của T-Fluencers, tóm tắt lựa chọn + mã, hai nút "Quay lại chỉnh sửa" / "Xác nhận".

**Phạm vi:** chỉ `parasola/`. `frontend/` và 12 folder partner còn lại **không đụng tới**.

**AC:**
- [ ] Modal không đóng được bằng X, ESC hay click ra ngoài
- [ ] Nhánh "không thuộc Parasola" **không** hiện ô mã, một click là xong
- [ ] Hai bước, có màn xác nhận trước khi gửi
- [ ] Giá trị lưu trong DB khớp giá trị user thấy
- [ ] Partner tắt tính năng → modal không xuất hiện
- [ ] Không hiện chồng với `ModalCompleteRegistration`
- [ ] **12 folder partner còn lại không có thay đổi nào trong diff**

---

### FR-010: Sửa lại trạng thái nhân viên

**Priority:** Must Have

**Vì sao cần.** FR-007 khiến modal chỉ hiện một lần; FR-017 backfill toàn bộ user cũ thành `not_employee`. Không có đường sửa thì:
- Nhân viên nhập nhầm mã → kẹt vĩnh viễn
- Nhân viên đăng ký trước ngày bật cờ → mất quyền vĩnh viễn
- Nhân viên nghỉ việc → không gỡ nhãn được
- Luật BVDLCN 2025 (hiệu lực 01/01/2026): người rời đi có quyền yêu cầu xoá dữ liệu — không có cơ chế thực thi

**Chi phí gần bằng 0.** `confirm-is-staff` đã cho ghi đè (FR-008) — chỉ cần thêm lối vào, không cần endpoint mới.

**Phía người dùng** — mục "Thông tin nhân viên" trong `parasola/src/pages/account/`:
- Đang `not_employee` hoặc chưa xác nhận → nhập mã, đổi sang nhân viên
- Đang `employee` → hiện mã, **không tự gỡ được**, hướng dẫn liên hệ hỗ trợ

Một chiều `not_employee → employee` để tránh trò bật tắt lách gate.

**Phía Admin** — nút "Sửa trạng thái nhân viên" trong `admin/src/pages/user-partner/`:
- Đổi được sang bất kỳ trạng thái nào
- Gỡ nhãn → gỡ luôn khỏi các segment `staff_import`
- Bắt buộc nhập lý do

**AC:**
- [ ] User tự chuyển `not_employee → employee` được
- [ ] User **không** tự gỡ được nhãn nhân viên
- [ ] Admin gỡ nhãn → user rời khỏi segment `staff_import`
- [ ] Nhân viên bị backfill nhầm ở FR-017 khai lại được

---

### FR-011: Chiến dịch dành riêng cho nhân viên

**Priority:** Must Have

Port đủ ba cơ chế của T-Fluencers vào `EventOpts`:

```go
ApplyForStaff    bool     `bson:"applyForStaff,omitempty"`
StaffCodes       []string `bson:"staffCodes,omitempty"`
ApplyForSegments []AppID  `bson:"applyForSegments,omitempty"`
```

`UserEventRaw` thiếu `Options`, cần bổ sung:
```go
type UserEventOpts struct {
    CodeInput      string `bson:"codeInput" json:"codeInput"`
    StatusEmployee string `bson:"statusEmployee" json:"statusEmployee"`
}
```

**Điểm chặn khi nộp bài:**

| Điều kiện | Kiểm tra | Lỗi |
|---|---|---|
| `ApplyForStaff` | `statusStaff == "employee"` | Chương trình này chỉ áp dụng cho nhân viên của công ty |
| `StaffCodes` | `user-events.options.codeInput` nằm trong danh sách | Bạn cần nhập mã để tham gia chương trình này |
| `ApplyForSegments` | thuộc segment trong danh sách **và** `IsStaff` | Bạn không đủ điều kiện tham gia chương trình này |

#### ⚠️ Ràng buộc cắm gate — bắt buộc

`content.go:123` đã có sẵn `Eligibility().JoinEvent()`. Hàm đó **không dùng được** cho gate nhân viên:

```go
// eligibility.go:216 — đã join thì thoát, không kiểm lại
if err == nil && !existingUserEvent.ID.IsZero() { return nil }
// eligibility.go:64 — Enabled = false thì Eligible = true (fail-open)
```

**Cấm nhét ba điều kiện trên vào `CalculateEligibility`.** Hậu quả: campaign chạy mở 3 ngày → 500 creator ngoài join → Marketing bật `applyForStaff` → 500 người đó vẫn nộp bài và nhận thưởng tới hết campaign.

Cách đúng — **khối kiểm tra độc lập, đặt trước `JoinEvent`**:
- Chạy ở **mỗi lần nộp bài**
- **Không phụ thuộc** `ParticipationRequirements.Enabled`
- Đọc `statusStaff` tươi mỗi lần
- Không grandfather

> **Lưu ý cho dev:** `content.go` của Ambassador **chưa load `userPartner`** (khác T-Fluencers có ở `content.go:105`). Phải thêm bước `UserPartnerDAO().FindOne({user, partner: event.Partner})` trước khối kiểm tra. Biến `event` thì đã có sẵn (`content.go:95`, `:107`).

#### `AllowedSegments` luôn AND với `IsStaff`

Segment là bảng admin ghi tay được. Nếu đứng một mình, admin thêm tay 1 user vào segment là user đó qua gate dù chưa từng nhập mã.

#### Cờ ra FE

`isRequireCode` trên event list và event detail, logic như T-Fluencers.

> **Nợ kế thừa có chủ ý.** T-Fluencers tính cờ này khác nhau: event list (`event.go:515`) = `len(StaffCodes) > 0`, không xét user đã nhập chưa; event detail (`event.go:1074`) chỉ `true` khi user chưa có mã hợp lệ. Cùng một event, hai màn hình trả hai giá trị. Port nguyên để giữ parity — ghi ra để dev không tưởng mình làm sai.

#### Admin UI — `admin/src/pages/event/components/modal.tsx`

Gom thành một section. Form này hiện dùng `Row`/`Col` với bộ `Rc*` (`RcSwitchFormNew`, `RcFormSelectNew`) và **chưa có `Divider` nào** — thêm `<Divider orientation="left">Cấu hình nhân viên</Divider>` là pattern mới cho file này, lấy từ form Partner.

```
──────── Cấu hình nhân viên ────────

[RcSwitchFormNew]  Chỉ dành cho nhân viên

[RcFormSelectNew mode="tags", cả dòng]  Mã tham gia riêng của chiến dịch
   tokenSeparators={[',', ' ', '\n']}
   Placeholder: Dán danh sách mã, phân tách bằng dấu phẩy hoặc xuống dòng
   Ghi chú: Khác với mã nhân viên ở trang Quản lý mã.

[RcFormSelectNew mode="multiple"]  Giới hạn theo nhóm nhân viên
```

**Ba quyết định về nhãn:**

| | T-Fluencers | Ambassador | Lý do |
|---|---|---|---|
| `applyForStaff` | "Chỉ nhân viên nội bộ" | **"Chỉ dành cho nhân viên"** | Parasola không phải ngân hàng, nhân sự cửa hàng cũng là nhân viên |
| `staffCodes` | "Mã code nhân viên" | **"Mã tham gia riêng của chiến dịch"** | Tên cũ trùng mã ở `/manage-code` nhưng hai vòng đời tách rời, Ops dễ nhầm |
| `applyForSegments` | "User Segment" | **"Giới hạn theo nhóm nhân viên"** | Bản gốc để tiếng Anh giữa form tiếng Việt |

**Cảnh báo khi chọn nhóm**, nếu partner còn mã chưa thuộc segment nào:
> ⚠️ Partner này còn {n} mã nhân viên chưa thuộc nhóm nào. Nhân viên dùng các mã đó sẽ không tham gia được chiến dịch này.

**AC:**
- [ ] Ba điều kiện hoạt động độc lập và kết hợp được
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] **Bật `applyForStaff` nhưng `Enabled = false` → người ngoài vẫn bị chặn**
- [ ] **User join khi campaign mở, admin bật `applyForStaff` sau → không nộp được bài kế tiếp**
- [ ] User trong segment `staff_import` nhưng `statusStaff != employee` → không qua gate
- [ ] Dán 200 mã một lần → tách đúng 200 tag
- [ ] Có test khẳng định gate nằm trên đường nộp bài, không nằm sau nhánh "đã join"

---

### FR-012: Thông báo khi không đủ điều kiện

**Priority:** Must Have

Port `modal-not-employee.tsx`. Modal này **đóng được** — khác FR-009.

| Trường hợp | Tiêu đề | Hành động |
|---|---|---|
| Không phải nhân viên, vào event `applyForStaff` | Thử thách này dành riêng cho nhân viên Parasola | Đã hiểu / Khám phá thêm |
| Không thuộc nhóm được phép | Bạn không đủ điều kiện tham gia chương trình này | Đã hiểu / Khám phá thêm |

**AC:**
- [ ] Modal đóng được, "Khám phá thêm" về trang chủ

---

### FR-013: Bật/tắt theo từng partner

**Priority:** Must Have

```go
EnableStaffCode            bool `bson:"enableStaffCode,omitempty"`
RequireStaffCodeValidation bool `bson:"requireStaffCodeValidation,omitempty"`
```

**UI** (`admin/src/pages/partner/components/modal.tsx`): section `<Divider orientation="left">Cấu hình nhân viên</Divider>` + 2 `<Form.Item>` với `<Switch />` của antd — **đúng cách 2 toggle BXH đang làm ở file này** (file này không dùng `RcSwitchFormNew`). Toggle thứ hai disable khi toggle thứ nhất tắt, dùng `<Form.Item noStyle shouldUpdate>` + render prop như BXH.

**AC:**
- [ ] Mặc định cả 2 = `false` — 13 partner hiện tại không đổi hành vi
- [ ] **Chỉ Parasola được bật khi release**
- [ ] Tắt `EnableStaffCode` → modal biến mất, API từ chối, dữ liệu giữ nguyên

---

### FR-014: Admin — hiển thị và lọc theo nhân viên/nhóm

**Priority:** Must Have

**Cột mới:** `Nhân viên` (Có/Không) \| `Mã nhân viên` \| `Nhóm`
**Filter mới:** `statusStaff` **(chọn nhiều)**, `segment` (chọn nhiều)

Theo quy ước toàn sản phẩm: mọi bộ lọc là multi-select (BE dùng `$in`, URL dạng CSV).

**AC:**
- [ ] Ba cột hiển thị đúng, rỗng hiện `—`
- [ ] Filter multi-select, kết hợp được với filter sẵn có

---

### FR-015: Thống kê theo nhóm nhân viên

**Priority:** Must Have

T-Fluencers chỉ tách nhị phân staff/guest. Giữ nguyên quy tắc tính của họ, thêm chiều nhóm từ FR-006.

| Nhóm | Số người | Đã tham gia | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|
| **Tổng — Nhân viên** | 210 | 168 | 1.180 | 3,1tr | 190tr |
| ├ Nhóm Miền Bắc | 85 | 72 | 520 | 1,4tr | 82tr |
| ├ Nhóm Miền Nam | 78 | 61 | 410 | 1,1tr | 68tr |
| ├ Khối Vận hành | 35 | 28 | 200 | 0,5tr | 33tr |
| └ Chưa phân nhóm | 12 | 7 | 50 | 0,1tr | 7tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9,3tr | 650tr |

**Quy tắc tính** — giữ quy ước T-Fluencers:
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên, không cộng dồn từng loại
- Không tính bài đã huỷ
- Nhân viên chưa thuộc segment nào gom vào "Chưa phân nhóm"

**Phân loại theo trạng thái hiện tại, không snapshot.** Nhân viên xác nhận muộn thì số kỳ cũ đổi theo. Đây cũng là hành vi T-Fluencers; khác ở chỗ Ambassador **in ghi chú rõ** trên bảng và export:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo.*

> ⚠️ **Chờ Parasola xác nhận:** nếu breakdown theo nhóm dùng để **chi tiền**, phải đóng băng `isStaff` + `segment` vào `ReconciliationItem` lúc chốt kỳ, nếu không số kỳ đã chốt vẫn đổi. T-Fluencers có snapshot đối soát nhưng **không phủ chiều nhân viên** — chỗ này không có tiền lệ để bám. Chỉ để xem thì giữ nguyên như trên.

**AC:**
- [ ] Tổng các nhóm con = dòng tổng "Nhân viên"
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] Có ghi chú "không bao gồm bài đã huỷ" và ghi chú phân loại theo trạng thái hiện tại
- [ ] Tải xong dưới 3 giây

---

### FR-016: Xuất dữ liệu

**Priority:** Should Have

Bổ sung 3 cột `Nhân viên` \| `Mã nhân viên` \| `Nhóm` vào file export hiện có; thêm nút export cho bảng FR-015.

**AC:**
- [ ] Excel và CSV đều có 3 cột mới
- [ ] Cột "Nhân viên" xuất "Có"/"Không"

---

### FR-017: Backfill user Parasola hiện có trước khi bật cờ

**Priority:** Must Have — **chặn release**

Parasola đang chạy thật và đã có user. Theo FR-007, `isOpenInputStaffCode` trả `true` cho mọi user có `statusStaff` rỗng — tức **toàn bộ user hiện có**. Bật cờ mà không backfill thì tất cả họ gặp modal blocking ở lần vào tiếp theo.

*"Migration dữ liệu: không cần"* chỉ đúng về schema. T-Fluencers gặp đúng chuyện này và phải viết script backfill.

```js
// Chạy TRƯỚC khi bật options.enableStaffCode
db.getCollection('user-partners').updateMany(
  { partner: <parasolaId>, statusStaff: { $exists: false } },
  { $set: { statusStaff: 'not_employee', updatedAt: new Date() } }
)
```

Chọn `not_employee` chứ không phải `not_verify` vì `not_verify` vẫn khiến modal bung.

**Đánh đổi:** nhân viên đăng ký trước ngày bật cờ bị gán nhầm là người ngoài — **khai lại được qua FR-010**, đó là lý do FR-010 là Must Have chứ không phải Should.

**AC:**
- [ ] Chạy trên staging trước, đếm số bản ghi bị ảnh hưởng
- [ ] Sau backfill + bật cờ, user cũ đăng nhập **không** thấy modal
- [ ] User mới đăng ký sau đó **vẫn** thấy modal
- [ ] Backfill chỉ chạm `statusStaff`
- [ ] Nhân viên bị gán nhầm khai lại được qua FR-010

---

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
- Field mới đều `omitempty`, không cần migration schema
- `EnableStaffCode` mặc định `false` — 13 partner hiện tại không đổi hành vi
- Segment hiện có không có `Type` → coi như `manual`, hành vi không đổi
- Không đụng `UserPartnerRaw.Code`

### NFR-002: Data Integrity
- Luồng `confirm-is-staff` không bao giờ ghi `isJoined`/`joinedAt`/`code`
- **Mọi truy vấn `user-segments` kèm điều kiện partner** (FR-003)
- Gán segment tự động idempotent
- Xoá segment bị từ chối khi còn được `events.options.applyForSegments` tham chiếu

### NFR-003: Performance
Quy mô nhân viên Parasola nhỏ. Các mốc dưới đây chỉ để chặn thiết kế sai kiểu N+1, không phải bài toán tải thật. **Không tối ưu sớm.**
- Import 1.000 mã < 10 giây
- Thống kê FR-015 < 3 giây
- "Áp dụng lại" segment < 10 giây

### NFR-004: Ngôn ngữ
**Chỉ tiếng Việt.** `parasola/` và `admin/` chỉ có `vi-VN.ts`, không có `en-US` — khác T-Fluencers (có `properties/en/`). Không thêm chuỗi tiếng Anh.

---

## 6. Epics và thứ tự

| Epic | FR | Ghi chú |
|---|---|---|
| **EPIC-000** Tiền đề | FR-003 | `user-segments` mang `partner` + backfill. **Xong trước EPIC-003 và EPIC-006** |
| **EPIC-001** Nền tảng | FR-001, 002, 013 | Model, constants, collection, index, tenant toggle |
| **EPIC-002** Quản lý mã | FR-004, 005 | Admin CRUD + import |
| **EPIC-003** Phân nhóm | FR-006 | Segment tự động + nút "Áp dụng lại" |
| **EPIC-004** Luồng người dùng | FR-007, 008, 009, 010 | API + modal + sửa lại |
| **EPIC-005** Chiến dịch | FR-011, 012 | Ba cơ chế gate + modal từ chối |
| **EPIC-006** Báo cáo | FR-014, 015, 016 | Cột, filter, thống kê, export |
| **EPIC-007** Phát hành | FR-017 | Backfill, chạy **trước** khi bật cờ |

---

## 7. Kiến trúc

```
Parasola phát mã (kênh nội bộ)
        │
        ▼
Admin import Excel 1 cột  →  manage-codes {partner, type, code}
Admin tạo segment automatic → segments {type, applyType: staff_code, staffCodes[]}
        │
        ▼
Nhân viên nhập mã  →  POST /users/confirm-is-staff
        ├──► user-partners  {statusStaff, staffCode}
        └──► CheckUserInSegmentWithStaffCode → user-segments {user, partner, segment, note}
        │
   ┌────┴───────────────┬────────────────────┐
   ▼                    ▼                    ▼
Gate chiến dịch      Thống kê            Hiển thị/Export
content.go           theo nhóm           admin user-partner
(độc lập JoinEvent)
```

---

## 8. Implementation Scope

### Thay đổi cần làm

| Vùng | File | Nội dung |
|---|---|---|
| **Model** | `model/mg/user_partner.go` | +2 field |
| **Model** | `model/mg/manage_code.go` | File mới |
| **Model** | `model/mg/segment.go` | +`Type`, +`ConditionForAutomatic` |
| **Model** | `model/mg/user_segment.go` | +`Partner`, +`Note` |
| **Model** | `model/mg/user_event.go` | +`Options` |
| **Model** | `model/mg/partner.go` | +2 field trong `PartnerOpts` |
| **Model** | `model/mg/event.go` | +3 field trong `EventOpts` |
| **Constants** | `constants/staff_code.go`, `constants/segments.go` | File mới |
| **DAO** | `module/database/mongodb/` | `ManageCodeDAO` + collection + index |
| **Service** | `internal/service/segment.go` | `CheckUserInSegmentWithStaffCode` + hàm "Áp dụng lại" |
| **Public API** | `pkg/public/{router,handler,service}/user.go` | `confirm-is-staff` |
| **Public API** | `pkg/public/{router,handler,service}/partner.go` | `status-employee` |
| **Public API** | `pkg/public/{router,handler,service}/event.go` | `input-code-join-event` |
| **Public API** | `pkg/public/service/content.go` | Load `userPartner` + 3 điểm chặn, **trước** `JoinEvent` |
| **Admin API** | `pkg/admin/{router,handler,service}/manage_code.go` | File mới |
| **Admin API** | `pkg/admin/service/segment.go` | `type` + `conditionForAutomatic` + "Áp dụng lại" |
| **Admin API** | `pkg/admin/service/user_segment.go` | `Delete` kiểm `IsAllowPartner` |
| **Admin API** | `pkg/admin/service/user_partner.go` | Trả thêm field + filter + sửa trạng thái |
| **Export** | `pkg/admin/service/export_*.go` | +3 cột |
| **Thống kê** | `aggregate_pipeline/` | Breakdown theo nhóm |
| **Locale** | `internal/locale/staff_code.go` + `properties/vi/` | Key mới, chỉ tiếng Việt |
| **Admin UI** | `admin/src/pages/manage-code/` | Trang mới |
| **Admin UI** | `admin/src/pages/segment/components/modal.tsx` | +type, +applyType, +danh sách mã, +nút Áp dụng lại |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | +Divider section, +2 `Form.Item`+`Switch` antd |
| **Admin UI** | `admin/src/pages/event/components/modal.tsx` | +Divider section, +1 `RcSwitchFormNew`, +2 `RcFormSelectNew` |
| **Admin UI** | `admin/src/pages/user-partner/` | +3 cột, +2 filter, +nút sửa trạng thái |
| **Admin UI** | `admin/src/pages/event-statistic/` | Tab thống kê theo nhóm |
| **Frontend** | `parasola/src/.../header/index.tsx` | Trigger modal |
| **Frontend** | `parasola/src/.../modal-staff-code.tsx`, `modal-not-employee.tsx` | Component mới |
| **Frontend** | `parasola/src/pages/account/` | Mục "Thông tin nhân viên" (FR-010) |
| **Frontend** | `parasola/src/models/main.ts`, `configs/api.ts`, `utils/staff.ts` | State, endpoint, mirror `isStaff` |

### KHÔNG làm

- **Không đụng `frontend/` và 12 folder partner còn lại** (`anker`, `flamingo`, `hdbank`, `lusso`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `vpbank`, `wildrift`, `yody`)
- Không bật cờ cho partner nào ngoài Parasola
- Không dùng lại `UserPartnerRaw.Code`
- Không ghi `isJoined`/`joinedAt` trong luồng xác nhận
- **Không nhét gate vào `CalculateEligibility`**
- Không dùng ENV toàn cục
- Không thêm cột nhóm vào file import
- Không thêm ràng buộc một-mã-một-người, rate limit, audit trail, transaction
- Không thêm chuỗi tiếng Anh
- Không đụng logic tính thưởng, xếp hạng, duyệt nội dung
- Không tự sinh mã — Parasola cấp, Admin import

---

## 9. Assumptions

1. Parasola phát mã qua kênh nội bộ; Ambassador không gửi mã
2. Parasola cung cấp danh sách mã và cho biết mã nào thuộc nhóm nào
3. Trạng thái nhân viên gắn theo partner, không phải toàn hệ thống
4. `parasola/` tiếp tục dùng Umi + dva; modal mới bám pattern `ModalCompleteRegistration`

---

## 10. Out of Scope

- Triển khai cho 12 partner còn lại
- Tự sinh mã hàng loạt trong hệ thống
- Hạn dùng cho mã
- Phân cấp nhóm nhiều tầng — phase 1 một tầng
- Snapshot trạng thái nhân viên theo từng bài đăng
- Phân quyền xem thống kê theo nhóm — admin partner thấy toàn bộ. **T-Fluencers cũng không có.**

### Bốn hạng mục T-Fluencers cũng chưa có — kèm rủi ro tồn dư

| Hạng mục | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|
| **Vòng đời nghỉ việc** — đồng bộ theo kỳ, thu hồi hàng loạt, HRIS/SCIM | Trung bình. Nhân viên nghỉ vẫn nhận campaign nội bộ tới khi Ops gỡ tay qua FR-010. Từ 01/01/2026 Luật BVDLCN 2025 + NĐ 356/2025 cho người rời đi quyền yêu cầu xoá dữ liệu — FR-010 là mức tối thiểu đáp ứng | >1.000 nhân viên, hoặc kỳ đối soát đầu phát hiện người đã nghỉ vẫn nhận thưởng |
| **Xác thực email tên miền công ty + OTP / SSO / SCIM** | Trung bình. Mã là bearer token, chuyền tay được. Phương án trung gian rẻ hơn SSO, mạnh hơn mã dùng chung — chưa đưa vào vì chưa biết Parasola có cấp email cho nhân sự cửa hàng không | Parasola xác nhận ≥90% nhân viên có email công ty |
| **Disclosure bắt buộc cho content nhân viên** | Trung bình. Luật 75/2025/QH15 hiệu lực 01/01/2026 buộc người chuyển tải sản phẩm quảng cáo thông báo trước và trong khi thực hiện. Hệ thống đã biết ai là nhân viên nên ép hashtag gần như miễn phí | Pháp chế yêu cầu, hoặc mở cho partner thứ hai |
| **Snapshot đối soát cấp content** | Thấp. T-Fluencers có (`content_snapshot`), Ambassador không. Tranh chấp thưởng chỉ truy được tới `reconciliation_item` | Có tranh chấp cần truy vết theo ngày |

### Nợ kỹ thuật ghi nhận

- **13 folder frontend fork.** Partner thứ hai là chép tay lần nữa toàn bộ modal + model + api.
- **`isRequireCode` lệch giữa event list và detail** — port nguyên từ T-Fluencers, xem FR-011.
- **Điều kiện `isUsed` khi xoá mã là code chết** — xem FR-002.

---

## 11. Traceability

| Yêu cầu gốc | FR đáp ứng |
|---|---|
| Có nơi để nhân viên nhập mã | FR-007, 008, 009, 010 |
| Có thống kê kết quả theo nhóm nhân viên | FR-003, 006, 014, 015, 016 |
| Có campaign dành riêng cho nhân viên | FR-011, 012 |
| Import nhân viên để về sau còn phân loại | FR-002, 004, 005, 006 |

| Priority | FR |
|---|---|
| **Must Have** (16) | FR-001 → FR-015, FR-017 |
| **Should Have** (1) | FR-016 |

Tổng 17 FR.

**Thứ tự bắt buộc:** FR-003 trước FR-006 và FR-015. FR-017 trước khi bật cờ ở FR-013.

---

## 12. Resolved Questions

1. **Bám theo T-Fluencers không?** → Có. Chỉ khác ở 3 điểm bắt buộc (2.2), 3 lỗi đã kiểm chứng (2.3), và phần T-Fluencers không có.
2. **Một mã dùng cho mấy người?** → Nhiều người, như T-Fluencers.
3. **Modal có chặn không?** → Có, blocking. Khác một điểm: chỉ nhánh nhân viên nhập mã (FR-009).
4. **Có port `staffCodes` theo event không?** → Có, đủ ba cơ chế.
5. **Phân nhóm bằng cách nào?** → Segment tự động port từ T-Fluencers, thêm `applyType: staff_code`. **Không** thêm cột `group` vào file import.
6. **Format mã?** → `PRS_<8 hex ngẫu nhiên viết hoa>`, sinh bằng `f"PRS_{secrets.token_hex(4).upper()}"` như Handbook hướng dẫn.
7. **Bật/tắt bằng gì?** → `PartnerOpts` thay ENV.
8. **Tên trường mã?** → `staffCode`, vì `Code` đã là referral.
9. **Gọi lại `confirm-is-staff` khi đã xác nhận?** → **Cho ghi đè**, như T-Fluencers. Đây là nền tảng của FR-010.
10. **Sửa lại trạng thái?** → **Có** (FR-010). T-Fluencers không có UI nhưng API vốn cho ghi đè. Bắt buộc vì FR-017 backfill tạo ra nhu cầu này.
11. **Sửa danh sách mã trong segment có hồi tố?** → **Không tự động**, phải bấm "Áp dụng lại" (FR-006). Không có nút này thì nhân viên chuyển bộ phận kẹt nhóm cũ vĩnh viễn.
12. **Ngôn ngữ?** → **Chỉ tiếng Việt.** Ambassador không có `en-US`.

---

## 13. Open Questions

**Chặn FR-015, không chặn EPIC-000 → 005:**

1. **Breakdown theo nhóm có dùng để chi tiền không?**
   - Không (chỉ để xem) → giữ FR-015 như hiện tại
   - Có → đóng băng `isStaff` + `segment` vào `ReconciliationItem` lúc chốt kỳ

**Cần Parasola xác nhận, không chặn code:**

2. Có phát mã cho nhân viên không, qua kênh nào
3. Chia nhóm theo tiêu chí gì, mã nào thuộc nhóm nào
4. Có chiến dịch nội bộ nào định chạy không — nếu không, FR-011 có thể hạ ưu tiên

Bối cảnh: tính năng **không nằm trong yêu cầu hệ thống gốc** Parasola gửi (`[AT - PV] Parasola Ambassador_Working file Final - 2. Yêu cầu hệ thống_Parasola.csv` không nhắc gì tới nhân viên), chưa có BR, chưa kickoff.

---

## 14. Revision History

| Version | Date | Changes |
|---------|------|---------|
| **4.0** | 2026-08-07 | **Bản chốt.** Áp feedback review của Vinh Nguyễn + kết quả tự soát lại toàn bộ khẳng định với code.<br>**FR mới:** FR-003 (`user-segments` thiếu `partner` — chặn FR-006/015), FR-010 (sửa lại trạng thái — bị cắt nhầm ở v2.0 khiến FR-017 tự mâu thuẫn), FR-017 (backfill user hiện có).<br>**FR-006:** thêm nút "Áp dụng lại" — sửa danh sách mã trong segment vốn không hồi tố, PRD v3.x hứa sai chỗ này.<br>**FR-011:** ràng buộc cấm nhét gate vào `CalculateEligibility`; `AllowedSegments` AND `IsStaff`; ghi nhận nợ `isRequireCode`; **lưu ý `content.go` chưa load `userPartner`** — code mẫu ở techspec v3.x không compile.<br>**FR-002:** ghi rõ điều kiện `isUsed` khi xoá mã là code chết.<br>**FR-008:** ghi rõ cho phép ghi đè khi gọi lại.<br>**Sửa 3 mô tả sai:** partner modal dùng antd `Switch` chứ không phải `RcSwitchFormNew`; event modal chưa có `Divider` nào; NFR-004 đòi VI+EN trong khi Ambassador chỉ có `vi-VN`.<br>**FR-009:** sửa lập luận sai — nhánh "không phải nhân viên" ở T-Fluencers không validate mã nên không phải ngõ cụt; lý do đúng là dữ liệu rác + copy sai.<br>Đánh số FR lại liền mạch, bỏ FR-002b. 14 → 17 FR |
| 3.2 | 2026-08-07 | Áp một phần feedback review |
| 3.0–3.1 | 2026-08-06 | Phân nhóm chuyển sang segment tự động port từ T-Fluencers |
| 2.0 | 2026-08-06 | Viết lại theo hướng bám T-Fluencers, bỏ các thay đổi tự đề xuất |
| 1.0–1.6 | 2026-08-06 | Bản đầu và các vòng soát |
