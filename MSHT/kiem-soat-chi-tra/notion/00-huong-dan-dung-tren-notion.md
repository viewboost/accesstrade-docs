# Hướng dẫn dựng workspace Notion — Kiểm soát chi trả MSHT

Bộ này gồm **5 database** import thẳng từ CSV, liên kết với nhau bằng Relation, và các view dựng sẵn
để quản lý tiến độ. Nội dung lấy từ [`ke-hoach-scrum-nhom-a.md`](../ke-hoach-scrum-nhom-a.md) và
[`ke-hoach-trien-khai.md`](../ke-hoach-trien-khai.md).

| File | Thành database | Số bản ghi |
|---|---|---|
| `db-backlog.csv` | **Backlog** — story · spike · task | 26 |
| `db-sprint.csv` | **Sprint** | 3 |
| `db-tieu-chi-g1.csv` | **Tiêu chí nghiệm thu G1** | 9 |
| `db-quyet-dinh.csv` | **Quyết định đang chặn** | 10 |
| `db-bat-bien.csv` | **Bất biến BB** | 12 |

---

## Bước 1 — Import

Trong Notion: `Import` → `CSV` → chọn file. Mỗi file thành một database riêng. Import **Backlog cuối
cùng**, vì nó cần trỏ Relation sang 4 database kia.

## Bước 2 — Sửa kiểu thuộc tính

Notion import tất cả thành `Text`. Đổi lại như sau — **đây là bước quan trọng nhất**, làm sai thì
không lọc và không rollup được.

### Database **Backlog**

| Thuộc tính | Kiểu | Cấu hình |
|---|---|---|
| Mã | Title | giữ nguyên |
| Tên | Text | |
| Loại | Select | `Story` · `Spike` · `Task` |
| Làn | Select | `Kỹ thuật` · `Vận hành` · `Đối tác` |
| Sprint | **Relation** → Sprint | |
| Điểm | Number | |
| Trạng thái | **Status** | Nhóm *Chưa bắt đầu*: `Chưa bắt đầu` · Nhóm *Đang làm*: `Đang làm`, `Đang review`, `Bị chặn` · Nhóm *Xong*: `Xong` |
| Vai trò | Select | `BE` · `BE lead` · `QC` · `PM` · `Vận hành` · `Dữ liệu` |
| Bất biến | **Relation** → Bất biến BB | giá trị cách nhau bằng dấu cách, cần nối tay |
| Phụ thuộc | **Relation** → chính Backlog (self-relation) | |
| Tiêu chí chấp nhận | Text | |
| Rủi ro | Select | `Cao` · `Trung bình` · `Thấp` |
| Ngày bắt đầu / Ngày kết thúc | Date | |

> **Mẹo:** gộp `Ngày bắt đầu` và `Ngày kết thúc` thành **một** thuộc tính Date có bật *End date* nếu
> muốn dùng Timeline gọn hơn. Import xong rồi gộp tay.

### Database **Sprint**

| Thuộc tính | Kiểu |
|---|---|
| Tên | Title |
| Mục tiêu sprint | Text |
| Ngày bắt đầu / Ngày kết thúc | Date |
| Trạng thái | Select: `Chưa bắt đầu` · `Đang chạy` · `Đã đóng` |
| Điểm cam kết | Number |
| Cổng | Select: `Chuẩn bị G1` · `G1` · `G2` · `G3` · `G4` |

### Database **Tiêu chí nghiệm thu G1**

| Thuộc tính | Kiểu |
|---|---|
| Mã | Title |
| Tiêu chí | Text |
| Cổng | Select |
| Bất biến | Relation → Bất biến BB |
| Story liên quan | Relation → Backlog |
| Đạt | Checkbox *(đổi từ Text: `Chưa` = bỏ tick)* |
| Cách kiểm | Text |

### Database **Quyết định đang chặn**

| Thuộc tính | Kiểu |
|---|---|
| Mã | Title · Nội dung cần quyết | Text |
| Người quyết | Select |
| Chặn việc gì | Relation → Backlog |
| Cần trước | **Date** |
| Trạng thái | Select: `Đang chờ` · `Đã chốt` · `Không áp dụng` |
| Đề xuất của DISO | Text |

### Database **Bất biến BB**

| Thuộc tính | Kiểu |
|---|---|
| Mã | Title · Nội dung | Text |
| Nhóm | Select: `A`…`F` |
| Story bảo vệ | Relation → Backlog |
| Có test tự động | Checkbox |

---

## Bước 3 — Rollup và Formula

### Trên database **Sprint**

| Tên | Kiểu | Cấu hình |
|---|---|---|
| Số việc | Rollup | Relation `Backlog` → thuộc tính `Mã` → **Count all** |
| Điểm trong sprint | Rollup | → `Điểm` → **Sum** |
| Việc đã xong | Rollup | → `Trạng thái` → **Count per group** *(hoặc Count checked nếu dùng checkbox phụ)* |
| **% hoàn thành** | Formula | `if(prop("Điểm trong sprint") == 0, 0, prop("Điểm đã xong") / prop("Điểm trong sprint"))` — đặt định dạng **Percent**, bật hiển thị dạng **Bar** |
| Lệch cam kết | Formula | `prop("Điểm trong sprint") - prop("Điểm cam kết")` |

> Để có `Điểm đã xong`: thêm trên Backlog một Formula `Điểm xong` = `if(prop("Trạng thái") == "Xong", prop("Điểm"), 0)`
> rồi Rollup **Sum** thuộc tính đó lên Sprint.

### Trên database **Backlog**

| Tên | Kiểu | Cấu hình |
|---|---|---|
| Điểm xong | Formula | `if(prop("Trạng thái") == "Xong", prop("Điểm"), 0)` |
| Quá hạn | Formula | `and(prop("Trạng thái") != "Xong", dateBefore(prop("Ngày kết thúc"), now()))` → Checkbox đỏ trong view |
| Đang bị chặn | Rollup | Relation `Phụ thuộc` → `Trạng thái` → **Show original**, dùng để lọc nhanh |

### Trên database **Tiêu chí nghiệm thu G1**

| Tên | Kiểu |
|---|---|
| **Tiến độ G1** | Đặt ở đầu trang: `Count` các bản ghi có `Đạt` = checked / tổng 9 |

---

## Bước 4 — Các view cần tạo

### Backlog

| View | Kiểu | Cấu hình |
|---|---|---|
| **Sprint hiện tại** | Board | Group theo `Trạng thái`; Filter `Sprint` = sprint đang chạy; Sort `Rủi ro` giảm dần |
| **Theo sprint** | Board | Group theo `Sprint` |
| **Timeline** | Timeline | Dùng `Ngày bắt đầu` → `Ngày kết thúc`; Group theo `Làn` để thấy 3 làn chạy song song |
| **Ba làn** | Board | Group theo `Làn` — nhìn ra việc đối tác và vận hành không nằm trong sprint phát triển |
| **🔴 Đang bị chặn** | Table | Filter `Trạng thái` = `Bị chặn` **hoặc** `Rủi ro` = `Cao` |
| **Quá hạn** | Table | Filter `Quá hạn` = checked |
| **Theo vai trò** | Table | Group theo `Vai trò` — dùng lúc planning để thấy ai đang gánh nặng |

### Sprint

| View | Kiểu | Cấu hình |
|---|---|---|
| **Tiến độ** | Table | Hiện `% hoàn thành` dạng Bar, `Điểm cam kết`, `Lệch cam kết` |
| **Lịch** | Calendar | Theo `Ngày bắt đầu` |

### Tiêu chí nghiệm thu G1

| View | Kiểu | Cấu hình |
|---|---|---|
| **Bảng cổng G1** | Table | Sort theo `Mã`; hiện `Đạt`, `Story liên quan`, `Cách kiểm` |
| **Chưa đạt** | Table | Filter `Đạt` = unchecked |

### Quyết định đang chặn

| View | Kiểu | Cấu hình |
|---|---|---|
| **Sắp tới hạn** | Table | Filter `Trạng thái` = `Đang chờ`; Sort `Cần trước` tăng dần |
| **Lịch quyết định** | Calendar | Theo `Cần trước` |

---

## Bước 5 — Tự động hoá (Database automation)

Notion cho phép đặt automation ngay trên database. Ba cái đáng làm:

| Khi nào | Làm gì | Vì sao |
|---|---|---|
| `Trạng thái` đổi thành `Xong` | Set `Ngày hoàn thành` = today | Có dữ liệu thật để vẽ burndown |
| `Trạng thái` đổi thành `Bị chặn` | Gửi thông báo cho PM | Epic này phụ thuộc nhiều vào quyết định bên ngoài |
| Bản ghi mới thêm vào **Quyết định** | Gửi thông báo cho người quyết | Quyết định chậm là rủi ro số một của dự án |

---

## Bước 6 — Trang tổng quan cho founder

Tạo một page `📊 Kiểm soát chi trả — Tổng quan`, chèn theo thứ tự:

1. **Callout** ghi mục tiêu cổng đang hướng tới: *"G1 — Không tạo thêm khoản chi thứ hai nữa"*.
2. **Linked view** của `Tiêu chí nghiệm thu G1`, kiểu Table, chỉ hiện `Mã` · `Tiêu chí` · `Đạt`
   → đây là thước đo duy nhất có nghĩa với founder: **9 ô, xanh hết là qua cổng**.
3. **Linked view** của `Sprint` kiểu Table, hiện `% hoàn thành` dạng Bar.
4. **Linked view** của `Quyết định đang chặn`, filter `Đang chờ`, sort `Cần trước` — danh sách việc
   founder cần quyết, có hạn cụ thể.
5. **Linked view** của `Backlog` filter `Rủi ro` = `Cao`.

> **Nguyên tắc theo dõi:** báo cáo tiến độ bằng **số tiêu chí nghiệm thu đã đạt**, không bằng số story
> đã xong. Story xong mà tiêu chí chưa đạt thì cổng chưa qua.

---

## Lưu ý khi import

- **Relation không import được từ CSV.** Các cột `Sprint`, `Phụ thuộc`, `Bất biến`, `Story liên quan`,
  `Chặn việc gì` sau khi import vẫn là Text — đổi kiểu sang Relation rồi **nối tay** theo giá trị đang
  có trong ô. 26 bản ghi nên làm tay khoảng 15 phút.
- **Giữ lại cột Text gốc** trước khi đổi kiểu (duplicate property) để còn đối chiếu lúc nối.
- **Ngày trong CSV là giả định**: Sprint 0 bắt đầu 28/09/2026. Nếu ngày khởi động khác, sửa ở database
  `Sprint` trước rồi chỉnh lại ngày trong `Backlog` theo.
- **Điểm và velocity cũng là giả định** (2 BE · 1 QC · 1 PM bán thời gian, velocity 34đ/sprint). Chốt
  lại với đội trước khi cam kết lịch — xem §2 của `ke-hoach-scrum-nhom-a.md`.
