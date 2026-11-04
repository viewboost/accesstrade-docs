# Technical Specification: MCN trên KOC Ambassador — Phase 1

**Date:** 2026-11-04
**Author:** Vinh Nguyễn
**Version:** 1.0
**Status:** Draft — chờ review
**PRD:** [prd-mcn-phase1-2026-11-04.md](./prd-mcn-phase1-2026-11-04.md)
**Repo:** `ambassador/` — `backend/` (Go, module `viewboost`, MongoDB), `frontend/` (UmiJS 3 + dva, SSR), `admin/` (Umi + antd 4, Ant Design Pro)

Mọi đường dẫn trong tài liệu tính từ gốc repo `ambassador/`. Số dòng đọc ngày 2026-11-04, có thể lệch vài dòng khi code đổi.

---

## 1. Tổng quan

### Nguyên tắc

1. **Vai MCN đến từ bảng quan hệ.** Không thêm `type`/`role`/`kind` lên `users`. User là tài khoản MCN khi có dòng `mcn-accounts` đang hoạt động trỏ tới user đó. KOL/KOC thuộc MCN khi có dòng `mcn-members` đang mở. Mọi chỗ cần biết "user này là gì với MCN" đều tra hai bảng này qua một service duy nhất (`internal/service/mcn.go`, mục 3).
2. **Không đổi nghĩa dữ liệu cũ.** Không đổi trạng thái kỳ đối soát, trạng thái đợt chi, các action dòng tiền hiện có. Người không liên quan MCN cho kết quả y như cũ.
3. **Snapshot ở dữ liệu đối soát.** Tỷ lệ và MCN của từng khoản được chụp lên `reconciliation-items` lúc Lấy danh sách; lúc Duyệt chỉ đọc snapshot. Màn hình Admin, MCN, KOL/KOC đều đọc cùng snapshot nên số luôn khớp.
4. **Một chỗ ghi tiền.** Mọi dòng tiền MCN ghi qua `CashFlow().AddCashFlow` như hiện nay, có khóa idempotent theo kỳ.

### 1.1 Hiện trạng code liên quan

| Phần | Vị trí | Ghi chú |
|---|---|---|
| User | `backend/internal/model/mg/user.go:19-58` | Không có trường vai trò. `IsEkyc` (:54), `Accesstrade` (:51, SSO id), `Statistic` (:27) |
| User–partner | `backend/internal/model/mg/user_partner.go:13-32` | Có `statistic.cashRemaining` theo partner |
| Vai trò chỉ có ở staff | `backend/internal/model/mg/staff.go:27,32` | `StaffRaw.Type`, `StaffRaw.Role` |
| Kỳ đối soát | `backend/internal/model/mg/reconciliation.go:18-29`, items `reconciliation_item.go:13-30` | Item type `content`/`milestone`/`bonus` |
| Máy trạng thái kỳ | `backend/pkg/admin/service/reconciliation.go:239,366-385` | `pending → processing → processed → running → completed`, `rejected` |
| Lấy danh sách | `backend/pkg/admin/service/reconciliation_processing.go:21-55` | Set `processed` ở :55 |
| Duyệt, cộng tiền | `backend/pkg/admin/service/reconciliation_running.go:36-112`, `runCashBack` :241-582 | Pool 50 goroutine theo user; `AddCashFlow` :513 |
| Sổ dòng tiền | `backend/internal/service/cashflow.go:58-84`, model `internal/model/mg/cash_flow.go:14-42` | Không transaction, insert bỏ qua lỗi |
| Action dòng tiền | `backend/internal/constants/cash_flow.go:4-26` | `ActionMustTaxReward` dùng để tính thu nhập chịu thuế theo tháng (`cashflow.go:120-140`) |
| Đợt chi | `backend/pkg/admin/service/transfer_processing.go:19-153` | Lọc SSO id (:49), hợp đồng `B2C_AMBASSADOR` SIGNED (:54-86), số dư (:96-105) |
| Thuế TNCN | `backend/internal/service/withdraw.go:136-139` | 10% khi `Cash >= MinTaxableRevenue` (5.000.000, `constants/cash_flow.go:12`) |
| Econtract, eKYC | `backend/pkg/public/service/user.go:2539-2680` | Proxy sang AT core `/econtract-service`, loại hợp đồng cứng `B2C_AMBASSADOR` (:2586). Không có webhook |
| Tra tên chủ TK | `backend/pkg/public/service/bank.go:60-81` | Proxy AT core `/uaa-service`, ngữ cảnh user |
| Upload file | `backend/pkg/file/service/file.go:203` `UploadFile` | Có service, **chưa có route** |
| Email | `backend/pkg/admin/service/staff_auth_mail.go:22-44` | Qua AT email API, cần template code do AT cấp |
| Thông báo | `backend/internal/service/notification.go:40` | `Notification().Push` |
| Đăng nhập Google | `backend/pkg/public/service/user.go:1681-1760` | Tìm user theo `google.id`; user mới mà email đã tồn tại → lỗi `CommonKeyEmailIsExisted` |
| Collections | `backend/internal/module/database/mongodb/collection.go` | Feature mới khai báo file riêng, tiền lệ `collection_partner_app_config.go` |
| Index | `backend/internal/module/database/mongodb/index.go:34,391-433` | `newIndex`, `newUniqIndex`, `process` |
| Transaction | `backend/internal/module/database/mongodb/transaction.go:28` | `TransactionDatabase().WithTransaction` |

### 1.2 Hệ quả từ hiện trạng

- **Không tạo sẵn user cho MCN lúc kích hoạt.** Đăng nhập Google tìm theo `google.id`; nếu đã có user mang email đó mà chưa có `google.id`, đăng nhập bị chặn vì "email đã tồn tại". Vì vậy kích hoạt chỉ tạo dòng `mcn-accounts` giữ **email**, user được gắn ở lần đăng nhập đầu (mục 3.3).
- **Không có tab Người nhận** ở Admin đối soát hiện nay. Tab này là mới (mục 8.3).
- **Web không có khung trang tài khoản có menu trái.** Trang Quản lý MCN cần layout riêng (mục 10.3).
- **Route `/:partner/` và `/:partner/:slug`** (`frontend/config/routes.ts:119-167`) sẽ nuốt `/mcn/...`. Route MCN phải khai báo trước dòng 119.
- **Sau đăng nhập web luôn chuyển `/tai-khoan`** (`frontend/src/components/layout/main/header/index.tsx:65-68`). Cần nhánh quay lại trang lời mời (mục 10.2).

---

## 2. Data model

Năm collection mới, khai báo trong `backend/internal/module/database/mongodb/collection_mcn.go`:

```go
const (
    CollectionMcn           = "mcns"
    CollectionMcnAccount    = "mcn-accounts"
    CollectionMcnDocument   = "mcn-documents"
    CollectionMcnInviteLink = "mcn-invite-links"
    CollectionMcnMember     = "mcn-members"
)
```

Model đặt ở `backend/internal/model/mg/mcn*.go`, DAO ở `backend/internal/module/database/mongodb/dao/mcn*.go`, theo khuôn `XxxDAO` / `XxxRaw` / `DbModelName()` hiện có.

### 2.1 `mcns` — hồ sơ MCN

```go
type McnRaw struct {
    ID           AppID     `bson:"_id"`
    Partner      AppID     `bson:"partner"`      // partner Ambassador (Q6 PRD)
    Name         string    `bson:"name"`         // tên pháp nhân
    TaxCode      string    `bson:"taxCode"`
    LoginEmail   string    `bson:"loginEmail"`   // lowercase, trim
    Address      string    `bson:"address,omitempty"`
    Representative string  `bson:"representative,omitempty"`
    Phone        string    `bson:"phone,omitempty"`
    Status       string    `bson:"status"`       // pending | active
    ActivatedAt  *time.Time `bson:"activatedAt,omitempty"`
    ActivatedBy  AppID     `bson:"activatedBy,omitempty"` // staff
    CreatedBy    AppID     `bson:"createdBy"`             // staff
    Statistic    McnStatistic `bson:"statistic"`         // totalMember, totalLink (cache)
    SearchString string    `bson:"searchString"`
    CreatedAt, UpdatedAt time.Time
}
```

Index: `uniq(taxCode)`, `uniq(loginEmail)`, `(status, -createdAt)`, `(searchString)`.

### 2.2 `mcn-accounts` — tài khoản đăng nhập của MCN (bảng quan hệ)

Đây là chỗ duy nhất quyết định user có vai MCN.

```go
type McnAccountRaw struct {
    ID        AppID      `bson:"_id"`
    Mcn       AppID      `bson:"mcn"`
    Email     string     `bson:"email"`            // email được mời, lowercase
    User      *AppID     `bson:"user,omitempty"`   // nil cho tới lần đăng nhập đầu
    Role      string     `bson:"role"`             // owner (phase 1 chỉ có owner)
    Status    string     `bson:"status"`           // invited | active | inactive
    BoundAt   *time.Time `bson:"boundAt,omitempty"`
    CreatedBy AppID      `bson:"createdBy"`
    CreatedAt, UpdatedAt time.Time
}
```

Index:
- `uniq(user)` partial `{user: {$exists: true}}` — một user là tài khoản của tối đa một MCN.
- `uniq(email)` partial `{status: "invited"}`.
- `(mcn, status)`.

Phase 1 mỗi MCN một dòng `owner`. Cấu trúc đã cho phép nhiều tài khoản/MCN về sau mà không đổi schema.

### 2.3 `mcn-documents` — hồ sơ pháp lý, có lịch sử

Mỗi lần cập nhật là **một dòng mới**; dòng hiện hành có `isCurrent: true`. Không update đè, không xóa.

```go
type McnDocumentRaw struct {
    ID         AppID      `bson:"_id"`
    Mcn        AppID      `bson:"mcn"`
    Kind       string     `bson:"kind"`  // kyb | contract | dpa | bank | policy
    IsCurrent  bool       `bson:"isCurrent"`
    File       *McnFile   `bson:"file,omitempty"`      // {fileId, name, size}
    SignedDate *time.Time `bson:"signedDate,omitempty"` // contract, dpa, policy
    Bank       *McnBank   `bson:"bank,omitempty"`
    CreatedBy  AppID      `bson:"createdBy"` // staff
    CreatedAt  time.Time  `bson:"createdAt"`
}

type McnBank struct {
    BankID         AppID  `bson:"bankId"`
    BankName       string `bson:"bankName"`
    AccountNumber  string `bson:"accountNumber"`
    HolderName     string `bson:"holderName"`      // tên tra được, hoặc Admin nhập khi không tra được
    Match          string `bson:"match"`           // ok | mismatch | unverified
    MismatchReason string `bson:"mismatchReason,omitempty"` // bắt buộc khi match != ok
}
```

Index: `(mcn, kind, -createdAt)`, `uniq(mcn, kind)` partial `{isCurrent: true}`.

Ghi bản mới trong transaction: set `isCurrent=false` bản cũ → insert bản mới `isCurrent=true`.

### 2.4 `mcn-invite-links`

```go
type McnInviteLinkRaw struct {
    ID        AppID      `bson:"_id"`
    Mcn       AppID      `bson:"mcn"`
    Code      string     `bson:"code"`   // 8 ký tự [A-Z2-9], sinh ngẫu nhiên crypto/rand
    Rate      int        `bson:"rate"`   // 1..99
    Status    string     `bson:"status"` // active | off
    OffAt     *time.Time `bson:"offAt,omitempty"`
    CreatedBy AppID      `bson:"createdBy"` // user (tài khoản MCN)
    Statistic struct{ TotalJoined int `bson:"totalJoined"` } `bson:"statistic"`
    CreatedAt, UpdatedAt time.Time
}
```

Index: `uniq(code)`, `(mcn, -createdAt)`. Sinh mã trùng thì sinh lại (tối đa 5 lần).

### 2.5 `mcn-members` — KOL/KOC thuộc MCN (bảng quan hệ)

Một dòng cho một lần đi từ đồng ý tới kết thúc. Lần sau tham gia lại là dòng mới.

```go
type McnMemberRaw struct {
    ID     AppID  `bson:"_id"`
    Mcn    AppID  `bson:"mcn"`
    User   AppID  `bson:"user"`
    Link   AppID  `bson:"link"`
    Rate   int    `bson:"rate"`   // chép từ link lúc đồng ý, không đổi về sau
    Status string `bson:"status"` // agreed | active | leaving | ended | declined | sign_expired
    Open   bool   `bson:"open"`   // true khi status ∈ {agreed, active, leaving}

    AgreedAt       time.Time  `bson:"agreedAt"`
    SignDeadline   time.Time  `bson:"signDeadline"`   // agreedAt + 7 ngày
    ConsentShareAt *time.Time `bson:"consentShareAt,omitempty"`
    Annex          *McnAnnex  `bson:"annex,omitempty"` // {contractType, contractId, signLink, signedAt}
    StartAt        *time.Time `bson:"startAt,omitempty"` // = annex.signedAt
    EndAt          *time.Time `bson:"endAt,omitempty"`   // startAt + 12 tháng (Q7 PRD)
    LeaveNoticeAt  *time.Time `bson:"leaveNoticeAt,omitempty"`
    LeaveEffectiveAt *time.Time `bson:"leaveEffectiveAt,omitempty"` // 00:00 ngày (notice + 15)
    EndedAt        *time.Time `bson:"endedAt,omitempty"`
    EndReason      string     `bson:"endReason,omitempty"` // koc_leave | mcn_terminate | annex_expired

    History   []McnMemberEvent `bson:"history"` // {status, at, byType: user|mcn|system, by, note}
    CreatedAt, UpdatedAt time.Time
}
```

Index:
- `uniq(user)` partial `{open: true}` — **một KOL/KOC chỉ có một quan hệ đang mở** (D11, cũng chặn đồng ý hai lời mời cùng lúc). Dùng cờ `open` vì `partialFilterExpression` không nhận `$in`.
- `(mcn, status, -createdAt)`, `(status, signDeadline)`, `(status, leaveEffectiveAt)`.

Máy trạng thái:

```
agreed ──ký xong──► active ──báo rời──► leaving ──tới ngày──► ended (koc_leave)
  │                   ▲  ◄──rút lại──────┘
  ├─từ chối─► declined          active|leaving ──MCN chấm dứt──► ended (mcn_terminate)
  └─quá 7 ngày─► sign_expired
```

Mọi chuyển trạng thái dùng `UpdateOne` có điều kiện trạng thái nguồn trong filter (`{_id, status: <from>}`); `MatchedCount == 0` → trả `409 MCN_MEMBER_STATE_CHANGED`.

### 2.6 Thay đổi model hiện có

**`ReconciliationItemRaw`** (`backend/internal/model/mg/reconciliation_item.go`) thêm:

```go
Mcn *ReconciliationItemMcn `bson:"mcn,omitempty"`

type ReconciliationItemMcn struct {
    Mcn    AppID   `bson:"mcn"`
    Member AppID   `bson:"member"` // _id của mcn-members
    Rate   int     `bson:"rate"`
    Fee    float64 `bson:"fee"`    // math.Round(TotalCash * Rate / 100)
}
```

Index mới trên `reconciliation-items`: `(reconciliation, mcn.mcn)`.

**`CashFlowOptions`** (`backend/internal/model/mg/cash_flow.go:32-42`) thêm `Reconciliation AppID`, `Mcn AppID`, `McnFee float64` (phí đã trừ của khoản, chỉ để truy vết).

**Constants** — `backend/internal/constants/mcn.go` (mới):

```go
const (
    McnStatusPending = "pending"; McnStatusActive = "active"
    McnAccountInvited = "invited"; McnAccountActive = "active"
    McnMemberAgreed = "agreed"; McnMemberActive = "active"; McnMemberLeaving = "leaving"
    McnMemberEnded = "ended"; McnMemberDeclined = "declined"; McnMemberSignExpired = "sign_expired"
    McnRateMin = 1; McnRateMax = 99
    McnSignDays = 7; McnLeaveNoticeDays = 15; McnAnnexMonths = 12
    McnDocKyb = "kyb"; McnDocContract = "contract"; McnDocDpa = "dpa"; McnDocBank = "bank"; McnDocPolicy = "policy"
)
var McnRequiredDocs = []string{McnDocKyb, McnDocContract, McnDocDpa, McnDocBank, McnDocPolicy}
```

`backend/internal/constants/cash_flow.go` thêm action `mcn_fee` (category `mcn`). **Không** thêm vào `ActionMustTaxReward`.

---

## 3. Xác định vai MCN

### 3.1 Service

`backend/internal/service/mcn.go`:

```go
type McnInterface interface {
    AccountOf(ctx, user AppID) (*McnAccountRaw, *McnRaw)      // nil nếu không phải tài khoản MCN
    OpenMembershipOf(ctx, user AppID) *McnMemberRaw          // dòng open=true, nil nếu không có
    ActiveMemberAt(ctx, user AppID, at time.Time) *McnMemberRaw // active, hoặc leaving mà leaveEffectiveAt > at
    BindAccountOnLogin(ctx, user *UserRaw)                    // mục 3.3
    IsPayableMcnUser(ctx, user AppID, partner AppID) (*McnRaw, *McnDocumentRaw, bool) // mục 9
}
```

Kết quả `AccountOf` cache Redis 5 phút theo user, xóa cache khi bind/đổi trạng thái tài khoản.

### 3.2 Middleware public

`backend/pkg/public/router/routeauth/mcn.go`: `RequiredMcnAccount` — sau `RequiredLogin`, gọi `AccountOf`; không có hoặc MCN không `active` → `403 MCN_ACCOUNT_REQUIRED`. Đặt `mcn_id` vào context. Mọi API `/api/public/mcn/*` dùng `mcn_id` từ context, **không** nhận mcn id từ client.

### 3.3 Gắn user vào tài khoản MCN

`BindAccountOnLogin` được gọi ở cuối mọi luồng đăng nhập thành công (Google :1681, Facebook :636, mật khẩu :1925, TikTok :1500 — TikTok không có email nên không bao giờ khớp):

1. Lấy email đã xác thực của user (`google.email` của lần đăng nhập này, hoặc `info.email` khi `info.emailVerified`).
2. Tìm `mcn-accounts {email, status: invited}` của MCN `active`.
3. Có: trong transaction set `user`, `status: active`, `boundAt`; upsert `user-partners {user, partner: mcn.partner}` để đợt chi tìm được (mục 9). Lỗi index `uniq(user)` (user đã là tài khoản MCN khác) → log, bỏ qua.
4. User đang có quan hệ `mcn-members` mở thì **không** bind, gửi cảnh báo cho Admin (tài khoản MCN không được đồng thời là thành viên).

### 3.4 `/users/me`

`GET /users/me` (`frontend/src/configs/api.ts:67-70`) trả thêm:

```json
"mcn": { "role": "owner", "id": "...", "name": "Công ty ..." } | null,
"mcnMembership": { "status": "agreed|active|leaving", "mcnName": "...", "rate": 15 } | null
```

Frontend chỉ đọc hai trường này để hiện menu; quyền thật kiểm ở middleware.

---

## 4. Admin API

Router mới `backend/pkg/admin/router/mcn.go`, nhóm `e.Group("/mcns", a.RequiredLogin, a.IsAdmin)` (khuôn như `reconciliation.go:14-27`). Staff không root chỉ thấy MCN cùng `Partner` của mình (khuôn `Staff.Partner != rc.Partner`, `reconciliation.go:246`).

| Method | Path | Mô tả |
|---|---|---|
| GET | `/mcns` | Danh sách; query `status`, `keyword`, `page`, `limit` |
| POST | `/mcns` | Tạo (FR-002). Lỗi: `MCN_EMAIL_IN_USE` (email có ở `users.info.email`, `users.google.email`, hoặc `mcns.loginEmail`), `MCN_TAX_CODE_IN_USE` |
| GET | `/mcns/:id` | Chi tiết + trạng thái 5 điều kiện (`checks: [{kind, ok, current}]`) |
| PUT | `/mcns/:id` | Sửa thông tin hồ sơ (không sửa `loginEmail` sau khi kích hoạt) |
| POST | `/mcns/:id/documents` | Thêm bản mới cho `kind`. Body `{kind, fileId, signedDate}` hoặc `{kind: "bank", bankId, accountNumber, holderName, match, mismatchReason}` |
| GET | `/mcns/:id/documents/:kind` | Bản hiện hành + lịch sử |
| GET | `/mcns/:id/documents/:kind/:docId/download` | Presigned URL tải file (`minio.PresignedURLForDownload`) |
| POST | `/mcns/:id/bank/lookup` | `{bankId, accountNumber}` → `{holderName, match}` (mục 4.2) |
| POST | `/mcns/:id/activate` | FR-005. `422 MCN_ACTIVATION_INCOMPLETE {missing: [kind]}` |
| GET | `/mcns/:id/members` | Danh sách thành viên, chỉ đọc |

### 4.1 Upload hồ sơ

Route mới `POST /api/file/admin/document` trong `backend/pkg/file/router/file.go` (cạnh `/admin/photo` :17-20), gọi `File(bucket).UploadFile` (`pkg/file/service/file.go:203`). Bucket **riêng tư**; chỉ trả `fileId`, tải về qua presigned URL ngắn hạn. Chấp nhận `application/pdf`, ≤ 20MB (Q3 PRD).

### 4.2 Tra tên chủ tài khoản

`bank.go:60-81` đang gọi AT core `/uaa-service/.../user/payment-info/account-name` trong ngữ cảnh user có SSO. MCN không có SSO user. Cần AT core xác nhận gọi được bằng client credentials cho tài khoản công ty (phụ thuộc A3). Trong lúc chờ: `lookup` trả `match: unverified`, Admin nhập tên chủ tài khoản và lý do — form vẫn chạy được.

So khớp: `format.NonAccentVietnamese` + upper + gộp khoảng trắng, bỏ tiền tố `CONG TY`, `CTY`, `TNHH`, `CP`, `CO PHAN` ở cả hai vế, rồi so bằng.

### 4.3 Kích hoạt

Trong transaction:
1. Kiểm `McnRequiredDocs` đều có bản `isCurrent`; bản `bank` phải có `match=ok` hoặc `mismatchReason` khác rỗng.
2. Kiểm lại email chưa thuộc user nào (có thể đã có người đăng ký trong lúc chờ).
3. `mcns.status = active`, `activatedAt/By`.
4. Insert `mcn-accounts {mcn, email: loginEmail, role: owner, status: invited}`.
5. Sau commit: gửi email (mục 11), ghi audit.

---

## 5. Public API — MCN

Nhóm `e.Group("/mcn", a.RequiredLogin, a.RequiredMcnAccount)`, router `backend/pkg/public/router/mcn.go`.

| Method | Path | Mô tả |
|---|---|---|
| GET | `/mcn/me` | Hồ sơ MCN (tên, trạng thái, số thành viên) |
| GET | `/mcn/links` | Danh sách link |
| POST | `/mcn/links` | `{rate}` 1..99 → link mới. `400 MCN_RATE_INVALID` |
| POST | `/mcn/links/:id/off` | Tắt link (một chiều) |
| GET | `/mcn/invites` | `mcn-members` của MCN với status `agreed`, `declined`, `sign_expired` |
| GET | `/mcn/members` | `active`, `leaving`, `ended`. Dòng `ended`: chỉ trả tên, ngày, trạng thái, lý do |
| POST | `/mcn/members/:id/terminate` | `active|leaving → ended (mcn_terminate)` |
| GET | `/mcn/reconciliations` | Các kỳ `completed` có item `mcn.mcn = mcn_id` |
| GET | `/mcn/reconciliations/:id` | Từng thành viên: tỷ lệ, G, phí (aggregate trên `reconciliation-items`) |

Mọi truy vấn lọc `mcn = mcn_id` từ context. Dữ liệu thành viên trả cho MCN chỉ gồm tên hiển thị và avatar, không email/SĐT.

---

## 6. Public API — KOL/KOC

Router `backend/pkg/public/router/mcn_invite.go`.

| Method | Path | Login | Mô tả |
|---|---|---|---|
| GET | `/mcn-invites/:code` | Không bắt buộc | `{mcnName, rate, linkActive, viewer: {state}}`. `state` khi có login: `can_accept`, `in_other_mcn`, `already_member`, `is_mcn_account`, `pending_other_invite`, `pending_this_invite` |
| POST | `/mcn-invites/:code/agree` | Có | Body `{understood: true}`. Tạo `mcn-members` status `agreed`. Lỗi index `uniq(user)` partial → `409 MCN_ALREADY_IN_MCN` |
| POST | `/mcn-memberships/me/decline` | Có | `agreed → declined` |
| POST | `/mcn-memberships/me/sign` | Có | Body `{consentShare: true}`. Kiểm `users.is_ekyc` → `422 EKYC_REQUIRED`. Kiểm `signDeadline`. Gọi econtract (mục 7), trả `signLink` |
| POST | `/mcn-memberships/me/sync-sign` | Có | FE gọi khi người dùng quay về từ trang ký. Hỏi econtract, SIGNED → `active` |
| GET | `/mcn-memberships/me` | Có | Quan hệ đang mở + quan hệ gần nhất đã kết thúc |
| POST | `/mcn-memberships/me/leave` | Có | `active → leaving`, `leaveEffectiveAt = startOfDay(now + 15d)` (giờ VN) |
| POST | `/mcn-memberships/me/cancel-leave` | Có | `leaving → active`, chỉ khi `now < leaveEffectiveAt` |
| GET | `/users/reconciliations` | Có | Mọi creator: các kỳ `completed` có item của mình. Cột G, phí (`Σ mcn.fee`), cộng vào số dư |
| GET | `/users/reconciliations/:id` | Có | Chi tiết khoản của mình trong kỳ |

`agree` kiểm theo thứ tự: link `active` và MCN `active` → user không phải tài khoản MCN (`AccountOf`) → không có quan hệ mở. Tăng `mcn-invite-links.statistic.totalJoined` khi thành viên chuyển `active` (không phải lúc đồng ý).

---

## 7. Phụ lục trên hợp đồng điện tử

- Tái dùng client econtract hiện có (`backend/pkg/public/service/user.go:2578-2610`), tách hàm nhận `contractType` thay vì cứng `B2C_AMBASSADOR`.
- Loại hợp đồng mới, ví dụ `B2C_AMBASSADOR_MCN_ANNEX`, AT core phải cấp kèm mẫu có trường động: tên MCN, MST MCN, tỷ lệ, ngày bắt đầu, thời hạn 12 tháng (phụ thuộc A1). **Chặn FR-014 cho tới khi có.**
- Không có webhook ký: trạng thái lấy bằng `FindPubContract` (:2588) theo `contract_types=<annex>`:
  - `sync-sign` khi FE quay về;
  - job mỗi 15 phút cho các dòng `agreed` có `annex.contractId` (mục 12).
- Mỗi dòng `mcn-members` lưu `annex.contractId` để không nhầm với phụ lục của lần tham gia trước.
- Đợt chi KOL/KOC **không** đổi điều kiện: vẫn cần hợp đồng `B2C_AMBASSADOR` SIGNED như hiện nay. Phụ lục MCN không thay thế hợp đồng chính.

---

## 8. Đối soát

### 8.1 Snapshot lúc Lấy danh sách

Trong `Processing()` (`backend/pkg/admin/service/reconciliation_processing.go:21`), sau khi ba hàm `ProcessingMilestone/Content/Bonus` tạo xong item và **trước** khi set `processed` (:55), gọi `r.applyMcnSnapshot(ctx, rc)`:

1. Bỏ qua nếu `rc.Partner` không phải partner có MCN (Q6 PRD: chỉ Ambassador; cấu hình bằng `PartnerOpts.McnEnabled`).
2. Lấy danh sách user có item trong kỳ (distinct `user`, theo trang).
3. Với lô user, query `mcn-members {user: {$in}, status: {$in: [active, leaving]}}`, loại `leaving` có `leaveEffectiveAt <= now`, join `mcns.status = active`.
4. `BulkWrite` set `mcn = {mcn, member, rate, fee: math.Round(totalCash*rate/100)}` cho các item `pending` của những user đó.

Thời điểm xét là lúc Lấy danh sách (Q5 PRD). Từ đây tới lúc Duyệt, snapshot không đổi kể cả khi thành viên bị chấm dứt.

### 8.2 Cộng tiền lúc Duyệt

**KOL/KOC** — trong `runCashBack` (`reconciliation_running.go:256-266`), chỉ đổi giá trị payload:

```go
value := item.TotalCash
if item.Mcn != nil {
    value = item.TotalCash - item.Mcn.Fee
    // options.Mcn, options.McnFee để truy vết
}
payload := internalservice.CashFlowPayload{ ..., Value: value, ... }
```

Ghi **một** dòng giá trị net, giữ action cũ (`event_reward_*`, `event_bonus`). Không ghi "+G" rồi "−phí": `ActionMustTaxReward` được cộng để tính thu nhập chịu thuế theo tháng (`cashflow.go:120-140`), phải chỉ thấy phần KOL/KOC thực nhận. Thông báo cho KOL/KOC (:580) dùng số net.

**MCN** — **không** ghi trong `runCashBack` (pool 50 goroutine; nhiều thành viên cùng MCN sẽ ghi song song vào một user, `oldBalance` sai). Ghi sau `wg.Wait()` trong `Running()` (:103), trước khi set `completed` (:112):

```go
func (r reconciliationImpl) creditMcnFees(ctx, rc) {
    // Σ mcn.fee theo mcn.mcn, chỉ item status completed của kỳ
    for each (mcnID, total) {
        acc := McnAccount active của mcnID      // luôn có user (MCN phải đăng nhập mới tạo được link)
        credited := Σ cash-flows {user: acc.User, action: mcn_fee, options.reconciliation: rc.ID}
        delta := total - credited
        if delta <= 0 { continue }
        AddCashFlow(ctx, []CashFlowPayload{{Partner: rc.Partner, Action: mcn_fee, Category: mcn,
            Value: delta, Options: {Reconciliation: rc.ID, Mcn: mcnID}}}, acc.User)
        Notification().Push(mcn_fee_credited)
    }
}
```

Tính `delta` theo những gì đã ghi giúp chạy lại an toàn: kỳ `run_failed` chạy lại (`running` cho phép từ `run_failed`, `reconciliation.go:366-385`) chỉ cộng phần còn thiếu.

**Rủi ro có sẵn:** `runCashBack` không có transaction; `AddCashFlow` bỏ qua lỗi insert (`cashflow.go:58-84`). Phase 1 không sửa toàn bộ, nhưng phần MCN đọc lại trạng thái item `completed` nên chỉ cộng phí cho khoản KOL/KOC đã thực sự được ghi.

### 8.3 Tab Người nhận (API)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/admin/reconciliations/:id/recipients` | Aggregate `reconciliation-items` theo `user`: `G = Σ totalCash`, `fee = Σ mcn.fee`, `net = G − fee`, `mcn`, `rate`, trạng thái. Thêm một dòng cho mỗi `mcn.mcn`: `net = Σ fee`. Query `type=all|none|member|mcn`, phân trang |
| GET | `/admin/reconciliations/:id/recipients/mcn/:mcnId` | Từng thành viên của MCN trong kỳ: tỷ lệ, G, phí |

Cả hai đọc snapshot nên có số ngay sau Lấy danh sách. `Statistic` của kỳ thêm `totalMcnFee`, `totalMcn` (tính trong `applyMcnSnapshot`) để modal Duyệt tất cả hiện "x MCN, tổng phí y".

---

## 9. Chi trả

Sửa `Processing` của đợt chi (`backend/pkg/admin/service/transfer_processing.go:40-105`). Trong vòng lặp user, **trước** các bước lọc SSO/hợp đồng:

```go
if mcn, bankDoc, ok := internalservice.Mcn().IsPayableMcnUser(ctx, user.ID, transfer.Partner); mcn != nil {
    if !ok { continue }              // MCN không active hoặc thiếu bank hiện hành
    // bỏ qua kiểm SSO id (:49) và hợp đồng B2C_AMBASSADOR (:54-86)
    // vẫn áp điều kiện số dư user-partners như hiện nay (:96-105)
    t.generateWithdrawMcn(ctx, transfer, user, mcn, bankDoc)
    continue
}
```

**Lưu ý:** vòng lặp đang chỉ lấy user `banned:false` (:22-26) — user tài khoản MCN thỏa điều kiện này. Cần `user-partners {user, partner}` tồn tại (đã upsert lúc bind, mục 3.3).

`generateWithdrawMcn` giống `generateWithdraw` (:118-153), khác:
- `WithdrawCashBody.TaxExempt = true` (trường mới).
- Điền `Bank`, `CardNumber`, `CardHolderName` từ `bankDoc.Bank` (với KOL/KOC các trường này đang để trống vì đoạn :123-129 bị comment).

`Withdraw().Create` (`backend/internal/service/withdraw.go:136-139`):

```go
if !payload.Body.TaxExempt && payload.Body.Cash >= constants.MinTaxableRevenue { ... }
```

`WithdrawRaw` thêm `RecipientType string bson:"recipientType"` (`user` | `mcn`), `Mcn AppID`. File xuất ngân hàng (`backend/pkg/admin/service/export_transfer.go:170-212`): dòng MCN lấy MST từ `mcns.taxCode` thay vì `user.Contract`.

**Ngưỡng thuế (Q1 PRD):** code đang 5.000.000. Nghiệp vụ nói 2.000.000. Không đổi trong việc MCN; nếu chốt đổi thì sửa `MinTaxableRevenue` thành việc riêng vì ảnh hưởng mọi creator.

**Quirk có sẵn, không sửa ở phase 1:** khi `MaxCashWithdraw > 0`, ngưỡng lọc thành `max(Min, Max)` (:96-105), người có số dư dưới Max bị loại khỏi đợt. Áp dụng như nhau cho MCN.

---

## 10. Frontend web (`frontend/`)

### 10.1 Route

Thêm vào `frontend/config/routes.ts` **trước** khối `/:partner/` (:119), dưới layout `@/layouts/home`:

| Path | Page | Ai |
|---|---|---|
| `/quan-ly-mcn` | `pages/mcn-manage` → mặc định tab thành viên | Tài khoản MCN |
| `/quan-ly-mcn/loi-moi` | `pages/mcn-manage` (tab lời mời) | Tài khoản MCN |
| `/quan-ly-mcn/doi-soat`, `/quan-ly-mcn/doi-soat/:id` | `pages/mcn-manage` | Tài khoản MCN |
| `/mcn/moi/:code` | `pages/mcn-invite` | Ai cũng mở được |
| `/mcn-cua-toi` | `pages/mcn-my` | KOL/KOC có quan hệ mở |
| `/doi-soat`, `/doi-soat/:id` | `pages/settlement` | Mọi creator |

Không có auth gate ở route (`wrappers/auth.tsx` không dùng); mỗi page tự kiểm `mainState.user` và gọi API, 403 thì về `/`.

### 10.2 Giữ mã mời qua đăng nhập

Theo tiền lệ `?ref=` (`frontend/src/layouts/home/index.tsx:138-146`):
- `pages/mcn-invite` khi chưa đăng nhập: ghi cookie `mcn_invite=<code>` 7 ngày, hiện nút Đăng nhập (mở modal login có sẵn).
- `proceedAfterLogin()` (`header/index.tsx:65-68`): nếu có cookie `mcn_invite` → `navigator.pushPath('/mcn/moi/' + code)` thay vì `/tai-khoan`. Cũng áp dụng sau `acceptPrivacy` (:257) cho người đăng ký mới.
- Xóa cookie khi đồng ý/từ chối thành công và khi logout (cạnh chỗ xóa `ref`, `models/main.ts:222-235`).
- `pages/main-home/index.tsx:51-56` (tự chuyển `/chien-dich`) không ảnh hưởng vì người dùng đã ở trang lời mời.

### 10.3 Menu và layout

- `header/components/profile.tsx` `menuItems` (:73-210) thêm, dùng khuôn `hidden` (:149):
  - `Quản lý MCN` → `/quan-ly-mcn`, `hidden: !user?.mcn`
  - `MCN của tôi` → `/mcn-cua-toi`, `hidden: !user?.mcnMembership`
  - `Đối soát` → `/doi-soat`, mọi creator
- Layout Quản lý MCN: chưa có khung tài khoản có menu trái dùng chung; làm component `components/mcn/side-menu` riêng (tham khảo sidebar cục bộ ở `pages/affiliate-commission/index.tsx:271-291`), không sửa các trang tài khoản hiện có.
- Bảng dùng antd `Table` + `Tag` như `pages/ekyc/index.tsx:76-130`. Chuỗi tiếng Việt viết thẳng như phần còn lại của app (i18n gần như không dùng).

### 10.4 API layer

- `frontend/src/configs/api.ts`: nhóm `mcn`, `mcnInvite`, `mcnMembership`, `settlement` theo khuôn `group: { name: (): IApi => ({url, method}) }`.
- `frontend/src/services/mcn.ts`, re-export ở `services/index.ts`.
- dva model `pages/mcn-manage/model.ts` (`mcnModel`), `pages/mcn-invite/model.ts` (`mcnInviteModel`).
- `IUser` (`frontend/src/interfaces/user.ts:3-27`) thêm `mcn`, `mcnMembership`.

### 10.5 Ký phụ lục

- `pages/mcn-invite` bước ký: `users.is_ekyc` false → modal dẫn tới `/thong-tin-dinh-danh?back=/mcn/moi/<code>`.
- Gọi `POST /mcn-memberships/me/sign` → `window.open(signLink)` (khuôn `components/button-view-contract.tsx:13-21`), lắng nghe `focus` của cửa sổ để gọi `sync-sign`.

---

## 11. Admin (`admin/`)

| Việc | Vị trí |
|---|---|
| Route `/mcn` (menu "Danh sách MCN") và `/mcn/:id` (`hideInMenu`), `access: 'isAdminAccess'` | `admin/config/routes.ts`, label `admin/src/locales/vi-VN/menu.ts` |
| Danh sách, filter, modal tạo | `admin/src/pages/mcn/index.tsx`, `components/table.tsx`, `components/filter.tsx`, `components/modal-create.tsx` — khuôn `pages/reconciliation/*` (tạo bằng modal như convention admin) |
| Chi tiết: tab Điều kiện kích hoạt / Hồ sơ pháp lý, tab Thành viên, nút Kích hoạt | `admin/src/pages/mcn/detail/*` — khuôn `pages/reconciliation/detail/index.tsx:103-119` |
| Upload hồ sơ | `FormUploadOneNew` (`components/form-upload-one-file`, `containerType: 'file'`, `accept: '.pdf'`); service upload mới gọi `/api/file/admin/document` |
| Drawer Xem hồ sơ + lịch sử | `admin/src/pages/mcn/detail/components/drawer-document.tsx` |
| Model, service, endpoint | `pages/mcn/model.ts` (`mcnModel`), `admin/src/services/mcn.ts`, `admin/src/configs/api.ts` |
| Tab Người nhận | Thêm vào `admin/src/pages/reconciliation/detail/components/tabs/index.tsx:28-53`, component `tabs/recipients/*` dùng `RcTableNew` + `ProColumns`; drawer dòng MCN |
| Modal Duyệt tất cả | Hiện thêm `statistic.totalMcn`, `totalMcnFee` |
| Đợt chi | `admin/src/pages/transfer/detail/components/table/view.tsx:109-178` thêm cột Loại (`recipientType`); `cashTax` = 0 cho MCN tự hiện đúng |

---

## 12. Jobs

Đăng ký theo khuôn schedule hiện có (`backend/pkg/public/service/schedule.go`):

| Job | Chu kỳ | Việc |
|---|---|---|
| `mcn-sync-annex` | 15 phút | `agreed` có `annex.contractId`: hỏi econtract, SIGNED → `active` |
| `mcn-sign-expire` | 1 giờ | `agreed` có `signDeadline < now` → `sign_expired`, `open=false` |
| `mcn-sign-remind` | 1 ngày | `agreed` còn ≤ 2 ngày → thông báo KOL/KOC |
| `mcn-leave-effective` | 15 phút | `leaving` có `leaveEffectiveAt <= now` → `ended (koc_leave)`, `open=false` |
| `mcn-annex-expire` | 1 ngày | Chờ Q7 PRD. Nếu chốt tự kết thúc: `active|leaving` có `endAt <= now` → `ended (annex_expired)` |

Mọi job cập nhật có điều kiện trạng thái nguồn trong filter để chạy song song với thao tác người dùng không ghi đè nhau.

---

## 13. Email và thông báo

- **Email kích hoạt:** qua AT email API (`staff_auth_mail.go:22-44`), template code mới, ví dụ `AMBASSADOR_EMAIL_MCN_ACTIVATED`, AT phải cấp (phụ thuộc A2). Nội dung: tên MCN, link đăng nhập web Ambassador, câu "đăng nhập bằng Google với email này". Chưa có template thì kích hoạt vẫn chạy, Admin thấy cảnh báo "chưa gửi được email" và tự báo MCN.
- **Thông báo web:** `Notification().Push`, type mới trong `backend/internal/constants/notification.go`: `mcn_invite_agreed`, `mcn_member_joined`, `mcn_sign_remind`, `mcn_member_leaving`, `mcn_member_leave_cancelled`, `mcn_member_terminated`, `mcn_member_ended`, `mcn_fee_credited`; category `mcn`.

---

## 14. Ánh xạ FR → code

| FR | Backend | Frontend / Admin |
|---|---|---|
| 001–002 | `admin/router/mcn.go`, `admin/service/mcn.go`, model `mcn.go` | `admin/src/pages/mcn/*` |
| 003 | `mcn_document.go`, route upload `pkg/file` | `pages/mcn/detail/*` |
| 004 | `admin/service/mcn_bank.go` | modal tài khoản ngân hàng |
| 005 | `admin/service/mcn.go` Activate, `internal/service/mcn.go` BindAccountOnLogin, `public/service/user.go` (gọi bind ở 4 luồng login), `/users/me` | — |
| 006 | `GET /admin/mcns/:id/members` | tab Thành viên |
| 007 | middleware `RequiredMcnAccount` | `profile.tsx`, layout MCN |
| 008–011 | `public/router/mcn.go`, `public/service/mcn.go` | `pages/mcn-manage/*` |
| 012–014 | `public/router/mcn_invite.go`, econtract annex | `pages/mcn-invite/*`, `header/index.tsx` |
| 015 | `mcn-memberships/me/*`, job leave | `pages/mcn-my/*` |
| 016 | `reconciliation_processing.go` `applyMcnSnapshot` | — |
| 017 | `reconciliation_recipients.go` | `reconciliation/detail/components/tabs/recipients/*` |
| 018 | `reconciliation_running.go` (`runCashBack`, `creditMcnFees`) | — |
| 019 | `transfer_processing.go`, `withdraw.go`, `export_transfer.go` | `transfer/detail/components/table/view.tsx` |
| 020 | `GET /mcn/reconciliations*` | `pages/mcn-manage` tab đối soát |
| 021 | `GET /users/reconciliations*` | `pages/settlement/*` |
| 022 | `constants/notification.go`, email | — |

---

## 15. Thứ tự triển khai

1. **Nền:** collections, model, index, constants, `internal/service/mcn.go`. Không ảnh hưởng gì đang chạy.
2. **Admin hồ sơ MCN** (FR-001–006) + route upload. Có thể lên production sớm, tạo hồ sơ thật trong lúc chờ phụ thuộc.
3. **Bind tài khoản + `/users/me` + menu web** (FR-005, 007).
4. **Link mời, đồng ý, MCN quản lý** (FR-008–013, 015). Ký phụ lục (FR-014) chờ A1.
5. **Đối soát** (FR-016–018), bật bằng `PartnerOpts.McnEnabled` — tắt thì `applyMcnSnapshot` không chạy, hành vi y như cũ.
6. **Chi trả** (FR-019) — phải lên **cùng hoặc trước** bước 5, nếu không phí MCN nằm trong số dư mà không có đường chi.
7. **Màn xem đối soát** (FR-020–021), thông báo (FR-022).

---

## 16. Test plan

### 16.1 Unit test bắt buộc

- `applyMcnSnapshot`: không thành viên → item không có `mcn`; `active` → có; `leaving` chưa tới ngày → có; `leaving` đã tới ngày → không; MCN `pending` → không; partner tắt `McnEnabled` → không.
- Làm tròn phí: `TotalCash=3.000.000, rate=15 → 450.000`; `1.234.567 × 15%` → `185.185`; luôn `net + fee == TotalCash`.
- `creditMcnFees` chạy hai lần → chỉ một lần cộng; chạy lại sau khi thêm item completed → cộng đúng phần chênh.
- `Withdraw().Create` với `TaxExempt` → `CashTax = 0` dù ≥ ngưỡng; không có cờ → như cũ.
- Máy trạng thái `mcn-members`: mọi chuyển hợp lệ; chuyển không hợp lệ → 409; đồng ý lời mời thứ hai khi đang mở → lỗi index → 409.
- So khớp tên chủ tài khoản: có/không dấu, tiền tố CÔNG TY TNHH.

### 16.2 Kịch bản tích hợp

1. Tạo MCN → thiếu hồ sơ → Kích hoạt bị chặn, liệt kê thiếu → đủ → kích hoạt → đăng nhập Google bằng email đó → thấy Quản lý MCN.
2. Email MCN trùng user đã có → không tạo được.
3. Tạo link 15% → KOL/KOC chưa đăng nhập mở link → đăng nhập lần đầu, chấp nhận điều khoản → quay về đúng trang lời mời → đồng ý → chưa eKYC bị chặn → eKYC → ký → thành viên.
4. KOL/KOC đang thuộc MCN A mở link MCN B → bị chặn.
5. Kỳ đối soát có 3 người (15%, 10%, không MCN) G = 3.000.000 / 2.000.000 / 1.500.000 → tab Người nhận: 450.000 / 200.000 / 0, dòng MCN 650.000 → Duyệt → số dư KOL/KOC 2.550.000 / 1.800.000 / 1.500.000, MCN 650.000.
6. Đợt chi: MCN có mặt, `cashTax = 0`, có số TK công ty; KOL/KOC như cũ.
7. Kỳ đối soát không có thành viên MCN → kết quả byte-giống bản trước khi có tính năng (so `cash-flows` của kỳ).

### 16.3 Kiểm trước khi merge

```bash
# Không có trường vai trò MCN trên users
grep -rn "AccountType\|account_type\|IsMcn" backend/internal/model/mg/user.go   # → rỗng
# Mọi kiểm vai MCN đi qua service
grep -rn "CollectionMcnAccount" backend --include='*.go' | grep -v "internal/service/mcn.go\|collection_mcn.go\|index.go\|model/mg\|dao/"   # → rỗng
# mcn_fee không nằm trong ActionMustTaxReward
grep -n "mcn_fee" backend/internal/constants/cash_flow.go
```

---

## 17. Rủi ro

| Rủi ro | Giảm thiểu |
|---|---|
| Ghi tiền không atomic (có sẵn) làm lệch KOL/KOC và MCN | Phí MCN tính từ item `completed`, cộng theo delta |
| MCN dùng email không phải tài khoản Google | Nêu rõ trong email kích hoạt; Admin xác nhận với MCN trước khi tạo (A4) |
| Chưa có loại hợp đồng phụ lục | Làm và phát hành các phần khác trước; FR-014 bật sau |
| Bật đối soát MCN trước chi trả | Thứ tự triển khai mục 15, cờ `McnEnabled` |
| Ngưỡng thuế lệch nghiệp vụ | Q1 PRD, xử lý riêng |
| Tên chủ TK công ty không tra được | Cho nhập tay kèm lý do, lưu lịch sử |

---

## 18. Câu hỏi cần chốt trước khi code

Xem PRD mục 9 (Q1–Q8). Thêm cho kỹ thuật:

| # | Câu hỏi | Ai trả lời |
|---|---|---|
| T1 | AT core: mã loại hợp đồng phụ lục, mẫu, trường động | AccessTrade core |
| T2 | AT core: tra tên chủ TK công ty không cần SSO user được không | AccessTrade core |
| T3 | AT: template code email kích hoạt MCN | AccessTrade |
| T4 | Bucket file riêng tư cho hồ sơ pháp lý: dùng bucket nào, thời hạn presigned URL | DevOps |

---

## 19. Revision History

| Version | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-11-04 | Bản đầu. Vai MCN qua `mcn-accounts`, thành viên qua `mcn-members`; không thêm loại tài khoản trên `users` |
