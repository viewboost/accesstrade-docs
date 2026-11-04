# Phân quyền admin Ambassador — vai trò và quyền

Hệ thống có **8 vai trò** và **89 mã quyền**, cộng tài khoản **root** đứng ngoài mô hình.

**Cập nhật 04/11 theo [PRD Root, Admin và vai trò quản lý](prd-root-admin-va-vai-tro-quan-ly-2026-11-02.md) (PR #38, chờ chốt) và code PR #333 (chờ nghiệm thu):** thêm 14 mã thay cho các việc trước đây chỉ root làm (75 → 89 mã); Admin là vai trò quản trị lâu dài, đủ 89 mã; root thành tài khoản hệ thống, không ai đăng nhập. Phiên bản đang chạy trước #333 vẫn là 75 mã, root đăng nhập được.

Một thao tác được phép khi: nhân sự đang hoạt động, chưa hết hạn **và** vai trò đang hoạt động, có mã quyền của thao tác **và** bản ghi thuộc ADV trong phạm vi của nhân sự.

## 1. Vai trò

| Vai trò | Viết tắt | Mã | Ai dùng | Phạm vi ADV | Số quyền |
|---|---|---|---|---|:-:|
| Root | — | (cờ trên tài khoản, không phải vai trò) | Tài khoản hệ thống (`isGenerate`) cho việc nền và nhật ký. **Không ai đăng nhập** (mục 5.1) | Mọi ADV | Tất cả |
| Quản lý vận hành | QLVH | `ops_manager` | Trưởng nhóm vận hành | ADV mình phụ trách | 30 |
| Vận hành nội dung | VHND | `ops_content` | Nhân viên duyệt nội dung | ADV được giao | 15 |
| Vận hành hiệu suất | VHHS | `ops_performance` | Nhân viên theo dõi hiệu suất | ADV được giao | 19 |
| Duyệt chi | Duyệt chi | `payout_approver` | Người chốt tiền, biz chỉ định | ADV được giao, Admin đặt | 14 |
| Kỹ thuật hỗ trợ | KTHT | `tech_support` | Đội kỹ thuật AT và đối tác | Đội AT: mọi ADV; đối tác: chờ chốt (mục 7) | 27 |
| Cấu hình ứng dụng | CHUD | `config_editor` | Người dựng site ADV | ADV mình dựng (ít nhất 1) | 19 |
| Cộng tác viên | CTV | `collaborator` | Người duyệt nội dung (hiện gần như không dùng) | ADV được giao | 6 |
| Admin | Admin | `admin` | Người chịu trách nhiệm hệ thống, đích danh; được có nhiều người, luôn còn ít nhất 1 | Bắt buộc Mọi ADV, không có hạn dùng | 89 (gieo 70, nhận thêm 19 qua migration, mục 4) |
| Quản lý ADV | — | (chưa có) | Người đang giữ `admin` có gắn ADV | Danh sách ADV | Chờ biz chốt (PRD #38 mục 3.4 đề xuất 68) |

Quản lý ADV không gieo sẵn: Admin tạo trên màn Vai trò sau khi biz chốt bộ quyền. Bộ quyền QLVH cũng chờ biz chốt lại theo PRD #38 mục 3.4 (đề xuất 52 mã); bảng dưới là bộ gieo sẵn hiện tại.

## 2. Tóm tắt quyền

**Nguyên tắc chung**
- Có quyền sửa / import / xuất / duyệt của một chức năng thì tự có quyền xem chức năng đó. Một số quyền còn tự kéo theo quyền tra cứu mà hộp của nó cần: `bonus.view` → `event.view`; `bonus.edit` → `creator.view`; `mission.edit` → `category.view`; `user_segment.edit` → `creator.view`.
- **Không bắt buộc tách người lập và người duyệt khoản chi** (chốt 29/10, [comment #312](https://github.com/AT-Core/ambassador/pull/312#issuecomment-6487523688); code #312 đang gỡ phần chặn). Một vai trò được giữ cả hai nhóm quyền, một người duyệt được khoản do mình tạo, giống production. Vai trò mặc định vẫn tách: VHHS lập, Duyệt chi duyệt; Admin có cả hai.
  - Nhóm lập: `bonus.edit`, `bonus.import`, `bonus.cancel`, `reconciliation.create`, `reconciliation.cancel_item`, `transfer.create`.
  - Nhóm duyệt: `bonus.approve`, `reconciliation.change_status`, `transfer.change_status`.
  - Hai nhóm này vẫn dùng cho **luật quản lý tài khoản**: người mang vai trò có quyền nhóm lập không mời, sửa hay gán được vai trò có quyền nhóm duyệt.
- **Dữ liệu cá nhân của creator:**
  - SĐT, email: chỉ người có `user.view_contact` thấy (QLVH, VHND, Admin); người khác không thấy. Riêng ô tìm creator ở bảng xếp hạng, người không có quyền vẫn thấy 4 số cuối SĐT để phân biệt creator trùng tên.
  - Nhật ký xem SĐT, email hiện **chỉ ghi khi mở chi tiết creator**. Người có `user.view_contact` còn thấy SĐT, email ở các bảng Creator (Danh sách creator, Duyệt Creator), Sự kiện › Duyệt sự kiện, Hồ sơ, Quà tặng › Lịch sử đổi quà, Thông số › CBNV, Lịch sử đăng nhập và file xuất người dùng ADV, kênh creator — các chỗ này không ghi nhật ký.
  - CCCD, mã số thuế, ngân hàng: người có `user.view_sensitive` (Admin) và hệ thống AT qua API ngoài (mục 5.5) thấy đầy đủ, mỗi lần mở chi tiết người dùng được ghi nhật ký; người khác thấy bản che (CCCD/MST 3 ký tự cuối, số thẻ 4 số cuối, không thấy chủ thẻ).
- **Mã toàn hệ thống** chỉ có tác dụng với nhân sự phạm vi Mọi ADV; người phạm vi danh sách ADV lỡ được tick thì hệ thống bỏ qua các mã này: `role.view`, `role.edit`, `staff.assign_all_scope`, `staff.reset_password`, `partner.create`, `partner.edit`, `user_partner.edit_wildrift`, `creator.create`, `creator.ban`, `contract.view`, `contract.reject`, `audit.view_system`.
- **Chống tự nâng quyền:** người có `role.edit` chỉ tick được mã chính họ đang có; vai trò Admin không bỏ được `role.view`, `role.edit`, `staff.view`, `staff.invite`, `staff.edit`, `staff.assign_all_scope`; không tắt hay đổi vai trò được Admin cuối cùng đang hoạt động; chỉ người có đủ quyền của Admin mới gán được Admin.
  - **Ngoại lệ — file rút tiền:** file chuyển khoản gửi ngân hàng chứa **đủ CCCD, MST, SĐT và số thẻ**, không che. Ai có `transfer.export` đều tải được: QLVH, VHHS, Duyệt chi, Admin (cần chốt, mục 7).
- Token đăng nhập mạng xã hội của creator: không ai thấy, kể cả root.

| Vai trò | Làm được | Không làm được |
|---|---|---|
| Root | Việc nền của hệ thống (tự từ chối video, gắn tag cảnh báo, chạy file xuất) | Đăng nhập (khi `ROOT_LOGIN_ENABLED=false`) |
| Quản lý vận hành | Mọi việc của VHND và VHHS; xem nhật ký thao tác, lịch sử đăng nhập; mời, đổi vai trò, tắt tài khoản nhân sự VHND/VHHS trong ADV mình | Duyệt chi; sửa tài khoản Duyệt chi, KTHT, Admin, QLVH khác; xoá nội dung |
| Vận hành nội dung | Duyệt, từ chối, ghim nội dung, gắn cảnh báo, cộng trừ tay lượt xem; duyệt creator đăng ký sự kiện và người dùng vào ADV; xem SĐT, email creator; xuất và tải file nội dung | Việc tiền; sửa sự kiện; xoá nội dung |
| Vận hành hiệu suất | Xem thống kê, bảng xếp hạng; lập thưởng thêm (tạo, sửa, import, huỷ); từ chối mục đối soát không hợp lệ; tải file đối soát, rút tiền; xuất nội dung, thống kê | Duyệt chi (kể cả khoản mình lập); duyệt nội dung; xem SĐT, email; xoá nội dung |
| Duyệt chi | Duyệt, từ chối thưởng thêm; lấy danh sách, duyệt, huỷ cả bản đối soát; duyệt, từ chối đợt rút và lệnh rút; xem màn tiền; tải file đối soát, rút tiền | Tạo, sửa, huỷ khoản thưởng; từ chối mục trong đối soát; lập đối soát, đợt rút |
| Kỹ thuật hỗ trợ | Chỉ xem mọi màn nghiệp vụ trong phạm vi ADV được giao | Mọi thao tác ghi; xem SĐT, email; tải file; xem nhân sự |
| Cấu hình ứng dụng | Cấu hình, xuất bản, khôi phục site; tin tức, bài viết, kênh hỗ trợ, affiliate; tạo, sửa sự kiện và mẫu sự kiện | Việc tiền; duyệt nội dung |
| Cộng tác viên | Duyệt nội dung; cộng trừ tay lượt xem của bài | Mọi việc khác |
| Admin | Mọi thao tác trên giao diện admin: vai trò, nhân sự (kể cả mời Admin, Duyệt chi), ADV, khoá creator, hợp đồng, xem đủ CCCD/MST/ngân hàng, nhật ký hệ thống, mọi nghiệp vụ cả lập lẫn duyệt chi | Xoá nội dung và các API không có màn hình (mục 3, "Không có mã quyền") |

## 3. Danh sách quyền

✔ = có · ô trống = không.

| # | Mã quyền | Tên | Cho phép làm gì | QLVH | VHND | VHHS | Duyệt chi | KTHT | CHUD | CTV | Admin |
|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | **Nội dung** | | | | | | | | | | |
| 1 | `content.view` | Xem nội dung | Xem danh sách, chi tiết, số liệu nội dung creator đã đăng | ✔ | ✔ | ✔ |  | ✔ |  | ✔ | ✔ |
| 2 | `content.moderate` | Duyệt nội dung | Duyệt, từ chối (từng bài và theo lô), ghim, gắn tag cảnh báo, cập nhật số liệu một nội dung | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| 3 | `content_manual_flow.view` | Xem cộng trừ lượt xem thủ công | Xem các lần cộng, trừ tay lượt xem của một bài (tab Cộng trừ thủ công) | ✔ | ✔ |  |  | ✔ |  | ✔ | ✔ |
| 4 | `content_manual_flow.edit` | Cộng trừ lượt xem thủ công | Cộng hoặc trừ tay lượt xem của một bài; có thể làm đổi thưởng tính theo lượt xem | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| | **Người dùng và creator** | | | | | | | | | | |
| 5 | `user.view_contact` | Xem liên hệ creator | Thấy số điện thoại, email creator ở mọi bảng và file xuất, mở trang chi tiết creator. Chỉ lượt mở trang chi tiết được ghi nhật ký | ✔ | ✔ |  |  |  |  |  | ✔ |
| 6 | `creator.view` | Xem hồ sơ creator | Danh sách và chi tiết hồ sơ creator, thống kê hồ sơ và bộ lọc tìm creator | ✔ | ✔ | ✔ | ✔ | ✔ |  |  | ✔ |
| 7 | `creator.edit` | Sửa hồ sơ creator | Đổi trạng thái hồ sơ, cập nhật chỉ số, cấu hình điều kiện hồ sơ |  |  |  |  |  |  |  | ✔ |
| 8 | `creator.approve` | Duyệt đăng ký sự kiện | Duyệt hoặc từ chối yêu cầu tham gia sự kiện của creator (tab Duyệt sự kiện) | ✔ | ✔ |  |  |  |  |  | ✔ |
| 9 | `partner_member.approve` | Duyệt thành viên ADV | Duyệt hoặc từ chối yêu cầu tham gia ADV của người dùng (tab Duyệt Creator) | ✔ | ✔ |  |  |  |  |  | ✔ |
| 10 | `user_partner.view` | Xem người dùng ADV | Xem người dùng thuộc ADV: trạng thái CBNV, số dư, đã rút, ngân hàng và MST đã che |  |  |  |  | ✔ |  |  | ✔ |
| 11 | `user_partner.edit_staff_status` | Đổi trạng thái CBNV | Đánh dấu / bỏ đánh dấu người dùng ADV là nhân viên của thương hiệu |  |  |  |  |  |  |  | ✔ |
| | **Sự kiện và thống kê** | | | | | | | | | | |
| 12 | `event.view` | Xem danh sách sự kiện | Danh sách sự kiện (dùng cả ở ô chọn sự kiện khi duyệt nội dung) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 13 | `event.view_detail` | Xem chi tiết sự kiện | Chi tiết sự kiện, yêu cầu, ngân sách, bảng xếp hạng | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| 14 | `event.edit` | Quản lý sự kiện | Tạo, sửa, nhân bản, bật/tắt sự kiện; yêu cầu, ngân sách, opshub; cấu hình và ghim bảng xếp hạng |  |  |  |  |  | ✔ |  | ✔ |
| 15 | `event_schema.view` | Xem mẫu sự kiện | Danh sách mẫu sự kiện |  |  |  |  | ✔ | ✔ |  | ✔ |
| 16 | `event_schema.edit` | Quản lý mẫu sự kiện | Tạo, sửa, bật/tắt mẫu sự kiện dùng để dựng sự kiện |  |  |  |  |  | ✔ |  | ✔ |
| 17 | `statistic.view` | Xem thống kê | Thông số, Thông số cũ, thống kê theo nhân viên (CBNV), biểu đồ, báo cáo | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| | **Thưởng, nhiệm vụ, quà** | | | | | | | | | | |
| 18 | `bonus.view` | Xem thưởng thêm | Danh sách và chi tiết các khoản thưởng thêm | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 19 | `bonus.edit` | Cộng thưởng thêm | Tạo, sửa một khoản thưởng thêm cho creator | ✔ |  | ✔ |  |  |  |  | ✔ |
| 20 | `bonus.import` | Import thưởng thêm | Cộng thưởng hàng loạt bằng file Excel; dòng ngoài phạm vi ADV bị từ chối kèm lý do | ✔ |  | ✔ |  |  |  |  | ✔ |
| 21 | `bonus.cancel` | Huỷ thưởng thêm | Huỷ một khoản thưởng thêm đã tạo | ✔ |  | ✔ |  |  |  |  | ✔ |
| 22 | `bonus.approve` | Duyệt thưởng thêm | Duyệt hoặc từ chối khoản thưởng thêm do nhóm lập tạo |  |  |  | ✔ |  |  |  | ✔ |
| 23 | `mission.view` | Xem nhiệm vụ | Danh sách và chi tiết nhiệm vụ, danh sách điểm chờ duyệt |  |  |  |  | ✔ |  |  | ✔ |
| 24 | `mission.edit` | Quản lý nhiệm vụ | Tạo, sửa nhiệm vụ |  |  |  |  |  |  |  | ✔ |
| 25 | `mission.approve` | Duyệt điểm nhiệm vụ | Duyệt hoặc từ chối điểm creator nhận từ nhiệm vụ |  |  |  |  |  |  |  | ✔ |
| 26 | `gift.view` | Xem quà | Danh sách quà, chi tiết, lịch sử đổi quà |  |  |  |  | ✔ |  |  | ✔ |
| 27 | `gift.edit` | Quản lý quà | Tạo, sửa, bật/tắt quà |  |  |  |  |  |  |  | ✔ |
| 28 | `gift.process` | Xử lý đổi quà | Duyệt / từ chối lượt đổi quà của creator |  |  |  |  |  |  |  | ✔ |
| | **Đối soát, rút tiền, xuất** | | | | | | | | | | |
| 29 | `reconciliation.view` | Xem đối soát | Danh sách và chi tiết bản đối soát với các tab Tổng quan, Nội dung, Nhiệm vụ, Thưởng thêm | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 30 | `reconciliation.create` | Tạo bản đối soát | Tạo, sửa thông tin bản đối soát |  |  |  |  |  |  |  | ✔ |
| 31 | `reconciliation.cancel_item` | Từ chối từng mục trong đối soát | Nút Từ chối trên từng dòng Chờ duyệt (tab Nội dung, Nhiệm vụ, Thưởng thêm) để loại một khoản khỏi bản đối soát, kèm lý do. Không phải nút Hủy đối soát ở đầu trang | ✔ |  | ✔ |  |  |  |  | ✔ |
| 32 | `reconciliation.change_status` | Lấy danh sách, duyệt, hủy cả bản đối soát | Các nút đầu trang chi tiết: Lấy danh sách, Duyệt tất cả, Hủy đối soát (cả bản) |  |  |  | ✔ |  |  |  | ✔ |
| 33 | `reconciliation.export` | Tải file đối soát | Tạo yêu cầu xuất và tải file đối soát; file luôn mang ADV của bản đối soát | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 34 | `transfer.view` | Xem rút tiền | Danh sách, chi tiết đợt rút và danh sách lệnh rút bên trong | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 35 | `transfer.create` | Tạo đợt rút tiền | Tạo, sửa đợt rút tiền |  |  |  |  |  |  |  | ✔ |
| 36 | `transfer.export` | Tải file rút tiền | Tạo yêu cầu xuất và tải file rút tiền | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 37 | `transfer.change_status` | Xử lý rút tiền | Đổi trạng thái đợt rút, từ chối lệnh rút |  |  |  | ✔ |  |  |  | ✔ |
| 38 | `export.view` | Xem dữ liệu xuất | Xem danh sách file đã xuất. Tải từng file cần quyền tải của loại file đó (xem Giải thích quyền) | ✔ | ✔ | ✔ | ✔ |  |  |  | ✔ |
| 39 | `content.export` | Xuất file nội dung | Tạo yêu cầu xuất và tải file nội dung | ✔ | ✔ | ✔ |  |  |  |  | ✔ |
| 40 | `statistic.export` | Xuất file biểu đồ | Tạo yêu cầu xuất và tải file biểu đồ thống kê | ✔ |  | ✔ |  |  |  |  | ✔ |
| 41 | `user_partner.export` | Xuất file người dùng ADV | Tạo yêu cầu xuất và tải file người dùng ADV |  |  |  |  |  |  |  | ✔ |
| 42 | `creator.export` | Xuất file kênh creator | Tạo yêu cầu xuất và tải file kênh mạng xã hội của creator |  |  |  |  |  |  |  | ✔ |
| | **Segment, mã, thông báo, danh mục** | | | | | | | | | | |
| 43 | `segment.view` | Xem segment | Danh sách và chi tiết segment |  |  |  |  | ✔ |  |  | ✔ |
| 44 | `segment.edit` | Quản lý segment | Tạo, sửa, bật/tắt segment |  |  |  |  |  |  |  | ✔ |
| 45 | `user_segment.view` | Xem người dùng trong segment | Danh sách người dùng thuộc segment |  |  |  |  | ✔ |  |  | ✔ |
| 46 | `user_segment.edit` | Sửa người dùng trong segment | Thêm, xoá người dùng khỏi segment |  |  |  |  |  |  |  | ✔ |
| 47 | `user_segment.import` | Import người dùng vào segment | Thêm hàng loạt bằng Excel |  |  |  |  |  |  |  | ✔ |
| 48 | `code.view` | Xem mã | Danh sách mã |  |  |  |  | ✔ |  |  | ✔ |
| 49 | `code.edit` | Quản lý mã | Tạo, xoá mã |  |  |  |  |  |  |  | ✔ |
| 50 | `code.import` | Import mã | Nhập mã hàng loạt bằng Excel |  |  |  |  |  |  |  | ✔ |
| 51 | `notification.view` | Xem thông báo | Danh sách và chi tiết thông báo admin |  |  |  |  | ✔ |  |  | ✔ |
| 52 | `notification.edit` | Soạn thông báo | Tạo, sửa, nhân bản thông báo |  |  |  |  |  |  |  | ✔ |
| 53 | `notification.approve` | Duyệt thông báo | Duyệt (gửi ngay hoặc hẹn giờ) hoặc huỷ bỏ thông báo |  |  |  |  |  |  |  | ✔ |
| 54 | `category.view` | Xem danh mục | Danh sách danh mục | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| 55 | `category.edit` | Quản lý danh mục | Tạo, sửa danh mục |  |  |  |  |  |  |  | ✔ |
| | **Cấu hình ADV và site** | | | | | | | | | | |
| 56 | `app_config.view` | Xem cấu hình ứng dụng | Xem cấu hình site của ADV, bản nháp, lịch sử phiên bản, trạng thái onboarding |  |  |  |  | ✔ | ✔ |  | ✔ |
| 57 | `app_config.edit` | Sửa cấu hình ứng dụng | Sửa bản nháp cấu hình site, bật/tắt tính năng của ADV |  |  |  |  |  | ✔ |  | ✔ |
| 58 | `app_config.publish` | Xuất bản cấu hình | Xuất bản bản nháp lên site đang chạy, khôi phục phiên bản cũ |  |  |  |  |  | ✔ |  | ✔ |
| 59 | `news.view` | Xem tin tức | Danh sách và chi tiết tin tức (gồm banner trang chủ) |  |  |  |  | ✔ | ✔ |  | ✔ |
| 60 | `news.edit` | Quản lý tin tức | Tạo, sửa, nhân bản, bật/tắt tin tức |  |  |  |  |  | ✔ |  | ✔ |
| 61 | `article.view` | Xem bài viết | Danh sách và chi tiết bài viết (gồm ba bài pháp lý) |  |  |  |  | ✔ | ✔ |  | ✔ |
| 62 | `article.edit` | Quản lý bài viết | Tạo, sửa bài viết |  |  |  |  |  | ✔ |  | ✔ |
| 63 | `quick_action.view` | Xem kênh hỗ trợ | Danh sách kênh hỗ trợ của ADV |  |  |  |  | ✔ | ✔ |  | ✔ |
| 64 | `quick_action.edit` | Quản lý kênh hỗ trợ | Tạo, sửa, bật/tắt kênh hỗ trợ |  |  |  |  |  | ✔ |  | ✔ |
| 65 | `affiliate.view` | Xem chiến dịch affiliate | Danh sách, chi tiết chiến dịch và liên kết chiến dịch – sự kiện |  |  |  |  | ✔ | ✔ |  | ✔ |
| 66 | `affiliate.edit` | Quản lý chiến dịch affiliate | Tạo, sửa, bật/tắt chiến dịch, gắn chiến dịch vào sự kiện |  |  |  |  |  | ✔ |  | ✔ |
| | **Hệ thống** | | | | | | | | | | |
| 67 | `tag.view` | Xem tag | Danh sách tag (gồm tag cảnh báo dùng khi duyệt nội dung) | ✔ | ✔ | ✔ |  | ✔ | ✔ | ✔ | ✔ |
| 68 | `tag.edit` | Quản lý tag | Tạo, sửa, bật/tắt tag. Tag dùng chung cần phạm vi Mọi ADV |  |  |  |  |  |  |  | ✔ |
| 69 | `common_config.view` | Xem cấu hình chung | Xem cấu hình dùng chung của hệ thống |  |  |  |  | ✔ |  |  | ✔ |
| 70 | `common_config.edit` | Sửa cấu hình chung | Tạo, sửa, xoá cấu hình chung trong ADV được giao; cấu hình toàn hệ thống cần phạm vi Mọi ADV |  |  |  |  |  |  |  | ✔ |
| 71 | `audit.view` | Xem nhật ký thao tác | Xem nhật ký thao tác chung trong phạm vi ADV của mình (chưa có màn). Lịch sử từng bản ghi không cần quyền này | ✔ |  |  |  | ✔ |  |  | ✔ |
| 72 | `login_history.view` | Xem lịch sử đăng nhập | Xem lịch sử đăng nhập của nhân sự và creator, kèm IP, thiết bị | ✔ |  |  |  | ✔ |  |  | ✔ |
| 73 | `staff.view` | Xem nhân sự | Danh sách và chi tiết nhân sự có phạm vi giao với phạm vi của mình; không thấy root | ✔ |  |  |  |  |  |  | ✔ |
| 74 | `staff.invite` | Mời nhân sự | Mời, mời hàng loạt, gửi lại, thu hồi lời mời — chỉ với vai trò và ADV không vượt quá mình | ✔ |  |  |  |  |  |  | ✔ |
| 75 | `staff.edit` | Sửa nhân sự | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản — chỉ nhân sự nằm trọn trong phạm vi mình | ✔ |  |  |  |  |  |  | ✔ |
| | **14 mã thay cho "chỉ root" (PRD #38, PR #333)** — 🌐 = mã toàn hệ thống, chỉ có tác dụng với phạm vi Mọi ADV | | | | | | | | | | |
| 76 | `user_partner.edit_wildrift` 🌐 | Sửa thông tin Wild Rift | Sửa cấp, follower, điểm Wild Rift của người dùng ADV |  |  |  |  |  |  |  | ✔ |
| 77 | `creator.create` 🌐 | Tạo người dùng | Tạo tài khoản người dùng từ admin |  |  |  |  |  |  |  | ✔ |
| 78 | `creator.ban` 🌐 | Khoá, mở khoá creator | Khoá hoặc mở khoá tài khoản creator |  |  |  |  |  |  |  | ✔ |
| 79 | `contract.view` 🌐 | Tải hợp đồng | Tải file hợp đồng của creator (có CCCD, số thẻ) |  |  |  |  |  |  |  | ✔ |
| 80 | `contract.reject` 🌐 | Từ chối hợp đồng | Từ chối hợp đồng creator đã ký |  |  |  |  |  |  |  | ✔ |
| 81 | `user.view_sensitive` | Xem đủ CCCD, mã số thuế, số thẻ | Thấy bản đầy đủ thay vì bản che ở mọi bảng, chi tiết và file xuất; mỗi lần xem chi tiết người dùng được ghi nhật ký |  |  |  |  |  |  |  | ✔ |
| 82 | `partner.create` 🌐 | Tạo ADV | Tạo ADV mới |  |  |  |  |  |  |  | ✔ |
| 83 | `partner.edit` 🌐 | Quản lý ADV | Menu ADV: sửa thông tin, tên miền, ngân sách, bật/tắt ADV |  |  |  |  |  |  |  | ✔ |
| 84 | `staff.create` | Tạo nhân sự trực tiếp | Tạo nhân sự kèm mật khẩu, không qua thư mời — cùng luật vai trò và phạm vi như mời |  |  |  |  |  |  |  | ✔ |
| 85 | `staff.reset_password` 🌐 | Đổi mật khẩu, email nhân sự khác | Đặt mật khẩu mới hoặc đổi email cho nhân sự mình sửa được |  |  |  |  |  |  |  | ✔ |
| 86 | `staff.assign_all_scope` 🌐 | Gán phạm vi Mọi ADV | Giao phạm vi Mọi ADV và sửa nhân sự có phạm vi Mọi ADV |  |  |  |  |  |  |  | ✔ |
| 87 | `role.view` 🌐 | Xem vai trò | Màn Vai trò: xem đủ vai trò, chi tiết quyền, số nhân sự |  |  |  |  |  |  |  | ✔ |
| 88 | `role.edit` 🌐 | Quản lý vai trò | Tạo, sửa, bật/tắt vai trò; chỉ tick được mã mình đang có |  |  |  |  |  |  |  | ✔ |
| 89 | `audit.view_system` 🌐 | Xem nhật ký hệ thống | Thấy nhật ký về vai trò, lần đăng nhập root và tài khoản root |  |  |  |  |  |  |  | ✔ |
| | **Tổng** | | | 30 | 15 | 19 | 14 | 27 | 19 | 6 | 89 |

Cột Tên và Cho phép làm gì lấy đúng nhãn và mô tả trong code (`constants.Permissions`), là chữ hiện trên màn tick quyền. Trên màn tick quyền, 14 mã mới nằm trong nhóm chức năng của chúng (Người dùng và creator, Cấu hình ADV và site, Hệ thống), không thành nhóm riêng; số 76–89 ở đây chỉ để giữ nguyên số của 75 mã cũ. `user_segment.import` bị **ẩn trên màn tick quyền** vì chưa có nút trên giao diện; mã vẫn hợp lệ, Admin có sẵn từ lúc gieo.

**Cột Admin:** lúc gieo Admin có 70 mã như cũ. Thêm 19 mã (14 mã mới, `staff.view`, `staff.invite`, `staff.edit`, `quick_action.view`, `quick_action.edit`) bằng migration chạy tay `POST /migration/rbac-admin-full` (mục 4), không tự cấp lúc deploy. Kỹ thuật hỗ trợ không nhận `role.view` và `contract.view` dù có đuôi `.view`, vì hợp đồng có CCCD và số thẻ.

**Không có mã quyền (không có màn hình trên admin):** chỉ root gọi được, mà root không còn đăng nhập, nên sau khi khoá root thì không ai gọi được qua đăng nhập. Có màn hình thì phải thêm mã quyền cùng lúc.
- Hợp đồng, eKYC: tạo hợp đồng theo người dùng (`POST /users/contract/generate-by-user-id`), sửa eKYC (`PUT /users/update-ekyc`).
- Xác thực CCCD (`/identifications`, 3 API). Code giao diện đã xoá; API backend giữ, chờ chốt (PRD #38 mục 9 câu 8).
- Thưởng sự kiện: đổi trạng thái, xoá, từ chối (`POST /event-reward/change-status`, `DELETE /event-reward/:id`, `POST /events/reject-reward-event`). Khác với từ chối mục trong đối soát, việc đó có mã `reconciliation.cancel_item`.
- **Xoá nội dung** (xoá cứng, kéo theo thưởng sự kiện và số liệu; nội dung đã vào đối soát thì không xoá được). Cần chốt, mục 7.
- Cấp cờ root mới: không ai làm được, kể cả root. Trên form nhân sự chỉ còn tắt được cờ root.

**Đi qua cổng kỹ thuật** (khoá HMAC riêng `OPS_GATE_CLIENT_ID` / `OPS_GATE_SECRET_KEY`, không có giao diện, Admin không gọi được; mỗi lần gọi ghi nhật ký dưới tài khoản hệ thống):
- Mọi route `/migration/*` (chạy migration, backfill dữ liệu).
- 6 công cụ chạy lại số liệu: chạy lại analytic, cập nhật dữ liệu sự kiện, chạy lại thưởng sự kiện, đổi danh mục sự kiện, cập nhật hàng loạt trạng thái / tag cảnh báo nội dung.

**Không cần đăng nhập:** đăng nhập; xác minh và nhận lời mời; quên, đặt lại mật khẩu.

**Cần đăng nhập, không cần mã quyền:** thông tin tài khoản của mình (`/staffs/me`); đổi mật khẩu của mình; danh sách ADV cho ô chọn (`GET /partners`, tự lọc theo phạm vi); danh sách phạm vi (`GET /common/scopes`).

## 4. Gán người khi triển khai

Biz ký bảng này **trước khi deploy**. Mỗi tài khoản đang hoạt động một dòng. DISO đổ sẵn 4 cột đầu từ DB production; biz điền các cột còn lại.

| Tài khoản (email) | Vai trò hôm nay | ADV hôm nay | Root | Vai trò mới | Phạm vi (mọi ADV / danh sách) | ADV phụ trách | Hạn dùng | Người duyệt |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Nếu deploy mà chưa có bảng này:
- Nhân sự không gắn ADV tự thành phạm vi **mọi ADV** (đã chốt 07/10, root rà lại sau deploy). Ngoại lệ: vai trò **Cấu hình ứng dụng** chưa gắn ADV thì phạm vi rỗng, **không đăng nhập được** cho tới khi được giao ít nhất 1 ADV.
- Ai mang vai trò đã ngừng sẽ **không đăng nhập được**.
- Một số người mất việc quen làm, ví dụ Admin, CTV, Cấu hình ứng dụng **không còn thấy CCCD, MST, số thẻ** của creator; CTV và Cấu hình ứng dụng mất các API ngoài việc (thưởng thêm, duyệt creator, nhật ký, cấu hình chung).

**Lên bản Admin thay root (PR #333) — thứ tự bắt buộc** (chi tiết ở PRD #38 mục 5–6):
1. Biz chốt danh sách Admin, bộ quyền QLVH và Quản lý ADV, bảng gán người.
2. Chuyển người ra khỏi `admin` (trưởng nhóm vận hành sang QLVH, Admin có ADV sang Quản lý ADV); Admin còn lại đặt phạm vi Mọi ADV.
3. Chạy `POST /migration/rbac-admin-full` với `dryRun`, đối chiếu danh sách, rồi chạy thật kèm `confirmEmails` khớp đúng danh sách đang giữ `admin`. Chạy trước bước 2 thì mọi người đang giữ `admin` đều có đủ 89 mã.
4. Bỏ cờ root của các tài khoản root đích danh, gán vai trò theo bảng; chỉ còn tài khoản `isGenerate` có cờ root.
5. Admin thử tạo vai trò, mời người, sửa ADV, khoá rồi mở khoá creator thử.
6. Đặt `ROOT_LOGIN_ENABLED=false` rồi khởi động lại.

## 5. Quản trị tài khoản

### 5.1 Tài khoản root
- **Là gì:** tài khoản hệ thống (`isGenerate`), việc nền dùng để chạy và ghi nhật ký. Giữ cờ `isRoot`, không tắt tài khoản. Không có hạn dùng.
- **Không ai đăng nhập:** cấu hình `ROOT_LOGIN_ENABLED=false` chặn đăng nhập root và chặn cả phiên root đang mở ở request kế tiếp. Chỉ khoá khi ghi rõ `false` / `0` / `no` / `off`; bỏ trống là còn mở. Mở chỉ để chuyển đổi (mục 4), tắt rồi không bật lại để làm việc.
- **Nhật ký:** mỗi lần thử đăng nhập root đúng mật khẩu khi đã khoá được ghi `staff.root_login_blocked`. Người có `audit.view_system` (Admin) xem được dòng đăng nhập root, dòng về tài khoản root và dòng về vai trò. **Chưa gửi cảnh báo đi đâu**, muốn có cần thêm ticket.
- **Không còn Admin nào dùng được:** không mở lại root. Người được chỉ định duyệt ghi lý do, DISO chạy lệnh phía server gán Admin cho người được duyệt, ghi nhật ký. Ai duyệt: chờ chốt (mục 7).

### 5.1b Tài khoản Admin
- Đích danh, được có nhiều người, giữ ít nhất có thể, nên có người dự phòng. Danh sách: biz và anh Vinh chốt.
- Bắt buộc phạm vi Mọi ADV, không có hạn dùng.
- Luôn còn ít nhất 1 Admin đang hoạt động: không tắt hay đổi vai trò được Admin cuối cùng.
- Chỉ đăng nhập bằng mật khẩu, chưa có MFA (chờ chốt, mục 7).

### 5.2 Hạn dùng tài khoản
| Loại tài khoản | Hạn mặc định | Ai gia hạn |
|---|---|---|
| Nội bộ AT | Chờ chốt | Chờ chốt |
| Đối tác (kể cả KTHT phía đối tác) | Chờ chốt — bắt buộc có hạn | Chờ chốt |
| Cộng tác viên | Chờ chốt | Chờ chốt |

**Nhắc hết hạn:** hệ thống **chưa gửi nhắc**. Người phụ trách tự lọc **"Sắp hết hạn"** (còn ≤ 7 ngày hoặc đã quá hạn) trên màn Nhân viên. Muốn có email nhắc thì cần ticket (mục 7).

### 5.3 Cấp và thu hồi quyền
Bảng dưới là đề xuất, chờ biz chốt.

| Vai trò | Ai đề xuất | Ai duyệt | Ai thao tác trên hệ thống |
|---|---|---|---|
| Vận hành nội dung, Vận hành hiệu suất | Quản lý vận hành | Quản lý vận hành | Quản lý vận hành |
| Quản lý vận hành | Biz | Biz | Admin |
| Duyệt chi | Biz | Biz | Admin |
| Kỹ thuật hỗ trợ (AT) | Đội kỹ thuật AT | AT | Admin |
| Kỹ thuật hỗ trợ (đối tác) | Đối tác | AT | Admin, bắt buộc có hạn dùng |
| Cấu hình ứng dụng, Cộng tác viên | Chờ chốt | Chờ chốt | Admin |
| Admin | Biz, anh Vinh | Biz, anh Vinh | Admin |
| Quản lý ADV | Biz | Biz | Admin |
| **Người nghỉ việc** | Quản lý trực tiếp báo | — | QLVH tắt với VHND/VHHS; Admin tắt với vai trò khác; thời hạn: chờ chốt |

Tắt tài khoản, đổi vai trò hay đổi phạm vi **có hiệu lực ngay từ thao tác kế tiếp** của người đó: mỗi request hệ thống đều đọc lại nhân sự và vai trò từ DB, kể cả dịch vụ tải file.

### 5.4 Rà soát quyền định kỳ
- Tần suất: chờ chốt (đề xuất hằng tháng).
- Quản lý vận hành rà người trong đội mình; Admin rà Admin, Duyệt chi, Kỹ thuật hỗ trợ, Cấu hình ứng dụng, Quản lý ADV.
- Dùng màn Nhân viên (lọc vai trò, phạm vi, sắp hết hạn) và nhật ký thao tác, lịch sử đăng nhập.

### 5.5 Ranh giới với API ngoài của AT
AT gọi **API ngoài bằng khoá API**, với quyền ngang root:
- **Ghi tiền:** tạo, sửa bản đối soát và đợt rút; đổi trạng thái đối soát, mục đối soát, đợt rút, lệnh rút.
- **Đọc dữ liệu cá nhân không che:** danh sách người dùng (`GET /users`) trả đủ CCCD, MST; lệnh rút của một đợt (`GET /transfers/:id/withdraw-cashes`) trả đủ số thẻ, chủ thẻ; tạo file xuất (`POST /data-exports`).

## 6. Tiêu chí thành công sau release
- Số tài khoản có cờ root: **đúng 1**, là tài khoản hệ thống `isGenerate`.
- `ROOT_LOGIN_ENABLED=false` trên production; không có lần đăng nhập root nào.
- **7 ngày liền** sau khi khoá root, mọi việc vận hành làm được bằng Admin và các vai trò khác.

## 7. Điểm còn chờ chốt

| # | Câu hỏi | Phương án | Ai chốt |
|---|---|---|---|
| 1 | **Xoá nội dung** — PRD giao cho QLVH và VHHS, hiện không có mã quyền. Sau khi khoá root thì **không ai xoá được** qua giao diện. | Hỏi đội vận hành xoá để làm gì. (a) Chỉ để nội dung không tính thưởng → dùng "từ chối nội dung" hoặc "huỷ mục đối soát", không cần xoá. (b) Thật sự cần xoá → thêm mã quyền, giao riêng QLVH hoặc Admin, kèm ghi nhật ký (hiện xoá không ghi nhật ký). | Biz + anh Vinh |
| 2 | **File rút tiền chứa đủ CCCD, MST, SĐT, số thẻ** — 4 vai trò tải được. | (a) Giữ như hiện tại, biz duyệt có ý thức. (b) Chỉ người đưa file lên ngân hàng (Duyệt chi) tải bản đầy đủ, vai trò khác tải bản che. | Biz |
| ~~3~~ | ~~**Lộ trình Admin**~~ | **Đã chốt theo PRD #38:** Admin là vai trò lâu dài, đủ 89 mã, cấp được cho người mới. | — |
| 4 | **Phạm vi Duyệt chi** | Giao theo danh sách ADV người đó chịu trách nhiệm chi; Admin giao "mọi ADV" khi biz xác nhận. Mỗi ADV nên có ít nhất 2 người Duyệt chi để khi một người nghỉ thì người kia vẫn duyệt được. | Biz |
| 5 | **Kỹ thuật hỗ trợ phía đối tác** có được xem mọi ADV không | Đề xuất: không; đội AT được mọi ADV, đối tác chỉ các ADV đang hỗ trợ, có hạn dùng. | AT |
| 6 | **Nhật ký xem SĐT, email** chỉ ghi ở chi tiết creator | (a) Chấp nhận như hiện tại. (b) Ghi thêm nhật ký ở các chỗ còn lại (cần ticket). | Anh Vinh |
| 7 | **Root và Admin:** kênh nhận cảnh báo lần thử đăng nhập root; ai duyệt khôi phục khi không còn Admin (mục 5.1) | Chờ AT chỉ định kênh, cần ticket gửi cảnh báo. Người duyệt khôi phục: đề xuất một người ngoài nhóm Admin. | AT, anh Vinh |
| 8 | **Hạn dùng, cấp/thu hồi, rà soát định kỳ** (mục 5.2–5.4) | Điền các ô "chờ chốt". Có cần email nhắc tài khoản sắp hết hạn không (cần ticket). | Biz + AT |
| ~~9~~ | ~~**Sửa tiền rồi tự duyệt**~~ | **Hết ý nghĩa (chốt 29/10):** đã bỏ luật tách người lập / người duyệt, một người duyệt được khoản do mình tạo, giống production (mục 2). | — |
| 10 | **Tạo vai trò mới** — code cho người có `role.edit` (Admin) tạo vai trò (`POST /roles`), chỉ tick được mã mình có. Quản lý ADV cần tạo vai trò mới. | Cho phép như code (PRD #38 cần để tạo Quản lý ADV). | AT |
| 11 | **Danh sách Admin** | Ít người nhất có thể, đích danh, có người dự phòng. | Biz, anh Vinh |
| 12 | **Bộ quyền QLVH và Quản lý ADV** (PRD #38 mục 3.4) | Như cột đề xuất: QLVH 52 mã, Quản lý ADV 68 mã. Chưa chốt thì dừng trước bước chạy migration nâng Admin; hệ thống chạy như bản cũ. | Biz |
| 13 | **MFA cho Admin** trước khi khoá root | Nên có, vì Admin toàn quyền mà chỉ đăng nhập bằng mật khẩu. Không kịp thì làm ticket riêng và ghi nhận rủi ro. | Anh Vinh |
| 14 | **AT đồng ý thôi giữ root** — tài liệu cũ ghi AT giữ root | Hỏi AT trước khi deploy. | Anh Vinh |
