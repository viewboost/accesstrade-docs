# Product Requirements Document: Cập nhật giao diện Trang cá nhân Ambassador

| | |
|---|---|
| **Mã tài liệu** | PRD-AMB-PROFILE-PAGE-001 |
| **Phiên bản** | 1.1 |
| **Ngày ban hành** | 2026-10-23 |
| **Trạng thái** | Đã triển khai trên nhánh tính năng, chờ nghiệm thu |
| **Mức độ ưu tiên** | P1 |
| **Cấp độ dự án** | Level 2 — thay đổi frontend, không đổi API hoặc dữ liệu |
| **Đối tượng đọc** | Product Owner, PM, Frontend Dev, QA, Tech Lead |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Nhánh triển khai** | `feat/profile-page-ui-from-frontend` |
| **Ứng dụng áp dụng** | `fecredit/`, `creator-app/` |
| **Ứng dụng tham chiếu** | `frontend/` |
| **Thiết kế kỹ thuật** | [TECH_SPEC.md](./TECH_SPEC.md) |

---

## Document Overview

Tài liệu này là nguồn yêu cầu sản phẩm và tiêu chí nghiệm thu cho việc cập nhật trang
`/trang-ca-nhan` trên `fecredit/` và `creator-app/`. Tài liệu trả lời **cần thay đổi gì,
vì sao cần thay đổi và điều kiện nào được coi là đạt**; chi tiết file triển khai chỉ
được ghi ở phụ lục truy vết Mục 11.

PRD được lập **hồi cứu** sau khi nhánh tính năng đã có code. Vì vậy, mọi mô tả hiện trạng
và yêu cầu trong tài liệu đã được đối chiếu với:

- nhánh nền `release` để xác định hành vi trước thay đổi;
- năm commit của `feat/profile-page-ui-from-frontend` liệt kê tại Mục 12;
- giao diện tham chiếu trong `frontend/src/pages/home/components/`;
- hợp đồng dữ liệu đang dùng trong `backend/internal/model/mg/user_event.go` và response
  của `GET /events/by-slug`.

### Nguyên tắc biên soạn

1. Không coi việc sao chép giao diện từ `frontend/` là yêu cầu tự thân; mỗi phần được
   giữ lại phải giải quyết một vấn đề người dùng nêu trong Mục 2.
2. Không port nguyên xi khi hành vi của FE Credit khác ứng dụng tham chiếu.
3. Không tạo hợp đồng API mới chỉ để phục vụ thay đổi trình bày.
4. Các phép tính và ánh xạ số liệu phải chỉ ra field nguồn, không suy diễn từ UI.
5. Trạng thái “đã triển khai” không đồng nghĩa “đã nghiệm thu”; Mục 10 vẫn là cửa kiểm
   bắt buộc trước khi gộp hoặc phát hành.

## 1. Tóm tắt

Trang `/trang-ca-nhan` của FE Credit đang dùng bố cục hai tab **Tiến trình** và
**Danh sách bài đăng**. Bố cục này không cho creator thấy đầy đủ thu nhập tạm tính,
không có bảng thống kê theo nền tảng và khó chuyển qua lại giữa các chiến dịch.

Hạng mục này thay trang cũ bằng bố cục đã được kiểm chứng ở ứng dụng Ambassador
`frontend/`: cột chọn chiến dịch ở bên trái, khối thu nhập và thống kê ở bên phải,
danh sách bài đăng ở phía dưới. Khi kế thừa bố cục, hệ thống PHẢI giữ các quy tắc
riêng đang có của FE Credit: điều kiện hoàn thiện hồ sơ, cổng nhân viên, mã tham gia,
khóa chiến dịch hết hạn và nút chia sẻ chương trình.

Thay đổi chỉ sử dụng dữ liệu API đang có. Không sửa backend, không migration và không
thay đổi hợp đồng API.

## 2. Bối cảnh và vấn đề

| Vấn đề hiện tại | Ảnh hưởng |
|---|---|
| Thu nhập bị phân tán giữa các tab, không có tổng tiền tạm tính rõ ràng | Creator khó đối chiếu số tiền đang chờ duyệt, chờ đối soát và đã đối soát |
| Không có bảng thống kê theo nền tảng | Creator không biết lượt xem và lượt xem tính thưởng đến từ nguồn nào |
| Danh sách chiến dịch dùng chip ngang | Khó sử dụng khi creator tham gia nhiều chiến dịch |
| Bố cục tham chiếu từ `frontend/` thiếu một số nguồn và thiếu tiền chờ duyệt | Sao chép nguyên trạng sẽ hiển thị thiếu dữ liệu |
| Modal mã tham gia không được mount tại trang cá nhân | Nút Đăng bài có thể bật state nhưng không hiện hộp thoại |
| Banner liên kết tài khoản dùng `position: fixed` nhưng không giữ chỗ | Banner che breadcrumb và phần đầu nội dung |
| Wording “Thử thách của tôi” không khớp tên trang | Người dùng khó nhận biết đích điều hướng |

## 3. Mục tiêu

| Mã | Mục tiêu | Thước đo |
|---|---|---|
| G1 | Creator xem được toàn bộ thông tin thu nhập quan trọng trên một màn hình | Tổng tiền và các trạng thái tiền hiện đúng từ dữ liệu API |
| G2 | Creator đối chiếu được hiệu quả theo từng nền tảng | Mọi nguồn của chiến dịch có một dòng thống kê, kể cả khi số liệu bằng 0 |
| G3 | Creator chuyển chiến dịch thuận tiện | Chọn chiến dịch từ sidebar và nội dung cập nhật đúng |
| G4 | Không làm mất hành vi nghiệp vụ riêng của FE Credit | Các cổng hồ sơ, nhân viên, mã tham gia và hết hạn hoạt động như trước |
| G5 | Giao diện sử dụng được trên desktop và mobile | Không tràn khung; bảng cuộn ngang khi cần; banner không che nội dung |

### 3.1 Chỉ số nghiệm thu

| Mã | Chỉ số | Ngưỡng đạt |
|---|---|---|
| M1 | Sai lệch giữa tổng tạm tính và `waiting + pending + completed` | 0 |
| M2 | Nguồn trong `applyForSources` bị mất khỏi bảng | 0 |
| M3 | Luồng Đăng bài bỏ qua hoặc đảo thứ tự một cổng nghiệp vụ tại PP-006 | 0 |
| M4 | Test các hàm thuần nêu tại NFR-005 | 100% pass |
| M5 | Trường hợp banner che breadcrumb/nội dung ở desktop hoặc mobile | 0 |

## 4. Phạm vi

### 4.1 Trong phạm vi

- Trang `/trang-ca-nhan` của `fecredit/` và `creator-app/`.
- Bố cục chọn chiến dịch, thu nhập, bảng theo nguồn, mốc thưởng và danh sách bài đăng.
- Luồng Đăng bài và Gửi bạn bè tại trang cá nhân.
- Wording của mục điều hướng tới trang cá nhân.
- Sửa khoảng giữ chỗ cho banner nhắc liên kết tài khoản.
- Kiểm thử đơn vị cho phép tính thu nhập, ánh xạ nguồn và gom chiến dịch theo ADV.

### 4.2 Ngoài phạm vi

- Thay đổi backend hoặc cấu trúc `user_event`/`event_reward`.
- Thay đổi cách crawl, duyệt hoặc đối soát bài đăng.
- Thiết kế lại trang `/tai-khoan`.
- Áp dụng đồng loạt cho 14 ứng dụng white-label còn lại.
- Thay đổi giao diện hoặc nghiệp vụ của `frontend/`.

## 5. Người dùng và user stories

| Đối tượng | Nhu cầu |
|---|---|
| Creator tham gia một chiến dịch | Xem nhanh thu nhập, thống kê và bài đã đăng |
| Creator tham gia nhiều chiến dịch | Chuyển đúng chiến dịch mà không rời trang |
| Creator có bài đang chờ duyệt | Thấy khoản tiền đang được giữ tạm tính, không bị báo thiếu |
| Creator thuộc chiến dịch có điều kiện | Nhận đúng hướng dẫn hoàn thiện hồ sơ, khai báo nhân viên hoặc nhập mã |
| Bộ phận vận hành | Có số liệu hiển thị nhất quán với trạng thái backend để hỗ trợ người dùng |

### US-01 — Theo dõi thu nhập

> Là một creator, tôi muốn thấy tổng thu nhập tạm tính và từng trạng thái tiền trên
> cùng một màn hình để biết khoản nào đã đối soát, khoản nào còn chờ và vì sao tổng
> có thể thay đổi.

Ánh xạ yêu cầu: PP-001, PP-003, PP-005.

### US-02 — Đối chiếu theo nền tảng

> Là một creator đăng nội dung trên nhiều nền tảng, tôi muốn xem lượt xem và lượt xem
> tính thưởng theo từng nguồn để tự đối chiếu với kết quả chiến dịch.

Ánh xạ yêu cầu: PP-004.

### US-03 — Chuyển chiến dịch

> Là một creator tham gia nhiều chiến dịch, tôi muốn chuyển chiến dịch ngay trên trang
> cá nhân để xem đúng thu nhập và bài đăng mà không phải quay về trang chủ.

Ánh xạ yêu cầu: PP-002, PP-008.

### US-04 — Tiếp tục hành động

> Là một creator đang xem kết quả, tôi muốn có thể đăng bài hoặc gửi chiến dịch cho
> bạn bè ngay tại đây, đồng thời nhận đúng hướng dẫn nếu chưa đủ điều kiện tham gia.

Ánh xạ yêu cầu: PP-006, PP-007.

### US-05 — Hỗ trợ người dùng

> Là nhân viên vận hành, tôi muốn số liệu và thông báo trên trang phản ánh đúng trạng
> thái backend để có thể giải thích cho creator mà không cần suy đoán cách frontend tính.

Ánh xạ yêu cầu: PP-003, PP-004, PP-006.

## 6. Yêu cầu chức năng

### PP-001 — Bố cục thống nhất cho Trang cá nhân

Trang PHẢI hiển thị breadcrumb **Trang chủ / Trang cá nhân**, sidebar chiến dịch,
khối **Doanh thu của bạn**, mốc thưởng và danh sách bài đăng trong cùng một trang.
Bố cục hai tab **Tiến trình / Danh sách bài đăng** cũ PHẢI được loại bỏ.

**Tiêu chí chấp nhận:**

- [ ] Desktop hiển thị sidebar bên trái và nội dung bên phải.
- [ ] Mobile xếp các khối theo chiều dọc, không mất nội dung.
- [ ] Breadcrumb thẳng hàng với trang `/tai-khoan`.
- [ ] Tên chiến dịch, “Lần cập nhật gần nhất” và “Lần cập nhật kế tiếp” (gần nhất + 2 giờ)
  được hiển thị khi API có `lastUpdatedAt`, giống `frontend/`.
- [ ] Wording trên trang y hệt `frontend/`.

### PP-002 — Chọn chiến dịch theo ADV

Hệ thống PHẢI gom chiến dịch theo `event.partner._id` và giữ thứ tự ADV do API
`/partners` trả về.

**Tiêu chí chấp nhận:**

- [ ] Site chỉ có một ADV liệt kê thẳng các chiến dịch, không thêm tầng thu gọn dư thừa.
- [ ] Có từ hai ADV trở lên thì hiển thị tầng ADV → chiến dịch và cho phép thu gọn.
- [ ] Nhóm chứa chiến dịch hiện tại được mở sẵn.
- [ ] Việc người dùng tự mở nhóm khác không bị reset khi đổi dữ liệu.
- [ ] Chiến dịch không khớp danh sách ADV vẫn xuất hiện trong một nhóm dự phòng, không bị mất.
- [ ] Trạng thái đang chọn có `aria-current` để hỗ trợ công nghệ trợ năng.

### PP-003 — Hiển thị số tiền tạm tính

Tổng tiền tạm tính PHẢI được tính từ `userEventStatistic.cashTotal` theo công thức:

```text
Tổng tạm tính = waiting + pending + completed
```

Trong đó `waiting` là chờ duyệt, `pending` là chờ đối soát và `completed` là đã đối
soát. Giá trị thiếu, `null` hoặc không phải số được coi là 0.

**Tiêu chí chấp nhận:**

- [ ] Tổng tiền bao gồm cả khoản chờ duyệt.
- [ ] Luôn hiển thị hai dòng Đã đối soát và Chờ đối soát.
- [ ] Chỉ hiển thị dòng Chờ duyệt khi giá trị lớn hơn 0 để giảm nhiễu.
- [ ] Tất cả giá trị dùng cùng hàm định dạng tiền tệ của ứng dụng.

### PP-004 — Bảng thống kê theo nền tảng

Bảng PHẢI tạo một dòng cho từng phần tử trong `event.options.applyForSources`, theo
đúng thứ tự cấu hình chiến dịch.

Các nguồn tối thiểu phải hỗ trợ: TikTok, YouTube, YouTube Shorts, Facebook, Facebook
Reels, Facebook Post, Instagram, Instagram Reels, Threads và Shopee. Tên nguồn hiển thị
giống `frontend/`: khóa `snake_case` viết hoa chữ đầu từng từ (`tiktok` → Tiktok,
`youtube_shorts` → Youtube Shorts). Nguồn mới không được loại bỏ.

| Cột | Nguồn dữ liệu |
|---|---|
| Nguồn | tên nguồn như trên |
| Lượt xem | `<source>.view.completed` |
| Lượt xem tính thưởng (đã đối soát) | `<source>.viewRewarded.cashback` |
| Lượt xem tính thưởng (chờ đối soát) | `<source>.viewRewarded.completed` |

**Tiêu chí chấp nhận:**

- [ ] Không tự lấy `Lượt xem` trừ cho `Lượt xem tính thưởng`; mỗi số đọc đúng field backend.
- [ ] Field thiếu hiển thị 0.
- [ ] Tiêu đề cột và tên nguồn y hệt `frontend/`.
- [ ] Mỗi cột số sắp xếp theo chính giá trị của cột đó.
- [ ] Tooltip ở cột “Lượt xem tính thưởng (đã đối soát)” chép nguyên văn `frontend/`.
- [ ] Tiêu đề nằm trên một hàng; khung hẹp cho phép cuộn ngang thay vì làm vỡ layout.

### PP-005 — Mốc thưởng

Khi chiến dịch có `eventSchema`, trang PHẢI hiển thị dãy mốc và dòng **Thưởng:** như
`frontend/`. Số tiền bằng `cashReward.pending + cashReward.completed`.

**Tiêu chí chấp nhận:**

- [ ] Không cộng khoản chưa được duyệt vào số tiền thưởng.
- [ ] Không hiển thị khối khi chiến dịch không có mốc.

### PP-006 — Đăng bài không làm mất cổng nghiệp vụ

Nút **Đăng bài** PHẢI giữ thứ tự kiểm tra sau:

1. Yêu cầu hoàn thiện hồ sơ.
2. Cổng chiến dịch dành cho nhân viên.
3. Mã tham gia chiến dịch.
4. Mở biểu mẫu nộp bài.

**Tiêu chí chấp nhận:**

- [ ] Chiến dịch hết hạn vô hiệu hóa nút và giải thích bằng tooltip.
- [ ] Thiếu hồ sơ dẫn tới `/tai-khoan?returnEvent=<slug>`.
- [ ] Không đủ điều kiện nhân viên thì không mở đồng thời modal mã hoặc modal nộp bài.
- [ ] Chiến dịch yêu cầu mã hiển thị được `ModalEventCode` ngay trên trang cá nhân.
- [ ] Nhập mã thành công tải lại chiến dịch và mở biểu mẫu nộp bài.
- [ ] Nộp bài thành công đóng biểu mẫu và giữ luồng refresh hiện có.

### PP-007 — Chia sẻ đúng đường dẫn chiến dịch

Nút **Gửi bạn bè** PHẢI chia sẻ URL của chiến dịch, không chia sẻ URL hiện tại
`/trang-ca-nhan`. URL PHẢI được dựng bằng helper dùng chung và xét slug ADV khi cần.

### PP-008 — Danh sách bài đăng

Danh sách bài đăng PHẢI nằm sau khối thu nhập, tiếp tục dùng bộ lọc, phân trang và
luồng tải dữ liệu hiện có. Tiêu đề PHẢI dùng token cỡ chữ hợp lệ của ứng dụng.

### PP-009 — Điều hướng và banner liên kết tài khoản

- Mục menu dẫn tới `/trang-ca-nhan` PHẢI có nhãn **Trang cá nhân**.
- Banner liên kết tài khoản dạng fixed PHẢI tạo khoảng giữ chỗ bằng đúng chiều cao thực
  tế của banner.
- Khoảng giữ chỗ PHẢI cập nhật khi banner đổi chiều cao theo viewport và được gỡ khi
  người dùng đóng banner.

## 7. Yêu cầu phi chức năng

- **NFR-001 — Tương thích:** Không thay đổi API, backend hoặc dữ liệu lưu trữ.
- **NFR-002 — Đồng bộ:** `fecredit/` và `creator-app/` phải có hành vi tương đương cho
  toàn bộ PP-001 đến PP-009.
- **NFR-003 — Responsive:** Không có cuộn ngang toàn trang ở breakpoint mobile; chỉ
  bảng thống kê được phép cuộn trong khung của nó.
- **NFR-004 — Khả năng truy cập:** Nút thu gọn có `aria-expanded`, chiến dịch hiện tại
  có `aria-current`, nút icon có nội dung thay thế phù hợp.
- **NFR-005 — Khả năng kiểm thử:** Phép tính tiền, ánh xạ nguồn và gom chiến dịch phải
  nằm trong hàm thuần và có kiểm thử đơn vị.
- **NFR-006 — Wording đồng nhất:** Mọi chữ trên trang lấy y hệt `frontend/`. Chỉ khác
  `frontend/` ở số liệu: tổng tạm tính gồm `waiting` (PP-003) và đủ khóa nguồn (PP-004).

## 8. Phụ thuộc và giả định

### 8.1 Phụ thuộc

| Phụ thuộc | Điều kiện sử dụng |
|---|---|
| `GET /events` | Trả danh sách chiến dịch kèm `partner._id`, `partner.name`, `code` và `name` |
| `GET /partners` | Trả danh sách ADV theo thứ tự hiển thị mong muốn |
| `GET /events/by-slug` | Trả `userEventStatistic`, `eventSchema`, `lastUpdatedAt` và các cờ điều kiện tham gia |
| Luồng nộp bài hiện có | Tiếp tục nhận `eventHome`, người dùng và callback tạo nội dung như trước |
| Helper URL chiến dịch | Dựng đúng URL theo slug chiến dịch và slug ADV |

### 8.2 Giả định

- `cashTotal.waiting`, `pending`, `completed` có cùng đơn vị tiền tệ.
- `applyForSources` là nguồn sự thật về các dòng cần xuất hiện trong bảng.
- Số liệu `viewRewarded` do backend chốt; frontend không tự tái tạo quy tắc tính thưởng.
- `creator-app/` và `fecredit/` cùng phục vụ trải nghiệm FE Credit ở hai lộ trình triển
  khai, nên phải giữ hành vi tương đương trong phạm vi tài liệu này.

Nếu một giả định không còn đúng, Product và Tech Lead phải cập nhật PRD hoặc lập tài
liệu thay thế trước khi đổi cách tính trên giao diện.

## 9. Rủi ro và biện pháp

| Rủi ro | Biện pháp |
|---|---|
| Sao chép UI từ `frontend/` làm mất quy tắc riêng FE Credit | Tách `PostActions`, giữ thứ tự bốn cổng tại PP-006 |
| Tổng tiền thấp hơn số backend giữ ngân sách | Cộng đủ `waiting + pending + completed`, khóa bằng unit test |
| Nguồn mới hoặc nguồn ít dùng biến mất khỏi bảng | Fallback trực tiếp theo khóa nguồn và sinh nhãn chuẩn hóa |
| Bảng rộng làm tràn khung | `min-width: 0` cho cột nội dung và scroll ngang riêng cho bảng |
| Banner che nội dung trên kích thước màn hình khác nhau | Đo chiều cao bằng `ResizeObserver`, không hardcode pixel |
| Modal chồng nhau | Không hiển thị mã tham gia khi modal hệ thống đang mở; cổng nhân viên chạy trước |

## 10. Nghiệm thu và release gate

Một mục chỉ được đánh dấu đạt khi có bằng chứng là kết quả test tự động, ảnh/video kiểm
thử giao diện hoặc payload API dùng trong ca kiểm. Việc code đã tồn tại không được coi
là bằng chứng nghiệm thu.

- [ ] PP-001 đến PP-009 đạt trên `fecredit/` và `creator-app/`.
- [ ] Unit test của `cash-summary`, `source-rows` và `group-events-by-partner` đều pass.
- [ ] Kiểm tra thủ công desktop và mobile với: một ADV/một chiến dịch, một ADV/nhiều
  chiến dịch, nhiều ADV, chiến dịch hết hạn và chiến dịch yêu cầu mã.
- [ ] Kiểm tra creator có đủ ba trạng thái tiền; tổng hiển thị bằng tổng ba trạng thái.
- [ ] Kiểm tra chiến dịch có `facebook_post`, `threads` và `shopee` không hiển thị sai 0
  khi API có dữ liệu.
- [ ] Banner liên kết tài khoản không che breadcrumb trước và sau khi resize viewport.
- [ ] Không phát sinh thay đổi backend hoặc lỗi hồi quy ở luồng nộp bài.

### 10.1 Ma trận ca kiểm tối thiểu

| Nhóm | Ca kiểm bắt buộc |
|---|---|
| Dữ liệu tiền | Không có thống kê; chỉ có `waiting`; đủ ba trạng thái; field sai kiểu |
| Nguồn | Nguồn phổ biến; `facebook_post`; `threads`; `shopee`; nguồn mới chưa có nhãn |
| Chiến dịch | Một ADV/một chiến dịch; một ADV/nhiều chiến dịch; nhiều ADV; chiến dịch lệch danh sách ADV |
| Cổng nộp bài | Thiếu hồ sơ; không đủ điều kiện nhân viên; yêu cầu mã; hết hạn; đủ điều kiện |
| Responsive | Desktop; mobile; bảng rộng; banner một dòng; banner xuống nhiều dòng; đóng banner |

### 10.2 Điều kiện phát hành

- Toàn bộ unit test liên quan pass trên cả `fecredit/` và `creator-app/`.
- Không còn lỗi P0/P1 trong phạm vi PP-001 đến PP-009.
- Các ca kiểm thủ công ở Mục 10.1 có bằng chứng và người nghiệm thu.
- Product Owner xác nhận wording; QA xác nhận responsive và các cổng nộp bài.

## 11. Phụ lục A — Truy vết triển khai

| Yêu cầu | Thành phần chính |
|---|---|
| PP-001 | `pages/home/components/logged-in-view/index.tsx` |
| PP-002 | `pages/home/components/partner-sidebar/` |
| PP-003 | `pages/home/components/statistic/cash-summary.ts`, `index.tsx` |
| PP-004 | `pages/home/components/statistic/source-rows.ts`, `table.tsx`, `style.scss` |
| PP-005 | `logged-in-view/index.tsx`, `event-schema` |
| PP-006, PP-007 | `logged-in-view/components/post-actions/index.tsx` |
| PP-008 | `pages/home/components/my-post/index.tsx` |
| PP-009 | `components/layout/main/header/components/profile.tsx`, `alert-link-account.tsx` |

Các đường dẫn trong bảng tồn tại dưới cả `fecredit/src/` và `creator-app/src/` trừ khi
được ghi chú khác.

## 12. Phụ lục B — Trạng thái triển khai

Đã triển khai trên `feat/profile-page-ui-from-frontend` qua các commit:

| Commit | Nội dung |
|---|---|
| `dc6d0715a` | Bố cục mới, thu nhập, bảng theo nguồn, sidebar ADV/chiến dịch |
| `cda10e7ad` | Sửa tổng tiền, modal mã, tràn bảng và banner che nội dung |
| `7d3e8ba40` | Làm phẳng sidebar một ADV, đồng bộ spacing và wording |
| `4e7acc29b` | Hoàn thiện tiêu đề bảng theo nền tảng |
| `3fc93a490` | Đồng bộ tiêu đề bảng với Ambassador |
| `0a0c6cef5` | Trả toàn bộ wording về y hệt Ambassador |

Tài liệu này ghi lại yêu cầu sản phẩm và tiêu chí nghiệm thu của phần đã triển khai;
không dùng PRD `ambassador/creator-profile/prd.md` vì tài liệu đó mô tả đăng ký,
xác minh và enrich kênh social — một phạm vi nghiệp vụ khác.

## Lịch sử sửa đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-10-23 | Bản đầu, lập hồi cứu từ nhánh tính năng |
| 1.1 | 2026-10-28 | Wording y hệt `frontend/`: “Doanh thu của bạn”, hiện “Lần cập nhật kế tiếp”, “Thưởng:”, tên nguồn và tooltip như `frontend/` |
