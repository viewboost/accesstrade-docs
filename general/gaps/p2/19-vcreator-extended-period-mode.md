# Gap #19 — vCreator Extended Period mode (cho phép ghi nhận content sau khi event kết thúc, gán về kỳ kế toán cũ)

> **Priority**: 🟡 **P2** (reclassified P3→P2 2026-05-10 — user confirm cần giữ trong backlog)
> **Source**: Initial gap-analysis #19
> **Direction port**: vCreator → TCB/Ambassador (selective, cần product confirm có cần không)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Sau khi event kết thúc, vCreator vẫn cho phép admin **bật chế độ Extended Period** — content post sau ngày kết thúc vẫn được ghi nhận, NHƯNG ngày ghi nhận sẽ map về **tháng/năm kỳ kế toán cũ** (vd post 3/3/2026 → ghi sổ 3/12/2025).

Use case business:
- Event tháng 12/2025 kết thúc 31/12, nhưng creator post bài thật vào ngày 2/1/2026 → cần tính vào doanh thu tháng 12 cho đúng kỳ tài chính
- Đối soát quyết toán cuối kỳ với khách hàng (TCB enterprise đôi khi cần điều chỉnh kỳ ghi nhận)
- Cho phép linh hoạt khi chốt budget event mà creator post trễ vài ngày

TCB và Ambassador **không có** feature này — content post sau `endAt` thì bị reject hoàn toàn, không ghi nhận.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Cho phép content post sau `endAt`? | ❌ Reject | ✅ Có (nếu `ExtendedPeriod.Enabled`) | ❌ Reject |
| Field config `ExtendedPeriodConfig` trong Event | ❌ | ✅ `{Enabled, RecordMonth, RecordYear}` | ❌ |
| Helper `IsExtendedPeriod()` + `GetRecordingDate()` | ❌ | ✅ | ❌ |
| API admin `UpdateExtendedPeriod` | ❌ | ✅ `pkg/admin/handler/event.go:307` | ❌ |
| Frontend admin form bật/tắt + chọn tháng/năm | ❌ | ✅ `admin/src/pages/event` | ❌ |
| Tích hợp `content_flow.go` map ngày recording | ❌ | ✅ `service/content_flow.go:37-43` | ❌ |

## Hệ quả

- **TCB**: nếu khách hàng (vd Techcombank) có yêu cầu "cho phép quyết toán linh hoạt cuối kỳ" → hiện không support → phải tạo event mới hoặc nhập liệu manual
- **Ambassador**: tương tự — không có cơ chế adjust kỳ ghi nhận khi creator post trễ
- **Đặc thù business**: Đây không phải bug, là **feature linh hoạt** vCreator có vì khách hàng vCr (B2B brand như Trường Sinh, CaSe) có nhu cầu này thường xuyên

## Giải pháp (cần product confirm trước)

Port `ExtendedPeriodConfig` từ vCreator sang TCB/Ambassador:
1. Backend: copy struct + 3 helper methods (`IsExtendedPeriod`, `GetRecordingDate`, `GetRecordingDateTime`) — ~50 LOC
2. Admin handler `UpdateExtendedPeriod` + request body
3. Tích hợp vào `content_flow.go` để map ngày khi tính reward
4. Admin frontend: form bật/tắt + chọn RecordMonth/RecordYear

**Effort**: ~3-5 ngày mỗi sản phẩm (backend + admin frontend).

**Cần product confirm**:
1. TCB/Ambassador có khách hàng yêu cầu quyết toán linh hoạt như vCr không?
2. Nếu có, business rule giống vCr (giữ day, đổi month+year) hay khác?
3. Edge case: nếu RecordMonth không có ngày tương ứng (vd 31 mà tháng 2) → vCr fallback "last day of month" — TCB/Amb có chấp nhận?

→ **P2 vì**: feature có giá trị business rõ ràng (kỳ kế toán) nhưng chưa có incident hay khiếu nại từ khách hàng TCB/Amb. Backlog đợi khách hàng request.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

vCreator có `ExtendedPeriodConfig` struct + 3 helpers + admin endpoint `UpdateExtendedPeriod` + tích hợp `content_flow.go`. TCB/Ambassador không có gì tương đương.

## Verify code

### vCreator (source of truth)

**Model** — `internal/model/mg/event.go:81-105`:
```go
type ExtendedPeriodConfig struct {
    Enabled     bool `bson:"enabled" json:"enabled"`
    RecordMonth int  `bson:"recordMonth" json:"recordMonth"`
    RecordYear  int  `bson:"recordYear" json:"recordYear"`
}

// EventRaw có field:
// ExtendedPeriod *ExtendedPeriodConfig `bson:"extendedPeriod,omitempty"`

func (s *EventRaw) IsExtendedPeriod() bool {
    return s != nil && s.ExtendedPeriod != nil && s.ExtendedPeriod.Enabled
}

func (s *EventRaw) GetRecordingDate(actualDate time.Time) time.Time {
    if s.ExtendedPeriod == nil || !s.ExtendedPeriod.Enabled {
        return actualDate
    }
    _, _, d := util.TimeOfDayInHCM(actualDate).Date()
    year := s.ExtendedPeriod.RecordYear
    month := time.Month(s.ExtendedPeriod.RecordMonth)
    t := time.Date(year, month, d, 0, 0, 0, 0, util.TimeLocationHCM)

    // Fallback nếu day không có trong month đích (vd 31 mà month=2)
    if t.Month() != month {
        t = time.Date(year, month+1, 0, 0, 0, 0, 0, util.TimeLocationHCM) // last day
    }
    return t.UTC()
}
```

**Caller chính** — `internal/service/content_flow.go:37-43`:
```go
if event.IsExtendedPeriod() {
    src := content.PostedAt
    mapped := event.GetRecordingDate(src)
    // dùng mapped làm ngày ghi nhận thay vì PostedAt
}
```

**Admin handler** — `pkg/admin/handler/event.go:306-320`:
```go
// PUT /v1/admin/events/:id/extended-period
func (u eventImpl) UpdateExtendedPeriod(c echo.Context) error {
    payload := cc.Get(constants.KeyPayload).(request.EventExtendedPeriodBody)
    data, err := s.UpdateExtendedPeriod(ctx, eventId, payload)
    ...
}
```

**Frontend** — `admin/src/pages/event/`:
- Type definition: `type.d.ts` có `extendedPeriod`
- Model: `model.ts` có effect `updateExtendedPeriod`
- API config: `configs/api.ts` có endpoint
- Locale: vi-VN.ts có labels "Chế độ ghi nhận mở rộng"

### TCB status

```bash
grep -rn "ExtendedPeriod" techcombank/backend/internal → ❌ KHÔNG có
grep -rn "ExtendedPeriod" techcombank/admin/src → ❌ KHÔNG có
```

### Ambassador status

```bash
grep -rn "ExtendedPeriod" ambassabor/backend/internal → ❌ KHÔNG có
grep -rn "ExtendedPeriod" ambassabor/admin/src → ❌ KHÔNG có
```

## Đề xuất implementation

### Phase 1: Product alignment (1-2 ngày)
- Confirm với product TCB/Ambassador có khách hàng cần kỳ kế toán linh hoạt
- Define edge case: fallback last-day-of-month có chấp nhận không

### Phase 2: Backend port (1-2 ngày mỗi sản phẩm)
- Copy struct `ExtendedPeriodConfig` vào `event.go`
- Copy 3 methods: `IsExtendedPeriod`, `GetRecordingDate`, `GetRecordingDateTime`
- Thêm field `ExtendedPeriod` vào `EventRaw`
- Tích hợp vào content flow service

### Phase 3: Admin (1-2 ngày mỗi sản phẩm)
- Handler `UpdateExtendedPeriod` + request body
- Frontend form bật/tắt + chọn RecordMonth/RecordYear
- Locale strings vi/en

**Total**: ~3-5 ngày mỗi sản phẩm.

## Risks + mitigations

1. **Đối soát kế toán bị sai**: nếu admin bật nhầm Extended Period → ghi nhận sai kỳ
   - **Mitigation**: log audit + require role admin cao + show rõ trên UI
2. **Reward calc 2 lần**: nếu trong period chuyển tiếp, content post `endAt + 1 day` được tính cho cả kỳ cũ lẫn kỳ mới
   - **Mitigation**: ExtendedPeriod chỉ map ngày, KHÔNG đổi event → reward vẫn theo event đó. Test kỹ edge case.
3. **Migration**: TCB/Amb có data event cũ không có field này → mặc định nil/disabled, không break

## Files referenced

**vCreator (source of truth)**:
- `internal/model/mg/event.go:81-160` (struct + helpers)
- `internal/service/content_flow.go:37-43` (caller)
- `internal/service/event.go` (UpdateExtendedPeriod service)
- `pkg/admin/handler/event.go:306-320` (handler)
- `admin/src/pages/event/{type.d.ts,model.ts}`
- `admin/src/configs/api.ts` (endpoint)

**TCB/Ambassador (target — chưa có)**:
- KHÔNG có struct `ExtendedPeriodConfig`
- KHÔNG có endpoint `UpdateExtendedPeriod`
- KHÔNG có frontend form

## Lịch sử phân loại

- **Initial**: P3 (Total 5) — đánh giá ban đầu là "vCreator-specific, không port"
- **Reclassified P3→P2 (2026-05-10)**: User confirm cần giữ trong backlog với mô tả đầy đủ. Lý do: feature có business value rõ (kỳ kế toán linh hoạt), chỉ là chưa có khách hàng TCB/Amb yêu cầu — backlog đợi request.
