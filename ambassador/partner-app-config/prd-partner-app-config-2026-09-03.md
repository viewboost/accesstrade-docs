# Product Requirements Document: Hợp nhất frontend đối tác trên nền cấu hình lúc chạy (`partner-app/`)

**Date:** 2026-09-03 (cập nhật 2026-09-04)
**Author:** Nguyễn Đăng Định
**Version:** 1.2
**Reviewer:** _chưa có_
**Project Level:** Level 4 — ứng dụng mới + mở rộng backend + mở rộng admin + migrate 5 hệ thống đang chạy
**Status:** Draft — phạm vi đã chốt, chờ review
**Mức độ:** **P2** — không có sự cố đang diễn ra, nhưng chi phí cộng dồn theo mỗi lần onboard và mỗi lần sửa lỗi
**Phạm vi:** ứng dụng mới `partner-app/` + mở rộng `backend/` + mở rộng `admin/` + **migrate 5 đối tác đang hoạt động theo 4 đợt**

---

## Document Overview

Mỗi lần onboard một đối tác, hệ thống sinh thêm một bản sao frontend độc lập. Tài liệu này đặc tả `partner-app/` — ứng dụng frontend hợp nhất, vận hành đa tenant với cấu hình đọc lúc chạy — và lộ trình migrate 5 đối tác đang hoạt động.

### Phạm vi được thu hẹp — chốt 04/09

Repository chứa 15 thư mục frontend, nhưng **chỉ 5 đối tác còn hoạt động**: `hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`. Mười thư mục còn lại (`anker`, `flamingo`, `mbbank`, `tpbank`, `turborg`, `vng`, `vnpay`, `wildrift`, `yody`, `frontend`) thuộc đối tác đã ngừng. Tài liệu này **chỉ nói về 5 đối tác đang hoạt động**; mười thư mục kia không nằm trong phạm vi và **không bị đụng tới**.

Năm đối tác này tình cờ là cụm đồng nhất nhất trong repository — cùng hồ sơ phân hệ KYC đầy đủ, và không đối tác nào có màn hình hình dạng riêng ngoại trừ hai màn affiliate của `fecredit`.

### Nguyên tắc

**Nhận diện thương hiệu là dữ liệu, không phải mã nguồn.** Mọi khác biệt giữa 5 bản hiện hành phải nằm trong một bản ghi cấu hình đọc lúc chạy.

**Backend hỗ trợ đa tenant ở tầng phân giải; không viết lại.** `PartnerRaw.AllowDomains` và `GetDetailByDomain` đã phục vụ production.

**`creator-os` là tài liệu tham khảo thiết kế, không phải nguồn mã.** Kế thừa mô hình và bài học vận hành (mục 2.3), không nhập mã nguồn, không tạo phụ thuộc chéo repository.

**Một triển khai duy nhất, resolve partner theo domain theo `Host`.** Năm domain hiện hành đều kết thúc trên hạ tầng nội bộ (`SSH_HOST_{env}` — một máy chủ mỗi môi trường; `Dockerfile.release` và `nginx/` đồng nhất).

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
| **ADV** | Cách gọi trong tài liệu dự án. Trong mã nguồn là **`partner`** (`PartnerRaw`, `allowDomains`, `COMMON_PARTNER`) — cùng một thứ. Tài liệu này dùng `partner` khi nói về mã, `ADV` khi nói về phạm vi dự án |
| **Đối tác đang hoạt động** | `hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`. Phạm vi duy nhất của tài liệu này |
| **`partner-app/`** | Ứng dụng hợp nhất được đặc tả tại đây. Một codebase, một triển khai |
| **Cấu hình ứng dụng** (`PartnerAppConfig`) | Bản ghi chứa toàn bộ khác biệt giữa các đối tác |
| **Design token** | Giá trị cấu hình giao diện, ánh xạ thành CSS custom property khi SSR |
| **Section** | Khối nội dung trên trang chủ. Trang chủ là mảng có thứ tự các section |
| **Section catalogue** | Danh mục loại section hợp lệ. Định nghĩa nằm trong mã nguồn, không nằm trong cơ sở dữ liệu |
| **Đợt migrate** | Nhóm đối tác chuyển sang `partner-app/` cùng lúc. Bốn đợt (mục 6) |
| **Chạy song song** | Giai đoạn đối tác đã chuyển nhưng ứng dụng cũ vẫn sẵn sàng khôi phục |
| **Cutover** | Thời điểm chuyển lưu lượng của một domain sang `partner-app/` |
| **Bảy tầng onboard** | Toàn bộ chuỗi việc để một đối tác mới có site chạy được (mục 2.7) |

---

## 1. Executive Summary

Mô hình một-đối-tác-một-codebase tạo hai loại chi phí đo được:

```
Sửa một lỗi ở tầng dùng chung  →  phải áp dụng lại tại 4 vị trí khác
                               →  hoặc bỏ sót, dẫn tới khác nhau hành vi
Onboard một đối tác            →  copy ~25.000 LOC, dựng pipeline, dựng image, triển khai
```

Chi phí đã hiện thực hoá — nội dung commit trong repository ghi trực tiếp: `d25209fcc docs(budget-alert): cảnh báo file có 14 bản sao, phải sửa đồng loạt`.

### Mức trùng lặp cho phép hợp nhất với chi phí thấp

So hash nội dung đường dẫn `.ts`/`.tsx`/`.scss` trên **5 đối tác đang hoạt động** (loại trừ `.umi`):

| Số phiên bản của cùng một file | Số file |
|---|---|
| 1 — đồng nhất trên cả 5 | **246 (69%)** |
| 2 | 45 |
| 3 | 22 |
| 4 | 24 |
| 5 — khác nhau thực sự | **22 (6%)** |
| **tổng** | **359** |

**18/21 màn hình có ở cả 5 đối tác.** Chỉ 3 màn lệch: `contract` (4/5, `vpbank` không có), `affiliate-campaign-detail` và `affiliate-commission` (chỉ `fecredit`).

Và trong 157 biến SCSS của hệ thiết kế, **152 giống hệt nhau ở cả 5 đối tác**. Khác biệt giao diện thực chất gói trong **một biến `$primary`**, cộng ba biến gradient riêng của `fecredit`.

### Chỉ số thành công

Ba số đã đo được hôm nay, dùng làm mốc so sánh:

| Chỉ số | Hôm nay | Mục tiêu |
|---|---|---|
| Thời gian onboard tầng cấu hình | một đợt việc của dev + một lần triển khai | **dưới 1 giờ**, đội vận hành tự làm |
| Commit chạm nhiều ứng dụng cùng lúc | **37 commit / 6 tháng** (11 commit chạm 12–14 thư mục) | **0** sau khi migrate xong |
| Commit chỉ phục vụ một ADV | **158 commit / 6 tháng** | **0** — đây là phiên bản đo được của "quay lại fork" |

Số thứ ba là chỉ số quan trọng nhất và cũng dễ bị bỏ qua nhất: nó không đo dự án làm xong hay chưa, mà đo dự án **có giữ được kết quả hay không**.

---

## 2. Bối cảnh

### 2.1 Hiện trạng — đã đối chiếu mã nguồn

**Hạ tầng đã đồng nhất.** Tập dependency trùng khớp (`umi ^3.5.20`, `react 16`, 43 dependency). Trong 23 biến môi trường, **14 giống hệt ở cả 5** — `API_ENDPOINT`, `CLIENT_ID`, `TIKTOK_CLIENT_ID`, toàn bộ `FB_*`, `ORIGIN`, `SSO_*`. Chín biến còn lại là khác biệt thật:

```
COMMON_PARTNER · APP_NAME · NEXT_PUBLIC_ORIGIN
SUPPORT_ARTICLE_ID · QA_ARTICLE_ID · TERM_ID · CONDITION_ID
DOCUMENT_SHARE_LINK (lusso, parasola) · ACCESSTRADE_PARTNER_ID (parasola)
```

**Khác nhau ở tầng lõi là hệ quả copy:** `configs/api.ts` (`hdbank` ↔ `vpbank`) khác biệt duy nhất ở **thứ tự khai báo**; `services/user.ts` (`hdbank` ↔ `parasola`) **trùng khớp hoàn toàn**; `wrappers/home.tsx` có 5 phiên bản nhưng toàn bộ là chuỗi nhận diện thương hiệu.

**Nền tảng frontend đã hết vòng đời hỗ trợ.** Cả 5 ứng dụng build trên `node:14.17.3` (kết thúc hỗ trợ 04/2023) kèm `node-sass ^4.9.0`. Backend không nằm trong tình trạng này: Go 1.24, Echo v4, mongo-driver 1.11.

**Chuyển umi → Next là viết lại tầng routing và state, không phải chuyển từng phần.** Đo trên `hdbank` (194 file `.tsx`):

| Bám vào đâu | Số đo |
|---|---|
| File import từ `'umi'` | **74/194**, 83 lượt import |
| API umi đang dùng | `useDispatch` 23 · `useSelector` 19 · `useLocation` 13 · `useParams` 10 · `connect` 7 · `Redirect` 2 · `Helmet` 2 · `history` 3 · `request` 1 · `getDvaApp` 1 |
| Routing | 27 route khai trong `config/routes.ts`, 21 chỗ dùng `wrappers` |
| State | 41 file dùng `connect`/`useDispatch`/`useSelector`; `models/main.ts` 411 LOC, 27 effect, 2 reducer |

Mảng route khai báo → file-based App Router. `wrappers` → layout và middleware. dva + redux-saga **không có tương đương** ở Next, phải chọn lại tầng state.

Phần rẻ nằm ở **lớp giao diện**, không phải ở đây: 41% `components/` là UI nguyên thuỷ thay bằng thư viện, và class utility-first của Bootstrap ánh xạ sang Tailwind mang tính cơ học (3.707 lượt class utility, 25 lượt CSS module).

### 2.2 Năm ứng dụng là bản sao của cùng một ứng dụng đa tenant

**Phía backend** đã có đủ tầng phân giải:

| Thành phần | Vị trí |
|---|---|
| `PartnerRaw.AllowDomains []string` | `internal/model/mg/partner.go:51` |
| `GetDetailByDomain`, `GetListPartnersByDomain` | `pkg/public/service/partner.go:40-88` |
| Truy vấn public giới hạn theo `query.Domain` | `pkg/public/service/partner.go:310` |
| Cache Redis theo domain, TTL 4 giờ | `pkg/public/service/partner.go:44-52` |
| Cờ tính năng theo đối tác (`PartnerOpts`) | leaderboard, `enableStaffCode`, `allowResubmitRejectedContent` |

**Phía frontend**, cả 5 ứng dụng đều có 10 tuyến `/:partner/…` và logic `isOwnerPartner`. Chế độ hiển thị do backend quyết định: `res.AllowHeaderPartner = len(res.Data) > 1` (`partner.go:376`). Khác biệt white-label nằm ở một chỉ thị điều hướng tại `pages/main-home/index.tsx` và 2–3 tham chiếu `COMMON_PARTNER`.

**Hai hệ quả:** `partner-app/` không cần xây cơ chế phân giải mới; và **cấu trúc URL `/<partner>/<slug>` giữ nguyên sau migrate** — không phát sinh bảng chuyển hướng, không gián đoạn chỉ mục tìm kiếm.

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

### 2.5 Khác nhau giữa 5 đối tác — cơ sở cho lộ trình

Khoảng cách từng cặp (số file khác biệt trên `src/**`):

```
           hdbank   lusso  parasola  vpbank  fecredit
hdbank         ·      45      69       99      131
lusso         45       ·      57      107      126
parasola      69      57       ·      112      118
vpbank        99     107     112        ·      154
fecredit     131     126     118      154        ·
```

**Hồ sơ cấu hình thật** — đây là dữ liệu khởi tạo cho migrate:

| | hdbank | lusso | parasola | vpbank | fecredit |
|---|---|---|---|---|---|
| slug | `hdbank` | `lussosaigon` | `parasola` | `vpbank` | `fecredit` |
| domain | creator.hdbank.com.vn | megalive.lussosaigon.vn | parasola-creator.com | vpbank.koc.com.vn | ambassador.fecredit.com.vn |
| `$primary` | `#FAA61A` | `#066A9D` | `#EE5799` | `#005baa` | `#00994F` |
| font | BeVietnamPro | BeVietnamPro | Rosellinda | SVN-Gilroy | FE Font |
| phân hệ `contract` | ● | ● | ● | — | ● |
| phân hệ `affiliate` | — | — | — | — | ● |
| token riêng | — | — | — | — | 3 gradient |

**Ảnh:** 20 khoá trên 5 app, chỉ **5 khoá có ở cả 5** (`logoImage`, `logoMobileImage`, `logoBrandFooter`, `decorLeft`, `decorRight`). 15 khoá còn lại là ảnh mốc thưởng có ở 4/5 hoặc 1/5. Do đó `assets` phải là **map có bộ lõi bắt buộc**, không phải danh sách trường cố định.

### 2.6 Năm lỗi đang chạy trên production — phải sửa trước, ngoài phạm vi tài liệu này

Phát hiện trong quá trình khảo sát. Không do việc hợp nhất tạo ra; cần xử lý như task độc lập, là tiền đề của E2.

**PRE-1 — Điều hướng mở ở luồng uỷ quyền TikTok. Quyết định: GIỮ NGUYÊN (04/09).**
`login-tiktok/index.tsx:14` và `connect-tiktok/index.tsx:12` dùng tham số `state` do bên gọi cung cấp làm đích điều hướng, không kiểm danh sách cho phép. Backend cũng không giới hạn `redirectURI` (`internal/module/social/tiktok/tiktok.go:113`); tìm `allowlist|whitelist|validateRedirect` trên `backend/internal` và `backend/pkg` không có kết quả. Quét toàn bộ nhánh remote 04/09: không nhánh nào có bản vá.

**Quyết định 04/09: `partner-app` port nguyên luồng hiện tại, không thay đổi.** Ghi nhận đây là **quyết định giữ nguyên hiện trạng**, không phải kết luận đã kiểm tra và thấy an toàn — hai câu đó khác nhau và tài liệu này không có căn cứ cho câu thứ hai.

**PRE-2 — Giá trị fallback cứng trỏ tới bài viết pháp lý của đối tác khác.**
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

**PRE-4 — Thẻ canonical trỏ sai domain ở cả 5 ứng dụng.**
`wrappers/home.tsx` gán `url: process.env.ORIGIN`, trong khi `ORIGIN = https://ambassador.koc.com.vn/` ở cả 5; giá trị này dùng cho `<link rel="canonical">` và `og:url`. Nguyên nhân là nhầm giữa `ORIGIN` (domain callback dùng chung) và `NEXT_PUBLIC_ORIGIN` (domain đối tác).

**PRE-5 — Trạng thái toàn cục theo request tại tầng SSR.**
`server.js:25-26` gán `global._cookies` và `global._navigatorLang` trên tiến trình dùng chung. Hiện không nơi nào đọc, nên chưa gây hậu quả. Cần loại bỏ trước khi hợp nhất.

**PRE-6 — Mỗi trang nạp HAI container GTM, và ba ADV bắn dữ liệu vào container của ADV khác.**

`pages/document.ejs` là template HTML per-ADV, chứa một mã GTM gán cứng. `config.prod.ts` lại chèn một mã GTM nữa qua `headScripts`. Cả hai cùng chạy:

| ADV | GTM trong `document.ejs` | GTM trong `config.prod.ts` |
|---|---|---|
| `hdbank` | `GTM-MP23BMKX` | `GTM-PBXTJ86T` |
| `lusso` | `GTM-MP23BMKX` — **của HDBank** | `GTM-N7C2MVPM` |
| `parasola` | `GTM-TN9CMZ6X` | `GTM-TN9CMZ6X` |
| `vpbank` | *(trống)* | `GTM-PBXTJ86T` — **của HDBank** |
| `fecredit` | `GTM-TN9CMZ6X` — **của Parasola** | `GTM-NLRX5THC` |

GTM hỏng thì im lặng, nên không ai phát hiện. `partner-app` sinh thẻ head từ config nên lỗi này biến mất theo thiết kế — nhưng dữ liệu đã bắn sai suốt thời gian qua, và người làm báo cáo cần biết.

`document.ejs` còn chứa các giá trị per-ADV khác chưa từng được đếm: thẻ `og:title`/`og:description`/`keywords` (**trùng với `wrappers/home.tsx`** — hai nguồn cùng đặt meta), và `campaign_id: 3481` của ACCESSTRADE **giống hệt ở cả 5 ADV** — cần xác nhận đây là mã dùng chung của nền tảng hay là giá trị bị copy.

**PRE-7 — Hai bản Bootstrap trên cùng một trang.**

```
build SCSS   bootstrap 5.2.3   ← chứa $primary của ADV
CDN CSS      bootstrap 5.3.2   ← màu mặc định của Bootstrap
CDN JS       bootstrap 5.2.3
```

`document.ejs` nạp CSS 5.3.2 từ cdnjs trong khi bản build biên dịch SCSS từ 5.2.3. Cái nào thắng phụ thuộc thứ tự chèn — cần kiểm trên trang thật. `partner-app` chỉ có một nguồn CSS nên hết.

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

Đo trên 1.333 file `.ts`/`.tsx` của 5 ứng dụng:

| Chỉ số | Tổng | Mỗi ứng dụng |
|---|---:|---|
| `tsc --noEmit --skipLibCheck` — lỗi trong mã của app | **0** | 0 |
| `console.log` còn sót | 144 | ~29 |
| `any` / `@ts-ignore` | 1.474 | ~290 |
| Khối JSX bị comment | 359 | 53–111 |
| Dòng mã bị comment | 421 | ~85 |
| `catch` nuốt lỗi | 5 | 1 |

**Mã nguồn sạch về kiểu; cổng gác thì hỏng.** Không ứng dụng nào chạy được `tsc` vì thiếu `skipLibCheck: true` — trình biên dịch dừng ở file `.d.ts` của dependency. Đây là sửa một dòng, và nó mở lại cổng gác kiểu cho cả 5.

Backend: **149 phát hiện `go vet`** (phần lớn là `bson.E` không đặt tên trường và khoảng trắng trong struct tag), **9 gói test PASS, 0 FAIL**.

### 2.9 Bản đồ chuyển umi → Next

Đây **không phải chuyển từng phần**. Bảy hệ con phải viết lại, và mỗi cái đều có lời giải sẵn ở `creator-os` — một app Next đang chạy production.

| Hệ con | umi (Ambassador hôm nay) | Next (`creator-os` đã làm) |
|---|---|---|
| Route + guard | `wrappers: ['@/wrappers/home', '@/wrappers/auth']` khai theo từng route | **Route group** `(app)` `(public)` `(auth)`, mỗi group một `layout.tsx`; guard thật ở `middleware.ts` |
| Cây route lồng | `routes: [...]` — 27 route, layout ở 2 tầng (`layouts/home`, `layouts/event-detail`) | Thư mục lồng, `layout.tsx` mỗi tầng. Bên họ: 25 page, 4 layout |
| Redirect | `redirect:` khai trong cây route, `path: '**'` catch-all | `redirect()` trong page, hoặc `redirects()` ở config, `not-found.tsx` |
| Request | `export const request: RequestConfig` — plugin riêng của umi | `HttpClient` tự viết trong `packages/api-client` |
| State | dva + redux-saga: `models/main.ts` 411 LOC, 27 effect, 41 file tiêu thụ | React Query + provider. **Không map cơ học được** |
| HTML template | `pages/document.ejs` | `app/layout.tsx` + `metadata` + `<Script>` |
| Gọi API | Browser gọi thẳng backend | **BFF proxy** `app/api/[...path]/route.ts` |

**Một chỗ nối phải gỡ trước:** response interceptor gọi thẳng vào store —

```js
// app.tsx — tầng HTTP biết về tầng state
const dispatch = getDvaApp()._store.dispatch;
dispatch({ type: 'mainState/updateState', payload: { isLoggedIn: false } });
```

Đổi cả hai tầng cùng lúc mà chỗ nối này còn thì gỡ rất khó.

#### Bốn bài học `creator-os` đã trả giá — Ambassador sẽ vấp y hệt

**1. KHÔNG dùng `rewrites()` để trỏ backend.** Nguyên văn: *"`rewrites()` nội suy `process.env.API_ORIGIN` lúc `next build` và **nướng cứng destination vào `.next/routes-manifest.json`**. Đặt env lúc `docker run` KHÔNG có tác dụng ⇒ mỗi môi trường phải build một image riêng."*

Triệu chứng đánh lừa: *"login chạy được (BFF handler tường minh đọc env runtime) nhưng mọi màn hình sau đó 500 `ECONNREFUSED`."*

Đây đúng cùng họ với `NEXT_PUBLIC_*` — giá trị bị nướng vào lúc build. Ambassador một image chạy mọi domain thì tuyệt đối không được dính. **Dùng BFF proxy route handler, đọc env mỗi request.**

**2. Proxy phải `force-dynamic`.** *"Proxy mà bị cache thì user A đọc được dữ liệu user B — đây là ranh giới tenant, không phải chỗ để tiết kiệm."*

**3. Refresh token phải single-flight.** *"khi NHIỀU request cùng 401, CHỈ 1 refresh chạy… Refresh token là one-time-use (rotate + revoke ở BE) → gọi 2 lần song song = 1 cái 200, 1 cái 401."*

**4. `403 password_reset_required` là nhánh RIÊNG, không gộp vào 401.** *"401 → refresh mint lại pwreset → 401 → loop."*

#### Quyết định auth — giữ `localStorage`

`wrappers/auth.tsx` hiện:

```tsx
if (!isBrowser()) return <></>;                       // SSR trả RỖNG
if (!storage.getTokenStorage()) return <Redirect to="/" />;
```

Token ở `localStorage`, SSR không đọc được, nên **9/27 route thực chất chỉ render ở client** — đã vậy từ trước.

| | Giữ `localStorage` | Theo `creator-os`: cookie + BFF |
|---|---|---|
| Route cần đăng nhập | Client Component — **không thua hiện tại** | Server Component + middleware chặn |
| Phải làm thêm | không | BFF proxy · endpoint refresh · rotate token ở BE · đổi cả 5 app · đụng luồng bounce TikTok |
| SSR phục vụ | trang công khai — landing, chi tiết event, bài viết | mọi trang |

**Chốt: giữ `localStorage`.** SSR vẫn phục vụ đúng chỗ cần SEO, và cookie kéo theo backend cùng luồng TikTok mà mục 2.6 đã chốt giữ nguyên.

**Nhưng vẫn lấy BFF proxy**, dù chọn đường nào — vì nó là chỗ đọc `API_ENDPOINT` lúc chạy. Không có nó thì URL backend bị nướng vào bundle, và một image không chạy được nhiều môi trường.

### 2.10 Ngoài phạm vi bổ sung

- Không trình dựng trang tự do; section là danh mục đóng có schema
- Không cho nhập CSS hoặc JavaScript thô
- Không đa ngôn ngữ (`src/locales` đã đồng nhất 167 dòng ở cả 5 — không cần gộp bản)
- Không thay đổi mô hình `PartnerRaw`; chỉ bổ sung collection mới
- **Không có cơ chế slot override.** Năm đối tác hiện tại không có màn hình hình dạng riêng; `affiliate` của `fecredit` là phân hệ bật/tắt. Xây registry cho zero consumer là vi phạm YAGNI. Trường `slots` giữ chỗ trong lược đồ, chưa hiện thực

---

## 3. User Personas

**P1. Đội vận hành** — người dùng chính của màn hình cấu hình, **không phải kỹ sư**. Phải hoàn thành tầng 3 mà không cần hỗ trợ, và sai thì khôi phục được.

**P2. Pháp chế và marketing của đối tác** — chủ sở hữu bốn bài viết ở tầng 2 và nội dung trang chủ. Đây là đường găng dài nhất của một lần onboard.

**P3. Kỹ sư frontend** — hiện mất một đợt việc cho mỗi lần onboard, đồng thời nhân bản mỗi bản sửa lỗi ra 5 vị trí. Sau khi hoàn tất, chỉ tham gia khi có yêu cầu vượt ngoài lược đồ cấu hình.

**P4. Kỹ sư backend** — bổ sung một collection và bốn nhóm endpoint. Không đụng gate, sổ cái, logic tính thưởng.

**P5. Người dùng hiện hữu của 5 đối tác** — **đối tượng chịu tác động trực tiếp.** Ràng buộc: không mất phiên đăng nhập, không đứt liên kết, không suy giảm chức năng. Điều kiện thuận lợi đã xác nhận: `authToken` lưu tại `localStorage` theo origin (`utils/storage.ts:10,31`), mỗi domain giữ nguyên origin sau khi chuyển, nên **phiên đăng nhập không bị ảnh hưởng**.

**P6. DevOps** — tầng 0. Mỗi domain mới cần DNS, chứng chỉ, và ba lần đăng ký OAuth thủ công cho tới khi PC-011 hoàn tất.

---

## 4. Functional Requirements

### PC-001: Phân giải tenant theo `Host`

**Priority:** Must Have — nền tảng cho mọi yêu cầu còn lại

**Vì sao cần.** Cả 5 ứng dụng đã có 10 tuyến `/:partner/…` và logic `isOwnerPartner`; chế độ hiển thị do backend quyết bằng `res.AllowHeaderPartner = len(res.Data) > 1` (`pkg/public/service/partner.go:376`). Khác biệt white-label chỉ nằm ở một chỉ thị điều hướng. Nên `partner-app/` **không xây cơ chế phân giải mới** — nó bỏ `COMMON_PARTNER` và đọc cờ backend đã trả.

| Điều kiện | Kết quả |
|---|---|
| `Host` phân giải ra đúng một đối tác | White-label: ẩn bộ chuyển, `/` chuyển hướng tới `/<slug>` |
| `Host` phân giải ra nhiều đối tác | Đa đối tác: hiện bộ chuyển |
| `Host` không phân giải được đối tác nào | **Trang lỗi nêu rõ domain chưa đăng ký.** Không chuyển hướng |
| `PARTNER_SLUG` có giá trị | Ghi đè `Host` — môi trường phát triển |

**URL giữ nguyên `/<partner>/<slug>`.** Cả 5 ứng dụng đã dùng cấu trúc này, nên migrate không đứt liên kết và không cần bảng chuyển hướng.

#### ⚠️ Nhánh thứ ba là bắt buộc — hệ cũ rơi vào vòng lặp câm

Sai `allowDomains` hôm nay cho ra vòng lặp vô tận, không thông báo gì:

```
getDetailPartner lỗi → navigator.replacePath('/')            models/main.ts:230
'/'                  → <Redirect to={`/${COMMON_PARTNER}`} />     main-home/index.tsx:4
'/<slug>'            → getDetailPartner lỗi → '/' → …
```

Người onboard không biết mình sai ở đâu. `partner-app/` **cấm chuyển hướng khi không phân giải được đối tác** — phải dừng lại và nói ra.

**AC:**
- [ ] Hai domain trên cùng container trả hai bộ nhận diện khác nhau
- [ ] `Host` lạ hiện trang lỗi nêu domain chưa đăng ký; **không** có chuyển hướng nào
- [ ] `PARTNER_SLUG` ghi đè `Host`, có unit test cả hai nhánh
- [ ] `grep COMMON_PARTNER partner-app/src` trả về 0 kết quả
- [ ] Danh sách tuyến sau migrate trùng khớp trước migrate

---

### PC-002: Giao diện điều khiển bằng token

**Priority:** Must Have

**Vì sao đưa cả bảng màu vào cấu hình, không chỉ một màu.** Đo 157 biến SCSS trên 5 ADV: 152 biến giống hệt nhau, khác biệt thật gói trong `$primary`. Nhưng con số đó chỉ chứng minh **5 ADV hiện tại dùng chung một bản thiết kế** — không chứng minh ADV thứ sáu sẽ vậy. ADV muốn nền kem thay vì trắng, hoặc chữ ấm thay vì xám lạnh, thì `$primary` không nói được gì.

Nên lược đồ mở đủ, **mặc định đúng hiện trạng**: 18 màu và 4 giá trị bo góc, giá trị mặc định bằng đúng giá trị đang chạy. Không tốn thêm gì lúc làm — backend lưu map, frontend đổ ra CSS variable — mà không phải sửa lược đồ khi có ADV cần khác.

**Token cấu hình được:**

```
colors{}      18 khoá, lấy từ khối //Color của bootstrap-custom.scss
              primary · secondary · success · warning · danger · muted · light · lighter
              dark · green · red · sky · quaternary · tertiary · border-secondary
              button-border-secondary · violet · blue

radius{}      4 khoá     base 8px · sm 4px · lg 24px · modal 12px

fontFamily    tên font family
fontFiles[]   { family, weight, style, url }
```

`fecredit` có 3 token gradient riêng — thêm thẳng vào `colors{}` như ba khoá nữa, không cần ngăn riêng.

**Admin hiện `primary` ở trên cùng, 21 khoá còn lại gấp trong mục Nâng cao.** Đủ trường trong lược đồ không có nghĩa là đổ hết 22 ô lên màn hình.

#### ⚠️ KHÔNG có phép tính màu ở bất kỳ đâu

Bootstrap 5.2.3 tính hover và active **lúc biên dịch** bằng hàm SCSS, không chạy được trong trình duyệt:

```scss
// mixins/_buttons.scss:22-25 — phát ra HẰNG SỐ hex
--#{$prefix}btn-hover-bg: #{$hover-background};  // = shade-color($bg, 15%)
--#{$prefix}btn-color:    #{$color};             // = color-contrast($bg)
```

Đo được 90 lượt dùng `btn-primary` và `btn-outline-primary` trên 5 ADV. Nếu giữ cách này thì phải viết lại ba hàm SCSS bằng Go hoặc TypeScript, và bản viết lại sẽ lệch so với bản đang chạy.

**Không làm vậy.** Kế thừa `packages/ui/src/button.tsx` của `creator-os`:

```tsx
primary: 'bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80'
```

Hover và active **không phải màu mới** — là chính token đó ở độ mờ giảm, trình duyệt hợp thành lúc chạy. 18 màu trong cấu hình đều là **giá trị nhập vào**, không có màu nào được tính ra.

**Không nhấp nháy.** CSS variable ghi vào thuộc tính `style` của `<html>` khi SSR.

**AC:**
- [ ] Đổi `primary`, xuất bản, tải lại: giao diện đổi, không build lại
- [ ] Đổi `radius.base` từ 8 sang 0: nút và thẻ ra góc vuông, không cần sửa mã
- [ ] `grep -rE "#[0-9a-fA-F]{6}" partner-app/src` (trừ file token) trả về **0**
- [ ] `grep -rE "shade-color|tint-color|color-contrast"` trên toàn repo trả về **0**
- [ ] Tải trang throttle 3G không thấy nhấp nháy màu mặc định
- [ ] Nút hover có màu là `primary` ở độ mờ giảm — xác nhận bằng DevTools
- [ ] 5 ADV sau migrate render **giống hệt** bản cũ khi dùng giá trị mặc định — đối chiếu bằng ảnh
### PC-003: Asset theo đối tác, gồm font

**Priority:** Must Have

**Vì sao `assets` là map chứ không phải danh sách trường.** Đo 20 khoá ảnh trên 5 đối tác: **chỉ 5 khoá có ở cả 5** (`logoImage`, `logoMobileImage`, `logoBrandFooter`, `decorLeft`, `decorRight`). 15 khoá còn lại là ảnh mốc thưởng, có ở 4/5 hoặc 1/5. Khai cứng 20 trường thì đối tác thứ sáu cần khoá thứ 21 lại phải sửa lược đồ.

**Bộ lõi bắt buộc:** 5 khoá trên, cộng `favicon` và `ogImage`.
**Map mở:** phần còn lại.

**Font là asset, không phải chuỗi CSS.** Bốn font family khác nhau trên 5 ADV:

```
BeVietnamPro (hdbank, lusso) · Rosellinda (parasola) · SVN-Gilroy (vpbank) · FE Font (fecredit)
```

Nên admin phải cho **tải lên file font**, và ứng dụng sinh `@font-face` theo đối tác lúc chạy. Token `fontFamily` một mình không đủ.

**Lưu trữ:** MinIO qua service `file` hiện có.

**Kiểm URL:** nhận `http(s)://…` hoặc đường dẫn nội bộ bắt đầu bằng `/`. **Chặn** `//host` (protocol-relative — thoát khỏi origin) và mọi scheme khác (`javascript:`, `data:`).

**AC:**
- [ ] Đổi logo, xuất bản: giao diện cập nhật, không build lại
- [ ] Asset thiếu dùng mặc định của ứng dụng, không vỡ bố cục
- [ ] `javascript:` và `//evil.com` bị từ chối tại **máy chủ**, không chỉ ở form
- [ ] Tải file font: `@font-face` sinh đúng, chỉ áp cho đối tác đó
- [ ] Font chuyển sang `woff2` trong quá trình migrate

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

**`PartnerOpts` giữ nguyên chỗ cũ.** Các cờ leaderboard, `enableStaffCode`, `allowResubmitRejectedContent` không di chuyển trong suốt giai đoạn chạy song song — ứng dụng chưa migrate vẫn đang đọc chúng ở vị trí hiện tại.

**AC:**
- [ ] Tắt `contract`: mục biến khỏi nav **và** gõ URL trực tiếp bị chặn
- [ ] API cấu hình lỗi: ứng dụng vẫn render với bộ cờ mặc định
- [ ] `PartnerOpts` giữ nguyên tên trường và vị trí; ứng dụng chưa migrate đọc được như trước

---

### PC-005: Trang chủ dựng bằng section catalogue

**Priority:** Must Have

**Một landing mặc định, bám layout và tính năng của FE hiện tại** — chốt 04/09. Không dựng theme thứ hai, không chờ thiết kế mới. Bố cục và thành phần lấy từ `pages/partner-home` đang chạy, vì cả 5 ADV đã dùng chung đúng bộ component đó (`Ratio`, `AppCarousel`, `Statistics`, `AppItemsCarousel`, `EventActive`, `ContentHighlight`).

**Vì sao là mảng section chứ không phải bố cục cứng.** `creator-os` đã trả giá cho bài này: *"template cố định ⇒ section không có dữ liệu VẪN phải render ⇒ đẻ ra dữ liệu GIẢ để lấp chỗ trống"*. Bằng chứng bên họ là hằng `MOCK_QUOTES` — lời chứng thực bịa gán vào tên và ảnh đại diện của người dùng **có thật**. Ở mô hình mảng, ADV không thêm block thì block đó không tồn tại; hết ô trống để bịa.

**Danh mục:**

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

`hero` lấy ảnh từ `PartnerRaw.Covers` — đã có sẵn, upload trong admin.

**Section `dữ liệu` chỉ lưu tham số truy vấn.** `events` lưu `limit`, **không** lưu danh sách chiến dịch. Copy dữ liệu vào cấu hình là tự tạo một bản cũ không ai cập nhật.

**Mọi section biên tập bắt `items.min(1)`.** Kế thừa trực tiếp từ `creator-os`: *"đây là thứ GIẾT `MOCK_QUOTES`"*. Không có nội dung thật thì không thêm block, chứ không render khối trống rồi chờ ai đó nhét dữ liệu giả vào.

**Mọi schema `.strict()`** — trường lạ bị từ chối, không âm thầm bỏ qua.

**Điều hướng sinh từ `sections[]`.** Không có bảng nav riêng, nên xoá section là mục nav tự mất — không bao giờ có anchor chết.

**`key` bền vững.** Sửa và sắp xếp địa chỉ hoá theo `key`, **không theo chỉ số mảng**. Sắp lại thứ tự không được làm hỏng bản sửa đang chờ.

#### ⚠️ Danh mục nằm trong mã nguồn, KHÔNG nằm trong DB

Để trong DB là **hai nguồn sự thật**, và mất whitelist — ADV tự chế được loại block mới. MongoDB chỉ lưu mảng `sections`; luật kiểm nằm ở tầng ứng dụng và **chặn ở server**, không chỉ ẩn nút xoá trên giao diện.

#### ⚠️ Renderer nhận `sections[]` làm dữ liệu, KHÔNG hỏi ADV nào

Dựng đúng **một** renderer. Nhưng nó phải là `switch` trên `section.type`, tuyệt đối không có nhánh theo ADV. Nhờ vậy nếu về sau có ADV cần ngôn ngữ thị giác khác, thêm renderer thứ hai là **thêm một tệp**, không phải refactor — đúng cách `creator-os` làm với `aurora.tsx` và `brutalist.tsx`.

Đây là ràng buộc cấu trúc, không phải phần việc công việc: không dựng renderer thứ hai trong phạm vi này.

**AC:**
- [ ] Kéo đổi thứ tự, xuất bản: trang chủ đổi thứ tự
- [ ] Tắt `leaderboard`: khối **và** mục nav cùng biến mất
- [ ] Gọi thẳng API xoá section `hero`: máy chủ từ chối
- [ ] Gửi `type` ngoài danh mục: máy chủ từ chối, không ghi vào DB
- [ ] Thêm section `faq` với `items` rỗng: máy chủ từ chối
- [ ] Gửi trường lạ trong một section: máy chủ từ chối
- [ ] Sắp lại thứ tự rồi sửa một section: thao tác áp dụng đúng section
- [ ] `grep -rE "partner ===|adv ===" partner-app/src/components/landing` trả về **0**
- [ ] 5 ADV sau migrate có trang chủ **giống bản cũ** — đối chiếu bằng ảnh
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

Nguyên nhân: **`ORIGIN` gánh hai vai.** Comment ngay trong `fecredit/config/config.prod.ts` nói rõ: *"Domain API, không phải domain FE (dùng cho canonical/og:url + redirect TikTok)"*. Một biến vừa là domain callback dùng chung — **đúng cho TikTok** — vừa là domain chuẩn hoá SEO — **sai cho canonical**.

#### ⚠️ KHÔNG sửa canonical bằng cách đổi giá trị `ORIGIN`

Đổi `ORIGIN` sẽ **phá luồng đăng nhập TikTok của cả 5 ứng dụng**, vì `redirect_uri` gửi TikTok dựng từ chính biến đó và đã đăng ký một lần dùng chung.

Cách đúng là **tách hai vai**: `canonical` và `og:url` sinh từ `Host` của request; `ORIGIN` giữ nguyên giá trị, chỉ còn phục vụ callback TikTok. **`canonical` không lưu trong lược đồ.**

**`robots.txt` và `sitemap.xml` sinh theo domain.** Hiện không ứng dụng nào có hai file này; đây là năng lực mới, không phải phần việc chuyển đổi.

**AC:**
- [ ] Hai domain trả hai bộ thẻ meta khác nhau
- [ ] `canonical` và `og:url` trỏ về **chính domain đang truy cập**
- [ ] `gtmId` trống: không chèn script GTM
- [ ] `robots.txt` và `sitemap.xml` phản ánh đúng domain yêu cầu

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
| **Dữ liệu đối tác khác** | cấu hình chứa domain, hotline, email hoặc article ID đã đăng ký cho đối tác khác |

Hai cửa cuối là chốt chặn cho lỗi **đang chạy trên production**: `lusso` dùng Facebook, TikTok, YouTube, link tải app và email của HDBank; `parasola` dùng hotline của HDBank; ba ứng dụng có giá trị fallback cứng trỏ tới bài viết pháp lý của HDBank (mục 2.6).

Khi migrate, cấu hình được **trích tự động từ chính các ứng dụng đó**. Không chặn ở bước xuất bản thì các giá trị sai theo sang hệ mới và trở thành dữ liệu chính thức — khó phát hiện hơn bây giờ.

**Trường bắt buộc không có giá trị mặc định và không kế thừa.** Nguyên nhân gốc của cả hai lỗi trên là các giá trị này được **thừa hưởng** chứ không được **hỏi**.

**Khoá cache khớp tuyệt đối** giữa frontend và backend. Lệch một ký tự thì purge không trúng gì cả — xuất bản xong trang vẫn cũ và **không ai thấy lỗi**. Bắt buộc có test đối chiếu hai phía.

#### Mẫu xem trước — lấy từ `creator-os`, đã tránh sẵn open redirect

`app/api/draft/route.ts` của họ ghi rõ cái bẫy: *"Mẫu preview của nhiều CMS nhận `?slug=` rồi redirect thẳng tới đó — thành cần câu open-redirect (`?slug=//evil.com`)."*

Hai luật áp thẳng:
- **Không nhận đích đến từ URL.** Landing chỉ có một trang nên đích luôn là `/`, hằng số trong mã. Không có tham số đích thì không có gì để bẻ
- **Không tự kiểm chữ ký token.** Frontend đổi token lấy dữ liệu ở API; API trả cờ `preview: true` mới là token thật, đúng ADV, còn hạn. Sai → 401, **không** bật chế độ xem trước

#### ⚠️ Xem trước phải đi VÒNG QUA cache

Cấu hình đã xuất bản được cache Redis 4 giờ theo domain. Nếu xem trước dùng chung đường đọc đó, người vận hành sửa nháp, bấm xem trước, và **thấy bản cũ** — không hiểu vì sao, tưởng mình lưu hỏng.

Request có token xem trước phải bỏ qua cache hoàn toàn: đọc thẳng bản nháp từ cơ sở dữ liệu, và **không ghi kết quả vào cache** — ghi vào là bản nháp của một người rò sang mọi khách truy cập domain đó.

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
| Nhận diện | tên, slug, domain, `primary`, `primaryForeground`, font |
| Asset | 7 khoá lõi + file font + khoá mở rộng |
| Nội dung | 4 article ID, liên hệ, mạng xã hội, liên kết footer, liên kết tài liệu |
| SEO | title, description, keywords, GTM |
| Phân hệ | công tắc `contract`, `affiliate` |
| Trang chủ | danh sách section: thêm, xoá, kéo sắp xếp, sửa nội dung theo từng loại — **xem phân tích bên dưới** |
| Xuất bản | xem trước, xuất bản kèm changelog, lịch sử phiên bản kèm khôi phục |
| Chẩn đoán domain | xem PC-014 |
| Danh sách kiểm onboard | xem PC-014 |

#### Trình sửa section — phân tích và ước lượng

Đây là màn khó nhất của yêu cầu này. Điều kiện sẵn có thuận hơn dự kiến:

| | |
|---|---|
| antd `^4.20.0` | `Form.List` cấp sẵn `{ add, remove, **move** }` từ 4.7 — **đổi thứ tự là API có sẵn**, kéo thả chỉ là cách kích hoạt |
| Khuôn mẫu đã chạy | `partner/components/modal.tsx:244-315` — `Form.List` cho `covers`: map từng item, thêm/xoá, trường lồng `name={[field.name, 'default']}`. **~75 dòng** |
| Thư viện kéo thả | `@dnd-kit/core`, `@dnd-kit/sortable`, `react-dnd`, `react-sortable-hoc` **đã cài, chưa dùng dòng nào** |
| Component form dùng lại | 15 cái: `form-input` · `form-select` · `form-editor` · `form-upload-one-file` · `form-input-number` … |

**Phần thật sự mới: item không đồng nhất.** `covers` dễ vì mọi item cùng hai trường. Section thì mỗi `type` một form khác — cần `switch` theo `type` bên trong `fields.map`.

| Nhóm | Loại | Dựng bằng |
|---|---|---|
| Tầm thường | `statistic` · `creator-newest` · `steps` | `form-input` |
| Dễ | `events` · `content-highlight` · `leaderboard` | `form-input` + `form-input-number` |
| Dễ | `hero` | `form-input` ×3 |
| Trung bình | `banner` | `form-upload-one-file` — đã có |
| **Khó nhất** | `faq` | `Form.List` **lồng trong** `Form.List`, đường dẫn `['sections', i, 'items', j, 'question']` |

**Bốn chỗ dễ vấp:**

1. **Sắp xếp bằng `move()`, không tự sửa mảng.** `Form.List` giữ trạng thái nội bộ; sửa mảng bên ngoài là form mất đồng bộ
2. **`key` bền vững KHÁC `field.key` của antd.** `field.key` là chỉ số nội bộ, đổi khi sắp xếp. `key` trong lược đồ phải sinh lúc thêm và giữ nguyên suốt đời — lẫn hai cái là sửa nhầm section
3. **Thêm phải chọn `type` trước** rồi mới `add({ key: sinhMới(), type })`, vì form con phụ thuộc `type`
4. **Ẩn nút xoá `hero`/`events` là UX, không phải guard.** Server vẫn phải từ chối (PC-005). Hai nơi cùng đọc một danh mục, nếu không thì admin cho xoá rồi server chặn

**Ước lượng ~960 dòng, 6–8 ngày** kể cả kiểm thử — khoảng gấp đôi `partner/modal.tsx` (454 dòng).

**Xếp sau bước 3, không nằm trên đường găng.** Không ADV nào trong 5 cần màn này để migrate — landing của cả 5 giữ nguyên, `sections[]` do PC-016 trích và seed. Làm sau khi `hdbank` migrate xong: nếu bước 3 lộ ra lược đồ section cần đổi, sửa lược đồ trước khi có UI bám vào thì rẻ hơn nhiều.

**Người dùng là P1, không phải kỹ sư.** Nhãn tiếng Việt rõ nghĩa; ô màu có bảng chọn chứ không bắt gõ hex trần; thông báo lỗi nói **sai gì và sửa thế nào**, không phải tên trường kỹ thuật.

**Nghiệm thu bằng một buổi làm thật, không phải đọc code.** P1 tạo và xuất bản một đối tác từ đầu tới cuối, không hỏi ai.

**AC:**
- [ ] P1 hoàn thành tạo và xuất bản một đối tác mà không cần hỗ trợ
- [ ] Mọi kiểm tra ở máy chủ đều có thông báo tương ứng trên biểu mẫu — không để lỗi trần lọt lên
- [ ] Ô màu xem được kết quả ngay trong admin
- [ ] Màn chẩn đoán cảnh báo khi một domain được khai ở nhiều đối tác

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

Thay đổi backend giữ tương thích ngược suốt giai đoạn chạy song song — ứng dụng chưa migrate vẫn gọi cùng bộ endpoint.

**AC:**
- [ ] Mỗi đợt: khôi phục về ứng dụng cũ trong **dưới 15 phút**, có diễn tập trước cutover
- [ ] Hình dạng response của endpoint public giữ nguyên
- [ ] Không thời điểm nào có hai hệ cùng phục vụ một domain

---

### PC-011: Uỷ quyền OAuth trên nhiều domain

**Priority:** Should Have

**Vì sao cần.** Lời hứa "onboard không cần dev" đúng với TikTok, không đúng với hai nhà cung cấp còn lại:

| Nhà cung cấp | Cơ chế hiện tại | Thêm domain cần gì |
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
- [ ] Luồng TikTok không thay đổi hành vi — đối chiếu trước/sau trên một domain thật

---

### PC-012: Gộp 5 bản về một

**Priority:** Must Have

22 file có đủ 5 phiên bản. Chia ba nhóm, và **chỉ nhóm ba mới đắt**:

| Nhóm | File | Ai quyết |
|---|---|---|
| Chuyển thành cấu hình | `wrappers/home.tsx`, `configs/app.ts`, `configs/image.ts`, `bootstrap-custom.scss`, footer | Kỹ sư, ghi lý do trong commit |
| Trôi do copy | `configs/api.ts` (khác **thứ tự khai báo**, nội dung y hệt), `utils/helper.ts`, `app.tsx` | Kỹ sư, chọn bản đầy đủ nhất |
| **Khác biệt hành vi** | `not-logged-in`, `header`, `models/main.ts`, `interfaces/event.ts` | **Không có đáp án kỹ thuật** |

Nhóm ba: mỗi trường hợp phải có quyết định ghi nhận, nêu rõ **đối tác nào thay đổi hành vi** và hình thức xử lý. Đối tác bị ảnh hưởng phải được thông báo **trước** cutover, không phải sau.

Duy trì bảng theo dõi quyết định, cập nhật **cùng commit** với thay đổi mã nguồn — không cập nhật sau.

**AC:**
- [ ] Toàn bộ 22 file được phân loại và có quyết định ghi nhận
- [ ] Mọi trường hợp nhóm ba có xác nhận từ đối tác trước cutover
- [ ] Bảng theo dõi cập nhật cùng commit

---

### PC-013: Migrate và cutover theo đợt

**Priority:** Must Have

**Điều kiện vào cutover:**
- Cấu hình của đối tác đã khởi tạo và xuất bản ở staging
- Bộ ảnh đối chiếu trước/sau hoàn tất cho từng màn × từng đối tác (NFR-007)
- PC-012 xong cho phạm vi file đợt chạm tới
- **Mọi giá trị "trích rồi xác minh" có xác nhận từ đối tác** — liên hệ, mạng xã hội, article ID
- Diễn tập khôi phục thành công

**Điều kiện nghiệm thu:** hai tuần vận hành không sự cố P1/P2 liên quan tới migrate.

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

Cái `setup.md` **chưa** giải quyết: nó là file markdown trong repo, mỗi đối tác một bản chép tay, và không có gì đối chiếu nó với trạng thái thật trong cơ sở dữ liệu. Thất bại đầu tiên khi làm thiếu vẫn là vòng lặp chuyển hướng câm (mục 2.7).

**Ba thứ phải có:**

**Chẩn đoán domain.** Tra một domain, biết nó phân giải ra đối tác nào. Cảnh báo khi nhiều đối tác cùng khai một domain — sai `allowDomains` hôm nay làm site **tự đổi sang chế độ đa đối tác**, hiện bộ chuyển và cho thấy đối tác lạ, mà không báo lỗi gì.

**Danh sách kiểm bảy tầng.** Hiển thị trạng thái từng tầng cho một đối tác: bản ghi nền → 4 bài viết → cấu hình ứng dụng → danh mục → ít nhất một chiến dịch → cờ nghiệp vụ → nhân sự quản trị. Mỗi mục nêu **còn thiếu gì** và mở được màn tương ứng.

**Trạng thái "đang dựng".** Hiện `status=active` bật ngay, nên đối tác chưa xong tầng 2–4 vẫn phục vụ lưu lượng — người dùng vào thấy site chưa có điều khoản hoặc chưa có chiến dịch nào.

**AC:**
- [ ] Tra domain chưa đăng ký: nêu rõ không phân giải ra đối tác nào
- [ ] Domain khai ở hai đối tác: hiện cảnh báo
- [ ] Danh sách kiểm phản ánh đúng trạng thái từng tầng — kiểm bằng một đối tác dựng dở
- [ ] Đối tác "đang dựng" không phục vụ lưu lượng công khai

---
### PC-015: Phân quyền cho màn cấu hình

**Priority:** Must Have — yêu cầu mới tại v1.4

**Vì sao cần.** PC-008 giao màn cấu hình cho đội vận hành, nhưng hiện **chỉ `root` ghi được bản ghi ADV** (`pkg/admin/router/partner.go` — `Create`, `Update`, `ChangeStatus`, `GetDetail` đều nằm trong nhóm `gRoot`). Cấp `root` cho vận hành nghĩa là họ tạo, xoá và đổi trạng thái được **mọi ADV**.

#### ⚠️ Hệ scope 20 mã đang KHÔNG chặn ở server ở đâu

`RoleRaw` có trường `Scopes []constants.Scope`. `constants.ListScopes` khai 4 nhóm × 5 quyền = **20 mã**. Admin có API trả danh sách (`handler/common.go:110`) và có màn gán quyền cho vai trò.

Nhưng `grep -rn "\.Scopes"` trên toàn backend (bỏ test) **không có kết quả**. Kiểm quyền thật nằm ở so sánh chuỗi:

```go
// routeauth/auth.go:85
if role.Code != constants.StaffRole.Admin { return cc.Response401(...) }
```

Nghĩa là người vận hành tick 20 ô quyền, lưu thành công, và **không ô nào có tác dụng**. Ghi ra đây để người thiết kế phân quyền không tưởng nó đang bảo vệ cái gì.

Thêm nữa, mọi vai trò hiện có `Scopes` **rỗng** (`dummy_db.go:82` seed `make([]constants.Scope, 0)`). Bật chặn ở server lên mà không backfill trước thì **mọi admin không phải root mất sạch quyền ngay lập tức** — đó là thay đổi phải đi kèm một đợt di dữ liệu, không phải một commit.

**Phạm vi của yêu cầu này — hẹp có chủ đích:**

| Làm | Không làm |
|---|---|
| Thêm vai trò `config_editor` vào `StaffRole` | Kích hoạt hệ scope 20 mã |
| Guard mới cho 5 endpoint `app-config` | Chặn ở server `staff.Partner` trong 12 service admin cũ |
| Kiểm `staff.Partner` **chỉ trong** các endpoint cấu hình mới | Đổi hành vi của bất kỳ endpoint đang chạy nào |

Hai cột phải là task riêng có kế hoạch di dữ liệu. Gộp vào dự án hợp nhất frontend là mở hai mặt trận cùng lúc.

**Ràng buộc theo ADV hiện chắp vá.** `staff.Partner` được kiểm ở đúng hai vùng — `handler/leaderboard_view.go:123,131` và `service/event_bonus.go` (5 chỗ). Event, content, article, category, news, quick-action đều **không kiểm**. Yêu cầu này không sửa việc đó, chỉ bảo đảm endpoint mới không lặp lại.

**AC:**
- [ ] `config_editor` của ADV X đọc và ghi được `app-config` của X
- [ ] `config_editor` của ADV X gọi `app-config` của ADV Y → **401**
- [ ] `config_editor` **không** tạo, xoá hay đổi trạng thái được ADV nào
- [ ] `root` giữ nguyên mọi quyền hiện có
- [ ] Không endpoint nào đang chạy đổi hành vi — đối chiếu bằng danh sách route trước/sau

---

### PC-016: Công cụ trích cấu hình từ ứng dụng hiện hành

**Priority:** Must Have — yêu cầu mới tại v1.4

**Vì sao cần.** PC-013 đặt điều kiện *"mọi giá trị trích ra phải được ADV xác nhận"* nhưng không nói **trích bằng gì**. Mỗi ADV có ~22 giá trị màu, ~20 khoá ảnh, 3 mã bài viết, bộ liên hệ, mạng xã hội, font. Nhân 5 ADV. Gõ tay là sai số chắc chắn, và sai ở đây là dữ liệu sai đi thẳng vào production.

**Công cụ đọc:**

| Nguồn | Lấy ra |
|---|---|
| `<adv>/src/bootstrap-custom.scss` | 18 màu + 4 bo góc |
| `<adv>/config/config.prod.ts` | slug, domain, 3 mã bài viết |
| `<adv>/src/configs/image.ts` | danh sách khoá ảnh |
| `<adv>/src/font.scss` + `assets/fonts/` | font family + danh sách file |
| `<adv>/src/components/app/image/constants.ts` | liên kết mạng xã hội |
| `<adv>/src/pages/contact/index.tsx` | hotline, email |
| cấu trúc `<adv>/src/pages/` | cờ phân hệ |

**Xuất ra:** một file JSON đúng lược đồ `PartnerAppConfigBody`, kèm **cột nguồn** cho từng giá trị — trích từ file nào, dòng nào.

#### ⚠️ Trích xong KHÔNG được nhập thẳng

`lusso` đang mang Facebook, TikTok, YouTube, liên kết tải ứng dụng và email của HDBank; `parasola` mang hotline của HDBank (mục 2.6, PRE-3). Script trích được thì ai cũng muốn nhập thẳng — nhưng làm vậy là **hợp thức hoá lỗi**, và lúc đó nó nằm trong cơ sở dữ liệu chứ không nằm trong mã nguồn, khó thấy hơn hôm nay.

Nên đầu ra của công cụ là **bản nháp chờ xác minh**, không phải bản xuất bản. Kiểm tra chéo của PC-007 là chốt chặn cuối; công cụ này phải đánh dấu sẵn những giá trị trùng với ADV khác để người xác minh biết chỗ cần hỏi.

**AC:**
- [ ] Chạy trên `hdbank` sinh ra JSON hợp lệ theo lược đồ, nạp được vào bản nháp
- [ ] Mỗi giá trị có cột nguồn `tệp:dòng`
- [ ] Giá trị trùng với ADV khác bị đánh dấu, kèm tên ADV bị trùng
- [ ] Chạy trên cả 5 ADV không lỗi
- [ ] Đầu ra **không** tự động xuất bản

---

### PC-017: Nội dung tĩnh — hai phạm vi, không gộp

**Priority:** Must Have

**Vì sao phải nói rõ.** Brief dự án ghi *"nội dung tĩnh (thể lệ, hướng dẫn) quản lý per-ADV trong admin"*. Đọc mã thì thấy **gộp nhầm hai phạm vi**, và làm theo nguyên văn sẽ phá mô hình nhiều chiến dịch.

#### Thể lệ và Hướng dẫn là per-CHIẾN DỊCH — giữ nguyên, không đụng

```go
// internal/model/mg/event.go:31-32
Guide   AppID   // → GuideContent
Privacy AppID   // → PrivacyContent
```

Backend nạp hai bài này khi trả chi tiết chiến dịch (`pkg/public/service/event.go:1374-1390`, hai goroutine song song). Frontend đọc `eventHome?.guideContent?.title` (`not-logged-in/index.tsx:275`).

Form admin **đã có sẵn** ô chọn: `admin/src/pages/event/components/overview.tsx:190` (`guide`) và `:198` (`privacy`).

Một ADV chạy nhiều chiến dịch với thể lệ khác nhau — đó là lý do hai bài này gắn với chiến dịch. **Kéo lên per-ADV là làm hỏng.** Yêu cầu này: không thay đổi gì.

#### Q&A, Điều khoản, Chính sách là per-ADV — vào cấu hình

Ba bài này không đổi theo chiến dịch, hiện là biến build-time dùng làm link `/bai-viet/<id>` ở header và footer.

```
content.articleIds { qa, term, condition }
```

`SUPPORT_ARTICLE_ID` **không nằm trong danh sách** — `fecredit/setup.md` xác nhận *"env này code không đọc"*, bị comment ở `src/configs/app.ts:60` và header, cả ba app. Thể lệ và Hướng dẫn trên frontend lấy từ chiến dịch, không phải từ env này.

Trong `partner-app` là ba ô chọn bài viết trong màn cấu hình, dropdown lấy từ danh sách bài đã có (`admin/src/pages/article/`). Bắt buộc, chặn xuất bản nếu trống (PC-007).

#### Hệ quả cho lịch onboard

Một ADV mới chạy hai chiến dịch phải soạn **7 bài**, không phải 3:

```
3 bài per-ADV          Q&A · Điều khoản · Chính sách
2 bài × 2 chiến dịch   Thể lệ · Hướng dẫn
```

Đây là việc của pháp chế và marketing, không cấu hình nào rút ngắn được — và là đường găng dài nhất của tầng 2 trong bảy tầng onboard (mục 2.7).

**AC:**
- [ ] `EventRaw.Guide` và `EventRaw.Privacy` giữ nguyên; form chiến dịch trong admin không đổi
- [ ] Ba ô chọn bài viết per-ADV trong màn cấu hình, dropdown từ danh sách bài đã có
- [ ] Thiếu bất kỳ trong ba: chặn xuất bản
- [ ] Không có `SUPPORT_ARTICLE_ID` trong lược đồ
- [ ] Danh sách kiểm onboard (PC-014) đếm đúng số bài cần soạn theo số chiến dịch

---

## 5. Non-Functional Requirements

### NFR-001: Tương thích ngược trong giai đoạn chạy song song
Hình dạng response của endpoint public giữ nguyên cho tới khi đợt cuối nghiệm thu.

### NFR-002: Không nhân bản luật nghiệp vụ ra frontend
Điều kiện tính thưởng, gate nộp bài, luật xét duyệt tiếp tục ở backend.

### NFR-003: Khả năng chịu lỗi
API cấu hình lỗi hoặc chậm → dùng bản cache gần nhất; không trả trang trắng.

### NFR-004: Hiệu năng và kích thước gói
SSR phát sinh tối đa một request cấu hình mỗi request trang, tỷ lệ trúng cache cao. Yêu cầu **code splitting theo route và tải theo cờ phân hệ** — hiện không ứng dụng nào bật `dynamicImport`. Ngưỡng xác lập sau lần build đầu tiên.

### NFR-005: Ngôn ngữ
Toàn bộ tiếng Việt.

### NFR-006: Chất lượng hiển thị
Vỡ bố cục, tràn văn bản, chồng lớp, sai lệch trên di động là lỗi chặn nghiệm thu. Mỗi màn kiểm tra trực quan trên cả desktop và di động, với tối thiểu hai bộ token tương phản.

### NFR-007: Đường cơ sở hồi quy
Repository hiện không có đường cơ sở (`hdbank`, `parasola` mỗi ứng dụng một file kiểm thử). Trước mỗi đợt migrate, thiết lập bộ ảnh đối chiếu cho từng màn × từng đối tác, chụp từ ứng dụng cũ đang chạy.

Kiểm thử tự động bắt buộc cho: kiểm tra schema section, kiểm tra chéo dữ liệu đối tác, resolve partner theo domain theo `Host`, đối chiếu khoá cache hai phía.

### NFR-008: Bán kính ảnh hưởng và observability
Sau hợp nhất, một sự cố tác động 5 đối tác thay vì 1. Yêu cầu:
- Mọi bản ghi nhật ký gắn định danh domain và đối tác, từ ngày đầu
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

## 6. Ba bước và thứ tự làm

Cấu trúc theo brief dự án (3 bước), không theo epic rời.

### Bước 1 — Phân tích và thiết kế

| Đầu ra | Trạng thái |
|---|---|
| PRD + sơ đồ kiến trúc | Tài liệu này |
| Mô hình cấu hình: branding, domain & routing, nội dung tĩnh, feature flag, phân quyền | PC-002 → PC-008, PC-015 |
| Danh sách ADV sẽ migrate | 5 ADV, mục 2.5 |
| Thiết kế landing | **Bám layout và tính năng của FE hiện tại** — chốt 04/09, không chờ Figma mới (PC-005) |

### Bước 2 — Dựng khung và lớp cấu hình

| # | Nội dung | Phụ thuộc |
|---|---|---|
| E1 | Backend: collection `PartnerAppConfig`, phiên bản, endpoint đọc theo domain, xoá cache | — |
| E2 | `partner-app` khởi tạo + PC-001 + PC-002 + PC-003 | E1 |
| E3 | Admin: cấu hình + PC-007 + PC-014 + PC-015 | E1 |
| E4 | 18 màn lõi + hạ tầng dùng chung. **Ưu tiên `home`, `ekyc`, `account` ở đầu epic** (28% khối lượng) | E2 |
| E5 | PC-005 section catalogue + màn Trang chủ trong admin | E3, E4 |
| E6 | PC-004 + màn `contract` | E4 |
| E7 | 2 màn affiliate của `fecredit` | E6 |
| E8 | PC-016 công cụ trích cấu hình | E1 |

**Mốc nghiệm thu bước 2: chạy được với một ADV mẫu nội bộ.** Không ADV thật nào được migrate. Mốc này tách bạch *"khung chạy được"* khỏi *"ADV thật chạy được"* — thiếu nó thì không có điểm dừng để đánh giá trước khi đụng production.

### Bước 3 — Migrate 01 ADV mẫu

**Chọn `hdbank`** — branding đơn giản nhất trong 5:

```
hdbank    5 màu riêng · BeVietnamPro · không gradient
lusso     6 màu riêng · BeVietnamPro
vpbank    6 màu riêng · SVN-Gilroy
parasola  12 màu riêng · Rosellinda
fecredit  63 màu riêng · FE Font · 3 gradient
```

Thêm một lý do: `hdbank` là bản gốc mà `lusso` và `parasola` được copy ra, nên cấu hình của nó **sạch nhất** — không mang dữ liệu của ADV nào khác. `lusso` để sau `hdbank` để có bản đúng làm chuẩn đối chiếu.

Mục tiêu của bước này là **xác thực mô hình cấu hình đủ dùng**, không phải hoàn thành migrate.

### Sau bước 3 — các đợt còn lại

```
lusso  →  parasola  →  vpbank  →  fecredit
```

Mỗi đợt tuân thủ PC-013. `fecredit` để cuối: xa nhất về khoảng cách (118–154), có 2 màn affiliate và 3 token gradient riêng.
## 7. Kiến trúc

```
Trình duyệt → <domain đối tác>
   │
   ▼ partner-app: đọc Host  (hoặc PARTNER_SLUG — PC-001)
   │
   ▼ GET /api/public/partners/app-config?domain=…      [Redis 4h — đã có]
   │      └─ ?preview=<token> → trả bản draft (PC-007)
   │
   ▼ Render phía máy chủ
   │   ghi CSS variable vào style của <html>            → không FOUC (PC-002)
   │   sinh title / favicon / OG / canonical theo Host / GTM  (PC-006)
   │
   ▼ Render phía trình duyệt
       ThemeProvider   → component đọc token, hover bằng ĐỘ MỜ
       FeatureFlags    → ẩn nav và chặn tuyến theo cờ  (PC-004)
       sections[]      → render theo thứ tự; nav sinh từ đây (PC-005)

admin (umi 3 + antd 4)
   │  chỉnh nháp → Xem trước → Xuất bản → sinh phiên bản + xoá cache
   ├─ chẩn đoán domain + danh sách kiểm 7 tầng (PC-014)
   └─ Khôi phục phiên bản trước
```

### Bốn đường cấu hình xuống component

Không có một "config object" duy nhất. Bốn thứ này có ràng buộc khác nhau nên đi bốn đường — kế thừa cách `creator-os` tổ chức:

| Đường | Chở gì | Cơ chế |
|---|---|---|
| **CSS variable** | 18 màu, 4 bo góc, font | Ghi thẳng vào `style` của `<html>` trong `layout.tsx`, **không qua provider** |
| **ThemeProvider** | logo, tên thương hiệu — dùng làm **dữ liệu**, không phải kiểu dáng | `useTheme()` trong component |
| **Props từ Server Component** | cờ bật/tắt nút social | Đọc env lúc chạy ở layout, truyền xuống |
| **Dữ liệu SSR** | `sections[]`, campaigns | Fetch một lần, truyền vào renderer |

**Vì sao tách CSS variable khỏi provider** — comment trong `creator-os/providers.tsx` nói thẳng: *"CSS-var thật đã ghi thẳng lên `<html>` ở layout (không phụ thuộc provider để tránh FOUC)"*. Màu đi qua React context thì trang render một nhịp bằng màu mặc định rồi mới đổi.

#### ⚠️ KHÔNG dùng `NEXT_PUBLIC_*`

`NEXT_PUBLIC_*` bị nướng vào bundle lúc build — đổi giá trị phải build lại, đúng cái bệnh đang chữa. Đọc env trong Server Component thì mỗi lần chạy đọc lại. `creator-os` ghi rõ lý do này trong `providers.tsx`.

#### Validate lại ở frontend, không tin backend

Backend đã kiểm lúc ghi. Frontend kiểm lại lúc đọc, vì dữ liệu có thể đã nằm trong DB từ trước khi có luật, hoặc ai đó sửa tay. Hỏng thì rơi về mặc định — **không trắng trang**.

### BFF proxy — bắt buộc

Browser **không** gọi thẳng backend. Mọi request đi qua `app/api/[...path]/route.ts` của `partner-app`.

Lý do không phải kiến trúc cho đẹp, mà là một cái bẫy `creator-os` đã vấp: dùng `rewrites()` trong `next.config` thì `process.env.API_ORIGIN` bị nội suy **lúc build** và nướng cứng vào `.next/routes-manifest.json` — đặt env lúc `docker run` không có tác dụng, mỗi môi trường phải build một image riêng. Route handler đọc env **mỗi request** nên một image chạy được mọi môi trường.

Bắt buộc `export const dynamic = 'force-dynamic'` — proxy bị cache thì người dùng này đọc được dữ liệu của người dùng khác.

### Thay đổi hạ tầng chạy

Mỗi ứng dụng hiện chạy `server.js` (Koa) để SSR, `Dockerfile` build `node:14.17.3` rồi `node server.js`. `partner-app` là Next.js — **Koa và `server.js` biến mất**, cách build và chạy container đổi hoàn toàn. Đây là phần việc devops phải biết trước khi tới E2.

**Endpoint bổ sung — toàn bộ là thêm mới:**
- `GET /api/public/partners/app-config` — cấu hình `published` theo domain, hoặc `draft` khi có token xem trước
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
- Kiểm tra schema section, chặn ở server section bắt buộc (BH-2)
- Kiểm tra URL asset (PC-003)
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
- Một image, một triển khai, nhiều domain
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

1. Domain đối tác tiếp tục kết thúc trên hạ tầng nội bộ, như 5 domain hiện hành
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
| `portal-creator/app/layout.tsx` | **PC-002** | Áp dụng cách chèn CSS variable khi SSR |
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
| Giữ `umi 3` hay đổi nền tảng? | **Đổi**, và không nhẹ hoá chi phí. Căn cứ: `node:14.17.3` hết hỗ trợ 04/2023, `node-sass 4` ngừng phát triển, và 5 app dù ở nền tảng nào cũng phải gộp về một bản. Nhưng đây là **viết lại tầng routing và state** — 74/194 file bám `'umi'`, 27 route, 41 file dùng dva (mục 2.1). Phần rẻ chỉ nằm ở lớp giao diện |
| Một triển khai chung hay tách theo đối tác? | **Một triển khai**, phân giải theo `Host`, giữ `PARTNER_SLUG` để tách khi cần |
| Phạm vi đối tác? | **5 đối tác đang hoạt động.** Mười thư mục còn lại không thuộc phạm vi và không bị đụng (04/09) |
| Phạm vi màn hình? | **21 màn** — 18 lõi, `contract`, 2 affiliate |
| Có cần slot override? | **Không.** Không đối tác nào trong 5 có màn hình hình dạng riêng |
| Có cần chế độ đa đối tác? | **Không cần xây thêm** — cả 5 domain phân giải ra một đối tác. Cờ `AllowHeaderPartner` đã có, giữ nguyên |
| Màu dẫn xuất tính ở đâu? | **Không tính ở đâu cả.** Hover và active dùng độ mờ của cùng token (mục 2.4) |
| Có tách thư viện dùng chung? | **Không.** Vì không còn phép tính nào để dùng chung, và chỉ có một app FE |
| Cấu hình có hiệu lực ngay hay qua duyệt? | **Nháp → xem trước → xuất bản**, có lịch sử và khôi phục |
| Ai vận hành màn cấu hình? | **Đội vận hành.** Nghiệm thu bằng phiên thao tác thực tế |
| Màn cấu hình dựng trên nền tảng nào? | **`admin/` hiện hành** (umi 3 + antd 4) |
| URL có đổi sau migrate? | **Không.** Cấu trúc `/<partner>/<slug>` đã dùng ở cả 5 |
| Người dùng có bị đăng xuất? | **Không.** `authToken` ở `localStorage` theo origin, mỗi domain giữ nguyên origin |

---

## 13. Open Questions

1. **Ngưỡng blast radius** — số đối tác tối đa trên một triển khai trước khi cần tách. Cần trước khi lên production.
3. **Chủ sở hữu quy trình NFR-009** — ai quyết định phân loại một yêu cầu riêng của đối tác. Cần trước M2.
3. **PC-012 nhóm khác biệt hành vi** — 4 file (`not-logged-in` Δ914, `header` Δ659, `models/main` Δ288, `interfaces/event` Δ251) cần **đối tác chấp thuận** trước cutover. Chưa xác định đầu mối phía 5 đối tác. Cần trước M1.

### Đã đóng

| Câu hỏi | Kết luận | Ngày |
|---|---|---|
| Link Zalo giống hệt ở 4 đối tác — hằng số nền tảng hay lỗi copy? | **Lỗi copy, đã biết.** `fecredit/setup.md`: *"Zalo OA + nhóm Zalo cộng đồng + group Facebook vẫn là link của Parasola — chờ ADV cấp link FE Credit"* | 04/09 |
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
| 1.0 | 2026-09-03 | Bản đầu. Chốt phương án ứng dụng mới trên nền tảng hiện đại, backend giữ nguyên, `creator-os` là tài liệu tham khảo. Phạm vi khi đó: 15 ứng dụng, giữ nguyên không migrate |
| 1.1 | 2026-09-04 | Đổi phạm vi sang migrate toàn bộ 15 ứng dụng theo 6 đợt. Bổ sung PC-011 → PC-013, NFR-007 → NFR-009. Sửa PC-001 theo mô hình domain → tập đối tác |
| 1.6 | 2026-09-04 | Bổ sung **PC-017 — nội dung tĩnh, hai phạm vi**: Thể lệ và Hướng dẫn là per-chiến-dịch (`EventRaw.Guide`/`Privacy`, form admin đã có) và **không kéo lên per-ADV**; chỉ Q&A, Điều khoản, Chính sách là per-ADV. Đây là mục thứ năm của mô hình cấu hình theo brief, trước đó chỉ nằm ở Revision History. Ghi hệ quả lịch: ADV chạy 2 chiến dịch cần soạn **7 bài**, không phải 3. Bổ sung **phân tích và ước lượng trình sửa section** vào PC-008 — antd 4.20 có sẵn `Form.List.move()`, khuôn mẫu `covers` 75 dòng, 4 thư viện kéo thả đã cài chưa dùng; ước ~960 dòng, 6–8 ngày; **xếp sau bước 3**, không nằm trên đường găng |
| 1.5 | 2026-09-04 | Bổ sung **mục 2.9 — bản đồ chuyển umi → Next**: bảy hệ con phải viết lại, đối chiếu với lời giải của `creator-os`; bốn bài học họ đã trả giá (`rewrites()` nướng env lúc build · proxy phải `force-dynamic` · refresh single-flight · 403 pwreset tách khỏi 401); **chốt giữ `localStorage`** cho auth, nhưng **lấy BFF proxy**. Sửa lại đánh giá chi phí chuyển nền tảng — trước đó đo `getInitialProps` là đo sai đối tượng. Bổ sung **PRE-6** (mỗi trang nạp hai container GTM, ba ADV bắn vào container của ADV khác) và **PRE-7** (hai bản Bootstrap trên cùng trang). Bổ sung mẫu xem trước không open-redirect vào PC-007 và BFF proxy vào mục 7 |
| 1.4 | 2026-09-04 | Cấu trúc lại mục 6 theo **ba bước của brief dự án**; ADV mẫu bước 3 = **`hdbank`** (branding đơn giản nhất: 5 màu riêng, không gradient). Bổ sung mốc *chạy được với một ADV mẫu nội bộ* làm điều kiện nghiệm thu bước 2. **PC-002**: token từ 2 màu lên **18 màu + 4 bo góc**, mặc định bằng giá trị đang chạy — sửa lỗi rút gọn dựa trên 5 ADV vốn dùng chung một bản thiết kế. **PC-005**: chốt **một landing mặc định bám layout và tính năng của FE hiện tại**, không dựng theme thứ hai; thêm ràng buộc renderer nhận `sections[]` làm dữ liệu, không nhánh theo ADV. Bổ sung **PC-015** (phân quyền — ghi rõ hệ scope 20 mã không chặn ở server ở đâu) và **PC-016** (công cụ trích cấu hình). Bổ sung **chỉ số thành công** vào mục 1, **bốn đường cấu hình xuống component** và **thay đổi hạ tầng chạy** vào mục 7, quy tắc **xem trước đi vòng qua cache** vào PC-007, ánh xạ **ADV ↔ partner** vào mục 0. Xoá mục E0 — các phần việc đó hệ mới không mang theo. Đổi thuật ngữ tự dịch sang từ dev dùng thật |
| 1.3 | 2026-09-04 | Đính chính theo `fecredit/setup.md` — checklist onboard thật do người thực hiện viết. Gỡ ba env chết khỏi lược đồ (`APP_NAME`, `documentShareLink`, `accesstradePartnerId` — không component nào đọc); article ID từ **4 xuống 3** (`SUPPORT_ARTICLE_ID` code không đọc; Thể lệ và Hướng dẫn lấy từ `eventHome.ruleContent`/`guideContent`, dán vào event trên admin). PC-014 viết lại thành **điện tử hoá `setup.md` sẵn có**. **PRE-1: quyết định giữ nguyên luồng TikTok** (04/09), gỡ khỏi tiền đề chặn E2; PC-011 thu về Google và SSO. PC-006 thêm cảnh báo `ORIGIN` gánh hai vai. Đóng 5 câu hỏi mở |
| 1.2 | 2026-09-04 | Viết lại mục 4 theo văn phong của [prd-staff-code-frontend](../employee-code/prd-staff-code-frontend-2026-09-03.md): mỗi FR mở bằng **Vì sao cần**, bẫy đã kiểm chứng nâng thành tiêu đề con `#### ⚠️`, bằng chứng `file:line` đặt ngay trong FR thay vì dồn về mục 2. **Thu hẹp phạm vi còn 5 đối tác đang hoạt động** (`hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`); 10 thư mục còn lại thuộc đối tác đã ngừng, không thuộc phạm vi. Màn hình 33 → 21, đợt migrate 6 → 4, file khác nhau 33 → 22. **Gỡ PC-009** (slot override) — không còn consumer. **Đổi PC-002**: loại bỏ toàn bộ phép tính màu, hover và active dùng độ mờ theo mô hình `packages/ui/src/button.tsx` của `creator-os`; token cấu hình rút còn `primary` + `primaryForeground` do đo được 152/157 biến SCSS là đồng nhất. Bổ sung **PC-014** (chẩn đoán domain, danh sách kiểm onboard, trạng thái "đang dựng") suy từ phân tích bảy tầng onboard. Bổ sung **NFR-010** (cổng CI chặn giá trị gán cứng) và **NFR-011** (cổng kiểm tra kiểu). Bổ sung mục 2.4 (quyết định về phép tính màu), 2.6 (năm lỗi production), 2.7 (bảy tầng onboard), 2.8 (trạng thái chất lượng mã nguồn) |
