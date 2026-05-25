# Gap #9 — TCB và vCreator thiếu cơ chế bảo vệ khi tính lại tiền thưởng cho content đã thay đổi trạng thái

> **Priority**: 🟡 **P2** (reclassified P1→P2 2026-05-07 sau khi user clarify)
> **Source**: [semantic-diff-campaign-event.md](../../semantic-diff-campaign-event.md)
> **Direction port**: Ambassador → TCB + vCreator
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

### Bối cảnh nghiệp vụ

Trong các campaign creator economy, tiền thưởng creator được tính theo **metrics tăng dần theo thời gian** (views, likes, comments mỗi ngày). Mỗi ngày hệ thống tính reward riêng cho ngày đó.

Tuy nhiên có 1 trường hợp đặc biệt: **content thay đổi trạng thái** (vd: admin reject content sau khi đã được duyệt, hoặc đảo ngược quyết định). Khi đó hệ thống cần:
1. Reset toàn bộ reward đã tạo cho content đó
2. Tính lại từ đầu theo trạng thái mới (vd: nếu rejected → cash = 0 cho mọi ngày)

→ Quá trình này gọi là **recheck** — chạy qua N ngày của content để tính lại reward từng ngày.

### Vấn đề khi recheck bị gián đoạn

Nếu **server crash giữa quá trình recheck** (đã tính lại 5/10 ngày, server restart đột ngột):
- 5 ngày đầu đã tính theo trạng thái mới
- 5 ngày sau vẫn còn reward cũ theo trạng thái cũ
- → Reward **lệch nhau giữa các ngày** trong cùng 1 content
- Creator nhận tiền sai → khiếu nại
- Admin/finance không có cách phát hiện vì không có dấu hiệu nhận biết

### Hiện trạng 3 sản phẩm

- **Ambassador**: Đã có cơ chế bảo vệ đầy đủ — đánh dấu "đang recheck" trên các reward, sau khi server restart có cron tự dò và hoàn thành quá trình
- **TCB**: Có dấu hiệu **đã từng định build cơ chế này** — có sẵn field "đang recheck" trong dữ liệu reward, nhưng implementation chưa hoàn thiện (xem section "Phát hiện thú vị" bên dưới)
- **vCreator**: Hoàn toàn không có gì — kể cả field dữ liệu cũng chưa có

→ Cả TCB và vCreator đều có nguy cơ **reward bị tính sai** khi server crash giữa lúc recheck content.

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khi server crash giữa lúc recheck content... | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Có "dấu hiệu đang recheck dở dang" trên reward không? | 🟡 Có sẵn ô lưu nhưng KHÔNG được dùng | ❌ Không có ô lưu | ✅ Có và dùng đầy đủ |
| Có reset cash=0 trước khi tính lại để budget tính đúng không? | ❌ Không | ❌ Không | ✅ Có |
| Có cron tự động hoàn thành recheck dở dang sau khi server restart không? | ❌ Không | ❌ Không | ✅ Có |
| Hậu quả khi crash | Reward bị **tính sai lệch** giữa các ngày, không cách phát hiện | Reward bị tính sai lệch, không cách phát hiện | Reward stuck ở trạng thái rõ ràng → cron tự recover |

## Phát hiện thú vị về TCB — implementation dở dang

TCB có **field `RecheckInProgress`** trong cấu trúc dữ liệu reward (giống Ambassador), nhưng:

- Code TCB **chỉ set field này về `false`** ở 2 chỗ (sau khi tính reward xong)
- **Không có chỗ nào set `true`** trong toàn bộ codebase
- → Field tồn tại nhưng **chưa từng được dùng** đúng cách

→ Có vẻ TCB **đã từng định** port pattern này từ Ambassador nhưng **port chỉ một phần** (cleanup state) và bỏ dở phần quan trọng (set state + cron recovery). vCreator thì hoàn toàn chưa biết đến concept này.

→ Điều này gợi ý: **port hoàn thiện cho TCB sẽ nhanh hơn vCreator** vì TCB đã có sẵn field model, chỉ cần thêm logic. vCreator phải làm migration data + thêm field model trước.

## Rủi ro thực tế

**Rủi ro thấp đến trung bình**:

1. **Tần suất**: Crash xảy ra khi server restart (deploy, scale, update infra) hoặc khi process bị OOM. Production thường ổn định → vài lần/tháng
2. **Số lượng content bị ảnh hưởng**: chỉ những content **đang được recheck đúng lúc crash** mới bị → thường chỉ vài content/lần crash
3. **Phát hiện**: KHÔNG có cách phát hiện tự động → chỉ phát hiện khi creator khiếu nại hoặc finance audit
4. **Tác động**: tiền thưởng sai vài chục đến vài trăm nghìn VND/lần (depends on scale campaign)

→ Đây là lý do classify **P2**: không gây revenue loss lớn, không ảnh hưởng nhiều creator, có workaround manual (admin trigger recheck lại bằng tay khi phát hiện).

**Tăng priority nếu**:
- Có incident creator khiếu nại reward sai sau khi content bị reject
- Tần suất deploy/restart tăng cao
- Campaign budget lớn → impact 1 lần crash có thể đáng kể

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port pattern recheck-with-safety từ Ambassador sang TCB và vCreator.

**Pattern Ambassador**:
1. Trước khi loop tính lại — đánh dấu tất cả reward của content "đang recheck" + reset cash về 0
2. Loop tính lại từng ngày → mỗi reward tính xong tự xoá đánh dấu
3. Khi server start (lúc khởi động) — chạy cron quét tất cả reward còn đánh dấu "đang recheck" → tự hoàn thành nốt

**Lý do chọn pattern Ambassador**:
- Ambassador đã chạy production OK → có template
- Ý tưởng đơn giản — dùng trạng thái database làm "checkpoint" để recover sau crash
- Không yêu cầu hạ tầng phức tạp (không cần queue, message broker)

**Việc cần làm**:

### Cho TCB (effort thấp ~3-5 ngày)
- TCB đã có field `RecheckInProgress` sẵn → chỉ cần thêm logic set true + reset cash trước loop
- Thêm cron recovery vào lúc server start
- Cleanup field hiện tại đang set false sai vị trí

### Cho vCreator (effort cao hơn ~5-7 ngày)
- Cần thêm field `RecheckInProgress` vào cấu trúc reward (migration data)
- Port toàn bộ logic + cron giống TCB
- Có thể combine với gap #8 (vCreator port budget engine) — cùng touch reward engine

**Cần product/business confirm trước khi triển khai**:
1. Có incident creator khiếu nại reward sai sau khi admin reject content không? (xác nhận risk có manifest thực tế)
2. Tần suất TCB/vCreator deploy production ra sao? (1 lần/tuần? 1 lần/tháng?)
3. Bao nhiêu content/ngày bị change status (reject/đảo ngược)? (đo scope risk)
4. Combine gap #9 với gap #8 cho vCreator hay tách riêng PR?
5. Cleanup TCB partial implementation: xoá field model nếu không có roadmap dùng, hay giữ + hoàn thiện?

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Cả 3 sản phẩm có function `RecheckSchemaWithContentWhenChangeStatus` để tính lại reward khi content đổi status. Khác biệt:

- **Ambassador**: Set `recheckInProgress=true + cash=0` trước loop. Có cron `RecoverRecheckInProgress` chạy lúc server start để recover dang dở.
- **TCB**: KHÔNG set `recheckInProgress=true` (field tồn tại trong model, chỉ set false ở 2 chỗ). KHÔNG có cron recovery.
- **vCreator**: KHÔNG có field `recheckInProgress` trong model. KHÔNG có cron recovery.

## Verify code

### Ambassador (đầy đủ — pattern source of truth)

**`internal/service/event_schema.go:765-790`** — set state trước loop:
```go
if len(contentAnalytics) > 0 {
    fmt.Println("[Recheck] SET recheckInProgress=true + cash=0 for content=%s")
    _ = daomongodb.EventRewardDAO().GetShare().UpdateMany(ctx, ..., bson.M{
        "options.contentId": content.ID,
        "type":              constants.EventSchemaTypeByStatistic,
        "status":            bson.M{"$ne": constants.StatusCompleted},
    }, bson.M{
        "$set": bson.M{
            "cash":              0,
            "recheckInProgress": true,  // ← MARK đang recheck
            "updatedAt":         time.Now(),
        },
    })
    Event().UpdateBudgetStatistic(ctx, content.User, content.Event, content.ID)

    for i, doc := range contentAnalytics {
        e.UpdateRewardTypeByStatisticContent(ctx, content, doc)
        // → upsertPrimaryReward set recheckInProgress=false sau khi xong
    }
}
```

**`internal/service/event_schema.go:1158-1230`** — cron recovery:
```go
func (e eventSchemaImpl) RecoverRecheckInProgress() {
    // Find all rewards still flagged
    var rewards []*modelmg.EventRewardRaw
    _ = daomongodb.EventRewardDAO().GetShare().Find(ctx, ..., bson.M{
        "recheckInProgress": true,
        "type":              constants.EventSchemaTypeByStatistic,
    })(&rewards)

    // Group by (contentId, date) — dedup
    processed := make(map[recheckKey]bool)
    for _, reward := range rewards {
        key := recheckKey{ContentID: ..., Date: ...}
        if processed[key] { continue }
        processed[key] = true

        // Re-fetch content/event/schema/analyticDaily và re-run UpdateRewardTypeByStatisticContent
    }
}
```

**`pkg/public/server/initialize/initialize.go:25`** — wired vào server start:
```go
go internalservice.EventSchema().RecoverRecheckInProgress()
```

### TCB (dở dang — partial implementation)

**`internal/model/mg/event_reward.go:34`** — field tồn tại:
```go
type EventRewardRaw struct {
    // ...
    RecheckInProgress bool   `bson:"recheckInProgress" json:"recheckInProgress"`
}
```

**`internal/service/event_schema.go:271-296`** — recheck function (KHÔNG set true):
```go
func (e eventSchemaImpl) RecheckSchemaWithContentWhenChangeStatus(ctx, event, content) error {
    if event.IsBlockCreateReward() { return errors.New(...) }

    contentAnalytics := ...
    if len(contentAnalytics) > 0 {
        // ← KHÔNG có UpdateMany set recheckInProgress=true + cash=0
        for _, doc := range contentAnalytics {
            err := e.UpdateRewardTypeByStatisticContent(ctx, content, doc)
        }
    }
    // ...
}
```

**`internal/service/event_schema.go:746, 792`** — set false (cleanup state đã không bao giờ được set):
```go
// upsertPrimaryReward và upsertOverflowReward
"$set": bson.M{
    // ...
    "recheckInProgress": false,  // ← cleanup, nhưng nothing sets it to true
}
```

→ TCB **đã port partial từ Ambassador**: copy field + cleanup logic, nhưng không port set-true + cron recovery. Có thể:
- Developer định port full nhưng quên hoàn thiện
- Pull pattern từ Ambassador để chuẩn bị, để dở dang
- → Cleanup hoặc finish — có thể quyết định khi triển khai

### vCreator (không có gì)

**`internal/model/mg/event_reward.go`** — KHÔNG có field `RecheckInProgress`.

**`internal/service/event_schema.go:331-365`** — recheck function (giống TCB skeleton, naive):
```go
func (e eventSchemaImpl) RecheckSchemaWithContentWhenChangeStatus(ctx, event, content) {
    if event.ID.IsZero() || event.Status != constants.StatusActive { return }

    contentAnalytics := ...
    if len(contentAnalytics) > 0 {
        for _, doc := range contentAnalytics {
            e.UpdateRewardTypeByStatisticContent(ctx, content, doc)
        }
    }
    // ...
}
```

→ Tính lại trực tiếp, không có safety state, không có recovery.

## Đề xuất implementation

### Phase 1 (TCB) — Hoàn thiện partial implementation (~3-5 ngày)

Vì TCB đã có field `RecheckInProgress` sẵn, chỉ cần:

1. **Thêm UpdateMany trước loop** trong `RecheckSchemaWithContentWhenChangeStatus`:
   ```go
   if len(contentAnalytics) > 0 {
       _ = daomongodb.EventRewardDAO().GetShare().UpdateMany(ctx, ..., bson.M{
           "options.contentId": content.ID,
           "type":              constants.EventSchemaTypeByStatistic,
           "status":            bson.M{"$ne": constants.StatusCompleted},
       }, bson.M{
           "$set": bson.M{
               "cash":              0,
               "recheckInProgress": true,
               "updatedAt":         time.Now(),
           },
       })
       Event().UpdateBudgetStatistic(ctx, content.User, content.Event, content.ID)
       // ... existing loop
   }
   ```

2. **Port `RecoverRecheckInProgress` function** từ Ambassador (~70 LOC)

3. **Wire vào server initialize** ở TCB:
   ```go
   // pkg/public/server/initialize/initialize.go (TCB)
   go internalservice.EventSchema().RecoverRecheckInProgress()
   ```

4. **Test**:
   - Trigger `RecheckSchemaWithContentWhenChangeStatus` cho 1 content có 10 ngày analytics
   - Kill process giữa loop (vd: ngày 5)
   - Restart → verify cron tự complete 5 ngày còn lại

### Phase 2 (vCreator) — Port full với migration (~5-7 ngày)

vCreator cần làm thêm:

1. **Migration data**: thêm field `RecheckInProgress bool` vào `EventRewardRaw` model + migration script set false cho records cũ

2. **Port logic giống Phase 1 TCB**

3. **Combine với gap #8?**: vCreator port budget engine từ Ambassador (gap #8) cũng touch `event_schema.go` — có thể combine 2 PRs hoặc làm tuần tự (gap #8 trước, #9 sau).

### Risks + mitigations

| Risk | Mitigation |
|---|---|
| Cron `RecoverRecheckInProgress` chạy đồng thời với recheck mới đang running → race | Wrap trong `WithBudgetLock` (đã có ở Ambassador), hoặc check timestamp threshold (chỉ recover records đã stuck > 5 phút) |
| Migration vCreator cần touch tất cả existing EventReward records | Script default `recheckInProgress=false` cho records cũ, không thay đổi behavior |
| TCB cleanup logic ở line 746, 792 hiện đang "set false vô dụng" — sau khi port có thể giữ hoặc xoá | Giữ — sau khi port, logic này trở thành cleanup state cuối flow recheck (đúng pattern Ambassador) |

## Effort estimate

| Phase | Task | Effort |
|---|---|---|
| 1 | TCB hoàn thiện partial: thêm set-true + cron + wire | ~3-5 ngày |
| 2 | vCreator port full: migration + logic + cron + wire | ~5-7 ngày |
| | **Tổng nếu làm cả 2** | **~8-12 ngày** |

## Files referenced

**Ambassador (source of truth)**:
- `internal/service/event_schema.go:765-790` — set state trước loop
- `internal/service/event_schema.go:1158-1230` — `RecoverRecheckInProgress` cron function
- `pkg/public/server/initialize/initialize.go:25` — wired vào server start
- `internal/model/mg/event_reward.go` — field `RecheckInProgress`

**TCB (cần hoàn thiện)**:
- `internal/model/mg/event_reward.go:34` — field tồn tại
- `internal/service/event_schema.go:271-296` — `RecheckSchemaWithContentWhenChangeStatus` (thiếu set-true)
- `internal/service/event_schema.go:746, 792` — chỉ có cleanup set false
- KHÔNG có cron recovery
- KHÔNG có wire trong initialize

**vCreator (cần port full)**:
- `internal/model/mg/event_reward.go` — KHÔNG có field `RecheckInProgress`
- `internal/service/event_schema.go:331-365` — `RecheckSchemaWithContentWhenChangeStatus` (naive, không có safety)
- KHÔNG có cron recovery

## Liên quan đến gap khác

- **Gap #8** (vCreator port budget engine từ Ambassador): cùng touch `event_schema.go` ở vCreator. Có thể combine PR. Nếu làm gap #8 trước → dev đã quen pattern Ambassador → port gap #9 nhanh hơn.
- **Gap #18** (BudgetInfo struct port Amb→TCB): cùng touch `event.go` ở TCB. Có thể combine.

## Lịch sử phân loại

- **Initial (2026-05-07)**: P1 (Total 14, score: BV=4, Risk=4, Effort=4, XProd=2)
  - Title cũ: "Ambassador `RecoverRecheckInProgress` (cron recovery sau crash) — TCB không có"
  - Direction cũ: Ambassador → TCB (chỉ port cron)

- **Re-verified scope (2026-05-07)**: User hỏi "còn vCreator thì sao?" → verify thêm:
  - vCreator KHÔNG có field `RecheckInProgress` trong model
  - vCreator có function recheck nhưng naive (giống TCB skeleton)
  - Phát hiện TCB **partial implementation** — field model có, cleanup state có, nhưng không có set-true + cron recovery

- **Reclassified P1→P2 (2026-05-07)**: User chỉ định P2 vì:
  - Risk thấp đến trung bình (chỉ trigger khi server crash giữa recheck)
  - Tần suất thấp (vài lần/tháng)
  - Không gây revenue loss lớn (vài chục đến vài trăm nghìn/lần)
  - Có workaround manual (admin trigger recheck lại bằng tay)

- **Rescope direction**: từ "Ambassador → TCB" thành "Ambassador → TCB + vCreator" (cả 2 đều có gap)

### Bài học methodology
- TCB có field tồn tại nhưng **không dùng đúng** → easy to miss khi chỉ check existence
- Phải verify cả **set true** lẫn **set false** flow → mới biết partial implementation
- Khi compare 3 sản phẩm, dù 2 sản phẩm "không có feature" giống nhau cũng cần verify implementation level (vCreator thiếu cả field, TCB có field nhưng không dùng)
