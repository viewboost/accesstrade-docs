# PRD — Luồng xác thực mã nhân viên trên ứng dụng đa đối tác (`frontend/`)

| | |
|---|---|
| **Mã tài liệu** | PRD-AMB-STAFF-FE-001 |
| **Phiên bản** | 2.0 |
| **Ngày ban hành** | 2026-09-03 |
| **Cập nhật gần nhất** | 2026-09-04 |
| **Người biên soạn** | Nguyễn Đăng Định |
| **Người duyệt** | _chưa phân công_ |
| **Trạng thái** | Bản thảo — phạm vi đã chốt, chờ duyệt |
| **Mức độ ưu tiên** | P1 — khiếm khuyết đang tồn tại trên môi trường production |
| **Cấp độ dự án** | Level 2 |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Tài liệu kỹ thuật** | [techspec-staff-code-frontend-2026-09-04.md](./techspec-staff-code-frontend-2026-09-04.md) |

---

## Quy ước ngôn ngữ

Tài liệu sử dụng các động từ tình thái theo RFC 2119:

| Từ khoá | Ý nghĩa |
|---|---|
| **PHẢI** / **KHÔNG ĐƯỢC** | Yêu cầu bắt buộc. Vi phạm là lỗi nghiệm thu. |
| **NÊN** / **KHÔNG NÊN** | Khuyến nghị. Sai lệch phải có lý do được ghi nhận. |
| **CÓ THỂ** | Tuỳ chọn, không ảnh hưởng nghiệm thu. |

Mã định danh yêu cầu sử dụng tiền tố `FE-` nhằm phân biệt với `FR-0xx` của PRD-AMB-STAFF-001. Bảng truy vết giữa hai hệ mã đặt tại Mục 11.

---

## 1. Mục đích và phạm vi

### 1.1 Mục đích

Tài liệu đặc tả yêu cầu nghiệp vụ cho việc bổ sung giao diện xác thực mã nhân viên vào ứng dụng `frontend/` — ứng dụng đa đối tác của hệ thống Ambassador.

### 1.2 Phạm vi áp dụng

| Hạng mục | Trong phạm vi |
|---|---|
| `frontend/` | Có |
| `backend/`, `admin/` | Không — đã hoàn thiện, xem Mục 2.2 |
| `parasola/`, `fecredit/` | Không |
| 12 thư mục đối tác còn lại | Không |

### 1.3 Quan hệ với tài liệu tiền nhiệm

Tài liệu này là một hạng mục công việc độc lập, **không** phải bản sửa đổi của [PRD-AMB-STAFF-001](./prd-employee-code-2026-08-06.md) (phiên bản 5.1, trạng thái Final).

Cơ sở của việc tách tài liệu: PRD-AMB-STAFF-001 xây dựng trên giả định *một đối tác tương ứng một ứng dụng*. Toàn bộ yêu cầu giao diện người dùng của tài liệu đó (FR-009, FR-010) kế thừa giả định này. `frontend/` là ứng dụng đa đối tác duy nhất trong kho mã nguồn, do đó các yêu cầu nêu trên không áp dụng trực tiếp được và cần đặc tả lại.

Mục 8 của PRD-AMB-STAFF-001 quy định *"Không đụng `frontend/`"*. Ràng buộc đó phù hợp tại thời điểm ban hành và **được giữ nguyên** — tài liệu tiền nhiệm không bị chỉnh sửa.

---

## 2. Bối cảnh

### 2.1 Phát biểu vấn đề

Cơ chế kiểm soát điều kiện tham gia chiến dịch (sau đây gọi là *cổng kiểm soát*) được cài đặt tại tầng dịch vụ dùng chung `backend/pkg/public/service/content.go:132`, thực thi trước `Eligibility().JoinEvent()` (`:139`) trong mọi lượt nộp bài, không phụ thuộc ứng dụng khách gọi đến.

`frontend/` chưa có giao diện tương ứng để người dùng đáp ứng điều kiện của cổng kiểm soát này.

| Hành vi người dùng | `fecredit/` | `frontend/` (hiện trạng) |
|---|---|---|
| Nộp bài vào chiến dịch giới hạn cho nhân viên | Hộp thoại giải thích, chặn trước khi mở biểu mẫu | Biểu mẫu mở, người dùng nhập liên kết, yêu cầu bị từ chối kèm thông báo lỗi không có hướng dẫn xử lý |
| Chiến dịch yêu cầu mã tham gia riêng | Hộp thoại nhập mã, sau đó mở biểu mẫu | Không có giao diện nhập mã; mọi lượt nộp bài đều thất bại |
| Khai báo hoặc điều chỉnh trạng thái nhân viên | Mục "Thông tin nhân viên" tại trang Hồ sơ | Không có |

Hệ quả: người dùng không có phương án tự xử lý, bộ phận vận hành không có quy trình hướng dẫn.

### 2.2 Hiện trạng hệ thống

Kết quả rà soát mã nguồn trên nhánh `release`:

| Thành phần | Trạng thái | Tham chiếu |
|---|---|---|
| Cổng kiểm soát khi nộp bài | Đã có, dùng chung mọi ứng dụng | `backend/pkg/public/service/content.go:132` |
| Kiểm thử ràng buộc vị trí cổng kiểm soát | Đã có | `backend/pkg/public/service/staff_gate_test.go:34,41` |
| `POST /users/confirm-is-staff` | Đã có, hỗ trợ ghi đè | `backend/pkg/public/service/staff_code.go` |
| `GET /partners/:id/status-employee` | Đã có, tự vô hiệu theo đối tác | `staff_code.go:47` |
| `POST /events/:id/input-code-join-event` | Đã có | `backend/pkg/public/service/event.go` |
| Cờ `isRequireCode`, `staffGateReason` | Đã có tại API chi tiết chiến dịch | `event.go:1292-1293` |
| Phân hệ quản trị (quản lý mã, cột, bộ lọc, thống kê) | Đã có, 23 tệp | `admin/src/pages/manage-code/`, `user-partner/`, `event-statistic/` |
| Giao diện người dùng — `fecredit/` | Đã có, 11 tệp | nhánh `release` |
| Giao diện người dùng — `parasola/` | Chỉ có trên nhánh `develop` | Loại khỏi phạm vi phát hành theo commit `22ef6d8eb` (PR #135) |
| Giao diện người dùng — `frontend/` | **Chưa có** | Không có tệp nào |

Kết luận: hạng mục công việc này không phát sinh thay đổi tại `backend/` và `admin/`.

### 2.3 Xác nhận trên môi trường production

Số liệu thu thập ngày 2026-09-03 thông qua API công khai, sử dụng Origin của `frontend/` (`https://ambassador.koc.com.vn`, tham chiếu `frontend/config/config.prod.ts:13`):

| Nội dung kiểm tra | Kết quả |
|---|---|
| `GET /api/public/partners` | 17 đối tác; `allowHeaderPartner = true` |
| Đối tác FE CREDIT có hiện diện | Có — định danh `6a8d6e38f6aec40a65991d71`, slug `fecredit` |
| Chiến dịch của FE CREDIT trên site này | 2 chiến dịch; chiến dịch slug `fecredit` có `applyForStaff = true` |

Diễn giải: tại thời điểm lập tài liệu, người dùng truy cập chiến dịch nêu trên qua `frontend/` và thực hiện thao tác nộp bài sẽ bị từ chối, đồng thời không có giao diện nào để khai báo mã nhân viên. Cùng chiến dịch, cùng tầng dịch vụ, người dùng truy cập qua ứng dụng white-label hoàn tất được thao tác. Yếu tố khác biệt duy nhất là tên miền truy cập.

Ghi chú: trạng thái `options.enableStaffCode` của đối tác FE CREDIT chưa xác minh trực tiếp được do endpoint `status-employee` yêu cầu xác thực (`backend/pkg/public/router/partner.go:24`). Xem Mục 13, vấn đề số 1.

### 2.4 Đặc thù kiến trúc của `frontend/`

Đây là cơ sở của phần lớn yêu cầu trong tài liệu.

**Cơ chế phân giải đối tác:**

| Bước | Tham chiếu |
|---|---|
| Tầng handler lấy tên miền từ header Origin | `backend/pkg/public/handler/partner.go:203` |
| Tầng dịch vụ lọc đối tác theo `allowDomains` | `backend/pkg/public/service/partner.go:308` |
| Backend trả cờ `AllowHeaderPartner = len(Data) > 1` | `backend/pkg/public/service/partner.go:376` |
| Tầng giao diện suy ra `isOwnerPartner = !allowHeaderPartner` | `frontend/src/models/main.ts:243` |

Ứng dụng white-label vận hành trên tên miền riêng, nhận về đúng một đối tác, `isOwnerPartner = true`. `frontend/` vận hành trên tên miền ACCESSTRADE, nhận về nhiều đối tác, `isOwnerPartner = false`.

**Cơ chế định tuyến:** chỉ nhánh định tuyến lồng dưới `/:partner/` mang thông tin đối tác (`frontend/config/routes.ts:114-155`). Các tuyến dùng chung — `/tai-khoan`, `/thong-bao`, `/trang-ca-nhan`, `/ho-tro` — không gắn với đối tác nào.

**Hệ quả đối với việc tái sử dụng mã nguồn:** hàm `resolveCurrentPartner` của ứng dụng white-label (`fecredit/src/utils/staff.ts:34-45`) có hai nhánh xử lý — đọc `partnerDetail._id`, hoặc `isOwnerPartner && partners.length === 1`. Nhánh thứ hai không bao giờ thoả trên `frontend/`. Tái sử dụng nguyên trạng dẫn tới:

- Hộp thoại xác nhận không hiển thị trong mọi trường hợp
- Mục "Thông tin nhân viên" tại `/tai-khoan` không hiển thị trong mọi trường hợp
- Chỉ phần kiểm soát theo chiến dịch hoạt động, do cờ đi kèm chiến dịch mà chiến dịch có mang định danh đối tác

Đây là dạng suy giảm chức năng không phát sinh lỗi và không ghi nhật ký, do đó khó phát hiện trong quá trình kiểm thử. Yêu cầu FE-001 xử lý trường hợp này.

### 2.5 Kinh nghiệm rút ra từ bản cài đặt `fecredit/`

Ba nội dung dưới đây có commit đối chứng, được ghi nhận để không lặp lại:

| Nội dung | Đối chứng | Áp dụng cho `frontend/` |
|---|---|---|
| Hộp thoại chặn kích hoạt lúc tải trang | Commit `212f1eca0` đã điều chỉnh: vừa hiển thị thừa với người dùng chỉ xem nội dung, vừa bỏ sót thao tác cần kiểm soát | Chỉ kích hoạt khi người dùng thao tác nộp bài (FE-002) |
| Hộp thoại xác nhận tự kích hoạt khi tải trang | `fecredit/src/components/layout/main/header/index.tsx:100-107`; `parasola/…:101-107` | Không áp dụng — xem FE-006 |
| Suy diễn trạng thái kiểm soát tại tầng giao diện từ `user.statusStaff` | `fecredit/src/utils/staff.ts:84-92`: `statusStaff` gắn theo từng cặp người dùng × đối tác (`UserPartnerRaw.StatusStaff`), tầng giao diện chỉ có một giá trị chung | Chỉ đọc lại `staffGateReason` do backend trả về (FE-002) |

Nội dung thứ ba đặc biệt quan trọng với ứng dụng đa đối tác: một người dùng là nhân viên của đối tác A không đồng thời là nhân viên của đối tác B, nên phép so sánh dựa trên giá trị chung cho kết quả sai.

---

## 3. Mục tiêu và phi mục tiêu

### 3.1 Mục tiêu

| # | Mục tiêu | Thước đo |
|---|---|---|
| G1 | Người dùng `frontend/` bị cổng kiểm soát từ chối nhận được giải thích và hướng xử lý | Không còn trường hợp nộp bài thất bại kèm thông báo lỗi không có hướng dẫn |
| G2 | Nhân viên của đối tác tự khai báo được trạng thái nhân viên trên `frontend/` | Có đường khai báo hoàn chỉnh, không cần can thiệp của quản trị viên |
| G3 | Người dùng của đối tác chưa bật tính năng không ghi nhận thay đổi nào | Không phát sinh giao diện và không phát sinh yêu cầu mạng bổ sung |

### 3.2 Phi mục tiêu

- Đồng bộ trải nghiệm với `fecredit/` và `parasola/`. Mục 6.6 nêu điểm khác biệt có chủ đích.
- Thay đổi logic kiểm soát điều kiện tại backend.
- Bổ sung khả năng phân nhóm nhân viên. Hạng mục này đã được loại bỏ tại PRD-AMB-STAFF-001 phiên bản 5.0.

---

## 4. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Ứng dụng đa đối tác** | `frontend/` — hiển thị nhiều đối tác, mỗi đối tác là một nhánh định tuyến `/:partner/…` |
| **Ứng dụng white-label** | `fecredit/`, `parasola/`, `vpbank/` và các thư mục tương tự — mỗi thư mục phục vụ một đối tác |
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`, nhận giá trị `employee`, `not_employee` hoặc `not_verify`. Gắn theo từng cặp người dùng × đối tác |
| **Đối tác hiện tại** | Đối tác dùng để truy vấn và ghi trạng thái nhân viên tại trang đang hiển thị |
| **Điểm khởi tạo biểu mẫu nộp bài** | Trình xử lý sự kiện đặt `openPostContentModal: true` |
| **Cổng kiểm soát nhân viên** | Khối kiểm tra tại `content.go:132`, thực thi mỗi lượt nộp bài, trước `JoinEvent` |
| **Cờ bật tính năng theo đối tác** | `PartnerOpts.EnableStaffCode` |

---

## 5. Đối tượng người dùng

| Mã | Đối tượng | Nhu cầu |
|---|---|---|
| P1 | Người dùng `frontend/` là nhân viên của một đối tác | Khai báo trạng thái để tham gia chiến dịch nội bộ |
| P2 | Người dùng `frontend/` không thuộc đối tác nào — chiếm đa số | Không bị ảnh hưởng bởi tính năng |
| P3 | Bộ phận vận hành AccessTrade | Có quy trình hướng dẫn người dùng thuộc nhóm P1 |
| P4 | Bộ phận marketing của đối tác | Chiến dịch nội bộ tiếp cận đúng và đủ nhân viên |
| P5 | Người dùng các ứng dụng white-label | Không ghi nhận thay đổi — đây là ràng buộc, không phải mục tiêu |

---

## 6. Yêu cầu chức năng

### FE-001 — Phân giải đối tác hiện tại trên ứng dụng đa đối tác

**Mức độ:** Bắt buộc. Là tiền đề của FE-005.

Hệ thống PHẢI xác định đối tác hiện tại theo quy tắc sau:

| Ngữ cảnh | Kết quả |
|---|---|
| Tuyến định tuyến có tham số `:partner` (`partnerDetail._id` có giá trị) | Đối tác tương ứng |
| Tuyến dùng chung | Không xác định (`undefined`) |

Hệ thống KHÔNG ĐƯỢC suy đoán đối tác hiện tại trong trường hợp không xác định — cụ thể là KHÔNG ĐƯỢC lấy phần tử đầu của danh sách đối tác, KHÔNG ĐƯỢC lấy đối tác truy cập gần nhất, KHÔNG ĐƯỢC lưu trữ để suy diễn về sau. Cơ sở: giá trị suy đoán sai dẫn tới ghi `user-partners.statusStaff` vào sai đối tác, ảnh hưởng trực tiếp tới điều kiện xét thưởng.

Mọi yêu cầu phụ thuộc PHẢI xử lý được kết quả không xác định.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-001.1 | Trên tuyến `/:partner/…`, hàm trả về đúng đối tác của tuyến |
| AC-001.2 | Trên tuyến dùng chung, hàm trả về giá trị không xác định |
| AC-001.3 | Có kiểm thử đơn vị phủ cả hai nhánh |

---

### FE-002 — Kiểm soát điều kiện tại mọi điểm khởi tạo biểu mẫu nộp bài

**Mức độ:** Bắt buộc.

**Cơ sở:** cổng kiểm soát tại backend thực thi ở mỗi lượt nộp bài. Nếu tầng giao diện không kiểm tra trước, người dùng hoàn tất việc nhập liệu rồi mới nhận thông báo từ chối.

**Nguồn dữ liệu:** hệ thống PHẢI đọc lại hai cờ `isRequireCode` và `staffGateReason` do API chi tiết chiến dịch trả về (`backend/pkg/public/service/event.go:1292-1293`). Hệ thống KHÔNG ĐƯỢC tự tái hiện logic kiểm soát tại tầng giao diện; backend tính `staffGateReason` bằng chính hàm thực thi cổng kiểm soát.

**Thứ tự kiểm tra khi người dùng thao tác nộp bài:**

| Thứ tự | Điều kiện | Hành vi |
|---|---|---|
| 1 | `staffGateReason` có giá trị | Hiển thị hộp thoại FE-004; KHÔNG mở biểu mẫu |
| 2 | `isRequireCode` bằng `true` | Hiển thị hộp thoại FE-003; KHÔNG mở biểu mẫu |
| 3 | Còn lại | Mở biểu mẫu nộp bài |

Hộp thoại KHÔNG ĐƯỢC tự kích hoạt khi tải trang.

**Các điểm khởi tạo trên `frontend/`** (đo trên `origin/release` ngày 2026-09-04):

| # | Trình xử lý | Thành phần kích hoạt |
|---|---|---|
| 1 | `src/components/layout/main/header/index.tsx:157` | `:374` |
| 2 | `src/pages/home/components/not-logged-in/index.tsx:42` | `:178` |
| 3 | `src/pages/home/components/logged-in-view/index.tsx:31` | `:129` |

Logic kiểm tra PHẢI được đặt trong một đơn vị dùng chung. Nhân bản khối điều kiện tại từng điểm làm tăng rủi ro bỏ sót, và điểm bị bỏ sót thường là điểm ít được kiểm thử nhất.

**Hai lưu ý về phạm vi:**

1. `src/pages/home/components/post-modal/index.tsx:72,89` KHÔNG phải điểm khởi tạo. Hai lệnh này khôi phục biểu mẫu sau khi đóng hộp thoại phụ Threads/Facebook (`handleCloseThreadsModal`, `handleCloseFacebookModal`). Đặt kiểm tra tại đây buộc người dùng đi qua cổng kiểm soát hai lần trong cùng một luồng.
2. Điểm khởi tạo số 3 được tái sử dụng trên hai trang: thành phần `logged-in-view` hiển thị tại cả trang chi tiết chiến dịch lẫn `/trang-ca-nhan` (thông qua `src/pages/profile/index.tsx:118`), và `PostContentModal` được gắn tại hai vị trí (`src/layouts/event-detail/index.tsx:292` và `logged-in-view/index.tsx:163`). Do đó logic kiểm tra PHẢI nhận dữ liệu chiến dịch từ nơi gọi.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-002.1 | Cả ba điểm khởi tạo cùng gọi một đơn vị kiểm tra |
| AC-002.2 | Chiến dịch không bật điều kiện nào: hành vi không thay đổi, không phát sinh yêu cầu mạng bổ sung |
| AC-002.3 | Không hộp thoại nào tự kích hoạt khi tải trang chi tiết chiến dịch |
| AC-002.4 | Thao tác nộp bài tại `/trang-ca-nhan` được kiểm soát đúng |
| AC-002.5 | Đóng hộp thoại phụ Threads/Facebook rồi quay lại biểu mẫu: không kiểm soát lần thứ hai |
| AC-002.6 | Người dùng chưa đăng nhập: hành vi không thay đổi |
| AC-002.7 | Mã nguồn không chứa phép so sánh dựa trên `user.statusStaff` |

---

### FE-003 — Hộp thoại nhập mã tham gia riêng của chiến dịch

**Mức độ:** Bắt buộc.

Hộp thoại PHẢI đóng được.

**Luồng xử lý:** người dùng nhập mã → gọi `POST /events/:id/input-code-join-event` → tải lại dữ liệu chi tiết chiến dịch để backend tính lại `isRequireCode` → mở biểu mẫu nộp bài.

Hệ thống KHÔNG ĐƯỢC tự suy diễn tại tầng giao diện rằng điều kiện đã thoả sau khi gửi mã thành công. Giá trị `isRequireCode` được tính từ `user-events.options.codeInput` (`backend/pkg/public/service/event.go:1190-1206`).

Việc mở biểu mẫu ngay sau khi tải lại là có chủ đích: người dùng đến bước này với mục đích nộp bài, yêu cầu thao tác thêm một lần là thừa.

Mã nhập vào PHẢI được chuẩn hoá tại thời điểm nhập (viết hoa, loại bỏ khoảng trắng hai đầu) để giá trị gửi đi trùng với giá trị hiển thị. Backend chuẩn hoá lại một lần nữa.

Nội dung hiển thị KHÔNG ĐƯỢC gọi đây là "mã nhân viên". Mã này đối chiếu trực tiếp với `event.Options.StaffCodes`, không tra cứu bảng `manage-codes` (`event.go:1218-1245`); hai đối tượng có vòng đời tách biệt.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-003.1 | Nhập mã hợp lệ: hộp thoại đóng, biểu mẫu nộp bài mở, không cần thao tác bổ sung |
| AC-003.2 | Nhập mã không hợp lệ: thông báo lỗi hiển thị tại chỗ, hộp thoại không đóng |
| AC-003.3 | Mã nhập bằng chữ thường được chấp nhận |
| AC-003.4 | Không hiển thị đồng thời với hộp thoại đăng nhập hoặc hộp thoại hệ thống khác |

---

### FE-004 — Hộp thoại thông báo không đủ điều kiện tham gia

**Mức độ:** Bắt buộc.

Hộp thoại PHẢI đóng được.

| Trường hợp | Nội dung | Hành động |
|---|---|---|
| Người dùng không phải nhân viên, thao tác nộp bài vào chiến dịch có `applyForStaff` | Thông báo chiến dịch giới hạn cho nhân viên của đối tác | Đóng; hoặc chuyển tới FE-005 |

Tên đối tác PHẢI lấy động theo chiến dịch đang hiển thị. Bản cài đặt tham chiếu cố định chuỗi tên đối tác trong nội dung (`fecredit/src/components/layout/main/header/components/modal-staff-code.tsx:145`) do chỉ phục vụ một đối tác; cách làm này hiển thị sai trên ứng dụng đa đối tác.

Hộp thoại PHẢI tự ẩn khi điều kiện không còn đúng — người dùng chuyển sang chiến dịch khác, hoặc vừa hoàn tất khai báo và dữ liệu chi tiết chiến dịch đã được tải lại.

Hộp thoại PHẢI cung cấp lối đi tới mục "Thông tin nhân viên" (FE-005). Cơ sở: theo FE-006, `frontend/` không có hộp thoại xác nhận chủ động, nên đây là điểm tiếp xúc duy nhất giữa hệ thống và một nhân viên chưa khai báo. Thông báo không kèm hướng xử lý không đáp ứng mục tiêu G1.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-004.1 | Hộp thoại đóng được |
| AC-004.2 | Tên đối tác đúng với chiến dịch đang hiển thị |
| AC-004.3 | Chuyển sang chiến dịch khác: hộp thoại tự ẩn |
| AC-004.4 | Có lối đi tới mục "Thông tin nhân viên" |
| AC-004.5 | Hoạt động đúng tại mọi điểm khởi tạo, bao gồm `/trang-ca-nhan` |

---

### FE-005 — Mục "Thông tin nhân viên" tại trang Hồ sơ

**Mức độ:** Bắt buộc.

**Cơ sở.** Tại PRD-AMB-STAFF-001, yêu cầu tương ứng (FR-010) đóng vai trò đường khắc phục: hộp thoại xác nhận chỉ hiển thị một lần, và người dùng đăng ký trước thời điểm bật tính năng được gán trạng thái `not_employee` bởi tiến trình backfill; thiếu đường khắc phục thì các trường hợp này không tự xử lý được.

Trên `frontend/`, do FE-006 không áp dụng hộp thoại xác nhận chủ động, đây là **đường khai báo duy nhất**. Hai yêu cầu bổ sung phát sinh từ đó được nêu tại AC-005.7 và FE-004.

**Nguồn danh sách đối tác.** Hệ thống PHẢI sử dụng danh sách đối tác của ứng dụng, đã được nạp bởi `getListPartner` (`frontend/src/models/main.ts:234-247`) và đã được backend lọc theo tên miền.

Hệ thống KHÔNG ĐƯỢC sử dụng `user.partnerApproval`. Thuộc tính này nằm trên thực thể `user-socials`, không nằm trên thực thể người dùng: `backend/internal/model/mg/user_social.go:26`, gán tại `backend/pkg/public/service/user.go:602-603`; phía giao diện thuộc `IUserSocial` chứ không thuộc `IUser` (`frontend/src/interfaces/user.ts:383,403`). Nội dung của nó là trạng thái phê duyệt tài khoản mạng xã hội theo đối tác, khác với quan hệ người dùng × đối tác trong `user-partners` — nơi lưu `statusStaff`.

Ghi chú: không có API công khai trả về trực tiếp danh sách `user-partners` của người dùng. `backend/pkg/public/service/partner.go:337-341` có tính tập định danh này nhưng chỉ dùng để sắp thứ tự, không đưa vào cấu trúc phản hồi.

**Quy trình dựng danh sách:**

1. Lấy danh sách đối tác của ứng dụng
2. Với mỗi đối tác, gọi `GET /partners/:id/status-employee`
3. Chỉ hiển thị đối tác có `enabled = true`

Điều kiện lọc PHẢI là cờ `enabled`, không phải sự tồn tại của đối tượng phản hồi: backend vẫn trả về đối tượng đầy đủ khi đối tác chưa bật tính năng (`staff_code.go:47-49`).

**Nội dung mỗi dòng:**

| `statusStaff` | Hiển thị |
|---|---|
| `employee` | Mã nhân viên ở chế độ chỉ đọc, kèm hướng dẫn liên hệ bộ phận hỗ trợ khi cần thay đổi |
| Giá trị khác | Ô nhập mã và nút xác nhận |

Chuyển đổi trạng thái theo một chiều: từ `not_employee` sang `employee`. Giao diện KHÔNG ĐƯỢC cung cấp thao tác gỡ trạng thái nhân viên; backend đã từ chối thao tác này (`staff_code.go:105-116`).

**Ràng buộc phi chức năng cục bộ:** số lượng yêu cầu mạng tỉ lệ với số đối tác. Hệ thống PHẢI giới hạn số yêu cầu đồng thời và hiển thị dần. Một yêu cầu thất bại chỉ được làm ẩn dòng tương ứng, KHÔNG ĐƯỢC ảnh hưởng các dòng khác hoặc phần còn lại của trang.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-005.1 | Người dùng không có đối tác nào bật tính năng: mục này không hiển thị |
| AC-005.2 | Hai đối tác bật tính năng: hiển thị hai dòng, trạng thái độc lập |
| AC-005.3 | Khai báo tại đối tác A không ảnh hưởng trạng thái tại đối tác B |
| AC-005.4 | Trạng thái `employee`: không có thao tác gỡ trên giao diện |
| AC-005.5 | Mã không hợp lệ: thông báo lỗi rõ ràng, dữ liệu các dòng khác không mất |
| AC-005.6 | Một yêu cầu `status-employee` thất bại: các dòng còn lại vẫn hiển thị |
| AC-005.7 | Mục hiển thị ở vị trí dễ nhận biết trên trang Hồ sơ |
| AC-005.8 | Người dùng bị gán trạng thái sai bởi tiến trình backfill khai báo lại được |

---

### FE-006 — Không áp dụng hộp thoại xác nhận chủ động

**Mức độ:** Quyết định phạm vi. Đã chốt ngày 2026-09-03.

`frontend/` KHÔNG áp dụng hộp thoại xác nhận trạng thái nhân viên tự kích hoạt khi người dùng truy cập trang đối tác. Đây là điểm khác biệt trải nghiệm duy nhất so với `fecredit/` và `parasola/`, và là khác biệt có chủ đích.

#### 6.1 Hiện trạng của hai ứng dụng white-label

Kết quả rà soát mã nguồn: hai ứng dụng này có hai nhóm hộp thoại, và chỉ một nhóm đã chuyển sang mô hình kiểm soát theo thao tác.

| Hộp thoại | Cơ chế kích hoạt hiện tại | Tham chiếu |
|---|---|---|
| Thông báo không đủ điều kiện | Khi người dùng thao tác nộp bài | commit `212f1eca0` |
| Nhập mã tham gia riêng | Khi người dùng thao tác nộp bài | commit `212f1eca0` |
| Xác nhận trạng thái nhân viên | **Tự kích hoạt khi tải trang** | `fecredit/…/header/index.tsx:100-107`; `parasola/…:101-107` |

Hộp thoại thứ ba chỉ chờ hộp thoại chấp thuận điều khoản hoàn tất, ngoài ra không có điều kiện nào khác. Rà soát toàn bộ nhánh từ 2026-08-01 không ghi nhận thay đổi nào đối với cơ chế này.

Do đó, "tương đương `fecredit/`" và "kiểm soát theo thao tác" là hai phương án khác nhau. Tài liệu này chọn phương án thứ hai.

#### 6.2 Cơ sở của quyết định

Trên ứng dụng một đối tác, việc hỏi chủ động phù hợp: mọi người dùng truy cập ứng dụng đều nằm trong phạm vi câu hỏi. Trên ứng dụng đa đối tác, ba yếu tố sau làm thay đổi kết luận:

**(a) Cơ cấu người dùng.** Ứng dụng hiển thị 17 đối tác. Hỏi chủ động đồng nghĩa với việc chặn toàn bộ người truy cập để xác định một nhóm thiểu số.

**(b) Phạm vi tiến trình backfill.** Tiến trình `admin/service/migration_backfill_staff_status.go` gán `not_employee` theo điều kiện `{partner, statusStaff: {$exists: false}}`, tức chỉ tác động lên bản ghi đã tồn tại trong `user-partners`. Người dùng chưa từng tham gia đối tác không có bản ghi để backfill, do đó `isOpenInputStaffCode` trả về `true` và họ nằm trong nhóm bị hỏi ngay lần truy cập đầu tiên.

**(c) Đường truy cập phổ biến.** Tuyến `/:partner/:slug` thuộc cùng cây định tuyến (`frontend/config/routes.ts:114-155`). Đây là đường truy cập chính từ liên kết chiến dịch chia sẻ trên mạng xã hội. Hỏi chủ động khiến hộp thoại chặn xuất hiện trước nội dung chiến dịch. Cờ ghi nhận thao tác bỏ qua được lưu trong bộ nhớ ứng dụng và mất khi tải lại trang (`fecredit/src/utils/staff.ts:64-72` — thiết kế có chủ đích, vì thao tác bỏ qua không phải một câu trả lời), nên hộp thoại xuất hiện lại ở mỗi lần tải trang.

Áp dụng vào số liệu tại Mục 2.3: FE CREDIT đang vận hành một chiến dịch `applyForStaff` trên `ambassador.koc.com.vn`. Áp dụng hộp thoại chủ động đồng nghĩa với việc mọi lượt truy cập liên kết chiến dịch này đều bị chặn trước khi hiển thị nội dung. Đây là rủi ro về tỉ lệ chuyển đổi và cần thống nhất với bộ phận marketing.

#### 6.3 Phương án thay thế

| Tình huống | Đường xử lý |
|---|---|
| Nhân viên thao tác nộp bài vào chiến dịch nội bộ | Hộp thoại FE-004, kèm lối đi tới FE-005 |
| Nhân viên chủ động khai báo | Mục "Thông tin nhân viên" (FE-005) |

Cả hai đều nằm trong phạm vi tài liệu này.

#### 6.4 Khả năng đảo ngược

Phương án đã chọn là tập con của phương án có hộp thoại chủ động: FE-002, FE-004 và FE-005 đều cần thiết cho cả hai. Trường hợp cần bổ sung hộp thoại chủ động về sau, công việc là thêm mới, không phải viết lại.

Chiều ngược lại không tương đương. Áp dụng hộp thoại chủ động rồi gỡ bỏ đòi hỏi xử lý các bản ghi `user-partners` đã phát sinh: hàm ghi trạng thái sử dụng `SetUpsert(true)` (`backend/pkg/public/service/staff_code.go:192-214`), nên người dùng chỉ truy cập xem và chọn "không thuộc đối tác" cũng tạo bản ghi mới. Bản ghi này không làm sai lệch số lượng creator do `isJoined` và `joinedAt` không được ghi, nhưng vẫn là dữ liệu phát sinh ngoài ý định.

#### 6.5 Tiêu chí chấp nhận

| # | Tiêu chí |
|---|---|
| AC-006.1 | Không hộp thoại nào tự kích hoạt khi truy cập trang đối tác hoặc trang chi tiết chiến dịch |
| AC-006.2 | Mã nguồn không chứa `modal-staff-code`, `visibleModalStaffCode`, `staffCodeDismissed` |
| AC-006.3 | Nhân viên chưa khai báo có đủ hai đường xử lý nêu tại Mục 6.3 |

---

### FE-007 — Bảo toàn hành vi đối với đối tác chưa bật tính năng

**Mức độ:** Bắt buộc. Đây là ràng buộc, không phải hạng mục chức năng.

Backend đã tự vô hiệu theo đối tác (`staff_code.go:47`, `:99`). Tầng giao diện KHÔNG ĐƯỢC bổ sung bất kỳ thành phần nào đối với người dùng của đối tác chưa bật tính năng.

**Tiêu chí chấp nhận:**

| # | Tiêu chí |
|---|---|
| AC-007.1 | Đối tác chưa bật tính năng: không hộp thoại, không mục tại trang Hồ sơ, không yêu cầu mạng bổ sung |
| AC-007.2 | Chiến dịch không bật `applyForStaff` và không có `staffCodes`: luồng nộp bài không thay đổi |
| AC-007.3 | Tắt `EnableStaffCode` của đối tác đang bật: mọi thành phần giao diện biến mất, dữ liệu `statusStaff` được giữ nguyên |
| AC-007.4 | Tập thay đổi không chạm tới `parasola/`, `fecredit/` và 12 thư mục đối tác còn lại |

---

## 7. Yêu cầu phi chức năng

| Mã | Yêu cầu | Nội dung |
|---|---|---|
| NFR-001 | Tương thích ngược | Người dùng của đối tác chưa bật tính năng không ghi nhận thay đổi, kể cả một yêu cầu mạng bổ sung |
| NFR-002 | Không nhân bản logic nghiệp vụ | Mọi quyết định kiểm soát đọc lại cờ từ backend. Tầng giao diện quyết định nội dung hiển thị, không quyết định điều kiện tham gia |
| NFR-003 | Hiệu năng | FE-005 phát sinh số yêu cầu tỉ lệ với số đối tác; PHẢI giới hạn đồng thời, hiển thị dần, và cô lập lỗi theo từng dòng |
| NFR-004 | Ngôn ngữ | Chỉ tiếng Việt. Không bổ sung chuỗi tiếng Anh (`frontend/src/locales/` chỉ có `vi-VN`) |
| NFR-005 | Kiểm thử | Logic tách được PHẢI có kiểm thử đơn vị. Hạ tầng đã sẵn sàng: `jest.config.js` cùng `umi-test`, hiện có 9 tệp kiểm thử đang vận hành |
| NFR-006 | Chất lượng giao diện | Mọi màn hình mới PHẢI được kiểm tra trực quan trên cả desktop và mobile trước khi nghiệm thu. Nội dung kiểm tra tối thiểu: bố cục không vỡ ở khung hẹp, chuỗi tên đối tác dài không tràn, không có hai hộp thoại chồng nhau, thành phần nút giữ đúng kiểu dáng |

**Ghi chú về NFR-006.** Giao diện bám hệ thống thành phần sẵn có của `frontend/` (`components/app/modal`, `components/app/toast`, `components/common/form-field`); không chờ bản thiết kế riêng. Trường hợp đã ghi nhận tại `fecredit/`: thành phần `AppButton` tự bổ sung lớp `rounded-2` và ghi đè `border-radius` của `.btn-primary`.

---

## 8. Phạm vi triển khai

### 8.1 Hạng mục thực hiện

Toàn bộ nằm trong `frontend/`.

| Tầng | Tệp | Nội dung |
|---|---|---|
| Tiện ích | `src/utils/staff.ts` | Viết mới hàm phân giải đối tác; tái sử dụng các hàm phân loại và chuẩn hoá |
| Kiểm thử | `src/utils/staff.test.ts` | Tái sử dụng và bổ sung trường hợp đa đối tác |
| Cấu hình API | `src/configs/api.ts` | Bổ sung 3 endpoint |
| Dịch vụ | `src/services/user.ts`, `partner.ts`, `event.ts` | Bổ sung 3 hàm |
| Kiểu dữ liệu | `src/interfaces/app.ts` | Bổ sung `visibleModalEventCode`, `visibleModalNotEmployee`, `staffStatus`. KHÔNG bổ sung `visibleModalStaffCode`, `staffCodeDismissed` |
| Kiểu dữ liệu | `src/interfaces/event.ts` | Bổ sung `isRequireCode`, `staffGateReason` |
| Trạng thái ứng dụng | `src/models/main.ts` | Bổ sung 2 tác vụ bất đồng bộ |
| Thành phần | `src/components/common/modal-not-employee/` | Tệp mới |
| Thành phần | `src/pages/home/components/modal-event-code/` | Tệp mới |
| Thành phần | `src/pages/account/components/form-staff/` | Tệp mới, kèm lớp dựng danh sách theo đối tác |
| Trang | `src/pages/account/index.tsx` | Bổ sung mục "Thông tin nhân viên" |
| Bố cục | `src/components/layout/main/header/index.tsx` | Gắn hai hộp thoại và đơn vị kiểm tra |
| Điểm khởi tạo | `not-logged-in/index.tsx`, `logged-in-view/index.tsx` | Gọi đơn vị kiểm tra dùng chung |

### 8.2 Hạng mục loại trừ

- `backend/`, `admin/`
- `parasola/`, `fecredit/` và 12 thư mục đối tác còn lại
- Nhãn phân loại nhóm đối tượng trên thẻ chiến dịch
- Điều chỉnh khác biệt cách tính `isRequireCode` giữa màn danh sách và màn chi tiết (nợ kỹ thuật đã ghi nhận tại PRD-AMB-STAFF-001)
- Mọi hình thức phân nhóm nhân viên

---

## 9. Giả định và phụ thuộc

### 9.1 Giả định

| # | Giả định | Ảnh hưởng nếu sai |
|---|---|---|
| A1 | Số đối tác hiển thị trên ứng dụng đủ nhỏ để gọi `status-employee` tuần tự | Cần bổ sung endpoint gộp — hiện thuộc phạm vi loại trừ |
| A2 | `frontend/` tiếp tục sử dụng Umi và dva | Thay đổi cách cài đặt tầng trạng thái |
| A3 | Trạng thái nhân viên gắn theo đối tác, không theo toàn hệ thống | Đã xác minh tại backend |

### 9.2 Phụ thuộc

| # | Phụ thuộc | Bên chịu trách nhiệm |
|---|---|---|
| D1 | `options.enableStaffCode` của đối tác được bật | Vận hành / Backend |
| D2 | Tiến trình backfill `statusStaff` đã chạy cho đối tác trước khi bật cờ | Backend |
| D3 | Bộ ca kiểm thử nghiệm thu | Bộ phận kiểm thử — ngoài phạm vi tài liệu này |

---

## 10. Ngoài phạm vi

- Hộp thoại xác nhận trạng thái nhân viên chủ động (xem FE-006)
- Điều chỉnh hành vi hộp thoại chủ động của `fecredit/` và `parasola/`
- Endpoint trả trạng thái nhân viên của nhiều đối tác trong một yêu cầu — chỉ xem xét khi giả định A1 không thoả
- Triển khai cho 12 thư mục đối tác còn lại
- Nhãn phân loại nhóm đối tượng trên thẻ chiến dịch
- Phân nhóm nhân viên

---

## 11. Truy vết yêu cầu

| PRD-AMB-STAFF-001 (v5.1) | Tài liệu này | Quan hệ |
|---|---|---|
| FR-001 … FR-008 | — | Đã hoàn thiện, sử dụng nguyên trạng |
| FR-009 — Hộp thoại xác nhận | **FE-006** | Không áp dụng, có chủ đích. Cơ sở tại Mục 6.2 |
| FR-010 — Mục Thông tin nhân viên | **FE-005** | Đặc tả lại: từ một khối đơn thành danh sách theo đối tác |
| FR-011 — Cờ `isRequireCode` | **FE-003** | Áp dụng trực tiếp |
| FR-012 — Thông báo không đủ điều kiện | **FE-004** | Áp dụng trực tiếp, bổ sung yêu cầu tên đối tác động và lối đi tới FE-005 |
| FR-013 — Bật/tắt theo đối tác | **FE-007** | Không phát sinh mã nguồn. Xem ghi chú bên dưới |
| FR-014 … FR-017 | — | Đã hoàn thiện |
| — | **FE-001** | Yêu cầu mới. Không có tương ứng tại tài liệu tiền nhiệm |
| — | **FE-002** | Yêu cầu mới. Không có tương ứng tại tài liệu tiền nhiệm |

**Ghi chú về FR-013.** `options.enableStaffCode` là cờ theo đối tác, không theo ứng dụng. Trước hạng mục công việc này, bật cờ cho một đối tác trên thực tế chỉ ảnh hưởng ứng dụng white-label của đối tác đó. Sau khi triển khai, việc bật cờ ảnh hưởng cả ứng dụng white-label lẫn `frontend/`, với điều kiện đối tác hiện diện trên tên miền ACCESSTRADE. Bộ phận vận hành cần nắm thông tin này trước khi bật cờ cho đối tác tiếp theo.

---

## 12. Quyết định đã chốt

| # | Nội dung | Quyết định | Ngày |
|---|---|---|---|
| DEC-01 | Hình thức tài liệu | Hạng mục độc lập, tài liệu riêng. PRD-AMB-STAFF-001 giữ nguyên trạng thái Final | 2026-09-03 |
| DEC-02 | Vị trí mục "Thông tin nhân viên" | Danh sách theo đối tác tại `/tai-khoan` | 2026-09-03 |
| DEC-03 | Nhãn nhóm đối tượng trên thẻ chiến dịch | Không thực hiện | 2026-09-03 |
| DEC-04 | Đưa giao diện `parasola/` lên nhánh phát hành | Không thực hiện; xử lý bằng hạng mục riêng | 2026-09-03 |
| DEC-05 | Nguồn thiết kế giao diện | Bám hệ thống thành phần sẵn có; không chờ bản thiết kế riêng. Ràng buộc chất lượng tại NFR-006 | 2026-09-03 |
| DEC-06 | Nội dung hiển thị | Yêu cầu duy nhất là hiển thị đúng tên đối tác | 2026-09-03 |
| DEC-07 | Bộ ca kiểm thử nghiệm thu | Do bộ phận kiểm thử phụ trách, ngoài phạm vi tài liệu | 2026-09-03 |
| DEC-08 | Đối tác đã bật cờ và hiện diện trên `frontend/` | FE CREDIT — xác nhận bằng API công khai. Mức ưu tiên nâng lên P1 | 2026-09-03 |
| DEC-09 | Hộp thoại xác nhận chủ động | Không áp dụng. Cơ sở tại Mục 6.2 | 2026-09-03 |

---

## 13. Vấn đề còn mở

| # | Nội dung | Ảnh hưởng | Bên xử lý |
|---|---|---|---|
| OI-01 | Xác nhận `options.enableStaffCode` của đối tác FE CREDIT trên production đang được bật. Không tự kiểm chứng được do endpoint yêu cầu xác thực | Không cản trở triển khai; cần trước khi phát hành | Backend |
| OI-02 | Số lượng đối tác hiển thị trên ứng dụng ở thời điểm triển khai, dùng để thẩm định giả định A1. Số liệu ngày 2026-09-03 là 17 | Không cản trở triển khai | Nhóm phát triển |
| OI-03 | Có áp dụng cùng cơ chế kiểm soát theo thao tác cho `fecredit/` và `parasola/` hay không. Lập luận tại Mục 6.2 chỉ áp dụng cho ứng dụng đa đối tác | Ngoài phạm vi; xử lý bằng hạng mục riêng nếu cần | Sản phẩm |

---

## 14. Lịch sử sửa đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 2.0 | 2026-09-04 | Chuẩn hoá toàn bộ văn phong theo khuôn tài liệu kỹ thuật: bổ sung quy ước động từ tình thái, chuyển tiêu chí chấp nhận sang dạng bảng có mã định danh, tách Mục tiêu / Phi mục tiêu, bổ sung Giả định & Phụ thuộc và Nhật ký quyết định. Nội dung kỹ thuật và các tham chiếu mã nguồn giữ nguyên |
| 1.5 | 2026-09-04 | Liên kết tài liệu kỹ thuật. Đính chính số điểm khởi tạo biểu mẫu: 3 thay vì "4+" |
| 1.4 | 2026-09-03 | Chốt FE-006: không áp dụng hộp thoại xác nhận chủ động. Loại 2 thuộc tính trạng thái và bộ biểu tượng khỏi phạm vi |
| 1.3 | 2026-09-03 | Phân tích FE-006: cơ chế kích hoạt, ba hệ quả của phương án hỏi chủ động, tính khả thi của các biến thể |
| 1.2 | 2026-09-03 | Xác nhận hiện trạng production bằng API công khai; nâng mức ưu tiên lên P1. Chốt hướng giao diện và phạm vi kiểm thử |
| 1.1 | 2026-09-03 | Đính chính nguồn dữ liệu của FE-005 |
| 1.0 | 2026-09-03 | Bản đầu |
