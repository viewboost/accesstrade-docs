# Phân quyền admin Ambassador — vai trò và quyền

Hệ thống có **8 vai trò** và **75 mã quyền**, cộng tài khoản **root** đứng ngoài mô hình.

Một thao tác được phép khi: nhân sự đang hoạt động, chưa hết hạn **và** vai trò đang hoạt động, có mã quyền của thao tác **và** bản ghi thuộc ADV trong phạm vi của nhân sự.

## 1. Vai trò

| Vai trò | Viết tắt | Mã | Ai dùng | Phạm vi ADV | Số quyền |
|---|---|---|---|---|:-:|
| Root | — | (cờ trên tài khoản, không phải vai trò) | 1 tài khoản do AT giữ | Mọi ADV | Tất cả |
| Quản lý vận hành | QLVH | `ops_manager` | Trưởng nhóm vận hành | ADV mình phụ trách | 30 |
| Vận hành nội dung | VHND | `ops_content` | Nhân viên duyệt nội dung | ADV được giao | 15 |
| Vận hành hiệu suất | VHHS | `ops_performance` | Nhân viên theo dõi hiệu suất | ADV được giao | 19 |
| Duyệt chi | Duyệt chi | `payout_approver` | Người chốt tiền, biz chỉ định | ADV được giao, chỉ root đặt | 14 |
| Kỹ thuật hỗ trợ | KTHT | `tech_support` | Đội kỹ thuật AT và đối tác | Đội AT: mọi ADV; đối tác: chờ chốt (mục 7) | 27 |
| Cấu hình ứng dụng | CHUD | `config_editor` | Người dựng site ADV | ADV mình dựng (ít nhất 1) | 19 |
| Cộng tác viên | CTV | `collaborator` | Người duyệt nội dung (hiện gần như không dùng) | ADV được giao | 6 |
| Admin | Admin | `admin` | Tài khoản Admin hiện có; không cấp cho người mới | ADV được giao; người không gắn ADV → mọi ADV | 70 |

## 2. Tóm tắt quyền

**Nguyên tắc chung**
- Có quyền sửa / import / xuất / duyệt của một chức năng thì tự có quyền xem chức năng đó. Một số quyền còn tự kéo theo quyền tra cứu mà hộp của nó cần: `bonus.view` → `event.view`; `bonus.edit` → `creator.view`; `mission.edit` → `category.view`; `user_segment.edit` → `creator.view`.
- **Không bắt buộc tách người lập và người duyệt khoản chi** (chốt 29/10, [comment #312](https://github.com/AT-Core/ambassador/pull/312#issuecomment-6487523688); code #312 đang gỡ phần chặn). Một vai trò được giữ cả hai nhóm quyền, một người duyệt được khoản do mình tạo, giống production. Vai trò mặc định vẫn tách: VHHS lập, Duyệt chi duyệt; Admin có cả hai.
  - Nhóm lập: `bonus.edit`, `bonus.import`, `bonus.cancel`, `reconciliation.create`, `reconciliation.cancel_item`, `transfer.create`.
  - Nhóm duyệt: `bonus.approve`, `reconciliation.change_status`, `transfer.change_status`.
  - Hai nhóm này vẫn dùng cho **luật quản lý tài khoản**: người mang vai trò có quyền nhóm lập không mời, sửa hay gán được vai trò có quyền nhóm duyệt.
- **Dữ liệu cá nhân của creator:**
  - SĐT, email: chỉ người có `user.view_contact` thấy (QLVH, VHND, Admin, root); người khác không thấy. Riêng ô tìm creator ở bảng xếp hạng, người không có quyền vẫn thấy 4 số cuối SĐT để phân biệt creator trùng tên.
  - Nhật ký xem SĐT, email hiện **chỉ ghi khi mở chi tiết creator**. Người có `user.view_contact` còn thấy SĐT, email ở các bảng Creator (Danh sách creator, Duyệt Creator), Sự kiện › Duyệt sự kiện, Hồ sơ, Quà tặng › Lịch sử đổi quà, Thông số › CBNV, Lịch sử đăng nhập và file xuất người dùng ADV, kênh creator — các chỗ này không ghi nhật ký.
  - CCCD, mã số thuế, ngân hàng: chỉ root và hệ thống AT qua API ngoài (mục 5.5) thấy đầy đủ; người khác thấy bản che (CCCD/MST 3 ký tự cuối, số thẻ 4 số cuối, không thấy chủ thẻ).
  - **Ngoại lệ — file rút tiền:** file chuyển khoản gửi ngân hàng chứa **đủ CCCD, MST, SĐT và số thẻ**, không che. Ai có `transfer.export` đều tải được: QLVH, VHHS, Duyệt chi, Admin (cần chốt, mục 7).
- Token đăng nhập mạng xã hội của creator: không ai thấy, kể cả root.

| Vai trò | Làm được | Không làm được |
|---|---|---|
| Root | Mọi việc trên mọi ADV, kể cả các việc chỉ root (mục 3) | — |
| Quản lý vận hành | Mọi việc của VHND và VHHS; xem nhật ký thao tác, lịch sử đăng nhập; mời, đổi vai trò, tắt tài khoản nhân sự VHND/VHHS trong ADV mình | Duyệt chi; sửa tài khoản Duyệt chi, KTHT, Admin, QLVH khác; xoá nội dung |
| Vận hành nội dung | Duyệt, từ chối, ghim nội dung, gắn cảnh báo, cộng trừ tay lượt xem; duyệt creator đăng ký sự kiện và người dùng vào ADV; xem SĐT, email creator; xuất và tải file nội dung | Việc tiền; sửa sự kiện; xoá nội dung |
| Vận hành hiệu suất | Xem thống kê, bảng xếp hạng; lập thưởng thêm (tạo, sửa, import, huỷ); từ chối mục đối soát không hợp lệ; tải file đối soát, rút tiền; xuất nội dung, thống kê | Duyệt chi (kể cả khoản mình lập); duyệt nội dung; xem SĐT, email; xoá nội dung |
| Duyệt chi | Duyệt, từ chối thưởng thêm; lấy danh sách, duyệt, huỷ cả bản đối soát; duyệt, từ chối đợt rút và lệnh rút; xem màn tiền; tải file đối soát, rút tiền | Tạo, sửa, huỷ khoản thưởng; từ chối mục trong đối soát; lập đối soát, đợt rút |
| Kỹ thuật hỗ trợ | Chỉ xem mọi màn nghiệp vụ trong phạm vi ADV được giao | Mọi thao tác ghi; xem SĐT, email; tải file; xem nhân sự |
| Cấu hình ứng dụng | Cấu hình, xuất bản, khôi phục site; tin tức, bài viết, kênh hỗ trợ, affiliate; tạo, sửa sự kiện và mẫu sự kiện | Việc tiền; duyệt nội dung |
| Cộng tác viên | Duyệt nội dung; cộng trừ tay lượt xem của bài | Mọi việc khác |
| Admin | Gần như toàn bộ nghiệp vụ, cả lập lẫn duyệt chi; xem SĐT, email creator | Xem đủ CCCD, MST, ngân hàng; kênh hỗ trợ; quản lý nhân sự; xoá nội dung; sửa tag, cấu hình dùng chung nếu không có phạm vi "mọi ADV" |

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
| 63 | `quick_action.view` | Xem kênh hỗ trợ | Danh sách kênh hỗ trợ của ADV |  |  |  |  | ✔ | ✔ |  |  |
| 64 | `quick_action.edit` | Quản lý kênh hỗ trợ | Tạo, sửa, bật/tắt kênh hỗ trợ |  |  |  |  |  | ✔ |  |  |
| 65 | `affiliate.view` | Xem chiến dịch affiliate | Danh sách, chi tiết chiến dịch và liên kết chiến dịch – sự kiện |  |  |  |  | ✔ | ✔ |  | ✔ |
| 66 | `affiliate.edit` | Quản lý chiến dịch affiliate | Tạo, sửa, bật/tắt chiến dịch, gắn chiến dịch vào sự kiện |  |  |  |  |  | ✔ |  | ✔ |
| | **Hệ thống** | | | | | | | | | | |
| 67 | `tag.view` | Xem tag | Danh sách tag (gồm tag cảnh báo dùng khi duyệt nội dung) | ✔ | ✔ | ✔ |  | ✔ | ✔ | ✔ | ✔ |
| 68 | `tag.edit` | Quản lý tag | Tạo, sửa, bật/tắt tag. Tag dùng chung cần phạm vi Mọi ADV |  |  |  |  |  |  |  | ✔ |
| 69 | `common_config.view` | Xem cấu hình chung | Xem cấu hình dùng chung của hệ thống |  |  |  |  | ✔ |  |  | ✔ |
| 70 | `common_config.edit` | Sửa cấu hình chung | Tạo, sửa, xoá cấu hình chung trong ADV được giao; cấu hình toàn hệ thống cần phạm vi Mọi ADV |  |  |  |  |  |  |  | ✔ |
| 71 | `audit.view` | Xem nhật ký thao tác | Xem nhật ký thao tác chung trong phạm vi ADV của mình (chưa có màn). Lịch sử từng bản ghi không cần quyền này | ✔ |  |  |  | ✔ |  |  | ✔ |
| 72 | `login_history.view` | Xem lịch sử đăng nhập | Xem lịch sử đăng nhập của nhân sự và creator, kèm IP, thiết bị | ✔ |  |  |  | ✔ |  |  | ✔ |
| 73 | `staff.view` | Xem nhân sự | Danh sách và chi tiết nhân sự có phạm vi giao với phạm vi của mình; không thấy root | ✔ |  |  |  |  |  |  |  |
| 74 | `staff.invite` | Mời nhân sự | Mời, mời hàng loạt, gửi lại, thu hồi lời mời — chỉ với vai trò và ADV không vượt quá mình | ✔ |  |  |  |  |  |  |  |
| 75 | `staff.edit` | Sửa nhân sự | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản — chỉ nhân sự nằm trọn trong phạm vi mình | ✔ |  |  |  |  |  |  |  |
| | **Tổng** | | | 30 | 15 | 19 | 14 | 27 | 19 | 6 | 70 |

Cột Tên và Cho phép làm gì lấy đúng nhãn và mô tả trong code (`constants.Permissions`), là chữ hiện trên màn tick quyền. `user_segment.import` bị **ẩn trên màn tick quyền** vì chưa có nút trên giao diện; mã vẫn hợp lệ, Admin có sẵn từ lúc gieo.

**Chỉ root (không có mã quyền, không gán được cho vai trò nào):**
- Vai trò & phân quyền: xem chi tiết, tạo, sửa, ngừng vai trò; tick quyền.
- Nhân sự đặc biệt: cấp cờ root; giao phạm vi "mọi ADV"; đặt lại mật khẩu người khác; tạo nhân sự kiểu cũ (đặt sẵn mật khẩu).
- ADV: tạo, sửa, ngừng hoạt động.
- Người dùng: khoá, mở khoá; hợp đồng điện tử (tạo, xem, từ chối); eKYC; tạo người dùng; xác thực tài khoản.
- Xem đầy đủ CCCD, mã số thuế, ngân hàng của creator.
- Thưởng sự kiện: đổi trạng thái, xoá, từ chối, chạy lại tính thưởng.
- **Xoá nội dung** (xoá cứng, kéo theo thưởng sự kiện và số liệu; nội dung đã vào đối soát thì không xoá được). Cần chốt, mục 7.
- Sửa dữ liệu người dùng ADV WildRift (`PUT /partners/users/wildrift`). Không dùng nữa thì gỡ route khỏi code.
- Công cụ kỹ thuật: mọi route `/migration/*` (chạy migration, backfill dữ liệu); chạy lại analytic, cập nhật dữ liệu sự kiện, cập nhật hàng loạt trạng thái / tag cảnh báo nội dung.

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

## 5. Quản trị tài khoản

### 5.1 Tài khoản root
- **Ai giữ:** AT, đúng 1 tài khoản. Không có hạn dùng (một root duy nhất mà hết hạn thì khoá cả hệ thống).
- **Mỗi lần root đăng nhập:** hệ thống ghi nhật ký (chỉ root xem được dòng này). **Chưa gửi cảnh báo đi đâu** — muốn có cảnh báo cần thêm ticket.
- **Kênh nhận cảnh báo, quy trình khôi phục root khẩn cấp:** chờ AT chốt (mục 7).

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
| Quản lý vận hành | Biz | Biz | Root |
| Duyệt chi | Biz | Biz | Root |
| Kỹ thuật hỗ trợ (AT) | Đội kỹ thuật AT | AT | Root |
| Kỹ thuật hỗ trợ (đối tác) | Đối tác | AT | Root, bắt buộc có hạn dùng |
| Cấu hình ứng dụng, Cộng tác viên | Chờ chốt | Chờ chốt | Root |
| **Người nghỉ việc** | Quản lý trực tiếp báo | — | QLVH tắt với VHND/VHHS; root tắt với vai trò khác; thời hạn: chờ chốt |

Tắt tài khoản, đổi vai trò hay đổi phạm vi **có hiệu lực ngay từ thao tác kế tiếp** của người đó: mỗi request hệ thống đều đọc lại nhân sự và vai trò từ DB, kể cả dịch vụ tải file.

### 5.4 Rà soát quyền định kỳ
- Tần suất: chờ chốt (đề xuất hằng tháng).
- Quản lý vận hành rà người trong đội mình; root rà Admin, Duyệt chi, Kỹ thuật hỗ trợ, Cấu hình ứng dụng.
- Dùng màn Nhân viên (lọc vai trò, phạm vi, sắp hết hạn) và nhật ký thao tác, lịch sử đăng nhập.

### 5.5 Ranh giới với API ngoài của AT
AT gọi **API ngoài bằng khoá API**, với quyền ngang root:
- **Ghi tiền:** tạo, sửa bản đối soát và đợt rút; đổi trạng thái đối soát, mục đối soát, đợt rút, lệnh rút.
- **Đọc dữ liệu cá nhân không che:** danh sách người dùng (`GET /users`) trả đủ CCCD, MST; lệnh rút của một đợt (`GET /transfers/:id/withdraw-cashes`) trả đủ số thẻ, chủ thẻ; tạo file xuất (`POST /data-exports`).

## 6. Tiêu chí thành công sau release
- Số tài khoản root đang hoạt động: **đúng 1**.
- **7 ngày liền** không đăng nhập root để làm việc vận hành.

## 7. Điểm còn chờ chốt

| # | Câu hỏi | Phương án | Ai chốt |
|---|---|---|---|
| 1 | **Xoá nội dung** — PRD giao cho QLVH và VHHS, hiện chỉ root làm được. Giữ chỉ root thì vận hành phải nhờ root, trượt tiêu chí "7 ngày không dùng root". | Hỏi đội vận hành xoá để làm gì. (a) Chỉ để nội dung không tính thưởng → dùng "từ chối nội dung" hoặc "huỷ mục đối soát", giữ xoá chỉ root. (b) Thật sự cần xoá → giao riêng QLVH, kèm ghi nhật ký (hiện xoá không ghi nhật ký). | Biz + anh Vinh |
| 2 | **File rút tiền chứa đủ CCCD, MST, SĐT, số thẻ** — 4 vai trò tải được. | (a) Giữ như hiện tại, biz duyệt có ý thức. (b) Chỉ người đưa file lên ngân hàng (Duyệt chi) tải bản đầy đủ, vai trò khác tải bản che. | Biz |
| 3 | **Lộ trình Admin** — nếu bỏ Admin thì không vai trò nào làm: nhiệm vụ, quà, phân khúc, mã, thông báo, sửa hồ sơ creator, CBNV, xuất người dùng, lập đối soát và đợt rút trên admin. | (a) Admin là vai trò lâu dài cho nhóm việc này. (b) Thêm vai trò mới cho nhóm việc này, Admin ngừng sau hạn (PRD đề xuất hết Mốc 3 + 30 ngày). | Biz |
| 4 | **Phạm vi Duyệt chi** | Giao theo danh sách ADV người đó chịu trách nhiệm chi; root giao "mọi ADV" khi biz xác nhận. Mỗi ADV nên có ít nhất 2 người Duyệt chi để khi một người nghỉ thì người kia vẫn duyệt được. | Biz |
| 5 | **Kỹ thuật hỗ trợ phía đối tác** có được xem mọi ADV không | Đề xuất: không; đội AT được mọi ADV, đối tác chỉ các ADV đang hỗ trợ, có hạn dùng. | AT |
| 6 | **Nhật ký xem SĐT, email** chỉ ghi ở chi tiết creator | (a) Chấp nhận như hiện tại. (b) Ghi thêm nhật ký ở các chỗ còn lại (cần ticket). | Anh Vinh |
| 7 | **Root:** kênh nhận cảnh báo đăng nhập; quy trình khôi phục khẩn cấp | Chờ AT chỉ định kênh; cần ticket gửi cảnh báo. | AT |
| 8 | **Hạn dùng, cấp/thu hồi, rà soát định kỳ** (mục 5.2–5.4) | Điền các ô "chờ chốt". Có cần email nhắc tài khoản sắp hết hạn không (cần ticket). | Biz + AT |
| ~~9~~ | ~~**Sửa tiền rồi tự duyệt**~~ | **Hết ý nghĩa (chốt 29/10):** đã bỏ luật tách người lập / người duyệt, một người duyệt được khoản do mình tạo, giống production (mục 2). | — |
| 10 | **Root có được tạo vai trò mới không** — code đã cho (`POST /roles`), PRD Q4 đề xuất "chưa cần ở đợt này". | (a) Cho phép như code. (b) Chặn tạo mới, root chỉ sửa tập quyền của vai trò có sẵn. | AT |
