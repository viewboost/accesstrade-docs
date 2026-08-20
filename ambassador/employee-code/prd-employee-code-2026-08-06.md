# Product Requirements Document: Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Date:** 2026-08-06 (cập nhật 2026-08-17)
**Author:** Nguyễn Đăng Định
**Reviewer:** Vinh Nguyễn — [review-feedback-2026-08-07.md](./review-feedback-2026-08-07.md)
**Version:** 5.1 — đồng bộ với code sau đợt QA
**Project Level:** Level 2
**Status:** Final
**Phạm vi:** **Chỉ partner Parasola.** 12 partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD cho tính năng cho phép **nhân viên Parasola** tự xác nhận danh tính nội bộ trên Ambassador bằng mã do Parasola cấp, phục vụ ba mục tiêu gốc: có nơi nhập mã, có thống kê tách nhân viên với người ngoài, có chiến dịch dành riêng cho nhân viên.

> **Thay đổi lớn ở v5.0 — bỏ phân nhóm bằng segment.** Danh sách mã đã được Admin import bằng Excel, đó là đủ để định danh nhân viên; lớp segment tự động dựng thêm bên trên chỉ để chia nhóm là chi phí không tương xứng. FR-006 gỡ bỏ, FR-011 còn hai cơ chế, FR-015 quay về nhị phân **Nhân viên / Ngoài** đúng như T-Fluencers. Các FR khác giữ nguyên số hiệu để mọi tham chiếu chéo (techspec, bộ 210 test case, PR) không lệch.

### Nguyên tắc

**Bám sát T-Fluencers.** Bản đó đã chạy production và được nghiệm thu nên lấy làm chuẩn. Mọi cơ chế port từ đó.

Chỉ đi khác ở ba loại tình huống, mỗi chỗ đều ghi rõ lý do tại chỗ:
1. **Bắt buộc** — Ambassador khác kiến trúc, không thể làm giống (mục 2.2)
2. **T-Fluencers không có** — phải thiết kế mới (tenant toggle theo partner, sửa lại trạng thái nhân viên)
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
  → Nhân viên nhập mã trên web
  → Hệ thống ghi trạng thái nhân viên
  → Dùng để chặn campaign nội bộ và tách số liệu báo cáo
```

**Về phân nhóm:** không làm. Bản 3.x–4.x từng thiết kế phân nhóm bằng segment tự động port từ T-Fluencers (`applyType: staff_code`). Bỏ ở v5.0: file Excel Admin import đã là nguồn danh sách mã, dựng thêm một lớp nhóm bên trên kéo theo nút "Áp dụng lại", ràng buộc chặn sửa thành viên tay, điều kiện gate thứ ba và breakdown báo cáo — nhiều bề mặt hỏng cho một nhu cầu chưa ai xác nhận. T-Fluencers chạy production cũng chỉ tách nhị phân nhân viên / ngoài.

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
| `UserEventRaw.Options` | ❌ Không có | verify |
| `EventOpts.applyForStaff` / `staffCodes` | ❌ Không có | verify |
| `PartnerOpts` (tenant toggle) | ✅ Có pattern | `AllowResubmitRejectedContent` |
| Gate người tham gia khi nộp bài | ❌ **Không có gì** | `content.go` chỉ chặn theo nguồn, thời gian, link, trùng bài |
| Ngôn ngữ | Backend **cần en+vi**; frontend chỉ tiếng Việt | `internal/locale/properties/{en,vi}/` 12 file mỗi bên; `parasola/` và `admin/` chỉ có `vi-VN.ts` |

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
- **Phân nhóm nhân viên dưới mọi hình thức** (bỏ ở v5.0): không segment tự động, không cột nhóm trong file import, không breakdown theo nhóm trong báo cáo. T-Fluencers cũng chỉ có nhị phân nhân viên / ngoài

---

## 3. User Personas

**P1. Nhân viên Parasola** — được cấp mã qua kênh nội bộ, nhập một lần khi đăng nhập.
**P2. Creator bên ngoài trên Parasola** — chiếm đa số người dùng.
**P3. Admin/Ops AccessTrade** — nhận file mã, import, sửa trạng thái nhân viên khi cần.
**P4. Marketing Parasola** — cấu hình chiến dịch nội bộ, xem báo cáo tách nhân viên với người ngoài.
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

### FR-003: Vá quyền xoá thành viên nhóm

**Priority:** Must Have — **rút gọn ở v5.0**

**Bản 4.x** yêu cầu thêm `partner` vào `UserSegmentRaw` và backfill, vì phân nhóm nhân viên và thống kê theo nhóm đều cưỡi lên bảng này. Bỏ phân nhóm rồi thì luồng mã nhân viên **không đọc `user-segments` nữa**, nên tiền đề đó không còn: **không thêm field, không backfill**.

Giữ lại đúng một phần — lỗ hổng phân quyền, vốn tồn tại độc lập với phân nhóm:

`pkg/admin/service/user_segment.go` — `Delete` gọi `DeleteMany` theo `{_id: {$in}}`, **không gọi `IsAllowPartner`** trong khi `Add` cùng file thì có. Admin của partner A xoá được thành viên nhóm của partner B chỉ bằng cách đoán `_id`.

Sửa: `Delete` yêu cầu `segmentId`, kiểm `IsAllowPartner` như `Add`, và ràng buộc thêm `segment` vào điều kiện xoá thay vì xoá theo `_id` trần.

**AC:**
- [ ] `UserSegment.Delete` kiểm `IsAllowPartner` như `Add`
- [ ] Admin partner A không xoá được bản ghi của partner B
- [ ] Không thêm field mới vào `user-segments`, không cần backfill

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

**Bảng:** Mã nhân viên \| Đối tác \| Đã dùng \| Người dùng \| Ngày dùng \| Ngày tạo

**Phân trang dùng `page` 0-based, `limit` mặc định 20.** Đây là quy ước chung của repo: `GetFindOptsUsingPage` là `SetSkip(Page * Limit)` và mọi màn admin gửi `page: current - 1`. `GetList` của `/manage-codes` **tự phân trang trong bộ nhớ** (vì phải đối soát `isUsed` động với `user-partners` trước khi lọc) nên rất dễ tự đặt lại quy ước 1-based cho riêng nó — làm vậy thì trang 1 và trang 2 trả cùng một khoảng dữ liệu, mọi trang sau lệch một nhịp, và trang cuối không bao giờ tới được.

**Bắt buộc chọn partner tường minh.** `StaffRaw.Partner` đơn trị (`staff.go:38`) và `IsPermissionAllPartner()` trả `true` khi `Partner` rỗng (`:92`) — admin chưa gắn partner tự thành super-admin xuyên tenant. Với dữ liệu nhân sự thì mặc định đó sai hướng:
- Trang `/manage-code` **không có chế độ "tất cả partner"**
- Import/xoá yêu cầu `partner` trong request, không suy từ session

**AC:**
- [ ] CRUD hoạt động, chặn trùng mã trong cùng partner
- [ ] Admin có `Partner` rỗng **không** xem được mã của mọi partner
- [ ] Sang trang 2 ra đúng 20 bản ghi tiếp theo, không lặp lại trang 1; bản ghi cuối của trang cuối truy cập được

---

### FR-005: Import mã hàng loạt

**Priority:** Must Have

Port nguyên T-Fluencers. **File một cột**, nhận cả `.xlsx` lẫn `.csv`.

| `code` |
|---|
| `PRS_A3F91B2C` |
| `PRS_7D0E4A88` |

Xử lý: bỏ dòng header → chuẩn hoá TRIM + UPPERCASE → mã đã tồn tại thì skip → insert phần còn lại. Không có cột nhóm — v5.0 không phân nhóm (FR-006).

**Nhận cả `.csv`, không chỉ `.xlsx`.** Modal cho chọn `.csv` và nút "Tải file mẫu" phát ra đúng một file `.csv`; nếu backend chỉ mở bằng `xlsx.OpenFile` thì tải mẫu về rồi nộp lại chính nó cũng báo lỗi. Cố ý **không** nhận `.xls`: thư viện `tealeg/xlsx` không đọc được định dạng BIFF cũ, cho chọn rồi báo lỗi chung chung còn tệ hơn là không cho chọn.

**Cắt phần đuôi rỗng của file.** Excel coi mọi ô đã từng chạm tới là "có dòng", nên file 20 mã vẫn trả về hàng trăm dòng rỗng phía sau; CSV do Excel xuất cũng hay kèm một loạt dòng chỉ có dấu phẩy. Không cắt thì mỗi dòng đó thành một bản ghi `"Dòng trống"`, `Total` phồng lên hàng trăm và bảng lỗi dài vô nghĩa. **Chỉ cắt ở đuôi** — dòng trống nằm GIỮA vùng dữ liệu vẫn phải báo, vì đó thường là Ops xoá nhầm một ô và cần biết mã nào rơi.

**Báo cáo từng dòng lỗi kèm số dòng.** Khác T-Fluencers: bản đó skip im lặng nên Ops không biết dòng nào hỏng và vì sao. Ambassador trả về `{total, inserted, skipped, errors[]}`, mỗi `error` gồm `{row, code, reason}` với `reason` ∈ *Dòng trống* · *Trùng trong file* · *Mã đã tồn tại* · *Không đọc được dòng*. Dòng đọc hỏng cũng phải xuất hiện trong báo cáo, không được bỏ lặng — nếu không Ops đối chiếu "file 100 dòng, import báo 97" mà không biết 3 dòng nào rơi ở đâu, tưởng hệ thống ăn mất mã.

**Hành vi modal sau khi import.** Import sạch, không dòng lỗi nào ⇒ **đóng modal**. Còn dòng lỗi ⇒ giữ modal để Ops đọc bảng lỗi, nhưng **gỡ file khỏi ô chọn**. Bắt buộc phải gỡ: giữ lại thì bấm "Tải lên" thêm lần nữa là nộp đúng file vừa import, mà các mã giờ đã nằm trong DB nên tất cả quay về dưới dạng *Mã đã tồn tại* — báo cáo đầy dòng trùng do chính lần import trước sinh ra.

**Sửa một bug của T-Fluencers:** `ImportExcel` bên đó kiểm `len(newCodes) == 0` hai lần liên tiếp, nhánh thứ hai là code chết. Bỏ nhánh thừa.

**AC:**
- [ ] Import file 1 cột hoạt động với cả `.xlsx` và `.csv`, báo số dòng thành công / bị skip
- [ ] Mã chuẩn hoá TRIM + UPPERCASE trước khi lưu
- [ ] File 20 mã có đuôi rỗng ⇒ `Total = 20`, bảng lỗi rỗng
- [ ] Dòng trống ở GIỮA vùng dữ liệu vẫn được liệt kê trong bảng lỗi
- [ ] Import sạch ⇒ modal tự đóng; có lỗi ⇒ modal ở lại nhưng ô chọn file đã trống

---

### FR-006: ~~Segment tự động theo mã nhân viên~~ — GỠ Ở v5.0

**Priority:** ~~Must Have~~ → **Không làm**

Bản 3.x–4.x thiết kế phân nhóm bằng segment tự động: Admin tạo segment `automatic` với `applyType: staff_code` và một danh sách mã, ai nhập mã trong danh sách thì tự vào nhóm; kèm nút "Áp dụng lại" để đồng bộ khi Ops sửa danh sách mã, và ràng buộc cấm sửa thành viên tay trên nhóm `source: staff_import`.

**Vì sao gỡ.** Import Excel (FR-005) đã cho Admin toàn quyền quản danh sách mã; nhu cầu chia nhóm chưa được Parasola xác nhận (Open Question 3 vẫn treo từ 06/08). Trong khi đó lớp nhóm kéo theo bốn bề mặt phải nuôi: đồng bộ không hồi tố phải có nút thủ công, cấm-sửa-tay để nhóm không thành cửa hậu qua gate, điều kiện gate thứ ba ở FR-011, và breakdown ở FR-015 mà tổng các dòng con không khớp dòng tổng khi một người thuộc nhiều nhóm. T-Fluencers — bản đã nghiệm thu production và là chuẩn bám của PRD này — không dùng segment cho nhân viên.

**Hệ quả kéo theo:** FR-003 rút gọn còn vá quyền, FR-010 bỏ bước gỡ khỏi nhóm, FR-011 còn hai cơ chế, FR-014/015/016 bỏ chiều nhóm.

**Muốn làm lại sau này** thì đây là một phase riêng, và điều kiện kích hoạt là Parasola trả lời được hai câu: chia nhóm theo tiêu chí gì, và số liệu theo nhóm dùng để chi tiền hay chỉ để xem.

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
         mã đã isUsed bởi user KHÁC ⇒ lỗi "Mã nhân viên này đã được tài khoản khác sử dụng"
     mã đã nằm ở user-partners của user KHÁC cùng partner ⇒ cùng lỗi trên
4. Upsert user-partners: statusStaff + staffCode
```

#### Một mã chỉ thuộc về một tài khoản

Chặn ở **hai tầng**, vì hai tầng ghi dữ liệu khác nhau và không phải lúc nào cũng đồng bộ: `manage-codes.isUsed/usedBy` (bảng mã do Admin quản), và `user-partners.staffCode` (mã user đã khai). Thiếu tầng thứ hai thì mã chưa kịp đánh dấu `isUsed` vẫn bị người thứ hai khai trùng, và báo cáo có hai creator cùng một mã nhân viên.

Lỗi trả về là key **riêng** `StaffCodeKeyCodeAlreadyUsed` → *"Mã nhân viên này đã được tài khoản khác sử dụng"*. Không dùng lại key `AlreadyUsed` của luồng Admin (*"Mã đã được sử dụng, không thể xoá"*) — câu đó nói về thao tác xoá mã ở màn quản lý, hiện cho người dùng cuối là sai ngữ cảnh hoàn toàn.

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

(Backend cần bản `en` tương ứng — xem NFR-004.)

**AC:**
- [ ] **`isJoined`/`joinedAt` không xuất hiện trong bất kỳ câu ghi nào** — có test khẳng định
- [ ] User bấm "Tôi không thuộc Parasola" → **không** bị tính vào danh sách creator của partner
- [ ] `UserPartnerRaw.Code` không bị thay đổi
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
- Gỡ nhãn → xoá luôn `staffCode` đã ghi, không để lại dữ liệu mồ côi
- **Bắt buộc nhập lý do**, và lý do phải được **lưu lại** (xem dưới)

**Đường admin phải áp đúng bộ luật của luồng người dùng tự khai (FR-008).** Gán mã ở đây cũng là ghi `staffCode`, nên cũng phải: đối chiếu `manage-codes` khi partner bật `RequireStaffCodeValidation`, và chặn mã đã thuộc về tài khoản khác — kiểm ở cả `manage-codes.isUsed/usedBy` lẫn `user-partners.staffCode`. Chỉ hiện dòng chữ nhắc trên form là **không đủ**: không có gì thực thi thì admin gán được mã không tồn tại và gán trùng mã của người khác, mà hai creator cùng một mã nhân viên thì báo cáo đối soát không còn quy về được ai.

**Lý do phải ghi vào audit, không chỉ validate rồi bỏ.** Nhận field rồi vứt đi là bắt admin gõ vào chỗ không ai đọc được, và làm hỏng chính lập luận BVDLCN 2025 ở trên. Ghi qua `internalservice.Audit()` kèm trạng thái và mã **trước/sau**, để đọc lại còn biết đã đổi từ đâu sang đâu chứ không chỉ giá trị cuối. Kiểm bắt buộc trên chuỗi đã TRIM — một dấu cách lách qua được thì audit lưu về một dòng trắng. Lỗi ghi audit không được làm hỏng thao tác: trạng thái đã cập nhật xong, bắt admin làm lại chỉ vì mất một dòng log là đánh đổi sai.

**AC:**
- [ ] User tự chuyển `not_employee → employee` được
- [ ] User **không** tự gỡ được nhãn nhân viên
- [ ] Admin gỡ nhãn → `statusStaff` đổi và `staffCode` bị xoá
- [ ] Nhân viên bị backfill nhầm ở FR-017 khai lại được
- [ ] Không nhập lý do ⇒ bị từ chối; nhập toàn khoảng trắng cũng bị từ chối
- [ ] Đổi trạng thái xong ⇒ có bản ghi audit chứa lý do và trạng thái/mã trước–sau
- [ ] Admin gán mã đã thuộc tài khoản khác ⇒ bị từ chối
- [ ] Partner bật "Chỉ chấp nhận mã đã cấp" ⇒ admin gán mã không có trong `manage-codes` bị từ chối
- [ ] Nút submit của modal ghi "Cập nhật", không phải "Tạo mới"

---

### FR-011: Chiến dịch dành riêng cho nhân viên

**Priority:** Must Have

Port hai cơ chế của T-Fluencers vào `EventOpts` (cơ chế thứ ba — `applyForSegments` — gỡ cùng FR-006):

```go
ApplyForStaff bool     `bson:"applyForStaff,omitempty"`
StaffCodes    []string `bson:"staffCodes,omitempty"`
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

#### Cờ ra FE

`isRequireCode` trên event list và event detail, logic như T-Fluencers.

> **Nợ kế thừa có chủ ý.** T-Fluencers tính cờ này khác nhau: event list (`event.go:515`) = `len(StaffCodes) > 0`, không xét user đã nhập chưa; event detail (`event.go:1074`) chỉ `true` khi user chưa có mã hợp lệ. Cùng một event, hai màn hình trả hai giá trị. Port nguyên để giữ parity — ghi ra để dev không tưởng mình làm sai.

#### Admin UI — `admin/src/pages/event/components/modal.tsx`

Gom thành một section. Form này hiện dùng `Row`/`Col` với bộ `Rc*` (`RcSwitchFormNew`, `RcFormSelectNew`) và **chưa có `Divider` nào** — thêm `<Divider orientation="left">Cấu hình nhân viên</Divider>` là pattern mới cho file này, lấy từ form Partner.

```
──────── Cấu hình nhân viên ────────

[RcSwitchFormNew]  Chỉ dành cho nhân viên

[RcFormSelectNew mode="tags", cả dòng]  Mã tham gia riêng của chiến dịch  (?)
   tokenSeparators={[',', ' ', '\n']}
   Placeholder: Dán danh sách mã, phân tách bằng dấu phẩy hoặc xuống dòng
   tooltip: Khác với mã nhân viên ở trang Quản lý mã. Mã ở đây chỉ dùng cho chiến dịch này.
```

**Ghi chú đặt ở tooltip cạnh nhãn, không phải khối `Alert` dưới ô nhập.** Đây là bước trong `StepsForm`: một khối `Alert` chiếm nguyên một hàng sẽ đẩy cặp nút Quay lại / Tiếp theo xuống và kéo dài bước chỉ để nói một câu. Dùng prop `tooltip` của `Form.Item` (antd hỗ trợ từ 4.7, dự án đang 4.20), cùng khuôn với các ô đã có ở màn Đối tác.

**Hai quyết định về nhãn:**

| | T-Fluencers | Ambassador | Lý do |
|---|---|---|---|
| `applyForStaff` | "Chỉ nhân viên nội bộ" | **"Chỉ dành cho nhân viên"** | Parasola không phải ngân hàng, nhân sự cửa hàng cũng là nhân viên |
| `staffCodes` | "Mã code nhân viên" | **"Mã tham gia riêng của chiến dịch"** | Tên cũ trùng mã ở `/manage-code` nhưng hai vòng đời tách rời, Ops dễ nhầm |

**AC:**
- [ ] Hai điều kiện hoạt động độc lập và kết hợp được
- [ ] Event không bật điều kiện nào → hành vi không đổi
- [ ] **Bật `applyForStaff` nhưng `Enabled = false` → người ngoài vẫn bị chặn**
- [ ] **User join khi campaign mở, admin bật `applyForStaff` sau → không nộp được bài kế tiếp**
- [ ] Dán 200 mã một lần → tách đúng 200 tag
- [ ] Có test khẳng định gate nằm trên đường nộp bài, không nằm sau nhánh "đã join"

---

### FR-012: Thông báo khi không đủ điều kiện

**Priority:** Must Have

Port `modal-not-employee.tsx`. Modal này **đóng được** — khác FR-009.

| Trường hợp | Tiêu đề | Hành động |
|---|---|---|
| Không phải nhân viên, vào event `applyForStaff` | Thử thách này dành riêng cho nhân viên Parasola | Đã hiểu / Khám phá thêm |

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

### FR-014: Admin — hiển thị và lọc theo trạng thái nhân viên

**Priority:** Must Have

**Cột mới:** `Nhân viên` (Có/Không) \| `Mã nhân viên`
**Filter mới:** `statusStaff` **(chọn nhiều)**

Theo quy ước toàn sản phẩm: mọi bộ lọc là multi-select (BE dùng `$in`, URL dạng CSV).

**AC:**
- [ ] Hai cột hiển thị đúng, rỗng hiện `—`
- [ ] Filter multi-select, kết hợp được với filter sẵn có

---

### FR-015: Thống kê tách nhân viên với người ngoài

**Priority:** Must Have

Giữ nguyên quy tắc nhị phân staff/guest của T-Fluencers. **Không có chiều nhóm** (FR-006 đã gỡ).

| Phân loại | Số người | Đã tham gia | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|
| **Tổng — Nhân viên** | 210 | 168 | 1.180 | 3,1tr | 190tr |
| **Tổng — Ngoài** | 770 | 640 | 3.340 | 9,3tr | 650tr |

Kèm bốn ô đếm phía trên: Tổng creator, Nhân viên, Không phải nhân viên, Chưa khai báo.

**Bảng chi tiết "Nhân viên & creator đã gán mã".** Dưới hai dòng tổng là danh sách từng người:

| Creator | Mã nhân viên | Trạng thái | Số bài | Lượt xem | Chi phí |
|---|---|---|---|---|---|

Gồm creator đã xác nhận là nhân viên **và** creator đã được gán mã nhưng chưa xác nhận — nên đây không phải tập con của ô đếm "Nhân viên".

- **Creator đứng cột đầu**, trước Mã nhân viên và Trạng thái: người xem tìm theo tên trước, mã chỉ là thuộc tính của người đó
- Cột Creator hiện avatar, tên, và số điện thoại ở dòng phụ; tên chỉ là link tới trang user khi tài khoản có quyền root, vì tài khoản khác bấm vào sẽ rơi vào 403
- **20 dòng/trang, không có ô đổi số dòng.** Bảng gom sẵn toàn bộ dữ liệu và phân trang phía client; `GetPagination` dùng chung của dự án đã mặc định tắt `showSizeChanger` nên không khai báo lại

**Quy tắc tính** — giữ quy ước T-Fluencers:
- "Nhân viên" = `constants.IsStaff(statusStaff)`; mọi giá trị khác thuộc "Ngoài"
- "Ngoài" = Tổng − Nhân viên, không cộng dồn từng loại
- Không tính bài đã huỷ

**Phân loại theo trạng thái hiện tại, không snapshot.** Nhân viên xác nhận muộn thì số kỳ cũ đổi theo. Đây cũng là hành vi T-Fluencers; khác ở chỗ Ambassador **in ghi chú rõ** trên bảng và export:

> *Phân loại nhân viên theo trạng thái tại thời điểm xem báo cáo.*

> ⚠️ **Chờ Parasola xác nhận:** nếu số liệu tách nhân viên dùng để **chi tiền**, phải đóng băng `isStaff` vào `ReconciliationItem` lúc chốt kỳ, nếu không số kỳ đã chốt vẫn đổi. T-Fluencers có snapshot đối soát nhưng **không phủ chiều nhân viên** — chỗ này không có tiền lệ để bám. Chỉ để xem thì giữ nguyên như trên.

**AC:**
- [ ] Nhân viên + Ngoài = tổng toàn hệ thống
- [ ] Có ghi chú "không bao gồm bài đã huỷ" và ghi chú phân loại theo trạng thái hiện tại
- [ ] Tải xong dưới 3 giây

---

### FR-016: Xuất dữ liệu

**Priority:** Should Have

Hai việc tách rời: bổ sung 2 cột `Nhân viên` | `Mã nhân viên` vào file export creator hiện có, và thêm nút **Xuất CSV** cho bảng FR-015.

#### File xuất của bảng FR-015

Bám đúng khuôn báo cáo Parasola đang dùng: **một bảng phẳng**, dòng 1 là tiêu đề, từ dòng 2 là dữ liệu.

| User ID | Tên Creator | Hashtag | Mã nhân viên | Nhân viên | Số video | Tổng lượt xem | Phí quảng cáo |
|---|---|---|---|---|---|---|---|

**Không chèn khối ngữ cảnh hay khối tổng quan lên đầu file.** Bản 5.0 xuất ba khối chồng nhau (ngữ cảnh bộ lọc → tổng quan → chi tiết), khiến tiêu đề bảng nằm giữa file: mở bằng Excel hay Sheets là không lọc và sắp xếp được nếu chưa xoá tay mấy dòng đầu — việc người nhận file luôn làm đầu tiên. Ngữ cảnh chuyển hết vào **tên file**: `thong-ke-nhan-vien-{đối-tác}-{từ}-{đến}.csv`.

**Quy ước từng cột:**

- `Hashtag` — hashtag cá nhân của creator, lấy từ `user.hashtag`. Giá trị lưu sẵn cả dấu `#` (Parasola cho creator copy thẳng chuỗi này để dán vào bài) nên ghi nguyên, không thêm bớt
- `Nhân viên` — ghi **nhãn tiếng Việt** *Nhân viên* / *Không phải nhân viên* / *Chưa khai báo*, đúng chữ đang hiện trên bảng. Không ghi `"Có"/"Không"` như bản 5.0, cũng không ghi giá trị thô `employee`
- `Số video` · `Tổng lượt xem` · `Phí quảng cáo` — số trần, không format nghìn, để Excel còn tính được

**Cố ý không có `Tổng bình luận` và `Engagement (%)`** dù báo cáo mẫu của Parasola có: hai cột đó không phục vụ việc đối soát nhân viên. **Cũng không có `Tổng lượt thích`** — đã cân nhắc rồi bỏ ở v5.1, vì giữ nó buộc pipeline phân tích cộng thêm `statistic.like.total` trên mọi bản ghi chỉ để phục vụ một cột không ai đọc.

**CSV phải chống Excel diễn giải nhầm:** BOM `﻿` để Excel nhận UTF-8 (không có thì tiếng Việt vỡ), CRLF, và ô chữ mở đầu bằng `=` `+` `-` `@` phải chèn nháy đơn — số điện thoại dạng `+8498...` không xử lý sẽ thành `#NAME?`.

**AC:**
- [ ] File export creator hiện có mọc thêm 2 cột `Nhân viên` | `Mã nhân viên`
- [ ] File xuất bảng FR-015 có đúng 8 cột trên, dòng 1 là tiêu đề, không có khối phụ nào
- [ ] Mở bằng Excel/Sheets lọc và sắp xếp được ngay, không cần xoá dòng nào
- [ ] Tiếng Việt không vỡ; số điện thoại giữ nguyên dạng chữ

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
- Không đụng `UserPartnerRaw.Code`

### NFR-002: Data Integrity
- Luồng `confirm-is-staff` không bao giờ ghi `isJoined`/`joinedAt`/`code`
- `UserSegment.Delete` kiểm quyền partner như `Add` (FR-003)

### NFR-003: Performance
Quy mô nhân viên Parasola nhỏ. Các mốc dưới đây chỉ để chặn thiết kế sai kiểu N+1, không phải bài toán tải thật. **Không tối ưu sớm.**
- Import 1.000 mã < 10 giây
- Thống kê FR-015 < 3 giây

### NFR-004: Ngôn ngữ

Hai tầng khác nhau, đừng gộp:

| Tầng | Yêu cầu |
|---|---|
| **Backend** | **Bắt buộc CẢ `en` và `vi`.** `internal/locale/properties/` có 12 file mỗi bên, và `properties.MustLoadFile` gọi `log.Fatal` nếu thiếu file `en/` → thiếu là **service không khởi động được** |
| **Frontend** (`parasola/`, `admin/`) | **Chỉ tiếng Việt.** Cả hai chỉ có `vi-VN.ts`, không có `en-US` |

---

## 6. Epics và thứ tự

| Epic | FR | Ghi chú |
|---|---|---|
| **EPIC-000** Vá quyền | FR-003 | `UserSegment.Delete` kiểm quyền partner. Độc lập, làm lúc nào cũng được |
| **EPIC-001** Nền tảng | FR-001, 002, 013 | Model, constants, collection, index, tenant toggle |
| **EPIC-002** Quản lý mã | FR-004, 005 | Admin CRUD + import |
| ~~**EPIC-003** Phân nhóm~~ | ~~FR-006~~ | **Gỡ ở v5.0** |
| **EPIC-004** Luồng người dùng | FR-007, 008, 009, 010 | API + modal + sửa lại |
| **EPIC-005** Chiến dịch | FR-011, 012 | Hai cơ chế gate + modal từ chối |
| **EPIC-006** Báo cáo | FR-014, 015, 016 | Cột, filter, thống kê, export |
| **EPIC-007** Phát hành | FR-017 | Backfill, chạy **trước** khi bật cờ |

---

## 7. Kiến trúc

```
Parasola phát mã (kênh nội bộ)
        │
        ▼
Admin import Excel 1 cột  →  manage-codes {partner, type, code}
        │
        ▼
Nhân viên nhập mã  →  POST /users/confirm-is-staff
        └──► user-partners  {statusStaff, staffCode}
        │
   ┌────┴───────────────┬────────────────────┐
   ▼                    ▼                    ▼
Gate chiến dịch      Thống kê            Hiển thị/Export
content.go           nhân viên / ngoài   admin user-partner
(độc lập JoinEvent)
```

---

## 8. Implementation Scope

### Thay đổi cần làm

| Vùng | File | Nội dung |
|---|---|---|
| **Model** | `model/mg/user_partner.go` | +2 field |
| **Model** | `model/mg/manage_code.go` | File mới |
| **Model** | `model/mg/user_event.go` | +`Options` |
| **Model** | `model/mg/partner.go` | +2 field trong `PartnerOpts` |
| **Model** | `model/mg/event.go` | +2 field trong `EventOpts` |
| **Constants** | `constants/staff_code.go` | File mới |
| **DAO** | `module/database/mongodb/` | `ManageCodeDAO` + collection + index |
| **Public API** | `pkg/public/{router,handler,service}/user.go` | `confirm-is-staff` |
| **Public API** | `pkg/public/{router,handler,service}/partner.go` | `status-employee` |
| **Public API** | `pkg/public/{router,handler,service}/event.go` | `input-code-join-event` |
| **Public API** | `pkg/public/service/content.go` | Load `userPartner` + 2 điểm chặn, **trước** `JoinEvent` |
| **Admin API** | `pkg/admin/{router,handler,service}/manage_code.go` | File mới |
| **Admin API** | `pkg/admin/service/user_segment.go` | `Delete` kiểm `IsAllowPartner` |
| **Admin API** | `pkg/admin/service/user_partner.go` | Trả thêm field + filter + sửa trạng thái |
| **Export** | `pkg/admin/service/export_*.go` | +2 cột |
| **Thống kê** | `aggregate_pipeline/` | Đếm theo `statusStaff` + gộp số liệu theo user |
| **Locale** | `internal/locale/staff_code.go` + `properties/vi/` | Key mới, chỉ tiếng Việt |
| **Admin UI** | `admin/src/pages/manage-code/` | Trang mới |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | +Divider section, +2 `Form.Item`+`Switch` antd |
| **Admin UI** | `admin/src/pages/event/components/modal.tsx` | +Divider section, +1 `RcSwitchFormNew`, +1 `RcFormSelectNew` |
| **Admin UI** | `admin/src/pages/user-partner/` | +2 cột, +1 filter, +nút sửa trạng thái |
| **Admin UI** | `admin/src/pages/event-statistic/` | Khối thống kê nhân viên / ngoài |
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
- **Không phân nhóm nhân viên** — không segment tự động, không cột nhóm khi import, không breakdown theo nhóm (v5.0)
- Không dùng ENV toàn cục
- Không thêm cột nhóm vào file import
- Không thêm ràng buộc một-mã-một-người, rate limit, audit trail, transaction
- Không thêm chuỗi tiếng Anh **ở frontend** (backend vẫn cần, xem NFR-004)
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
- **Phân nhóm nhân viên** — gỡ ở v5.0, xem FR-006. Muốn làm lại là một phase riêng
- Snapshot trạng thái nhân viên theo từng bài đăng

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
- **Không có cách nhóm nhân viên theo bộ phận.** Muốn số liệu theo phòng ban/khu vực thì phải xử lý ngoài hệ thống bằng chính file mã Ops giữ.

---

## 11. Traceability

| Yêu cầu gốc | FR đáp ứng |
|---|---|
| Có nơi để nhân viên nhập mã | FR-007, 008, 009, 010 |
| Có thống kê kết quả tách nhân viên với người ngoài | FR-014, 015, 016 |
| Có campaign dành riêng cho nhân viên | FR-011, 012 |
| Import nhân viên để về sau còn phân loại | FR-002, 004, 005 |

| Priority | FR |
|---|---|
| **Must Have** (15) | FR-001 → FR-005, FR-007 → FR-015, FR-017 |
| **Should Have** (1) | FR-016 |
| **Đã gỡ** (1) | FR-006 |

Tổng 16 FR còn hiệu lực.

**Thứ tự bắt buộc:** FR-017 trước khi bật cờ ở FR-013.

---

## 12. Resolved Questions

1. **Bám theo T-Fluencers không?** → Có. Chỉ khác ở 3 điểm bắt buộc (2.2), 3 lỗi đã kiểm chứng (2.3), và phần T-Fluencers không có.
2. **Một mã dùng cho mấy người?** → Nhiều người, như T-Fluencers.
3. **Modal có chặn không?** → Có, blocking. Khác một điểm: chỉ nhánh nhân viên nhập mã (FR-009).
4. **Có port `staffCodes` theo event không?** → Có, đủ ba cơ chế.
5. **Phân nhóm bằng cách nào?** → **Không phân nhóm** (v5.0). Bản 3.x–4.x định dùng segment tự động; gỡ vì import Excel đã đủ và nhu cầu chia nhóm chưa được xác nhận.
6. **Format mã?** → `PRS_<8 hex ngẫu nhiên viết hoa>`, sinh bằng `f"PRS_{secrets.token_hex(4).upper()}"` như Handbook hướng dẫn.
7. **Bật/tắt bằng gì?** → `PartnerOpts` thay ENV.
8. **Tên trường mã?** → `staffCode`, vì `Code` đã là referral.
9. **Gọi lại `confirm-is-staff` khi đã xác nhận?** → **Cho ghi đè**, như T-Fluencers. Đây là nền tảng của FR-010.
10. **Sửa lại trạng thái?** → **Có** (FR-010). T-Fluencers không có UI nhưng API vốn cho ghi đè. Bắt buộc vì FR-017 backfill tạo ra nhu cầu này.
11. ~~**Sửa danh sách mã trong segment có hồi tố?**~~ → không còn đặt ra sau khi gỡ FR-006.
12. **Ngôn ngữ?** → **Backend cần cả `en` và `vi`** (`MustLoadFile` sẽ `log.Fatal` nếu thiếu `en`); **frontend chỉ tiếng Việt** (`parasola/`, `admin/` không có `en-US`).

---

## 13. Open Questions

**Chặn FR-015, không chặn EPIC-000 → 005:**

1. **Số liệu tách nhân viên có dùng để chi tiền không?**
   - Không (chỉ để xem) → giữ FR-015 như hiện tại
   - Có → đóng băng `isStaff` vào `ReconciliationItem` lúc chốt kỳ

**Cần Parasola xác nhận, không chặn code:**

2. Có phát mã cho nhân viên không, qua kênh nào
3. Có cần chia nhóm nhân viên không — nếu có thì theo tiêu chí gì, và số liệu theo nhóm dùng để xem hay để chi tiền. Đây là điều kiện để mở lại FR-006 ở một phase riêng
4. Có chiến dịch nội bộ nào định chạy không — nếu không, FR-011 có thể hạ ưu tiên

Bối cảnh: tính năng **không nằm trong yêu cầu hệ thống gốc** Parasola gửi (`[AT - PV] Parasola Ambassador_Working file Final - 2. Yêu cầu hệ thống_Parasola.csv` không nhắc gì tới nhân viên), chưa có BR, chưa kickoff.

---

## 14. Revision History

| Version | Date | Changes |
|---------|------|---------|
| **5.1** | 2026-08-17 | **Đồng bộ PRD với code sau đợt QA.**<br>**FR-010:** đường admin phải áp đúng bộ luật FR-008 khi gán mã (đối chiếu `manage-codes` khi partner bật cờ, chặn mã đã thuộc tài khoản khác ở cả hai tầng) — trước đó chỉ có dòng chữ nhắc trên form, không có gì thực thi; lý do đổi trạng thái bắt buộc thật và phải ghi vào audit kèm trạng thái/mã trước–sau, kiểm trên chuỗi đã TRIM; thêm 5 AC kiểm được.<br>Không đổi phạm vi, chỉ ghi lại đúng những gì đã dựng và những luật phát hiện khi chạy thật.<br>**FR-004:** ghi rõ phân trang `page` 0-based, `limit` mặc định 20 — `GetList` tự phân trang trong bộ nhớ nên đã có lúc tự đặt lại quy ước 1-based, làm trang 1 và 2 trùng nhau và trang cuối không tới được.<br>**FR-005:** nhận cả `.csv` (nút tải mẫu phát ra `.csv`), cố ý loại `.xls`; cắt phần đuôi rỗng của file — Excel trả hàng trăm dòng rỗng sau vùng dữ liệu, không cắt thì `Total` phồng lên và bảng lỗi vô nghĩa; chỉ cắt ở đuôi, dòng trống ở giữa vẫn báo; bổ sung hợp đồng `errors[]` bốn loại lý do; chốt hành vi modal sau import (sạch thì đóng, có lỗi thì giữ nhưng gỡ file khỏi ô chọn để không nộp lại nhầm).<br>**FR-008:** bổ sung luật một mã chỉ thuộc một tài khoản, chặn ở cả `manage-codes.isUsed` lẫn `user-partners.staffCode`, dùng key lỗi riêng thay vì mượn câu của luồng xoá mã ở Admin.<br>**FR-011:** ghi chú mã chiến dịch chuyển từ khối `Alert` sang `tooltip` cạnh nhãn.<br>**FR-015:** bổ sung bảng chi tiết "Nhân viên & creator đã gán mã" vốn đã dựng nhưng PRD chưa mô tả — thứ tự cột với Creator đứng đầu, 20 dòng/trang, không có ô đổi số dòng.<br>**FR-016:** viết lại theo khuôn báo cáo Parasola — một bảng phẳng 8 cột, bỏ ba khối phụ ở đầu file vì chúng đẩy tiêu đề xuống giữa khiến không lọc/sắp xếp được; chốt nhãn cột "Nhân viên" là tiếng Việt; ghi rõ đã cân nhắc rồi bỏ `Tổng lượt thích` |
| **5.0** | 2026-08-14 | **Bỏ phân nhóm bằng segment.** Lý do: Admin đã import danh sách mã bằng Excel (FR-005), lớp nhóm dựng thêm bên trên chỉ phục vụ một nhu cầu chưa được Parasola xác nhận (Open Question 3 treo từ 06/08) nhưng kéo theo bốn bề mặt phải nuôi — đồng bộ thủ công, cấm sửa thành viên tay, điều kiện gate thứ ba, breakdown báo cáo lệch khi một người thuộc nhiều nhóm.<br>**FR-006:** gỡ toàn bộ (segment `applyType: staff_code`, nút "Áp dụng lại", ràng buộc `source: staff_import`).<br>**FR-003:** rút gọn — không thêm `partner`/`note` vào `user-segments`, không backfill; chỉ giữ vá quyền cho `UserSegment.Delete` vì đó là lỗ hổng độc lập.<br>**FR-011:** còn hai cơ chế, bỏ `applyForSegments` và cảnh báo mã mồ côi.<br>**FR-010:** gỡ nhãn không còn bước gỡ khỏi nhóm, thay bằng xoá `staffCode`.<br>**FR-012:** còn một trường hợp từ chối.<br>**FR-014/016:** bỏ cột `Nhóm` và filter segment.<br>**FR-015:** về nhị phân Nhân viên / Ngoài như T-Fluencers, bỏ dòng nhóm, dòng "Chưa phân nhóm" và cảnh báo trùng nhóm.<br>Giữ nguyên số hiệu FR để không phá tham chiếu chéo. 17 → 16 FR còn hiệu lực |
| **4.1** | 2026-08-10 | Sửa NFR-004 — lỗi phát hiện khi code. Bản 4.0 ghi "chỉ tiếng Việt, Ambassador không có en-US", nhưng đó là kết luận từ việc chỉ kiểm locale **frontend**. Backend có `internal/locale/properties/en/` 12 file và `MustLoadFile` sẽ `log.Fatal` nếu thiếu — làm đúng theo bản cũ thì **service không khởi động được**. Nay tách rõ: backend bắt buộc en+vi, chỉ frontend mới thuần Việt |
| **4.0** | 2026-08-07 | **Bản chốt.** Áp feedback review của Vinh Nguyễn + kết quả tự soát lại toàn bộ khẳng định với code.<br>**FR mới:** FR-003 (`user-segments` thiếu `partner` — chặn FR-006/015), FR-010 (sửa lại trạng thái — bị cắt nhầm ở v2.0 khiến FR-017 tự mâu thuẫn), FR-017 (backfill user hiện có).<br>**FR-006:** thêm nút "Áp dụng lại" — sửa danh sách mã trong segment vốn không hồi tố, PRD v3.x hứa sai chỗ này.<br>**FR-011:** ràng buộc cấm nhét gate vào `CalculateEligibility`; `AllowedSegments` AND `IsStaff`; ghi nhận nợ `isRequireCode`; **lưu ý `content.go` chưa load `userPartner`** — code mẫu ở techspec v3.x không compile.<br>**FR-002:** ghi rõ điều kiện `isUsed` khi xoá mã là code chết.<br>**FR-008:** ghi rõ cho phép ghi đè khi gọi lại.<br>**Sửa 3 mô tả sai:** partner modal dùng antd `Switch` chứ không phải `RcSwitchFormNew`; event modal chưa có `Divider` nào; NFR-004 đòi VI+EN trong khi Ambassador chỉ có `vi-VN`.<br>**FR-009:** sửa lập luận sai — nhánh "không phải nhân viên" ở T-Fluencers không validate mã nên không phải ngõ cụt; lý do đúng là dữ liệu rác + copy sai.<br>Đánh số FR lại liền mạch, bỏ FR-002b. 14 → 17 FR |
| 3.2 | 2026-08-07 | Áp một phần feedback review |
| 3.0–3.1 | 2026-08-06 | Phân nhóm chuyển sang segment tự động port từ T-Fluencers |
| 2.0 | 2026-08-06 | Viết lại theo hướng bám T-Fluencers, bỏ các thay đổi tự đề xuất |
| 1.0–1.6 | 2026-08-06 | Bản đầu và các vòng soát |
