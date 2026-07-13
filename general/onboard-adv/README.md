# Onboard ADV mới lên Landing page

Bộ tài liệu quy trình **onboard một ADV (advertiser/đối tác) MỚI** lên landing page Ambassador — từ lúc tiếp nhận nhu cầu đến khi go-live.

> **Phạm vi:** chỉ áp dụng cho **ADV mới**. ADV hiện hữu (mở chiến dịch mới trên ADV đã có) là luồng khác, không dùng bộ này.
> **Đầu mối chính:** Biz AT (phụ trách kinh doanh bên AT) — sở hữu luồng onboard từ đầu đến go-live.

## Cách dùng

- **[Onboard-ADV — Playbook & Checklist.md](Onboard-ADV%20—%20Playbook%20&%20Checklist.md)** — bản mô tả đầy đủ (đọc để hiểu toàn cảnh).
- **7 file CSV** — import vào 1 file Excel, mỗi CSV thành 1 sheet (Data → From Text/CSV). Một số bước (Pre-release, Release) không có file riêng — chỉ ghi trong Overview.
- **Sheet `05_Testcases`** (user tự import): mẫu test case dùng cho **cả 2 bước** nghiệm thu Dev (bước 5) và post-release (bước 10).
- **Bullet trong cell**: nhiều ô có bullet xuống dòng. Sau khi import, bật **Wrap Text** (Excel: Home → Wrap Text; Sheets: Format → Wrapping → Wrap) cho các cột Hạng mục/Mô tả/Ghi chú để hiển thị đẹp.
- **Đặt đúng tên sheet**: sheet thiết kế phải tên chính xác `02_Design` — vì các file Tech-Req dùng công thức `='02_Design'!Cx` để lấy giá trị. Sai tên → lỗi `#REF!`.

## 3 loại tài liệu trong bộ này

| Loại | File | Bản chất |
| :--- | :--- | :--- |
| **Form input** | 01_ADV-Input, 02_Design, 04_Tech-Req-Dev, 07_Tech-Req-Prod | Bảng nhập liệu — điền thông tin, không có Trạng thái |
| **Checklist task** | 03_Config-Dev, 06_Config-Prod | Danh sách task, có cột Trạng thái dropdown |
| **Bảng tra** | 10_Troubleshooting | Tra triệu chứng → cách xử lý |

## Luồng thông tin cốt lõi

**1. ADV cung cấp → Hiếu AT vẽ Figma → chẻ nhỏ thành các field**
`01_ADV-Input` (ADV điền, gồm Brand guide) → `02_Design` (Hiếu AT vẽ Figma: Logo, Favicon, Banner, Cover, Màu, Font — mỗi cái 1 frame export-ready).

**2. Config setup TRƯỚC → sinh ID → Tech-Req lấy ID làm value**
Đây là điểm mấu chốt về thứ tự: **phải setup xong mới có ID**, nên Config đứng trước Tech-Req.

| Bước Config | Setup xong trả về | → điền value vào |
| :--- | :--- | :--- |
| Setup ADV (tạo tenant) | `AMBASSADOR_PARTNER_ID` | Tech-Req |
| Setup Campaign | `EVENT_ID` | Tech-Req |
| Setup nội dung (bài CMS) | `SUPPORT/QA/TERM/CONDITION_ARTICLE_ID` | Tech-Req |

**3. Field design trong Tech-Req dùng công thức ref**
Các field Hiếu AT (`LOGO_FILE`, `FONT`, `PRIMARY_COLOR`...) trong Tech-Req không điền lại — cột Giá trị là công thức `='02_Design'!Cx` tự đổ từ sheet Design.

## Mốc thời gian (Deadline)

**D = ngày release (go-live lên Production).** Các mốc đếm ngược từ D:

| Mốc | Nghĩa |
| :--- | :--- |
| D-7 | Thu thập đầu vào ADV, fork thiết kế |
| D-5 | Cấu hình Develop (setup ADV/Campaign/nội dung) → tổng hợp tech requirement (Dev) |
| D-3 | DevOps Diso deploy Dev, QA kiểm thử & nghiệm thu |
| D-1 | Pre-release: soạn meeting note, gửi thông báo lịch release |
| D-Day | Cấu hình Prod → tech requirement (Prod) → merge PR, deploy, setup ENV → test theo mẫu |

## Cột Trạng thái (dropdown)

Các file **checklist task** (03, 06) có cột **Trạng thái** (gần cuối, trước Ghi chú), mặc định `Chưa làm`. Các file **form input** không có cột Trạng thái.

Format cột chuẩn của file task: `STT | Nhóm | Hạng mục | Phụ trách | Deadline | Trạng thái | Ghi chú`.

Sau khi import, tạo dropdown: chọn cột Trạng thái → Data → Data Validation (Excel) / Data validation (Sheets) → nhập các giá trị.

| Loại file | Giá trị dropdown |
| :--- | :--- |
| Task (03, 06) | `Chưa làm` · `Đang làm` · `Xong` · `Blocked` · `N/A` |

Riêng `06_Config-Prod` có thêm cột **"Khớp Dev?"** (checkbox `☐`) để đối chiếu 1-1 với cấu hình Dev.

## Danh sách file (theo thứ tự dùng)

| File | Nội dung | Ai làm | Khi nào |
| :--- | :--- | :--- | :--- |
| [00_Overview.csv](00_Overview.csv) | Tổng quan các đầu mục lớn, trỏ tới sheet chi tiết | — (đọc) | Xuyên suốt |
| [01_ADV-Input.csv](01_ADV-Input.csv) | **Form** — bảng thông tin gửi đối tác điền (thương hiệu, hình ảnh, domain, chiến dịch, brand guide) | ADV / Biz AT | D-7 |
| [02_Design.csv](02_Design.csv) | **Form** — Hiếu AT vẽ Figma & điền thay đổi design (Logo/Favicon/Banner/Cover/Màu/Font) | Hiếu AT | D-7 |
| [03_Config-Dev.csv](03_Config-Dev.csv) | **Task** — setup ADV/Campaign/nội dung trên **Develop** → sinh các ID | Campaign Operation | D-5 |
| [04_Tech-Req-Dev.csv](04_Tech-Req-Dev.csv) | **Form** — gom bộ biến ENV bản **Develop** (điền ID vừa sinh ở Config) | Biz AT + Campaign Operation | D-5 |
| *05_Testcases (user tự import)* | Deploy Dev & nghiệm thu — DevOps Diso set ENV + deploy Dev, QA nghiệm thu theo **sheet 05_Testcases** | DevOps Diso / QA | D-3 |
| [06_Config-Prod.csv](06_Config-Prod.csv) | **Task** — setup ADV/Campaign/nội dung trên **Production** (giống Dev + task chỉ-Prod) | Campaign Operation | D-Day |
| [07_Tech-Req-Prod.csv](07_Tech-Req-Prod.csv) | **Form** — gom bộ biến ENV bản **Production** (ID khác Dev) | Biz AT + Campaign Operation | D-Day |
| *(không có file — xem Overview)* | Pre-release: soạn meeting note, gửi thông báo lịch release | Huyền Diso | D-1 |
| *(không có file — xem Overview)* | Release: merge PR, deploy, setup ENV Production | DevOps AT | D-Day |
| *05_Testcases (user tự import)* | Post-release: test theo **sheet 05_Testcases** (cùng mẫu bước 5) | QA | D-Day |
| [10_Troubleshooting.csv](10_Troubleshooting.csv) | **Bảng tra** — triệu chứng → cách xử lý sự cố | Campaign Operation / DevOps | Khi gặp lỗi |

## Vai trò

- **Biz AT** — đầu mối chính, đối ngoại với ADV; nhập phần text của tech requirement (tên, domain, OG, slug).
- **Hiếu AT** — fork thiết kế từ template, vẽ Figma (Logo/Favicon/Banner/Cover/Màu/Font — mỗi cái 1 frame export-ready).
- **Campaign Operation** — thao tác setup trên admin (tạo ADV/campaign/bài CMS), điền các ID sinh ra vào Tech-Req.
- **DevOps Diso** — set ENV theo tech requirement + deploy trên **Develop**.
- **DevOps AT** — merge PR, set ENV, deploy trên **Production**.
- **Huyền Diso** — pre-release: soạn meeting note, gửi thông báo lịch release.
- **QA** — nghiệm thu Dev & test Prod theo mẫu test case.

## Lưu ý quan trọng

- **Config làm TRƯỚC Tech-Req**: phải setup xong (tạo tenant/campaign/bài CMS) mới có ID → mang ID đó điền vào Tech-Req của môi trường tương ứng.
- **Slug / PARTNER_ID**: chữ thường không dấu, duy nhất, KHÔNG đổi sau khi công bố (đổi = hỏng link cũ, 404). Prod dùng đúng slug của Dev.
- **PARTNER_ID ≠ AMBASSADOR_PARTNER_ID**: `PARTNER_ID` là slug chữ (Biz AT đặt); `AMBASSADOR_PARTNER_ID` là ObjectId hệ thống (sinh khi tạo tenant).
- **Allow domains**: chỉ nhập tên miền — KHÔNG `https://`, không `/` cuối, không `@`-prefix.
- **Config Prod phải khớp Dev**: dùng cột "Khớp Dev?" trong `06_Config-Prod` để đối chiếu 1-1.
- **Quy ước DevOps theo môi trường**: **Dev → DevOps Diso**, **Prod → DevOps AT**.
- **DOMAIN**: bản Dev mặc định `slug.demo.accesstrade.click`; bản Prod trỏ về IP `54.169.3.115` (hoặc cấu hình Cloudflare).
- **Các ID (`*_ARTICLE_ID`, `EVENT_ID`, `AMBASSADOR_PARTNER_ID`)**: bản Dev và Prod KHÁC nhau — điền riêng ở `04_Tech-Req-Dev` và `07_Tech-Req-Prod`.
