# Gap #10 — TCB và Ambassador dùng 2 cơ chế khác nhau để chặn cảnh báo Telegram trùng lặp

> **Priority**: ⚪ **P3** (consolidation task — không phải bug, nhưng nên unify để dễ maintain)
> **Source**: [semantic-diff-campaign-event.md](../../semantic-diff-campaign-event.md)
> **Direction port**: Cần thiết kế chung cho cả 3 sản phẩm
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi campaign vượt ngân sách (75% / 95% / 100%), hệ thống cần gửi cảnh báo **một lần duy nhất** cho team operations qua Telegram — không spam lặp lại.

**Cả TCB và Ambassador đều giải quyết được vấn đề này**, nhưng dùng **2 cơ chế hoàn toàn khác nhau**:

### Cơ chế TCB — "Khóa cứng campaign"
- Khi campaign vượt ngân sách lần đầu → set flag "khóa campaign"
- Mọi tính toán reward sau đó **bị skip ngay từ đầu** — không vào nhánh check budget nữa
- **Hiệu ứng phụ**: campaign tê liệt hoàn toàn, không tính reward cho creator nào nữa cho đến khi admin **manual reset** (mở khóa)

### Cơ chế Ambassador — "Khóa thông minh + cờ alert"
- Khi vượt ngân sách lần đầu → set flag "khóa", đồng thời ghi nhận "ngưỡng này đã được alert"
- Tính reward vẫn tiếp tục chạy (chỉ block submit content)
- Lần sau gặp lại cùng ngưỡng đã alert → im lặng, không gửi Telegram lại
- **Tự động unblock**: nếu admin tăng budget, hệ thống tự nhận biết và resume

### Hệ quả của việc khác nhau

| Khía cạnh | TCB | Ambassador |
|---|---|---|
| Telegram dedup hoạt động không? | ✅ Có (gián tiếp qua flag khóa) | ✅ Có (trực tiếp qua flag alert) |
| Khi vượt budget, reward calc còn chạy không? | ❌ **Tê liệt** — bị block hoàn toàn | ✅ Vẫn chạy (chỉ block content submit) |
| Cần admin manual reset không? | ✅ Có — admin phải mở khóa | ❌ Không — tự động unblock khi budget mở rộng |
| Khi admin tăng budget thêm, có resume tự động không? | ❌ Không — phải toggle flag tay | ✅ Có — tự nhận biết |

→ **2 cơ chế đều giải quyết được vấn đề Telegram spam** (không phải bug), **nhưng**:
- Trải nghiệm khác nhau hoàn toàn cho team operations
- Khi dev mới đọc code Ambassador thấy flag `isSendNotification`, nhìn TCB không có → có thể đoán nhầm "TCB thiếu, cần port" → effort lãng phí
- Khi vCreator port (gap #8), không biết nên copy theo pattern TCB hay Ambassador
- Tăng độ phức tạp khi muốn debug hoặc thay đổi business rule

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khi campaign vượt ngân sách... | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Có gửi Telegram cảnh báo? | ✅ Có (1 lần đầu) | ❌ KHÔNG có hệ thống cảnh báo (xem gap #8) | ✅ Có (1 lần đầu) |
| Telegram có bị spam lặp lại không? | ❌ Không (đã dedup) | — | ❌ Không (đã dedup) |
| Reward calc còn chạy sau khi vượt? | ❌ Tê liệt — block toàn bộ | — | ✅ Vẫn chạy |
| Admin mở khóa thế nào? | Manual reset flag | — | Tự động khi tăng budget |
| Trải nghiệm operations | Cần admin can thiệp ngay | — | Có thể quan sát + xử lý dần |

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: **Unify 2 cơ chế** để 3 sản phẩm dùng chung 1 design pattern.

**Hướng đi đề xuất**: Áp dụng pattern Ambassador (khóa thông minh + cờ alert) cho cả 3 sản phẩm.

**Lý do chọn pattern Ambassador làm chuẩn**:
- Mềm dẻo hơn — không tê liệt campaign khi vừa vượt ngưỡng
- Tự động hồi phục khi admin tăng budget (giảm việc manual cho ops)
- Dễ extend cho các loại alert khác sau này
- Khi vCreator port (gap #8), đã xác nhận sẽ copy từ Ambassador → unify TCB cũng theo pattern này → toàn bộ 3 sản phẩm consistent

**Việc cần làm cho TCB**:
- Bỏ cơ chế "khóa cứng" (flag block reward calc)
- Thêm cờ "đã alert ngưỡng này chưa" để dedup Telegram giống Ambassador
- Sau khi vượt budget, reward calc vẫn chạy nhưng không tạo reward mới (đã có engine cap reward — gap #8)
- Migration: các campaign hiện đang bị "khóa cứng" cần được reset + unblock khi tăng budget

**Effort dự kiến**: ~3-5 ngày dev cho TCB (refactor logic + migration data + test).

**Cần product/business confirm trước khi triển khai**:
1. Ops team TCB có quen với cơ chế "khóa cứng cần manual reset" không? Đổi sang "tự động unblock" có cần training lại không?
2. Có incident nào ở TCB do campaign bị tê liệt sau khi vượt budget mà admin không reset kịp không?
3. Nếu chốt unify theo Ambassador pattern: có cần làm trước/sau gap #8 (vCreator port) không?
   - **Đề xuất**: làm sau gap #8. Khi gap #8 hoàn thành, vCreator đã có pattern Ambassador → đối chiếu sẽ rõ hơn.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

**TCB và Ambassador đều dedup Telegram alert** — nhưng dùng 2 cơ chế:

- **TCB**: `IsBlockReward` flag được dùng làm gate ở **7 entry point** của reward calc → khi block, mọi flow reward bị skip ngay → không vào `EstimateBudgetByEvent` nữa → không send Telegram lại
- **Ambassador**: `isSendNotification` flag bên trong `HandleBudgetExceeded` chỉ set true khi insert threshold record mới → check trước khi gọi `telegram.SendMessenger`

→ Cả 2 đều correct, nhưng **side effect khác nhau**:
- TCB: block reward calc hoàn toàn → tê liệt campaign
- Ambassador: reward calc tiếp tục, chỉ block submit content

→ **KHÔNG phải bug** ở TCB (như đoán ban đầu). **Nhưng** cần unify cho consistency.

## Verify code

### TCB cơ chế gate qua `IsBlockCreateReward()`

7 entry point trong `internal/service/event_schema.go` đều check sớm:

```go
// event_schema.go:44, 193, 272, 300, 462, 496, 530
if event.IsBlockCreateReward() {
    return  // skip toàn bộ reward calc
}
```

Khi `EstimateBudgetByEvent` set `isBlockReward=true` lần đầu (line 127-135), tất cả reward calc subsequent calls đều return ngay → không bao giờ đến đoạn `if Telegram.Token != ""` để gửi lại.

→ Telegram alert chỉ được gửi **1 lần duy nhất** trong vòng đời event (cho đến khi admin reset).

### Ambassador cơ chế cờ `isSendNotification`

```go
// internal/service/event.go:296 (HandleBudgetExceeded)
isSendNotification := false
for percent in [75, 95, 100]:
    threshold := find threshold record
    if threshold.ID.IsZero() {
        INSERT threshold
        isSendNotification = true  // chỉ set true khi có threshold mới
    }
update isBlockReward=true + isBlockSubmitContent=true
if Telegram.Token != "" && isSendNotification:
    SendTelegram(...)
```

Khi function được gọi lại với cùng ngưỡng đã insert → `isSendNotification=false` → không gửi Telegram. Reward calc tiếp tục bình thường (không có guard `IsBlockCreateReward` ở các entry points).

### Hệ quả khi vCreator port (gap #8)

vCreator port từ Ambassador (theo quyết định gap #8) → sẽ tự động dùng pattern Ambassador. Nếu sau đó muốn TCB consistency với 2 sản phẩm còn lại → cần refactor TCB.

## Đề xuất implementation (refactor TCB)

### Phase 1: Thêm cờ `isSendNotification` vào TCB `EstimateBudgetByEvent` (~1 ngày)

```go
// internal/service/event.go (TCB) — sửa lại
func (e eventImpl) EstimateBudgetByEvent(ctx context.Context, event *modelmg.EventRaw, tracking EstimateBudgetTracking) bool {
    if event.Budget == 0 {
        return false
    }
    if availiableCash < tracking.TotalCashPending {
        var isSendNotification bool  // ← THÊM
        for _, percent := range []float64{75, 95, 100} {
            threshold := findThreshold(...)
            if threshold.ID.IsZero() {
                insertThreshold(...)
                isSendNotification = true  // ← THÊM
                go Notification().SendNotificationAndEmailBudget(...)
            }
        }
        // ... update isBlockReward=true ...
        if config.GetENV().Telegram.TokenBudget != "" && isSendNotification {  // ← MODIFY
            telegram.SendMessenger(...)
        }
    }
}
```

→ Sau Phase 1, Telegram dedup vẫn work (vì flag `IsBlockReward` skip vẫn còn). Đây chỉ là **safety net** — nếu sau này bỏ guard `IsBlockCreateReward`, Telegram vẫn không spam.

### Phase 2: Refactor TCB bỏ "tê liệt campaign" (~2-3 ngày)

**Bước 2.1**: Bỏ guard `IsBlockCreateReward()` ở 7 entry point trong `event_schema.go`. Reward calc tiếp tục chạy sau khi event vượt budget.

**Bước 2.2**: Confirm engine reward V2 (đã có ở TCB) handle được case "vượt budget" đúng:
- Khi vượt: tạo primary reward với cash = available + overflow record cash=0 (`IsBudgetExceeded=true`)
- KHÔNG tạo reward mới khi không có cash còn lại

**Bước 2.3**: Đổi `isBlockReward` từ "block reward calc" thành "block content submit only" (theo Ambassador pattern). Reward calc vẫn run, chỉ block creator submit thêm.

**Bước 2.4**: Migration: các event đang `IsBlockReward=true` cần verify đã có overflow records đầy đủ. Nếu chưa → re-run reward calc once để fill.

### Phase 3: Auto-unblock khi tăng budget (~1 ngày)

Hiện tại admin tăng budget TCB → flag `IsBlockReward` vẫn `true` → admin phải manual toggle. Cần thêm logic:
- Khi admin update `event.Budget` qua admin handler → check `availableCash > 0` → tự động set `isBlockReward=false`, `isBlockSubmitContent=false`
- Optional: gửi Telegram thông báo "Đã unblock"

### Phase 4: Test + rollout (~1 ngày)

- Test campaign vượt budget → verify Telegram chỉ 1 alert (Phase 1 effect)
- Test reward calc vẫn chạy sau khi vượt (Phase 2 effect)
- Test admin tăng budget → verify auto-unblock (Phase 3 effect)

## Effort estimate

| Phase | Task | Effort |
|---|---|---|
| 1 | Thêm cờ `isSendNotification` (safety net) | ~1 ngày |
| 2 | Refactor: bỏ tê liệt campaign | ~2-3 ngày |
| 3 | Auto-unblock khi tăng budget | ~1 ngày |
| 4 | Test + rollout | ~1 ngày |
| | **Tổng** | **~5-6 ngày dev** |

## Risks + mitigations

1. **Bỏ "tê liệt campaign" có thể gây over-spending** nếu engine cap reward (gap #8 V2 split) chưa hoàn thiện ở TCB
   - **Mitigation**: verify TCB đã có primary/overflow split đầy đủ trước khi bỏ guard `IsBlockCreateReward`. TCB đã có theo semantic diff → OK.
2. **Migration data**: campaigns đang block có thể chưa có overflow records
   - **Mitigation**: Tool admin để re-run reward calc cho từng campaign block, fill missing overflows
3. **Ops team quen với "khóa cứng"** → đổi sang "tự động unblock" có thể confuse
   - **Mitigation**: training + changelog notify trước khi deploy

## Liên quan đến gap khác

- **Gap #8** (vCreator port budget engine): nếu vCreator port từ Ambassador → vCreator dùng pattern Ambassador (`isSendNotification`). Gap #10 này refactor TCB cũng theo pattern Ambassador → cuối cùng 3 sản phẩm consistent.
- **Gap #18** (BudgetInfo struct port Amb → TCB): có thể combine vào cùng PR vì cùng touch `event.go` ở TCB. Effort tổng của PR: gap #10 + #18 ~7-8 ngày.
- **Gap #30** (Telegram channel chưa unify): scope khác — chỉ về naming convention. Có thể làm độc lập.

## Files referenced

**TCB (cần refactor)**:
- `internal/service/event.go:127-135` — set `isBlockReward=true`
- `internal/service/event.go:135-167` — send Telegram (cần thêm `isSendNotification` guard)
- `internal/service/event_schema.go:44, 193, 272, 300, 462, 496, 530` — 7 guard `IsBlockCreateReward()` cần bỏ
- `internal/model/mg/event.go:127-129` — method `IsBlockCreateReward()` (có thể giữ để backward compat hoặc xóa)
- Admin handler tăng budget: cần thêm logic auto-unblock

**Ambassador (reference pattern)**:
- `internal/service/event.go:296-360` — `HandleBudgetExceeded` với `isSendNotification` flag

**vCreator (sau khi gap #8 hoàn thành)**:
- Sẽ tự động có pattern Ambassador (port từ Ambassador)

## Lịch sử phân loại

- **Initial (2026-05-07)**: P1 (Total 14, đoán là bug TCB spam Telegram)
- **Reclassified P3 (2026-05-07)**: User chỉ định P3 — easy win
- **Re-verified 2026-05-07**: User push verify lại với 2 hypothesis:
  - "TCB cũng có dedup" → đúng (qua flag `IsBlockReward` gate ở 7 entry points)
  - "Hoặc bị block sớm bởi flag" → đúng — đây chính là cơ chế TCB
- **Reclassify scope (2026-05-07)**: KHÔNG phải bug — TCB đã dedup Telegram thông qua flag block reward calc
  - **Nhưng** 2 cơ chế khác nhau giữa TCB và Ambassador → cần unify để consistency
  - **User direction (2026-05-07)**: *"solution sẽ là tìm cách làm cho 2 luồng này đi giống hệt nhau"*
  - Title đổi từ "TCB spam Telegram" → "2 cơ chế khác nhau, cần unify"
  - Solution đổi từ "fix bug TCB ~5 LOC" → "refactor TCB bỏ tê liệt campaign + dùng pattern Ambassador ~5-6 ngày"

### Bài học methodology (lần thứ 7+ trong session)

**Sai pattern**: Đọc 1 đoạn code → kết luận bug. Cần trace caller graph kỹ.

**Reality**: TCB không có flag `isSendNotification` rõ ràng nhưng có cơ chế gate sớm hơn (`IsBlockCreateReward` check ở 7 entry points). Cùng outcome (Telegram dedup), khác mechanism.

→ Khi gặp pattern khác biệt giữa 2 sản phẩm cùng team viết, **luôn assume cả 2 đều intentional** trước khi conclude là bug. Verify gating logic ở **caller flow**, không chỉ implementation 1 function.
