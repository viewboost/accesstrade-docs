# Semantic Diff — User & Auth Group (Prototype)

> **Generated**: 2026-05-07
> **Method**: Đọc 3 service files + 4 model files (~3500 LOC) ở 3 dự án, diff struct fields + business logic.
> **Mục đích**: Hiểu khác biệt **về mặt nghĩa** (không chỉ tên hàm/file). Đây là prototype cho 7 groups còn lại.

**Files trong scope**:
- `service/user.go` — divergent (TCB:663, vCr:453, Amb:510 LOC)
- `service/user_social.go` — divergent (TCB:347, vCr:85, Amb:338 LOC)
- `service/user_social_partner.go` — TCB+Amb only (vCr ❌); divergent (TCB:225, Amb:66)
- `service/otp.go` — **100% identical** (md5 match) → skip

**Models đọc cùng**: `user.go`, `user_social.go`, `user_social_partner.go`, `user_partner.go`

---

## Tóm tắt insight (TL;DR)

3 dự án có **cùng skeleton** (concurrent goroutines aggregate stats từ 5-6 collection: cashflow, event_reward, withdraw, user_partner, event_bonus). Khác biệt nằm ở:

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Khái niệm tổ chức** | (không có) | Workplace 3 cấp: Brand → Company → Unit + Employee onboarding workflow | Multi-partner (Anker/HDBank/...) + chương trình referrer |
| **Social platforms hỗ trợ** | TikTok, YouTube, Google, Facebook, Instagram | TikTok, Google, Facebook, Instagram | TikTok, Google, Facebook, YouTube, Instagram, **Threads, Shopee, Accesstrade, WildRift** |
| **Auto-approve influencer** | Có (`PartnerInfluencerConfig` + min subs/views/videos check) | Không | Stub đơn giản (mọi user-social → pending, không auto-approve) |
| **Notification on social status change** | Có (`SendNotificationInfluencerChangeStatus`) | Không | Chưa có (comment trong code: "not yet ported") |
| **Per-platform stats trong UserPartner** | Có (Facebook/Instagram/Tiktok subscribers/views/cash) | Không | Không |
| **EKYC chuyên dụng** | `IsEKYC` flag (boolean) | `EkycInfo` struct (19 fields chi tiết: card front/back, issue date, address...) | `IsEkyc` flag (boolean) + privacy consent |
| **Referrer tracking** | Không có | Không có | Có (`ReferrerInformation` 5 fields cho first VID commission) |
| **Số trường UserRaw** | 34 | **49** (nhiều nhất) | 38 |

**Pattern lớn**: vCreator được thiết kế cho **B2B onboarding** (workplace + employee + EKYC chi tiết), Ambassador cho **multi-platform creator economy** (nhiều social platform + referrer chain), TCB **gọn nhất ở User layer** nhưng có auto-approve influencer và notification flow.

---

## 1. `service/user.go` — Statistic aggregation

### Skeleton chung (cả 3 đều có)
Cả 3 dự án implement `UpdateStatistic` và `UpdateUserPartnerStatistic` dạng concurrent goroutines aggregate từ:
- `CashFlow.GetRemaining` / `GetPartnerRemaining`
- `EventRewardRaw` (TotalCashRewardByEvent)
- `WithdrawRaw` (TransferStatistic)
- `UserPartnerRaw` (list partner đã join)
- `EventBonusRaw` (TotalCashBonus)

3 dự án **đều update `partners` array** (list partner ID joined) trên UserRaw. Logic giống ~80%.

### Khác biệt về mặt nghĩa

**TCB**:
- Tracking thêm 4 field bonus: `TotalCashBonusPending/Rejected/Completed` + tách rõ pending = `TotalCashPending + TotalCashApproved`
- Trong `UpdateUserPartnerStatistic`: aggregate **per-platform stats** (Facebook/Instagram/Tiktok views + cash) + demographics (audienceAges, genders, topics, interactionTimes...) lưu vào `UserPartnerRaw.SocialSourceStats` và `UserPartnerRaw.Demographics`.
  - **Ý nghĩa nghiệp vụ**: TCB tracking creator performance per-platform per-partner, dùng cho dashboard analytics & influencer matching engine của TCB.
- Có thêm `User()` interface stub (3 hàm), không thêm fn lớn.

**vCreator**:
- Dùng `pfloat.RoundToOneDecimal` trên mọi cash field → tránh float precision issues khi lưu.
- KHÔNG track per-platform stats / demographics.
- **Ý nghĩa**: vCreator coi user statistic ở mức **tổng**, không phân tích sâu per-platform. Workflow đơn giản hơn TCB.

**Ambassador**:
- Hàm `UpdateUserPartnerStatistic` có thêm param `forceJoin bool` → cho phép **bắt buộc tạo joinedAt = now** khi user submit application (không cần đợi có content).
- Có `CheckUserIsFullFullProfile` (Ambassador-only): phone verified + email tồn tại → return bool. Dùng cho gate KYC trước khi join campaign.
- KHÔNG track per-platform stats / demographics chi tiết như TCB.

### Diff bảng nhanh `UserStatistic` model

| Field | TCB (24) | vCr (20) | Amb (21) |
|---|:---:|:---:|:---:|
| TotalCashBonusPending | ✅ | ❌ | ✅ |
| TotalCashBonusRejected | ✅ | ❌ | ❌ |
| TotalCashBonusCompleted | ✅ | ❌ | ❌ |
| TotalEventCashNotRejected | ✅ | ❌ | ❌ |

→ **TCB phân loại bonus chi tiết hơn** (pending/rejected/completed riêng từng tier), Ambassador chỉ có pending, vCreator không tách bonus.

---

## 2. `service/user_social.go` — Generate UserSocial record từ user data

### Skeleton chung
Hàm `GenerateUserSocial(user, source)` build 1 `UserSocialRaw` từ `UserRaw` dựa trên source platform. Cả 3 đều support TikTok, Google, Facebook, Instagram.

### Khác biệt về mặt nghĩa

**TCB**:
- Hỗ trợ 5 source: TikTok, **YouTube**, Google, Facebook, Instagram.
- Pass thêm `stats UserChannelStats` vào fn → lưu sẵn subscribers/views/videoCount khi tạo.
- Field `IsUseLogin: true` cho mọi platform → mọi social account đều có thể dùng để login.

**vCreator**:
- Chỉ 4 source: TikTok, Google, Facebook, Instagram (KHÔNG có YouTube).
- KHÔNG pass channel stats → social record tạo ra rỗng stats, phải enrich sau.
- File chỉ 85 LOC vì model `UserSocialRaw` của vCreator chỉ có 11 fields (so với TCB:21, Amb:23 fields). **Ý nghĩa**: vCreator dùng UserSocial chỉ cho login flow đơn giản, không tracking creator metrics.

**Ambassador**:
- Hỗ trợ 7 source: TikTok, Google, Facebook, YouTube, Instagram, **Threads**, **Shopee** (chưa thấy Accesstrade/WildRift trong fn này).
- Cho Facebook/YouTube/Threads/Shopee/Instagram: `IsUseLogin = false` → các platform này KHÔNG dùng login, chỉ link để display creator profile.
- TikTok và Google vẫn `IsUseLogin = true`.
- Field `LinkSocial` (URL profile) lưu trong UserSocialData → dùng cho admin verify link manually.
- **Ý nghĩa nghiệp vụ**: Ambassador coi social account là **portfolio creator** (link profile để brand đánh giá), không chỉ auth provider.

### Diff bảng `UserSocialRaw` model

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Stats (UserChannelStats) | ✅ | ❌ | ✅ |
| Demographics | ✅ | ❌ | ✅ |
| **EventApproval** (per-event approve flow) | ❌ | ❌ | ✅ |
| **PartnerApproval** (per-partner approve flow) | ❌ | ❌ | ✅ |
| OwnershipStatus / OwnershipMethod / OwnershipAt | ✅ | ❌ | ✅ |
| AtCoreJobID / AtCoreStatus / AtCoreSyncedAt | ✅ | ❌ | ✅ |
| IsPrimary | ✅ | ❌ | ✅ |
| IsEnriched | ✅ | ❌ | ✅ |

→ **vCreator's UserSocial là minimal** (chỉ login). TCB/Ambassador tracking sâu (ownership verification, at-core enrichment job, primary account flag).
→ **Ambassador unique**: per-event và per-partner approval lưu trực tiếp trong UserSocial (denormalized) → cho phép 1 social account đăng ký riêng từng event/partner.

---

## 3. `service/user_social_partner.go` — Map social account ↔ partner approval

### Existence
- TCB: 225 LOC (đầy đủ logic)
- Ambassador: 66 LOC (**comment trong code**: "simplified version of TCB's implementation")
- vCreator: ❌ KHÔNG có service và KHÔNG có model

### Khác biệt nghiệp vụ

**TCB** (file chính):
- `GenerateInfluencerWhenCreatePartner(partner)`: khi 1 partner mới được tạo, **bulk upsert UserSocialPartner records** cho mọi user-social hiện có với status=pending. Pagination 100 records/batch.
  - **Ý nghĩa**: Onboarding partner mới → tự động setup approval matrix với tất cả creator hiện hữu.
- `GenerateUserSocialPartner(userSocial, isNew)`: khi 1 social account mới được link → loop qua mọi partner, check `PartnerInfluencerConfig` (config auto-approve theo source: min subscribers, min videos, min views, **statusStaff required**).
  - Pre-fetch all configs → group by partnerID → O(1) lookup (anti N+1 optimization).
  - Nếu match config → approved. Nếu không match VÀ là Instagram/Facebook + isNew → status `PendingUpdate` (chờ user supply thêm thông tin).
  - Nếu approved → fire goroutine `Notification().SendNotificationInfluencerChangeStatus`.
- `CheckStatusUserSocialPartner(userSocial, config, partnerID)`: hàm core check rule → kiểm tra MinSubscribe / MinVideo / MinView / **StatusStaffRequired** (nếu config yêu cầu user phải là staff đã approve).
  - **Ý nghĩa**: TCB có khái niệm "creator được pre-approved nếu là nhân viên Techcombank đã verified" — `UserPartnerRaw.StatusStaff` được dùng làm điều kiện auto-approve.

**Ambassador** (stub):
- Chỉ có `GenerateUserSocialPartner`: tạo record mới với `status=Pending` cho mọi partner user thuộc về. **KHÔNG có config check, KHÔNG có notification, KHÔNG có status staff logic**.
- Comment trong code (line 21-26):
  > "This is a simplified version of TCB's implementation. TCB additionally checks PartnerInfluencerConfig auto-approve conditions (min subscribers/views/videos) and dispatches SendNotificationInfluencerChangeStatus notifications. Both are not yet ported to Ambassador (PartnerInfluencerConfig collection + Notification.SendNotificationInfluencerChangeStatus don't exist here). Records are created with StatusPending and the partner approval flow (SubmitApplicationPartner) handles approval."
- **Ý nghĩa**: Ambassador đang **chờ approval thủ công** qua `SubmitApplicationPartner` flow (handler riêng), chưa có auto-approve.

**vCreator**: Hoàn toàn không có concept này.
- Gắn user với partner thông qua `UserPartnerRaw` (đơn giản: user joined partner hay chưa).
- Không có matrix social-account × partner approval.

### Pattern lớn
TCB là **source of truth nghiệp vụ** cho user_social_partner. Ambassador đã port phần data (model identical 9 fields) nhưng chưa port logic. vCreator skip hoàn toàn. → Đây là feature **TCB-led**, có thể là target để port sang Ambassador trong tương lai.

---

## 4. Models phát hiện thú vị

### `UserRaw` — divergent nhất

**TCB-specific fields** (3): `StaffCode`, `CompanyCode`, `IsCreateByAdmin`, `ContractTOS` (UserContractTOS struct với 6 fields: UserSSOId, ContractId, UserBankVerified, Status, SignedAt, UpdatedAt).
- **Ý nghĩa**: TCB có quy trình staff onboarding nhẹ + ký contract TOS + verified bank trước khi sign. SSO integration với TCB.

**vCreator-specific** (15+ fields): `WorkplaceBrandCode`, `WorkplaceBrandName`, `WorkplaceCompanyCode`, `WorkplaceCompanyName`, `WorkplaceUnitCode`, `WorkplaceUnitName`, `EmployeeCode`, `StaffStatus`, `StaffVerifiedAt`, `StaffRejectReason`, `StaffRemovalScheduledAt`, `RegistPartner`, `AccountType`, `AT` (ATInfo: id, username), `EkycInfo` (19 fields chi tiết: card front/back, issue date, address, gender...), `ProfileCompletedAt`, `DismissCount`, `PhoneVerified`, `PhoneVerifiedAt`, `EmailVerified`, `EmailVerifiedAt`.
- **Ý nghĩa**: vCreator triển khai **3-tier organization model** (Brand → Company → Unit) với employee verification workflow đầy đủ (verified/rejected/scheduled removal). EKYC chi tiết hơn 2 dự án (lưu cả ảnh CCCD, issue date, address). Account type phân biệt staff vs partner registration.

**Ambassador-specific** (10+ fields): `Threads`, `Shopee`, `Accesstrade`, `WildRift` (gaming-specific), `ReferrerInfo` (5 fields tracking commission từ referrer chain), `GameInfo` (game integration), `IsEkyc`, `PrivacyAccepted`, `PrivacyAcceptedAt`.
- **Ý nghĩa**: Ambassador hỗ trợ **multi-platform creator** (kể cả gaming WildRift). Có hệ thống **referrer commission** (first video commission, 6-month commission tracking) → đây là affiliate-creator-pyramid kiểu MLM. GDPR-style privacy consent tracking.

### `UserPartnerRaw` — partnership shape

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| ID, Partner, Code, JoinedAt, IsJoined, User, Statistic, ContentStatistic | ✅ | ✅ | ✅ |
| **StatusStaff** | ✅ | ❌ | ❌ |
| **Demographics** (UserPartnerSocialDemographics) | ✅ | ❌ | ❌ |
| **SocialSourceStats** (per-platform subscribers/views/cash) | ✅ | ❌ | ❌ |
| **GameInfo** | ❌ | ❌ | ✅ |

→ TCB tracking **per-partner staff status + per-platform stats + demographics** = chuẩn bị cho influencer matching engine của TCB. Ambassador thêm GameInfo cho gaming campaigns. vCreator giữ minimal — không cần phân tích sâu per-partner.

### `UserSocialRaw` — biggest divergence

vCr: **11 fields, 53 LOC, 0 stats tracking** (chỉ login).
TCB: **21 fields, 179 LOC**, có Stats + Demographics + Ownership + AtCore enrichment.
Amb: **23 fields, 214 LOC**, giống TCB + thêm `EventApproval` + `PartnerApproval` (per-event/per-partner approval lưu denormalized).

→ Đây là **chỉ số rõ nhất** cho thấy 3 sản phẩm có business model khác biệt:
- vCreator: social = login provider
- TCB: social = creator profile + ownership verification + at-core enrichment job
- Ambassador: social = portfolio + per-event/per-partner approval matrix (denormalized cho query nhanh)

---

## 5. Câu hỏi business mở ra từ phân tích này

(Đây là những thứ tôi đoán cần PM/tech lead clarify, không phải kết luận chắc chắn)

1. **vCreator workplace 3-tier (Brand→Company→Unit)** có dùng thật không, hay là dead code copy từ feature cũ? (Codebase này có `staff.go` service riêng → có vẻ active.)
2. **Ambassador referrer commission** (ReferrerInformation, FirstVidCommissionID, 6-month tracking) — có phải MLM-style affiliate? Có liên quan đến `affiliate.go` service không?
3. **TCB `PartnerInfluencerConfig`** có status staff requirement → có nghĩa TCB cho phép "chỉ nhân viên đã verify mới được auto-approve làm influencer"? Confirm với business team.
4. **TCB không có YouTube** trong UserRaw direct (chỉ Tiktok/Google/Facebook/Instagram) nhưng `GenerateUserSocial` switch-case lại có YouTube → có thể có YouTube struct nằm chỗ khác hoặc là dead branch.
5. **Ambassador `UserSocialData.LinkSocial`** lưu URL profile để brand verify — có UI cho admin click vào không? Hay chỉ data dump?

---

## 6. Đánh giá methodology cho prototype này

### Effort thực tế
- Đọc 9 files code (~3500 LOC) + 4 model file: ~30 phút
- Diff tự động bằng Python script (struct fields): ~1 phút
- Synthesis viết doc này: ~20 phút
→ **Tổng ~50 phút cho 1 group nhẹ**.

### Output có dùng được không?
**Useful**:
- Phân biệt được "synced" (otp.go) vs "structurally similar nhưng business khác" (user.go).
- Trả lời được câu hỏi "TCB có gì mà 2 dự án kia không có" ở mức nghiệp vụ, không chỉ tên function.
- Phát hiện comment trong code chính xác là **smoking gun** cho semantic relationship (Ambassador's user_social_partner.go nói thẳng "simplified version of TCB").

**Limitations**:
- Methodology phụ thuộc vào việc đọc code → cần thời gian. Group lớn (Campaign & Event ~7K LOC) sẽ tốn 2-3h.
- Đoán business intent từ code có thể sai. Cần verify với PM/business team (xem section 5).
- Chưa cover frontend / admin pages → chỉ backend service + model.

### Đề xuất cho 7 group còn lại
- **Reconciliation, Analytics, Targeting**: TCB-only, ngắn → mỗi group ~30 phút.
- **Financial, Infrastructure**: medium ~1h.
- **Content & Media, Campaign & Event**: lớn ~2-3h mỗi group → cân nhắc spawn agent thay vì tôi đọc trực tiếp.
- **Format chung**: dùng cấu trúc của file này (TL;DR table → diff per file → models → câu hỏi business mở).

---

## Files referenced

- TCB: `accesstrade-projects/techcombank/backend/internal/service/{user,user_social,user_social_partner,otp}.go`
- vCreator: `accesstrade-projects/vcreator/backend/internal/service/{user,user_social,otp}.go`
- Ambassador: `accesstrade-projects/ambassabor/backend/internal/service/{user,user_social,user_social_partner,otp}.go`
- Models: `*/backend/internal/model/mg/{user,user_social,user_social_partner,user_partner}.go`
