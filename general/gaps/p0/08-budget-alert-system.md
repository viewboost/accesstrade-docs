# Gap #8 — vCreator thiếu hệ thống kiểm soát ngân sách campaign

> **Priority**: 🔴 **P0** (Total score 16)
> **Source**: [semantic-diff-financial.md](../../semantic-diff-financial.md), [semantic-diff-campaign-event.md](../../semantic-diff-campaign-event.md)
> **Direction port**: TCB hoặc Ambassador → vCreator
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Mỗi campaign (chương trình thưởng nội dung) trong AccessTrade có một **ngân sách giới hạn** — số tiền tối đa platform sẽ trả thưởng cho creators. Khi campaign đạt giới hạn:

- **Phải dừng nhận content mới** (không cho creator submit thêm)
- **Phải dừng tạo phần thưởng mới** (không tính tiền cho content đã submit nhưng chưa duyệt)
- **Phải báo cho team operations** biết để xử lý (gia hạn budget hoặc đóng campaign)

Hiện tại:
- **TCB**: Đã có ✅ — kiểm soát ở 3 mức (cả campaign / mỗi user / mỗi content) + tự động chặn + cảnh báo Telegram & Email
- **Ambassador**: Đã có ✅ — gần như tương đương TCB (3 mức + chặn + cảnh báo Telegram)
- **vCreator**: ❌ **KHÔNG có gì cả**

→ vCreator đang chạy campaign **không có giới hạn chi tiêu**. Nếu một campaign vCreator nào đó có nhiều creator submit content tốt → platform có thể chi vượt budget mà không ai phát hiện cho đến khi báo cáo tài chính cuối tháng.

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Tính năng | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Cài đặt ngân sách tổng cho campaign** | ✅ Có | ❌ Không | ✅ Có |
| **Cài đặt ngân sách trần cho mỗi creator** | ✅ Có | ❌ Không | ✅ Có |
| **Cài đặt ngân sách trần cho mỗi bài content** | ✅ Có | ❌ Không | ✅ Có |
| **Tự động dừng nhận content khi hết budget** | ✅ Có | ❌ Không | ✅ Có |
| **Tự động dừng tạo reward khi hết budget** | ✅ Có | ❌ Không | ✅ Có |
| **Cảnh báo sớm tại 75% / 95% / 100% budget** | ✅ Có | ❌ Không | ✅ Có |
| **Báo cáo Telegram khi vượt ngưỡng** | ✅ Có | ❌ Không | ✅ Có (label `[Ambassador]`) |
| **Email cho creator: "Campaign sắp hết budget, submit nhanh"** | ✅ Có | ❌ Không | ❌ Không |
| **Admin tự cấu hình email alert riêng cho stakeholder** | ✅ Có (`BudgetCampaign`) | ❌ Không | ❌ Không |
| **Hiện sẵn % budget đã dùng trên dashboard** | 🟡 Phải tính lại mỗi lần | ❌ Không | ✅ Có sẵn (`BudgetInfo.UsedPercent`) |

## Rủi ro nếu không sửa (cho vCreator)

1. **Chi vượt ngân sách** — không có cơ chế gate, một campaign hot có thể trả thưởng vượt số tiền đã duyệt
2. **Phát hiện muộn** — không có Telegram alert → ops team không biết campaign sắp cạn cho đến cuối kỳ
3. **Khó audit** — không có lịch sử threshold tracking → khó báo cáo cho stakeholder "campaign này đạt 95% lúc nào"
4. **Operations bị động** — admin phải manual check trên dashboard hàng ngày thay vì có cảnh báo tự động

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port hệ thống budget từ **Ambassador sang vCreator** (KHÔNG phải từ TCB).

**Lý do chọn Ambassador làm template**:
- Ambassador và TCB có engine ngân sách giống nhau ~90%
- Nhưng Ambassador đơn giản hơn (chỉ Telegram, không có email)
- vCreator chưa có hệ thống gửi email transactional — port từ Ambassador không cần setup SendGrid mới
- Kết quả tương đương về mặt protection (chặn chi vượt + cảnh báo team ops qua Telegram)

**Effort dự kiến**: 3-4 ngày developer → có 1 release nhỏ tách riêng.

**Cần product/business confirm 5 câu trước khi triển khai**:
1. vCreator hiện có những campaign nào lớn cần kiểm soát? (Nếu chỉ là test campaigns nhỏ → có thể defer)
2. Ai care về budget control ở vCreator? (CFO? Operations? Brand owner?)
3. Có sẵn Telegram channel `[vCreator]` cho budget alert chưa? (cần tạo trước khi launch)
4. Migration: các event vCreator hiện tại sẽ default budget = 0 (không giới hạn) — OK không?
5. Ambassador đang có feature `RecoverRecheckInProgress` (tự khôi phục trạng thái sau crash). vCreator có cần feature này luôn không?

**Tách 2 việc riêng (có thể defer P2)**:
- Port `BudgetInfo` struct (UsedPercent pre-compute) từ Ambassador → TCB: cải thiện performance dashboard
- Port `BudgetCampaign` (custom email alert config) từ TCB → Ambassador: cho team marketing setup alert riêng cho từng stakeholder

→ 2 việc này không khẩn cấp, làm sau khi đã vá xong vCreator.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR (đã sửa lại sau verify)

Đánh giá ban đầu sai: nghĩ "TCB-only feature port sang Amb". Thực tế:

- **TCB và Ambassador có hệ thống budget control gần như tương đương**: 3 levels (event/user/content), block reward khi vượt, threshold tracking 75/95/100%, distributed lock, Telegram alert
- **vCreator KHÔNG có gì**: 0 fields budget trong EventRaw, 0 logic check trong event service

→ Gap thật: **vCreator → cần backport** từ TCB hoặc Ambassador.

→ Khác biệt nhỏ TCB vs Ambassador (~10% cosmetic + 1 feature riêng), không phải gap lớn cần port qua lại.

---

## Picture đầy đủ về budget control 3 sản phẩm

### vCreator EventRaw model
```go
type EventRaw struct {
    ID, Type, Partner, Covers, Tags, Name, ...
    StartAt, EndAt, Options, ...
    AutoRejectConditions, Reward, ExtendedPeriod
    // NO: Budget, Bpu, Bpc, IsBlockReward, IsBlockSubmitContent, threshold logic
}
```

→ Event vCreator **không có budget**. Nếu admin set reward cao + nhiều creator submit → tiền chi không giới hạn, không có gate dừng.

### TCB EventRaw model (có đầy đủ)
```go
type EventRaw struct {
    ...
    IsBlockSubmitContent bool        ← block user submit content khi vượt
    IsBlockReward        bool        ← block tạo reward khi vượt
    Budget               float64     ← event-level budget (BPE)
    Bpu                  float64     ← budget per user
    Bpc                  float64     ← budget per content
}
```

### Ambassador EventRaw model (có đầy đủ + struct nicer)
```go
type EventRaw struct {
    ...
    Bpe                  *BudgetInfo  ← struct: Total/Used/Remain/UsedPercent (pre-compute)
    Bpc                  float64
    Bpu                  float64
    // ParticipationRequirements + ResourceLibrary (Ambassador-specific, không liên quan budget)
}

type BudgetInfo struct {
    Total       float64
    Used        float64
    Remain      float64
    UsedPercent float64  ← tiện cho dashboard query
}
```

---

## So sánh chi tiết TCB vs Ambassador (~90% giống nhau)

| Khía cạnh | TCB | Ambassador |
|---|---|---|
| **Budget event level** | `Budget float64` (raw) | `Bpe *BudgetInfo` (struct với pre-compute UsedPercent) |
| **Budget per user** | `Bpu float64` | `Bpu float64` ✅ giống |
| **Budget per content** | `Bpc float64` | `Bpc float64` ✅ giống |
| **Block flags** | `IsBlockReward + IsBlockSubmitContent` | `IsBlockReward + IsBlockSubmitContent` ✅ giống |
| **Threshold tracking** | `EventTrackingThresholdRaw` | `EventTrackingThresholdRaw` ✅ giống |
| **Threshold values** | 75/95/100% (hardcoded) | 75/95/100% (hardcoded) ✅ giống |
| **Multi-level estimate fn** | `EstimateBudgetMultiLevel` | `EstimateBudget` (tên ngắn hơn) |
| **Distributed lock** | `WithBudgetLock` (Redis) | `WithBudgetLock` (Redis 2 phút) ✅ giống |
| **Trigger inline khi tạo reward** | ✅ | ✅ |
| **Telegram alert** | ✅ | ✅ (có label `[Ambassador]` để phân biệt chat) |
| **Email alert (creators trong event)** | ✅ `SendNotificationAndEmailBudgetToAllUserInEvent` | ❌ chỉ Telegram |
| **`BudgetCampaign` collection** (admin config alert riêng) | ✅ + cron `CheckThresholdBudgetCampaign` | ❌ |
| **`BudgetInfo` pre-compute UsedPercent** | ❌ raw float | ✅ tiện cho dashboard |
| **Recovery cron after crash** | ❌ | ✅ `RecoverRecheckInProgress` |

### Khác biệt thực sự (chỉ 4 điểm)

1. **TCB có `BudgetCampaign` collection riêng**: admin tạo nhiều alert config với threshold custom (vd: 50M, 100M...) độc lập với threshold 75/95/100% built-in. Cron check threshold này định kỳ và gửi email staff list.
   - Use case: stakeholder A muốn nhận email khi event vượt 50M, stakeholder B muốn nhận khi vượt 80M → admin tạo 2 BudgetCampaign khác nhau

2. **TCB email all users trong event** khi vượt threshold (notify creators rằng event sắp hết budget → submit nhanh kẻo lỡ). Ambassador chỉ Telegram nội bộ admin team.

3. **Ambassador `BudgetInfo` struct có `UsedPercent` pre-compute** → dashboard query nhanh (không phải `(used/total)*100` mỗi lần). TCB dùng raw float, phải compute on-the-fly.

4. **Ambassador có `RecoverRecheckInProgress` cron** → recovery sau crash (xem [gap #9](./)). TCB chưa có.

---

## Verify 5-layer (theo methodology học từ gap #1, #5)

### Layer 1: Code tồn tại

| Component | TCB | vCreator | Ambassador |
|---|---|---|---|
| `service/budget.go` (BudgetCampaign + alert email) | ✅ 188 LOC | ❌ | ❌ |
| `event.go` budget logic (Estimate/Block/Lock) | ✅ ~200 LOC | ❌ | ✅ ~250 LOC |
| Model `EventRaw` budget fields | ✅ 5 fields | ❌ 0 | ✅ 4 fields |
| Model `EventTrackingThresholdRaw` | ✅ | ❌ | ✅ |
| Model `BudgetCampaignRaw` (alert config) | ✅ | ❌ | ❌ |
| Model `BudgetAlertRaw` (alert history) | ✅ | ❌ | ❌ |

### Layer 2: Code được gọi

**TCB callers** (verified bằng grep):
- `pkg/admin/service/shedule.go:120` — cron job gọi `CheckThresholdByEventID`
- `pkg/public/service/schedule.go:294,526,1821` — public scheduler gọi
- `pkg/admin/handler/budget_alert.go:25` — admin handler config
- `pkg/admin/router/routevalidation/budget.go:19` — router validation

**Ambassador callers**:
- `pkg/admin/handler/event_budget.go` — admin update budget API
- `internal/service/event.go` — `EstimateBudget` được gọi inline khi tạo reward
- `internal/service/event.go` — `HandleBudgetExceeded` trigger Telegram + block

**vCreator**: 0 callers (vì 0 code).

### Layer 3: Runtime DB usage

- **TCB**: `BudgetCampaignRaw` collection có records (admin tạo config), `EventTrackingThresholdRaw` ghi khi event vượt, EventRaw có field `Budget` được set
- **Ambassador**: tương tự (chỉ thiếu `BudgetCampaignRaw`)
- **vCreator**: 0 collections, 0 records

### Layer 4: Business need ở vCreator (cần verify với user)

Câu hỏi business:
1. **vCreator có campaign nào budget lớn không?** (creator-vn brand campaign)
2. **Hiện tại làm sao để control chi tiêu?** (manual check qua admin? Hay risk chi vượt?)
3. **Có incident chi vượt budget không?** (lý do thực tế cần port)
4. **Operations team có demand control không?** (CFO, finance team)

### Layer 5: Direction port

Mặc định: **TCB hoặc Ambassador → vCreator** (vì vCreator thiếu hoàn toàn).

Cross-pollination giữa TCB và Ambassador:
- Ambassador có thể học `BudgetCampaign` (custom alert config) từ TCB
- TCB có thể học `BudgetInfo` struct (UsedPercent pre-compute) từ Ambassador

→ Cross-pollination là P2-P3 (nice-to-have), không cấp bách như backport vCreator.

---

## Đề xuất implementation cho vCreator

### Option A — Port full từ TCB (giống TCB nhất)
- Schema: thêm 5 fields vào EventRaw + tạo `EventTrackingThresholdRaw` + `BudgetCampaignRaw`
- Service: copy `event.go` budget logic + `service/budget.go` (BudgetCampaign cron)
- Handler: copy admin handler để set budget + manage BudgetCampaign
- Email template: copy `threshold.html` + setup SendGrid

**Effort**: ~5-7 ngày (300-400 LOC + email template + cron setup)

**Pros**:
- vCreator có cả Telegram + Email alert (TCB style)
- Có `BudgetCampaign` cho stakeholder muốn alert custom

**Cons**:
- Email setup cần SendGrid config
- Admin UI phải build mới (BudgetCampaign list/create/edit pages)

### Option B — Port simple từ Ambassador (gọn hơn)
- Schema: thêm `Bpe *BudgetInfo + Bpu + Bpc` + tạo `EventTrackingThresholdRaw`
- Service: copy `event.go` budget logic
- Handler: copy `event_budget.go` UpdateBudget API
- Telegram setup (nếu chưa có)

**Effort**: ~3-4 ngày (~200 LOC)

**Pros**:
- Engine đơn giản hơn
- Ambassador `BudgetInfo` struct nicer cho dashboard

**Cons**:
- Chỉ có Telegram alert, không có email
- Không có BudgetCampaign custom config (1 threshold = 75/95/100% fixed)

### Option C — Cross-pollinate trước, sau đó port (recommended)
1. **Phase 1**: TCB port `BudgetInfo` struct từ Ambassador (~50 LOC + migration)
2. **Phase 2**: Ambassador port `BudgetCampaign` từ TCB (~150 LOC + admin UI)
3. **Phase 3**: vCreator port từ TCB (giờ đã có cả 2 features)

**Effort**: ~10-15 ngày tổng (3 phases)

**Pros**: Cuối cùng 3 sản phẩm đều có feature đầy đủ + consistent
**Cons**: Effort cao, cần plan kỹ migration data

### Đề xuất

→ **Option B** cho vCreator (đơn giản, fast). Cross-pollinate TCB ↔ Ambassador là **P2** (gap riêng, làm sau).

---

## Action items

1. **NGAY** — verify với business: vCreator có campaign nào budget lớn không, ai care về budget control?
2. **Nếu có demand** → chọn Option B (port từ Ambassador):
   - Schema migration EventRaw (+ `Bpe/Bpu/Bpc/IsBlockReward/IsBlockSubmitContent`)
   - Tạo collection `EventTrackingThresholdRaw`
   - Copy `event.go` budget logic
   - Copy admin handler `event_budget.go`
   - Setup Telegram bot config
3. **Test regression**: tạo 1 event với budget thấp + tạo content vượt → verify block reward + Telegram alert
4. **Document**: thêm vào admin handbook hướng dẫn admin cách set Bpe/Bpu/Bpc

---

## Câu hỏi business mở (cần user verify)

1. **vCreator có business need cho budget control không?** Nếu campaign vCreator nhỏ + chỉ chạy nội bộ (B2B workplace, đã ghi trong gap #28) → có thể không cần.
2. **TCB và Ambassador team có muốn unify budget engine không?** Hay chấp nhận 2 implementation gần giống vĩnh viễn?
3. **Migration data cũ vCreator**: nếu port budget thì các event hiện tại default Budget=0 (no limit). OK không?
4. **Email channel**: vCreator có SendGrid setup chưa? Nếu chưa → Option B (Telegram-only) hợp lý hơn.
5. **`BudgetCampaign` collection của TCB**: có thực sự được dùng ở production không? Hay là feature legacy ít stakeholder dùng → có thể skip khi port.

---

## Effort estimate

| Direction | LOC | Effort | Risk |
|---|---|---|---|
| **Port Ambassador → vCreator** (Option B, recommended) | ~200 | 3-4 ngày | Low (Ambassador code đã production-tested) |
| Port TCB → vCreator (Option A) | ~400 | 5-7 ngày | Medium (cần SendGrid setup + admin UI mới) |
| Cross-pollinate TCB ↔ Ambassador (Option C, full unify) | ~600 | 10-15 ngày | High (migration 2 sản phẩm + admin UI) |

→ Wave 1 (1-2 tuần): chỉ làm Option B cho vCreator. Cross-pollinate TCB ↔ Ambassador defer P2.

---

## Lịch sử phân loại

### Lần 1 — Initial classification (2026-05-07): SAI
- Priority: 🔴 P0 (Total 16)
- Title: "TCB Budget alert — TCB-only feature port sang vCr/Amb"
- Direction: TCB → vCr/Amb
- Sai vì: chưa verify Ambassador. Đoán Ambassador không có dựa trên semantic-diff financial (chỉ check `service/budget.go`, không check `service/event.go` của Ambassador).

### Lần 2 — User catch (2026-05-07): ĐÃ ĐÚNG
User: *"Trong mỗi event của TCB và Ambassador sẽ có cấu hình budget. Cả 2 đều block mà, chỉ là 1 bên theo event 1 bên theo user. Mà TCB cũng có theo user rồi"*

→ Verify lại event service:
- TCB có `EstimateBudgetByEvent` + `EstimateBudgetMultiLevel` (3 level event/user/content) + `IsBlockReward/IsBlockSubmitContent`
- Ambassador có `EstimateBudget` + `HandleBudgetExceeded` (3 level y hệt) + flag block tương đương
- vCreator KHÔNG có gì

→ **Direction port reclassify**: từ "TCB → vCr/Amb" thành **"TCB hoặc Ambassador → vCreator"**.
→ Priority giữ nguyên P0 vì vCreator vẫn là gap nghiêm trọng (no budget control).

### Bài học methodology (sai 6 lần liên tiếp trong session)

Lần này tôi sai vì:
- semantic-diff-financial.md viết "Budget allocation + alert: TCB ✅, vCr ❌, Amb ❌"
- semantic-diff-campaign-event.md viết "TCB và Amb đều V2, vCr V1" — có nói nhưng không nhấn mạnh
- Khi tổng hợp gap-analysis tôi pick từ semantic-diff-financial → bỏ qua context của campaign-event

→ **Khi build cross-product gap, cần tổng hợp từ NHIỀU file semantic-diff** thay vì chỉ 1. Một feature có thể nằm trong nhiều group (budget liên quan cả Financial lẫn Campaign-Event).

→ **Tốt hơn**: dùng grep filesystem trực tiếp để verify ngay, đừng trust mỗi file semantic-diff cho 1 feature lan rộng nhiều domain.

---

## Files referenced

**TCB (source of truth)**:
- `internal/service/event.go` — budget engine (`EstimateBudgetByEvent`, `EstimateBudgetMultiLevel`, `WithBudgetLock`)
- `internal/service/budget.go` — `BudgetCampaign.CheckThresholdByEventID` + email
- `internal/model/mg/event.go` — fields `Budget/Bpu/Bpc/IsBlockReward/IsBlockSubmitContent`
- `internal/model/mg/budget_alert.go` — `BudgetCampaignRaw` schema
- `internal/model/mg/event_tracking_threshold.go` — threshold tracking
- `pkg/admin/service/shedule.go:96-120` — cron `CheckThresholdBudgetCampaign`
- `pkg/admin/handler/budget_alert.go` — admin config handler
- `internal/module/sendgird/templates/budget.go` — email template

**Ambassador (source of truth alternative)**:
- `internal/service/event.go` — budget engine (`EstimateBudget`, `HandleBudgetExceeded`, `WithBudgetLock`, `RecoverRecheckInProgress`)
- `internal/model/mg/event.go` — fields `Bpe (BudgetInfo) / Bpu / Bpc`
- `internal/model/mg/event_tracking_threshold.go` — threshold tracking
- `pkg/admin/handler/event_budget.go` — `UpdateBudget` API

**vCreator (target — needs port)**:
- `internal/service/event.go` — KHÔNG có budget logic
- `internal/model/mg/event.go` — KHÔNG có budget fields
- 0 admin handler, 0 model
