# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM — DASHBOARD PHÂN TÍCH

### Dự án: **Techcombank Influencer Platform (T-Fluencers) — Dashboard phân tích nâng cao**
### Phiên bản: **1.0**
### Ngày cập nhật: **2026-04-23**

---

## Lịch sử thay đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-04-23 | Tài liệu SRS riêng cho Dashboard phân tích (tách khỏi srs-v2.md mục 14) |

---

## Giới thiệu

Dashboard phân tích nâng cao là hệ thống báo cáo độc lập, cung cấp cho AT và TCB góc nhìn tổng thể, đa chiều về hiệu quả chiến dịch Influencer — gồm chỉ số KPI, xu hướng, phân tích theo nền tảng, Influencer, và chiến dịch.

- **Đối tượng sử dụng**: Admin AT, Admin TCB, nhân viên phân tích dữ liệu
- **Ngôn ngữ hỗ trợ**: Tiếng Việt (mặc định) + Tiếng Anh
- **Thiết bị**: Responsive (Desktop / Tablet / Mobile)

---

# I. Yêu cầu chức năng

## 1. Trang Analytics tổng quan

### Mục tiêu
Trang chính của Dashboard, cung cấp view tổng hợp hiệu quả chiến dịch Influencer với khả năng lọc đa chiều theo chiến dịch, Influencer, nền tảng và thời gian.

### Luồng nghiệp vụ
1. Admin truy cập trang Analytics.
2. Hệ thống hiển thị 3 khu vực theo thứ tự:
   - **Platform Overview** (luôn hiển thị, không cần lọc): chỉ số toàn hệ thống
   - **Bộ lọc đa chiều**: Chiến dịch / Thời gian / Influencer / Tag
   - **Dashboard Tabs**: 2 tab — Tổng quan / Creator
3. Admin áp dụng bộ lọc → dữ liệu trong Tabs cập nhật, trang tự động cuộn xuống section kết quả.
4. Trạng thái bộ lọc được lưu vào URL → có thể chia sẻ, bookmark, reload giữ nguyên filter.
5. Admin chuyển tab (Tổng quan / Creator) → nội dung tab tương ứng hiển thị.

### API đã triển khai
- `GET /analytics/global/dashboard` — KPI toàn hệ thống (Platform Overview)
- `GET /analytics/dashboard` — KPI chi tiết theo filter
- `GET /events` — Danh sách chiến dịch cho filter

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.1.1 | Platform Overview luôn hiển thị | Vào trang → khu vực KPI toàn hệ thống hiển thị ngay, không cần lọc |
| AC-DB.1.2 | Tabs chuyển đổi | Click tab Tổng quan/Creator → nội dung tương ứng hiển thị, URL cập nhật |
| AC-DB.1.3 | Filter auto-scroll | Áp dụng filter → trang tự động cuộn xuống khu vực kết quả |
| AC-DB.1.4 | URL state persistence | Reload trang với filter trong URL → filter được áp dụng tự động |
| AC-DB.1.5 | Shareable link | Copy URL có filter → paste trình duyệt khác → hiển thị cùng view |

---

## 2. Bộ lọc đa chiều (Multi-dimensional Filters)

### Mục tiêu
Cho phép người dùng lọc dữ liệu phân tích theo nhiều tiêu chí đồng thời, hỗ trợ **chọn nhiều giá trị cùng lúc (multi-select)** với các filter Chiến dịch, Influencer, Tag.

### Các loại bộ lọc

#### 2.1. Lọc theo Chiến dịch (Multi-select)
- Dropdown checkbox cho phép chọn **nhiều chiến dịch** cùng lúc.
- Tìm kiếm chiến dịch theo từ khóa trong dropdown.
- Mặc định trống = Tất cả chiến dịch.
- Hiển thị badge số lượng đã chọn.

#### 2.2. Lọc theo Thời gian
- 4 tùy chọn: **7 ngày / 30 ngày / 90 ngày / Tùy chỉnh**.
- Preset tự động tính khoảng ngày theo giờ Việt Nam.
- Chọn "Tùy chỉnh" → hiện calendar picker 2 chiều (ngày bắt đầu + ngày kết thúc).

#### 2.3. Lọc theo Influencer (Multi-select)
- 4 chế độ chọn:
  - **Tất cả**: Toàn bộ Influencer
  - **Nhân viên TCB (Techcomers)**: Chỉ nhân viên TCB
  - **Ngoài TCB (Guest)**: Chỉ Influencer bên ngoài
  - **Tùy chọn**: Chọn cụ thể từng Influencer
- Chế độ "Tùy chọn" hiển thị danh sách có tìm kiếm, cho phép chọn nhiều.

#### 2.4. Lọc theo Tag (Multi-select)
- Dropdown checkbox chọn **nhiều tag** để lọc chiến dịch.

#### 2.5. Lọc theo Nền tảng (Multi-select)
- Chọn một hoặc nhiều nền tảng: **Facebook / YouTube / TikTok / Instagram**.

### Hành vi chung
- Nút **Apply**: Áp dụng bộ lọc, URL và dữ liệu cập nhật.
- Nút **Reset**: Xóa toàn bộ filter, về trạng thái ban đầu.
- Tất cả trạng thái filter được lưu vào URL query parameters.

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.2.1 | Multi-select Chiến dịch | Chọn 2+ chiến dịch → dữ liệu tổng hợp từ các chiến dịch đã chọn |
| AC-DB.2.2 | Preset thời gian | Chọn 7d/30d/90d → ngày bắt đầu/kết thúc tự động tính chính xác |
| AC-DB.2.3 | Tùy chỉnh thời gian | Chọn "Tùy chỉnh" → calendar mở → chọn từ ngày đến ngày → dữ liệu lọc đúng khoảng |
| AC-DB.2.4 | Lọc Influencer — 4 chế độ | Chuyển chế độ Tất cả / Nhân viên / Ngoài / Tùy chọn → dữ liệu lọc đúng nhóm |
| AC-DB.2.5 | Multi-select Influencer (Tùy chọn) | Chế độ Tùy chọn → chọn nhiều Influencer → dữ liệu tổng hợp |
| AC-DB.2.6 | Multi-select Tag | Chọn nhiều tag → chỉ lọc chiến dịch có chứa ít nhất một tag đã chọn |
| AC-DB.2.7 | Multi-select Nền tảng | Chọn nhiều nền tảng → dữ liệu từ các nền tảng đã chọn |
| AC-DB.2.8 | Nút Apply | Click Apply → URL cập nhật, dữ liệu refetch đúng filter |
| AC-DB.2.9 | Nút Reset | Click Reset → tất cả filter xóa, URL về trạng thái ban đầu |
| AC-DB.2.10 | Tìm kiếm trong dropdown | Gõ từ khóa trong dropdown Chiến dịch/Influencer → danh sách lọc theo từ khóa |

---

## 3. Platform Overview (Chỉ số toàn hệ thống)

### Mục tiêu
Hiển thị chỉ số toàn hệ thống, luôn sẵn có ngay khi vào trang Analytics, không phụ thuộc vào bộ lọc.

### Luồng nghiệp vụ
1. Admin vào trang Analytics.
2. Hệ thống hiển thị **4 thẻ KPI** (không cần lọc):
   - **Tổng Creator**: Tổng số creator trên platform
   - **Creator mới**: Creator mới trong kỳ
   - **Tỷ lệ hoạt động (Active Rate)**: Tỷ lệ creator đang hoạt động
   - **Tỷ lệ rời bỏ (Churn Rate)**: Tỷ lệ creator ngừng hoạt động
3. Mỗi thẻ có **trend indicator**: mũi tên up/down + % so sánh với kỳ trước.
4. Admin click vào thẻ KPI → áp dụng filter tương ứng xuống khu vực Tabs (drill-down).

### API đã triển khai
- `GET /analytics/global/dashboard` — KPI toàn hệ thống
- `GET /analytics/creator-kpis` — KPI creator (global)

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.3.1 | Hiển thị 4 thẻ KPI | 4 thẻ với dữ liệu đúng từ API toàn hệ thống |
| AC-DB.3.2 | Trend indicator | Hiển thị mũi tên up/down + % so sánh kỳ trước, màu xanh/đỏ/xám theo chiều |
| AC-DB.3.3 | Drill-down | Click vào thẻ → filter tương ứng áp dụng xuống Tabs |
| AC-DB.3.4 | Loading state | Khi đang tải → hiển thị skeleton placeholder |
| AC-DB.3.5 | Error state | Lỗi API → hiển thị alert với nút thử lại |

---

## 4. Tab "Tổng quan"

### Mục tiêu
Cung cấp góc nhìn tổng thể về hiệu quả chiến dịch theo nhiều chiều: KPI chính, xu hướng thời gian, phân bố nền tảng, ngân sách, tương tác, và trạng thái duyệt.

### Luồng nghiệp vụ
1. Admin chọn tab Tổng quan.
2. Hệ thống hiển thị:
   - **6 thẻ KPI chính**: Tổng video, Tổng lượt xem, Ngân sách, CPV (Phí/lượt xem), Tỷ lệ tương tác, Tổng thanh toán
   - **Bảng Campaign Portfolio**: Danh sách chiến dịch với KPI, hỗ trợ sort đa cột, phân trang 20 dòng/trang
   - **Timeline Chart (Line)**: Xu hướng theo thời gian — 4 metric (Lượt xem / Video / Tương tác / Khách mới)
   - **Budget Chart (Bar)**: Ngân sách theo nền tảng/chiến dịch
   - **Interaction Chart (Pie/Doughnut)**: Phân bố tương tác (Lượt xem / Thích / Bình luận / Chia sẻ)
   - **Creator Segments** (collapsible): Phân khúc creator (Đang tham gia / Ngừng / Mới / Quay lại)
   - **Platform Chart (Doughnut)**: Phân bố nội dung theo nền tảng
   - **Approval Chart (Doughnut)**: Trạng thái duyệt (Approved / Pending / Rejected)
   - **Platform Views Chart (Bar)**: So sánh lượt xem theo nền tảng
3. Mỗi thẻ KPI hỗ trợ tooltip giải thích (wiki) khi hover.
4. Khi không có dữ liệu → hiển thị "Không có dữ liệu" với icon và thông báo.

### API đã triển khai
- `GET /analytics/dashboard` — KPI chính (6 thẻ)
- `GET /analytics/campaign-portfolio` — Bảng danh sách chiến dịch
- `GET /analytics/trends` — Timeline xu hướng
- `GET /analytics/budget` — Dữ liệu ngân sách
- `GET /analytics/interactions` — Phân bố tương tác
- `GET /analytics/segments` — Phân khúc creator
- `GET /analytics/platforms` — Phân bố nền tảng
- `GET /analytics/approval` — Trạng thái duyệt

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.4.1 | 6 thẻ KPI chính | Hiển thị đủ 6 KPI với giá trị, đơn vị, trend %, tooltip |
| AC-DB.4.2 | Campaign Portfolio sort | Click header → sort ASC/DESC; Shift+click → sort đa cột |
| AC-DB.4.3 | Campaign Portfolio phân trang | 20 dòng/trang, có điều hướng đầu/giữa/cuối |
| AC-DB.4.4 | Timeline Chart đa metric | Hiển thị 4 metric cùng lúc, hover tooltip đúng giá trị |
| AC-DB.4.5 | Platform Chart | Doughnut 4 nền tảng với tỷ lệ %, tổng = 100% |
| AC-DB.4.6 | Approval Chart | Doughnut 3 trạng thái (Approved / Pending / Rejected), đúng số lượng |
| AC-DB.4.7 | Budget Chart | Bar chart phân bố ngân sách đúng theo nền tảng/chiến dịch |
| AC-DB.4.8 | Interaction Chart | Pie chart đúng tỷ lệ Lượt xem / Thích / Bình luận / Chia sẻ |
| AC-DB.4.9 | Creator Segments | Hiển thị 4 phân khúc với số lượng chính xác |
| AC-DB.4.10 | Empty state | API trả rỗng → hiển thị "Không có dữ liệu" với icon |
| AC-DB.4.11 | Chart responsive | Thu nhỏ trình duyệt → chart co giãn theo container |
| AC-DB.4.12 | Chart theo theme | Chuyển dark/light mode → màu sắc chart tự điều chỉnh |

---

## 5. Tab "Creator"

### Mục tiêu
Phân tích chi tiết theo góc nhìn Influencer — xếp hạng, KPI, thanh toán, và lý do từ chối nội dung.

### Luồng nghiệp vụ
1. Admin chọn tab Creator.
2. Hệ thống hiển thị:
   - **4 thẻ KPI Creator**: Tổng Creator / Creator hoạt động / Hiệu suất trung bình / Phân khúc hàng đầu
   - **Bảng xếp hạng Creator (Leaderboard)**: Rank, Tên, Nền tảng, Video, Lượt xem, Tương tác, Doanh thu
     - Sort đa cột
     - Phân trang 20 Creator/trang
     - **Expandable row**: Click vào dòng → hiển thị chi tiết các chiến dịch Creator đã tham gia
   - **Widget Đối soát (Reconciliation)**: Trạng thái thanh toán — Chờ / Hoàn thành / Thất bại kèm giá trị tiền
   - **Top lý do từ chối (Rejection Reasons)**: Danh sách tag lý do từ chối + số lượng, sắp xếp giảm dần

### API đã triển khai
- `GET /analytics/creators` — Xếp hạng creator
- `GET /analytics/creator-kpis` — KPI creator
- `GET /analytics/transfers` — Dữ liệu đối soát/thanh toán
- `GET /analytics/approval/rejections` — Lý do từ chối

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.5.1 | 4 thẻ KPI Creator | Hiển thị đủ 4 thẻ với dữ liệu và trend |
| AC-DB.5.2 | Leaderboard sort | Click header → sort theo cột (Lượt xem / Tương tác / Doanh thu) |
| AC-DB.5.3 | Expandable row | Click vào dòng → expand hiển thị chiến dịch Creator tham gia; click lại → collapse |
| AC-DB.5.4 | Pagination | 20 Creator/trang, chuyển trang đúng |
| AC-DB.5.5 | Widget Đối soát | Hiển thị 3 trạng thái thanh toán với giá trị tiền đúng định dạng VND |
| AC-DB.5.6 | Top lý do từ chối | Hiển thị top N lý do + số lượng, sắp xếp giảm dần |

---

## 6. Quản lý hồ sơ Influencer (Profiles)

### Mục tiêu
Cho phép Admin xem danh sách, tìm kiếm, lọc, đánh giá và xuất dữ liệu hồ sơ Influencer.

### Luồng nghiệp vụ

**Danh sách Profiles:**
1. Admin truy cập trang Profiles.
2. Lọc theo: **Nền tảng** (multi-select), **Trạng thái** (multi-select), **Tier** (multi-select), **Engagement Tier** (multi-select), **Tìm kiếm** theo tên/handle.
3. Bảng hiển thị danh sách với sort đa cột, phân trang 20 dòng/trang.
4. Click nút **Export** → dialog chọn format (CSV/Excel) → tạo job export → toast thông báo.
5. Click vào Influencer → vào trang chi tiết.

**Chi tiết Profile:**
1. Tab **Tổng quan**:
   - Hàng KPI: Followers, Video, Lượt xem, Tỷ lệ tương tác, CPV, Thanh toán
   - Thông tin hồ sơ: Avatar, tên, bio, link, nền tảng, badge trạng thái
   - Creator Score: Điểm chất lượng kèm breakdown tiêu chí
   - Demographics: Biểu đồ phân bố Tuổi / Giới tính / Địa lý
   - Sibling profiles: Các tài khoản MXH khác của cùng Creator
2. Tab **Đánh giá (Reviews)**:
   - Danh sách đánh giá từ staff (rating + nội dung)
   - Nút "Thêm đánh giá" → mở modal:
     - Rating 5 sao cho từng tiêu chí
     - Nội dung đánh giá (text)
     - Preset lý do từ chối
   - Submit thiếu rating hoặc nội dung → báo lỗi, không cho submit
   - Review mới xuất hiện trong danh sách

### API đã triển khai
- `GET /profiles` — Danh sách Profile (hỗ trợ filter, sort, phân trang)
- `GET /profiles/:id` — Chi tiết Profile
- `GET /profiles/:id/demographics` — Dữ liệu nhân khẩu học
- `GET /profiles/:id/reviews` — Danh sách đánh giá
- `POST /profiles/:id/reviews` — Tạo đánh giá mới
- `POST /data-exports/profiles` — Tạo job export Profiles

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.6.1 | Danh sách Profiles | Hiển thị đầy đủ thông tin, có sort/phân trang |
| AC-DB.6.2 | Lọc Profile đa điều kiện | Kết hợp Nền tảng / Trạng thái / Tier (multi-select) → dữ liệu lọc đúng |
| AC-DB.6.3 | Tìm kiếm Profile | Gõ từ khóa → tìm theo tên/handle, có debounce |
| AC-DB.6.4 | Export Profile | Click Export → dialog chọn CSV/Excel → tạo job, hiển thị toast |
| AC-DB.6.5 | Chi tiết Profile — Tab Tổng quan | Hiển thị đủ KPI, thông tin hồ sơ, score, demographics, sibling profiles |
| AC-DB.6.6 | Demographics chart | Bar chart Tuổi / Giới tính / Địa lý với tỷ lệ đúng |
| AC-DB.6.7 | Sibling profiles | Hiển thị tài khoản cùng Creator trên các nền tảng khác |
| AC-DB.6.8 | Chi tiết Profile — Tab Đánh giá | Hiển thị danh sách đánh giá với rating + nội dung + người đánh giá + thời gian |
| AC-DB.6.9 | Thêm đánh giá | Mở modal → chọn rating + nhập nội dung → submit → đánh giá mới thêm vào danh sách |
| AC-DB.6.10 | Validate đánh giá | Submit thiếu rating hoặc nội dung → báo lỗi, không cho submit |

---

## 7. Quản lý chiến dịch (Campaigns)

### Mục tiêu
Cho phép Admin tạo, xem, chỉnh sửa chiến dịch và quản lý Influencer tham gia thông qua thuật toán matching.

### Luồng nghiệp vụ

**Danh sách Campaigns:**
1. Admin truy cập trang Campaigns.
2. Lọc theo **Trạng thái**, **Tìm kiếm** theo từ khóa.
3. Bảng hiển thị: Tên chiến dịch, badge trạng thái, Ngày tạo, Số Influencer đã chọn.
4. Click nút **Tạo chiến dịch** → vào trang tạo mới.

**Tạo/Chỉnh sửa Campaign:**
1. Form điền thông tin chiến dịch: Tên, mô tả, trạng thái, ngày bắt đầu/kết thúc, ngân sách.
2. Bảng chọn Influencer (multi-select).
3. Nút Save / Cancel.

**Chi tiết Campaign — 3 tab:**
1. **Tab Thông tin (Info)**: Tên, mô tả, trạng thái, ngày, ngân sách, nút Chỉnh sửa.
2. **Tab Matching**:
   - Bảng kết quả matching (thuật toán ghép Influencer-Campaign)
   - Click vào dòng → modal **"Chi tiết điểm matching"** hiển thị breakdown điểm theo tiêu chí
   - Nút **"Chạy Matching"** → trigger thuật toán → kết quả cập nhật
   - Lịch sử các lần chạy
3. **Tab Influencers**:
   - Danh sách Influencer đã chọn
   - Thêm/xóa Influencer
   - Hiệu suất từng Influencer trong chiến dịch (Lượt xem, Tương tác, Doanh thu)

### API đã triển khai
- `GET /campaigns` — Danh sách chiến dịch
- `GET /campaigns/:id` — Chi tiết chiến dịch
- `POST /campaigns` — Tạo chiến dịch mới
- `PUT /campaigns/:id` — Cập nhật chiến dịch
- `POST /campaigns/:id/matching` — Chạy thuật toán matching
- `GET /campaigns/:id/matching-results` — Kết quả matching
- `GET /campaigns/:id/influencers` — Danh sách Influencer đã chọn
- `POST /campaigns/:id/influencers` — Thêm Influencer
- `DELETE /campaigns/:id/influencers/:influencerId` — Xóa Influencer

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.7.1 | Danh sách Campaigns | Hiển thị với badge trạng thái, filter/search hoạt động, phân trang đúng |
| AC-DB.7.2 | Tạo chiến dịch | Điền form → submit → chiến dịch mới xuất hiện trong danh sách |
| AC-DB.7.3 | Validate form | Thiếu trường bắt buộc → báo lỗi, không cho submit |
| AC-DB.7.4 | Chỉnh sửa chiến dịch | Lưu thay đổi → dữ liệu cập nhật, không mất dữ liệu cũ |
| AC-DB.7.5 | 3 tab chi tiết | Chuyển Info / Matching / Influencers → nội dung tương ứng hiển thị đúng |
| AC-DB.7.6 | Modal điểm matching | Click vào dòng trong bảng matching → modal hiện chi tiết điểm theo tiêu chí |
| AC-DB.7.7 | Chạy matching | Click "Chạy Matching" → loading → kết quả cập nhật, lịch sử lưu lại |
| AC-DB.7.8 | Thêm/xóa Influencer | Tab Influencers → thêm hoặc xóa → danh sách cập nhật ngay |
| AC-DB.7.9 | Hiệu suất Influencer | Mỗi Influencer trong chiến dịch hiển thị số liệu hiệu suất |

---

## 8. Quản lý nội dung (Contents)

### Mục tiêu
Cho phép Admin xem danh sách, lọc, sắp xếp và xem chi tiết các bài đăng/video của Influencer trên Dashboard phân tích.

### Luồng nghiệp vụ

**Danh sách Contents:**
1. Admin truy cập trang Contents.
2. Bảng hiển thị 20 dòng/trang với: thumbnail, link, nền tảng, trạng thái, thông số tương tác.
3. Hỗ trợ **sort đa cột** (Shift+click — tối đa 3 cột cùng lúc).
4. Lọc theo nhiều tiêu chí:
   - **Nền tảng** (multi-select)
   - **Chiến dịch (Event)** (multi-select)
   - **Trạng thái** (multi-select)
   - **Khoảng thời gian**
   - **Người tạo** (Creator)
   - **Tag** (multi-select)
   - **Là nhân viên TCB** (toggle Yes/No)
5. Tìm kiếm theo từ khóa.
6. Click vào một content → vào trang chi tiết.

**Chi tiết Content:**
- Metadata: tiêu đề, mô tả, link, ngày đăng
- Thông số hiệu suất: Lượt xem, Thích, Bình luận, Chia sẻ, Tỷ lệ tương tác
- Thông tin Creator liên quan
- Chiến dịch liên quan (nếu có)

### API đã triển khai
- `GET /contents` — Danh sách content (hỗ trợ filter, sort đa cột, phân trang)
- `GET /contents/:id` — Chi tiết content

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.8.1 | Danh sách Content | Hiển thị đủ thumbnail, link, nền tảng, trạng thái, thông số, phân trang đúng |
| AC-DB.8.2 | Sort đa cột | Shift+click header → sort đa cột (VD: trạng thái ASC + lượt xem DESC) |
| AC-DB.8.3 | Lọc tổng hợp | Kết hợp 3+ filter cùng lúc → dữ liệu lọc đúng |
| AC-DB.8.4 | Multi-select Chiến dịch | Chọn nhiều chiến dịch → content lọc đúng |
| AC-DB.8.5 | Multi-select Nền tảng/Tag | Chọn nhiều nền tảng hoặc tag → dữ liệu lọc đúng |
| AC-DB.8.6 | Lọc Nhân viên TCB | Toggle "Nhân viên" → chỉ hiển thị content của staff hoặc guest |
| AC-DB.8.7 | Tìm kiếm | Gõ từ khóa → tìm theo tiêu đề, có debounce |
| AC-DB.8.8 | Chi tiết Content | Hiển thị đủ metadata, thông số, Creator, chiến dịch liên quan |

---

## 9. Import dữ liệu hiệu suất (Performance Import)

### Mục tiêu
Cho phép Admin import file CSV chứa dữ liệu hiệu suất nội dung (views, engagement...) từ các nguồn ngoài, phục vụ phân tích tổng hợp.

### Luồng nghiệp vụ
1. Admin truy cập trang Performance.
2. Click nút **Upload CSV** → chọn file từ máy.
3. Hệ thống validate file:
   - Định dạng .csv
   - Header đúng chuẩn
   - Kích thước file trong giới hạn
4. Upload thành công → tạo **import job**, thêm vào hàng đợi xử lý.
5. Hệ thống hiển thị tiến độ job real-time: **Pending → Processing → Success / Failed**.
6. Job hoàn thành:
   - **Thành công**: Toast thông báo + dữ liệu xuất hiện trong bảng Performance
   - **Thất bại**: Hiển thị chi tiết lỗi theo từng dòng (row number, error message)
7. **Lịch sử import** (panel thu gọn/mở rộng): Thời gian, tên file, trạng thái, số dòng xử lý.
8. Bảng Performance data hỗ trợ filter, sort, phân trang.

### API đã triển khai
- `POST /performance/import` — Upload file CSV
- `GET /performance/imports` — Lịch sử import
- `GET /performance/imports/:id` — Chi tiết job import (bao gồm lỗi)
- `GET /performance/data` — Dữ liệu performance

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.9.1 | Upload CSV hợp lệ | Chọn file .csv đúng format → upload thành công, job được tạo |
| AC-DB.9.2 | Validate format sai | File sai định dạng/header → báo lỗi rõ ràng, không upload |
| AC-DB.9.3 | Tiến độ import | Trạng thái job cập nhật real-time (Pending/Processing/Done) |
| AC-DB.9.4 | Lịch sử import | Panel thu gọn/mở rộng → hiển thị thời gian, tên file, trạng thái, số dòng |
| AC-DB.9.5 | Chi tiết lỗi | Job failed → hiển thị dòng lỗi + lý do (row number, error message) |
| AC-DB.9.6 | Dữ liệu sau import | Import thành công → dữ liệu xuất hiện trong bảng Performance |
| AC-DB.9.7 | Bảng Performance | Hỗ trợ filter, sort, phân trang đúng |

---

## 10. Xuất dữ liệu (Exports)

### Mục tiêu
Quản lý các job xuất dữ liệu bất đồng bộ (CSV/Excel) từ các nguồn khác nhau (Profiles, Campaigns, Analytics...), cho phép Admin tải về file đã hoàn thành.

### Luồng nghiệp vụ
1. Từ các trang khác (VD: Profiles, Analytics), Admin click nút **Export** → mở dialog chọn:
   - Định dạng: CSV / Excel
   - Các trường dữ liệu cần xuất (metrics)
2. Submit → tạo **export job** → thêm vào hàng đợi.
3. Hệ thống hiển thị toast "Job đã được tạo".
4. Admin chuyển sang trang **Exports** để xem danh sách job.
5. Trạng thái job: **Waiting → Running → Completed / Failed**.
6. Job hoàn thành:
   - Hiển thị nút **Download** (kích hoạt)
   - Click Download → hệ thống sinh URL tải → trình duyệt tải file
7. Job thất bại: Hiển thị lý do lỗi, có nút **Retry** nếu khả dụng.
8. Bảng Exports: 20 job/trang, cột: Tên, Loại, Người tạo, Thời gian tạo, Trạng thái, Thao tác.

### API đã triển khai
- `POST /data-exports` — Tạo job export mới
- `GET /data-exports` — Danh sách job (phân trang)
- `GET /data-exports/:id` — Chi tiết job
- `GET /data-exports/:id/download` — Lấy URL tải file
- `POST /data-exports/:id/retry` — Thử lại job thất bại

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.10.1 | Tạo job export | Click Export từ trang khác → dialog mở → chọn format → submit → job tạo |
| AC-DB.10.2 | Chọn định dạng | Chọn CSV/Excel → job tạo đúng format tương ứng |
| AC-DB.10.3 | Danh sách Exports | Hiển thị đúng trạng thái (Waiting/Running/Completed/Failed) với badge màu |
| AC-DB.10.4 | Tải file hoàn thành | Click Download job Completed → file tải về thành công, đúng định dạng |
| AC-DB.10.5 | Disable Download | Job chưa Completed → nút Download bị disable |
| AC-DB.10.6 | Phân trang | 20 job/trang, chuyển trang đúng |
| AC-DB.10.7 | Job thất bại | Job Failed → hiển thị lý do lỗi, có nút Retry |
| AC-DB.10.8 | Retry job | Click Retry → job chuyển về Waiting, xử lý lại |

---

## 11. Đa ngôn ngữ (i18n)

### Mục tiêu
Dashboard hỗ trợ song ngữ **Tiếng Việt** (mặc định) và **Tiếng Anh**, phục vụ người dùng AT và TCB ở nhiều vai trò.

### Luồng nghiệp vụ
1. Admin click Language Switcher ở header → chọn ngôn ngữ (VI / EN).
2. Toàn bộ giao diện chuyển đổi sang ngôn ngữ đã chọn.
3. URL cập nhật theo locale (`/vi/analytics`, `/en/analytics`).
4. Ngôn ngữ được lưu giữ qua các phiên.

### Định dạng dữ liệu theo locale
| Dữ liệu | Tiếng Việt | Tiếng Anh |
|---|---|---|
| Số | `1.234.567` | `1,234,567` |
| Compact | `1,2 Tr` / `3,4 N` | `1.2M` / `3.4K` |
| Tiền tệ | `1.234.567 ₫` | `1,234,567 VND` |
| Phần trăm | `45,3%` | `45.3%` |
| Ngày | `DD/MM/YYYY` | `MM/DD/YYYY` hoặc `DD/MM/YYYY` |

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.11.1 | Chuyển ngôn ngữ | Click Language Switcher vi↔en → toàn bộ UI chuyển đổi chính xác |
| AC-DB.11.2 | URL theo locale | URL `/en/...` hiển thị tiếng Anh, `/vi/...` hiển thị tiếng Việt |
| AC-DB.11.3 | Ngôn ngữ được ghi nhớ | Reload trang → giữ nguyên ngôn ngữ đã chọn |
| AC-DB.11.4 | Format số | Số hiển thị đúng định dạng locale hiện tại |
| AC-DB.11.5 | Format tiền tệ | VND hiển thị với ký hiệu ₫ (vi) hoặc VND (en) |
| AC-DB.11.6 | Format ngày | Calendar, timestamp đúng định dạng theo locale |
| AC-DB.11.7 | Dịch đầy đủ | Không còn text chưa dịch trong bất kỳ trang nào |

---

## 12. Chế độ Sáng/Tối (Dark Mode & Theme)

### Mục tiêu
Hỗ trợ chế độ giao diện Sáng / Tối / Theo hệ thống, giúp người dùng làm việc thoải mái trong nhiều điều kiện môi trường.

### Luồng nghiệp vụ
1. Admin click Theme Toggle ở header.
2. Chọn 1 trong 3 chế độ: **Light / Dark / System** (theo cài đặt hệ điều hành).
3. Toàn bộ UI chuyển sang theme đã chọn ngay lập tức.
4. Các biểu đồ tự điều chỉnh màu sắc (contrast, background, gridlines) theo theme.
5. Theme được ghi nhớ giữa các phiên.
6. Chọn chế độ "System" → UI theo OS, khi OS đổi theme → UI cũng đổi tương ứng.

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.12.1 | Theme toggle | Click Theme Toggle → chuyển Light/Dark/System, UI cập nhật ngay |
| AC-DB.12.2 | Biểu đồ theo theme | Chart tự chuyển màu sắc phù hợp theme |
| AC-DB.12.3 | Theme được ghi nhớ | Reload trang → theme giữ nguyên |
| AC-DB.12.4 | Chế độ System | Chọn "System" → theo OS; OS đổi theme → UI đổi theo |

---

# II. Yêu cầu phi chức năng

## 13. Hiệu năng (Performance)

| Tiêu chí | Yêu cầu |
|---|---|
| Thời gian tải trang Analytics | ≤ 2s (với cache) / ≤ 4s (lần đầu) |
| Thời gian áp dụng bộ lọc | ≤ 1.5s |
| Thời gian render biểu đồ | ≤ 500ms |
| Cache dữ liệu (client-side) | 5-10 phút tùy loại dữ liệu |
| Auto refetch khi filter thay đổi | Có |

---

## 14. Responsive Design

| Thiết bị | Độ rộng | Layout |
|---|---|---|
| Mobile | < 640px | 1 cột, filter thu gọn vào drawer |
| Tablet | 640-1024px | 2 cột cho chart |
| Desktop | 1024-1280px | 2-3 cột |
| Large Desktop | ≥ 1280px | 3+ cột, sidebar cố định |

---

## 15. Accessibility (A11y)

| Tiêu chí | Yêu cầu |
|---|---|
| ARIA labels | Đầy đủ trên nút, input, element tương tác |
| Keyboard navigation | Tab, Enter, Esc hoạt động đúng trên form và dropdown |
| Tôn trọng reduced motion | Khi OS bật "Reduce motion" → giảm animation |
| Color contrast | Đạt WCAG AA (tỷ lệ ≥ 4.5:1 cho text) |
| Form validation | Thông báo lỗi gắn liền với input |

---

## 16. Bảo mật (Security)

| Yêu cầu | Chi tiết |
|---|---|
| Xác thực | Token-based, token hết hạn → tự động đăng xuất |
| Phiên làm việc | Gắn với thiết bị (device ID) |
| XSS prevention | Escape dữ liệu hiển thị |
| HTTPS | Bắt buộc trên production |
| Phân quyền | Chỉ Admin AT/TCB được cấp tài khoản mới truy cập |

---

## 17. Xử lý lỗi & Phục hồi

### Hành vi chung
- **Error Boundary**: Lỗi một section không làm crash toàn trang, chỉ section đó hiện alert + nút thử lại.
- **Toast Notification**: Mọi hành động (thành công/thất bại) đều có toast thông báo, tự ẩn sau 3-5s.
- **Empty State**: API trả rỗng → hiển thị icon + thông báo "Không có dữ liệu".
- **Loading State**: Khi fetch → skeleton placeholder thay vì blank.
- **Network Error**: Mất mạng → banner cảnh báo, tự retry khi có mạng lại.

### Tiêu chí chấp nhận
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-DB.17.1 | Error boundary | API một section lỗi → hiển thị alert + retry, các section khác vẫn hoạt động |
| AC-DB.17.2 | Toast notification | Action thành công/thất bại → toast hiện 3-5s rồi tự ẩn |
| AC-DB.17.3 | Empty state | API trả rỗng → hiển thị icon + "Không có dữ liệu" |
| AC-DB.17.4 | Loading skeleton | Đang fetch → skeleton placeholder thay vì blank |
| AC-DB.17.5 | Network error | Offline → banner cảnh báo, có mạng lại → tự retry |

---

# III. Giao diện dữ liệu (API)

## 18. Danh sách API đã triển khai

### Analytics APIs
| Endpoint | Mô tả |
|---|---|
| `GET /analytics/global/dashboard` | KPI toàn hệ thống (Platform Overview) |
| `GET /analytics/dashboard` | KPI chi tiết theo filter |
| `GET /analytics/platforms` | Phân bố nền tảng |
| `GET /analytics/creators` | Xếp hạng creator |
| `GET /analytics/creator-kpis` | KPI creator |
| `GET /analytics/approval` | Trạng thái duyệt nội dung |
| `GET /analytics/approval/rejections` | Lý do từ chối |
| `GET /analytics/budget` | Dữ liệu ngân sách |
| `GET /analytics/segments` | Phân khúc creator |
| `GET /analytics/interactions` | Dữ liệu tương tác |
| `GET /analytics/trends` | Timeline xu hướng |
| `GET /analytics/transfers` | Đối soát thanh toán |
| `GET /analytics/campaign-portfolio` | Danh sách chiến dịch với KPI |

### Resource APIs
| Endpoint | Mô tả |
|---|---|
| `GET /events` | Danh sách chiến dịch (cho filter) |
| `GET /profiles` | Danh sách Profile Influencer |
| `GET /profiles/:id` | Chi tiết Profile |
| `GET /profiles/:id/demographics` | Nhân khẩu học |
| `GET /profiles/:id/reviews` | Đánh giá Profile |
| `POST /profiles/:id/reviews` | Tạo đánh giá mới |
| `GET /campaigns` | Danh sách chiến dịch |
| `GET /campaigns/:id` | Chi tiết chiến dịch |
| `POST /campaigns` | Tạo chiến dịch |
| `PUT /campaigns/:id` | Cập nhật chiến dịch |
| `POST /campaigns/:id/matching` | Chạy matching |
| `GET /campaigns/:id/matching-results` | Kết quả matching |
| `GET /campaigns/:id/influencers` | Danh sách Influencer |
| `POST /campaigns/:id/influencers` | Thêm Influencer |
| `DELETE /campaigns/:id/influencers/:id` | Xóa Influencer |
| `GET /contents` | Danh sách content |
| `GET /contents/:id` | Chi tiết content |
| `POST /performance/import` | Import CSV hiệu suất |
| `GET /performance/imports` | Lịch sử import |
| `GET /performance/data` | Dữ liệu performance |
| `POST /data-exports` | Tạo job export |
| `GET /data-exports` | Danh sách job export |
| `GET /data-exports/:id/download` | Tải file export |

### Query Parameters chuẩn
```
?events=ID1,ID2              # Multi-chiến dịch
&creators=C1,C2              # Multi-Influencer
&period=7d|30d|90d           # Preset thời gian
&startDate=2026-01-01        # Tùy chỉnh từ ngày
&endDate=2026-02-01          # Tùy chỉnh đến ngày
&platforms=facebook,youtube,tiktok,instagram  # Multi-nền tảng
&tagIds=T1,T2                # Multi-tag
&page=1&limit=20             # Phân trang
&sort=field1:asc,field2:desc # Sort đa cột
&keyword=search_term         # Tìm kiếm
&status=active               # Trạng thái
```

---

# IV. Tóm tắt nghiệm thu

## 19. Tổng số tiêu chí chấp nhận

| Mục | Nội dung | Số AC |
|---|---|---|
| 1 | Trang Analytics tổng quan | 5 |
| 2 | Bộ lọc đa chiều | 10 |
| 3 | Platform Overview | 5 |
| 4 | Tab "Tổng quan" | 12 |
| 5 | Tab "Creator" | 6 |
| 6 | Quản lý hồ sơ Influencer (Profiles) | 10 |
| 7 | Quản lý chiến dịch (Campaigns) | 9 |
| 8 | Quản lý nội dung (Contents) | 8 |
| 9 | Import hiệu suất (Performance) | 7 |
| 10 | Xuất dữ liệu (Exports) | 8 |
| 11 | Đa ngôn ngữ | 7 |
| 12 | Chế độ Sáng/Tối | 4 |
| 17 | Xử lý lỗi & Phục hồi | 5 |
| **TỔNG** | | **96 tiêu chí AC** |

---

**Hết tài liệu SRS — Dashboard phân tích nâng cao**
