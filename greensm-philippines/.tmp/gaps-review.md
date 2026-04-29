# Gaps Review — Pre-launch checklist

**Date:** 2026-04-29
**Method:** Reverse Brainstorming + Starbursting + Cross-check tasks vs audit

---

## 🔴 CRITICAL Gaps — phải fix trước launch

### 1. Third-party credentials & external services chưa setup cho PH

| Service | Env var | Issue |
|---|---|---|
| **Google OAuth** | `GOOGLE_CLIENT_ID` | App Indo dùng client riêng — PH cần đăng ký mới + verify domain `gen-green.ph` |
| **TikTok OAuth + Crawl** | `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` + `TIKTOK_REDIRECT_URI` | App Indo — PH cần đăng ký TikTok Developer App mới (region availability cần check) |
| **Facebook OAuth** | `FACEBOOK_CLIENT_ID` + `FACEBOOK_CLIENT_SECRET` | Có thể reuse hoặc đăng ký mới |
| **Instagram OAuth** | `INSTAGRAM_CLIENT_ID` + `INSTAGRAM_CLIENT_SECRET` + `INSTAGRAM_REDIRECT_URI` | Cần verify |
| **Firebase (Push Notification)** | `FIREBASE_PROJECT_ID` + `FIREBASE_CREDENTIALS` | Cần Firebase project mới cho PH (FCM tokens không cross-project) |
| **Google Drive** (contract PDF) | `GOOGLE_DRIVE_FOLDER_ID` + `GOOGLE_DRIVE_SERVICE_ACCOUNT` | Folder PH mới + service account mới |
| **content-catcher** (crawl service) | `CONTENT_CATCHER_BASE_URL` + `CONTENT_CATCHER_API_KEY` | Service riêng VN/Indo? Cần clarify provider có support PH không |
| **AccessTradeSMS** | `ACCESS_TRADE_SMS_*` | Service VN — KHÔNG dùng được cho PH → cần SMS provider PH thay thế |
| **reCAPTCHA v3** | `CAPTCHA_SECRET_KEY` + `CAPTCHA_END_POINT` | Site key mới cho domain `gen-green.ph` |
| **TOTP** | `TOTP_ISSUER` + `TOTP_APPLICATION_NAME` + `TOTP_PASS_PHRASE` | Update issuer cho PH |

→ **Tasks list THIẾU** explicit task setup từng third-party. SETUP-09 chỉ là Telegram. Cần thêm 7-8 setup tasks.

### 2. DB Migration script — chưa có task

- Schema currency `int VND` → `int centavos` (CONFIG-04 đã list nhưng không có migration script task riêng)
- Indexes mới cho PH-specific queries
- Migration data nếu seed từ Indo (hay fresh DB?)

→ **Cần thêm task MIGRATION-01/02** trong Phase 1 hoặc Phase 7.

### 3. Email transactional templates chưa rebrand

Tasks có I18N + Email template translation, nhưng **CHƯA có task explicit rebrand subject + sender + footer + signature** từ Indo → GreenSM PH.

→ Có thể merge vào BRAND-13 (email signature) nhưng nên tách riêng task.

### 4. Test data / seed data cho UAT

- Không có task seed creators/events/content sample cho UAT
- Partner UAT trống không có data thật để test

→ **Cần thêm task DATA-09 Seed UAT data**.

### 5. Monitoring + Alerting setup

- Source có Telegram alerts (RoomReconciliationID + RoomID) — config được
- Nhưng KHÔNG có task setup error tracking (Sentry/Datadog)
- KHÔNG có task setup health check + uptime monitoring
- KHÔNG có task setup log aggregation (CloudWatch?)

→ **Cần thêm task INFRA-MON-01/02**.

### 6. Backup + Restore strategy

- KHÔNG có task setup MongoDB backup schedule
- KHÔNG có task disaster recovery plan
- KHÔNG có task test restore

→ **Cần thêm task INFRA-BAK-01**.

### 7. Soft launch / Rollback plan

- Tasks có "Production deployment" (QA-15) nhưng không nói:
  - Soft launch với 10-20 creator pilot trước hay launch full?
  - Rollback plan nếu lỗi
  - Feature flag toggle để disable feature buggy

→ **Cần thêm task QA-17 Rollback plan + soft launch strategy**.

---

## 🟡 IMPORTANT Gaps — nên có

### 8. Right to access/erasure flow (DPA 2012)

- Audit-summary nhắc đến trong "Modules sạch business logic" mục cuối: "Right to access/erasure flow"
- Tasks list KHÔNG có task explicit
- Question I4 đã hỏi "Có cần?" — default Yes (BẮT BUỘC theo DPA)
- → 17h dev (đã ghi trong note question I4) nhưng chưa thêm vào tasks

→ **Cần thêm task COMP-NEW-01** (~17h) cho data export + delete account flow.

### 9. Admin documentation / training

- Admin GreenSM PH lần đầu dùng hệ thống — cần docs + training
- KHÔNG có task viết admin user guide

→ **Cần thêm task DOC-01**.

### 10. Performance baseline / load test

- KHÔNG có task load test
- Không biết hệ thống có chịu được spike khi launch campaign

→ **Cần thêm task QA-18 Load test** (optional P1).

### 11. Content samples cho UAT

- Cần partner cung cấp 5-10 content links thật để test crawl flow
- Không có task list này trong DATA-INIT

### 12. Data residency check (DPA 2012)

- AWS Singapore region — DPA 2012 có yêu cầu data lưu trên đất PH không?
- Tasks không có audit/check item này
- Question chưa hỏi partner

→ **Add question C9 Data residency requirement**.

### 13. Content moderation rules theo luật PH

- Audit-05 mention luật quảng cáo Indonesia trong contract template
- PH có luật riêng (DOH cho health/cosmetics, FDA, etc.)
- Reconciliation checklist cần update theo luật PH?

→ **Add question I7 Content moderation rules PH**.

### 14. SMS rate limiting + abuse prevention

- Source có rate limit OTP 5/day (audit-user) — đủ chưa?
- SMS spam có thể tốn budget nhanh

→ Add task hardening SMS rate limit nếu cần.

### 15. Email deliverability check

- AWS SES Singapore → cần verify DKIM + SPF + DMARC
- Tasks SETUP-07 chỉ ghi "verify domain" — chưa explicit SPF/DMARC

→ Update SETUP-07 ghi rõ.

---

## 🟢 NICE-TO-HAVE Gaps

### 16. CHANGELOG + Release notes
### 17. Internal devops runbook
### 18. Customer support FAQ (creator-facing)
### 19. Analytics dashboard cho business team
### 20. A/B test framework cho future campaigns

---

## ❓ Open questions cần partner clarify (mới phát sinh)

| Code | Question | Why |
|---|---|---|
| **C9** | DPA 2012 có yêu cầu data residency PH không? | Quyết định AWS Singapore vs Manila region |
| **C10** | DPO cụ thể là ai (tên + contact)? | Cần điền vào privacy policy |
| **G7** | content-catcher service có support content PH không? | Crawl content PH có hoạt động không |
| **G8** | TikTok Developer App đăng ký mới hay reuse Indo? | Approval timeline (TikTok thường mất 5-10 ngày) |
| **G9** | Firebase project mới hay reuse? | Push notification |
| **H6** | Test data UAT — partner cung cấp 5-10 content links thật không? | UAT trống |
| **I7** | Content moderation rules theo luật PH? | Reconciliation checklist |
| **I8** | Soft launch (pilot 10-20 creator) hay hard launch toàn bộ? | Risk mitigation |
| **J4** | Critical bug fix SLA sau launch? | Support model |
| **K4** | Customer support team (ai trả lời ticket creator)? | Operational |

---

## 📊 Tasks cần ADD (tổng hợp)

| Task ID đề xuất | Description | Phase | Effort | Priority |
|---|---|---|---|---|
| **SETUP-10** Setup Google OAuth app PH | Đăng ký + verify domain | 1. Setup | 4h | P0 |
| **SETUP-11** Setup TikTok Developer App PH | Đăng ký app + KYB | 1. Setup | 8h | P0 |
| **SETUP-12** Setup Facebook + Instagram apps PH | Verify credentials | 1. Setup | 4h | P0 |
| **SETUP-13** Setup Firebase project PH | FCM mới | 1. Setup | 4h | P0 |
| **SETUP-14** Setup Google Drive folder PH + service account | Contract storage | 1. Setup | 2h | P0 |
| **SETUP-15** Setup reCAPTCHA v3 site key PH | Captcha cho gen-green.ph | 1. Setup | 2h | P0 |
| **SETUP-16** Setup TOTP issuer PH | Update env | 1. Setup | 1h | P0 |
| **SETUP-17** Verify content-catcher service support PH | Test crawl content PH | 1. Setup | 4h | P0 |
| **MIGRATION-01** DB migration script VND→centavos | Currency schema | 7. Data Init | 8h | P0 |
| **DATA-09** Seed UAT test data | 10 creators + 3 events + 20 content samples | 7. Data Init | 6h | P0 |
| **INFRA-MON-01** Setup Sentry / error tracking | Monitor errors | 1. Setup | 6h | P0 |
| **INFRA-MON-02** Setup CloudWatch + Telegram alerts | Health check + alert | 1. Setup | 4h | P0 |
| **INFRA-BAK-01** Setup MongoDB backup schedule | Daily backup + test restore | 1. Setup | 6h | P0 |
| **COMP-NEW-01** Build Right to access/erasure flow | DPA 2012 compliance | 4. Contract & Legal | 17h | P0 |
| **EMAIL-01** Rebrand all email templates GreenSM PH | Subject/sender/footer | 6. Branding | 6h | P0 |
| **DOC-01** Admin user guide PH | Markdown docs | 11. QA & Launch | 8h | P1 |
| **QA-17** Rollback + soft launch plan | Document strategy | 11. QA & Launch | 4h | P0 |
| **QA-18** Load test | Apache Bench / k6 | 11. QA & Launch | 8h | P1 |

**Tổng add:** ~102h (~13 person-days)

→ Tasks list mới sẽ là **672h + 102h = 774h ≈ 97 person-days**

---

## 🚨 Top 5 Insights — risks lớn nhất

### Insight 1: Third-party credentials có thể block launch
**Source:** Reverse brainstorm + Starbursting WHEN
**Impact:** HIGH
**Effort:** Tasks ~25h setup

10+ third-party services cần đăng ký mới cho PH. **TikTok Developer App approval thường mất 5-10 ngày** — phải submit ngay tuần 1.

→ **Action:** Partner submit ngay TikTok/Firebase/reCAPTCHA apps tuần này.

### Insight 2: DB migration thiếu task
**Source:** Cross-check audit
**Impact:** HIGH
**Effort:** 8h script + test

Currency schema đổi `int VND → int centavos` (×100) cần migration script + indexes. Tasks list miss explicit task này. Nếu không làm → bug currency display sai 100 lần.

→ **Action:** Add MIGRATION-01 vào Phase 7.

### Insight 3: UAT trống không có data thật
**Source:** Starbursting WHAT
**Impact:** HIGH
**Effort:** 6h seed

UAT cần test với content thật → cần partner cung cấp 10-20 content link TikTok/FB thật. Nếu không → UAT chỉ test UI form, miss bug crawl/reward calc.

→ **Action:** Add question H6 + task DATA-09.

### Insight 4: Compliance Right-to-access là legal requirement
**Source:** Audit + DPA 2012
**Impact:** HIGH
**Effort:** 17h dev

DPA 2012 BẮT BUỘC có flow user export data + delete account. Tasks list không có. Launch không có flow này = vi phạm DPA → phạt ₱5M.

→ **Action:** Add COMP-NEW-01.

### Insight 5: Soft launch / rollback plan thiếu
**Source:** Reverse brainstorm
**Impact:** MEDIUM
**Effort:** 4h plan

Production deploy direct với deadline 22/05 + 134 tasks → risk cao có bug. Cần soft launch pilot 10-20 creator trước hard launch.

→ **Action:** Add QA-17 + discuss với partner soft launch strategy.

---

## 📋 Action items

1. **Add 18 tasks mới** vào tasks.csv (102h)
2. **Add 10 questions mới** vào questions-for-partner.csv (C9, C10, G7-9, H6, I7-8, J4, K4)
3. **Update overview.md** — recompute total 774h ≈ 97 days
4. **Highlight TikTok Developer App** approval timeline urgent với partner
5. **Setup Telegram alert** ngay tuần 1 để detect bug sớm
