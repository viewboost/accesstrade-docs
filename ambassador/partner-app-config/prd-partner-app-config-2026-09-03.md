# Product Requirements Document: Hợp nhất frontend đối tác trên nền cấu hình lúc chạy (`partner-app/`)

**Date:** 2026-09-03 (cập nhật 2026-09-04)
**Author:** Nguyễn Đăng Định
**Version:** 1.2
**Reviewer:** _chưa có_
**Project Level:** Level 4 — ứng dụng mới + mở rộng backend + mở rộng admin + di cư 5 hệ thống đang chạy
**Status:** Draft — phạm vi đã chốt, chờ review
**Mức độ:** **P2** — không có sự cố đang diễn ra, nhưng chi phí cộng dồn theo mỗi lần onboard và mỗi lần sửa lỗi
**Phạm vi:** ứng dụng mới `partner-app/` + mở rộng `backend/` + mở rộng `admin/` + **di cư 5 đối tác đang hoạt động theo 4 đợt**

---

## Document Overview

Mỗi lần onboard một đối tác, hệ thống sinh thêm một bản sao frontend độc lập. Tài liệu này đặc tả `partner-app/` — ứng dụng frontend hợp nhất, vận hành đa người thuê với cấu hình đọc lúc chạy — và lộ trình di cư 5 đối tác đang hoạt động.

### Phạm vi được thu hẹp — chốt 04/09

Repository chứa 15 thư mục frontend, nhưng **chỉ 5 đối tác còn hoạt động**: `hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`. Mười thư mục còn lại (`anker`, `flamingo`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `wildrift`, `yody`, `frontend`) thuộc đối tác đã ngừng. Tài liệu này **chỉ nói về 5 đối tác đang hoạt động**; mười thư mục kia không nằm trong phạm vi và **không bị đụng tới**.

Năm đối tác này tình cờ là cụm đồng nhất nhất trong repository — cùng hồ sơ phân hệ KYC đầy đủ, và không đối tác nào có màn hình hình dạng riêng ngoại trừ hai màn affiliate của `fecredit`.

### Nguyên tắc

**Nhận diện thương hiệu là dữ liệu, không phải mã nguồn.** Mọi khác biệt giữa 5 bản hiện hành phải nằm trong một bản ghi cấu hình đọc lúc chạy.

**Backend hỗ trợ đa người thuê ở tầng phân giải; không viết lại.** `PartnerRaw.AllowDomains` và `GetDetailByDomain` đã phục vụ production.

**`creator-os` là tài liệu tham khảo thiết kế, không phải nguồn mã.** Kế thừa mô hình và bài học vận hành (mục 2.3), không nhập mã nguồn, không tạo phụ thuộc chéo repository.

**Một triển khai duy nhất, phân giải người thuê theo `Host`.** Năm tên miền hiện hành đều kết thúc trên hạ tầng nội bộ (`SSH_HOST_{env}` — một máy chủ mỗi môi trường; `Dockerfile.release` và `nginx/` đồng nhất).

**Không có phép tính màu trong đường chạy.** Kế thừa trực tiếp từ `creator-os`: trạng thái hover và active dùng **độ mờ của cùng một token**, không dùng màu dẫn xuất. Chi tiết mục 2.4.

**Cấu hình thiếu phải báo lỗi, không được rơi về giá trị của đối tác khác.** Đây là nguyên tắc rút từ 5 lỗi thực tế đang chạy trên production (mục 2.6).

**Đánh số yêu cầu bằng tiền tố `PC-`.**

**Related Documents:**
- Báo cáo khảo sát: `ambassador/plans/reports/research-260903-1718-partner-config-admin-tham-khao-creator-os.md`
- Kế hoạch triển khai: `ambassador/plans/260904-1522-partner-app/plan.md`
- **Quy trình onboard đang dùng thật:** `ambassador/fecredit/setup.md` (149 dòng) và `ambassador/parasola/setup.md` — checklist do người thực hiện viết, nguồn từ Google Sheet *"Onboard FEC checklist - Golive"*. Mục 2.7 và PC-014 dựng trên khung này
- Thiết kế tham khảo: `pmax/creator-os` — `docs/architecture/05-theme-and-portals.md`, `packages/theme/src/tokens.ts`, `packages/ui/src/button.tsx`

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Đối tác đang hoạt động** | `hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`. Phạm vi duy nhất của tài liệu này |
| **`partner-app/`** | Ứng dụng hợp nhất được đặc tả tại đây. Một codebase, một triển khai |
| **Cấu hình ứng dụng** (`PartnerAppConfig`) | Bản ghi chứa toàn bộ khác biệt giữa các đối tác |
| **Design token** | Giá trị cấu hình giao diện, ánh xạ thành CSS custom property khi kết xuất phía máy chủ |
| **Section** | Khối nội dung trên trang chủ. Trang chủ là mảng có thứ tự các section |
| **Section catalogue** | Danh mục loại section hợp lệ. Định nghĩa nằm trong mã nguồn, không nằm trong cơ sở dữ liệu |
| **Đợt di cư** | Nhóm đối tác chuyển sang `partner-app/` cùng lúc. Bốn đợt (mục 6) |
| **Chạy song song** | Giai đoạn đối tác đã chuyển nhưng ứng dụng cũ vẫn sẵn sàng khôi phục |
| **Cutover** | Thời điểm chuyển lưu lượng của một tên miền sang `partner-app/` |
| **Bảy tầng onboard** | Toàn bộ chuỗi việc để một đối tác mới có site chạy được (mục 2.7) |

---

## 1. Executive Summary

Mô hình một-đối-tác-một-codebase tạo hai loại chi phí đo được:

```
Sửa một lỗi ở tầng dùng chung  →  phải áp dụng lại tại 4 vị trí khác
                               →  hoặc bỏ sót, dẫn tới phân kỳ hành vi
Onboard một đối tác            →  sao chép ~25.000 LOC, dựng pipeline, dựng image, triển khai
```

Chi phí đã hiện thực hoá — nội dung commit trong repository ghi trực tiếp: `d25209fcc docs(budget-alert): cảnh báo file có 14 bản sao, phải sửa đồng loạt`.

### Mức trùng lặp cho phép hợp nhất với chi phí thấp

Băm nội dung đường dẫn `.ts`/`.tsx`/`.scss` trên **5 đối tác đang hoạt động** (loại trừ `.umi`):

| Số phiên bản của cùng một đường dẫn | Số tệp |
|---|---|
| 1 — đồng nhất trên cả 5 | **246 (69%)** |
| 2 | 45 |
| 3 | 22 |
| 4 | 24 |
| 5 — phân kỳ thực sự | **22 (6%)** |
| **tổng** | **359** |

**18/21 màn hình có ở cả 5 đối tác.** Chỉ 3 màn lệch: `contract` (4/5, `vpbank` không có), `affiliate-campaign-detail` và `affiliate-commission` (chỉ `fecredit`).

Và trong 157 biến SCSS của hệ thiết kế, **152 giống hệt nhau ở cả 5 đối tác**. Khác biệt giao diện thực chất gói trong **một biến `$primary`**, cộng ba biến gradient riêng của `fecredit`.

---

## 2. Bối cảnh

### 2.1 Hiện trạng — đã đối chiếu mã nguồn

**Hạ tầng đã đồng nhất.** Tập dependency trùng khớp (`umi ^3.5.20`, `react 16`, 43 dependency). Trong 23 biến môi trường, **14 giống hệt ở cả 5** — `API_ENDPOINT`, `CLIENT_ID`, `TIKTOK_CLIENT_ID`, toàn bộ `FB_*`, `ORIGIN`, `SSO_*`. Chín biến còn lại là khác biệt thật:

```
COMMON_PARTNER · APP_NAME · NEXT_PUBLIC_ORIGIN
SUPPORT_ARTICLE_ID · QA_ARTICLE_ID · TERM_ID · CONDITION_ID
DOCUMENT_SHARE_LINK (lusso, parasola) · ACCESSTRADE_PARTNER_ID (parasola)
```

**Phân kỳ ở tầng lõi là hệ quả sao chép:** `configs/api.ts` (`hdbank` ↔ `vpbank`) khác biệt duy nhất ở **thứ tự khai báo**; `services/user.ts` (`hdbank` ↔ `parasola`) **trùng khớp hoàn toàn**; `wrappers/home.tsx` có 5 phiên bản nhưng toàn bộ là chuỗi nhận diện thương hiệu.

**Nền tảng frontend đã hết vòng đời hỗ trợ.** Cả 5 ứng dụng build trên `node:14.17.3` (kết thúc hỗ trợ 04/2023) kèm `node-sass ^4.9.0`. Backend không nằm trong tình trạng này: Go 1.24, Echo v4, mongo-driver 1.11.

### 2.2 Năm ứng dụng là bản sao của cùng một ứng dụng đa người thuê

**Phía backend** đã có đủ tầng phân giải:

| Thành phần | Vị trí |
|---|---|
| `PartnerRaw.AllowDomains []string` | `internal/model/mg/partner.go:51` |
| `GetDetailByDomain`, `GetListPartnersByDomain` | `pkg/public/service/partner.go:40-88` |
| Truy vấn public giới hạn theo `query.Domain` | `pkg/public/service/partner.go:310` |
| Cache Redis theo tên miền, TTL 4 giờ | `pkg/public/service/partner.go:44-52` |
| Cờ tính năng theo đối tác (`PartnerOpts`) | leaderboard, `enableStaffCode`, `allowResubmitRejectedContent` |

**Phía frontend**, cả 5 ứng dụng đều có 10 tuyến `/:partner/…` và logic `isOwnerPartner`. Chế độ hiển thị do backend quyết định: `res.AllowHeaderPartner = len(res.Data) > 1` (`partner.go:376`). Khác biệt white-label nằm ở một chỉ thị điều hướng tại `pages/main-home/index.tsx` và 2–3 tham chiếu `COMMON_PARTNER`.

**Hai hệ quả:** `partner-app/` không cần xây cơ chế phân giải mới; và **cấu trúc URL `/<partner>/<slug>` giữ nguyên sau di cư** — không phát sinh bảng chuyển hướng, không gián đoạn chỉ mục tìm kiếm.

### 2.3 Bài học kế thừa từ `creator-os` — ràng buộc thiết kế bắt buộc

**BH-1 — Bố cục cố định dẫn tới dữ liệu giả. Ràng buộc: PC-005.**
*"template cố định ⇒ section không có dữ liệu VẪN phải render ⇒ đẻ ra dữ liệu GIẢ để lấp chỗ trống"*. Hệ quả tại hệ thống đó là hằng `MOCK_QUOTES` — nội dung chứng thực tạo giả gắn vào tên và ảnh người dùng có thật. Do đó trang chủ là **mảng có thứ tự các section**, loại trừ mô hình chọn một trong N bố cục.

**BH-2 — Section catalogue thuộc mã nguồn. Ràng buộc: PC-005.**
*"Nếu để schema section trong DB → 2 nguồn sự thật + mất guardrail whitelist"*.

**BH-3 — Nâng "chất" của thiết kế lên thành token. Ràng buộc: PC-002.**
*"Cái làm nên brutalist lại nằm ở chỗ khác — micro-label viết hoa giãn chữ, và kẻ ngang thay cho card"*. Với 5 đối tác hiện tại, đo được cả 5 dùng giá trị y hệt ở mọi trục ngoài `$primary`, nên **các token này giữ compile-time**; mở ra cấu hình khi có đối tác đầu tiên thực sự cần.

**BH-4 — Điều hướng sinh từ `sections[]`. Ràng buộc: PC-005.**
*"Xoá section thì mục nav tự biến mất ⇒ không bao giờ có anchor chết"*.

**BH-5 — Component đọc token, không đọc giá trị. Ràng buộc: NFR-010.**
`packages/ui/src/button.tsx` ghi rõ: *"Mọi màu qua TOKEN → tenant override runtime được"*, *"`rounded-lg` map về `var(--radius)` → preset radiusBase 0 tự ra góc vuông, KHÔNG cần variant riêng. Đừng đổi thành `rounded-[8px]`"*, *"Cùng 1 variant, khác nhau do TOKEN — KHÔNG fork component"*.

**Bài học bổ sung, ràng buộc PC-007:** khoá cache frontend phải trùng khớp tuyệt đối với backend; sai lệch dẫn tới *"purge im lặng không trúng gì cả: publish xong trang vẫn cũ, không ai thấy lỗi"*.

### 2.4 Quyết định kỹ thuật: loại bỏ phép tính màu khỏi đường chạy

Bootstrap 5.2.3 sinh **hai kiểu output** từ `$primary`, và chỉ một kiểu đổi được lúc chạy:

```scss
// _root.scss:16-21 — phát ra BIẾN CSS, ghi đè runtime được
--#{$prefix}#{$color}: #{$value};        // --bs-primary
--#{$prefix}#{$color}-rgb: #{$value};    // --bs-primary-rgb

// mixins/_buttons.scss:22-25 — phát ra HẰNG SỐ hex
--#{$prefix}btn-bg: #{$background};
--#{$prefix}btn-hover-bg: #{$hover-background};   // = shade-color($bg, 15%), tính lúc BIÊN DỊCH
--#{$prefix}btn-color: #{$color};                 // = color-contrast($bg), tính lúc BIÊN DỊCH
```

Đo trên 5 đối tác, các class phụ thuộc `$primary`:

| Nhóm | Lượt dùng | Xử lý |
|---|---:|---|
| `text-primary` 173 · `border-primary` 36 · `bg-primary` 11 | **220** | Đọc `var(--bs-primary-rgb)` — ghi đè biến là xong |
| `btn-primary` 81 · `btn-outline-primary` 9 | **90** | Bootstrap sinh hằng số + màu dẫn xuất compile-time |

**Giải pháp — kế thừa `creator-os`:** thay màu dẫn xuất bằng **độ mờ của cùng token**.

```tsx
// packages/ui/src/button.tsx, creator-os
primary: 'bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80'
```

Hover và active không phải màu mới — là chính token đó ở độ mờ 90% và 80%, trình duyệt hợp thành lúc chạy. Chỉ màu chữ tương phản (`primaryForeground`) là token khai tường minh, vì độ mờ không giải được bài toán tương phản.

**Hệ quả:** không có `shade-color`, `tint-color`, `color-contrast` ở bất kỳ đâu trong hệ thống mới. Không có phép toán nào để nhân đôi giữa backend và frontend. Cấu hình màu của một đối tác là **hai trường**: `primary` và `primaryForeground`.

*Lưu ý:* bổ ngữ độ mờ của Tailwind v4 hiện thực bằng `color-mix()`, yêu cầu Chrome 111+ / Safari 16.2+. Đây là cơ chế mặc định của framework, không phải thủ thuật riêng.

### 2.5 Phân kỳ giữa 5 đối tác — cơ sở cho lộ trình

Khoảng cách từng cặp (số tệp khác biệt trên `src/**`):

```
           hdbank   lusso  parasola  vpbank  fecredit
hdbank         ·      45      69       99      131
lusso         45       ·      57      107      126
parasola      69      57       ·      112      118
vpbank        99     107     112        ·      154
fecredit     131     126     118      154        ·
```

**Hồ sơ cấu hình thật** — đây là dữ liệu khởi tạo cho di cư:

| | hdbank | lusso | parasola | vpbank | fecredit |
|---|---|---|---|---|---|
| slug | `hdbank` | `lussosaigon` | `parasola` | `vpbank` | `fecredit` |
| tên miền | creator.hdbank.com.vn | megalive.lussosaigon.vn | parasola-creator.com | vpbank.koc.com.vn | ambassador.fecredit.com.vn |
| `$primary` | `#FAA61A` | `#066A9D` | `#EE5799` | `#005baa` | `#00994F` |
| phông chữ | BeVietnamPro | BeVietnamPro | Rosellinda | SVN-Gilroy | FE Font |
| phân hệ `contract` | ● | ● | ● | — | ● |
| phân hệ `affiliate` | — | — | — | — | ● |
| token riêng | — | — | — | — | 3 gradient |

**Ảnh:** 20 khoá trên 5 app, chỉ **5 khoá có ở cả 5** (`logoImage`, `logoMobileImage`, `logoBrandFooter`, `decorLeft`, `decorRight`). 15 khoá còn lại là ảnh mốc thưởng có ở 4/5 hoặc 1/5. Do đó `assets` phải là **map có bộ lõi bắt buộc**, không phải danh sách trường cố định.

### 2.6 Năm lỗi đang chạy trên production — phải sửa trước, ngoài phạm vi tài liệu này

Phát hiện trong quá trình khảo sát. Không do việc hợp nhất tạo ra; cần xử lý như task độc lập, là tiền đề của E2.

**PRE-1 — Điều hướng mở ở luồng uỷ quyền TikTok. Quyết định: GIỮ NGUYÊN (04/09).**
`login-tiktok/index.tsx:14` và `connect-tiktok/index.tsx:12` dùng tham số `state` do bên gọi cung cấp làm đích điều hướng, không kiểm danh sách cho phép. Backend cũng không giới hạn `redirectURI` (`internal/module/social/tiktok/tiktok.go:113`); tìm `allowlist|whitelist|validateRedirect` trên `backend/internal` và `backend/pkg` không có kết quả. Quét toàn bộ nhánh remote 04/09: không nhánh nào có bản vá.

**Quyết định 04/09: `partner-app` port nguyên luồng hiện tại, không thay đổi.** Ghi nhận đây là **quyết định giữ nguyên hiện trạng**, không phải kết luận đã kiểm tra và thấy an toàn — hai câu đó khác nhau và tài liệu này không có căn cứ cho câu thứ hai.

**PRE-2 — Giá trị dự phòng cứng trỏ tới bài viết pháp lý của đối tác khác.**
```js
termId      = process.env.TERM_ID       || '68254accdc42a0356265318c'   // bài viết của HDBank
conditionId = process.env.CONDITION_ID  || '68254a8ddc42a0356265318a'   // bài viết của HDBank
qaArticleId = process.env.QA_ARTICLE_ID || '682549b7dc42a03562653188'   // bài viết của HDBank
```
Có ở `hdbank`, `lusso`, `parasola`. Đối tác quên khai một biến sẽ **hiển thị điều khoản và điều kiện của HDBank**. `fecredit` đã đổi thành `|| ''`, `vpbank` gỡ hẳn ba biến.

**PRE-3 — Dữ liệu của HDBank đang chạy trên site của đối tác khác.**

| Vị trí | Nội dung |
|---|---|
| `lusso/components/app/image/constants.ts:53-55` | Facebook, TikTok, YouTube — **toàn bộ là kênh của HDBank** |
| `lusso/configs/app.ts:65-68` | Liên kết tải app HDBank, kèm điều kiện `if (slug === 'thehdbank')` |
| `lusso/pages/home/components/not-logged-in/index.tsx:569` | Điều kiện UI dựa trên slug chiến dịch của HDBank |
| `lusso/pages/contact/index.tsx:75,77` | `info@hdbank.com.vn` |
| `parasola/pages/contact/index.tsx` | Hotline `1900 6060` của HDBank |

**PRE-4 — Thẻ canonical trỏ sai tên miền ở cả 5 ứng dụng.**
`wrappers/home.tsx` gán `url: process.env.ORIGIN`, trong khi `ORIGIN = https://ambassador.koc.com.vn/` ở cả 5; giá trị này dùng cho `<link rel="canonical">` và `og:url`. Nguyên nhân là nhầm giữa `ORIGIN` (tên miền callback dùng chung) và `NEXT_PUBLIC_ORIGIN` (tên miền đối tác).

**PRE-5 — Trạng thái toàn cục theo request tại tầng SSR.**
`server.js:25-26` gán `global._cookies` và `global._navigatorLang` trên tiến trình dùng chung. Hiện không nơi nào đọc, nên chưa gây hậu quả. Cần loại bỏ trước khi hợp nhất.

### 2.7 Bảy tầng của một lần onboard — bối cảnh cho phạm vi thực tế

Trace luồng khởi động thật của ứng dụng cho thấy onboard một đối tác không phải một biểu mẫu, mà là chuỗi việc qua 8 màn admin và 5 hệ thống bên ngoài:

| Tầng | Nội dung | Cấu hình hoá được? |
|---|---|---|
| **0. Ngoài hệ thống** | DNS · TLS · **Google Cloud Console** (JS origin) · **ACCESSTRADE SSO** (redirect URI) | **Không**, trừ khi làm PC-011. **TikTok không cần gì** — đã giải xong bằng callback dùng chung. Facebook đã tắt |
| **1. Bản ghi nền** | `admin/partner`: name, slug, logo, website, `allowDomains`, status, bpp | Đã có form; **thiếu chẩn đoán** — xem PC-014 |
| **2. Bốn bài viết** | Điều khoản · Điều kiện · Câu hỏi thường gặp · Bài hỗ trợ | **Không.** Phải có người soạn. Đây là đường găng dài nhất theo thời gian thực tế |
| **3. Cấu hình ứng dụng** | theme, assets, contact, social, seo, modules, sections | **Có** — phạm vi chính của tài liệu này |
| **4. Dữ liệu vận hành** | Category → Event (bắt buộc `Name`, `Code`, cặp ngày) · quick-action · news | Đã có form |
| **5. Cờ nghiệp vụ** | leaderboard · staff code (+ `manage-code` nếu bật) · ngưỡng tự duyệt creator · resubmit | Đã có form |
| **6. Nhân sự** | `admin/staff` gắn với đối tác, để duyệt nội dung | Đã có form |
| **7. Kiểm chứng** | Đăng nhập TikTok thật → nộp bài thật → đi hết 18 màn | — |

**Kết luận về giá trị dự án:** cấu hình hoá rút ngắn **tầng 3**, không rút ngắn cả luồng. Thời gian onboard thực tế bị chặn bởi tầng 2 và tầng 0. Lợi ích thật nằm ở chỗ tầng 3 hôm nay tốn một đợt việc của dev cộng một lần deploy, và mỗi bản sửa lỗi phải nhân ra 5 nơi.

**Bẫy phát hiện ở tầng 1:** thiếu hoặc sai `allowDomains` dẫn tới vòng lặp chuyển hướng vô tận, không thông báo:
```
getDetailPartner lỗi → navigator.replacePath('/')          models/main.ts:230
'/'                  → <Redirect to={`/${COMMON_PARTNER}`} />   main-home:4
'/<slug>'            → getDetailPartner lỗi → '/' → …
```

### 2.8 Trạng thái chất lượng mã nguồn hiện tại

Đo trên 1.333 tệp `.ts`/`.tsx` của 5 ứng dụng:

| Chỉ số | Tổng | Mỗi ứng dụng |
|---|---:|---|
| `tsc --noEmit --skipLibCheck` — lỗi trong mã của app | **0** | 0 |
| `console.log` còn sót | 144 | ~29 |
| `any` / `@ts-ignore` | 1.474 | ~290 |
| Khối JSX bị comment | 359 | 53–111 |
| Dòng mã bị comment | 421 | ~85 |
| `catch` nuốt lỗi | 5 | 1 |

**Mã nguồn sạch về kiểu; cổng gác thì hỏng.** Không ứng dụng nào chạy được `tsc` vì thiếu `skipLibCheck: true` — trình biên dịch dừng ở tệp `.d.ts` của dependency. Đây là sửa một dòng, và nó mở lại cổng gác kiểu cho cả 5.

Backend: **149 phát hiện `go vet`** (phần lớn là `bson.E` không đặt tên trường và khoảng trắng trong struct tag), **9 gói test PASS, 0 FAIL**.

### 2.9 Ngoài phạm vi bổ sung

- Không trình dựng trang tự do; section là danh mục đóng có schema
- Không cho nhập CSS hoặc JavaScript thô
- Không đa ngôn ngữ (`src/locales` đã đồng nhất 167 dòng ở cả 5 — không cần hoà giải)
- Không thay đổi mô hình `PartnerRaw`; chỉ bổ sung collection mới
- **Không có cơ chế slot override.** Năm đối tác hiện tại không có màn hình hình dạng riêng; `affiliate` của `fecredit` là phân hệ bật/tắt. Xây registry cho zero consumer là vi phạm YAGNI. Trường `slots` giữ chỗ trong lược đồ, chưa hiện thực

---

## 3. User Personas

**P1. Đội vận hành** — người dùng chính của màn hình cấu hình, **không phải kỹ sư**. Phải hoàn thành tầng 3 mà không cần hỗ trợ, và sai thì khôi phục được.

**P2. Pháp chế và marketing của đối tác** — chủ sở hữu bốn bài viết ở tầng 2 và nội dung trang chủ. Đây là đường găng dài nhất của một lần onboard.

**P3. Kỹ sư frontend** — hiện mất một đợt việc cho mỗi lần onboard, đồng thời nhân bản mỗi bản sửa lỗi ra 5 vị trí. Sau khi hoàn tất, chỉ tham gia khi có yêu cầu vượt ngoài lược đồ cấu hình.

**P4. Kỹ sư backend** — bổ sung một collection và bốn nhóm endpoint. Không đụng gate, sổ cái, logic tính thưởng.

**P5. Người dùng hiện hữu của 5 đối tác** — **đối tượng chịu tác động trực tiếp.** Ràng buộc: không mất phiên đăng nhập, không đứt liên kết, không suy giảm chức năng. Điều kiện thuận lợi đã xác nhận: `authToken` lưu tại `localStorage` theo origin (`utils/storage.ts:10,31`), mỗi tên miền giữ nguyên origin sau khi chuyển, nên **phiên đăng nhập không bị ảnh hưởng**.

**P6. DevOps** — tầng 0. Mỗi tên miền mới cần DNS, chứng chỉ, và ba lần đăng ký OAuth thủ công cho tới khi PC-011 hoàn tất.

---

## 4. Functional Requirements

### PC-001: Phân giải người thuê theo `Host`

**Priority:** Must Have — nền tảng cho mọi yêu cầu còn lại

**Vì sao cần.** Cả 5 ứng dụng đã có 10 tuyến `/:partner/…` và logic `isOwnerPartner`; chế độ hiển thị do backend quyết bằng `res.AllowHeaderPartner = len(res.Data) > 1` (`pkg/public/service/partner.go:376`). Khác biệt white-label chỉ nằm ở một chỉ thị điều hướng. Nên `partner-app/` **không xây cơ chế phân giải mới** — nó bỏ `COMMON_PARTNER` và đọc cờ backend đã trả.

| Điều kiện | Kết quả |
|---|---|
| `Host` phân giải ra đúng một đối tác | White-label: ẩn bộ chuyển, `/` chuyển hướng tới `/<slug>` |
| `Host` phân giải ra nhiều đối tác | Đa đối tác: hiện bộ chuyển |
| `Host` không phân giải được đối tác nào | **Trang lỗi nêu rõ tên miền chưa đăng ký.** Không chuyển hướng |
| `PARTNER_SLUG` có giá trị | Ghi đè `Host` — môi trường phát triển |

**URL giữ nguyên `/<partner>/<slug>`.** Cả 5 ứng dụng đã dùng cấu trúc này, nên di cư không đứt liên kết và không cần bảng chuyển hướng.

#### ⚠️ Nhánh thứ ba là bắt buộc — hệ cũ rơi vào vòng lặp câm

Sai `allowDomains` hôm nay cho ra vòng lặp vô tận, không thông báo gì:

```
getDetailPartner lỗi → navigator.replacePath('/')            models/main.ts:230
'/'                  → <Redirect to={`/${COMMON_PARTNER}`} />     main-home/index.tsx:4
'/<slug>'            → getDetailPartner lỗi → '/' → …
```

Người onboard không biết mình sai ở đâu. `partner-app/` **cấm chuyển hướng khi không phân giải được đối tác** — phải dừng lại và nói ra.

**AC:**
- [ ] Hai tên miền trên cùng container trả hai bộ nhận diện khác nhau
- [ ] `Host` lạ hiện trang lỗi nêu tên miền chưa đăng ký; **không** có chuyển hướng nào
- [ ] `PARTNER_SLUG` ghi đè `Host`, có unit test cả hai nhánh
- [ ] `grep COMMON_PARTNER partner-app/src` trả về 0 kết quả
- [ ] Danh sách tuyến sau di cư trùng khớp trước di cư

---

### PC-002: Giao diện điều khiển bằng token

**Priority:** Must Have

**Vì sao chỉ hai màu.** Đo 157 biến SCSS của hệ thiết kế trên 5 đối tác: **152 biến giống hệt nhau**. Năm biến khác gồm `$modal-inner-padding` (chỉ khác khoảng trắng) và ba biến gradient riêng của `fecredit`. Khác biệt giao diện thật gói trong **một biến `$primary`**.

**Token cấu hình được:**

```
primary             mã hex
primaryForeground   mã hex — màu chữ trên nền primary
fontFamily          tên họ phông
fontFiles[]         { family, weight, style, url }
colorsExtra{}       map mở — hiện chỉ fecredit dùng
```

**152 biến còn lại giữ compile-time** trong `partner-app`. Đưa lên admin chỉ tạo 152 ô để gõ sai mà chưa ai từng cần đổi.

#### ⚠️ KHÔNG có phép tính màu ở bất kỳ đâu

Bootstrap 5.2.3 tính hover và active **lúc biên dịch** bằng hàm SCSS, không thể chạy trong trình duyệt:

```scss
// mixins/_buttons.scss:22-25 — phát ra HẰNG SỐ hex
--#{$prefix}btn-hover-bg: #{$hover-background};  // = shade-color($bg, 15%)
--#{$prefix}btn-color:    #{$color};             // = color-contrast($bg)
```

Đo được 90 lượt dùng `btn-primary` và `btn-outline-primary` trên 5 đối tác — nếu giữ Bootstrap thì phải viết lại ba hàm này bằng Go hoặc TypeScript, và bản viết lại sẽ lệch so với bản đang chạy.

**Không làm vậy.** Kế thừa `packages/ui/src/button.tsx` của `creator-os`:

```tsx
primary: 'bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80'
```

Hover và active **không phải màu mới** — là chính token đó ở độ mờ giảm, trình duyệt hợp thành lúc chạy. Chỉ `primaryForeground` khai tường minh, vì độ mờ không giải được bài toán tương phản chữ.

Hệ quả: không có `shade-color`, `tint-color`, `color-contrast` ở đâu cả. Không có phép toán nào để nhân đôi giữa backend và frontend, nên **không cần thư viện dùng chung** cho việc này.

**Không nhấp nháy.** CSS variable ghi vào thuộc tính `style` của `<html>` khi kết xuất phía máy chủ.

**AC:**
- [ ] Đổi `primary`, xuất bản, tải lại: giao diện đổi, không build lại
- [ ] `grep -rE "#[0-9a-fA-F]{6}" partner-app/src` (trừ tệp token) trả về **0**
- [ ] `grep -rE "shade-color|tint-color|color-contrast"` trên toàn repo trả về **0**
- [ ] Tải trang throttle 3G không thấy nhấp nháy màu mặc định
- [ ] Nút hover có màu là `primary` ở độ mờ giảm — xác nhận bằng DevTools

---

### PC-003: Tài nguyên theo đối tác, gồm phông chữ

**Priority:** Must Have

**Vì sao `assets` là map chứ không phải danh sách trường.** Đo 20 khoá ảnh trên 5 đối tác: **chỉ 5 khoá có ở cả 5** (`logoImage`, `logoMobileImage`, `logoBrandFooter`, `decorLeft`, `decorRight`). 15 khoá còn lại là ảnh mốc thưởng, có ở 4/5 hoặc 1/5. Khai cứng 20 trường thì đối tác thứ sáu cần khoá thứ 21 lại phải sửa lược đồ.

**Bộ lõi bắt buộc:** 5 khoá trên, cộng `favicon` và `ogImage`.
**Map mở:** phần còn lại.

**Phông chữ là tài nguyên, không phải chuỗi CSS.** Bốn họ phông khác nhau trên 5 đối tác:

```
BeVietnamPro (hdbank, lusso) · Rosellinda (parasola) · SVN-Gilroy (vpbank) · FE Font (fecredit)
```

Nên admin phải cho **tải lên tệp phông**, và ứng dụng sinh `@font-face` theo đối tác lúc chạy. Token `fontFamily` một mình không đủ.

**Lưu trữ:** MinIO qua service `file` hiện có.

**Kiểm URL:** nhận `http(s)://…` hoặc đường dẫn nội bộ bắt đầu bằng `/`. **Chặn** `//host` (protocol-relative — thoát khỏi origin) và mọi scheme khác (`javascript:`, `data:`).

**AC:**
- [ ] Đổi logo, xuất bản: giao diện cập nhật, không build lại
- [ ] Tài nguyên thiếu dùng mặc định của ứng dụng, không vỡ bố cục
- [ ] `javascript:` và `//evil.com` bị từ chối tại **máy chủ**, không chỉ ở form
- [ ] Tải tệp phông: `@font-face` sinh đúng, chỉ áp cho đối tác đó
- [ ] Phông chuyển sang `woff2` trong quá trình di cư

---

### PC-004: Bật/tắt phân hệ

**Priority:** Must Have

**Vì sao chỉ hai cờ.** 18/21 màn có ở cả 5 đối tác. Chỉ ba màn lệch:

```
contract   → hdbank ✓ lusso ✓ parasola ✓ fecredit ✓   vpbank ✗
affiliate  → fecredit ✓ (2 màn)                        4 đối tác còn lại ✗
```

Tắt cờ phải **ẩn khỏi điều hướng VÀ chặn tại tuyến**, không chỉ ẩn menu — gõ thẳng URL cũng không vào được.

**Lỗi mềm.** Tải cấu hình thất bại thì dùng bộ mặc định an toàn, **không** trả trang trắng. Mặc định an toàn = bật nhóm lõi, tắt phân hệ tuỳ chọn.

**`PartnerOpts` giữ nguyên chỗ cũ.** Các cờ leaderboard, `enableStaffCode`, `allowResubmitRejectedContent` không di chuyển trong suốt giai đoạn chạy song song — ứng dụng chưa di cư vẫn đang đọc chúng ở vị trí hiện tại.

**AC:**
- [ ] Tắt `contract`: mục biến khỏi nav **và** gõ URL trực tiếp bị chặn
- [ ] API cấu hình lỗi: ứng dụng vẫn kết xuất với bộ cờ mặc định
- [ ] `PartnerOpts` giữ nguyên tên trường và vị trí; ứng dụng chưa di cư đọc được như trước

---

### PC-005: Trang chủ dựng bằng section catalogue

**Priority:** Must Have

**Vì sao là mảng chứ không phải template.** `creator-os` đã trả giá cho bài này: *"template cố định ⇒ section không có dữ liệu VẪN phải render ⇒ đẻ ra dữ liệu GIẢ để lấp chỗ trống"*. Bằng chứng bên họ là hằng `MOCK_QUOTES` — lời chứng thực bịa gán vào tên và ảnh đại diện của người dùng **có thật**. Ở mô hình mảng, đối tác không thêm block thì block đó không tồn tại; hết ô trống để bịa.

**Danh mục** — suy từ tập component mà cả 5 đối tác dùng chung ở `pages/partner-home`:

| Loại | Phân loại | Bắt buộc | Lặp | Lên nav |
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

**Section `dữ liệu` chỉ lưu tham số truy vấn.** `events` lưu `limit`, **không** lưu danh sách chiến dịch. Sao chép dữ liệu vào cấu hình là tự tạo bản cũ không ai cập nhật.

**Điều hướng sinh từ `sections[]`.** Không có bảng nav riêng, nên xoá section là mục nav tự mất — không bao giờ có anchor chết.

**`key` bền vững.** Sửa và sắp xếp địa chỉ hoá theo `key`, **không theo chỉ số mảng**. Sắp lại thứ tự không được làm hỏng bản sửa đang chờ.

#### ⚠️ Danh mục nằm trong mã nguồn, KHÔNG nằm trong DB

Để trong DB là **hai nguồn sự thật**, và mất hàng rào whitelist — đối tác tự chế được loại block mới. MongoDB chỉ lưu mảng `sections`; luật kiểm nằm ở tầng ứng dụng và **cưỡng chế ở server**, không chỉ ẩn nút xoá trên giao diện.

**AC:**
- [ ] Kéo đổi thứ tự, xuất bản: trang chủ đổi thứ tự
- [ ] Tắt `leaderboard`: khối **và** mục nav cùng biến mất
- [ ] Gọi thẳng API xoá section `hero`: máy chủ từ chối
- [ ] Gửi `type` ngoài danh mục: máy chủ từ chối, không ghi vào DB
- [ ] Sắp lại thứ tự rồi sửa một section: sửa đúng section đó

---

### PC-006: SEO, OpenGraph, GTM, `robots.txt`, `sitemap.xml`

**Priority:** Must Have

Lấy từ cấu hình: `title`, `description`, `keywords`, `ogImage`, `gtmId`.

#### ⚠️ Canonical sinh từ `Host`, KHÔNG từ hằng số môi trường

Cả 5 ứng dụng hiện đang khai sai. `wrappers/home.tsx` gán `url: process.env.ORIGIN`, mà `ORIGIN = https://ambassador.koc.com.vn/` ở **cả 5**:

```html
<!-- đang render trên creator.hdbank.com.vn, parasola-creator.com, … -->
<link rel="canonical" href="https://ambassador.koc.com.vn/">
<meta property="og:url"  content="https://ambassador.koc.com.vn/">
```

Nguyên nhân: **`ORIGIN` gánh hai vai.** Comment ngay trong `fecredit/config/config.prod.ts` nói rõ: *"Domain API, không phải domain FE (dùng cho canonical/og:url + redirect TikTok)"*. Một biến vừa là tên miền callback dùng chung — **đúng cho TikTok** — vừa là tên miền chuẩn hoá SEO — **sai cho canonical**.

#### ⚠️ KHÔNG sửa canonical bằng cách đổi giá trị `ORIGIN`

Đổi `ORIGIN` sẽ **phá luồng đăng nhập TikTok của cả 5 ứng dụng**, vì `redirect_uri` gửi TikTok dựng từ chính biến đó và đã đăng ký một lần dùng chung.

Cách đúng là **tách hai vai**: `canonical` và `og:url` sinh từ `Host` của request; `ORIGIN` giữ nguyên giá trị, chỉ còn phục vụ callback TikTok. **`canonical` không lưu trong lược đồ.**

**`robots.txt` và `sitemap.xml` sinh theo tên miền.** Hiện không ứng dụng nào có hai tệp này; đây là năng lực mới, không phải hạng mục chuyển đổi.

**AC:**
- [ ] Hai tên miền trả hai bộ thẻ meta khác nhau
- [ ] `canonical` và `og:url` trỏ về **chính tên miền đang truy cập**
- [ ] `gtmId` trống: không chèn script GTM
- [ ] `robots.txt` và `sitemap.xml` phản ánh đúng tên miền yêu cầu

---

### PC-007: Bản nháp — xem trước — xuất bản — khôi phục

**Priority:** Must Have

Hai trạng thái `draft` và `published`. Site công khai **chỉ đọc bản đã xuất bản**.

1. Sửa bản nháp — site không đổi
2. Xem trước — mở site thật với bản nháp qua token, **cùng hạ tầng**, không dựng riêng
3. Xuất bản — sinh phiên bản bất biến kèm changelog và người thực hiện; chuyển con trỏ; xoá cache
4. Khôi phục — trỏ con trỏ về phiên bản cũ, một thao tác, **không** đụng bản nháp đang sửa

#### ⚠️ Bốn cửa kiểm khi xuất bản, không phải khi lưu nháp

Người vận hành phải lưu được bản dở dang. Nhưng xuất bản thì chặn nếu:

| Cửa | Chặn cái gì |
|---|---|
| Token giao diện | thiếu `primary` hoặc `primaryForeground`, hoặc không phải mã hex |
| Section | thiếu `hero`/`events`, loại ngoài danh mục, `key` trùng hoặc rỗng |
| **Trường bắt buộc** | thiếu bất kỳ trong 7: `website`, `footerBrandLink`, `contact.hotline`, `contact.email`, 3 article ID |
| **Dữ liệu đối tác khác** | cấu hình chứa tên miền, hotline, email hoặc article ID đã đăng ký cho đối tác khác |

Hai cửa cuối là hàng rào cho lỗi **đang chạy trên production**: `lusso` dùng Facebook, TikTok, YouTube, link tải app và email của HDBank; `parasola` dùng hotline của HDBank; ba ứng dụng có giá trị dự phòng cứng trỏ tới bài viết pháp lý của HDBank (mục 2.6).

Khi di cư, cấu hình được **trích tự động từ chính các ứng dụng đó**. Không chặn ở bước xuất bản thì các giá trị sai theo sang hệ mới và trở thành dữ liệu chính thức — khó phát hiện hơn bây giờ.

**Trường bắt buộc không có giá trị mặc định và không kế thừa.** Nguyên nhân gốc của cả hai lỗi trên là các giá trị này được **thừa hưởng** chứ không được **hỏi**.

**Khoá cache khớp tuyệt đối** giữa frontend và backend. Lệch một ký tự thì purge không trúng gì cả — xuất bản xong trang vẫn cũ và **không ai thấy lỗi**. Bắt buộc có test đối chiếu hai phía.

**AC:**
- [ ] Sửa nháp: site công khai không đổi
- [ ] Link xem trước hiện bản nháp; mở ẩn danh không token thấy bản đã xuất bản
- [ ] Xuất bản: thay đổi có hiệu lực trong một lần tải lại
- [ ] Khôi phục: trạng thái về đúng như trước, bản nháp không bị đụng
- [ ] Xuất bản cấu hình chứa `info@hdbank.com.vn` cho đối tác khác HDBank: **từ chối**, thông báo nêu tên đối tác bị lẫn
- [ ] Xuất bản khi thiếu `contact.hotline`: từ chối, thông báo liệt kê **đủ** các trường thiếu, không dừng ở cái đầu tiên
- [ ] Có test đối chiếu khoá cache hai phía

---

### PC-008: Màn hình cấu hình trong admin

**Priority:** Must Have

Xây trong `admin/` hiện hành (umi 3 + antd 4), đặt cạnh biểu mẫu đối tác ở `admin/src/pages/partner/components/modal.tsx`. **Không dựng admin mới.**

| Nhóm | Nội dung |
|---|---|
| Nhận diện | tên, slug, tên miền, `primary`, `primaryForeground`, phông chữ |
| Tài nguyên | 7 khoá lõi + tệp phông + khoá mở rộng |
| Nội dung | 4 article ID, liên hệ, mạng xã hội, liên kết footer, liên kết tài liệu |
| SEO | title, description, keywords, GTM |
| Phân hệ | công tắc `contract`, `affiliate` |
| Trang chủ | danh sách section: thêm, xoá, sắp xếp, sửa nội dung |
| Xuất bản | xem trước, xuất bản kèm changelog, lịch sử phiên bản kèm khôi phục |
| Chẩn đoán tên miền | xem PC-014 |
| Danh sách kiểm onboard | xem PC-014 |

**Người dùng là P1, không phải kỹ sư.** Nhãn tiếng Việt rõ nghĩa; ô màu có bảng chọn chứ không bắt gõ hex trần; thông báo lỗi nói **sai gì và sửa thế nào**, không phải tên trường kỹ thuật.

**Nghiệm thu bằng một buổi làm thật, không phải đọc code.** P1 tạo và xuất bản một đối tác từ đầu tới cuối, không hỏi ai.

**AC:**
- [ ] P1 hoàn thành tạo và xuất bản một đối tác mà không cần hỗ trợ
- [ ] Mọi kiểm tra ở máy chủ đều có thông báo tương ứng trên biểu mẫu — không để lỗi trần lọt lên
- [ ] Ô màu xem được kết quả ngay trong admin
- [ ] Màn chẩn đoán cảnh báo khi một tên miền được khai ở nhiều đối tác

---

### PC-009: *(đã gỡ tại v1.2)*

Cơ chế slot override loại khỏi phạm vi. Sáu màn one-off từng ghi nhận — `agency`, `lp-store`, `mission`, `mission-detail`, `category-home`, `info` — **đều thuộc đối tác đã ngừng**. Trong 5 đối tác đang hoạt động không ai có màn hình hình dạng riêng; `affiliate` của `fecredit` là phân hệ bật/tắt, không phải slot.

Xây registry cho zero consumer là vi phạm YAGNI. Trường `slots` giữ chỗ trong lược đồ để không phải đổi cấu trúc khi cần, **không hiện thực**.

---

### PC-010: Vận hành song song và ngừng ứng dụng cũ

**Priority:** Must Have

| Giai đoạn | Ứng dụng cũ |
|---|---|
| Trước cutover | Đang phục vụ lưu lượng |
| Sau cutover, trong thời gian theo dõi | **Giữ nguyên image và cấu hình triển khai**, khôi phục bằng thao tác chuyển ingress |
| Sau nghiệm thu | Ngừng triển khai |

**Theo dõi tối thiểu hai tuần mỗi đợt.** Không xoá thư mục mã nguồn trước khi hết thời gian này.

Thay đổi backend giữ tương thích ngược suốt giai đoạn chạy song song — ứng dụng chưa di cư vẫn gọi cùng bộ endpoint.

**AC:**
- [ ] Mỗi đợt: khôi phục về ứng dụng cũ trong **dưới 15 phút**, có diễn tập trước cutover
- [ ] Hình dạng response của endpoint public giữ nguyên
- [ ] Không thời điểm nào có hai hệ cùng phục vụ một tên miền

---

### PC-011: Uỷ quyền OAuth trên nhiều tên miền

**Priority:** Should Have

**Vì sao cần.** Lời hứa "onboard không cần dev" đúng với TikTok, không đúng với hai nhà cung cấp còn lại:

| Nhà cung cấp | Cơ chế hiện tại | Thêm tên miền cần gì |
|---|---|---|
| **TikTok** | Một `redirect_uri` dùng chung + chuyển tiếp theo `state` | **Không gì cả** |
| Google | `@react-oauth/google`, `<GoogleLogin>` — render sống ở cả 5 app | Đăng ký Authorized JavaScript origin |
| ACCESSTRADE SSO | `redirectUri = ${NEXT_PUBLIC_ORIGIN}lien-ket-tai-khoan` | Đăng ký redirect URI |
| ~~Facebook~~ | import bị comment ở 4/5 app | **đã tắt, ngoài phạm vi** |

#### ⚠️ TikTok NGOÀI phạm vi yêu cầu này

Bằng chứng thực nghiệm: `fecredit` là app thêm gần nhất (24/08/2026), và `fecredit/setup.md` — checklist onboard **149 dòng**, chi tiết đến kích thước banner và mã màu viền thẻ KPI — **không nhắc TikTok một chữ**. Hai giá trị `ORIGIN` và `TIKTOK_CLIENT_ID` chép nguyên từ app trước.

Trong khi SSO thì được ghi chú thẳng trong `config.prod.ts:44`: *"Domain FE, sinh redirect_uri SSO — phải trùng giá trị đăng ký bên AccessTrade"*.

Cơ chế TikTok **giữ nguyên, không đụng** (PRE-1, quyết định 04/09). Yêu cầu này chỉ nói về Google và SSO.

**Hai đường xử lý, chọn một:**
- Áp mô hình callback dùng chung của TikTok cho Google và SSO — **kèm kiểm tra đích chuyển tiếp tại tầng máy chủ theo `allowDomains`**. Áp mà quên vế kiểm là nhân lỗ hổng ra ba chỗ thay vì một
- Hoặc giữ nguyên, và ghi hai thao tác thủ công **tường minh** vào quy trình onboard. Không hứa "0 thao tác" rồi để người làm tự phát hiện

**AC:**
- [ ] Quy trình onboard nêu rõ hai thao tác thủ công còn lại, hoặc chứng minh đã bỏ được
- [ ] Nếu áp mô hình callback dùng chung: đích chuyển tiếp kiểm tại **máy chủ** theo `allowDomains`; giá trị ngoài danh sách bị từ chối
- [ ] Luồng TikTok không thay đổi hành vi — đối chiếu trước/sau trên một tên miền thật

---

### PC-012: Hoà giải 5 biến thể về một

**Priority:** Must Have

22 tệp có đủ 5 phiên bản. Chia ba nhóm, và **chỉ nhóm ba mới đắt**:

| Nhóm | Tệp | Ai quyết |
|---|---|---|
| Chuyển thành cấu hình | `wrappers/home.tsx`, `configs/app.ts`, `configs/image.ts`, `bootstrap-custom.scss`, footer | Kỹ sư, ghi lý do trong commit |
| Trôi do sao chép | `configs/api.ts` (khác **thứ tự khai báo**, nội dung y hệt), `utils/helper.ts`, `app.tsx` | Kỹ sư, chọn bản đầy đủ nhất |
| **Khác biệt hành vi** | `not-logged-in`, `header`, `models/main.ts`, `interfaces/event.ts` | **Không có đáp án kỹ thuật** |

Nhóm ba: mỗi trường hợp phải có quyết định ghi nhận, nêu rõ **đối tác nào thay đổi hành vi** và hình thức xử lý. Đối tác bị ảnh hưởng phải được thông báo **trước** cutover, không phải sau.

Duy trì bảng theo dõi quyết định, cập nhật **cùng commit** với thay đổi mã nguồn — không cập nhật sau.

**AC:**
- [ ] Toàn bộ 22 tệp được phân loại và có quyết định ghi nhận
- [ ] Mọi trường hợp nhóm ba có xác nhận từ đối tác trước cutover
- [ ] Bảng theo dõi cập nhật cùng commit

---

### PC-013: Di cư và cutover theo đợt

**Priority:** Must Have

**Điều kiện vào cutover:**
- Cấu hình của đối tác đã khởi tạo và xuất bản ở staging
- Bộ ảnh đối chiếu trước/sau hoàn tất cho từng màn × từng đối tác (NFR-007)
- PC-012 xong cho phạm vi tệp đợt chạm tới
- **Mọi giá trị "trích rồi xác minh" có xác nhận từ đối tác** — liên hệ, mạng xã hội, article ID
- Diễn tập khôi phục thành công

**Điều kiện nghiệm thu:** hai tuần vận hành không sự cố P1/P2 liên quan tới di cư.

#### ⚠️ Trích tự động rồi nhập thẳng là sai

Script trích được cấu hình từ ứng dụng cũ, nên ai cũng muốn nhập thẳng. Nhưng `lusso` và `parasola` đang mang dữ liệu của HDBank. Nhập thẳng nghĩa là **hợp thức hoá lỗi**, và lúc đó nó nằm trong cơ sở dữ liệu chứ không nằm trong mã nguồn — khó thấy hơn hôm nay.

**AC:**
- [ ] Mỗi đợt có biên bản điều kiện vào và nghiệm thu
- [ ] Diễn tập khôi phục trước mỗi cutover, ghi nhận thời gian thực tế
- [ ] Không đợt nào bắt đầu khi đợt trước chưa nghiệm thu

---

### PC-014: Chẩn đoán và danh sách kiểm onboard

**Priority:** Must Have — yêu cầu mới tại v1.2

**Vì sao cần — và vì sao KHÔNG phát minh lại.** Quy trình này **đã tồn tại**: `fecredit/setup.md` (149 dòng) và `parasola/setup.md`, nguồn từ Google Sheet *"Onboard FEC checklist - Golive"*, bám sát `new-client-config.csv` ở gốc repository. PC-014 là **điện tử hoá cái đang có**, không phải thiết kế mới.

Hai thứ `setup.md` đã có mà thiết kế phải giữ:

- **Cột trạng thái ba mức** — `✅ đã vào config` · `⏳ chờ đối tác gửi` · `⚠️ sheet ghi hai giá trị khác nhau, chờ chốt`. Không phải xong/chưa xong, vì phần lớn thời gian nằm ở mức thứ ba
- **Mục "Còn lại — yêu cầu design/ADV"** — việc đang chờ bên ngoài, không phải việc của dev. Bản `fecredit` có 6 mục ở đây tại thời điểm lên release

Cái `setup.md` **chưa** giải quyết: nó là tệp markdown trong repo, mỗi đối tác một bản chép tay, và không có gì đối chiếu nó với trạng thái thật trong cơ sở dữ liệu. Thất bại đầu tiên khi làm thiếu vẫn là vòng lặp chuyển hướng câm (mục 2.7).

**Ba thứ phải có:**

**Chẩn đoán tên miền.** Tra một tên miền, biết nó phân giải ra đối tác nào. Cảnh báo khi nhiều đối tác cùng khai một tên miền — sai `allowDomains` hôm nay làm site **tự đổi sang chế độ đa đối tác**, hiện bộ chuyển và cho thấy đối tác lạ, mà không báo lỗi gì.

**Danh sách kiểm bảy tầng.** Hiển thị trạng thái từng tầng cho một đối tác: bản ghi nền → 4 bài viết → cấu hình ứng dụng → danh mục → ít nhất một chiến dịch → cờ nghiệp vụ → nhân sự quản trị. Mỗi mục nêu **còn thiếu gì** và mở được màn tương ứng.

**Trạng thái "đang dựng".** Hiện `status=active` bật ngay, nên đối tác chưa xong tầng 2–4 vẫn phục vụ lưu lượng — người dùng vào thấy site chưa có điều khoản hoặc chưa có chiến dịch nào.

**AC:**
- [ ] Tra tên miền chưa đăng ký: nêu rõ không phân giải ra đối tác nào
- [ ] Tên miền khai ở hai đối tác: hiện cảnh báo
- [ ] Danh sách kiểm phản ánh đúng trạng thái từng tầng — kiểm bằng một đối tác dựng dở
- [ ] Đối tác "đang dựng" không phục vụ lưu lượng công khai

---
## 5. Non-Functional Requirements

### NFR-001: Tương thích ngược trong giai đoạn chạy song song
Hình dạng response của endpoint public giữ nguyên cho tới khi đợt cuối nghiệm thu.

### NFR-002: Không nhân bản luật nghiệp vụ ra frontend
Điều kiện tính thưởng, gate nộp bài, luật xét duyệt tiếp tục ở backend.

### NFR-003: Khả năng chịu lỗi
API cấu hình lỗi hoặc chậm → dùng bản cache gần nhất; không trả trang trắng.

### NFR-004: Hiệu năng và kích thước gói
SSR phát sinh tối đa một request cấu hình mỗi request trang, tỷ lệ trúng cache cao. Yêu cầu **tách gói theo tuyến và tải theo cờ phân hệ** — hiện không ứng dụng nào bật `dynamicImport`. Ngưỡng xác lập sau lần build đầu tiên.

### NFR-005: Ngôn ngữ
Toàn bộ tiếng Việt.

### NFR-006: Chất lượng hiển thị
Vỡ bố cục, tràn văn bản, chồng lớp, sai lệch trên di động là lỗi chặn nghiệm thu. Mỗi màn kiểm tra trực quan trên cả desktop và di động, với tối thiểu hai bộ token tương phản.

### NFR-007: Đường cơ sở hồi quy
Repository hiện không có đường cơ sở (`hdbank`, `parasola` mỗi ứng dụng một tệp kiểm thử). Trước mỗi đợt di cư, thiết lập bộ ảnh đối chiếu cho từng màn × từng đối tác, chụp từ ứng dụng cũ đang chạy.

Kiểm thử tự động bắt buộc cho: kiểm tra schema section, kiểm tra chéo dữ liệu đối tác, phân giải người thuê theo `Host`, đối chiếu khoá cache hai phía.

### NFR-008: Bán kính ảnh hưởng và khả năng quan sát
Sau hợp nhất, một sự cố tác động 5 đối tác thay vì 1. Yêu cầu:
- Mọi bản ghi nhật ký gắn định danh tên miền và đối tác, từ ngày đầu
- Phân biệt hai lớp khôi phục: **mã nguồn** tác động toàn bộ; **cấu hình** tác động một đối tác. Quyền thực hiện mỗi lớp quy định tường minh
- Triển khai mã nguồn áp dụng phát hành từng phần

### NFR-009: Quản trị thay đổi theo yêu cầu đối tác
Sau hợp nhất, yêu cầu riêng của một đối tác tác động toàn hệ thống. Cần quy trình phân loại yêu cầu thành cấu hình hoặc từ chối, kèm người chịu trách nhiệm. Thiếu quy trình này, áp lực vận hành sẽ dẫn tới tách nhánh mã nguồn trở lại.

Chỉ số theo dõi: **số khoá trong `slots`** — bắt đầu ở 0. Khác 0 nghĩa là lược đồ cấu hình chưa đủ.

### NFR-010: Cổng gác chống quay lại giá trị gán cứng
Kiểm tra trong CI: `partner-app/src/**` không được chứa URL bên ngoài, số điện thoại, địa chỉ email, mã màu hex, hoặc slug chiến dịch nằm ngoài module cấu hình. Vi phạm là build đỏ.

Không có cổng này thì `lusso/pages/home/components/not-logged-in/index.tsx:569` — điều kiện UI dựa trên slug chiến dịch cứng — sẽ tái sinh ở hệ mới.

### NFR-011: Cổng gác kiểm tra kiểu
`partner-app/` phải chạy được `tsc --noEmit` sạch trong CI. Năm ứng dụng hiện tại có **0 lỗi kiểu trong mã của chính chúng** nhưng không chạy được vì thiếu `skipLibCheck: true` — sửa một dòng, và nên sửa cho cả 5 ứng dụng hiện hành ngay, độc lập với dự án.

---

## 6. Epics và thứ tự

### 6.1 Tiền đề — task độc lập, hoàn tất trước E2

| # | Nội dung |
|---|---|
| E0-A | PRE-2, PRE-3 — gỡ giá trị dự phòng cứng ở `hdbank`, `lusso`, `parasola` (`fecredit` đã sửa, `vpbank` đã gỡ); sửa dữ liệu HDBank trên `lusso` (4 chỗ) và `parasola` (hotline) |
| E0-B | PRE-4 — `canonical` sinh từ `Host`. **Không đổi giá trị `ORIGIN`** — đổi sẽ phá đăng nhập TikTok cả 5 app |
| E0-C | PRE-5 — gỡ `global._cookies`; thêm `skipLibCheck` cho cả 5 ứng dụng (NFR-011) |

**PRE-1 không còn trong danh sách này** — quyết định 04/09 giữ nguyên luồng TikTok, xem mục 2.6.

### 6.2 Xây dựng

| # | Epic | Phụ thuộc |
|---|---|---|
| E1 | Backend: collection `PartnerAppConfig`, phiên bản, endpoint đọc theo tên miền, xoá cache | — |
| E2 | `partner-app/` khởi tạo + PC-001 + PC-002 + PC-003 | E0, E1 |
| E3 | Admin: cấu hình + PC-007 + PC-014 | E1 |
| E4 | 18 màn lõi + hạ tầng dùng chung. **Ưu tiên `home`, `ekyc`, `account` ở đầu epic** | E2 |
| E5 | PC-005 + màn Trang chủ trong admin | E3, E4 |
| E6 | PC-004 + màn `contract` | E4 |
| E7 | 2 màn affiliate của `fecredit` | E6 |
| E8 | PC-011 uỷ quyền OAuth đa tên miền | E2 |
| E9 | PC-012 hoà giải biến thể | E4 |

### 6.3 Di cư

| Đợt | Đối tác | Khoảng cách | Căn cứ |
|---|---|---|---|
| M1 | `hdbank` · `lusso` | **45** | Cặp gần nhau nhất. Đợt này gánh toàn bộ hạ tầng dùng chung |
| M2 | `parasola` | 57–69 | Cùng hồ sơ phân hệ |
| M3 | `vpbank` | 99–112 | Không có `contract` — kiểm chứng cờ phân hệ |
| M4 | `fecredit` | 118–154 | Xa nhất, có 2 màn affiliate và 3 token gradient riêng |

`lusso` nằm ở đợt đầu và là đối tác có nhiều dữ liệu HDBank nhất — E0-B **phải** hoàn tất trước M1.

---

## 7. Kiến trúc

```
Trình duyệt → <tên miền đối tác>
   │
   ▼ partner-app: đọc Host  (hoặc PARTNER_SLUG — PC-001)
   │
   ▼ GET /api/public/partners/app-config?domain=…      [Redis 4h — đã có]
   │      └─ ?preview=<token> → trả bản draft (PC-007)
   │
   ▼ Kết xuất phía máy chủ
   │   ghi CSS variable vào style của <html>            → không FOUC (PC-002)
   │   sinh title / favicon / OG / canonical theo Host / GTM  (PC-006)
   │
   ▼ Kết xuất phía trình duyệt
       ThemeProvider   → component đọc token, hover bằng ĐỘ MỜ
       FeatureFlags    → ẩn nav và chặn tuyến theo cờ  (PC-004)
       sections[]      → kết xuất theo thứ tự; nav sinh từ đây (PC-005)

admin (umi 3 + antd 4)
   │  chỉnh nháp → Xem trước → Xuất bản → sinh phiên bản + xoá cache
   ├─ chẩn đoán tên miền + danh sách kiểm 7 tầng (PC-014)
   └─ Khôi phục phiên bản trước
```

**Endpoint bổ sung — toàn bộ là thêm mới:**
- `GET /api/public/partners/app-config` — cấu hình `published` theo tên miền, hoặc `draft` khi có token xem trước
- `GET|PUT /api/admin/partners/:id/app-config`
- `POST /api/admin/partners/:id/app-config/publish` và `.../restore/:version`
- `GET /api/admin/partners/:id/onboarding-status` — trạng thái 7 tầng (PC-014)

**Bề mặt API mà `partner-app/` phải hiện thực: 70 endpoint** — `user` 27, `bank` 12, `event` 10, `taxCode` 4, `partners` 4, `withdraw` 3, `upload` 2, `notification` 2, còn lại 6.

**Lược đồ `partner_app_configs`:**

```
partner        ObjectId
status         draft | published
version        int

identity     { slug, brandName, domain }
theme        { primary, primaryForeground, fontFamily, fontFiles[], colorsExtra{} }
assets       { core{logo, logoMobile, logoFooter, favicon, ogImage, decorLeft, decorRight},
               named{} }
content      { articleIds{qa, term, condition},     ← 3, KHÔNG phải 4: xem PC-007
               contact{hotline, email},
               social[{platform, url}],
               footerBrandLink }
seo          { title, description, keywords, ogImage, gtmId }
modules      { contract, affiliate }
sections     [{key, type, props}]
slots        {}                      ← giữ chỗ, chưa hiện thực (PC-009)

publishedAt / publishedBy / changelog
```

Khoảng **20 trường**. `canonical` không lưu — sinh từ `Host`. `PartnerOpts` giữ nguyên vị trí hiện tại.

---

## 8. Implementation Scope

### Thay đổi cần thực hiện

**`backend/` (Go 1.24 · Echo · MongoDB · Redis · MinIO — giữ nguyên nền tảng):**
- Model `PartnerAppConfigRaw`, `PartnerAppConfigVersionRaw`, collection mới
- Bốn nhóm endpoint ở mục 7
- Kiểm tra schema section, cưỡng chế section bắt buộc (BH-2)
- Kiểm tra URL tài nguyên (PC-003)
- Kiểm tra chéo dữ liệu đối tác và trường bắt buộc lúc xuất bản (PC-007)
- Kiểm tra đích chuyển tiếp OAuth theo `allowDomains` (PC-011)
- Xoá cache theo khoá trùng khớp với frontend

**`partner-app/` (ứng dụng mới — Next.js · React 18/19 · Tailwind):**
- PC-001 → PC-007, PC-011
- 21 màn: 18 lõi, `contract`, 2 màn affiliate
- Hạ tầng dùng chung: components, layouts, models, services, utils, hooks

**`admin/` (umi 3 + antd 4 — giữ nguyên nền tảng):**
- Chín nhóm màn ở PC-008, gồm chẩn đoán và danh sách kiểm (PC-014)

**Hạ tầng:**
- Một image, một triển khai, nhiều tên miền
- Dự phòng cấu hình khi API lỗi (NFR-003)
- Gắn thẻ đối tác trong nhật ký (NFR-008)
- Cổng CI chặn giá trị gán cứng (NFR-010) và kiểm tra kiểu (NFR-011)

### Không thực hiện

- Không đụng 10 thư mục của đối tác đã ngừng
- Không xây cơ chế slot override (PC-009 đã gỡ)
- Không đổi nền tảng `admin/`
- Không đổi backend nghiệp vụ: gate, sổ cái, thu thập chỉ số, đối soát, tính thưởng
- Không di chuyển `PartnerOpts` trong giai đoạn chạy song song
- Không tạo phụ thuộc vào package của `creator-os`
- Không xử lý 149 phát hiện `go vet` của backend — nằm ngoài phạm vi, nên làm thành task dọn riêng

---

## 9. Assumptions

1. Tên miền đối tác tiếp tục kết thúc trên hạ tầng nội bộ, như 5 tên miền hiện hành
2. Backend là nguồn dữ liệu duy nhất; `partner-app/` không có cơ sở dữ liệu riêng
3. Đội ngũ có ít nhất một kỹ sư thành thạo Next.js và Tailwind
4. Số đối tác trên `partner-app/` trong năm đầu ở mức dưới hai chục
5. Đội vận hành tiếp nhận công việc onboard tầng 3
6. Các đối tác chấp nhận chuẩn hoá một số hành vi riêng trong phạm vi PC-012
7. Mười thư mục của đối tác đã ngừng không phát sinh yêu cầu bảo trì trong thời gian dự án
8. **Luồng uỷ quyền TikTok giữ nguyên hiện trạng** theo quyết định 04/09; `partner-app` port nguyên. Đây là quyết định giữ nguyên, không phải kết luận đã kiểm tra và thấy an toàn (PRE-1)
9. Đăng ký Authorized JavaScript origin bên Google Console là **một bước có trong quy trình onboard hiện tại** — xác nhận 04/09

---

## 10. Out of Scope

- Mười thư mục frontend của đối tác đã ngừng
- Cơ chế slot override
- Nâng cấp `umi`, Node, `node-sass` của 5 ứng dụng hiện hành — chúng được thay thế
- Hỗ trợ đa ngôn ngữ
- Đối tác truy cập admin trực tiếp
- Trình dựng trang tự do
- Chuyển sang `creator-os` như một nền tảng
- Dọn 149 phát hiện `go vet`
- Xử lý PRE-1 → PRE-5: task độc lập, tiền đề của E2

---

## 11. Traceability — đối chiếu với `creator-os`

| `creator-os` | Tài liệu này | Quan hệ |
|---|---|---|
| `packages/ui/src/button.tsx` — hover bằng độ mờ | **PC-002** | **Kế thừa trực tiếp.** Loại bỏ toàn bộ phép tính màu khỏi hệ thống |
| `packages/theme/src/tokens.ts` | **PC-002** | Kế thừa mô hình token; rút gọn còn 2 màu vì 152/157 biến đo được là đồng nhất |
| `portal-creator/app/layout.tsx` | **PC-002** | Áp dụng cách chèn CSS variable khi kết xuất phía máy chủ |
| `packages/feature-flags` | **PC-004** | Kế thừa mô hình, giữ xử lý lỗi mềm |
| `packages/contracts/src/landing-sections.ts` | **PC-005** | Kế thừa mô hình danh mục; danh mục riêng theo component thực tế |
| `CmsDocument` + `CmsDocumentVersion` | **PC-007** | Kế thừa mô hình bản nháp và phiên bản; hiện thực trên MongoDB |
| `portal-creator/themes/` — slot registry | — | **Không dùng.** Không có consumer |
| `packages/ui` (gói riêng) | — | **Không tách gói.** creator-os có 12 nơi dùng; Ambassador có một |
| Model `Domain` | — | Không dùng — đã có `AllowDomains` |
| NestJS, Prisma, PostgreSQL, RLS | — | Không dùng |

---

## 12. Resolved Questions

| Câu hỏi | Kết luận |
|---|---|
| Đưa đối tác lên `creator-os` hay xây trong Ambassador? | **Xây trong Ambassador.** `creator-os` là tài liệu tham khảo (03/09) |
| Dùng mã nguồn hoặc package của `creator-os`? | **Không.** Kế thừa mô hình thiết kế và bài học (03/09) |
| Giữ `umi 3` hay đổi nền tảng? | **Đổi.** `node:14.17.3` kết thúc hỗ trợ 04/2023; khảo sát cho thấy chi phí chuyển thấp hơn dự kiến — 41% `components/` là UI nguyên thuỷ thay được bằng thư viện, lớp giao diện là utility-first nên ánh xạ sang Tailwind mang tính cơ học, toàn ứng dụng chỉ 2 vị trí phụ thuộc SSR |
| Một triển khai chung hay tách theo đối tác? | **Một triển khai**, phân giải theo `Host`, giữ `PARTNER_SLUG` để tách khi cần |
| Phạm vi đối tác? | **5 đối tác đang hoạt động.** Mười thư mục còn lại không thuộc phạm vi và không bị đụng (04/09) |
| Phạm vi màn hình? | **21 màn** — 18 lõi, `contract`, 2 affiliate |
| Có cần slot override? | **Không.** Không đối tác nào trong 5 có màn hình hình dạng riêng |
| Có cần chế độ đa đối tác? | **Không cần xây thêm** — cả 5 tên miền phân giải ra một đối tác. Cờ `AllowHeaderPartner` đã có, giữ nguyên |
| Màu dẫn xuất tính ở đâu? | **Không tính ở đâu cả.** Hover và active dùng độ mờ của cùng token (mục 2.4) |
| Có tách thư viện dùng chung? | **Không.** Vì không còn phép tính nào để dùng chung, và chỉ có một app FE |
| Cấu hình có hiệu lực ngay hay qua duyệt? | **Nháp → xem trước → xuất bản**, có lịch sử và khôi phục |
| Ai vận hành màn cấu hình? | **Đội vận hành.** Nghiệm thu bằng phiên thao tác thực tế |
| Màn cấu hình dựng trên nền tảng nào? | **`admin/` hiện hành** (umi 3 + antd 4) |
| URL có đổi sau di cư? | **Không.** Cấu trúc `/<partner>/<slug>` đã dùng ở cả 5 |
| Người dùng có bị đăng xuất? | **Không.** `authToken` ở `localStorage` theo origin, mỗi tên miền giữ nguyên origin |

---

## 13. Open Questions

1. **Ngưỡng bán kính ảnh hưởng** — số đối tác tối đa trên một triển khai trước khi cần tách. Cần trước khi lên production.
3. **Chủ sở hữu quy trình NFR-009** — ai quyết định phân loại một yêu cầu riêng của đối tác. Cần trước M2.
3. **PC-012 nhóm khác biệt hành vi** — 4 tệp (`not-logged-in` Δ914, `header` Δ659, `models/main` Δ288, `interfaces/event` Δ251) cần **đối tác chấp thuận** trước cutover. Chưa xác định đầu mối phía 5 đối tác. Cần trước M1.

### Đã đóng

| Câu hỏi | Kết luận | Ngày |
|---|---|---|
| Link Zalo giống hệt ở 4 đối tác — hằng số nền tảng hay lỗi sao chép? | **Lỗi sao chép, đã biết.** `fecredit/setup.md`: *"Zalo OA + nhóm Zalo cộng đồng + group Facebook vẫn là link của Parasola — chờ ADV cấp link FE Credit"* | 04/09 |
| `fecredit` thiếu `APP_NAME` — giá trị đúng là gì? | **Câu hỏi sai.** `APP_NAME` là env chết, gỡ có chủ đích: tên app lấy từ `wrappers/home.tsx` + `document.ejs` | 04/09 |
| `partner-app/` cùng repository hay tách? | **Cùng repository `ambassador`** | 04/09 |
| PRE-1 có tách thành task độc lập xử lý ngay? | **Không.** Giữ nguyên luồng TikTok, port sang `partner-app` | 04/09 |
| Mười thư mục đối tác đã ngừng xử lý thế nào? | **Không thuộc phạm vi, không đụng tới** | 04/09 |
| `vpbank` không có `contract` — chủ đích hay sót? | **Không điều tra.** Mặc định: `contract` là **cờ phân hệ**, `vpbank` giữ nguyên `contract = false` — khớp hành vi hiện tại. Nếu là thiếu sót thì bật cờ, không phải sửa mã | 04/09 |
| `vpbank` còn import `FacebookSection` sống? | **Không điều tra.** Mặc định: `partner-app` **không hiện thực Facebook** (4/5 app đã tắt). Nếu tới M3 phát hiện `vpbank` dùng thật thì xử lý tại đợt đó, ghi thành rủi ro chứ không chặn | 04/09 |

---

## 14. Revision History

| Version | Date | Thay đổi |
|---|---|---|
| 1.0 | 2026-09-03 | Bản đầu. Chốt phương án ứng dụng mới trên nền tảng hiện đại, backend giữ nguyên, `creator-os` là tài liệu tham khảo. Phạm vi khi đó: 15 ứng dụng, giữ nguyên không di cư |
| 1.1 | 2026-09-04 | Đổi phạm vi sang di cư toàn bộ 15 ứng dụng theo 6 đợt. Bổ sung PC-011 → PC-013, NFR-007 → NFR-009. Sửa PC-001 theo mô hình tên miền → tập đối tác |
| 1.3 | 2026-09-04 | Đính chính theo `fecredit/setup.md` — checklist onboard thật do người thực hiện viết. Gỡ ba env chết khỏi lược đồ (`APP_NAME`, `documentShareLink`, `accesstradePartnerId` — không component nào đọc); article ID từ **4 xuống 3** (`SUPPORT_ARTICLE_ID` code không đọc; Thể lệ và Hướng dẫn lấy từ `eventHome.ruleContent`/`guideContent`, dán vào event trên admin). PC-014 viết lại thành **điện tử hoá `setup.md` sẵn có**. **PRE-1: quyết định giữ nguyên luồng TikTok** (04/09), gỡ khỏi tiền đề chặn E2; PC-011 thu về Google và SSO. PC-006 thêm cảnh báo `ORIGIN` gánh hai vai. Đóng 5 câu hỏi mở |
| 1.2 | 2026-09-04 | Viết lại mục 4 theo văn phong của [prd-staff-code-frontend](../employee-code/prd-staff-code-frontend-2026-09-03.md): mỗi FR mở bằng **Vì sao cần**, bẫy đã kiểm chứng nâng thành tiêu đề con `#### ⚠️`, bằng chứng `file:line` đặt ngay trong FR thay vì dồn về mục 2. **Thu hẹp phạm vi còn 5 đối tác đang hoạt động** (`hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`); 10 thư mục còn lại thuộc đối tác đã ngừng, không thuộc phạm vi. Màn hình 33 → 21, đợt di cư 6 → 4, tệp phân kỳ 33 → 22. **Gỡ PC-009** (slot override) — không còn consumer. **Đổi PC-002**: loại bỏ toàn bộ phép tính màu, hover và active dùng độ mờ theo mô hình `packages/ui/src/button.tsx` của `creator-os`; token cấu hình rút còn `primary` + `primaryForeground` do đo được 152/157 biến SCSS là đồng nhất. Bổ sung **PC-014** (chẩn đoán tên miền, danh sách kiểm onboard, trạng thái "đang dựng") suy từ phân tích bảy tầng onboard. Bổ sung **NFR-010** (cổng CI chặn giá trị gán cứng) và **NFR-011** (cổng kiểm tra kiểu). Bổ sung mục 2.4 (quyết định về phép tính màu), 2.6 (năm lỗi production), 2.7 (bảy tầng onboard), 2.8 (trạng thái chất lượng mã nguồn) |
