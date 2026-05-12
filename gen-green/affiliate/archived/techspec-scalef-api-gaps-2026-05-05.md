# Tech Spec — VCreator × Scalef Affiliate Integration

> **Ngày:** 2026-05-05
> **Tác giả:** VCreator Tech Lead
> **Trạng thái:** Draft
> **Đối tượng:** VCreator BE/FE, Scalef API team, PM, QA
> **Liên quan:**
> - [scalef-api.md](./scalef-api.md) — Scalef API spec hiện có
> - [account-linking-overview.md](./account-linking-overview.md)
> - [fe-display-generate-link-report-overview.md](./fe-display-generate-link-report-overview.md)
> - [prd-account-linking-2026-05-04.md](./prd-account-linking-2026-05-04.md)
> - [prd-fe-creator-2026-05-04.md](./prd-fe-creator-2026-05-04.md)
> - Plan: [`plans/20260505-1332-affiliate-vcreator/`](../../plans/20260505-1332-affiliate-vcreator/)

---

## 1. Tổng quan

### 1.1 Mục tiêu

Tích hợp nền tảng affiliate **Scalef** vào **VCreator (Gen-Green)** để creator có nguồn thu nhập thứ 2 từ chia sẻ link sản phẩm + nhận hoa hồng.

**KPI mục tiêu:**
- 1.000 creator generate doanh thu affiliate
- 50 tỷ VNĐ doanh thu affiliate / năm
- 40% creator active tạo affiliate link trong 3 tháng đầu

### 1.2 Phạm vi (3 track)

| # | Track | PRD | Estimate |
|---|---|---|---|
| **P1** | Account Linking — OAuth SSO Scalef ↔ Gen-Green, identity matching, OTP, conflict resolution | [prd-account-linking-2026-05-04.md](./prd-account-linking-2026-05-04.md) | 12.5 ngày |
| **P2** | FE Creator V1 — Browse/Join campaign + Generate Link + My-links | [prd-fe-creator-2026-05-04.md](./prd-fe-creator-2026-05-04.md) | 7.5 ngày |
| **P3** | FE Creator V2 — Commission Report Dashboard | [prd-fe-creator-2026-05-04.md](./prd-fe-creator-2026-05-04.md) | 5 ngày |
| **PM** | Migration 1.000 publisher Scalef cũ | account-linking overview | 3 ngày |

**Tổng:** ~28 ngày (1 BE + 1 FE).

### 1.3 Nguyên tắc thiết kế

| Nguyên tắc | Áp dụng |
|---|---|
| **1-to-1** | 1 Gen-Green user ↔ 1 Scalef user, cứng |
| **CCCD = identity key** | Khác CCCD → reject (không cùng người) |
| **B2B sensitive data** | CCCD/SĐT/Email truyền backend-to-backend, browser chỉ thấy mã ngẫu nhiên |
| **Pending state resumable** | TTL 15 phút, user F5 quay lại resume từ bước dở |
| **OTP khi đổi data** | Update SĐT/Email phải qua OTP |
| **Auto-retry + circuit breaker** | Scalef API timeout → 3 lần retry, không kẹt user |
| **Audit trail** | Mọi lần link/unlink/conflict ghi vào `link_history` permanent |

### 1.4 Stack kỹ thuật

**Backend (`vcreator/backend`):**
- Go + Echo v4 + native MongoDB driver (no ORM)
- Pattern: `pkg/public/{domain}/{handler,service,dao}.go`
- Resty v2 cho external HTTP, golang-jwt v3.2.2, robfig/cron v3
- Reuse `internal/service/otp.go`, Redis cho TTL/rate-limit
- godotenv + go-envconfig

**Frontend (`vcreator/frontend-vcreator`):**
- UmiJS 3.5.20 (auto-routing) + DVA (Redux wrapper)
- Bootstrap 5.2.3 + SCSS (custom design system, NOT AntD-first)
- Formik + Yup, Umi `request` wrapper
- i18n: `src/locales/{key.ts, vi-VN.ts}`
- Toast: `src/components/app/toast/manager.tsx`

**Clone source:** `/Users/ltt251292/Desktop/Workspace/ambassador/frontend/src/pages/affiliate-*` (~1.586 LOC) — clone logic, rewrite UI sang Bootstrap+SCSS.

---

## 2. Kiến trúc tổng

```
┌─────────────────┐         ┌─────────────────────────┐         ┌─────────────────┐
│  VCreator FE    │  HTTPS  │     VCreator BE         │  HTTPS  │   Scalef        │
│  (UmiJS+DVA)    │ ──────> │  (Go + Echo + Mongo)    │ ──────> │  SSO + API      │
│                 │ Bearer  │                         │  HMAC   │                 │
└─────────────────┘         │  ┌──────────────────┐   │         └─────────────────┘
                            │  │ affiliate_link   │   │
                            │  │  (Phase 1)       │   │         Browser KHÔNG
                            │  ├──────────────────┤   │         truy cập trực tiếp
                            │  │ affiliate_creator│   │         Scalef (data sensitive)
                            │  │  (Phase 2,3)     │   │
                            │  └──────────────────┘   │
                            │  ┌──────────────────┐   │
                            │  │ Redis: pending,  │   │
                            │  │  rate-limit,     │   │
                            │  │  report cache    │   │
                            │  └──────────────────┘   │
                            └─────────────────────────┘
```

**2 BE domain mới:**
1. `pkg/public/affiliate_link/` — Account Linking (OAuth, matching, OTP, history)
2. `pkg/public/affiliate_creator/` — Proxy Scalef integration APIs (campaigns, links, reports)

**Lý do tách:** lifecycle khác nhau (Linking là one-time setup, Creator là daily use), bảo mật khác (Linking đụng CCCD, Creator chỉ proxy).

---

## 3. Phase 1 — Account Linking

### 3.1 User flow

**Kịch bản A (no conflict, ~30s):** Login → Consent → Done
**Kịch bản B (có conflict, ~2min):** Login → Consent → Confirm so khớp → Resolve (chọn data + OTP) → Done

5 màn UI:
1. **Login redirect** — bấm "Liên kết Scalef" trên Gen-Green → redirect SSO Scalef
2. **Consent** — màn hiện sau callback OAuth, list rõ field chia sẻ (Họ tên, CCCD, SĐT, Email)
3. **Confirm** — bảng so sánh từng trường, badge Khớp/Lệch/Bổ sung, CCCD masked 4 số cuối
4. **Resolve** — mỗi field lệch hiện 2 thẻ chọn (Gen-Green vs Scalef), OTP nếu chọn data Scalef
5. **Done** — profile hợp nhất + list campaign sẵn tham gia

**6 touchpoint trên Gen-Green** (đều dẫn về cùng flow):
- Login/Register page (SSO button)
- Settings → Tài khoản liên kết
- Tab Affiliate dashboard (banner)
- Event detail (banner)
- Popup chặn click "Tham gia chiến dịch" khi chưa link
- Popup chặn click "Tạo link" khi chưa link

**4 reject case** (→ auto-tạo support ticket, hẹn 3 ngày):
1. Gen-Green user đã link Scalef khác
2. Scalef user đã link Gen-Green khác
3. CCCD 2 bên khác nhau
4. SĐT/Email mới (sau khi user chọn) đã thuộc user khác

### 3.2 OAuth2 flow (Authorization Code)

Theo [scalef-api.md §0.4](./scalef-api.md):

```
Step 1  FE: bấm "Liên kết Scalef"
Step 2  BE: generate state random, lưu Redis TTL 15ph, response redirect URL
Step 3  Browser → https://sso.directsale.vn/oauth/authorize?client_id=...&state=...&redirect_uri=...
Step 4  User login Scalef
Step 5  Scalef redirect → https://gengreen.vn/scalef/callback?code=...&state=...
Step 6  BE verify state (chống CSRF), reject nếu không khớp
Step 7  BE → POST https://sso.directsale.vn/oauth/token
        grant_type=authorization_code, code=..., Authorization: Basic base64(client_id:secret)
Step 8  Scalef trả access_token + user_id + phone + email
Step 9  BE → GET /user/me → bổ sung CCCD + full_name (gap A1)
Step 10 BE chạy matching logic (§3.4)
```

### 3.3 Data model

**MongoDB collection mới:**

```js
// affiliate_link (1 doc / Gen-Green user đã link)
{
  _id: ObjectId,
  gengreen_user_id: ObjectId,       // unique index
  scalef_user_id: Int,               // unique index
  scalef_username: String,
  linked_at: ISODate,
  status: "active" | "suspended",
  link_method: "self" | "batch" | "admin",
  unified_profile: {                 // snapshot tại thời điểm link
    full_name: String,
    national_id: String,             // hash để search, plain encrypted at-rest
    phone: String,
    email: String
  }
}

// pending_scalef_link (TTL 15 phút, Redis hoặc Mongo TTL index)
{
  _id: ObjectId,
  gengreen_user_id: ObjectId,
  scalef_user_id: Int,
  step: "consent" | "confirm" | "resolve" | "otp_pending",
  oauth_state: String,
  scalef_token: String (encrypted),
  diff: { phone: { gg, sf, chosen }, email: {...} },
  otp_id: ObjectId,
  expires_at: ISODate,                // 15 phút sau create
  created_at: ISODate
}

// scalef_link_history (permanent audit)
{
  _id: ObjectId,
  gengreen_user_id: ObjectId,
  scalef_user_id: Int,
  action: "link" | "unlink" | "reject" | "conflict_resolved",
  reason: String,
  metadata: {...},
  actor: "user" | "admin" | "system",
  created_at: ISODate
}
```

**User collection (`internal/model/mg/user.go`) thêm:**

```go
ScalefUserID       *int64    `bson:"scalef_user_id,omitempty"`
ScalefUsername     *string   `bson:"scalef_username,omitempty"`
ScalefLinkedAt     *time.Time `bson:"scalef_linked_at,omitempty"`
NationalID         *string   `bson:"national_id,omitempty"`        // encrypted
NationalIDHash     *string   `bson:"national_id_hash,omitempty"`   // for search
NationalIDType     *string   `bson:"national_id_type,omitempty"`   // CCCD | CMND
NationalIDVerified bool      `bson:"national_id_verified"`
```

### 3.4 Matching logic

**Chuẩn hóa trước compare:**

| Field | Rule |
|---|---|
| CCCD | Bỏ ký tự không phải số. CMND 9 số → giữ nguyên, không pad. |
| SĐT | Convert về `+84xxxxxxxxx` (drop `0` đầu, prepend `+84`). Bỏ space/dash. |
| Email | Lowercase, trim. |
| Họ tên | **KHÔNG match** — chỉ hiển thị, không dùng làm key |

**Algorithm:**

```
1. Nếu cả 2 bên có CCCD:
     CCCD trùng → MATCH (continue)
     CCCD khác → REJECT (case 3, "không cùng người")
2. Nếu 1 bên thiếu CCCD (gap A1 fallback):
     SĐT + Email cùng trùng → MATCH
     Chỉ 1 trong 2 trùng → MATCH (warn admin)
     Cả 2 lệch → REJECT (CCCD null + SĐT/Email lệch)
3. Check 1-1:
     Gen-Green user đã có scalef_user_id khác → REJECT (case 1)
     Scalef user đã trong affiliate_link với gengreen_user_id khác → REJECT (case 2)
4. Detect diff:
     phone_gg ≠ phone_sf → diff["phone"]
     email_gg ≠ email_sf → diff["email"]
     1 bên trống → diff["{field}"].action = "fill" (auto, không cần user chọn)
5. Có diff cần user chọn → flow B (Resolve)
   Không diff hoặc chỉ "fill" → flow A (Done luôn)
```

### 3.5 OTP flow (khi user chọn data Scalef → update Gen-Green)

Reuse `internal/service/otp.go`:

```
1. User chọn "phone Scalef" tại màn Resolve
2. BE check phone Scalef chưa thuộc Gen-Green user khác (unique)
3. BE call OTP service: gửi 6 số đến phone Scalef
4. Rate limit 1 OTP/60s/target, max 5 lần sai → lock 15ph
5. User nhập OTP → BE verify → update User.Phone = phone_scalef
6. Sau khi tất cả conflict resolve xong → commit affiliate_link doc
```

### 3.6 BE API contract

**Gen-Green BE expose cho FE:**

| Method | Path | Mô tả |
|---|---|---|
| `POST` | `/api/affiliate/linking/initiate` | Tạo state + return redirect URL Scalef |
| `GET`  | `/api/affiliate/linking/callback?code&state` | OAuth callback, đổi token |
| `POST` | `/api/affiliate/linking/consent` | User confirm consent → run matching |
| `GET`  | `/api/affiliate/linking/compare` | Trả diff để FE render màn Confirm |
| `POST` | `/api/affiliate/linking/resolve` | Body: `{ field, source: "gg"\|"sf" }` → trigger OTP nếu cần |
| `POST` | `/api/affiliate/linking/otp/verify` | Body: `{ otp_id, code }` → update profile |
| `POST` | `/api/affiliate/linking/confirm` | Commit `affiliate_link` doc |
| `GET`  | `/api/affiliate/linking/status` | Check current user link status (đã link / pending / chưa) |

**BE proxy Scalef:**

| Method | Scalef Endpoint | Khi gọi |
|---|---|---|
| GET    | `/oauth/authorize` (browser redirect) | Step 3 OAuth |
| POST   | `/oauth/token` | Step 7 đổi code → token |
| GET    | `/user/me` | Step 9 lấy CCCD (gap A1) |
| POST   | `/api/v1/user/editUser` | Update profile 2 chiều (gap A2) |

### 3.7 Gaps Phase 1

#### 🔴 A1 — CCCD field trong user info

**Hiện trạng:** `/oauth/token` response trả `phone, email`, **không có** `national_id`. `/user/me` chưa có spec response.

**Đề xuất Scalef bổ sung `/user/me`:**

```json
{
  "user_id": 108,
  "user_name": "pub_4",
  "phone": "+84921234568",
  "email": "pub_4@example.com",
  "is_active": true,
  "national_id": "030199012345",      // ← THÊM
  "national_id_type": "CCCD",          // ← THÊM (CCCD | CMND | null)
  "full_name": "Nguyễn Văn A",         // ← THÊM
  "national_id_verified": true         // ← THÊM
}
```

**Workaround nếu Scalef không cấp:** Fallback matching SĐT+Email (degrade UX, có risk false positive). UX: thêm bước "Xác thực CCCD" sau OAuth ở Gen-Green.

---

#### 🔴 A2 — API update user profile (2 chiều)

**Hiện trạng:** [scalef-api.md §0.7](./scalef-api.md) liệt kê `POST /user/{action}` với `editUser`, **không có** request/response shape, không nói role User được edit field nào.

**Đề xuất:**

```http
POST https://<sso-domain>/api/v1/user/editUser
Authorization: Bearer {{user_access_token}}
Content-Type: application/json

{ "phone": "+84987654321", "email": "new@example.com" }
```

**Error codes cần đặc tả:**

| HTTP | Code | Khi nào |
|---|---|---|
| 400 | `INVALID_PHONE_FORMAT` | SĐT sai định dạng |
| 409 | `PHONE_ALREADY_USED` | SĐT đã thuộc user khác |
| 409 | `EMAIL_ALREADY_USED` | Email đã thuộc user khác |
| 422 | `KYC_LOCKED` | Field đã KYC, không cho user tự đổi |

**Workaround:** Phase 1 downgrade thành 1 chiều (Scalef → Gen-Green). User chọn data Gen-Green → chặn, hiển thị message "Vui lòng update Scalef trước".

---

#### 🟡 A3 — Check Scalef user đã link external client nào chưa

**Đề xuất:**

```http
GET /api/v1/user/{user_id}/external-links
```

**Workaround:** Gen-Green tự enforce 1-1 bằng unique index trên `affiliate_link.scalef_user_id`. Đủ dùng cho Gen-Green-only.

---

#### 🟡 A4 — Reverse linking entry (1K publisher cũ)

**Đề xuất:** VC chủ động batch import (xem §6 Migration). Không phụ thuộc Scalef UI.

---

#### 🟡 A5 — Re-sign ToS khi sync email/phone từ Scalef về Gen-Green

**Mức:** 🟡 Required (Legal/Compliance)
**Nghiệp vụ:** User đã ký Terms of Service Gen-Green với email/phone cũ. Sau khi link Scalef → ở màn Resolve user chọn data Scalef → email/phone Gen-Green bị overwrite. Câu hỏi pháp lý: **chữ ký ToS cũ còn hiệu lực không?**

**Phân tích:**

| Dữ liệu trong ToS | Có cần re-sign khi đổi không? |
|---|---|
| Họ tên + CCCD | ❌ Không đổi (CCCD = identity key, không bao giờ thay) |
| Email | ⚠️ Tùy — nếu ToS định danh user qua email (rare) → cần re-sign. Nếu chỉ dùng email làm liên lạc → không |
| SĐT | ⚠️ Tương tự email |
| Tax info / số tài khoản | 🔴 Có — đụng đến chi trả + thuế TNCN |

**Đề xuất xử lý:**

**Phương án 1 (Conservative — đề xuất):** Re-sign ToS bất cứ khi nào "thông tin định danh liên lạc" thay đổi
- Sau khi user verify OTP + commit profile mới → hiện màn "Xác nhận điều khoản với thông tin mới"
- User tick checkbox + bấm "Đồng ý" → tạo bản ghi `tos_signature` mới với version + new contact info
- Bản ghi cũ giữ lại trong audit (không xóa)
- ✅ Đảm bảo legal, có audit trail
- ❌ Thêm 1 bước UX (~10s)

**Phương án 2 (Lenient):** Chỉ re-sign khi ToS version đổi
- Email/phone là "contact info", không phải "identity" → ToS không cần ký lại
- Chỉ ký lại khi Gen-Green publish ToS version mới
- ✅ UX mượt
- ❌ Risk pháp lý nếu Legal yêu cầu strict tracking

**Phương án 3 (Hybrid):** Re-sign chỉ khi đổi field có ảnh hưởng pháp lý (tax email, billing phone)
- Phân loại field trong ToS: `contact_only` (re-confirm popup) vs `legal_binding` (re-sign full)
- Nếu chỉ đổi email login → popup confirm "Bạn đã đổi email, ToS giữ nguyên hiệu lực" + log
- Nếu đổi email nhận hợp đồng / hoá đơn → re-sign

**Câu hỏi cần Legal Gen-Green confirm:**
1. ToS hiện tại có điều khoản nào ràng buộc theo email/phone cụ thể không?
2. Email/phone trong ToS dùng để định danh hay chỉ liên lạc?
3. Tax info (cho TNCN) tách riêng khỏi ToS hay nhúng trong ToS?
4. Nếu user đổi email mà không re-sign → có rủi ro pháp lý gì với AccessTrade?
5. Quy định thuế TNCN có yêu cầu chữ ký mới khi đổi email/phone không?

**Đề xuất technical implementation (nếu chọn PA1 hoặc PA3):**

```js
// Bổ sung vào pending_scalef_link
{
  ...
  resolved_diff: {
    phone: { old: "+84xxx", new: "+84yyy", source: "scalef" },
    email: { old: "a@x.com", new: "b@y.com", source: "scalef" }
  },
  requires_tos_resign: true,    // ← computed từ resolved_diff
  tos_resigned_at: null,         // ← set sau khi user ký
  tos_version: "2026.04"
}

// User collection
{
  ...
  tos_signatures: [
    { version: "2026.01", signed_at: "...", contact: { email: "...", phone: "..." } },
    { version: "2026.04", signed_at: "...", contact: { email: "new@...", phone: "..." }, trigger: "scalef_link_sync" }
  ]
}
```

**FE flow bổ sung (giữa Resolve và Done):**

```
4. Resolve (chọn data + OTP)
   ↓
4.5. (NEW) ToS re-sign — chỉ hiện nếu requires_tos_resign=true
       - Hiện ToS với info mới highlighted
       - Checkbox "Tôi đồng ý điều khoản với thông tin cập nhật"
       - Bấm "Xác nhận" → POST /api/affiliate/linking/tos-resign
   ↓
5. Done
```

**BE endpoint mới:**

```http
POST /api/affiliate/linking/tos-resign
Body: { pending_link_id, tos_version, accepted: true }
→ Tạo bản ghi tos_signature mới + commit affiliate_link
```

**Workaround tạm:** Chọn PA2 (lenient) cho V1 launch — log warning trong audit trail "ToS not re-signed after contact change". Phase 2 implement đầy đủ sau khi Legal review.

---

#### 🔴 A6 — Ongoing sync sau khi đã link (post-link profile drift)

**Mức:** 🔴 Blocker (nghiệp vụ chưa định nghĩa)
**Nghiệp vụ:** **PRD và overview chỉ định nghĩa update 2 chiều TẠI thời điểm Linking (bước Resolve).** Không định nghĩa hành vi khi:

| Tình huống | Câu hỏi chưa trả lời |
|---|---|
| User đã link, vào Settings Gen-Green đổi SĐT | Có auto-sync sang Scalef không? Có cần OTP không? |
| User đã link, vào Settings Gen-Green đổi Email | Tương tự |
| User đổi SĐT/Email **bên Scalef** sau khi link | Gen-Green có biết không? Detect bằng gì (webhook? login check? cron)? |
| User đổi cả 2 bên, gây drift | Bên nào win? Last-write-wins? User chọn? |
| User đổi CCCD bên Scalef (rare) | CCCD = identity key → có invalidate link không? |

**Tác động:**
- Gen-Green có chính sách thuế TNCN — drift dữ liệu = sai chứng từ
- OTP cho update profile bên Gen-Green hiện đã có (`internal/service/otp.go`) — nhưng chưa biết trigger Scalef sync ở đâu
- Nếu không sync → 2 bên drift → reconciliation hell sau 6 tháng

**Đề xuất chính sách (cần PM + Legal confirm):**

**Phương án 1 (Strict 2-chiều, real-time):**
- User đổi SĐT/Email bên Gen-Green → OTP → commit local → call Scalef `editUser` (gap A2) → nếu fail rollback
- Ngược lại: user đổi bên Scalef → Scalef webhook → Gen-Green nhận → có thể require user re-confirm OTP nếu Gen-Green chưa lưu giá trị mới
- ✅ Data consistency cao
- ❌ Tight coupling, phụ thuộc Scalef API stability

**Phương án 2 (One-way master, Scalef = source of truth):**
- Scalef là master cho contact info của user đã link
- Gen-Green disable edit SĐT/Email trên Settings cho user đã link → hiện link "Cập nhật trên Scalef"
- Login check: mỗi lần user login, BE call `/user/me` Scalef so với local → khác thì update local + thông báo user
- ✅ Đơn giản, không saga
- ❌ UX: user khó chịu khi không edit được tại Gen-Green

**Phương án 3 (Detect-and-prompt):**
- Cho user đổi tự do bên Gen-Green (OTP nội bộ)
- Background cron mỗi 24h hoặc mỗi lần login → so contact info 2 bên → drift thì hiển thị banner "Thông tin Scalef khác Gen-Green, cập nhật?"
- User chọn merge data như flow Resolve gốc
- ✅ Linh hoạt, không block user
- ❌ Drift window có thể lên đến 24h

**Đề xuất:** **PA2 cho V1** (đơn giản, đảm bảo legal), **PA3 cho V2** (tốt UX hơn).

**Câu hỏi cần PM trả lời:**
1. Sau khi link, user có được edit SĐT/Email bên Gen-Green không?
2. Nếu có → có push sang Scalef không? Khi nào (real-time / batch)?
3. Drift check ở đâu: login? cron? on-demand?
4. CCCD đổi bên Scalef có invalidate link không? (re-link required?)
5. Conflict policy khi cả 2 bên cùng đổi: last-write-wins / Scalef-wins / Gen-Green-wins / user-chooses?

**Liên quan A5:** Mỗi lần sync contact info post-link cũng đụng vấn đề ToS re-sign tương tự.

**Technical impl đề xuất (PA3):**

```js
// Cron / login hook
async function checkContactDrift(userId) {
  const local = await User.findById(userId);
  if (!local.scalef_user_id) return;
  const scalef = await scalefAPI.userMe(local.scalef_token);
  const drift = diff(local, scalef);
  if (Object.keys(drift).length === 0) return;
  await Notification.create({
    user_id: userId,
    type: "scalef_profile_drift",
    payload: drift,
    cta: "/settings/account-linking/resolve-drift"
  });
}
```

```http
// Endpoint mới
GET  /api/affiliate/linking/drift-check       → trả diff hiện tại
POST /api/affiliate/linking/resolve-drift     → giống resolve gốc, có OTP nếu cần
```

**Workaround tạm V1:** Disable SĐT/Email edit cho user đã link Scalef. Hiển thị note "Liên hệ Scalef để cập nhật thông tin liên lạc". Không có cron drift detect → chấp nhận drift, fix sau khi Legal định chính sách.

---

## 4. Phase 2 — FE Creator V1

### 4.1 Tính năng

| # | Tính năng | UI | Endpoint |
|---|---|---|---|
| 1 | Section "Chiến dịch Affiliate liên kết" trong Event detail | Card grid 1col mobile / 2col desktop | `GET /campaigns?event_id=` |
| 2 | Trang chi tiết chiến dịch | 2 cột (banner + 3 badge / info + accordion Thể lệ/Hướng dẫn) | `GET /campaigns/{id}` |
| 3 | Tham gia chiến dịch | Nút → response APPROVED/PENDING/REJECTED | `POST /campaigns/join` |
| 4 | PENDING countdown 24h | Banner vàng + countdown | poll hoặc webhook |
| 5 | REJECTED countdown 14 ngày | Banner đỏ + countdown | — |
| 6 | Modal tạo link | Input URL sản phẩm (optional) → trả deeplink + short_link | `POST /campaigns/generate-link` |
| 7 | Trang `/affiliate-links` | Group theo campaign, search, filter, copy | `GET /publisher/links` (gap B2) |
| 8 | Touchpoint "Liên kết Scalef" 6 vị trí | Banner + popup chặn | — |

### 4.2 BE API contract

**Gen-Green BE expose cho FE** (proxy + middleware `RequireScalefLinked`):

| Method | Path | Mô tả |
|---|---|---|
| GET    | `/api/affiliate/campaigns` | List campaign affiliate (filter event_id) |
| GET    | `/api/affiliate/campaigns/:id` | Detail campaign + parse markdown thể lệ |
| POST   | `/api/affiliate/campaigns/:id/join` | Trả `{ status: APPROVED \| PENDING \| REJECTED, retry_at? }` |
| POST   | `/api/affiliate/campaigns/:id/generate-link` | Body `{ url?, utm_source?, sub_1? }` → trả `{ deeplink, short_link }` |
| GET    | `/api/affiliate/my-links` | List link đã tạo, group by campaign, search, paginate |

**Middleware:** mọi request kiểm tra `User.ScalefUserID != nil`, nếu không → response `403 SCALEF_NOT_LINKED` để FE hiện popup chặn.

### 4.3 Status mapping (gap B1)

`POST /campaigns/join` Scalef trả `{ status, publisher_status, advertiser_status }` (int).

**Mapping đề xuất Scalef confirm:**

| `status` | `publisher_status` | `advertiser_status` | Mapping FE |
|---|---|---|---|
| 1 | 1 | 1 | APPROVED |
| 0 | * | * | PENDING (24h countdown) |
| 1 | 0 | * | PENDING |
| 1 | 1 | 0 | PENDING |
| 2 | * | * | REJECTED (14 ngày countdown) |
| 3 | * | * | CANCELLED |

**Workaround:** Đoán mapping → kiểm thử sandbox → confirm.

### 4.4 Gaps Phase 2

#### 🔴 B1 — Mapping `status` int → enum

(xem §4.3 trên) — đang đoán, cần Scalef confirm.

---

#### 🔴 B2 — API list link đã tạo (`GET /publisher/links`)

**Đề xuất:**

```http
GET /api/integration/v1/publisher/links?campaign_id=&page=1&page_size=20&search=&from_date=&to_date=
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "links": [
      {
        "link_id": "lnk_abc123",
        "campaign_id": 229,
        "campaign_name": "Shopee Summer Sale",
        "deeplink": "https://pub.accesstrade.vn/...",
        "short_link": "https://at.link/xyz123",
        "utm_source": "facebook",
        "sub_1": "ad01",
        "created_at": "2026-04-15T09:44:09+0700",
        "click_count": 128,
        "order_count": 5
      }
    ],
    "meta": { "total": 45, "page": 1, "page_size": 20 }
  }
}
```

**Workaround V1:** Gen-Green tự lưu mỗi response `generate-link` vào collection `affiliate_links` local. ❌ Thiếu link tạo từ Scalef portal trước đó (legacy 1K publisher), ❌ thiếu click/order count.

---

#### 🟡 B3 — Webhook contract status change

**Đề xuất:**

```http
POST https://<gengreen-callback>/webhook/scalef/contract-status
X-Scalef-Signature: sha256={{hmac}}

{
  "event": "contract.status.changed",
  "data": {
    "contract_id": 5566,
    "old_status": 0, "new_status": 1,
    "reject_reason": null
  }
}
```

**Workaround:** Cron poll mỗi 5ph với contract đang PENDING (chỉ user active 24h).

---

## 5. Phase 3 — FE Creator V2 (Report)

### 5.1 Tính năng

Trang `/affiliate-commission`:

| Component | Detail |
|---|---|
| **3 KPI card** | Hoa hồng chờ duyệt / tạm duyệt / đã duyệt |
| **Filter thời gian** | Preset 7d / 1m / 3m / custom max 90 ngày |
| **Filter campaign** | Sidebar list campaign đã tham gia |
| **Table đơn hàng** | order_id, sản phẩm, sale_amount, commission, status, ngày |
| **Status badge** | pending/pre_approved/approved/rejected/hold (gap C2) |
| (V3) Chart conversion | Theo ngày, breakdown status |
| (V3) Click/order per link | Gap C1 |
| (V3) Export CSV | — |

### 5.2 BE API contract

| Method | Path | Mô tả | Cache |
|---|---|---|---|
| POST | `/api/affiliate/report/overview` | KPI tổng + chart data | Redis 5 phút |
| GET  | `/api/affiliate/report/conversions` | List đơn hàng, paginate | Redis 5 phút |
| POST | `/api/affiliate/report/click` | Compare 2 khoảng thời gian | Redis 15 phút |

### 5.3 Gaps Phase 3

#### 🟡 C1 — Click + order count **per link**

**Hiện trạng:** `/report/click` aggregate theo campaign, không break down theo `link_id`.

**Đề xuất:** Thêm `group_by: "link_id"` + `link_ids: [...]` vào body `/report/click`.

**Workaround:** Bỏ tính năng V2, đẩy V3.

---

#### 🟡 C2 — Enum `order_status` đầy đủ

**Hiện trạng:** [§3.7](./scalef-api.md) response có meta `{approved, pre_approved, pending, rejected, hold}` nhưng `hold` không có giải thích.

**Đề xuất Scalef cấp legend:**

| Status | Khi nào | Display |
|---|---|---|
| `pending` | Đơn vừa phát sinh, chưa verify | "Chờ duyệt" — vàng |
| `pre_approved` | Đã verify nguồn click | "Tạm duyệt" — xanh nhạt |
| `approved` | Advertiser duyệt | "Đã duyệt" — xanh |
| `rejected` | Advertiser từ chối | "Từ chối" — đỏ |
| `hold` | ??? | ??? |

---

#### 🟡 C3 — Report freshness SLA

**Câu hỏi:** Data trễ bao lâu? Có async aggregate ban đêm? → quyết định cache TTL.

---

## 6. Migration 1.000 publisher Scalef cũ

### 6.1 Strategy

| Tình huống | Cách xử lý |
|---|---|
| Đã có Gen-Green account (cùng CCCD/SĐT) | Tự link qua flow chuẩn (§3.1) |
| Chưa có Gen-Green | Admin batch tạo placeholder + magic-link email |
| Mâu thuẫn data | Admin review thủ công |

### 6.2 Admin tool flow

1. Admin upload CSV: `scalef_user_id, phone, email, national_id, full_name`
2. BE script:
   - Check Gen-Green có user trùng phone/email/CCCD chưa
   - Nếu chưa → tạo placeholder user, status `pending_set_password`
   - Tạo `affiliate_link` doc với `link_method: "batch"`
   - Generate magic-link token TTL 7 ngày
   - Gửi email "Bạn có tài khoản Scalef đã được mời sang Gen-Green, click để set password"
3. User click link → set password → done

### 6.3 Gap D3 — Bulk export publisher từ Scalef

**Đề xuất:** Scalef cấp CSV export hoặc endpoint `GET /admin/publishers/export` cho VC admin.

---

## 7. Bảo mật

| Vector | Mitigation |
|---|---|
| **CCCD lộ qua browser** | Browser chỉ thấy mã ngẫu nhiên (`pending_link._id`), data thật B2B |
| **CCCD at-rest** | Encrypt AES-256-GCM + lưu `national_id_hash` (SHA-256) cho search |
| **OAuth CSRF** | State random 32 byte, lưu Redis 15ph, verify match |
| **Authorization code replay** | Code chỉ dùng 1 lần (Scalef enforce) |
| **client_secret lộ** | Lưu `.env`, không commit; production rotate mỗi 6 tháng |
| **OTP brute-force** | Rate-limit 1/60s/target, max 5 sai → lock 15ph |
| **Pending link race** | Mongo unique index `(gengreen_user_id, scalef_user_id)` |
| **Webhook spoofing** | HMAC-SHA256 signature verify (header `X-Scalef-Signature`) |
| **Scalef API token leak** | Không log access_token, mask trong audit |

---

## 8. Non-functional

| NFR | Target |
|---|---|
| OAuth callback → Done page | p95 < 3s |
| `POST /campaigns/generate-link` | p95 < 1.5s |
| Report endpoint | p95 < 2s (cached 5ph) |
| Pending state TTL | 15 phút |
| OTP TTL | 5 phút |
| Concurrent linking flows | 100 đồng thời (Phase 1 day-1) |
| Scalef API timeout | 10s, retry 3 lần exponential backoff |
| Circuit breaker | Open sau 5 fail liên tiếp, half-open sau 30s |
| Rate limit Scalef (gap D4) | TBD |

---

## 9. Plan triển khai

| Phase | File | Effort |
|---|---|---|
| 1 | [phase-01-be-account-linking.md](../../plans/20260505-1332-affiliate-vcreator/phase-01-be-account-linking.md) | 5d BE |
| 2 | [phase-02-fe-account-linking.md](../../plans/20260505-1332-affiliate-vcreator/phase-02-fe-account-linking.md) | 5d FE |
| 3 | [phase-03-migration-publishers.md](../../plans/20260505-1332-affiliate-vcreator/phase-03-migration-publishers.md) | 3d |
| 4 | [phase-04-be-fe-creator-v1.md](../../plans/20260505-1332-affiliate-vcreator/phase-04-be-fe-creator-v1.md) | 3.5d BE |
| 5 | [phase-05-fe-fe-creator-v1.md](../../plans/20260505-1332-affiliate-vcreator/phase-05-fe-fe-creator-v1.md) | 4d FE |
| 6 | [phase-06-be-report.md](../../plans/20260505-1332-affiliate-vcreator/phase-06-be-report.md) | 2d BE |
| 7 | [phase-07-fe-report.md](../../plans/20260505-1332-affiliate-vcreator/phase-07-fe-report.md) | 3d FE |

Phase 1+2 song song (BE+FE), Phase 4+5 song song. Phase 3 chen vào sau Phase 1. Phase 6+7 cuối.

---

## 9.5 Additional Gaps (Edge cases / Integration / Ops / Security / UX) — E1–K6

> Phát hiện thêm sau khi audit toàn bộ docs lần 2. Nguồn: [`plans/.../reports/gap-audit-additional.md`](../../plans/20260505-1332-affiliate-vcreator/reports/gap-audit-additional.md).
> Tổng **47 gap mới**, format ngắn gọn — chi tiết workaround xem report nguồn.

### E. Edge cases nghiệp vụ (10 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| E1 | Multi-device session sau khi link (mobile link → web tab cũ chưa biết) | P1 | 🟡 | not mentioned |
| **E2** | **Scalef access_token expiry** (2.6h) — không có refresh strategy sau link | P1/P2 | 🔴 | scalef-api.md:108 |
| E3 | User suspended/deleted bên Scalef → Gen-Green xử lý sao? | P1/P2 | 🟡 | not mentioned |
| E4 | User deleted bên Gen-Green → Scalef link, hoa hồng pending về đâu? GDPR cascade | PM | 🟡 | not mentioned |
| E5 | GDPR / right-to-erasure vs audit log vĩnh viễn (NFR-006) | PM | 🟡 | not mentioned |
| E6 | Concurrent linking attempts (2 tab) — FE behavior chưa định nghĩa | P1 | 🟡 | PRD:1176 |
| E7 | User chưa verify email/phone Gen-Green → matching dùng gì? | P1 | 🟡 | not mentioned |
| E8 | Business / tổ chức account (MST thay vì CCCD) | P1 | 🟢 | not mentioned |
| E9 | Underage user (< 18) — chưa có CCCD, luật thuế TNCN yêu cầu 18+ | P1 | 🟡 | not mentioned |
| E10 | CMND 9 số ↔ CCCD 12 số mapping (cùng người, khác format) | P1 | 🟡 | PRD:223,1046 |

### F. Integration / data gaps (9 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| F1 | Timezone mismatch — Scalef trả `+0700` ISO + epoch ms, GG aggregate theo VN day hay UTC? | P2/P3 | 🟡 | scalef-api.md:514,593 |
| F2 | Pagination max page_size không cap → DoS risk | P2/P3 | 🟡 | scalef-api.md:567 |
| **F3** | **Idempotency key cho POST /join, /generate-link** (double-click → duplicate) | P2 | 🟡 | not mentioned |
| F4 | Retry policy 4xx vs 5xx granularity (401 token expired ≠ 429 rate limit ≠ 5xx) | P2 | 🟡 | NFR-004 |
| F5 | Error message i18n — Scalef trả tiếng gì? Không có error code dictionary | P2 | 🟢 | not mentioned |
| F6 | Avatar / display name sync giữa 2 bên | P1 | 🟢 | not mentioned |
| F7 | Tax info (TNCN) flow — ai issue chứng từ khi 1 user 2 nguồn thu? | PM | 🟡 | overview:27 |
| F8 | Withdrawal / payout flow — qua Scalef hay GG? Threshold? | P3 | 🟡 | PRD:926 (out of scope) |
| F9 | Currency hardcoded VND — multi-currency tương lai crash format | P3 | 🟢 | scalef-api.md:596 |

### G. Operational / observability (6 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| G1 | Monitoring metrics + SLO — không có Scalef p95/error_rate/OTP delivery | P1/P2 | 🟡 | not mentioned |
| G2 | Alerting thresholds — saga rollback rate? Scalef 5xx rate? | PM | 🟡 | NFR-003 |
| G3 | Audit log retention chi tiết — 150K user × N năm storage cost | PM | 🟢 | NFR-006 |
| **G4** | **PII masking trong Telegram auto-ticket** (FR-012 leak CCCD/SĐT?) | P1 | 🔴 | NFR-006:709, FR-012:439 |
| G5 | Backup / DR — pending Redis flush, history backup tần suất? | PM | 🟢 | not mentioned |
| G6 | Dispute resolution process — creator claim sai hoa hồng? | PM | 🟡 | not mentioned |

### H. Security (5 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| **H1** | **Scalef access_token storage location + rotation** (Redis vs DB, KMS, multi-instance share) | P1 | 🔴 | FR-002:148 |
| H2 | Webhook signature verification thuật toán + replay protection | P2 | 🟡 | PRD:924 |
| H3 | CORS policy cho API affiliate (mobile WebView whitelist) | P2 | 🟢 | not mentioned |
| **H4** | **Phishing risk** — user gen link với originalUrl trỏ malicious site | P2 | 🟡 | FR-005:238 |
| H5 | CSP cho affiliate pages — markdown desc từ Scalef có XSS không? | P2 | 🟢 | not mentioned |

### I. UX (5 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| I1 | Accessibility (a11y) cho 5-step linking — chưa có ARIA spec | P1 | 🟢 | NFR-008 chỉ FE Creator |
| I2 | Error recovery khi network drop giữa OTP — gửi lại tốn SMS | P1 | 🟡 | FR-013 |
| I3 | Empty states & skeletons — chưa systematic | P2 | 🟢 | FR-001/006 |
| I4 | i18n strings — toàn bộ hardcode tiếng Việt | P2 | 🟢 | not mentioned |
| I5 | Offline / poor network — copy link offline? Cache campaign list? | P2 | 🟢 | not mentioned |

### J. Phase 2 (FE Creator) edges (6 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| J1 | Campaign expired khi user đang xem detail → click Tham gia → reject | P2 | 🟡 | not mentioned |
| **J2** | **Link đã tạo cho campaign đã end** — còn track conversion? FR-006 không filter | P2 | 🟡 | not mentioned |
| J3 | Multi-link same campaign — không cap, spam DB risk | P2 | 🟢 | FR-005:243 |
| J4 | Sub-affiliate / MLM — out of scope nhưng cần document | Future | 🟢 | not mentioned |
| J5 | Saved / favorite campaigns — 100+ campaign khó tìm lại | P2 | 🟢 | not mentioned |
| J6 | Notification khi có conversion mới — push/email | P2/P3 | 🟡 | not mentioned |

### K. Phase 3 (Report) edges (6 gap)

| ID | Gap | Phase | Mức | Nguồn |
|---|---|---|---|---|
| K1 | VND format separator (`1,200,000₫` vs `1.200.000 đ` vs `1tr2`) | P3 | 🟢 | FR-009:369 |
| **K2** | **Hoa hồng retroactive change** (approved → rejected sau) → KPI confused | P3 | 🟡 | not mentioned |
| K3 | So sánh "tháng trước" — Scalef API hỗ trợ, FE không dùng | P3 | 🟢 | scalef-api.md:477 |
| K4 | Drill-down theo campaign trong commission | P3 | 🟢 | FR-009 |
| K5 | Export CSV format/encoding (UTF-8 BOM cho Excel VN) | P3 | 🟢 | PRD:382,922 |
| K6 | Time aggregation UTC vs VN+7 cho epoch buckets | P3 | 🟡 | scalef-api.md:469 |

### Tổng số gap mới: 47

| Mức | Count | IDs |
|---|---|---|
| 🔴 Blocker | 5 | E2, G4, H1, plus J2 mức cao của K2/F3 cần escalate |
| 🟡 Required | 22 | hầu hết E/F/G/I/J/K |
| 🟢 NTH | 20 | E8, F5/F6/F9, G3/G5, H3/H5, I1/I3-I5, J3-J5, K1/K3-K5 |

---

## 10. Tóm tắt Gap (cần Scalef phản hồi)

| ID | Tên | Phase | Mức | Block launch? |
|---|---|---|---|---|
| **A1** | CCCD field trong `/user/me` | P1 | 🔴 | Có (degrade matching) |
| **A2** | Spec `editUser` (update 2 chiều) | P1 | 🔴 | Có (downgrade 1 chiều) |
| **A3** | Check user external-links | P1 | 🟡 | Không (workaround DB) |
| **A4** | Reverse linking entry | PM | 🟡 | Không (workaround batch) |
| **A5** | Re-sign ToS khi sync email/phone | P1 | 🟡 | Tùy Legal (workaround log) |
| **A6** | Ongoing sync sau khi link (drift) | P1 | 🔴 | Có (cần PM define policy) |
| **B1** | Mapping `contract.status` int | P2 | 🔴 | Có (đoán → risk) |
| **B2** | `GET /publisher/links` | P2 | 🔴 | Có (workaround DB local) |
| **B3** | Webhook contract status | P2 | 🟡 | Không (poll) |
| **C1** | Click+order per link | P3 | 🟡 | Không (đẩy V3) |
| **C2** | Enum `order_status` (`hold`?) | P3 | 🟡 | Không (display "Khác") |
| **C3** | Report freshness SLA | P3 | 🟡 | Không (chọn TTL conservative) |
| **D1** | API leave campaign | Future | 🟢 | Không |
| **D2** | API revoke link | Future | 🟢 | Không |
| **D3** | Bulk export publisher | PM | 🟡 | Có (cho migration) |
| **D4** | Rate limit spec | NFR | 🟡 | Không (sizing conservative) |
| **D5** | Production credentials + URL | P1 D1 | 🔴 | **Day-1 blocker** |
| **E2** | Scalef token expiry / refresh sau link | P1/P2 | 🔴 | Có (cần document re-auth flow) |
| **G4** | PII masking trong Telegram auto-ticket | P1 | 🔴 | Có (compliance) |
| **H1** | Scalef token storage + rotation | P1 | 🔴 | Có (security) |
| **F3** | Idempotency key cho POST endpoints | P2 | 🟡 | Có (data integrity) |
| **H4** | Phishing risk via custom URL | P2 | 🟡 | Có (reputation) |
| **J2** | Link cho campaign đã end | P2 | 🟡 | Không (workaround flag) |
| **K2** | Retroactive commission change | P3 | 🟡 | Không (snapshot+changelog) |
| E1, E3-E10 | Edge cases nghiệp vụ (multi-device, suspended, GDPR, race, business, underage, CMND→CCCD) | P1/PM | 🟡/🟢 | Tùy case (xem §9.5) |
| F1, F2, F4-F9 | Integration (timezone, pagination, retry granularity, i18n, avatar, tax, payout, currency) | P2/P3/PM | 🟡/🟢 | Tùy case (xem §9.5) |
| G1-G3, G5-G6 | Operational (metrics, alerting, audit retention, DR, dispute) | PM | 🟡/🟢 | Tùy case (xem §9.5) |
| H2, H3, H5 | Security (webhook sig, CORS, CSP) | P2 | 🟡/🟢 | Có/Không (xem §9.5) |
| I1-I5 | UX (a11y, OTP recovery, empty states, i18n, offline) | P1/P2 | 🟡/🟢 | Không (polish) |
| J1, J3-J6 | Phase 2 edges (campaign expired, multi-link cap, MLM, favorites, noti) | P2/Future | 🟡/🟢 | Không (V2/Future) |
| K1, K3-K6 | Phase 3 edges (VND format, compare period, drill-down, CSV, timezone) | P3 | 🟡/🟢 | Không (polish/V3) |

---

## 11. Action items

| # | Item | Owner | Deadline |
|---|---|---|---|
| 1 | Gửi Scalef bộ câu hỏi 5 blocker (A1, A2, B1, B2, D5) | VC PM | 2026-05-06 |
| 2 | Call kickoff confirm A3, A4, B3, C1-C3, D3, D4 | VC TL + Scalef TL |
| 2.5 | Legal review A5 (re-sign ToS policy khi đổi contact info) | VC PM + Legal |
| 2.6 | PM define A6 policy (ongoing sync post-link) — chọn PA1/PA2/PA3 | VC PM | 2026-05-08 |
| 2.7 | Document E2 token refresh strategy (HMAC integration vs OAuth user-info) | VC TL | 2026-05-07 |
| 2.8 | Security review H1 (token storage) + G4 (Telegram PII masking) + H4 (URL allowlist) | VC TL + Security | 2026-05-09 |
| 2.9 | Design F3 idempotency contract cho POST /join, /generate-link | VC BE | 2026-05-09 |
| 2.10 | PM/Legal handle E4-E5 (deletion / GDPR) + E9 (underage) + F7 (TNCN flow) | VC PM + Legal | 2026-05-12 |
| 2.11 | UX team handle I1-I5 (a11y, OTP recovery, empty states, i18n, offline) | VC FE + Design | 2026-05-13 |
| 2.12 | Define G1-G2 monitoring + alerting thresholds | VC TL + DevOps | 2026-05-10 | 2026-05-08 |
| 3 | Scalef cập nhật `scalef-api.md` thêm enum + missing endpoints | Scalef | 2026-05-12 |
| 4 | VC khởi động Phase 1 BE (OAuth flow + matching SĐT/Email) | VC BE | 2026-05-06 |
| 5 | VC khởi động Phase 5 FE (clone Ambassador, mock API) | VC FE | 2026-05-06 |
| 6 | Re-evaluate plan sau khi nhận response Scalef | VC TL | 2026-05-13 |
| 7 | Production credentials handover + sandbox quota | Scalef Ops | 2026-05-14 |

---

## 12. Phụ lục — Quy ước trả lời gap

Khi Scalef phản hồi mỗi gap, format:

```
[ID] [Status: confirmed | will-build | wont-build | clarification-needed]
Response: <chi tiết>
ETA: <nếu sẽ build>
```

VD:

```
[A1] confirmed
Response: Field `national_id` đã có DB, sẽ thêm vào `/user/me` response.
ETA: 2026-05-15

[B1] clarification-needed
Response: Bảng mapping status sẽ gửi sau, hiện cần internal sync với Advertiser team.
ETA: 2026-05-10
```
