# Gen-Green Philippines — Overview

> Phiên bản localized của hệ thống vCreator (Gen-Green VN) cho thị trường Philippines.

**Date:** 2026-04-26
**Domain:** `gen-green.ph`
**Brand:** Green SM Philippines (GreenSM)

---

## 1. Yêu cầu

Theo brief từ partner:

- Hệ thống dành cho creator
- **Có tất cả tính năng** như hệ thống Gen Green tại thị trường Việt Nam
- **Ngôn ngữ:** EN + Filipino (Tagalog)
- **Đơn vị tiền tệ:** Philippine Peso (₱)
- **Điều chỉnh giao diện theo pháp luật Philippines:**
  - Trang Thanh toán
  - Trang Hợp đồng điện tử
  - Hệ thống Admin quản trị

---

## 2. Tóm tắt cách thực hiện

Fork source [vCreator](../../vcreator/) → repo mới → localize cho thị trường PH:

1. Replace toàn bộ tiếng Việt → EN + Filipino
2. Đổi currency VND → PHP (Peso)
3. Đổi phone format +84 → +63
4. Đổi bank list VN → PH banks
5. Rewrite contract template + TOS theo luật PH
6. Đổi branding sang GreenSM
7. Init data PH mới (cơ sở làm việc, employee registry, banks)
8. Bỏ scope: Tax module, Payment/Withdraw, Scalef, Affiliate (xem §4)

---

## 3. Hạng mục localize

### 3.1. Internationalization (EN + Filipino)

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| Frontend creator (`frontend-green`) | `vi-VN.ts` 86 dòng + tiếng Việt hard-code khắp components | Replace + add EN + Filipino |
| Frontend admin | `vi-VN.ts` 405 dòng + tiếng Việt hard-code | Replace → EN |
| Backend error messages | Tiếng Việt hard-code trong service/social/* | Replace → EN + Filipino |
| Backend `locale/properties/` | Có `en/` + `vi/` | Audit `en/` + thêm `fil/` |
| Email templates | Tiếng Việt hard-code | EN + Filipino templates |
| Date/time format | `dd/MM/yyyy` | `MM/dd/yyyy` (PH convention) |
| Number/Currency format | `1.000.000đ` | `1,000,000 ₱` (comma + 2 decimals) |
| Language toggle UI | Không có | Build mới do support 2 languages |

> **Lưu ý:** I18n hiện tại coverage thấp — nhiều UI text tiếng Việt nằm trực tiếp trong components/services. Filipino translation cần native translator hoặc partner cung cấp text.

### 3.2. Currency & Format

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| Currency formatter | `format.ToCurrencyVND` (`đ`, no decimal, dot thousands) | `ToCurrencyPHP` (`₱`, 2 decimals, comma thousands) |
| Currency stored in DB | Integer VND | Integer centavos (₱1 = 100 centavos) |
| Phone regex | `^(0|\+84|84)(\d{9}|\d{10})$` | `^(09|\+639|639)\d{9}$` (PH 11 digits) |
| Phone format util | `format.ToPhoneVN()` (+84 strip) | Generic theo region (+63) |

### 3.3. Contract & Legal

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| Contract HTML template | `internal/constants/contract.go` 786 dòng tiếng Việt + luật VN | Rewrite EN/Bilingual theo luật PH (RA 8792 + DPA 2012) — **legal team partner cung cấp** |
| Bên A trong contract | "CÔNG TY TNHH INTERSPACE VIỆT NAM" | GreenSM Philippines (Pasay City) |
| Jurisdiction | Tòa án Hà Nội | Manila courts / PDRCI arbitration (theo template legal cung cấp) |
| Click-to-sign + OTP | Đã có | Giữ nguyên — RA 8792 § 8 công nhận |
| Upload contract PDF Drive | Đã có | Giữ nguyên + folder Drive mới cho PH |
| TOS / Privacy Policy | TOSv3.0 VN | Rewrite theo DPA 2012 — **legal team partner cung cấp** |
| DPA 2012 consent flow | Không có | **Build mới** — explicit consent checkboxes (registration + login) |
| Identification reference | "Số CCCD" only | Multi-type: PhilSys ID, TIN, UMID, Driver's License, Passport, SSS, Voter's ID |

### 3.4. KYC

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| ID type constant | `IdentificationTypeCCCD` only | Multi-type theo §3.3 |
| eKYC provider | VN-specific (FPT.AI/VNPT) | TBD: Manual hoặc auto provider PH (xem questions §F) |

### 3.5. Branding (Cleanup + Replace)

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| VinFast Creator legacy | Còn sót: README "VINFAST CREATOR" + email templates + assets `Gen-G.png` `Green-Creator.png` | Audit & xóa toàn bộ tham chiếu |
| Logo / Favicon | Logo Gen-Green VN | Asset GreenSM PH (partner đã cung cấp KV + Brand Guidelines PDF) |
| Color palette | VN palette | Theo Brand Guideline GreenSM PH |
| Banner home + Campaign banner | Có | Banner 3:4 mobile + 20:8 desktop + 9:16 campaign (cần file thiết kế) |
| OG title + description | Mặc định | Dịch từ trang Indo Gen-Green |
| Hashtag campaign default | Tùy event | `#GreenSM` |
| GTM ID | N/A | `GTM-WTMZXPHC` |
| CTA "Về Đối tác" link | vinfast.vn | https://www.greengsm.ph/ |
| Email signature footer | Tiếng Việt + Interspace VN | EN + GreenSM Philippines |
| Hotline | Hotline VN | 02-7777-8080 |
| Email hỗ trợ | support@vcreator.global | support.ph@greensm.com |
| Địa chỉ công ty | Hà Nội | 6TH FLOOR TWO E-COM CENTER, BAYSHORE AVE, MALL OF ASIA COMPLEX BRGY 76, PASAY CITY 1300 |
| Facebook page | FB VN | https://www.facebook.com/greengsm.ph |

### 3.6. SMS / Notification

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| SMS provider | AccessTrade SMS (eSMS / Zalo channel) | SMS PH provider (TBD: Semaphore / Globe Labs / Twilio / Movider) |
| SMS sender ID | Brand ID VN | Đăng ký sender ID với telco PH (Globe + Smart + Dito) |
| OTP via Zalo | Có | **Bỏ Zalo channel**, dùng SMS |
| Push notification (Firebase) | Có | Giữ nguyên |
| In-app notification | Có | Giữ logic + đổi text EN/Filipino |

### 3.7. Bank & Staff Data

| Hạng mục | Hiện tại | Cần làm cho PH |
|---|---|---|
| Bank list seed | VN banks | PH banks: BDO, BPI, Metrobank, UnionBank, LandBank, Security Bank, RCBC, PNB, China Bank, EastWest |
| Cơ sở làm việc | 57 cơ sở Vin VN | Init cơ sở GreenSM PH (số lượng TBD từ partner) |
| Employee registry | VN staff data | Init data nhân viên GreenSM PH mới |

### 3.8. Infrastructure

| Hạng mục | Quyết định |
|---|---|
| Repo | Tạo mới (tên TBD) |
| Hosting | AWS — server có sẵn IP `54.169.3.115`, cluster mới hoàn toàn |
| Database | MongoDB cluster mới, data fresh |
| Redis | Instance mới |
| MinIO | 4 buckets mới (public/private/video/contract) |
| Domain & DNS | `gen-green.ph` (Cloudflare DNS) |
| Email service | AWS SES Singapore region |

---

## 4. Scope KHÔNG bao gồm (cắt khỏi bản VN)

### 4.1. Tax module — bỏ hẳn

Theo confirm partner: **"khách sẽ tự thanh toán hoa hồng cho creator thông qua lương"** → hệ thống KHÔNG cần tax module.

Bỏ: auto withhold tax, tax refund flow, trang tax frontend.

### 4.2. Payment / Withdraw — bỏ hẳn

Cùng lý do trên — khách tự payout qua payroll. Hệ thống chỉ tracking commission earned (giữ Cash flow log để creator xem số tiền earned), không có flow rút tiền.

Bỏ: bank account binding, withdraw request, QR payment.

→ Thay thế: **Commission report export** (CSV/Excel) cho khách import vào payroll system.

### 4.3. Scalef integration — bỏ hẳn

Không phục vụ thị trường PH.

### 4.4. Instagram crawl — bỏ hẳn

Hiện tại disabled (`INSTAGRAM_IS_ENABLE=false`) trong source.

### 4.5. Affiliate / E-commerce — không trong scope

Không có ở source vCreator. Không build mới.

---

## 5. Timeline & Team

- **Timeline:** ~3 tuần
- **Team:** 1 BE + 1 FE + 1 QC + 1 PM + 1 Designer
- **Capacity:** ~75 person-days

---

## 6. Tài liệu / asset cần partner cung cấp

| # | Item | Owner | Deadline | Status |
|---|---|---|---|---|
| 1 | Contract template (EN, luật PH) | Legal team | Trước tuần 2 | ⏳ |
| 2 | TOS & Privacy Policy (DPA 2012) | Legal team | Trước tuần 2 | ⏳ |
| 3 | Entity ký Bên A | Legal team | Trước tuần 1 | ⏳ |
| 4 | Bank list PH (bank code chính thức) | Ops team | Tuần 1 | ⏳ |
| 5 | Cơ sở làm việc PH + employee data | Ops team | Tuần 1 | ⏳ |
| 6 | Branding asset (logo, favicon, banners) | Marketing team | Tuần 1 | ⏳ |
| 7 | OG title + description text | Marketing team | Tuần 1 | ⏳ |
| 8 | SMS sender ID đăng ký với telco PH | Ops team | Tuần 1 | ⏳ |
| 9 | NPC registration | Legal team | Trước launch | ⏳ |
| 10 | DPO appointment | Partner | Trước launch | ⏳ |
| 11 | SMS provider account | Ops team | Tuần 1 | ⏳ |
| 12 | eKYC provider account (nếu chọn auto) | Ops team | Tuần 2 | ⏳ |
| 13 | CMS article IDs (Support / Q&A / Term / Condition) | Ops team | Tuần 1 | ⏳ |
| 14 | Event ID trên ambassador system | Ops team | Tuần 1 | ⏳ |
| 15 | Filipino translation (text content) | Marketing/Translator | Tuần 2 | ⏳ |

---

## 7. Câu hỏi cần partner trả lời

Form đầy đủ trong [questions-for-partner.csv](questions-for-partner.csv).

Tóm tắt nhóm câu hỏi còn pending:

- **A. Language:** Default language? Toggle UI?
- **C. Legal:** Entity ký, DPO, NPC registration, jurisdiction
- **F. KYC:** Manual hay auto eKYC, ID types accept, provider preference
- **G. SMS:** Provider preference, sender ID đã đăng ký chưa
- **H. Repo & Infra:** Tên repo, AWS account, MongoDB cluster
- **I. Scope:** Số cơ sở GreenSM PH, contract auto-sign vs DocuSign, min creator age, commission export format
- **J. Timeline:** UAT period, PIC UAT phía partner
- **L. SEO:** OG title/description text, OG image

---

## 8. Risks chính

| # | Risk | Mitigation |
|---|---|---|
| 1 | Legal docs (contract, TOS, Privacy) chậm từ partner | Bắt đầu work với placeholder template, hot-swap khi nhận được |
| 2 | Filipino translation chậm | Start với EN trước, Filipino layer add sau |
| 3 | DPA 2012 violation | Hire DPO + register NPC trước launch (partner-side) |
| 4 | i18n debt — tiếng Việt hard-code khắp codebase | Tuần 1 grep audit toàn bộ |
| 5 | SMS provider PH KYB chậm | Bắt đầu apply ngay tuần 1 |
| 6 | Timeline 3 tuần với full scope tight | Đã cắt Tax + Payment khỏi scope; nếu chậm thì cắt thêm i18n Filipino |

---

## 9. Files liên quan

| File | Mục đích |
|---|---|
| [overview.md](overview.md) | Tài liệu tổng quan này |
| [questions-for-partner.csv](questions-for-partner.csv) | Form câu hỏi partner cần trả lời |
| `[AT- GSM Creator Philippines] Ambassador- Onboarding - 1. Thông tin.csv` | Thông tin onboarding partner cung cấp |

> Feature checklist + estimate đang được rebuild — sẽ verify từng feature từ source code thực tế.
