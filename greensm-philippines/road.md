# Road — GreenSM Philippines TODO List

> Danh sách task có thể làm ngay, loại Branding refactor (BRAND-01..02) + DevOps (SETUP-D01..03) + các task block bởi partner.

**Tổng:** 18 tasks, 329h | **Deadline:** 22/05/2026

## ✅ Đã xong

- [x] Setup local env: backend (3010/3011/3012) + admin FE (8000) + DB `vcreator-philippines` + captcha + TOTP + seed staff `vinhnguyen@diso.vn`
- [x] Symlink locales (backend + admin)

## ⏸ Deferred (skip lúc này)

- Frontend creator (port 8002) — `React is not defined` chưa fix, để sau khi làm BRAND-01 refactor giao diện

---

## 🟢 Phase 1 — Foundation (làm đầu tiên, block các task khác)

### FOUND-01: Region config + utility functions + ENV setup PH (30h) ✅

> Block: REPL-01..05 phải đợi cái này xong.

**Backend:**
- [x] Add Region struct vào `internal/config/env.go` (COUNTRY_CODE, PHONE_CODE, PHONE_REGEX, TIMEZONE, CURRENCY, TAX_PERCENT, LANGUAGE)
- [x] Add constants `IPCountryCodePH` + `LangFil` (+ `IPCountryCodeVN`, `IPCountryCodeID`)
- [x] Load Region từ ENV (verified: Asia/Manila, +63, PHP)
- [x] `format/phone.go`: build `FormatPhoneRegion` + `PhoneNumberFormatRegion` + `PhoneNumberIsValidRegion`
- [x] `util/ptime/region.go`: build `GetRegionLocation`, `TimeOfDayInRegion`, `TimeStartOfDayInRegion`, `TimeEndOfDayInRegion` (cached location)
- [x] Refactor `util/time.go`: 15 HCM functions → wrappers gọi Region functions (giữ tên cũ deprecated cho REPL-02 swap callsite ở Phase 3)
- [x] Refactor `util/ptime/parse.go` + `helper.go`: HCM helpers → Region helpers
- [x] `format/string.go`: thêm `NormalizeSearchString` (canonical), `NonAccentVietnamese` thành wrapper deprecated. `SearchString` đã dùng tên mới

**Config:**
- [x] Tạo `.env` với values PH:
  - [x] `REGION_COUNTRY_CODE=PH`
  - [x] `REGION_PHONE_CODE=+63`
  - [x] `REGION_PHONE_REGEX=^(09|\+639|639)\d{9}$`
  - [x] `REGION_TIMEZONE=Asia/Manila`
  - [x] `REGION_CURRENCY=PHP`
  - [x] `REGION_TAX_PERCENT=0`
  - [x] `REGION_LANGUAGE=fil`

**QC:**
- [x] Smoke test cơ bản utils (load ENV, format phone, get timezone) — verified: Region load PH/+63/Asia/Manila/PHP/fil; phone format 09xxx → +639xxx; PH regex pass, VN regex fail; NormalizeSearchString diacritics OK; admin server start clean với DB `vcreator-philippines`.

---

## 🟢 Phase 2 — Cleanup ẩn modules ngoài scope (song song với Phase 1)

### PAYOUT-01: Ẩn payment / bank / withdraw / tax / KYC / FB-IG / OTP (28h) ⏳ BE+Admin xong, Creator FE deferred

**Frontend Creator:** ⏸ deferred (frontend bị block bởi React-not-defined)
- [ ] Hide Withdraw button trong cashflow page
- [ ] Hide Bank account form (page `/bank`)
- [ ] Hide Tax declaration page (`/khai-bao-thue` / tax)
- [ ] Hide KYC Identification upload page
- [ ] Hide Facebook login button + route `/login-with-facebook`
- [ ] Hide Instagram login button + route `/login-with-instagram`
- [ ] Update label "Số dư có thể rút" → "Hoa hồng đã tích lũy"

**Frontend Admin:**
- [x] Transfer/Payout menu — **GIỮ** (cần cho PAYOUT-02 approve commission + export)
- [x] Hide Identification Review menu (đã comment sẵn trong [admin/config/routes.ts](accesstrade-projects/vcreator-philippines/admin/config/routes.ts))

**Backend (comment-out routes):**
- [x] Comment `/users/bank-cards/*` (4 routes) — [pkg/public/router/user.go](accesstrade-projects/vcreator-philippines/backend/pkg/public/router/user.go)
- [x] Comment `/users/identification/*` (3 routes) — same file. (Không có route `/users/ekyc/*` trong code base.)
- [x] Comment `/users/login-with-facebook` + `/users/login-with-instagram`
- [x] Comment `/users/request-otp` + `/users/verify-otp`
- [x] Skip `UpdateCashFlowTax` cron entirely — guard `if Region.TaxPercent <= 0 { return }` ở [pkg/public/service/schedule.go](accesstrade-projects/vcreator-philippines/backend/pkg/public/service/schedule.go) (no-op trên PH)
- [x] Skip `UpdateInfoContract` cron — guard country-code != VN
- [x] Disable admin `identification` route group ở [pkg/admin/router/router.go](accesstrade-projects/vcreator-philippines/backend/pkg/admin/router/router.go) (transfers giữ enable cho PAYOUT-02)

### LEGAL-01: Ẩn/xóa contract sign flow (16h) ⏳ BE+Admin xong, Creator FE deferred

**Backend:**
- [x] Comment `/users/contract/info` (POST upsert info) — [pkg/public/router/user.go](accesstrade-projects/vcreator-philippines/backend/pkg/public/router/user.go)
- [x] Comment `/users/contract/estimate`
- [x] Comment `/users/contract/agree`
- [x] Comment `/users/contract/pre-signed` (sign OTP)
- [x] Skip `UploadContract` (Drive + MinIO upload PDF) — guard `if ContractTemplate == "" { return "", nil }` ở cả [admin](accesstrade-projects/vcreator-philippines/backend/pkg/admin/service/user.go#L156) + [public](accesstrade-projects/vcreator-philippines/backend/pkg/public/service/user.go#L666) services + GetContractEstimate
- [x] Empty `constants/contract.go` template (219 dòng Bahasa → 9 dòng stub) — [internal/constants/contract.go](accesstrade-projects/vcreator-philippines/backend/internal/constants/contract.go)

**Frontend Creator:** ⏸ deferred
- [ ] Hide Contract sign page + flow
- [ ] Hide Profile section "Hợp đồng" (status + download PDF)

**Frontend Admin:**
- [x] Không có Contract management menu trong admin routes hiện tại — không cần action.

### PAYOUT-02: Verify Commission Export flow cho offline payout (4h) ✅ partial

- [x] Verify code path:
  - Admin Transfer page (`/transfer`) → tạo + approve batch (route `transfers(r)` giữ enable, menu admin FE giữ).
  - Export trigger: `DataExportTypeTransferUserCash` → `exportImpl.ExportTransferUserCash` ([pkg/admin/service/export_transfer_user_cash.go](accesstrade-projects/vcreator-philippines/backend/pkg/admin/service/export_transfer_user_cash.go)) → file Excel: index, userId, name, hashtag, eventId, totalView, total + per-event breakdown + tổng.
  - Locale keys: `ExportUserTransferCash*` ([internal/locale/export.go](accesstrade-projects/vcreator-philippines/backend/internal/locale/export.go)).
- [ ] End-to-end QA test (cần data): Admin chạy reconciliation → Approve → Export → import payroll. Đợi có dummy data + môi trường staging.

---

## 🟢 Phase 3 — Replace hardcode (sau FOUND-01)

### REPL-01: Replace +84 hardcode (5h, 12 chỗ)

- [ ] `format/string.go:31, 70-71, 77` (PhoneNumberFormatFromPhone)
- [ ] `model/mg/user.go:152` (search string)
- [ ] `service/otp.go:108` (OTP send)
- [ ] `public/service/user.go:113, 616` (contract)
- [ ] `public/service/identification.go:83`
- [ ] `public/service/schedule.go:413`
- [ ] `admin/service/user.go:184`
- [ ] Verify pass test sau khi replace

### REPL-02: Replace HCM timezone (36h, 91 chỗ)

**Refactor utility:**
- [ ] `util/time.go` — refactor 15 HCM functions → Region functions
- [ ] `util/ptime/parse.go`

**Public services callsite:**
- [ ] `public/service/schedule.go`
- [ ] `public/service/user.go`
- [ ] `public/service/withdraw.go`
- [ ] `public/service/identification.go`

**Admin services callsite:**
- [ ] `admin/service/transfer.go`
- [ ] `admin/service/reconciliation.go`
- [ ] `admin/service/content.go`
- [ ] `admin/service/event.go`
- [ ] `admin/service/exports.go`
- [ ] `admin/service/migration.go`
- [ ] `admin/service/user.go`
- [ ] `admin/service/schedule.go`

**Handlers:**
- [ ] `admin/handler/event.go`

**Cleanup:**
- [ ] Remove constant `timezoneHCM`

### REPL-03: Replace Vietnamese accent functions (6h, 38 chỗ)

- [ ] `admin/service/reconciliation.go` (3 chỗ)
- [ ] `admin/service/transfer.go` (2 chỗ)
- [ ] `admin/service/event.go` (slug generators - 2 chỗ)
- [ ] `admin/service/partner.go` (slug - 2 chỗ)
- [ ] `admin/service/export.go` (filename - 2 chỗ)
- [ ] `admin/service/common.go` (bank search)
- [ ] `admin/model/request/notification.go`
- [ ] `admin/model/request/article.go`
- [ ] `admin/model/request/news.go`
- [ ] `admin/model/request/segment.go`
- [ ] `admin/model/request/tag.go`
- [ ] `admin/server/initialize/dummy_db.go` (3 chỗ)
- [ ] Verify search/sort vẫn work sau replace

### REPL-04: Replace constants + slug VN-specific (4h)

- [ ] Move `RegexPhoneNumber` (line 40) → đọc từ ENV
- [ ] Remove constant `timezoneHCM` (line 72)
- [ ] Remove `PercentTaxIndonesia` + `PercentTaxVietNam` (line 226-227) → config-driven
- [ ] Remove `ConvertSlugProvince` + `ConvertSlugProvinceFind` (ho-chi-minh ⇄ tp-ho-chi-minh logic)

### REPL-05: Replace VN error messages + Indonesia/VN-specific code (11h)

- [ ] Vietnamese error messages → locale keys (3 chỗ):
  - [ ] `public/service/identification.go:453`
  - [ ] `public/service/schedule.go:739`
  - [ ] `public/service/schedule.go:1775`
- [ ] Remove hardcode `if typeBank != "indo"` (admin/common.go:150)
- [ ] Refactor `BeneficiaryForVietinbank` field → generic (admin/common.go:182 + bank model)
- [ ] Update tax cron firstMonth date (schedule.go:760) hardcode 2024-03-31 → ENV var

### FE-01: Replace FE hardcode (12h)

**Phone format:**
- [ ] `frontend/src/configs/app.tsx:58` — phoneNumberPrefix `+84` → `+63`
- [ ] `frontend/src/configs/form.ts:3` — phoneRegExp Indonesia → PH
- [ ] `admin/src/utils/format.ts:69-70` — +84 hardcode

**Currency:**
- [ ] `admin/src/utils/format.ts:112` — unit `VND` → `PHP`

**Default locale config:**
- [ ] `frontend/config/config.ts` — `id-ID` → auto-detect
- [ ] `admin/config/config.ts` — `id-ID` → auto-detect

**Tiếng Việt hardcode (~7 chỗ):**
- [ ] `frontend/src/pages/bank/components/user-cards/index.tsx:107, 123`
- [ ] `frontend/src/pages/account/management/index.tsx:64`
- [ ] `frontend/src/pages/main-home/index.tsx:116`
- [ ] `admin/src/utils/format.ts` comments
- [ ] `admin/src/utils/upload.ts:38` error message
- [ ] `frontend/src/utils/breadcrumb-utils.ts` (~10 comments)

**Cleanup:**
- [ ] Verify `admin/format.ts` Vietnamese accent funcs còn cần không

---

## 🟢 Phase 4 — Bug fixes (làm bất kỳ lúc nào, độc lập)

### BUG-01: P0 Security bugs admin staff (9h) — BẮT BUỘC TRƯỚC LAUNCH

- [ ] `staff.go:264` — `GetMe()` permission check (validate userID==tokenOwner OR isRoot)
- [ ] `staff.go:339` — UpdateInfo isRoot escalation (block isRoot field từ user-controlled body)
- [ ] `staff.go:325` — `$nin` syntax error (MongoDB syntax `$nin` → `$ne`)
- [ ] `staff.go:214` — reCAPTCHA score validation (validate score threshold)

### BUG-02: Staff hardening (9h)

- [ ] `staff.go:118` — Add TOTP rate limit (lock after N attempts)
- [ ] `staff.go:207` — Normalize email lowercase trong login
- [ ] `transfer_processing.go:56` — Fix transfer math.Max logic bug (filter inverted)

### BUG-03: Event + Content + Schedule logic bugs (25h)

**Event:**
- [ ] `event.go:296-298` — GetList sort bug (boolean sort)
- [ ] `event.go:574` — GetLeaderBoard sort (add SortInterface)
- [ ] `event.go:314-319` — Commented schema time-window (decide enable/remove)

**Content & Schedule:**
- [ ] `transcript.go:28, 38` — Loop return → continue
- [ ] `referral.go:76` — Referral cash always 0 (populate value)
- [ ] `news.go:38` — Fix typo "new" → "news"
- [ ] `user.go:1797` — `isExistedEmail` incomplete (check tất cả email fields)
- [ ] `reconciliation_running.go:304` — Reconciliation rollback on failure
- [ ] `schedule.go:1408` — OOM protection `UpdateSearchStringContent` (pagination)

### BUG-04: Cleanup tech debt (7h, P2 — có thể defer)

- [ ] `user.go:1639` — Add max recursion guard cho `GenerateCode`
- [ ] `user.go:662` — Add PDF cleanup sau `UploadContract`
- [ ] Cleanup withdraw dead code (route không wire)
- [ ] Implement `event_reward` stub hoặc remove
- [ ] Branch card feature decide — uncomment & fix HOẶC remove
- [ ] Tax double-charge verify — code không crash khi rate=0

---

## 🟢 Phase 5 — i18n infrastructure (không cần Filipino text)

### I18N-02: Language toggle UI + format date/number (11h)

- [ ] Wire `SelectLang` component vào header (component đã có sẵn 316 lines)
- [ ] Add language option `fil-PH` vào dropdown
- [ ] Verify auto-detect browser language work
- [ ] Persist language choice trong localStorage
- [ ] Update date format `dd/MM/yyyy` → `MM/dd/yyyy` (12 chỗ trong configs)
- [ ] Update number format → `en-PH` style (comma thousands + 2 decimals)

---

## 🟡 Phase 6 — QA & Documentation (làm song song với phases trên)

### QA-05: Build handbook site (56h, BA-heavy)

> Source: fork từ `accesstrade-projects/techcombank/handbook`

**Setup (FE):**
- [ ] Fork code TCB handbook
- [ ] Adjust branding (logo, theme color)
- [ ] Deploy

**Content Creator (~10 bài, BA):**
- [ ] 00. Getting started
- [ ] 01. Đăng ký + Đăng nhập
- [ ] 02. Cập nhật profile
- [ ] 03. Liên kết tài khoản TikTok
- [ ] 04. Browse & tham gia campaign
- [ ] 05. Submit content
- [ ] 06. Theo dõi commission earned
- [ ] 07. Notification
- [ ] 08. Referral
- [ ] 09. FAQ

**Content Admin (~8 bài, BA):**
- [ ] 00. Getting started + login 2FA
- [ ] 01. RBAC + tạo staff account
- [ ] 02. Quản lý creator (list/filter/ban)
- [ ] 03. Tạo & quản lý campaign/event
- [ ] 04. Content moderation (approve/reject)
- [ ] 05. Reconciliation flow + đối soát commission
- [ ] 06. Export commission cho payroll
- [ ] 07. CMS articles + notification

**Tài liệu nghiệm thu:**
- [ ] Acceptance checklist (theo scope đã chốt)
- [ ] Test report tóm tắt
- [ ] Changelog vs source ID gốc
- [ ] Hướng dẫn tiếp nhận hệ thống (env vars + admin root + monitoring access)

### QA-01: Setup test environments + smoke test (30h)

- [ ] Setup staging environment
- [ ] Setup UAT environment
- [ ] Smoke test E2E:
  - [ ] Register + login (Email + Google + TikTok)
  - [ ] Submit content + reconcile + view stats
  - [ ] Currency PHP + timezone Manila
  - [ ] Admin 2FA + Captcha

### QA-02: Test core business flows (30h)

- [ ] Admin Reconciliation + Transfer flow (full lifecycle)
- [ ] Tax flow validation (verify code không crash khi rate=0)
- [ ] i18n EN + Filipino toggle
- [ ] Browser/responsive (Chrome/Safari/iOS/Android)

---

## 📋 Tóm tắt theo phase

| Phase | Tasks | Hours | Note |
|---|---|---|---|
| 1. Foundation | FOUND-01 | 30h | Block các task khác |
| 2. Cleanup ẩn modules | PAYOUT-01, LEGAL-01, PAYOUT-02 | 48h | Song song Phase 1 |
| 3. Replace hardcode | REPL-01..05, FE-01 | 74h | Sau Phase 1 |
| 4. Bug fixes | BUG-01..04 | 50h | Độc lập, BUG-01 ưu tiên |
| 5. i18n infra | I18N-02 | 11h | FE chính |
| 6. QA & Docs | QA-01, QA-02, QA-05 | 116h | BA viết handbook sớm |
| **TOTAL** | **18 tasks** | **329h** | |

---

## 🚫 Chưa làm bây giờ (đợi)

| Task | Lý do đợi |
|---|---|
| BRAND-01, BRAND-02 (96h) | Đợi confirm design final + sẵn sàng rebrand |
| SETUP-D01..03 (38h) | DevOps task, làm sau |
| LEGAL-03 (11h) | Đợi partner cung cấp TOS + Privacy Policy text |
| I18N-01 (24h) | Đợi partner cung cấp Filipino translation ~3,800 keys |
| DATA-01 (10h) | Đợi partner cung cấp CMS article content |

## 📌 Khuyến nghị thứ tự bắt đầu

**Day 1-3:** FOUND-01 (BE) + LEGAL-01 (BE+FE) — dọn contract trước
**Day 4-6:** REPL-01..04 (sau FOUND-01) + PAYOUT-01 (FE)
**Day 7-10:** REPL-05 + REPL-02 (lớn nhất) + FE-01 + I18N-02
**Day 11-15:** BUG-01..03 + QA-05 (BA viết handbook) + QA-01 (setup test)
**Day 16+:** QA-02 + BUG-04 + finalize handbook + buffer fix bug
