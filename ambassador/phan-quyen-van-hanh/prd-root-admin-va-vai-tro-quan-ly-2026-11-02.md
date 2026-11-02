# PRD cập nhật: Root, Admin và các vai trò quản lý

**Ngày:** 2026-11-02
**Sản phẩm:** Ambassador, trang quản trị (admin)
**Trạng thái:** nháp, chờ chốt các điểm ở mục 9
**Mã nguồn đã đối chiếu:** nhánh `release` commit `e24f4e73`; PR #312 head `7694f853` (chưa merge)
**Quan hệ với tài liệu cũ:** bổ sung [PRD 05/10](prd-phan-quyen-he-thong-2026-10-05.md) và [vai-tro-va-quyen](vai-tro-va-quyen-2026-10-16.md). Chỗ nào khác nhau thì theo tài liệu này. Mục 10 liệt kê các đoạn cũ cần sửa.

**Vấn đề cần sửa:** từ phiên bản trước tháng 10, "admin" đang gộp ba loại người khác nhau, và việc quản lý người chỉ làm được bằng root. Phiên bản hiện tại thêm được bảng quyền nhưng giữ nguyên cả hai điểm đó: admin vẫn không quản lý được người, nên vẫn phải có người đăng nhập root.

---

## 1. Cần đạt được

| # | Mục tiêu | Đo bằng |
|---|---|---|
| 1 | **Root chỉ là danh tính của hệ thống**, dùng để việc nền chạy và ghi nhật ký. Không ai đăng nhập | Đăng nhập bằng root bị từ chối; việc nền và API ngoài vẫn chạy |
| 2 | **Có trên giao diện thì phải có mã quyền, và Admin thao tác được hết**. Admin gắn với người đích danh | Không còn API nào giao diện gọi mà chỉ root dùng được |
| 3 | **Được có nhiều Admin**, hệ thống luôn còn ít nhất 1 | Không tắt hay đổi vai trò được Admin cuối cùng |
| 4 | **Mỗi loại người một vai trò riêng**: Admin hệ thống, Quản lý vận hành, Quản lý ADV | Mỗi tài khoản "admin" cũ được chuyển sang đúng vai |
| 5 | **Quyền đều có mã, gán bằng cách tick trên màn Vai trò** | Đổi ai làm gì không cần deploy |

---

## 2. Vai trò qua từng phiên bản

**Phiên bản trước tháng 10** là nhánh `release`, đang coi là production. **Phiên bản hiện tại** là #312, chưa merge. **Phiên bản tháng 11** là kết quả của PRD này.

| Vai trò | Phiên bản trước tháng 10 | Phiên bản hiện tại | Phiên bản tháng 11 |
|---|---|---|---|
| **Root** | Cờ `isRoot` trong DB, có người đăng nhập | Giữ nguyên | Giữ cờ. **Không ai đăng nhập** |
| **Admin hệ thống** | Vai trò `admin`, không ADV | `admin`, 70/75 quyền, không ADV | `admin`, đủ mọi mã, không ADV |
| **Quản lý vận hành** | Vai trò `admin`, không ADV | Vẫn là `admin`, chưa tách khỏi Admin hệ thống | Vai trò `ops_manager`, bộ quyền do biz chốt, root chỉnh và gán người |
| **Quản lý ADV** | Vai trò `admin`, có ADV | Vẫn là `admin`, chưa tách khỏi hai vai trên | Vai trò mới, bộ quyền do biz chốt, root tạo và gán người |
| **Vận hành nội dung, Vận hành hiệu suất, Duyệt chi, Kỹ thuật hỗ trợ, Cấu hình ứng dụng, Cộng tác viên** | Chỉ Cấu hình ứng dụng và Cộng tác viên có sẵn | Theo `vai-tro-va-quyen` | **Giữ nguyên hiện trạng.** Admin tự rà soát và đánh giá thêm |

### Mục tiêu từng vai trò

**Root: danh tính hệ thống**
- Việc nền tìm tài khoản `isGenerate` để chạy và ghi nhật ký, ví dụ tự từ chối video, gắn tag cảnh báo, chạy file xuất.
- Tài khoản này giữ nguyên cờ `isRoot`, vì việc nền dựa vào cờ đó để qua các bước kiểm quyền trong service.
- Không dùng cho thao tác của con người, trừ giai đoạn chuyển đổi ở mục 6.

**Admin: quản trị hệ thống**
- Ai dùng: người chịu trách nhiệm hệ thống, đích danh. Được có nhiều người, nên giữ ít nhất có thể.
- Làm được: mọi thao tác trên giao diện admin, gồm thêm và sửa vai trò, thêm và sửa nhân sự, tạo và sửa ADV, các nghiệp vụ.
- Phạm vi: bắt buộc **Mọi ADV**.

**Quản lý vận hành: điều phối vận hành**
- Ai dùng: trưởng nhóm vận hành, hiện đang giữ `admin` không ADV.
- Làm được: việc vận hành hằng ngày và quản lý nhân sự Vận hành nội dung, Vận hành hiệu suất.
- Không làm được: quản lý vai trò, ADV, nhân sự cấp cao hơn.
- Phạm vi: Mọi ADV hoặc danh sách ADV phụ trách, theo bảng gán người.

**Quản lý ADV: phụ trách một hoặc vài ADV**
- Ai dùng: người đang giữ `admin` có gắn ADV.
- Làm được: nghiệp vụ của ADV mình, theo bộ quyền biz chốt.
- Không làm được: những việc dùng chung toàn hệ thống, kể cả khi lỡ được tick mã (mục 4, PQ-21).
- Phạm vi: danh sách ADV.

---

## 3. Bộ quyền

Hiện có 75 mã. Thêm 14 mã, tổng là **89 mã**. Tên mã bên dưới là đề xuất, team dev có thể chỉnh khi làm.

### 3.1 14 mã mới

| Mã | Tên hiển thị | Thay cho |
|---|---|---|
| `role.view` | Xem vai trò | `GET /roles/:id`; thấy đủ vai trò ở `GET /roles`; menu Vai trò |
| `role.edit` | Quản lý vai trò | `POST /roles`, `PUT /roles/:id`, `PATCH /roles/:id/status` |
| `staff.create` | Tạo nhân sự trực tiếp | `POST /staffs/register` |
| `staff.reset_password` | Đổi mật khẩu nhân sự khác | `PUT /staffs/:id/update-password` |
| `staff.assign_all_scope` | Gán phạm vi Mọi ADV | Giao "Mọi ADV"; sửa nhân sự phạm vi Mọi ADV |
| `partner.create` | Tạo ADV | `POST /partners` |
| `partner.edit` | Quản lý ADV | `PUT /partners/:id`, `PATCH /partners/:id/status`; menu ADV |
| `user_partner.edit_wildrift` | Sửa thông tin Wild Rift | `PUT /partners/users/wildrift` |
| `creator.create` | Tạo người dùng | `POST /users` |
| `creator.ban` | Khoá, mở khoá creator | `PATCH /users/:id/ban`, `PATCH /users/:id/un-ban` |
| `contract.view` | Tải hợp đồng | `GET /users/:id/contract/pre-signed` |
| `contract.reject` | Từ chối hợp đồng | `PATCH /users/:id/reject-contract` |
| `user.view_sensitive` | Xem đủ CCCD, mã số thuế, số thẻ | Thay cho `canViewFullPII` đang chỉ cho root |
| `audit.view_system` | Xem nhật ký hệ thống | Dòng về vai trò, dòng đăng nhập root, dòng về tài khoản root |

### 3.2 Admin nhận gì

Admin hiện có 70 mã, cần thêm **19 mã**: 14 mã mới, cộng 3 mã nhân sự và 2 mã kênh hỗ trợ đang thiếu (`staff.view`, `staff.invite`, `staff.edit`, `quick_action.view`, `quick_action.edit`). Kết quả là 89/89.

Việc này đi bằng **migration chạy tay** (PQ-27), root không phải tự tick. Không để migration tự chạy lúc khởi động: migration cấp theo vai trò, nên mọi người đang giữ `admin` sẽ có đủ quyền ngay khi deploy.

Quản lý vận hành và Quản lý ADV **không có migration** trong PRD này. Biz chốt bộ quyền theo ma trận ở mục 3.4, rồi root cấu hình trên màn Vai trò.

### 3.3 Không có trên giao diện: không tạo mã

Các API này không có màn hình trên admin, nên không tạo mã quyền. Nếu sau này có màn hình, ví dụ bật lại Xác thực CCCD, thì phải thêm mã quyền cùng lúc.

| Nhóm | API |
|---|---|
| Xác thực CCCD (route và menu đã bị comment, code giao diện sẽ xoá theo PQ-29) | `GET /identifications`, `GET /identifications/:id`, `PATCH /identifications/:id/status` |
| Sửa trực tiếp bản ghi thưởng sự kiện (khác với từ chối mục trong Đối soát, việc đó đã có giao diện và có mã `reconciliation.cancel_item`) | `POST /event-reward/change-status`, `DELETE /event-reward/:id`, `POST /events/reject-reward-event` |
| Hợp đồng, eKYC | `POST /users/contract/generate-by-user-id`, `PUT /users/update-ekyc` |
| Xoá cứng nội dung | `DELETE /contents/:id` |
| Công cụ chạy lại số liệu | `GET /events/migrate-category-ead`, `GET /events/rerun-reward-event-by-cad`, `GET /events/run-analytic-daily`, `GET /common/update-event-daily`, `GET /contents/update-status-data-contents`, `GET /contents/update-warning-tags-content` |
| Migration | `/migration/*` |

Sau khi khoá root, không ai gọi được các API này qua đăng nhập. `/migration/*` và công cụ chạy lại số liệu đi qua cổng kỹ thuật ở PQ-28. Các API còn lại nếu vẫn cần dùng thì team dev chuyển sang cổng đó, không mở lại root.

### 3.4 Ma trận vai trò và quyền

Cột Admin là chốt. Hai cột còn lại chỉ là **đề xuất để biz chốt**, chưa phải quyết định. ✔ = có, ô trống = không.

Cách đề xuất:
- **Quản lý vận hành:** 30 mã mặc định của `ops_manager`, thêm nhiệm vụ, quà, segment, mã, thông báo, sửa hồ sơ creator, người dùng ADV và xuất file. Tổng 52 mã.
- **Quản lý ADV:** bộ trên, thêm sự kiện, mẫu sự kiện, cấu hình site, tin tức, bài viết, affiliate, danh mục, tag và cấu hình chung của ADV mình. Tổng 68 mã.
- **Cả hai không có:** lập đối soát, lập đợt rút, duyệt thưởng thêm, duyệt đối soát, xử lý rút tiền, vì vẫn để Admin lập và Duyệt chi duyệt (Q14 chưa chốt).

Nên đối chiếu với việc họ đang làm bằng `admin`: bớt mã nào thì họ mất việc đó sau khi chuyển vai.

| Mã quyền | Tên | Admin | QLVH (đề xuất) | Quản lý ADV (đề xuất) |
|---|---|:-:|:-:|:-:|
| **Nội dung** | | | | |
| `content.view` | Xem nội dung | ✔ | ✔ | ✔ |
| `content.moderate` | Duyệt nội dung | ✔ | ✔ | ✔ |
| `content_manual_flow.view` | Xem cộng trừ lượt xem thủ công | ✔ | ✔ | ✔ |
| `content_manual_flow.edit` | Cộng trừ lượt xem thủ công | ✔ | ✔ | ✔ |
| **Người dùng và creator** | | | | |
| `user.view_contact` | Xem liên hệ creator | ✔ | ✔ | ✔ |
| `creator.view` | Xem hồ sơ creator | ✔ | ✔ | ✔ |
| `creator.edit` | Sửa hồ sơ creator | ✔ | ✔ | ✔ |
| `creator.approve` | Duyệt đăng ký sự kiện | ✔ | ✔ | ✔ |
| `partner_member.approve` | Duyệt thành viên ADV | ✔ | ✔ | ✔ |
| `user_partner.view` | Xem người dùng ADV | ✔ | ✔ | ✔ |
| `user_partner.edit_staff_status` | Đổi trạng thái CBNV | ✔ | ✔ | ✔ |
| **Sự kiện và thống kê** | | | | |
| `event.view` | Xem danh sách sự kiện | ✔ | ✔ | ✔ |
| `event.view_detail` | Xem chi tiết sự kiện | ✔ | ✔ | ✔ |
| `event.edit` | Quản lý sự kiện | ✔ |  | ✔ |
| `event_schema.view` | Xem mẫu sự kiện | ✔ |  | ✔ |
| `event_schema.edit` | Quản lý mẫu sự kiện | ✔ |  | ✔ |
| `statistic.view` | Xem thống kê | ✔ | ✔ | ✔ |
| **Thưởng, nhiệm vụ, quà** | | | | |
| `bonus.view` | Xem thưởng thêm | ✔ | ✔ | ✔ |
| `bonus.edit` | Cộng thưởng thêm | ✔ | ✔ | ✔ |
| `bonus.import` | Import thưởng thêm | ✔ | ✔ | ✔ |
| `bonus.cancel` | Huỷ thưởng thêm | ✔ | ✔ | ✔ |
| `bonus.approve` | Duyệt thưởng thêm | ✔ |  |  |
| `mission.view` | Xem nhiệm vụ | ✔ | ✔ | ✔ |
| `mission.edit` | Quản lý nhiệm vụ | ✔ | ✔ | ✔ |
| `mission.approve` | Duyệt điểm nhiệm vụ | ✔ | ✔ | ✔ |
| `gift.view` | Xem quà | ✔ | ✔ | ✔ |
| `gift.edit` | Quản lý quà | ✔ | ✔ | ✔ |
| `gift.process` | Xử lý đổi quà | ✔ | ✔ | ✔ |
| **Đối soát, rút tiền, xuất** | | | | |
| `reconciliation.view` | Xem đối soát | ✔ | ✔ | ✔ |
| `reconciliation.create` | Tạo bản đối soát | ✔ |  |  |
| `reconciliation.cancel_item` | Từ chối từng mục trong đối soát | ✔ | ✔ | ✔ |
| `reconciliation.change_status` | Lấy danh sách, duyệt, hủy cả bản đối soát | ✔ |  |  |
| `reconciliation.export` | Tải file đối soát | ✔ | ✔ | ✔ |
| `transfer.view` | Xem rút tiền | ✔ | ✔ | ✔ |
| `transfer.create` | Tạo đợt rút tiền | ✔ |  |  |
| `transfer.export` | Tải file rút tiền | ✔ | ✔ | ✔ |
| `transfer.change_status` | Xử lý rút tiền | ✔ |  |  |
| `export.view` | Xem dữ liệu xuất | ✔ | ✔ | ✔ |
| `content.export` | Xuất file nội dung | ✔ | ✔ | ✔ |
| `statistic.export` | Xuất file biểu đồ | ✔ | ✔ | ✔ |
| `user_partner.export` | Xuất file người dùng ADV | ✔ | ✔ | ✔ |
| `creator.export` | Xuất file kênh creator | ✔ | ✔ | ✔ |
| **Segment, mã, thông báo, danh mục** | | | | |
| `segment.view` | Xem segment | ✔ | ✔ | ✔ |
| `segment.edit` | Quản lý segment | ✔ | ✔ | ✔ |
| `user_segment.view` | Xem người dùng trong segment | ✔ | ✔ | ✔ |
| `user_segment.edit` | Sửa người dùng trong segment | ✔ | ✔ | ✔ |
| `user_segment.import` | Import người dùng vào segment | ✔ | ✔ | ✔ |
| `code.view` | Xem mã | ✔ | ✔ | ✔ |
| `code.edit` | Quản lý mã | ✔ | ✔ | ✔ |
| `code.import` | Import mã | ✔ | ✔ | ✔ |
| `notification.view` | Xem thông báo | ✔ | ✔ | ✔ |
| `notification.edit` | Soạn thông báo | ✔ | ✔ | ✔ |
| `notification.approve` | Duyệt thông báo | ✔ | ✔ | ✔ |
| `category.view` | Xem danh mục | ✔ | ✔ | ✔ |
| `category.edit` | Quản lý danh mục | ✔ |  | ✔ |
| **Cấu hình ADV và site** | | | | |
| `app_config.view` | Xem cấu hình ứng dụng | ✔ |  | ✔ |
| `app_config.edit` | Sửa cấu hình ứng dụng | ✔ |  | ✔ |
| `app_config.publish` | Xuất bản cấu hình | ✔ |  | ✔ |
| `news.view` | Xem tin tức | ✔ |  | ✔ |
| `news.edit` | Quản lý tin tức | ✔ |  | ✔ |
| `article.view` | Xem bài viết | ✔ |  | ✔ |
| `article.edit` | Quản lý bài viết | ✔ |  | ✔ |
| `quick_action.view` | Xem kênh hỗ trợ | ✔ |  |  |
| `quick_action.edit` | Quản lý kênh hỗ trợ | ✔ |  |  |
| `affiliate.view` | Xem chiến dịch affiliate | ✔ |  | ✔ |
| `affiliate.edit` | Quản lý chiến dịch affiliate | ✔ |  | ✔ |
| **Hệ thống** | | | | |
| `tag.view` | Xem tag | ✔ | ✔ | ✔ |
| `tag.edit` | Quản lý tag | ✔ |  | ✔ |
| `common_config.view` | Xem cấu hình chung | ✔ |  | ✔ |
| `common_config.edit` | Sửa cấu hình chung | ✔ |  | ✔ |
| `audit.view` | Xem nhật ký thao tác | ✔ | ✔ | ✔ |
| `login_history.view` | Xem lịch sử đăng nhập | ✔ | ✔ | ✔ |
| `staff.view` | Xem nhân sự | ✔ | ✔ | ✔ |
| `staff.invite` | Mời nhân sự | ✔ | ✔ | ✔ |
| `staff.edit` | Sửa nhân sự | ✔ | ✔ | ✔ |
| **Mã mới** | | | | |
| `role.view` | Xem vai trò | ✔ |  |  |
| `role.edit` | Quản lý vai trò | ✔ |  |  |
| `staff.create` | Tạo nhân sự trực tiếp | ✔ |  |  |
| `staff.reset_password` | Đổi mật khẩu nhân sự khác | ✔ |  |  |
| `staff.assign_all_scope` | Gán phạm vi Mọi ADV | ✔ |  |  |
| `partner.create` | Tạo ADV | ✔ |  |  |
| `partner.edit` | Quản lý ADV | ✔ |  |  |
| `user_partner.edit_wildrift` | Sửa thông tin Wild Rift | ✔ |  |  |
| `creator.create` | Tạo người dùng | ✔ |  |  |
| `creator.ban` | Khoá, mở khoá creator | ✔ |  |  |
| `contract.view` | Tải hợp đồng | ✔ |  |  |
| `contract.reject` | Từ chối hợp đồng | ✔ |  |  |
| `user.view_sensitive` | Xem đủ CCCD, mã số thuế, số thẻ | ✔ |  |  |
| `audit.view_system` | Xem nhật ký hệ thống | ✔ |  |  |
| | **Tổng** | **89** | **52** | **68** |

Sáu vai trò còn lại không đổi quyền, xem `vai-tro-va-quyen` mục 3. Không vai trò nào trong số đó nhận 14 mã mới.

---

## 4. Yêu cầu chức năng

Tiếp nối đánh số của PRD 05/10.

### PQ-19: Khoá đăng nhập root
- Thêm cờ cấu hình `ROOT_LOGIN_ENABLED`, mặc định `true`, chỉ để phục vụ giai đoạn chuyển đổi ở mục 6. Tắt rồi thì không bật lại để làm việc.
- Khi `false`: đăng nhập bằng tài khoản `isRoot` bị từ chối; phiên root đang mở bị chặn ở request kế tiếp; ghi nhật ký mỗi lần thử.
- Đổi mật khẩu qua email không mở được đường vào.
- Không tắt tài khoản root (`active=false`). Việc nền và API ngoài không đổi, luật "còn ít nhất một root đang bật" giữ nguyên.

**Nghiệm thu:** với cờ `false`, root không đăng nhập được, còn tự từ chối video, gắn tag cảnh báo và file xuất vẫn chạy trên dev.

### PQ-20: Thêm 14 mã quyền
- Thêm vào danh mục mã, nhãn, mô tả, nhóm.
- Đổi các API ở mục 3.1 từ `Root()` sang `Perm(mã)`.
- Đổi các chỗ service kiểm tra root tương ứng sang kiểm tra mã, gồm `requireRoot` trong `role.go`, kiểm tra root ở `staff.go` và `canViewFullPII`.
- Đổi menu Người dùng, ADV, Vai trò từ `isRootAccess` sang mã quyền. Menu Người dùng dùng `creator.view`.

**Nghiệm thu:** mỗi mã mới có ca được phép và ca bị 403; ma trận route × vai trò cập nhật theo; không còn API nào `admin/src` gọi mà route là `Root()`.

### PQ-21: Mã toàn hệ thống chỉ có tác dụng với phạm vi Mọi ADV
- Áp cho: `role.*`, `staff.assign_all_scope`, `partner.*`, `creator.create`, `creator.ban`, `contract.*`, `audit.view_system`.
- Lý do: các dữ liệu này dùng chung, không thuộc riêng ADV nào.
- Luật nằm ở mã quyền và phạm vi, không gắn với tên vai trò.

**Nghiệm thu:** vai trò có `role.edit` nhưng phạm vi danh sách vẫn nhận 403 khi sửa vai trò.

### PQ-22: Chống tự nâng quyền
- Người có `role.edit` chỉ được tick những mã chính họ đang có.
- Không tự sửa tài khoản của mình (đã có).
- Vai trò `admin` không bỏ được `role.view`, `role.edit`, `staff.view`, `staff.invite`, `staff.edit`, `staff.assign_all_scope`.
- Không tắt hay đổi vai trò được Admin cuối cùng đang hoạt động.

**Nghiệm thu:** mỗi luật có một ca bị từ chối với thông báo rõ.

### PQ-23: Gán và mời được vai trò Admin
- Bỏ chặn mời Admin: `checkRoleUsable`, và bộ lọc `forInvite` ở `use-role-partner-options.ts`.
- Bỏ loại trừ Admin ở `canAssignRole`, `filterAssignableRoles` và `subsetAssignableCodes`. Luật tập con đã đủ: chỉ người có toàn bộ quyền của Admin mới gán được Admin.
- Sửa `makerCannotAssign`: không chặn khi người gán đã có sẵn các mã nhóm duyệt của vai trò đích. Nếu không sửa, Admin giữ cả nhóm lập và nhóm duyệt sẽ không gán được Duyệt chi hay Admin khác.
- Nhân sự mang vai trò Admin phải có phạm vi Mọi ADV.

**Nghiệm thu:** Admin mời được Admin và Duyệt chi; Quản lý vận hành không gán được hai vai trò này; Admin phạm vi danh sách không lưu được.

### PQ-24: Phạm vi Mọi ADV đi theo mã quyền
Đổi các luật đang ghi "chỉ root" sang `staff.assign_all_scope`: gán Mọi ADV và sửa nhân sự Mọi ADV (`checkStaffAssignment`, `checkStaffEditable`), cùng ô chọn trên form nhân sự.

**Nghiệm thu:** Admin giao được Mọi ADV; Quản lý vận hành phạm vi Mọi ADV không giao được và không sửa được nhân sự Mọi ADV.

### PQ-25: Xem dữ liệu nhạy cảm
- Thay `canViewFullPII` bằng `user.view_sensitive`.
- Ghi nhật ký mỗi lần xem bản đầy đủ.
- File rút tiền giữ như hiện tại, chờ quyết định ở `vai-tro-va-quyen` mục 7 #2.

**Nghiệm thu:** có mã thì thấy đủ và có dòng nhật ký; không có mã thì thấy bản che.

### PQ-26: Nhật ký hệ thống
- Thay điều kiện root ở `auditPeopleCond` và `auditPeopleHiddenTargets` bằng `audit.view_system`.
- Các Admin xem được nhật ký của nhau và mọi lần thử đăng nhập root.

**Nghiệm thu:** Admin thấy dòng `role.*` và dòng về root; Quản lý vận hành không thấy.

### PQ-27: Migration nâng Admin đủ quyền
- Thêm `POST /migration/rbac-admin-full`, chạy tay như `rbac-staff-scope`, theo dõi qua `GET /migration/jobs/:id`.
- `dryRun`: liệt kê mọi người đang giữ `admin` và phạm vi của họ, không ghi gì.
- Chạy thật: body phải có `confirmEmails` khớp đúng danh sách đang giữ `admin`. Lệch thì từ chối, không ghi gì.
- Cấp 19 mã bằng `$addToSet`, chỉ vào vai trò `admin` có `isSystem`. Chạy lại không đổi kết quả. Ghi nhật ký.
- `SeedRoles` của `admin` loại trừ 14 mã mới, để luồng này giống nhau ở DB cũ và DB mới, và `TestRBACMigrationsReproduceSeedRoles` vẫn đúng.

**Nghiệm thu:** dry-run không đổi dữ liệu; `confirmEmails` lệch thì bị từ chối; chạy xong Admin có 89/89, các vai trò khác không đổi.

### PQ-28: Cổng kỹ thuật cho migration và công cụ
- Đổi `/migration/*` và công cụ chạy lại số liệu từ đăng nhập root sang cổng kỹ thuật: khoá riêng lưu ở cấu hình server, ký request như API ngoài, không dùng chung khoá với API ngoài.
- Không có giao diện, không có mã quyền, Admin không gọi được.
- Thao tác ghi nhật ký dưới tài khoản `isGenerate`, kèm tên công cụ.
- Runbook đang dùng `curl` với token root phải sửa theo.

**Nghiệm thu:** gọi không có khoá hoặc bằng token nhân sự bị từ chối; gọi đúng khoá chạy được khi root đã khoá.

### PQ-29: Xoá code giao diện Xác thực CCCD
Màn hình này không mở được, nên xoá hẳn khỏi `admin/`:
- Thư mục `src/pages/identification` (7 file).
- `src/services/identification.ts` và dòng export trong `src/services/index.ts`.
- Mục `identification` trong `src/configs/api.ts` và `src/configs/app.ts`.
- Nhãn `menu.identification` trong `src/locales/vi-VN/menu.ts`.
- Các dòng route đã comment trong `config/routes.ts`.

Giữ `identificationNumber` trong `src/pages/user/type.d.ts`, vì đó là trường của người dùng, không thuộc màn hình này.

Không đụng luồng creator gửi giấy tờ (`creator-app`, `pkg/public`). Ba API `/identifications` phía backend chờ câu 8 ở mục 9.

**Nghiệm thu:** tìm `identification` trong `admin/src` chỉ còn `identificationNumber`; admin build được; không còn menu hay route nào liên quan.

### Không đổi
- Luật tiền vẫn giữ: sửa tiền của khoản đã duyệt thì khoản về "Chờ duyệt", kể cả với Admin. Ngoại lệ dành cho root ở `checkBonusUpdate` không còn ai dùng sau khi khoá root.
- Vẫn không bắt buộc tách người lập và người duyệt (chốt 29/10).
- Một người một vai trò.

---

## 5. Thứ tự bắt buộc

1. Chuyển người ra khỏi `admin` trước, rồi mới chạy migration nâng Admin. Nếu chạy trước, mọi người đang giữ `admin` đều có đủ quyền.
2. Có Admin đích danh và thử xong, rồi mới khoá root.
3. Từ khi deploy đến khi gán xong nên làm trong cùng một ngày, vì trong khoảng đó admin không ADV sửa được site của mọi ADV (phiên bản trước tháng 10 đang chặn việc này).

**Nếu biz chưa chốt ma trận:** dừng sau bước 2 ở mục 6. Admin chưa đủ quyền và root vẫn mở, hệ thống chạy như phiên bản hiện tại.

---

## 6. Thao tác khi lên phiên bản tháng 11

**Chuẩn bị trước deploy**

| Việc | Ai | Xong khi |
|---|---|---|
| Lấy danh sách nhân sự production bằng lệnh dưới | DISO | Có danh sách từng người |
| Kiểm tra có tài khoản `isGenerate`. Không có thì dừng, vì việc nền đang dựa vào nó | DISO | Có đúng tài khoản hệ thống |
| Chốt ma trận mục 3.4 cho Quản lý vận hành và Quản lý ADV | Biz | Không còn cột "đề xuất" |
| Chốt danh sách Admin và bảng gán: mỗi tài khoản một vai trò và phạm vi. Không tự suy được, vì Admin hệ thống và Quản lý vận hành đều là "admin không ADV" | Biz, Vinh | Bảng được duyệt |

```
db.staffs.aggregate([{$match:{active:true}},{$lookup:{from:"roles",localField:"role",foreignField:"_id",as:"r"}},{$project:{_id:0,email:1,isRoot:1,isGenerate:1,partner:1,role:{$arrayElemAt:["$r.code",0]}}},{$sort:{role:1}}])
```

**Sau deploy, với `ROOT_LOGIN_ENABLED=true`**

| Bước | Ai | Làm gì | Kiểm tra |
|---|---|---|---|
| 1 | DISO | Deploy. Vai trò và quyền tự gieo lúc khởi động | Log `rbac-v1` đến `rbac-v5` không lỗi; admin cũ vẫn đăng nhập được, vẫn 70 mã |
| 2 | Root | Chạy `POST /migration/rbac-staff-scope` với `dryRun`, xem `GET /migration/jobs/:id`, rồi chạy thật | `db.staffs.countDocuments({isRoot:{$ne:true},partnerScope:{$in:[null,""]}})` bằng 0 |
| 3 | Root | Trên màn Vai trò: chỉnh bộ quyền `ops_manager`, tạo vai trò Quản lý ADV theo ma trận biz đã chốt | Hai vai trò đúng ma trận |
| 4 | Root | Trên màn Nhân viên: chuyển từng người theo bảng gán. Admin có ADV sang Quản lý ADV; trưởng nhóm vận hành sang Quản lý vận hành | Chỉ còn người trong danh sách Admin giữ `admin` |
| 5 | Root | Đổi Admin còn lại sang phạm vi Mọi ADV nếu chưa có | Đúng danh sách, đúng phạm vi |
| 6 | DISO | Chạy `POST /migration/rbac-admin-full` với `dryRun`, đối chiếu danh sách, rồi chạy thật với `confirmEmails` | Admin có 89/89 mã |
| 7 | Root | Các tài khoản root đích danh: bỏ cờ root, gán vai trò theo bảng | Chỉ còn tài khoản `isGenerate` có `isRoot` |
| 8 | Admin | Đăng nhập, thử: tạo vai trò, mời người, sửa ADV, khoá rồi mở khoá một creator thử | Tất cả chạy được không cần root |
| 9 | DISO | Đặt `ROOT_LOGIN_ENABLED=false`, khởi động lại | Root không đăng nhập được; việc nền vẫn chạy |
| 10 | Admin | Theo dõi 7 ngày | Không có lần đăng nhập root nào; mọi việc vận hành làm được |

**Nếu có sự cố trước bước 9:** root vẫn đăng nhập được, sửa tiếp trên giao diện. **Sau bước 9:** không mở lại root; mất Admin thì dùng mục 7.

---

## 7. Khôi phục khi không còn Admin

Không mở lại đăng nhập root. Nếu không còn Admin nào dùng được:

1. Người được chỉ định duyệt (mục 9) ghi lại lý do.
2. DISO chạy lệnh phía server gán vai trò Admin cho người được duyệt.
3. Ghi nhật ký, thông báo cho các bên liên quan.

---

## 8. Ngoài phạm vi

- Đổi 6 vai trò còn lại: giữ nguyên hiện trạng, Admin tự rà soát và chỉnh trên màn Vai trò khi cần.
- Tạo màn hình và mã quyền cho các việc ở mục 3.3.
- Tách khoá API ngoài; đổi danh tính API ngoài trong nhật ký.
- File rút tiền bản che.
- Ghi thêm nhật ký cho xoá nội dung, duyệt CCCD, thưởng sự kiện, tải file.
- Màn tổng hợp nhật ký thao tác.

---

## 9. Cần chốt

| # | Câu hỏi | Đề xuất | Ai chốt |
|---|---|---|---|
| 1 | Phiên bản tháng 11 làm trong #312 hay PR riêng? | PR riêng ngay sau #312, để khỏi chạy lại toàn bộ QA của #312. Khi đó mục 6 áp cho bản PR riêng, còn bước 2 chạy sau khi #312 lên | Vinh |
| 2 | Danh sách Admin | Ít người nhất có thể, đích danh, có người dự phòng | Biz, Vinh |
| 3 | Bộ quyền Quản lý vận hành và Quản lý ADV (mục 3.4) | Như cột đề xuất của ma trận | Biz |
| 4 | Có bắt buộc MFA trước khi khoá root không? | Nên có. Admin toàn quyền mà hiện chỉ đăng nhập bằng mật khẩu. Không kịp thì làm ticket riêng ngay sau đó và ghi nhận rủi ro | Vinh |
| 5 | Ai duyệt khôi phục Admin (mục 7)? | Một người ngoài nhóm Admin | Vinh, AT |
| 6 | AT có đồng ý thay đổi không? PRD cũ ghi AT giữ root | Hỏi AT trước khi deploy | Vinh |
| 7 | Có ai đang gọi các API ở mục 3.3 bằng tay không? | Team dev kiểm tra; nếu có thì chuyển sang cổng kỹ thuật (PQ-28) | Team dev |
| 8 | Có xoá luôn 3 API `/identifications` phía backend không? Creator vẫn gửi giấy tờ ở trạng thái chờ, và mình chỉ thấy `PATCH /identifications/:id/status` chuyển sang hoàn tất hoặc từ chối | Chưa xoá. Team dev kiểm tra còn hồ sơ chờ không và luồng nào cần hồ sơ đã duyệt, rồi mới chốt | Vinh, Team dev |

---

## 10. Tài liệu cũ cần sửa khi PRD này được chốt

| Tài liệu | Đoạn | Sửa thành |
|---|---|---|
| PRD 05/10 | Mục 3, dòng "Admin hiện có", "Root (AT)" | Vai trò và mục tiêu ở mục 2 tài liệu này |
| PRD 05/10 | Mục 4.2, mô tả Root và Admin; bỏ "không cấp cho người mới" | Mục 2 tài liệu này |
| PRD 05/10 | Mục 5.3, bảng "Không có mã quyền, chỉ root" | Chỉ còn các việc ở mục 3.3 |
| PRD 05/10 | PQ-14 (không cấp Admin cho người mới), PQ-16 | PQ-22, PQ-23, PQ-24 |
| `vai-tro-va-quyen` | Mục 1, 2, 3, 5.1, 6 | Thêm 14 mã, cột vai trò Quản lý ADV, root không đăng nhập |
| `vai-tro-va-quyen` | Mục 7 #3 Lộ trình Admin | Đã chốt: Admin là vai trò lâu dài |
