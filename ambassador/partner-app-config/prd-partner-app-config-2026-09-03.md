# Product Requirements Document: Hợp nhất frontend đối tác trên nền cấu hình lúc chạy (`partner-app/`)

**Date:** 2026-09-03 (cập nhật 2026-09-04)
**Author:** Nguyễn Đăng Định
**Version:** 2.2
**Reviewer:** _chưa có_
**Project Level:** Level 4 — ứng dụng mới + mở rộng backend + mở rộng admin + migrate 5 hệ thống đang chạy
**Status:** Đang triển khai — bước nền cấu hình backend và màn hình admin đã xong, đã chạy thử đầu-cuối
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

### 2.6 Lỗi đang chạy trên production — phải sửa trước, ngoài phạm vi tài liệu này

Phát hiện trong quá trình khảo sát. Không do việc hợp nhất tạo ra; cần xử lý như task độc lập, là tiền đề của E2.

**Trạng thái tại v1.9 — KHÔNG mục nào được vá.**

Dự án này làm trên thư mục mới; **không sửa mã của 5 ứng dụng đang chạy**. Toàn bộ mục dưới
đây là *phát hiện*, ghi lại để chủ sở hữu quyết định xử lý ở đâu và lúc nào — chúng là task
độc lập, không thuộc phạm vi tài liệu này.

| Mục | Ảnh hưởng | Hệ mới có mang theo không |
|---|---|---|
| PRE-1 điều hướng mở ở luồng TikTok | chiếm tài khoản, 5 app × 2 trang | **có** nếu port nguyên xi — xem cảnh báo dưới |
| PRE-2 dự phòng cứng article ID | hiển thị văn bản pháp lý của ADV khác | **không** — PC-007 bắt buộc khai, không có dự phòng |
| PRE-3 dữ liệu HDBank trên site khác | sai dữ liệu hiển thị | **không** — PC-007 chặn xuất bản, đã kiểm bằng E2E |
| PRE-4 canonical sai domain | SEO, 20 chỗ trên 5 app | **không** — sinh từ `Host` |
| PRE-5 biến toàn cục theo request + log cả header | rò dữ liệu phiên | **không** — nền mới không có `server.js` này |
| PRE-8 (mới) `state` của SSO AccessTrade không được kiểm | chiếm liên kết tài khoản | **có** nếu port nguyên xi |

⚠️ **Hai mục PRE-1 và PRE-8 là thứ hệ mới SẼ mang theo** nếu port nguyên luồng uỷ quyền như
quyết định 04/09. Đây là chỗ duy nhất trong mục 2.6 chạm vào phạm vi tài liệu này: khi dựng
`partner-app`, hai luồng đó phải được viết đúng ngay từ đầu chứ không chép lại.

**PRE-1 — Điều hướng mở ở luồng uỷ quyền TikTok. Quyết định: GIỮ NGUYÊN (04/09).**
`login-tiktok/index.tsx:14` và `connect-tiktok/index.tsx:12` dùng tham số `state` do bên gọi cung cấp làm đích điều hướng, không kiểm danh sách cho phép. Backend cũng không giới hạn `redirectURI` (`internal/module/social/tiktok/tiktok.go:113`); tìm `allowlist|whitelist|validateRedirect` trên `backend/internal` và `backend/pkg` không có kết quả. Quét toàn bộ nhánh remote 04/09: không nhánh nào có bản vá.

**Quyết định 04/09: `partner-app` port nguyên luồng hiện tại, không thay đổi.** Ghi nhận đây là **quyết định giữ nguyên hiện trạng**, không phải kết luận đã kiểm tra và thấy an toàn — hai câu đó khác nhau và tài liệu này không có căn cứ cho câu thứ hai.

#### Đính chính v1.9 — đã xác minh đường khai thác cụ thể

Câu "giữ nguyên" ở trên nói về việc **`partner-app` port nguyên luồng thay vì thiết kế lại**.
Việc xử lý trên 5 site đang chạy là **quyết định của chủ sở hữu**, không thuộc phạm vi tài
liệu này. Ghi lại đường khai thác cụ thể để quyết định đó có đủ dữ kiện:

```js
// pages/login-tiktok/index.tsx và pages/connect-tiktok/index.tsx — GIỐNG HỆT ở cả 5 app
window.location.href = `${query.state}dang-nhap-tiktok?code=${query.code}&redirect_uri=${redirectUri}`;
```

`query.state` đến thẳng từ URL và làm **gốc** của URL chuyển hướng. Mở

```
https://<site-that>/dang-nhap-tiktok?code=<mã uỷ quyền của nạn nhân>&state=https://evil.com/
```

là trình duyệt giao mã uỷ quyền TikTok của nạn nhân cho tên miền của kẻ tấn công — đủ để
hoàn tất đăng nhập và chiếm tài khoản. **5 ứng dụng × 2 trang.**

**Cách vá khi nào xử lý:** chỉ cho phép quay về chính tên miền của ứng dụng (`ORIGIN` hoặc
`NEXT_PUBLIC_ORIGIN`); giá trị ngoài danh sách bị bỏ qua và luồng đi tiếp nhánh bình thường,
nên giá trị hợp lệ không đổi hành vi. **Ràng buộc cho `partner-app`: luồng này phải viết theo
danh sách cho phép ngay từ đầu, không chép lại bản hiện tại.**

Backend cũng nhận `redirectURI` từ client và chuyển thẳng cho TikTok (`tiktok.go:113`).
TikTok tự đối chiếu với URI đã đăng ký nên đây không phải đường rò thêm, nhưng vẫn nên siết.

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
| `parasola/pages/contact/index.tsx:69` | Hotline `1900 6060` của HDBank |
| `lusso/pages/contact/index.tsx:69` | Hotline `1900 6060` của HDBank — **bản khảo sát đầu bỏ sót chỗ này** |

**PRE-3 cần người quyết, không phải việc của kỹ thuật.** Không ai trong nhóm phát triển
biết hotline, email và ba kênh mạng xã hội **đúng** của `lusso` và `parasola`. Sửa bằng cách
đoán là thay một giá trị sai bằng một giá trị sai khác, lần này còn khó phát hiện hơn vì
trông có vẻ hợp lý.

Hai lý do nữa để không vội:

1. Đây đúng là loại dữ liệu mà PC-002/PC-017 chuyển về khai trong admin. Sửa cứng trong mã
   bây giờ là làm một việc sắp bị xoá.
2. Cửa kiểm chéo của PC-007 **đã chặn** đường lây sang hệ mới: công cụ trích cấu hình
   (PC-016) đọc từ chính các ứng dụng này, và bất kỳ giá trị nào đã đăng ký cho ADV khác sẽ
   bị từ chối lúc xuất bản. Đã kiểm bằng test đầu-cuối với đúng hai giá trị `1900 6060` và
   `info@hdbank.com.vn`.

**Việc cần người quyết:** đội vận hành cung cấp hotline, email và ba kênh mạng xã hội đúng
của `lusso` và `parasola`. Có giá trị rồi thì khai thẳng vào cấu hình ADV — không cần sửa mã.

**PRE-4 — Thẻ canonical trỏ sai domain ở cả 5 ứng dụng.**
`wrappers/home.tsx` gán `url: process.env.ORIGIN`, trong khi `ORIGIN = https://ambassador.koc.com.vn/` ở cả 5; giá trị này dùng cho `<link rel="canonical">` và `og:url`. Nguyên nhân là nhầm giữa `ORIGIN` (domain callback dùng chung) và `NEXT_PUBLIC_ORIGIN` (domain đối tác).

Rà lại thì **rộng hơn bản khảo sát đầu**: ngoài `wrappers/home.tsx` còn
`layouts/event-detail/index.tsx` và `pages/partner-home/index.tsx` — tức là trang chủ, trang
chi tiết chiến dịch và trang chủ theo ADV, cả ba đều khai canonical về tên miền của người
khác. Đã đổi 20 chỗ trên 5 ứng dụng.

Bốn chỗ `redirect_uri` của TikTok và một chỗ phân giải partner **vẫn dùng `ORIGIN`** — chúng
gắn với tên miền đã đăng ký, đổi là hỏng luồng đăng nhập.

**PRE-5 — Trạng thái toàn cục theo request tại tầng SSR.**
`server.js:25-26` gán `global._cookies` và `global._navigatorLang` trên tiến trình dùng chung. Hiện không nơi nào đọc, nên chưa gây hậu quả. Cần loại bỏ trước khi hợp nhất.

Ngay dòng dưới còn một lỗi **mới tìm ra**: `console.log('👨‍💻 Log PARAMS 👉 ctx:', ctx.request)`
in nguyên đối tượng request mỗi lần gọi, tức là ghi cả khối header — gồm cookie phiên và
`Authorization` — vào log máy chủ của cả 5 ứng dụng.

**PRE-8 — `state` của luồng SSO AccessTrade sinh ra nhưng không bao giờ được kiểm.**

Không có trong bản khảo sát đầu; tìm ra khi rà PRE-1. Khác PRE-1 ở chỗ đây là luồng
AccessTrade, không phải TikTok.

`accesstrade-section/index.tsx` sinh `state`, gửi đi, rồi ở nhánh quay về chỉ đọc `code` và
đổi lấy token — **không đối chiếu `state`**. Ai dụ được nạn nhân mở
`/lien-ket-tai-khoan?code=<mã của kẻ tấn công>` sẽ gắn tài khoản AccessTrade **của kẻ tấn
công** vào tài khoản nạn nhân; nạn nhân thấy màn hình báo liên kết thành công.

Hai lỗi phụ cùng chỗ: `state` là `sha256` của mốc thời gian mili giây (đoán được nếu biết
người dùng bấm lúc nào), và được tính **một lần lúc nạp module** nên mọi lần liên kết trong
cùng phiên dùng chung một giá trị.

**Ràng buộc cho `partner-app`:** `state` sinh bằng nguồn ngẫu nhiên mật mã, mới cho mỗi lần
bấm, lưu lại và đối chiếu khi quay về, dùng một lần rồi xoá.

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

#### Đính chính khi triển khai (v1.8): mặc định là để KHÔNG khai, không phải để khai sẵn

Bản trước ngầm hiểu ADV khai đủ token rồi ghi đè. Lúc dựng màn hình mới thấy hệ quả: nếu
bắt khai đủ thì **mỗi ADV giữ một bản sao của cùng một giá trị**, và sửa mặc định về sau
không ADV nào nhận được — đúng cái bệnh "mỗi ADV một mã nguồn" mà hệ này sinh ra để chữa,
chỉ đổi chỗ từ mã nguồn sang cơ sở dữ liệu.

Nên chốt lại ba điểm:

1. **Không token nào bắt buộc, kể cả `primary`.** Bản nháp và bản xuất bản đều chấp nhận
   theme rỗng. Cái được kiểm là **định dạng của giá trị có mặt** (phải là hex 3 hoặc 6 ký
   tự), không phải sự có mặt của khoá.
2. **Hợp nhất với mặc định chạy ở SERVER**, trong endpoint công khai, không ở frontend.
   Để frontend tự điền mặc định là frontend phải giữ một bản sao của bộ giá trị đó — bản
   sao ấy sẽ lệch dần, và lệch im lặng.
3. **`primaryForeground` không tồn tại.** Bản v1.2 nhắc token này khi rút danh sách xuống
   2 khoá; nó không nằm trong 18 khoá của khối `//Color`, và cách dùng độ mờ ở trên khiến
   nó không cần thiết. Danh sách chuẩn là **18 khoá màu + 4 bo góc**, không có ngoại lệ.

Bo góc `0` là **giá trị hợp lệ** (góc vuông), không phải "chưa khai" — lớp hợp nhất duyệt
theo khoá có mặt, không so với `0`.

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
- [ ] ADV **không khai token nào** vẫn xuất bản được, và endpoint công khai trả **đủ 18 màu + 4 bo góc + font** lấy từ mặc định
- [ ] Khai `radius.base = 0` thì endpoint công khai trả `0`, không bị mặc định `8` đè
- [ ] Gõ hex sai trong admin: ô báo lỗi **tại chỗ**, ô xem trước màu không vẽ giá trị hỏng
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
| Token giao diện | giá trị có mặt không phải mã hex, bo góc âm, file font thiếu tên hoặc đường dẫn — **không** đòi khoá nào phải có mặt, xem đính chính ở PC-002 |
| Section | thiếu `hero`/`events`, loại ngoài danh mục, `key` trùng hoặc rỗng |
| **Trường bắt buộc** | thiếu bất kỳ trong 7: `website`, `footerBrandLink`, `contact.hotline`, `contact.email`, 3 article ID |
| **Dữ liệu đối tác khác** | cấu hình chứa domain, hotline, email hoặc article ID đã đăng ký cho đối tác khác |

Hai cửa cuối là chốt chặn cho lỗi **đang chạy trên production**: `lusso` dùng Facebook, TikTok, YouTube, link tải app và email của HDBank; `parasola` dùng hotline của HDBank; ba ứng dụng có giá trị fallback cứng trỏ tới bài viết pháp lý của HDBank (mục 2.6).

Khi migrate, cấu hình được **trích tự động từ chính các ứng dụng đó**. Không chặn ở bước xuất bản thì các giá trị sai theo sang hệ mới và trở thành dữ liệu chính thức — khó phát hiện hơn bây giờ.

**Trường bắt buộc không có giá trị mặc định và không kế thừa.** Nguyên nhân gốc của cả hai lỗi trên là các giá trị này được **thừa hưởng** chứ không được **hỏi**.

#### Đính chính khi triển khai (v1.8): dấu hiệu ADV khác phải là HOST, không phải URL đầy đủ

Bản đầu dựng danh sách dấu hiệu từ `website` của ADV khác, để nguyên dạng URL
(`https://hdbank.com.vn/`). Test đầu-cuối bắt được ngay: cách đó **chỉ khớp khi bị chép y
hệt**, trong khi giá trị lẫn thật lại là liên kết trỏ vào một đường dẫn khác cùng tên miền
— ảnh trên CDN, trang tải ứng dụng. Đúng ca `lusso` đang mang link tải app của HDBank.

Nên dấu hiệu lấy **host** của `website` (`hdbank.com.vn`), cộng với `allowDomains`, hotline,
email và ba mã bài viết đọc từ cấu hình **đã xuất bản** của ADV đó — lùi về bản nháp khi họ
chưa xuất bản lần nào, vì lúc chuyển sang hệ mới chưa ai xuất bản mà đó đúng là lúc cần
chặn nhất.

Phép dò đi **đệ quy** qua cả `content` lẫn `assets`: chỗ hay sai nhất lại nằm trong mảng
object (`social[]`), dò nông sẽ bỏ sót đúng chỗ đó.

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
- [ ] Xuất bản cấu hình chứa liên kết trỏ vào **subdomain** của ADV khác (`cdn.hdbank.com.vn`): từ chối
- [ ] Có test đối chiếu khoá cache hai phía
- [ ] Xuất bản lần hai làm endpoint công khai trả bản mới **ngay lần gọi kế tiếp** — chứng minh khoá xoá cache trùng khoá đọc
- [ ] Xuất bản thất bại: hộp thoại trong admin **đóng lại**, thông báo lỗi ở lại — không che mất ô cần sửa

---

### PC-008: Màn hình cấu hình trong admin

**Priority:** Must Have

Xây trong `admin/` hiện hành (umi 3 + antd 4), đặt cạnh biểu mẫu đối tác ở `admin/src/pages/partner/components/modal.tsx`. **Không dựng admin mới.**

| Nhóm | Nội dung |
|---|---|
| Nhận diện | tên, slug, domain, 18 khoá màu + 4 bo góc (ô trống = dùng mặc định), font |
| Asset | 7 khoá lõi + file font + khoá mở rộng |
| Nội dung | 3 article ID (xem v1.3), liên hệ, mạng xã hội, liên kết footer, liên kết tài liệu |
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

### PC-012: Gộp 5 bản về một — lấy bản đầy đủ nhất

**Priority:** Must Have

**Chốt 04/09: gộp về bản đầy đủ nhất.** Không chuẩn hoá xuống mẫu số chung, không hỏi từng ADV.

**Vì sao không cần ADV chấp thuận.** Tôi từng ghi rằng bốn file phân kỳ nặng chứa "khác biệt hành vi không có đáp án kỹ thuật, phải hỏi từng ADV". Đo lại trên 5 ADV thật thì không đúng — chỉ có một ADV đi sau, không có xung đột.

`not-logged-in/index.tsx` (file khác nhau nặng nhất, Δ914):

| Tính năng | hdbank | lusso | parasola | vpbank | fecredit |
|---|:--:|:--:|:--:|:--:|:--:|
| `ShareSocialDropdown` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `isMustInputProfile` | ✓ | ✓ | ✓ | **·** | ✓ |
| `Tooltip` | ✓ | ✓ | ✓ | **·** | ✓ |
| `useResponsive` | ✓ | ✓ | ✓ | **·** | ✓ |
| `FAQCollapse` | · | · | · | **✓** | · |

`components/layout/main/header/index.tsx` (Δ659):

| | hdbank | lusso | parasola | vpbank | fecredit |
|---|:--:|:--:|:--:|:--:|:--:|
| `isOwnerPartner` · `notificationList` · `menuVisible` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `qaArticleId` | ✓ | ✓ | ✓ | **·** | ✓ |

**`vpbank` chỉ đơn giản đi sau.** Thiếu bốn thứ bốn ADV kia có, và có đúng một thứ họ chưa có.

Gộp về bản đầy đủ nhất nghĩa là:

```
vpbank ĐƯỢC THÊM   isMustInputProfile · Tooltip · useResponsive · link Q&A ở header
                   → không ADV nào mất gì
FAQCollapse        → đã là section `faq` trong catalogue PC-005
                   → bật bằng cấu hình
```

**Số cờ mới cần thêm: 0.**

Một chi tiết: `isMustInputProfile` đến từ `eventHome` — dữ liệu backend theo từng chiến dịch. `vpbank` thiếu không phải do chủ đích mà do chưa hiện thực. Thêm vào là kích hoạt đúng khi chiến dịch bật cờ, không đổi hành vi hiện tại của ai.

**Ba nhóm file, xử lý khác nhau:**

| Nhóm | File | Cách làm |
|---|---|---|
| Chuyển thành cấu hình | `wrappers/home.tsx`, `configs/app.ts`, `configs/image.ts`, `bootstrap-custom.scss`, footer | Trích bằng PC-016 |
| Trôi do copy | `configs/api.ts` (khác **thứ tự khai báo**, nội dung y hệt), `utils/helper.ts`, `app.tsx` | Chọn bản đầy đủ nhất |
| Khác nhau về tính năng | `not-logged-in`, `header`, `models/main.ts`, `interfaces/event.ts` | **Lấy hợp của mọi tính năng** |

**AC:**
- [ ] Toàn bộ 22 file khác nhau được phân loại và có quyết định ghi trong commit
- [ ] Bốn tính năng `vpbank` đang thiếu có mặt sau khi gộp
- [ ] Không ADV nào mất tính năng đang có — đối chiếu bằng ma trận trước/sau
- [ ] Không thêm cờ phân hệ nào ngoài `contract` và `affiliate`

---

### PC-013: Migrate và cutover theo đợt

**Priority:** Must Have

**Điều kiện vào cutover:**
- Cấu hình của đối tác đã khởi tạo và xuất bản ở staging
- Bộ ảnh đối chiếu trước/sau hoàn tất cho từng màn × từng đối tác (NFR-007)
- PC-012 xong cho phạm vi file đợt chạm tới
- Cấu hình điền đủ trường bắt buộc và qua được kiểm tra chéo của PC-007
- Diễn tập khôi phục thành công

**Điều kiện nghiệm thu:** hai tuần vận hành không sự cố P1/P2 liên quan tới migrate.

#### Giá trị sai là lỗi nhập liệu, không phải rủi ro thiết kế

Liên hệ, mạng xã hội, article ID đều là trường cấu hình. Người setup điền đúng thì đúng. `lusso` và `parasola` đang mang dữ liệu của HDBank trong mã nguồn — sang hệ mới thì đó là hai ô cần điền đúng, không phải hạng mục phải xử lý riêng.

Lưới an toàn đã có sẵn ở PC-007: kiểm tra chéo chặn xuất bản nếu cấu hình chứa dữ liệu đã đăng ký cho ADV khác. Không cần thêm điều kiện nào.

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
| Guard mới cho 6 endpoint `app-config` | Chặn ở server `staff.Partner` trong 12 service admin cũ |
| Kiểm `staff.Partner` **chỉ trong** các endpoint cấu hình mới | Đổi hành vi của bất kỳ endpoint đang chạy nào |

Hai cột phải là task riêng có kế hoạch di dữ liệu. Gộp vào dự án hợp nhất frontend là mở hai mặt trận cùng lúc.

**Ràng buộc theo ADV hiện chắp vá.** `staff.Partner` được kiểm ở đúng hai vùng — `handler/leaderboard_view.go:123,131` và `service/event_bonus.go` (5 chỗ). Event, content, article, category, news, quick-action đều **không kiểm**. Yêu cầu này không sửa việc đó, chỉ bảo đảm endpoint mới không lặp lại.

#### ⚠️ Đính chính khi triển khai (v1.8): thêm một vai trò đụng BA danh sách, và bản gieo bỏ qua môi trường đang chạy

Thêm `config_editor` xong, chạy thử thì vai trò **không xuất hiện dưới cơ sở dữ liệu** và
guard mới im lặng không cho ai qua. Hai nguyên nhân, đều là bẫy sẵn có chứ không phải lỗi
của yêu cầu này:

1. **Ba danh sách vai trò song song.** `constants.StaffRole` (mã), `constants.StaffRoleName`
   (nhãn) và `constants.Roles` (bản gieo xuống DB) là ba bản viết tay tách rời. Thêm vai trò
   mà quên bản thứ ba thì vai trò đó không bao giờ có bản ghi, và **không có lỗi nào báo ra**
   — về mặt kỹ thuật chẳng có gì hỏng cả.
   → `Roles` nay **sinh từ** `StaffRoleList` + `StaffRoleNameList`, có test canh ba bản khớp nhau.

2. **`GenerateRole` thoát ngay khi đã có bất kỳ vai trò nào** (`dummy_db.go` — `if total > 0 { return }`).
   Nghĩa là mọi môi trường đang chạy — vốn đã có sẵn hai vai trò — **sẽ không bao giờ nhận
   được vai trò mới**, kể cả sau khi deploy.
   → Nay xét **từng vai trò một**, chỉ gieo cái còn thiếu. Đã xác nhận trên một cơ sở dữ liệu
   đã có sẵn hai vai trò: lần khởi động sau in `Generate 1 roles success`.

Bài học rộng hơn cho các yêu cầu sau: **thêm hằng số vào một danh sách trong repo này thì
phải đi tìm các bản sao của danh sách đó trước.**

**AC:**
- [ ] `config_editor` của ADV X đọc và ghi được `app-config` của X
- [ ] `config_editor` của ADV X gọi `app-config` của ADV Y → **401**
- [ ] `config_editor` **không** tạo, xoá hay đổi trạng thái được ADV nào
- [ ] Vai trò mới xuất hiện dưới DB **của môi trường đã có sẵn vai trò cũ**, không chỉ trên DB trắng
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

Nên đầu ra của công cụ là **bản nháp**, không phải bản xuất bản, và phải **đánh dấu những giá trị trùng với ADV khác** để người điền biết chỗ cần sửa. Kiểm tra chéo của PC-007 là chốt chặn cuối.

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

Đội soạn nội dung tạo bài trong admin; frontend chỉ đọc mã bài từ cấu hình và hiển thị.

**AC:**
- [ ] `EventRaw.Guide` và `EventRaw.Privacy` giữ nguyên; form chiến dịch trong admin không đổi
- [ ] Ba ô chọn bài viết per-ADV trong màn cấu hình, dropdown từ danh sách bài đã có
- [ ] Thiếu bất kỳ trong ba: chặn xuất bản
- [ ] Không có `SUPPORT_ARTICLE_ID` trong lược đồ
- [ ] Danh sách kiểm onboard (PC-014) đếm đúng số bài cần soạn theo số chiến dịch

---

### PC-018: Lược đồ cấu hình do server phát ra, admin không khai lại

**Priority:** Must Have — yêu cầu mới tại v1.8, phát sinh khi dựng màn hình

**Vì sao cần.** Màn cấu hình cần bốn thứ để dựng được: danh mục section hợp lệ, danh sách
khoá màu chuẩn, giá trị mặc định của từng khoá, và danh sách trường bắt buộc. Cả bốn **đã
nằm trong mã nguồn backend** — đó là nơi luật được thi hành.

Nếu admin khai lại một bản của riêng mình thì có hai nguồn sự thật, và cái sai sẽ **im
lặng** theo đúng một trong hai chiều:

| Lệch kiểu gì | Người dùng thấy gì |
|---|---|
| Admin có khối mà server không nhận | Thêm khối, bấm lưu, bị từ chối, không hiểu vì sao khối đó có trong danh sách |
| Server nhận khối mà admin không hiện | Khối không bao giờ dùng được, không có dấu hiệu nào để lần ra |
| Admin thiếu một trường bắt buộc mới | Lỗi lúc xuất bản, mà màn hình **không có ô nào để sửa** |

Đây đúng là dạng phân kỳ mà cả dự án sinh ra để xoá — chỉ đổi chỗ từ giữa 5 frontend sang
giữa admin và backend.

**Một endpoint, đọc-chỉ, không gắn ADV nào** (siêu dữ liệu hệ thống, chỉ cần đăng nhập):

```
GET /partners/app-config/schema
  sections[]             { type, removable, repeatable, nav } — thứ tự ỔN ĐỊNH
  defaultSections[]      bộ khối khởi đầu của một ADV mới
  theme.colorKeys[]      18 khoá
  theme.radiusKeys[]     4 khoá
  theme.default          bộ token mặc định đầy đủ
  requiredContentPaths[] 7 đường dẫn bắt buộc
```

**Thứ tự phải ổn định.** Danh mục section lưu dạng map; duyệt map trong Go cho thứ tự ngẫu
nhiên, nên nếu không sắp thì danh sách khối trong admin **nhảy chỗ mỗi lần tải lại trang**.

**Ô nhập của phần bắt buộc dựng TỪ `requiredContentPaths`**, không viết tay theo cây trường
— nhờ đó thêm một trường bắt buộc ở server là màn hình tự có ô cho nó.

#### `defaultSections` — ADV mới mở lên đã có trang, không phải trang trắng

Bộ khởi đầu là `hero → statistic → events → content-highlight`, đúng thứ tự bốn khối mà cả
năm ADV đang chạy dùng hôm nay (`<adv>/src/pages/partner-home/desktop.tsx`). Việc người vận
hành phải làm là **ĐỔI**, không phải **DỰNG**.

Bộ này chưa ghi xuống cơ sở dữ liệu — chỉ trả về khi ADV chưa có bản ghi, ghi thật khi bấm lưu.

**AC:**
- [ ] Danh mục trả về phủ **đúng** danh mục trong mã nguồn — không thiếu, không thừa; có test canh
- [ ] Gọi hai lần cho thứ tự **giống hệt**
- [ ] `defaultSections` tự nó qua được luật kiểm section — ADV mới mở màn hình không thấy lỗi ở trạng thái chưa ai chạm vào
- [ ] `grep` trong `admin/src` không thấy danh sách khoá màu, danh mục section hay danh sách trường bắt buộc nào được khai lại
- [ ] Thêm một loại section ở backend: admin hiện nó ra **mà không cần sửa mã admin**

### PC-019: Bẫy nền tảng khi dựng lại giao diện — năm thứ hỏng im lặng

**Priority:** Must Have — yêu cầu mới tại v2.0, phát sinh khi dựng lại 21 màn hình

**Vì sao cần.** Cả ba mục dưới đây **biên dịch sạch, không lỗi runtime, không cảnh báo**.
Không có kiểm thử tự động nào bắt được: kiểu dữ liệu đúng, DOM đúng, chỉ có hình ảnh sai.
Chúng chỉ lộ ra khi mở trình duyệt và nhìn — nên phải ghi thành ràng buộc, không thì mỗi
đợt migrate lại vấp một lần.

**1. SVGR xoá `viewBox`.** Bộ tối ưu mặc định của SVGO bỏ `viewBox` ở mọi file **có sẵn
`width`/`height`** — và 161/161 icon port từ ứng dụng cũ đều có. Mất `viewBox` thì path vẽ
theo toạ độ gốc 24 đơn vị **bên trong khung 16px người gọi yêu cầu**, tức chỉ hiện góc trên
trái của hình: chuông thông báo thành một nét cong, mũi tên thành gạch chéo. Phải đặt
`removeViewBox: false`, và `dimensions: false` để `width` truyền từ props có tác dụng thật.

**2. Token `muted` của partner là màu CHỮ; shadcn coi `muted` là màu NỀN.** Bộ token đang
chạy đặt `muted: #8b9092` — xám dùng cho chữ phụ. shadcn dùng `bg-muted` cho thanh tab và
vằn bảng, vốn mong một màu nền rất nhạt. Nối thẳng hai cái vào nhau cho ra **chữ xám trên
nền xám**. Các bề mặt đó phải trỏ sang `light`; **không được** định nghĩa lại `muted` trong
lớp cầu nối, vì như thế sẽ hỏng `text-muted` ở mọi nơi khác.

**3. `background` của partner là nền TRANG có sắc, không phải màu trắng.** `fecredit` chạy
nền bạc hà, `hdbank` chạy trắng. shadcn mặc định `background` là trắng và dùng luôn làm bề
mặt cho hộp thoại, popover và nút viền. Hộp thoại `bg-background` đặt trên nền có sắc trông
**như lớp phủ không hiện** — người dùng không phân biệt được đâu là hộp thoại. Những bề mặt
đó phải dùng `popover`/`card`.

**4. SVGO đổi TÊN mọi id thành `a`.** 51/193 icon có `clipPath`, `mask` hoặc gradient tham chiếu bằng `url(#…)`. Bộ tối ưu rút gọn mọi id thành `a`, mà id là **toàn cục trong một document** khi icon được nhúng thẳng vào DOM — nên mười icon trên một trang đều trỏ về `#a` ĐẦU TIÊN, và chín cái còn lại bị cắt theo vùng clip của một glyph khác. Icon "sao chép" ra một góc vụn. Phải bật `prefixIds` để mỗi tập tin có prefix riêng.

**5. Tailwind v4 đổi mặc định `border-color` sang `currentColor`.** v3 mặc định là xám nhạt. Component shadcn viết `border` trần và trông đợi một lớp base cấp màu; thiếu lớp đó thì **mọi** thẻ, dropdown và ô đều viền màu CHỮ, tức gần đen. Không có cảnh báo nào.

**Điểm chung cần rút ra:** ánh xạ token của partner sang tên ngữ nghĩa của thư viện component
**không phải phép nối tên giống nhau**. Cùng một từ (`muted`, `background`) mang hai nghĩa
khác nhau ở hai hệ; nối theo tên cho ra giao diện sai mà không có tín hiệu lỗi nào. Cũng
vậy với công cụ: mặc định của SVGO và của Tailwind đều đổi theo phiên bản, và cả hai đổi
theo hướng **hỏng im lặng** chứ không báo lỗi.

**AC:**
- [ ] Mở một trang bất kỳ, mọi `<svg>` trong DOM đều có thuộc tính `viewBox`
- [ ] Không có hai phần tử nào trong DOM trùng `id` — kiểm bằng một dòng script, không bằng mắt
- [ ] Thẻ và dropdown viền màu nhạt, không phải màu chữ
- [ ] Icon yêu cầu `width={16}` chiếm đúng 16px và hiện **trọn** hình, không phải một góc
- [ ] Thanh tab, vằn bảng, hộp thoại và popover đều **tương phản được** với nền trang trên cả `fecredit` (nền bạc hà) và `hdbank` (nền trắng)
- [ ] Lớp cầu nối token có chú thích ghi rõ vì sao `muted` và `background` **không** nối thẳng

---

### PC-020: Gradient là một loại token, không gộp được vào bảng màu đơn

**Priority:** Must Have — yêu cầu mới tại v2.2, phát sinh khi đối chiếu trang chủ với trang đang chạy

**Vì sao cần.** Bộ 18 màu **đơn** không mô tả được `fecredit`. Tiêu đề khối, nút chính và nền
trang của họ đều là **gradient ba stop** (`#2ECEFF → #0DD09F → #00A078`). Ép về một màu đơn là chỗ sai lệch dễ thấy nhất giữa hệ mới và trang đang chạy: tiêu đề xanh lá thay vì
xanh ngọc, nút màu đơn thay vì chuyển sắc, nền một màu thay vì gradient.

Không gộp được vào `colors`: một gradient là **nhiều stop màu cộng một góc**, còn `colors`
là map khoá → một mã màu.

**Lưu thành DỮ LIỆU, không phải chuỗi CSS.** Chuỗi `linear-gradient(...)` từ cấu hình sẽ đi
thẳng vào thuộc tính `style` của thẻ gốc, tức **tiêm CSS tuỳ ý** — đúng thứ mà bộ kiểm màu
sinh ra để chặn. Góc và các stop được kiểm riêng rồi hệ thống tự ghép chuỗi.

```
theme.gradients { <tên>: { angle?: number, stops: [{ color: "#hex", at?: 0-100 }] } }
```

Ba tên đang dùng: `heading`, `cta`, `page`.

**Đòi tối thiểu HAI stop.** Gradient một stop chính là màu đơn viết dài dòng; nhận vào thì một lần nhập sai ở admin sẽ **âm thầm làm mất gradient của cả nhận diện thương hiệu** thay vì báo lỗi.

**Mọi chỗ dùng phải rơi về màu đơn.** `var(--gradient-x, var(--color-y))` — ADV không khai
gradient nào thì nhận đúng thứ họ vẫn có. Đây cũng là lý do dùng được `background-clip: text`
cho cả hai: tô chữ bằng màu đơn cho kết quả y như tô bằng gradient.

**AC:**
- [ ] `ResolveTheme` GIỮ `gradients`; ADV không khai thì **không** có gradient mặc định nào
- [ ] Mỗi stop qua đúng bộ kiểm hex như một màu đơn; stop sai làm hỏng **cả** gradient, không phải một nửa
- [ ] Vị trí stop ngoài 0-100 bị từ chối lúc xuất bản
- [ ] Gỡ hết `gradients` khỏi cấu hình: trang vẫn đúng, chỉ còn màu đơn — không chỗ nào trống

---

### PC-021: Quy ước hiển thị đo TỪNG MÀN, không suy ra một thang chung

**Priority:** Must Have — yêu cầu mới tại v2.2, phát sinh khi soi từng trang

**Vì sao cần.** Đối chiếu từng màn với trang đang chạy cho thấy các quy ước hiển thị
**khác nhau theo màn**, và mỗi lần tự suy ra một thang chung là một lần lệch:

| Quy ước | Giá trị thật | Suy đoán sai đã mắc |
|---|---|---|
| Cỡ tiêu đề khối | Trang chủ **36px**, màn chi tiết **20px** | Dùng 36px cho cả hai; màn chi tiết to gấp rưỡi |
| Tuổi bài đăng | Tương đối trong **8 ngày**, sau đó ngày giờ tuyệt đối | Luôn tương đối; "47 ngày trước" bắt người đọc tự tính |
| Định dạng ngày giờ | `DD/MM/YYYY - HH:mm` | `Intl` với `dateStyle`/`timeStyle` cho `18:28 26/8/26` — giờ trước, năm hai chữ số |
| Thẻ chiến dịch | Khung **`aspect-ratio` cố định**, panel `position: absolute` đè lên cover | Xếp nối tiếp; bấm mở một thẻ là cả hàng nhảy |
| Lớp phủ (overlay) khi mở panel | Trắng **10%** | Đen 40% — làm poster bạc trắng. Stylesheet của FE cũ ghi rõ họ đã thử 0.55 đen và bỏ |
| Thẻ mốc thưởng | Chỉ tiêu đề + huy chương + tiền | Thêm `desc`; `desc` là một câu điều kiện đầy đủ, biến 5 thẻ gọn thành 5 đoạn văn |
| Chip trên poster | view / bài đăng / **tiền thưởng**, số rút gọn, không chú thích | Chỉ số thứ ba là số creator; viết đủ số + chú thích làm chip rộng gấp đôi poster |
| Trang văn bản dài | Breadcrumb **trong** thẻ, bề ngang **1040px**, khoảng cách đoạn sát | Breadcrumb ngoài, khung nội dung 1216px, lề đoạn rộng — trình soạn thảo xuất một `<p>` mỗi DÒNG nên danh sách năm ý thành năm câu rời rạc |

**Quy tắc:** trước khi dựng một màn, **đo trên trang đang chạy** — cỡ chữ, khoảng cách,
ngưỡng định dạng — thay vì suy từ màn đã dựng. Bộ token cho biết *màu gì*, không cho biết *cỡ bao nhiêu ở màn nào*.

**AC:**
- [ ] Mỗi màn có một lần đối chiếu trực tiếp với trang đang chạy trước khi nghiệm thu
- [ ] Ngưỡng và định dạng (8 ngày, `DD/MM/YYYY - HH:mm`) nằm trong **một** hàm dùng chung, có test — không lặp ở từng màn

---

### PC-022: `loading.tsx` ở gốc thay luôn cả header và footer

**Priority:** Must Have — yêu cầu mới tại v2.2

**Vì sao cần.** Header và footer hiện nằm trong `PageFrame`, mà `PageFrame` do **từng trang**
render. Nên một `app/loading.tsx` ở gốc thay **toàn bộ** đầu ra của route — kể cả header và footer — và
mỗi lần điều hướng làm cả màn hình trắng rồi dựng lại. Người dùng hiểu đó là trang bị tải lại.

**Hai đường, phải chọn một:**

1. **Không có `loading.tsx` ở gốc.** Next giữ trang hiện tại cho tới khi trang mới sẵn sàng.
   Các khối vẫn chảy vào dần nhờ `Suspense` bọc từng section. Đây là trạng thái hiện tại.
2. **Đưa header và footer lên `app/layout.tsx`.** Lúc đó `loading.tsx` chỉ thay phần thân. Vướng một
   điểm cần quyết: trên tên miền nhiều ADV, header hiện ADV nào là do **đường dẫn** quyết,
   mà layout chỉ biết tên miền — nên hoặc chấp nhận header lấy ADV đầu tiên, hoặc đẩy phần
   chọn ADV xuống một client component đọc `usePathname`.

**AC:**
- [ ] Chuyển trang KHÔNG làm header/footer biến mất rồi hiện lại
- [ ] Nếu chọn đường 2, ghi rõ header hiển thị ADV nào trên tên miền nhiều ADV

---

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

### NFR-009: Theme chung — ADV không có quyền chỉnh riêng
**Chốt 04/09.** Giao diện và hành vi là **một bản dùng chung**. ADV không được yêu cầu thay đổi ngoài các trường cấu hình đã định trong lược đồ.

Ba đường xử lý một yêu cầu riêng rút còn hai: **biến thành cấu hình** nếu nằm trong lược đồ sẵn có, hoặc **từ chối**. Không có đường fork riêng.

Đây là câu trả lời bằng **chính sách**, mạnh hơn mọi cổng gác kỹ thuật — không ai phải đứng gác vì cổng đóng sẵn. Cần một dòng tương ứng trong hợp đồng vận hành, không chỉ trong tài liệu này.

Chỉ số theo dõi: **số commit chỉ phục vụ một ADV — mục tiêu 0**. Khác 0 nghĩa là chính sách đang bị lách.

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

### Hợp đồng backend — tám điều chỉ lộ ra khi chạy với dữ liệu thật

Tám điều dưới đây không nằm trong tài liệu API nào; tất cả tìm ra khi dựng màn hình chiến dịch, màn tài khoản và khi chạy thử với backend dev thật, và tất cả đều **hỏng im lặng**: request trả `code: 1`, không có lỗi ở đâu, chỉ là màn hình thiếu dữ liệu.

**1. `Origin` quyết định ADV nào được trả về — kể cả cổng.** `GET /events` và `GET /events/statistic` gọi `GetListPartnersByDomain(cc.GetAppOrigin())`, tức lọc `partners.allowDomains` theo header `Origin` (rơi về `Referer` nếu thiếu). Không có header thì tập đối tác rỗng và **danh sách chiến dịch rỗng ở mọi ADV** — vẫn `code: 1`, vẫn `"Thành công!"`. Các ứng dụng đang chạy không bao giờ gặp vì trình duyệt tự gắn `Origin`; `partner-app` render ở server nên **phải chuyển tiếp `Host` của request thành `Origin`**.

Kèm theo: `pstring.GetHostNameByURL` trả `uri.Host`, tức **giữ nguyên cổng**. `localhost:8000` và `localhost` là hai tập đối tác khác nhau. Cắt cổng ở server sẽ làm request phía server resolve khác request phía trình duyệt **trên cùng một trang** — chạy production không lộ vì host thật không có cổng, chỉ vỡ ở môi trường dev.

> Hệ quả cho **BFF proxy** ở trên: proxy đứng giữa thì `Origin` backend nhìn thấy là của proxy, không phải của trình duyệt. Route handler **phải chuyển tiếp `Origin` gốc**, nếu không mọi ADV mất danh sách chiến dịch ngay khi bật proxy.

**2. Thời gian là chuỗi ISO, không phải `{ unix }`.** Mọi mốc thời gian đi qua `ptime.TimeResponse`, `MarshalJSON` trả `t.Time.Format(DateISOFormat)` — và trả **chuỗi rỗng**, không phải `null`, khi chưa đặt. Đọc theo hình dạng `{ unix }` thì mọi ngày trên toàn ứng dụng hiện trống mà không báo lỗi.

**3. Một dòng bảng xếp hạng không có `view`/`cash`.** `UserEventResponse` trả `statistic.pointTotal` và `statistic.cashTotal`, mỗi cái tách `completed` và `pending`. Số của một dòng là **tổng hai phần**: bài đang đối soát vẫn tính vào thứ hạng, nên chỉ đọc `completed` sẽ cho dòng trên ít view hơn dòng dưới — bảng trông như sắp sai.

**4. `code: 1` với `data: null` là "không tìm thấy", không phải thành công.** `GET /articles/:id` với id không tồn tại trả đúng như vậy. Lớp gọi API phải coi payload `null` là thiếu dữ liệu, nếu không màn hình đọc `article.title` trên `null` và vỡ trang thay vì hiện nhánh không-tìm-thấy.

**5. Ảnh có BỐN hình dạng, tuỳ endpoint.** Cùng một khái niệm "ảnh" về theo bốn kiểu: chuỗi URL thuần (`cover` của bài đăng), `{ url }`, `{ dimensions: { sm|md|lg: { url } } }` (logo đối tác, ảnh bìa chiến dịch, icon) và `{ default|medium|high: { url } }` (thumbnail video). Ảnh bìa chiến dịch nằm ở `covers[0].default` — **không có khoá `photo`**, và mỗi entry còn giữ nhiều bản cắt khác (`stretch`). Đọc thiếu một dạng thì thẻ hiện nền phẳng trông như thiết kế cố ý.

**6. Hai endpoint bài đăng dùng hai bộ tên cho cùng ba thứ.** `/partners/content-features` trả `cover` + `statistic.view.total` + `author`; `/events/:id/content` trả `thumbnail` + `view`. Ảnh đại diện có thể nằm ở `user.socialInfo.photo` khi `user.avatar` rỗng — tài khoản đăng nhập bằng mạng xã hội và chưa tải ảnh lên.
---

**7. Affiliate nằm ở prefix RIÊNG, và trả thẳng một mảng.** `GET /affiliate/events/:id/campaigns`, không phải `/events/:id/campaigns` — đường dẫn thứ hai trả **404**, mà lớp gọi API biến 404 thành kết quả rỗng, nên cả khối Affiliate biến mất khỏi màn chi tiết **không một dấu vết**. Payload trả thẳng **một mảng** dưới `data`, không phải object bọc `{ list }`. Affiliate dùng chung một backend cho mọi app white-label và **không có tham số partner**: token của người dùng quyết định họ thuộc đối tác nào.

**8. Response bảng xếp hạng mang sẵn siêu dữ liệu mà không màn nào đọc.** `period`, `periodStartAt`/`periodEndAt`, `rankBy`, `metrics`, `valueBasis`, `graceDays`, `isSettling` — tất cả đã về cùng danh sách dòng. Bỏ qua chúng thì bảng vô nghĩa: "hạng 1 với 500 view" không cho biết là tháng này hay luỹ kế, và người mới đăng bài không biết bảng tuần sẽ reset.

Nguy nhất là `isSettling`. Trong những **ngày ân hạn** sau khi một kỳ đóng, bảng vẫn hiện kỳ **TRƯỚC** — người đăng bài hôm qua tìm không thấy mình và kết luận bảng hỏng. `metrics` cũng phải đọc: cột nào hiện và theo thứ tự nào là do nó quyết, gán cứng "view rồi cash" sẽ hiện cột thưởng cho ADV đã tắt, và đặt chỉ số xếp hạng xuống thứ hai trên bảng xếp theo tiền.

### Thay đổi hạ tầng chạy

Mỗi ứng dụng hiện chạy `server.js` (Koa) để SSR, `Dockerfile` build `node:14.17.3` rồi `node server.js`. `partner-app` là Next.js — **Koa và `server.js` biến mất**, cách build và chạy container đổi hoàn toàn. Đây là phần việc devops phải biết trước khi tới E2.

**Endpoint bổ sung — toàn bộ là thêm mới:**
- `GET /api/public/partners/app-config` — cấu hình `published` theo domain, hoặc `draft` khi có token xem trước
- `GET|PUT /api/admin/partners/:id/app-config`
- `POST /api/admin/partners/:id/app-config/publish` và `.../restore/:version`
- `GET /api/admin/partners/:id/onboarding-status` — trạng thái 7 tầng (PC-014)

**Bề mặt API mà `partner-app/` phải hiện thực: 70 endpoint** — `user` 27, `bank` 12, `event` 10, `taxCode` 4, `partners` 4, `withdraw` 3, `upload` 2, `notification` 2, còn lại 6.

**Lược đồ `partner_app_configs`:**

Cập nhật v1.8 theo lược đồ đã hiện thực. Hai điểm khác bản phác thảo trước:
**bản nháp và bản đã xuất bản nằm ở hai collection** (bản xuất bản là bất biến, con trỏ
`currentVersion` trỏ tới bản đang chạy — nhờ đó khôi phục chỉ là đổi con trỏ, không đụng
bản nháp), và **`theme` là map mở** thay vì các khoá cố định.

```
partner-app-configs          ← mỗi ADV đúng MỘT bản ghi, chỉ mục duy nhất theo partner
  partner        ObjectId
  draft          <body>
  currentVersion ObjectId    ← rỗng = chưa xuất bản lần nào
  createdAt / updatedAt

partner-app-config-versions  ← bất biến, chỉ mục duy nhất theo (partner, version)
  partner / version / body / changelog / publishedBy / publishedAt

<body>
theme        { colors{}      ← map mở; 18 khoá chuẩn + khoá riêng của ADV
               radius{}      ← map mở; 4 khoá chuẩn, giá trị 0 hợp lệ
               fontFamily, fontFiles[{family, weight, style, url}] }
             ← KHÔNG khoá nào bắt buộc; server hợp nhất với mặc định lúc trả (PC-002)
assets       {}              ← map mở: logo, favicon, ogImage, badge tải app…
content      { articleIds{qa, term, condition},     ← 3, KHÔNG phải 4: xem PC-007
               contact{hotline, email},
               social[{platform, url}],
               website, footerBrandLink }
seo          {}              ← map mở: title, description, keywords, ogImage
modules      {}              ← map cờ bật/tắt phân hệ
sections     [{key, type, props}]
slots        {}                      ← giữ chỗ, chưa hiện thực (PC-009)
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

## 12b. Đối chiếu màn hình với `fecredit` — phần còn nợ

Kiểm ngày 07/09 bằng cách mở song song `partner-app` và trang đang chạy, từng trang một.
**Đã khớp:** trang chủ đối tác, chi tiết chiến dịch, thể lệ, hướng dẫn, bài đăng, liên hệ,
bài viết. **Chưa dựng:**

| Màn / tính năng | Đường dẫn ở `fecredit` | Ghi chú |
|---|---|---|
| Hoa hồng affiliate | `/hoa-hong-affiliate` | Chưa có route nào |
| Chi tiết chiến dịch affiliate | `/:partner/:slug/affiliate/:campaignId` | Endpoint đã biết: `/affiliate/campaigns/:id` |
| Nút nổi góc phải | `components/layout/main/floater-chat` | Mở modal hashtag khi đã đăng nhập; kèm quick actions |
| Popup khuyến mãi | `/news?type=popup` | Hiện 1 lần/giờ, mốc lưu ở `localStorage` |

**Chưa soi được:** cả nhóm màn tài khoản (`/tai-khoan`, `/thong-tin-thanh-toan`,
`/ma-so-thue`, `/thong-tin-dinh-danh`, `/khai-bao-thue`, `/lien-ket-tai-khoan`,
`/hop-dong-dien-tu`, `/trang-ca-nhan`, `/thong-bao`). Chúng đứng sau cổng đăng nhập, mà môi
trường dev đăng nhập bằng Google thật — cần một tài khoản thật mới đối chiếu được. **Đây là
khoảng trống nghiệm thu lớn nhất còn lại**, vì chín màn này chiếm phần lớn số màn của ứng
dụng.

---

## 13. Open Questions

1. **Ngưỡng blast radius** — số đối tác tối đa trên một triển khai trước khi cần tách. Cần trước khi lên production.
2. **Chủ sở hữu quy trình NFR-009** — ai quyết định phân loại một yêu cầu riêng của đối tác. Cần trước M2.
3. **Tài khoản thật trên dev để nghiệm thu nhóm màn đăng nhập** — chín màn tài khoản chưa từng được đối chiếu với trang đang chạy. Cần trước M1.
4. **Chọn đường cho PC-022** — bỏ hẳn `loading.tsx` ở gốc (hiện tại) hay đưa header và footer lên layout. Ảnh hưởng tới việc header hiển thị ADV nào trên tên miền nhiều ADV.
5. **PC-012 nhóm khác biệt hành vi** — 4 file (`not-logged-in` Δ914, `header` Δ659, `models/main` Δ288, `interfaces/event` Δ251) cần **đối tác chấp thuận** trước cutover. Chưa xác định đầu mối phía 5 đối tác. Cần trước M1.

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
| 2.2 | 2026-09-07 | **Đính chính sau khi soi từng trang song song với trang đang chạy.** Mục 7 lên **tám** điều: **affiliate nằm ở prefix riêng** `/affiliate/events/:id/campaigns` và **trả thẳng một mảng** (đường cũ trả 404, mà lớp gọi API biến 404 thành rỗng nên cả khối Affiliate biến mất không dấu vết), và **response bảng xếp hạng mang sẵn siêu dữ liệu chưa ai đọc** (`period`, biên kỳ, `rankBy`, `metrics`, `graceDays`, `isSettling` — nguy nhất là `isSettling`: trong ngày ân hạn bảng hiện kỳ TRƯỚC nên người đăng bài hôm qua tưởng bảng hỏng). **PC-019 lên năm thứ**: SVGO đổi mọi id thành `a` nên 51/193 icon dùng `clipPath` tranh nhau một id và chín trên mười cái bị cắt theo vùng clip của glyph khác; Tailwind v4 đổi mặc định `border-color` sang `currentColor` nên mọi component shadcn viền màu chữ. Bổ sung **PC-020 — gradient là một loại token riêng** (18 màu đơn không mô tả được `fecredit`; lưu thành dữ liệu chứ không phải chuỗi CSS; tối thiểu hai stop; mọi chỗ dùng rơi về màu đơn), **PC-021 — quy ước hiển thị đo TỪNG MÀN** (tiêu đề trang chủ 36px nhưng màn chi tiết 20px; tuổi bài tương đối trong 8 ngày; thẻ chiến dịch khung tỉ lệ cố định + panel đè lên; lớp phủ trắng 10% chứ không phải đen 40% — FE cũ đã thử và bỏ), **PC-022 — `loading.tsx` ở gốc thay luôn cả header/footer**. Bổ sung **mục 12b** liệt kê phần còn nợ: hai màn affiliate, nút nổi, popup, và **cả chín màn tài khoản chưa soi được** vì đứng sau cổng đăng nhập Google thật |
| 2.1 | 2026-09-07 | **Đính chính sau khi chạy `partner-app` với backend dev thật** — mục 7 lên **sáu** điều: bổ sung **ảnh có BỐN hình dạng tuỳ endpoint** (chuỗi URL thuần · `{url}` · `{dimensions:{sm|md|lg:{url}}}` · `{default|medium|high:{url}}`; ảnh bìa chiến dịch ở `covers[0].default`, **không có khoá `photo`**) và **hai endpoint bài đăng dùng hai bộ tên cho cùng ba thứ** (`cover`/`statistic.view.total`/`author` so với `thumbnail`/`view`; ảnh đại diện rơi về `user.socialInfo.photo`). Cả hai chỉ lộ ra với dữ liệu thật — dữ liệu seed không có ảnh nên màn hình trông vẫn đúng. Ghi nhận cấu hình chạy song song trong giai đoạn quá độ: `/partners/app-config` chưa deploy lên dev nên tách `PARTNER_CONFIG_API_BASE_URL` (cấu hình lấy ở local, dữ liệu lấy ở dev) và `DEV_FORCE_ORIGIN` (ghim Origin về host mà môi trường dich biết, vì `allowDomains` của nó không có `localhost`) |
| 2.0 | 2026-09-06 | **Đính chính từ khi dựng `partner-app`** — bổ sung mục 7 "Hợp đồng backend — bốn điều chỉ lộ ra khi render ở server": `Origin` quyết định tập ADV **và giữ nguyên cổng** (không có header thì danh sách chiến dịch rỗng ở mọi ADV mà vẫn `code: 1`; **hệ quả trực tiếp cho BFF proxy**: proxy phải chuyển tiếp `Origin` gốc, không thì bật proxy là mất chiến dịch); thời gian là **chuỗi ISO** qua `ptime.TimeResponse`, không phải `{ unix }`; dòng bảng xếp hạng là `statistic.pointTotal`/`cashTotal` tách `completed` + `pending` và phải **cộng cả hai**; `code: 1` + `data: null` là không-tìm-thấy. Cả bốn đều hỏng im lặng. Bổ sung **PC-019 — bẫy nền tảng khi dựng lại giao diện**: SVGR xoá `viewBox` nên **cả 161 icon** render sai trong khung nhỏ; token `muted` của partner là màu **chữ** còn shadcn coi là màu **nền**; `background` của partner là **nền trang có sắc** nên hộp thoại `bg-background` trông như mất lớp phủ |
| 1.9 | 2026-09-04 | **Viết lại mục 2.6 thành DANH SÁCH PHÁT HIỆN, không phải danh sách đã sửa** — dự án làm trên thư mục mới, không sửa mã của 5 ứng dụng đang chạy; việc xử lý chúng là quyết định của chủ sở hữu và là task độc lập. Bổ sung cột **"hệ mới có mang theo không"**: PRE-2/3/4/5 thì không (lược đồ mới đã chặn sẵn), nhưng **PRE-1 và PRE-8 thì CÓ** nếu port nguyên luồng uỷ quyền theo quyết định 04/09 — nên hai mục này thành ràng buộc thiết kế cho `partner-app`. Bổ sung **PRE-8** (`state` của SSO AccessTrade sinh ra nhưng không bao giờ được kiểm, cộng hai lỗi phụ: băm mốc thời gian nên đoán được, và tính một lần lúc nạp module). Xác minh cụ thể đường khai thác **PRE-1** (`query.state` làm gốc URL chuyển hướng → giao mã uỷ quyền TikTok của nạn nhân cho tên miền kẻ tấn công, 5 app × 2 trang) — làm rõ câu "giữ nguyên 04/09" nói về việc `partner-app` port nguyên luồng, không phải kết luận an toàn. **PRE-4 rộng hơn khảo sát đầu**: 20 chỗ, cả `event-detail` và `partner-home`. **PRE-5 kèm lỗi mới**: `console.log` in nguyên `ctx.request`, tức ghi cookie phiên và `Authorization` vào log. **PRE-3 cần người quyết**: không ai biết hotline/email/mạng xã hội đúng của `lusso` và `parasola` |
| 1.8 | 2026-09-04 | **Đính chính từ khi triển khai** — bước nền backend và màn hình admin đã dựng xong và chạy thử đầu-cuối với MongoDB, Redis và trình duyệt thật. Bổ sung **PC-018 — lược đồ cấu hình do server phát ra**: danh mục section, 18 khoá màu, giá trị mặc định và 7 trường bắt buộc đều lấy từ một endpoint, admin không khai lại; kèm `defaultSections` để ADV mới mở màn hình đã có sẵn trang giống các FE đang chạy. **PC-002**: gỡ ràng buộc "phải khai `primary`" — mặc định là để KHÔNG khai, hợp nhất chạy ở server; ghi rõ `primaryForeground` **không tồn tại** (nhắc nhầm ở v1.2); bo góc `0` là giá trị hợp lệ. **PC-007**: dấu hiệu ADV khác lấy **host** thay vì URL đầy đủ — test đầu-cuối bắt được ca `lusso` mang link CDN của HDBank mà bản cũ bỏ lọt; dò đệ quy qua cả `assets` và mảng object. **PC-015**: ghi hai bẫy sẵn có làm vai trò mới vô hiệu — `constants.Roles` là **danh sách vai trò thứ ba** tách rời `StaffRole`/`StaffRoleName`, và `GenerateRole` bỏ qua mọi môi trường đã có sẵn vai trò; cả hai đã sửa, có test canh. Bổ sung AC cho hai lỗi UI tìm ra trên trình duyệt (hex sai không báo tại chỗ; hộp thoại xuất bản che mất ô cần sửa khi lỗi) |
| 1.7 | 2026-09-04 | Đóng ba câu hỏi về người. **NFR-009 viết lại thành chính sách**: theme chung, ADV không có quyền chỉnh riêng — không cần người đứng cổng. **PC-012 viết lại thành gộp về bản đầy đủ nhất**, kèm ma trận tính năng 5 ADV: `vpbank` chỉ đi sau (thiếu `isMustInputProfile`, `Tooltip`, `useResponsive`, link Q&A), `FAQCollapse` đã là section `faq` — **không ADV nào mất gì, 0 cờ mới, không cần ADV chấp thuận**. **PC-013 bỏ điều kiện xác nhận từ ADV** — giá trị cấu hình sai là lỗi nhập liệu, đã có kiểm tra chéo của PC-007 làm lưới an toàn |
| 1.6 | 2026-09-04 | Bổ sung **PC-017 — nội dung tĩnh, hai phạm vi**: Thể lệ và Hướng dẫn là per-chiến-dịch (`EventRaw.Guide`/`Privacy`, form admin đã có) và **không kéo lên per-ADV**; chỉ Q&A, Điều khoản, Chính sách là per-ADV. Đây là mục thứ năm của mô hình cấu hình theo brief, trước đó chỉ nằm ở Revision History. Ghi hệ quả lịch: ADV chạy 2 chiến dịch cần soạn **7 bài**, không phải 3. Bổ sung **phân tích và ước lượng trình sửa section** vào PC-008 — antd 4.20 có sẵn `Form.List.move()`, khuôn mẫu `covers` 75 dòng, 4 thư viện kéo thả đã cài chưa dùng; ước ~960 dòng, 6–8 ngày; **xếp sau bước 3**, không nằm trên đường găng |
| 1.5 | 2026-09-04 | Bổ sung **mục 2.9 — bản đồ chuyển umi → Next**: bảy hệ con phải viết lại, đối chiếu với lời giải của `creator-os`; bốn bài học họ đã trả giá (`rewrites()` nướng env lúc build · proxy phải `force-dynamic` · refresh single-flight · 403 pwreset tách khỏi 401); **chốt giữ `localStorage`** cho auth, nhưng **lấy BFF proxy**. Sửa lại đánh giá chi phí chuyển nền tảng — trước đó đo `getInitialProps` là đo sai đối tượng. Bổ sung **PRE-6** (mỗi trang nạp hai container GTM, ba ADV bắn vào container của ADV khác) và **PRE-7** (hai bản Bootstrap trên cùng trang). Bổ sung mẫu xem trước không open-redirect vào PC-007 và BFF proxy vào mục 7 |
| 1.4 | 2026-09-04 | Cấu trúc lại mục 6 theo **ba bước của brief dự án**; ADV mẫu bước 3 = **`hdbank`** (branding đơn giản nhất: 5 màu riêng, không gradient). Bổ sung mốc *chạy được với một ADV mẫu nội bộ* làm điều kiện nghiệm thu bước 2. **PC-002**: token từ 2 màu lên **18 màu + 4 bo góc**, mặc định bằng giá trị đang chạy — sửa lỗi rút gọn dựa trên 5 ADV vốn dùng chung một bản thiết kế. **PC-005**: chốt **một landing mặc định bám layout và tính năng của FE hiện tại**, không dựng theme thứ hai; thêm ràng buộc renderer nhận `sections[]` làm dữ liệu, không nhánh theo ADV. Bổ sung **PC-015** (phân quyền — ghi rõ hệ scope 20 mã không chặn ở server ở đâu) và **PC-016** (công cụ trích cấu hình). Bổ sung **chỉ số thành công** vào mục 1, **bốn đường cấu hình xuống component** và **thay đổi hạ tầng chạy** vào mục 7, quy tắc **xem trước đi vòng qua cache** vào PC-007, ánh xạ **ADV ↔ partner** vào mục 0. Xoá mục E0 — các phần việc đó hệ mới không mang theo. Đổi thuật ngữ tự dịch sang từ dev dùng thật |
| 1.3 | 2026-09-04 | Đính chính theo `fecredit/setup.md` — checklist onboard thật do người thực hiện viết. Gỡ ba env chết khỏi lược đồ (`APP_NAME`, `documentShareLink`, `accesstradePartnerId` — không component nào đọc); article ID từ **4 xuống 3** (`SUPPORT_ARTICLE_ID` code không đọc; Thể lệ và Hướng dẫn lấy từ `eventHome.ruleContent`/`guideContent`, dán vào event trên admin). PC-014 viết lại thành **điện tử hoá `setup.md` sẵn có**. **PRE-1: quyết định giữ nguyên luồng TikTok** (04/09), gỡ khỏi tiền đề chặn E2; PC-011 thu về Google và SSO. PC-006 thêm cảnh báo `ORIGIN` gánh hai vai. Đóng 5 câu hỏi mở |
| 1.2 | 2026-09-04 | Viết lại mục 4 theo văn phong của [prd-staff-code-frontend](../employee-code/prd-staff-code-frontend-2026-09-03.md): mỗi FR mở bằng **Vì sao cần**, bẫy đã kiểm chứng nâng thành tiêu đề con `#### ⚠️`, bằng chứng `file:line` đặt ngay trong FR thay vì dồn về mục 2. **Thu hẹp phạm vi còn 5 đối tác đang hoạt động** (`hdbank`, `lusso`, `parasola`, `vpbank`, `fecredit`); 10 thư mục còn lại thuộc đối tác đã ngừng, không thuộc phạm vi. Màn hình 33 → 21, đợt migrate 6 → 4, file khác nhau 33 → 22. **Gỡ PC-009** (slot override) — không còn consumer. **Đổi PC-002**: loại bỏ toàn bộ phép tính màu, hover và active dùng độ mờ theo mô hình `packages/ui/src/button.tsx` của `creator-os`; token cấu hình rút còn `primary` + `primaryForeground` do đo được 152/157 biến SCSS là đồng nhất. Bổ sung **PC-014** (chẩn đoán domain, danh sách kiểm onboard, trạng thái "đang dựng") suy từ phân tích bảy tầng onboard. Bổ sung **NFR-010** (cổng CI chặn giá trị gán cứng) và **NFR-011** (cổng kiểm tra kiểu). Bổ sung mục 2.4 (quyết định về phép tính màu), 2.6 (năm lỗi production), 2.7 (bảy tầng onboard), 2.8 (trạng thái chất lượng mã nguồn) |
