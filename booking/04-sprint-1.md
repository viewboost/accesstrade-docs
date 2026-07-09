# Sprint 1 — Chi tiết

> Thuộc Phase 1 ([scope](03-scope-phase-1.md)). Sprint 1 tập trung **3 chức năng**: Import creator · Quản lý danh sách creator · Lọc + tạo shortlist + export.
> *(Sprint 2 — xem cuối file — làm phần creator đăng ký tài khoản + mapping.)*

---

## A. Yêu cầu kỹ thuật (phi user-story)

> Những thứ phải có để 3 chức năng chạy được, nhưng không phải "user làm gì".

### A1. Dựng Admin mới (Next.js)
- Dựng app admin mới (Next.js), **port màn quản lý creator từ techcombank dashboard** (đã có sẵn: bảng danh sách, cột, filter, profile card — cùng stack Next.js nên port được, không viết lại).
- **Không** mở rộng admin cũ (Umi/React 16) — màn creator là surface mới, port từ Next.js sang Umi = viết lại từ đầu.

### A2. Đăng nhập bằng link (tái dùng cơ chế techcombank)
- Admin mới **không tự xây màn login** — dùng cơ chế của techcombank dashboard: chưa đăng nhập → redirect sang trang login chung kèm `returnUrl` → đăng nhập xong nhận `code` qua link → đổi `code` lấy token.
- Backend xác thực **tái dùng nguyên** — chỉ cần phần redirect + đổi code lấy token + gắn token vào API call.

### A3. Model dữ liệu creator (không đụng user sẵn có)
- Thêm **model creator mới** (như đã phân tích): hồ sơ creator **độc lập tài khoản người dùng** — để import được creator chưa có tài khoản.
- **Không migrate / không đụng** dữ liệu user đang chạy — chỉ tạo bảng mới cho luồng import.

### A4. ⚠️ Mảnh nối ẩn — bắt buộc, không thấy ở 3 chức năng bề mặt

> **Phát hiện quan trọng:** Hệ thống hiện hiển thị/lọc danh sách creator qua bản ghi **gắn tài khoản người dùng**. Creator import lại **độc lập user** → nếu chỉ build 3 màn mà bỏ qua các mảnh nối này, **import xong creator không hiện trong danh sách** (list/lọc/export trả 0 kết quả). Đây là điều kiện để Sprint 1 có giá trị thật.

| # | Mảnh nối (MUST) | Vì sao chặn ship |
|---|-----------------|------------------|
| A4.1 | **Cho phép tạo creator KHÔNG cần user** (nới ràng buộc tài khoản) | Tiền đề cho mọi mảnh dưới — không có thì import không tạo nổi bản ghi hợp lệ |
| A4.2 | **Nối import → hiển thị**: creator import lọt vào đúng nguồn mà màn danh sách đang đọc *(cách nhẹ: sinh kèm bản ghi đệm tối thiểu)* | Không có → import xong không ai thấy |
| A4.3 | **Nối làm giàu hồ sơ (enrichment) cho creator import** (trigger + nhận kết quả về model mới) | Enrichment hiện khóa vào bản ghi gắn user → import ra hàng loạt creator **rỗng số liệu** |
| A4.4 | **Lớp đọc gộp** 2 loại creator (qua-user cũ + import-mới) cho danh sách/lọc | Hiện chỉ đọc loại cũ → bỏ lỡ 100% creator import |
| A4.5 | **Trạng thái cho creator import** (để vào được list/lọc theo trạng thái) | List key theo trạng thái → import không có = vô hình |
| A4.6 | **Lọc theo tier ở backend** (nhận tham số tier → quy ra khoảng follower; KHÔNG thêm cột) | Giao diện port từ dashboard gửi tham số tier → backend không nhận = lọc chết ngay |
| A4.7 | **Unique + dedup theo (nền tảng + ID kênh)** + chuẩn hóa handle (xử lý tiền tố @) | Write-path duy nhất; không có → import lại sinh trùng, dọn dẹp tốn kém |

> Phần lớn các mảnh trên xoay quanh **1 mối nối duy nhất** (user-độc-lập). Hướng tiết kiệm nhất: khi import, sinh kèm **bản ghi đệm tối thiểu** để creator import dùng chung pipeline hiển thị/làm giàu/thống kê đang chạy — thay vì viết lại lớp đọc dữ liệu.

---

## A5. 🔴 Quyết định cần chốt TRƯỚC khi code (ảnh hưởng thiết kế dữ liệu)

| # | Quyết định | Khuyến nghị |
|---|-----------|-------------|
| 1 | **Shortlist** là bảng lưu lâu dài (theo khách hàng) hay chỉ chọn-tạm-export-ngay? | Lưu lâu dài (đúng marketplace tra cứu) |
| 2 | **Creator import** ở trạng thái duyệt sẵn (approved) hay phải duyệt tay? | — chờ business |
| 3 | **Creator import không gắn khách hàng** → gán "pool chung" hay miễn quy tắc phân quyền? | — chờ business |

---

## B. User stories

### Chức năng 1 — Import creator từ Excel

> *1a: tận dụng luồng làm giàu hồ sơ (enrichment) đã có. 1b: cần model creator mới (chưa migrate user).*

- **US-1.1** — *Là Ops*, tôi muốn **upload file Excel/CSV danh sách creator** và **map các cột** trong file sang trường hệ thống, để nhập đúng dữ liệu dù file có định dạng khác nhau.
- **US-1.2** — *Là Ops*, tôi muốn **xem trước (preview) + thấy báo lỗi từng dòng** (sai nền tảng / thiếu handle / URL hỏng) trước khi ghi, để không đổ dữ liệu rác vào kho.
- **US-1.3** — *Là Ops*, tôi muốn hệ thống **tự loại trùng** (cùng nền tảng + kênh) khi import, để không tạo creator trùng.
- **US-1.4** — *Là Ops*, sau khi import tôi muốn hệ thống **tự làm giàu hồ sơ** (follower, engagement, category…) qua luồng enrichment có sẵn.
- **US-1.5** — *Là Ops*, tôi muốn **xem lịch sử các đợt import** (số dòng OK / lỗi) để theo dõi và đối chiếu.

### Chức năng 2 — Quản lý danh sách creator *(port từ techcombank dashboard)*

- **US-2.1** — *Là Ops/AM*, tôi muốn **xem danh sách creator** (bảng có phân trang) để duyệt kho.
- **US-2.2** — *Là Ops/AM*, tôi muốn **xem chi tiết một creator** (số liệu, hồ sơ, trạng thái làm giàu) để đánh giá.
- **US-2.3** — *Là Ops*, tôi muốn **phân biệt rõ field tự động (làm giàu, không sửa được) vs field admin nhập (sửa được)**, để không vô tình sửa sai số liệu crawl.

### Chức năng 3 — Lọc, tạo shortlist & export

- **US-3.1** — *Là AM*, tôi muốn **lọc creator** theo nhiều tiêu chí (nền tảng / category / tier / follower / engagement / quốc gia) để tìm creator phù hợp.
- **US-3.2** — *Là AM*, tôi muốn **tạo một danh sách (shortlist)** từ kết quả lọc — thêm/bớt creator, đặt tên, gắn theo khách hàng.
- **US-3.3** — *Là AM*, tôi muốn **export shortlist ra CSV** để gửi cho khách hàng/dùng nội bộ.

---

## C. Điểm cần làm rõ thêm (chờ business)

> (Các quyết định ảnh hưởng thiết kế dữ liệu đã liệt kê ở **A5**.)

| # | Câu hỏi | Liên quan |
|---|---------|-----------|
| 1 | Nguồn file Excel: ai chuẩn bị/làm sạch? cột gồm gì? | Chức năng 1 |
| 2 | "Tier" tự tính từ follower theo **ngưỡng nào** (Nano/Micro/Macro/Mega)? | Chức năng 3 (filter) |

---

## D. SHOULD (nên có, không chặn ship)

- **Audit trail** import/sửa/export creator — khung audit đã có sẵn, chi phí ~0; cần truy vết (PII creator + nhiều khách hàng).
- **Validate format chi tiết** khi import: URL kênh hợp lệ, chuẩn hóa handle, kiểm tra nền tảng — báo lỗi từng dòng rõ ràng.
- **Lọc theo engagement** (mức tương tác) — đi kèm cùng giao diện filter port về; làm chung cơ chế với tier.

## E. LATER (sprint sau)

- Màn xem lịch sử thay đổi (audit UI) đầy đủ + export audit.
- Refactor sạch: tách hẳn enrichment + lớp đọc danh sách khỏi ràng buộc bản ghi gắn-user (Sprint 1 dùng cách "bản ghi đệm" cho nhanh).

---

## F. Ranh giới Sprint 1 (KHÔNG làm)

- ❌ Creator đăng ký tài khoản + mapping về hồ sơ import → **Sprint 2**.
- ❌ Brand portal / creator portal.
- ❌ Booking giao dịch: mời / chốt / HĐ / thanh toán.
- ❌ Di chuyển dữ liệu creator khỏi bảng user đang chạy (dùng "bản ghi đệm", refactor sạch để sau).

---

# Sprint 2 (định hướng)

### Chức năng — Creator đăng ký tài khoản + mapping

- **US** — *Là Creator*, tôi đăng ký tài khoản và cung cấp link kênh social; hệ thống **tự động mapping** với hồ sơ đã import (theo nền tảng + kênh) nếu trùng.
- **US** — *Là Ops*, với trường hợp không tự map được, tôi muốn **mapping thủ công** (gán creator đăng ký với hồ sơ import đúng).

> Đây là bước "claim" hồ sơ import — nối creator thật vào dữ liệu đã có. Chi tiết khi vào Sprint 2.

---

*Bản nháp Sprint 1 — chờ review. Estimate làm sau khi chốt scope.*
