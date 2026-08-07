# Feedback thiết kế — Luồng nhập mã nhân viên trên Ambassador (Parasola)

**Ngày:** 2026-08-07
**Người review:** Vinh Nguyễn
**Tài liệu được review:** `prd-employee-code-2026-08-06.md` (v1.3) + `techspec-employee-code-2026-08-06.md`
**Phương pháp:** verify trực tiếp trên code `AT-Core/ambassador` và `Viewboost-2025/techcombank`, không dựa vào mô tả trong tài liệu.

---

## 0. Kết luận nhanh

PRD chất lượng cao. Ba quyết định quan trọng nhất đều **đúng** và phải giữ nguyên:

| Quyết định | Bằng chứng xác nhận |
|---|---|
| `statusStaff` đặt trên `user-partners` (edge), không trên `user` | `user.go:44` — `UserRaw.Partners []AppID`: user là **global**, một người thuộc nhiều partner. Cùng một người có thể là NV Parasola + creator VNPay. Đây đúng chuẩn "global identity + tenant membership" |
| `PartnerOpts` thay ENV toàn cục | Code hiện đang hardcode `partner.Slug == "wildrift"` (`pkg/public/service/user.go:1567`) — flag theo tenant là bước tiến thật |
| Cấm ghi `isJoined`/`joinedAt` trong `confirm-is-staff` | Verified `internal/service/user.go:226`. TCB ghi `IsJoined: true` ở `pkg/public/service/user.go:241` — PRD bắt đúng bug nghiêm trọng nhất của bản TCB |

Phần còn lại chia làm hai:
- **Phần A — 7 mục phải sửa** (2 mục P0 money-path). Mỗi mục ghi rõ sửa **theo TCB** hay **theo chuẩn ngành**.
- **Phần B — 5 mục bổ sung vào Out of Scope**: những thứ TCB **cũng chưa có**, không có tiền lệ để bám, không nên gánh trong phase này — nhưng phải ghi ra kèm rủi ro tồn dư.

---

# PHẦN A — PHẢI SỬA

## A1. 🔴 P0 — Gate campaign nhân viên có thể mở toang, im lặng

**Sửa theo: TECHCOMBANK (a) + chuẩn ngành fail-closed (b)**

Hai lỗi độc lập, cùng dẫn tới một hậu quả: campaign "chỉ dành cho nhân viên" cho người ngoài vào, không báo lỗi gì.

### (a) Gate chỉ chạy lúc join, không chạy lúc nộp bài — **bước lùi so với TCB**

`backend/pkg/public/service/eligibility.go:216`:
```go
// 2. Check if user already joined
if err == nil && !existingUserEvent.ID.IsZero() {
    return nil          // ← thoát, KHÔNG kiểm tra lại điều kiện
}
```
Mà `content.go:123` là chỗ **duy nhất** gọi gate.

**Kịch bản hỏng:** campaign chạy mở 3 ngày → 500 creator ngoài join → Marketing bật `staffRequired` → 500 người đó nộp bài và ăn thưởng đến hết campaign.

**TCB đã giải quyết đúng.** `contentImpl.Create` (`content.go:43`) đặt gate **trong luồng nộp bài**, đọc `statusStaff` tươi mỗi lần (`content.go:105-120`):
```go
_ = UserPartnerDAO().FindOne(ctx, userPartner, bson.M{"user": userId, "partner": event.Partner})
if event.Options.ApplyForStaff {
    if userPartner.ID.IsZero() || userPartner.StatusStaff != constants.StatusStaffIsEmployee {
        return errors.New(locale.EventKeyApplyOnlyStaff)
    }
}
```
Bật `applyForStaff` giữa chừng → người ngoài bị chặn ngay bài kế tiếp. Không grandfather.

### (b) `Enabled` short-circuit — gate fail-open

`eligibility.go:64`:
```go
if event.ParticipationRequirements == nil || !event.ParticipationRequirements.Enabled {
    return &EligibilityResult{Eligible: true, ...}   // ← thoát sớm
}
```
Techspec §6 cắm check `StaffRequired` **sau** dòng này. Marketing bật switch "Chỉ dành cho nhân viên" nhưng quên bật master toggle `Enabled` → **mở cho toàn bộ creator ngoài**.

Chuẩn ngành với mọi cơ chế phân quyền: **fail-closed**. Điều kiện bảo vệ tiền không được phụ thuộc vào một toggle thứ hai mà người vận hành dễ quên.

### Thay đổi yêu cầu

Sửa **FR-011**, thêm 3 dòng vào phần Quy tắc:
- `StaffRequired` / `AllowedSegments` được đánh giá **độc lập với `ParticipationRequirements.Enabled`**. Bật một trong hai điều kiện này là đủ để gate hoạt động.
- Điều kiện được kiểm tra ở **mỗi lần nộp bài**, không chỉ lần join đầu tiên (theo TCB `content.go:105-120`).
- Không grandfather: người đã join trước khi bật điều kiện, nếu không thoả, bị chặn từ bài tiếp theo.

Thêm 3 AC:
- [ ] Event bật `staffRequired` nhưng `Enabled = false` → người ngoài **vẫn bị chặn**
- [ ] User join khi campaign còn mở, admin bật `staffRequired` sau → user đó **không nộp được bài tiếp theo**
- [ ] Có test khẳng định gate nằm trên đường nộp bài, không nằm sau nhánh "đã join"

---

## A2. 🔴 P0 — `user-segments` không có tenant discriminator, nhưng nhóm nhân viên cưỡi lên nó

**Sửa theo: CHUẨN NGÀNH (multi-tenant pool model)**

`internal/model/mg/user_segment.go:16` — `UserSegmentRaw{User, Segment, CreatedAt, CreatedBy}`. **Không có `partner`.** (`SegmentRaw.Partner` có, nhưng `omitempty` — tồn tại segment global legacy, xem `AssignPartnerWithNonExistsPartnerForStaff`.)

### Hậu quả 1 — báo cáo gán nhầm nhóm, lộ tên nhóm partner khác

Techspec §7, pipeline thống kê FR-014:
```go
{"$lookup": {"from": "user-segments", "localField": "user",
             "foreignField": "user", "as": "us"}},
{"$addFields": {"segmentId": {"$arrayElemAt": ["$us.segment", 0]}}},
```
Lookup **chỉ theo `user`**, rồi lấy phần tử **đầu tiên**. Một người vừa là NV Parasola vừa nằm trong segment marketing của VNPay → báo cáo Parasola gán họ vào nhóm của VNPay, và **tên nhóm của partner khác hiện lên trong báo cáo Parasola**. Vừa sai số vừa rò rỉ xuyên tenant.

### Hậu quả 2 — admin partner khác xoá được nhóm nhân viên Parasola

`pkg/admin/service/user_segment.go:110` — `Delete` xoá theo `{_id: {$in: ids}}`, **không gọi `IsAllowPartner`** (trong khi `Add` ở cùng file thì có gọi). Lỗi sẵn có, nhưng tính năng này biến nó từ "sai dữ liệu marketing" thành "hỏng gate tiền + sai báo cáo".

### Vì sao là chuẩn ngành, không phải ý kiến

Ambassador đang ở **pool model** (shared DB, tenant discriminator). Nguyên tắc bất di bất dịch của mô hình này: **mọi bảng tenant-scoped phải mang tenant id, và filter phải fail-closed ở tầng dưới** (RLS hoặc repository guard) — không dựa vào kỷ luật viết query, vì một `WHERE` quên là một lần rò dữ liệu.

Tham chiếu: [AWS SaaS multi-tenant — pool/silo & tenant isolation](https://hidekazu-konishi.com/entry/aws_saas_multi_tenant_architecture_guide.html), [RLS as defense-in-depth](https://dzone.com/articles/multi-tenant-data-isolation-row-level-security).

### Thay đổi yêu cầu

**FR mới (đề xuất FR-002b), Must Have, là prerequisite của FR-011 và FR-014:**
- Thêm `partner` vào `user-segments` + backfill từ `segments.partner`
- Mọi `$lookup` / query trên `user-segments` **bắt buộc** kèm điều kiện partner
- `UserSegment.Delete` phải kiểm `IsAllowPartner` như `Add`
- Bỏ `$arrayElemAt[0]` — một user có thể thuộc nhiều nhóm; phải quyết định rõ quy tắc (đề xuất: nhóm sinh từ `staff_import` là duy nhất trong một partner, xem A3)

Bổ sung **NFR-003**: *"Không truy vấn nào trên `user-segments` được phép thiếu điều kiện partner."*

---

## A3. 🟠 P1 — Nhầm hai khái niệm: "segment marketing" ≠ "org unit HR"

**Sửa theo: CHUẨN NGÀNH**

Chuẩn ngành tách rõ hai thứ:
- **Audience / segment** — marketer tự định nghĩa, động, *không authoritative*, ai có quyền admin cũng sửa được
- **Org group / department** — nguồn HR, *authoritative*, dùng để **gate quyền** (trong SCIM/HRIS đây là `Group` đồng bộ từ IdP, không gõ tay)

PRD gộp cả hai vào `Segment`. Hệ quả: một người có quyền admin thêm tay 1 user vào segment *"Chi nhánh Hà Nội"* → user đó **qua được gate campaign nhân viên mà chưa từng nhập mã nào**. Gate đang tin vào một bảng ai cũng ghi được.

### Thay đổi yêu cầu

Sửa **FR-004** + **FR-011**:
- Segment sinh từ import mã mang `source: "staff_import"`; admin UI **không cho thêm/xoá thành viên thủ công** trên loại segment này (chỉ đổi qua import hoặc FR-009)
- **`AllowedSegments` luôn AND với `IsStaff`** khi segment thuộc loại `staff_import` — không phụ thuộc admin có bật cả hai switch hay không

AC bổ sung:
- [ ] Thêm tay user vào segment `staff_import` → **bị từ chối**
- [ ] User nằm trong segment `staff_import` nhưng `statusStaff != employee` → **không qua gate**

---

## A4. 🟠 P1 — Audit không tenant-scoped, không dành cho end-user — mâu thuẫn trực tiếp NFR-002

**Sửa theo: CHUẨN NGÀNH**

`internal/model/mg/audit.go:16`:
```go
type AuditRaw struct {
    ID, TargetId primitive.ObjectID
    Data     interface{}
    Message  string
    ActionBy primitive.ObjectID `bson:"staff"`   // ← ngữ nghĩa STAFF
    BatchID  *primitive.ObjectID
}
```
Không có `partner`, không có `actorType`. `internal/service/audit.go` — `CreatePayload(targetID, staffID, ...)` cũng mang ngữ nghĩa staff.

`pkg/admin/router/audit.go`:
```go
g = e.Group("/audits", a.RequiredLogin)      // ← KHÔNG có a.IsAdmin
```
và `GetList` chỉ filter `targetId` + `staff`, **không filter partner**.

FR-016 yêu cầu ghi *"mã đã thử"* vào audit → **mã nhân viên Parasola đọc được bởi admin partner khác**. Phá thẳng NFR-002 *"Admin chỉ thao tác được trên mã của partner mình quản lý"*.

Ngoài ra: mã nhân viên là dữ liệu nhân sự. Ghi mã thô vào log vi phạm nguyên tắc data minimisation.

### Thay đổi yêu cầu

Sửa **FR-016** + **NFR-002**:
- `AuditRaw` bổ sung `partner` (bắt buộc với mọi sự kiện của tính năng này) và `actorType: "user" | "staff"`
- `GET /audits` bổ sung `a.IsAdmin` và **scoping theo partner của staff đang đăng nhập**
- **Không ghi mã thô**. Sự kiện "nhập mã sai" chỉ ghi 4 ký tự cuối hoặc hash; sự kiện "xác nhận thành công" ghi tham chiếu `manageCodeId`, không ghi chuỗi mã

AC bổ sung:
- [ ] Admin partner A gọi `GET /audits` → **không thấy** bản ghi của partner B
- [ ] Không có response/log nào chứa mã nhân viên ở dạng thô

---

## A5. 🟠 P1 — Đóng băng phân loại nhân viên khi đối soát (thay cho tranh cãi A/B ở FR-014)

**Sửa theo: CHUẨN NGÀNH — và đây là chỗ TCB có máy móc nhưng chưa nối dây**

### TCB xác nhận số này dùng để ra tiền

PRD dashboard TCB (`t-fluencers/dashboard-wiki-and-techcomer/prd.md:44`):
> *"**P2. Ops / Finance** — dùng số từ dashboard để đối chiếu chi phí quảng cáo và **đối soát**. Cần số chính xác, không bao gồm bài đăng đã hủy."*

Breakdown nhân viên (`staffCash`) nằm ngay trên dashboard đó.

### TCB có snapshot bất biến — nhưng không phủ chiều nhân viên

SRS TCB *"Snapshot đối soát (20A)"*: `content_snapshot` ghi view/like/comment/share/hashtags, **immutable** (BR-SS.1), *"bằng chứng cuối cùng gửi đến Creator khi công bố kết quả đối soát"*.

**Nhưng snapshot không ghi `statusStaff`, không ghi segment.** Breakdown staff/guest vẫn `$lookup` live (`creator_analytics.go:409`).

→ Ở TCB hôm nay: **tổng tiền đã đóng băng, nhưng "bao nhiêu phần thuộc nhân viên" thì vẫn trôi.** Đây chính xác là rủi ro FR-014 mô tả, và TCB không phải tiền lệ để bám — TCB đang mắc lỗi đó.

### Giải pháp rẻ, và né được đúng lý do PRD loại phương án B

PRD loại phương án B vì *"thêm field vào content, và không xử lý được dữ liệu đã có trước khi tính năng ra đời"*. Lý do này **không áp dụng** nếu đóng băng ở tầng đối soát:

Ambassador **không có** `reconciliation_snapshot` như TCB, nhưng **có** `internal/model/mg/reconciliation_item.go` đã đóng băng `User` + `TotalCash` + metrics per user. `ReconciliationItem` là **bản ghi sinh mới tại thời điểm chốt kỳ** — không có dữ liệu cũ để lo.

### Thay đổi yêu cầu

Sửa **FR-014**, thay phần "Phân loại theo trạng thái hiện tại, không snapshot" thành **hai chế độ tách bạch**:

| Loại báo cáo | Nguồn phân loại | Đặc tính |
|---|---|---|
| **Báo cáo vận hành** (xem hằng ngày trên admin) | `statusStaff` hiện tại (phương án A cũ) | Số kỳ cũ có thể đổi — **giữ ghi chú bắt buộc như PRD đã viết** |
| **Báo cáo đối soát** (ra tiền) | `isStaff` + `segment` **ghi vào `ReconciliationItem` tại thời điểm tạo** | Bất biến, không đổi khi có người xác nhận muộn |

AC bổ sung:
- [ ] `ReconciliationItem` lưu `isStaff` + `segment` tại thời điểm tạo
- [ ] Nhân viên xác nhận muộn → báo cáo vận hành đổi, **báo cáo đối soát kỳ đã chốt không đổi**
- [ ] Hai loại báo cáo ghi rõ nhãn loại nào ngay trên đầu bảng và trên file export

> ⚠️ Vẫn cần Parasola xác nhận: breakdown **theo nhóm** có dùng để trả tiền không, hay chỉ để xem. Nếu chỉ để xem, mục này hạ xuống Should Have.

---

## A6. 🟡 P2 — Trang `/manage-code` phải bắt buộc chọn partner

**Sửa theo: CHUẨN NGÀNH**

`internal/model/mg/staff.go` — `StaffRaw.Partner` là **đơn trị**, và:
```go
func (s StaffInfo) IsPermissionAllPartner() bool {
    return s.IsRoot || s.Partner.IsZero()      // ← partner RỖNG = thấy TẤT CẢ
}
```
Admin chưa gắn partner (dữ liệu cũ, hoặc tạo thiếu) tự động thành super-admin xuyên tenant. Với dữ liệu nhân sự thì mặc định này sai hướng.

**Thay đổi yêu cầu** — bổ sung vào FR-003:
- `/manage-code` **bắt buộc chọn một partner cụ thể**; không có chế độ "tất cả partner" cho danh sách mã nhân viên
- Import/export/xoá đều yêu cầu partner tường minh trong request, không suy ra từ session

---

## A7. 🟡 P2 — Hai việc nhỏ

**a) Bộ lọc phải là multi-select.** FR-013 đang ghi filter `statusStaff` dạng đơn trị *("Tất cả / Nhân viên / Không phải / Chưa xác nhận")*. Theo quy ước áp dụng toàn bộ sản phẩm: **mọi bộ lọc là multi-select** (BE `$in`, URL dạng CSV). `segment` PRD đã ghi chọn nhiều — làm `statusStaff` giống vậy.

**b) Gỡ hai tham chiếu chết ở đầu PRD.**
- `handbook.diso.vn/wiki/admin/nhan-vien/03-quan-ly-ma-nhan-vien` — trang **rỗng hoàn toàn**: `status: skeleton`, mọi mục là *"🚧 TODO: Nội dung đang được viết"*
- `handbook.diso.vn/srs/admin-portal/14-code` — mô tả **một thứ khác**: mã tham gia thử thách gán theo event (`Thử thách: Ref (Event), bắt buộc`), không phải mã nhân viên theo partner. Và AC-30.5 nói *"mã chuyển trạng thái USED"* — hành vi **không tồn tại trong code TCB**

Để nguyên thì người đọc sau tưởng đã có căn cứ nghiệp vụ. Gỡ, hoặc ghi rõ "chưa có nội dung".

---

## Tổng hợp Phần A

| # | Vấn đề | Mức | Sửa theo | FR ảnh hưởng |
|---|---|---|---|---|
| A1 | Gate campaign fail-open + chỉ chạy lúc join | 🔴 P0 | TCB (a) + chuẩn ngành (b) | FR-011 |
| A2 | `user-segments` thiếu tenant discriminator | 🔴 P0 | Chuẩn ngành | FR mới 002b, chặn FR-011/014 |
| A3 | Segment marketing ≠ org unit HR | 🟠 P1 | Chuẩn ngành | FR-004, FR-011 |
| A4 | Audit không tenant-scoped, ghi mã thô | 🟠 P1 | Chuẩn ngành | FR-016, NFR-002 |
| A5 | Phân loại nhân viên không đóng băng khi đối soát | 🟠 P1 | Chuẩn ngành (TCB sai) | FR-014 |
| A6 | `/manage-code` không bắt buộc partner | 🟡 P2 | Chuẩn ngành | FR-003 |
| A7 | Filter đơn trị + 2 tham chiếu chết | 🟡 P2 | Quy ước nội bộ | FR-013, §Overview |

---

# PHẦN B — BỔ SUNG VÀO OUT OF SCOPE

Năm mục dưới đây **TCB cũng chưa có**. Không có tiền lệ để bám, không nên gánh trong phase này. Nhưng phải ghi vào §10 Out of Scope **kèm rủi ro tồn dư và điều kiện kích hoạt** — để lần sau không ai tưởng là đã làm.

## B1. Vòng đời nhân viên nghỉ việc — đồng bộ và thu hồi hàng loạt

**TCB có không:** ❌ Không có gì.
- Chỉ **2 nơi** ghi `statusStaff` trong toàn repo TCB: `migration.go:600` (backfill, luôn set `employee`) và `user.go:253` (user tự confirm). **Không có endpoint admin nào đổi/gỡ.**
- `ManageCodeRaw` của TCB không có `expiredAt`, `revokedAt`, `status`
- grep `nghỉ việc|offboard|thôi việc|thu hồi mã` trong `docs/` + `plans/` + `handbook/` TCB: **0 kết quả**

**Ghi vào Out of Scope:**
> Đồng bộ danh sách nhân viên theo kỳ (reconcile snapshot), thu hồi nhãn hàng loạt khi nhân viên nghỉ việc, tích hợp HRIS/SCIM. **TCB cũng không có.** Phase 1 chỉ có đường gỡ nhãn thủ công từng người (FR-009 phía Admin).

**Rủi ro tồn dư — phải ghi kèm:**
TCB "không cần" offboarding một cách tình cờ: họ **cũng không set `isUsed`**, nên mã vốn đã chuyền tay được, nhãn vốn đã không đáng tin. **Ambassador chọn 1 mã 1 người** → nhãn dính vĩnh viễn vào đúng một người → nhân viên nghỉ việc **vẫn ăn campaign nội bộ** cho tới khi Ops gỡ tay. Chọn thiết kế chặt hơn thì kèm nghĩa vụ mới.

Thêm nữa: từ **01/01/2026**, NĐ 13/2023 hết hiệu lực, thay bằng Luật Bảo vệ dữ liệu cá nhân 2025 + NĐ 356/2025 — người rời đi có quyền yêu cầu xoá dữ liệu. FR-009 (admin gỡ nhãn, có lý do, ghi log) là mức tối thiểu để đáp ứng; **phải giữ trong scope, không hạ xuống Should Have**.

**Điều kiện kích hoạt phase sau:** số nhân viên Parasola vượt ~1.000, hoặc có kỳ đối soát đầu tiên phát hiện người đã nghỉ vẫn nhận thưởng.

---

## B2. Xác thực bằng email tên miền công ty / SSO / SCIM

**TCB có không:** ❌ Không. grep `emailDomain|corporate email|hasSuffix.*email` toàn backend TCB: **rỗng**. TCB chỉ dùng mã.

**Lưu ý khi ghi:** bảng đánh giá phương án ở §2 PRD hiện cân A (tự do) / B (regex) / C (import mã) / D (SSO+HR API) — **thiếu phương án trung gian chuẩn ngành: xác thực bằng email tên miền công ty + OTP**. Rẻ hơn SSO nhiều bậc, mạnh hơn mã dùng chung nhiều bậc (mã là bearer token viết trên giấy, chuyền tay được).

**Không suy ra được từ TCB:** TCB là ngân hàng, gần như 100% CBNV có email công ty, mà vẫn chọn mã — nhiều khả năng vì không muốn đụng AD/HR của TCB, chứ không phải vì email không dùng được. Parasola (bán lẻ, store staff) là bối cảnh khác hẳn.

**Ghi vào Out of Scope:**
> Xác thực bằng email tên miền công ty + OTP, SSO, SCIM/HRIS. **TCB cũng không có.** Phase 1 dùng mã import sẵn (phương án C).

**Bổ sung vào §2 bảng đánh giá phương án — một dòng, để người đọc biết đã cân nhắc:**
> | **B'. Xác thực email tên miền công ty + OTP** | ⏸️ Hoãn. Mạnh hơn mã dùng chung, rẻ hơn SSO — nhưng phụ thuộc việc Parasola có cấp email công ty cho toàn bộ nhân viên (kể cả nhân sự cửa hàng) hay không. Chưa xác nhận được. |

**Điều kiện kích hoạt:** Parasola xác nhận ≥90% nhân viên có email tên miền công ty.

---

## B3. Nghĩa vụ công bố (disclosure) cho content của nhân viên

**TCB có không:** ❌ Không. grep `disclos|công bố|tài trợ|#ad` trong TCB — không có gì liên quan tới nghĩa vụ công bố của nhân viên.

**Nhưng hạ tầng đã sẵn:** checklist đối soát TCB đã có tiêu chí `hashtag_present` (SRS 20A phần 3) — máy móc "bắt buộc hashtag + kiểm tra tự động + lưu bằng chứng" đã chạy production. Nối dây, không phải xây mới.

**Vì sao đáng ghi ra thay vì im lặng:**
- [FTC 16 CFR §255.5](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5) Example 8 nói thẳng: nhân viên quảng bá sản phẩm công ty mình **phải công bố quan hệ**; và **employer có nghĩa vụ train + monitor** để giới hạn trách nhiệm của chính mình
- Việt Nam: [Luật 75/2025/QH15](https://thuvienphapluat.vn/phap-luat-doanh-nghiep/bai-viet/luat-quang-cao-2025-sua-doi-co-hieu-luc-tu-01-01-2026-da-duoc-thong-qua-ngay-16-6-2025-12818.html) sửa Luật Quảng cáo, **hiệu lực 01/01/2026**, buộc người chuyển tải sản phẩm quảng cáo *"thông báo về việc quảng cáo ngay trước và trong khi thực hiện"*

Hệ thống **đã biết ai là nhân viên** thì việc ép hashtag disclosure cho nhóm nhân viên gần như miễn phí — và biến tính năng từ "công cụ báo cáo nội bộ" thành lợi thế tuân thủ bán được cho cả 12 partner còn lại.

**Ghi vào Out of Scope:**
> Ép hashtag/disclosure bắt buộc riêng cho content của nhân viên, và kiểm tra tự động khi đối soát. **TCB cũng không có** (dù đã có hạ tầng `hashtag_present`). Phase 1 không làm.

**Điều kiện kích hoạt:** Parasola hoặc pháp chế AT yêu cầu; hoặc khi mở tính năng cho partner thứ hai — thời điểm tự nhiên để làm một lần dùng chung.

---

## B4. Snapshot đối soát cấp content

**TCB có không:** ✅ TCB **có** (`content_snapshot`, SRS 20A) — nhưng **Ambassador chưa có**. Ambassador chỉ có `reconciliation_item` (đóng băng per-user, không per-content).

**Ghi vào Out of Scope:**
> Dựng cơ chế snapshot bất biến cấp content như TCB (`daily_crawl` / `post_expiry_crawl` / `makeup_crawl`). Ngoài phạm vi tính năng mã nhân viên. A5 chỉ bổ sung `isStaff` + `segment` vào `reconciliation_item` đã có.

**Rủi ro tồn dư:** khi tranh chấp thưởng, Ambassador chỉ truy được tới mức `reconciliation_item`, không có chuỗi lịch sử view theo ngày như TCB.

---

## B5. Phân quyền xem thống kê theo nhóm (trưởng nhóm chỉ xem nhóm mình)

**TCB có không:** ❌ Không. TCB chỉ có filter `staff/guest/custom` toàn dashboard, không phân quyền theo nhóm.

PRD **đã có** mục này ở §10 — chỉ cần bổ sung ghi chú "TCB cũng không có" để lần sau không ai đi tìm bản tham chiếu.

---

## Tổng hợp Phần B

| # | Hạng mục | TCB | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|---|---|
| B1 | Vòng đời nghỉ việc / thu hồi hàng loạt | ❌ | **Cao** — 1 mã 1 người làm rủi ro này nặng hơn TCB | >1.000 NV, hoặc kỳ đối soát đầu phát hiện sai |
| B2 | Email tên miền / SSO / SCIM | ❌ | Trung bình — mã chuyền tay được | ≥90% NV có email công ty |
| B3 | Disclosure cho content nhân viên | ❌ (có hạ tầng) | Trung bình — rủi ro pháp lý từ 01/01/2026 | Pháp chế yêu cầu, hoặc mở partner thứ 2 |
| B4 | Snapshot đối soát cấp content | ✅ TCB có, Ambassador không | Thấp | Có tranh chấp thưởng cần truy vết theo ngày |
| B5 | Phân quyền xem thống kê theo nhóm | ❌ | Thấp | Parasola yêu cầu |

---

# Việc cần làm tiếp

1. **Cập nhật PRD lên v1.4** theo Phần A (7 mục) và Phần B (bổ sung 4 mục vào §10, thêm 1 dòng vào bảng đánh giá phương án §2).
2. **Cập nhật techspec §6** — gate phải nằm trên đường nộp bài và độc lập với `Enabled` (A1). Đây là thay đổi kiến trúc, không phải sửa chữ.
3. **Đưa A2 lên trước** trong thứ tự triển khai (techspec §13) — FR-011 và FR-014 xây trên `user-segments`, sửa sau thì phải làm lại.
4. **Hỏi Parasola 1 câu duy nhất còn treo:** breakdown theo nhóm có dùng để trả tiền không? (quyết định A5 là Must hay Should)

---

## Phụ lục — Bảng đối chiếu multi-tenant

| Chiều | TCB | Ambassador phải làm | Trạng thái PRD |
|---|---|---|---|
| Identity | 1 partner, user ≈ CBNV TCB | user global (`UserRaw.Partners[]`), thuộc tính trên edge `user-partners` | ✅ đúng |
| Feature flag | ENV toàn cục | `PartnerOpts` theo partner | ✅ đúng |
| Namespace mã | unique global | unique `{partner, code}` | ✅ đúng |
| Gate campaign | trong luồng nộp bài, mỗi lần | Ambassador đặt trong `JoinEvent` — join-time only + fail-open | ❌ A1 |
| Nhóm | không có | `user-segments` **thiếu tenant id** | ❌ A2 |
| Audit | không có | bảng có nhưng không tenant-safe, thiếu `IsAdmin` | ❌ A4 |
| Đóng băng khi đối soát | có snapshot nhưng **không phủ chiều nhân viên** | ghi `isStaff`+`segment` vào `reconciliation_item` | ❌ A5 |
| Admin RBAC | 1 tenant | `StaffRaw.Partner` đơn trị; partner rỗng = thấy tất cả | ⚠️ A6 |
| Frontend | 1 FE | **14 codebase fork** (220–324 file mỗi folder) | ⚠️ chấp nhận cho phase 1 — nên ghi nợ: partner thứ 2 = chép tay lần nữa |
