# Feedback review — PRD Phân quyền chức năng cấu hình được

**Ngày:** 2026-10-01
**Người review:** Vinh Nguyễn (DISO)
**Tài liệu được review:** `prd-phan-quyen-van-hanh-2026-09-25.md`, bản cập nhật 30/9 (đổi hướng sang phân quyền cấu hình được)
**Phương pháp:** đo trực tiếp trên `AT-Core/ambassador`, nhánh `develop`, commit `0b411b25` (01/10). Mọi trích dẫn
`file:dòng` dưới đây theo commit này. Cách đếm ở phụ lục.
**Trạng thái:** chờ người viết PRD phản hồi trước khi estimate

Review đi hai lượt: **Phần A** từ góc sản phẩm (kết quả, phạm vi, nghiệm thu), **Phần B** từ góc kiến trúc (mô
hình dữ liệu, cổng API, chuyển đổi).

---

## 0. Kết luận

Những quyết định nên giữ nguyên:

- Tách **"được làm gì"** (quyền) khỏi **"trên ADV nào"** (phạm vi). Đây là điểm mạnh nhất của bản này.
- Danh mục quyền nằm trong mã, vai trò nằm trong DB.
- Fail-closed; chặn thật ở backend; nghiệm thu bằng gọi API chứ không bằng bấm giao diện.
- Mỗi nhân sự một vai trò, không gán quyền lẻ.

Chưa nên estimate, vì bốn điểm dưới đây làm đổi quy mô hoặc thứ tự công việc:

| # | Vấn đề | Mục |
|---|---|---|
| 1 | Root tạm tồn tại hết Mốc 1, trong khi có đường gỡ sớm mà không phải sửa cổng | A1 |
| 2 | Phạm vi ADV đang đọc từ JWT, không đọc DB. Giả định 8.3 chỉ đúng với vai trò | B2 |
| 3 | Luật ADV mới thiếu bản ghi dùng chung và ADV tạo sau này | B3 |
| 4 | Một số số đo lệch, làm sai quy mô PQ-006 và PQ-010 | B1 |

---

## Phần A — Góc sản phẩm

### A1. Kết quả biz cần đứng sau một mốc mà không ai thấy gì thay đổi

Biz cần hai thứ: thu hồi root tạm, và đội vận hành tự làm năm việc. Theo mục 7, root tạm tồn tại suốt Mốc 1
(PQ-001 → PQ-005, "người khác không thấy gì đổi") và chỉ được thu hồi ở PQ-013.

Mục 7 có nêu đường ngắn (PQ-006 + PQ-007 + PQ-008 trên vai trò Admin) nhưng gạt đi vì "phải sửa cổng hai lần".
Theo chính bảng 1.3, đường ngắn **không đụng cổng nào**:

- Đối soát, rút tiền và dữ liệu xuất nằm dưới `IsAdmin`; thưởng thêm chỉ cần đăng nhập. Admin **có gắn ADV** đã
  qua được cả cổng lẫn phép so sánh thô.
- Manager phải mượn root vì phụ trách nhiều ADV, trong khi bản ghi nhân sự chỉ chứa được một ADV.

Đường ngắn vì vậy chỉ gồm:

1. PQ-007: nhân sự gắn được nhiều ADV.
2. PQ-006, áp cho các service của năm việc.
3. Mở chi tiết người dùng (`GET /users/:id`, `GET /users/:id/socials`, hiện dưới `IsRoot`) cho Admin, trong phạm
   vi ADV của mình.

Phần còn thừa so với request: Admin có quyền đổi trạng thái chi tiền, việc mà đội vận hành không xin. Dù vậy
phần thừa này vẫn nhỏ hơn root rất nhiều: không có 26 endpoint chỉ root, không chạm ADV ngoài danh sách.

**Biz cần quyết:** chấp nhận phần thừa này trong thời gian chờ mô hình mới, hay giữ root tạm cho tới PQ-013.

### A2. Danh mục quyền bỏ sót việc duyệt creator

Hai endpoint sau hôm nay chỉ cần đăng nhập, nên CTV và Cấu hình ứng dụng đều gọi được:

- `POST /users/approval-creator/change-status` — `backend/pkg/admin/router/user.go:30`
- `POST /users/approval-partner/change-status` — `backend/pkg/admin/router/user.go:32`

PQ-010 không liệt kê hai endpoint này, và mục 2.1 không có mã quyền nào cho việc duyệt. Đề xuất thêm một mã
quyền riêng (vd `creator.approve`) và đưa vào câu hỏi ở A5.

### A3. "Khoá root" lấy mất việc Admin đang làm, mâu thuẫn với PQ-005

PQ-005 cam kết không đổi hành vi. Nhưng mục 2.1 và PQ-011 lại khoá root hai nhóm mà Admin đang làm được:

| Nhóm | Hôm nay | PRD |
|---|---|---|
| Tag — tạo, sửa, đổi trạng thái | `IsAdmin` (`router/tag.go:15`) | Khoá root |
| Cấu hình chung | Hai thứ trùng tên: `/common-configs` dưới `IsAdmin` (`router/common_configs.go:14`); `PUT /common/configurations` ai đăng nhập cũng ghi được (`router/common.go:21`) | Xem: `common_config.view`; sửa: khoá root |

Đề xuất:

- Nói rõ "Cấu hình chung" trong PRD là cái nào trong hai.
- Tách một danh sách **"đổi hành vi có chủ đích"** khỏi PQ-005, để ma trận trước/sau có sẵn các ngoại lệ đã được
  duyệt.

### A4. Chỉ một root mà lại có hạn dùng thì có thể tự khoá

PQ-009 áp hạn dùng "cho mọi vai trò, gồm cả root"; PQ-011 quy định chỉ root bật được cờ root; PQ-013 chỉ để lại
một root. Nếu root hết hạn, quên mật khẩu, hoặc người giữ root nghỉ việc, thì không ai vào được màn Nhân viên.

Đề xuất:

- Root không bị áp hạn dùng.
- Có quy trình break-glass bằng văn bản: script chạy trên DB, ai được chạy, ghi lại ở đâu.
- Mỗi lần root đăng nhập đều báo về một kênh. Root được dùng hiếm, nên lần dùng nào cũng đáng biết; đây cũng là
  cách đo PQ-013.

### A5. Câu hỏi bổ sung cho mục 9

5. Ai được duyệt creator và duyệt partner? (A2)
6. Bản ghi dùng chung, tức không thuộc ADV nào (tag, danh mục, kênh hỗ trợ chung…): sau khi chuyển sang
   fail-closed, ai được sửa? (B3)
7. Nhân sự VFDC và vai trò Kỹ thuật hỗ trợ: tự thấy ADV mới tạo, hay phải có người gán tay từng ADV? (B3)
8. `user.view_contact` mở số điện thoại và email của creator cho hai đội. Có ghi nhật ký **lượt xem**, hay chỉ
   lượt sửa? Đây là dữ liệu cá nhân.
9. Có chấp nhận phương án gỡ root sớm ở A1 không?

### A6. Nghiệm thu cần chỉnh

- **PQ-013** "một tuần không xin root lần nào" cần đo được: dựa vào lịch sử đăng nhập của tài khoản root, yêu cầu
  0 lượt phục vụ vận hành trong 7 ngày (kết hợp với cảnh báo ở A4).
- **Vai trò Kỹ thuật hỗ trợ** có trong bảng kết quả mục 1 nhưng không PQ nào nghiệm thu. Thêm một dòng: chỉ đọc
  được; gọi bất kỳ API ghi nào đều bị chặn.
- **PQ-009** "tắt một tài khoản có hiệu lực ngay" đã đúng từ hôm nay: `UpdateInfo` và `ChangeStatus` đều gọi
  `resetToken`, xoá mọi token của nhân sự (`backend/pkg/admin/service/staff.go:292`, `:360`). Nên ghi là "giữ
  nguyên" để khỏi estimate thừa.

---

## Phần B — Góc kiến trúc

### B1. Đối chiếu số đo

| PRD | Đo trên `develop` 01/10 | Ảnh hưởng |
|---|---|---|
| 87 chỗ gắn cổng | 87 ✓ | |
| "42 chỗ chỉ là `RequiredLogin`" (mục 1.1, PQ-010) | 42 là **tổng số lần xuất hiện** `RequiredLogin`; phần lớn đi kèm `IsAdmin` hoặc cổng khác. Số endpoint thật sự chỉ có `RequiredLogin` **vẫn là 60**: 40 migration/backfill, 5 thưởng thêm, 5 `/users`, 5 `/partners`, 4 `/common`, 1 `/audits` | PQ-010 không nhỏ đi. Đọc ra "60 còn 42" là sai |
| 233 endpoint | 263 route, trong đó có 20 route external API | Xem B5 |
| "Hai cách hỏi ADV", khoảng 50 + 25 chỗ | **Ít nhất bốn luật** (bảng dưới). Riêng các hàm `StaffInfo` có 78 lời gọi: `AssignPartnerForStaff` 29, `IsPermissionAllPartner` 28, `IsAllowPartner` 21. Thêm khoảng 15 phép so sánh thô | PQ-006 nên ước theo khoảng 95 chỗ, không phải khoảng 75 |
| 3 vai trò, 8 khoá access, `scopes` không ai đọc, 401 đá người dùng ra, nhật ký không có trường hành động/ADV, token 8 giờ | Khớp cả sáu | |

Bốn luật phạm vi ADV đang cùng tồn tại:

| Luật | Đọc nhân sự từ | Nhân sự chưa gắn ADV | Vị trí |
|---|---|---|---|
| Các hàm `StaffInfo` | JWT | Toàn quyền | `internal/model/mg/staff.go:91–118` |
| So sánh thô `Staff.Partner` với `doc.Partner` | DB | Bị chặn | Nhiều nhất ở `service/reconciliation.go`, `service/event_bonus.go` |
| `StaffCanReachPartner` trong các guard `*InScope` (thêm sau 25/9) | DB | Toàn quyền; bản ghi không có ADV chỉ VFDC chạm được | `router/routeauth/partner_scope.go:63` |
| `CanEditAppConfig` | DB | **Từ chối — đã fail-closed** | `internal/service/partner_app_config_access.go:11` |

Còn một biến thể riêng cho tag: nhân sự ADV thấy cả tag của mình lẫn tag dùng chung
(`AssignPartnerWithNonExistsPartnerForStaff`, `service/tag.go:99`).

Đề xuất: PQ-006 lấy `CanEditAppConfig` làm khuôn, vì nó đã đúng luật fail-closed mà PRD muốn.

### B2. Phạm vi ADV đọc từ JWT — giả định 8.3 chỉ đúng một nửa

Giả định 8.3 ("mọi cổng đọc nhân sự và vai trò từ DB ở mỗi lần gọi") đúng với **vai trò**. Nhưng **phạm vi ADV**
thì đọc từ token:

- Middleware `Auth` dựng `StaffInfo` từ hai claim `isRoot` và `partner` của JWT
  (`router/routeauth/auth.go:201`, `:225`). Hai claim này được ghi vào token lúc đăng nhập
  (`internal/model/mg/staff.go:67–68`).
- Cả 78 lời gọi hàm `StaffInfo` ở B1 đều đọc từ đó.

Hôm nay đổi ADV vẫn có tác dụng ngay, nhưng là nhờ `resetToken` xoá token: người dùng **bị đá ra đăng nhập lại**,
chứ không phải "có hiệu lực ở thao tác kế tiếp". Hệ quả:

- Nghiệm thu PQ-007 "bỏ một ADV, mất quyền ngay, không cần đăng nhập lại" sẽ không đạt nếu danh sách ADV vẫn nằm
  trong token như ô `partner` hiện nay.
- Hạn dùng ở PQ-009 không có sự kiện nào kích hoạt xoá token đúng lúc hết hạn, nên phải kiểm ở mỗi lần gọi. Hiện
  `Auth` không kiểm `active` hay bất cứ gì trong DB, và các cổng vai trò cũng không kiểm `role.active`.

Đề xuất:

- `Auth` nạp **một principal** cho mỗi request: nhân sự, vai trò, tập quyền, danh sách ADV, `active`, hạn dùng.
  Đặt vào context; mọi cổng và service đọc từ đó.
- Token chỉ còn giữ `_id`.
- Hôm nay một request qua cổng vai trò tốn 2 lần `FindById`, qua guard `inScope` thêm 1 lần. Gom lại thì chỉ còn
  1 lần, hoặc cache ngắn và xoá cache khi đổi nhân sự hay vai trò (NFR-006 đã nêu).
- Ghi quyết định này vào PRD, thay cho giả định 8.3.

### B3. Luật "ADV của bản ghi thuộc danh sách ADV của nhân sự" chưa đủ

- **Bản ghi dùng chung** (không có ADV): theo công thức ở mục 2 thì ngoài root không ai chạm được. Hôm nay
  `StaffCanReachPartner` coi các bản ghi này là của VFDC, còn tag thì cho nhân sự ADV thấy cả phần dùng chung.
  Cần một phạm vi "dùng chung" được khai báo tường minh trong mô hình.
- **ADV tạo sau:** PQ-007 gán cho nhân sự VFDC một danh sách cố định 14 ADV, nên ADV thứ 15 sẽ không ai ngoài root
  thấy cho tới khi có người gán tay. Đề xuất phạm vi có hai dạng: `all` (chỉ root được đặt) và `list`. Danh sách
  rỗng thì từ chối. Cách này vẫn fail-closed, vì `all` phải được đặt có chủ đích.
- **Bản ghi thuộc nhiều ADV** (trường `partners` dạng mảng, `AssignPartnersForStaff`): PRD cần viết rõ luật là
  "có giao nhau" hay "nằm trọn trong".
- Trường `type` (`vfdc` / `partner`) đã có trên bản ghi nhân sự (`internal/constants/staff.go:4`) nhưng không chỗ
  nào đọc. Nên dùng hẳn hoặc bỏ đi, để nó không thành nguồn sự thật thứ năm.

### B4. Gieo dữ liệu cho PQ-005

- `GenerateRole()` chỉ chèn những vai trò còn thiếu theo mã
  (`pkg/admin/server/initialize/dummy_db.go:74`, `:80`), không cập nhật vai trò đã có. Vì vậy nó không gieo được
  tập quyền cho ba vai trò hiện có.
- Nếu sửa nó để ghi đè lúc khởi động, thì mỗi lần deploy sẽ xoá mất những quyền root vừa tick trên màn hình.
- Cách đúng là một migration chạy một lần, có đánh dấu phiên bản. Khung `/migration/jobs` đã có sẵn.
- Trường `scopes` đang lưu mảng `{name, code}` theo danh mục giả (`internal/model/mg/role.go:18`). Nên dùng một
  trường mới chỉ chứa mã quyền, không tái dùng tên và dữ liệu cũ.

### B5. External API nằm ngoài mô hình

Có 20 route ở `/api/admin/external-api` (`router/external_api.go`), đi qua cổng `CheckKeyAuth`:

- Một cặp client-id và secret dùng chung cho mọi ADV.
- Các route gồm: tạo và đổi trạng thái đối soát, đổi trạng thái từng mục đối soát, tạo/sửa/đổi trạng thái/từ
  chối đợt rút tiền.
- Chữ ký HMAC chỉ phủ `clientID|traceNo|time` (`router/routeauth/external_auth.go:90`), **không phủ body**. Không
  chỗ nào kiểm trace-no đã được dùng hay chưa. Trong cửa sổ 5 phút, ai có được một bộ header hợp lệ có thể gửi
  kèm một body khác.
- Backend dùng đúng kiểu ký này khi gọi sang AT Core (`internal/module/core/client.go:42`), nên có thể đây là
  chuẩn chung phía AT. Muốn đổi thì hai bên phải thống nhất.

Thực chất đây là một "root thứ hai" cho dòng tiền. Đề xuất:

- Ghi vào mục 4.2 Ngoài phạm vi, kèm một ticket riêng.
- Nói rõ mục tiêu "chỉ còn một root" là root **người dùng**.
- Nhật ký ghi người thực hiện dạng `client:<id>` cho các thao tác qua external API.
- Bài kiểm CI ở PQ-010 có danh sách riêng cho nhóm route này, để không báo đỏ sai.

### B6. Cổng API và CI

- Echo không lưu thông tin middleware trong `e.Routes()`. Muốn sinh "bảng endpoint → quyền" từ mã (PQ-002,
  NFR-008) thì cần một lớp đăng ký route tự ghi lại mã quyền. CI duyệt `e.Routes()`: route nào không có trong
  registry và không thuộc danh sách công khai (login, xác nhận và nhận lời mời, quên và đặt lại mật khẩu,
  `/staffs/me`) thì báo đỏ.
- Kiểm vai trò bằng mã còn nằm ở các cổng có điều kiện kèm theo, ví dụ "config_editor phải gắn ADV" trong
  `HasAnyRole`, `IsConfigEditor`, `IsAdminOrConfigEditor`. Những điều kiện kiểu này thuộc PQ-006 (phạm vi), không
  nên biến thành mã quyền.
- Quy tắc "`edit` kéo theo `view`" (PQ-004) phải được ép ở backend khi lưu vai trò, không chỉ ở giao diện.
- Đổi lỗi thiếu quyền từ 401 sang 403 (NFR-005) là đúng hướng. Hiện mọi cổng vai trò trả 401 khi thiếu quyền,
  và admin đăng xuất người dùng khi gặp 401 (`admin/src/utils/request.ts:27`); riêng guard `inScope` đã trả 403.
  Vẫn phải giữ 401 cho token hỏng, và frontend phải hiển thị được thông báo của 403.

### B7. Nhật ký

- `AuditRaw` hiện chỉ có `targetId`, `data` (chụp cả document), `message`, `staff`, `createdAt`, `batchId`
  (`internal/model/mg/audit.go:15`).
- Thêm hai trường hành động và ADV (PQ-012) thì cần index phục vụ lọc theo người, hành động, ADV và thời gian.
- Các dòng cũ không có ADV. Lọc theo ADV phải backfill qua `targetId`, hoặc hiển thị là "không rõ ADV".
- Thao tác qua external API không có nhân sự thực hiện (xem B5).

### B8. Viết test ma trận trước khi refactor

Chụp lại ma trận (vai trò × trạng thái ADV × endpoint) trên `develop` hôm nay để làm mốc so sánh. Không có mốc
này thì nghiệm thu "không ô nào đổi" của PQ-005 không có gì để so. Đây cũng là đầu vào giúp estimate chính xác
nhất, nên là việc đầu tiên của Mốc 1.

---

## Đề xuất chia lại mốc

| Mốc | Gồm | Kết quả |
|---|---|---|
| **0. Gỡ root tạm** | PQ-007 (có hai dạng `all` / `list`), PQ-006 cho các service của năm việc, mở chi tiết người dùng cho Admin trong phạm vi ADV, nhật ký tối thiểu cho năm việc, PQ-013 | Manager dùng tài khoản Admin gắn nhiều ADV thay cho root. Cần biz đồng ý ở A1 |
| **1. Nền** | Test ma trận làm mốc (B8), principal nạp mỗi request (B2), danh mục quyền và `RequirePermission`, vai trò gieo bằng migration (B4) | Không đổi hành vi của ai |
| **2. Vận hành và màn hình** | Vai trò Vận hành và Kỹ thuật hỗ trợ, màn Vai trò & phân quyền, lời mời theo nhóm quyền, hạn dùng | Biz tự cấu hình quyền, không cần phát hành bản mới |
| **3. Đóng rủi ro** | PQ-010, PQ-011, danh sách "đổi hành vi có chủ đích" (A3), external API (B5) | Không còn endpoint chỉ cần đăng nhập; CI kiểm ma trận |

Nếu biz không đồng ý phương án ở A1, Mốc 0 gộp vào Mốc 2 và thứ tự quay về như mục 7 của PRD.

---

## Phụ lục — cách đo

Tất cả trên `AT-Core/ambassador`, commit `0b411b25`.

- **Route:** đếm các lời gọi `.GET(` / `.POST(` / `.PUT(` / `.PATCH(` / `.DELETE(` trong
  `backend/pkg/admin/router/*.go`, được 263.
- **Cổng:** đếm số lần xuất hiện từng middleware trong cùng thư mục: `RequiredLogin` 42, `IsAdmin` 17,
  `IsConfigEditor` 10, `IsRoot` 7, `HasAnyRole` 7, `IsCollaborator` 2, `IsAdminOrConfigEditor` 2. Tổng 87.
- **Endpoint không có cổng vai trò:** một route được tính là có cổng nếu group của nó hoặc chính nó gắn một trong
  các middleware `IsRoot`, `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole`.
  Có 87 route không có cổng; trừ 20 route external API (dùng cổng riêng) và 7 route `/staffs` công khai hoặc tự
  phục vụ, còn 60.
- **Hàm `StaffInfo`:** đếm các lời gọi `.AssignPartnerForStaff(`, `.IsPermissionAllPartner(`, `.IsAllowPartner(`
  trên toàn `backend`.
- **So sánh thô:** tìm các biểu thức so sánh `Staff.Partner` với `Partner` của bản ghi bằng `!=` hoặc `==`.
  Con số khoảng 15 là cận dưới, vì các cách viết khác (qua `.Hex()`, qua biến trung gian) không được bắt.
