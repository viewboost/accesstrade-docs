# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06
**Author:** Nguyễn Đăng Định
**Version:** 1.5
**Project Level:** Level 2
**Status:** Draft
**Phạm vi:** **Chỉ partner Parasola.** 12 partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD cho tính năng cho phép **nhân viên Parasola** tự xác nhận danh tính nội bộ trên Ambassador bằng mã do Parasola cấp, phục vụ 3 mục tiêu: có nơi nhập mã, có thống kê theo nhóm nhân viên, và có campaign dành riêng cho nhân viên.

Backend và admin xây dựng theo hướng dùng chung cho mọi partner (bật/tắt bằng cờ), nhưng **phase này chỉ bật cho Parasola và chỉ làm frontend cho `parasola/`**.

**Related Documents:**
- Tham chiếu nghiệp vụ: T-Fluencers Handbook — https://handbook.diso.vn/wiki/admin/nhan-vien/03-quan-ly-ma-nhan-vien
- Tham chiếu SRS: https://handbook.diso.vn/srs/admin-portal/14-code
- PRD liên quan (T-Fluencers): `t-fluencers/prd-employee-code-profile.md`, `t-fluencers/dashboard-wiki-and-techcomer/prd.md`
- Dossier phân tích code T-Fluencer: `ambassador/employee-code/tf-reference-employee-code-flow.md`

**Điểm cắm trong repo `AT-Core/ambassador`:**
- `backend/internal/model/mg/user_partner.go` — `UserPartnerRaw`
- `backend/internal/model/mg/segment.go`, `user_segment.go` — hạ tầng phân nhóm đã có
- `backend/internal/model/mg/partner.go` — `PartnerOpts` (feature flag theo tenant)
- `backend/internal/model/mg/event.go` — `ParticipationRequirements`
- `backend/pkg/public/service/eligibility.go` — `CalculateEligibility` / `JoinEvent`
- `backend/pkg/admin/router/user_segment.go` — `POST /user-segments/import-excel` đã có
- `admin/src/pages/user-partner/`, `admin/src/pages/segment/`, `admin/src/pages/event/components/modal.tsx`
- **`parasola/src/components/layout/main/header/index.tsx`** — điểm cắm modal (đã có sẵn pattern, xem FR-008)
- **`parasola/src/models/main.ts`**, **`parasola/src/pages/account/`**

---

## 0. Thuật ngữ

Dùng thống nhất trong cả PRD và tech spec.

| Thuật ngữ | Định nghĩa |
|---|---|
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`, nhận một trong ba giá trị `employee` \| `not_employee` \| `not_verify`. Rỗng = chưa hỏi, phân loại như `not_verify` |
| **Claim mã** | Thao tác chuyển một bản ghi `manage-codes` từ `isUsed: false` sang `true` đồng thời ghi `usedBy`/`usedAt`. Thực hiện bằng một `findOneAndUpdate` để đảm bảo atomic |
| **Giải phóng mã** | Thao tác ngược của claim: đưa `isUsed` về `false` và xoá `usedBy`/`usedAt`, trả mã về trạng thái dùng được |
| **Atomic ở cấp document** | Đảm bảo của MongoDB: một lệnh ghi lên **một** document là bất khả phân. Không mở rộng sang nhiều document — đó là lý do cần transaction |
| **Multi-document transaction** | Cơ chế ACID của MongoDB gói nhiều lệnh ghi trên nhiều collection thành một đơn vị commit/rollback. Yêu cầu replica set. Repo dùng qua helper `WithTransaction` |
| **Partial write** | Trạng thái không nhất quán khi một phần chuỗi ghi thành công còn phần sau thất bại — ví dụ mã đã claim nhưng `statusStaff` chưa ghi |
| **Tấn công vét cạn** (brute-force) | Thử tuần tự hoặc ngẫu nhiên nhiều giá trị mã cho tới khi trúng một mã hợp lệ |
| **Attack vector** | Một đường vào mà kẻ tấn công dùng được. Ở đây: mỗi endpoint nhận mã nhân viên là một attack vector, nên tất cả phải chung một bộ đếm rate limit |
| **Entropy của mã** | Số bit ngẫu nhiên thực sự trong mã. Mã tuần tự có entropy ≈ 0 nên rate limit không đủ bảo vệ |
| **Tenant-level feature toggle** | Cờ bật/tắt tính năng theo từng partner, lưu trong `PartnerOpts`. Khác với ENV vốn có phạm vi toàn service |
| **Segment** | Thực thể phân nhóm người dùng đã có sẵn trong Ambassador (`segments` + `user-segments`). PRD này dùng lại để biểu diễn nhóm nhân viên |
| **Silent failure** | Lỗi xảy ra nhưng không phát sinh cảnh báo, hệ thống vẫn báo thành công — ví dụ import đọc sai cột mà vẫn trả "OK" |
| **Dry-run** | Chạy toàn bộ logic nghiệp vụ và trả kết quả dự kiến, nhưng không thực hiện lệnh ghi nào |
| **Idempotent** | Thực hiện nhiều lần cho cùng kết quả như một lần. Áp dụng cho upsert `user-segments` |
| **Compensating transaction** | Cơ chế bù trừ thủ công: khi bước sau thất bại thì tự tay hoàn tác bước trước. **Đã loại bỏ** khỏi thiết kế vì dùng được multi-document transaction |

---

## 1. Executive Summary

Parasola muốn phân biệt **nhân viên nội bộ** với creator bên ngoài trên Ambassador, để chạy chiến dịch riêng cho nội bộ và báo cáo tách bạch đóng góp của hai nhóm.

Ambassador hiện **chưa có gì** cho việc này: `UserPartnerRaw` không có trường trạng thái nhân viên (có comment xác nhận cố ý bỏ tại `partner_creator_config.go:23`), không có bảng mã nhân viên, không có API xác nhận.

**Giải pháp:** Parasola cấp mã cho nhân viên qua kênh nội bộ → Admin import danh sách mã kèm nhóm vào Ambassador → Nhân viên nhập mã trên web → Hệ thống đối chiếu, ghi trạng thái nhân viên và **tự động đưa vào nhóm tương ứng**. Nhãn và nhóm này dùng cho gate campaign và báo cáo.

**Vì sao vẫn làm backend dùng chung dù chỉ chạy cho Parasola:** chi phí thêm gần như bằng 0 (`PartnerOpts` đã có sẵn pattern), nhưng tránh phải viết lại khi partner thứ hai cần. Phần tốn công là frontend — và phần đó **chỉ làm cho `parasola/`**, không đụng 12 folder còn lại.

**Ba khác biệt có chủ ý so với bản T-Fluencer:**

| | T-Fluencer | Ambassador (Parasola) |
|---|---|---|
| Phân nhóm | Chỉ nhị phân nhân viên/người ngoài | **File import có cột Nhóm → tự gán Segment** |
| Bật/tắt | ENV toàn cục | **Cờ theo từng partner** (`PartnerOpts`), chỉ bật cho Parasola |
| Vòng đời mã | Dùng lại vô hạn (`isUsed` không set) | **1 mã 1 người**, claim mã ngay khi xác nhận |

**Scope:** Không dựng dashboard analytics mới. Thống kê bổ sung vào trang admin đã có (`user-partner`, `segment/detail`) + export. Frontend chỉ làm trong `parasola/`.

---

## 2. Bối cảnh & Vấn đề

### Hiện trạng Ambassador

| Thành phần | Trạng thái |
|---|---|
| `UserPartnerRaw.statusStaff` | ❌ Không có |
| `UserPartnerRaw.code` | ⚠️ **Đã bị chiếm** làm referral code (`migration.go:1109`) |
| Bảng mã nhân viên | ❌ Không có |
| API xác nhận nhân viên | ❌ Không có |
| `Segment` + `UserSegment` + import Excel | ✅ **Đã có đủ** (BE + admin UI) |
| `ParticipationRequirements` + `EligibilityInterface` | ✅ **Đã có**, có `FailReasons` |
| `PartnerOpts` (feature flag theo tenant) | ✅ **Đã có** pattern (`AllowResubmitRejectedContent`) |

### Vấn đề

1. **Không biết ai là nhân viên** — Parasola không đo được mức độ tham gia của nội bộ
2. **Không chạy được chiến dịch nội bộ** — không có cách giới hạn người tham gia
3. **Không phân nhóm được** — Parasola muốn so sánh giữa các nhóm nhân viên, hiện không có dữ liệu nhóm

### Các phương án đã đánh giá

| Phương án | Kết luận |
|---|---|
| **A. Nhập tự do, Ops đối chiếu sau** | ❌ Loại. Nhãn nhân viên mở khoá tiền thưởng — không thể dựa vào khai báo không kiểm chứng |
| **B. Validate bằng regex do partner cấu hình** | ❌ Loại. Chặn được rác nhưng không xác minh được mã có thật; Parasola vẫn phải gửi danh sách để đối soát |
| **C. Import danh sách mã trước + 1 mã 1 người** | ✅ **Chọn.** Kiểm chứng được, chống chia sẻ mã, và là chỗ tự nhiên để đính kèm thông tin nhóm |
| **D. Tích hợp SSO/HR API của Parasola** | ❌ Loại cho phase 1. Chính xác nhất nhưng chi phí tích hợp không khả thi trong 1 phase |
| **E. Hardcode riêng cho Parasola, không dùng cờ** | ❌ Loại. Tiết kiệm không đáng kể, nhưng partner thứ hai sẽ phải viết lại từ đầu |

### Vì sao không copy nguyên T-Fluencer

Bản T-Fluencer đã chạy production nhưng có các lỗ hổng sau (đã kiểm chứng trên code):

| Vấn đề | Hệ quả |
|---|---|
| `isUsed/usedBy/usedAt` không set ở luồng live | 1 mã chia sẻ được cho vô hạn người, tất cả thành "nhân viên" |
| `InputCodeJoinEvent` gán `statusEmployee` không đối chiếu cấp partner | Người đã khai "không phải NV" vẫn vào được campaign nội bộ |
| Không rate limit, `Code` không validate format | Dò mã bằng script khả thi |
| Hai nguồn mã tách rời (`manage-codes` vs `event.options.staffCodes`) | Không đồng bộ, không audit chung |
| Bắt cả người ngoài nhập mã họ không có | Dữ liệu rác trong cột mã |
| Không audit trail | Không truy được khi tranh chấp thưởng |

PRD này giữ phần nghiệp vụ, bỏ các lỗi trên.

---

## 3. User Personas

**P1. Nhân viên Parasola (Creator nội bộ)** — được cấp mã qua email nội bộ hoặc quản lý trực tiếp. Muốn nhập mã nhanh, một lần, không phải hỏi ai.

**P2. Creator bên ngoài trên Parasola** — chiếm đa số người dùng. Không có mã, không quan tâm tính năng này. **Không được để tính năng làm phiền nhóm này.**

**P3. Admin/Ops AccessTrade** — nhận file mã từ Parasola, import vào hệ thống, theo dõi mã đã phát/đã dùng, xử lý khi nhân viên nhập nhầm.

**P4. Marketing Parasola** — cấu hình chiến dịch chỉ dành cho nhân viên hoặc cho nhóm cụ thể, xem báo cáo theo nhóm.

**P5. Người dùng của 12 partner còn lại** — **không được thấy bất kỳ thay đổi nào.** Đây là ràng buộc, không phải mục tiêu.

---

## 4. Functional Requirements

### FR-001: Thêm trạng thái nhân viên vào `UserPartnerRaw`

**Priority:** Must Have

**Description:** Thêm 5 field mới. **Không tái sử dụng** `UserPartnerRaw.Code` vì trường này đã dùng cho referral code.

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/user_partner.go — UserPartnerRaw

// Trạng thái nhân viên
StatusStaff  string    `bson:"statusStaff,omitempty" json:"statusStaff,omitempty"`  // "employee" | "not_employee" | "not_verify"
StaffCode    string    `bson:"staffCode,omitempty" json:"staffCode,omitempty"`      // mã nhân viên đã xác nhận
StaffCodeAt  time.Time `bson:"staffCodeAt,omitempty" json:"staffCodeAt,omitempty"`  // thời điểm xác nhận

// Giới hạn số lần hỏi lại khi user đóng modal (xem FR-008)
StaffPromptDismissedAt  time.Time `bson:"staffPromptDismissedAt,omitempty" json:"-"`
StaffPromptDismissCount int       `bson:"staffPromptDismissCount,omitempty" json:"-"`
```

```go
// backend/internal/constants/staff_code.go — mới
const (
    StatusStaffNotVerify   = "not_verify"
    StatusStaffIsEmployee  = "employee"
    StatusStaffNotEmployee = "not_employee"
)

// IsStaff là quy tắc canonical duy nhất để xác định nhân viên.
// Mọi giá trị mơ hồ (rỗng, not_verify) đều KHÔNG tính là nhân viên,
// để số liệu nhân viên không bao giờ bị sai lệch tăng do dữ liệu không hợp lệ.
func IsStaff(statusStaff string) bool { return statusStaff == StatusStaffIsEmployee }
```

**Acceptance Criteria:**
- [ ] 3 field được thêm, đều `omitempty` — bản ghi cũ không bị ảnh hưởng
- [ ] `constants.IsStaff()` là nơi duy nhất định nghĩa quy tắc; không nơi nào so sánh chuỗi trực tiếp
- [ ] Có mirror `isStaff()` phía FE, kèm comment yêu cầu giữ đồng bộ với Go
- [ ] `UserPartnerRaw.Code` (referral) **không bị đụng tới**

---

### FR-002: Collection `manage-codes` — danh sách mã nhân viên hợp lệ

**Priority:** Must Have

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/manage_code.go — mới
type ManageCodeRaw struct {
    ID        AppID     `bson:"_id"`
    Partner   AppID     `bson:"partner"`
    Type      string    `bson:"type"`               // constants.ManageCodeApplyForEmployee
    Code      string    `bson:"code"`               // đã chuẩn hoá: TRIM + UPPERCASE
    Group     string    `bson:"group,omitempty"`    // tên nhóm/phòng ban/chi nhánh
    Segment   AppID     `bson:"segment,omitempty"`  // segment tương ứng với Group
    IsUsed    bool      `bson:"isUsed"`
    UsedBy    AppID     `bson:"usedBy,omitempty"`
    UsedAt    time.Time `bson:"usedAt,omitempty"`
    CreatedBy AppID     `bson:"createdBy"`
    CreatedAt time.Time `bson:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt"`
}
```

**Index bắt buộc:**
```
{ partner: 1, code: 1 }  unique   — chống trùng mã trong cùng partner
{ partner: 1, isUsed: 1 }         — phục vụ filter danh sách
{ usedBy: 1 }                     — tra ngược từ user
```

**Acceptance Criteria:**
- [ ] Unique index `{partner, code}` — cùng mã ở 2 partner khác nhau là hợp lệ
- [ ] `Code` luôn lưu dạng chuẩn hoá (TRIM + UPPERCASE), chuẩn hoá ở **backend**
- [ ] `Group` optional — partner chưa phân nhóm vẫn dùng được tính năng

---

### FR-003: Admin — CRUD mã nhân viên

**Priority:** Must Have

**Description:** Trang `/manage-code` trong admin, theo đúng pattern các trang hiện có (`index.tsx` + `model.ts` + `type.d.ts` + `components/`).

**API:**
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/manage-codes` | Danh sách, filter: `partner`, `code`, `group`, `isUsed`, `keyword` |
| `POST` | `/manage-codes` | Tạo lẻ `{partner, code, group?}` |
| `DELETE` | `/manage-codes/:id` | Xoá — **từ chối nếu `isUsed = true`** |
| `POST` | `/manage-codes/import-excel` | Import hàng loạt (xem FR-004) |
| `GET` | `/manage-codes/export` | Xuất danh sách ra Excel |

**Bảng hiển thị:** Mã | Partner | Nhóm | Trạng thái | Người dùng | Ngày dùng | Ngày tạo

**Acceptance Criteria:**
- [ ] Mọi thao tác qua kiểm tra quyền partner của admin đang đăng nhập (theo pattern `IsAllowPartner`)
- [ ] Tạo mã trùng trong cùng partner → báo lỗi rõ ràng
- [ ] Xoá mã đã dùng → từ chối kèm thông báo *"Mã đã được sử dụng, không thể xoá"*
- [ ] Filter `isUsed` + `group` hoạt động độc lập và kết hợp được
- [ ] Export ra file Excel đủ 7 cột trên

---

### FR-004: Import mã hàng loạt kèm nhóm

**Priority:** Must Have

**Description:** Điểm khác biệt cốt lõi so với T-Fluencer — file import có **cột Nhóm**, đây là điều kiện tiên quyết duy nhất biến "thống kê theo nhóm nhân viên" thành khả thi.

**Format file:**

| Cột A — `code` (bắt buộc) | Cột B — `group` (tuỳ chọn) |
|---|---|
| `HDB000123` | `Chi nhánh Hà Nội` |
| `HDB000124` | `Chi nhánh Hà Nội` |
| `HDB000125` | `Khối Vận hành` |

**Xử lý:**
1. Đọc header **theo tên cột** (`code`, `group`), không theo vị trí — file sai thứ tự cột vẫn đúng
2. Chuẩn hoá `code`: TRIM + UPPERCASE
3. Với mỗi `group` chưa có: tự tạo `SegmentRaw{Name: group, Partner: partnerId}`; đã có thì tái dùng
4. Gán `ManageCodeRaw.Segment` = ID segment tương ứng
5. Xử lý mã đã tồn tại — **không skip mù quáng**:

   | Trường hợp | Hành động |
   |---|---|
   | `group` giống mã đã có | Skip |
   | `group` khác mã đã có, mã **chưa dùng** | Cập nhật `group` + `segment` của mã |
   | `group` khác mã đã có, mã **đã dùng** | Cập nhật `group` + `segment`, **và đồng bộ lại `user-segments`** của `usedBy`: gỡ segment cũ, thêm segment mới |

6. Insert phần còn lại, gắn `importBatchId` chung cho cả lô

**Vì sao cần bước 5:** nhân viên chuyển bộ phận là kịch bản chắc chắn xảy ra. Nếu chỉ skip như T-Fluencer, người đó vĩnh viễn nằm ở nhóm cũ và không có đường sửa — mã đã dùng thì không xoá được. Thống kê theo nhóm sẽ sai dần theo thời gian.

**Kết quả trả về:**
```json
{
  "importBatchId": "66b2...",
  "total": 500,
  "inserted": 460,
  "groupUpdated": 27,
  "skipped": 11,
  "segmentsCreated": ["Nhóm Miền Bắc", "Nhóm Miền Nam"],
  "errors": [
    { "row": 102, "code": "", "reason": "Mã trống" },
    { "row": 245, "code": "PRS8F2A1C", "reason": "Mã sai format" }
  ]
}
```

**Dry-run:** upload có tuỳ chọn "Xem trước" — chạy toàn bộ logic, trả kết quả như trên nhưng **không ghi DB**. Ops xác nhận rồi mới import thật.

**Xoá theo lô:** `DELETE /manage-codes/batch/:importBatchId` — xoá các mã **chưa dùng** của một lô. Đường lùi khi import nhầm file.

**Acceptance Criteria:**
- [ ] Đọc theo **tên cột**, không theo vị trí
- [ ] File thiếu cột `code` → từ chối toàn bộ, báo lỗi rõ, không import một phần
- [ ] Cột `group` trống → mã vẫn import được, không gán segment
- [ ] Segment mới được tạo đúng partner, không tạo trùng khi nhiều dòng cùng nhóm
- [ ] Đổi `group` của mã **đã dùng** → user tương ứng chuyển segment ngay, thống kê phản ánh đúng
- [ ] Dry-run **không ghi bất kỳ thứ gì** vào DB, kể cả segment mới
- [ ] Xoá theo lô chỉ xoá mã chưa dùng, mã đã dùng giữ nguyên và được báo lại
- [ ] Báo cáo kết quả liệt kê **từng dòng lỗi kèm số dòng** (T-Fluencer chỉ skip không phát sinh cảnh báo)
- [ ] Import 5.000 dòng hoàn thành dưới 30 giây

---

### FR-005: API kiểm tra trạng thái nhân viên

**Priority:** Must Have

```
GET /partners/:id/staff-status        (yêu cầu đăng nhập)
```

**Response:**
```json
{
  "isFeatureEnabled": true,
  "shouldAskStaffStatus": true,
  "statusStaff": "not_verify",
  "canEdit": true
}
```

| Trường | Ý nghĩa |
|---|---|
| `isFeatureEnabled` | Partner có bật tính năng không (FR-010) |
| `shouldAskStaffStatus` | FE có nên hiện modal không |
| `statusStaff` | Trạng thái hiện tại |
| `canEdit` | Còn được sửa không (FR-009) |

**Logic `shouldAskStaffStatus`:**
```
partner chưa bật tính năng             → false
statusStaff ∈ {employee, not_employee} → false
đã bỏ qua ≥ 3 lần                      → false   (xem FR-008)
bỏ qua lần gần nhất chưa quá 7 ngày    → false
còn lại (rỗng / not_verify)            → true
```

**Gộp vào `GET /users/me` thay vì tạo endpoint riêng.** Endpoint riêng bắt **mọi** người dùng — kể cả người đã trả lời từ lâu — tốn thêm một round-trip mỗi lần mở app. `GetMe` (`pkg/public/service/user.go:1770`) đã tải sẵn dữ liệu cần thiết. Thêm khối `staffStatus` vào `GetMeResponse`:

```json
{
  "...": "các trường hiện có",
  "staffStatus": {
    "isFeatureEnabled": true,
    "shouldAskStaffStatus": true,
    "statusStaff": "not_verify",
    "canEdit": true
  }
}
```

Endpoint `GET /partners/:id/staff-status` vẫn giữ, dùng cho trường hợp FE cần đọc lại sau khi xác nhận mà không muốn tải lại toàn bộ `users/me`.

**Acceptance Criteria:**
- [ ] Partner tắt tính năng → luôn `false`, FE không hiện gì
- [ ] Đã chọn rồi → `false`
- [ ] `GET /users/me` **không chậm đi rõ rệt** sau khi thêm khối `staffStatus`
- [ ] Partner chưa bật tính năng → khối `staffStatus` không phát sinh truy vấn thừa

---

### FR-006: API xác nhận nhân viên

**Priority:** Must Have

```
POST /users/confirm-is-staff          (yêu cầu đăng nhập)
Body: { "partner": "<partnerId>", "isStaff": true, "code": "HDB000123" }
```

**Luồng xử lý:**
```
1. Kiểm tra user tồn tại, không bị ban
2. Kiểm tra partner tồn tại + đã bật tính năng
3. Nếu isStaff = false:
     → ghi user-partners (xem quy tắc ghi bên dưới) với statusStaff = "not_employee"
     → KHÔNG ghi staffCode
     → kết thúc
4. Nếu isStaff = true:
     a. Chuẩn hoá code: TRIM + UPPERCASE
     b. code rỗng / sai format → lỗi StaffCodeRequired / StaffCodeInvalid
     c. Nếu partner bật requireCodeValidation:
          Claim mã (atomic, MỘT thao tác): findOneAndUpdate
            filter: {partner, code, type: apply_for_employee, isUsed: false}
            update: {isUsed: true, usedBy: userId, usedAt: now}
          không match → phân biệt 2 lỗi bằng 1 truy vấn đọc:
            mã không tồn tại → StaffCodeInvalid
            mã tồn tại       → StaffCodeAlreadyUsed
     d. ghi user-partners với statusStaff = "employee", staffCode, staffCodeAt
     e. Nếu mã có Segment → upsert user-segments {user, segment}
        [ (c)(d)(e) nằm TRONG MỘT TRANSACTION — xem bên dưới ]
     f. Sau khi commit: ghi audit log bất đồng bộ (FR-016)
```

#### ⚠️ Quy tắc ghi `user-partners` — bắt buộc tuân thủ

Đây là chỗ dễ gây lỗi nghiêm trọng nhất. T-Fluencer tạo bản ghi mới với `IsJoined: true, JoinedAt: time.Now()` gán cứng. **Ambassador tuyệt đối không được làm vậy.**

Trong Ambassador, `isJoined` là điều kiện xác định user thuộc partner nào (`internal/service/user.go:226`):
```go
Find(..., bson.M{"user": userId, "isJoined": true})   // → partnerIds
```
và chỉ được set khi user **thực sự tham gia** (`internal/service/user.go:491`).

Nếu `confirm-is-staff` ghi `isJoined`, thì mọi người chỉ mới bấm **"Tôi không phải nhân viên"** cũng bị tính là đã tham gia Parasola → số liệu partner, danh sách creator, thống kê tham gia đều sai lệch theo chiều **tăng** và rất khó phát hiện.

**Thao tác ghi duy nhất được phép:**
```go
opts := options.Update().SetUpsert(true)
UserPartnerDAO().UpdateOne(ctx, ..., bson.M{"user": userId, "partner": partnerId}, bson.M{
    "$set": bson.M{
        "statusStaff": status,
        "staffCode":   code,       // bỏ qua khi isStaff = false
        "staffCodeAt": time.Now(), // bỏ qua khi isStaff = false
        "updatedAt":   time.Now(),
    },
    "$setOnInsert": bson.M{
        "_id": modelmg.NewAppID(), "user": userId, "partner": partnerId,
        "createdAt": time.Now(),
    },
}, opts)
```

**Cấm tuyệt đối** trong luồng này: `isJoined`, `joinedAt`, `code` (referral), `statistic`, `contentStatistic`.

#### Xử lý lỗi giữa chừng — dùng transaction

Ba bước (c), (d), (e) ghi vào **ba collection khác nhau** (`manage-codes`, `user-partners`, `user-segments`). MongoDB chỉ atomic trong phạm vi một document, nên nếu (c) thành công rồi (d) lỗi thì mã bị chiếm mà không ai sở hữu: nhân viên mất mã, không nhập lại được, Ops nhìn dashboard thấy `isUsed: true` trỏ tới người không có trạng thái `employee`.

**Gói cả ba bước trong một transaction.** Repo đã có sẵn helper `databasemongodb.TransactionDatabase().WithTransaction()` (`internal/module/database/mongodb/transaction.go`), đang dùng thật ở luồng rút tiền (`internal/service/withdraw.go:131`) — hạ tầng Mongo là replica set, không cần xác minh thêm.

```
WithTransaction:
    c. claim mã       manage-codes
    d. ghi trạng thái       user-partners
    e. gán nhóm       user-segments
  → bất kỳ bước nào lỗi ⇒ toàn bộ rollback, mã trở về chưa dùng
```

Nhờ vậy **không cần** cơ chế bù trừ thủ công, cũng **không cần** job đối soát — partial write không thể xảy ra.

Audit log (bước f) ghi **sau khi** transaction commit thành công, bất đồng bộ, để lỗi ghi log không làm hỏng nghiệp vụ.

**Thông báo lỗi:**

| Key | VI | EN |
|---|---|---|
| `staffCodeRequired` | Vui lòng nhập mã nhân viên | Employee code is required |
| `staffCodeInvalid` | Mã nhân viên không hợp lệ | Invalid employee code |
| `staffCodeAlreadyUsed` | Mã này đã được sử dụng bởi tài khoản khác | This code has already been used |
| `staffFeatureDisabled` | Tính năng chưa được bật cho đối tác này | Feature not enabled for this partner |

**Acceptance Criteria:**
- [ ] Claim mã bằng **một thao tác `findOneAndUpdate` atomic** — hai user nhập cùng lúc, chỉ một người thành công
- [ ] **`isJoined` và `joinedAt` không xuất hiện trong bất kỳ câu ghi nào** của luồng này — có test khẳng định điều này
- [ ] User chưa từng tham gia Parasola, bấm "Tôi không phải nhân viên" → **không** bị tính vào danh sách creator của partner
- [ ] `UserPartnerRaw.Code` (referral) không bị thay đổi
- [ ] Nhánh `isStaff = false` **không ghi** `staffCode` (khác T-Fluencer)
- [ ] Mã được chuẩn hoá ở backend — user gõ `prs8f2a1c` hay ` PRS8F2A1C ` đều khớp
- [ ] Xác nhận thành công + mã có nhóm → user xuất hiện trong segment tương ứng ngay
- [ ] Không dùng lại key lỗi của referral code
- [ ] Mô phỏng lỗi ở bước (d) → **transaction rollback**, mã trở về `isUsed: false`, user nhập lại thành công
- [ ] Mô phỏng lỗi ở bước (e) → rollback cả trạng thái lẫn mã, không để lại trạng thái không nhất quán (partial write)

---

### FR-007: Chống tấn công vét cạn (brute-force)

**Priority:** Must Have

**Description:** T-Fluencer không có rate limit và không validate format `Code`; kết hợp với việc mã đúng cho quyền vĩnh viễn, vét cạn bằng script là khả thi. Ambassador phải chặn.

**Yêu cầu:**
| Biện pháp | Ngưỡng |
|---|---|
| Rate limit theo user | 5 lần nhập sai / 10 phút |
| Rate limit theo IP | 20 lần nhập sai / 10 phút |
| Validate format | độ dài 6–32 ký tự, chỉ `A-Z 0-9 - _` |
| Khoá tạm | vượt ngưỡng → khoá 30 phút, thông báo rõ thời gian mở lại |

Quy mô nhân viên Parasola nhỏ, nên ngưỡng này rộng rãi so với nhu cầu thật — nhân viên nhập đúng mã thì không bao giờ chạm tới. Không cần nới thêm cho đợt onboard tập trung.

**Áp cho MỌI đường nhập mã**, đếm chung một khoá theo user — bao gồm:
- `POST /users/confirm-is-staff` (FR-006)
- Đổi trạng thái từ trang Hồ sơ (FR-009)

FR-009 cho phép đổi từ "không phải nhân viên" sang "là nhân viên" không giới hạn số lần; nếu đường đó không dùng chung bộ đếm thì đó là **kênh tấn công (attack vector) thứ hai**.

#### Format mã — theo đúng cách T-Fluencers đang làm

**Đã chốt:** dùng cùng quy ước với T-Fluencers.

```
PRS_<8 ký tự hex ngẫu nhiên viết hoa>

Ví dụ:  PRS_A3F91B2C   PRS_7D0E4A88   PRS_C15B9F30
```

Cách sinh (T-Fluencers Handbook đang hướng dẫn Ops như vậy):
```python
import secrets
codes = [f"PRS_{secrets.token_hex(4).upper()}" for _ in range(N)]
# xuất ra Excel với cột "code" và cột "group"
```

Quy ước này thoả sẵn yêu cầu chống vét cạn: 8 ký tự hex = 4 tỷ tổ hợp, không tuần tự, không suy ra được từ mã nhân sự hay số điện thoại. Prefix `PRS_` chỉ để nhận diện, không làm giảm entropy.

Rate limit một mình không đủ nếu mã đặt tuần tự (`PRS001`, `PRS002`…) — 20 lần/10 phút vẫn vét cạn được vài nghìn mã trong một đêm. Format trên loại bỏ rủi ro đó ngay từ gốc.

**Acceptance Criteria:**
- [ ] Nhập sai quá ngưỡng → bị chặn kèm thông báo *"Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau 30 phút."*
- [ ] Nhập **đúng** không bị tính vào ngưỡng
- [ ] Mã sai format bị từ chối trước khi truy vấn DB
- [ ] Nhập sai 3 lần ở modal + 3 lần ở trang Hồ sơ → **bị chặn**, chứng minh dùng chung bộ đếm
- [ ] Mỗi lần nhập sai đều ghi log (FR-016)

---

### FR-008: Modal xác nhận trên Frontend Parasola

**Priority:** Must Have

**Description:** Hiện sau khi đăng nhập, khi `shouldAskStaffStatus = true`. **Chỉ làm trong `parasola/`.**

**Điểm cắm — đã có sẵn pattern trong Parasola:**

`parasola/src/components/layout/main/header/index.tsx` hiện đã làm đúng việc này cho màn đồng ý điều khoản:

```
initApp gọi users/me
  → user state update
  → useEffect [user] kiểm tra user.privacyAccepted === false
  → bung ModalCompleteRegistration
```

Modal mã nhân viên đi theo **đúng cơ chế đó**, đặt cạnh trong cùng file, dùng chung component `AppModal`. Không phát minh cơ chế mới.

Thứ tự ưu tiên khi cả hai cùng thoả điều kiện: **modal điều khoản trước, modal nhân viên sau** — không hiện chồng.

**Khác biệt có chủ ý với T-Fluencer:**

| | T-Fluencer | Parasola |
|---|---|---|
| Đóng modal | ❌ Không đóng được | ✅ **Đóng được** (X / ESC / click ngoài) |
| Người ngoài nhập mã | ❌ Bắt buộc | ✅ **Không cần** — 1 click là xong |
| Sửa lại sau | ❌ Không | ✅ Có (FR-009) |

Lý do: Parasola phần lớn là creator bên ngoài (P2). Chặn cứng toàn bộ người dùng để thu dữ liệu của một nhóm nhỏ là đánh đổi sai. Lưu ý đây là điểm **khác** với `ModalCompleteRegistration` (`closeButton={false}`) — điều khoản là bắt buộc pháp lý, khai báo nhân viên thì không.

**Bố cục:**
```
┌────────────────────────────────────────────┐
│  Bạn có phải nhân viên {Tên đối tác}?   ✕ │
├────────────────────────────────────────────┤
│  Đối tác có những chiến dịch dành riêng    │
│  cho nhân viên nội bộ.                     │
│                                            │
│  ┌──────────────────┐ ┌──────────────────┐ │
│  │ Tôi là nhân viên │ │ Tôi không phải   │ │
│  └──────────────────┘ └──────────────────┘ │
│                                            │
│  [ chỉ hiện khi chọn "Tôi là nhân viên" ]  │
│  Mã nhân viên                              │
│  ┌────────────────────────────────────┐    │
│  │ Nhập mã được cấp                   │    │
│  └────────────────────────────────────┘    │
│                                            │
│              [ Xác nhận ]                  │
└────────────────────────────────────────────┘
```

**Hành vi:**
- Chọn "Tôi không phải" → gọi API ngay, đóng modal, không hỏi lại
- Chọn "Tôi là nhân viên" → hiện ô mã; nút Xác nhận khoá cho tới khi có mã
- Ô mã **tự viết hoa khi gõ**, và giá trị gửi lên đúng bằng giá trị hiển thị
- Lỗi từ backend hiện ngay dưới ô mã, không đóng modal

**Đóng modal mà không chọn — có giới hạn:**

Bỏ modal blocking (không dismiss được) của T-Fluencer là đúng, nhưng "lần sau hỏi lại" mà không giới hạn thì với creator ngoài không bao giờ bấm gì sẽ thành **hỏi mãi mãi** — khó chịu không kém blocking, chỉ là chia nhỏ ra.

```
Đóng modal → ghi user-partners.staffPromptDismissedAt + tăng staffPromptDismissCount
Hỏi lại khi: đã qua 7 ngày kể từ lần đóng gần nhất
Ngừng hỏi khi: staffPromptDismissCount >= 3
```

Sau khi ngừng hỏi, user vẫn khai được bất cứ lúc nào qua trang Hồ sơ (FR-009).

Hai field `staffPromptDismissedAt` / `staffPromptDismissCount` khai trong FR-001.

**Phạm vi triển khai:**

| Folder | Làm gì |
|---|---|
| `parasola/` | ✅ Toàn bộ FR-008, FR-009, FR-012 |
| `frontend/` và 12 folder partner còn lại | ❌ **Không đụng tới** |

**Acceptance Criteria:**
- [ ] Người ngoài hoàn tất bằng **đúng 1 click**
- [ ] Modal đóng được bằng cả X, ESC và click ra ngoài
- [ ] Nhánh "không phải nhân viên" **không hiện** ô nhập mã
- [ ] Giá trị hiển thị và giá trị gửi lên luôn khớp nhau
- [ ] Partner tắt tính năng → modal không bao giờ xuất hiện
- [ ] Không hiện chồng với `ModalCompleteRegistration`
- [ ] Đóng modal 3 lần → **không hỏi lại nữa**, nhưng vẫn khai được từ trang Hồ sơ
- [ ] Đóng modal lần 1 → không hỏi lại trong vòng 7 ngày
- [ ] Hoạt động đúng trên mobile
- [ ] **12 folder partner còn lại không có thay đổi nào trong diff**

---

### FR-009: Sửa lại trạng thái nhân viên

**Priority:** Should Have

**Description:** T-Fluencer không cho sửa, dẫn tới mọi trường hợp nhập nhầm đều phải nhờ Ops sửa DB tay. Ambassador cần đường chính thức.

**Phía người dùng** — mục "Thông tin nhân viên" trong `parasola/src/pages/account/`:
- Đang là "không phải nhân viên" → được đổi sang "là nhân viên" + nhập mã, **không giới hạn**
- Đang là "nhân viên" → **không tự đổi được**, hiện hướng dẫn liên hệ hỗ trợ (tránh hành vi claim rồi giải phóng mã để thao túng)

**Phía Admin** — nút "Sửa trạng thái nhân viên" trong `admin/src/pages/user-partner/`:
- Đổi được sang bất kỳ trạng thái nào
- Thu hồi trạng thái nhân viên → **giải phóng mã** (`isUsed = false`, xoá `usedBy`/`usedAt`) và gỡ khỏi segment
- Bắt buộc nhập lý do, ghi vào audit log

**Acceptance Criteria:**
- [ ] User tự chuyển từ "không phải" sang "là nhân viên" được
- [ ] User **không** tự thu hồi được trạng thái nhân viên
- [ ] Admin thu hồi trạng thái → mã quay về trạng thái chưa dùng, dùng lại được
- [ ] Mọi thao tác sửa đều có lý do và được ghi log

---

### FR-010: Bật/tắt theo từng partner

**Priority:** Must Have

**Description:** T-Fluencer dùng ENV toàn cục — với 13 partner của Ambassador thì bật cho một partner là bật cho tất cả. Dùng `PartnerOpts` đã có sẵn.

**Phase này chỉ bật cho Parasola.** Cờ là cơ chế bảo vệ 12 partner còn lại, đồng thời là đường mở rộng khi có partner thứ hai — không phải tính năng thừa.

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/partner.go — PartnerOpts
// EnableStaffCode bật luồng nhập mã nhân viên cho partner này.
EnableStaffCode bool `bson:"enableStaffCode,omitempty" json:"enableStaffCode"`
// RequireStaffCodeValidation bắt buộc mã phải có trong manage-codes.
// Tắt = chấp nhận mọi mã đúng format (dùng khi partner chưa kịp gửi danh sách).
RequireStaffCodeValidation bool `bson:"requireStaffCodeValidation,omitempty" json:"requireStaffCodeValidation"`
```

**UI:** 2 toggle trong section "Cấu hình nhân viên" của `admin/src/pages/partner/components/modal.tsx`. Toggle thứ hai bị vô hiệu khi toggle thứ nhất tắt.

**Acceptance Criteria:**
- [ ] Mặc định cả 2 = `false` — 13 partner hiện tại không thay đổi hành vi
- [ ] **Chỉ Parasola được bật khi release**; 12 partner còn lại giữ `false`
- [ ] Bật cho Parasola không ảnh hưởng bất kỳ partner nào khác
- [ ] Tắt `EnableStaffCode` → modal biến mất, API xác nhận từ chối, dữ liệu đã có **giữ nguyên** không bị xoá

---

### FR-011: Chiến dịch dành riêng cho nhân viên

**Priority:** Must Have

**Description:** Cắm vào `ParticipationRequirements` + `EligibilityInterface` đã có, **không** tạo nhánh kiểm tra riêng như T-Fluencer nhét inline vào `content.go`.

**Thay đổi cụ thể:**
```go
// backend/internal/model/mg/event.go — ParticipationRequirements
StaffRequired   bool    `bson:"staffRequired,omitempty" json:"staffRequired"`
AllowedSegments []AppID `bson:"allowedSegments,omitempty" json:"allowedSegments,omitempty"`
```

```go
// backend/pkg/public/service/eligibility.go — EligibilityChecks
IsStaff        bool `json:"isStaff"`
InAllowedGroup bool `json:"inAllowedGroup"`
```

**Quy tắc:**
- `StaffRequired = true` và `statusStaff != "employee"` → không đủ điều kiện, `FailReasons` chứa `staffRequired`
- `AllowedSegments` không rỗng và user không thuộc segment nào trong đó → không đủ điều kiện, `FailReasons` chứa `notInAllowedGroup`
- Hai điều kiện là **AND** — bật cả hai thì phải thoả cả hai

**Hệ quả cần lưu ý:** nhân viên có mã **không kèm `group`** sẽ không thuộc segment nào, nên bị chặn khỏi chiến dịch giới hạn nhóm dù đúng là nhân viên. Đây là hành vi đúng theo thiết kế, nhưng dễ gây bất ngờ cho Ops.

→ Admin UI phải **cảnh báo ngay khi chọn segment** nếu partner còn mã chưa gán nhóm:
> ⚠️ Partner này còn 34 mã nhân viên chưa gán nhóm. Những nhân viên dùng các mã đó sẽ không tham gia được chiến dịch này.

**Admin UI** (`admin/src/pages/event/components/modal.tsx`, trong section điều kiện tham gia đã có):
- Switch "Chỉ dành cho nhân viên"
- Select nhiều "Giới hạn theo nhóm" — chỉ liệt kê segment của partner đang chọn

**KHÔNG làm:** không port `EventOpts.StaffCodes` của T-Fluencer. Đó là nguồn mã thứ hai, tách rời `manage-codes`, và là gốc của lỗi bypass mô tả ở mục 2.

**Acceptance Criteria:**
- [ ] Điều kiện mới đi qua đúng `CalculateEligibility`, không thêm nhánh kiểm tra song song
- [ ] `FailReasons` trả về lý do đọc được, FE hiển thị đúng
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] Chỉ chọn được segment thuộc partner của event

---

### FR-012: Thông báo khi không đủ điều kiện

**Priority:** Must Have

**Description:** Người không đủ điều kiện phải hiểu vì sao và biết đi đâu tiếp, thay vì gặp lỗi cụt.

**Nội dung:**

| Trường hợp | Tiêu đề | Nội dung | Hành động |
|---|---|---|---|
| Chưa xác nhận nhân viên | Chiến dịch dành riêng cho nhân viên | Bạn cần xác nhận là nhân viên {Partner} để tham gia | **Nhập mã ngay** / Để sau |
| Đã xác nhận không phải NV | Chiến dịch dành riêng cho nhân viên | Đừng lo, còn nhiều chiến dịch khác đang chờ bạn | **Khám phá thêm** / Đã hiểu |
| Không thuộc nhóm được phép | Chiến dịch dành riêng cho nhóm khác | Chiến dịch này chỉ dành cho: {tên các nhóm} | **Khám phá thêm** / Đã hiểu |

**Acceptance Criteria:**
- [ ] Modal đóng được ở cả 3 trường hợp
- [ ] Trường hợp 1 mở thẳng được modal nhập mã (FR-008)
- [ ] Đủ cả tiếng Việt và tiếng Anh

---

### FR-013: Admin — hiển thị và lọc theo nhân viên/nhóm

**Priority:** Must Have

**Description:** Bổ sung vào `admin/src/pages/user-partner/` đã có.

**Cột mới:** `Nhân viên` (Có/Không) | `Mã nhân viên` | `Nhóm`

**Filter mới:** `statusStaff` (Tất cả / Nhân viên / Không phải / Chưa xác nhận), `segment` (chọn nhiều)

**Acceptance Criteria:**
- [ ] Ba cột hiển thị đúng, giá trị rỗng hiện `—`
- [ ] Filter hoạt động độc lập và kết hợp được với filter sẵn có
- [ ] Nhãn "Nhân viên" dùng chung một component với nơi khác, không tự vẽ lại

---

### FR-014: Thống kê theo nhóm nhân viên

**Priority:** Must Have

**Description:** Yêu cầu gốc *"Có thống kê kết quả theo nhóm nhân viên"*. **T-Fluencer không có phần này** (chỉ tách nhị phân nhân viên/người ngoài) nên phải thiết kế mới.

**Vị trí:** tab "Thống kê" mới trong `admin/src/pages/event-statistic/`, và tab overview của `admin/src/pages/segment/detail/`.

**Bảng thống kê:**

| Nhóm | Số người | Đã tham gia | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|
| **Tổng — Nhân viên** | 210 | 168 | 1.180 | 3.1tr | 190tr |
| ├ Chi nhánh Hà Nội | 85 | 72 | 520 | 1.4tr | 82tr |
| ├ Chi nhánh HCM | 78 | 61 | 410 | 1.1tr | 68tr |
| └ Khối Vận hành | 47 | 35 | 250 | 0.6tr | 40tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9.3tr | 650tr |

**Bộ lọc:** khoảng thời gian, chiến dịch, nhóm (chọn nhiều)

**Quy tắc tính:**
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên (không cộng dồn từng loại, tránh sai lệch do dữ liệu không hợp lệ)
- Số liệu bài/xem/chi phí **không tính bài đã bị huỷ**
- Nhân viên chưa được gán nhóm gom vào dòng "Chưa phân nhóm"

#### Phân loại theo trạng thái hiện tại, không snapshot

Số liệu tính theo `statusStaff` **tại thời điểm xem báo cáo**, không phải trạng thái tại thời điểm đăng bài. Hệ quả trực tiếp:

> Nhân viên A đăng 50 bài trong tháng 7 khi chưa xác nhận → 50 bài nằm ở cột "Ngoài".
> Tháng 8, A nhập mã → **50 bài tháng 7 chuyển sang cột "Nhân viên"**.
> Báo cáo tháng 7 in hôm nay khác báo cáo tháng 7 in tuần trước.

Hai phương án đã cân nhắc:

| | Cách làm | Đánh giá |
|---|---|---|
| **A** | Tính theo trạng thái hiện tại | ✅ **Chọn.** Không thêm field, không cần xử lý dữ liệu cũ. Đúng tinh thần "phân loại người, không phân loại bài" |
| **B** | Snapshot `isStaffAtSubmit` vào content khi đăng | Số liệu bất biến, nhưng thêm field vào content, và **không xử lý được dữ liệu đã có** trước khi tính năng ra đời |

**Chọn phương án A**, kèm ràng buộc bắt buộc: mọi bảng thống kê và mọi file export **phải in ghi chú**:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo. Số liệu kỳ cũ có thể thay đổi khi có nhân viên xác nhận muộn.*

T-Fluencer cũng có đặc tính này nhưng không ghi ra ở đâu, dẫn tới việc Ops đối soát không hiểu vì sao số lệch.

**Acceptance Criteria:**
- [ ] Tổng các nhóm con = dòng tổng "Nhân viên"
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] Số liệu khớp với trang danh sách khi lọc cùng điều kiện
- [ ] Có ghi chú rõ "không bao gồm bài đã huỷ" ngay trên bảng
- [ ] **Có ghi chú về phân loại theo trạng thái hiện tại** trên cả bảng và file export
- [ ] Tải xong dưới 3 giây với 10.000 user

---

### FR-015: Xuất dữ liệu

**Priority:** Should Have

**Description:** Bổ sung 3 cột `Nhân viên` | `Mã nhân viên` | `Nhóm` vào các file export hồ sơ/creator hiện có; thêm nút export cho bảng thống kê FR-014.

**Acceptance Criteria:**
- [ ] Cả Excel và CSV đều có 3 cột mới
- [ ] Cột "Nhân viên" xuất "Có"/"Không", không xuất mã kỹ thuật
- [ ] Export thống kê giữ nguyên cấu trúc nhóm và dòng tổng

---

### FR-016: Audit log

**Priority:** Must Have

**Description:** T-Fluencer không có phần này — khi tranh chấp thưởng thì không truy được. Ambassador dùng `internal/model/mg/audit.go` đã có.

**Sự kiện cần ghi:**

| Sự kiện | Dữ liệu |
|---|---|
| Xác nhận trạng thái nhân viên | user, partner, trạng thái cũ → mới, mã, thời điểm, IP |
| Nhập mã sai | user, partner, mã đã thử, thời điểm, IP |
| Admin sửa trạng thái | admin, user, trạng thái cũ → mới, lý do, thời điểm |
| Import mã | admin, partner, số dòng, số thành công/lỗi, tên file |
| Xoá mã | admin, mã, thời điểm |

**Acceptance Criteria:**
- [ ] Đủ 5 loại sự kiện
- [ ] Tra được lịch sử theo user và theo mã
- [ ] Ghi log không làm chậm luồng chính (bất đồng bộ)

---

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility

- Mọi field mới đều `omitempty`; bản ghi cũ không cần migration
- `EnableStaffCode` mặc định `false` — 13 partner hiện tại không đổi hành vi
- Event chưa bật `StaffRequired`/`AllowedSegments` → `CalculateEligibility` trả kết quả như cũ
- **Không đụng** `UserPartnerRaw.Code` (referral code)

### NFR-002: Security

- Claim mã bằng thao tác atomic — không có kẽ hở race condition
- Rate limit theo cả user và IP (FR-007)
- Mã nhân viên không xuất hiện trong log lỗi hay response cho user khác
- Admin chỉ thao tác được trên mã của partner mình quản lý
- Thông báo lỗi không tiết lộ mã có tồn tại hay không ngoài mức cần thiết

### NFR-003: Data Integrity

- Mỗi mã tối đa một người dùng (`isUsed` + unique index)
- Một user một trạng thái trên mỗi partner
- **Luồng `confirm-is-staff` không bao giờ ghi `isJoined`/`joinedAt`/`code`** (xem FR-006)
- Xoá segment bị từ chối khi còn được tham chiếu bởi **một trong hai**:
  - `manage-codes.segment`
  - `events.participationRequirements.allowedSegments` — bỏ sót chỗ này thì event thành gate rỗng, âm thầm cho tất cả vào hoặc chặn tất cả
- Xác nhận thất bại giữa chừng → transaction rollback toàn bộ; không thể tồn tại mã bị chiếm mà không có chủ

### NFR-004: Performance

- Khối `staffStatus` trong `GET /users/me` không làm `users/me` chậm đi rõ rệt; partner chưa bật tính năng thì không phát sinh truy vấn nào
- Import 1.000 mã < 10 giây (cả dry-run lẫn import thật)
- Thống kê FR-014 < 3 giây

Quy mô nhân viên Parasola nhỏ nên các mốc này rất dư. Mục tiêu hiệu năng ở đây chỉ để chặn thiết kế sai kiểu N+1 query, không phải bài toán tải thật. **Không tối ưu sớm** — chỉ thêm cache khi đo thấy vượt ngưỡng.

### NFR-005: i18n

- Toàn bộ chuỗi mới có cả tiếng Việt và tiếng Anh
- Tên nhóm lấy nguyên từ file import, không dịch

---

## 6. Epics

### EPIC-001: Nền tảng dữ liệu và mã
FR-001, FR-002, FR-010, FR-016 — model, constants, collection, index, feature flag, audit.

### EPIC-002: Quản lý mã phía Admin
FR-003, FR-004 — trang `/manage-code`, CRUD, import kèm nhóm, export.

### EPIC-003: Luồng xác nhận của người dùng
FR-005, FR-006, FR-007, FR-008, FR-009 — API, chống vét cạn, modal, sửa lại.

### EPIC-004: Chiến dịch cho nhân viên
FR-011, FR-012 — điều kiện tham gia, admin UI, thông báo từ chối.

### EPIC-005: Báo cáo
FR-013, FR-014, FR-015 — cột, filter, bảng thống kê theo nhóm, export.

---

## 7. Kiến trúc kỹ thuật

### Luồng dữ liệu

```
Parasola phát mã cho nhân viên (email nội bộ / quản lý trực tiếp)
        │
        ▼
Admin import Excel (Mã | Nhóm)
        │
        ├──► manage-codes   {partner, code, group, segment, isUsed}
        └──► segments       tự tạo theo cột Nhóm
        │
        ▼
Nhân viên nhập mã trên web
        │
   POST /users/confirm-is-staff
        │
        ├──► claim mã (atomic ở cấp document)     manage-codes {isUsed, usedBy, usedAt}
        ├──► ghi trạng thái              user-partners {statusStaff, staffCode, staffCodeAt}
        ├──► gán nhóm              user-segments {user, segment}
        └──► ghi log               audit
        │
        ▼
   ┌────┴─────────────────────┬──────────────────────┐
   ▼                          ▼                      ▼
Gate chiến dịch          Thống kê              Hiển thị/Export
CalculateEligibility     theo nhóm             admin user-partner
```

### Luồng xác nhận

```
Đăng nhập xong
  → GET /users/me  (khối staffStatus đi kèm, không thêm round-trip)
  → shouldAskStaffStatus = false → kết thúc
  → shouldAskStaffStatus = true  → hiện modal
       ├─ "Tôi không phải"  → POST confirm-is-staff {isStaff:false} → xong, không hỏi lại
       ├─ "Tôi là nhân viên" + mã → POST confirm-is-staff {isStaff:true, code}
       │      ├─ thành công → claim mã + ghi trạng thái + vào nhóm + đóng modal
       │      ├─ lỗi ở bước ghi trạng thái/gán nhóm → GIẢI PHÓNG MÃ, báo lỗi
       │      └─ mã sai     → hiện lỗi dưới ô mã, giữ modal, tăng bộ đếm rate limit
       └─ đóng modal        → ghi staffPromptDismissedAt + tăng dismissCount
                              hỏi lại sau 7 ngày, tối đa 3 lần rồi thôi
```

### Luồng gate chiến dịch

```
User mở chi tiết chiến dịch
  → CalculateEligibility(user, event)
      ├─ StaffRequired && !IsStaff(statusStaff)      → FailReasons += staffRequired
      ├─ AllowedSegments != ∅ && user ∉ AllowedSegments → FailReasons += notInAllowedGroup
      └─ (các điều kiện email/phone/facebook sẵn có)
  → eligible = false → hiện thông báo FR-012
```

---

## 8. Implementation Scope

### Thay đổi cần làm

| Vùng | File | Nội dung |
|---|---|---|
| **Model** | `backend/internal/model/mg/user_partner.go` | +5 field |
| **Model** | `backend/internal/model/mg/manage_code.go` | File mới |
| **Model** | `backend/internal/model/mg/partner.go` | +2 field trong `PartnerOpts` |
| **Model** | `backend/internal/model/mg/event.go` | +2 field trong `ParticipationRequirements` |
| **Constants** | `backend/internal/constants/staff_code.go` | File mới — trạng thái + `IsStaff()` + chuẩn hoá/validate mã |
| **DAO** | `backend/internal/module/database/mongodb/` | `ManageCodeDAO` + collection + index (cần helper unique index) |
| **Public API** | `backend/pkg/public/service/user.go` | `GetMe` +khối `staffStatus`; `ConfirmIsStaff` |
| **Public API** | `backend/pkg/public/{router,handler,service}/partner.go` | `staff-status` (đường phụ) |
| **Middleware** | `backend/internal/echo/middleware/staff_code_rate_limit.go` | File mới — chống vét cạn (FR-007) |
| **Eligibility** | `backend/pkg/public/service/eligibility.go` | +2 điều kiện |
| **Admin API** | `backend/pkg/admin/{router,handler,service}/manage_code.go` | File mới — CRUD + import (dry-run) + xoá theo lô + export |
| **Admin API** | `backend/pkg/admin/service/user_partner.go` | Trả thêm field + filter + sửa trạng thái |
| **Export** | `backend/pkg/admin/service/export_*.go` | +3 cột |
| **Thống kê** | `backend/internal/module/database/mongodb/aggregate_pipeline/` | Pipeline breakdown theo nhóm |
| **Audit** | `backend/internal/model/mg/audit.go` + service | 4 loại sự kiện (FR-016) |
| **Locale** | `backend/internal/locale/staff_code.go` + `properties/{vi,en}/` | Key lỗi mới, **không** tái dùng key referral |
| **Admin UI** | `admin/src/pages/manage-code/` | Trang mới |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | +2 toggle |
| **Admin UI** | `admin/src/pages/event/components/modal.tsx` | +1 switch, +1 select nhóm |
| **Admin UI** | `admin/src/pages/user-partner/` | +3 cột, +2 filter, nút sửa trạng thái |
| **Admin UI** | `admin/src/pages/event-statistic/` | Tab thống kê theo nhóm |
| **Frontend** | `parasola/src/components/layout/main/header/index.tsx` | Trigger modal, cạnh logic `privacyAccepted` đã có |
| **Frontend** | `parasola/src/components/layout/main/header/components/modal-staff-code.tsx` | Component mới |
| **Frontend** | `parasola/src/models/main.ts` | State + effect `confirmIsStaff` / `dismissStaffPrompt` / `getStaffStatus` |
| **Frontend** | `parasola/src/configs/api.ts` | 2 endpoint mới |
| **Frontend** | `parasola/src/utils/staff.ts` | Mirror của `constants.IsStaff`, giữ đồng bộ với Go |
| **Frontend** | `parasola/src/pages/account/` | Mục "Thông tin nhân viên" (FR-009) |
| **Frontend** | `parasola/src/pages/content/` hoặc trang chi tiết chiến dịch | Thông báo từ chối (FR-012) |

### KHÔNG làm

- **Không đụng `frontend/` và 12 folder partner còn lại** (`anker`, `flamingo`, `hdbank`, `lusso`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `vpbank`, `wildrift`, `yody`)
- Không bật cờ cho partner nào ngoài Parasola
- Không port `EventOpts.StaffCodes` — nguồn mã thứ hai, gốc lỗi bypass ở T-Fluencer
- Không dùng lại `UserPartnerRaw.Code` (đang là referral code)
- Không dùng ENV toàn cục
- Không dựng dashboard analytics riêng như T-Fluencer — bổ sung vào trang admin đã có
- Không đụng logic tính thưởng, xếp hạng, duyệt nội dung
- Không tích hợp SSO/HR API của Parasola
- Không tự sinh mã — Parasola cấp, Admin import

---

## 9. Assumptions

1. Parasola chịu trách nhiệm phát mã cho nhân viên qua kênh nội bộ; Ambassador không gửi mã
2. Parasola cung cấp được file danh sách mã, và cột nhóm (nếu muốn thống kê theo nhóm)
3. Một nhân viên chỉ dùng một mã cho một partner
4. Tên nhóm trong file import là duy nhất trong phạm vi một partner
5. Trạng thái nhân viên gắn theo partner, không phải toàn hệ thống — cùng một người có thể là nhân viên Parasola nhưng là creator ngoài với partner khác
6. Ambassador đã có hạ tầng audit log dùng được (`internal/model/mg/audit.go`)
7. `parasola/` tiếp tục dùng cấu trúc Umi + dva như hiện tại; modal mới bám theo pattern `ModalCompleteRegistration` sẵn có

---

## 10. Out of Scope

- **Triển khai cho 12 partner còn lại** — backend/admin đã sẵn sàng, chỉ cần bật cờ + làm frontend cho folder tương ứng, nhưng không thuộc phase này
- Tích hợp SSO hoặc HR API của Parasola (cân nhắc phase sau)
- Tự sinh mã hàng loạt trong hệ thống
- Hạn dùng cho mã (`expiredAt`)
- Thu hồi mã hàng loạt (bulk revoke)
- Gửi mã cho nhân viên qua email/SMS từ Ambassador
- Phân cấp nhóm nhiều tầng (khối → phòng → tổ) — phase 1 chỉ một tầng
- Nhập mã theo từng chiến dịch riêng lẻ
- Chính sách thưởng khác nhau giữa nhân viên và người ngoài
- Xếp hạng riêng cho nhân viên
- **Snapshot trạng thái nhân viên theo từng bài đăng** (phương án B ở FR-014) — số liệu kỳ cũ có thể đổi, đã ghi chú rõ trên báo cáo
- **Phân quyền xem thống kê theo nhóm** — phase 1 admin partner thấy toàn bộ nhóm; chưa hỗ trợ trưởng nhóm chỉ xem nhóm mình

---

## 11. Traceability Matrix

| Yêu cầu gốc | FR đáp ứng |
|---|---|
| Có nơi để nhân viên nhập mã | FR-005, FR-006, FR-008, FR-009 |
| Có thống kê kết quả theo nhóm nhân viên | FR-004, FR-013, FR-014, FR-015 |
| Có campaign dành riêng cho nhân viên | FR-011, FR-012 |
| Import nhân viên để về sau còn phân loại | FR-002, FR-003, FR-004 |

### Prioritization Summary

| Priority | FR |
|---|---|
| **Must Have** (14) | FR-001, 002, 003, 004, 005, 006, 007, 008, 010, 011, 012, 013, 014, 016 |
| **Should Have** (2) | FR-009, FR-015 |

Tổng 16 FR.

---

## 12. Resolved Questions

1. **Modal blocking (không dismiss được) như T-Fluencer?** → **Không.** Ambassador phần lớn là creator bên ngoài; modal đóng được, người ngoài xong trong 1 click. Bù lại có đường sửa (FR-009) nên không cần ép chọn một lần vĩnh viễn.

2. **Người không phải nhân viên có phải nhập mã?** → **Không.** Đây là lỗi thiết kế form của T-Fluencer, sinh dữ liệu rác.

3. **Một mã dùng được mấy người?** → **Một.** Claim mã atomic ngay khi xác nhận. T-Fluencer bỏ sót bước này nên mã chia sẻ được vô hạn.

4. **Bật/tắt bằng gì?** → **`PartnerOpts` theo từng partner**, không dùng ENV. Ambassador có 13 partner.

5. **Nhóm nhân viên lấy từ đâu?** → **Cột `group` trong file import mã**, tự tạo và gán `Segment`. Tái dùng hạ tầng `Segment`/`UserSegment` đã có.

6. **Có port `EventOpts.StaffCodes` không?** → **Không.** Nguồn mã thứ hai tách rời, gốc của lỗi bypass. Dùng `ParticipationRequirements` + `EligibilityInterface` đã có.

7. **Đặt tên trường mã là gì?** → **`staffCode`**, vì `UserPartnerRaw.Code` đã là referral code.

8. **Partner nào làm trước?** → **Parasola, và chỉ Parasola.** Backend + admin xây dùng chung (chi phí thêm gần bằng 0 vì `PartnerOpts` đã có sẵn), frontend chỉ làm `parasola/`.

9. **Modal cắm vào đâu trên Parasola?** → `header/index.tsx`, cạnh logic `privacyAccepted` đã có. Tái dùng cơ chế và component `AppModal` sẵn có, không phát minh mới.

10. **Xử lý mã trùng khi import lại?** → **Không skip mù quáng.** `group` khác thì cập nhật, và nếu mã đã dùng thì đồng bộ lại `user-segments`. Skip như T-Fluencer khiến nhân viên chuyển bộ phận vĩnh viễn kẹt ở nhóm cũ.

11. **Thống kê có snapshot theo thời điểm đăng bài không?** → **Không** (phương án A). Tính theo trạng thái hiện tại, đổi lại phải in ghi chú trên mọi bảng và export. Snapshot cần thêm field vào content và vẫn không xử lý được dữ liệu cũ.

12. **Đảm bảo nhất quán giữa `manage-codes`, `user-partners` và `user-segments` bằng gì?** → **Mongo transaction.** Repo đã có helper `WithTransaction` (`internal/module/database/mongodb/transaction.go`) chạy thật ở luồng rút tiền (`internal/service/withdraw.go:131`), nên hạ tầng là replica set. Bỏ được cơ chế bù trừ thủ công và job đối soát bản ghi mã không nhất quán.

13. **Người dùng đóng modal thì hỏi lại bao nhiêu lần?** → Cách nhau 7 ngày, tối đa 3 lần rồi thôi. Bỏ blocking mà hỏi vô hạn thì cũng phiền tương đương.

14. **Format mã của Parasola?** → **Theo đúng quy ước T-Fluencers**: `PRS_<8 hex ngẫu nhiên viết hoa>`, ví dụ `PRS_A3F91B2C`. Thoả sẵn yêu cầu chống vét cạn, không cần quy ước riêng.

15. **Quy mô nhân viên Parasola?** → **Nhỏ.** Ngưỡng rate limit và mục tiêu hiệu năng hiện tại đã rất dư; không tối ưu sớm, chỉ thêm cache nếu đo thấy vượt.

---

## 13. Open Questions

1. **Parasola đã có sẵn dữ liệu nhóm theo mã chưa, và chia nhóm theo tiêu chí gì?** (phòng ban / khu vực / cửa hàng…) — **câu duy nhất còn có thể làm đổi phạm vi.** Nếu Parasola không cung cấp được cột nhóm, FR-014 chỉ chạy được ở mức nhị phân nhân viên/người ngoài, tức là một trong ba mục tiêu gốc không đạt. Cần hỏi trước khi Parasola phát mã, vì cột nhóm phải có ngay từ file import đầu tiên.
2. **Xử lý nhân viên nghỉ việc?** Chưa có cơ chế thu hồi trạng thái hàng loạt — tạm thời Ops gỡ tay qua FR-009. Với quy mô nhân viên nhỏ thì chấp nhận được.

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-06 | Nguyễn Đăng Định | PRD đầu tiên. Tham chiếu T-Fluencer, sửa 6 lỗi của bản đó, bổ sung phân nhóm nhân viên (T-Fluencer chưa có) |
| 1.1 | 2026-08-06 | Nguyễn Đăng Định | Thu hẹp phạm vi về **chỉ Parasola**. Frontend chỉ làm `parasola/`, cắm theo pattern `ModalCompleteRegistration` sẵn có. Thêm persona P5 (12 partner còn lại không được ảnh hưởng) và các AC bảo vệ tương ứng |
| 1.5 | 2026-08-06 | Nguyễn Đăng Định | Chuẩn hoá thuật ngữ kỹ thuật trên cả PRD và tech spec: claim/giải phóng mã, atomic ở cấp document, multi-document transaction, partial write, tấn công vét cạn, attack vector, entropy, tenant-level feature toggle, silent failure. Bổ sung mục 0 — Thuật ngữ (16 định nghĩa) |
| 1.4 | 2026-08-06 | Nguyễn Đăng Định | Chốt 3 câu hỏi treo. **Dùng Mongo transaction** thay bù trừ — repo đã có `WithTransaction` chạy thật ở luồng rút tiền, nên hạ tầng là replica set; bỏ được cơ chế bù trừ thủ công và job cron đối soát bản ghi không nhất quán. **Format mã** theo đúng quy ước T-Fluencers (`PRS_<8 hex>`), thoả sẵn yêu cầu chống vét cạn. **Quy mô nhân viên nhỏ** → nới mốc hiệu năng, ghi rõ không tối ưu sớm. Open Questions còn 2, trọng tâm là dữ liệu phân nhóm |
| 1.3 | 2026-08-06 | Nguyễn Đăng Định | Soát nhất quán sau đợt vá v1.2: gom 2 field dismissal về FR-001 (đang khai lạc ở FR-008); sửa sơ đồ "Luồng xác nhận" ở mục 7 còn mô tả hành vi cũ (`staff-status` riêng, đóng modal không lưu); NFR-004 đổi sang `users/me`; sửa đếm sai Must Have 13→14; bổ sung 5 hạng mục thiếu trong Implementation Scope (GetMe, rate limit middleware, audit, cron đối soát, `utils/staff.ts`) |
| 1.2 | 2026-08-06 | Nguyễn Đăng Định | Vá 12 lỗ hổng phát hiện khi review flow. **P0:** cấm ghi `isJoined`/`joinedAt` trong `confirm-is-staff` (sẽ làm sai lệch tăng số liệu partner); bù trừ khi claim mã thành công nhưng ghi trạng thái lỗi; chốt phương án A cho thống kê hồi tố kèm ghi chú bắt buộc. **P1:** import cập nhật nhóm thay vì skip; dry-run + `importBatchId`; giới hạn số lần hỏi lại; rate limit dùng chung mọi đường nhập mã. **P2:** yêu cầu entropy khi Parasola đặt mã; ngữ nghĩa AND của `AllowedSegments` + cảnh báo trên admin UI; chặn xoá segment đang được event tham chiếu; gộp `staffStatus` vào `users/me` |
