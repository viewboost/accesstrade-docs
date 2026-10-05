# PRD v2: Phân quyền chức năng cấu hình được — gỡ phụ thuộc vào Admin Root

**Phiên bản:** 2.1 — ngày 2026-10-05 (bản 2: 2026-10-02)
**Thay cho:** `prd-phan-quyen-van-hanh-2026-09-25.md` (bản 30/9). Bản cũ giữ nguyên để đối chiếu.
**Đầu vào:** `feedback-review-2026-10-01.md` của Vinh Nguyễn (DISO), đo trên `AT-Core/ambassador` nhánh `develop`,
commit `0b411b25`. Số liệu trong bản này lấy theo lần đo đó, **trừ** các số ở mục 1.2 (đo 25/9, chưa đo lại —
có ghi rõ tại chỗ). Danh mục quyền và Phụ lục A đối chiếu router `develop` ngày 05/10.
**Trạng thái:** chờ biz chốt các quyết định ở mục 10, sau đó DISO estimate.

---

## 0a. Thay đổi bản 2.1 so với bản 2

| Vấn đề ở bản 2 | Sửa trong 2.1 | Mục |
|---|---|---|
| Mốc 0 phụ thuộc PQ-014 (Mốc 1): PQ-006 đọc phạm vi từ principal, PQ-007 cần nhiều ADV trong khi phạm vi đang nằm trong claim `partner` của JWT (một ADV) | Tách **PQ-014a — đọc phạm vi ADV từ DB** đưa lên Mốc 0. Phương án dự phòng ghi trong PQ-014a | PQ-014a, 8 |
| Mục 1.2 dùng số đo 25/9 nhưng đầu bản ghi "mọi số liệu theo 01/10" | Ghi rõ nguồn; số chính xác lấy từ PQ-015 | 1.2 |
| Danh mục quyền bỏ sót 10 nhóm endpoint, trong đó có **thưởng sự kiện** (tiền) | Bổ sung vào 2.3; thêm định nghĩa hành động | 2.3 |
| "Cộng thưởng cho creator" và "Thưởng thêm" bị gộp làm một | Tách lại thành hai việc, chờ biz xác nhận (Q10) | 1, PQ-008, Q10 |
| Ba vai trò hiện có chỉ ghi "như hôm nay" — biz không duyệt được | Thêm **Phụ lục A**: ma trận hiện trạng theo nhóm chức năng | Phụ lục A |
| Thiếu vai trò Manager vận hành | Thêm cột vào 2.4 | 2.4 |
| `staff.edit` chưa định nghĩa; chưa nói về tạo nhân sự kiểu cũ | Định nghĩa trong 2.3 và PQ-011 | 2.3, PQ-011 |
| Chưa ghi "một vai trò áp cho mọi ADV" | Thêm vào ngoài phạm vi | 4.2 |
| Màn Vai trò thiếu ràng buộc dữ liệu | Tên không trùng; ai thấy danh sách vai trò | PQ-004 |

## 0. Thay đổi bản 2 so với bản 30/9

| Feedback | Thay đổi trong v2 | Mục |
|---|---|---|
| A1 — root tạm tồn tại hết Mốc 1 | Thêm **Mốc 0: gỡ root tạm** trên vai trò Admin hiện có, không sửa cổng. Cần biz đồng ý phần thừa quyền | 8, Q1 |
| B2 — phạm vi ADV đọc từ JWT | Giả định "mọi cổng đọc DB" bỏ. Thêm **PQ-014: principal nạp mỗi request**, token chỉ giữ `_id` | PQ-014 |
| B3 — luật ADV thiếu trường hợp | Phạm vi có hai dạng `all` / `list`; khai báo tường minh bản ghi dùng chung và bản ghi nhiều ADV | 2.2, PQ-006 |
| B1 — số đo lệch | Sửa: 60 endpoint chỉ cần đăng nhập (không phải 42); **4 luật** phạm vi ADV, khoảng 95 chỗ (không phải 2 luật, 75 chỗ); 263 route | 1.1, 1.3 |
| A2 — thiếu quyền duyệt creator | Thêm `creator.approve`, `partner_member.approve` | 2.3 |
| A3 — khoá root mâu thuẫn PQ-005 | Tag và Cấu hình chung **không khoá root** nữa. Thêm danh sách **đổi hành vi có chủ đích** | 2.3, PQ-005 |
| A4 — root có hạn dùng thì tự khoá | Root **không** bị áp hạn dùng; thêm quy trình break-glass và cảnh báo mỗi lần root đăng nhập | PQ-013 |
| A6 — nghiệm thu | PQ-013 đo bằng lịch sử đăng nhập; thêm nghiệm thu Kỹ thuật hỗ trợ; "tắt tài khoản có hiệu lực ngay" ghi là đã có | PQ-008, PQ-009, PQ-013 |
| B4 — gieo vai trò | Gieo bằng **migration chạy một lần**, không qua `GenerateRole()`; trường quyền mới, không tái dùng `scopes` | PQ-005 |
| B5 — external API | Đưa ra ngoài phạm vi, ticket riêng; nhật ký ghi `client:<id>` | 4.2, PQ-012 |
| B6 — cổng và CI | Registry route tự ghi mã quyền; điều kiện phạm vi không thành mã quyền; ép `edit ⇒ view` ở backend; 403 vs 401 | PQ-002, PQ-004, NFR-005 |
| B7 — nhật ký | Index lọc; dòng cũ hiện "không rõ ADV" | PQ-012 |
| B8 — test ma trận trước | Thêm **PQ-015: chụp ma trận hiện tại làm mốc**, là việc đầu tiên của Mốc 1 | PQ-015 |

---

## 1. Mục tiêu

Rà soát lại toàn bộ danh sách quyền, sắp xếp lại thành các **nhóm quyền đúng với từng đội**, và cho phép
**cấu hình nhóm quyền trên màn hình** thay vì sửa mã nguồn mỗi lần một đội cần thêm việc.

| | Hôm nay | Sau đợt này |
|---|---|---|
| Đội vận hành | Admin không làm được năm việc, phải mượn root | Làm đủ năm việc **bằng tài khoản của chính mình**, trong ADV được giao |
| Tài khoản root | Có tài khoản root cấp tạm cho Manager đội vận hành | **Chỉ còn một** tài khoản root người dùng, do AT giữ |
| Đội kỹ thuật | Xin root mỗi lần cần hỗ trợ tra cứu | Có nhóm quyền chỉ đọc để hỗ trợ |
| Mời tài khoản qua email | Chỉ chọn được 1 trong 3 vai trò cứng, một ADV | Người được mời nhận **đúng nhóm quyền và ADV** ngay từ lời mời |
| Thêm/đổi quyền cho một đội | Sửa mã ở 3 tầng, phát hành bản mới | Root tick quyền trên màn **Vai trò & phân quyền**, có hiệu lực ngay |

Năm việc đội vận hành đang phải mượn root:

| Việc | Hôm nay |
|---|---|
| **Người dùng** — liên hệ creator bị sai video | `GET /users/:id`, `/users/:id/socials` nằm dưới `IsRoot` |
| **Cộng thưởng cho creator** | Cần biz xác nhận là việc nào (Q10). Nếu là **thưởng sự kiện** (`/event-reward/*`) thì hôm nay chỉ root làm được |
| **Thưởng thêm** — cộng thưởng | `/event-bonus/*`; Admin chưa gắn ADV bấm Lưu là "Không có quyền" |
| **File đối soát** — huỷ nội dung, huỷ mốc thưởng, tải file | Mở chi tiết là trắng; Huỷ và Tải trả lỗi |
| **File rút tiền** — xem và tải | Danh sách hiện, chi tiết trả lỗi |

Lý do gốc của bốn việc sau: Manager phụ trách **nhiều ADV**, nhưng bản ghi nhân sự chỉ chứa **một** ADV. Không
gắn ADV thì bị các phép so sánh thô chặn; gắn một ADV thì thiếu các ADV còn lại. Root là tài khoản duy nhất chạm
được nhiều ADV.

### 1.1 Vì sao phải bỏ phân quyền viết cứng

"Ai được làm gì" đang viết cứng ở **ba tầng**, phải sửa khớp nhau mỗi lần đổi:

| Tầng | Viết cứng ở đâu | Số đo (01/10) |
|---|---|---|
| Danh sách vai trò | `StaffRoleList` / `StaffRoleNameList` | 3 vai trò + cờ `isRoot` |
| Cổng API | `IsRoot`, `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole(...)` | 263 route; 87 lần gắn middleware; **60 endpoint** không có cổng vai trò nào, chỉ cần đăng nhập |
| Menu và nút | `admin/src/access.ts` so mã vai trò bằng mảng chuỗi | 8 khoá access |

Collection `roles` đã có trường `scopes` và API `GET /common/scopes`, nhưng danh mục là 4 nhóm giả
(`User`/`File`/`Staff`/`Content` × `edit/delete/view/create/full`) và **không cổng nào đọc**.

### 1.2 Quy mô rủi ro của tài khoản root

Root đi qua mọi route của admin, trong đó khoảng 26 endpoint không vai trò nào khác chạm tới: nhân sự, ADV, ban
người dùng, hợp đồng điện tử, eKYC, thưởng sự kiện, xác thực tài khoản. Cấp root cho một người chỉ cần năm việc vận
hành là cấp thừa các endpoint đó và thừa 13 ADV.

*Nguồn: đo ngày 25/9, chưa đo lại trên `0b411b25`. Số chính xác lấy từ bảng mốc PQ-015.*

### 1.3 Phạm vi ADV — bốn luật đang cùng tồn tại

| Luật | Đọc nhân sự từ | Nhân sự chưa gắn ADV | Vị trí |
|---|---|---|---|
| Hàm `StaffInfo` (`AssignPartnerForStaff` 29, `IsPermissionAllPartner` 28, `IsAllowPartner` 21) | **JWT** | Toàn quyền | `internal/model/mg/staff.go:91–118` |
| So sánh thô `Staff.Partner` với `doc.Partner` (≥ 15 chỗ) | DB | Bị chặn | nhiều nhất `service/reconciliation.go`, `service/event_bonus.go` |
| `StaffCanReachPartner` trong guard `*InScope` | DB | Toàn quyền | `router/routeauth/partner_scope.go:63` |
| `CanEditAppConfig` | DB | **Từ chối — đã fail-closed** | `internal/service/partner_app_config_access.go:11` |

Thêm một biến thể riêng cho tag: nhân sự ADV thấy cả tag của mình và tag dùng chung
(`AssignPartnerWithNonExistsPartnerForStaff`).

Hệ quả nhìn thấy được: **màn danh sách mở, mọi thao tác bên trong đóng**, và tất cả trả "Không có quyền". Phân
quyền chức năng trả lời "được làm gì"; bốn luật này trả lời "trên ADV nào". Làm cái thứ nhất mà không gom cái thứ
hai thì tick đủ quyền vẫn bị chặn.

### 1.4 Nền đã có sẵn

| Có sẵn | Dùng lại thế nào |
|---|---|
| Collection `roles` | Thành bản ghi nhóm quyền; tập quyền lưu ở **trường mới**, không tái dùng `scopes` |
| Mời nhân sự qua email (PR #253) | Chọn nhóm quyền, ADV, hạn dùng ngay trong lời mời |
| `resetToken` khi sửa hoặc tắt nhân sự (`service/staff.go:292`, `:360`) | Tắt tài khoản đã có hiệu lực ngay — giữ nguyên |
| `CanEditAppConfig` | Khuôn cho luật phạm vi ADV duy nhất |
| Khung `/migration/jobs` | Chạy migration gieo quyền một lần |
| Guard `*InScope` trả 403 | Khuôn cho mã lỗi thiếu quyền |

---

## 2. Mô hình phân quyền

### 2.1 Ba khái niệm

| Khái niệm | Trả lời câu | Nằm ở đâu | Ai đổi |
|---|---|---|---|
| **Quyền** | Làm được **việc gì** — *chức năng × hành động*, vd `reconciliation.cancel_item` | Danh mục khai trong mã | Đội kỹ thuật, khi thêm chức năng |
| **Vai trò** | Một đội làm được **những việc gì** — một tập quyền | DB, cấu hình trên màn | Root |
| **Phạm vi ADV** | Làm trên **ADV nào** | Bản ghi nhân sự | Root, hoặc người có `staff.invite` trong giới hạn của mình |

Một thao tác được phép khi và chỉ khi:

```
nhân sự đang hoạt động, chưa hết hạn
VÀ vai trò đang hoạt động, chứa mã quyền của thao tác
VÀ bản ghi nằm trong phạm vi ADV của nhân sự (luật ở 2.2)
```

**Root** đứng ngoài mô hình: qua mọi quyền, mọi ADV, không có hạn dùng.

### 2.2 Phạm vi ADV

Phạm vi của nhân sự có **hai dạng**:

| Dạng | Nghĩa | Ai đặt được |
|---|---|---|
| `all` | Mọi ADV, gồm cả ADV tạo sau này | **Chỉ root** |
| `list` | Danh sách ADV cụ thể. Rỗng = không chạm ADV nào | Root; người có `staff.invite` trong giới hạn của mình |

`all` vẫn fail-closed vì phải được đặt có chủ đích; không có đường nào để "chưa cấu hình" thành `all`.

Luật cho từng loại bản ghi:

| Bản ghi | Xem | Sửa / thao tác |
|---|---|---|
| Thuộc một ADV | ADV ∈ phạm vi | ADV ∈ phạm vi |
| **Thuộc nhiều ADV** (trường `partners` dạng mảng) | Có giao nhau với phạm vi | **Nằm trọn** trong phạm vi |
| **Dùng chung** (không ADV: tag, danh mục, kênh hỗ trợ chung…) | Mọi nhân sự có quyền `view` của chức năng đó | Chỉ nhân sự phạm vi `all` |

Bảng "xem / sửa" ở trên là đề xuất; biz chốt ở Q2.

Trường `type` (`vfdc` / `partner`) trên bản ghi nhân sự hiện không chỗ nào đọc. Sau khi có `all` / `list`, **bỏ
trường này** để không thành nguồn sự thật thứ năm.

### 2.3 Danh mục quyền — bản dự thảo

Theo menu admin, đối chiếu router `develop` ngày 05/10. DISO rà lại khi dựng registry route (PQ-002); mỗi endpoint
thuộc đúng một quyền.

**Hành động chuẩn.** Mỗi nhóm dùng các hành động sau; nhóm nào cần tách hơn thì ghi riêng trong bảng:

| Hành động | Gồm | Ví dụ endpoint |
|---|---|---|
| `view` | Xem danh sách, chi tiết, thống kê của nhóm | `GET /gifts`, `GET /gifts/:id` |
| `edit` | Tạo, sửa, nhân bản, **đổi trạng thái** (bật/tắt), xoá mềm | `POST`, `PUT`, `PATCH /:id/status`, `/:id/clone` |
| `import` / `export` | Nhập Excel hàng loạt / xuất và tải file | `/import-excel`, `/pre-sign` |
| `approve` | Duyệt hoặc từ chối một yêu cầu của bên khác | `/point-approval`, `/:id/completed`, `/:id/rejected` |
| Hành động riêng | Thao tác liên quan tiền hoặc không đảo ngược được — luôn tách khỏi `edit` | `reconciliation.cancel_item`, `event_reward.change_status` |

Xoá cứng không có mã quyền riêng; nếu endpoint xoá cứng tồn tại thì khoá root hoặc đổi thành xoá mềm.

| Nhóm (menu) | Quyền | Ghi chú |
|---|---|---|
| Nội dung | `content.view`, `content.moderate` | `/contents/*`. Ghim, gắn tag cảnh báo, cập nhật thống kê thuộc `moderate`. Các route cập nhật hàng loạt dữ liệu (`/update-status-data-contents`, `/update-warning-tags-content`) DISO phân loại: vận hành hay công cụ kỹ thuật (→ khoá root) |
| Luồng nội dung thủ công | `content_manual_flow.view`, `content_manual_flow.edit` | `/content-manual-flows` — hôm nay CTV và Admin |
| Người dùng | `user.view_contact` | Chi tiết, liên hệ, kênh MXH, nội dung đã đăng. Ghi nhật ký **lượt xem** (Q4) |
| | `creator.approve` | `POST /users/approval-creator/change-status` — hôm nay ai đăng nhập cũng gọi được |
| | `partner_member.approve` | `POST /users/approval-partner/change-status` — như trên |
| | ban, hợp đồng, eKYC, tạo người dùng | **Khoá root** |
| | `user.edit_partner_data` | `PUT /partners/users/wildrift` — sửa dữ liệu người dùng của một ADV; hôm nay ai đăng nhập cũng gọi được. DISO xác nhận còn dùng không; không dùng thì gỡ |
| Hồ sơ creator | `creator.view` | `GET /creator-profiles/*` |
| | `creator.edit` | `PATCH /:id/change-status`, `PUT /:id/update-stats`, điều kiện hồ sơ (`/conditions`) |
| Người dùng ADV | `user_partner.view`, `user_partner.edit_staff_status` | `PUT /user-partners/:id/staff-status` — đổi trạng thái nhân viên (CBNV) của user ADV |
| Thống kê, Dashboard | `statistic.view` | Gồm `/events/statistic`, `/staff-statistic`, `/chart`, `/report-statistic` |
| Sự kiện | `event.view`, `event.edit` | `edit` gồm yêu cầu, ngân sách, opshub, cấu hình và ghim **bảng xếp hạng** |
| Mẫu sự kiện | `event_schema.view`, `event_schema.edit` | `/event-schemas/*` — hôm nay ai đăng nhập cũng gọi được |
| **Thưởng sự kiện** | `event_reward.change_status`, `event_reward.delete` | `/event-reward/*` — **liên quan tiền**, hôm nay chỉ root. Có mở cho Vận hành không: Q10 |
| | huỷ thưởng sự kiện, chạy lại tính thưởng (`/events/reject-reward-event`, `/rerun-reward-event-by-cad`) | **Khoá root** — công cụ kỹ thuật |
| Thưởng thêm | `bonus.view`, `bonus.edit`, `bonus.import`, `bonus.cancel` | Liên quan tiền |
| Nhiệm vụ | `mission.view`, `mission.edit`, `mission.approve` | `approve` = duyệt điểm nhiệm vụ (`/point-approval`) |
| Quà | `gift.view`, `gift.edit` | Gồm lịch sử đổi quà |
| Phân khúc người dùng | `user_segment.view`, `user_segment.edit`, `user_segment.import` | `/user-segments/*`, tách khỏi `segment.*` |
| Thông báo admin | `notification.view`, `notification.edit`, `notification.approve` | `approve` = đánh dấu hoàn thành / từ chối (`/:id/completed`, `/:id/rejected`) |
| Đối soát | `reconciliation.view`, `reconciliation.cancel_item`, `reconciliation.change_status`, `reconciliation.export` | Liên quan tiền |
| Rút tiền | `transfer.view`, `transfer.export`, `transfer.change_status` | Liên quan tiền |
| Dữ liệu xuất | `export.view`, `export.download` | |
| Phân khúc, Danh mục | `segment.*`, `category.*` (`view` / `edit`) | |
| Mã | `code.view`, `code.edit`, `code.import` | `/manage-codes/import-excel` |
| Cấu hình ứng dụng, Tin tức, Bài viết, Affiliate | `app_config.*`, `news.*`, `article.*`, `affiliate.*` (`view` / `edit`) | Cấu hình ứng dụng thêm `app_config.publish` (xuất bản, khôi phục phiên bản) |
| Kênh hỗ trợ | `quick_action.view`, `quick_action.edit` | Hôm nay chỉ root và Cấu hình ứng dụng — **Admin không có** (Phụ lục A) |
| Danh sách ADV | — | `GET /partners`: **`public` cho mọi nhân sự đăng nhập**, tự lọc theo phạm vi — các màn đều cần cho ô chọn ADV |
| Danh sách người dùng của ADV | `creator.view` | `GET /partners/users` |
| **Tag** | `tag.view`, `tag.edit` | **Không khoá root** — Admin đang làm được (`router/tag.go:15`) |
| **Cấu hình chung** | `common_config.view`, `common_config.edit` | Gồm cả `/common-configs` (Admin) và `/common/configurations` (hôm nay ai cũng ghi được). Tag và cấu hình chung là bản ghi dùng chung: `edit` cần thêm phạm vi `all` |
| Nhật ký | `audit.view`, `login_history.view` | |
| Nhân sự | `staff.view` | Danh sách, chi tiết nhân sự trong phạm vi |
| | `staff.invite` | Mời, mời hàng loạt, gửi lại, thu hồi lời mời |
| | `staff.edit` | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản |
| | đặt lại mật khẩu cho người khác, tạo nhân sự kiểu cũ (đặt sẵn mật khẩu, `POST /staffs/register`) | **Khoá root.** Người dùng tự đặt lại qua "quên mật khẩu". Tạo kiểu cũ giữ cho root để dự phòng khi email lỗi |
| Vai trò & phân quyền, ADV, Xác thực tài khoản, `/migration/*` | — | **Khoá root** |

"Khoá root" = không có mã quyền để tick.

Ngoài các nhóm trên, mọi route `/migration/*`, `/migration/backfill-*`, `/common/update-event-daily`,
`/events/run-analytic-daily`, `/events/migrate-category-ead` là **công cụ kỹ thuật → đề xuất khoá root**. Route nào
trong số này hôm nay Admin đang gọi được thì đưa vào danh sách đổi hành vi có chủ đích (PQ-005).

Điều kiện kiểu "config_editor phải gắn ADV" (hiện nằm trong `HasAnyRole`, `IsConfigEditor`,
`IsAdminOrConfigEditor`) là điều kiện **phạm vi**, không thành mã quyền; nó được thay bằng luật "danh sách rỗng
thì từ chối" ở 2.2.

### 2.4 Vai trò mẫu

**Ba vai trò hiện có** (Admin, CTV, Cấu hình ứng dụng) được gieo **đúng bằng hành vi hôm nay**, trừ các mục trong
danh sách "đổi hành vi có chủ đích" (PQ-005). Hành vi hôm nay của từng vai trò, theo nhóm chức năng, ở
**Phụ lục A** — biz duyệt bảng đó. Ma trận chính xác ở mức endpoint lấy từ PQ-015.

**Ba vai trò mới** — điểm xuất phát, biz và AT chốt:

| Nhóm quyền | **Vận hành** | **Manager vận hành** | **Kỹ thuật hỗ trợ** |
|---|---|---|---|
| Nội dung | xem | xem | xem |
| Duyệt creator / partner | *Q3* | *Q3* | — |
| Người dùng — liên hệ | ✔ | ✔ | *Q5* |
| Hồ sơ creator | xem | xem | xem |
| Thưởng thêm | xem, sửa, import, huỷ | xem, sửa, import, huỷ | xem |
| Thưởng sự kiện | *Q10* | *Q10* | — |
| Đối soát | xem, huỷ mục, tải file | xem, huỷ mục, tải file | xem |
| Rút tiền | xem, tải file | xem, tải file | xem |
| Sự kiện, Nhiệm vụ, Quà | xem | xem | xem |
| Cấu hình ứng dụng, Tin tức, Bài viết, Kênh hỗ trợ | — | — | xem |
| Tag, Cấu hình chung | — | — | xem |
| Thống kê | xem | xem | xem |
| Nhật ký | xem | xem | xem |
| Nhân sự | — | xem, **mời**, sửa (theo ràng buộc PQ-011) | — |
| Đổi trạng thái chi tiền | — | — | — |
| **Phạm vi gợi ý** | `list` | `list` | `all` |

- **Manager vận hành** = Vận hành + quản lý nhân sự trong đội. Chỉ tạo khi Q6 đồng ý; nếu không, Manager dùng
  vai trò Vận hành và root mời người.
- **Kỹ thuật hỗ trợ**: **chỉ đọc**. Không có bất kỳ quyền ghi nào.
- Vai trò mới không lấy quyền nào ngoài danh mục 2.3; nhóm khoá root không vai trò nào nhận được.

---

## 3. Người dùng

**Root (AT)** — giữ tài khoản root người dùng duy nhất. Dựng nhóm quyền, mời nhân sự, đặt phạm vi `all`.

**Nhân viên vận hành biz** — người dùng chính. Liên hệ creator sai video, cộng thưởng, chốt đối soát, xử lý rút
tiền. Phụ trách một hoặc vài ADV.

**Manager biz** — đang giữ root tạm. Mốc 0: chuyển sang Admin gắn nhiều ADV. Mốc 2: vai trò Vận hành, có thể kèm
`staff.invite` để tự mời người trong đội (Q6).

**Đội kỹ thuật (AT và đối tác)** — dùng vai trò Kỹ thuật hỗ trợ, phạm vi `all`, chỉ đọc.

**CTV**, **Cấu hình ứng dụng** — không đổi hành vi, trừ việc mất các endpoint "chỉ cần đăng nhập" không thuộc
việc của mình (PQ-010).

**Hệ thống đối tác gọi external API** — ngoài phạm vi đợt này (4.2).

**Đội kỹ thuật đối tác (DISO)** — bên thực hiện.

---

## 4. Phạm vi

### 4.1 Trong phạm vi

- Gỡ root tạm sớm trên vai trò Admin hiện có (Mốc 0, nếu biz đồng ý)
- Test ma trận quyền hiện tại làm mốc so sánh
- Principal nạp từ DB mỗi request; token chỉ giữ `_id`
- Danh mục quyền chức năng; registry route kèm mã quyền; cổng `RequirePermission`
- Menu và nút theo danh sách quyền
- Màn **Vai trò & phân quyền**
- Gieo quyền cho ba vai trò hiện có bằng migration; gieo hai vai trò mẫu mới
- Một luật phạm vi ADV duy nhất, fail-closed, hai dạng `all` / `list`
- Lời mời chọn nhóm quyền, phạm vi, hạn dùng
- Nhật ký đủ người, hành động, ADV; ghi cả lượt xem liên hệ creator và mọi thay đổi vai trò
- Đóng 60 endpoint chỉ cần đăng nhập; CI kiểm ma trận
- Còn một root người dùng; quy trình break-glass; cảnh báo root đăng nhập

### 4.2 Ngoài phạm vi

- **External API** (`/api/admin/external-api`, 20 route, cổng `CheckKeyAuth`): một cặp key dùng chung mọi ADV;
  chữ ký không phủ body; không chống gửi lại trace-no. Đây là "root thứ hai" cho dòng tiền — **tách ticket riêng**,
  vì phải thống nhất cách ký với AT Core. Mục tiêu "một root" trong PRD này là root **người dùng**
- Gán quyền lẻ cho một người; nhiều vai trò trên một người
- **Vai trò khác nhau theo từng ADV.** Một nhân sự có đúng một vai trò, áp như nhau cho mọi ADV trong phạm vi.
  Không có trường hợp "Admin ở ADV A nhưng CTV ở ADV B"; cần vậy thì dùng hai tài khoản
- Phân quyền theo trường dữ liệu
- Tạo mã quyền mới từ màn hình
- Đổi thời hạn token 8 giờ
- Đổi quy trình nghiệp vụ đối soát, rút tiền, thưởng. Ai được bấm thì đổi; **bấm xong ra gì thì giữ nguyên**
- Phân quyền cho app creator và các site white-label

---

## 5. Yêu cầu chức năng

Sắp theo mốc ở mục 8. Mã PQ giữ như bản 30/9 để đối chiếu; mã mới từ PQ-014.

### Mốc 0 — Gỡ root tạm

#### PQ-014a — Đọc phạm vi ADV từ DB (phần đầu của PQ-014)

**Vì sao cần.** PQ-007 cho nhân sự gắn nhiều ADV, nhưng hôm nay phạm vi ADV đọc từ claim `partner` trong JWT — chỉ
chứa được một ADV. Không làm phần này thì Mốc 0 không chạy: màn danh sách vẫn đọc ADV cũ từ token.

**Yêu cầu**

- Middleware `Auth` đọc nhân sự từ DB và dựng `StaffInfo` từ đó (phạm vi `all` / `list`, `isRoot`), không từ claim
  `partner` / `isRoot` của token
- Ba hàm `StaffInfo` (`AssignPartnerForStaff`, `IsPermissionAllPartner`, `IsAllowPartner`) sửa **bên trong** để
  hiểu phạm vi `list` (lọc `$in`); 78 chỗ gọi giữ nguyên chữ ký, không phải sửa ở Mốc 0
- Cổng vai trò (`IsAdmin`…) giữ nguyên ở Mốc 0
- Phần còn lại của PQ-014 (gom thành một principal, token chỉ giữ `_id`, kiểm `active` / hạn dùng / `role.active`)
  làm ở Mốc 1, dựng tiếp trên phần này

**Phương án dự phòng** — nếu DISO estimate phần này quá lớn cho Mốc 0: ghi danh sách ADV vào token thay cho claim
`partner`, đổi phạm vi thì gọi `resetToken` (người dùng bị đăng xuất, như hôm nay). Khi đó nghiệm thu "không bị đăng
xuất" chuyển sang Mốc 1, và phần token phải sửa lại ở PQ-014.

**Nghiệm thu**

- [ ] Nhân sự `list` 3 ADV: màn danh sách và màn chi tiết đều thấy đúng 3 ADV
- [ ] Sửa phạm vi trực tiếp trong DB (không qua màn Nhân viên, không xoá token): lần gọi kế tiếp áp phạm vi mới

#### PQ-007 — Nhân sự phụ trách được nhiều ADV, phạm vi `all` / `list`

**Vì sao cần.** Đây là lý do thật khiến Manager phải mượn root. Bật cờ root còn xoá luôn ô ADV và ô vai trò, nên
không có "root của 2 ADV".

**Yêu cầu**

- Bản ghi nhân sự có phạm vi theo 2.2: `all` hoặc `list`
- Màn Nhân viên và màn mời chọn được nhiều ADV; chỉ root thấy lựa chọn `all`
- Chuyển dữ liệu:
  - Nhân sự đang gắn một ADV → `list` một phần tử
  - Nhân sự không gắn ADV, không phải root (đang được hiểu là toàn quyền) → `all`, **sau khi biz rà từng người**
    (Q7); ai không được xác nhận thì → `list` theo danh sách biz đưa
- Bỏ trường `type`

**Nghiệm thu**

- [ ] Tài khoản `list` 3 ADV thao tác được đúng 3; ADV thứ tư trả "ADV ngoài phạm vi"
- [ ] Tạo ADV mới: tài khoản `all` thấy ngay, tài khoản `list` không thấy
- [ ] Nhân sự không phải root không đặt được `all` cho ai, kể cả qua API
- [ ] Đối chiếu trước/sau từng tài khoản: không ai mất hay thừa ADV ngoài quyết định của biz

#### PQ-006 — Một luật phạm vi ADV duy nhất, fail-closed

**Vì sao cần.** Mục 1.3: bốn luật, khoảng 95 chỗ gọi, trả lời ngược nhau.

**Yêu cầu**

- Một hàm duy nhất, lấy `CanEditAppConfig` làm khuôn, cài đúng luật ở 2.2 (một ADV, nhiều ADV, dùng chung)
- Hàm đọc phạm vi từ DB: Mốc 0 qua `StaffInfo` dựng ở PQ-014a; từ Mốc 1 qua principal (PQ-014). Không đọc claim
  `partner` trong JWT
- Mốc 0: áp cho service của năm việc (đối soát, rút tiền, thưởng thêm, dữ liệu xuất, chi tiết người dùng)
- Mốc 1: thay nốt toàn bộ — `AssignPartnerForStaff`, `IsPermissionAllPartner`, `IsAllowPartner`,
  `StaffCanReachPartner`, `AssignPartnerWithNonExistsPartnerForStaff`, các so sánh thô (kể cả viết qua `.Hex()`
  hay biến trung gian)
- Danh sách và chi tiết dùng chung một luật

**Nghiệm thu**

- [ ] Nhân sự `list` rỗng: mọi màn liệt kê không trả bản ghi nào
- [ ] Mọi bản ghi thấy trong danh sách đều mở được chi tiết (nếu có quyền xem)
- [ ] Hết Mốc 1: `git grep` không còn năm hàm cũ và không còn so sánh `Staff.Partner` trong `pkg/admin/service`
- [ ] Root không đổi hành vi

#### PQ-003a — Mở chi tiết người dùng cho Admin (tạm thời, Mốc 0)

- `GET /users/:id` và `GET /users/:id/socials` chuyển từ `IsRoot` sang Admin, trong phạm vi ADV (PQ-006)
- Các thao tác ban, hợp đồng, eKYC, tạo người dùng giữ `IsRoot`
- Mỗi lượt mở chi tiết ghi nhật ký (PQ-012, mức tối thiểu)
- Ở Mốc 2, hai endpoint này chuyển sang quyền `user.view_contact`

#### PQ-013 — Thu hồi root tạm, còn một root người dùng

**Vì sao cần.** Đây là kết quả rủi ro của cả đợt.

**Yêu cầu**

- Manager đội vận hành chuyển sang tài khoản riêng (Mốc 0: Admin gắn nhiều ADV), tài khoản root tạm bị tắt
- **Root không bị áp hạn dùng** — một root duy nhất mà có hạn thì có thể tự khoá hệ thống
- **Break-glass** viết thành văn bản: script tạo hoặc khôi phục root chạy trực tiếp trên DB; ai được chạy; ghi
  lại ở đâu; sau khi dùng phải làm gì
- Mỗi lần root đăng nhập **báo về một kênh** (Slack/email do AT chỉ định)
- Màn Nhân viên hiện số tài khoản root; cảnh báo khi khác 1

**Nghiệm thu**

- [ ] Đếm nhân sự `isRoot = true` đang hoạt động trên production: **đúng 1**
- [ ] Lịch sử đăng nhập root trong 7 ngày liên tiếp sau Mốc 0: **0 lượt phục vụ vận hành** (mỗi lượt có cảnh báo
  và có lý do ghi lại)
- [ ] Chạy thử break-glass trên staging: khôi phục được root trong thời gian quy trình đề ra

### Mốc 1 — Nền phân quyền

#### PQ-015 — Chụp ma trận quyền hiện tại làm mốc

**Vì sao cần.** Không có mốc thì nghiệm thu "không ô nào đổi" ở PQ-005 không có gì để so. Đây cũng là đầu vào
estimate chính xác nhất.

**Yêu cầu**

- Bộ test gọi mọi route admin với mọi tổ hợp **(root, Admin, CTV, Cấu hình ứng dụng) × (chưa gắn ADV, gắn ADV
  đúng, gắn ADV khác)**, ghi kết quả cho phép / chặn
- Chạy trên `develop` **trước** mọi thay đổi ở Mốc 1, lưu kết quả vào repo làm bảng mốc
- Là việc **đầu tiên** của Mốc 1

**Nghiệm thu**

- [ ] Bảng mốc phủ đủ 263 route trừ external API, chạy lại được trong CI

#### PQ-014 — Principal nạp mỗi request

**Vì sao cần.** Vai trò hôm nay đọc từ DB, nhưng **phạm vi ADV đọc từ JWT** (claim `isRoot`, `partner`;
`router/routeauth/auth.go:201`, `:225`). Đổi ADV hôm nay có tác dụng chỉ vì `resetToken` đá người dùng ra đăng
nhập lại. Hạn dùng không có sự kiện nào xoá token đúng lúc. `Auth` không kiểm `active`; các cổng không kiểm
`role.active`.

**Yêu cầu**

- Dựng tiếp trên PQ-014a (Mốc 0 đã đưa phạm vi ADV về DB)
- Middleware `Auth` nạp **một principal** mỗi request: nhân sự, vai trò, tập quyền, phạm vi ADV, `active`, hạn
  dùng. Đặt vào context; mọi cổng và service đọc từ đó
- Token chỉ còn `_id` (và `exp`)
- Nhân sự `active = false`, quá hạn dùng, hoặc vai trò `active = false`: bị chặn ở `Auth`
- Gom số lần đọc DB: hôm nay 2–3 lần `FindById` mỗi request, sau đổi còn 1. Nếu thêm cache ngắn thì phải xoá khi
  nhân sự hoặc vai trò thay đổi

**Nghiệm thu**

- [ ] Bỏ một ADV khỏi phạm vi: thao tác kế tiếp vào ADV đó bị chặn, **người dùng không bị đăng xuất**
- [ ] Đặt hạn dùng vào 1 phút sau: hết phút đó thao tác kế tiếp bị chặn
- [ ] Không service nào còn đọc claim `partner` / `isRoot` từ token

#### PQ-001 — Danh mục quyền chức năng

- Một danh mục duy nhất trong mã: mã, nhãn tiếng Việt, nhóm, mô tả, cờ "liên quan tiền"
- Theo bản dự thảo 2.3
- `GET /common/scopes` trả danh mục mới, gom theo nhóm
- Quyền khoá root không có trong danh mục

**Nghiệm thu:** mọi menu (trừ nhóm khoá root) có ít nhất một quyền `view`; không còn mã kiểu `user_full`.

#### PQ-002 — Registry route và cổng `RequirePermission`

**Vì sao cần.** Echo không lưu middleware trong `e.Routes()`, nên không sinh được bảng endpoint → quyền từ mã nếu
mỗi route tự gắn middleware như hôm nay.

**Yêu cầu**

- Một lớp đăng ký route: mỗi route khai **đúng một** trong ba: mã quyền, `root`, hoặc `public`
- Cổng `RequirePermission(code)` đọc principal (PQ-014)
- Danh sách `public` cố định: đăng nhập, xác nhận và nhận lời mời, quên và đặt lại mật khẩu, `/staffs/me`
- Thay hết `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole`
- Bảng endpoint → quyền **sinh từ registry**, là tài liệu bàn giao
- CI duyệt `e.Routes()`: route không có trong registry và không thuộc `public` hay external API → đỏ

**Nghiệm thu**

- [ ] Bỏ một quyền khỏi vai trò: endpoint tương ứng bị chặn ở lần gọi kế tiếp
- [ ] `pkg/admin/router` không còn so mã vai trò
- [ ] Thêm route không khai trong registry: CI đỏ

#### PQ-003 — Menu và nút theo quyền

- `/staffs/me` trả danh sách mã quyền và phạm vi
- `access.ts`, `routes.ts` tính từ danh sách quyền; không còn chuỗi `'admin'`, `'collaborator'`,
  `'config_editor'`
- Nút thao tác ẩn khi thiếu quyền; trang đích là menu đầu tiên có quyền xem
- Ẩn/hiện chỉ để màn sạch; chặn thật ở PQ-002

**Nghiệm thu:** vai trò chỉ có `reconciliation.view` đăng nhập chỉ thấy Đối soát, không thấy nút Huỷ.

#### PQ-005 — Gieo quyền bằng migration, không đổi hành vi

**Yêu cầu**

- Tập quyền lưu ở **trường mới** trên bản ghi vai trò, chỉ chứa mã quyền. Trường `scopes` cũ không dùng, xoá ở
  Mốc 3
- Gieo bằng **migration chạy một lần, có đánh dấu phiên bản** qua khung `/migration/jobs`. Không sửa
  `GenerateRole()` để ghi đè lúc khởi động — làm vậy mỗi lần deploy sẽ xoá quyền root vừa tick
- Giữ nguyên `_id` và `code` của ba vai trò
- Tập quyền gieo cho ba vai trò = đúng bảng mốc PQ-015, **trừ** danh sách đổi hành vi có chủ đích dưới đây

**Danh sách đổi hành vi có chủ đích** (được duyệt, ma trận trước/sau cho phép khác ở các ô này):

| Thay đổi | Ai bị ảnh hưởng | Mốc | Lý do |
|---|---|---|---|
| Đóng 60 endpoint chỉ cần đăng nhập, gán quyền tối thiểu | CTV, Cấu hình ứng dụng mất các endpoint không thuộc việc của mình | 3 | PQ-010 |
| `/migration/*` khoá root | Mọi vai trò không phải root | 3 | Công cụ kỹ thuật |
| `PUT /common/configurations` cần `common_config.edit` + phạm vi `all` | Mọi vai trò không phải root đang ghi được | 3 | Ghi cấu hình xuyên ADV |
| Duyệt creator / partner cần quyền riêng | Tuỳ Q3 | 3 | Hôm nay ai đăng nhập cũng duyệt được |
| Thưởng thêm cần `bonus.*` | CTV, Cấu hình ứng dụng mất quyền tạo/import thưởng | 3 | Lỗ hổng chi tiền |
| Mẫu sự kiện cần `event_schema.*` | CTV, Cấu hình ứng dụng mất quyền sửa mẫu sự kiện | 3 | Hôm nay ai đăng nhập cũng sửa được |
| `PUT /partners/users/wildrift` cần `user.edit_partner_data` hoặc bị gỡ | Mọi vai trò không phải root | 3 | Ghi dữ liệu người dùng mà không kiểm vai trò |
| Nhật ký `/audits` cần `audit.view`, lọc theo phạm vi | CTV, Cấu hình ứng dụng; nhân sự ADV khác | 3 | PQ-012 |
| Công cụ kỹ thuật dưới `/events`, `/common` (2.3) khoá root | Theo kết quả phân loại của DISO | 3 | Không phải công cụ vận hành |
| Thưởng sự kiện mở cho Vận hành | Tuỳ Q10 | 2 | Một trong năm việc |
| Nhân sự không gắn ADV chuyển sang `all` hoặc `list` | Theo Q7 | 0 | PQ-007 |
| Chi tiết người dùng mở cho Admin | Admin | 0 | PQ-003a |
| Thiếu quyền trả 403 thay vì 401 | Mọi vai trò | 1 | NFR-005 |

Danh sách này là nguồn duy nhất; thay đổi ngoài danh sách là lỗi.

**Nghiệm thu**

- [ ] Ma trận sau Mốc 1 so với bảng mốc PQ-015: mọi ô khác đều nằm trong danh sách trên
- [ ] Deploy lại nhiều lần: quyền root đã tick trên màn không bị ghi đè

### Mốc 2 — Vận hành tự cấu hình

#### PQ-004 — Màn Vai trò & phân quyền

- Menu **Vai trò & phân quyền**, chỉ root
- Danh sách vai trò: tên, mô tả, số quyền, số nhân sự dùng, trạng thái
- Tạo, sửa, **nhân bản**, ngừng dùng; không xoá được vai trò đang có người dùng
- Tên vai trò **không trùng** (so không phân biệt hoa thường, bỏ dấu); `code` sinh tự động, không sửa được sau khi
  tạo. Ba vai trò hiện có và các vai trò mẫu không xoá được, chỉ sửa quyền
- Ngừng dùng một vai trò: phải chuyển hết nhân sự sang vai trò khác trước; vai trò ngừng dùng không xuất hiện ở ô
  chọn khi mời
- **Ai thấy danh sách vai trò:** root thấy tất cả. Người có `staff.invite` / `staff.edit` chỉ thấy, ở ô chọn vai trò,
  những vai trò có tập quyền nằm trong tập quyền của mình (PQ-011); không vào được màn này
- Bảng tick theo nhóm × hành động; quyền liên quan tiền được đánh dấu
- `edit` kéo theo `view` cùng nhóm — **ép ở backend khi lưu**, không chỉ ở giao diện
- Lưu hiện tóm tắt: thêm/bớt quyền nào, ảnh hưởng bao nhiêu người
- Mọi thay đổi ghi nhật ký

**Nghiệm thu**

- [ ] Root tạo vai trò, tick quyền, gán cho nhân sự: dùng được ngay, không cần kỹ thuật
- [ ] Gọi API lưu vai trò có `edit` mà thiếu `view`: backend tự thêm `view` hoặc từ chối
- [ ] Nhân sự không phải root không gọi được API sửa vai trò
- [ ] Tạo vai trò trùng tên (khác hoa thường hoặc dấu): bị từ chối
- [ ] Manager có `staff.invite` mở ô chọn vai trò: không thấy vai trò rộng hơn mình

#### PQ-008 — Vai trò Vận hành, Manager vận hành và Kỹ thuật hỗ trợ

| Việc | Quyền | Yêu cầu riêng | Nghiệm thu |
|---|---|---|---|
| Liên hệ creator | `user.view_contact` | Ban, hợp đồng, eKYC không hiện và API chặn | Gõ id creator ngoài phạm vi: bị chặn. Mỗi lượt xem có nhật ký |
| Cộng thưởng cho creator | Theo Q10: `event_reward.change_status` nếu là thưởng sự kiện | Mở được thì chỉ trong phạm vi ADV, ghi nhật ký | Chốt sau Q10 |
| Thưởng thêm | `bonus.edit`, `bonus.import`, `bonus.cancel` | Import có dòng ngoài phạm vi: dòng đó bị từ chối kèm lý do, dòng hợp lệ vẫn vào | File trộn hai ADV xử lý đúng |
| Đối soát | `reconciliation.cancel_item`, `reconciliation.export` | Đủ bốn tab chi tiết; huỷ kèm lý do; đổi trạng thái cả bản **không** thuộc vai trò này | Không tab nào trắng; thống kê cập nhật sau huỷ |
| Tải file | `reconciliation.export`, `transfer.export` | Yêu cầu xuất luôn mang ADV; không sinh được file trộn nhiều ADV từ tài khoản không phải `all` | Id file ngoài phạm vi: bị chặn |
| Rút tiền | `transfer.view`, `transfer.export` | Đổi trạng thái, từ chối lệnh rút **không** thuộc vai trò này | Đợt rút ngoài phạm vi: bị chặn |

**Manager vận hành — nghiệm thu riêng** (nếu Q6 đồng ý)

- [ ] Mời một người vào đội với vai trò Vận hành, trong ADV của mình: người đó dùng được ngay
- [ ] Mời với vai trò rộng hơn mình, hoặc ADV ngoài phạm vi: bị chặn

**Kỹ thuật hỗ trợ — nghiệm thu riêng**

- [ ] Gọi lần lượt mọi API ghi (theo registry): **tất cả bị chặn**
- [ ] Đọc được dữ liệu của mọi ADV, gồm ADV tạo sau khi gán vai trò

#### PQ-009 — Mời nhân sự đúng nhóm quyền, có hạn dùng

- Lời mời chọn: vai trò (từ DB), phạm vi, **ngày hết hiệu lực** (trống = không hạn)
- Hạn dùng áp cho mọi vai trò **trừ root**
- Quá hạn: không đăng nhập được; phiên đang mở bị chặn ở thao tác kế tiếp (nhờ PQ-014)
- Màn Nhân viên sửa được ngày này, lọc tài khoản sắp hết hạn
- Tắt tài khoản: **giữ nguyên** cơ chế `resetToken` hiện có — đã có hiệu lực ngay, không cần làm thêm

**Nghiệm thu**

- [ ] Mời người với vai trò Vận hành + 2 ADV: nhận lời mời xong dùng được đúng 2 ADV
- [ ] Đặt hạn vào hôm qua: không đăng nhập được, phiên đang mở bị chặn
- [ ] Không đặt được hạn dùng cho root

### Mốc 3 — Đóng rủi ro

#### PQ-010 — Không endpoint nào "chỉ cần đăng nhập"

**Vì sao cần.** 60 endpoint không có cổng vai trò: 40 migration/backfill, 5 thưởng thêm, 5 `/users` (gồm hai
endpoint duyệt), 5 `/partners`, 4 `/common`, 1 `/audits`.

**Yêu cầu**

- Mỗi endpoint được khai trong registry (PQ-002) với mã quyền hoặc `root`
- `/migration/*` và backfill: `root`, hoặc đưa ra khỏi API công khai
- Thay đổi hành vi đi theo danh sách ở PQ-005

**Nghiệm thu**

- [ ] Đăng nhập CTV, gọi 60 endpoint: chỉ qua những endpoint có trong vai trò CTV
- [ ] Không endpoint `/migration/*` nào gọi được bằng tài khoản không phải root

#### PQ-011 — Khoá root và chống tự nâng quyền

Giữ **chỉ root**: Vai trò & phân quyền; tạo/sửa/ngừng **ADV**; **ban / gỡ ban**; **hợp đồng**, **eKYC**, tạo
người dùng; Xác thực tài khoản; `/migration/*` và các công cụ kỹ thuật ở 2.3; huỷ / chạy lại tính thưởng sự kiện;
bật cờ root; đặt phạm vi `all`; đặt lại mật khẩu cho người khác; tạo nhân sự kiểu cũ (đặt sẵn mật khẩu).

Tag và Cấu hình chung **không** khoá root (khác bản 30/9): dùng `tag.edit`, `common_config.edit` kèm phạm vi
`all`.

**Quyền nhân sự** (định nghĩa ở 2.3):

| Quyền | Làm được | Không làm được |
|---|---|---|
| `staff.view` | Xem nhân sự có phạm vi giao với phạm vi của mình | Xem root |
| `staff.invite` | Mời, mời hàng loạt, gửi lại, thu hồi lời mời | Mời với vai trò hoặc ADV vượt quá mình |
| `staff.edit` | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản | Đặt lại mật khẩu người khác; sửa root; sửa chính mình |

Ràng buộc chung cho người có `staff.invite` / `staff.edit` (nếu Q6 đồng ý):

- Chỉ gán vai trò có tập quyền **nằm trong** tập quyền của mình
- Chỉ gán ADV **nằm trong** phạm vi của mình; không gán `all`
- Chỉ sửa nhân sự có phạm vi **nằm trọn** trong phạm vi của mình
- Không sửa tài khoản của chính mình, không sửa root

**Nghiệm thu**

- [ ] Không có mã quyền nào cho các nhóm khoá root
- [ ] Manager có `staff.invite` mời người với vai trò rộng hơn mình hoặc ADV ngoài phạm vi: bị chặn

#### PQ-012 — Nhật ký thao tác

`AuditRaw` hôm nay chỉ có `targetId`, `data`, `message`, `staff`, `createdAt`, `batchId`.

**Yêu cầu**

- Thêm trường **hành động** (danh mục có sẵn) và **ADV**
- Index phục vụ lọc theo người, hành động, ADV, thời gian
- Ghi: năm việc ở PQ-008, **lượt xem** chi tiết người dùng, mọi thay đổi vai trò / phạm vi / hạn dùng
- Dòng cũ không có ADV: hiển thị "không rõ ADV"; không bắt buộc backfill
- Đọc nhật ký cần `audit.view`, trong phạm vi ADV; root xem toàn bộ
- Khi external API được đưa vào phân quyền (ticket riêng), người thực hiện ghi dạng `client:<id>`
- Không xoá, không sửa nhật ký từ giao diện

**Nghiệm thu**

- [ ] Mỗi việc ở PQ-008 và mỗi lần sửa vai trò: đủ người, hành động, bản ghi, ADV, thời gian
- [ ] Nhân sự ADV A không đọc được nhật ký ADV B
- [ ] Lọc theo người, hành động, ADV ra đúng trên dữ liệu production cỡ thật trong thời gian chấp nhận được

---

## 6. Yêu cầu phi chức năng

**NFR-001 — Không làm hỏng cái đang chạy.** Ma trận sau mỗi mốc so với bảng mốc PQ-015; mọi ô khác phải nằm
trong danh sách đổi hành vi có chủ đích.

**NFR-002 — Thiếu cấu hình thì từ chối.** Không vai trò, vai trò ngừng dùng, phạm vi `list` rỗng, hết hạn — đều
bị chặn. `all` chỉ root đặt được.

**NFR-003 — Không rò dữ liệu chéo ADV.** Mọi màn liệt kê, chi tiết, file xuất, dòng nhật ký nằm trong phạm vi.

**NFR-004 — Chặn nằm ở backend.** Nghiệm thu bằng gọi API trực tiếp.

**NFR-005 — Mã lỗi và thông báo.** Thiếu quyền hoặc ngoài phạm vi trả **403**, kèm thông báo tiếng Việt phân
biệt *thiếu quyền* (tên quyền) với *ADV ngoài phạm vi*. **Giữ 401** cho token hỏng, hết hạn, tài khoản bị tắt.
Frontend (`admin/src/utils/request.ts`) hiển thị được thông báo 403 và **không** đăng xuất người dùng.

**NFR-006 — Đổi quyền có hiệu lực ngay, không đăng xuất.** Nhờ PQ-014. Có cache thì xoá khi nhân sự hoặc vai trò
đổi.

**NFR-007 — CI kiểm ma trận.** Registry route + test ma trận chạy mỗi PR.

**NFR-008 — Tài liệu bàn giao sinh từ mã.** Bảng endpoint → quyền và vai trò mẫu → quyền.

---

## 7. Phụ thuộc và giả định

1. Biz gửi **danh sách nhân sự, vai trò, phạm vi từng người** trước Mốc 0 (cho PQ-007) — đặc biệt danh sách nhân
   sự không gắn ADV hôm nay.
2. Biz và AT chốt tập quyền của Vận hành, Manager vận hành và Kỹ thuật hỗ trợ (2.4), và duyệt Phụ lục A, trước
   Mốc 2.
3. ~~Mọi cổng đọc nhân sự và vai trò từ DB mỗi lần gọi~~ — **giả định này sai với phạm vi ADV** (đọc từ JWT).
   Thay bằng PQ-014a (Mốc 0) và PQ-014 (Mốc 1).
4. Đổi bản ghi nhân sự và vai trò cần migration trên production, ngoài giờ vận hành, có bản lùi.
5. Số ADV hiện 14 và còn tăng; phạm vi `all` đảm bảo ADV mới không cần gán tay cho đội kỹ thuật và VFDC.
6. AT chỉ định kênh nhận cảnh báo root đăng nhập và người được chạy break-glass.

---

## 8. Mốc giao hàng

| Mốc | Gồm | Kết quả | Điều kiện xong |
|---|---|---|---|
| **0. Gỡ root tạm** | PQ-014a, PQ-007, PQ-006 (cho năm việc), PQ-003a, nhật ký tối thiểu, PQ-013 | Manager dùng Admin gắn nhiều ADV; root tạm bị tắt | Đếm root = 1; 7 ngày không dùng root cho vận hành |
| **1. Nền** | PQ-015 (đầu tiên), PQ-014 (phần còn lại), PQ-001, PQ-002, PQ-003, PQ-005, PQ-006 (phần còn lại) | Không đổi hành vi ngoài danh sách có chủ đích | Ma trận khớp bảng mốc |
| **2. Vận hành tự cấu hình** | PQ-004, PQ-008, PQ-009 | Biz tự cấu hình quyền; Admin của Manager chuyển sang vai trò Vận hành | Nghiệm thu PQ-008 với biz |
| **3. Đóng rủi ro** | PQ-010, PQ-011, PQ-012 đầy đủ, xoá trường `scopes` cũ | Không còn endpoint chỉ cần đăng nhập | CI kiểm ma trận |

**Mốc 0 thừa gì so với request:** Admin có quyền đổi trạng thái đối soát và đợt rút tiền — việc đội vận hành
không xin. Phần thừa này nhỏ hơn root nhiều: không có 26 endpoint chỉ root, không chạm ADV ngoài phạm vi. Nó tồn
tại tới hết Mốc 2.

**Mốc 0 thiếu gì:** nếu Q10 xác nhận "Cộng thưởng cho creator" là **thưởng sự kiện** (`/event-reward/*`, hôm nay
`IsRoot`), Mốc 0 phải thêm việc chuyển hai endpoint này sang Admin trong phạm vi ADV (giống PQ-003a). Nếu không
thêm, việc đó vẫn phải nhờ root tới Mốc 2 — khi ấy root tạm chưa tắt được ở Mốc 0, mà chỉ được thay bằng quy trình
"nhờ root của AT làm hộ, có ghi lại".

Nếu biz không đồng ý (Q1): Mốc 0 gộp vào Mốc 2, root tạm giữ tới hết Mốc 2, cần gia hạn bằng văn bản.

---

## 9. Ticket tách riêng

- **External API — ký và phân quyền:** chữ ký phủ body, chống gửi lại trace-no, key theo từng ADV hoặc từng
  client, nhật ký ghi `client:<id>`. Cần thống nhất với AT Core vì backend dùng cùng kiểu ký khi gọi sang AT
  (`internal/module/core/client.go:42`).

---

## 10. Quyết định cần chốt trước khi estimate

| # | Câu hỏi | Đề xuất | Ai chốt |
|---|---|---|---|
| Q1 | Chấp nhận Mốc 0 (Admin gắn nhiều ADV, thừa quyền đổi trạng thái chi tiền tới hết Mốc 2) để gỡ root tạm sớm? | Đồng ý | Biz |
| Q2 | Bản ghi dùng chung và bản ghi nhiều ADV: luật xem / sửa ở 2.2 có đúng không? | Theo 2.2 | Biz + DISO |
| Q3 | Ai được duyệt creator và duyệt partner? | Admin và Vận hành; CTV nếu hôm nay CTV đang làm | Biz |
| Q4 | Có ghi nhật ký **lượt xem** thông tin liên hệ creator (dữ liệu cá nhân)? | Có | AT |
| Q5 | Kỹ thuật hỗ trợ có được xem liên hệ creator? | Không | AT |
| Q6 | Manager vận hành có được tự mời người trong đội (`staff.invite` có ràng buộc)? | Có, từ Mốc 2 | Biz + AT |
| Q7 | Nhân sự không gắn ADV hôm nay: ai thành `all`, ai thành `list`? | Rà từng người | Biz |
| Q8 | Vai trò Admin: giữ riêng, hay gộp vào Vận hành sau Mốc 2? | Giữ, xem lại sau Mốc 3 | Biz |
| Q9 | Kênh nhận cảnh báo root đăng nhập; người được chạy break-glass | — | AT |
| Q10 | "Cộng thưởng cho creator" trong request là việc nào: **thưởng sự kiện** (`/event-reward`, đổi trạng thái / xoá, hôm nay chỉ root) hay chính là **Thưởng thêm**? Nếu là thưởng sự kiện: Vận hành có được đổi trạng thái không, và có cần ở Mốc 0? | Hỏi biz kèm ảnh chụp màn hình việc họ làm | Biz |
| Q11 | Admin có cần **Kênh hỗ trợ** không? Hôm nay chỉ root và Cấu hình ứng dụng sửa được, Admin không | Giữ như hôm nay | Biz |
| Q12 | Các route cập nhật hàng loạt dưới `/contents`, `/events`, `/common` (2.3): công cụ vận hành hay công cụ kỹ thuật? | DISO phân loại khi dựng registry | DISO |
| Q13 | `PUT /partners/users/wildrift` còn dùng không? | Không dùng thì gỡ | DISO |

---

## Phụ lục A — Hiện trạng quyền của ba vai trò (router `develop`, 05/10)

Đọc từ middleware ở tầng router, theo nhóm chức năng. Đây là thứ PQ-005 phải giữ nguyên khi gieo quyền, trừ các ô
trong danh sách đổi hành vi có chủ đích. Ma trận chính xác theo endpoint và theo trạng thái ADV lấy từ PQ-015.

Ký hiệu: ✔ gọi được · — bị chặn · **∀** chỉ cần đăng nhập (mọi vai trò gọi được — sẽ đóng ở PQ-010) ·
**ADV** chỉ khi nhân sự gắn ADV và bản ghi thuộc ADV đó

| Nhóm chức năng | Route | Admin | CTV | Cấu hình ứng dụng | Root |
|---|---|---|---|---|---|
| Nội dung — xem, duyệt, ghim, gắn tag | `/contents` | ✔ | ✔ | — | ✔ |
| Luồng nội dung thủ công | `/content-manual-flows` | ✔ | ✔ | — | ✔ |
| Người dùng — danh sách | `GET /users` | ∀ | ∀ | ∀ | ✔ |
| Người dùng — chi tiết, kênh MXH | `/users/:id`, `/:id/socials` | — | — | — | ✔ |
| Người dùng — ban, hợp đồng, eKYC, tạo | `/users/*` | — | — | — | ✔ |
| Duyệt creator / partner | `/users/approval-*` | ∀ | ∀ | ∀ | ✔ |
| Người dùng ADV — trạng thái CBNV | `/user-partners` | ✔ | — | — | ✔ |
| Hồ sơ creator — xem, sửa, điều kiện | `/creator-profiles` | ✔ | — | — | ✔ |
| Sự kiện — danh sách | `GET /events` | ✔ | ✔ | ✔ | ✔ |
| Sự kiện — tạo, sửa, ngân sách, bảng xếp hạng, thống kê | `/events/*` | ✔ ADV | — | ✔ ADV | ✔ |
| Sự kiện — chạy lại thống kê ngày | `/events/run-analytic-daily` | ✔ | — | — | ✔ |
| Sự kiện — huỷ / chạy lại thưởng | `/events/reject-reward-event`… | — | — | — | ✔ |
| **Thưởng sự kiện** — đổi trạng thái, xoá | `/event-reward` | — | — | — | ✔ |
| Mẫu sự kiện | `/event-schemas` | ∀ | ∀ | ∀ | ✔ |
| **Thưởng thêm** — tạo, sửa, import | `/event-bonus` | ∀ | ∀ | ∀ | ✔ |
| Nhiệm vụ, duyệt điểm | `/missions` | ✔ | — | — | ✔ |
| Quà | `/gifts` | ✔ | — | — | ✔ |
| **Đối soát** — mọi thao tác | `/reconciliations` | ✔ | — | — | ✔ |
| **Rút tiền** — mọi thao tác | `/transfers` | ✔ | — | — | ✔ |
| Dữ liệu xuất | `/data-exports` | ✔ | — | — | ✔ |
| Phân khúc, Phân khúc người dùng, Mã, Thông báo admin | `/segments`, `/user-segments`, `/manage-codes`, `/admin-notifications` | ✔ | — | — | ✔ |
| Danh mục — xem | `GET /categories` | ✔ | — | ✔ | ✔ |
| Danh mục — sửa | `/categories` | ✔ | — | — | ✔ |
| Tin tức, Bài viết | `/news`, `/articles` | ✔ | — | ✔ | ✔ |
| Affiliate | `/affiliate-campaigns` | ∀ ADV | ∀ ADV | ∀ ADV | ✔ |
| Kênh hỗ trợ | `/quick-actions` | — | — | ✔ ADV | ✔ |
| Cấu hình ứng dụng ADV | `/partners/:id/app-config`, `/:id/features` | ✔ ADV | — | ✔ ADV | ✔ |
| ADV — danh sách | `GET /partners` | ∀ | ∀ | ∀ | ✔ |
| ADV — tạo, sửa, ngừng | `/partners` | — | — | — | ✔ |
| Dữ liệu user WildRift | `PUT /partners/users/wildrift` | ∀ | ∀ | ∀ | ✔ |
| Tag — danh sách | `GET /tags` | ∀ | ∀ | ∀ | ✔ |
| Tag — tạo, sửa | `/tags` | ✔ | — | — | ✔ |
| Cấu hình chung (`/common-configs`) | `/common-configs` | ✔ | — | — | ✔ |
| Cấu hình chung (`/common/configurations`) — đọc, **ghi** | `/common/configurations` | ∀ | ∀ | ∀ | ✔ |
| Nhật ký thao tác | `/audits` | ∀ | ∀ | ∀ | ✔ |
| Lịch sử đăng nhập | `/audits/login-histories` | ✔ | — | — | ✔ |
| Xác thực tài khoản | `/identifications` | — | — | — | ✔ |
| Nhân sự, Vai trò | `/staffs`, `/roles` | — | — | — | ✔ |
| Công cụ kỹ thuật | `/migration/*`, `/migration/backfill-*` | ∀ | ∀ | ∀ | ✔ |

Đọc nhanh:

- **∀** là các ô sẽ đổi ở Mốc 3 (PQ-010); mỗi ô đã có dòng tương ứng trong danh sách đổi hành vi có chủ đích.
- Ô **ADV** của Admin chỉ đúng khi Admin **gắn ADV**; Admin chưa gắn ADV hôm nay bị các phép so sánh thô chặn ở
  tầng service (mục 1.3) dù cổng router cho qua.
- Cấu hình ứng dụng chỉ qua được khi có gắn ADV (điều kiện nằm trong cổng).
