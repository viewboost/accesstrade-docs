# Gap #43 — Ambassador/T-Fluencer còn nguyên các lỗ hổng public API mà Gen-Green đã hotfix

> **Priority**: 🔴 **P0** (lỗ hổng active, đã có đối tác chứng minh khai thác được)
> **Source**: Gen-Green báo tháng 8/2026 → hotfix trên vCreator/Gen-Green 26–27/08/2026
> **Direction port**: Gen-Green (vCreator) → Ambassador + T-Fluencer (TCB)
> **Last verified**: 2026-09-14

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Tháng 8/2026 đối tác **Gen-Green** gọi thẳng các endpoint public của platform (không cần login) và đọc được dữ liệu không thuộc về họ: **thu nhập từng creator**, **ngân sách hoa hồng theo từng nhãn**, và **danh sách user id** để enumerate. Đã hotfix xong trên Gen-Green.

Ambassador và T-Fluencer chạy cùng codebase gốc → còn nguyên hầu hết các lỗ hổng đó.

## ⚠️ CẢ HAI target đều KHÔNG port nguyên si được — đọc mục này trước

Gen-Green **không hiển thị tiền ở chỗ công khai**, nên fix của nó là cắt sạch field tiền khỏi response công khai. **Ambassador và TCB thì có** — đó là tính năng sản phẩm:

| Chỗ hiển thị | Field API | Ai xem được | Amb | TCB |
|---|---|---|:---:|:---:|
| Cột **"Kiếm được"** trên BXH — từng creator | `statistic.cashTotal.{completed,pending}` | **Khách vãng lai** | ✅ | ✅ |
| Cờ ẩn/hiện cột tiền | `partner.showLeaderboardAmount` | — | ✅ | ✅ |
| Stat **"Hoa hồng được xác nhận"/"Tiền thưởng"** trên landing | `totalCommission` | Khách vãng lai | ✅ | ❌ không dùng |
| Thanh **% ngân sách campaign** | `statisticBudget.percent` | Khách vãng lai | ❌ không có | ✅ |
| Mốc thưởng, tiền tạm tính, `cashback` theo nguồn | `userEventStatistic.*` | Chính chủ sau login | ✅ | ✅ |

→ Áp nguyên fix Gen-Green sẽ **làm vỡ tính năng cốt lõi của cả hai**.

**Lỗ hổng thật của Ambassador và TCB nằm ở chỗ khác**: cờ `showLeaderboardAmount = false` hiện **chỉ được ẩn ở FE** — server vẫn trả đủ tiền cho mọi creator. Nhãn nào tắt cột tiền thì cứ mở DevTools/curl là đọc được đúng thứ vừa tắt:

```tsx
// ambassador/frontend/.../not-logged-in/index.tsx:201  và  Techcombank/frontend/.../not-logged-in/index.tsx:831
showAmount={partnerDetail?.showLeaderboardAmount !== false}   // ← chặn DUY NHẤT, nằm ở client
```

Cộng thêm phần **dữ liệu thừa không FE nào đọc** (`cashReward`, `cashBonus`, `cash` từng nền tảng, `cashback`) vẫn nằm trong payload công khai.

→ **Hướng fix cho CẢ HAI: ép server tôn trọng đúng cờ đã có, và chỉ trả những field FE thật sự đọc.** Không cắt mù.

Khác biệt giữa hai target: **Ambassador đã có sẵn chỗ phân giải cờ** (`internal/service/leaderboard_config.go`, `EffectiveMetrics()`), chỉ thiếu bước áp vào payload. **TCB chưa có** — phải tự dựng, nhưng nhỏ hơn nhiều vì TCB chưa có tầng `LeaderboardOpts`.

## Bảng so sánh 3 sản phẩm

| # | Lỗ hổng | Endpoint | Gen-Green | Ambassador | TCB |
|---|---|---|:---:|:---:|:---:|
| 1 | BXH trả tiền của creator khác, cờ ẩn tiền chỉ chặn ở FE | `/events/{id}/leaderboards` | ✅ cắt sạch | ❌ **ép cờ server-side** (hook có sẵn) | ❌ **ép cờ server-side** (phải dựng hook) |
| 2 | Content công khai trả tiền từng bài | `/events/{id}/content` | ✅ | ❌ port thẳng | ❌ port thẳng |
| 3 | Enumerate user id qua phân trang vô hạn | leaderboards + content | ✅ | ❌ port thẳng | ❌ port thẳng |
| 4 | **BOLA** `?user=<id>`, không cần token | `/user-statistic*` | ✅ tắt group | ❌ **fix authz** (2 FE đang dùng) | ❌ tắt group như GG |
| 5 | Lộ ngân sách qua `?partner=` | `/events/statistic` | ✅ bỏ `totalCommission` | ✅ **đã an toàn sẵn** — giữ nguyên | ❌ bỏ `totalCommission` |
| 5b | Lộ số tiền ngân sách campaign | `statisticBudget` trong event response | — không có | — không có | ❌ **giữ `percent`, bỏ 5 field tiền** |
| 6 | Endpoint chết, lộ URL ảnh social thô | `/events/user-newest` | ✅ | ❌ port thẳng | ❌ port thẳng |
| 7 | eKYC `access_token` postMessage `'*'` | FE `step-ekyc.tsx` | ✅ | ❌ 9 FE | — không có luồng eKYC FE |
| 8 | `GetMe.statistic` trả dư field tiền | `/users/me` | ✅ rút còn 3 field | ⏭️ **bỏ qua** — FE dùng 9 field | ⏭️ bỏ qua |

## Hệ quả

- **Cả hai**: nhãn đã tắt cột tiền (`showLeaderboardAmount = false`) vẫn bị đọc thu nhập từng creator qua API → cam kết với nhãn đó đang không được giữ. `cashReward`/`cashBonus`/cash từng nền tảng lộ chi tiết hơn hẳn mức nhãn muốn công khai.
- **TCB**: thêm số tiền ngân sách campaign (`totalCashValid/Waiting/Pending/Completed/Rejected`) đọc được ẩn danh, trong khi FE chỉ cần `percent`.
- `cashback` = số lượt view đã được tính tiền, nhân đơn giá công khai là **suy ra thu nhập** dù không trả field tiền trực tiếp.
- Cả hai: enumerate user id qua phân trang; `/user-statistic?user=<id>` đọc thu nhập + danh sách invitee của user bất kỳ **không cần đăng nhập**.

## Giải pháp

| Sản phẩm | Cách làm | Effort |
|---|---|---|
| **Ambassador** | #2,3,6 port thẳng · #1 áp `EffectiveMetrics()` có sẵn vào payload · #4 fix authz · #5 giữ nguyên · #7 sửa 9 FE | ~3 ngày |
| **TCB** | #2,3,6 port thẳng · #1 dựng chỗ phân giải `ShowLeaderboardAmount` rồi gate payload · #4 tắt group · #5 bỏ `totalCommission` · #5b giữ `percent` | ~3 ngày |

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Nguyên nhân gốc chung: **response công khai nhúng thẳng model MongoDB** (`modelmg.UserEventStatistic`, `modelmg.UserContentStatistic`). Model có field tiền → API public có field tiền. Fix: dựng struct response riêng + hàm `New*()` map thủ công + comment `SECURITY` chặn người sau thêm field tiền vào lại.

Riêng Ambassador và TCB thêm một tầng: **quyết định trả tiền hay không phải nằm ở server, theo đúng cờ mà admin đã đặt**, thay vì để FE tự ẩn.

Commit nguồn (repo `Vin-VCreator/vcreator`, đã merge `develop`):

| Commit | Nội dung |
|---|---|
| `c57e7fe2` | `fix(security)`: không trả thu nhập của creator khác ở leaderboard và content công khai |
| `1ceae870` | `fix(security)`: tắt route `user-newest` + bỏ field `totalCommission` công khai |
| `cec8c898` | `feat(public)`: giới hạn leaderboard tối đa 100 item (5 trang) |
| `cc9919b8` | `chore(router)`: comment out `userStatistic(r)` trong `Init` |
| `9389a9d3` | `chore(frontend-green)`: tắt route `/statistics` |
| `c4f3b47d`, `3aa6a59f`, `e492c094` | trim field tiền thừa ở `GetMe` / event response / cash-flow |
| `9c0ff3b7` | `hide token`: bỏ `access_token` khỏi `postMessage` của eKYC iframe |

---

## Fix 1 — BXH lộ tiền creator khác *(hướng chung cho cả 2, chi tiết khác nhau)*

### Hiện trạng

```go
// Ambassador — pkg/public/model/response/event.go:190
Statistic modelmg.UserEventStatistic `json:"statistic"`   // trả TẤT CẢ, kể cả khi partner tắt cột tiền

// TCB — pkg/public/model/response/event.go:156-169
// có struct riêng UserEventStatisticResponse (không có cashReward/cashTotal/cashBonus cấp cao)
// nhưng mỗi nền tảng vẫn nhúng modelmg.UserContentStatistic → còn nguyên .cash + .cashback
Tiktok/Youtube/... modelmg.UserContentStatistic
```

⚠️ **TCB trả `cashTotal` ở BXH bằng đường nào?** `UserEventStatisticResponse` không khai `cashTotal`, nhưng FE `logged-in-view/table.tsx:106` đọc `value?.cashTotal` và cột vẫn hiện → **xác minh lại trên môi trường chạy thật bằng một lần curl BXH** trước khi code. Hai khả năng: (a) FE đang đọc field không tồn tại và cột luôn hiện 0 — tức tính năng đã hỏng sẵn, (b) có đường trả khác chưa rà ra. Kết quả quyết định TCB đi nhánh 🅰️ hay 🅱️ bên dưới.

### Field FE **thật sự đọc** trên mỗi dòng BXH

Verify từ `content-rank-item/{index.tsx,metric-value.ts,total-metrics.ts}` và `logged-in-view/table.tsx` của cả hai sản phẩm:

| Field | Dùng làm gì | Amb | TCB |
|---|---|:---:|:---:|
| `statistic.pointTotal.{completed,pending}` | cột "lượt xem" | ✅ | ✅ |
| `statistic.cashTotal.{completed,pending}` | cột "Kiếm được" — **chỉ khi cờ cho phép** | ✅ | ✅ (table view) |
| `statistic.<nền tảng>.view.completed` (+`pending` ở Amb) | dãy icon nền tảng | ✅ | ✅ (youtube, tiktok) |
| `statistic.totalContent` | đếm bài | ✅ | ✅ |
| `cashReward`, `cashBonus` | — | ❌ | ❌ |
| `<nền tảng>.cash`, `.point`, `.like`, `.comment`, `.viewRewarded` | — | ❌ | ❌ |
| `cashback`, `transfer`, `manual`, `waiting`, `rejected`, `total` trong từng metric | — | ❌ | ❌ |

> TCB có **hai view BXH**: card (`content-rank-item`) đã comment out cột tiền từ trước (`index.tsx:26-32`), và table (`logged-in-view/table.tsx`) vẫn có cột "Kiếm được" gated bằng `showAmount`. Chỉ view table cần `cashTotal`.

### Struct đề xuất *(dùng chung cả 2)*

```go
// SECURITY 2026-09: field tiền ở đây CÓ CHỦ ĐÍCH — BXH công khai có cột "Kiếm được".
// Nhưng nó chỉ được set khi cờ cho phép: partner.ShowLeaderboardAmount (và ở Ambassador
// là LeaderBoardConfig.EffectiveMetrics() có "cash"). Partner tắt tiền thì CashTotal phải
// nil — trước đây chỉ FE ẩn cột, API vẫn trả đủ.
// KHÔNG thêm field tiền nào khác: cashReward/cashBonus/cash từng nền tảng không FE nào đọc.
type LeaderBoardStatistic struct {
    TotalContent int64                      `json:"totalContent"`
    PointTotal   PublicMetric               `json:"pointTotal"`
    CashTotal    *PublicMetric              `json:"cashTotal,omitempty"`   // nil = cột tiền tắt
    Tiktok       LeaderBoardSourceStatistic `json:"tiktok"`
    // ... các nền tảng còn lại, mỗi nguồn chỉ có View
}

// PublicMetric: bỏ cashback/transfer/manual. `cashback` là số lượt view đã được tính tiền,
// nhân đơn giá là suy ra thu nhập.
type PublicMetric struct { Completed, Pending float64 }

func NewLeaderBoardStatistic(s modelmg.UserEventStatistic, showCash bool) LeaderBoardStatistic
```

### 🅰️ Ambassador — hook đã có sẵn

```go
// internal/service/leaderboard_config.go — ĐÃ CÓ, đang chạy
type LeaderBoardConfig struct {
    Opts       *modelmg.LeaderboardOpts
    ShowAmount bool                       // từ partner.ShowLeaderboardAmount
}
func (c LeaderBoardConfig) EffectiveMetrics() []string   // áp ShowAmount lên metrics, bỏ "cash" khi tắt
```

`pkg/public/service/event.go:750,759` đã gọi `cfg.EffectiveMetrics()` để trả field `metrics` cho FE, và `plan.Metrics` có sẵn trong `buildLeaderBoard` (`:788`) → chỉ cần truyền `showCash := funk.Contains(plan.Metrics, constants.LeaderboardMetricCash)` xuống hàm map dòng.

⚠️ **Cache key phải đổi theo** — xem Risks #2.

### 🅱️ TCB — phải dựng chỗ phân giải cờ

TCB **có** `partner.ShowLeaderboardAmount` (`internal/model/mg/partner.go:26`, trả ra public ở `response/partner.go:24`) nhưng **không có** `LeaderboardOpts`/`leaderboard_config.go`, và `GetLeaderBoard` (`pkg/public/service/event.go:353`) **không đọc partner** — chỉ `FindOne` event rồi query `user_event`.

→ Thêm đúng một bước: load partner theo `event.Partner`, lấy `ShowLeaderboardAmount` (nil hoặc partner lỗi → mặc định `true`, giữ hành vi hiện tại), truyền `showCash` xuống hàm map. **Không cần port cả tầng `LeaderboardOpts` của Ambassador** — TCB chưa có cấu hình `metrics`/`valueBasis`, đưa vào là mở rộng scope ngoài lỗ hổng.

⚠️ TCB `GetLeaderBoard` hiện **không cache** → không dính Risks #2.

---

## Fix 2 — Content công khai lộ tiền từng bài *(port thẳng cả 2)*

FE cả hai chỉ đọc `statistic.view.total` và `statistic.like.total` trên danh sách content (`video-item/index.tsx:57,61`) → struct Gen-Green vừa khít:

```go
type ContentStatisticPublic struct { Point, View, Like, Comment PublicMetric }
func NewContentStatisticPublic(s modelmg.UserContentStatistic) ContentStatisticPublic  // bỏ nhánh Cash
```

Sửa ở: `service/event.go` — `GetListContentByEvent`, `GetListContentByMe`, `GetLeaderBoard`; `service/partner.go` — `GetContentFeature`. **TCB thêm `GetListContentLeaderboard`** (`router/event.go:27` — route riêng TCB có, hai sản phẩm kia không).

## Fix 3 — Cap phân trang chặn enumerate user id *(port thẳng cả 2)*

```go
// internal/constants/event.go
EventLeaderBoardMaxItems = 100   // limit 20/trang → page 0..4
EventContentLimit        = 20
EventContentMaxItems     = 100   // chỉ áp cho danh sách CÔNG KHAI
```

```go
// handler/event.go
if query.Page*query.Limit >= constants.EventContentMaxItems {
    return cc.Response200(&response.ContentAllResponse{Data: ..., NextPageToken: ""}, "")
}
if len(data.Data) == int(query.Limit) && (query.Page+1)*query.Limit < constants.EventContentMaxItems {
    data.NextPageToken = cc.PageTokenUsingPage(query.Page + 1)
}
```

**Không cap `/events/{id}/content/me`** (nội dung chính chủ). Amb: `handler/event.go:265,304,346`. TCB: `:276,:315,:353`.

⚠️ Ambassador có `options.leaderboard.size` (tổng dòng tối đa của bảng) — cap 100 là **trần cứng chống enumerate**, không thay thế `size`. Lấy `min(size, 100)`. TCB chưa có `size` nên áp thẳng 100.

## Fix 4 — BOLA `/user-statistic`

```go
// ambassador/backend/pkg/public/handler/user_statistic.go:54
data := s.GetListInvitee(ctx, util.GetAppIDFromHex(param.User), query)
//                             ^^^^^^^^^^ lấy thẳng từ query string
```

Group `/user-statistic` **không có `a.RequiredLogin`**; middleware `auth.Auth` chỉ parse token nếu có chứ không chặn → gọi ẩn danh với `?user=<bất kỳ>` đọc được thống kê/thu nhập/invitee của người đó. TCB giống hệt (`router/router.go:30`, `router/user_statistic.go`).

| | Gen-Green | Ambassador | TCB |
|---|---|---|---|
| FE gọi `/user-statistic`? | Không | **Có** — `frontend/src/pages/statistic/model.ts` (5 lời gọi) + `anker/src/pages/statistic/*` | **Không** (chỉ còn 1 khai báo type ở `interfaces/event.ts:252`, không có lời gọi) |
| Cách xử lý | Tắt group | **Fix authz**: thêm `a.RequiredLogin` vào cả 4 route, bỏ `param.User`, lấy userId từ token | Tắt `userStatistic(r)` như GG |

Ambassador: `anker/src/pages/statistic/components/tab-invitee.tsx` đang render `record.statistic.cash.{pending,approved,cashback,transfer}` của **invitee** — dữ liệu người khác nhưng là tuyến dưới của chính chủ. Giữ nguyên, chỉ cần chủ sở hữu được xác định từ token.

## Fix 5 — `totalCommission`

### 🅰️ Ambassador — GIỮ NGUYÊN, đã an toàn sẵn

`service/event.go:117-127` **đã có guard mà vCreator không có**:

```go
partners := Partner().GetListPartnersByDomain(ctx, query.Domain)
if len(partners) == 0 { return res }                               // domain lạ → trả rỗng
if query.PartnerID != "" {
    if !funk.Contains(partnerIds, query.PartnerID) { return res }  // partner không thuộc domain → rỗng
}
```

→ `?partner=<nhãn khác>` trả về 0, không pivot được. Con số còn lại đúng bằng thứ landing page của chính nhãn đó đang hiện công khai. **Không gỡ field** (13 FE đang render).

*(Hardening tuỳ chọn, ngoài P0: `query.Domain` lấy từ header `Origin`/`Referer` — `internal/echo/echo.go:199` — nên giả được; giả xong cũng chỉ đọc ra số liệu tenant đó vốn đã công khai.)*

### 🅱️ TCB — bỏ như Gen-Green

TCB `GetStatistic` (`service/event.go:335`) **không có guard domain**, `?partner=` đi thẳng vào `AssignPartnerID` → pivot được y hệt vCreator. **FE TCB không đọc `totalCommission`** (0 lời gọi trong `frontend/src` lẫn `dashboard/src`) → gỡ sạch, không ảnh hưởng UI.

## Fix 5b — `statisticBudget` *(chỉ TCB — giữ `percent`, bỏ tiền)*

```go
// pkg/public/model/response/event.go:122 — nằm trong EventBriefResponse + EventDetailResponse công khai
type EventStatisticBudgetResponse struct {
    TotalCashValid, TotalCashWaiting, TotalCashPending, TotalCashCompleted, TotalCashRejected float64
    Percent float64
}
```

FE **chỉ đọc `percent`** (thanh tiến độ ngân sách): `home/components/budget-banner/index.tsx:10`, `partner-home/components/event-simple-card/index.tsx:179,187,197`.

→ Bỏ 5 field tiền tuyệt đối, **giữ `Percent`**. Đây là sửa đúng chỗ: `percent` là thứ nhãn muốn khoe, số tiền tuyệt đối thì không.

## Fix 6 — Tắt `/events/user-newest` *(port thẳng cả 2)*

```go
// SECURITY: tắt route user-newest — endpoint chết ở mọi FE, nhưng vẫn public
// lộ URL ảnh Google/TikTok thô nếu gọi trực tiếp.
// g.GET("/user-newest", h.GetListUserNewest, v.EventStatistic)
```

Verify: Amb `router/event.go:21`, TCB `router/event.go:21` vẫn bật. Endpoint **chỉ khai báo trong `configs/api.ts`, không component nào gọi** ở cả hai → tắt an toàn.

## Fix 7 — eKYC token *(chỉ Ambassador)*

```tsx
iframe.contentWindow.postMessage(
  { config: configData, /* token: ekycConfig.access_token, */ result: 'init_data_iframe' },
  '*',   // targetOrigin '*' → iframe bất kỳ đọc được token
);
```

9 FE: `fecredit, flamingo, frontend, hdbank, lusso, parasola, tpbank, vng, vpbank` — `src/pages/ekyc/components/step-ekyc.tsx` (~dòng 225 và 232). Bỏ luôn `console.log('Post message', {...token...})` ngay phía trên. TCB không có luồng eKYC ở FE.

## Fix 8 — Trim `GetMe.statistic` *(BỎ QUA cả 2)*

Gen-Green rút còn 3 field. Ambassador FE đọc **9 field**: `cashRemaining` (15 chỗ), `cashTotal`, `totalInvitee`, `totalCashWaiting`, `totalCashPending`, `totalCashCompleted`, `totalCashTransferred`, `totalCashRejected`, `totalContent`. TCB tương tự.

→ Đây là **dữ liệu chính chủ sau login**, không phải lỗ hổng — chỉ là dọn payload. **Ngoài scope P0.**

---

## 🚫 KHÔNG được đụng vào — `userEventStatistic` của chính chủ

`PublicMetric` (bỏ `cashback`) **chỉ áp cho BXH và danh sách content của người khác**. `userEventStatistic` trong `/events`, `/events/current`, `/events/by-slug` là số liệu của chính chủ và FE cả hai sản phẩm **đang đọc `cashback`** từ đó:

```tsx
// Techcombank/frontend/src/pages/home/components/statistic/table.tsx:77
const cashback = view?.cashback || 0;
cashPending: Math.max(completedViews - cashback, 0),
cashCompleted: cashback,
```

Gen-Green cũng ghi đúng cảnh báo này trong comment `PublicMetric`. Áp nhầm = vỡ bảng "tiền theo nguồn" ở trang cá nhân.

---

## Đề xuất implementation

### Phase 0 — Xác minh BXH TCB (~0.5 ngày, **làm trước Phase 3**)
- Curl `/events/{id}/leaderboards` của TCB trên dev, xem payload có `cashTotal` không
- Kết quả quyết định TCB đi nhánh 🅰️ hay 🅱️ của Fix 1

### Phase 1 — Ambassador backend (~2 ngày)
- Fix 1: `LeaderBoardStatistic` + `CashTotal *PublicMetric`, nối `plan.Metrics` xuống hàm map dòng, **đổi cache key** (Risks #2)
- Fix 2, 3, 6 port thẳng từ Gen-Green
- Fix 4 theo hướng authz (thêm `RequiredLogin`, bỏ `param.User`)
- Port + sửa test: `leaderboard_pagination_test.go`, `statistic_shape_test.go`; thêm case **"partner tắt cột tiền → payload không có `cashTotal`"**
- Regenerate swagger

### Phase 2 — Ambassador frontend (~0.5 ngày)
- Fix 7 trên 9 FE
- Không đụng `totalCommission` (13 FE giữ nguyên)
- Confirm `frontend` + `anker` trang `/statistics` vẫn chạy sau khi bỏ `?user=`
- FE đọc `cashTotal` qua optional chaining sẵn → dòng thiếu field hiện 0, không crash. Vẫn smoke test 1 nhãn bật tiền + 1 nhãn tắt tiền

### Phase 3 — TCB (~2 ngày)
- Fix 1: thêm bước load partner trong `GetLeaderBoard` → `showCash`; gate `cashTotal`; cắt field thừa khỏi `UserEventStatisticResponse`
- Fix 2, 3, 6 port thẳng + `GetListContentLeaderboard`
- Fix 4: tắt `userStatistic(r)`
- Fix 5: bỏ `totalCommission` · Fix 5b: giữ `percent`, bỏ 5 field tiền
- Port test tương ứng

### Phase 4 — Verify + rollout (~0.5 ngày)
- Curl 6 endpoint không kèm token, assert không còn field tiền ngoài danh sách cho phép
- **Cả hai**: curl BXH của 1 nhãn có `showLeaderboardAmount = false` → assert **không có** `cashTotal`
- TCB: assert `statisticBudget` chỉ còn `percent`
- Regression: trang cá nhân/thống kê chính chủ vẫn đủ số liệu (nhất là bảng `cashback` theo nguồn)

**Total**: ~6 ngày cho cả 2 sản phẩm.

## Risks + mitigations

1. **Cắt nhầm field đang hiển thị** → mất cột "Kiếm được" trên 15 white-label Amb / bảng BXH TCB.
   - *Mitigation*: bảng field giữ/bỏ ở Fix 1 đã verify từ code FE của cả hai. Thêm test khoá JSON shape trước khi sửa service.
2. **Ambassador: cache BXH giữ payload cũ sau khi Ops đổi cờ tiền** — `GetKeyCacheListLeaderBoardEvent` hiện chỉ gồm `period_rankBy_valueBasis`. Gate payload theo `metrics` mà không đưa cờ cash vào key → tắt cột tiền xong API vẫn trả tiền suốt TTL.
   - *Mitigation*: nối cờ cash vào `plan.CacheSuffix`. **Bắt buộc.** TCB không cache BXH nên không dính.
3. **Áp `PublicMetric` nhầm vào `userEventStatistic`** → vỡ bảng "tiền theo nguồn" của chính chủ ở cả hai sản phẩm.
   - *Mitigation*: xem mục 🚫 ở trên; giới hạn phạm vi đúng 4 hàm map (5 với TCB).
4. **Ambassador không tắt được `/user-statistic` như Gen-Green** — `frontend` + `anker` đang dùng.
   - *Mitigation*: fix authz thay vì tắt route; test kỹ 2 app này sau khi bỏ `?user=`.
5. **Cap 100 item đá nhau với `options.leaderboard.size`** (Amb) ở campaign lớn.
   - *Mitigation*: lấy `min(size, 100)`; nhãn cần sâu hơn thì làm endpoint có auth, không nới cap public.
6. **Sót surface riêng của từng sản phẩm**.
   - *Đã rà xong*: Amb `missions/leaderboard-by-point` (`LeaderBoardItemResponse` chỉ `name/avatar/follower/point` → sạch); `affiliate` — `Commission`/`SaleAmount` nằm ở `AffiliateOrderItem`, endpoint `my-links`/`campaigns` đều có `RequiredLogin` → sạch; `event_schema.CashReward` + `mission.Reward` là cấu hình mốc thưởng của event, marketing công khai → giữ. TCB: chỉ còn `event_schema.CashReward` cùng loại → giữ.
7. **Người sau nhúng lại model mg vào response công khai**.
   - *Mitigation*: copy nguyên comment `SECURITY` + giữ `statistic_shape_test.go` (fail ngay khi field tiền quay lại).

## Files referenced

**Gen-Green / vCreator (source)** — repo `Vin-VCreator/vcreator`, nhánh `fix/security-hide-commission-and-disable-usernewest`:
- `backend/pkg/public/model/response/event.go` — `LeaderBoardStatistic`, `PublicMetric`
- `backend/pkg/public/model/response/content.go` — `ContentStatisticPublic`
- `backend/internal/constants/event.go` — `EventLeaderBoardMaxItems`, `EventContentMaxItems`
- `backend/pkg/public/handler/event.go` — cap phân trang
- `backend/pkg/public/router/event.go`, `router/router.go`
- `backend/pkg/public/handler/leaderboard_pagination_test.go`, `model/response/statistic_shape_test.go` — **port kèm**
- `frontend-green/src/pages/contract/components/step-ekyc.tsx`

**Ambassador (target)** — repo `AT-Core/ambassador`:
- `backend/internal/service/leaderboard_config.go` — `LeaderBoardConfig`, `EffectiveMetrics()` — **hook Fix 1, có sẵn**
- `backend/internal/model/mg/leaderboard_opts.go` · `internal/model/mg/partner.go:55` — `ShowLeaderboardAmount`
- `backend/pkg/public/service/event.go:750,759` (`EffectiveMetrics`), `:788` (`buildLeaderBoard`), `:117-127` (**guard domain, Fix 5**)
- `backend/pkg/public/model/response/event.go:190`, `content.go:24` — nhúng thẳng model mg
- `backend/pkg/public/handler/event.go:265,304,346` — phân trang không cap
- `backend/pkg/public/handler/user_statistic.go:54` — BOLA `param.User`
- `backend/pkg/public/router/event.go:21`, `router/user_statistic.go`, `router/router.go:34`
- FE tiền BXH: `frontend/src/pages/home/components/content-rank-item/{metric-value.ts,total-metrics.ts}`, `<app>/src/pages/home/components/logged-in-view/table.tsx`, `not-logged-in/index.tsx:201`
- FE trang statistic: `frontend/src/pages/statistic/model.ts`, `anker/src/pages/statistic/*`
- FE eKYC: `{fecredit,flamingo,frontend,hdbank,lusso,parasola,tpbank,vng,vpbank}/src/pages/ekyc/components/step-ekyc.tsx`

**T-Fluencer / TCB (target)**:
- `backend/internal/model/mg/partner.go:26` — `ShowLeaderboardAmount` (có cờ, **chưa ai đọc ở public**)
- `backend/pkg/public/service/event.go:353` — `GetLeaderBoard`, **không load partner** → chỗ thêm bước phân giải cờ
- `backend/pkg/public/model/response/event.go:156-169` — `UserEventStatisticResponse` còn cash từng nguồn
- `backend/pkg/public/model/response/event.go:37` (`TotalCommission`), `:122` (`EventStatisticBudgetResponse`)
- `backend/pkg/public/model/response/content.go:24`
- `backend/pkg/public/handler/event.go:276,315,353` — phân trang không cap
- `backend/pkg/public/service/event.go:335` — `TotalCommission`, **không có guard domain**
- `backend/pkg/public/router/event.go:21,27` · `router/router.go:30`
- FE tiền BXH: `frontend/src/pages/home/components/logged-in-view/table.tsx:98-106` (cột "Kiếm được", gated), `content-rank-item/index.tsx:26-32` (đã comment out), `not-logged-in/index.tsx:831`
- FE ngân sách: `frontend/src/pages/home/components/budget-banner/index.tsx:10`, `partner-home/components/event-simple-card/index.tsx:179-197`
- FE chính chủ đọc `cashback`: `frontend/src/pages/home/components/statistic/table.tsx:77`

## Lịch sử

- **2026-08**: Gen-Green báo lỗ hổng qua việc gọi trực tiếp endpoint public.
- **2026-08-26/27**: hotfix + merge trên vCreator/Gen-Green.
- **2026-09-14**: verify Ambassador + TCB → mở gap #43, phân loại **P0**.
  - Chốt **cả hai** đi hướng "ép cờ `showLeaderboardAmount` server-side" thay vì cắt mù — đọc code FE thấy cả hai đều hiển thị cột "Kiếm được" công khai, cờ ẩn tiền hiện chỉ chặn ở client.
  - Ambassador giữ `totalCommission` (đã có guard domain); TCB bỏ (không có guard, FE không dùng).
  - TCB giữ `statisticBudget.percent`, bỏ 5 field tiền tuyệt đối.
