# vCreator Codebase Audit — 2026-04-26

Verify từng feature có thật trong codebase không. Tham chiếu để build feature checklist + estimate cho dự án Gen-Green PH.

**Codebase paths:**
- Backend Go: `accesstrade-projects/vcreator/backend/internal/` + `pkg/`
- Admin (UmiJS React): `accesstrade-projects/vcreator/admin/src/`
- Frontend creator: `accesstrade-projects/vcreator/frontend-green/src/`

## Status Legend
- ✅ EXISTS — code thực, có file path & function/route chính
- ⚠️ PARTIAL — có 1 phần (model có nhưng handler chưa wire, hoặc có route nhưng không hoạt động)
- ❌ NOT EXISTS — grep không thấy
- 🤔 UNCLEAR — code có liên quan nhưng không chắc thuộc feature này

---

## Audit Results

| # | Feature | Status | Evidence |
|---|---|---|---|
| 1 | Đăng ký creator (form họ tên/email/password) | ✅ | `pkg/public/handler/user.go: Create()`; route `POST /register` |
| 2 | Verify số điện thoại qua OTP | ✅ | `internal/service/otp.go: SendOTP() + VerifyOTP()` |
| 3 | Đăng nhập bằng Google OAuth | ✅ | `pkg/public/handler/user.go: LoginWithGoogle()`; route `POST /login-with-google` |
| 4 | Liên kết tài khoản TikTok | ✅ | `LoginWithTiktok()` + model `UserTiktokData` |
| 5 | Crawl content Facebook | ✅ | `pkg/public/router/schedule.go: GET /crawl-content-facebook` (scheduled job) |
| 6 | Crawl content Instagram | ❌ | `INSTAGRAM_IS_ENABLE=false`, không có route/handler |
| 7 | Profile cá nhân (form 2 bước) | ✅ | `Update() + CompleteProfile()`; FE `pages/account/` |
| 8 | Phân loại CBNV vs creator ngoài | ✅ | Model: `StaffStatus`, `EmployeeCode`, `StaffVerifiedAt`, workplace fields |
| 9 | Staff verification (employee registry) | ✅ | `pkg/admin/handler/employee_registry.go` (full import/match/apply pipeline) |
| 10 | eKYC liveness + ID OCR | ✅ | Model `EkycInfoData` + `SaveEkycInfo()` handler |
| 11 | Upload ảnh ID 2 mặt | ✅ | `CreateIdentification()` + model `IdentificationUser` |
| 12 | Liveness check (selfie video) | ✅ | Embedded trong `EkycInfoData` |
| 13 | TIN field (tax ID / MST) | ✅ | Contract có field `IdentificationNumber` |
| 14 | Đăng bài creator | ✅ | `pkg/public/handler/content.go: Create()`; route `POST /events/{id}/content` |
| 15 | Quản lý content (CRUD) | ✅ | `pkg/admin/handler/content.go` full CRUD |
| 16 | Hashtag rules theo campaign | ✅ | `internal/service/content.go: CheckHashTag()` |
| 17 | Resubmit rejected content | ⚠️ | Có status tracking nhưng KHÔNG có endpoint resubmit explicit |
| 18 | Event/Campaign management | ✅ | `pkg/admin/handler/event.go` full CRUD + model `EventRaw` |
| 19 | Đăng ký tham gia campaign | ⚠️ | Có browse/list/detail nhưng KHÔNG có endpoint "register/join" explicit |
| 20 | Tracking participation | ✅ | `internal/service/event.go` (46KB) + model `EventReward` |
| 21 | **Crawl content post-expiry (cron)** | ❌ | KHÔNG có cron post-expiry. Chỉ có active crawls |
| 22 | **Checklist auto-validate** | ❌ | KHÔNG có auto-validation logic |
| 23 | Admin force reject + reason | ✅ | `internal/service/content.go: RejectListContentByIds(reason)` |
| 24 | **Snapshot dữ liệu đối soát** | ⚠️ | Model `reconciliation.go` có nhưng snapshot mechanism unclear |
| 25 | Classification filter | ⚠️ | Có `AccountType` + admin filter nhưng KHÔNG có explicit classification service |
| 26 | **Fractional reward by statistic** | ❌ | EventReward chỉ flat reward, KHÔNG fractional |
| 27 | Bank account binding | ✅ | `CreateUserBankCard() + UpdateUserBankCard()` + model `UserBankCardRaw` |
| 28 | E-wallet binding | ❌ | KHÔNG có e-wallet model/handler |
| 29 | Withdraw request | ✅ | `pkg/public/handler/withdraw.go: Create()` + model `WithdrawRaw` |
| 30 | QR payment (VietQR/napas247) | ❌ | KHÔNG có integration |
| 31 | Bank reconciliation auto match (Sepay) | ❌ | KHÔNG có Sepay webhook. OpsHub webhook có nhưng khác |
| 32 | Cash flow log | ✅ | `internal/service/cashflow.go` + model `CashFlowRaw` |
| 33 | Payout schedule | ⚠️ | Transfer model có nhưng KHÔNG có schedule logic |
| 34 | Auto withhold tax (TNCN 10%) | ⚠️ | Constants `CashFlowActionTax`, field `TotalCashTax` có; auto-calc logic chưa verify |
| 35 | Tax refund flow | ⚠️ | Constant `CashFlowActionTaxRefund` + field `TotalCashRefundTax`; flow logic unclear |
| 36 | Hợp đồng điện tử HTML template | ✅ | `internal/constants/contract.go: ContractTemplate` (786 dòng) |
| 37 | Click-to-sign + OTP | ✅ | `UpsertContractInfo() + CreateEcontract()` + `OTPPurposeSignContractOnline` |
| 38 | Lưu contract PDF (Google Drive) | ⚠️ | File model có; integration GDrive trong env (`GOOGLE_DRIVE_FOLDER_ID`) nhưng wire chưa rõ |
| 39 | Contract revocation | ❌ | KHÔNG có revocation endpoint/logic |
| 40 | TOS / Privacy Policy display | ⚠️ | News/article system generic — có thể serve nhưng không có route TOS/PP riêng |
| 41 | Email transactional | ✅ | Module `internal/module/smtp/` |
| 42 | SMS OTP | ✅ | AccessTrade SMS với channel Zalo |
| 43 | Push notification (Firebase) | ✅ | `internal/service/notification.go: firebase.SendToListDevices()` |
| 44 | Telegram admin alert | ❌ | Module có nhưng KHÔNG có route alert wired |
| 45 | In-app notification | ✅ | `pkg/public/handler/notification.go` + model `NotificationRaw` |
| 46 | Dashboard analytics widgets | 🤔 | `admin/src/pages/dashboard/` có; số widget cụ thể cần inspect UI |
| 47 | Creator management (search) | ✅ | `pkg/admin/handler/user.go` user list/search; CCCD via `EmployeeCode` |
| 48 | Filter CBNV/Cơ sở (57 cơ sở Vin) | ✅ | Workplace model: `WorkplaceBrandCode`, `WorkplaceCompanyCode`, `WorkplaceUnitCode` |
| 49 | Content review (reject + reason) | ✅ | `pkg/admin/handler/content.go` review/reject |
| 50 | Export chọn cột | ✅ | `pkg/admin/handler/export.go: Export()` field selection |
| 51 | Hashtag cá nhân | ✅ | User model: `Hashtag` field |
| 52 | Tax report | ⚠️ | Frontend `pages/account/tax/` + backend tax fields; generation logic unclear |
| 53 | Bank reconciliation export | ⚠️ | Reconciliation model + export handler có |
| 54 | Quick action buttons | ✅ | `pkg/admin/handler/quick_action.go` + model `QuickActionRaw` |
| 55 | Audit log | ✅ | `pkg/admin/handler/audit.go` + model `AuditRaw` |
| 56 | Referral system | ✅ | User model `ReferralInfo` + handler `Referral()` |
| 57 | Reward referral | ⚠️ | Model có nhưng explicit reward logic chưa rõ |
| 58 | Scalef integration | ❌ | Không có (giống VinFast Creator legacy đã rebrand?) |
| 59 | Dual currency / multi-region | ❌ | Không có |
| 60 | Region filter | ⚠️ | Có Province + Country model, không có region filter routes |

---

## Summary

| Status | Count | Features |
|---|---:|---|
| ✅ EXISTS | 32 | 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 23, 27, 29, 32, 36, 37, 41, 42, 43, 45, 47, 48, 49, 50, 51, 54, 55, 56 |
| ⚠️ PARTIAL | 17 | 17, 19, 24, 25, 33, 34, 35, 38, 40, 52, 53, 57, 60 |
| ❌ NOT EXISTS | 11 | **6, 21, 22, 26**, 28, 30, 31, 39, 44, 58, 59 |
| 🤔 UNCLEAR | 1 | 46 |

---

## KEY FINDINGS (Reconciliation v2/v3 NOT in vCreator)

User confirmed: **Crawl post-expiry, Checklist auto-validate, Snapshot reconciliation, Fractional reward — KHÔNG có ở vCreator.**

→ Reconciliation v2/v3 docs trong `docs/reconciliation-v2/` là **PRD cho techcombank** (Hệ thống Đối Soát V2 — *"Techcombank và nhiều PnL khác hiện tại không thể thực hiện đối soát được"*) — KHÔNG phải vCreator.

→ Các feature RECON-01, RECON-02, RECON-04, RECON-06 cần BỎ KHỎI scope hoặc đánh dấu "Không có ở source — sẽ không build".

---

## Other Features NOT in vCreator (cần xác định scope cho PH)

- **#28 E-Wallet** — chỉ có bank card. Nếu PH muốn GCash/Maya phải build mới (NHƯNG đã chốt bỏ Payment scope)
- **#30 QR payment** — chưa có VietQR/napas247
- **#31 Sepay reconciliation** — KHÔNG có. (Note: `docs/gen-green/scalef-integration` & meeting docs có thể nhắc Sepay nhưng vCreator codebase chưa wire)
- **#39 Contract revocation** — chỉ có sign, KHÔNG revoke
- **#44 Telegram admin alert** — module có nhưng chưa wire route nào
- **#58 Scalef integration** — không có trong vCreator. (Nhưng `docs/gen-green/` có PRD Scalef cho Gen-Green, có thể chưa implement)

---

## Cần verify thêm (PARTIAL)

1. **#34-35 Tax auto-withhold/refund** — có constants + fields nhưng calculation logic chưa rõ. Quan trọng vì Gen-Green PH đã chốt **bỏ Tax** → có thể bỏ bao gồm cả phần code partial này
2. **#38 Contract PDF Google Drive** — env có `GOOGLE_DRIVE_FOLDER_ID + GOOGLE_DRIVE_SERVICE_ACCOUNT` nhưng wire có thực sự lưu PDF lên Drive không?
3. **#19 Campaign register** — creator có thể tham gia campaign không? Có endpoint nào không?
4. **#46 Dashboard widget count** — claim 13 widgets cần verify thực tế trong admin UI
5. **#17 Resubmit rejected content** — có flow nào không? Hay creator phải tạo content mới?
