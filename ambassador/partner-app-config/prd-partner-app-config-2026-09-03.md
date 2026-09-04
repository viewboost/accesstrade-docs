# Product Requirements Document: Hợp nhất frontend đa đối tác trên nền cấu hình lúc chạy (`partner-app/`)

**Date:** 2026-09-03 (cập nhật 2026-09-04)
**Author:** Nguyễn Đăng Định
**Version:** 1.1
**Reviewer:** _chưa có_
**Project Level:** Level 4 — ứng dụng mới + mở rộng backend + mở rộng admin + di cư 15 hệ thống đang chạy
**Status:** Draft — phương án và phạm vi đã chốt, chờ review
**Mức độ:** **P2** — không có sự cố đang diễn ra, nhưng chi phí vận hành cộng dồn theo mỗi lần onboard và mỗi lần sửa lỗi
**Phạm vi:** ứng dụng mới `partner-app/` + mở rộng `backend/` + mở rộng `admin/` + **di cư toàn bộ 15 ứng dụng đối tác hiện hành theo 6 đợt**

---

## Document Overview

Hiện tại, mỗi lần onboard một đối tác, hệ thống sinh thêm một bản sao frontend độc lập. Repository đang chứa 15 bản sao như vậy. Tài liệu này đặc tả `partner-app/` — ứng dụng frontend hợp nhất, vận hành theo mô hình đa người thuê (multi-tenant) với cấu hình đọc lúc chạy — và lộ trình di cư 15 ứng dụng hiện hành về ứng dụng này.

Sau khi hoàn tất, việc onboard một đối tác là thao tác tạo một bản ghi cấu hình trong admin, không phát sinh mã nguồn và không phát sinh triển khai.

### Nguyên tắc

**Nhận diện thương hiệu là dữ liệu, không phải mã nguồn.** Toàn bộ khác biệt giữa 15 bản hiện hành — bảng màu, logo, hình ảnh, nội dung văn bản, thẻ SEO, mã GTM, trạng thái bật/tắt các phân hệ, bố cục trang chủ — phải được biểu diễn bằng một bản ghi cấu hình đọc lúc chạy, không nằm trong tệp `.scss` hay `.tsx`.

**Backend đã hỗ trợ đa người thuê; không viết lại.** `PartnerRaw.AllowDomains` và `GetDetailByDomain` đã tồn tại và đang phục vụ production. Tài liệu này bổ sung một collection cấu hình và ba nhóm endpoint, không thay đổi mô hình dữ liệu đối tác hiện có.

**`creator-os` là tài liệu tham khảo thiết kế, không phải nguồn mã.** Repository `pmax/creator-os` đã hiện thực hoá cùng bài toán và đang vận hành. Tài liệu này kế thừa **mô hình thiết kế và các bài học vận hành** (mục 2.3), không nhập mã nguồn và không tạo phụ thuộc chéo repository. Hai hệ thống khác nền tảng (Go/MongoDB ↔ NestJS/Prisma/PostgreSQL); phụ thuộc chéo sẽ tái tạo chính vấn đề đang xử lý.

**Một triển khai duy nhất, phân giải người thuê theo `Host`.** Một image phục vụ toàn bộ tên miền đối tác. Thay đổi cấu hình có hiệu lực ngay, không cần build, không cần triển khai lại. Điều kiện hạ tầng đã sẵn sàng: 15 tên miền hiện hành đều kết thúc trên hạ tầng nội bộ (`SSH_HOST_{env}` — một máy chủ cho mỗi môi trường; `Dockerfile.release` và cấu hình `nginx/` đồng nhất giữa các thư mục).

**Di cư toàn bộ 15 ứng dụng hiện hành, theo 6 đợt — chốt 04/09.** Đây là điều kiện để đạt mục tiêu chính: chấm dứt việc nhân bản mỗi bản sửa lỗi ra 15 nơi. Phương án chỉ phục vụ đối tác mới đã được cân nhắc và loại bỏ, vì nó không giải quyết vấn đề gốc mà còn bổ sung một hệ thống phải duy trì song song vô thời hạn.

**Đánh số yêu cầu bằng tiền tố `PC-`** (Partner Configuration), tách biệt với `FR-0xx` và `FE-0xx` của các tài liệu khác trong repository.

**Related Documents:**
- Báo cáo khảo sát và số liệu đo đạc: `ambassador/plans/reports/research-260903-1718-partner-config-admin-tham-khao-creator-os.md` (repository mã nguồn)
- Thiết kế tham khảo: `pmax/creator-os` — `docs/architecture/05-theme-and-portals.md`, `14-editions-and-deployment.md`
- Tài liệu liên quan (cờ tính năng theo đối tác đã triển khai): [../employee-code/prd-employee-code-2026-08-06.md](../employee-code/prd-employee-code-2026-08-06.md)

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Ứng dụng white-label** | `hdbank/`, `parasola/`, `yody/`… — mỗi thư mục là một frontend độc lập phục vụ một đối tác. Hiện có 15 |
| **`partner-app/`** | Ứng dụng hợp nhất được đặc tả tại tài liệu này. Một codebase, một triển khai, phục vụ toàn bộ đối tác |
| **Cấu hình ứng dụng** (`PartnerAppConfig`) | Bản ghi chứa toàn bộ khác biệt giữa các đối tác: giao diện, tài nguyên, SEO, phân hệ, bố cục trang chủ |
| **Design token** | Một giá trị cấu hình giao diện (màu, bán kính bo góc, đổ bóng, phông chữ, kiểu chữ nhãn), được ánh xạ thành CSS custom property khi kết xuất phía máy chủ |
| **Preset** | Bộ design token đặt tên sẵn, đóng vai trò lớp nền; đối tác ghi đè từng giá trị bên trên |
| **Section** | Một khối nội dung trên trang chủ. Trang chủ là mảng có thứ tự các section |
| **Section catalogue** | Danh mục các loại section hợp lệ. Định nghĩa nằm trong mã nguồn, không nằm trong cơ sở dữ liệu (mục 2.3) |
| **Slot** | Một màn hình mà đối tác có thể thay thế bằng bản triển khai riêng thông qua registry. Mức tuỳ biến L4 |
| **Đợt di cư** | Một nhóm đối tác được chuyển sang `partner-app/` cùng lúc. Tổng cộng 6 đợt (mục 6) |
| **Chạy song song** | Giai đoạn một đối tác đã chuyển sang `partner-app/` nhưng ứng dụng cũ vẫn được giữ ở trạng thái sẵn sàng khôi phục |
| **Cutover** | Thời điểm chuyển lưu lượng của một tên miền từ ứng dụng cũ sang `partner-app/` |
| **Hoà giải biến thể** | Quá trình rút gọn N phiên bản của cùng một tệp về một phiên bản duy nhất (mục 4, PC-012) |
| **Bán kính ảnh hưởng** | Số đối tác bị tác động bởi một sự cố đơn lẻ. Tăng từ 1 lên 15 sau khi hợp nhất (mục 5, NFR-008) |

---

## 1. Executive Summary

Mô hình một-đối-tác-một-codebase tạo ra hai loại chi phí đo được:

```
Sửa một lỗi ở tầng dùng chung
  → phải áp dụng lại tại 14 vị trí khác (11 commit/6 tháng chạm 12–14 thư mục)
  → hoặc bỏ sót, dẫn tới phân kỳ hành vi (158 commit/6 tháng chạm đúng 1 thư mục)

Onboard một đối tác
  → sao chép ~25.000 LOC, thay bảng màu và tài nguyên, dựng pipeline, dựng image, triển khai
```

### Chi phí này đã hiện thực hoá, không phải rủi ro dự phóng

Nội dung commit trong repository ghi nhận trực tiếp:

| Commit | Nội dung |
|---|---|
| `d25209fcc` | `docs(budget-alert): cảnh báo file có 14 bản sao, phải sửa đồng loạt` |
| `ae3a8a963` | `feat(web): them cot luot xem khong duoc tinh thuong va sua sorter o 14 ung dung` |
| `88f436183` | `feat(all-partners): sync leaderboard config to all 12 partner frontends` |
| `543216578` | `fix(all-partners): crash trang chi tiết event do partnerDetail chưa destructure` |

Phân kỳ hành vi đã xảy ra: `src/app.tsx` có xử lý token hết hạn tại `vnpay/`, không có tại `yody/` — cùng tệp, cùng vai trò, hai hành vi khác nhau, không do chủ đích.

### Mức độ trùng lặp cho phép hợp nhất với chi phí thấp hơn dự kiến

Băm nội dung 522 đường dẫn `.ts`/`.tsx`/`.scss` (loại trừ thư mục sinh tự động `.umi`):

| Số phiên bản của cùng một đường dẫn | Số tệp |
|---|---|
| 1 — đồng nhất trên toàn bộ 15 ứng dụng | **317 (61%)** |
| 2 | 81 |
| 3–4 | 41 |
| 5–9 | 50 |
| 10–15 — phân kỳ thực sự | **33 (6%)** |

33 tệp phân kỳ tập trung vào ba nhóm: nhận diện thương hiệu, trang chủ, và tầng lõi bị trôi. Nhóm thứ ba không phải khác biệt chủ đích — chứng cứ tại mục 2.1.

---

## 2. Bối cảnh

### 2.1 Hiện trạng — đã đối chiếu mã nguồn

**Hạ tầng 15 ứng dụng đã đồng nhất.** Tập dependency trùng khớp hoàn toàn (`umi ^3.5.20`, `react 16`, 43 dependency; `hdbank − yody = ∅`). Toàn bộ 15 ứng dụng trỏ về **một** backend `https://ambassador.koc.com.vn/api/public`, **một** dự án Firebase `acreator-135b9`, **một** Google client, **một** TikTok client. Khác biệt cấu hình giới hạn ở `COMMON_PARTNER`, `APP_NAME`, `NEXT_PUBLIC_ORIGIN`, ba mã bài viết và mã GTM.

**Phân kỳ ở tầng lõi là hệ quả của việc sao chép, không phải thiết kế:**

| Tệp | Kết quả đối chiếu |
|---|---|
| `src/configs/api.ts` (`hdbank` ↔ `vpbank`) | Khác biệt duy nhất là **thứ tự khai báo**; nội dung trùng khớp |
| `src/services/user.ts` (`hdbank` ↔ `parasola`) | **Trùng khớp hoàn toàn** |
| `src/wrappers/home.tsx` | 15 phiên bản, nhưng toàn bộ nội dung là chuỗi nhận diện thương hiệu; không chứa logic |

**Nền tảng frontend đã hết vòng đời hỗ trợ.** Toàn bộ 16 ứng dụng (15 frontend + admin) build trên `node:14.17.3` — kết thúc hỗ trợ tháng 04/2023 — kèm `node-sass ^4.9.0` cũng đã ngừng phát triển. Backend không nằm trong tình trạng này: Go 1.24, Echo v4, mongo-driver 1.11, redis v8, minio-go v7.

### 2.2 Backend đã hỗ trợ đa người thuê; 15 ứng dụng là bản sao của cùng một ứng dụng đa người thuê

Đây là yếu tố làm giảm đáng kể phạm vi công việc so với ước lượng ban đầu.

**Phía backend:**

| Thành phần | Vị trí |
|---|---|
| `PartnerRaw.AllowDomains []string` | `backend/internal/model/mg/partner.go:51` |
| `GetDetailByDomain`, `GetListPartnersByDomain` | `backend/pkg/public/service/partner.go:40-88` |
| Toàn bộ truy vấn public giới hạn theo `query.Domain` | `backend/pkg/public/service/partner.go:310` |
| Cache Redis theo tên miền, TTL 4 giờ | `backend/pkg/public/service/partner.go:44-52` |
| Cờ tính năng theo đối tác (`PartnerOpts`) | leaderboard, `enableStaffCode`, `requireStaffCodeValidation`, `allowResubmitRejectedContent` |
| Biểu mẫu admin đã hỗ trợ chỉnh sửa các cờ trên | `admin/src/pages/partner/components/modal.tsx:219-457` |

**Phía frontend — kết quả đối chiếu quan trọng:** 15 ứng dụng không phải ứng dụng đơn-đối-tác. Chúng là cùng một ứng dụng đa người thuê, khác nhau ở một chỉ thị điều hướng.

| Thành phần | White-label (`hdbank`) | Đa đối tác (`frontend`) |
|---|---|---|
| `config/routes.ts` | **10** tuyến `/:partner/…` | 10 tuyến tương đương |
| `isOwnerPartner` | có (3–4 tệp) | có (3 tệp) |
| `pages/main-home` | `<Redirect to={/${COMMON_PARTNER}} />` | Trang giới thiệu gồm 5 section |
| Số lần dùng `COMMON_PARTNER` | 2 (hdbank), 3 (yody) | **0** |

Chế độ hiển thị do backend quyết định: `res.AllowHeaderPartner = len(res.Data) > 1` (`public/service/partner.go:376`). Ngoài ra `layouts/home/index.tsx:165` đã có sẵn nhánh không phụ thuộc `COMMON_PARTNER`.

**Hai hệ quả:**

1. `partner-app/` không cần xây dựng cơ chế phân giải người thuê mới; cơ chế đã tồn tại ở cả hai tầng.
2. Cấu trúc URL `/<partner>/<slug>` đã được áp dụng trên toàn bộ 15 tên miền, nên **di cư không làm thay đổi URL** — không phát sinh bảng chuyển hướng, không gián đoạn chỉ mục tìm kiếm.

### 2.3 Bài học kế thừa từ `creator-os` — ràng buộc thiết kế bắt buộc

`creator-os` được xây dựng để giải quyết cùng bài toán (`docs/architecture/05-theme-and-portals.md`: *"1 codebase + runtime theme config — giết bỏ điểm đau lớn nhất của Ambassador"*). Bốn bài học dưới đây đã được kiểm chứng qua sự cố thực tế tại hệ thống đó và được nâng thành ràng buộc bắt buộc của tài liệu này.

**BH-1 — Bố cục cố định dẫn tới dữ liệu giả. Ràng buộc: PC-005.**
Ghi nhận nguyên văn: *"template cố định ⇒ thứ tự + sự hiện diện của section nằm CỨNG trong JSX ⇒ section không có dữ liệu VẪN phải render ⇒ đẻ ra dữ liệu GIẢ để lấp chỗ trống"*. Hệ quả tại hệ thống đó là hằng số `MOCK_QUOTES` — nội dung chứng thực được tạo giả và gắn vào tên cùng ảnh đại diện của người dùng có thật. Do đó PC-005 quy định trang chủ là **mảng có thứ tự các section**, loại trừ mô hình chọn một trong N bố cục cố định.

**BH-2 — Section catalogue thuộc mã nguồn, không thuộc cơ sở dữ liệu. Ràng buộc: PC-005.**
*"Nếu để schema section trong DB → 2 nguồn sự thật + mất guardrail whitelist (tenant tự chế block mới)."* Cơ sở dữ liệu chỉ lưu mảng `sections`; kiểm tra tính hợp lệ thực hiện tại tầng ứng dụng dựa trên danh mục khai báo trong mã nguồn.

**BH-3 — Bảng màu, bán kính và đổ bóng không đủ để biểu diễn một bộ nhận diện. Ràng buộc: PC-002.**
*"Đổi preset chỉ đổi được màu, radius, shadow. Cái làm nên brutalist lại nằm ở chỗ khác — micro-label viết hoa giãn chữ, và kẻ ngang thay cho card (cấu trúc, không phải màu)."* Do đó bộ token phải bao gồm nhóm **style token**. Kèm một ràng buộc kỹ thuật cụ thể: sử dụng toán tử `??` thay cho `||` khi hợp nhất token, vì `radius = 0` là giá trị hợp lệ.

**BH-4 — Điều hướng được sinh từ `sections[]`. Ràng buộc: PC-005.**
*"Xoá section thì mục nav tự biến mất ⇒ không bao giờ có anchor chết."*

**Bài học bổ sung, ràng buộc PC-007:** khoá cache phía frontend phải trùng khớp tuyệt đối với khoá phía backend; sai lệch dẫn tới *"purge im lặng không trúng gì cả: publish xong trang vẫn cũ, không ai thấy lỗi"*. Yêu cầu kiểm thử đối chiếu hai phía.

### 2.4 Kết quả khảo sát bổ sung ảnh hưởng tới ước lượng

| Hạng mục | Số liệu | Ảnh hưởng |
|---|---|---|
| Lớp giao diện | **3.707** lượt sử dụng utility class Bootstrap tại 82% (160/194) tệp `.tsx`; **25** lượt dùng CSS module; tổng `.scss` chỉ 2.526 LOC | Bootstrap utility và Tailwind cùng mô hình utility-first ⇒ chuyển đổi mang tính **ánh xạ cơ học**, không phải thiết kế lại |
| Thư mục `components/` | 2.802/6.856 LOC (**41%**) là 35 component UI nguyên thuỷ (button, modal, input, select, toast, pagination…) | Thay thế bằng thư viện component, không viết lại |
| Kết xuất phía máy chủ | Toàn ứng dụng có **2** vị trí sử dụng `getInitialProps` | Không phát sinh chi phí gỡ bỏ SSR cũ; nhưng SSR chèn theme (PC-002) là **năng lực mới**, không có tiền lệ trong repository |
| Tầng trạng thái | `models/main.ts`: 411 LOC, 27 effect, 2 reducer, 62 tệp tiêu thụ | Không có máy trạng thái phức tạp |
| Độc lập phân hệ | `ekyc`, `tax-code`, `identity-info` không tham chiếu màn hình khác; chỉ `contract → pages/bank` | PC-004 không phát sinh công việc tách rời phụ thuộc |
| Bề mặt API | **70 endpoint**: `user` 27 · `bank` 12 · `event` 10 · `taxCode` 4 · `partners` 4 · `withdraw` 3 · còn lại 10 | Hợp đồng `partner-app/` phải hiện thực đầy đủ |
| Phân bố độ phức tạp | `home` 3.600 LOC · `ekyc` 2.602 · `account` 2.075 = **28%** tổng khối lượng màn hình | Ba màn này thuộc đợt đầu tiên (mục 6) |
| Kiểm thử hiện có | `hdbank` 1 tệp · `parasola` 1 tệp · `frontend` 9 · `fecredit` 7 | Không tồn tại đường cơ sở hồi quy ⇒ NFR-007 |
| Phông chữ | 528 KB (`yody`) → **26 MB** (`turborg`); định dạng `.ttf`; tên font-family khác nhau theo đối tác (`Averta`, `BeVietnamPro`, `Inter`) | Phông chữ là **tài nguyên theo đối tác**, phải tải lên và phục vụ lúc chạy ⇒ PC-003 |
| Tách gói | Không ứng dụng nào bật `dynamicImport` | Không có tách gói theo tuyến ⇒ NFR-004 |

### 2.5 Phân kỳ giữa 15 ứng dụng — cơ sở cho lộ trình di cư

Đo khoảng cách từng cặp (số tệp khác biệt, bao gồm tệp chỉ tồn tại một phía) trên `src/**` với `.ts`/`.tsx`/`.scss`:

| Cụm | Khoảng cách nội bộ | Đặc điểm |
|---|---|---|
| `yody` · `vnpay` · `mbbank` | **24–37** | Gần nhau nhất; chỉ có phân hệ `contract` |
| `hdbank` · `lusso` · `tpbank` · `parasola` · `flamingo` | 45–94 | Cùng hồ sơ phân hệ đầy đủ KYC |
| `vpbank` · `fecredit` · `vng` | 92–207 | KYC kèm biến thể riêng |
| `anker` · `turborg` | 152 | Hồ sơ nhẹ, có màn hình riêng |
| `wildrift` | ≥163 tới mọi ứng dụng | Bố cục trang chủ khác biệt hoàn toàn |
| `frontend` | ≥203 tới mọi ứng dụng | Chế độ đa đối tác, phạm vi phân hệ rộng nhất |

**Hồ sơ phân hệ theo đối tác** — đây là dữ liệu khởi tạo cấu hình cho quá trình di cư:

| Ứng dụng | Slug | Màu chính | ekyc | identity | tax-code | contract | contact | statistic | Màn hình riêng |
|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `yody` | `yody` | `#2a2a86` | | | | ● | | | |
| `vnpay` | `vnpaytaxi` | `#005baa` | | | | ● | | | |
| `mbbank` | `mbstudio` | `#151fd0` | | | | ● | | | |
| `anker` | *(fallback)* | `#1464f4` | | | | ● | | ● | `category-home` |
| `turborg` | `tuborg` | `#3DC00F` | | | | ● | ● | | `agency`, `info` |
| `flamingo` | `flamingo` | `#FE4177` | ● | ● | ● | ● | ● | | `info` |
| `tpbank` | `tpbank` | `#5E2E86` | ● | ● | ● | ● | ● | | |
| `hdbank` | `hdbank` | `#FAA61A` | ● | ● | ● | ● | ● | | |
| `lusso` | `lussosaigon` | `#066A9D` | ● | ● | ● | ● | ● | | |
| `parasola` | `parasola` | `#EE5799` | ● | ● | ● | ● | ● | | |
| `vpbank` | `vpbank` | `#005baa` | ● | ● | ● | | ● | | |
| `fecredit` | `fecredit` | `#00994F` | ● | ● | ● | ● | ● | | affiliate ×2 |
| `vng` | `vnggames` | `#F6910A` | ● | ● | ● | ● | ● | | `category-home` |
| `wildrift` | `wildrift` | `#F6910A` | | | | ● | ● | | `lp-store`, `mission`, `mission-detail` |
| `frontend` | *(không có)* | `#1464f4` | ● | ● | ● | ● | | ● | affiliate ×4, `support`, `campaigns`, `creator-profile` |

**Bốn điểm bất thường cần xác nhận trước khi di cư** (xem mục 13):
1. `anker/src/configs/app.ts:67` sử dụng `process.env.COMMON_PARTNER || 'anker'` trong khi biến không được khai báo tại `config.prod.ts` — cơ chế khác 14 ứng dụng còn lại.
2. `vpbank` không có phân hệ `contract` dù có đầy đủ KYC.
3. `frontend` không có màn hình `contact` trong khi 10/15 ứng dụng có.
4. Trùng màu chính: `vpbank` = `vnpay` (`#005baa`); `vng` = `wildrift` (`#F6910A`).

### 2.6 Phụ thuộc phải xử lý trước — ngoài phạm vi tài liệu này

Bốn vấn đề dưới đây phát hiện trong quá trình khảo sát, **tồn tại trên hệ thống hiện hành** và không do việc hợp nhất tạo ra. Chúng cần được xử lý như các task độc lập; nếu chuyển nguyên trạng sang `partner-app/` thì phạm vi ảnh hưởng sẽ mở rộng.

**PRE-1 — Điều hướng mở dẫn tới rò mã uỷ quyền OAuth (mức nghiêm trọng).**
`login-tiktok/index.tsx:14` và `connect-tiktok/index.tsx:12` sử dụng tham số `state` do bên gọi cung cấp làm đích điều hướng, không kiểm tra danh sách cho phép:
```js
window.location.href = `${query.state}dang-nhap-tiktok?code=${query.code}&redirect_uri=${redirectUri}`;
```
Backend cũng không giới hạn `redirectURI` (`internal/module/social/tiktok/tiktok.go:113`); tìm kiếm `allowlist|whitelist|validateRedirect` trên `backend/internal` và `backend/pkg` không có kết quả. `client_key` và `redirect_uri` dùng chung đều công khai trong bundle. Chuỗi khai thác dẫn tới chiếm đoạt tài khoản. Hiện diện tại **cả 15 ứng dụng, mỗi ứng dụng 2 trang**. Kết luận dựa trên đọc mã nguồn; cần xác nhận trên môi trường production trước khi xếp mức độ chính thức.

**PRE-2 — Truy vấn chi tiết chiến dịch không ràng buộc người thuê.**
`backend/pkg/public/service/event.go:186-195`: điều kiện truy vấn là `{"slug": param.Slug}`, tham số `partner` chỉ được thêm khi bên gọi cung cấp, và không có kiểm tra tên miền — khác với endpoint tương ứng của đối tác vốn có `funk.Contains(s.AllowDomains, host)` tại `partner.go:268`.

**PRE-3 — Không có ràng buộc duy nhất cho `slug` chiến dịch, và khoá cache thiếu phạm vi người thuê.**
Không tìm thấy khai báo unique index cho `slug` tại `internal/module/database/mongodb/index.go`. `GetKeyCacheEventDetailBySlug(slug)` (`redis/key.go:119`) đặt khoá chỉ theo `slug`; hàm hiện chưa được gọi.

**PRE-4 — Thẻ canonical trỏ sai tên miền trên toàn bộ ứng dụng white-label.**
`wrappers/home.tsx` gán `url: process.env.ORIGIN`, trong khi `ORIGIN = https://ambassador.koc.com.vn/` ở **cả 15 ứng dụng**; giá trị này được dùng cho `<link rel="canonical">` và `og:url`. Nguyên nhân là nhầm lẫn giữa `ORIGIN` (tên miền callback dùng chung) và `NEXT_PUBLIC_ORIGIN` (tên miền của đối tác). Mức độ ảnh hưởng thực tế cần tra cứu Search Console.

**PRE-5 — Trạng thái toàn cục theo request tại tầng SSR.**
`server.js:25-26` gán `global._cookies` và `global._navigatorLang` theo từng request trên tiến trình dùng chung. Hiện không có nơi nào đọc hai biến này (`grep "global\._"` trên `src/` không có kết quả), nên chưa gây hậu quả. Cần loại bỏ trước khi hợp nhất.

### 2.7 Ngoài phạm vi bổ sung

- Không cung cấp trình dựng trang tự do; section là danh mục đóng có schema.
- Không cho phép nhập CSS hoặc JavaScript thô; mọi tuỳ biến đi qua design token.
- Không hỗ trợ đa ngôn ngữ.
- Không thay đổi mô hình dữ liệu `PartnerRaw` hiện có; chỉ bổ sung collection mới.

---

## 3. User Personas

**P1. Đội vận hành** — người sử dụng chính của màn hình cấu hình, **không phải kỹ sư**. Phải hoàn thành toàn bộ quy trình onboard mà không cần hỗ trợ: nhập bảng màu, tải tài nguyên, bật/tắt phân hệ, sắp xếp trang chủ, xem trước, xuất bản, và khôi phục khi sai.

**P2. Marketing của đối tác** — chủ sở hữu nội dung trang chủ và văn bản hiển thị. Không truy cập admin trực tiếp; yêu cầu được chuyển qua P1.

**P3. Kỹ sư frontend** — hiện phải thực hiện một khối lượng công việc cho mỗi lần onboard, đồng thời nhân bản mỗi bản sửa lỗi ra 15 vị trí. Sau khi hoàn tất, chỉ tham gia khi đối tác yêu cầu một màn hình có cấu trúc chưa từng tồn tại (PC-009).

**P4. Kỹ sư backend** — bổ sung một collection và ba nhóm endpoint. Không thay đổi gate, sổ cái, hoặc logic tính thưởng.

**P5. Người dùng hiện hữu của 15 ứng dụng đối tác** — **đối tượng chịu tác động trực tiếp và là trọng tâm của yêu cầu chất lượng.** Toàn bộ nhóm này sẽ được chuyển sang `partner-app/` theo đợt. Ràng buộc: không mất phiên đăng nhập, không đứt liên kết, không suy giảm chức năng đang sử dụng. Một điều kiện thuận lợi đã được xác nhận: `authToken` lưu tại `localStorage` theo origin (`utils/storage.ts:10,31`) và mỗi tên miền giữ nguyên origin sau khi chuyển, nên phiên đăng nhập không bị ảnh hưởng.

**P6. Đối tác đang vận hành** — chủ sở hữu các hành vi riêng hiện có. Trong quá trình hoà giải biến thể (PC-012), một số hành vi sẽ được chuẩn hoá; mỗi thay đổi ảnh hưởng tới đối tác phải được thông báo và chấp thuận trước khi cutover.

---

## 4. Functional Requirements

### PC-001: Phân giải người thuê theo `Host` trên một triển khai duy nhất

**Priority:** Must Have — nền tảng cho toàn bộ yêu cầu còn lại

`partner-app/` vận hành trên một triển khai. Tập đối tác của mỗi request được xác định từ `Host`.

**Quy tắc phân giải:**

| Điều kiện | Kết quả |
|---|---|
| `Host` phân giải ra **đúng một** đối tác | Chế độ white-label: ẩn bộ chuyển đối tác, `/` chuyển hướng tới `/<slug>` |
| `Host` phân giải ra **nhiều** đối tác | Chế độ đa đối tác: hiển thị bộ chuyển, `/` hiển thị trang giới thiệu |
| `Host` không phân giải được đối tác nào | Trang lỗi tường minh; **không** rơi về đối tác mặc định |
| Biến môi trường `PARTNER_SLUG` có giá trị | Ghi đè `Host`; phục vụ môi trường phát triển và trường hợp cần tách triển khai riêng |

Chế độ hiển thị lấy từ cờ backend đã có (`AllowHeaderPartner`), không tính toán lại tại frontend.

**Cấu trúc URL giữ nguyên `/<partner>/<slug>`** như 15 ứng dụng hiện hành, đảm bảo tính liên tục của liên kết và chỉ mục tìm kiếm sau khi di cư.

**AC:**
- [ ] Hai tên miền khác nhau trên cùng một container trả về hai bộ nhận diện khác nhau
- [ ] Tên miền phân giải ra một đối tác: bộ chuyển bị ẩn, `/` chuyển hướng đúng
- [ ] Tên miền phân giải ra nhiều đối tác: bộ chuyển hiển thị, `/` là trang giới thiệu
- [ ] `Host` không hợp lệ trả về trang lỗi, không rò nhận diện của đối tác bất kỳ
- [ ] `PARTNER_SLUG` ghi đè `Host`, có unit test cho cả hai nhánh
- [ ] Không còn tham chiếu `COMMON_PARTNER` trong mã nguồn
- [ ] URL của mọi đối tác sau di cư trùng khớp URL trước di cư — đối chiếu bằng danh sách tuyến

---

### PC-002: Giao diện điều khiển bằng design token, kết xuất phía máy chủ

**Priority:** Must Have

Toàn bộ diện mạo được xác định bởi cấu hình lúc chạy. Không component nào được gán cứng giá trị màu.

**Bộ token bắt buộc:**

| Nhóm | Token |
|---|---|
| Màu | `primary`, `primaryForeground`, `secondary`, `secondaryForeground`, `accent`, `accentForeground`, `background`, `surface`, `elevated`, `text`, `textMuted`, `textSubtle`, `disabled`, `border`, `borderSubtle`, `success`, `warning`, `danger` |
| Hình khối | `radiusBase`, `radiusPill`, `shadowCard`, `shadowPop` |
| Chữ | `fontSans`, `fontDisplay` |
| Kiểu | `labelTransform`, `labelTracking`, `ctaTransform`, `ctaTracking`, `surfaceMode` |

Nhóm **Kiểu** là yêu cầu bắt buộc theo BH-3. `surfaceMode` (`rule` ↔ `card`) không ánh xạ qua CSS variable vì nó thay đổi cấu trúc kết xuất; component đọc giá trị này qua JavaScript.

**Thứ tự hợp nhất:** mặc định ứng dụng → preset đối tác lựa chọn → bộ token nền của preset → giá trị đối tác ghi đè. Sử dụng `??`, không sử dụng `||` (BH-3).

**Loại trừ hiện tượng nhấp nháy nội dung chưa định kiểu (FOUC).** CSS variable được ghi vào thuộc tính `style` của phần tử `<html>` tại thời điểm kết xuất phía máy chủ.

**AC:**
- [ ] Thay đổi giá trị màu trong admin, xuất bản, tải lại trang: giao diện thay đổi mà không build lại
- [ ] Tìm kiếm mã màu hex trong `partner-app/src/**` (trừ tệp định nghĩa token) trả về **0** kết quả
- [ ] Tải trang với băng thông giới hạn không xuất hiện nhấp nháy bảng màu mặc định
- [ ] `radiusBase = 0` được giữ nguyên; có unit test riêng cho trường hợp này
- [ ] Thay đổi `surfaceMode` làm thay đổi cấu trúc khối, không chỉ màu sắc

---

### PC-003: Quản lý tài nguyên theo đối tác, bao gồm phông chữ

**Priority:** Must Have

Toàn bộ tài nguyên nhận diện lấy từ cấu hình lúc chạy, không nhúng qua `require()` từ `src/assets/`.

**Hình ảnh — tối thiểu:** `logoUrl`, `logoMobileUrl`, `logoFooterUrl`, `faviconUrl`, `ogImageUrl`, `heroBannerUrl`, và bộ ảnh mốc thưởng.

**Phông chữ — hạng mục bổ sung tại v1.1.** Khảo sát cho thấy phông chữ là tài nguyên theo đối tác cả về tệp lẫn tên font-family (`Averta`, `BeVietnamPro`, `Inter`), dung lượng từ 528 KB tới 26 MB. Do đó token `fontSans` (chuỗi CSS font-family) không đủ. Yêu cầu: admin cho phép tải lên tệp phông chữ; ứng dụng sinh khai báo `@font-face` theo đối tác lúc chạy.

**Lưu trữ:** MinIO (`backend/internal/module/minio`), tải lên qua service `file` hiện có.

**Kiểm tra URL:** chấp nhận `http(s)://…` hoặc đường dẫn nội bộ bắt đầu bằng `/`. Từ chối URL protocol-relative (`//host`) và mọi scheme khác (`javascript:`, `data:`).

**AC:**
- [ ] Thay đổi logo trong admin, xuất bản: giao diện cập nhật mà không build lại
- [ ] Tài nguyên thiếu: sử dụng giá trị mặc định của ứng dụng, không vỡ bố cục
- [ ] URL dạng `javascript:` và `//evil.com` bị từ chối tại tầng máy chủ
- [ ] Tải lên tệp phông chữ cho một đối tác: `@font-face` được sinh đúng, chỉ áp dụng cho đối tác đó
- [ ] Phông chữ được chuyển sang định dạng `woff2` trong quá trình di cư

---

### PC-004: Bật/tắt phân hệ theo đối tác

**Priority:** Must Have

Mỗi nhóm màn hình tuỳ chọn tương ứng một cờ cấu hình. Tắt cờ dẫn tới ẩn khỏi điều hướng **và** chặn tại tuyến, không chỉ ẩn phần tử menu.

**Danh sách cờ tối thiểu:** `ekyc`, `identityInfo`, `taxCode`, `contract`, `contact`, `statistic`, `affiliate`, `guide`, `support`, `creatorProfile`. Giá trị khởi tạo cho 15 đối tác lấy từ bảng hồ sơ phân hệ tại mục 2.5.

**Xử lý lỗi mềm.** Khi tải cấu hình thất bại, ứng dụng sử dụng bộ mặc định an toàn (bật nhóm lõi, tắt phân hệ tuỳ chọn) thay vì trả về trang trắng.

Các cờ hiện có tại `PartnerOpts` (leaderboard, `enableStaffCode`, `requireStaffCodeValidation`, `allowResubmitRejectedContent`) **giữ nguyên vị trí và ngữ nghĩa** trong suốt giai đoạn chạy song song, vì các ứng dụng chưa di cư vẫn đang đọc chúng.

**AC:**
- [ ] Tắt `taxCode`: mục biến mất khỏi điều hướng và truy cập trực tiếp URL bị chặn
- [ ] API cấu hình lỗi: ứng dụng vẫn kết xuất với bộ cờ mặc định
- [ ] `PartnerOpts` giữ nguyên tên trường và vị trí; ứng dụng chưa di cư đọc được như trước

---

### PC-005: Trang chủ cấu hình bằng section catalogue

**Priority:** Must Have

Trang chủ là mảng có thứ tự các section (BH-1). Danh mục loại section nằm trong mã nguồn (BH-2); cơ sở dữ liệu chỉ lưu mảng, kiểm tra hợp lệ thực hiện tại tầng máy chủ.

**Danh mục tối thiểu** — suy ra từ tập component mà 14/15 ứng dụng đang sử dụng chung tại `pages/partner-home` (`Ratio`, `AppCarousel`, `Statistics`, `AppItemsCarousel`, `EventActive`, `ContentHighlight`):

| Loại | Phân loại | Bắt buộc | Cho phép lặp | Lên điều hướng |
|---|---|:--:|:--:|:--:|
| `hero` | biên tập | ● | | |
| `events` | dữ liệu | ● | | ● |
| `statistic` | dữ liệu | | | |
| `content-highlight` | dữ liệu | | | ● |
| `creator-newest` | dữ liệu | | | |
| `leaderboard` | dữ liệu | | | ● |
| `banner` | biên tập | | ● | |
| `faq` | biên tập | | | ● |
| `steps` | biên tập | | | |

**Section phân loại `dữ liệu` chỉ lưu tham số truy vấn**, không sao chép dữ liệu: `events` lưu `limit`, không lưu danh sách chiến dịch.

**Điều hướng được sinh từ `sections[]`** (BH-4).

**Section bắt buộc được cưỡng chế tại tầng máy chủ**, không chỉ vô hiệu hoá nút xoá trên giao diện.

**Định danh section bền vững.** Mỗi section mang `key` riêng; thao tác sửa và sắp xếp định địa chỉ theo `key`, không theo chỉ số mảng.

`wildrift` sử dụng tập section khác biệt hoàn toàn (`HeroSection`, `LevelSystemSection`, `RankingSection`, `RulesSection`, `CreatorsListSection`) và được xử lý qua PC-009.

**AC:**
- [ ] Thay đổi thứ tự trong admin, xuất bản: trang chủ phản ánh đúng thứ tự
- [ ] Tắt `leaderboard`: khối và mục điều hướng tương ứng cùng biến mất
- [ ] Gọi trực tiếp API để xoá section `hero`: máy chủ từ chối
- [ ] Gửi `type` không thuộc danh mục: máy chủ từ chối, không ghi vào cơ sở dữ liệu
- [ ] Sắp xếp lại rồi chỉnh sửa một section: thao tác áp dụng đúng section

---

### PC-006: Thẻ SEO, OpenGraph, GTM, `robots.txt` và `sitemap.xml` theo tên miền

**Priority:** Must Have

Lấy từ cấu hình: `title`, `description`, `keywords`, `ogImage`, `gtmId`.

**Thẻ canonical và `og:url` phải sinh từ `Host` của request**, không từ hằng số môi trường. Yêu cầu này khắc phục PRE-4; nếu chuyển nguyên trạng `wrappers/home.tsx` thì lỗi hiện hành sẽ được nhân rộng.

**`robots.txt` và `sitemap.xml` sinh theo tên miền.** Hiện không ứng dụng nào có hai tệp này; đây là năng lực bổ sung, không phải hạng mục chuyển đổi.

**AC:**
- [ ] Hai tên miền khác nhau trả về hai bộ thẻ meta khác nhau
- [ ] `canonical` và `og:url` trỏ về chính tên miền đang truy cập
- [ ] `gtmId` trống: không chèn script GTM
- [ ] `robots.txt` và `sitemap.xml` phản ánh đúng nội dung của tên miền yêu cầu

---

### PC-007: Quy trình bản nháp — xem trước — xuất bản — khôi phục

**Priority:** Must Have

Cấu hình có hai trạng thái: `draft` và `published`. Ứng dụng công khai chỉ đọc trạng thái `published`.

**Quy trình:**
1. P1 chỉnh sửa bản nháp; ứng dụng công khai không thay đổi.
2. Xem trước: mở ứng dụng thật với bản nháp thông qua token xem trước, dùng chung hạ tầng.
3. Xuất bản: sinh một phiên bản bất biến kèm `changelog` và định danh người thực hiện; con trỏ `published` chuyển sang phiên bản mới; xoá cache liên quan.
4. Khôi phục: đưa con trỏ về một phiên bản trước bằng một thao tác.

**Token xem trước** phải có thời hạn và không đoán được.

**Khoá cache phải trùng khớp tuyệt đối giữa frontend và backend**, có kiểm thử đối chiếu hai phía (mục 2.3).

**AC:**
- [ ] Chỉnh sửa bản nháp: ứng dụng công khai không thay đổi
- [ ] Liên kết xem trước hiển thị bản nháp; truy cập không có token hiển thị bản đã xuất bản
- [ ] Xuất bản: thay đổi có hiệu lực trong một lần tải lại
- [ ] Khôi phục phiên bản trước: trạng thái trở về đúng như trước
- [ ] Có kiểm thử đối chiếu khoá cache hai phía
- [ ] Nhật ký ghi nhận đầy đủ người thực hiện, thời điểm và nội dung thay đổi

---

### PC-008: Màn hình cấu hình trong admin

**Priority:** Must Have

Xây dựng trong `admin/` hiện hành (umi 3 + antd 4), đặt cạnh biểu mẫu đối tác tại `admin/src/pages/partner/components/modal.tsx`. Không xây dựng ứng dụng admin mới.

| Nhóm | Nội dung |
|---|---|
| Nhận diện | tên, slug, tên miền, preset, 18 giá trị màu, bán kính, đổ bóng, phông chữ, style token |
| Tài nguyên | tải lên và gán logo, favicon, ảnh OG, ảnh hero, ảnh mốc, **tệp phông chữ** |
| SEO | title, description, keywords, GTM |
| Phân hệ | công tắc cho từng cờ tại PC-004 |
| Trang chủ | danh sách section: thêm, xoá, sắp xếp, chỉnh sửa nội dung theo loại |
| Xuất bản | xem trước, xuất bản kèm changelog, danh sách phiên bản kèm thao tác khôi phục |
| **Chẩn đoán tên miền** | hiển thị tập đối tác mà mỗi tên miền phân giải ra; cảnh báo khi một tên miền được nhiều đối tác khai báo |

Nhóm cuối là yêu cầu bổ sung tại v1.1: cấu hình `allowDomains` sai khiến một tên miền chuyển sang chế độ đa đối tác mà không phát sinh lỗi, dẫn tới hiển thị đối tác không mong muốn.

**Đối tượng sử dụng là P1, không phải kỹ sư.** Nhãn trường bằng tiếng Việt, bộ chọn màu trực quan, thông báo lỗi mô tả nguyên nhân và cách khắc phục thay vì tên trường kỹ thuật.

**AC:**
- [ ] P1 hoàn thành quy trình tạo và xuất bản một đối tác mà không cần hỗ trợ — nghiệm thu bằng phiên thao tác thực tế
- [ ] Mọi kiểm tra tại tầng máy chủ đều có thông báo tương ứng trên biểu mẫu
- [ ] Bộ chọn màu hiển thị kết quả trực tiếp trong admin
- [ ] Màn hình chẩn đoán cảnh báo đúng khi một tên miền được khai báo tại nhiều đối tác

---

### PC-009: Cơ chế slot cho màn hình riêng của đối tác

**Priority:** Must Have — nâng từ Should Have tại v1.1

Sáu màn hình không thể biểu diễn bằng cấu hình: `agency` (`turborg`), `lp-store`, `mission`, `mission-detail` (`wildrift`), `category-home` (`anker`, `vng`), `info` (`flamingo`, `turborg`). Sau quyết định di cư toàn bộ, các màn hình này có người dùng thực và thuộc phạm vi bắt buộc.

**Cơ chế:** mỗi màn hình là một slot với hợp đồng props tường minh — tầng trang chịu trách nhiệm dữ liệu, slot chịu trách nhiệm hiển thị. Registry ánh xạ đối tác sang module; slot không được khai báo sẽ kế thừa bản nền.

**Ràng buộc:** không sử dụng điều kiện theo định danh đối tác (`if (partner === 'x')`) trong mã màn hình. Lựa chọn component thực hiện qua registry.

**AC:**
- [ ] Bổ sung một slot cho một đối tác chỉ yêu cầu thêm một thư mục và một dòng registry
- [ ] Đối tác không khai báo override nhận bản nền, không cần cấu hình bổ sung
- [ ] Tìm kiếm `partner ===` trong thư mục màn hình trả về **0** kết quả

---

### PC-010: Vận hành song song và ngừng ứng dụng cũ

**Priority:** Must Have — yêu cầu này được định nghĩa lại hoàn toàn tại v1.1

Trước đây yêu cầu này quy định không thay đổi 15 ứng dụng hiện hành. Sau quyết định di cư, mục tiêu chuyển thành: **duy trì ứng dụng cũ ở trạng thái sẵn sàng khôi phục cho tới khi đợt di cư tương ứng được nghiệm thu, sau đó mới ngừng.**

**Quy tắc:**

| Giai đoạn | Trạng thái ứng dụng cũ |
|---|---|
| Trước cutover của đợt | Đang phục vụ lưu lượng |
| Sau cutover, trong thời gian theo dõi | **Giữ nguyên image và cấu hình triển khai**, không phục vụ lưu lượng, có thể khôi phục trong vài phút bằng thao tác chuyển ingress |
| Sau khi nghiệm thu đợt | Ngừng triển khai; thư mục mã nguồn được gỡ trong một commit riêng |

Thời gian theo dõi tối thiểu cho mỗi đợt: **hai tuần** kể từ cutover.

Thay đổi backend phải giữ tương thích ngược trong toàn bộ giai đoạn chạy song song: các ứng dụng chưa di cư vẫn đang gọi cùng bộ endpoint.

**AC:**
- [ ] Với mỗi đợt: khôi phục về ứng dụng cũ thực hiện được trong dưới 15 phút, có diễn tập trước cutover
- [ ] Hình dạng response của các endpoint public giữ nguyên trong suốt giai đoạn chạy song song
- [ ] Thư mục mã nguồn cũ chỉ được gỡ sau khi đợt tương ứng nghiệm thu, bằng commit riêng biệt
- [ ] Không có thời điểm nào tồn tại hai hệ cùng phục vụ một tên miền

---

### PC-011: Uỷ quyền OAuth trên nhiều tên miền

**Priority:** Must Have — yêu cầu mới tại v1.1

Khảo sát cho thấy chỉ một trong bốn nhà cung cấp danh tính hiện hỗ trợ thêm tên miền mà không cần thao tác thủ công:

| Nhà cung cấp | Cơ chế hiện tại | Yêu cầu khi thêm tên miền |
|---|---|---|
| TikTok (đăng nhập, liên kết) | Một `redirect_uri` dùng chung kèm chuyển tiếp theo `state` | Không |
| Google (đăng nhập) | `@react-oauth/google`, thành phần `<GoogleLogin>` | Đăng ký Authorized JavaScript origin |
| Facebook (liên kết) | `react-facebook-login` tại `account/management/facebook-section` | Đăng ký App Domain và Valid OAuth Redirect URI |
| ACCESSTRADE SSO | `redirectUri = ${NEXT_PUBLIC_ORIGIN}lien-ket-tai-khoan` | Đăng ký redirect URI |

**Yêu cầu:** áp dụng mô hình một điểm callback dùng chung cho cả bốn nhà cung cấp, **kèm kiểm tra đích chuyển tiếp tại tầng máy chủ dựa trên `allowDomains`**. Nếu phương án này không khả thi với một nhà cung cấp cụ thể, tài liệu vận hành phải liệt kê tường minh thao tác thủ công tương ứng và quy trình onboard phải phản ánh điều đó.

Yêu cầu này đồng thời là biện pháp khắc phục PRE-1 trong phạm vi `partner-app/`.

**AC:**
- [ ] Thêm một tên miền mới trong admin: đăng nhập TikTok hoạt động, không thao tác bên ngoài
- [ ] Đích chuyển tiếp sau uỷ quyền được kiểm tra tại máy chủ theo `allowDomains`; giá trị ngoài danh sách bị từ chối
- [ ] Tham số chống CSRF tách biệt khỏi tham số định tuyến
- [ ] Với nhà cung cấp còn yêu cầu thao tác thủ công: thao tác được ghi trong tài liệu vận hành và trong quy trình onboard

---

### PC-012: Hoà giải biến thể giữa 15 ứng dụng

**Priority:** Must Have — yêu cầu mới tại v1.1

15 phiên bản của mỗi tệp phân kỳ phải được rút gọn về một. Đo khoảng cách lớn nhất giữa hai phiên bản bất kỳ:

| Tệp | Số phiên bản | Δ dòng tối đa | Phân loại |
|---|---:|---:|---|
| `wrappers/home.tsx` | 15 | 12 | Chuyển thành cấu hình |
| `app.tsx` | 10 | 31 | Trôi — chọn phiên bản đầy đủ nhất |
| `configs/app.ts` | 12 | 59 | Chuyển thành cấu hình |
| `utils/helper.ts` | 10 | 68 | Trôi |
| `components/app/button` | 15 | 79 | Chuyển thành design token |
| `services/user.ts` | 10 | 168 | Cần đối chiếu hành vi |
| `pages/partner-home/index.tsx` | 15 | 210 | Chuyển thành section |
| `configs/api.ts` | 10 | 222 | Trôi kèm chênh lệch endpoint |
| `layouts/home/index.tsx` | 14 | 246 | Trôi kèm logic |
| `interfaces/event.ts` | 11 | 251 | **Khác biệt hành vi** |
| `models/main.ts` | 11 | 288 | **Khác biệt hành vi** |
| `global.scss` | 15 | 300 | Chuyển thành design token |
| `components/layout/main/footer` | 14 | 305 | Chuyển thành cấu hình |
| `components/layout/main/header` | 15 | 659 | **Khác biệt hành vi** |
| `pages/home/components/not-logged-in` | 15 | 914 | **Khác biệt hành vi** |

**Quy trình bắt buộc:**
1. Phân loại từng tệp vào một trong ba nhóm: chuyển thành cấu hình, trôi, khác biệt hành vi.
2. Nhóm *chuyển thành cấu hình* và *trôi*: kỹ sư quyết định, ghi lý do trong commit.
3. Nhóm *khác biệt hành vi*: mỗi trường hợp phải có quyết định được ghi nhận, nêu rõ đối tác nào thay đổi hành vi và hình thức xử lý (cấu hình, slot, hoặc chuẩn hoá). **Đối tác bị ảnh hưởng phải được thông báo trước cutover.**
4. Duy trì một bảng theo dõi quyết định, cập nhật trong cùng commit với thay đổi mã nguồn.

**AC:**
- [ ] Toàn bộ 33 tệp phân kỳ được phân loại và có quyết định ghi nhận
- [ ] Mọi trường hợp thuộc nhóm *khác biệt hành vi* có xác nhận từ phía đối tác trước cutover
- [ ] Bảng theo dõi quyết định được cập nhật cùng commit, không cập nhật sau

---

### PC-013: Di cư và cutover theo đợt

**Priority:** Must Have — yêu cầu mới tại v1.1

Di cư thực hiện theo 6 đợt (mục 6), không chuyển đổi đồng loạt.

**Điều kiện vào cutover của mỗi đợt:**
- Cấu hình của toàn bộ đối tác trong đợt đã khởi tạo và xuất bản ở môi trường staging
- Bộ ảnh đối chiếu trước/sau hoàn tất cho từng màn hình × từng đối tác (NFR-007)
- PC-012 hoàn tất cho phạm vi tệp mà đợt chạm tới
- Diễn tập khôi phục thành công

**Điều kiện nghiệm thu đợt:** hai tuần vận hành không phát sinh sự cố mức P1/P2 liên quan tới di cư.

**AC:**
- [ ] Mỗi đợt có biên bản điều kiện vào và điều kiện nghiệm thu
- [ ] Diễn tập khôi phục thực hiện trước mỗi cutover, có ghi nhận thời gian thực tế
- [ ] Không đợt nào bắt đầu khi đợt trước chưa nghiệm thu

---

## 5. Non-Functional Requirements

### NFR-001: Tương thích ngược trong giai đoạn chạy song song
Hình dạng response của các endpoint public giữ nguyên cho tới khi đợt cuối nghiệm thu, vì các ứng dụng chưa di cư vẫn đang gọi chúng.

### NFR-002: Không nhân bản luật nghiệp vụ ra frontend
Điều kiện tính thưởng, gate nộp bài và luật xét duyệt tiếp tục nằm tại backend.

### NFR-003: Khả năng chịu lỗi
Khi API cấu hình lỗi hoặc phản hồi chậm, ứng dụng sử dụng bản cache gần nhất; không trả về trang trắng.

### NFR-004: Hiệu năng và kích thước gói
Kết xuất phía máy chủ phát sinh tối đa một request lấy cấu hình cho mỗi request trang, với tỷ lệ trúng cache cao. Do `partner-app/` chứa toàn bộ 33 màn hình và hiện không ứng dụng nào bật `dynamicImport`, yêu cầu **tách gói theo tuyến và tải theo cờ phân hệ**. Ngưỡng cụ thể xác lập sau lần build đầu tiên và ghi bổ sung vào tài liệu.

### NFR-005: Ngôn ngữ
Toàn bộ tiếng Việt.

### NFR-006: Chất lượng hiển thị
Vỡ bố cục, tràn văn bản, chồng lớp, sai lệch trên thiết bị di động đều là lỗi chặn nghiệm thu. Mỗi màn hình phải được kiểm tra trực quan trên cả desktop và di động, với tối thiểu hai preset tương phản, trước khi báo hoàn thành.

### NFR-007: Đường cơ sở hồi quy
Repository hiện không có đường cơ sở hồi quy (`hdbank` và `parasola` mỗi ứng dụng một tệp kiểm thử). Trước mỗi đợt di cư, phải thiết lập bộ ảnh đối chiếu cho từng màn hình × từng đối tác trong đợt, chụp từ ứng dụng cũ đang chạy. Bộ ảnh này là căn cứ nghiệm thu.

Kiểm thử tự động bắt buộc cho: hợp nhất design token (bao gồm trường hợp `radius = 0`), kiểm tra schema section, phân giải người thuê theo `Host`, và đối chiếu khoá cache hai phía.

### NFR-008: Bán kính ảnh hưởng và khả năng quan sát
Sau hợp nhất, một sự cố đơn lẻ tác động tới toàn bộ đối tác thay vì một. Yêu cầu:
- Mọi bản ghi nhật ký gắn định danh tên miền và đối tác, áp dụng từ ngày đầu tiên
- Phân biệt rõ hai lớp khôi phục: khôi phục **mã nguồn** tác động toàn bộ đối tác; khôi phục **cấu hình** tác động một đối tác. Quyền thực hiện mỗi lớp phải được quy định tường minh
- Triển khai mã nguồn áp dụng cơ chế phát hành từng phần trước khi mở toàn bộ

### NFR-009: Quản trị thay đổi theo yêu cầu đối tác
Sau hợp nhất, yêu cầu riêng của một đối tác tác động tới toàn bộ hệ thống. Cần quy trình tiếp nhận và phân loại yêu cầu thành: cấu hình, slot (PC-009), hoặc từ chối — kèm người chịu trách nhiệm quyết định. Thiếu quy trình này, áp lực vận hành sẽ dẫn tới việc tách nhánh mã nguồn trở lại.

---

## 6. Epics và thứ tự

### 6.1 Giai đoạn xây dựng

| # | Epic | Phụ thuộc |
|---|---|---|
| E0 | Xử lý phụ thuộc PRE-1 → PRE-5 (mục 2.6) — task độc lập, phải hoàn tất trước E2 | — |
| E1 | Backend: collection `PartnerAppConfig`, phiên bản và trạng thái, endpoint đọc theo tên miền, xoá cache | — |
| E2 | `partner-app/` khởi tạo + PC-001 + PC-002 + PC-003 | E0, E1 |
| E3 | Admin: nhóm Nhận diện, Tài nguyên, SEO, PC-007, chẩn đoán tên miền | E1 |
| E4 | 14 màn hình lõi + hạ tầng dùng chung. **Ưu tiên `home`, `ekyc`, `account` (28% khối lượng) ở đầu epic** | E2 |
| E5 | PC-005 + màn hình Trang chủ trong admin | E3, E4 |
| E6 | PC-004 + 5 màn hình KYC/thuế/hợp đồng | E4 |
| E7 | 8 màn hình phân hệ: affiliate ×4, `statistic`, `creator-profile`, `support`, `campaigns` | E6 |
| E8 | PC-009 + 6 màn hình riêng | E7 |
| E9 | PC-011 uỷ quyền OAuth trên nhiều tên miền | E2 |
| E10 | PC-012 hoà giải biến thể | E4 |

Cơ chế slot (PC-009) triển khai tại E8 nhưng **phải được thiết kế từ E4**; xây dựng màn hình lõi không theo hợp đồng slot sẽ dẫn tới phải viết lại.

### 6.2 Giai đoạn di cư

| Đợt | Đối tác | Khoảng cách nội bộ | Căn cứ |
|---|---|---|---|
| M1 | `yody` · `vnpay` · `mbbank` | 24–37 | Gần nhau nhất, hồ sơ phân hệ tối thiểu. Đợt này gánh toàn bộ hạ tầng dùng chung |
| M2 | `hdbank` · `lusso` · `tpbank` · `parasola` · `flamingo` | 45–94 | Cụm đồng nhất, cùng hồ sơ KYC |
| M3 | `vpbank` · `fecredit` · `vng` | 92–207 | KYC kèm biến thể riêng |
| M4 | `anker` · `turborg` | 152 | Hồ sơ nhẹ kèm màn hình riêng |
| M5 | `wildrift` | ≥163 | Bố cục trang chủ khác biệt hoàn toàn |
| M6 | `frontend` | ≥203 | Chế độ đa đối tác, phạm vi phân hệ rộng nhất |

Thứ tự này bảo đảm rủi ro giảm dần theo thời gian, và chi phí biên của mỗi đối tác giảm sau đợt M1. Mỗi đợt tuân thủ PC-013.

---

## 7. Kiến trúc

```
Trình duyệt → <tên miền đối tác>
   │
   ▼ partner-app: đọc Host  (hoặc biến PARTNER_SLUG — PC-001)
   │
   ▼ GET /api/public/partners/app-config?domain=…      [Redis 4h — đã có]
   │      └─ ?preview=<token> → trả bản draft thay bản published (PC-007)
   │
   ▼ Kết xuất phía máy chủ
   │   hợp nhất token: mặc định ứng dụng → preset → ghi đè   (sử dụng ??)
   │   ghi CSS variable vào thuộc tính style của <html>       → loại trừ FOUC (PC-002)
   │   sinh title / favicon / OG / canonical theo Host / GTM  (PC-006)
   │
   ▼ Kết xuất phía trình duyệt
       ThemeProvider   → component đọc token
       FeatureFlags    → ẩn điều hướng và chặn tuyến theo cờ  (PC-004)
       sections[]      → kết xuất theo thứ tự; điều hướng sinh từ đây (PC-005)
       slot registry   → đối tác có override dùng bản riêng, còn lại kế thừa bản nền (PC-009)

admin (umi 3 + antd 4)
   │  chỉnh bản nháp → Xem trước → Xuất bản → sinh phiên bản + xoá cache
   └───────────────────────────────────────→ Khôi phục phiên bản trước
```

**Endpoint bổ sung — toàn bộ là thêm mới:**
- `GET /api/public/partners/app-config` — đọc cấu hình `published` theo tên miền, hoặc `draft` khi có token xem trước
- `GET|PUT /api/admin/partners/:id/app-config` — đọc và ghi bản nháp
- `POST /api/admin/partners/:id/app-config/publish` và `.../restore/:version`

**Bề mặt API mà `partner-app/` phải hiện thực: 70 endpoint** — `user` 27, `bank` 12, `event` 10, `taxCode` 4, `partners` 4, `withdraw` 3, `upload` 2, `notification` 2, còn lại 6.

**Lược đồ `partner_app_configs` (MongoDB):**

```
partner        ObjectId          — tham chiếu PartnerRaw hiện có
status         draft | published
version        int
branding       { logoUrl, logoMobileUrl, logoFooterUrl, faviconUrl, ogImageUrl,
                 heroBannerUrl, brandName, preset,
                 colors{18 token}, radiusBase, radiusPill,
                 fontSans, fontDisplay, fontFiles[], shadowCard, shadowPop,
                 style{labelTransform, labelTracking, ctaTransform,
                       ctaTracking, surfaceMode} }
seo            { title, description, keywords, ogImage, gtmId }
content        { articleIds{support, qa, term, condition}, footerLinks[], website }
modules        { ekyc, identityInfo, taxCode, contract, contact,
                 statistic, affiliate, guide, support, creatorProfile }
sections       [ { key, type, …theo loại } ]
auth           { google, tiktok, facebook, sso{…} }
publishedAt / publishedBy / changelog
```

`canonical` không lưu trong lược đồ; giá trị này sinh từ `Host` của request (PC-006).

`PartnerOpts` giữ nguyên vị trí hiện tại trong suốt giai đoạn chạy song song (PC-004).

---

## 8. Implementation Scope

### Thay đổi cần thực hiện

**`backend/` (Go 1.24 · Echo · MongoDB · Redis · MinIO — giữ nguyên nền tảng):**
- Model `PartnerAppConfigRaw` và `PartnerAppConfigVersionRaw`, collection mới
- Ba nhóm endpoint tại mục 7
- Kiểm tra schema section tại tầng máy chủ (BH-2), cưỡng chế danh mục và section bắt buộc
- Kiểm tra URL tài nguyên (PC-003)
- Kiểm tra đích chuyển tiếp OAuth theo `allowDomains` (PC-011)
- Xoá cache theo khoá trùng khớp với frontend khi xuất bản

**`partner-app/` (ứng dụng mới — Next.js · React 18/19 · Tailwind):**
- PC-001 → PC-007, PC-009, PC-011
- 33 màn hình: 14 lõi, 5 KYC/thuế/hợp đồng, 8 phân hệ, 6 riêng
- Chế độ đa đối tác kèm trang giới thiệu (phục vụ đợt M6)
- Hạ tầng dùng chung: components, layouts, models, services, utils, hooks

**`admin/` (umi 3 + antd 4 — giữ nguyên nền tảng):**
- Bảy nhóm màn hình tại PC-008

**Hạ tầng và vận hành:**
- Một image, một triển khai, nhiều tên miền
- Cơ chế dự phòng cấu hình khi API lỗi (NFR-003)
- Gắn thẻ đối tác trong nhật ký (NFR-008)
- Quy trình cutover và khôi phục theo đợt (PC-013)

### Không thực hiện

- Không nâng cấp hoặc tái cấu trúc 15 ứng dụng hiện hành — chúng được **thay thế**, không được sửa
- Không thay đổi nền tảng `admin/`
- Không thay đổi backend nghiệp vụ: gate, sổ cái, thu thập chỉ số, đối soát, tính thưởng
- Không di chuyển `PartnerOpts` sang cấu hình mới trong giai đoạn chạy song song
- Không tạo phụ thuộc vào package của `creator-os`

---

## 9. Assumptions

1. Toàn bộ tên miền đối tác tiếp tục kết thúc trên hạ tầng nội bộ, như 15 tên miền hiện hành.
2. Backend là nguồn dữ liệu duy nhất; `partner-app/` không có cơ sở dữ liệu riêng.
3. Đội ngũ có ít nhất một kỹ sư thành thạo Next.js và Tailwind, hoặc điều động được từ đội `creator-os`.
4. Số đối tác vận hành trên `partner-app/` trong năm đầu ở mức vài chục, phù hợp với cơ chế cache theo tên miền hiện có.
5. Đội vận hành (P1) tiếp nhận công việc onboard. Nếu không, PC-008 mất phần lớn giá trị và cần xem lại mức đầu tư.
6. Các đối tác chấp nhận chuẩn hoá một số hành vi riêng trong phạm vi PC-012, sau khi được thông báo.

---

## 10. Out of Scope

- Nâng cấp `umi`, Node hoặc `node-sass` của 15 ứng dụng hiện hành — chúng được thay thế, không nâng cấp
- Hỗ trợ đa ngôn ngữ
- Đối tác truy cập admin trực tiếp
- Trình dựng trang tự do, nhập HTML hoặc CSS thô
- Chuyển đổi sang `creator-os` như một nền tảng
- Endpoint gộp cấu hình nhiều đối tác trong một request — chỉ thực hiện nếu Assumption #4 không còn đúng
- Xử lý PRE-1 → PRE-5: là các task độc lập, tiền đề của E2, không thuộc phạm vi tài liệu này

---

## 11. Traceability — đối chiếu với thiết kế tham khảo `creator-os`

| `creator-os` | Tài liệu này | Quan hệ |
|---|---|---|
| `packages/theme/src/tokens.ts` | **PC-002** | Kế thừa mô hình token và thứ tự hợp nhất, bao gồm ràng buộc `??` thay `\|\|`. Hiện thực lại |
| `portal-creator/app/layout.tsx` | **PC-002** | Áp dụng phương pháp chèn CSS variable khi kết xuất phía máy chủ |
| `packages/feature-flags` | **PC-004** | Kế thừa mô hình, giữ đặc tính xử lý lỗi mềm. Hiện thực lại |
| `packages/contracts/src/landing-sections.ts` | **PC-005** | Kế thừa mô hình danh mục. Danh mục section xây dựng riêng theo tập component thực tế của Ambassador |
| `CmsDocument` + `CmsDocumentVersion` | **PC-007** | Kế thừa mô hình bản nháp và phiên bản; hiện thực trên MongoDB |
| `portal-creator/themes/` | **PC-009** | Kế thừa mô hình registry và kế thừa bản nền |
| Model `Domain` | **PC-001** | Không sử dụng — Ambassador đã có `AllowDomains` trên `PartnerRaw` |
| `docs/architecture/14-editions-and-deployment.md` | **PC-001**, **PC-010** | Kế thừa nguyên tắc: khác biệt về triển khai không nằm trong mã nguồn |
| NestJS, Prisma, PostgreSQL, RLS | — | Không sử dụng; backend giữ Go và MongoDB |
| `packages/ui` | — | Không sử dụng mã nguồn |

---

## 12. Resolved Questions

| Câu hỏi | Kết luận |
|---|---|
| Đưa đối tác lên `creator-os` hay xây dựng trong Ambassador? | **Xây dựng trong Ambassador.** `creator-os` là tài liệu tham khảo thiết kế (03/09) |
| Có sử dụng mã nguồn hoặc package của `creator-os`? | **Không.** Kế thừa mô hình thiết kế và bài học vận hành (03/09) |
| Giữ nền tảng `umi 3` hay chuyển sang nền tảng mới? | **Chuyển.** Căn cứ: `node:14.17.3` kết thúc hỗ trợ 04/2023 và `node-sass 4` đã ngừng phát triển; đồng thời khảo sát cho thấy chi phí chuyển đổi thấp hơn dự kiến — 41% thư mục `components/` là UI nguyên thuỷ thay thế được bằng thư viện, lớp giao diện là utility-first nên ánh xạ sang Tailwind mang tính cơ học, và toàn ứng dụng chỉ có 2 vị trí phụ thuộc SSR. Việc di cư 15 ứng dụng không làm thay đổi kết luận này, vì cả 15 đều phải hoà giải về một bản dù ở nền tảng nào |
| Một triển khai chung hay tách theo đối tác? | **Một triển khai**, phân giải theo `Host`. Giữ một điểm ghi đè (`PARTNER_SLUG`) để tách khi cần (03/09) |
| Xử lý 15 ứng dụng hiện hành thế nào? | **Di cư toàn bộ theo 6 đợt**, có giai đoạn chạy song song và khả năng khôi phục (04/09 — thay thế kết luận ngày 03/09) |
| Phạm vi màn hình? | **33 màn hình**, bao gồm 6 màn hình riêng vốn có người dùng thực |
| Mức độ cấu hình của trang chủ? | **Cấu hình đầy đủ**: bật/tắt, sắp xếp, chỉnh sửa nội dung, kèm khối nội dung tự do có schema |
| Cấu hình có hiệu lực ngay hay qua bước duyệt? | **Bản nháp → xem trước → xuất bản**, có lịch sử phiên bản và khôi phục (PC-007) |
| Ai vận hành màn hình cấu hình? | **Đội vận hành.** P1 không phải kỹ sư ⇒ PC-008 nghiệm thu bằng phiên thao tác thực tế |
| Xây dựng màn hình cấu hình trên nền tảng nào? | **`admin/` hiện hành** (umi 3 + antd 4), đặt cạnh biểu mẫu đối tác |
| Có cần chế độ đa đối tác không? | **Có, bắt buộc** — `frontend/` thuộc phạm vi di cư (đợt M6) |
| URL có thay đổi sau di cư không? | **Không.** Cấu trúc `/<partner>/<slug>` đã được áp dụng trên toàn bộ 15 ứng dụng |
| Người dùng có bị đăng xuất khi chuyển không? | **Không.** `authToken` lưu tại `localStorage` theo origin và mỗi tên miền giữ nguyên origin |

---

## 13. Open Questions

1. **Bốn điểm bất thường tại mục 2.5 cần xác nhận từ phía sản phẩm trước đợt M3–M4:** `anker` sử dụng cơ chế fallback khác 14 ứng dụng còn lại; `vpbank` không có phân hệ `contract`; `frontend` không có màn hình `contact`; hai cặp đối tác trùng màu chính. Cần xác định mỗi trường hợp là chủ đích hay thiếu sót.
2. **Ngưỡng bán kính ảnh hưởng:** số đối tác tối đa trên một triển khai trước khi cần tách. Chưa cản trở việc bắt đầu, nhưng cần xác lập trước khi đưa lên production.
3. **Bộ preset khởi điểm:** đề xuất tối thiểu hai preset tương phản để kiểm chứng tính đầy đủ của hợp đồng token — chỉnh sửa một preset mà bỏ sót preset còn lại phải làm kiểm thử thất bại. Cần thiết kế tham gia.
4. **Vị trí `partner-app/`:** cùng repository `ambassador` hay tách repository riêng. Phương án cùng repository dẫn tới hai nền tảng frontend song song trong giai đoạn di cư; phương án tách repository phát sinh thêm một pipeline. Đề xuất: cùng repository, ranh giới thư mục tường minh. Cần devops xác nhận.
5. **Chủ sở hữu quy trình NFR-009:** ai là người quyết định phân loại một yêu cầu riêng của đối tác thành cấu hình, slot, hoặc từ chối. Cần xác định trước đợt M2.
6. **Thứ tự ưu tiên của E0:** PRE-1 (điều hướng mở) có mức nghiêm trọng cao hơn phạm vi tài liệu này. Cần xác nhận việc tách thành task độc lập và xử lý ngay, không chờ lộ trình di cư.

---

## 14. Revision History

| Version | Date | Thay đổi |
|---|---|---|
| 1.0 | 2026-09-03 | Bản đầu. Chốt phương án: ứng dụng mới trên nền tảng hiện đại, backend Go/MongoDB giữ nguyên, `creator-os` là tài liệu tham khảo thiết kế. Chốt một triển khai phân giải theo `Host`, phạm vi 33 màn hình, quy trình bản nháp/xem trước/xuất bản/khôi phục. Bốn bài học từ `creator-os` nâng thành ràng buộc của PC-002 và PC-005. **Phạm vi khi đó: 15 ứng dụng hiện hành giữ nguyên, không di cư** |
| 1.1 | 2026-09-04 | **Thay đổi phạm vi: di cư toàn bộ 15 ứng dụng theo 6 đợt.** PC-010 định nghĩa lại từ "không thay đổi ứng dụng cũ" thành "vận hành song song và ngừng theo đợt". Bổ sung PC-011 (uỷ quyền OAuth trên nhiều tên miền), PC-012 (hoà giải biến thể), PC-013 (di cư và cutover theo đợt), NFR-007 → NFR-009. Sửa PC-001 theo mô hình tên miền → tập đối tác, phù hợp với `AllowHeaderPartner` đã có ở backend; ghi nhận URL không thay đổi sau di cư. Bổ sung phông chữ vào PC-003; canonical, `robots.txt`, `sitemap.xml` vào PC-006; màn hình chẩn đoán tên miền vào PC-008. PC-009 nâng lên Must Have. Bổ sung mục 2.4 (kết quả khảo sát ảnh hưởng ước lượng), 2.5 (phân kỳ giữa 15 ứng dụng và hồ sơ phân hệ), 2.6 (năm phụ thuộc phải xử lý trước). Viết lại P5 và P6. Thay lập luận của kết luận chuyển nền tảng, do lập luận cũ dựa trên tiền đề không di cư |
