# Semantic Diff — Targeting & Matching Group

> **Generated**: 2026-05-07
> **Files trong scope**: `segment.go`, `registry_match.go`, `influencer.go`, `review.go`

| Service | TCB | vCreator | Ambassador |
|---|---:|---:|---:|
| segment.go | 81 LOC | ❌ | ❌ |
| registry_match.go | ❌ | **445 LOC** | ❌ |
| influencer.go | 332 LOC | ❌ | ❌ |
| review.go | 441 LOC | ❌ | ❌ |
| **Tổng** | 854 LOC | 445 LOC | 0 |

---

## TL;DR

Không có service nào shared cả 3 dự án. Mỗi service phục vụ 1 sản phẩm:

- **TCB**: 3 services (segment + influencer + review) — tập trung vào **influencer matching engine** + review system
- **vCreator**: 1 service (registry_match) — engine match employee từ HR registry, KHÁC HOÀN TOÀN TCB về mục đích
- **Ambassador**: 0 — không có concept matching/targeting trong service layer (logic nằm ở `affiliate.go` group khác)

→ Đây là group có **business model distinct nhất** giữa 3 sản phẩm. Không có khả năng port qua lại vì mục đích nghiệp vụ khác nhau.

---

## 1. `service/segment.go` (TCB-only, 81 LOC, 2 hàm)

### Hàm public

| Hàm | Mục đích |
|---|---|
| `CheckUserInSegmentWithReferralCode(userID, referralCode)` | Khi user đăng ký với referral code → tự động join các segment có config `applyType=referralCode` matching code đó |
| `UpdateStatistic(segmentID)` | Đếm lại số user trong segment, update `statistic.userTotal` |

### Logic
- Segment có `type=automatic` + `applyType=referralCode` → tự động assign user khi đăng ký bằng code matching.
- Tạo `UserSegmentRaw` records, set note "Automatic add to segment by referral code".
- Sau đó goroutine recompute statistic per segment.

### Ý nghĩa nghiệp vụ
TCB có **segmentation engine** cho marketing campaign:
- Marketer định nghĩa segment (vd: "user đăng ký từ HR campaign A" → referral code "HR-A")
- User register với code → tự động vào segment
- Sau đó campaign có thể target user trong segment (vd: gửi noti, hoặc filter eligible cho event)

→ Đặc trưng của TCB partner-bank model: nhiều campaign internal cho nhân viên/khách hàng, cần segmentation để target chính xác.

vCr/Amb có model `segment` + admin page `segment` → có UI nhưng **không có engine assignment**. Có thể manually add user vào segment qua admin (CRUD), không có auto-assign theo referral.

---

## 2. `service/registry_match.go` (vCreator-only, 445 LOC)

### Concept

Engine match **HR employee registry** vs **user data** (đăng ký từ frontend hoặc bulk import). Đây là feature **vCreator B2B**:
- HR import file CSV chứa employee code + phone + workplace (Brand/Company/Unit)
- User đăng ký với employee code + phone của họ
- Engine match: code+phone trùng → auto-verify; code match nhưng phone khác → mismatch (cancelled); code không có → no_match.

### ChangeAction enum (10 actions)

| Action | Ý nghĩa |
|---|---|
| `auto_verified` | code + phone khớp → tự verify user, set `staffStatus=verified` |
| `cancelled_mismatch` | code match nhưng phone không match (hoặc ngược lại) → reject với reason |
| `workplace_updated` | code + phone match nhưng workplace thay đổi → transfer user sang workplace mới |
| `missing_from_file` | registry có nhưng không có trong file mới → mark needs review |
| `new_record` | code chưa có trong registry → tạo mới |
| `no_match` | user khai code mà HR chưa import → để pending |
| `unchanged` | đã verified + workplace không đổi → no-op |
| `invalid` | row format invalid |
| `registry_updated` | HR đính chính cho code chưa có user claim → update theo file mới |

### Surface (3 hàm public)

| Hàm | Mục đích |
|---|---|
| `MatchEngine()` | factory |
| `GenerateChanges(rows, importID)` | bulk match cho admin import V2 — preview phase, sinh ChangeAction list cho admin review trước khi apply |
| `LookupSingle(code, phone)` | single lookup cho public register hook (FR-009) |

### Reason mapping

```go
ReasonCodeMismatch  = "code_mismatch"   // SĐT user/file khớp với mã NV khác trong HR data
ReasonPhoneMismatch = "phone_mismatch"  // Mã NV user/file khớp với SĐT khác trong HR data
```

`MapMismatchReason()` map key → Vietnamese text user-friendly. DB lưu key, UI map text → cho phép i18n flexibility tương lai.

### Ý nghĩa nghiệp vụ

vCreator phục vụ **B2B campaign cho doanh nghiệp**: company HR upload danh sách nhân viên, nhân viên đăng ký vào platform → match tự động với HR data → auto verify.

Workflow này KHÔNG TỒN TẠI ở TCB và Ambassador vì 2 sản phẩm kia không có B2B HR-driven onboarding. TCB cũng có concept "staff" nhưng dùng `PartnerInfluencerConfig` check (group User & Auth) — khác hẳn về cấu trúc.

→ Đây là **vCreator's killer feature** — không thể port sang 2 sản phẩm còn lại vì khác business model.

### Comment đáng chú ý
File header viết:
> "Trước đây nằm ở `pkg/admin/service` nhưng `pkg/public/service/user.go` cần dùng cho FR-009 register hook (Phase G.4). Move sang internal để tránh public import admin — vi phạm layer (admin có thể có dependency root staff/audit không phù hợp public)."

→ Có signal về **layer architecture** trong vCreator. Engine bị move từ admin → internal/shared để cả admin batch import + public register flow đều dùng được.

---

## 3. `service/influencer.go` (TCB-only, 332 LOC)

### Hàm public chính

| Hàm | Mục đích |
|---|---|
| `CheckStatusUserSocialWithConfig(partner, partnerInfluencerConfig)` | Re-evaluate tất cả pending user-social-partner records của 1 partner sau khi config thay đổi |
| (12 fns total) | Các utility cho influencer profile management |

### Logic chính

Khi admin TCB **cập nhật config auto-approve** của partner (vd: tăng min subscribers từ 1000 → 5000), service này:
1. Loop qua tất cả `UserSocialPartnerRaw` với status=pending hoặc pending_update của partner đó
2. Mỗi user-social, gọi `UserSocialPartnerImpl.CheckStatusUserSocialPartner` (group User & Auth) re-evaluate
3. Nếu status thay đổi → update record + trigger notification

→ Đây là **bulk re-evaluation engine** cho khi config thay đổi. Không có ở vCr/Amb vì:
- vCreator không có concept user_social_partner
- Ambassador có user_social_partner nhưng chưa có config check (xem comment "not yet ported" group User & Auth)

### Ý nghĩa nghiệp vụ
TCB partner thay đổi tiêu chí approve (vd: brand quyết định raise quality bar) → tất cả creator pending phải được re-evaluate ngay, không đợi admin manual approve từng người.

---

## 4. `service/review.go` (TCB-only, 441 LOC)

### Hàm public

| Hàm | Mục đích |
|---|---|
| `SubmitReview(req, userID, brandID)` | Brand/staff submit review cho 1 creator profile sau campaign |
| `GetReview(reviewID)` | Get 1 review |
| `ListReviews(profileID, page, limit)` | List reviews của 1 profile (paginated) |
| `EditReview(reviewID, req, userID)` | Edit review (nếu trong window cho phép) |

### Validation logic

- **Min 3/5 criteria rated**: phải rate ≥3 trong 5 tiêu chí (Content Quality, Professionalism, Communication, On-Time Delivery, Performance).
- Permission check: chỉ brand staff đã submit mới edit được.

### Liên kết với rating_aggregation

Sau khi submit/edit, `rating_aggregation.RecalculateProfileRating(profileID)` được trigger (xem group Analytics) → re-tính weighted rating cho profile.

### Ý nghĩa nghiệp vụ

TCB có hệ thống **review profile creator post-campaign**:
- Sau khi creator chạy 1 campaign cho TCB partner → brand staff có thể rate creator
- Rating tổng hợp lưu cache → hiển thị trên influencer profile + dùng filter discovery
- Đây là **trust layer** giữa brand và creator → giảm risk cho brand khi book lại

vCr/Amb không có concept này. vCr có review content (nội dung được duyệt/từ chối) nhưng KHÔNG review profile.

---

## 5. Models phát hiện thú vị

### TCB-specific models (target/match dùng)
- **`SegmentRaw`** + `UserSegmentRaw` — segmentation system (cũng có ở vCr/Amb như đã thấy ở matrix v2, nhưng KHÔNG có service)
- **`InfluencerProfileRaw`** — extended profile data riêng cho influencer (khác `UserRaw`)
- **`ProfileReview`** + `RatingCacheRaw` — review + cached aggregated rating
- **`PartnerInfluencerConfigRaw`** — config auto-approve per partner

### vCreator-specific models (registry-match)
- **`EmployeeRegistryRaw`** — HR registry imported per employee
- **`ImportHistoryRaw`** — track import batches (audit trail cho HR upload)
- **`ImportChangeRaw`** — preview changes (sinh từ `GenerateChanges`) → admin review trước khi apply

→ 2 sản phẩm này dùng **data structure HOÀN TOÀN khác nhau** cho khái niệm "user identity".

---

## 6. Câu hỏi business mở

1. **TCB segment dùng cho campaign nào?** Logic chỉ chạy với segment type=automatic + applyType=referralCode. Có manual segment (admin add user) hoạt động không?
2. **vCr `staffRejectReason` field** (đã thấy ở UserRaw group User) — chính là field mà registry_match set khi `cancelled_mismatch` action xảy ra. Confirm flow.
3. **TCB review system** — brand role có thật không? Hay dùng staff TCB review thay brand external?
4. **vCreator có `RegistryUpdated` action** — HR đính chính cho code chưa có user claim. Workflow này có hay xảy ra không, hay là edge case?
5. **TCB `InfluencerProfileRaw` vs `UserRaw`** — tại sao tách 2 model khác nhau? Performance hay business logic?

---

## 7. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Segment engine** | ✅ Auto-assign by referral code | ❌ (chỉ admin CRUD) | ❌ (chỉ admin CRUD) |
| **HR registry match** | ❌ | ✅ Bulk import + 10 ChangeActions | ❌ |
| **Influencer config re-evaluate** | ✅ Bulk recompute pending | ❌ | ❌ |
| **Profile review + rating** | ✅ 5-criteria + weighted aggregate | ❌ | ❌ |

**Đặc điểm group**:
- Không có service shared cả 3
- Mỗi service tied chặt với business model riêng → khả năng port qua lại = thấp
- TCB có 3 services hỗ trợ "trust + matching" cho creator economy
- vCreator có 1 service riêng phục vụ B2B HR onboarding

**Direction port nếu cần**:
- TCB → vCr/Amb: **review system** có thể useful cho brand-creator trust (effort medium ~441 LOC + models). Còn segment + influencer phụ thuộc vào TCB-specific business model nên không port được.
- vCreator → TCB/Amb: registry_match KHÔNG port được (phụ thuộc workplace 3-tier model của vCreator).
