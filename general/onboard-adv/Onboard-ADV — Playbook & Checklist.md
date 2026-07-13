# Onboard đối tác (ADV) lên Landing page — Playbook & Checklist

> **Tài liệu gồm 2 phần, dùng song song:**
> - **PHẦN I — PLAYBOOK**: *lên task* — mỗi dòng là một task kỹ thuật, có người làm và động từ hành động.
> - **PHẦN II — CHECKLIST**: *kiểm tra* — danh sách tick ✓ để xác nhận đã làm đủ và đúng trước khi go-live.
>
> Định hướng: **thiên kỹ thuật**. Mỗi bước = 1 task hành động, không mô tả điều kiện "nếu... thì...".
>
> **Phạm vi:** chỉ áp dụng cho **onboard ADV MỚI**. ADV hiện hữu (mở chiến dịch mới trên ADV đã có) là luồng khác, không dùng playbook này.
>
> **Đầu mối chính:** Biz AT — sở hữu luồng onboard từ đầu đến khi go-live.

---

# PHẦN I — PLAYBOOK (lên task)

## 1. Trigger — task khởi động

| # | Task | Vai trò |
| :-- | :--- | :--- |
| T0.1 | Tiếp nhận nhu cầu ADV mới và khởi tạo yêu cầu onboard | Biz AT |
| T0.2 | Gửi file mẫu **"Yêu cầu hệ thống"** cho đối tác điền | Biz AT |
| T0.3 | Nhận lại file mẫu đã điền đủ field bắt buộc | Biz AT |

## 2. Đầu vào cần thu thập (task tiền đề)

> Toàn bộ đầu vào kỹ thuật gom trong 1 file mẫu duy nhất: **`Yêu cầu hệ thống`** (VD: `[AT - PV] Parasola Ambassador — 2. Yêu cầu hệ thống.csv`). Playbook không lặp lại từng field — chỉ thu thập theo mẫu.

| # | Task thu thập | Vai trò |
| :-- | :--- | :--- |
| T1.1 | Gửi file mẫu "Yêu cầu hệ thống" cho đối tác, hướng dẫn điền theo cột `required` | Biz AT |
| T1.2 | Nhận file đã điền, kiểm tra đủ các field bắt buộc (`APP_NAME`, `PARTNER_ID`, `DOMAIN`, `PRIMARY_COLOR`, `LOGO_FILE`, `FAVICON_FILE`, `OG_TITLE`, `OG_DESCRIPTION`, `FONT`, `BANNER`, `BRAND_GUIDE`) | Biz AT |
| T1.3 | Xác nhận đối tác đã trỏ `DOMAIN` về IP `54.169.3.115` (nếu domain trên Cloudflare thì cấu hình trên Cloudflare) | Biz AT/DevOps |
| T1.4 | Thu file thiết kế đi kèm (logo, favicon, banner theo size, brand guide) | Biz AT |
| T1.5 | Chặn setup production khi thiếu field bắt buộc — trả file lại đối tác yêu cầu bổ sung | Biz AT |

## 3. Fork thiết kế từ template

| # | Task | Vai trò |
| :-- | :--- | :--- |
| T2.1 | Fork thiết kế ADV mới từ template chung | Designer |
| T2.2 | Chỉ thay đổi Logo · Cover · Màu chủ đạo · Font chữ; giữ nguyên bố trí/giao diện tổng thể | Designer |
| T2.3 | Liệt kê chi tiết toàn bộ thay đổi so với template để đối chiếu khi implement | Designer |

## 4. Quy trình onboard — task theo giai đoạn

### GIAI ĐOẠN A — SETUP ADMIN

| # | Task | Vai trò |
| :-- | :--- | :--- |
| A1 | Mở trang quản trị, tạo ADV mới | Admin |
| A2 | Upload Logo | Admin |
| A3 | Upload Cover bản Tiêu chuẩn + Stretch (bấm + Thêm nếu nhiều cover) | Admin |
| A4 | Nhập Tên hiển thị (có dấu, viết hoa bình thường) | Admin |
| A5 | Nhập Slug chuẩn: chữ thường, không dấu, không khoảng trắng, nối từ bằng gạch ngang (VD: parasola) | Admin |
| A6 | Kiểm tra Slug không trùng với ADV khác | Admin |
| A7 | Giữ nguyên Slug đã công bố — không đổi | Admin |
| A8 | Báo Biz AT phát lại link cho đối tác khi buộc phải đổi Slug (link cũ sẽ 404) | Admin |
| A9 | Nhập domain trỏ về vào **Allow domains**, mỗi domain Enter thành 1 thẻ | Admin |
| A10 | Loại bỏ https:// / http://, dấu / cuối, và @-prefix khỏi Allow domains | Admin |
| A11 | Nhập domain thật của đối tác vào Allow domains | Admin |
| A12 | Cấu hình domain demo/localhost tạm + ghi note "chờ domain thật" khi chưa có domain thật | Admin |
| A13 | Cập nhật lại Allow domains bằng domain thật ngay khi đối tác giao | Admin |
| A14 | Xóa hết domain localhost/test trong Allow domains trước khi lên production | Admin |
| A15 | Nhập Website đối tác (ô này CÓ https://, khác Allow domains) | Admin |
| A16 | Dán nội dung Mô tả chương trình | Admin |
| A17 | Nhập Ngân sách / ADV (VND) | Admin |
| A18 | Bật/tắt toggle Hiển thị BXH theo chương trình (mặc định Bật) | Admin |
| A19 | Bật/tắt toggle Hiển thị số tiền trong BXH theo yêu cầu bảo mật đối tác | Admin |
| A20 | Bật/tắt toggle Cho phép gửi lại nội dung bị từ chối (mặc định Tắt) | Admin |
| A21 | Bấm Cập nhật để lưu cấu hình ADV | Admin |
| A22 | Bàn giao cấu hình sang Dev/QA sau khi lưu thành công | Admin |

### GIAI ĐOẠN B — DEPLOY & KIỂM THỬ (Dev / QA)

| # | Task | Vai trò |
| :-- | :--- | :--- |
| B1 | Tạo PR và review code | Dev |
| B2 | Deploy cấu hình ADV + thiết kế fork lên Dev/Staging | Dev |
| B3 | Seed data tenant mới: rate-card, quota, budget | Dev |
| B4 | Dry-run migration trên Dev, xác nhận thành công | Dev |
| B5 | Truy cập landing qua domain trong Allow domains, đối chiếu đúng thiết kế | QA |
| B6 | Chạy toàn bộ test case chuẩn trên Dev (chưa login, đăng nhập, trang chủ, chi tiết chương trình, đăng bài, thông báo) | QA |
| B7 | Verify branding đúng ADV: Logo/Cover/Màu/Font, không lẫn ADV khác | QA |
| B8 | Verify phân tách tenant: không rò rỉ creator/nội dung/BXH sang ADV khác | QA |
| B9 | Kiểm tra responsive/mobile, layout không vỡ | QA |
| B10 | Trả cấu hình về Admin (Giai đoạn A) kèm mô tả lỗi khi phát hiện bug | QA |

### GIAI ĐOẠN C — RELEASE LÊN PRODUCTION (Dev/DevOps)

| # | Task | Vai trò |
| :-- | :--- | :--- |
| C1 | Soạn Release note (tính năng mới, thay đổi, bug đã fix, hướng dẫn) | Dev/QA |
| C2 | Thông báo lịch release & downtime cho các bên liên quan | PM |
| C3 | Phân vai war-room và chỉ định Release Manager (quyền go/no-go) | PM |
| C4 | Code Freeze — chốt tag/phiên bản, ngừng merge vào nhánh release | Lead |
| C5 | Xác định ngưỡng rollback (lỗi gì thì revert code/data) | Lead |
| C6 | Viết quy trình rollback thực thi: revert về tag nào, có rollback data không, ai bấm, báo ai | Lead/DevOps |
| C7 | Backup DB Production trước khi chạy migration | DevOps |
| C8 | Deploy đúng tag đã duyệt lên Production | DevOps |
| C9 | Chạy migration Production, kiểm tra thành công | DevOps |
| C10 | Cấu hình Allow domains & config ADV trên Prod đúng như verify ở Dev | Admin |
| C11 | Xóa sạch domain test còn sót trên Prod | Admin |

### GIAI ĐOẠN D — SAU RELEASE / GO-LIVE (QA / PM / DevOps)

| # | Task | Vai trò |
| :-- | :--- | :--- |
| D1 | Smoke test trang chủ Prod: load được, đúng thiết kế (banner, creator, thử thách) | QA |
| D2 | Mở landing đối tác trên domain thật, xác nhận Allow domains hoạt động | QA |
| D3 | Đăng nhập Google / TikTok thành công trên Production | QA |
| D4 | Chạy 1 luồng nghiệp vụ quan trọng end-to-end (đăng bài / xem BXH) | QA |
| D5 | Kiểm tra không có lỗi 404 / 500 / trang trắng ở các route chính | QA |
| D6 | Verify branding & phân tách tenant trên Production | QA |
| D7 | Theo dõi log/lỗi/hiệu năng ít nhất 30–60 phút đầu | Dev/DevOps |
| D8 | Xác nhận release thành công khi không phát sinh lỗi nghiêm trọng | PM |
| D9 | Thông báo go-live cho các bên liên quan (Biz AT, đối tác, support) | PM/Biz AT |
| D10 | Cập nhật trạng thái release | PM |
| D11 | Ghi lại vấn đề phát sinh + gắn owner & hạn khắc phục (retro) | PM |

## 5. Xử lý sự cố (Troubleshooting) — task khi gặp lỗi

| Triệu chứng | Task xử lý | Vai trò |
| :--- | :--- | :--- |
| Landing bị chặn / trắng trang / báo không được phép trên domain đối tác | Mở lại Allow domains, nhập đúng domain (không https://, không / cuối, không @-prefix); kiểm tra từng ký tự | Admin |
| Vào link đối tác ra landing đối tác khác / 404 | Kiểm tra Slug duy nhất; khôi phục Slug cũ hoặc phát lại link mới cho đối tác | Admin |
| Link "Về [đối tác]" không mở được | Nhập lại Website đầy đủ dạng https://... | Admin |
| BXH không hiển thị / lộ số tiền ngoài ý muốn | Chỉnh lại 2 toggle "Hiển thị BXH" và "Hiển thị số tiền trong BXH" | Admin |
| User không nộp lại được bài bị từ chối (hoặc ngược lại) | Bật/tắt lại toggle "Cho phép gửi lại nội dung bị từ chối" theo thỏa thuận | Admin |
| Font tiếng Việt / tên hiển thị lỗi | Nhập lại Mô tả, kiểm tra hiển thị | Admin |
| Lỗi nghiêm trọng sau go-live | Kích hoạt quy trình rollback (C5–C6); khôi phục từ backup Prod (C7) | Lead/DevOps |

## 6. Định nghĩa Hoàn thành (Definition of Done)

Onboard HOÀN TẤT khi tất cả đạt:

- ☑ ADV đã tạo/cập nhật và lưu thành công.
- ☑ Slug đúng chuẩn, duy nhất, đã chốt (không đổi về sau).
- ☑ Allow domains chứa đúng domain thật, không https://, không / cuối, không @-prefix; đã dọn domain test.
- ☑ Logo, Cover, Tên, Mô tả, Ngân sách, Website đầy đủ & đúng; branding fork đúng template.
- ☑ Các toggle BXH & nội dung đúng thỏa thuận.
- ☑ QA test Pass trên domain thật (đối chiếu bộ test case) + verify tenant isolation.
- ☑ Đã backup + deploy + migration Prod thành công; giám sát 30–60 phút không lỗi nghiêm trọng.
- ☑ Đã thông báo go-live cho các bên liên quan; đã ghi retro.

---

## 7. Phụ lục tham chiếu — Slug & Allow domains

### 7.1 Slug là gì?

Slug là phần **đường dẫn (URL) định danh** cho đối tác — mã đường dẫn duy nhất để hệ thống nhận ra landing của đối tác nào. VD: slug = `parasola` → hệ thống load đúng cấu hình, logo, cover, chương trình của đối tác đó.

| ✅ ĐÚNG | ❌ SAI |
| :--- | :--- |
| Chữ thường không dấu: `parasola` · Số: `parasola2026` · Gạch ngang: `parasola-summer` | Có dấu: `pàrasola` · Khoảng trắng: `para sola` · Viết hoa: `Parasola` · Ký tự đặc biệt: `para_sola`, `parasola@!` |

- Slug phải DUY NHẤT — trùng sẽ xung đột, load sai landing.
- KHÔNG đổi Slug sau khi công bố — slug nằm trong URL, đổi là làm hỏng toàn bộ link cũ (404).

### 7.2 Allow domains là gì?

Là **danh sách domain được phép truy cập / được hệ thống tin tưởng** để phục vụ landing — chính là (các) domain trỏ về đối tác dùng cho người dùng vào xem. Domain truy cập không nằm trong danh sách → hệ thống chặn.

**Chỉ nhập phần TÊN MIỀN. KHÔNG https:// / http://, không dấu / cuối, không @-prefix.**

| ✅ ĐÚNG | ❌ SAI |
| :--- | :--- |
| `parasola.demo.accesstrade.click` | `https://parasola.demo.accesstrade.click` · `http://ambassador.diso.vn` · `parasola.demo.accesstrade.click/` |

**Phân biệt rõ:** Allow domains = domain trỏ về → KHÔNG https://. Website = link ra ngoài → CÓ https:// đầy đủ.

---
---

# PHẦN II — CHECKLIST (kiểm tra)

*Danh sách tick ✓ xác nhận đã làm đủ & đúng trước khi go-live. Cột "Task PB" trỏ về task tương ứng trong Playbook.*

## Giai đoạn 1 — Trước release (Chuẩn bị + Build + QA trên Dev)

| ✓ | Nhóm | Hạng mục kiểm tra | Task PB | Phụ trách | Deadline |
| :-- | :--- | :--- | :--- | :--- | :--- |
| ☐ | Chuẩn bị | File "Yêu cầu hệ thống" đã nhận lại, đủ field bắt buộc (đối chiếu cột `required`) | T1.1–T1.2 | Admin | D-7 |
| ☐ | | DOMAIN đã trỏ về IP 54.169.3.115 (hoặc cấu hình Cloudflare) | T1.3 | Biz AT/DevOps | D-7 |
| ☐ | | Thiết kế fork từ template, chỉ đổi Logo/Cover/Màu/Font, có list thay đổi chi tiết | T2.1–T2.3 | Designer | D-7 |
| ☐ | | Slug duy nhất, không trùng, không đổi so với bản công bố | A5–A7 | Admin | D-7 |
| ☐ | Dữ liệu (Dev) | Allow domains đúng (không https://, không / cuối, không @-prefix) — verify Dev trước | A9–A11 | Admin | D-5 |
| ☐ | | Cấu hình ADV (Logo, Cover, Mô tả, Ngân sách, toggle BXH/nội dung) đúng thỏa thuận | A2–A20 | Admin | D-5 |
| ☐ | | Seed + dry-run migration data tenant mới thành công trên Dev | B3–B4 | Dev | D-5 |
| ☐ | Code & Build | Đã tạo PR, review code | B1 | Dev | D-5 |
| ☐ | | Đã deploy lên Dev/Staging | B2 | Dev | D-5 |
| ☐ | Kiểm thử (QA) | Chạy toàn bộ test case trên Dev → tất cả Pass | B6 | QA | D-3 |
| ☐ | | Test luồng chính: đăng nhập, trang chủ, chi tiết chương trình, đăng bài, liên kết tài khoản | B6 | QA | D-3 |
| ☐ | | Verify branding đúng ADV, không lẫn ADV khác | B7 | QA | D-3 |
| ☐ | | Verify phân tách tenant: không rò rỉ creator/nội dung/BXH | B8 | QA | D-3 |
| ☐ | | Kiểm tra responsive / mobile — layout không vỡ | B9 | QA | D-3 |
| ☐ | Kế hoạch Release | Release note (tính năng mới, thay đổi, bug đã fix, hướng dẫn) | C1 | Dev/QA | D-1 |
| ☐ | | Thông báo lịch release & downtime cho các bên liên quan | C2 | PM | D-1 |
| ☐ | | Phân vai war-room, chỉ định Release Manager (quyền go/no-go) | C3 | PM | D-1 |
| ☐ | | Code Freeze — chốt tag/phiên bản, ngừng merge | C4 | Lead | D-1 |
| ☐ | Kế hoạch Rollback | Xác định ngưỡng quyết định rollback | C5 | Lead | D-1 |
| ☐ | | Quy trình rollback thực thi: revert tag nào, có rollback data không, ai bấm, báo ai | C6 | Lead/DevOps | D-1 |

## Giai đoạn 2 — Triển khai (D-Day)

| ✓ | Nhóm | Hạng mục kiểm tra | Task PB | Phụ trách | Deadline |
| :-- | :--- | :--- | :--- | :--- | :--- |
| ☐ | Thực thi release | Backup DB Production TRƯỚC khi chạy migration | C7 | DevOps | D-Day |
| ☐ | | Deploy đúng tag đã duyệt lên Production | C8 | DevOps | D-Day |
| ☐ | | Chạy migration Production, kiểm tra thành công | C9 | DevOps | D-Day |
| ☐ | | Cấu hình Allow domains & config ADV trên Prod đúng như verify Dev, dọn domain test | C10–C11 | Admin | D-Day |

## Giai đoạn 3 — Sau release (Smoke test + Đóng release)

| ✓ | Nhóm | Hạng mục kiểm tra | Task PB | Phụ trách | Deadline |
| :-- | :--- | :--- | :--- | :--- | :--- |
| ☐ | Smoke test | Trang chủ load được, đúng thiết kế (banner, creator, thử thách) | D1 | QA | D-Day |
| ☐ | | Landing đối tác mở được trên domain thật (Allow domains hoạt động) | D2 | QA | D-Day |
| ☐ | | Đăng nhập Google / TikTok thành công trên Production | D3 | QA | D-Day |
| ☐ | | Chạy 1 luồng nghiệp vụ quan trọng end-to-end (đăng bài / xem BXH) | D4 | QA | D-Day |
| ☐ | | Không có lỗi 404 / 500 / trang trắng ở các route chính | D5 | QA | D-Day |
| ☐ | | Verify branding & phân tách tenant trên Production | D6 | QA | D-Day |
| ☐ | Giám sát & Đóng release | Theo dõi log / lỗi / hiệu năng ít nhất 30–60 phút đầu | D7 | Dev/DevOps | D-Day |
| ☐ | | Không phát sinh lỗi nghiêm trọng → xác nhận release thành công | D8 | PM | D-Day |
| ☐ | | Thông báo go-live cho các bên liên quan (Biz AT, đối tác, support) | D9 | PM/Biz AT | D-Day |
| ☐ | | Cập nhật trạng thái release | D10 | PM | D-Day |
| ☐ | | Ghi lại vấn đề phát sinh + gắn owner & hạn khắc phục (retro) | D11 | PM | D+1 |
