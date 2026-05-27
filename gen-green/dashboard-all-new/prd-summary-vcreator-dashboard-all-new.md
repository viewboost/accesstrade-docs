# PRD Summary — vCreator Brand Portal (Dashboard All-New)

**Dự án:** Gen-Green / vCreator
**Loại tài liệu:** PRD Summary (rút gọn, do phạm vi lớn)
**Cập nhật:** 2026-05-27
**Tham chiếu nguồn:** PRD T-Fluencers Dashboard (Techcombank) + [PRD vCreator Dashboard v2 (2026-04-12)](../vcreator-dashboard/prd-vcreator-dashboard-v2-2026-04-12.md)

> **Định vị sản phẩm:** Đây là **Brand Portal** — cổng dành cho **brand (Partner / ADV / Advertiser)** tự đăng nhập để theo dõi hiệu quả chương trình creator marketing **của chính mình**.
> **Người dùng là brand, KHÔNG phải đội vận hành nội bộ vCreator.** Đội vận hành tiếp tục dùng admin hiện tại; portal này không phục vụ tác vụ vận hành nội bộ.

> **Lưu ý phạm vi (kế thừa từ PRD TCB):** KHÔNG bao gồm khởi tạo/chỉnh sửa thử thách (Event CRUD), matching influencer, đánh giá influencer (review/rating). Cũng **KHÔNG** có module "Dữ liệu mở thẻ" (đặc thù thẻ TCB, không tồn tại ở vCreator).

---

## 1. Tổng quan

**vCreator Brand Portal** là cổng analytics tự phục vụ (self-service) cho brand. Sau khi đăng nhập, brand chỉ thấy dữ liệu thuộc Partner (ADV) của mình: thống kê KPI, theo dõi nội dung video/content, danh sách creator tham gia, và xuất dữ liệu.

### 1.1. Nguyên tắc nền tảng
- **Scope theo Partner = danh tính đăng nhập:** Brand đăng nhập → toàn bộ dữ liệu tự động giới hạn trong Partner của brand. Không có việc "chọn Partner" như tool nội bộ.
- **i18n:** Toàn bộ text qua `next-intl`, **Tiếng Việt (mặc định)** + Tiếng Anh.
- **Trạng thái URL / cache:** Bộ lọc, sort, phân trang, tab đồng bộ URL; TanStack Query cache ~5 phút.
- **Giao diện:** Next.js 16 App Router, TailwindCSS + shadcn/ui, theme sáng/tối, responsive desktop + tablet.

---

## 2. ⭐ Vai trò Brand / Partner (ADV) — Trung tâm của portal

Đây là phần quan trọng nhất và cần làm rõ tuyệt đối: **portal này thuộc về brand, mọi thứ xoay quanh brand đang đăng nhập.**

### 2.1. Partner (ADV) là gì
- **Partner (ADV)** = **brand / nhà quảng cáo (Advertiser)** sử dụng nền tảng vCreator để chạy chương trình creator marketing. Mỗi Partner là một **tenant** độc lập.
- Một Partner sở hữu: tập **thử thách (event)** riêng, tập **creator** tham gia, tập **nội dung (video/content)**, ngân sách, đối soát thanh toán riêng.
- Mô hình dữ liệu Partner: `name`, `slug`, `logo`, `status`, `options` (feature toggle theo tenant, ví dụ `allowResubmitRejectedContent`). → Portal phải tôn trọng feature toggle & nhận diện thương hiệu (logo/tên) theo Partner.

### 2.2. Partner = danh tính người đăng nhập (KHÔNG phải filter)
- Tài khoản brand gắn với **một hoặc nhiều Partner** (multi-brand được hỗ trợ). Khi đăng nhập, hệ thống tự xác định tập Partner từ phiên đăng nhập.
- **Toàn bộ dữ liệu portal được scope cứng theo Partner đang xem** — KPI, biểu đồ, bảng nội dung, danh sách creator, export. Không bao giờ có option "Tất cả Partner".
- **Quy tắc hiển thị bộ chuyển Partner (quan trọng):**
  - Tài khoản gắn **đúng 1 Partner** → **KHÔNG hiển thị** bất kỳ bộ chọn/lọc Partner nào; scope cứng vào Partner đó, ẩn hoàn toàn UI chọn Partner.
  - Tài khoản gắn **nhiều Partner** → hiển thị **bộ chuyển Partner** ở header; mặc định chọn Partner đầu tiên; đổi Partner → reload toàn bộ scope.
- Branding: header hiển thị logo + tên Partner đang đăng nhập/đang xem để brand biết rõ đang ở không gian của mình.

### 2.3. Cô lập dữ liệu (multi-tenant isolation) — BẮT BUỘC
- Backend **enforce** scope Partner ở mọi endpoint; frontend tuyệt đối không được truy cập hay rò rỉ dữ liệu của Partner khác.
- **Portal là READ-ONLY:** brand chỉ xem/lọc/xuất dữ liệu của mình. Không có tác vụ ghi (duyệt/từ chối nội dung, sửa creator, chỉnh ngân sách...) — các tác vụ vận hành đó nằm ở admin nội bộ.
- Mọi request gắn ngữ cảnh Partner từ token/phiên (không nhận `partnerId` tùy ý từ client để tránh truy cập chéo).

### 2.4. Acceptance Criteria (Brand / Partner)
- [ ] Đăng nhập brand → tự scope đúng (tập) Partner từ phiên.
- [ ] Tài khoản 1 Partner → **không hiển thị** bộ chọn/lọc Partner; scope cứng.
- [ ] Tài khoản nhiều Partner → có bộ chuyển Partner ở header; đổi Partner reload toàn bộ scope.
- [ ] Không bao giờ có option "Tất cả Partner".
- [ ] Header hiển thị logo + tên Partner đang xem.
- [ ] Mọi widget/table/export chỉ chứa dữ liệu của Partner đang xem.
- [ ] Backend chặn truy cập chéo Partner kể cả khi client cố truyền tham số khác.
- [ ] Feature toggle theo Partner được tôn trọng (ví dụ resubmit rejected content).

---

## 3. Đối tượng người dùng (đều là phía brand)

| Vai trò (brand-side) | Nhu cầu chính |
|----------------------|---------------|
| **Brand Marketing Manager** | Theo dõi KPI chương trình của brand, hiệu quả nội dung & creator |
| **Brand Business Lead** | Xem tổng quan hiệu quả, ngân sách, ROI; xuất báo cáo cho nội bộ brand |
| **Brand Analyst** | Phân tích chi tiết, export dữ liệu theo nhu cầu |

> Đội vận hành vCreator **không** dùng portal này.

---

## 4. Khái niệm đặc thù vCreator (khác TCB)

| Khái niệm | Mô tả |
|-----------|-------|
| **Partner (ADV)** | Brand/advertiser — danh tính đăng nhập, scope toàn bộ portal (mục 2). |
| **Phân loại CBNV / Bên ngoài** | `account_type`: `staff` (CBNV của brand) hoặc `creator` (bên ngoài). Filter & badge trên bảng. |
| **Cơ sở làm việc (workplace)** | `workplace_name`. Grouped dropdown (~6 nhóm, ~57 cơ sở: VinPalace, Vinpearl, VinWonders, Vinpearl Golf, Green SM, Khác). Phục vụ brand có lực lượng CBNV theo cơ sở. |
| **Hashtag cá nhân** | Hashtag định danh creator, hiển thị trên bảng nội dung & creator. |

> TCB dùng "Techcomer" + mã nhân viên; vCreator dùng "CBNV/Bên ngoài" + cơ sở làm việc.

---

## 5. Chức năng theo module (Functional Requirements — rút gọn)

> Tất cả module mặc định đã scope theo Partner đăng nhập (mục 2). Các filter dưới đây là filter **trong phạm vi Partner đó**.

### FR1 — Xác thực & tài khoản
- OAuth2 code flow: redirect → login → callback code → exchange token; phiên xác định Partner của brand.
- Token inject qua HTTP interceptor; 401 → clear token + redirect login; không expose token qua URL.
- Đổi mật khẩu, đăng xuất (có xác nhận) ở Cài đặt.

### FR2 — Thống kê (Analytics) — `/analytics`
Mọi widget scope theo **Partner (đăng nhập) + Date range + CBNV + Cơ sở**.
- **Platform Overview:** KPI tổng quan của brand (Tổng creator, Creator mới, Tỷ lệ hoạt động/nghỉ) + trend % so kỳ trước.
- **Filter bar (trong phạm vi brand):** Date range, Event (thử thách của brand), Creator, Warning Tag, **CBNV/Bên ngoài**, **Cơ sở làm việc**.
- **KPI chính:** Tổng video, Lượt xem, Ngân sách %, CPV TB, Engagement, Tổng phí quảng cáo.
- **Widget/biểu đồ:** Bảng thử thách của brand; biểu đồ timeline (toggle series, Daily/Monthly); ngân sách (progress + đã dùng/tổng/còn lại VND); tương tác (view/like/comment + %); trạng thái duyệt (stacked bar + Top 5 lý do từ chối); phân bố & lượt xem theo nền tảng; đối soát thanh toán (KPI + bảng đợt chuyển).
- Skeleton loading; xử lý lỗi tải dữ liệu.

### FR3 — Nội dung (Contents) — `/contents`
- **Bảng:** Thumbnail, Tiêu đề (→ chi tiết), Creator, **Phân loại (CBNV/Bên ngoài)**, **Cơ sở làm việc**, **Hashtag cá nhân**, Nguồn (nền tảng), Sự kiện, Lượt xem (sort), Trạng thái (Đã duyệt/Chờ/Từ chối), Warning Tags, Ngày đăng. Phân trang 20/trang.
- **Filter:** Search, Date range, Nguồn, Event, Status, Warning Tag, Phân loại, Cơ sở. Debounce 500ms, reset trang khi đổi filter.
- **Chi tiết nội dung:** thông tin bài, thống kê (view/like/comment), điểm AI + recommendation (nếu có), tóm tắt LLM (nếu có).
- **Read-only:** không có duyệt/từ chối/sửa nội dung trên portal — chỉ xem & lọc.

### FR4 — Creator — `/creators`
- **Bảng:** Avatar, Tên (→ chi tiết), **Hashtag cá nhân**, **Phân loại**, **Nơi làm việc**, Tổng view, Tổng tiền, Đã rút, Số video, Ngày tham gia. Sort theo view/tiền/video; phân trang 20/trang.
- **Filter:** Search, Phân loại (CBNV/Bên ngoài), Cơ sở làm việc.
- **Chi tiết creator:** chỉ số tổng hợp + danh sách nội dung/thử thách đã tham gia (trong phạm vi brand).

### FR5 — Xuất dữ liệu (Exports) — `/exports`
- **Export chọn cột:** dialog checkbox cho brand tự chọn cột (default bỏ tick cột thừa: ID video, Thumbnail, Sentiment, Ngày tạo); "Chọn tất cả"/"Mặc định". Áp dụng cho Nội dung, Creator, Thống kê. Job scope theo Partner + gắn `columns[]`.
- **Quản lý job:** bảng lịch sử (Tên, Loại, Trạng thái, Số dòng, Số cột, Kích thước, Thời gian, Download). Trạng thái: Hoàn tất (download qua pre-signed URL) / Đang xử lý (polling) / Thất bại (retry).

### FR6 — Layout & Cài đặt
- **Header:** logo + tên Partner đang xem; bộ chuyển Partner **chỉ hiện khi tài khoản gắn nhiều Partner** (1 Partner → ẩn); theme toggle; chuyển ngôn ngữ; tài khoản.
- **Sidebar:** Thống kê, Nội dung, Creator, Xuất dữ liệu, Cài đặt. Active highlight, collapse trên mobile.
- **Cài đặt:** đổi mật khẩu (≥8 ký tự, xác nhận khớp), đăng xuất (có xác nhận).

---

## 6. Yêu cầu phi chức năng (NFR — rút gọn)

| # | Yêu cầu |
|---|---------|
| NFR1 | **Multi-tenant isolation:** Backend enforce scope Partner theo phiên; chặn truy cập chéo Partner kể cả khi client giả mạo tham số. |
| NFR2 | **Hiệu suất:** Portal load < 3s; filter/pagination < 500ms; chart render < 1s. |
| NFR3 | **Cache:** TanStack Query stale 5 phút; retry 3 lần exponential backoff; invalidate khi mutation. |
| NFR4 | **i18n:** Mọi text qua `next-intl`, không hardcode, đủ VI/EN. |
| NFR5 | **Bảo mật:** OAuth2 token qua interceptor; 401 auto-redirect; không expose token URL. |
| NFR6 | **Tương thích:** Chrome 90+/Safari 15+/Firefox 90+/Edge 90+; desktop 1024px+ & tablet 768px+. |
| NFR7 | **Deploy:** Standalone build, Docker-ready; ENV `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_ADMIN_URL`. |

---

## 7. Dependencies & Open Questions

### Cần backend bổ sung
- Fields `account_type`, `workplace_name`, `hashtag` trên user/content response.
- Cơ chế xác định Partner từ phiên đăng nhập brand; mọi API analytics/contents/creators/exports tự scope theo Partner (không nhận `partnerId` từ client).
- API `POST /exports` hỗ trợ `columns[]`.

### Đã chốt
- **Read-only:** Brand chỉ xem/lọc/xuất, không có tác vụ ghi (duyệt/từ chối/sửa).
- **Multi-brand:** Hỗ trợ 1 tài khoản gắn nhiều Partner; tài khoản 1 Partner thì ẩn bộ chọn Partner.

### Open questions
1. Export format: chỉ `.xlsx` hay thêm CSV?
2. Filter persistence: URL params (đề xuất) hay localStorage?

---

## 8. So sánh nhanh với PRD TCB (nguồn port)

| Khía cạnh | TCB | vCreator Brand Portal (tài liệu này) |
|-----------|-----|--------------------------------------|
| Người dùng | Đội nội bộ TCB | **Brand (Partner/ADV)** tự phục vụ ⭐ |
| Tenant | Single-tenant | **Multi-tenant; scope theo brand đăng nhập** |
| Cách chọn phạm vi | Filter thử thách | **Tự scope theo danh tính brand** (không có "chọn Partner") |
| Phân loại nhân viên | Techcomer + mã | CBNV/Bên ngoài + Cơ sở làm việc |
| Module "Dữ liệu mở thẻ" | Có (đặc thù thẻ) | **Không có** |
| Profiles MXH chi tiết / Demographics | Có | Không (ngoài domain Gen-Green) |
| Export | Job bất đồng bộ | Job + **chọn cột linh hoạt** |

---

## 9. Tài liệu liên quan
- [PRD vCreator Dashboard v2 (2026-04-12)](../vcreator-dashboard/prd-vcreator-dashboard-v2-2026-04-12.md) — nguồn chi tiết FR
- Mô hình Partner: `vcreator/backend/internal/model/mg/partner.go`
