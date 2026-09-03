# Product Requirements Document: Onboard đối tác bằng cấu hình trong admin (`partner-app/`)

**Date:** 2026-09-03
**Author:** Nguyễn Đăng Định
**Version:** 1.0
**Reviewer:** _chưa có_
**Project Level:** Level 4 — app mới + backend + admin
**Status:** Draft — phương án và phạm vi đã chốt, chờ review
**Mức độ:** **P2** — không có lỗi đang sống trên production, nhưng chi phí cộng dồn mỗi lần onboard và mỗi lần sửa bug
**Phạm vi:** app mới `partner-app/` + bổ sung `backend/` + bổ sung `admin/`. **15 folder đối tác hiện tại đóng băng, không đụng.**

---

## Document Overview

Hôm nay, onboard một đối tác mới nghĩa là **copy cả một frontend**. Repo đang có 15 bản như vậy. PRD này đặc tả app thứ 16 — bản cuối cùng phải viết bằng tay — sau đó mọi đối tác mới là **một bản ghi cấu hình trong admin**, không phải một thư mục code.

### Nguyên tắc

**Branding là DỮ LIỆU, không phải CODE.** Mọi thứ khác nhau giữa 15 bản hiện tại — màu, logo, ảnh, câu chữ, SEO, GTM, module bật/tắt, bố cục trang chủ — phải nằm trong một bản ghi cấu hình đọc lúc chạy, không nằm trong file `.scss` hay `.tsx`.

**Backend đã multi-tenant, không viết lại.** `PartnerRaw.AllowDomains` và `GetDetailByDomain` đã có và đang chạy. PRD này **thêm** một collection cấu hình, không sửa mô hình dữ liệu đối tác đang có.

**`creator-os` chỉ để tham khảo thiết kế — chốt 03/09.** Repo `pmax/creator-os` đã giải xong đúng bài toán này và có bản chạy thật. Lấy **thiết kế và bài học**, mục 2.3. **Không lấy code, không phụ thuộc package của họ.** Hai repo khác hệ (Go/Mongo ↔ NestJS/Prisma/Postgres), ràng buộc phụ thuộc chéo sẽ đẻ ra đúng cái bệnh đang chữa.

**Một deployment duy nhất — chốt 03/09.** Một image phục vụ mọi domain đối tác, phân giải theo `Host`. Sửa cấu hình trong admin là mọi site đổi theo, không build, không deploy. Đo được: 15 domain hiện tại **đã terminate ở hạ tầng mình** (`SSH_HOST_{env}` — một host mỗi môi trường; `Dockerfile.release` và `nginx/` giống hệt nhau giữa các folder).

**15 app cũ đóng băng — chốt 03/09.** Không di cư. PRD này **không** gỡ được cảnh clone bug fix cho 15 bản đó; nó chặn đống đó phình thêm. Đây là quyết định đã cân nhắc, không phải thiếu sót — xem mục 10.

**Đánh số bằng tiền tố `PC-`** (Partner Config) để không lẫn với `FR-0xx` / `FE-0xx` của các PRD khác trong repo.

**Related Documents:**
- Báo cáo khảo sát + số đo đầy đủ: `ambassador/plans/reports/research-260903-1718-partner-config-admin-tham-khao-creator-os.md` (repo code)
- Thiết kế tham khảo: `pmax/creator-os` — `docs/architecture/05-theme-and-portals.md`, `14-editions-and-deployment.md`
- PRD liên quan (cờ theo đối tác đã có): [../employee-code/prd-employee-code-2026-08-06.md](../employee-code/prd-employee-code-2026-08-06.md)

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **App white-label** | `hdbank/`, `parasola/`, `yody/`… — mỗi folder một frontend phục vụ đúng một đối tác. Hiện có 15 |
| **`partner-app/`** | App mới của PRD này. **Một** codebase, **một** deployment, phục vụ mọi đối tác mới |
| **Cấu hình app** (`PartnerAppConfig`) | Bản ghi chứa toàn bộ phần khác nhau giữa các đối tác: theme, asset, SEO, module, bố cục trang chủ |
| **Token** | Một giá trị trong cấu hình theme (màu, bo góc, đổ bóng, font, kiểu chữ nhãn) — đổ ra CSS custom property lúc SSR |
| **Preset** | Bộ token đặt tên sẵn làm lớp nền; đối tác vẫn ghi đè được từng field lên trên |
| **Section** | Một khối trên trang chủ. Trang chủ = **mảng có thứ tự** các section, không phải template cố định |
| **Catalogue section** | Danh sách loại section hợp lệ. **Nằm trong code**, không nằm trong DB — xem PC-005 |
| **Slot** | Một màn hình mà đối tác có thể thay hẳn bằng bản riêng, qua registry. Mức tuỳ biến L4 |
| **Đối tác mới** | Đối tác onboard sau khi `partner-app/` lên production. Chạy trên `partner-app/`, không có folder riêng |

---

## 1. Executive Summary

Mỗi đối tác mới đẻ ra một bản sao frontend. Hệ quả đo được:

```
Sửa 1 bug ở tầng dùng chung
  → phải sửa lại ở 14 chỗ nữa (11 commit/6 tháng chạm 12–14 folder)
  → hoặc quên, và 14 bản trôi khác nhau dần (158 commit/6 tháng chạm đúng 1 folder)

Onboard 1 đối tác mới
  → copy ~25.000 LOC, sửa màu + logo + câu chữ, dựng pipeline, dựng image, deploy
```

### Đây không phải rủi ro giả định — đã xảy ra

Chính commit message trong repo nói ra:

| Commit | Nội dung |
|---|---|
| `d25209fcc` | `docs(budget-alert): cảnh báo file có 14 bản sao, phải sửa đồng loạt` |
| `ae3a8a963` | `feat(web): them cot luot xem khong duoc tinh thuong va sua sorter o 14 ung dung` |
| `88f436183` | `feat(all-partners): sync leaderboard config to all 12 partner frontends` |
| `543216578` | `fix(all-partners): crash trang chi tiết event do partnerDetail chưa destructure` |

Và drift đã có thật, không phải lo xa: `src/app.tsx` xử lý token hết hạn **có ở `vnpay/`, không có ở `yody/`** — cùng một file, cùng một vai trò, hai hành vi khác nhau, không ai chủ ý.

### Điều làm bài toán này rẻ hơn vẻ ngoài

**61% số file source giống hệt nhau ở cả 15 bản.** Băm nội dung 522 đường dẫn `.ts`/`.tsx`/`.scss` (bỏ `.umi` sinh tự động):

| Số biến thể của cùng một đường dẫn | Số file |
|---|---|
| 1 — giống hệt ở mọi nơi | **317 (61%)** |
| 2 | 81 |
| 3–4 | 41 |
| 5–9 | 50 |
| 10–15 — khác nhau thật | **33 (6%)** |

Và 33 file "khác thật" đó gom đúng ba nhóm: **branding thuần**, **trang chủ**, và **core bị trôi**. Nhóm thứ ba không phải khác biệt cố ý — bằng chứng ở mục 2.1.

---

## 2. Bối cảnh

### 2.1 Hiện trạng — đã verify từng dòng

**Hạ tầng 15 app đã đồng nhất tuyệt đối.** Dependency set giống hệt nhau (`umi ^3.5.20`, `react 16`, 43 deps; `hdbank − yody = ∅`). Cả 15 cùng trỏ **một** backend `https://ambassador.koc.com.vn/api/public`, **một** Firebase `acreator-135b9`, **một** Google client, **một** TikTok client. Chỉ khác `COMMON_PARTNER`, `APP_NAME`, `NEXT_PUBLIC_ORIGIN`, ba article ID, GTM ID.

**Ba bằng chứng cho thấy khác biệt ở tầng core là drift, không phải chủ ý:**

| File | Đo được |
|---|---|
| `src/configs/api.ts` (`hdbank` vs `vpbank`) | Khác nhau **chỉ vì thứ tự khối code**. Nội dung y hệt |
| `src/services/user.ts` (`hdbank` vs `parasola`) | **Giống 100%** |
| `src/wrappers/home.tsx` | Một trong 6 file có đủ **15 biến thể** — mà nội dung là **100% chuỗi branding**, không một dòng logic |

**Trang chủ đối tác đã là một danh sách section, không ai nhận ra.** 14/15 app dùng đúng cùng 4 component trong `pages/partner-home/components/`: `event-active`, `event-active-new`, `statistic`, `user-newest`. Chỉ `wildrift/` thêm 5 section riêng. File `desktop.tsx` chỉ 72–176 LOC, và khoảng một nửa khác biệt giữa các bản là **whitespace do prettier**.

**Stack FE đã hết hạn.** Cả 16 app (15 FE + admin) build trên `node:14.17.3` — EOL 04/2023 — kèm `node-sass ^4.9.0` cũng EOL. Ngược lại **backend hoàn toàn khoẻ**: Go 1.24, Echo v4, mongo-driver 1.11, redis v8, minio-go v7. Mục ruỗng chỉ ở frontend.

### 2.2 Khác biệt kiến trúc cốt lõi: backend đã multi-tenant, chỉ frontend là fork

Đây là lý do PRD này rẻ hơn vẻ ngoài — phần khó nhất của multi-tenant đã xong từ lâu:

| Thứ đã có và đang chạy | Vị trí |
|---|---|
| `PartnerRaw.AllowDomains []string` | `backend/internal/model/mg/partner.go:51` |
| `GetDetailByDomain`, `GetListPartnersByDomain` | `backend/pkg/public/service/partner.go:40-88` |
| Mọi query public scope theo `query.Domain` | `backend/pkg/public/service/partner.go:310` |
| Cache Redis theo domain, TTL 4h | `backend/pkg/public/service/partner.go:44-52` |
| Cờ tính năng theo đối tác (`PartnerOpts`) | `partner.go` — leaderboard, `enableStaffCode`, `requireStaffCodeValidation`, `allowResubmitRejectedContent` |
| Form admin đã sửa được các cờ đó | `admin/src/pages/partner/components/modal.tsx:219-457` |

**Cấu hình đối tác trong admin không phải xây mới — nó đã tồn tại và đang được mở rộng dần.** Cái thiếu là lớp branding/theme/bố cục và cờ bật-tắt module.

Hệ quả cho thiết kế: `partner-app/` **không cần** cơ chế phân giải tenant riêng. Nó gửi `Host`, backend đã biết trả đúng đối tác.

### 2.3 Bốn bài học lấy từ `creator-os` — thiết kế, không phải code

`creator-os` được xây dựng chính xác để giết bài toán này (`docs/architecture/05-theme-and-portals.md` dòng 3: *"1 codebase + runtime theme config — giết bỏ điểm đau lớn nhất của Ambassador"*). Bốn bài học sau đã trả giá bằng bug thật bên đó, **áp thẳng vào PRD này**, mỗi cái ghi rõ nó ràng buộc FR nào:

**BH-1. Template cố định đẻ ra dữ liệu giả → PC-005 bắt buộc là mảng section.**
Nguyên văn: *"template cố định ⇒ thứ tự + sự hiện diện của section nằm CỨNG trong JSX ⇒ section không có dữ liệu VẪN phải render ⇒ đẻ ra dữ liệu GIẢ để lấp chỗ trống"*. Bằng chứng bên họ là `MOCK_QUOTES` — lời chứng thực bịa, gán vào tên và avatar creator **có thật**. Đây là lý do PC-005 **không** cho phép "chọn 1 trong N template".

**BH-2. Catalogue section nằm trong CODE, không nằm trong DB → PC-005.**
*"Nếu để schema section trong DB → 2 nguồn sự thật + mất guardrail whitelist (tenant tự chế block mới)."* DB chỉ lưu mảng `sections`; định nghĩa loại section hợp lệ nằm trong code và validate ở server.

**BH-3. Màu / bo góc / đổ bóng KHÔNG đủ để tả một theme → PC-002 phải có style token.**
*"Đổi preset chỉ đổi được màu, radius, shadow. Cái làm nên brutalist lại nằm ở chỗ khác — micro-label viết hoa giãn chữ, và kẻ ngang thay cho card (cấu trúc, không phải màu). Nếu để mấy thứ đó hardcode trong JSX thì mai mốt đổi theme sẽ ra 'bộ xương brutalist sơn màu khác'."* Kèm một cái bẫy cụ thể: **dùng `??` chứ không `||`** khi merge token, vì `radius: 0` là giá trị hợp lệ và `||` sẽ nuốt mất nó.

**BH-4. Nav sinh RA TỪ `sections[]` → PC-005.**
*"Xoá section thì mục nav tự biến mất ⇒ không bao giờ có anchor chết."*

Bài học phụ, áp vào PC-007: **tag cache phía FE phải khớp từng ký tự với BE**, nếu không thì *"purge im lặng không trúng gì cả: publish xong trang vẫn cũ, không ai thấy lỗi"*. PC-007 yêu cầu test canh hai bên.

### 2.4 Những gì KHÔNG thêm vào

- **Không** page-builder tự do kéo thả HTML. Section là whitelist đóng, có schema.
- **Không** cho đối tác nhập CSS/JS thô. Mọi thứ đi qua token đã định nghĩa.
- **Không** đa ngôn ngữ. Toàn bộ tiếng Việt như hiện tại.
- **Không** nâng cấp hay refactor 15 app cũ trong phạm vi này.
- **Không** đổi mô hình dữ liệu `PartnerRaw` đang có — chỉ thêm collection mới bên cạnh.

---

## 3. User Personas

**P1. Team vận hành** — người thực sự dùng màn cấu hình. **Không phải dev.** Phải làm được toàn bộ việc onboard mà không nhờ ai: nhập màu, tải logo, bật/tắt module, sắp lại trang chủ, xem trước, xuất bản. Sai thì rollback được.
**P2. Marketing của đối tác** — chủ sở hữu nội dung trang chủ và câu chữ. Không truy cập admin trực tiếp; đưa yêu cầu cho P1.
**P3. Dev frontend** — hôm nay mất một đợt việc cho mỗi lần onboard. Sau PRD này chỉ vào cuộc khi đối tác cần một màn hình **hình dạng chưa từng có** (PC-009).
**P4. Dev backend** — thêm một collection và ba endpoint. Không đụng gate, ledger, hay logic thưởng.
**P5. Người dùng của 15 app hiện tại** — **không được ảnh hưởng.** Ràng buộc, không phải mục tiêu.
**P6. Creator của đối tác mới** — không biết và không cần biết mình đang ở app dùng chung. Trải nghiệm phải bằng hoặc hơn app white-label.

---

## 4. Functional Requirements

### PC-001: Một deployment phục vụ mọi domain đối tác

**Priority:** Must Have — nền tảng cho mọi FR còn lại

`partner-app/` chạy **một** container. Đối tác hiện tại của mỗi request xác định bằng `Host`.

**Quy tắc:**

| Ngữ cảnh | Đối tác hiện tại |
|---|---|
| Request có `Host` khớp một `allowDomains` | Chính đối tác đó |
| `Host` không khớp đối tác nào | Trang lỗi có chủ đích, **không** rơi về đối tác mặc định |
| Biến môi trường `PARTNER_SLUG` có giá trị | Ghi đè `Host` — dùng cho môi trường dev và cho trường hợp về sau phải tách deployment riêng |

**Đây là điểm nối duy nhất giữa hai mô hình deployment.** Chốt kiểu nào cũng không phải sửa chỗ khác. Lý do giữ nó là **blast radius**: gộp mọi đối tác vào một container nghĩa là một sự cố chạm mọi đối tác cùng lúc; phải tách lại được một đối tác mà không sửa code.

**Không đoán bừa.** Không lấy đối tác đầu danh sách, không nhớ localStorage. Đoán sai nghĩa là người dùng thấy branding của đối tác khác trên domain của đối tác này.

**AC:**
- [ ] Hai domain khác nhau trên cùng một container trả về hai bộ branding khác nhau
- [ ] `Host` lạ → trang lỗi rõ ràng, không rò branding của đối tác nào
- [ ] `PARTNER_SLUG` ghi đè được `Host`, có test cho cả hai nhánh
- [ ] Không có chỗ nào trong code đọc `COMMON_PARTNER` kiểu build-time

---

### PC-002: Theme runtime từ cấu hình, không nhấp nháy

**Priority:** Must Have

Toàn bộ diện mạo đến từ cấu hình lúc chạy. **Không component nào được hardcode màu.**

**Bộ token bắt buộc:**

| Nhóm | Token |
|---|---|
| Màu | `primary`, `primaryForeground`, `secondary`, `secondaryForeground`, `accent`, `accentForeground`, `background`, `surface`, `elevated`, `text`, `textMuted`, `textSubtle`, `disabled`, `border`, `borderSubtle`, `success`, `warning`, `danger` |
| Hình | `radiusBase`, `radiusPill`, `shadowCard`, `shadowPop` |
| Chữ | `fontSans`, `fontDisplay` |
| Kiểu | `labelTransform`, `labelTracking`, `ctaTransform`, `ctaTracking`, `surfaceMode` |

Nhóm **Kiểu** là hệ quả trực tiếp của BH-3 (mục 2.3) — không có nó thì đổi theme chỉ đổi được lớp sơn. Riêng `surfaceMode` (`rule` ↔ `card`) **không đi qua CSS variable** vì nó rẽ nhánh cấu trúc render, CSS không làm được — component đọc bằng JS.

**Thứ tự merge:** mặc định của app → preset đối tác chọn → bộ token nền của preset → từng field đối tác ghi đè. **Dùng `??`, không dùng `||`** (BH-3).

**Không nhấp nháy (FOUC).** SSR ghi thẳng CSS variables vào thuộc tính `style` của `<html>` trước khi trả HTML. Không được có khoảnh khắc trang hiện màu mặc định rồi mới đổi sang màu đối tác.

**AC:**
- [ ] Đổi một giá trị màu trong admin → xuất bản → tải lại trang thấy đổi, **không build lại**
- [ ] `grep` màu hex trong `partner-app/src/**` (trừ file định nghĩa token) = **0**
- [ ] Tải trang ở mạng chậm (throttle 3G) không thấy nhấp nháy màu mặc định
- [ ] `radiusBase: 0` giữ nguyên là 0, không bị nuốt về giá trị mặc định — có unit test riêng cho ca này
- [ ] Đổi `surfaceMode` đổi được cấu trúc khối, không chỉ đổi màu

---

### PC-003: Ảnh và asset theo đối tác

**Priority:** Must Have

Mọi ảnh nhận diện lấy từ cấu hình, không `require()` từ `src/assets/`.

**Tối thiểu:** `logoUrl`, `logoMobileUrl`, `logoFooterUrl`, `faviconUrl`, `ogImageUrl`, `heroBannerUrl`, và các ảnh mốc thưởng.

**Lưu trữ:** MinIO — đã có sẵn (`backend/internal/module/minio`). Admin tải ảnh lên qua service `file` đang chạy.

**Validate URL:** chấp nhận `http(s)://…` hoặc đường dẫn nội bộ bắt đầu bằng `/`. **Chặn** `//host` (protocol-relative — thoát khỏi origin) và mọi scheme khác (`javascript:`, `data:` — nguồn XSS khi nhồi vào `<img src>` hay `href`).

**AC:**
- [ ] Đổi logo trong admin → xuất bản → site đổi, không build lại
- [ ] Ảnh thiếu → dùng ảnh mặc định của app, **không** vỡ layout, không hiện ảnh lỗi
- [ ] URL dạng `javascript:` và `//evil.com` bị từ chối ở server, không chỉ ở form

---

### PC-004: Bật/tắt module theo đối tác

**Priority:** Must Have

Mỗi nhóm màn hình tuỳ chọn là một cờ trong cấu hình. Tắt cờ → **ẩn khỏi nav VÀ chặn ở route**, không chỉ ẩn menu.

**Danh sách cờ tối thiểu:** `ekyc`, `identityInfo`, `taxCode`, `contract`, `contact`, `statistic`, `affiliate`, `guide`, `support`, `creatorProfile`.

**Fail-soft.** Nạp cờ lỗi → dùng bộ mặc định an toàn, **không** trắng trang. Mặc định an toàn = bật nhóm lõi, tắt mọi module tuỳ chọn.

**Không nhân bản luật ra FE.** Các cờ đã có ở `PartnerOpts` (leaderboard, `enableStaffCode`, `requireStaffCodeValidation`, `allowResubmitRejectedContent`) **giữ nguyên chỗ cũ và nguyên ý nghĩa** — 15 app đang đọc chúng, đổi chỗ là 15 app phải sửa. Cấu hình mới chỉ **thêm** cờ mới, không di dời cờ cũ.

**AC:**
- [ ] Tắt `taxCode` → mục biến khỏi nav, gõ thẳng URL cũng không vào được
- [ ] API cấu hình lỗi → app vẫn dựng được với bộ cờ mặc định
- [ ] `PartnerOpts` cũ đọc được y như trước, không đổi tên field, không đổi vị trí

---

### PC-005: Trang chủ dựng bằng catalogue section

**Priority:** Must Have

Trang chủ là **mảng có thứ tự** các section. Không phải template cố định (BH-1).

**Catalogue nằm trong code**, không nằm trong DB (BH-2). DB chỉ lưu mảng `sections`; validate bằng schema ở server trước khi ghi.

**Loại section tối thiểu** — suy ra từ 4 component mà 14/15 app đang dùng chung, cộng nhóm biên tập:

| Loại | Kiểu | Xoá được? | Lặp? | Lên nav? |
|---|---|---|---|---|
| `hero` | biên tập | Không | Không | — |
| `events` | dữ liệu | Không | Không | Có |
| `statistic` | dữ liệu | Có | Không | — |
| `content-highlight` | dữ liệu | Có | Không | Có |
| `creator-newest` | dữ liệu | Có | Không | — |
| `leaderboard` | dữ liệu | Có | Không | Có |
| `banner` | biên tập | Có | **Có** | — |
| `faq` | biên tập | Có | Không | Có |
| `steps` | biên tập | Có | Không | — |

**Section kiểu `dữ liệu` chỉ lưu tham số truy vấn, KHÔNG copy dữ liệu** (BH-3 phụ / nguyên tắc *reference, don't copy*): `events` lưu `limit`, không lưu danh sách chiến dịch.

**Nav sinh ra từ `sections[]`** (BH-4). Không có bảng nav riêng.

**Section bắt buộc enforce ở SERVER**, không chỉ ẩn nút xoá ở UI.

**`key` bền vững.** Mỗi section có `key` riêng; sửa và sắp xếp địa chỉ hoá theo `key`, **không theo index**.

**AC:**
- [ ] Kéo đổi thứ tự trong admin → xuất bản → trang chủ đổi thứ tự
- [ ] Tắt `leaderboard` → khối biến mất **và** mục nav tương ứng biến mất, không còn anchor chết
- [ ] Gọi thẳng API xoá section `hero` → server từ chối
- [ ] Gửi section `type` lạ → server từ chối, không ghi vào DB
- [ ] Sắp xếp lại rồi sửa một section → sửa đúng section đó, không nhầm sang cái khác

---

### PC-006: SEO, OpenGraph và GTM theo đối tác

**Priority:** Must Have

Lấy từ cấu hình: `title`, `description`, `keywords`, `ogImage`, `canonical`, `gtmId`.

Hôm nay khối này nằm cứng trong `src/wrappers/home.tsx` — file có đủ 15 biến thể mà nội dung là 100% chuỗi branding (mục 2.1). Nó là ví dụ sạch nhất cho toàn bộ PRD.

**AC:**
- [ ] Xem source HTML của hai domain khác nhau → thấy hai bộ meta khác nhau
- [ ] `gtmId` trống → **không** chèn script GTM, không chèn script rỗng
- [ ] Ảnh OG hiện đúng khi dán link vào Facebook/Zalo

---

### PC-007: Nháp → xem trước → xuất bản → rollback

**Priority:** Must Have — P1 là người không code, đây là lưới an toàn

Cấu hình có hai trạng thái: `draft` và `published`. Site công khai **chỉ đọc bản `published`**.

**Luồng:**
1. P1 sửa bản nháp trong admin. Site không đổi.
2. Bấm **Xem trước** → mở site thật với bản nháp, qua token xem trước. **Cùng một app, không hạ tầng riêng.**
3. Bấm **Xuất bản** → sinh một version bất biến kèm `changelog` và người xuất bản; `published` trỏ sang version mới; purge cache.
4. Hỏng → **Khôi phục** một version cũ, một thao tác.

**Token xem trước** phải hết hạn và không đoán được. Người không có token thấy bản `published`.

**Purge cache phải trúng.** Tag cache phía FE khớp **từng ký tự** với backend (bài học phụ, mục 2.3). Phải có test so hai bên — sai tag là lỗi im lặng: xuất bản xong trang vẫn cũ, không ai thấy báo lỗi.

**AC:**
- [ ] Sửa nháp → site công khai không đổi
- [ ] Link xem trước hiện bản nháp; mở ẩn danh không có token → thấy bản published
- [ ] Xuất bản → site đổi trong vòng một lần tải lại
- [ ] Khôi phục version trước → site về đúng trạng thái cũ
- [ ] Có test canh tag cache FE ↔ BE
- [ ] Lịch sử ghi đủ: ai, lúc nào, đổi gì

---

### PC-008: Màn cấu hình trong admin

**Priority:** Must Have

Đặt trong `admin/` hiện tại (umi 3 + antd 4), cạnh form đối tác đã có ở `admin/src/pages/partner/components/modal.tsx`. **Không dựng app admin mới.**

**Nhóm màn:**

| Nhóm | Nội dung |
|---|---|
| Nhận diện | tên, slug, domain, chọn preset, 18 ô màu, bo góc, đổ bóng, font, style token |
| Ảnh | tải lên và gán logo, favicon, OG, hero, ảnh mốc |
| SEO | title, description, keywords, canonical, GTM |
| Module | công tắc cho từng cờ ở PC-004 |
| Trang chủ | danh sách section: thêm, xoá, kéo thứ tự, sửa nội dung từng loại |
| Xuất bản | nút Xem trước, nút Xuất bản kèm ô changelog, danh sách version kèm nút Khôi phục |

**Người dùng là P1, không phải dev.** Mọi ô nhập phải có nhãn tiếng Việt rõ nghĩa, ô màu có bảng chọn chứ không bắt gõ hex trần, và lỗi validate nói **sai gì và sửa thế nào**, không phải tên field kỹ thuật.

**AC:**
- [ ] P1 tạo được một đối tác mới từ đầu tới xuất bản mà không hỏi dev — nghiệm thu bằng một buổi làm thật, không phải đọc code
- [ ] Mọi validate ở server đều có thông báo tương ứng ở form, không để server trả lỗi trần
- [ ] Ô màu xem được kết quả ngay trong admin, không phải xuất bản mới biết

---

### PC-009: Slot override cho màn riêng của đối tác

**Priority:** Should Have — cơ chế làm ngay, nội dung làm khi có đối tác cần

Có những màn không tổng quát hoá được: `agency` của `turborg`, `lp-store` + `mission` + `mission-detail` của `wildrift`. Cấu hình không tả được chúng.

**Cơ chế:** mỗi màn hình là một **slot** có hợp đồng props rõ ràng — trang lo **dữ liệu**, slot lo **hiển thị**. Một registry map `đối tác → module`, module nào thiếu slot thì **kế thừa bản nền**.

**Thêm một màn riêng = thêm một thư mục implement hợp đồng + một dòng registry.** Không đụng dữ liệu, không đụng logic, không đụng route.

**Luật:** **cấm** `if (partner === 'x')` rải rác trong màn hình. Chọn component qua registry, trang không biết mình đang chạy cho đối tác nào.

**AC:**
- [ ] Thêm một slot override cho một đối tác không phải sửa file nào ngoài thư mục của nó + một dòng registry
- [ ] Đối tác không override → nhận bản nền, không cần khai gì
- [ ] `grep` `partner ===` trong thư mục màn hình = **0**

---

### PC-010: Không đụng 15 app hiện tại

**Priority:** Must Have — ràng buộc, không phải tính năng

15 folder đối tác và `admin/` giữ nguyên hành vi. Thay đổi backend trong PRD này **chỉ thêm**, không sửa và không đổi tên field nào mà 15 app đang đọc.

**AC:**
- [ ] Response của `GET /partners/by-slug` và `GET /partners` giữ nguyên hình dạng cũ, đúng từng field
- [ ] Không commit nào của task này chạm vào 15 folder đối tác — kiểm bằng diff
- [ ] Hồi quy: mở 3 app cũ bất kỳ sau khi backend lên, mọi màn chính chạy như trước

---

## 5. Non-Functional Requirements

### NFR-001: Backward compatibility
Không đổi hình dạng response của các endpoint public mà 15 app đang gọi. Cấu hình mới đi qua endpoint mới.

### NFR-002: Không nhân bản luật nghiệp vụ ra FE
Điều kiện thưởng, gate nộp bài, luật xét duyệt tiếp tục nằm ở backend. `partner-app/` chỉ hiển thị.

### NFR-003: Chịu lỗi
API cấu hình lỗi hoặc chậm → dùng bản cache gần nhất. **Không được trắng trang.** Cache Redis đã có; cần thêm một lớp fallback ở phía app.

### NFR-004: Hiệu năng
SSR thêm tối đa **một** request lấy cấu hình mỗi request trang, và request đó phải trúng cache trong đa số trường hợp. Không được làm chậm hơn app white-label hiện tại một cách cảm nhận được.

### NFR-005: Ngôn ngữ
Toàn bộ tiếng Việt. Không đa ngôn ngữ trong phạm vi này.

### NFR-006: Không lỗi UI
Vỡ layout, tràn chữ, chồng modal, lệch mobile đều tính là chưa xong. Mỗi màn phải xem tận mắt trên **cả desktop lẫn mobile** trước khi báo hoàn thành, không chỉ đọc code. Ràng buộc này nặng hơn bình thường vì mọi màn phải đúng với **mọi bộ token**, không chỉ với bộ token của đối tác đầu tiên — tối thiểu kiểm bằng hai preset đối cực.

### NFR-007: Test
Bắt buộc có test cho: merge token (gồm ca `radius: 0`), validate schema section, phân giải đối tác theo `Host`, và khớp tag cache FE ↔ BE.

---

## 6. Epics và thứ tự

| # | Epic | Phụ thuộc |
|---|---|---|
| E1 | Backend: collection `PartnerAppConfig`, version/draft/published, endpoint đọc theo domain, purge cache | — |
| E2 | `partner-app/` scaffold + PC-001 phân giải theo `Host` + PC-002 theme runtime + PC-003 asset | E1 |
| E3 | Admin: nhóm Nhận diện + Ảnh + SEO + PC-007 xuất bản/khôi phục | E1 |
| E4 | 14 màn lõi + hạ tầng dùng chung (components, layouts, models, services, utils) | E2 |
| E5 | PC-005 catalogue section + màn Trang chủ trong admin | E3, E4 |
| E6 | PC-004 bật/tắt module + 5 màn KYC/thuế/hợp đồng | E4 |
| E7 | 8 màn module: affiliate ×4, `statistic`, `creator-profile`, `support`, `campaigns` | E6 |
| E8 | PC-009 cơ chế slot + 6 màn one-off (`agency`, `lp-store`, `mission`, `mission-detail`, `category-home`, `info`) | E7 |
| E9 | PC-010 hồi quy 15 app cũ + nghiệm thu P1 tự onboard một đối tác thật | E5, E6, E7 |

**Cơ chế slot (PC-009) làm ở E8 nhưng phải thiết kế từ E4** — dựng màn lõi mà không theo hợp đồng slot thì E8 phải viết lại.

E1–E3 là đường găng. Từ E4 trở đi các màn độc lập nhau, chia được 2–3 người.

---

## 7. Kiến trúc

```
Browser → creator.<đối-tác>.vn
   │
   ▼ partner-app: đọc Host  (hoặc env PARTNER_SLUG — PC-001)
   │
   ▼ GET /api/public/partners/app-config?domain=…      [Redis 4h — đã có]
   │      └─ ?preview=<token> ──> trả bản draft thay bản published (PC-007)
   │
   ▼ SSR
   │   merge token: mặc định app → preset → override  (dùng ??, không ||)
   │   đổ CSS variables vào style của <html>          → không FOUC (PC-002)
   │   đặt title / favicon / OG / GTM                 (PC-006)
   │
   ▼ Render
       ThemeProvider  ──> component đọc token, không hardcode màu
       FeatureFlags   ──> ẩn nav + chặn route theo cờ  (PC-004)
       sections[]     ──> render theo thứ tự, nav sinh từ đây (PC-005)
       slot registry  ──> đối tác nào override thì lấy bản riêng, còn lại kế thừa nền (PC-009)

admin (umi + antd)
   │  sửa bản draft ──> Xem trước ──> Xuất bản ──> sinh version + purge cache
   └────────────────────────────────> Khôi phục version cũ
```

**Endpoint mới, cả ba đều chỉ thêm:**
- `GET /api/public/partners/app-config` — đọc cấu hình `published` theo domain, hoặc `draft` nếu có token xem trước
- `GET|PUT /api/admin/partners/:id/app-config` — đọc và ghi bản nháp
- `POST /api/admin/partners/:id/app-config/publish` — xuất bản, và `.../restore/:version` để khôi phục

**Schema `partner_app_configs` (Mongo):**

```
partner        ObjectId          — trỏ tới PartnerRaw đã có
status         draft | published
version        int
branding       { logoUrl, logoMobileUrl, logoFooterUrl, faviconUrl, ogImageUrl,
                 heroBannerUrl, brandName, preset,
                 colors{18 token}, radiusBase, radiusPill,
                 fontSans, fontDisplay, shadowCard, shadowPop,
                 style{labelTransform, labelTracking, ctaTransform,
                       ctaTracking, surfaceMode} }
seo            { title, description, keywords, ogImage, canonical, gtmId }
content        { articleIds{support, qa, term, condition}, footerLinks[], website }
modules        { ekyc, identityInfo, taxCode, contract, contact,
                 statistic, affiliate, guide, support, creatorProfile }
sections       [ { key, type, …tuỳ type } ]
auth           { google, tiktok, sso{…} }
publishedAt / publishedBy / changelog
```

**`PartnerOpts` cũ không chuyển vào đây** (PC-004) — 15 app đang đọc nó tại chỗ.

---

## 8. Implementation Scope

### Thay đổi cần làm

**`backend/` (Go 1.24 · Echo · Mongo · Redis · MinIO — không đổi stack):**
- Model `PartnerAppConfigRaw` + `PartnerAppConfigVersionRaw`, collection mới
- Ba nhóm endpoint ở mục 7
- Validate schema section ở server (BH-2) — whitelist loại, chặn xoá section bắt buộc
- Validate URL asset (PC-003) — chặn protocol-relative và scheme lạ
- Purge cache theo tag khi xuất bản, tag khớp FE

**`partner-app/` (app mới — Next.js · React 18/19 · Tailwind):**
- Toàn bộ PC-001 → PC-006, PC-009
- 33 màn: 14 lõi + 5 KYC/thuế/hợp đồng + 8 module + 6 one-off
- Hạ tầng dùng chung viết lại: components, layouts, models, services, utils, hooks

**`admin/` (umi 3 + antd 4 — không đổi stack):**
- Sáu nhóm màn ở PC-008, đặt cạnh form đối tác đã có

**Hạ tầng:**
- Một image, một deployment, nhiều domain trỏ vào
- Fallback cấu hình khi API lỗi (NFR-003)

### KHÔNG làm

- **Không** đụng 15 folder đối tác (PC-010)
- **Không** đổi stack `admin/` — màn cấu hình viết bằng umi + antd sẵn có
- **Không** đổi hay viết lại backend nghiệp vụ: gate, ledger, crawl, đối soát, thưởng
- **Không** di dời `PartnerOpts` sang cấu hình mới
- **Không** phụ thuộc package của `creator-os`; không thêm dependency chéo hai repo
- **Không** nâng đời `umi` / Node của 15 app cũ

---

## 9. Assumptions

1. Mọi domain đối tác **mới** đều CNAME được về hạ tầng của mình, như 15 domain hiện tại đang làm.
2. Backend Go giữ nguyên là nguồn dữ liệu duy nhất; `partner-app/` không có DB riêng.
3. Team có ít nhất một người làm được Next.js + Tailwind, hoặc mượn được từ đội `creator-os` — cùng công ty.
4. Số đối tác chạy trên `partner-app/` trong năm đầu ở mức vài chục, đủ để cache theo domain hoạt động tốt mà không cần lớp cache đặc biệt.
5. Team vận hành (P1) sẵn sàng nhận việc onboard. Nếu không thì PC-008 mất phần lớn giá trị và nên xem lại mức đầu tư vào admin.

---

## 10. Out of Scope

- **Di cư 15 app cũ về `partner-app/`** — quyết định chốt 03/09: đóng băng. **Hệ quả phải nói rõ: PRD này KHÔNG gỡ được cảnh clone bug fix cho 15 bản đó.** 37 commit/6 tháng chạm nhiều folder vẫn còn nguyên. Nó chỉ chặn đống đó phình thêm.
- Nâng cấp `umi` / Node / `node-sass` của 15 app cũ
- Đa ngôn ngữ
- Đối tác tự truy cập admin (chỉ P1 nội bộ dùng)
- Page-builder tự do, nhập HTML/CSS thô
- Chuyển sang `creator-os` như một nền tảng
- Endpoint gộp cấu hình nhiều đối tác trong một request — chỉ làm nếu Assumption #4 sai

---

## 11. Traceability — map sang thiết kế tham khảo `creator-os`

| `creator-os` | PRD này | Quan hệ |
|---|---|---|
| `packages/theme/src/tokens.ts` — resolve + merge + đổ CSS var | **PC-002** | **Tham khảo thiết kế, viết lại.** Lấy nguyên bộ token và thứ tự merge, gồm bẫy `??` vs `||` |
| `portal-creator/app/layout.tsx` — SSR inject | **PC-002** | Áp thẳng cách làm |
| `packages/feature-flags` | **PC-004** | Tham khảo, viết lại; giữ tính chất fail-soft |
| `packages/contracts/src/landing-sections.ts` — catalogue | **PC-005** | **Tham khảo thiết kế, viết lại catalogue riêng.** Loại section suy từ 4 component thực tế của Ambassador, không bê nguyên 8 loại của họ |
| `CmsDocument` + `CmsDocumentVersion` | **PC-007** | Tham khảo mô hình draft/version/publish; hiện thực trên Mongo |
| `portal-creator/themes/` — registry + fallback | **PC-009** | Tham khảo thiết kế |
| model `Domain` | **PC-001** | **Không dùng** — Ambassador đã có `AllowDomains` trên `PartnerRaw` |
| `docs/architecture/14-editions-and-deployment.md` | **PC-001** | Lấy nguyên tắc: khác biệt deployment không nằm ở code |
| NestJS + Prisma + Postgres + RLS | — | **Không dùng.** Backend Ambassador giữ Go + Mongo |
| `packages/ui` (shadcn/radix) | — | **Không dùng code**; `partner-app/` tự dựng bộ component của mình |

---

## 12. Resolved Questions

| Câu hỏi | Chốt (03/09/2026) |
|---|---|
| Đưa đối tác mới lên `creator-os` hay làm trong Ambassador? | **Làm trong Ambassador.** `creator-os` chỉ để tham khảo thiết kế |
| Có dùng lại code / package của `creator-os` không? | **Không.** Tham khảo thiết kế và bài học, tự viết |
| Giữ stack `umi 3` cho app mới hay đổi? | **Đổi.** Đã chốt không di cư 15 app cũ ⇒ mất lý do duy nhất để ở lại `umi 3` / React 16 / `node:14.17.3` (EOL 04/2023) |
| Một deployment chung hay mỗi đối tác một deployment? | **Một deployment**, phân giải theo `Host`. Giữ một điểm nối (`PARTNER_SLUG`) để tách lại được nếu cần |
| 15 app cũ xử lý thế nào? | **Đóng băng.** App mới chỉ phục vụ đối tác mới |
| Đối tác mới cần bao nhiêu màn? | **Toàn bộ 33 màn** — xem mục 6, E4 → E8 |
| Trang chủ cấu hình tới mức nào? | **Mạnh nhất có thể**: bật/tắt, sắp thứ tự, sửa nội dung, cộng khối nội dung tự do có schema |
| Cấu hình sửa xong là ăn ngay hay có bước duyệt? | **Nháp → xem trước → xuất bản**, có lịch sử và khôi phục (PC-007) |
| Ai vận hành màn cấu hình? | **Có team vận hành.** P1 là người không code ⇒ PC-008 phải nghiệm thu bằng buổi làm thật |
| Màn cấu hình dựng bằng gì? | **`admin/` hiện tại** (umi 3 + antd 4), cạnh form đối tác đã có. Không dựng admin mới |

---

## 13. Open Questions

1. **Sáu màn one-off ở E8 có làm ngay không?** `agency` (chỉ `turborg`), `lp-store` + `mission` + `mission-detail` (chỉ `wildrift`), `category-home`, `info` — chủ sở hữu của chúng đều là đối tác **cũ, đã đóng băng**, nên viết xong sẽ chưa đối tác nào dùng. Phạm vi hiện chốt là **làm đủ 33**; nếu hoãn E8 thì rút ~3–4 tuần và ra pilot sớm hơn, cơ chế slot (PC-009) vẫn có sẵn từ ngày một. **Cần chốt trước khi bắt đầu E7.**
2. **Đối tác mới đầu tiên là ai, và bao giờ?** Có mốc thật thì mới xếp được thứ tự E6/E7 theo nhu cầu thật thay vì làm đều.
3. **Ngưỡng blast radius:** bao nhiêu đối tác trên một deployment thì phải tách? Chưa cần trả lời để bắt đầu, nhưng cần trước khi lên production.
4. **Bộ preset khởi điểm gồm những gì?** Đề xuất tối thiểu hai preset đối cực để chứng minh hợp đồng token đúng — sửa một preset mà quên preset kia thì test phải đỏ. Cần thiết kế tham gia.
5. **`partner-app/` nằm trong repo `ambassador` hay tách repo?** Cùng repo thì có hai stack FE song song; tách repo thì thêm một pipeline. Nghiêng về **cùng repo**, ranh giới thư mục rõ, nhưng cần devops xác nhận.

---

## 14. Revision History

| Version | Date | Thay đổi |
|---|---|---|
| 1.0 | 2026-09-03 | Bản đầu. Chốt phương án: app mới trên stack hiện đại, backend Go/Mongo giữ nguyên, `creator-os` chỉ tham khảo thiết kế. Chốt một deployment phân giải theo `Host`, 15 app cũ đóng băng, phạm vi 33 màn, luồng nháp/xem trước/xuất bản/khôi phục. Bốn bài học từ `creator-os` đưa thẳng vào ràng buộc của PC-002 và PC-005 |
