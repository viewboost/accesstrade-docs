# Road — GreenSM Philippines TODO List

> Danh sách task có thể làm ngay, loại Branding refactor (BRAND-01..02) + DevOps (SETUP-D01..03) + các task block bởi partner.

**Tổng:** 18 tasks, 329h | **Deadline:** 22/05/2026

## ✅ Đã xong

- [x] Setup local env: backend (3010/3011/3012) + admin FE (8000) + DB `vcreator-philippines` + captcha + TOTP + seed staff `vinhnguyen@diso.vn`
- [x] Symlink locales (backend + admin)

## ⏸ Deferred (skip lúc này)

- ~~Frontend creator (port 8002)~~ → **UNBLOCKED** (commit fix sass + node-sass)
- BRAND-01 design rebrand (96h) — đợi design final
- Filipino native review pass (~1h native speaker pass qua AI draft)

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

### PAYOUT-01: Ẩn payment / bank / withdraw / tax / KYC / FB-IG / OTP (28h) ✅ DONE

**Frontend Creator:** ✅ done (commit `35b15ec`)
- [x] Hide Withdraw button + Bank account page — route `/payment-info` commented out
- [x] Hide Tax declaration page — route `/tax-declaration` commented out
- [x] Hide KYC Identification + Connect Account — route `/connect-account` commented out
- [x] Hide Facebook + Instagram login buttons — already commented in source `modal-login.tsx`
- [x] Profile dropdown items `payment` / `accountLink` / `eContract` set `visible: false`
- [ ] Update label "Số dư có thể rút" → "Hoa hồng đã tích lũy" — string trong `bank/index.tsx`, route đã disable nên unreachable. Cần làm khi I18N-01 partner submit translation (handle qua locale key thay vì hardcode replace).

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

### LEGAL-01: Ẩn/xóa contract sign flow (16h) ✅ DONE

**Backend:**
- [x] Comment `/users/contract/info` (POST upsert info) — [pkg/public/router/user.go](accesstrade-projects/vcreator-philippines/backend/pkg/public/router/user.go)
- [x] Comment `/users/contract/estimate`
- [x] Comment `/users/contract/agree`
- [x] Comment `/users/contract/pre-signed` (sign OTP)
- [x] Skip `UploadContract` (Drive + MinIO upload PDF) — guard `if ContractTemplate == "" { return "", nil }` ở cả [admin](accesstrade-projects/vcreator-philippines/backend/pkg/admin/service/user.go#L156) + [public](accesstrade-projects/vcreator-philippines/backend/pkg/public/service/user.go#L666) services + GetContractEstimate
- [x] Empty `constants/contract.go` template (219 dòng Bahasa → 9 dòng stub) — [internal/constants/contract.go](accesstrade-projects/vcreator-philippines/backend/internal/constants/contract.go)

**Frontend Creator:** ✅ done (commit `35b15ec`)
- [x] Contract sign page + flow — route `/e-contract` commented out
- [x] Profile section "Hợp đồng" — menu item `eContract` `visible: false` trong profile dropdown

**Frontend Admin:**
- [x] Không có Contract management menu trong admin routes hiện tại — không cần action.

### PAYOUT-02: Verify Commission Export flow cho offline payout (4h) ✅ partial

- [x] Verify code path:
  - Admin Transfer page (`/transfer`) → tạo + approve batch (route `transfers(r)` giữ enable, menu admin FE giữ).
  - Export trigger: `DataExportTypeTransferUserCash` → `exportImpl.ExportTransferUserCash` ([pkg/admin/service/export_transfer_user_cash.go](accesstrade-projects/vcreator-philippines/backend/pkg/admin/service/export_transfer_user_cash.go)) → file Excel: index, userId, name, hashtag, eventId, totalView, total + per-event breakdown + tổng.
  - Locale keys: `ExportUserTransferCash*` ([internal/locale/export.go](accesstrade-projects/vcreator-philippines/backend/internal/locale/export.go)).
- [ ] End-to-end QA test (cần data): Admin chạy reconciliation → Approve → Export → import payroll. Đợi có dummy data + môi trường staging.

---

## ✅ Phase 3 — Replace hardcode (sau FOUND-01) — DONE (BE+admin FE; creator FE deferred)

### REPL-01: Replace +84 hardcode (5h, 12 chỗ)

- [x] `format/string.go:31, 70-71, 77` (PhoneNumberFormatFromPhone)
- [x] `model/mg/user.go:152` (search string)
- [x] `service/otp.go:108` (OTP send)
- [x] `public/service/user.go:113, 616` (contract)
- [x] `public/service/identification.go:83`
- [x] `public/service/schedule.go:413`
- [x] `admin/service/user.go:184`
- [x] Verify pass test sau khi replace

### REPL-02: Replace HCM timezone (36h, 91 chỗ)

**Refactor utility:**
- [x] `util/time.go` — refactor 15 HCM functions → Region functions
- [x] `util/ptime/parse.go`

**Public services callsite:**
- [x] `public/service/schedule.go`
- [x] `public/service/user.go`
- [x] `public/service/withdraw.go`
- [x] `public/service/identification.go`

**Admin services callsite:**
- [x] `admin/service/transfer.go`
- [x] `admin/service/reconciliation.go`
- [x] `admin/service/content.go`
- [x] `admin/service/event.go`
- [x] `admin/service/exports.go`
- [x] `admin/service/migration.go`
- [x] `admin/service/user.go`
- [x] `admin/service/schedule.go`

**Handlers:**
- [x] `admin/handler/event.go`

**Cleanup:**
- [x] Remove constant `timezoneHCM`

### REPL-03: Replace Vietnamese accent functions (6h, 38 chỗ)

- [x] `admin/service/reconciliation.go` (3 chỗ)
- [x] `admin/service/transfer.go` (2 chỗ)
- [x] `admin/service/event.go` (slug generators - 2 chỗ)
- [x] `admin/service/partner.go` (slug - 2 chỗ)
- [x] `admin/service/export.go` (filename - 2 chỗ)
- [x] `admin/service/common.go` (bank search)
- [x] `admin/model/request/notification.go`
- [x] `admin/model/request/article.go`
- [x] `admin/model/request/news.go`
- [x] `admin/model/request/segment.go`
- [x] `admin/model/request/tag.go`
- [x] `admin/server/initialize/dummy_db.go` (3 chỗ)
- [x] Verify search/sort vẫn work sau replace

### REPL-04: Replace constants + slug VN-specific (4h)

- [x] Move `RegexPhoneNumber` (line 40) → đọc từ ENV
- [x] Remove constant `timezoneHCM` (line 72)
- [x] Remove `PercentTaxIndonesia` + `PercentTaxVietNam` (line 226-227) → config-driven
- [x] Remove `ConvertSlugProvince` + `ConvertSlugProvinceFind` (ho-chi-minh ⇄ tp-ho-chi-minh logic)

### REPL-05: Replace VN error messages + Indonesia/VN-specific code (11h)

- [x] Vietnamese error messages → locale keys (3 chỗ):
  - [x] `public/service/identification.go:453`
  - [x] `public/service/schedule.go:739`
  - [x] `public/service/schedule.go:1775`
- [x] Remove hardcode `if typeBank != "indo"` (admin/common.go:150)
- [x] Refactor `BeneficiaryForVietinbank` field → generic (admin/common.go:182 + bank model)
- [x] Update tax cron firstMonth date (schedule.go:760) hardcode 2024-03-31 → ENV var

### FE-01: Replace FE hardcode (12h)

**Phone format:**
- [x] `frontend/src/configs/app.tsx:58` — phoneNumberPrefix `+84` → `+63`
- [x] `frontend/src/configs/form.ts:3` — phoneRegExp Indonesia → PH
- [x] `admin/src/utils/format.ts:69-70` — +84 hardcode

**Currency:**
- [x] `admin/src/utils/format.ts:112` — unit `VND` → `PHP`

**Default locale config:**
- [x] `frontend/config/config.ts` — `id-ID` → auto-detect
- [x] `admin/config/config.ts` — `id-ID` → auto-detect

**Tiếng Việt hardcode (~7 chỗ):**
- [x] `frontend/src/pages/bank/components/user-cards/index.tsx:107, 123`
- [x] `frontend/src/pages/account/management/index.tsx:64`
- [x] `frontend/src/pages/main-home/index.tsx:116`
- [x] `admin/src/utils/format.ts` comments
- [x] `admin/src/utils/upload.ts:38` error message
- [x] `frontend/src/utils/breadcrumb-utils.ts` (~10 comments)

**Cleanup:**
- [x] Verify `admin/format.ts` Vietnamese accent funcs còn cần không

---

## ✅ Phase 4 — Bug fixes (BE only) — DONE

### BUG-01: P0 Security bugs admin staff (9h) — BẮT BUỘC TRƯỚC LAUNCH

- [x] `staff.go:264` — `GetMe()` permission check (validate userID==tokenOwner OR isRoot)
- [x] `staff.go:339` — UpdateInfo isRoot escalation (block isRoot field từ user-controlled body)
- [x] `staff.go:325` — `$nin` syntax error (MongoDB syntax `$nin` → `$ne`)
- [x] `staff.go:214` — reCAPTCHA score validation (validate score threshold)

### BUG-02: Staff hardening (9h)

- [x] `staff.go:118` — Add TOTP rate limit (lock after N attempts)
- [x] `staff.go:207` — Normalize email lowercase trong login
- [x] `transfer_processing.go:56` — Fix transfer math.Max logic bug (filter inverted)

### BUG-03: Event + Content + Schedule logic bugs (25h)

**Event:**
- [x] `event.go:296-298` — GetList sort bug (boolean sort)
- [x] `event.go:574` — GetLeaderBoard sort (add SortInterface)
- [x] `event.go:314-319` — Commented schema time-window (decide enable/remove)

**Content & Schedule:**
- [x] `transcript.go:28, 38` — Loop return → continue
- [x] `referral.go:76` — Referral cash always 0 (populate value)
- [x] `news.go:38` — Fix typo "new" → "news"
- [x] `user.go:1797` — `isExistedEmail` incomplete (check tất cả email fields)
- [x] `reconciliation_running.go:304` — Reconciliation rollback on failure
- [x] `schedule.go:1408` — OOM protection `UpdateSearchStringContent` (pagination)

### BUG-04: Cleanup tech debt (7h, P2 — có thể defer)

- [x] `user.go:1639` — Add max recursion guard cho `GenerateCode`
- [x] `user.go:662` — Add PDF cleanup sau `UploadContract`
- [x] Cleanup withdraw dead code (route không wire)
- [x] Implement `event_reward` stub hoặc remove
- [x] Branch card feature decide — uncomment & fix HOẶC remove
- [x] Tax double-charge verify — code không crash khi rate=0

---

## ✅ Phase 5 — i18n infrastructure (admin FE) — DONE

### I18N-02: Language toggle UI + format date/number (~2h thực tế)

- [x] `SelectLang` đã wire sẵn từ source (RightContent header) — Umi-generated dropdown hardcode 3 keys
- [x] Add `fil-PH` vào dropdown — Umi auto-gen menu chỉ list en-US/id-ID/vi-VN, replace bằng custom `LangDropdown` component (4 options: en-US/fil-PH/vi-VN/id-ID) ở [admin/src/components/RightContent/index.tsx](accesstrade-projects/vcreator-philippines/admin/src/components/RightContent/index.tsx)
- [x] `src/locales/fil-PH.json` — copy từ en-US baseline (Filipino translation chờ partner — I18N-01)
- [x] Auto-detect browser language: Umi `locale.baseNavigator: true` ở [admin/config/config.ts](accesstrade-projects/vcreator-philippines/admin/config/config.ts#L23) — không cần code thêm
- [x] localStorage persist: Umi `locale.useLocalStorage: true` (cùng config) — key `umi_locale`, không cần code thêm
- [x] Date format DD/MM/YYYY: PH dùng cả DD/MM và MM/DD → giữ nguyên + TODO comment từ Phase 3 (đổi sau khi có spec rõ)
- [x] Number format: `cashValue`/`cashValuePositive` đã đọc `process.env.CASH_CURRENCY_STYLE='en-PH'` + `CASH_CURRENCY_UNIT='PHP'` từ Phase 3 FE-01 → `Intl.NumberFormat('en-PH','PHP')` tự ra `₱1,234.56`

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
| LEGAL-03 (11h) | ✅ AI dev draft seeded (TOS + Privacy + FAQ) qua `cmd/seed_articles` — IDs khớp FE constants. **Cần partner legal review trước production**. |
| I18N-01 (24h) | ~~Đợi partner cung cấp Filipino translation ~3,800 keys~~ → **AI-translated draft cho BE (346 keys) + admin FE (407 keys) đã ship**. Còn ~3,000 keys creator FE chờ unblock + native PH review pass.|
| DATA-01 (10h) | ✅ AI dev draft seeded (Welcome + About) qua `cmd/seed_articles` — `showOn: home_notice` + `home_list`. **Marketing review trước launch**. |

## 📌 Khuyến nghị thứ tự bắt đầu

**Day 1-3:** FOUND-01 (BE) + LEGAL-01 (BE+FE) — dọn contract trước
**Day 4-6:** REPL-01..04 (sau FOUND-01) + PAYOUT-01 (FE)
**Day 7-10:** REPL-05 + REPL-02 (lớn nhất) + FE-01 + I18N-02
**Day 11-15:** BUG-01..03 + QA-05 (BA viết handbook) + QA-01 (setup test)
**Day 16+:** QA-02 + BUG-04 + finalize handbook + buffer fix bug
