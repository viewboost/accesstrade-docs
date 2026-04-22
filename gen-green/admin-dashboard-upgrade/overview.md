# Admin Dashboard Upgrade — Yêu cầu từ Meeting 0410

> **Project:** Gen-Green Admin Dashboard Upgrade
> **Ngày:** 2026-04-12
> **Nguồn:** [Meeting note 0410](../meeting-notes/0410.md)
> **Người yêu cầu chính:** Bình (vận hành), chị Hạnh (quản lý), Quân (tech)
> **PRD hiện tại:** [VCreator Dashboard PRD](../vcreator-dashboard/prd-vcreator-dashboard-2026-04-01.md)
> **Trạng thái:** Chờ xác nhận qua email + mockup từ AT

---

> ⚠️ **Scope change (2026-04-22):** Toàn bộ nhóm yêu cầu **filter theo Cơ sở làm việc / Phân loại CBNV + cột CBNV/Cơ sở/Hashtag + Column Picker Export + CRUD cấu hình Thương hiệu/Công ty/Cơ sở** đã được **gộp vào PRD V1 của Registration & Grouping** vì chúng phụ thuộc trực tiếp vào cấu trúc 3 layer (Thương hiệu → Công ty → Cơ sở).
>
> Xem: [registration-grouping-v2/prd-registration-v1-2026-04-12.md](../registration-grouping-v2/prd-registration-v1-2026-04-12.md) — EPIC-005, EPIC-006, EPIC-007.
>
> Document này giữ lại để tham chiếu nguyên văn meeting 0410 và các yêu cầu dashboard **không liên quan tới phân nhóm CBNV** (nếu phát sinh sau).

---

## 1. Bối cảnh

Sau khi triển khai phân loại CBNV (cán bộ nhân viên) trên Gen-Green, admin dashboard cần bổ sung khả năng **filter, hiển thị, và export** theo phân loại này. Hiện tại:

- Dashboard chỉ filter được số video/lượt xem theo sự kiện
- Không phân biệt được CBNV và creator bên ngoài
- Export ra tất cả cột, nhiều cột thừa, file nặng
- Vận hành phải mapping thủ công giữa tab Nội dung và tab Creator trên Excel

**Mục tiêu:** Sau upgrade, Bình (vận hành) có thể trả lời câu hỏi kiểu "bao nhiêu CBNV của VinWonders Phú Quốc tham gia chương trình X?" **ngay trên giao diện**, không cần export rồi filter Excel.

---

## 2. Yêu cầu theo từng khu vực

### A. Tab Nội dung (Video)

#### A1. Giao diện — Thêm filter & cột

| # | Yêu cầu | Loại | Mô tả |
|---|---------|------|-------|
| A1.1 | Filter **Cơ sở làm việc** | Filter mới | Dropdown trên màn hình, lọc video theo cơ sở làm việc của creator (VinWonders Phú Quốc, Vinpearl Nha Trang...) |
| A1.2 | Cột **Phân loại creator** | Cột mới | Hiển thị "CBNV" hoặc "Bên ngoài" cho mỗi video |
| A1.3 | Cột **Cơ sở làm việc** | Cột mới | Hiện tên cơ sở ngay tại video (ví dụ: "VinWonders Phú Quốc") |
| A1.4 | Cột **Hashtag cá nhân** | Cột mới | Hiện hashtag cá nhân của creator tại mỗi video, để khỏi mapping từ tab Creator |

> **Trích Bình:** "em muốn là ở trên cái màn hình thì nó sẽ thể hiện được hai trường: filter cơ sở làm việc + phân loại creator"

#### A2. Export — Bỏ cột thừa

| # | Cột cần bỏ | Lý do (Bình) |
|---|-----------|------|
| A2.1 | **ID video** | "thừa, chưa cần thiết" |
| A2.2 | **Thumbnail** | "thừa" |
| A2.3 | **Đối tác / Mã sự kiện** | "thừa" |
| A2.4 | **Tích cực / Trung lập / Tiêu cực** (3 cột sentiment) | "data khá là thừa, làm nặng file khi cần xuất nhiều data" |

#### A3. Export — Thêm cột mới

| # | Cột cần thêm |
|---|-------------|
| A3.1 | **Cơ sở làm việc** |
| A3.2 | **Hashtag cá nhân** |
| A3.3 | **Phân loại creator** (CBNV / Bên ngoài) |

---

### B. Tab Creator

#### B1. Giao diện — Filter

| # | Yêu cầu | Mô tả |
|---|---------|-------|
| B1.1 | Filter **Nơi làm việc** | Dropdown grouped, lọc tất cả CBNV thuộc 1 cơ sở (ví dụ: chọn "VinWonders Phú Quốc" → hiện hết CBNV trực VinWonders PQ) |
| B1.2 | Filter **Tệp bên ngoài** | Option để lọc creator không phải CBNV |

> **Trích Bình:** "em sẽ có thể bấm xuống xem filter, ví dụ như là VinWonders Phú Quốc thì nó sẽ nhảy ra hết tất cả cán bộ nhân viên mà trực VinWonders Phú Quốc"

#### B2. Bảng hiển thị — Cột mong muốn

| # | Cột | Ghi chú |
|---|-----|---------|
| B2.1 | Tên creator | |
| B2.2 | Hashtag cá nhân | Mới |
| B2.3 | Tổng view | |
| B2.4 | Tổng tiền | |
| B2.5 | Tổng tiền đã rút | |
| B2.6 | Tổng số video đã nộp | |
| B2.7 | Ngày tham gia | **Giữ** |
| B2.8 | ~~Ngày tạo~~ | **Bỏ** — "chưa cần thiết" |

> **Trích Bình:** "em sẽ muốn xem được tên, hashtag cá nhân, tổng view, tổng tiền, tổng tiền đã rút, tổng view và tổng số video... Còn ngày tạo thì mình có thể ẩn đi"

#### B3. Export

| # | Yêu cầu |
|---|---------|
| B3.1 | Bỏ cột **Đối tác VinWonders** (thừa, nặng file) |
| B3.2 | Thêm cột tương ứng giao diện: nơi làm việc, hashtag cá nhân, phân loại |

---

### C. Màn hình Thống kê (Analytics)

| # | Yêu cầu | Mô tả |
|---|---------|-------|
| C1 | Thêm **filter CBNV** | Hiện tại chỉ filter theo sự kiện. Cần thêm filter cán bộ nhân viên để xem nhanh "bao nhiêu CBNV của cơ sở X tham gia?" |
| C2 | **Compile với dashboard mới** | Dashboard mới (đã demo) cần update lại để include trường CBNV + cơ sở làm việc |
| C3 | Nhiều bộ lọc hơn | Anh Tĩnh: "sửa nhiều nhất... đưa cái màn hình thống kê ra một cái màn hình tiện dụng hơn, nhiều bộ lọc" |

> **Trích Bình:** "hiện tại nó chỉ đang filter được số video và lượt xem theo từng sự kiện thôi. Chưa có filter về cán bộ nhân viên"

> **Trích chị Hạnh:** "em muốn biết bao nhiêu CBNV của Phú Quốc tham gia vào chương trình ABC chẳng hạn. Em chỉ muốn chọn đây và em nhìn số ngay ở đây. Thay vì kéo data bằng Excel xong rồi filter trên Excel"

---

### D. Export chung — Cơ chế chọn cột

| # | Yêu cầu | Mô tả |
|---|---------|-------|
| D1 | **Chọn cột khi xuất** | Khi bấm "Xuất dữ liệu", hiện dialog checkbox list cho user tích chọn cột muốn xuất. Giải quyết triệt để: không cần dev mỗi lần team vận hành muốn bỏ/thêm cột |

> **Trích Quân:** "mặc định nó sẽ đổ ra tất cả các cột. Nếu cảm thấy cột nào dư thừa thì bổ sung chức năng lựa chọn cái cột mà muốn đổ ra trong lúc xuất báo cáo"

> **Bình đồng ý:** "nếu mà được phép chọn những cái trường mà mình có thể xuất ra như thế thì ok"

#### UX chi tiết

```
Bấm "Xuất dữ liệu"
  → Dialog hiện danh sách cột (checkbox, default theo preset)
  → User bỏ tick cột không cần / tick thêm cột cần
  → Bấm "Xuất" → file chỉ chứa cột đã chọn
```

#### Default preset (bỏ tick sẵn cột thừa)

Mặc định bỏ tick các cột mà Bình xác nhận thừa, để user mở ra thấy preset "sạch" ngay. Muốn thêm lại thì tự tick.

**Tab Nội dung — bỏ tick sẵn:**
- ID video
- Thumbnail
- Đối tác / Mã sự kiện
- Tích cực / Trung lập / Tiêu cực (3 cột sentiment)

**Tab Creator — bỏ tick sẵn:**
- Đối tác VinWonders
- Ngày tạo

#### Lý do chọn approach này

- **Không ảnh hưởng team khác:** team vận hành bên kia cũng dùng export, bỏ cột cứng sẽ ảnh hưởng họ. Chọn cột = mỗi người tự quyết
- **Effort thấp:** UI chỉ 1 dialog checkbox. Backend đã trả đủ data, chỉ filter columns trước khi generate file (hoặc gửi `columns[]` param)
- **Không cần phức tạp V1:** Không cần saved presets, drag-drop sắp xếp cột. Chỉ checkbox list + default preset là đủ. Mở rộng sau nếu cần

---

## 3. Tổng hợp theo action type

### Cột mới cần backend hỗ trợ
| Cột | Nơi hiển thị | Nguồn data |
|-----|-------------|------------|
| Phân loại creator (CBNV/Bên ngoài) | Tab Nội dung + Tab Creator + Export | `user.account_type` |
| Cơ sở làm việc | Tab Nội dung + Tab Creator + Export | `user.workplace_name` |
| Hashtag cá nhân | Tab Nội dung + Tab Creator + Export | `user.personal_hashtag` (đã có ở tab Creator, cần join vào tab Nội dung) |

### Filter mới
| Filter | Nơi | UI |
|--------|-----|-----|
| Cơ sở làm việc | Tab Nội dung, Tab Creator, Analytics | Grouped dropdown (6 nhóm, ~57 cơ sở) |
| Phân loại CBNV/Bên ngoài | Tab Creator, Analytics | Toggle hoặc dropdown |

### Cột cần bỏ khỏi default export
| Cột | Tab |
|-----|-----|
| ID video | Nội dung |
| Thumbnail | Nội dung |
| Đối tác / Mã sự kiện | Nội dung |
| Tích cực / Trung lập / Tiêu cực | Nội dung |
| Đối tác VinWonders | Creator |
| Ngày tạo | Creator |

---

## 4. Phụ thuộc

| Phụ thuộc | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| Chức năng phân loại CBNV (form đăng ký) | Đang thiết kế | Phải có `account_type` + `workplace_name` trong user model trước |
| VCreator Dashboard mới (Next.js 16) | Đã có PRD | Clone từ TCB Dashboard, cần compile thêm yêu cầu CBNV |
| Backend API: join workplace vào tab Nội dung | Chưa có | Cần endpoint hoặc field mới trong response video/content |

---

## 5. Action items từ meeting

| # | Việc | Ai | Deadline |
|---|------|-----|---------|
| 1 | Bình gửi lại file requirement (đã show trong meeting) qua email | Bình | Ngay sau meeting |
| 2 | AT tổng hợp + làm mockup: (a) form nhập thông tin NV, (b) luồng liên kết tài khoản, (c) dashboard admin, (d) dashboard creator | AT (Vĩnh) | Đầu tuần sau |
| 3 | Chị Vui xác nhận các task qua email để start | Chị Vui | Đang chờ |
| 4 | Timeline triển khai chi tiết cho từng hạng mục | Cả 2 team | Sau khi confirm |

> **Trích Bình:** "chị có email mấy lần rồi nhưng mà team không có xác nhận gì thì bọn chị cũng chưa có thể start được"

---

## 6. Ghi chú thêm từ meeting

- **Dashboard mới đã demo** — Quân nói "sử dụng được khoảng 80% use case rồi", cần compile thêm yêu cầu CBNV
- **Không đưa hết report affiliate vào Gen-Green** — Quân: "chỉ cần 3-4 thứ cơ bản: tạo link, doanh thu, số đơn. Xem detail thì sang Scalef"
- **Target: đầu tháng 5** ra mắt — Bình hỏi timeline, team cần gấp
- **Mục tiêu năm:** 1K user generate doanh thu, 50 tỷ doanh thu affiliate, core là đội CBNV
