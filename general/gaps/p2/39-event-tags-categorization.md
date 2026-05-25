# Gap #39 — Thêm tag phân loại cho thử thách (campaign tags) — TCB có, vCreator/Ambassador có model Tag nhưng chưa link với Event

> **Priority**: 🟡 **P2** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: TCB → vCreator + Ambassador
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi platform chạy nhiều campaign cùng lúc, **BTC cần gộp campaign theo nhóm tag** để dễ quản lý/filter:
- "Ra mắt sản phẩm" — nhóm campaign launch
- "Theo mùa/dịp lễ" — campaign Tết, Black Friday, ...
- "Chạy liên tục" — campaign always-on
- "Nội bộ nhân viên" — campaign cho staff
- "Tăng tương tác", "Chuyển đổi/bán hàng", "Nhận diện thương hiệu"

TCB có **`Event.EventTags []AppID`** link tới collection `Tag` (type = `event`). 7 tag default được seed sẵn + admin có thể thêm tag custom với màu riêng.

vCreator + Ambassador **đã có model `TagRaw`** (giống TCB) nhưng:
- vCreator: tag được dùng cho `Content.WarningTags` (cảnh báo content) — khác mục đích
- Cả 2: `EventRaw` **không có** field `EventTags` → không link tag với event

→ Infrastructure tag đã sẵn (model + admin pages) nhưng **chưa wire** vào event categorization.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Model `TagRaw` (Type, Name, Color, Active, Partner) | ✅ | ✅ | ✅ |
| `TagType.Event` constant | ✅ | ❌ (có TagType khác) | ❌ |
| Admin pages quản lý tag | ✅ | ✅ (cho WarningTags) | ❓ |
| **Field `Event.EventTags []AppID`** | ✅ | ❌ | ❌ |
| Seed 7 default event tags | ✅ | ❌ | ❌ |
| Filter event list by tag | ✅ | ❌ | ❌ |
| Display tag với color trên admin | ✅ | (cho content) | (cho content) |

## Hệ quả

- **vCr + Amb**: BTC khó group/filter campaign khi có nhiều cái cùng chủ đề → phải search bằng name (kết quả không gom đầy đủ nếu tên khác nhau)
- **Reporting**: không thống kê được "tổng spend Q1 2026 cho nhóm 'Ra mắt sản phẩm' là bao nhiêu" → không phục vụ planning
- **Cross-campaign analysis**: không phân tích được performance theo tag (ví dụ campaign "Theo mùa/dịp lễ" có engagement cao hơn "Chạy liên tục" hay không)

## Liên quan các gap khác

- **Gap #38 (Event code)**: cùng touch admin display layer event — combo wave hợp lý
- **Gap #7 (Dashboard executive)**: dashboard cần filter theo tag để view group performance
- **Gap #37 (Rejection tags)**: không liên quan trực tiếp — đây là tag cho event, kia là tag cho rejection reason

## Giải pháp

### Phase 1: vCreator (~3-5 ngày)
1. **Constants** (~30 phút):
   - Thêm `TagType.Event = "event"` vào `internal/constants/tag.go`
2. **Model migration** (~1 giờ):
   - Thêm `EventTags []AppID` vào `EventRaw` struct (`bson:"eventTags,omitempty"`)
3. **Seed default tags** (~1 giờ):
   - Copy `SeedEventTags()` từ TCB (7 tag default + color)
   - Wire vào `initialize.go` startup
   - Có thể adapt tag list cho business vCr (vd thêm "Brand B2B", "Workplace internal", ...)
4. **Admin handler** (~1-2 giờ):
   - Update create/update event API: nhận `eventTags []string` (mongo IDs) + validation
   - Update list/detail response: trả `EventTags []EventTagInfo` (resolve ID → name + color)
   - Filter event list by tag IDs
5. **Frontend admin** (~1 ngày):
   - Form: multi-select tag (autocomplete, hiển thị color chip)
   - List: column tags hiển thị chip
   - Filter sidebar: filter event by tags
6. **Test** (~0.5 ngày)

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1, có thể adapt tag list theo business Amb

**Total**: ~1-2 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P2

- **Business value rõ**: BTC ops/PM/finance quản lý campaign theo nhóm dễ hơn
- **Effort thấp**: model `TagRaw` đã sẵn, chỉ thêm 1 field + seed + frontend (~5-7 chỗ)
- **Không urgent**: nice-to-have, không phải bug active
- **Pair tốt với #38** (event code) vì cùng touch admin display layer event

→ Làm khi có sprint trống, combo với #38 cho hiệu quả.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có field `Event.EventTags []AppID` + 7 default event tags được seed + admin filter/display. vCr/Amb có model `TagRaw` (giống TCB) nhưng `EventRaw` không có field `EventTags` → tag chưa link với event.

## Verify code

### TCB (source of truth)

**Model** — `internal/model/mg/event.go:56`:
```go
type EventRaw struct {
    // ...
    EventTags []AppID `bson:"eventTags,omitempty" json:"eventTags"`
    // ...
}
```

**Tag model** — `internal/model/mg/tag.go`:
```go
type TagRaw struct {
    ID           AppID
    SearchString string
    Type         string  // "event", "cheating_warning_high", etc.
    Name         string
    Color        string  // hex code
    Active       bool
    Partner      AppID   // optional, để partner-scoped
    CreatedAt, UpdatedAt time.Time
}
```

**TagType constants** — `internal/constants/tag.go`:
```go
var TagType = struct {
    // ...
    Event string  // "event"
    // 17 tag types khác (cheating, opshub, content rate, ...)
}{
    Event: "event",
    // ...
}
```

**Seed default** — `pkg/admin/server/initialize/seed_tag.go:86-130`:
```go
func SeedEventTags() {
    eventTags := []struct {
        Name  string
        Color string
    }{
        {"Nhận diện thương hiệu", "#3B82F6"},
        {"Ra mắt sản phẩm", "#F97316"},
        {"Theo mùa/dịp lễ", "#EF4444"},
        {"Chạy liên tục", "#22C55E"},
        {"Nội bộ nhân viên", "#6B7280"},
        {"Tăng tương tác", "#8B5CF6"},
        {"Chuyển đổi/bán hàng", "#EC4899"},
    }

    for _, tagData := range eventTags {
        // Idempotent: skip nếu existing
        existingTag := new(modelmg.TagRaw)
        tagDAO.FindOne(ctx, existingTag, bson.M{
            "type": constants.TagType.Event,
            "name": tagData.Name,
        })
        if !existingTag.ID.IsZero() { continue }

        // Create new
        newTag := &modelmg.TagRaw{
            ID:           modelmg.NewAppID(),
            Name:         tagData.Name,
            SearchString: format.NonAccentVietnamese(tagData.Name),
            Type:         constants.TagType.Event,
            Color:        tagData.Color,
            Active:       true,
            CreatedAt:    now,
            UpdatedAt:    now,
        }
        tagDAO.InsertOne(ctx, newTag)
    }
}
```

Wire trong `initialize.go:22`: `SeedEventTags()` chạy ở app startup.

**Admin API** — `pkg/admin/`:
- `model/request/event.go:50, 73`:
  ```go
  EventTags []string `json:"eventTags"`
  validation.Field(&m.EventTags, validation.Each(is.MongoID...))
  ```
- `model/response/event.go:57`:
  ```go
  EventTags []EventTagInfo `json:"eventTags"`  // resolved with name + color
  ```
- `service/event.go:319, 675`:
  ```go
  // Update
  "eventTags": update.EventTags,
  // Create
  if len(body.EventTags) > 0 { ... }
  ```

### vCreator status

**Tag model** — `internal/model/mg/tag.go`: ✅ giống TCB nhưng dùng cho mục đích khác.

**Event field**: ❌ KHÔNG có `EventTags`:
```bash
grep -nE "EventTags" vcreator/backend/internal/model/mg/event.go → empty
```

**TagType.Event**: ❌ KHÔNG có constant này.

**Tag usage hiện tại**: chỉ có `Content.WarningTags []AppID` (cảnh báo content).

**Admin pages tag**: tồn tại tại `admin/src/pages/tag/` nhưng cho `WarningTags` chứ chưa có Event tag.

### Ambassador status

**Tag model** — `internal/model/mg/tag.go`: ✅ giống TCB.

**Event field**: ❌ KHÔNG có `EventTags`.

**Admin pages tag**: ❓ chưa verify chi tiết, có thể không có hoặc tương tự vCr.

## Đề xuất implementation

### Phase 1: vCreator (~3-5 ngày)

1. **Constants** (~30 phút):
   ```go
   // vcreator/backend/internal/constants/tag.go
   var TagType = struct {
       // ... existing
       Event string
   }{
       // ... existing
       Event: "event",
   }
   ```

2. **Model** (~30 phút):
   ```go
   // internal/model/mg/event.go
   type EventRaw struct {
       // ...
       EventTags []AppID `bson:"eventTags,omitempty" json:"eventTags"`
       // ...
   }
   ```

3. **Seed default** (~1 giờ):
   ```bash
   cp tcb/pkg/admin/server/initialize/seed_tag.go vcr/pkg/admin/server/initialize/seed_tag.go
   ```
   - Adapt tag list theo business vCr (có thể giữ 7 tag TCB hoặc thêm "Brand B2B", "Workplace internal")
   - Wire vào `initialize.go`

4. **Admin handler + service** (~1-2 giờ):
   - Request body `EventTags []string` + validation MongoID
   - Response struct `EventTagInfo {ID, Name, Color}` + resolve aggregate
   - Service create/update wire `eventTags`
   - List filter: `?eventTags=id1,id2`

5. **Frontend admin** (~1 ngày):
   - Form: `MultiSelect` với option render color chip
   - List page: column "Tags" hiển thị chip
   - Filter sidebar: tag filter

6. **Test** (~0.5 ngày):
   - Create event với tags → verify save + display
   - Filter event list by tag → verify result
   - Seed idempotent (run 2 lần không tạo duplicate)

### Phase 2: Ambassador (~3-5 ngày)
Tương tự Phase 1.

**Total**: ~1-2 tuần.

## Risks + mitigations

1. **Tag list khác business**: TCB là B2B finance, 7 tag mặc định có thể không phù hợp hoàn toàn vCr/Amb
   - **Mitigation**: tag là dynamic (admin tự thêm), seed chỉ là defaults — admin có thể disable/edit
2. **Migration data cũ**: event đã chạy không có tag
   - **Mitigation**: optional, không backfill. Admin tag từng event thủ công nếu cần
3. **Conflict TagType với vCr**: vCr có thể đã có TagType khác cho WarningTags → thêm `Event` không conflict
   - **Mitigation**: TagType là string literal, không enum strict, thêm "event" type không break existing
4. **Display performance**: list event với populate tags → N+1 query
   - **Mitigation**: aggregate $lookup, hoặc cache tag list (chỉ ~10-20 tag, không nhiều)
5. **Color picker UX**: admin có thể chọn màu khó nhìn
   - **Mitigation**: preset color palette như TCB (7 màu Tailwind), không full free picker

## Files referenced

**TCB (source of truth)**:
- `internal/model/mg/event.go:56` (EventTags field)
- `internal/model/mg/tag.go` (TagRaw model)
- `internal/constants/tag.go` (TagType.Event constant)
- `pkg/admin/server/initialize/seed_tag.go:86-130` (SeedEventTags 7 defaults)
- `pkg/admin/server/initialize/initialize.go:22` (wire seed at startup)
- `pkg/admin/model/request/event.go:50, 73` (EventTags request + validation)
- `pkg/admin/model/response/event.go:57` (EventTags response with name + color)
- `pkg/admin/service/event.go:319, 675` (create/update wire eventTags)

**vCreator (target — partial — có Tag model nhưng chưa link Event)**:
- `internal/model/mg/tag.go` ✅ ĐÃ CÓ
- `internal/model/mg/event.go` — KHÔNG có EventTags field
- `internal/constants/tag.go` — KHÔNG có TagType.Event
- `pkg/admin/server/initialize/` — KHÔNG có SeedEventTags
- `admin/src/pages/tag/` ✅ ĐÃ CÓ (cho WarningTags) nhưng chưa wire Event

**Ambassador (target — partial — có Tag model)**:
- `internal/model/mg/tag.go` ✅ ĐÃ CÓ
- `internal/model/mg/event.go` — KHÔNG có EventTags field
- KHÔNG có TagType.Event, SeedEventTags

## Lịch sử phân loại

- **2026-05-10 (initial P2)**: User self-listed gap. Quote: "Thêm tag phân loại cho thử thách / Gộp nhiều campaign lại theo tag để hỗ trợ quản lý" + "P2".
  - Lý do P2: business value rõ (BTC quản lý campaign theo nhóm), effort thấp (model Tag đã sẵn 3 sản phẩm, chỉ thêm 1 field + seed + frontend), pair tốt với #38 (event code).
