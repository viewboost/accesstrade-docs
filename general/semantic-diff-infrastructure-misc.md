# Semantic Diff — Infrastructure & Misc Group

> **Generated**: 2026-05-07
> **Files trong scope**: `notification.go`, `check_rate_limit.go`, `tracking_request_crawl.go`, `load_data.go`, `staff.go`, `affiliate.go`

| Service | TCB | vCreator | Ambassador | Notes |
|---|---:|---:|---:|---|
| notification.go | 509 LOC | 294 LOC | 290 LOC | Divergent (3 md5 khác) |
| check_rate_limit.go | 113 LOC | ❌ | ❌ | TCB-only |
| tracking_request_crawl.go | 47 LOC | ❌ | ❌ | TCB-only |
| load_data.go | 30 LOC | ❌ | 30 LOC | **TCB+Amb md5 identical** |
| staff.go | ❌ | 62 LOC | ❌ | vCreator-only |
| affiliate.go | ❌ | ❌ | **399 LOC** | Ambassador-only |

---

## TL;DR

Group này **rất phân mảnh**:
- `notification.go` divergent 3 dự án nhưng cùng skeleton → khác chủ yếu ở channel hỗ trợ
- `load_data.go` synced TCB↔Ambassador (identical md5), vCr không có
- 3 service mỗi sản phẩm 1 cái: `check_rate_limit` (TCB), `staff` (vCr), `affiliate` (Amb)

→ Group này tổng hợp các utility services không thuộc domain chính, mỗi cái phục vụ tính chất riêng từng sản phẩm.

---

## 1. `service/notification.go` — Push notification (cả 3 đều có, divergent)

### Skeleton chung
3 dự án cùng pattern:
- `Push(notifications)` — gửi notification batch qua Firebase
- `GetContent(n)` — render title + content từ template
- `GetOption(n)` — get UI option per notification type
- `GetAppResponse(...)` — build response cho mobile app
- `GetNotificationPayload(...)` — build Firebase message

→ Đây là **shared notification skeleton**. Tất cả import `firebase.google.com/go/v4/messaging` + `internal/locale` cho i18n.

### Khác biệt nghiệp vụ

**TCB (509 LOC, lớn nhất)**:
- Imports thêm: `internal/module/sendgird` + `internal/module/smtp` + `emailtemplates`
- → Hỗ trợ **3 channel**: Firebase push, SendGrid (transactional email), SMTP (fallback email)
- Có template email cho các flow như: invite-creator, reset-password, etc.

**vCreator (294 LOC)**:
- Chỉ Firebase push (không thấy import sendgrid/smtp)
- Có thêm `SendNotificationInfluencerChangeStatus` (đã thấy ở user_social_partner phía TCB) — nhưng vCreator không có user_social_partner, có lẽ dùng cho flow khác

**Ambassador (290 LOC)**:
- Chỉ Firebase push
- Comment trong code (group User & Auth): "Notification.SendNotificationInfluencerChangeStatus" chưa có ở Ambassador → đúng là Ambassador notification scope hẹp hơn TCB

### Ý nghĩa nghiệp vụ
TCB là sản phẩm B2B-grade (banking partner) → cần email transactional cho compliance/audit. vCr/Amb là creator-facing, chỉ cần push notification.

---

## 2. `service/check_rate_limit.go` (TCB-only, 113 LOC)

### Hàm public

```go
type RateLimit struct {
    RemoteIP string
    StaffID  modelmg.AppID
}

func (r RateLimit) CheckRateLimitRequestOTP(ctx) (int, error)
```

### Logic
- Per (StaffID, RemoteIP) check rate limit OTP request
- Dùng Redis key `BlockIPRequestOTP` với TTL = config window
- Audit log action: `login_admin`, `auth_exchange`
- Trả về số giây còn lại + error nếu bị block

### Ý nghĩa nghiệp vụ
TCB là sản phẩm dành cho admin Techcombank → cần rate limit chống brute force OTP. vCr/Amb là creator-facing → đã có rate limit ở layer khác (gateway) nên không cần duplicate.

→ TCB-led security feature cho admin login flow.

---

## 3. `service/tracking_request_crawl.go` (TCB-only, 47 LOC)

### Hàm public
```go
func InsertTrackingRequestCrawl(ctx, payload, response, err)
```

### Logic
- Insert 1 record vào `TrackingRequestCrawlRaw` mỗi lần gọi `contentcatcher.GetData`
- Lưu: action, source, endpoint, method, headers (X-Request-Id), body, status code, duration, success flag, error message, raw response

### Ý nghĩa nghiệp vụ
TCB tracking mọi crawl request đến content_catcher (module crawl video/social) để:
- Debug failed crawls
- SLA monitoring (duration metric)
- Audit fairness reconciliation (đã thấy `MakeupCrawl` ở reconciliation_snapshot dùng tracking này)

→ Tied chặt với reconciliation engine. vCr/Amb không có MakeupCrawl nên không cần tracking này.

---

## 4. `service/load_data.go` (TCB ↔ Ambassador synced, vCr ❌)

### Hàm public
- `GetDataDemographic(...)`
- `LoadDataDemographic(...)`

### Existence
- TCB md5 = Ambassador md5 = `93a5b3af5499e12fd0002cfad61a5bf2` → **100% identical**
- vCreator: ❌ không có

### Ý nghĩa
File rất ngắn (30 LOC) — likely utility load demographic enums/metadata từ static source. Đã sync giữa TCB và Ambassador. vCreator không cần (có thể dùng pipeline khác cho demographics).

---

## 5. `service/staff.go` (vCreator-only, 62 LOC, 2 hàm)

### Hàm public
- `GetRoot()` — return root staff account
- `Staff()` — constructor

### Logic
- Get hardcoded "root" staff account (system actor) cho automation
- Comment trong code (xem audit.go group Reconciliation): "ActorTypeRootAccount là root system account dùng cho tác vụ tự động (webhook, batch import)"

→ Tied chặt với vCreator's automation flow:
- `crosscheck` module
- `pub_be` (public backend)
- batch import via `registry_match`

Mỗi flow tự động cần actor → gọi `Staff().GetRoot()` để có ID staff system.

### Ý nghĩa nghiệp vụ
vCreator có concept "system staff" cho audit/automation. TCB/Amb chưa cần concept này (audit không phân biệt actor type).

---

## 6. `service/affiliate.go` (Ambassador-only, 399 LOC, 16 hàm)

### Hàm public chính (16 hàm — feature flagship của Ambassador)

**Campaign CRUD**:
- `CreateCampaign`, `UpdateCampaign`, `GetCampaign`, `ListCampaigns`, `UpdateCampaignStatus`

**Mapping campaign ↔ event**:
- `LinkCampaignToEvent(mapping)`
- `UnlinkCampaignFromEvent(id)`
- `GetAffiliateCampaignsByEvent(eventID)` — list campaigns gắn với 1 event
- `GetMappingsByEvent(eventID)` / `GetMappingsByCampaign(campaignID)` — query mappings

**Contract (user join campaign)**:
- `JoinCampaign(userID, ssoID, campaignID)` → tạo `AffiliateContractRaw`
- `GetContract(userID, campaignID)` — get user's contract for campaign
- `GetUserContracts(userID)` — list all contracts of user

**Link generation**:
- `GenerateLink(userID, ssoUserID, campaignID, originalUrl, name)` → tạo `AffiliateLinkRaw`
- `GetUserLinks(userID, filter)` — list affiliate links của user

**Helper (private)**:
- `isCampaignInTimeRange(campaign)` — check campaign trong khoảng startAt-endAt

### Models cần (Ambassador-only)
- `AffiliateCampaignRaw` — campaign config (start/end, budget, commission %, brand info)
- `CampaignAffiliateMappingRaw` — mapping campaign ↔ event (1 campaign có thể trải qua nhiều events)
- `AffiliateContractRaw` — user contract khi join campaign (sử dụng SSO ID — integrate với external Accesstrade?)
- `AffiliateLinkRaw` — generated link cho user (track click → conversion)

### Ý nghĩa nghiệp vụ

Đây là **flagship feature của Ambassador**: khác với TCB và vCreator (campaign-reward style), Ambassador chạy **affiliate marketing**:

1. Brand tạo affiliate campaign với % commission
2. Campaign mapping vào event (= time window cho campaign)
3. User join campaign → tạo contract (lưu SSO ID = Accesstrade user ID)
4. User generate affiliate links (= URL gốc + tracking code) → share trên social
5. Khi có purchase qua link → commission cho user

Module `internal/module/pub2` (chỉ có ở Ambassador) likely là integration với **publisher-2 system** của Accesstrade (tracking conversions).

→ Đây là điểm khác biệt cốt lõi với TCB/vCreator: Ambassador = **affiliate marketing platform** (creator earn theo conversion), 2 sản phẩm kia = **content-reward platform** (creator earn theo views/engagement).

---

## 7. Models phát hiện thú vị

### TCB-specific models (cho infrastructure)
- `TrackingRequestCrawlRaw` (group này)
- `BlockIPRequestOTPRaw` hoặc tương đương (rate limit data, có thể chỉ ở Redis)

### vCreator-specific
- `StaffRaw` (root staff account) — đã thấy ở `model/mg/staff.go` group User

### Ambassador-specific (affiliate)
- `AffiliateCampaignRaw`, `CampaignAffiliateMappingRaw`, `AffiliateContractRaw`, `AffiliateLinkRaw`

→ 4 model này KHÔNG có ở TCB/vCr. Nếu port affiliate sang sản phẩm kia thì phải tạo cả 4.

---

## 8. Câu hỏi business mở

1. **TCB rate limit** chỉ apply cho admin login (action="login_admin", "auth_exchange")? Còn rate limit cho public API có ở module khác không?
2. **vCreator staff.go GetRoot** — root staff account này được seed thế nào? Init script có hardcoded ID không?
3. **Ambassador affiliate `ssoID`** — integration với Accesstrade SSO. SSO server ở đâu, scope nào, có doc không?
4. **Ambassador `pub2` module** — likely integration với Accesstrade publisher tracking. Có ở `accesstrade-projects/at-core` (memory đã ghi) hay là external system?
5. **`load_data.go` synced TCB↔Amb** — có deployment sync giữa 2 dự án không, hay là copy thủ công khi update?

---

## 9. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Notification channels** | Firebase + SendGrid + SMTP | Firebase only | Firebase only |
| **Admin rate limit** | ✅ Per-staff per-IP OTP guard | ❌ | ❌ |
| **Crawl request tracking** | ✅ Tied với reconciliation MakeupCrawl | ❌ | ❌ |
| **Demographic data loader** | ✅ (synced với Amb) | ❌ | ✅ (synced với TCB) |
| **Root system actor** | ❌ | ✅ Cho automation flows | ❌ |
| **Affiliate program engine** | ❌ | ❌ | ✅ Full (campaign + contract + links + mapping) |

**Đặc điểm group**:
- Rất phân mảnh, mỗi service phục vụ tính chất riêng
- Notification skeleton shared nhưng channel khác nhau (TCB có email, 2 sản phẩm khác chỉ push)
- Affiliate là feature lớn nhất, KHÔNG port được vì khác business model

**Direction port nếu cần**:
- TCB → vCr/Amb: `check_rate_limit` có thể useful nếu họ build admin portal nghiêm ngặt (effort nhỏ, ~113 LOC)
- TCB email channel có thể backport cho 2 sản phẩm kia nếu họ muốn email transactional
- vCreator's `staff.go` (root account) có thể useful cho automation ở 2 sản phẩm khác (effort cực nhỏ, ~62 LOC)
- Affiliate KHÔNG port (Ambassador-specific business model)
