# Gap #38 — Thêm tên/mã nội bộ cho campaign (event code) — TCB có, vCreator/Ambassador chưa có

> **Priority**: 🟡 **P2** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: TCB → vCreator + Ambassador
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi platform có nhiều campaign chạy song song, **ban tổ chức (BTC) cần phân biệt campaign theo tên nội bộ ngắn gọn** (ví dụ: `TCB-Q1-2026`, `TCB-CARD-MARCH`) khác với tên hiển thị cho user (ví dụ: "Thử thách thẻ tín dụng tháng 3").

TCB đã thêm field `Code` cho event + wire vào tất cả chỗ hiển thị campaign:
- Dropdown chọn campaign trong admin
- Bảng list campaign + content
- Export Excel/CSV (có cột Code)
- Email notification cho creator (`[CODE] Name`)
- Dashboard creator analytics, content filter

→ Format chuẩn: `[code] name` (ví dụ: `[TCB-Q1] Thử thách thẻ tín dụng`)

vCreator + Ambassador **không có** field `Code` — admin/ops chỉ phân biệt campaign qua tên dài hoặc ID dài → khó nhớ, dễ nhầm khi có nhiều campaign trùng chủ đề.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Field `Event.Code string` | ✅ (line 48) | ❌ | ❌ |
| Display "[code] name" trong admin | ✅ | ❌ | ❌ |
| Code trong dashboard + filter | ✅ | ❌ | ❌ |
| Code trong export Excel/CSV | ✅ | ❌ | ❌ |
| Code trong email template | ✅ (CashFlowOptions, NotificationOpts) | ❌ | ❌ |
| Search: code được include vào `searchText` | ✅ (line 120-121) | ❌ | ❌ |
| Validation/required code | ✅ (hotfix/event-required-code) | ❌ | ❌ |

## Hệ quả

- **vCreator + Ambassador**: BTC khó communicate "campaign nào" trong meeting/Slack → phải gửi link hoặc copy-paste ID dài → tốn thời gian ops
- **Reporting**: khi xuất báo cáo Excel, không có cột Code → phải search lại tên dài để tra cứu
- **Email creator**: notification chỉ có name → creator không biết là campaign cụ thể nào (đặc biệt khi creator tham gia nhiều campaign)
- **Cross-product**: nếu cả 3 sản phẩm có Code → có thể chuẩn hóa naming convention (vd: `TCB-`, `VCR-`, `AMB-` prefix)

## Liên quan các gap khác

- **Gap #7 (Dashboard executive)**: dashboard cần code cột để filter nhanh
- **Gap #15 (Reconciliation)**: reconciliation report sẽ readable hơn với code
- **Gap #37 (Rejection tags)**: analytics theo campaign code dễ thống kê

## Giải pháp

### Phase 1: vCreator (~3-5 ngày)
1. **Model** (~30 phút):
   - Thêm `Code string` vào `EventRaw` struct
   - Update `GetSearchString()` include code
2. **Validation** (~1 giờ):
   - Make code optional (giai đoạn đầu) hoặc required (như TCB hotfix)
   - Unique constraint per-partner để tránh duplicate
3. **Admin handler** (~1 ngày):
   - Update create/update event API: nhận `code` field
   - Update list/detail response: trả `code`
4. **Wire vào display layer** (~1-2 ngày):
   - Format "[code] name" ở chỗ admin display campaign
   - Email template: `EventCode` field trong `CashFlowOptions` + `NotificationOpts`
   - Aggregate pipeline: include code trong analytics response
   - Export Excel/CSV: thêm cột Code
5. **Frontend admin** (~1 ngày):
   - Form create/edit event: thêm input "Code"
   - List page: thêm column "Code"
   - Filter/search: search được theo code
6. **Test** (~0.5 ngày)

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1

**Total**: ~1-2 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P2

- **Business value rõ**: BTC ops/marketing/finance dễ communicate, ít nhầm lẫn campaign
- **Effort thấp**: 1 field text + wire vào display layer (~5-7 chỗ)
- **Không urgent**: không phải bug active, là QoL improvement
- **TCB đã production-tested**: pattern rõ, copy không nhiều risk

→ Nice-to-have, làm khi có sprint trống. Có thể combo wave với gap #7 (dashboard) hoặc #37 (rejection tags) vì cùng touch admin display layer.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có field `Event.Code string` + wire đầy đủ vào display layer (admin, dashboard, email, export, search). vCr/Amb không có field này — phân biệt campaign chỉ qua name + ID dài.

## Verify code

### TCB (source of truth)

**Model** — `internal/model/mg/event.go:48`:
```go
type EventRaw struct {
    // ... other fields
    Code string `bson:"code" json:"code"`
    // ... other fields
}
```

**Search inclusion** — `internal/model/mg/event.go:120-121`:
```go
func (r *EventRaw) GetSearchString() string {
    searchText := r.Name
    if r.Code != "" {
        searchText += " " + r.Code
    }
    // ...
}
```

**Display format** — `internal/service/event.go:137-138`:
```go
if event.Code != "" {
    eventLabel = "[" + event.Code + "] " + event.Name
}
```

**Wire scope** (theo commit `5169f48d`):
- Backend (Go):
  - `CashFlowOptions`, `NotificationOpts`, email templates: thêm `EventCode` field
  - Aggregate pipelines (creator analytics, dashboard): include code
  - Admin API responses: content, event-bonus, reconciliation đều có code
  - XLSX/CSV export: thêm cột "Code"
- Dashboard (Next.js):
  - Campaign list table + content list table: column code
  - Campaign select dropdown: hiển thị `[code] name`
  - Content filter, export dialog: filter theo code
  - Creator analytics expandable rows: prefix `[code]`
  - Campaign portfolio table

**Validation hotfix** (commit `6eee128d` — `hotfix/event-required-code`):
- Code field becomes required, unique per partner
- Frontend validation + backend constraint

### vCreator status

```bash
grep -nE "Code\b" vcreator/backend/internal/model/mg/event.go
# → ❌ KHÔNG có field Code
```

### Ambassador status

```bash
grep -nE "Code\b" ambassabor/backend/internal/model/mg/event.go
# → ❌ KHÔNG có field Code
```

## Đề xuất implementation

### Phase 1: vCreator (~3-5 ngày)

1. **Model** (~30 phút):
   ```go
   // vcreator/backend/internal/model/mg/event.go
   type EventRaw struct {
       // ...
       Code string `bson:"code,omitempty" json:"code,omitempty"` // optional initially
       // ...
   }

   func (r *EventRaw) GetSearchString() string {
       searchText := r.Name
       if r.Code != "" {
           searchText += " " + r.Code
       }
       return format.NonAccentVietnamese(searchText)
   }
   ```

2. **Migration data cũ** (~1 giờ):
   - Decide: leave Code empty cho event cũ HOẶC backfill auto-generate (vd `VCR-{eventID-prefix}`)
   - Recommendation: leave empty + admin update manual khi cần

3. **DAO + index** (~30 phút):
   - Thêm index `{partner: 1, code: 1}` partial unique (where code exists)

4. **Admin handler + service** (~1 ngày):
   - Update CreateEvent/UpdateEvent API: nhận `code` field
   - Validate uniqueness per partner
   - Search: support search-by-code

5. **Display wire** (~1-2 ngày):
   - Helper function `BuildEventLabel(event) string` → `[code] name` hoặc fallback `name` nếu code empty
   - Apply ở admin handler responses (event list, content list, reconciliation)
   - Email templates: thêm `EventCode` field (similar TCB CashFlowOptions pattern)
   - Export XLSX/CSV: thêm cột "Code"

6. **Frontend admin** (~1 ngày):
   - Form: thêm input "Code" (admin-only field, ops type)
   - List: column code (sortable, searchable)
   - Filter: search bao gồm code
   - Dropdown campaign: render `[code] name`

7. **Test** (~0.5 ngày)

### Phase 2: Ambassador (~3-5 ngày)
Tương tự Phase 1.

**Total**: ~1-2 tuần.

## Risks + mitigations

1. **Naming convention**: 3 sản phẩm dùng prefix khác (TCB-, VCR-, AMB-) hay tự do?
   - **Mitigation**: convention per-product, không enforce cross-product. Document trong admin UI hint.
2. **Migration data cũ**: event đã chạy có cần code không?
   - **Mitigation**: optional ban đầu, admin update khi cần. Không break existing display.
3. **Search performance**: nếu code rất nhiều và dài → search-by-text có thể chậm
   - **Mitigation**: index `code` field. Nếu search full-text thì dùng MongoDB text index.
4. **i18n**: Code thường là English/code-style, không cần i18n. Display label `[code] name` áp dụng mọi locale như nhau.
   - **Mitigation**: không cần i18n cho code field.
5. **Cross-partner duplicate**: 2 partner khác nhau có thể muốn dùng cùng code → unique constraint chỉ within partner
   - **Mitigation**: index `{partner: 1, code: 1}` partial unique.

## Files referenced

**TCB (source of truth)**:
- `internal/model/mg/event.go:48` (Code field)
- `internal/model/mg/event.go:120-121` (GetSearchString include code)
- `internal/service/event.go:137-138` (display label format)
- Commit `5169f48d` — full wire trên backend + dashboard
- Commit `6eee128d` — hotfix required code
- Commit `34d1fded` — refactor isStaff verification logic
- Commit `907a35ae` — UI styling (mute color)

**vCreator (target — chưa có)**:
- `internal/model/mg/event.go` — KHÔNG có Code field
- KHÔNG có wire trong service/handler/email/export

**Ambassador (target — chưa có)**:
- Tương tự vCreator

## Lịch sử phân loại

- **2026-05-10 (initial P2)**: User self-listed gap. Quote: "Thêm tên nội bộ cho campaign / TCB thêm code vào tất cả những chỗ hiển thị campaign, giúp phân biệt tên của campaign cho user xem và trong Ban tổ chức xem" + "P2".
  - Lý do P2: business value rõ (BTC dễ communicate), effort thấp (~1 field + wire 5-7 chỗ), TCB pattern production-tested. Pair tốt với #7 (dashboard) hoặc #37 (rejection analytics).
