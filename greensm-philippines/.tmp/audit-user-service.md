# Audit: vCreator-philippines/backend/pkg/public/service/user.go

**Date:** 2026-04-29
**Source:** `accesstrade-projects/vcreator-philippines/backend/pkg/public/service/user.go` (1896 dòng)
**Phụ trợ:** `service/identification.go` (516 dòng) — vì user.go gọi sang
**Method:** Đọc body từng function, không tin tên/comment

---

## Tổng quan

Total functions audited: **39** (32 user.go + 7 identification.go)

**Verdict:** Source ID là code **port từ vCreator VN nhưng CHƯA hoàn chỉnh**. Nhiều VN leftover quan trọng còn sót.

---

## VN Leftover findings

### 🔴 CRITICAL: Phone code +84 hardcode

| File:Line | Function | Code |
|---|---|---|
| user.go:113 | AgreeTermAndCondition | `strings.ReplaceAll(user.Phone.Full, "+84", "0")` |
| user.go:616 | VerifyOTP | `strings.ReplaceAll(user.Phone.Full, "+84", "0")` |
| identification.go:83 | UpsertContractInfo | `strings.ReplaceAll(user.Phone.Full, "+84", "0")` |

→ 3 chỗ hardcode `+84` cần đổi sang `+63`.

### 🔴 CRITICAL: VN timezone (HCM) hardcode

| File:Line | Function | Code |
|---|---|---|
| user.go:107 | AgreeTermAndCondition | `util.TimeOfDayInHCM(time.Now())` |
| user.go:572 | GetContractEstimate | `util.TimeOfDayInHCM(time.Now())` |
| user.go:610 | VerifyOTP | `util.TimeOfDayInHCM(time.Now())` |
| user.go:675 | UploadContract | `util.TimeOfDayInHCM(time.Now())` |
| user.go:719-720 | RequestOTP | `util.TimeStartOfDayInHCM(...)` |

→ 5 chỗ dùng timezone HCM. PH = Manila timezone (UTC+8 — same as HCM may be coincidence, nhưng code semantics sai).

### 🟡 MEDIUM: Vietnamese text utilities

| File:Line | Function | Code |
|---|---|---|
| user.go:1208 | CreatePublisher | `format.NonAccentVietnamese(payload.Name)` |
| user.go:1222 | CreatePublisher | `format.NonAccentVietnamese(payload.Desc)` |

→ Util "NonAccentVietnamese" được dùng cho search indexing publisher PH — không sai chức năng nhưng tên function khó hiểu cho dev mới.

### 🟡 MEDIUM: VN date format constants

| File:Line | Function | Constant |
|---|---|---|
| user.go:117 | AgreeTermAndCondition | `constants.FormantTimeDDTexMMYYYY` |
| user.go:577 | GetContractEstimate | `constants.FormantTimeDDTexMMYYYY` |
| user.go:620 | VerifyOTP | `constants.FormantTimeDDTexMMYYYY` |
| user.go:675 | UploadContract | `constants.CustomerDDMMYYYY` |

→ Format `dd/MM/yyyy` (VN) vs `MM/dd/yyyy` (PH) — cần verify constants giá trị.

### 🟡 Vietnamese error message hardcode

| File:Line | Function | Message |
|---|---|---|
| identification.go:453 | CreateIdentification | `"Hủy bởi người dùng tạo mới 1 yêu cầu khác"` |

→ Không localize, hardcode tiếng Việt.

---

## Bug / Red flags

### 🔴 Branch card feature broken

3 functions có branch card logic bị **comment out**:

| Function | Lines commented |
|---|---|
| UpdateUserBankCard | 938-942, 957-962 |
| CreateUserBankCard | 1008-1012 |
| GetUserBankCard | 1105 (always returns BranchName="") |

→ Tính năng "chi nhánh ngân hàng" chưa hoàn chỉnh ở source ID. Field `BranchName` luôn empty.

→ **Impact PH:** Nếu PH cần branch card → phải uncomment + verify; nếu không cần (vì đã chốt bỏ Bank scope) → OK skip.

### 🔴 Email uniqueness check incomplete

| Function | Issue |
|---|---|
| isExistedEmail (user.go:1797) | Chỉ check `google.email` field — không check `email`, `info.email`, `facebook.email`, `tiktok.email` |

→ User có thể đăng ký trùng email qua các provider khác.

### 🟡 OTP hardcoded trong dev mode

```go
// user.go:712
code = "123456"  // if !prod
```

→ Dev OTP cố định. Bình thường OK nhưng cần đảm bảo `ENV` đúng ở production.

### 🟡 Comment mismatches (copy-paste leftover)

| File:Line | Comment | Thực tế |
|---|---|---|
| user.go:238 | "Find database by info google" | LoginWithInstagram (Instagram, không phải Google) |
| user.go:464 | "Get user info from google" | LoginWithFacebook |

→ Code chạy đúng, comment sai.

### 🟡 No recursion guard

| Function | Issue |
|---|---|
| GenerateCode (user.go:1639) | Recursive uniqueness check, không có max depth |

### 🟡 Silent error logging

| File:Line | Issue |
|---|---|
| user.go:1755 | `fmt.Println("Error RenewAccessToken : ", err)` |

→ Dùng fmt.Println thay logger.

### 🟡 PDF cleanup không có

| Function | Issue |
|---|---|
| UploadContract (user.go:662) | Generate PDF local rồi upload Drive + Minio, không thấy `os.Remove` cleanup file local |

→ Có thể leak disk space.

---

## Function inventory (39 functions)

### Auth flows (core)

| Function | Line | Tóm tắt |
|---|---|---|
| Register | 1547 | Email/password registration. Validate email/phone, hash password, create user, optional referral |
| LoginWithPassword | 1514 | Email + password → token |
| LoginWithGoogle | 1341 | Google OAuth → find/create user, check email conflicts, return token |
| LoginWithTiktok | 1238 | TikTok OAuth → find/create user, return token |
| LoginWithFacebook | 457 | FB OAuth → find/create user, return token |
| LoginWithInstagram | 204 | IG OAuth → find/create user, return token. **Có comment sai** |
| Logout | 1466 | Mark device token IsActive=false |
| DeviceToken | 1483 | Upsert device record (IP, model, UA, FCM token) |

### OTP flows

| Function | Line | Tóm tắt |
|---|---|---|
| RequestOTP | 699 | Rate limit 5/day, gen OTP, gửi qua AccessTrade. **Dev = 123456** |
| VerifyOTP | 586 | Verify OTP. **Chỉ handle SignContractOnline purpose**, các purpose khác return không action |

### Profile / User info

| Function | Line | Tóm tắt |
|---|---|---|
| GetMe | 1448 | Lấy profile đầy đủ via getMeByUser helper |
| Update | 1128 | Update name/email/gender/avatar/birthday |
| getMeByUser | 1697 | Build GetMeResponse: avatar + social + identification + contract + referral + notification count |

### Bank cards

| Function | Line | Tóm tắt | Status |
|---|---|---|---|
| GetUserBankCard | 1078 | List bank cards, branch lookup commented | ⚠️ branch field empty |
| CreateUserBankCard | 990 | Add new bank card | ⚠️ branch logic commented |
| UpdateUserBankCard | 893 | Update bank card | ⚠️ branch logic commented |
| ChangeDefaultUserBankCard | 848 | Set default card |  |

### Identification (KYC)

| Function | Line/File | Tóm tắt |
|---|---|---|
| CreateIdentification | 300/identification.go | Tạo KYC. Limit 3/24h prod (10min dev). **VN error message hardcode** |
| UpdateIdentification | 168/identification.go | Update KYC info |
| GetIdentificationMe | 757/user.go | Lấy KYC của user |
| getIdentificationResponse | 481/identification.go | Build response với photo presigned URL |

### Contract flow

| Function | Line | Tóm tắt | VN issue |
|---|---|---|---|
| UpsertContractInfo | 30/identification.go | Lưu thông tin contract (phone, ID, tax, bank). Upload ID photos lên Drive | ✅ +84 hardcode (line 83) |
| GetContractEstimate | 566/user.go | Generate HTML preview contract (chưa PDF) | ✅ TimeOfDayInHCM (line 572) |
| GetPreSignContract | 547/user.go | Trả URL Minio presigned 15min cho PDF contract | — |
| AgreeTermAndCondition | 93/user.go | Mark contract Status=Completed, upload PDF | ✅ +84 + HCM TZ |
| UploadContract | 662/user.go | Generate PDF từ HTML template, upload Drive + Minio | ✅ HCM TZ + missing cleanup |

→ **Phát hiện:** Source ID **CÓ econtract sign flow**, nhưng route `/econtract/create`, `/econtract/:id`, `/econtract/list` của VN bị bỏ. Thay bằng `/users/contract/agree` đơn giản hơn.

### Social linking

| Function | Line | Tóm tắt |
|---|---|---|
| LinkUserSocial | 295/user.go | Link FB/TikTok/Google/IG vào user. Validate duplicate |
| GetListUserSocial | 416/user.go | List social linked. Auto-renew expired tokens |

### Publisher mode

| Function | Line | Tóm tắt | VN issue |
|---|---|---|---|
| CreatePublisher | 1196/user.go | Upsert publisher (name, desc, channel) | ✅ NonAccentVietnamese |
| GetPublisher | 1175/user.go | Lấy publisher info |

### Cashflow

| Function | Line | Tóm tắt |
|---|---|---|
| GetCashFlow | 777/user.go | List cashflow với pagination |
| GetCashFlowAppResponse | 806/user.go | Convert raw → response. Map action+targetType → locale title |

### Referral

| Function | Line | Tóm tắt |
|---|---|---|
| Referral | 1654/user.go | Validate code + gọi InputReferralCode |
| GetUserInfoByReferralCode | 155/user.go | Tra cứu user theo referral code |
| enableReferral | 1685/user.go | Init referral struct cho new user |

### Helpers (internal)

| Function | Line |
|---|---|
| newUserFromBodyRegisterData | 1601 |
| newUserFromGoogleData | 1807 |
| newUserFromTiktokData | 1838 |
| newUserFromFacebookData | 1861 |
| newUserFromInstagramData | 1880 |
| generateCodeForUser | 1633 |
| GenerateCode | 1639 |
| GetHashTag | 1856 |
| isExistedEmail | 1797 |
| generateUserSocial | 1833 |
| CheckUserValid | 1065 |

---

## Đối với task list PH

### Tasks cần thêm/cập nhật

1. **CONFIG-PH-01** Replace `+84` → `+63` ở 3 chỗ hardcode (user.go:113, 616, identification.go:83) — S, 2h
2. **CONFIG-PH-02** Replace `TimeOfDayInHCM` / `TimeStartOfDayInHCM` ở 5 chỗ → Manila timezone (UTC+8) — S, 3h
3. **CONFIG-PH-03** Verify `FormantTimeDDTexMMYYYY` + `CustomerDDMMYYYY` constants → đổi sang format MM/dd/yyyy — S, 2h
4. **CONFIG-PH-04** Localize Vietnamese error message ở identification.go:453 — S, 1h
5. **BUG-PH-01** Decision: branch card feature — uncomment & fix HOẶC chốt bỏ luôn (đã bỏ Bank scope) → confirm chỉ ghi rõ trong code — S, 1h
6. **BUG-PH-02** Sửa email uniqueness check ở isExistedEmail (user.go:1797) — S, 3h
7. **BUG-PH-03** Sửa comment sai ở LoginWithInstagram + LoginWithFacebook — S, 30min
8. **BUG-PH-04** Add max depth recursion guard cho GenerateCode — S, 30min
9. **CLEANUP-PH-01** Add PDF cleanup sau upload trong UploadContract — S, 1h
10. **CLEANUP-PH-02** Remove dev OTP hardcode "123456" hoặc gate kỹ hơn — S, 30min

→ Total cleanup user module: **~14h**

### Tasks confirmed có trong source (không cần build mới)

- ✅ Register email/password
- ✅ Login phone/password + 4 OAuth providers (Google/TikTok/FB/IG)
- ✅ Profile CRUD
- ✅ Bank card CRUD (nhưng branch broken)
- ✅ Identification CRUD + upload photos
- ✅ Contract flow (UpsertContractInfo + estimate + agree + sign with OTP)
- ✅ Cashflow log
- ✅ Referral system
- ✅ Publisher mode
- ✅ Device token + push setup
- ✅ Social linking (link/unlink existing user)

### Tasks confirmed KHÔNG có trong source ID

- ❌ `/users/identification/image` (OCR ảnh ID) — VN có
- ❌ `/users/ekyc/sdk`, `/users/ekyc/save`, `/users/ekyc/check-condition` — eKYC SDK flow VN có
- ❌ `/users/link-account` — link AT account
- ❌ `/users/update-phone-number` — đổi số phone với OTP
- ❌ `/users/check-bank-account` — verify tên chủ TK với ngân hàng
- ❌ `/users/bank/list` — bank list endpoint
- ❌ `/users/complete-profile`, `/users/check-unique`, `/users/dismiss-profile-popup`
- ❌ `/users/profile/request-otp`, `/users/profile/verify-otp` — OTP riêng cho update profile
- ❌ `/users/econtract/create`, `/users/econtract/:id`, `/users/econtract/list` — flow econtract chi tiết VN
- ❌ Workplace + Employee Registry + Migration + OpsHub modules

→ Quyết định: với scope PH (đã bỏ Bank/Tax/Withdraw), **các missing này KHÔNG cần port** trừ khi partner xác nhận cần.
