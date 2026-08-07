# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 3.2 — bản chốt
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
- ~~T-Fluencers SRS `/srs/admin-portal/14-code`~~ — **không dùng làm căn cứ**: trang mô tả mã gán theo `Ref (Event)` và trạng thái `USED`, không khớp implementation (mã gắn partner, `isUsed` không bao giờ set ở luồng live)
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

**Index:** `{partner, code}`, `{partner, isUsed}` — **không unique**, như T-Fluencers.

Chống trùng mã làm ở **tầng service** (đọc trước, chặn nếu đã có). Nghĩa là hai admin import cùng lúc vẫn có thể tạo ra hai bản ghi cùng mã. Chấp nhận có ý thức: import là thao tác thủ công hiếm, hệ quả của mã trùng chỉ là một dòng thừa trong danh sách chứ không ảnh hưởng luồng xác nhận (`FindOne` lấy bản ghi đầu tiên là đủ để validate).

**Acceptance Criteria:**
- [ ] Tạo mã trùng trong cùng partner → báo lỗi (kiểm tra ở tầng service như T-Fluencers)
- [ ] Luồng `confirm-is-staff` **không** ghi `isUsed`/`usedBy`/`usedAt`

---

### FR-002b: `user-segments` phải mang `partner`

**Priority:** Must Have — **prerequisite của FR-005 và FR-013, làm TRƯỚC**

**Vấn đề.** `UserSegmentRaw` hiện là `{User, Segment, CreatedAt, CreatedBy}` — **không có `partner`**. `SegmentRaw.Partner` có nhưng `omitempty`, tồn tại segment global cũ. Toàn bộ phân nhóm nhân viên (FR-005) và thống kê (FR-013) cưỡi lên bảng này, nên thiếu tenant discriminator là lỗi chặn release:

| Hệ quả | Chi tiết |
|---|---|
| Báo cáo gán nhầm nhóm | Một người vừa là NV Parasola vừa nằm trong segment marketing của partner khác → thống kê Parasola gán họ vào nhóm của partner kia, **và tên nhóm partner khác hiện lên trong báo cáo Parasola** |
| Admin partner khác xoá được nhóm NV Parasola | `pkg/admin/service/user_segment.go:110` — `Delete` xoá theo `{_id: {$in: ids}}`, **không gọi `IsAllowPartner`** (trong khi `Add` cùng file thì có) |

Ambassador ở **pool model** (shared DB, tenant discriminator). Nguyên tắc của mô hình này: mọi bảng tenant-scoped phải mang tenant id, và filter fail-closed ở tầng dưới — không dựa vào kỷ luật viết query, vì một điều kiện quên là một lần rò dữ liệu.

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/user_segment.go
Partner AppID  `bson:"partner,omitempty" json:"partner,omitempty"`
Note    string `bson:"note,omitempty" json:"note,omitempty"`   // dùng ở FR-005
```

Backfill `partner` từ `segments.partner` cho bản ghi hiện có.

**Acceptance Criteria:**
- [ ] `user-segments` có `partner`, đã backfill xong trước khi triển khai FR-005
- [ ] **Mọi truy vấn / `$lookup` trên `user-segments` đều kèm điều kiện partner** — không có ngoại lệ
- [ ] `UserSegment.Delete` kiểm `IsAllowPartner` như `Add`
- [ ] Admin partner A không xoá được bản ghi `user-segments` của partner B
- [ ] Thống kê FR-013 không bao giờ hiển thị tên segment của partner khác

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

**Bắt buộc chọn partner tường minh.** `StaffRaw.Partner` là đơn trị và `IsPermissionAllPartner()` trả `true` khi `Partner` rỗng — admin chưa gắn partner tự động thành super-admin xuyên tenant. Với dữ liệu nhân sự thì mặc định đó sai hướng:
- Trang `/manage-code` **không có chế độ "tất cả partner"**
- Import / xoá đều yêu cầu `partner` trong request, không suy ra từ session

**Acceptance Criteria:**
- [ ] CRUD hoạt động, chặn trùng mã trong cùng partner
- [ ] Xoá mã đã dùng → từ chối kèm thông báo
- [ ] Admin có `Partner` rỗng **không** xem được danh sách mã của mọi partner

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

**Segment sinh ra từ luồng mã nhân viên mang `source: "staff_import"`** — dùng ở FR-005 để phân biệt với segment marketing thông thường.

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

#### Segment nhân viên là org unit, không phải audience marketing

Hai khái niệm khác nhau, PRD này tách rõ:

| | Segment marketing | Segment nhân viên |
|---|---|---|
| Ai định nghĩa | Marketer, tự do | Sinh từ danh sách mã |
| Dùng để | Lọc, gửi thông báo | **Gate quyền tham gia** |
| Sửa thành viên | Thêm/xoá tay thoải mái | **Không cho thêm/xoá tay** |

Segment mang `source: "staff_import"` **không cho admin thêm/xoá thành viên thủ công** trên UI. Thành viên chỉ thay đổi qua việc nhân viên nhập mã, hoặc admin sửa danh sách mã trong segment. Nếu cho thêm tay, một người có quyền admin đưa user vào segment *"Nhóm Miền Bắc"* là user đó qua gate campaign nhân viên mà chưa từng nhập mã.

**Acceptance Criteria:**
- [ ] Thêm tay user vào segment `staff_import` → **bị từ chối**
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
5. Nếu isStaff = true → CheckUserInSegmentWithStaffCode(userId, partnerId, code)   ← FR-005
```

Bước 5 gọi cơ chế FR-005, đúng như T-Fluencers gọi `CheckUserInSegmentWithReferralCode` sau khi user nhập mã giới thiệu. Khác nguồn một tham số: có thêm `partnerId` để mã của partner này không kéo user vào segment của partner khác — T-Fluencers một partner nên không cần.

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
- **Chỉ nhánh "là nhân viên" mới nhập mã**; nút Xác nhận khoá tới khi có mã (xem lý do bên dưới)
- Hai bước: chọn + nhập mã → màn xác nhận tóm tắt → Confirm
- Lựa chọn ghi nhận cố định, không tự thay đổi được
- Lỗi từ backend hiển thị dưới ô mã, không đóng modal

**Sửa một lỗi hiển thị của T-Fluencers:** bản gốc hiển thị mã viết hoa (`value={employeeCode?.toUpperCase()}`) nhưng gửi lên nguyên bản (`code: employeeCode.trim()`) — user thấy `ABC123`, DB lưu `abc123`. Ambassador chuẩn hoá để giá trị lưu khớp giá trị hiển thị.

#### Vì sao bỏ ràng buộc "người ngoài cũng nhập mã" của T-Fluencers

T-Fluencers khoá nút Xác nhận ở **cả hai** nhánh: `disabled={isTcbEmployee === null || !employeeCode.trim()}`. Người chọn *"Tôi không thuộc Techcombank"* vẫn phải nhập một mã họ không được cấp.

Với Ambassador đây là **ngõ cụt thật**, không phải chuyện thẩm mỹ: modal blocking + không có mã ⇒ creator ngoài **không dùng được web nữa**. TCB thoát được vì gần như toàn bộ người dùng của họ là CBNV; Parasola thì ngược lại, creator ngoài chiếm đa số (P2).

Nên Ambassador giữ nguyên mọi thứ khác của modal TCB — blocking, hai bước, lựa chọn cố định — riêng nhánh *"Tôi không thuộc Parasola"* thì **một click là xong**, không cần mã.

#### Bố cục — bám component sẵn có của Parasola

Dùng `AppModal` (`parasola/src/components/app/modal`) với `closeButton={false}`, `keyboard={false}`, `hideFooter` — đúng cấu hình `ModalCompleteRegistration` đang dùng. Ô nhập dùng `components/form/input`.

```
┌──────────────────────────────────────────────┐
│  [logo]  Bạn có phải nhân viên Parasola?     │   ← không có nút X
├──────────────────────────────────────────────┤
│  Parasola có những chiến dịch dành riêng     │
│  cho nhân viên nội bộ.                       │
│                                              │
│  ┌────────────────┐  ┌────────────────┐      │
│  │   [icon]       │  │   [icon]       │      │
│  │ ─────────────  │  │ ─────────────  │      │
│  │ ☐ Tôi là nhân  │  │ ☐ Tôi không    │      │
│  │   viên Parasola│  │   thuộc Parasola│     │
│  └────────────────┘  └────────────────┘      │
│                                              │
│  [ chỉ hiện khi chọn thẻ trái ]              │
│  Mã nhân viên                                │
│  ┌────────────────────────────────────┐      │
│  │ Nhập mã được cấp                   │      │
│  └────────────────────────────────────┘      │
│  ⚠ lỗi từ backend hiện ở đây                 │
│                                              │
│              [   Xác nhận   ]                │
└──────────────────────────────────────────────┘
```

Bước 2 — màn xác nhận, giữ nguyên khung cảnh báo vàng của TCB:

> ⚠ Bạn đang xác nhận rằng bạn **là / không phải là** nhân viên Parasola
> Mã xác minh: **PRS_A3F91B2C**
>
> Parasola sẽ dựa trên lựa chọn này để hiển thị chiến dịch phù hợp.
> Lựa chọn này được ghi nhận cố định và không thay đổi được.
>
> [ Quay lại chỉnh sửa ]  [ Xác nhận ]

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
| `ApplyForSegments` | đếm `user-segments` giao với danh sách > 0 **và** `IsStaff(statusStaff)` | Bạn không đủ điều kiện tham gia chương trình này |

#### ⚠️ Ràng buộc cắm gate — bắt buộc

`content.go:123` **đã có sẵn** `Eligibility().JoinEvent()`. Hàm đó hiện có hai đặc tính khiến nó **không dùng được** cho gate nhân viên:

```go
// eligibility.go:216 — đã join thì thoát, không kiểm lại
if err == nil && !existingUserEvent.ID.IsZero() { return nil }

// eligibility.go:64 — Enabled = false thì Eligible = true (fail-open)
if event.ParticipationRequirements == nil || !event.ParticipationRequirements.Enabled { ... }
```

**Cấm nhét ba điều kiện trên vào `CalculateEligibility`.** Làm vậy sẽ dính cả hai lỗi: campaign chạy mở 3 ngày → 500 creator ngoài join → Marketing bật `applyForStaff` → 500 người đó vẫn nộp bài và nhận thưởng tới hết campaign.

Cách đúng — **khối kiểm tra độc lập, đặt trước lời gọi `JoinEvent`**:
- Chạy ở **mỗi lần nộp bài**, không chỉ lần join đầu
- **Không phụ thuộc** `ParticipationRequirements.Enabled` — bật `applyForStaff` là đủ để gate hoạt động
- Đọc `statusStaff` tươi mỗi lần, không cache
- Không grandfather: người đã join trước khi bật điều kiện, nếu không thoả, bị chặn từ bài kế tiếp

Đây đúng cách T-Fluencers làm (`content.go:105-120`) — không sửa `JoinEvent` để tránh đụng luồng đang chạy của 12 partner khác.

#### `AllowedSegments` luôn AND với `IsStaff`

Segment là bảng admin ghi tay được. Nếu `ApplyForSegments` đứng một mình, người có quyền admin thêm tay 1 user vào segment *"Nhóm Miền Bắc"* là user đó qua gate **dù chưa từng nhập mã nào**. Gate bảo vệ tiền không được tin vào bảng ai cũng ghi được.

Nên khi segment thuộc loại `staff_import` (FR-004), điều kiện luôn là `IsStaff AND inSegment`, bất kể admin có bật `ApplyForStaff` hay không.

**Mã riêng theo event:** `POST /events/:id/input-code-join-event` → upsert `user-events.options {codeInput, statusEmployee}`.

`UserEventRaw` của Ambassador hiện **thiếu** `Options` — cần bổ sung:
```go
type UserEventOpts struct {
    CodeInput      string `bson:"codeInput" json:"codeInput"`
    StatusEmployee string `bson:"statusEmployee" json:"statusEmployee"`
}
```

**Cờ ra FE:** `isRequireCode` trên event list và event detail, logic như T-Fluencers.

> **Nợ kế thừa có chủ ý.** T-Fluencers tính cờ này khác nhau ở hai chỗ: event list (`event.go:515`) = `len(StaffCodes) > 0`, **không xét user đã nhập mã chưa**; event detail (`event.go:1074`) chỉ `true` khi user **chưa** có mã hợp lệ. Cùng một event, hai màn hình trả hai giá trị. Ambassador port nguyên để giữ parity — ghi ra đây để dev không tưởng mình làm sai, và để lần sau có căn cứ sửa.

#### Admin UI — `admin/src/pages/event/components/modal.tsx`

Gom thành một section, theo pattern `<Divider orientation="left">` mà form Partner đang dùng cho *"Cấu hình BXH"* / *"Cấu hình nội dung"*. T-Fluencers để ba trường rải rác giữa các trường khác, Ops khó tìm.

```
──────── Cấu hình nhân viên ────────

[Switch]  Chỉ dành cho nhân viên
          Chỉ người đã xác nhận là nhân viên mới nộp bài được.

[Select tags, cả dòng]  Mã tham gia riêng của chiến dịch
          Placeholder: Dán danh sách mã, phân tách bằng dấu phẩy hoặc xuống dòng
          Ghi chú dưới ô: Khác với mã nhân viên ở trang Quản lý mã.
                          Mã ở đây chỉ dùng cho chiến dịch này.

[Select nhiều]  Giới hạn theo nhóm nhân viên
          Chỉ liệt kê segment của partner đang chọn
```

**Ba quyết định về nhãn:**

| | T-Fluencers | Ambassador | Lý do |
|---|---|---|---|
| `applyForStaff` | "Chỉ nhân viên nội bộ" | **"Chỉ dành cho nhân viên"** | Bỏ chữ "nội bộ" vì Parasola không phải ngân hàng, nhân sự cửa hàng cũng là nhân viên |
| `staffCodes` | "Mã code nhân viên" | **"Mã tham gia riêng của chiến dịch"** | Tên cũ trùng với mã ở `/manage-code` nhưng là hai vòng đời tách rời — Ops rất dễ nhầm |
| `applyForSegments` | "User Segment" | **"Giới hạn theo nhóm nhân viên"** | Bản gốc để tiếng Anh giữa form tiếng Việt |

Giữ nguyên `mode="tags"` với `tokenSeparators={[',', ' ', '\n']}` — Ops copy một cột Excel dán thẳng vào là ra đủ mã.

**Cảnh báo khi chọn nhóm.** Nếu partner còn mã chưa thuộc segment nào, hiện ngay dưới ô:

> ⚠️ Partner này còn {n} mã nhân viên chưa thuộc nhóm nào. Nhân viên dùng các mã đó sẽ không tham gia được chiến dịch này.

**Acceptance Criteria:**
- [ ] Ba điều kiện hoạt động độc lập và kết hợp được
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] Chỉ chọn được segment thuộc partner của event
- [ ] **Bật `applyForStaff` nhưng `ParticipationRequirements.Enabled = false` → người ngoài vẫn bị chặn**
- [ ] **User join khi campaign còn mở, admin bật `applyForStaff` sau → user đó không nộp được bài kế tiếp**
- [ ] User nằm trong segment `staff_import` nhưng `statusStaff != employee` → **không qua gate**
- [ ] Dán 200 mã một lần vào ô "Mã tham gia riêng" → tách đúng 200 tag
- [ ] Có test khẳng định gate nằm trên đường nộp bài, không nằm sau nhánh "đã join"

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
**Filter mới:** `statusStaff` **(chọn nhiều)** — Nhân viên / Không phải / Chưa xác nhận; `segment` (chọn nhiều)

Theo quy ước áp dụng toàn sản phẩm: mọi bộ lọc là multi-select (BE dùng `$in`, URL dạng CSV).

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
| ├ Nhóm Miền Bắc | 80 | 68 | 500 | 1,3tr | 78tr |
| ├ Nhóm Miền Nam | 78 | 61 | 410 | 1,1tr | 68tr |
| ├ Khối Vận hành | 35 | 28 | 200 | 0,5tr | 33tr |
| ├ Thuộc nhiều nhóm | 5 | 4 | 20 | 0,1tr | 4tr |
| └ Chưa phân nhóm | 12 | 7 | 50 | 0,1tr | 7tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9,3tr | 650tr |

#### Định nghĩa cột

| Cột | Định nghĩa |
|---|---|
| **Số người** | Số user có `IsStaff(statusStaff) = true` ở partner đang xem, trong phạm vi bộ lọc |
| **Đã tham gia** | Trong số đó, số user có **ít nhất một bài không bị huỷ** trong phạm vi bộ lọc |
| Số bài / Lượt xem / Chi phí | Cộng dồn từ bài không bị huỷ trong phạm vi bộ lọc |

#### "Nhóm nhân viên" là segment nào

Chỉ tính segment thoả **cả ba**: `type = automatic`, `applyType = staff_code`, và thuộc đúng partner đang xem.

Segment thủ công và segment `applyType = referral_code` **không** phải nhóm nhân viên — user nằm trong các segment đó vì lý do khác, gộp vào sẽ ra số vô nghĩa.

#### Một người thuộc nhiều nhóm

FR-005 cho phép một mã nằm trong nhiều segment, nên một nhân viên có thể thuộc từ hai nhóm trở lên. Quy tắc:

- **Mỗi người được đếm đúng một lần**, vào dòng riêng **"Thuộc nhiều nhóm"** — không đếm lặp vào từng nhóm, cũng không chọn bừa một nhóm
- Nhờ vậy tổng các dòng con luôn bằng dòng tổng "Nhân viên", Ops đối soát được
- Ops **nên** cấu hình mỗi mã chỉ thuộc một segment nhân viên. Dòng "Thuộc nhiều nhóm" khác 0 là tín hiệu cấu hình segment bị chồng lấn, cần xem lại

**Quy tắc tính** — giữ nguyên quy ước T-Fluencers:
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên, không cộng dồn từng loại
- Không tính bài đã bị huỷ
- Nhân viên không thuộc segment nhân viên nào gom vào "Chưa phân nhóm"

**Phân loại theo trạng thái hiện tại, không snapshot.** Nhân viên xác nhận muộn thì số liệu kỳ cũ thay đổi theo. Đây cũng là hành vi T-Fluencers; khác ở chỗ Ambassador **in ghi chú rõ** trên bảng và export:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo.*

**Acceptance Criteria:**
- [ ] Tổng các nhóm con = dòng tổng "Nhân viên" — kể cả khi có người thuộc nhiều nhóm
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] User thuộc 2 segment nhân viên → nằm ở dòng "Thuộc nhiều nhóm", **không** bị đếm hai lần
- [ ] User nằm trong segment thủ công hoặc segment `referral_code` → **không** bị tính là nhóm nhân viên
- [ ] Segment của partner khác không lọt vào bảng
- [ ] Có ghi chú "không bao gồm bài đã huỷ" và ghi chú phân loại theo trạng thái hiện tại
- [ ] Tải xong dưới 3 giây

---

### FR-014: Xuất dữ liệu

**Priority:** Should Have

Bổ sung 3 cột `Nhân viên` \| `Mã nhân viên` \| `Nhóm` vào file export hồ sơ/creator hiện có; thêm nút export cho bảng FR-013.

Nguồn dữ liệu: `UserPartnerRaw.StaffCode`. T-Fluencers còn fallback sang `UserRaw.StaffCode`, nhưng `UserRaw` của Ambassador **không có** field đó — không port phần fallback.

**Acceptance Criteria:**
- [ ] Excel và CSV đều có 3 cột mới
- [ ] Cột "Nhân viên" xuất "Có"/"Không"

---

### FR-015: Xử lý user Parasola hiện có trước khi bật cờ

**Priority:** Must Have — **chặn release**

**Vấn đề.** Parasola đang chạy thật và đã có user. Theo FR-006, `isOpenInputStaffCode` trả `true` cho mọi user có `statusStaff` rỗng — tức là **toàn bộ user hiện có**. Ngày bật cờ, tất cả họ gặp modal blocking ở lần vào tiếp theo.

Ghi chú *"Migration dữ liệu: không cần"* ở NFR-001 chỉ đúng về schema. Về vận hành thì đây là cú sốc trải nghiệm cho toàn bộ tập người dùng đang hoạt động. T-Fluencers gặp đúng chuyện này và phải viết script backfill (`pkg/admin/service/migration.go`).

**Giải pháp — backfill trước khi bật cờ:**

```js
// Đánh dấu toàn bộ user Parasola hiện có là "không phải nhân viên".
// Chạy TRƯỚC khi bật options.enableStaffCode.
db.getCollection('user-partners').updateMany(
  { partner: <parasolaId>, statusStaff: { $exists: false } },
  { $set: { statusStaff: 'not_employee', updatedAt: new Date() } }
)
```

Sau bước này chỉ **user mới** thấy modal. Nhân viên đã đăng ký từ trước vẫn khai được qua trang Hồ sơ (đường sửa ở FR-009 phía admin), hoặc Ops đổi tay.

**Vì sao chọn `not_employee` chứ không phải `not_verify`:** `not_verify` vẫn khiến `isOpenInputStaffCode` trả `true` → modal vẫn bung. Mục đích của backfill là để không bung.

**Đánh đổi đã cân nhắc:** nhân viên đăng ký trước ngày bật cờ sẽ bị gán nhầm là người ngoài, phải khai lại thủ công. Chấp nhận được vì số nhân viên Parasola nhỏ, và đổi lại không làm phiền toàn bộ creator ngoài đang hoạt động.

**Acceptance Criteria:**
- [ ] Chạy backfill trên staging trước, đếm số bản ghi bị ảnh hưởng
- [ ] Sau backfill + bật cờ, user cũ đăng nhập **không** thấy modal
- [ ] User mới đăng ký sau đó **vẫn** thấy modal
- [ ] Backfill chỉ chạm `statusStaff`, không đụng field nào khác
- [ ] Có đường cho nhân viên đăng ký trước đó khai lại

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
- Xoá segment bị từ chối khi còn được `events.options.applyForSegments` tham chiếu — thực thi ở `pkg/admin/service/segment.go` (Delete). Bỏ sót chỗ này thì event thành gate rỗng, âm thầm chặn hoặc cho qua tất cả

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
| **EPIC-000** Tiền đề | **FR-002b** | `user-segments` mang `partner` + backfill. **Phải xong trước EPIC-003 và EPIC-006** |
| **EPIC-001** Nền tảng | FR-001, 002, 011 | Model, constants, collection, index, tenant toggle |
| **EPIC-002** Quản lý mã | FR-003, 004 | Admin CRUD + import |
| **EPIC-003** Phân nhóm | FR-005 | Segment tự động theo mã nhân viên |
| **EPIC-004** Luồng người dùng | FR-006, 007, 008 | API + modal Parasola |
| **EPIC-005** Chiến dịch | FR-009, 010 | Ba cơ chế gate + modal từ chối |
| **EPIC-006** Báo cáo | FR-012, 013, 014 | Cột, filter, thống kê theo nhóm, export |
| **EPIC-007** Phát hành | **FR-015** | Backfill user hiện có, chạy **trước** khi bật cờ |

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
| **Admin API** | `pkg/admin/service/segment.go` | Hỗ trợ `type` + `conditionForAutomatic`; chặn xoá segment còn được `events.options.applyForSegments` tham chiếu (NFR-002) |
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
- Phân quyền xem thống kê theo nhóm — admin partner thấy toàn bộ. **T-Fluencers cũng không có.**

### Bốn hạng mục T-Fluencers cũng chưa có — ghi kèm rủi ro tồn dư

Không có tiền lệ để bám, không gánh trong phase này. Ghi ra để lần sau không ai tưởng đã làm.

| Hạng mục | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|
| **Vòng đời nghỉ việc** — đồng bộ theo kỳ, thu hồi hàng loạt, HRIS/SCIM | Trung bình. Nhân viên nghỉ vẫn nhận campaign nội bộ tới khi Ops gỡ tay. Ngang T-Fluencers vì cùng dùng mã dùng chung. Từ 01/01/2026 Luật BVDLCN 2025 + NĐ 356/2025 cho người rời đi quyền yêu cầu xoá dữ liệu — FR-009 (admin gỡ, có lý do) là mức tối thiểu, **phải giữ trong scope** | >1.000 nhân viên, hoặc kỳ đối soát đầu phát hiện người đã nghỉ vẫn nhận thưởng |
| **Xác thực bằng email tên miền công ty + OTP / SSO / SCIM** | Trung bình. Mã là bearer token viết trên giấy, chuyền tay được. Đây là phương án trung gian rẻ hơn SSO nhiều bậc, mạnh hơn mã dùng chung nhiều bậc — chưa đưa vào vì chưa biết Parasola có cấp email cho nhân sự cửa hàng không | Parasola xác nhận ≥90% nhân viên có email tên miền công ty |
| **Disclosure bắt buộc cho content nhân viên** | Trung bình. Luật Quảng cáo sửa đổi (Luật 75/2025/QH15) hiệu lực 01/01/2026 buộc người chuyển tải sản phẩm quảng cáo thông báo trước và trong khi thực hiện. Hệ thống đã biết ai là nhân viên nên ép hashtag cho nhóm này gần như miễn phí | Pháp chế yêu cầu, hoặc khi mở cho partner thứ hai |
| **Snapshot đối soát cấp content** | Thấp. T-Fluencers **có** (`content_snapshot`), Ambassador không. Khi tranh chấp thưởng chỉ truy được tới `reconciliation_item`, không có chuỗi lịch sử view theo ngày | Có tranh chấp cần truy vết theo ngày |

### Nợ kỹ thuật ghi nhận

- **13 folder frontend fork.** Phase này chỉ làm `parasola/`. Partner thứ hai là chép tay lần nữa toàn bộ modal + model + api, không có cơ chế dùng chung.
- **`isRequireCode` lệch giữa event list và detail** — port nguyên từ T-Fluencers, xem ghi chú ở FR-009.

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
| **Must Have** (15) | FR-001, **002b**, 002 → 013, **015** |
| **Should Have** (1) | FR-014 |

Tổng 16 FR.

**Thứ tự bắt buộc:** FR-002b trước FR-005 và FR-013 (cả hai xây trên `user-segments`, sửa sau thì phải làm lại). FR-015 chạy trước khi bật cờ ở FR-011.

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

### Chặn code — cần quyết trước khi bắt đầu

1. **Breakdown theo nhóm có dùng để chi tiền không?**
   - **Không** (chỉ để xem) → giữ nguyên FR-013 như hiện tại: phân loại theo trạng thái tại thời điểm xem, có ghi chú trên bảng
   - **Có** → phải đóng băng `isStaff` + `segment` vào `ReconciliationItem` lúc chốt kỳ, nếu không thì số kỳ đã chốt vẫn đổi khi có người xác nhận muộn. T-Fluencers có snapshot đối soát nhưng **không phủ chiều nhân viên** — chỗ này không có tiền lệ để bám

### Cần Parasola xác nhận — không chặn code backend

2. Có phát mã cho nhân viên không, phát qua kênh nào
3. Chia nhóm theo tiêu chí gì (phòng ban / khu vực / cửa hàng), và mã nào thuộc nhóm nào
4. Có chiến dịch nội bộ nào định chạy không — nếu không, FR-009 có thể hạ ưu tiên

Lưu ý bối cảnh: tính năng này **không nằm trong yêu cầu hệ thống gốc** Parasola gửi (`[AT - PV] Parasola Ambassador_Working file Final - 2. Yêu cầu hệ thống_Parasola.csv` không nhắc gì tới nhân viên), và task chưa có BR, chưa kickoff. Toàn bộ PRD đang đứng trên giả định.

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| **3.2** | 2026-08-07 | Nguyễn Đăng Định | Áp feedback review của Vinh Nguyễn (`review-feedback-2026-08-07.md`) + soát bổ sung. **Thêm FR-002b** (`user-segments` thiếu `partner` — chặn FR-005/FR-013) và **FR-015** (backfill user Parasola hiện có trước khi bật cờ — nếu không, toàn bộ creator đang hoạt động bị modal chặn). **FR-009:** ràng buộc cấm nhét gate vào `CalculateEligibility`, `AllowedSegments` luôn AND `IsStaff`, ghi nhận nợ `isRequireCode`. **FR-003** bắt buộc partner tường minh. **FR-004/005** segment `staff_import` không cho thêm thành viên tay. **FR-012** filter multi-select. **FR-008** bỏ ràng buộc người ngoài nhập mã (ngõ cụt thật với Parasola) + chốt bố cục UI. Out of Scope thêm 4 hạng mục kèm rủi ro tồn dư + 2 nợ kỹ thuật |
| **3.1** | 2026-08-06 | Nguyễn Đăng Định | Soát nhất quán với code Ambassador. **FR-013:** chốt định nghĩa cột "Số người"/"Đã tham gia"; chốt "nhóm nhân viên" chỉ gồm segment `automatic` + `applyType: staff_code` + đúng partner (trước đó không giới hạn → segment thủ công lọt vào); thêm dòng "Thuộc nhiều nhóm" để mỗi người đếm đúng một lần, giữ được bất biến tổng nhóm con = tổng nhân viên. **FR-014:** bỏ fallback `UserRaw.StaffCode` — Ambassador không có field này. **FR-007:** bổ sung `partnerId` vào chữ ký `CheckUserInSegmentWithStaffCode`. **FR-002:** ghi rõ index không unique, chống trùng ở tầng service là chấp nhận có ý thức. **NFR-002:** chỉ rõ nơi thực thi ràng buộc xoá segment |
| **3.0** | 2026-08-06 | Nguyễn Đăng Định | **Bản chốt.** Phân nhóm chuyển sang **segment tự động port từ T-Fluencers** (`applyType: staff_code`) thay cho cột `group` trong file import — cột `group` là cơ chế tự nghĩ, đã loại bỏ. `manage-codes` trở về đúng cấu trúc T-Fluencers. Bổ sung `SegmentRaw.Type`, `ConditionForAutomatic`, `UserSegmentRaw.Note` (T-Fluencers có, Ambassador chưa). 13 FR → 14 FR. Status: Final |
| 2.0 | 2026-08-06 | Nguyễn Đăng Định | Viết lại theo hướng bám T-Fluencers, bỏ các thay đổi tự đề xuất ở v1.x |
| 1.6 | 2026-08-06 | Nguyễn Đăng Định | Dùng brute-force thay "tấn công vét cạn" |
| 1.5 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ kỹ thuật, bổ sung mục 0 |
| 1.4 | 2026-08-06 | Nguyễn Đăng Định | Chốt 3 câu hỏi treo |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Soát nhất quán sau đợt vá v1.2 |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Vá 12 lỗ hổng phát hiện khi review flow |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Thu hẹp phạm vi về chỉ Parasola |
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | PRD đầu tiên |
