# Tài liệu thiết kế kỹ thuật — Portal chung cho ADV mới (`creator-app/`)

| | |
|---|---|
| **Mã tài liệu** | SDD-AMB-CREATOR-APP-001 |
| **Phiên bản** | 1.0 |
| **Ngày ban hành** | 2026-09-10 |
| **Người biên soạn** | Nguyễn Đăng Định |
| **Người rà soát** | _chưa có_ |
| **Trạng thái** | Bản thảo |
| **Tài liệu yêu cầu** | [prd-creator-app-2026-09-09.md](./prd-creator-app-2026-09-09.md), commit `12414f6` |
| **Tài liệu bối cảnh** | [project-overview-creator-app-2026-09-07.md](./project-overview-creator-app-2026-09-07.md) |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Nhánh tham chiếu** | `release` — số hiệu dòng của `fecredit/` đo trên `origin/release` ngày 2026-09-10 (`f8714b005`). Thư mục `fecredit/` **trùng khớp hoàn toàn** giữa `release` và `develop` (0 tệp khác biệt) |
| **Nhánh phụ trợ** | `feat/partner-app` — nơi duy nhất chứa 37 tệp tầng cấu hình theo ADV. **Chưa có trên `release` lẫn `develop`** (Mục 1.4) |

---

## Quy ước ngôn ngữ

Áp dụng quy ước động từ tình thái theo RFC 2119 (PHẢI, KHÔNG ĐƯỢC, NÊN, CÓ THỂ). Mã định danh yêu cầu `CA-0xx` tham chiếu tới tài liệu yêu cầu.

---

## 1. Mục đích và phạm vi

### 1.1 Mục đích

Mô tả phương án hiện thực hoá prd-creator-app-2026-09-09 — một ứng dụng frontend phục vụ mọi ADV **mới**, mỗi ADV một tên miền và một bộ nhận diện, cấu hình đọc lúc chạy.

### 1.2 Phạm vi

| Thành phần | Mức độ thay đổi |
|---|---|
| `creator-app/` | **Tạo mới**, dựng từ `fecredit/` |
| `backend/` | **Đưa 25 tệp tầng cấu hình từ `feat/partner-app` sang** (Mục 1.4), rồi bổ sung một tuyến tải tệp phông chữ |
| `admin/` | **Đưa 12 tệp màn cấu hình từ `feat/partner-app` sang** (Mục 1.4), rồi bổ sung nút tải lên và hai nút xuất/nhập cấu hình |
| `.github/workflows/` | Bổ sung một nhóm việc dựng ảnh |
| 14 thư mục frontend hiện có | **KHÔNG ĐƯỢC** phát sinh thay đổi, kể cả sửa lỗi (yêu cầu, Mục 3.2) |

### 1.3 Đối tượng đọc

Kỹ sư phát triển giao diện, kỹ sư backend, kỹ sư rà soát mã nguồn, kỹ sư kiểm thử, kỹ sư vận hành hạ tầng.

### 1.4 ⚠️ Tầng cấu hình chưa có trên nhánh phát hành

Kiểm ngày 2026-09-10:

| Nhánh | Số tệp mang tên `partner_app_config` hoặc `partner-app-config` |
|---|---|
| `origin/release` | **0** |
| `origin/develop` | **0** |
| `feat/partner-app` | **37** |

Toàn bộ tầng cấu hình theo ADV — mô hình dữ liệu, đối tượng truy cập, các luật kiểm, sáu tuyến quản trị, vai trò `config_editor`, và màn cấu hình trong phân hệ quản trị — **chỉ tồn tại trên nhánh `feat/partner-app`**, là nhánh đã quyết định không hợp nhất.

Phân bố: 25 tệp thuộc `backend/`, 12 tệp thuộc `admin/`.

**Hệ quả cho kế hoạch.** Tài liệu này KHÔNG ĐƯỢC mô tả tầng cấu hình như thứ "tái sử dụng nguyên trạng". Nó là **một hạng mục công việc thật**, phải đưa sang trước khi mọi thứ phía giao diện có chỗ để đọc cấu hình. Ba cách, cần chủ sở hữu chọn:

| # | Cách | Đánh đổi |
|---|---|---|
| 1 | Chọn lọc 37 tệp từ `feat/partner-app` sang nhánh mới cắt từ `release` | Rẻ nhất; 37 tệp là mã đã có kiểm thử. Phải rà phần phụ thuộc vào những thay đổi khác của nhánh đó |
| 2 | Mở một yêu cầu hợp nhất riêng đưa 37 tệp từ `feat/partner-app` vào `release` trước | Sạch về lịch sử; nhưng nhánh đó còn mang cả `partner-app/` viết bằng Next.js, phải tách ra |
| 3 | Viết lại từ đầu trên `release` | Đắt nhất, không có lý do chính đáng vì mã cũ đã chạy |

Đề xuất: **cách 1**. Ba mươi bảy tệp nằm gọn trong hai thư mục và không giao với `partner-app/`.

---

## 2. Nguyên tắc thiết kế

| # | Nguyên tắc | Diễn giải |
|---|---|---|
| P1 | Tái sử dụng bản cài đặt đã qua kiểm thử | Nguồn tham chiếu là `fecredit/` — bản rẽ nhánh gần nhất (28/08/2026), lớp thương hiệu vừa được làm sạch có hệ thống |
| P2 | Giữ nền tảng `umi`, **nâng lên phiên bản 4** | Không đổi sang Next.js (tài liệu bối cảnh, Mục 3.3). Nâng phiên bản trong cùng nền tảng là việc khác với đổi nền tảng: giữ nguyên cây tuyến, cách khai cấu hình và mô hình trạng thái. Chi tiết tại Mục 4.0 |
| P3 | Bóc thương hiệu **trước**, thêm tính năng **sau** | Rẽ nhánh rồi bổ sung dần sẽ cho ra bản rẽ nhánh thứ 15, không phải portal chung (tài liệu bối cảnh, Mục 4) |
| P4 | Không suy đoán khi dữ liệu không xác định | Tên miền không phân giải ra ADV nào PHẢI dừng lại và báo, KHÔNG ĐƯỢC chuyển hướng |
| P5 | Cấu hình quyết định **giá trị**, mã nguồn quyết định **cấu trúc** | Bố cục dùng chung cho mọi ADV (CA-007). Một yêu cầu riêng chỉ có hai đường: thành cấu hình cho mọi ADV, hoặc bị từ chối (NFR-006) |
| P6 | Trạng thái theo yêu cầu KHÔNG ĐƯỢC nằm ở phạm vi tiến trình | Một tiến trình phục vụ nhiều tên miền. Mục 3 liệt kê bốn vi phạm đã xác minh |

### 2.1 Bảng đối chiếu nguồn — đích

| Chức năng | Nguồn (`fecredit/`) | Đích (`creator-app/`) | Mức độ |
|---|---|---|---|
| Toàn bộ cây trang và tuyến | 22 trang, 29 tuyến, 217 tệp `.tsx` | tương ứng | Tái sử dụng |
| Trình biên dịch SCSS | `config/config.ts:12` — `require('node-sass')` | `require('sass')` | **Thay thế** |
| Phân giải ADV | `process.env.COMMON_PARTNER` (5 tệp) | Phân giải theo `Host` | **Viết mới** |
| Trang gốc | `src/pages/main-home/index.tsx` — 172 dòng, **1 dòng còn sống** | Ba nhánh theo số ADV | **Viết lại** |
| Nguồn ảnh | `src/configs/image.ts` — `require()` lúc dựng | Địa chỉ từ cấu hình | **Viết lại** |
| Phông chữ | `src/font.scss` + `src/global.scss:5` | Biến CSS, khối `@font-face` sinh lúc chạy | **Viết lại** |
| Tầng thành phần | `react-bootstrap` (92 tệp) + `antd` (24 tệp) | `antd` | **Hợp nhất về một** |
| Tầng bố cục | Lớp tiện ích Bootstrap (1.728 lượt) | Tailwind | **Chuyển đổi có bảng quy đổi** |
| Bảng màu | 408 mã màu gán cứng trong SCSS | Biến CSS `--adv-*` từ một tệp token | **Viết lại** |
| Địa chỉ gốc phía máy chủ | `src/utils/helper.ts:691-699` — hằng số lúc dựng | Đọc từ yêu cầu | **Sửa** |
| Tham số uỷ quyền SSO | `…/accesstrade-section/index.tsx:14-26` — hằng số phạm vi mô-đun | Hàm gọi mỗi lần bấm | **Sửa** |
| Đích chuyển tiếp TikTok | `pages/login-tiktok/index.tsx:14`, `connect-tiktok/index.tsx:12` | Kiểm theo danh sách cho phép | **Sửa** |
| Trạng thái toàn cục | `server.js:25-26` | Gỡ bỏ | **Gỡ** |
| Cấu hình theo ADV ở backend | `partner_app_configs` + 6 tuyến quản trị | không đổi | **Tái sử dụng** |
| Màn cấu hình quản trị | `admin/src/pages/partner-app-config/` | bổ sung tải tệp, xuất/nhập | Mở rộng |

### 2.2 Ràng buộc bắt buộc

| # | Ràng buộc |
|---|---|
| C1 | Kết xuất phía máy chủ PHẢI trả về **một chuỗi HTML đầy đủ**, không phải dòng dữ liệu — nếu không thì mất khả năng chèn khối `<style>` theo ADV (Mục 3.1). Trên `umi` 3 điều này tương ứng `ssr.mode: 'string'`; trên `umi` 4 PHẢI xác minh lại trước khi bắt đầu (Mục 4.0) |
| C2 | KHÔNG ĐƯỢC chèn giá trị theo ADV vào `src/pages/document.ejs`. Tệp này biên dịch một lần lúc dựng, dùng chung cho mọi tên miền |
| C3 | KHÔNG ĐƯỢC đọc hoặc ghi kho trạng thái ở đường kết xuất phía máy chủ (Mục 3.3) |
| C4 | KHÔNG ĐƯỢC để giá trị theo ADV trong khối `define:` của `config/*.ts` — webpack thay giá trị lúc biên dịch |
| C5 | Tên miền không phân giải ra ADV nào PHẢI hiện trang báo lỗi. KHÔNG ĐƯỢC chuyển hướng |
| C6 | Mọi bản ghi nhật ký PHẢI mang định danh ADV và tên miền, kể từ dòng đầu tiên (NFR-008) |
| C7 | KHÔNG ĐƯỢC phát sinh thay đổi tại 14 thư mục frontend hiện có |
| C8 | Khối `@font-face` sinh lúc chạy PHẢI kèm `font-display: swap`, và `src: url()` chỉ nhận giao thức HTTPS |
| C9 | KHÔNG ĐƯỢC để `bootstrap` hoặc `react-bootstrap` tồn tại sau khi chuyển đổi xong. Cổng gác: tìm kiếm trong `src/` trả về 0 kết quả trước khi gỡ khỏi `package.json` (Mục 4.0.5) |
| C10 | Bảng màu của Tailwind PHẢI trỏ vào biến CSS `var(--adv-*)`, KHÔNG ĐƯỢC gán mã màu trực tiếp |
| C11 | KHÔNG ĐƯỢC dùng lớp tiện ích để ghi đè phần bên trong thành phần `antd`. Phân vai: `antd` lo thành phần, Tailwind lo bố cục |
| C12 | Chuyển lớp tiện ích Bootstrap sang Tailwind PHẢI dùng bảng quy đổi thang đo, KHÔNG ĐƯỢC đổi tên máy móc — cùng tên lớp nhưng khác giá trị |

---

## 3. Phân tích nền tảng — sáu phát hiện đã xác minh

Mục này ghi kết quả đo trực tiếp trên mã nguồn và trên một lần dựng thật. Bốn phát hiện đầu là **điều kiện tiên quyết**: bỏ qua thì lỗi chỉ lộ ra khi đã có ADV thứ hai chạy chung một tiến trình.

### 3.1 Cơ chế chèn nội dung vào `<head>` — đã có sẵn trong `umi`

Bản dựng phía máy chủ của `umi` tự chèn khối định kiểu bằng phép thay chuỗi:

```js
// dist/umi.server.js — hàm handleHTML của umi
html = html.replace('</head>', `${cssChunkSet.join(EOL)}${EOL}</head>`);
...
return html.replace(rootHTML, newRootHTML);
```

Ba hệ quả:

1. `render()` trả về **một tài liệu HTML đầy đủ** dạng chuỗi.
2. Phép thay chuỗi `</head>` là cơ chế nội bộ của `umi`, không phải thủ thuật ngoài luồng.
3. `fecredit` khai `ssr: { forceInitial: true, mode: 'string' }` (`config/config.prod.ts:49`), rơi vào nhánh chuỗi. Nhánh `stream` trả về dòng dữ liệu — nguồn gốc của ràng buộc C1.

`server.js` đã nhận `{ html }` rồi gán vào thân phản hồi, và đang chạy trên môi trường thật.

### 3.2 Kênh truyền dữ liệu theo yêu cầu — cũng đã có sẵn

`server.js` truyền đối tượng yêu cầu vào bản dựng phía máy chủ:

```js
await render({ path: ctx.request.url, getInitialPropsCtx: { req: ctx.request } });
```

`umi` gộp thẳng vào ngữ cảnh đưa cho `getInitialProps`:

```js
defaultCtx = { isServer: true, history, ...opts.getInitialPropsCtx };
```

Ba trang đang dùng kênh này (`pages/partner-home/index.tsx:260`, `layouts/event-detail/index.tsx:233`, và bản tương ứng ở `hdbank`, `parasola`), gọi tầng dịch vụ rồi trả dữ liệu; `umi` tự truyền kết quả xuống trình duyệt.

**Kết luận:** năng lực "đọc cấu hình theo từng yêu cầu" không phải xây mới. Khoảng cách duy nhất là các trang đang phân giải theo tham số `:partner` trên đường dẫn và theo hằng số `process.env.ORIGIN`, thay vì theo `Host`.

### 3.3 Kho trạng thái nằm ở phạm vi tiến trình

```ts
// src/.umi/plugin-dva/dva.ts:16 — mã do umi sinh
let app: any = null;
export function _onCreate(options = {}) { app = dva({...}); return app; }
export function getApp() { return app; }
```

```tsx
// src/.umi/plugin-dva/runtime.tsx
ssr: {
  modifyGetInitialPropsCtx: async (ctx) => {
    if (process.env.__IS_SERVER && ctx.history) {
      const tmpApp = _onCreate({ history: ctx.history });   // ghi đè biến mô-đun
      ...
    }
    const { _store } = getApp();      // đọc lại biến mô-đun, không đọc tmpApp
    ctx.store = _store;
```

Với hai yêu cầu chạy chồng nhau:

```
yêu cầu A (adv-a.vn)   _onCreate  →  app = store_A
yêu cầu B (adv-b.vn)   _onCreate  →  app = store_B
yêu cầu A              getApp()   →  nhận store_B
```

Đây là mã do `umi` sinh ra, **KHÔNG sửa được trong mã ứng dụng**. Phương án: không chạm kho trạng thái ở đường kết xuất phía máy chủ (C3). Ràng buộc này áp cho cả `responseInterceptors` tại `src/app.tsx:112-118`, nơi tầng giao vận đang gọi thẳng `getDvaApp()._store.dispatch` khi gặp mã 401.

**Chưa xác minh trên trình duyệt.** Kết luận rút từ đọc mã sinh tự động; cần một lần chạy hai tên miền trên cùng tiến trình để quan sát.

### 3.4 Địa chỉ gốc phía máy chủ là hằng số lúc dựng

```ts
// src/utils/helper.ts:691-699
function getCurrentOrigin() {
  if (typeof window !== 'undefined') {
    origin = window.location.origin + '/';   // trình duyệt: đúng theo từng tên miền
  } else {
    origin = process.env.ORIGIN;             // máy chủ: HẰNG SỐ lúc dựng
  }
```

Tầng dịch vụ lọc tập ADV theo tiêu đề `Origin`. Một bản chạy phục vụ nhiều tên miền mà luôn gửi cùng một giá trị thì mọi ADV ngoài giá trị đã nướng vào gói dựng sẽ nhận sai tập dữ liệu — và sai kiểu này trả về danh sách rỗng kèm mã thành công, không có lỗi nào để đọc.

Nặng thêm: hàm được gọi ở **phạm vi mô-đun** tại ba vị trí, tức tính một lần lúc nạp rồi dùng suốt vòng đời tiến trình:

```
src/components/layout/main/header/components/modal-login.tsx:10
src/pages/home/components/post-modal/components/connect-tiktok/index.tsx:4
src/pages/account/management/components/tiktok-section/index.tsx:4
```

Và hai trang cùng nghiệp vụ đang hành xử khác nhau: `pages/partner-home/index.tsx:278` truyền tiêu đề `origin` bằng tay, `layouts/event-detail/index.tsx:246` không truyền. `src/app.tsx:94-104` không có bộ chặn nào bổ sung tiêu đề này.

### 3.5 Tham số uỷ quyền sinh một lần cho cả tiến trình

```ts
// src/pages/account/management/components/accesstrade-section/index.tsx:14-26
const createState = () => shajs('sha256').update(moment().valueOf().toString()).digest('hex');

export const SSO_PARAMS = {                       // HẰNG SỐ MÔ-ĐUN
  redirect_uri: AppConst.ssoParams.redirectUri,   // dựng từ NEXT_PUBLIC_ORIGIN — hằng số lúc dựng
  state: createState(),                           // chạy MỘT LẦN lúc nạp mô-đun
};
```

Ba khiếm khuyết chồng nhau: tham số `state` dùng chung cho mọi người dùng và mọi ADV trong vòng đời tiến trình; giá trị sinh từ mốc thời gian mili giây nên đoán được; nhánh quay về chỉ đọc mã uỷ quyền mà **không đối chiếu** `state`.

Cùng họ, hai trang uỷ quyền TikTok dùng tham số `state` từ địa chỉ làm **gốc** của địa chỉ chuyển tiếp, không kiểm danh sách cho phép:

```js
// pages/login-tiktok/index.tsx:14 và pages/connect-tiktok/index.tsx:12
window.location.href = `${query.state}dang-nhap-tiktok?code=${query.code}&redirect_uri=${redirectUri}`;
```

Với một bản chạy phục vụ N tên miền, danh sách cho phép PHẢI tra theo ADV lúc chạy — không còn là một hằng số cho mỗi ứng dụng như hiện nay.

### 3.6 Kết quả một lần dựng thật — bốn rào chắn của chuỗi công cụ

Đo ngày 2026-09-10 trên bản sao `fecredit`:

| # | Rào chắn | Biểu hiện | Xử lý |
|---|---|---|---|
| 1 | Trình quản lý gói | `npm install` dừng ở xung đột phụ thuộc ngang cấp (`antd-img-crop` với React 16) | Dùng `yarn --ignore-optional`, khớp với `Dockerfile` |
| 2 | Trình biên dịch SCSS | `config/config.ts:12` khai `implementation: require('node-sass')`, ghi đè mặc định của `@umijs/plugin-sass` | Đổi thành `require('sass')`. `umi generate tmp` và bản dựng đầy đủ đều chạy sạch |
| 3 | Thư viện mã hoá | Node 18 trở lên dùng OpenSSL 3, bỏ thuật toán băm mà webpack 4 cần → `ERR_OSSL_EVP_UNSUPPORTED` | Thêm `NODE_OPTIONS=--openssl-legacy-provider` vào các lệnh dựng |
| 4 | Trình biên dịch kiểu | TypeScript 4.4.4 không đọc nổi tệp khai báo của `antd-img-crop`, `remark-gfm` — dừng ở lỗi cú pháp | Nâng lên TypeScript 5.9.3, bổ sung `@types/jest` |

**Ghi nhận về `node-sass`.** Gói này là thứ ghim ứng dụng vào Node 14 ở khâu cài đặt, nhưng **không phải** rào chắn duy nhất. Rào chắn thật của việc nâng Node là **webpack 4** trong `umi` 3 (rào chắn số 3). Đây là căn cứ trực tiếp cho quyết định nâng `umi` lên dòng 4 tại Mục 4.0: cả bốn rào chắn ở bảng trên đều là hệ quả của việc đứng lại ở `umi` 3, và rào chắn số 3 không có cách xử lý nào ngoài việc thêm cờ tương thích cho một thuật toán đã bị loại bỏ.

**Kết quả dựng:** thành công sau 48 giây. `dist` 14 MB, `umi.js` 3,5 MB, `umi.server.js` 4,2 MB, `umi.css` 679 KB. Máy chủ chạy, trả mã 200 kèm HTML kết xuất sẵn.

**Trạng thái cổng gác kiểu:** sau khi nâng trình biên dịch và bổ sung khai báo kiểu cho bộ kiểm thử, còn **230 lỗi** trong mã ứng dụng — 67 lỗi biến khai mà không dùng, 56 lỗi truy cập thuộc tính không tồn tại, 30 lỗi gán sai kiểu, 77 lỗi còn lại. Các lỗi này tồn tại sẵn trong `fecredit`; chúng chưa từng lộ ra vì trình biên dịch không chạy tới nơi. Phương án tại Mục 6.3.

---

## 4. Thiết kế chi tiết

### 4.0 Nâng nền tảng `umi` 3 → 4

**Quyết định:** giữ `umi`, nâng lên dòng 4. Mốc tham chiếu trong nhà: `FE/bank-mall/frontend` và `FE/KYC-PIT/client` đều chạy `umi ^4.1.4` với `@umijs/plugins ^4.1.4`, cùng bố cục `config/` và cùng dùng `yarn` như ứng dụng này.

#### 4.0.1 Khối lượng đo được

| Hạng mục | Hiện tại | Sau khi nâng | Phạm vi ảnh hưởng |
|---|---|---|---|
| `umi` | 3.5.20 (webpack 4) | 4.1.4 | toàn ứng dụng |
| React | 16.x | 17 hoặc 18 | toàn ứng dụng |
| `antd` | 4, đến **gián tiếp** qua `@umijs/preset-react` 1.x — không khai trong `package.json` | 5, khai tường minh qua `@umijs/plugins/dist/antd` | **24 tệp, 17 thành phần**: `Carousel`, `DatePicker`, `Image`, `Input`, `Modal`, `Popconfirm`, `Segmented`, `Skeleton`, `Spin`, `Statistic`, `Steps`, `Switch`, `Table`, `Tabs`, `Tag`, `Tooltip`, `Upload` |
| Thư viện thời gian | `moment` | `dayjs` (yêu cầu của `antd` 5) | **15 tệp** |
| Tầng trạng thái | `dva` qua `@umijs/preset-react` | `@umijs/plugins/dist/dva` | **50/89 lượt** dùng API `umi` là `useDispatch`, `useSelector`, `connect` |
| Tầng giao vận | `export const request` trong `src/app.tsx` | `@umijs/plugins/dist/request` | 1 điểm khai báo + bộ chặn |
| SCSS | `@umijs/plugin-sass` + khai `implementation` | `umi` 4 hỗ trợ sẵn | gỡ một phụ thuộc |
| Lệnh nạp sau cài đặt | `umi generate tmp` | `umi setup` | 1 dòng |

**Bề mặt tiếp xúc với `umi`:** 82 trong 289 tệp mã nguồn nhập từ `'umi'`. Phân bố lượt dùng: `useDispatch` 26 · `useSelector` 24 · `useLocation` 13 · `useParams` 9 · `isBrowser` 7 · `connect` 7 · `history` 2 · `Redirect` 2 · `Helmet` 2 · `request` 1 · `getDvaApp` 1 · `Link` 1.

Đa số là API tầng trạng thái, và `umi` 4 giữ `dva` dưới dạng gói bổ trợ — nên phần lớn 82 tệp này không phải viết lại, chỉ đổi nguồn nhập nếu tên có thay đổi.

#### 4.0.2 Bốn lợi ích đo được

| # | Lợi ích | Căn cứ |
|---|---|---|
| 1 | Bỏ được cờ `--openssl-legacy-provider` | Rào chắn số 3 tại Mục 3.6 là webpack 4; `umi` 4 không còn dùng thuật toán băm đã bị OpenSSL 3 loại bỏ |
| 2 | Chạy được trên Node 18/20 mà không cần cờ tương thích | hệ quả của (1) |
| 3 | **Có sẵn cơ chế tách gói** | Bản dựng hiện tại không bật tách gói: `umi.js` 3,5 MB và `umi.css` 679 KB tải cho mọi ADV, kể cả trang không dùng tới. Mốc tham chiếu trong nhà khai `codeSplitting: { jsStrategy: 'granularChunks' }` |
| 4 | Gỡ được một tầng phụ thuộc | `@umijs/plugin-sass` và việc khai `implementation` không còn cần thiết |

Lợi ích (3) trực tiếp giảm nhẹ một điểm yếu cố hữu của mô hình một ứng dụng phục vụ nhiều ADV: mọi ADV cùng tải một gói chứa cả những màn mà cờ tính năng của họ đã tắt.

#### 4.0.3 Rủi ro then chốt — kết xuất phía máy chủ, CHƯA XÁC MINH

Toàn bộ thiết kế tại Mục 4.1 và 4.2 dựa trên hai cơ chế của `umi` 3:

1. `render()` trả về một **chuỗi HTML đầy đủ**, cho phép chèn khối `<style>` theo ADV trước khi trả về (Mục 3.1)
2. `getInitialPropsCtx` truyền đối tượng yêu cầu vào `getInitialProps` của từng trang (Mục 3.2)

**Chưa xác minh `umi` 4 còn giữ nguyên hai cơ chế này.** Hai dự án `umi` 4 trong nhà đều là ứng dụng kết xuất phía trình duyệt, không bật kết xuất phía máy chủ, nên không dùng làm mốc được; và tài liệu chính thức chưa tra được tại thời điểm biên soạn.

**Việc phải làm đầu tiên của đợt 1** — trước khi động tới bất kỳ hạng mục nào khác:

> Dựng một ứng dụng `umi` 4 tối thiểu, bật kết xuất phía máy chủ, kiểm hai điều: (a) đầu ra là chuỗi hay dòng dữ liệu; (b) đối tượng yêu cầu có tới được tầng lấy dữ liệu ban đầu hay không.

**Ba phương án dự phòng, xếp theo thứ tự ưu tiên nếu (a) hoặc (b) không đạt:**

| # | Phương án | Đánh đổi |
|---|---|---|
| 1 | Chèn khối `<style>` tại tầng máy chủ proxy (`nginx/`) thay vì trong `server.js` | Tầng proxy phải gọi được endpoint cấu hình; thêm một chỗ giữ trạng thái |
| 2 | Giữ `umi` 3 cho đợt 1, nâng phiên bản ở đợt sau | Phải làm hai lần phần chạm vào tầng khởi tạo |
| 3 | Chuyển sang tự dựng máy chủ kết xuất, không dùng cơ chế của `umi` | Khối lượng lớn nhất; chỉ chọn khi hai phương án trên đều không khả thi |

#### 4.0.4 Tầng định kiểu

Số đo trên `src/`:

| Hạng mục | Số đo |
|---|---|
| Tệp `.scss` | 65 tệp, 5.221 dòng |
| Nhập kiểu toàn cục (`import './x.scss'`) | 51 điểm |
| Nhập kiểu dạng mô-đun (`import styles from './x.scss'`) | 9 điểm, 25 lượt dùng `styles.<lớp>` |
| Tệp đặt tên theo quy ước mô-đun (`*.module.scss`) | **0** |
| Cú pháp `@import` của Sass | 8 điểm |
| Cú pháp `@use` | 0 |
| Lượt dùng lớp tiện ích Bootstrap trong `.tsx` | 1.728 |
| Lớp `btn-primary` và `btn-outline-primary` | 17 |

**Bốn hạng mục phát sinh:**

**(a) Quy ước tệp kiểu dạng mô-đun — hỏng im lặng.** Chín tệp đang nhập kiểu dạng mô-đun mà **không** dùng đuôi `.module.scss`:

```
components/app/button/index.tsx:8            import styles from './index.scss';
components/app/badge/index.tsx:8             import styles from './style.scss';
components/app/number-input/index.tsx:8      import styles from './styles.scss';
components/app/confirm-modal/index.tsx:16    import styles from './style.scss';
components/app/loading-indicator/index.tsx:5 import styles from './style.scss';
components/app/button-scroll-top/index.tsx:5 import styles from './styles.scss';
components/common/error-boundary/index.tsx:6 import styles from './styles.scss';
pages/home/components/logged-in-view/index.tsx:5   import styles from './tabs.scss';
pages/home/components/statistic/table.tsx:4        import styles from './style.scss';
```

`umi` 3 chấp nhận cách nhập này. Dòng 4 đòi đuôi `.module.*`. Nếu không đổi tên, biểu thức `styles.<lớp>` trả về giá trị không xác định — lớp biến mất khỏi thẻ, **việc dựng vẫn thành công, không có cảnh báo nào**. Ví dụ tại `components/app/button/index.tsx:63`, lớp `styles.linearGradient` mất thì nút nền chuyển sắc trở về nền trống.

Xử lý: đổi tên 9 tệp và sửa 9 dòng nhập tương ứng. PHẢI kiểm bằng mắt sau khi đổi, vì không có cơ chế tự động nào bắt được lỗi loại này.

**(b) Cú pháp `@import` của Sass đã vào diện khai tử.** 8 điểm dùng `@import`, 0 điểm dùng `@use`. Các bản Sass từ 1.80 phát cảnh báo và sẽ gỡ bỏ ở bản sau. Nâng `umi` thường kéo theo bản Sass mới hơn, nên chuyển sang `@use` và `@forward` NÊN làm trong cùng đợt.

**(c) Bốn trăm lẻ tám mã màu gán cứng làm vô hiệu cơ chế nhận diện.** 408 lượt dùng mã màu thập lục phân trong SCSS, **116 màu duy nhất**, trong khi bộ token chuẩn chỉ có 18 màu.

Hệ quả trực tiếp: ADV đổi màu chính trên phân hệ quản trị thì chỉ những chỗ đọc token mới đổi; 408 chỗ còn lại giữ nguyên màu của bản nền. Người vận hành thấy màu đổi một phần và không có gì để tra.

Đây là vấn đề nghiêm trọng nhất của tầng định kiểu xét theo mục tiêu dự án, và nó **độc lập với việc dùng bộ khung nào**. Xử lý tại Mục 4.0.5.

**(d) Hai bản Bootstrap cùng nạp trên mỗi trang.**

```
package.json      bootstrap 5.2.3  →  biên dịch từ SCSS, mang biến thương hiệu (global.scss:2)
document.ejs:47   bootstrap 5.3.2  →  CSS đầy đủ từ mạng phân phối
document.ejs:30   bootstrap 5.2.3  →  gói JavaScript từ một mạng phân phối khác
```

Bộ tải từ mạng phân phối mang màu mặc định của Bootstrap. Với luật cùng độ ưu tiên thì bộ đứng sau thắng, nên màu thương hiệu biên dịch từ SCSS có thể đang bị đè.

Đây nhiều khả năng là **nguyên nhân gốc của 195 lượt `!important`** trong SCSS: khi màu thương hiệu bị đè, cách nhanh nhất để sửa là tăng độ ưu tiên.

**(e) Thứ tự chèn của khối định kiểu theo ADV.** Khối `<style id="adv-theme">` PHẢI thắng CSS của bộ khung. Cơ chế hiện tại đặt nó **sau** các thẻ liên kết CSS do `umi` chèn, vì phép thay chuỗi chạy trên kết quả đã hoàn chỉnh (Mục 3.1) — nên thứ tự đúng theo thiết kế. Nếu dòng 4 đổi cách phát ra CSS, hoặc khi `antd` 5 chèn kiểu của nó, điểm này PHẢI kiểm lại.

**Số đo bổ sung:** 195 `!important` · 216 lớp tự định nghĩa, trong đó **79 lớp (37%) không thấy dùng** trong tệp `.tsx` nào · 10 điểm ngắt màn hình khác nhau, gồm những giá trị lẻ như `433px`, `305px` · `umi.css` sau khi dựng 679 KB.

---

#### 4.0.5 Quyết định: chuyển sang `antd` + Tailwind, bỏ hẳn Bootstrap

**Quyết định (10/09/2026):** `creator-app` dùng **`antd` làm tầng thành phần** và **Tailwind làm tầng bố cục**; gỡ bỏ hoàn toàn `bootstrap` và `react-bootstrap`.

Mô hình này khớp với hai dự án `umi` 4 trong nhà (`FE/bank-mall/frontend`, `FE/KYC-PIT/client`) — cả hai đều chạy `antd` 5 cộng Tailwind.

**Phân vai bắt buộc:** `antd` lo thành phần, Tailwind lo bố cục và khoảng cách. KHÔNG ĐƯỢC dùng lớp tiện ích để ghi đè phần bên trong thành phần `antd`.

##### Căn cứ

Ranh giới giữa hai thư viện trong mã nguồn hiện tại đã tự hình thành đúng chỗ:

```
antd            →  màn nghiệp vụ: eKYC, hợp đồng, thuế, ngân hàng, bảng, tải tệp, chọn ngày
react-bootstrap →  màn trình bày: trang chủ, chiến dịch, bố cục, thẻ, biểu mẫu
```

`antd` đang giữ đúng phần khó tự dựng nhất — `Steps` cho luồng nhiều bước, `Table`, `Upload`, `DatePicker`, `Popconfirm` — ở 23 điểm dùng trên 24 tệp. Việc chuyển đổi vì thế là **mở rộng vai trò của thư viện đang dùng**, không phải thay bằng một thư viện xa lạ.

##### Khối lượng đo được

92 tệp dùng `react-bootstrap`, phân bố rất phẳng:

| Số thành phần dùng trong một tệp | Số tệp |
|---|---|
| 1 | **58** |
| 2 | 26 |
| 3 | 7 |
| 4 | 1 |

Mười tệp đã dùng đồng thời cả `antd` lẫn `react-bootstrap`, nên việc hai thư viện cùng tồn tại không phải điều mới.

##### Bảng quy đổi

**Nhóm 1 — hoán đổi thẳng sang `antd`, khoảng 30 tệp**

| `react-bootstrap` | `antd` |
|---|---|
| `Spinner` (6 tệp) | `Spin` |
| `Card` (4) | `Card` |
| `Button` (3) | `Button` |
| `Modal` (2) | `Modal` |
| `Dropdown` (2) | `Dropdown` |
| `Badge` (2) | `Tag` |
| `ListGroup` (2) | `List` |
| `Carousel` · `Image` · `Alert` · `Toast`/`ToastContainer` | `Carousel` · `Image` · `Alert` · `message` |

**Nhóm 2 — sang Tailwind, không cần `antd`**

| `react-bootstrap` | Thay bằng |
|---|---|
| `Ratio` (3) | lớp tỉ lệ khung của Tailwind |
| `Container` · `Row` · `Col` | lưới Tailwind |
| `Navbar` · `Offcanvas` | tự dựng bằng Tailwind |
| `SSRProvider` | **bỏ hẳn** — chỉ là công cụ sinh định danh của `react-bootstrap` |

**Nhóm 3 — biểu mẫu, 27 tệp, phần việc thật**

```
<Form.Control  14 lượt      <Form.Check   5 lượt
<Form.Group    10           <Form.Text    3
<Form.Label     9           <Form.Select  1

16 điểm có kiểm hợp lệ (isInvalid, Feedback, validated, noValidate)
```

`Form` của `react-bootstrap` là lớp trình bày; `Form` của `antd` mang mô hình dữ liệu riêng. Không hoán đổi một-một được. Chia đôi:

- Điểm **không** kiểm hợp lệ → thẻ `<form>` thuần cộng `Input` của `antd` cộng Tailwind
- **16 điểm có kiểm hợp lệ** → chuyển sang `Form` của `antd`, viết lại luật kiểm. Đây là phần tốn công nhất của cả việc chuyển đổi

**Nhóm 4 — lớp tiện ích, 1.728 lượt**

Chuyển sang Tailwind bằng **bảng quy đổi thang đo**, KHÔNG ĐƯỢC đổi tên máy móc: `mt-3` của Bootstrap là `1rem`, của Tailwind là `0,75rem`. 731 lượt lớp khoảng cách nằm trong nhóm này, và sai lệch kiểu này **không phát sinh lỗi nào** khi dựng.

##### Cấu hình Tailwind bắt buộc

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.tsx'],
  theme: {
    extend: {
      colors: {                       // (1)
        primary: 'var(--adv-primary)',
        // …18 token, KHÔNG gán mã màu trực tiếp
      },
    },
  },
};
```

**(1)** Màu PHẢI trỏ vào biến CSS, KHÔNG ĐƯỢC gán mã màu. Dự án tham chiếu `bank-mall` đang gán trực tiếp `'#CC3366'`; làm vậy ở đây thì Tailwind trở thành nguồn thứ hai của đúng vấn đề 408 mã màu, và ADV đổi màu thì lớp Tailwind không đổi theo.

Không cần đặt tiền tố cho lớp Tailwind, vì Bootstrap bị gỡ bỏ hoàn toàn — không còn nguy cơ trùng tên lớp.

##### Hai đường theming song song

`antd` 5 tự suy ra dải mười sắc độ từ `colorPrimary` bằng thuật toán, nên truyền một biến CSS vào là không chạy. Cấu hình của ADV đã được đọc ở tầng máy chủ theo từng yêu cầu (Mục 4.1), nên mã màu thật có sẵn:

```
Tailwind và CSS tự viết  →  biến CSS --adv-*        (chèn vào <head>, Mục 4.2)
antd                     →  token của ConfigProvider (mã màu thật, cùng bản ghi cấu hình)
```

Hai đường PHẢI đọc **cùng một bản ghi cấu hình**. Lệch nguồn thì màu đúng ở phần này và sai ở phần kia, và không có cơ chế nào phát hiện.

##### Điều kiện bắt buộc trước khi bắt đầu

**PHẢI có bộ ảnh đối chiếu trước.** 92 tệp đổi hình dạng, kho mã hiện **không có bộ ảnh chuẩn nào**, và không có kiểm thử tự động nào bắt được lỗi bố cục. Thiếu bước này thì toàn bộ việc chuyển đổi là sửa mà không đo được.

##### Thứ tự

```
1. Dựng bộ ảnh đối chiếu cho các màn chính
2. Nhóm 1 và nhóm 2 — cơ học, khoảng 40 tệp
3. Nhóm 4 — bảng quy đổi thang đo, chuyển theo từng màn
4. Nhóm 3 — biểu mẫu, 27 tệp
5. Gỡ `bootstrap` và `react-bootstrap` khỏi `package.json`
   ← chỉ khi tìm kiếm trong `src/` trả về 0 kết quả
6. Token hoá 408 mã màu, bật cổng gác cấm mã màu ngoài tệp token
```

Bước 5 là cổng gác của chính việc chuyển đổi: chừng nào còn một điểm nhập `react-bootstrap` thì hai bộ khung vẫn cùng tồn tại.

##### Ba việc dọn kèm theo

| # | Việc | Số đo hiện tại |
|---|---|---|
| 1 | Gỡ hai thẻ Bootstrap tải từ mạng phân phối ở `document.ejs` | 2 dòng, bỏ khoảng 195 KB mỗi lượt tải |
| 2 | Rà lại `!important` sau khi gỡ nguyên nhân gốc | 195 lượt |
| 3 | Xoá lớp không dùng, chuẩn hoá điểm ngắt màn hình | 79 lớp · 10 điểm ngắt |

#### 4.0.6 Đối chiếu cú pháp umi 3 → umi 4

Mục này đối chiếu trực tiếp với source của hai dự án umi 4 trong nhà (`FE/KYC-PIT/client`, `FE/bank-mall/frontend`). Cột **Nguồn** ghi rõ điều nào đã xác minh trên source thật, điều nào còn phải tra document.

##### a. Routing — react-router v6

umi 4 chạy trên react-router v6. Đây là nhóm breaking change lớn nhất.

| Hạng mục | umi 3 (hiện tại) | umi 4 | Số lượng phải sửa | Nguồn |
|---|---|---|---|---|
| Khai route | `{ path, component }` | **giữ nguyên** | 24 route, không đổi | đã xác minh — `KYC-PIT/config/routes.ts` |
| Nested route | `routes: [...]` | giữ nguyên | 3 chỗ | như trên |
| `<Redirect to="…" />` | có | **bỏ**, thay bằng `<Navigate to="…" />` | 2 chỗ: `wrappers/auth.tsx:15`, `pages/main-home/index.tsx:15` | đã xác minh — repo umi 4 dùng `Navigate`, không còn `Redirect` |
| Layout nhận con | `props.children` | **`<Outlet />`** | 2 layout (`layouts/home`, `layouts/event-detail`) | đã xác minh — `Outlet`, `useOutletContext` export từ `'umi'` |
| `wrappers` trong route | 25 lượt, 2 file wrapper | umi 4 vẫn có `wrappers`, nhưng component wrapper phải render `<Outlet />` thay cho `children` | 25 lượt khai + 2 file | **cần tra document** |
| `redirect:` trong route config | 4 chỗ | dự kiến giữ | 4 | **cần tra document** |

##### b. Data layer — dva vẫn còn, không phải viết lại

Đây là điểm đáng mừng nhất: umi 4 giữ dva dưới dạng plugin, API export nguyên từ `'umi'`.

| API | Còn dùng được | Nguồn |
|---|---|---|
| `useDispatch` (26 lượt trong app) | có | đã xác minh — 36 lượt trong `KYC-PIT` |
| `connect` (7 lượt) | có | đã xác minh — 30 lượt |
| `useSelector` (24 lượt) | có | đã xác minh |
| Type `Reducer`, `Effect`, `Dispatch` | có, export từ `'umi'` | đã xác minh |
| `getDvaApp` (1 lượt) | có | đã xác minh |
| `useParams` (9), `useLocation` (13) | có, react-router v6 re-export | đã xác minh |
| `Helmet` (2 lượt) | có | đã xác minh |
| **`isBrowser` (7 lượt)** | **không rõ** — không repo umi 4 nào trong nhà dùng | **cần tra document**; nếu bỏ thì thay bằng `typeof window !== 'undefined'` |

Cách khai đổi từ preset sang plugin tường minh:

```ts
// umi 3 — dva đến gián tiếp qua @umijs/preset-react
{ dva: { hmr: true } }

// umi 4 — khai plugin tường minh
{
  plugins: ['@umijs/plugins/dist/dva'],
  dva: {},
}
```

##### c. Request layer

```ts
// umi 3 — src/app.tsx
export const request: RequestConfig = {
  errorHandler, requestInterceptors: [...], responseInterceptors: [...],
};

// umi 4 — khai plugin, config chuyển vào app.tsx theo shape mới
{ plugins: ['@umijs/plugins/dist/request'], request: {} }
```

Đây là nơi đặt `Origin` header (Mục 4.7) và interceptor 401, nên phải chuyển cẩn thận. **Cần tra document** về shape chính xác của `requestInterceptors` trong umi 4.

##### d. Build & config

| Hạng mục | umi 3 | umi 4 | Nguồn |
|---|---|---|---|
| `postinstall` | `umi generate tmp` | `umi setup` | đã xác minh |
| Bundler | webpack 4 | webpack 5 — hết lỗi `ERR_OSSL_EVP_UNSUPPORTED`, bỏ được cờ `--openssl-legacy-provider` | suy ra từ rào chắn số 3, Mục 3.6 |
| Code splitting | không bật | `codeSplitting: { jsStrategy: 'granularChunks' }` | đã xác minh — `bank-mall/config/config.ts` |
| `nodeModulesTransform` | `{ type: 'none' }` | `legacy: { nodeModulesTransform: false }` | đã xác minh |
| `npmClient` | không có | `npmClient: 'yarn'` | đã xác minh |
| Sass | `@umijs/plugin-sass` + khai `implementation` | hỗ trợ sẵn, bỏ được plugin | **cần tra document** |
| SSR | `ssr: { mode: 'string' }` | **chưa rõ** — cửa quyết định tại Mục 4.0.3 | **cần tra document** |

##### e. Tổng khối lượng theo nhóm

| Nhóm | Việc | Ước lượng |
|---|---|---|
| Routing | 2 `Redirect`, 2 layout đổi sang `Outlet`, 25 lượt `wrappers`, 4 `redirect:` | vừa |
| Data layer | Đổi cách khai plugin; API giữ nguyên | nhỏ |
| Request layer | Chuyển 1 khối config + 2 interceptor | nhỏ |
| `isBrowser` | 7 chỗ, tuỳ kết quả tra document | nhỏ |
| Build config | Đổi 5 khoá config, bỏ 1 plugin | nhỏ |
| **antd 4 → 5** | 24 file, 17 component | **lớn** — xem mục g |
| **moment → dayjs** | 15 file | vừa — xem mục f |
| **React 16 → 18** | toàn app | cần đo riêng sau khi lên umi 4 |

---

#### 4.0.7 moment → dayjs

`antd` 5 dùng `dayjs`, không dùng `moment`. 15 file trong app đang dùng `moment`.

**API đang dùng và mức hỗ trợ của dayjs:**

| API | Lượt | dayjs |
|---|---:|---|
| `.format()` | 25 | core |
| `.startOf()` / `.endOf()` | 12 / 9 | core |
| `.subtract()` / `.add()` / `.diff()` | 7 / 5 / 6 | core |
| `.isAfter()` / `.isBefore()` / `.isValid()` / `.valueOf()` | 2 / 1 / 2 / 2 | core |
| **`.fromNow()`** | 1 — `utils/formatter.ts:309` | **cần plugin `relativeTime`** |
| **`.duration()`** | 2 | **cần plugin `duration`** |

**Locale tiếng Việt:** dayjs có `dayjs/locale/vi`. App đang import `moment/locale/vi` tại `utils/formatter.ts:5` và trong file sinh tự động của locale plugin.

Locale này phục vụ `.fromNow()` — chuỗi kiểu "2 giờ trước" hiển thị cho end user, nên PHẢI kiểm bằng mắt sau khi đổi: hai thư viện diễn đạt relative time không giống nhau hoàn toàn.

**Điểm nối trực tiếp:** `components/app/rc-range-picker/index.tsx` truyền giá trị `moment` vào `DatePicker` của antd. Khi antd lên 5, component này chỉ nhận `dayjs` — đây là chỗ hai việc gặp nhau, phải đổi cùng lúc.

**Plugin `moment2dayjs`:** `@umijs/plugins` được cho là có plugin alias `moment` sang `dayjs` ở tầng build. **Cần tra document** ba điều: có tự đăng ký `relativeTime` và `duration` không; có tự nạp locale `vi` không; có xử lý được `moment.duration()` không. Nếu không, khai tay trong một file khởi tạo — vẫn nhẹ.

---

#### 4.0.8 Cấu hình Tailwind

```js
// tailwind.config.js
module.exports = {
  content: ['./src/pages/**/*.tsx', './src/components/**/*.tsx', './src/layouts/**/*.tsx'],
  theme: {
    extend: {
      colors: {
        primary:   'var(--adv-primary)',
        secondary: 'var(--adv-secondary)',
        // …18 token, KHÔNG hardcode hex
      },
      borderRadius: {
        DEFAULT: 'var(--adv-radius-base)',
        lg:      'var(--adv-radius-lg)',
      },
      fontFamily: {
        sans: ['var(--font-body)', 'Inter', 'sans-serif'],
      },
    },
  },
};
```

```css
/* tailwind.css — import một lần ở entry */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Khai plugin trong config của umi:

```ts
{ plugins: ['@umijs/plugins/dist/tailwindcss'], tailwindcss: {} }
```

**Bốn ràng buộc:**

1. **Màu trỏ vào CSS variable, không hardcode hex.** Dự án tham chiếu `bank-mall` đang hardcode `'#CC3366'`; làm vậy ở đây thì Tailwind thành nguồn thứ hai của đúng vấn đề 408 hex, và ADV đổi màu thì class Tailwind không đổi theo.
2. **Không cần `prefix`.** Bootstrap bị gỡ hoàn toàn nên không còn nguy cơ trùng tên class. Nếu vì lý do nào đó Bootstrap còn tồn tại song song trong giai đoạn chuyển tiếp thì PHẢI đặt `prefix: 'tw-'`, vì hai bên trùng tên class nhưng khác giá trị.
3. **`preflight` bật bình thường** sau khi Bootstrap đã gỡ. Trong giai đoạn còn song song thì phải tắt (`corePlugins: { preflight: false }`), vì nó reset base style mà Bootstrap dựa vào.
4. **`content` phải phủ đủ** `pages`, `components`, `layouts`. Thiếu thư mục nào thì class trong đó bị loại khỏi bundle — hỏng im lặng, không có cảnh báo.

---

#### 4.0.9 Thứ tự

Nâng phiên bản chạm toàn ứng dụng, nên PHẢI thực hiện **ngay đầu đợt 1**, trước khi bóc lớp thương hiệu. Làm ngược lại thì phần lớn công việc bóc thương hiệu phải rà lại lần thứ hai sau khi nâng.

Trình tự trong đợt 1:

```
1. Tra document umi 4, chốt 6 câu hỏi còn treo         ← xem bảng dưới
2. Kiểm chứng SSR trên umi 4                            ← cửa quyết định
3. Dựng bộ ảnh đối chiếu (Playwright) cho các màn chính
4. Nâng umi 3 → 4 + React 16 → 18 + routing v6         (Mục 4.0.6 a–d)
5. antd 4 → 5, moment → dayjs                           (Mục 4.0.7)
6. Gỡ Bootstrap, chuyển sang Tailwind                   (Mục 4.0.5, 4.0.8)
7. Bật code splitting
8. Chốt baseline cho type gate trên nền mới
```

Bước 2 là cửa quyết định: kết quả của nó chọn giữa việc đi tiếp hay chuyển sang phương án dự phòng tại Mục 4.0.3.

Bước 3 đặt trước mọi thay đổi giao diện: từ bước 4 trở đi có 92 file đổi hình dạng, không có baseline thì không đo được cái gì vỡ.

##### Sáu câu hỏi cần tra document umi 4

| # | Câu hỏi | Chặn bước nào |
|---|---|---|
| 1 | SSR có trả về HTML string đầy đủ không? | 2 — cửa quyết định |
| 2 | `getInitialPropsCtx` có còn truyền request object không? | 2 |
| 3 | `wrappers` trong route config còn không, và wrapper render `<Outlet />` hay `children`? | 4 |
| 4 | `isBrowser` còn export từ `'umi'` không? (7 chỗ dùng) | 4 |
| 5 | Shape của `requestInterceptors` trong plugin `request` | 4 |
| 6 | `moment2dayjs` có tự đăng ký `relativeTime`, `duration`, locale `vi` không? | 5 |

Sáu câu này gộp một lượt tra, không rải ra — vì bốn câu đầu quyết định cách viết của cả đợt.

---

### 4.1 Phân giải ADV theo tên miền — CA-001

**Tầng máy chủ.** Đơn vị mới `creator-app/serverConfig.js`:

| Hàm | Chữ ký | Trách nhiệm |
|---|---|---|
| `chuanHoaHost` | `(raw: string) => string` | Bỏ cổng, hạ chữ thường. PHẢI khớp từng ký tự với khoá lưu đệm phía dịch vụ |
| `layCauHinh` | `(host: string) => Promise<Config \| null>` | Gọi `GET /partners/app-config?domain=`, lưu đệm trong tiến trình 60 giây |

Lưu đệm 60 giây là để giảm số lần gọi trên mỗi yêu cầu, KHÔNG phải lớp lưu đệm thứ hai — tầng dịch vụ đã lưu đệm 4 giờ theo tên miền và tự xoá khi có thay đổi.

**Tầng ứng dụng.** Đơn vị mới `src/utils/adv.ts`:

| Hàm | Hành vi |
|---|---|
| `soLuongADV(cauHinh)` | Số ADV mà tên miền phân giải ra |
| `chonADV(cauHinh, slug?)` | Có `slug`: trả đúng ADV đó, không có thì trả `null`. Không có `slug`: chỉ trả khi tập có đúng một phần tử |

`chonADV` KHÔNG ĐƯỢC trả phần tử đầu tiên khi tập có nhiều phần tử. Đoán sai ở đây dẫn tới ghi dữ liệu vào nhầm ADV — thứ ảnh hưởng thẳng tới điều kiện xét thưởng.

**Ba nhánh tại trang gốc** (`src/pages/main-home/index.tsx`):

| Số ADV | Hành vi |
|---|---|
| 0 | Trang báo tên miền chưa đăng ký. **KHÔNG chuyển hướng** (C5) |
| 1 | Chuyển hướng tới `/<slug>` — chế độ nhận diện riêng |
| nhiều | Kết xuất trang tổng kèm bộ chuyển ADV |

Nhánh đầu là bắt buộc: hệ hiện tại rơi vào vòng lặp chuyển hướng không thông báo khi khai sai danh sách tên miền, và người thực hiện không có gì để đọc để lần ra nguyên nhân.

### 4.2 Nhận diện điều khiển bằng cấu hình — CA-002

Đơn vị mới `creator-app/themeCss.js`, hàm `dungTheStyle(cauHinh) → string`, sinh khối `<style id="adv-theme">` gồm:

| Nhóm | Nguồn | Quy tắc kiểm |
|---|---|---|
| Biến màu | `theme.colors` | Chỉ nhận mã màu 3 hoặc 6 ký tự thập lục phân. Giá trị khác bị bỏ qua |
| Biến bo góc | `theme.radius` | Số hữu hạn, không âm. Giá trị `0` là **hợp lệ** — góc vuông, không phải "chưa khai" |
| Họ phông chữ | `theme.fontFamily` | Chuỗi, loại bỏ dấu nháy kép |
| Khối `@font-face` | `theme.fontFiles` | Chỉ nhận giao thức HTTPS; luôn kèm `font-display: swap` (C8) |

Chuỗi lấy từ cấu hình đi thẳng vào thuộc tính định kiểu của thẻ gốc chính là con đường tiêm mã CSS tuỳ ý — đó là lý do mọi giá trị đều qua bộ kiểm trước khi ghép.

Khối được chèn tại `server.js` bằng cơ chế đã mô tả ở Mục 3.1.

**Nối vào tầng định kiểu — ba điểm.**

**(1) Phông chữ và bảng màu qua biến CSS.**

```scss
// src/global.scss
body { font-family: var(--font-body, 'Inter', sans-serif); }
```

**(2) Tailwind đọc thẳng biến CSS.** Bảng màu trong `tailwind.config.js` trỏ vào `var(--adv-*)` (Mục 4.0.5), nên mọi lớp tiện ích màu tự đổi theo ADV mà không cần ghi đè gì thêm. Trạng thái di chuột và nhấn dùng **độ mờ của cùng một biến**, không dùng màu dẫn xuất — nhờ vậy không có phép tính màu nào phải nhân đôi giữa tầng dịch vụ và tầng giao diện.

**(3) `antd` nhận mã màu thật qua `ConfigProvider`.** Thư viện này tự suy ra dải mười sắc độ từ `colorPrimary` bằng thuật toán, nên biến CSS không dùng được ở đây. Cấu hình của ADV đã có sẵn ở tầng máy chủ theo từng yêu cầu (Mục 4.1), nên truyền thẳng mã màu thật vào.

Ràng buộc: cả ba điểm PHẢI đọc **cùng một bản ghi cấu hình** của ADV. Lệch nguồn thì màu đúng ở phần này và sai ở phần kia, và không có cơ chế tự động nào phát hiện.

Cách này đáp ứng ràng buộc của CA-002 — *"đổi màu thương hiệu thì nút cũng đổi theo"* — mà không cần bước ghi đè nào: nút của `antd` nhận màu từ token, nút viết bằng Tailwind nhận màu từ biến CSS.

### 4.3 Tài nguyên và phông chữ — CA-003

**Phía giao diện.** `src/configs/image.ts` hiện dựng nguồn ảnh bằng `require('../assets/images/new/logo.png')` — giá trị nướng vào gói dựng. Chuyển sang đọc địa chỉ từ cấu hình. Toàn ứng dụng có **208 điểm nhập tài nguyên lúc dựng**; `ImageConst` được dùng ở 9 tệp.

Bộ ảnh bắt buộc tối thiểu: `logoImage`, `logoMobileImage`, `logoBrandFooter`, `decorLeft`, `decorRight`, `favicon`, `ogImage`. Ảnh tuỳ chọn thiếu thì dùng ảnh mặc định của hệ thống và KHÔNG ĐƯỢC làm vỡ bố cục.

**Phía dịch vụ.** Trạng thái hiện tại:

| | |
|---|---|
| Tuyến đang mở | `POST /photo`, `POST /admin/photo` (`backend/pkg/file/router/file.go`) |
| Định dạng chấp nhận | `jpeg`, `jpg`, `png` (`backend/internal/constants/constants.go:31`) |
| Xử lý sau khi nhận | Đổi kích thước ảnh, gắn kiểu nội dung `image/<ext>` |
| Hàm xử lý tệp tổng quát | `UploadFile`, `UploadFileData` — **đã có trong mã, chưa gắn tuyến nào** |

Bổ sung tuyến `POST /admin/file`: nhận `ttf`, `otf`, `woff2`; giới hạn kích thước không dưới 5 MB; **KHÔNG đổi kích thước**; chuyển sang `woff2` khi nhận; kiểu nội dung `font/woff2`.

Địa chỉ trả về theo `generateURLFileByName` (`backend/pkg/file/service/file.go:357`). Kho lưu PHẢI là kho công khai, KHÔNG ĐƯỢC dùng địa chỉ ký sẵn có hạn — địa chỉ hết hạn làm phông chữ ngừng hoạt động sau vài giờ mà không phát sinh lỗi nào.

**Kiểm địa chỉ tại tầng dịch vụ.** Hiện `backend/internal/service/partner_app_config_theme.go:110-118` chỉ kiểm tên họ phông và địa chỉ khác rỗng. Bổ sung: chỉ nhận HTTPS; chặn `javascript:`, `data:` và địa chỉ tương đối giao thức dạng `//host`.

**Hai nguồn phông chữ.** Số đo trên 5 ADV đang hoạt động: ba ADV dùng phông vốn có sẵn trên dịch vụ phông công cộng (`Be Vietnam Pro` ×2, `Roboto`), hai ADV dùng phông thương hiệu riêng (`SVN-Gilroy`, `FE Font`). Do đó cấu hình phông có **hai nguồn**:

```
theme.font = {
  source:  'google' | 'upload',
  family:  '<tên họ phông>',
  weights: [ ... ],        // khi source = google
  files:   [ { weight, style, url } ]   // khi source = upload
}
```

Nguồn `google` sinh thẻ liên kết theo ADV; nguồn `upload` sinh khối `@font-face`. Thẻ phông công cộng gán cứng trong `src/pages/document.ejs` PHẢI được gỡ — để nguyên thì ADV chọn phông nào cũng vẫn tải thêm một bộ không dùng tới.

### 4.4 Nội dung theo ADV — CA-004

Năm giá trị theo ADV PHẢI rời khỏi khối `define:` của `config/config.prod.ts`:

| Biến hiện tại | Đích |
|---|---|
| `COMMON_PARTNER` | Gỡ bỏ; thay bằng phân giải theo `Host` (Mục 4.1) |
| `QA_ARTICLE_ID` | `content.articleIds.qa` |
| `TERM_ID` | `content.articleIds.term` |
| `CONDITION_ID` | `content.articleIds.condition` |
| `NEXT_PUBLIC_ORIGIN` | Dựng từ `Host` của yêu cầu |

Giữ nguyên trong khối `define:` vì dùng chung mọi ADV: `API_ENDPOINT`, `API_ENDPOINT_UPLOAD`, `ORIGIN`, nhóm `FB_*`, `CLIENT_ID`, `TIKTOK_CLIENT_ID`, nhóm `SSO_*`.

Hotline, thư điện tử, các liên kết mạng xã hội và liên kết website đối tác đọc từ cấu hình.

**Thể lệ và Hướng dẫn giữ nguyên theo từng chiến dịch.** Hai bài này gắn với bản ghi chiến dịch (`backend/internal/model/mg/event.go:31-32`), và biểu mẫu chiến dịch trong phân hệ quản trị đã có sẵn ô chọn. Một ADV có thể chạy nhiều chiến dịch với thể lệ khác nhau; kéo hai bài này lên mức ADV là làm hỏng mô hình đó. Yêu cầu này KHÔNG ĐƯỢC phát sinh thay đổi tại biểu mẫu chiến dịch.

### 4.5 Thẻ mô tả và mã đo lường — CA-005

| Hạng mục | Vị trí hiện tại | Thay đổi |
|---|---|---|
| Địa chỉ chuẩn hoá, địa chỉ chia sẻ | `src/wrappers/home.tsx:9`, `layouts/event-detail/index.tsx:171,173`, `pages/partner-home/index.tsx:224,226` | Sinh từ `Host` của yêu cầu |
| Tiêu đề, mô tả, từ khoá, ảnh chia sẻ | mã nguồn | Đọc từ cấu hình |
| Mã đo lường | `config/config.prod.ts:56-62` — gán cứng trong `headScripts` | Sinh theo cấu hình. Không khai thì KHÔNG chèn mã nào |

**KHÔNG ĐƯỢC sửa địa chỉ chuẩn hoá bằng cách đổi giá trị `ORIGIN`.** Biến này gánh hai vai: vừa là tên miền gọi lại đã đăng ký cho luồng uỷ quyền TikTok, vừa bị dùng nhầm cho địa chỉ chuẩn hoá. Đổi giá trị sẽ làm gãy luồng đăng nhập. Cách đúng là tách hai vai: địa chỉ chuẩn hoá sinh từ `Host`, `ORIGIN` giữ nguyên và chỉ còn phục vụ việc gọi lại.

### 4.6 Bật tắt tính năng — CA-006

Hai tính năng lệch giữa các ADV: Hợp đồng điện tử và Quản lý hoa hồng affiliate.

Bộ bao tuyến đọc cờ từ cấu hình ADV. Tắt một tính năng PHẢI làm mục biến khỏi thanh điều hướng **và** chặn tại tuyến — gõ thẳng địa chỉ cũng không vào được. Ẩn mục khỏi thanh điều hướng là trải nghiệm người dùng, không phải cổng kiểm soát.

Tải cấu hình thất bại thì dùng bộ cờ mặc định an toàn, KHÔNG ĐƯỢC trả trang trắng (NFR-003).

### 4.7 Sửa bốn vi phạm phạm vi tiến trình

| # | Vị trí | Thay đổi |
|---|---|---|
| 1 | `src/utils/helper.ts:691-699` | Nhánh máy chủ đọc `Host` từ yêu cầu. Không có thì trả chuỗi rỗng — để lỗi lộ ra, KHÔNG ĐƯỢC im lặng dùng tên miền của ADV khác |
| 2 | `src/app.tsx:94-104` | Bổ sung tiêu đề `Origin` tại bộ chặn yêu cầu, thay cho việc truyền tay ở từng trang. Ba điểm gọi ở phạm vi mô-đun (Mục 3.4) chuyển vào trong thành phần |
| 3 | `…/accesstrade-section/index.tsx:14-26` | `SSO_PARAMS` chuyển thành hàm gọi mỗi lần bấm; tham số `state` sinh từ nguồn ngẫu nhiên mật mã, lưu lại và đối chiếu khi quay về, dùng một lần rồi xoá |
| 4 | `pages/login-tiktok/index.tsx:14`, `pages/connect-tiktok/index.tsx:12` | Kiểm đích chuyển tiếp theo danh sách tên miền cho phép của ADV. Giá trị ngoài danh sách bị bỏ qua và luồng đi tiếp nhánh bình thường — giá trị hợp lệ không đổi hành vi |
| 5 | `server.js:25-26` | Gỡ hai biến toàn cục theo yêu cầu và lệnh ghi nhật ký in nguyên đối tượng yêu cầu (bao gồm cả khối tiêu đề) |
| 6 | `src/app.tsx:112-118` | Chỉ điều phối trạng thái khi chạy trong trình duyệt (C3) |

### 4.8 Môi trường dựng thử — CA-008

Yêu cầu mô tả *"môi trường tách khỏi hệ thống đang chạy"*. Kho mã đã có sẵn hai môi trường (`Dockerfile.develop` / `Dockerfile.release`, ảnh gắn hậu tố `-develop` / `-release`). Phương án: **dùng môi trường `develop` làm môi trường dựng thử**, không dựng hạ tầng mới.

| Điều kiện nghiệm thu CA-008 | Đạt bằng |
|---|---|
| Các bước giống hệt môi trường thật | Cùng mã nguồn, cùng màn quản trị — sẵn có |
| Không tạo thay đổi nào trên môi trường thật | Cơ sở dữ liệu riêng — **PHẢI xác minh trước** |
| Người phụ trách kinh doanh tự dựng bản demo | Cấp vai trò `config_editor` trên phân hệ quản trị của `develop` — có sau khi đưa 37 tệp sang (Mục 1.4) |
| Đóng quyền sau khi xong | Gỡ vai trò đó — sẵn có |
| Khách mở liên kết xem không cần tài khoản | Quy ước tên miền `<slug>.sandbox.<tên miền>`; trang chủ ADV vốn công khai |
| Nhận diện chuyển sang hồ sơ thật | Hai tuyến mới, xem dưới |

**Hai tuyến chuyển cấu hình:**

```
GET  /partners/:id/app-config/export  →  JSON theo lược đồ PartnerAppConfigBody
POST /partners/:id/app-config/import  ←  JSON đó
```

Hàm thuần `LocDuLieuRiengCuaMoiTruong` lọc bỏ những trường là định danh của bản ghi ở môi trường nguồn:

| Mang sang | Không mang sang |
|---|---|
| `theme` (màu, bo góc, dải màu, phông chữ) | `content.articleIds` — mã bài viết ở môi trường kia |
| `seo`, `modules`, `assets` | `allowDomains` — tên miền dựng thử |
| `content.contact`, `content.social`, `content.footerBrandLink` | `slug`, `partner`, `version` |

Sau khi nhập, màn hình PHẢI nêu rõ những trường còn thiếu, KHÔNG ĐƯỢC im lặng để trống.

**Hai hạng mục hạ tầng, không thuộc mã nguồn:** bản ghi tên miền ký tự đại diện `*.sandbox.<tên miền>` trỏ về máy chủ `develop`, và chứng chỉ bảo mật tương ứng.

### 4.9 Không kế thừa dữ liệu của ADV khác — CA-009

ADV mới khởi tạo với **mọi trường bắt buộc rỗng**. Thiếu trường bắt buộc thì không lưu được, và thông báo PHẢI liệt kê **đủ** các chỗ còn thiếu, không dừng ở lỗi đầu tiên.

**Ranh giới giữa CA-002 và CA-009 — cần chốt.** CA-002 yêu cầu *"ADV không điền gì vẫn ra giao diện đúng"*; CA-009 yêu cầu *"không giá trị mặc định ẩn nào thay thế khi bỏ trống"*. Đọc nguyên văn thì hai câu triệt tiêu nhau. Thiết kế này áp dụng ranh giới sau, và ranh giới đó **cần chủ sở hữu tài liệu yêu cầu xác nhận**:

| Nhóm | Có giá trị mặc định? | Lý do |
|---|---|---|
| Token giao diện — màu, bo góc, phông chữ | **Có**, hợp nhất tại tầng dịch vụ | Bắt khai đủ thì mỗi ADV giữ một bản sao của cùng một giá trị; sửa mặc định về sau không ADV nào nhận được |
| Dữ liệu nhận dạng — hotline, thư điện tử, mạng xã hội, mã bài viết | **Không** | Nguyên nhân gốc của lỗi hiện có trên môi trường thật là các giá trị này được **thừa hưởng** thay vì được **hỏi** |

### 4.10 Không thực hiện

| Hạng mục | Căn cứ |
|---|---|
| Luồng bản nháp, xem trước, xuất bản, khôi phục | Tài liệu yêu cầu, Mục 3.2. Nút lưu trong phân hệ quản trị ghi thẳng và có hiệu lực ngay |
| Trình lắp và sắp xếp khối trang chủ | Tài liệu yêu cầu, Mục 3.2 |
| Đối chiếu chéo dữ liệu ADV khác lúc lưu | Tài liệu yêu cầu, Mục 3.2 |
| Danh sách kiểm tiến độ đưa ADV lên sóng | Tài liệu yêu cầu, Mục 3.2 |
| Chuyển ADV đang chạy sang `creator-app` | Tài liệu yêu cầu, Mục 3.2 |
| Đổi nền tảng sang Next.js | Tài liệu bối cảnh, Mục 3.3 — bước 4 của lộ trình, chưa cam kết |

**Ghi nhận rủi ro đã chấp nhận.** Tài liệu yêu cầu mô tả người vận hành *"sai thì phải khôi phục được"* (Mục 2), nhưng lại loại luồng khôi phục khỏi phạm vi (Mục 3.2). Với thiết kế này, người vận hành sửa sai thì website ADV sai ngay và không có đường lùi. Tầng dịch vụ đã sẵn có lịch sử phiên bản và tuyến khôi phục; bật lên là việc của phân hệ quản trị, chi phí không đáng kể. Ghi lại để chủ sở hữu quyết định, tài liệu này KHÔNG tự mở rộng phạm vi.

---

## 5. Ánh xạ yêu cầu — thành phần

| Yêu cầu | Thành phần chính | Mục |
|---|---|---|
| CA-001 | `serverConfig.js`, `src/utils/adv.ts`, `src/pages/main-home/index.tsx` | 4.1 |
| CA-002 | `themeCss.js`, `src/global.scss`, `src/bootstrap-custom.scss` | 4.2 |
| CA-003 | `src/configs/image.ts`, `backend/pkg/file/`, `admin/…/theme-form.tsx` | 4.3 |
| CA-004 | `src/configs/app.ts`, `config/config.prod.ts` | 4.4 |
| CA-005 | `src/wrappers/home.tsx`, `config/config.prod.ts`, `src/pages/document.ejs` | 4.5 |
| CA-006 | `config/routes.ts`, `src/wrappers/` | 4.6 |
| CA-007 | Bố cục dùng chung; nội dung đọc từ cấu hình | 4.2, 4.4 |
| CA-008 | Môi trường `develop`; hai tuyến xuất/nhập cấu hình | 4.8 |
| CA-009 | Luật kiểm trường bắt buộc tại tầng dịch vụ | 4.9 |
| CA-010 | `admin/src/pages/partner-app-config/` | 4.3, 4.4 |
| CA-011 | như trên | — |
| CA-012 | Vai trò `config_editor` — mã đã viết nhưng **chưa có trên `release`**, phải đưa sang | 1.4 |
| NFR-007 | Kiểm tra tự động chặn giá trị thương hiệu trong mã nguồn | 6.3 |
| NFR-008 | Định danh ADV và tên miền trong mọi bản ghi nhật ký | C6 |

---

## 6. Kế hoạch triển khai

### 6.1 Thứ tự

| Đợt | Nội dung | Phụ thuộc |
|---|---|---|
| **0** | **Đưa 37 tệp tầng cấu hình từ `feat/partner-app` sang nhánh cắt từ `release`** (Mục 1.4) | — |
| 1 | Khởi tạo `creator-app/`; **kiểm chứng kết xuất phía máy chủ trên `umi` 4 (cửa quyết định)**; nâng nền tảng (Mục 4.0) | Đợt 0 |
| 1b | **Chuyển tầng định kiểu sang `antd` + Tailwind, gỡ Bootstrap** (Mục 4.0.5) — dựng bộ ảnh đối chiếu trước | Đợt 1 |
| 2 | **Sửa bốn vi phạm phạm vi tiến trình** (Mục 4.7) | Đợt 1 |
| 3 | Phân giải theo tên miền, nhận diện điều khiển bằng cấu hình | Đợt 1 |
| 4 | Tài nguyên, nội dung, thẻ mô tả, cờ tính năng | Đợt 3 |
| 5 | Bóc sạch thương hiệu và cổng gác tự động | Đợt 3, 4 |
| 6 | Phân hệ quản trị: tải tệp, xuất/nhập cấu hình | Song song từ đợt 3 |
| 7 | Môi trường dựng thử và nghiệm thu | Toàn bộ |

Đợt 2 xếp sớm có chủ đích: bốn vi phạm ở Mục 4.7 chỉ biểu hiện khi một tiến trình phục vụ nhiều tên miền, và chi phí sửa tăng mạnh sau khi đã có ADV thứ hai chạy chung.

### 6.2 Trạng thái tại thời điểm ban hành

Đợt 1 đã thực hiện thử trên một bản sao và **xác minh chạy được**: bản dựng thành công sau 48 giây, máy chủ trả mã 200 kèm HTML kết xuất sẵn. Bốn rào chắn tại Mục 3.6 đều đã có cách xử lý đo được.

### 6.3 Hai cổng gác tự động

**Cổng gác kiểu.** Số đo trên nền `umi` 3 là 230 lỗi (Mục 3.6). Con số này **chỉ dùng để tham chiếu**, không dùng làm mốc chuẩn: nâng React và `antd` sẽ thay đổi nó theo cả hai chiều. Mốc chuẩn PHẢI chốt lại **sau** khi hoàn tất Mục 4.0.

Cơ chế: ghi nhận mốc chuẩn và để việc dựng thất bại khi số lỗi **tăng**, thay vì chờ dọn sạch mới bật cổng gác. Việc dọn lỗi tồn đọng tách thành hạng mục riêng.

**Cổng gác thương hiệu (NFR-007).** Chặn trong `creator-app/src/**`: mã màu thập lục phân ngoài tệp token, số điện thoại, địa chỉ thư điện tử, tên ADV, và địa chỉ bên ngoài nằm ngoài mô-đun cấu hình. Vi phạm làm việc dựng thất bại.

Không có cổng gác này thì theo thời gian sẽ có người gán cứng lại một màu, một liên kết, một cái tên — và `creator-app` trượt dần về đúng chỗ 14 bản rẽ nhánh đang đứng.

---

## 7. Chiến lược kiểm thử

### 7.1 Kiểm thử đơn vị

| Đơn vị | Trường hợp bắt buộc |
|---|---|
| `chuanHoaHost` | Bỏ cổng; hạ chữ thường; đầu vào rỗng trả chuỗi rỗng |
| `chonADV` | Một ADV trả chính nó; nhiều ADV không có `slug` trả `null`; `slug` không tồn tại trả `null`, KHÔNG rơi về phần tử đầu |
| `dungTheStyle` | Giá trị không phải mã màu bị loại; địa chỉ phông không phải HTTPS bị loại; khối sinh ra luôn có `font-display: swap` |
| `dungOrigin` | Ưu tiên `Host` của yêu cầu; thiếu `Host` trả chuỗi rỗng |
| `sinhState` / `kiemState` | Mỗi lần gọi ra giá trị khác; dùng một lần rồi hết hiệu lực; giá trị lạ bị từ chối |
| `dichHopLe` | Tên miền trong danh sách được chấp nhận; tên miền lạ, dạng `//host` và các giao thức khác bị chặn |
| `LocDuLieuRiengCuaMoiTruong` | Giữ token giao diện và thông tin liên hệ; loại mã bài viết và danh sách tên miền |

### 7.2 Kiểm thử tích hợp

| # | Trường hợp | Kỳ vọng |
|---|---|---|
| 1 | Hai tên miền trên **cùng một tiến trình** | Hai bộ nhận diện khác nhau |
| 2 | Tên miền chưa đăng ký | Trang báo lỗi; **không** có phản hồi chuyển hướng |
| 3 | Đổi màu thương hiệu, lưu, tải lại | Chữ, viền, nền **và nút** đều đổi |
| 4 | Đổi logo và phông chữ | Website đổi, không cần dựng lại |
| 5 | Tắt Hợp đồng điện tử | Mục mất khỏi thanh điều hướng **và** gõ thẳng địa chỉ bị chặn |
| 6 | Hai tên miền, so thẻ mô tả | Hai bộ khác nhau; địa chỉ chuẩn hoá trỏ đúng tên miền đang truy cập |
| 7 | Không khai mã đo lường | Không có mã đo lường nào được chèn |
| 8 | Tải trang với mạng bị làm chậm | Không nhấp nháy màu mặc định; không có lúc nào chữ tàng hình |
| 9 | Xuất cấu hình từ môi trường dựng thử, nhập vào môi trường thật | Token giao diện và thông tin liên hệ giữ nguyên; mã bài viết và tên miền để trống kèm nhắc phải điền |

### 7.3 Kiểm thử thủ công bắt buộc

| # | Trường hợp | Vì sao không tự động hoá được |
|---|---|---|
| 1 | Người vận hành tạo xong một ADV từ đầu đến cuối, không cần hỗ trợ | CA-011 quy định nghiệm thu bằng một buổi thao tác thật |
| 2 | Người phụ trách kinh doanh dựng một bản demo từ đầu đến cuối | CA-008 |
| 3 | Đối chiếu giao diện trên máy tính và điện thoại với **ít nhất hai bộ nhận diện tương phản** | NFR-004 |
| 4 | Quan sát kho trạng thái khi chạy hai tên miền trên cùng tiến trình | Mục 3.3 — chưa xác minh trên trình duyệt |
| 5 | **Đối chiếu ảnh từng màn trước và sau khi chuyển đổi tầng định kiểu** | 92 tệp đổi hình dạng; lỗi bố cục không phát sinh lỗi khi dựng |

**Bộ ảnh đối chiếu là hạ tầng bắt buộc, không phải việc tuỳ chọn.** Kho mã hiện không có bộ ảnh chuẩn nào. Phải dựng trước khi bắt đầu Mục 4.0.5, chụp từng màn với **ít nhất hai bộ nhận diện tương phản** theo NFR-004.

---

## 8. Rủi ro

| # | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| R1 | Kho trạng thái rò giữa các ADV (Mục 3.3) | Cao | C3; xác minh thủ công trước khi có ADV thứ hai |
| R2 | Tiêu đề `Origin` sai làm ADV nhận sai dữ liệu, **không phát sinh lỗi** | Cao | Đặt tại bộ chặn yêu cầu; kiểm thử tích hợp số 1 |
| R3 | Không có đường lùi khi người vận hành nhập sai (Mục 4.10) | Cao | Đã ghi nhận; chờ chủ sở hữu quyết |
| R4 | Bóc thương hiệu không triệt để → bản rẽ nhánh thứ 15 | Trung bình | Cổng gác thương hiệu tại 6.3; tiêu chí đo được |
| R5 | 230 lỗi kiểu tồn đọng che lỗi mới | Trung bình | Mốc chuẩn tại 6.3 |
| R6 | Môi trường `develop` dùng chung cơ sở dữ liệu với môi trường thật | Trung bình | Xác minh trước khi bắt đầu đợt 7 |
| R7 | Bộ nhận diện thương mại (`Averta`, `SVN-Gilroy`) có ràng buộc giấy phép | Thấp | Cần người có thẩm quyền xác nhận trước khi mang sang |
| R8 | **`umi` 4 không giữ cơ chế kết xuất phía máy chủ mà thiết kế đang dựa vào** (Mục 4.0.3) | **Cao** | Kiểm chứng là việc đầu tiên của đợt 1; ba phương án dự phòng đã xếp thứ tự |
| R9 | Nâng `antd` 4 → 5 làm vỡ giao diện ở 24 tệp | Trung bình | Đối chiếu từng màn với bản đang chạy; nằm trong kiểm thử thủ công số 3 |
| R10 | Nâng phiên bản làm số lỗi kiểu tăng vọt, mốc chuẩn 230 mất ý nghĩa | Trung bình | Chốt lại mốc chuẩn **sau** khi nâng, không phải trước (Mục 4.0.9, bước 4) |
| R11 | **Chín tệp kiểu dạng mô-đun mất lớp mà không phát sinh lỗi** khi đổi quy ước đặt tên (Mục 4.0.4a) | **Cao** | Đổi tên trước khi nâng; đối chiếu bằng mắt 9 thành phần liên quan — không có cơ chế tự động nào bắt được |
| R12 | **Chuyển 1.728 lượt lớp tiện ích làm lệch bố cục toàn ứng dụng** — cùng tên lớp, khác thang đo, việc dựng vẫn thành công | **Cao** | C12; bảng quy đổi; chuyển theo từng màn kèm ảnh đối chiếu |
| R13 | **92 tệp đổi hình dạng mà không có bộ ảnh chuẩn để so** | **Cao** | Dựng bộ ảnh đối chiếu **trước** khi bắt đầu (Mục 4.0.5) — điều kiện bắt buộc |
| R14 | Hai đường theming lệch nguồn: `antd` một bản ghi, biến CSS một bản ghi khác | Trung bình | Cả hai đọc cùng bản ghi cấu hình đã lấy ở tầng máy chủ (Mục 4.2) |
| R15 | 27 tệp biểu mẫu chuyển sang mô hình dữ liệu khác, 16 điểm kiểm hợp lệ phải viết lại | Trung bình | Tách hai loại: có kiểm hợp lệ và không; xử lý sau khi nhóm cơ học đã xong |
| R16 | **Tầng cấu hình chưa có trên `release`** — 37 tệp nằm trên nhánh đã quyết định không hợp nhất | **Cao** | Đợt 0 đưa sang trước mọi việc khác (Mục 1.4). Chậm bước này thì phần giao diện không có chỗ đọc cấu hình |

---

## 9. Câu hỏi cần chủ sở hữu tài liệu yêu cầu trả lời

1. **Ranh giới giá trị mặc định giữa CA-002 và CA-009** (Mục 4.9) — thiết kế đang áp dụng một ranh giới tự đề xuất.
2. **Trang chủ của ADV chưa có chiến dịch nào hiển thị gì?** CA-007 quy định khối lấy dữ liệu từ hệ thống giữ nguyên cách hoạt động hiện tại, nhưng đó là trạng thái của **mọi** ADV trong ngày đầu tiên.
3. **Tiêu chí hoàn thành của việc bóc lớp thương hiệu** — Phụ thuộc #1 yêu cầu xong trước khi thêm tính năng, nhưng không nêu cách đo.
4. **Luồng đăng nhập** — tài liệu yêu cầu không có hạng mục nào về việc này, trong khi bản nền mang theo hai khiếm khuyết đã mô tả tại Mục 3.5.
5. **Đường lùi khi nhập sai** (Mục 4.10, R3).
