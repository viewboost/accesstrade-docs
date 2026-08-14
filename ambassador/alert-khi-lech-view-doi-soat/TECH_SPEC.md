# Tech Spec — Job cảnh báo bất thường dữ liệu view (vòng 2)

**Trạng thái:** Đã triển khai · **sửa lỗi thiết kế 14/08** — mục 5 và 7.2 đã viết lại hoàn toàn
**PRD:** [2026-08-13-view-anomaly-alert-prd.md](2026-08-13-view-anomaly-alert-prd.md)
**Danh mục case:** [case.md](case.md)
**Tiền lệ kiến trúc:** [2026-08-12-reconciliation-alert-tech-spec.md](2026-08-12-reconciliation-alert-tech-spec.md)
**Ngày:** 2026-08-13

---

## 1. Tổng quan luồng

```
cron "0 0 6 * * *"  (Asia/Ho_Chi_Minh)          [pkg/admin/schedule/init.go]
 │
 └─► service.Schedule().ScanViewAnomaly()        [pkg/admin/service/shedule.go]
      │
      ├─ khoá chống chạy chồng (isRunViewAnomaly)
      ├─ nạp AlertConfig từ common-configs        [view_anomaly_config.go]
      │
      ├─ scanner.Run(ctx, cfg)                    [view_anomaly_scanner.go]  ── I/O
      │    │
      │    │  với mỗi event active (cursor _id, lô 200):
      │    │    nạp ctx dữ liệu → gọi detector theo lô
      │    │
      │    ├─ detectRewardMissing(scope)      ─┐
      │    ├─ detectMilestoneMissing(scope)   ─┤
      │    ├─ detectRewardLag(scope)          ─┼─► []Finding   (thuần, không I/O)
      │    ├─ detectViewDuplicated(scope)     ─┤
      │    └─ detectCallbackEmpty(scope)      ─┘
      │           │
      │           └─ reward_missing + reward_lag gọi shouldExpectReward  ★ module sâu
      │
      │  sau khi mọi lô đã quét xong — hai ngoại lệ cấp-run (mục 6.3):
      │    ├─ detectVendorOutage(scope)       — tally toàn run, theo Source
      │    └─ detectCrawlNoResponse(scope)    — sweep thẳng contents-callback
      │
      ├─ collector.Merge(findings)                [view_anomaly_collector.go]  ── thuần
      │    dedupe theo Fingerprint → gộp cụm → sắp xếp → cắt MaxRows
      │
      ├─ state.Filter(ctx, findings)              [view_anomaly_state.go]  ── I/O
      │    loại finding còn trong cooldown (collection view-anomaly-alerts)
      │
      ├─ state.Record(ctx, kept)                  ghi lại dấu vân tay + thời điểm
      │
      └─ notifyViewAnomalies(ctx, report)         [view_anomaly_notify.go]  ── I/O
           ├─ getViewAnomalyRecipients(ctx)       → staff isRoot → email
           ├─ buildViewAnomalyPayload(report)     → định dạng số, nhóm
           ├─ buildViewAnomalyTemplateData(...)   → shape API AccessTrade
           └─ core.Client().SmsGatewayAction(...) → POST /v1.0/partner/email/send
```

★ = module sâu nhất, quyết định chất lượng của hai alert nhạy cảm nhất.

**Bất biến quan trọng:**

1. Job **chỉ đọc** mọi collection nghiệp vụ. Collection duy nhất nó ghi là `view-anomaly-alerts` của chính nó.
2. Toàn bộ tri thức nghiệp vụ nằm trong tầng detector (thuần). Tầng scanner chỉ nạp dữ liệu.
3. `state.Record` chạy **kể cả khi gửi mail thất bại** — xem mục 7.3.

---

## 2. Vị trí mã nguồn

Toàn bộ đặt trong `pkg/admin/service/`, cùng chỗ với cảnh báo đối soát:

| File | Vai trò | I/O |
|---|---|---|
| `view_anomaly_types.go` | `Finding`, `Severity`, `AlertKind`, `Fingerprint()`, `Report` | Không |
| `view_anomaly_exclusion.go` | `shouldExpectReward` — cổng theo event-schemas | Không |
| `view_anomaly_detect.go` | 7 hàm detector + registry | Không |
| `view_anomaly_scanner.go` | Nạp dữ liệu theo lô, gọi detector | **Có** |
| `view_anomaly_collector.go` | Dedupe, gộp cụm, sắp xếp, cắt | Không |
| `view_anomaly_state.go` | Cooldown, đọc/ghi lịch sử phát hiện | **Có** |
| `view_anomaly_notify.go` | Dựng payload + gọi API AccessTrade | **Có** |
| `view_anomaly_config.go` | Nạp và validate ngưỡng từ `common-configs` | **Có** |

Model + DAO mới:

| File | Nội dung |
|---|---|
| `internal/model/mg/view_anomaly_alert.go` | `ViewAnomalyAlertRaw`, `ViewAnomalyAlertDAO` |
| `internal/module/database/mongodb/dao/view_anomaly_alert.go` | DAO theo đúng pattern các DAO hiện có |
| `internal/module/database/mongodb/collection.go` | thêm `CollectionViewAnomalyAlert = "view-anomaly-alerts"` |
| `internal/module/database/mongodb/index.go` | index cho collection mới (mục 5.2) |
| `internal/constants/email_template.go` | thêm `EmailTemplateViewAnomalyAlert` |
| `internal/module/smtp/templates/view_anomaly_alert_email.html` | file HTML mẫu bàn giao AccessTrade |

---

## 3. Kiểu dữ liệu cốt lõi

### 3.1 Finding

```go
// Bảy loại alert của vòng 2. Giá trị chuỗi đi thẳng vào Fingerprint và vào
// email, nên KHÔNG được đổi sau khi đã chạy production — đổi là mọi cooldown
// đang có bị vô hiệu và alert cũ bắn lại hàng loạt.
const (
    AlertRewardMissing    = "reward_missing"     // C1
    AlertMilestoneMissing = "milestone_missing"  // E4
    AlertVendorOutage     = "vendor_outage"      // A6
    AlertRewardLag        = "reward_lag"         // C4, E3
    AlertViewDuplicated   = "view_duplicated"    // B2
    AlertCallbackEmpty    = "callback_empty"     // A2
    AlertCrawlNoResponse  = "crawl_no_response"  // A3 — đổi tên từ crawl_not_queued 14/08, xem mục 4.7
)

const (
    SeverityHigh   = "high"    // vendor_outage, view_duplicated, reward_missing
    SeverityMedium = "medium"  // milestone_missing, reward_lag
    SeverityLow    = "low"     // callback_empty, crawl_no_response
)

// Finding là một phát hiện bất thường. Thuần dữ liệu, không có phương thức
// chạm I/O.
type Finding struct {
    Kind     string
    Severity string

    // Các mã định danh — dùng cả cho Fingerprint lẫn cho email.
    Event   modelmg.AppID
    Content modelmg.AppID    // Zero với alert dạng cụm và với milestone_missing
    User    modelmg.AppID    // Zero với alert dạng cụm
    Source  string           // nền tảng, chỉ có ở vendor_outage
    Date    time.Time        // ngày dữ liệu bị nghi vấn, đã chuẩn hoá về 00:00 HCM

    // Số liệu đem ra so — ý nghĩa tuỳ Kind, mô tả ở bảng mục 4.
    Expected float64
    Actual   float64

    // AffectedContents / AffectedUsers chỉ khác 0 ở finding dạng cụm.
    AffectedContents int
    AffectedUsers    int

    // Detail là câu giải thích ngắn, đi nguyên văn vào email.
    Detail string
}
```

### 3.2 Fingerprint — hợp đồng chống bắn lặp

```go
// Fingerprint là danh tính của một sự cố, KHÔNG phải của một lần phát hiện.
// Hai lần quét khác nhau thấy cùng một sự cố phải cho ra cùng một chuỗi.
//
// Vì vậy Fingerprint cố ý KHÔNG chứa Expected/Actual: số view của một content
// hỏng vẫn nhích lên mỗi ngày, nếu đưa vào vân tay thì cooldown không bao giờ
// khớp và alert bắn lại mỗi ngày — đúng thứ cơ chế này sinh ra để chặn.
func (f Finding) Fingerprint() string
```

Thành phần theo từng loại:

| Kind | Vân tay gồm |
|---|---|
| `reward_missing` | kind + content + date |
| `milestone_missing` | kind + event + user + ngưỡng mốc |
| `vendor_outage` | kind + source |
| `reward_lag` | kind + event |
| `view_duplicated` | kind + content + date |
| `callback_empty` | kind + content |
| `crawl_no_response` | kind + content |

**Bốn kind không có date** — `vendor_outage`, `reward_lag`, `callback_empty`, `crawl_no_response`. Đây là sự cố trạng thái kéo dài, không phải sự cố của một ngày. Đưa date vào là bắn lại mỗi ngày: một sự cố vendor ba ngày sẽ gửi ba email giống hệt nhau.

### 3.3 Report

```go
type Report struct {
    ScannedAt   time.Time
    Groups      []FindingGroup  // một nhóm mỗi Kind, đã sắp theo Severity
    TotalFound  int             // tổng phát hiện TRƯỚC khi cắt
    TotalShown  int             // số dòng thực sự vào email
    Suppressed  int             // số bị cooldown chặn
}

type FindingGroup struct {
    Kind     string
    Severity string
    Total    int
    Rows     []Finding  // đã cắt theo MaxRowsPerKind
    Omitted  int        // Total - len(Rows)
}
```

`TotalFound` và `TotalShown` tách bạch là bắt buộc: khi có sự cố diện rộng, con số thật quan trọng hơn danh sách.

---

## 4. Bảy detector

Chữ ký chung — mọi detector đều thuần, nhận dữ liệu đã nạp sẵn:

```go
type detectFn func(scope Scope, cfg AlertConfig) []Finding

// registry: thêm alert mới = thêm một phần tử. Không đụng alert cũ.
var detectors = map[string]detectFn{
    AlertRewardMissing:    detectRewardMissing,
    AlertMilestoneMissing: detectMilestoneMissing,
    // ...
}
```

`Scope` là lát dữ liệu của **một event, một lô content**, do scanner nạp:

```go
type Scope struct {
    Event    *modelmg.EventRaw
    Schemas  []*modelmg.EventSchemaRaw
    Missions map[modelmg.AppID]*modelmg.MissionRaw

    Contents  []*modelmg.ContentRaw
    Analytics map[modelmg.AppID][]*modelmg.ContentAnalyticDailyRaw  // theo content, sắp theo date tăng
    Rewards   map[modelmg.AppID][]*modelmg.EventRewardRaw           // theo content
    Callbacks map[modelmg.AppID][]*modelmg.ContentCallbackRaw       // theo content, N bản mới nhất

    // Tổng hợp mốc thưởng theo user, từ pipeline GetTotalCashRewardByContent.
    RewardedViewByUser map[modelmg.AppID]int64

    // Ranh giới thời gian, scanner tính sẵn để detector không gọi time.Now().
    Today     time.Time  // 00:00 HCM hôm nay
    LastClosed time.Time // 00:00 HCM hôm qua — ngày mới nhất được phép xét
}
```

Việc scanner tính sẵn `Today`/`LastClosed` thay vì để detector gọi `time.Now()` là điều kiện để test được: detector nhận thời gian như một tham số, test bơm ngày cố định.

### 4.1 `detectRewardMissing` (C1)

**Bất thường:** với mỗi `ContentAnalyticDailyRaw` có `View.Value > 0` và `Date <= LastClosed`, không tồn tại `EventRewardRaw` nào có `Options.ContentID == content` và `Date == analytic.Date`.

**Điều kiện tiên quyết:** `shouldExpectReward(...)` trả `expect == true`. Đây là toàn bộ giá trị của alert này.

**Bỏ qua:** ngày nằm trong cửa sổ `RewardLagCycleHours` gần nhất (chưa tới kỳ tính — đó là việc của `reward_lag`).

`Expected` = view của ngày; `Actual` = 0. `Detail` ghi rõ `"co view nhung khong sinh event_reward"`.

### 4.2 `detectMilestoneMissing` (E4) — viết lại 14/08

Đối chiếu `CheckPassSchemaTypeByViewMilestoneWithListSchema` (`internal/service/event_schema.go`):

```go
// schema: status=active, type = "by-view-milestone"
if len(s.ApplyForSources) == 0                        { skip }
if !s.Quantity.IsUnlimited && s.Quantity.Remaining<=0 { skip }
if s.Milestone == nil || s.Milestone.NumberOfView==0  { skip }

viewTotal := Σ userEvent.Statistic.<source>.View.Completed   // theo ApplyForSources
if viewTotal > float64(s.Milestone.NumberOfView) {           // > chứ không >=
    if count(event-rewards, {event, user, schema._id, status != rejected}) >= 1 { skip }
    → tạo reward mốc
}
```

**Ba sai sót của bản trước**, mỗi cái đủ làm detector vô dụng:

| Bản trước | Sự thật |
|---|---|
| ngưỡng so với `TotalViewPendingRewarded` (aggregate trên `event-rewards`) | **`user-events.statistic.<source>.view.completed`** |
| `>=` | **`>`** |
| "đã thưởng" = reward có `statistic.totalCashMilestone > 0` | **đếm theo `{event, user, schema._id, status != rejected}`** |

Kéo theo: `Scope.RewardedViewByUser` và `Scope.MilestoneRewardedUsers` bị thay bằng `Scope.UserEventViews` (`map[user]map[source]float64`) và `Scope.MilestoneClaimed` (`map[{user, schema}]bool`).

Finding của detector này thuộc về **user**, không gắn content — `Finding.Content` để Zero.

### 4.3 `detectVendorOutage` (A6)

**Bất thường (dạng cụm):** trong cửa sổ `VendorWindowHours`, đếm số content có view **đứng yên hoàn toàn** (`View.Value == 0` mọi ngày trong cửa sổ, hoặc không có bản ghi), nhóm theo `Source`. Bắn khi **đồng thời** vượt cả hai ngưỡng: `>= VendorMinContents` và `>= VendorMinUsers` user phân biệt.

Yêu cầu hai ngưỡng cùng lúc là để phân biệt với A4 (token một kênh hết hạn — nhiều content nhưng **một** user).

**Đây là detector duy nhất cần dữ liệu vượt phạm vi một lô.** Xử lý ở mục 5.3.

Một `Finding` cho cả cụm, `Content`/`User` để Zero, `AffectedContents`/`AffectedUsers` mang con số thật.

### 4.4 `detectRewardLag` (C4, E3)

**Bất thường:** tổng view đã ghi nhận của một nhiệm vụ trong khoảng `[LastClosed - RewardLagCycleHours, LastClosed]` lớn hơn tổng view đã quy đổi thành `event_reward` cùng khoảng, và khoảng chênh đó **đã quá** `RewardLagCycleHours`.

Gộp theo nhiệm vụ, không theo content: job hỏng thì hỏng cả nhiệm vụ.

Detector này là **lưới bắt phần đuôi** của `reward_missing`: cái kia bắt từng content cụ thể sau khi loại trừ hết nhóm D, cái này bắt tình huống job không chạy ở quy mô nhiệm vụ mà không cần loại trừ gì.

### 4.5 `detectViewDuplicated` (B2)

**Bất thường:** với chuỗi `Analytics[content]` sắp theo ngày, tính **trung vị** view của 7 ngày liền trước ngày đang xét. Bắn khi `view(d) >= median * DuplicateFactor` **và** `view(d) >= DuplicateMinView`.

Dùng trung vị chứ không dùng trung bình: một ngày đã nhảy vọt sẽ kéo trung bình lên và tự che chính nó.

**Hạn chế đã biết, ghi rõ để không ai tưởng đây là detector đáng tin:** content đang lên xu hướng tăng gấp đôi view trong một ngày là chuyện bình thường. Detector này **không phân biệt được** viral với đếm trùng. Nó là tín hiệu để người xem, không phải kết luận. Đây là detector nhiều khả năng phải hiệu chỉnh ngưỡng nhất, và là ứng viên số một để tắt riêng nếu nhiễu.

### 4.5b Vòng đời ba nhịp của `contents-callback`

Cả `callback_empty` và `crawl_no_response` đọc cùng một collection, `contents-callback`, và cả hai chỉ đúng nếu hiểu đúng vòng đời của một phiếu trong đó:

| Nhịp | Ai ghi | Vị trí trong mã | Trạng thái phiếu sau nhịp |
|---|---|---|---|
| 1. Enqueue | Crawler tạo phiếu khi bắn request | `pkg/public/service/schedule.go:2406` (`InsertContentCallback`) | `status: "processing"`, `information` rỗng, `receivedAt: nil` |
| 2. Vendor trả lời | POST inbound từ vendor | `pkg/public/service/content_callback.go:76` | set `receivedAt`, điền `information` |
| 3. Xử lý | Job `ProcessContentCallback` chạy theo giờ | — | chuyển phiếu sang trạng thái đã xử lý/thất bại |

Điểm mấu chốt cả hai detector đều dựa vào: **`receivedAt == nil` là dấu hiệu duy nhất đáng tin của "vendor chưa trả lời"**, không phải `status` — `status` còn đi qua nhiều giá trị trung gian ở nhịp 3, còn `receivedAt` chỉ được set đúng một lần ở nhịp 2.

### 4.6 `detectCallbackEmpty` (A2) — sửa 14/08

**Bất thường:** trong tối đa `callbackPerContent` (5) bản ghi `ContentCallbackRaw` mới nhất của content, đủ `CallbackEmptyStreak` bản ghi **mà vendor đã thật sự trả lời** (`hasReturned`, tức `receivedAt != nil`) liên tiếp không mang dữ liệu view (`isEmptyCallback`: `Information` rỗng, hoặc có `Information` nhưng thiếu cả bốn khoá `view`/`views`/`playCount`/`play_count`).

**Sửa so với bản gốc:** phiếu còn đang chờ vendor (`receivedAt == nil`) bị **bỏ qua hoàn toàn** khi tính chuỗi — không tính vào chuỗi rỗng, và cũng không cắt một chuỗi rỗng đang chạy. Bản gốc gọi `isEmptyCallback` trên mọi bản ghi kể cả phiếu đang chờ, và một phiếu đang chờ luôn "rỗng" theo định nghĩa đó — nên detector từng bắn vào cả vendor khoẻ mạnh nhưng trả lời chậm.

Dấu hiệu phân biệt với A1: **vẫn có** callback được trả lời. A1 thì không còn callback nào cả.

### 4.7 `detectCrawlNoResponse` (A3) — đổi tên và đổi cơ chế 14/08

**Đổi tên:** `crawl_not_queued` → `crawl_no_response`. Lý do đổi tên và hệ quả với các bản ghi cũ trên develop — xem PRD, mục "Đính chính 14/08 (tiếp)".

**Đổi cơ chế:** bản gốc dò trên content — đi từ content, tự suy luận content có "đáng được crawl hôm nay" không. Hướng đó buộc phải tái tạo lại bộ lọc của cả sáu job crawl bên trong alert, đã thử và bỏ vì quá giòn.

Bản đã triển khai đi hướng ngược lại: **quét thẳng `contents-callback`**, giống hệt `vendor_outage` là detector cấp-run, chạy **đúng một lần** ở cuối `runScan` chứ không theo từng lô content. Một phiếu còn `receivedAt: nil` tự nó là bằng chứng: nó chứng minh job crawl **đã** bắn request cho content, không cần biết content có thuộc diện crawl hôm nay hay không — phiếu đã tồn tại rồi.

**Sweep là BA bước, không phải hai:**

```go
// A) tìm nhanh các link ứng viên — link có ít nhất một phiếu còn kẹt
//    trong [LastClosed, Today)
links, _ := repo.StuckCallbackLinks(ctx, lastClosed, today)

// B) lấy lại TOÀN BỘ phiếu (kẹt và đã trả lời) của đúng các link đó,
//    trong cùng cửa sổ
callbacks, _ := repo.CallbacksByLinks(ctx, links, lastClosed, today)

// C) resolve callback -> content rồi đưa vào detectCrawlNoResponse
byLink, _ := repo.ContentsByLinks(ctx, links)
```

Vì sao không gộp A và B thành một truy vấn duy nhất trả thẳng phiếu kẹt: nếu chỉ đưa cho detector đúng tập phiếu-kẹt-theo-cấu-trúc ở bước A, thì `hasReturned` không bao giờ có cơ hội thấy `true` — một content có một request kẹt và một request khác (cùng link) đã được trả lời sẽ bị báo động giả, vì detector không thấy được cái đã trả lời. Bước B nạp lại cả hai phía để `hasReturned` phân biệt được "kẹt thật" với "chỉ là request chậm hơn request khác trên cùng link". Bước A cũng là lý do truy vấn còn nằm được trên index `{link, createdAt}` sẵn có — một lượt quét `createdAt` trần trên toàn collection không có index nào đỡ.

**Điều kiện query của bước A:** `createdAt` trong `[LastClosed, Today)` và `receivedAt: nil`.

**Vì sao link, không phải content:** `contents-callback` được đánh index theo `link`, không theo content id, và `link` là **non-unique** — hai content khác nhau (ví dụ hai partner submit cùng một URL) có thể trỏ tới cùng một link. Một request crawl phủ cả link, nên nếu nhiều content dùng chung link, phát hiện phải **lan ra hết** các content đó — không được âm thầm bỏ sót content nào. `ContentsByLinks` trả `map[string][]*ContentRaw` (nhiều content mỗi link) chính vì lý do này.

**Xử lý lỗi:** lỗi ở bất kỳ bước nào trong ba bước (`StuckCallbackLinks`, `CallbacksByLinks`, `ContentsByLinks`) làm **bỏ hẳn detector cho lượt quét đó** — không chạy tiếp với dữ liệu rỗng. Một sweep rỗng đọc y hệt "không có gì kẹt", nên nếu lỗi bị nuốt và coi như rỗng, một sự cố hạ tầng sẽ bị hiểu nhầm thành "mọi thứ ổn" đúng lúc cần cảnh báo nhất.

**Giới hạn có chủ ý:** detector này **không** phát hiện được content mà crawler chưa từng tạo phiếu nào trong `contents-callback`. Không có phiếu thì không có cách nào phân biệt "job crawl bỏ sót content" với "content này vốn không thuộc diện crawl hôm nay" — việc tái tạo bộ lọc của sáu job crawl để tự trả lời câu đó đã bị loại bỏ vì quá giòn. Đây là lỗ hổng phát hiện có thật, ghi lại để không ai đọc code rồi tưởng nó bao phủ toàn bộ A3.

**Bỏ qua khỏi kết quả:** một content mà **bất kỳ** phiếu nào trong cửa sổ đã được trả lời (`answered == true`) coi như content đó ổn — các phiếu khác còn kẹt trên cùng content không phải bằng chứng sự cố, chỉ là request enqueue quanh cái đã trả lời.

`PendingCallbacks` (field trong `Scope`) và `StuckCallbackLinks`/`CallbacksByLinks`/`ContentsByLinks` (method trong `anomalyRepo`) là tên thật trong mã — bản trước của mục này gọi sai là `PendingCallbacks` (method, hai bước). Không tồn tại method nào tên `PendingCallbacks` trong `anomalyRepo`; đó là tên field của `Scope`.

---

## 4.8 Cửa sổ nạp event — sửa 14/08

`ActiveEvents` lọc `endAt > now`, nên một event **biến mất khỏi lần quét ngay hôm sau khi nó kết thúc**.

Ghép với cutoff của `reward_missing` (chỉ xét ngày ≤ `LastClosed − RewardLagCycleHours`, tức D−2):

| Ngày quét | Event kết thúc 31/08 có được nạp? | Ngày xét được tới |
|---|---|---|
| 31/08 | có | 29/08 |
| 01/09 | **không** | — |

⇒ **30/08 và 31/08 không bao giờ được xét.** Hai ngày cuối của mọi event vĩnh viễn mù với `reward_missing` và `reward_lag` — đúng khoảng thời gian dễ hỏng nhất, khi budget cạn, schema hết hạn, và kỳ đối soát chốt số.

Cổng `event_ended` trong `shouldExpectReward` hoàn toàn đúng ở mức từng ngày, nhưng **không bao giờ được gọi** vì event đã bị loại ở tầng nạp. Cổng đúng, tầng nạp sai.

### Cách sửa

Thêm **hàm mới** `ActiveEventsInWindow(ctx, since)` thay vì đổi `ActiveEvents` — giữ nguyên ngữ nghĩa hàm cũ cho bất kỳ chỗ nào khác dùng tới:

```go
"status":  constants.StatusActive,
"startAt": bson.M{"$lte": time.Now()},
"endAt":   bson.M{"$gt": since},        // since = LastClosed - LookbackDays
```

Event kết thúc trong cửa sổ lookback vẫn được nạp; ngày sau `endAt` vẫn bị `event_ended` loại. **Không nới lỏng ngữ nghĩa, chỉ ngừng cắt sớm.**

`status: active` giữ nguyên: `EventRaw.IsValid()` kiểm tra status **và** cửa sổ ngày cùng lúc, nghĩa là status không tự đổi khi event kết thúc — nếu có thì vế ngày đã thừa.

---

## 5. Cổng loại trừ — viết lại 14/08

> **Bản trước của mục này sai từ gốc.** Nó mô tả cổng dựa trên `missions`, trong khi luồng sinh thưởng theo view không đọc `missions` ở bất kỳ đâu. Hệ quả: nhánh `mission_not_by_view` đứng đầu tiên nuốt toàn bộ, làm 4/7 detector vô hiệu. Trace trên develop xác nhận 8/8 content-ngày bị loại vì lý do đó.

### 5.1 Nguồn sự thật

`UpdateRewardTypeByStatisticContent` (`internal/service/event_schema.go`) là đường **duy nhất** tạo reward theo view:

```go
schemas := EventSchemaDAO().Find({
    "event":           event.ID,
    "status":          constants.StatusActive,
    "type":            constants.EventSchemaTypeByStatistic,   // "by-statistic"
    "applyForSources": content.Source,                          // array-contains
})
if len(schemas) == 0 { return }

for _, schema := range schemas {
    if !schema.Quantity.IsUnlimited && schema.Quantity.Remaining <= 0 { continue }
    if doc.Date.Before(schema.StartAt) || doc.Date.After(schema.EndAt) { continue }
    processRewardForSchema(...)   // LUÔN ghi bản ghi
}
```

Ba điều luồng này **không** làm:

| Không làm | Bằng chứng |
|---|---|
| Đọc `missions` | không xuất hiện trong hàm |
| Bỏ qua khi hết budget | `processRewardForSchema` nhánh `maxCash <= 0` gọi `upsertOverflowReward` — ghi doc `Cash: 0`, `IsBudgetExceeded: true`, **có `Options.ContentID`** |
| Bỏ qua theo trạng thái content | `switch content.Status` chỉ gán trạng thái cho **reward**, kể cả `rejected` |

Loại trừ theo bất kỳ điều nào ở trên là **giấu bug thật sau phán quyết "đúng thiết kế"**.

### 5.2 Chữ ký

```go
type ExcludeReason string

const (
    ExcludeEventEnded        ExcludeReason = "event_ended"
    ExcludeNoMatchingSchema  ExcludeReason = "no_matching_schema"
    ExcludeOutOfSchemaWindow ExcludeReason = "out_of_schema_window"
    ExcludeCapReached        ExcludeReason = "cap_reached"
)

func shouldExpectReward(
    event *modelmg.EventRaw,
    schemas []*modelmg.EventSchemaRaw,
    content *modelmg.ContentRaw,
    date time.Time,
) (bool, ExcludeReason)
```

Tham số `mission` bị bỏ hoàn toàn. Hàm vẫn **thuần** và vẫn trả lý do.

### 5.3 Thứ tự

1. `event == nil || content == nil` → `no_matching_schema`
2. `event.EndAt` trước `date` → `event_ended`
3. `matchingStatisticSchemas` rỗng → `no_matching_schema`
4. Duyệt schema khớp: bỏ schema ngoài cửa sổ; gặp schema **còn cap** → `expect = true`
5. Không schema nào trong cửa sổ → `out_of_schema_window`
6. Có trong cửa sổ nhưng đều cạn → `cap_reached`

### 5.4 Điểm tinh tế — "bất kỳ", không phải "tất cả"

Luồng thật **bỏ qua schema cạn rồi thưởng qua schema còn lại**. Nên cổng trả `expect = true` khi **có ít nhất một** schema sống sót cả hai bộ lọc.

Bản trước làm ngược — loại trừ khi *bất kỳ* schema nào cạn — và điều đó làm im lặng những trường hợp thiếu thưởng thật.

### 5.5 `matchingStatisticSchemas`

Cùng vị từ với truy vấn Mongo của luồng thật: `status = active`, `type = by-statistic`, `applyForSources` chứa `content.Source`.

`ApplyForSources` rỗng **khớp với không gì cả** — luồng thật truyền `content.Source` vào truy vấn dưới dạng array-contains, còn luồng mốc nói thẳng bằng `if len(s.ApplyForSources) == 0 { return }`.

## 6. Tầng scanner

### 6.1 Chiến lược quét

Theo đúng pattern các job hiện có trong `shedule.go`: cursor theo `_id`, lô cố định, không `skip`.

```
với mỗi event có IsValid() == true:
    nạp schemas + userEventViews + milestoneClaimed của event  (một lần, giữ trong Scope)
    lastId = zero
    vòng lặp:
        contents = ContentDAO.Find({event, status: {$in: [approved, waiting_approved]}, _id: {$gt: lastId}}, limit 200, sort _id)
        nếu rỗng → thoát
        nạp theo batch contentIds:
            ContentAnalyticDailyDAO.Find({content: {$in: ids}, date: {$gte: from, $lte: LastClosed}})
            EventRewardDAO.Find({\"options.contentId\": {$in: ids}, date: {...}})
            ContentCallbackDAO — N bản mới nhất mỗi content
        chạy detector theo lô trên Scope
        lastId = contents[cuối]._id
```

Cửa sổ ngày quét: `ViewAnomalyLookbackDays` (mặc định 7), tính lùi từ `LastClosed`. Không quét lại toàn bộ lịch sử — cooldown lo phần chống lặp, không phải phạm vi quét.

`ContentsPage` lọc `status $in [approved, waiting_approved]`, không chỉ `approved`: năm trong sáu job crawl chấp nhận cả `waiting_approved`, và luồng thưởng theo thống kê (`by-statistic`) không đọc `content.status` ở đâu cả — lọc chỉ trên `approved` sẽ giấu toàn bộ content đang chờ duyệt khỏi cả bảy detector.

### 6.2 Chỉ xét ngày đã đóng

`LastClosed = util.TimeStartOfDayInHCM(time.Now()).AddDate(0,0,-1)`.

Dữ liệu của ngày đang chạy chưa đầy đủ theo định nghĩa. Mọi alert dựa trên nó là báo động giả. Đây là bất biến có test riêng.

### 6.3 Xử lý riêng cho `vendor_outage`

Detector này cần dữ liệu **vượt phạm vi một lô và vượt phạm vi một event** — nó đếm theo `Source` trên toàn hệ thống.

Giải pháp: scanner tích luỹ một bộ đếm `map[source]{contents, users map[AppID]struct{}}` **trong suốt lần quét**, và chạy `detectVendorOutage` **một lần duy nhất sau khi mọi lô đã quét xong**, thay vì mỗi lô một lần.

Đây là ngoại lệ có chủ ý so với sáu detector còn lại. Chữ ký vẫn là hàm thuần — chỉ là `Scope` truyền vào ở bước cuối chứa bộ đếm toàn cục thay vì lát một lô.

`crawl_no_response` là ngoại lệ cấp-run **thứ hai**, cùng hình dạng với `vendor_outage` nhưng vì lý do khác: nó không tích luỹ qua các lô như `vendor_outage`, mà **quét thẳng `contents-callback`** sau khi mọi lô đã chạy xong — xem mục 4.7 cho ba bước sweep và tên method thật (`StuckCallbackLinks`, `CallbacksByLinks`, `ContentsByLinks`).

### 6.4 Cô lập lỗi

```go
for kind, fn := range detectors {
    if !cfg.Enabled[kind] { continue }
    func() {
        defer func() {
            if r := recover(); r != nil {
                fmt.Println(aurora.Red("[ScanViewAnomaly] detector panic: "), kind, r)
            }
        }()
        findings = append(findings, fn(scope, cfg)...)
    }()
}
```

Một detector panic vì dữ liệu hỏng không được làm mất sáu cái còn lại. Panic được log kèm tên detector — mất một phát hiện chứ không mất cả báo cáo.

### 6.5 Khoá chống chạy chồng

Theo đúng pattern `isRunAnalyticDaily` đã có trong `shedule.go`:

```go
var isRunViewAnomaly = false
```

Job này đọc nặng hơn mọi job hiện có; chạy chồng là nhân đôi tải database.

---

## 7. Trạng thái và chống bắn lặp

### 7.1 Lược đồ collection

```go
// CollectionViewAnomalyAlert = "view-anomaly-alerts"
type ViewAnomalyAlertRaw struct {
    ID          AppID     `bson:"_id"`
    Fingerprint string    `bson:"fingerprint"`
    Kind        string    `bson:"kind"`
    Severity    string    `bson:"severity"`
    Event       AppID     `bson:"event,omitempty"`
    Content     AppID     `bson:"content,omitempty"`
    User        AppID     `bson:"user,omitempty"`
    Source      string    `bson:"source,omitempty"`
    Date        time.Time `bson:"date,omitempty"`
    Expected    float64   `bson:"expected"`
    Actual      float64   `bson:"actual"`
    Detail      string    `bson:"detail"`
    NotifiedAt  time.Time `bson:"notifiedAt"`
    HitCount    int       `bson:"hitCount"`
    CreatedAt   time.Time `bson:"createdAt"`
    UpdatedAt   time.Time `bson:"updatedAt"`
}
```

Index cần thiết:
- `{fingerprint: 1}` unique — danh tính sự cố.
- `{notifiedAt: -1}` — truy vấn cooldown.
- `{kind: 1, notifiedAt: -1}` — cho việc đọc lại lịch sử về sau.

`HitCount` tăng mỗi lần quét thấy lại sự cố kể cả khi bị cooldown chặn. Nó là thứ trả lời được câu "sự cố này tồn tại bao lâu rồi" mà cảnh báo đối soát hiện không trả lời được.

### 7.2 Logic cooldown

```go
// isSuppressed là hàm THUẦN — tách khỏi phần đọc database để test được.
func isSuppressed(last time.Time, now time.Time, cooldownHours int) bool {
    return now.Sub(last) < time.Duration(cooldownHours) * time.Hour
}
```

Mặc định `CooldownHours = 72`. Ba ngày: đủ dài để không phiền, đủ ngắn để sự cố chưa xử lý không biến mất khỏi radar.

Cooldown **không phải im lặng vĩnh viễn**. Hết khoảng lặng thì báo lại — đây là điểm khác biệt có chủ ý so với phương án "báo một lần rồi thôi".

### 7.3 Ghi trạng thái kể cả khi gửi mail hỏng

`state.Record` chạy **trước** `notifyViewAnomalies`, và không phụ thuộc kết quả gửi.

Đánh đổi có chủ ý: phát hiện sẽ không bắn lại ở lần quét kế tiếp dù admin chưa hề nhận được email. Phương án ngược lại — chỉ ghi khi gửi thành công — khiến một sự cố mail kéo dài tích tụ thành một email khổng lồ khi mail hồi phục, và đó là kịch bản tệ hơn.

Bù lại: log ghi rõ lần quét nào gửi thất bại, và `HitCount` vẫn tăng nên sự cố không biến mất khỏi dữ liệu.

---

## 8. Cấu hình ngưỡng

### 8.1 Nguồn cấu hình

Dùng collection `common-configs` đã có (`CommonConfigsRaw.Value map[string]string`), **không** thêm biến môi trường — giữ nguyên tinh thần của cảnh báo đối soát: triển khai không kèm bước cấu hình dễ quên.

Bản ghi `{name: "view_anomaly_alert"}`, `Value` là map chuỗi, parse ra:

```go
type AlertConfig struct {
    Enabled map[string]bool  // theo AlertKind — bật tắt độc lập

    LookbackDays        int      // 7
    CooldownHours       int      // 72
    MaxRowsPerKind      int      // 50
    DryRun              bool     // true khi mới triển khai

    VendorWindowHours   int      // 24
    VendorMinContents   int      // 50
    VendorMinUsers      int      // 10

    DuplicateFactor     float64  // 1.8
    DuplicateMinView    float64  // 1000

    RewardLagCycleHours int      // 24
    CallbackEmptyStreak int      // 3
    CrawlSilentDays     int      // 3 — config CHẾT, xem ghi chú dưới
}
```

Thiếu bản ghi hoặc thiếu khoá → dùng mặc định trong mã. Job không được chết vì thiếu cấu hình.

**`CrawlSilentDays` là config chết kể từ khi `crawl_no_response` đổi cơ chế 14/08.** Detector bản mới không đọc số ngày im lặng — nó chỉ cần một phiếu còn kẹt trong ngày đang xét (xem mục 4.7). Không có detector nào trong bảy cái còn đọc khoá này. Giữ nguyên trong `AlertConfig` để không phá format `common-configs` hiện có; cần dọn ở lần sau.

### 8.2 `DryRun`

Khi bật: quét đầy đủ, ghi log đầy đủ, **không gửi email và không ghi trạng thái**. Đây là chế độ bắt buộc cho giai đoạn hiệu chỉnh ngưỡng — xem mục 11.1.

### 8.3 Giá trị mặc định là điểm khởi đầu, không phải giá trị đúng

Mọi con số trong bảng trên suy ra từ tài liệu case, **chưa đối chiếu với phân bố dữ liệu thật một lần nào**. Chúng tồn tại để job chạy được, không phải để tin.

---

## 9. Gửi email

### 9.1 Người nhận

Khác cảnh báo đối soát (gửi cho admin tạo kỳ — có người chịu trách nhiệm rõ ràng). Job này chạy theo lịch, không có "người tạo".

```go
// getViewAnomalyRecipients trả email nhóm admin vận hành.
// Xác định qua vai trò trong hệ thống nhân sự, KHÔNG qua danh sách cấu hình
// riêng — lý do giống cảnh báo đối soát: không bảo trì danh sách song song
// dễ lạc hậu.
func (s scheduleImpl) getViewAnomalyRecipients(ctx context.Context) []string
```

Truy vấn `StaffDAO` theo `{isRoot: true, status: active}`, lấy `Email`, rồi đi qua `normalizeRecipients` — hàm thuần đã có sẵn từ cảnh báo đối soát (cắt khoảng trắng, bỏ rỗng, hạ chữ thường, khử trùng giữ thứ tự). **Tái sử dụng, không viết lại.**

### 9.2 Đường gửi

Y hệt cảnh báo đối soát:

```go
body := map[string]interface{}{
    "template_code": constants.EmailTemplateViewAnomalyAlert,
    "template_data": buildViewAnomalyTemplateData(payload),
    "send_tos":      recipients,
}
res, err := core.Client().SmsGatewayAction(ctx, http.MethodPost, constants.EmailSendEndpoint, nil, body, false)
```

Vẫn phải đọc `res["status"]` — API trả HTTP 200 kèm status trong thân phản hồi. Bỏ qua bước này sẽ log "đã gửi thành công" trong khi email chưa hề đi.

`formatNumber` tái sử dụng nguyên hàm đã có (quy ước Việt Nam, dấu chấm phân tách hàng nghìn).

### 9.3 Cấu trúc `template_data`

Khác cảnh báo đối soát ở chỗ **có hai cấp**: nhóm, rồi dòng trong nhóm.

```
{
  "scanned_at": "13/08/2026",
  "total_found": "127",
  "total_shown": "50",
  "suppressed":  "12",
  "groups": [
    {
      "kind": "vendor_outage",
      "kind_label": "Su co vendor dien rong",
      "severity": "high",
      "total": "1",
      "omitted": "0",
      "rows": [ { ... } ]
    }
  ]
}
```

**Cần xác nhận với AccessTrade:** template bên đó có hỗ trợ **vòng lặp lồng nhau** (mảng trong mảng) hay không. Câu hỏi này đã đặt ra ở cảnh báo đối soát cho mảng một cấp và **vẫn chưa có câu trả lời**. Nếu chỉ nhận biến phẳng, phải dựng sẵn chuỗi HTML — thay đổi gói gọn trong `buildViewAnomalyTemplateData`.

---

## 10. Kế hoạch kiểm thử

Đã thống nhất kiểm thử **toàn bộ bảy module**, bao gồm ba module chạm I/O.

### 10.1 Chi phí phát sinh: tầng trừu tượng cho test

Dự án hiện **không có** tầng mock cho truy cập database — mọi service gọi thẳng `daomongodb.XxxDAO().GetShare()`. Cảnh báo đối soát đã **không** test ba phần tương ứng chính vì lý do này.

Để test scanner, state và notify, cần đưa vào ranh giới thay thế được:

```go
// Chỉ khai báo đúng những gì scanner cần — không mock cả IDatabase.
type anomalyRepo interface {
    ActiveEvents(ctx context.Context) ([]*modelmg.EventRaw, error)
    ActiveEventsInWindow(ctx context.Context, since time.Time) ([]*modelmg.EventRaw, error)
    ContentsPage(ctx context.Context, eventID modelmg.AppID, after modelmg.AppID, limit int) ([]*modelmg.ContentRaw, error)
    AnalyticsFor(ctx context.Context, ids []modelmg.AppID, from, to time.Time) (map[modelmg.AppID][]*modelmg.ContentAnalyticDailyRaw, error)
    CallbacksFor(ctx context.Context, ids []modelmg.AppID, limitPerContent int) (map[modelmg.AppID][]*modelmg.ContentCallbackRaw, error)

    // Ba method riêng cho crawl_no_response — dùng theo đúng thứ tự ba bước
    // của mục 4.7, KHÔNG phải hai bước và KHÔNG có method nào tên
    // "PendingCallbacks" (đó là tên field trong Scope, không phải method).
    StuckCallbackLinks(ctx context.Context, from, to time.Time) ([]string, error)
    CallbacksByLinks(ctx context.Context, links []string, from, to time.Time) ([]*modelmg.ContentCallbackRaw, error)
    ContentsByLinks(ctx context.Context, links []string) (map[string][]*modelmg.ContentRaw, error)
    // ...
}

type anomalySender interface {
    Send(ctx context.Context, body map[string]interface{}) (map[string]interface{}, error)
}
```

Bản cài đặt thật bọc DAO hiện có; bản test là struct trả dữ liệu dựng sẵn.

**Nói rõ đây là chi phí thật:** interface này không có tiền lệ trong khu vực mã hiện tại, và nó là phần việc phát sinh so với cách cảnh báo đối soát đã làm. Đổi lại, alert của vòng 1 và vòng 3 về sau kiểm thử được ngay từ đầu.

### 10.2 Ma trận test

| Module | Test |
|---|---|
| `Fingerprint` | Ổn định giữa hai lần gọi; **khác nhau khi định danh khác**; **giống nhau khi chỉ Expected/Actual đổi** (bất biến cốt lõi của cooldown); nil-safe với `Mission` |
| `shouldExpectReward` | **Một test cho mỗi nhánh loại trừ** (10 nhánh), cộng nhánh "không lý do nào". Bộ test dày nhất của tính năng |
| 7 detector | Mỗi hàm: bắn đúng khi bất thường; **im lặng khi bình thường**; **im lặng khi rơi vào loại trừ**; biên ngưỡng (dưới / đúng bằng / trên); dữ liệu rỗng; chỉ xét ngày đã đóng |
| `detectMilestoneMissing` | Thêm riêng: dùng view-được-tính-thưởng chứ không dùng view thô (case Phở Cung Đình) |
| `detectViewDuplicated` | Thêm riêng: trung vị không bị chính ngày nhảy vọt kéo lên |
| Scanner | Phân trang đúng, không sót lô cuối, dừng đúng khi hết; `LastClosed` loại ngày hôm nay; **detector panic không làm chết lần quét** |
| Collector | Dedupe; gộp cụm; sắp theo severity; cắt đúng `MaxRowsPerKind` và `Omitted` đúng số còn lại |
| `isSuppressed` | Trong cooldown → chặn; sau cooldown → cho qua; đúng biên |
| State | Finding mới không bị chặn nhầm; `HitCount` tăng cả khi bị chặn |
| Notify | Cấu trúc `template_data` đủ khoá hai cấp; **danh sách rỗng là mảng rỗng chứ không phải null**; bất biến **"không phát hiện thì không chạm API"**; `DryRun` không gửi |

### 10.3 Kiểm chứng test bằng cách phá code

Áp dụng lại kỹ thuật đã dùng ở cảnh báo đối soát — cố ý phá, xác nhận test đỏ, khôi phục. Bắt buộc cho ba bất biến:

1. Gỡ một nhánh loại trừ trong `shouldExpectReward` → test nhánh đó phải đỏ.
2. Bỏ kiểm tra `isSuppressed` → test chống lặp phải đỏ.
3. Đổi `LastClosed` thành `Today` → test "chỉ xét ngày đã đóng" phải đỏ.

Test không fail được khi hành vi sai là test vô dụng. Với job cảnh báo, cái sai nguy hiểm nhất không phải "không phát hiện được" mà là "phát hiện nhầm" — nên **test phủ định quan trọng ngang test khẳng định**.

### 10.4 Prior art

Phong cách bám theo test hiện có cùng khu vực: thư viện chuẩn, không framework ngoài; tên hàm test và thông điệp lỗi viết **không dấu**; mỗi test một tình huống. Tham chiếu gần nhất là bộ test cảnh báo lệch kỳ đối soát và bộ test dựng item đối soát.

---

## 11. Triển khai

### 11.1 Thứ tự bắt buộc

1. **Chạy `DryRun` ít nhất 7 ngày.** Quét đầy đủ, chỉ ghi log, không gửi mail, không ghi trạng thái.
2. **Đếm phát hiện theo từng alert mỗi ngày.** Alert nào ra hàng nghìn dòng là ngưỡng sai, không phải hệ thống hỏng hàng nghìn chỗ.
3. **Đối chiếu mẫu bằng tay.** Lấy 10 phát hiện của `reward_missing` và `milestone_missing`, kiểm tra thủ công xem có thật là bất thường không. Đây là bài kiểm tra chất lượng của `shouldExpectReward` — thứ duy nhất chứng minh được module đó đúng.
4. **Hiệu chỉnh ngưỡng.** Sửa `common-configs`, không sửa mã.
5. **Bàn giao template.** Gửi file HTML mẫu cho AccessTrade, nhận mã, sửa đúng một dòng hằng số.
6. **Tắt `DryRun`.**

Bỏ qua bước 1–3 gần như chắc chắn dẫn tới việc Ops tắt cả job trong tuần đầu.

### 11.2 Lịch cron

```go
// Scan view anomaly — sau AuditContentAnalytic (04:00) và
// AutoRejectContentNotFound (04:30) để đọc trên dữ liệu đã ổn định.
c.AddFunc("0 0 6 * * *", service.Schedule().ScanViewAnomaly)
```

06:00 giờ Việt Nam, thấp điểm, sau khi các job dữ liệu đã xong.

### 11.3 Gộp việc bàn giao template với cảnh báo đối soát

Mã template của cảnh báo đối soát (`AMBASSADOR_EMAIL_RECONCILIATION_ALERT`) **tới nay vẫn chưa được AccessTrade cấp**. Triển khai job này mà không gộp sẽ có **hai** tính năng cùng nằm chờ cùng một thứ.

Nên gửi cả hai file HTML mẫu trong một lần, nhận cả hai mã.

### 11.4 Rủi ro tải database

Bảy alert quét toàn bộ dữ liệu view và thưởng của các event đang chạy — khối lượng đọc lớn hơn hẳn mọi job hiện có. **Chưa ước lượng được chi phí thật** cho tới khi chạy trên production.

Theo dõi thời gian chạy và tải database ở lần quét đầu. Nếu quá nặng, phương án đầu tiên là **giảm `LookbackDays`**, không phải giảm số alert.

---

## 12. Ghi chú thiết kế

### 12.1 Vì sao không gộp vào cảnh báo kỳ đối soát

Hai cơ chế bổ sung cho nhau:

- Cảnh báo kỳ đối soát: lưới an toàn cho **khâu chi tiền**, chạy tại thời điểm chi, bắt biến động giữa lúc chốt và lúc chi.
- Job này: giám sát **chất lượng dữ liệu đầu vào**, chạy theo lịch, bắt sai lệch trước khi nó đi vào kỳ đối soát.

Một sự cố nghiêm trọng kích hoạt cả hai — đó là hành vi mong muốn, hai góc nhìn về cùng một vấn đề. Không gộp email vì hai loại có người đọc khác nhau và mức khẩn khác nhau.

### 12.2 Đường mở rộng sang vòng 1 và vòng 3

Thêm alert = thêm một phần tử vào `detectors` + một hàm thuần + một bộ test.

- **Vòng 1** (đứt chuỗi lũy kế B3, cờ `totalNotFound >= 3` A1, token hết hạn A4, miss ngày B4): đều là hàm thuần trên dữ liệu đã nạp trong `Scope`. Cắm thẳng vào, không cần đổi gì khác. B3 đặc biệt rẻ — nó chỉ là kiểm tra `Analytics[content][i].View.End == Analytics[content][i+1].View.Begin`.
- **Vòng 3** cần đổi lược đồ trước (lịch sử thay đổi số liệu view cho B1, trường thời điểm hết budget cho D2), nhưng phần phát hiện vẫn cắm vào cùng chỗ.

Nếu sau này làm vòng 1, chi phí gần như chỉ còn hàm phát hiện và test — hạ tầng quét, gom, chống lặp, gửi đã có.

### 12.3 Hạn chế đã biết

- **`view_duplicated` không phân biệt được viral với đếm trùng.** Đã nêu ở 4.5. Ứng viên số một để tắt riêng.
- **Điểm mù thời điểm hết budget** làm `reward_missing` và `milestone_missing` bỏ sót một lớp bug. Đã nêu ở 5.4.
- **`vendor_outage` có thể trùng lặp với A4** (token một kênh hết hạn) khi một user có rất nhiều content. Ngưỡng `VendorMinUsers` giảm thiểu nhưng không loại bỏ hẳn.
- **Không phát hiện được B1** — ghi đè dữ liệu trễ, case phổ biến nhất trong toàn bộ [case.md](case.md) — vì không có lịch sử thay đổi số liệu để so. Đây là khoảng trống lớn nhất còn lại sau khi vòng 2 xong.
