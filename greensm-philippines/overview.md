# GreenSM Creator Philippines — Project Overview

> Localization của hệ thống Creator (vCreator) cho thị trường Philippines, phục vụ chiến dịch GreenSM PH.

**Date:** 2026-04-29
**Launch deadline:** 22/05/2026
**Domain:** `gen-green.ph`
**Brand:** Green SM Philippines (#GreenSM)
**Default language:** Auto-detect (English + Filipino)
**Currency:** Philippine Peso (₱)
**Timezone:** Asia/Manila (UTC+8)

---

## 1. Yêu cầu

Theo brief partner cung cấp:

> Hệ thống dành cho creator GreenSM Philippines, hỗ trợ:
> - Đăng ký creator
> - Tham gia campaign + đăng nội dung trên TikTok / Facebook / YouTube
> - Tracking views/engagement → tính commission
> - Hiển thị commission earned cho creator
> - Admin quản lý creator + content + đối soát + export commission cho payroll
>
> **Ngôn ngữ:** EN + Filipino (Tagalog)
> **Tiền tệ:** Philippine Peso (₱)
> **Payout:** GreenSM PH tự thanh toán hoa hồng cho creator qua hệ thống lương (offline). Hệ thống chỉ tracking commission, không có flow rút tiền cho creator.

---

## 2. Cách thực hiện

Source code base: hệ thống Creator đã có sẵn ở thị trường Indonesia. Localize sang Philippines:

1. **Setup hạ tầng PH** (AT cung cấp: AWS server, MongoDB, Redis, MinIO, domain `gen-green.ph`, OAuth services, Telegram, monitoring)
2. **Foundation Config** — refactor utilities (phone, timezone, currency, search) thành config-driven qua Region struct + ENV variables
3. **Replace hardcode** Indonesia/Vietnam → Philippines (12 chỗ +84, 91 chỗ HCM timezone, 38 chỗ Vietnamese accent functions)
4. **Ẩn/xóa contract sign flow** — coi như source chưa có
5. **Ẩn các module ngoài scope** (payment / bank / withdraw / KYC / tax / FB-IG login / OTP SMS)
6. **Branding GreenSM PH** — logo, banner, font, color theo Brand Guideline + Figma. Layout PH khác hẳn source ID nên rebrand sâu, không chỉ replace assets
7. **Add Filipino (Tagalog)** translation cho ~3,800 keys
8. **Bug fixes** P0/P1/P2 (security + logic) trong source
9. **Init data baseline** (partner config, event đầu tiên, CMS articles, admin root account, RBAC)
10. **QA** core business flows (reconciliation + tax + i18n)
11. **Build handbook site** (user guide + tài liệu nghiệm thu)

---

## 3. Lưu ý phạm vi báo giá

Để hai bên thống nhất rõ ràng kỳ vọng và tránh hiểu nhầm, vui lòng đọc kỹ các điểm sau trước khi review chi tiết. Báo giá hiện tại là **$6,875** (DISO scope $6,732 + Design $143 do AT đảm nhận), chỉ áp dụng cho phạm vi dưới đây. Các hạng mục ngoài phạm vi sẽ được báo giá bổ sung khi cần.

### 3.1. Các chức năng không triển khai (đã thống nhất loại khỏi phạm vi)

Các chức năng dưới đây đã có trong source code Indonesia nhưng được loại khỏi phạm vi cho phiên bản PH lần này:

| Chức năng | Lý do | Cách xử lý |
|---|---|---|
| Hợp đồng điện tử (contract sign) | Theo yêu cầu partner — không ký hợp đồng qua app | Ẩn / xóa toàn bộ flow contract (LEGAL-01) |
| OTP SMS | Sau khi bỏ contract, OTP SMS không còn use case trong source | Comment route + bỏ tích hợp SMS provider |
| Payment / Withdraw / Bank account | Mô hình offline payout — partner thanh toán qua payroll | Ẩn UI + comment route |
| KYC / Identification | Không có flow rút tiền nên không cần xác minh danh tính | Ẩn UI + comment route |
| Tax module | Tax = 0% (partner tự xử lý qua payroll) | Set Region.TaxPercent=0 + skip cron |
| Facebook / Instagram OAuth login | Chỉ sử dụng Phone + Google + TikTok | Ẩn button + comment route |
| Email send module | Source code không có sẵn email module | Không cần rebrand email templates |
| DB migration | Database khởi tạo trống từ đầu, không có data cần migrate | Chỉ tạo data baseline tối thiểu |
| Seed UAT test data | Test data sẽ phát sinh tự nhiên trong quá trình QA | — |

### 3.2. Các hạng mục báo giá riêng

Một số phần công việc cần thiết nhưng được tách thành báo giá riêng để dễ quản lý phạm vi và budget:

| Hạng mục | Ghi chú | Estimate dự kiến |
|---|---|---|
| **DPA 2012 — Explicit consent flow** | Cần partner xác nhận 6 nội dung setup + cung cấp text consent trước khi triển khai | ~19h |
| **DPA 2012 — Right to access / Right to erasure** | Tách riêng cùng nhóm DPA compliance | ~17h |
| Security review + Load test | Khuyến nghị thực hiện trước launch | Báo giá riêng |
| Production deployment + Post-launch monitoring | Cần khi go-live | Báo giá riêng |
| UAT với partner | Phối hợp với partner sau khi system stable | Báo giá riêng |
| Customer support team | Vận hành sau launch (partner-side) | — |

> ⚠️ **Lưu ý compliance:** DPA 2012 là yêu cầu bắt buộc theo luật Philippines. Nếu launch mà thiếu DPA compliance, doanh nghiệp có thể bị NPC phạt **₱500,000 – ₱5,000,000**, kèm trách nhiệm hình sự với DPO và có thể bị tạm ngừng vận hành. Khuyến nghị partner lên kế hoạch triển khai DPA compliance song song với dự án này, dù chưa nằm trong báo giá hiện tại.

### 3.3. Đầu mục cần partner cung cấp / đảm nhận

Để dự án triển khai đúng tiến độ, một số nội dung sau cần partner chuẩn bị và cung cấp:

| Hạng mục | Đơn vị phụ trách | Mức độ ưu tiên |
|---|---|---|
| Terms of Service (TOS) | Partner Legal | Cần trước tuần 4 |
| Privacy Policy theo DPA 2012 | Partner Legal | Cần trước tuần 4 |
| Nội dung text DPA 2012 consent (cho registration form) | Partner Legal | Block DPA flow (báo giá riêng) |
| DPO appointment + NPC registration | Partner | Trước launch |
| Filipino (Tagalog) translation (~3,800 keys) | Partner / Translator | Block i18n phase |
| CMS article content (Support / Q&A / Term / Condition — 4 bài) | Partner Ops | Block data init |
| Content moderation rules theo luật PH (DOH / FDA cho health, cosmetics) | Partner | Block reconciliation checklist |
| TikTok Developer App approval (5-10 ngày) | Partner | URGENT — apply ngay tuần 1 |

→ Chi tiết câu hỏi đang chờ partner trả lời: xem [questions-for-partner.csv](questions-for-partner.csv)

---

## 4. Phạm vi chức năng

### 4.1. Cho Creator (App)

| Module | Mô tả |
|---|---|
| **Đăng ký + Đăng nhập** | Email + Password, Google OAuth, TikTok OAuth |
| **Profile** | Họ tên, email, avatar, gender, birthday |
| **Liên kết social** | TikTok để submit content |
| **Tham gia campaign** | Browse events theo partner, xem chi tiết + thể lệ + hướng dẫn |
| **Đăng nội dung** | Submit URL TikTok/Facebook/YouTube content vào event |
| **Tracking commission** | Xem cashflow log + commission earned (display PHP) |
| **Notification** | In-app + Push notification (Firebase). KHÔNG có email (source không có module email) |
| **Referral** | Mã giới thiệu + reward referral |
| **Statistics** | Thống kê views/contents/invitees của creator |

### 4.2. Cho Admin (Backoffice)

| Module | Mô tả |
|---|---|
| **Staff Auth + 2FA** | Login với reCAPTCHA v3 + TOTP 2FA |
| **RBAC** | Roles + permissions + scopes |
| **Creator Management** | List + filter + ban/unban creator |
| **Content Management** | Review + approve/reject content + bulk actions |
| **Campaign / Event** | CRUD events + reward schemas + statistics |
| **Reconciliation** | Đối soát commission theo period: load items + review + run cashback |
| **Notification** | Tạo + gửi push notification cho creator |
| **CMS** | Articles + News + Tags + Quick Actions |
| **Audit log** | Log tất cả admin actions |
| **Export** | CSV/Excel cho creator/content/event analytics + commission report (`export_transfer_user_cash` đã có sẵn) → import payroll |
| **Segments** | Phân loại creator theo segment + import Excel |

### 4.3. Modules có sẵn nhưng ẨN trong scope này

Các module dưới đây có trong source ID nhưng được **ẩn UI + comment route** (không xóa khỏi codebase). PAYOUT-01 task xử lý:

- Facebook / Instagram OAuth login → hide button + route
- Identification (KYC) creator + admin review → hide trang
- Transfer / Payout admin → hide menu (giữ Reconciliation)
- Bank Account form creator → hide trang
- Tax module → set Region.TaxPercent=0 + skip cron
- Withdraw flow → đã không wire route public sẵn
- OTP SMS request/verify → comment 2 routes (không còn use case sau khi bỏ contract)
- Contract sign flow → comment 4 routes + skip UploadContract + remove constants/contract.go (LEGAL-01)

### 4.4. Background jobs (cron) — giữ nguyên từ source

- Crawl content TikTok / Facebook / YouTube qua content-catcher service
- Cập nhật analytics daily + content flow status
- Tính reward (milestone-based + statistic-based)
- Cleanup old callback records

---

## 5. Localization

### 5.1. Ngôn ngữ
- Replace toàn bộ tiếng Indonesia → English
- Add Filipino (Tagalog) translation (~3,800 keys) — **block bởi partner cung cấp text**
- Default language: Auto-detect browser, có toggle UI để switch EN ↔ Filipino

### 5.2. Format & Region (config-driven qua Region struct)

| Hạng mục | Hiện tại (source ID) | Cần đổi |
|---|---|---|
| Phone code | `+62` (Indonesia) | `+63` (Philippines) |
| Phone regex | Indonesia pattern | `^(09\|\+639\|639)\d{9}$` |
| Currency | IDR (`Rp`) | PHP (`₱`) — comma thousands + 2 decimals |
| Timezone | Asia/Jakarta (UTC+7) → trong code còn `Asia/Ho_Chi_Minh` (91 chỗ) | **Asia/Manila (UTC+8)** |
| Date format | dd/MM/yyyy | MM/dd/yyyy |
| Tax percent | hardcoded VN/ID | 0% (offline payout) |
| Country code | `id`/`vn` | `ph` |

### 5.3. Pháp lý — chỉ rewrite TOS + Privacy Policy

- TOS + Privacy Policy: rewrite theo DPA 2012 (LEGAL-03, 11h)
- Hợp đồng điện tử: **BỎ HOÀN TOÀN** — không có flow ký contract trong scope này
- DPA 2012 consent flow + Right to access/erasure: **TÁCH RIÊNG** — xem mục "LƯU Ý QUAN TRỌNG"

### 5.4. Branding

- Logo, favicon, banner (3:4 mobile + 20:8 desktop + 9:16 campaign)
- Color palette + font theo Brand Guideline GreenSM PH
- Hashtag default: #GreenSM
- GTM tracking: GTM-WTMZXPHC
- Domain: gen-green.ph
- Email hỗ trợ: support.ph@greensm.com
- Hotline: 02-7777-8080
- ⚠️ **Layout PH thay đổi hoàn toàn khác source ID** — không chỉ replace assets, phải rework UI components nhiều page (BRAND-01: 72h, FE 40h + Design 12h + QC 16h + PM 4h)

### 5.5. Payout offline mode (theo §48)

> "GreenSM PH tự thanh toán hoa hồng cho creator qua lương."

- Creator KHÔNG tự rút tiền trong app (hide withdraw button + bank form)
- Hệ thống tracking commission earned + display cho creator
- **Admin Reconciliation module: GIỮ NGUYÊN** (vẫn cần đối soát commission)
- **Admin Transfer module: HIDE** (do payout offline qua payroll)
- Admin export commission qua **`export_transfer_user_cash`** (đã có sẵn trong source, đã verify hoạt động) → import vào payroll system
- Tax % = 0 (khách tự lo tax compliance qua payroll)
- **eKYC module: BỎ KHỎI SCOPE**

### 5.6. Data init PH

- **Partner config**: gengreen partner trên ambassador
- **Event/Campaign đầu tiên**
- **CMS articles**: 4 bài (Support / Q&A / Term / Condition) — partner cung cấp content
- **Admin root account**: 1 cái (partner tự tạo staff sau)
- **RBAC roles + permissions**: baseline

⚠️ **Bank list KHÔNG cần** (do bỏ payment/withdraw)

---

## 6. Hạ tầng (AT cung cấp toàn bộ)

| Hạng mục | Detail |
|---|---|
| Hosting | AWS Singapore region |
| Server IP | 54.169.3.115 (đã có sẵn) |
| Database | MongoDB cluster mới |
| Cache | Redis instance mới |
| Storage | MinIO 4 buckets (public, private, video, contract) |
| DNS | Cloudflare → IP 54.169.3.115 |
| AWS SES | Singapore region (sẵn cho future, hiện chưa có email module) |
| OAuth | Google OAuth + TikTok Developer App + Firebase + reCAPTCHA v3 |
| Monitoring | Sentry + CloudWatch + Telegram alerts |
| Backup | MongoDB daily auto + retention 30 ngày |
| Telegram | Channel admin PH (hoặc reuse VN room) |

---

## 7. Effort estimate (DISO scope only)

### Tổng quan

| Hạng mục | Tasks | Hours | Cost |
|---|---:|---:|---:|
| **DISO scope (tasks.csv)** | 26 | 500h (~62pd) | **$6,732 + $143 Design = $6,875** |
| AT scope (tasks-at.csv) | 7 | 94h (~12pd) | $1,531 |
| **GRAND TOTAL** | **33** | **594h (~74pd)** | **$8,406** |

### Cost theo role (DISO scope)

| Role | Hours | Rate | Cost | Bill to |
|---|---:|---:|---:|---|
| DevOps | 22h | $17/h | $374 | DISO |
| SA | 7h | $17/h | $119 | DISO |
| BE | 140h | $15/h | $2,100 | DISO |
| FE | 104h | $15/h | $1,560 | DISO |
| QC | 131h | $11/h | $1,441 | DISO |
| Design | 13h | $11/h | $143 | **AT** (Design tính sang AT) |
| BA | 58h | $11/h | $638 | DISO |
| PM | 25h | $20/h | $500 | DISO |
| **TOTAL** | **500h** | | **$6,875** | |

→ Chi tiết per-task: xem [tasks.csv](tasks.csv) | Summary: xem [summary.csv](summary.csv) | AT scope: xem [tasks-at.csv](tasks-at.csv)

### Per-module breakdown

| Module | Tasks | Hours | Cost |
|---|---:|---:|---:|
| 1. Setup (Dev local + CI/CD + linter) | 3 | 38h | $602 |
| 2. Foundation Config (Region struct + utils + ENV PH) | 1 | 30h | $451 |
| 3. Replace hardcode Backend (+84, HCM tz, accent, constants, errors) | 5 | 62h | $878 |
| 3. Replace hardcode Frontend (phone, currency, locale, VN text) | 1 | 12h | $168 |
| 4. Contract & Legal (ẩn contract flow + TOS/Privacy) | 2 | 27h | $381 |
| 5. i18n (Filipino translation + toggle UI + format) | 2 | 35h | $475 |
| 6. Branding (rebrand toàn bộ — layout khác hẳn) | 2 | 88h | $1,212 |
| 7. Data Init (init baseline) | 1 | 10h | $134 |
| 8. Bug Fixes Backend (security P0 + logic + tech debt) | 4 | 50h | $682 |
| 9. Payout Offline Mode (hide payment/bank/KYC/FB-IG/OTP/contract) | 2 | 32h | $459 |
| 11. QA & Launch (test + handbook site) | 3 | 116h | $1,433 |
| **TOTAL** | **26** | **500h** | **$6,875** |

---

## 8. Tài liệu / Resources cần partner cung cấp

| # | Item | Owner | Status | Block task |
|---|---|---|---|---|
| 1 | TOS + Privacy Policy text theo DPA 2012 | Legal | ⏳ | LEGAL-03 |
| 2 | Filipino (Tagalog) translation ~3,800 keys | Partner/Translator | ⏳ | I18N-01 |
| 3 | CMS article content (Support / Q&A / Term / Condition) | Ops | ⏳ | DATA-01 |
| 4 | Content moderation rules theo luật PH (DOH/FDA) | Partner | ⏳ | Reconciliation checklist |
| 5 | DPO appointment (Data Protection Officer) | Partner | ⏳ | Compliance |
| 6 | NPC registration (National Privacy Commission) | Partner | ⏳ | Compliance |
| 7 | TikTok Developer App approval (5-10 ngày) | Partner | ⏳ URGENT | SETUP-03 |
| 8 | Logo + Favicon + Brand Guideline PDF | Marketing | ✅ | — |
| 9 | Banner 3:4 + 20:8 + 9:16 (Figma) | Marketing | ✅ [Figma link](https://www.figma.com/design/9j52U0cygugj0b4ajkLn5j/-P--GreenGSM-PHIL---Creators) | — |
| 10 | OG title + description text | Marketing | ✅ Dịch từ trang Indo Gen Green | — |

→ Chi tiết câu hỏi pending: xem [questions-for-partner.csv](questions-for-partner.csv) (4 câu)

---

## 9. Rủi ro & biện pháp giảm thiểu

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | Legal docs (TOS + Privacy) chậm từ partner | Block LEGAL-03 (~11h) | Start work với placeholder, hot-swap khi nhận |
| 2 | Filipino translation chậm | Block I18N-01 (~24h) | Start với EN trước, Filipino layer add sau |
| 3 | Partner-side compliance (DPO + NPC) chưa xong | Block production launch | Partner tự lo, parallel với dev |
| 4 | TikTok app KYB chậm (5-10 ngày) | Block TikTok login | Apply ngay tuần 1 |
| 5 | Source có 4 P0 security bugs (admin staff module) | Phải fix trước launch | Đã list trong BUG-01..04 |
| 6 | **DPA 2012 compliance chưa estimate** | Block launch nếu thiếu (phạt ₱500K-5M) | Cần partner trả lời 6 câu C-DPA-CONSENT để estimate riêng |
| 7 | Layout PH khác hẳn source ID | Tăng effort BRAND-01 | Đã estimate 72h cho rebrand sâu |

---

## 10. Compliance Philippines

⚠️ **Compliance là partner-side responsibility** + technical implementation tách riêng (không trong báo giá $6,875 này):

| Requirement | Type | Status | Estimate riêng |
|---|---|---|---|
| **DPA 2012 explicit consent flow** | Technical | ⏳ Cần partner confirm | ~19h |
| **DPA 2012 Right to access/erasure** | Technical | ⏳ Cần partner confirm | ~17h |
| **TOS + Privacy Policy** | Content | ⏳ Partner Legal soạn | ✅ Đã trong scope (LEGAL-03) |
| **DPO appointment** | Partner-side | ⏳ Partner appoint | — |
| **NPC Registration** | Partner-side | ⏳ Partner đăng ký | — |
| **RA 8792 (E-Commerce)** | N/A | Đã bỏ contract flow nên không applicable | — |

**Phạt nếu thiếu DPA 2012:** ₱500K – ₱5M penalty + 1-6 năm tù DPO + có thể stop operations.

---

## 11. Success criteria

Launch production thành công khi tất cả flow dưới đây pass:

### Creator app

- ✅ Đăng ký creator (form theo source: tên, email, password, phone, ...). KHÔNG verify OTP SMS, KHÔNG ký contract
- ✅ Đăng nhập bằng Email+Password / Google OAuth / TikTok OAuth (FB/IG OAuth login đã ẩn)
- ✅ Hoàn thiện profile + liên kết tài khoản TikTok
- ✅ Browse campaigns + xem chi tiết / thể lệ / hướng dẫn event
- ✅ Submit URL content (TikTok / Facebook / YouTube) vào event
- ✅ Xem commission earned + cashflow log trong app (display PHP ₱ format đúng)
- ✅ Nhận in-app + push notification (Firebase). KHÔNG có email
- ⚠️ DPA 2012 consent + right to access/erasure: **chưa trong scope này, sẽ tách riêng**

### Backend processing

- ✅ Crawl content TikTok / Facebook / YouTube qua content-catcher service
- ✅ Reward calc đúng theo schema (milestone-based + statistic-based)
- ✅ Timezone Manila (UTC+8) cho tất cả daily cutoffs (reward, reconciliation, analytics)
- ✅ Currency stored & calculated chính xác (PHP integer centavos, no rounding bug)
- ✅ 4 P0 security bugs (admin staff) đã fix

### Admin backoffice

- ✅ Staff login với reCAPTCHA v3 + TOTP 2FA
- ✅ RBAC roles + permissions hoạt động
- ✅ Quản lý creator (list / filter / ban) + content review (approve / reject với reason)
- ✅ CRUD events + reward schemas
- ✅ Run reconciliation đợt: load items → review → run cashback
- ✅ Export commission qua `export_transfer_user_cash` (CSV/Excel cho payroll)
- ✅ Audit log ghi lại tất cả admin actions

### i18n + Branding

- ✅ UI hiển thị Auto-detect English / Filipino (toggle switch để override)
- ✅ Branding GreenSM PH đúng (logo, color, font, banner, hashtag #GreenSM)
- ✅ Layout PH theo Figma (khác hẳn source ID)
- ✅ Domain `gen-green.ph` + SSL active

### Documentation (handbook site)

- ✅ Site handbook style như handbook.diso.vn (fork từ techcombank/handbook)
- ✅ ~10 bài creator user guide
- ✅ ~8 bài admin user guide
- ✅ Acceptance docs (changelog + checklist + hướng dẫn tiếp nhận)

### KHÔNG nằm trong success criteria (làm riêng)

- ❌ Security review + load test
- ❌ Production deployment + post-launch monitoring
- ❌ UAT với partner
- ❌ DPA 2012 consent flow + Right to access/erasure

---

## 12. Files & references

### Internal docs

| File | Purpose |
|---|---|
| [tasks.csv](tasks.csv) | DISO scope: 26 tasks chi tiết với effort + cost theo role |
| [tasks-at.csv](tasks-at.csv) | AT/Partner scope: 7 tasks (setup hạ tầng + compliance) |
| [summary.csv](summary.csv) | Báo giá tổng hợp per-module (hours + cost) |
| [timeline.csv](timeline.csv) | Kế hoạch timeline đạt deadline 22/05/2026 (capacity + critical path + mitigation) |
| [questions-for-partner.csv](questions-for-partner.csv) | 4 câu hỏi pending |
| [decisions-confirmed.csv](decisions-confirmed.csv) | 34+ quyết định đã chốt |
| [.tmp/audit-*.md](.tmp/) | 11 audit reports source code |

### Partner-provided resources

| Resource | Link / Note |
|---|---|
| **Figma design** | [GreenGSM-PHIL Creators](https://www.figma.com/design/9j52U0cygugj0b4ajkLn5j/-P--GreenGSM-PHIL---Creators) |
| Onboarding info | `[AT- GSM Creator Philippines] Ambassador- Onboarding - 1. Thông tin.csv` |
| Brand Guidelines PDF | `GSM_MKT01.01_Global_Green SM Brand Guidelines.pdf` |
| KV (logo + colors) | https://drive.google.com/file/d/1FC7zrDDtfgUYV6qA1RGQ_rzFsgJRzbY7 |
| Favicon | https://drive.google.com/file/d/1DwtUdx3I8-qu_9axyp-El3ZgNceiA6i3 |
| Materials/Media kit | https://drive.google.com/drive/folders/1LBPynskkwPBqoZ_1tAWAO_DlJyud-KB5 |

### Rate sheet (DISO)

| Role | Rate ($/h) |
|---|---:|
| DevOps | $17 |
| SA | $17 |
| BE | $15 |
| FE | $15 |
| QC | $11 |
| Design | $11 (bill to AT) |
| BA | $11 |
| PM | $20 |
