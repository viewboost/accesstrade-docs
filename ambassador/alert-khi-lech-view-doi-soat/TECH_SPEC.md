# Tech Spec — Cảnh báo lệch số liệu kỳ đối soát qua email

**Trạng thái:** Đã triển khai — branch `hotfix/issue-view-content`, 12 commit (`d0dd15e4..fb3d122d`)
**Chưa chạy được:** đang chờ AccessTrade cấp `template_code` (xem mục 8.2)
**PRD:** [2026-08-12-reconciliation-alert-prd.md](2026-08-12-reconciliation-alert-prd.md)
**Ngày:** 2026-08-12

---

## 1. Tổng quan luồng

```
Running(rc, staffId)                        [reconciliation_running.go]
 │
 ├─ tạo mismatches := newMismatchCollector()
 │
 ├─ ants pool 50 worker ──► runCashBack(data)   × N user, SONG SONG
 │                            │
 │                            ├─ guard reward   ─┐
 │                            ├─ guard cash     ─┼─► mismatches.Add(...)  (có khoá)
 │                            └─ guard view ★   ─┘
 │
 ├─ wg.Wait()                                  ← mọi worker đã ghi xong
 ├─ cập nhật trạng thái kỳ = completed
 │
 └─ go func() {                                ← khối nền ĐÃ CÓ SẴN
      UpdateStatistic(...)
      SendCommissionToReferrer(...)
      notifyMismatches(ctx, rc, mismatches)    ★ điểm nối duy nhất
        │
        ├─ getMismatchRecipients(ctx, rc)      → tra history → staff.Email
        ├─ buildMismatchPayload(rc, items)     → định dạng số, dựng dữ liệu
        ├─ buildMismatchTemplateData(payload)  → chuyển sang shape API AT
        └─ core.Client().SmsGatewayAction(...) → POST /v1.0/partner/email/send
    }()
```

★ = phần mới thêm.

**Bất biến quan trọng:** `notifyMismatches` nằm sau `wg.Wait()` và sau khi trạng thái kỳ đã chuyển `completed`. Tiền đã chi xong hoàn toàn trước khi email được nghĩ tới.

---

## 2. Danh sách file

| File | Loại | Dòng | Trách nhiệm |
|---|---|---|---|
| `backend/pkg/admin/service/reconciliation_mismatch.go` | mới | 101 | Kiểu dữ liệu lệch, collector có khoá, điều kiện lệch view |
| `backend/pkg/admin/service/reconciliation_mismatch_test.go` | mới | 109 | Test collector + `hasViewMismatch` |
| `backend/pkg/admin/service/reconciliation_mismatch_recipient.go` | mới | 59 | Tra email admin tạo kỳ |
| `backend/pkg/admin/service/reconciliation_mismatch_recipient_test.go` | mới | 36 | Test `normalizeRecipients` |
| `backend/pkg/admin/service/reconciliation_mismatch_notify.go` | mới | 147 | Điều phối: định dạng → dựng payload → gọi API |
| `backend/pkg/admin/service/reconciliation_mismatch_notify_test.go` | mới | 157 | Test `formatNumber`, `buildMismatchPayload`, `buildMismatchTemplateData`, bất biến no-op |
| `backend/internal/module/smtp/templates/reconciliation_mismatch_email.go` | mới | 37 | Struct payload (chỉ kiểu dữ liệu, không có template) |
| `backend/internal/module/smtp/templates/reconciliation_mismatch_email.html` | mới | 176 | **File mẫu bàn giao AccessTrade**, kèm bảng mô tả biến |
| `backend/internal/constants/email_template.go` | mới | 28 | Mã template + endpoint gửi mail |
| `backend/pkg/admin/service/reconciliation_running.go` | sửa | +58/-3 | Nối collector, 3 guard, lời gọi gửi mail |
| `backend/pkg/admin/service/reconciliation.go` | sửa | +20/-0 | `GetViewRewardedByContent` |

Tổng: **928 thêm / 3 xoá**. Không đụng `env.example`, không đụng `internal/config/`, không đụng `aws.go`.

---

## 3. Chi tiết từng module

### 3.1 Module gom lệch — `reconciliation_mismatch.go`

Thuần logic, không I/O. Kiểm thử được không cần mock.

```go
const (
    MismatchKindCash   = "cash"   // tiền chốt ≠ tiền tính lại
    MismatchKindView   = "view"   // view thưởng chốt ≠ view thưởng tính lại
    MismatchKindReward = "reward" // bản ghi thưởng mốc không hợp lệ để chi
)

type ReconciliationMismatch struct {
    ItemID   modelmg.AppID
    UserID   modelmg.AppID
    ItemType string
    Kind     string
    Note     string   // nguyên văn note đã ghi vào DB
    Expected float64  // giá trị chốt lúc tạo kỳ
    Actual   float64  // giá trị tính lại lúc chi
}

func (m ReconciliationMismatch) Diff() float64 { return m.Actual - m.Expected }

type mismatchCollector struct {
    mu    sync.Mutex
    items []ReconciliationMismatch
}

func newMismatchCollector() *mismatchCollector
func (c *mismatchCollector) Add(m ReconciliationMismatch)  // nil-tolerant
func (c *mismatchCollector) All() []ReconciliationMismatch // nil-tolerant, trả BẢN SAO
func (c *mismatchCollector) Len() int                      // nil-tolerant

func hasViewMismatch(expected, actual int64) bool { return expected != actual }
```

**Hai quyết định đáng lưu ý:**

`All()` trả **bản sao** (`make` + `copy`), không trả thẳng slice nội bộ. Nếu trả thẳng, bên gọi đọc trong lúc goroutine khác vẫn `append` sẽ là tranh chấp dữ liệu.

Cả ba method **chịu được receiver nil**: `Add`/`All`/`Len` đều kiểm tra `c == nil` và thoát êm; `All()` trả slice rỗng chứ không nil để bên gọi `range`/`len` không cần kiểm tra thêm. Lý do: các method này nằm trong đường chi tiền. Hiện chỉ có một nơi khởi tạo `UserReconciliation{...}` và nó luôn gán `Mismatches`, nhưng một điểm khởi tạo mới trong tương lai quên gán sẽ panic giữa lúc trả tiền người dùng.

### 3.2 Module tra người nhận — `reconciliation_mismatch_recipient.go`

```go
func normalizeRecipients(emails []string) []string   // thuần
func (r reconciliationImpl) getMismatchRecipients(ctx context.Context, rc *modelmg.ReconciliationRaw) []string
```

`ReconciliationRaw` **không có** trường người tạo. Đường truy ngược:

```
rc.ID
 └─► reconciliation_history { reconciliation: rc.ID, type: "create" }
      └─► .Author  (staff ID)
           └─► staff.FindById
                └─► StaffRaw.Email
```

Hằng dùng: `constants.ReconciliationHistoryTypeCreate` (giá trị `"create"`).

Bản ghi lịch sử này được ghi tại `Create()`:
```go
go r.CreateHistory(ctx, constants.ReconciliationHistoryTypeCreate, b, r.Staff.ID, ...)
```

**Bẫy cần biết:** `StaffInfo` — struct được truyền quanh trong tầng service qua `r.Staff` — **không** có trường Email. Chỉ `StaffRaw` mới có. Bắt buộc `FindById` sang collection staff.

`normalizeRecipients` chuẩn hoá: `TrimSpace` → bỏ chuỗi rỗng → `ToLower` → khử trùng, **giữ nguyên thứ tự xuất hiện đầu tiên**.

Không tra được (history không tồn tại / staff không tồn tại / email rỗng) → trả `[]string{}`. Không lỗi, không panic.

### 3.3 Guard trong luồng chi tiền — `reconciliation_running.go`

Struct dùng chung cho cả phiên:

```go
type UserReconciliation struct {
    User           modelmg.AppID
    Reconciliation *modelmg.ReconciliationRaw
    Items          []*modelmg.ReconciliationItemRaw
    Mismatches     *mismatchCollector `json:"-"`  // MỚI
}
```

Ba guard, cùng một khuôn: ghi nhận → đánh dấu item `rejected` → `continue`.

| # | Vị trí | Điều kiện | Kind | Expected | Actual | Note |
|---|---|---|---|---|---|---|
| 1 | Milestone | `ID.IsZero() \|\| Status != Pending \|\| Cash != TotalCash` | `reward` | `item.TotalCash` | `eventReward.Cash` | "Thông tin thưởng không chính xác" |
| 2 | Content | `totalCashPending != item.TotalCash` | `cash` | `item.TotalCash` | `totalCashPending` | "Số tiền thưởng không hợp lệ" |
| 3 ★ | Content | `hasViewMismatch(...)` | `view` | `item.Content.TotalViewPendingRewarded` | `GetViewRewardedByContent(...)` | "Lượt xem được tính thưởng không hợp lệ" |

**Guard 1 và 2 giữ nguyên điều kiện, không đổi một ký tự.** Đã kiểm chứng bằng cách trích dòng điều kiện từ commit trước và `diff` — kết quả identical. Thay đổi duy nhất là hoist chuỗi note thành `const note` rồi dùng cho cả bản ghi DB lẫn collector, bảo đảm email và database không bao giờ nói khác nhau.

**Guard 3 đặt sau guard 2, trước `payload.Action = ...`** — item bị loại trước khi bất kỳ giá trị nào chạm cashflow hoặc notification.

Số liệu đối chứng trong `runCashBack`:

| | Trước | Sau |
|---|---|---|
| `continue` | 4 | 5 |
| `StatusRejected` | 3 | 4 |
| `Mismatches.Add` | 0 | 3 |

Nhánh `case ReconciliationItemTypeBonus` **không bị đụng** (đã `diff` xác nhận).

### 3.4 `GetViewRewardedByContent` — `reconciliation.go`

```go
func (r reconciliationImpl) GetViewRewardedByContent(ctx context.Context, cond bson.M) int64
```

Bám đúng khuôn `GetCashByContent` ở cùng file: cùng DAO, cùng pipeline `GetTotalCashRewardByContent`, `len(data) == 0` → `0`, lỗi → `0`. Khác duy nhất là đọc trường `TotalViewPendingRewarded` thay vì `TotalCashPending`.

**Vì sao hai vế của phép so là đồng nghĩa** — đây là điểm rủi ro nhất, đã truy nguồn thật để xác nhận:

| Vế | Nguồn |
|---|---|
| `Expected` — chốt lúc tạo kỳ | `buildReconciliationItemContent` gán `TotalViewPendingRewarded: int64(item.TotalViewPendingRewarded)` từ `aggregatepipeline.TotalCashRewardByContent` |
| `Actual` — tính lại lúc chi | `GetViewRewardedByContent` trả `int64(data[0].TotalViewPendingRewarded)` từ **cùng** pipeline |

Trường nguồn có **một định nghĩa duy nhất** trong `aggregate_pipeline/event_reward.go`:
```go
"totalViewPendingRewarded": SumWhere("$statistic.totalView", StatusPending, BudgetRewarded)
```

Cùng pipeline, cùng trường, cùng phép ép `float64 → int64`. Không có nguy cơ so float với int, cũng không có nguy cơ so "rewarded" với "pending".

### 3.5 Kiểu dữ liệu email — `reconciliation_mismatch_email.go`

Package `emailtemplates`. Sau khi chuyển sang API AccessTrade, file này **chỉ còn kiểu dữ liệu** — không còn hằng template, không còn hàm kết xuất, vì nội dung email nằm ở hệ thống AccessTrade.

```go
type MismatchRow struct {
    ItemID, UserID, ItemType, Kind, Note, Expected, Actual, Diff string
}

type ReconciliationMismatchTemplatePayload struct {
    ReconciliationID, ReconciliationTitle string
    PeriodFrom, PeriodTo                  string
    TotalMismatch                         int
    Rows                                  []MismatchRow
    Year, Company                         string
}
```

Mọi trường đều là `string` đã định dạng sẵn.

### 3.5b File mẫu bàn giao — `reconciliation_mismatch_email.html`

**Đây là hiện vật bàn giao, không phải mã chạy.** Gửi file này cho team AccessTrade để họ setup template.

176 dòng: một khối comment mở đầu liệt kê **7 biến cấp email** và **8 biến cấp dòng** kèm ý nghĩa từng biến, sau đó là HTML mẫu dùng cú pháp Go template (`{{.Ten}}`, `{{range .Rows}}`).

Comment ghi rõ hai điều quan trọng cho bên nhận: cú pháp biến có thể đổi theo hệ thống của họ miễn giữ nguyên danh sách biến, và **số dòng trong bảng không cố định** — phụ thuộc số item lệch của từng kỳ.

### 3.6 Hằng mã template — `internal/constants/email_template.go`

```go
const (
    EmailTemplateOTPVerification     = "AMBASSADOR_EMAIL_OTP_VERIFICATION"
    EmailTemplateReconciliationAlert = "AMBASSADOR_EMAIL_RECONCILIATION_ALERT"
)

const EmailSendEndpoint = "/v1.0/partner/email/send"
```

`EmailTemplateOTPVerification` là mã **đã được AccessTrade cấp** và đang chạy thật — trước đây viết thẳng trong `internal/service/otp.go`, nay gom về đây.

`EmailTemplateReconciliationAlert` **chưa được cấp**. Giá trị hiện tại đặt theo quy ước đặt tên của mã OTP. Khi nhận được mã thật, sửa đúng một dòng này.

### 3.7 Điều phối gửi — `reconciliation_mismatch_notify.go`

```go
func formatNumber(v float64) string
func buildMismatchPayload(rc *modelmg.ReconciliationRaw, items []ReconciliationMismatch) emailtemplates.ReconciliationMismatchTemplatePayload
func buildMismatchTemplateData(payload emailtemplates.ReconciliationMismatchTemplatePayload) map[string]interface{}
func (r reconciliationImpl) notifyMismatches(ctx context.Context, rc *modelmg.ReconciliationRaw, c *mismatchCollector)
```

**`formatNumber`** — phân tách hàng nghìn bằng dấu chấm, cắt phần thập phân.

Chi tiết tinh tế: `n := int64(v)` thực hiện **trước** `neg := n < 0`. Nếu đảo thành `v < 0` thì `-0.9` sẽ ra `"-0"`. Đã probe 18 giá trị biên (0, ±0.9, ±1, 999, 1000, ±1200, 999999, 10⁶, 10⁹) — tất cả đúng.

**`buildMismatchPayload`** — ánh xạ đủ 8 trường `ReconciliationMismatch` → `MismatchRow`, `TotalMismatch = len(items)`. Guard `rc.Conditions != nil` vì đó là con trỏ, có thể nil ở dữ liệu cũ.

**`buildMismatchTemplateData`** — chuyển payload sang `template_data` mà API AccessTrade nhận. Khoá dùng `snake_case` cho khớp quy ước của payload OTP sẵn có:

```go
{
  "reconciliation_id":    "...",
  "reconciliation_title": "...",
  "period_from":          "01/07/2026",
  "period_to":            "31/07/2026",
  "total_mismatch":       "12",          // chuỗi, không phải số
  "year":                 "2026",
  "company":              "AccessTrade",
  "rows": [
    {"item_id":"...", "user_id":"...", "item_type":"content",
     "kind":"cash", "note":"...", "expected":"1.000", "actual":"800", "diff":"-200"},
    ...
  ]
}
```

Hai quyết định: `total_mismatch` là **chuỗi** cho khớp kiểu của `template_data` OTP; `rows` luôn là **mảng rỗng chứ không nil** để không serialize thành `null`.

**`notifyMismatches`** — không trả về giá trị, nên lỗi **không thể** rò ra luồng đối soát. Bốn nhánh thoát, tất cả log rồi `return`:

| Nhánh | Log |
|---|---|
| `c == nil \|\| c.Len() == 0` | (im lặng) |
| `len(recipients) == 0` | vàng — kèm số item lệch |
| `SmsGatewayAction` trả lỗi | đỏ — kèm nội dung lỗi |
| `res["status"] != "success"` | đỏ — kèm nguyên văn phản hồi |
| thành công | xanh — kèm số item |

**Nhánh thứ tư đáng lưu ý:** API trả HTTP 200 kèm trạng thái nằm trong thân phản hồi. Bỏ qua bước đọc `status` sẽ dẫn tới ghi log "đã gửi thành công" trong khi email chưa hề đi. Cách xử lý này khớp với `SendOTPEmailAccessTrade` sẵn có.

Hai guard đầu return **trước** khi gọi `getMismatchRecipients`, nên "không lệch thì không chạm DB/API" là bất biến có test khoá.

Tham số `isDebug` truyền `false` — khác `SendOTPEmailAccessTrade` (truyền `true`) — vì cảnh báo chạy nền theo kỳ, không cần dump toàn bộ request/response vào log mỗi lần.

Thông điệp log viết **không dấu** (quy ước dự án); comment trong code viết **có dấu** tiếng Việt.

---

## 4. An toàn đa luồng

`Running` chạy `runCashBack` qua `ants.NewPoolWithFunc(50, ...)`. Biến chia sẻ duy nhất mới là `mismatches`, tạo một lần và truyền qua trường `Mismatches` vào cả 50 worker.

Các biến còn lại trong `runCashBack` (`payloadCashFlow`, `wRcItem`, `w`, `wEventBonus`, `notificationPayloads`) đều **cục bộ mỗi lời gọi**, không chia sẻ.

`data.Reconciliation` (`*rc`) đã được chia sẻ qua 50 worker **từ trước** thay đổi này, chỉ đọc — không phải vấn đề mới.

Kiểm chứng: test 200 goroutine ghi song song, chạy `-race`, sạch.

---

## 5. Kiểm thử

**28 test mới**, tất cả ở `pkg/admin/service`. Chạy cùng các test có sẵn của package thì tổng là 37, đều xanh.

```bash
cd backend
go test ./pkg/admin/service/ -race -vet=off -count=1          # 37 pass (28 mới + 9 có sẵn)
go build ./cmd/...                                            # 3 binary, sạch
```

Package `internal/module/smtp/templates` nay không còn test — 5 test kết xuất mẫu bị gỡ cùng hàm render khi chuyển sang API AccessTrade. Thay bằng 4 test cho `buildMismatchTemplateData` ở `pkg/admin/service`, kiểm chứng cấu trúc `template_data` gửi lên API.

### Hai test được chứng minh có "răng"

Trong quá trình triển khai, hai test được kiểm chứng bằng cách **cố ý phá code rồi xác nhận test đỏ**, sau đó khôi phục:

| Test | Cách phá | Kết quả |
|---|---|---|
| `TestCollector_NilReceiverIsSafe` | gỡ `if c == nil` trong `Add` | panic `invalid memory address` |
| `TestNotifyMismatches_NoItemsIsNoop` | đảo `getMismatchRecipients` lên trước guard | panic nil pointer |

Đây là tiêu chuẩn nên áp dụng cho test tương lai trong vùng này.

### Không có test

- `getMismatchRecipients` — thuần I/O, cần Mongo thật hoặc tầng mock chưa tồn tại trong dự án.
- `runCashBack` và các guard — phụ thuộc DAO Mongo toàn cục, không unit-test được nếu không tái cấu trúc. Ngoài phạm vi.

---

## 6. Môi trường build — ba lỗi CÓ SẴN

Không do thay đổi này gây ra. Ghi lại để người sau khỏi mất thời gian:

| # | Triệu chứng | Cách đi vòng |
|---|---|---|
| 1 | `go build ./...` fail: `function main is undeclared in the main package` — thư mục gốc `backend/` có file `package main` thiếu `func main()` | Dùng `go build ./cmd/...` |
| 2 | `go test ./pkg/admin/service/` fail ở **bước vet** do hàng chục lỗi `primitive.E struct literal uses unkeyed fields` ở `migration.go`, `export*.go`… | Thêm cờ `-vet=off` |
| 3 | `TestBuildDuplicateCheckFilter_*` ở `pkg/public/service` fail | Đã chứng minh fail y hệt tại commit gốc `d0dd15e4` bằng worktree — không phải hồi quy |

`gofmt` cũng báo bẩn ở `pkg/admin/service/common_configs.go` — file này không thuộc diff. Toàn bộ 11 file của thay đổi đều gofmt sạch.

---

## 7. Biến môi trường

**Không thêm biến nào.** Đã xác nhận: `git diff d0dd15e4..HEAD -- backend/env.example backend/internal/config/` trả về trống.

Dùng lại nhóm biến kết nối AccessTrade **đã có sẵn và đang chạy thật** cho email OTP:

```
ACCESS_TRADE_SMS_END_POINT
ACCESS_TRADE_SMS_ACCESS_KEY
ACCESS_TRADE_SMS_SECRET_KEY
ACCESS_TRADE_SMS_CHANNEL
```

Xác thực do `core.Client().SmsGatewayAction` lo: nó tự sinh `client-signature` từ access key + secret key + trace no + request time. Không cần thêm gì ở tầng gọi.

Nhóm biến `SMTP_AWS_SES_*` **không còn liên quan** tới tính năng này.

---

## 8. Rủi ro triển khai

### 8.1 Guard view thay đổi hành vi trả tiền — RỦI RO CAO NHẤT

`hasViewMismatch` là `expected != actual`, **không dung sai**. Item bị loại là item **không được trả tiền**.

Nếu lượt xem có biến động lành tính giữa lúc chốt kỳ và lúc chi, kỳ chạy đầu sau triển khai có thể loại nhiều item hơn dự kiến.

**Hành động bắt buộc:** theo dõi sát tỉ lệ item `rejected` ở kỳ đối soát đầu tiên, đối chiếu với các kỳ trước.

### 8.2 Chưa có `template_code` thật — TÍNH NĂNG CHƯA GỬI ĐƯỢC EMAIL

`EmailTemplateReconciliationAlert` hiện là `"AMBASSADOR_EMAIL_RECONCILIATION_ALERT"` — giá trị đặt theo quy ước, **chưa tồn tại bên AccessTrade**. Mọi lời gọi sẽ bị từ chối ở nhánh `res["status"] != "success"`.

Việc này được chặn tốt (log rồi đi tiếp, không ảnh hưởng chi tiền), nhưng nghĩa là **cho tới khi hoàn tất bàn giao, cảnh báo chỉ tồn tại dưới dạng dòng log.**

**Các bước theo thứ tự:**

1. Gửi `internal/module/smtp/templates/reconciliation_mismatch_email.html` cho team AccessTrade.
2. Thống nhất với họ: template bên đó có hỗ trợ **vòng lặp trên mảng** không? `template_data.rows` là mảng đối tượng vì số dòng lệch không cố định. Nếu hệ thống bên đó chỉ nhận biến phẳng, phải đổi sang đẩy một chuỗi HTML dựng sẵn — thay đổi gói gọn trong `buildMismatchTemplateData`.
3. Nhận mã template, cập nhật hằng `EmailTemplateReconciliationAlert` — đúng một dòng.
4. Chạy thử ở dev, `grep "\[notifyMismatches\]"` trong log để xác nhận nhánh thành công.

### 8.3 Hạ tầng SMTP nay là mã chết

Bản triển khai đầu của tính năng này dùng SMTP, sau đó chuyển sang API AccessTrade cho nhất quán với email OTP. Sau khi chuyển:

```
intenralsmtp.SendEmail          → 0 call site trong toàn repo (như trước khi có tính năng này)
verify_email.go                 → chỉ struct payload được dùng; template HTML không ai dùng
Email OTP thật                  → internal/service/otp.go, gọi API AccessTrade
                                   template_code: EmailTemplateOTPVerification
```

`aws.go` đã được đưa về **nguyên trạng** — `git diff` với commit gốc trả về trống.

Nên cân nhắc dọn hẳn phần SMTP ở một thay đổi riêng, để người sau không nhầm tưởng đó là kênh gửi mail đang hoạt động.

---

## 9. Nợ kỹ thuật đã ghi nhận

| # | Vấn đề | Mức | Ghi chú |
|---|---|---|---|
| 1 | Guard `reward` gộp 3 nguyên nhân nhưng luôn báo `Actual = eventReward.Cash`. Khi bản ghi không tồn tại thì hiện `Actual = 0` → admin có thể hiểu nhầm là "lệch tiền" | Minor | Note nguyên văn cứu vãn phần nào |
| 2 | `formatNumber` cắt cụt thập phân → lệch cash < 1 đồng hiện "Chênh 0" | Minor | Xác suất thấp, đã tuyên bố chủ ý trong comment |
| 3 | `GetViewRewardedByContent` chạy lại đúng pipeline `GetCashByContent` vừa chạy → gấp đôi aggregate query mỗi content item × 50 worker | Minor | Đúng chủ ý (cùng lát cắt dữ liệu). Gộp được sau mà không đổi ngữ nghĩa. **Theo dõi tải Mongo.** |
| 4 | `Year` dùng `time.Now()` giờ máy chủ (UTC) thay vì giờ VN | Minor | Chỉ ảnh hưởng dòng bản quyền |
| 5 | `Company` hard-code `"AccessTrade"` | Minor | Nhất quán với subject vốn cũng hard-code |
| 6 | `FindOne` không sort khi tra history `type=create` | Không phải gap | `Create()` chỉ gọi `CreateHistory` một lần; trùng lặp chỉ xảy ra nếu dữ liệu hỏng, và khi đó vẫn cùng `Author` |
| 7 | `GetCashByContent` log sai tên DAO (`"Aggregate ContentFlowDAO err"` trong khi DAO thật là EventReward) | Minor | Lỗi có sẵn từ trước |
| 8 | `verify_email.go:195` còn `panic(err)` | Minor | Mã chết, đã thống nhất không sửa trong phạm vi này |
| 9 | Cấu trúc `template_data` chưa được AccessTrade xác nhận, đặc biệt là mảng lồng cho `rows` | **Chặn chạy thật** | Xem mục 8.2 |
| 10 | Nội dung hiển thị email nằm ngoài repo, không test được | Chấp nhận | Đánh đổi khi dùng template phía AccessTrade |

---

## 10. Lịch sử commit

```
fb3d122d  refactor(reconciliation): gửi email cảnh báo qua API AccessTrade thay vì SMTP
e603507d  fix(reconciliation): chuan hoa log khong dau va them test bat bien notifyMismatches
f2564b3b  feat(reconciliation): gửi email tổng hợp cảnh báo lệch số liệu cuối phiên đối soát
446d2e4b  feat(email): thêm template cảnh báo lệch số liệu đối soát
1af57c60  fix(reconciliation): cho mismatchCollector chiu duoc receiver nil de khong sap luong chi tien
7f0ae473  feat(reconciliation): ghi nhận lệch cash và thêm guard lệch view thưởng khi chạy đối soát
9f06e9cd  feat(reconciliation): them dieu kien phat hien lech view thuong
7d335dfb  feat(reconciliation): thêm collector thread-safe gom lệch số liệu
ac57c3d1  feat(reconciliation): tra email admin đã tạo kỳ để gửi cảnh báo lệch
a5468a54  Revert "feat(config): thêm cấu hình email cảnh báo cho admin"
8fe3da70  feat(smtp): thêm SendEmailToMany để gửi email cho nhiều người nhận
ca5e6b33  feat(config): thêm cấu hình email cảnh báo cho admin
```

Hai lần đổi hướng giữa chừng, đều do yêu cầu nghiệp vụ chứ không phải sửa lỗi:

- `ca5e6b33` + `a5468a54` — bản thiết kế đầu dùng danh sách email cấu hình qua env, sau đó đổi sang tra admin tạo kỳ nên revert nguyên vẹn.
- `8fe3da70` + `446d2e4b` → `fb3d122d` — bản đầu gửi qua SMTP với template render trong repo, sau đó chuyển sang API AccessTrade. `fb3d122d` gỡ phần SMTP thừa và đưa `aws.go` về nguyên trạng.
