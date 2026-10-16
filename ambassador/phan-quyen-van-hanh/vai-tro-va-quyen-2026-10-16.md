# Phân quyền admin Ambassador — vai trò và quyền

Hệ thống có **8 vai trò** và **75 mã quyền**, cộng tài khoản **root** đứng ngoài mô hình.

Một thao tác được phép khi: nhân sự đang hoạt động, chưa hết hạn **và** vai trò có mã quyền của thao tác **và** bản ghi thuộc ADV trong phạm vi của nhân sự.

## 1. Vai trò

| Vai trò | Viết tắt | Mã | Ai dùng | Phạm vi ADV | Số quyền |
|---|---|---|---|---|:-:|
| Root | — | (cờ trên tài khoản) | 1 tài khoản do AT giữ | Mọi ADV | Tất cả |
| Quản lý vận hành | QLVH | `ops_manager` | Trưởng nhóm vận hành | ADV mình phụ trách | 30 |
| Vận hành nội dung | VHND | `ops_content` | Nhân viên duyệt nội dung | ADV được giao | 14 |
| Vận hành hiệu suất | VHHS | `ops_performance` | Nhân viên theo dõi hiệu suất | ADV được giao | 19 |
| Duyệt chi | Duyệt chi | `payout_approver` | Người chốt tiền, biz chỉ định | ADV được giao, chỉ root đặt (chờ chốt) | 13 |
| Kỹ thuật hỗ trợ | KTHT | `tech_support` | Đội kỹ thuật AT và đối tác | Đội AT: mọi ADV; đối tác: chờ chốt | 27 |
| Cấu hình ứng dụng | CHUD | `config_editor` | Người dựng site ADV | ADV mình dựng (ít nhất 1) | 19 |
| Cộng tác viên | CTV | `collaborator` | Người duyệt nội dung (hiện gần như không dùng) | ADV được giao | 6 |
| Admin | Admin | `admin` | Tài khoản Admin hiện có; không cấp cho người mới | ADV được giao; người không gắn ADV → mọi ADV | 69 |

## 2. Tóm tắt quyền

**Nguyên tắc chung**
- Có quyền sửa / import / xuất / duyệt của một chức năng thì tự có quyền xem chức năng đó.
- Người lập khoản chi và người duyệt khoản chi là hai người. Chỉ root và Admin có cả hai.
  - Nhóm lập: `bonus.edit`, `bonus.import`, `bonus.cancel`, `reconciliation.edit`, `reconciliation.cancel_item`, `transfer.edit`.
  - Nhóm duyệt: `bonus.change_status`, `reconciliation.change_status`, `transfer.change_status`.
- Mỗi lượt xem SĐT, email creator đều ghi nhật ký. CCCD, MST, ngân hàng chỉ root xem đầy đủ; người khác thấy bản che (CCCD/MST 3 ký tự cuối, số thẻ 4 số cuối).

| Vai trò | Làm được | Không làm được |
|---|---|---|
| Root | Mọi việc. Riêng root: tạo/sửa ADV; khoá/mở khoá creator; hợp đồng điện tử, eKYC; tạo người dùng; xác thực tài khoản; thưởng sự kiện; xoá nội dung; xem đủ CCCD, MST, ngân hàng; tạo/sửa vai trò, tick quyền; cấp root; giao "mọi ADV"; đặt lại mật khẩu người khác; công cụ kỹ thuật | — |
| Quản lý vận hành | Mọi việc của VHND và VHHS; xem nhật ký thao tác, lịch sử đăng nhập; mời, đổi vai trò, tắt tài khoản nhân sự VHND/VHHS trong ADV mình | Duyệt chi; sửa tài khoản Duyệt chi, KTHT, Admin, QLVH khác |
| Vận hành nội dung | Duyệt, từ chối, ghim nội dung, gắn cảnh báo, thêm tay nội dung; duyệt creator đăng ký và người dùng vào ADV; xem SĐT, email creator; xuất file nội dung | Việc tiền; sửa sự kiện |
| Vận hành hiệu suất | Xem thống kê, bảng xếp hạng; lập thưởng thêm (tạo, sửa, import, huỷ); huỷ mục đối soát không hợp lệ; tải file đối soát, rút tiền; xuất nội dung, thống kê | Duyệt chi (kể cả khoản mình lập); duyệt nội dung; xem SĐT, email |
| Duyệt chi | Duyệt, từ chối thưởng thêm; chốt đối soát; duyệt, từ chối đợt rút và lệnh rút; xem màn tiền; tải file đối soát, rút tiền | Tạo, sửa, huỷ khoản thưởng; huỷ mục đối soát; lập đối soát, đợt rút |
| Kỹ thuật hỗ trợ | Chỉ xem mọi màn nghiệp vụ trong phạm vi ADV được giao | Mọi thao tác ghi; xem SĐT, email; tải file; xem nhân sự |
| Cấu hình ứng dụng | Cấu hình, xuất bản, khôi phục site; tin tức, bài viết, kênh hỗ trợ, affiliate; tạo, sửa sự kiện và mẫu sự kiện | Việc tiền; duyệt nội dung |
| Cộng tác viên | Chỉ duyệt nội dung | Mọi việc khác |
| Admin | Gần như toàn bộ nghiệp vụ, cả lập lẫn duyệt chi; thêm quyền xem SĐT, email creator | Xem CCCD, MST, ngân hàng; kênh hỗ trợ; quản lý nhân sự; xoá nội dung; sửa tag, cấu hình dùng chung nếu không có phạm vi "mọi ADV" |

## 3. Danh sách quyền

✔ = có · ô trống = không.

| # | Mã quyền | Tên | Cho phép làm gì | QLVH | VHND | VHHS | Duyệt chi | KTHT | CHUD | CTV | Admin |
|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | **Nội dung** | | | | | | | | | | |
| 1 | `content.view` | Xem nội dung | Xem danh sách, chi tiết, số liệu nội dung creator đã đăng | ✔ | ✔ | ✔ |  | ✔ |  | ✔ | ✔ |
| 2 | `content.moderate` | Duyệt nội dung | Duyệt, từ chối (từng bài và theo lô), ghim, gắn tag cảnh báo, cập nhật số liệu một nội dung | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| 3 | `content.export` | Xuất dữ liệu nội dung | Xuất file nội dung và biểu đồ nội dung | ✔ | ✔ | ✔ |  |  |  |  | ✔ |
| 4 | `content_manual_flow.view` | Xem luồng nội dung thủ công | Xem các luồng nội dung được thêm tay | ✔ | ✔ |  |  | ✔ |  | ✔ | ✔ |
| 5 | `content_manual_flow.edit` | Tạo luồng nội dung thủ công | Thêm tay một luồng nội dung cho creator | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| | **Người dùng và creator** | | | | | | | | | | |
| 6 | `user.view_contact` | Xem liên hệ creator | Mở chi tiết creator: số điện thoại, email, kênh mạng xã hội, nội dung đã đăng. Mỗi lượt xem ghi nhật ký | ✔ | ✔ |  |  |  |  |  | ✔ |
| 7 | `user.view_sensitive` | Xem CCCD, MST, ngân hàng | Xem đầy đủ số CCCD, mã số thuế, tên ngân hàng, chủ thẻ, số thẻ của creator. Không có quyền này thì các trường bị che. Mỗi lượt xem ghi nhật ký |  |  |  |  |  |  |  |  |
| 8 | `user.export` | Xuất danh sách người dùng | Xuất file người dùng của ADV và kênh mạng xã hội; CCCD, MST, ngân hàng trong file bị che |  |  |  |  |  |  |  | ✔ |
| 9 | `creator.view` | Xem hồ sơ creator | Danh sách người dùng, danh sách và chi tiết hồ sơ creator, thống kê hồ sơ, danh sách người dùng của ADV | ✔ | ✔ | ✔ | ✔ | ✔ |  |  | ✔ |
| 10 | `creator.edit` | Sửa hồ sơ creator | Đổi trạng thái hồ sơ, cập nhật chỉ số, cấu hình điều kiện hồ sơ |  |  |  |  |  |  |  | ✔ |
| 11 | `creator.approve` | Duyệt creator | Duyệt hoặc từ chối hồ sơ đăng ký làm creator | ✔ | ✔ |  |  |  |  |  | ✔ |
| 12 | `partner_member.approve` | Duyệt thành viên ADV | Duyệt hoặc từ chối yêu cầu tham gia ADV của người dùng | ✔ | ✔ |  |  |  |  |  | ✔ |
| 13 | `user_partner.view` | Xem người dùng ADV | Xem người dùng thuộc ADV và trạng thái CBNV |  |  |  |  | ✔ |  |  | ✔ |
| 14 | `user_partner.edit_staff_status` | Đổi trạng thái CBNV | Đánh dấu / bỏ đánh dấu người dùng ADV là nhân viên của thương hiệu |  |  |  |  |  |  |  | ✔ |
| | **Sự kiện và thống kê** | | | | | | | | | | |
| 15 | `event.view` | Xem danh sách sự kiện | Danh sách sự kiện (dùng cả ở ô chọn sự kiện khi duyệt nội dung) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 16 | `event.view_detail` | Xem chi tiết sự kiện | Chi tiết sự kiện, yêu cầu, ngân sách, bảng xếp hạng | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| 17 | `event.edit` | Quản lý sự kiện | Tạo, sửa, nhân bản, bật/tắt sự kiện; yêu cầu, ngân sách, opshub; cấu hình và ghim bảng xếp hạng |  |  |  |  |  | ✔ |  | ✔ |
| 18 | `event_schema.view` | Xem mẫu sự kiện | Danh sách mẫu sự kiện |  |  |  |  | ✔ | ✔ |  | ✔ |
| 19 | `event_schema.edit` | Quản lý mẫu sự kiện | Tạo, sửa, bật/tắt mẫu sự kiện dùng để dựng sự kiện |  |  |  |  |  | ✔ |  | ✔ |
| 20 | `statistic.view` | Xem thống kê | Dashboard, thống kê sự kiện, thống kê theo nhân sự, biểu đồ, báo cáo | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| 21 | `statistic.export` | Xuất thống kê | Xuất biểu đồ người dùng, sự kiện | ✔ |  | ✔ |  |  |  |  | ✔ |
| | **Thưởng, nhiệm vụ, quà** | | | | | | | | | | |
| 22 | `bonus.view` | Xem thưởng thêm | Danh sách và chi tiết các khoản thưởng thêm | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 23 | `bonus.edit` | Cộng thưởng thêm | Tạo, sửa một khoản thưởng thêm cho creator; không tự duyệt được khoản thưởng | ✔ |  | ✔ |  |  |  |  | ✔ |
| 24 | `bonus.import` | Import thưởng thêm | Cộng thưởng hàng loạt bằng file Excel; dòng ngoài phạm vi ADV bị từ chối kèm lý do, dòng hợp lệ vẫn vào | ✔ |  | ✔ |  |  |  |  | ✔ |
| 25 | `bonus.cancel` | Huỷ thưởng thêm | Huỷ một khoản thưởng thêm đã tạo | ✔ |  | ✔ |  |  |  |  | ✔ |
| 26 | `bonus.change_status` | Duyệt thưởng thêm | Duyệt hoặc từ chối khoản thưởng thêm (đổi trạng thái) |  |  |  | ✔ |  |  |  | ✔ |
| 27 | `mission.view` | Xem nhiệm vụ | Danh sách và chi tiết nhiệm vụ, danh sách điểm chờ duyệt |  |  |  |  | ✔ |  |  | ✔ |
| 28 | `mission.edit` | Quản lý nhiệm vụ | Tạo, sửa nhiệm vụ |  |  |  |  |  |  |  | ✔ |
| 29 | `mission.approve` | Duyệt điểm nhiệm vụ | Duyệt hoặc từ chối điểm creator nhận từ nhiệm vụ |  |  |  |  |  |  |  | ✔ |
| 30 | `gift.view` | Xem quà | Danh sách quà, chi tiết, lịch sử đổi quà |  |  |  |  | ✔ |  |  | ✔ |
| 31 | `gift.edit` | Quản lý quà | Tạo, sửa, bật/tắt quà |  |  |  |  |  |  |  | ✔ |
| 32 | `gift.process` | Xử lý lượt đổi quà | Duyệt, từ chối, đổi trạng thái lượt creator đổi quà |  |  |  |  |  |  |  | ✔ |
| | **Đối soát, rút tiền, dữ liệu xuất** | | | | | | | | | | |
| 33 | `reconciliation.view` | Xem đối soát | Danh sách và chi tiết bản đối soát, đủ bốn tab: Tổng quan, Nội dung, Mốc thưởng, Thưởng thêm | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 34 | `reconciliation.edit` | Lập bản đối soát | Tạo, sửa bản đối soát trên admin |  |  |  |  |  |  |  | ✔ |
| 35 | `reconciliation.cancel_item` | Huỷ mục đối soát | Huỷ từng mục nội dung hoặc mốc thưởng trong bản đối soát, kèm lý do | ✔ |  | ✔ |  |  |  |  | ✔ |
| 36 | `reconciliation.change_status` | Chốt đối soát | Đổi trạng thái cả bản đối soát (chốt để chi, từ chối) |  |  |  | ✔ |  |  |  | ✔ |
| 37 | `reconciliation.export` | Tải file đối soát | Tạo yêu cầu xuất và tải file đối soát; file luôn mang ADV của bản đối soát | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 38 | `transfer.view` | Xem rút tiền | Danh sách, chi tiết đợt rút và danh sách lệnh rút bên trong | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 39 | `transfer.edit` | Lập đợt rút tiền | Tạo, sửa đợt rút tiền trên admin |  |  |  |  |  |  |  | ✔ |
| 40 | `transfer.export` | Tải file rút tiền | Tạo yêu cầu xuất và tải file rút tiền | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 41 | `transfer.change_status` | Duyệt rút tiền | Đổi trạng thái đợt rút, từ chối lệnh rút |  |  |  | ✔ |  |  |  | ✔ |
| 42 | `export.view` | Xem dữ liệu xuất | Xem danh sách file đã xuất. Tải từng file cần quyền tải của loại file đó | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| | **Phân khúc, mã, thông báo, danh mục** | | | | | | | | | | |
| 43 | `segment.view` | Xem phân khúc | Danh sách và chi tiết phân khúc |  |  |  |  | ✔ |  |  | ✔ |
| 44 | `segment.edit` | Quản lý phân khúc | Tạo, sửa, bật/tắt phân khúc |  |  |  |  |  |  |  | ✔ |
| 45 | `user_segment.view` | Xem người dùng trong phân khúc | Danh sách người dùng thuộc phân khúc |  |  |  |  | ✔ |  |  | ✔ |
| 46 | `user_segment.edit` | Sửa người dùng trong phân khúc | Thêm, xoá người dùng khỏi phân khúc |  |  |  |  |  |  |  | ✔ |
| 47 | `user_segment.import` | Import người dùng vào phân khúc | Thêm hàng loạt bằng Excel |  |  |  |  |  |  |  | ✔ |
| 48 | `code.view` | Xem mã | Danh sách mã |  |  |  |  | ✔ |  |  | ✔ |
| 49 | `code.edit` | Quản lý mã | Tạo, sửa mã |  |  |  |  |  |  |  | ✔ |
| 50 | `code.import` | Import mã | Nhập mã hàng loạt bằng Excel |  |  |  |  |  |  |  | ✔ |
| 51 | `notification.view` | Xem thông báo | Danh sách và chi tiết thông báo admin |  |  |  |  | ✔ |  |  | ✔ |
| 52 | `notification.edit` | Soạn thông báo | Tạo, sửa, nhân bản thông báo |  |  |  |  |  |  |  | ✔ |
| 53 | `notification.approve` | Duyệt thông báo | Đánh dấu hoàn thành hoặc từ chối thông báo |  |  |  |  |  |  |  | ✔ |
| 54 | `category.view` | Xem danh mục | Danh sách danh mục | ✔ | ✔ | ✔ |  | ✔ | ✔ |  | ✔ |
| 55 | `category.edit` | Quản lý danh mục | Tạo, sửa danh mục |  |  |  |  |  |  |  | ✔ |
| | **Cấu hình ADV và nội dung site** | | | | | | | | | | |
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
| 68 | `tag.edit` | Quản lý tag | Tạo, sửa, bật/tắt tag của ADV trong phạm vi. Tag không gắn ADV (dùng chung) cần phạm vi `all` |  |  |  |  |  |  |  | ✔ |
| 69 | `common_config.view` | Xem cấu hình chung | Xem cấu hình của ADV trong phạm vi và cấu hình không gắn ADV |  |  |  |  | ✔ |  |  | ✔ |
| 70 | `common_config.edit` | Sửa cấu hình chung | Sửa cấu hình của ADV trong phạm vi. Cấu hình không gắn ADV (toàn hệ thống) cần phạm vi `all` |  |  |  |  |  |  |  | ✔ |
| 71 | `audit.view` | Xem nhật ký thao tác | Xem nhật ký thao tác trong phạm vi ADV của mình | ✔ |  |  |  | ✔ |  |  | ✔ |
| 72 | `login_history.view` | Xem lịch sử đăng nhập | Xem lịch sử đăng nhập của nhân sự | ✔ |  |  |  | ✔ |  |  | ✔ |
| 73 | `staff.view` | Xem nhân sự | Danh sách và chi tiết nhân sự có phạm vi giao với phạm vi của mình; không thấy root | ✔ |  |  |  |  |  |  |  |
| 74 | `staff.invite` | Mời nhân sự | Mời, mời hàng loạt, gửi lại, thu hồi lời mời — chỉ với vai trò và ADV không vượt quá mình | ✔ |  |  |  |  |  |  |  |
| 75 | `staff.edit` | Sửa nhân sự | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản — chỉ nhân sự nằm trọn trong phạm vi mình và mang vai trò mình được gán | ✔ |  |  |  |  |  |  |  |
| | **Tổng** | | | 30 | 14 | 19 | 13 | 27 | 19 | 6 | 69 |

**Không có mã quyền — chỉ root:** vai trò & phân quyền; tạo/sửa/ngừng ADV; khoá, mở khoá, hợp đồng điện tử, eKYC, tạo người dùng; xác thực tài khoản (`/identifications`); thưởng sự kiện (`/event-reward`); **xoá nội dung** (`DELETE /contents/:id`); bật cờ root, đặt phạm vi `all`, đặt lại mật khẩu người khác, tạo nhân sự kiểu cũ; công cụ kỹ thuật (`/migration/*`, chạy lại analytic, route cập nhật hàng loạt dưới `/contents`).

**Không cần quyền (public):** đăng nhập, nhận lời mời, quên/đặt lại mật khẩu, `/staffs/me`, đổi mật khẩu của chính mình, `GET /partners` (tự lọc theo phạm vi).

## 4. Điểm còn chờ chốt

- **Phạm vi Duyệt chi:** ai giữ vai trò này, giao theo từng ADV hay mọi ADV. **Đề xuất:** giao theo danh sách ADV người đó chịu trách nhiệm chi; chỉ root đặt và sửa. Người chốt tiền cho toàn bộ ADV thì root giao "mọi ADV" theo xác nhận của biz. Mỗi ADV nên giao cho ít nhất 2 người Duyệt chi, để khi một người nghỉ thì người kia vẫn duyệt được.
    - Lý do: ADV mới không tự động thêm người có quyền duyệt tiền; phạm vi duyệt chi không bị Quản lý vận hành (bên lập) chỉnh được.
- **Phạm vi Kỹ thuật hỗ trợ phía đối tác:** có được xem mọi ADV không. **Đề xuất:** không; đội kỹ thuật AT được mọi ADV, đối tác chỉ được các ADV đang hỗ trợ.
- **Vận hành nội dung có `content.export` nhưng không có `export.view`:** xuất được file nhưng không vào được màn Dữ liệu xuất để tải. **Đề xuất:** thêm `export.view` cho Vận hành nội dung (lên 15 quyền).
