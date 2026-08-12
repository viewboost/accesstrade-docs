# Tech Spec — Cảnh báo lệch số liệu kỳ đối soát qua email

**Trạng thái:** Đã triển khai — branch `hotfix/issue-view-content`, 11 commit (`d0dd15e4..e603507d`)
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
        ├─ GetReconciliationMismatchTemplate() → kết xuất HTML + plain text
        └─ SendEmailToMany(recipients, ...)    → SMTP
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
| `backend/pkg/admin/service/reconciliation_mismatch_notify.go` | mới | 101 | Điều phối: định dạng → dựng payload → gửi |
| `backend/pkg/admin/service/reconciliation_mismatch_notify_test.go` | mới | 100 | Test `formatNumber`, `buildMismatchPayload`, bất biến no-op |
| `backend/internal/module/smtp/templates/reconciliation_mismatch_email.go` | mới | 224 | Mẫu HTML + plain text, hàm kết xuất |
| `backend/internal/module/smtp/templates/reconciliation_mismatch_email_test.go` | mới | 93 | Test kết xuất mẫu |
| `backend/pkg/admin/service/reconciliation_running.go` | sửa | +58/-3 | Nối collector, 3 guard, lời gọi gửi mail |
| `backend/pkg/admin/service/reconciliation.go` | sửa | +20/-0 | `GetViewRewardedByContent` |
| `backend/internal/module/smtp/aws.go` | sửa | +14/-3 | `SendEmailToMany` |

Tổng: **915 thêm / 6 xoá**. Không đụng `env.example`, không đụng `internal/config/`.

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

### 3.5 Mẫu email — `reconciliation_mismatch_email.go`

Package `emailtemplates`. Bám quy ước của `verify_email.go` (mẫu email duy nhất có sẵn):

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

const ReconciliationMismatchTemplateSubject   = "[AccessTrade] Cảnh báo lệch số liệu đối soát"
const ReconciliationMismatchTemplatePlainText = `...`
const ReconciliationMismatchTemplate          = `...`

func GetReconciliationMismatchTemplate(payload ReconciliationMismatchTemplatePayload) (subject, templateHtml, plainText string)
```

Mọi trường đều là `string` đã định dạng sẵn — mẫu chỉ trình bày, không tính toán.

Dùng `html/template` cho HTML (tự động escape) và `text/template` cho plain text. Không dùng `template.HTML` ở bất kỳ đâu, nên không có lối bypass escaping.

**Khác biệt cố ý so với `verify_email.go`:**

| | `verify_email.go` | Mẫu mới |
|---|---|---|
| Lỗi execute plain text | `panic(err)` | log + `return` (trả chuỗi rỗng) |
| Màu header | `#0b0d0f` (đen) | `#b42318` (đỏ cảnh báo) |
| `max-width` | 600px | 900px (bảng 8 cột) |

Không panic là bắt buộc: mẫu này chạy trong luồng đối soát, không được phép làm sập tiến trình.

### 3.6 Điều phối gửi — `reconciliation_mismatch_notify.go`

```go
func formatNumber(v float64) string
func buildMismatchPayload(rc *modelmg.ReconciliationRaw, items []ReconciliationMismatch) emailtemplates.ReconciliationMismatchTemplatePayload
func (r reconciliationImpl) notifyMismatches(ctx context.Context, rc *modelmg.ReconciliationRaw, c *mismatchCollector)
```

**`formatNumber`** — phân tách hàng nghìn bằng dấu chấm, cắt phần thập phân.

Chi tiết tinh tế: `n := int64(v)` thực hiện **trước** `neg := n < 0`. Nếu đảo thành `v < 0` thì `-0.9` sẽ ra `"-0"`. Đã probe 18 giá trị biên (0, ±0.9, ±1, 999, 1000, ±1200, 999999, 10⁶, 10⁹) — tất cả đúng.

**`buildMismatchPayload`** — ánh xạ đủ 8 trường `ReconciliationMismatch` → `MismatchRow`, `TotalMismatch = len(items)`. Guard `rc.Conditions != nil` vì đó là con trỏ, có thể nil ở dữ liệu cũ.

**`notifyMismatches`** — không trả về giá trị, nên lỗi **không thể** rò ra luồng đối soát. Bốn nhánh thoát, tất cả log rồi `return`:

| Nhánh | Log |
|---|---|
| `c == nil \|\| c.Len() == 0` | (im lặng) |
| `len(recipients) == 0` | vàng — kèm số item lệch |
| `htmlContent == ""` | đỏ — render thất bại |
| `SendEmailToMany` lỗi | đỏ — kèm nội dung lỗi |
| thành công | xanh — kèm số item |

Hai guard đầu return **trước** khi gọi `getMismatchRecipients`, nên "không lệch thì không chạm DB/SMTP" là bất biến có test khoá.

Thông điệp log viết **không dấu** (quy ước dự án); comment trong code viết **có dấu** tiếng Việt.

### 3.7 Mở rộng mailer — `aws.go`

```go
func SendEmail(to string, subject, plainText, htmlContent string) error {
    return SendEmailToMany([]string{to}, subject, plainText, htmlContent)
}

func SendEmailToMany(to []string, subject, plainText, htmlContent string) error
```

Chữ ký `SendEmail` **giữ nguyên** để không phá call site. Danh sách rỗng trả lỗi `"no recipients"` chứ không im lặng thành công.

Package tên `intenralsmtp` — typo có sẵn trong repo, giữ nguyên.

---

## 4. An toàn đa luồng

`Running` chạy `runCashBack` qua `ants.NewPoolWithFunc(50, ...)`. Biến chia sẻ duy nhất mới là `mismatches`, tạo một lần và truyền qua trường `Mismatches` vào cả 50 worker.

Các biến còn lại trong `runCashBack` (`payloadCashFlow`, `wRcItem`, `w`, `wEventBonus`, `notificationPayloads`) đều **cục bộ mỗi lời gọi**, không chia sẻ.

`data.Reconciliation` (`*rc`) đã được chia sẻ qua 50 worker **từ trước** thay đổi này, chỉ đọc — không phải vấn đề mới.

Kiểm chứng: test 200 goroutine ghi song song, chạy `-race`, sạch.

---

## 5. Kiểm thử

**29 test mới** do thay đổi này thêm (24 ở `pkg/admin/service`, 5 ở `templates`). Chạy cùng các test có sẵn thì tổng là 38, đều xanh.

```bash
cd backend
go test ./pkg/admin/service/ -race -vet=off -count=1          # 33 pass (24 mới + 9 có sẵn)
go test ./internal/module/smtp/templates/ -count=1            # 5 pass (đều mới)
go build ./cmd/...                                            # 3 binary, sạch
```

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

Dùng lại nhóm biến SMTP **đã có sẵn**:

```
SMTP_AWS_SES_ENABLE
SMTP_AWS_SES_HOST
SMTP_AWS_SES_PORT
SMTP_AWS_SES_USERNAME
SMTP_AWS_SES_PASSWORD
SMTP_AWS_SES_FROM
```

> **Cảnh báo:** nhóm biến này trước nay **chưa từng được thực thi kiểm chứng** — xem mục 8.

---

## 8. Rủi ro triển khai

### 8.1 Guard view thay đổi hành vi trả tiền — RỦI RO CAO NHẤT

`hasViewMismatch` là `expected != actual`, **không dung sai**. Item bị loại là item **không được trả tiền**.

Nếu lượt xem có biến động lành tính giữa lúc chốt kỳ và lúc chi, kỳ chạy đầu sau triển khai có thể loại nhiều item hơn dự kiến.

**Hành động bắt buộc:** theo dõi sát tỉ lệ item `rejected` ở kỳ đối soát đầu tiên, đối chiếu với các kỳ trước.

### 8.2 Đây là call site SMTP đầu tiên thực sự chạy

Phát hiện trong quá trình triển khai: **toàn bộ hạ tầng SMTP là mã chết.**

```
intenralsmtp.SendEmail          → 0 call site trong toàn repo
verify_email.go                 → chỉ struct payload được dùng; template HTML không ai dùng
Email OTP thật                  → internal/service/otp.go, gọi API AccessTrade
                                   template_code: "AMBASSADOR_EMAIL_OTP_VERIFICATION"
                                   (template nằm ở hệ thống ngoài)
```

Nghĩa là cấu hình SMTP production có thể sai hoặc rỗng mà không ai biết. Kịch bản xấu nhất đã được chặn tốt (chỉ log, không ảnh hưởng chi tiền), nhưng kịch bản **thực tế nhất** là: kỳ đầu có lệch, email im lặng không đến, chỉ còn dòng log.

**Hành động bắt buộc:**
1. Trước kỳ chạy đầu: gửi thử một email qua đường SMTP này ở staging.
2. Sau kỳ chạy đầu: `grep "\[notifyMismatches\]"` trong log để biết nhánh nào đã đi vào.

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

---

## 10. Lịch sử commit

```
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

`ca5e6b33` và `a5468a54` là một cặp thêm-rồi-gỡ: bản thiết kế đầu dùng danh sách email cấu hình qua env, sau đó đổi hướng sang tra admin tạo kỳ nên revert nguyên vẹn.
