# Extended Period Campaign - Giải pháp mở lại Campaign đã kết thúc

## 1. Bối cảnh & Vấn đề

### Tình huống

Campaign kết thúc vào cuối năm 2025. Khách hàng muốn **mở lại** để:
- Creator submit thêm video mới
- Hệ thống tiếp tục crawl và đếm lượt xem (view)

### Yêu cầu đặc biệt

> Dù creator submit vào năm 2026, nhưng toàn bộ số liệu (ngày submit, lượt xem, thống kê) phải được **ghi nhận như thuộc năm 2025** — để báo cáo và thống kê không bị lẫn sang năm mới.

### Điểm chặn hiện tại

| Điểm chặn | File | Logic |
|---|---|---|
| Submit bị block | `backend/pkg/public/service/content.go` | `event.IsValid()` → check `EndAt.After(now)` → `false` |
| Crawl không chạy | `backend/pkg/public/service/schedule.go` | Query chỉ tìm campaign `status=active` + `endAt > now` |
| Analytics ghi 2026 | Toàn bộ hệ thống | `time.Now()` / `util.TimeStartOfDayInHCM(time.Now())` |

### Giải quyết điểm chặn submit & crawl

**Admin vào web cập nhật `endAt`** sang ngày tương lai (VD: 30/06/2026) → Campaign active trở lại → `IsValid()` pass → crawl chạy → creator submit được. **Không cần sửa code.**

---

## 2. Tổng quan giải pháp

### Nguyên tắc cốt lõi

1. **Tách docs riêng (separate documents)**: Mọi data trong extended period được lưu vào document riêng với flag `isExtended: true`, **không đụng vào data gốc**
2. **Date mapping**: Mọi ngày trong 2026 được map về **tháng 12/2025** (giữ ngày, đổi tháng+năm)
3. **Cash = 0đ**: Extended period không tính tiền thưởng
4. **Tái sử dụng logic**: Không viết code mới cho extended — dùng lại flow hiện tại, chỉ thêm filter `isExtended`

### Quy tắc Date Mapping

```
Ngày thực (2026)          →  Ngày ghi nhận (2025)
─────────────────────────────────────────────────
3/3/2026                  →  3/12/2025
15/4/2026                 →  15/12/2025
28/5/2026                 →  28/12/2025
1/3/2026 và 1/4/2026      →  cùng 1/12/2025 (dồn bucket)
```

**Quy tắc**: Giữ nguyên ngày (`day`), tháng → 12, năm → 2025.

> **Lưu ý**: Nhiều ngày thực có thể map vào cùng 1 ngày 2025 (VD: 1/3 và 1/4 đều → 1/12). Điều này **không phải vấn đề** vì hệ thống đã xử lý nhiều flows cùng ngày (crawl chạy 2 lần/ngày). Các flows tích lũy đúng qua aggregate.

---

## 3. Kiến trúc hệ thống

### Collections bị ảnh hưởng

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTENDED PERIOD                          │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │ ContentRaw  │    │ ContentFlowRaw   │    │EventRewardRaw │  │
│  │             │    │                  │    │               │  │
│  │ date: 12/25 │    │ date: 12/25      │    │ date: 12/25   │  │
│  │ isExtended  │    │ isExtended: true │    │ isExtended    │  │
│  │             │    │ không bị xóa     │    │ cash: 0đ      │  │
│  └──────┬──────┘    └────────┬─────────┘    └───────┬───────┘  │
│         │                    │                      │          │
│         ▼                    ▼                      ▼          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ContentAnalyticDailyRaw                     │   │
│  │              isExtended: true                            │   │
│  │              chain Begin/End độc lập                     │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  EventAnalyticDailyRaw / UserEventAnalyticDailyRaw      │   │
│  │  Tự động đúng qua aggregate (sum cả gốc + extended)     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Model Changes

### 4.1 EventRaw — Thêm config Extended Period

**File**: `backend/internal/model/mg/event.go`

```go
type EventRaw struct {
    // ... existing fields ...

    // Extended Period Config
    ExtendedPeriod *ExtendedPeriodConfig `bson:"extendedPeriod,omitempty" json:"extendedPeriod,omitempty"`
}

type ExtendedPeriodConfig struct {
    Enabled      bool      `bson:"enabled" json:"enabled"`
    RecordMonth  int       `bson:"recordMonth" json:"recordMonth"`   // Tháng ghi nhận (12)
    RecordYear   int       `bson:"recordYear" json:"recordYear"`     // Năm ghi nhận (2025)
}
```

**Helper method**:

```go
// GetRecordingDate trả về ngày ghi nhận cho extended period
// Input: 3/3/2026 → Output: 3/12/2025 (giữ day, đổi month+year)
func (s *EventRaw) GetRecordingDate(actualDate time.Time) time.Time {
    if s.ExtendedPeriod == nil || !s.ExtendedPeriod.Enabled {
        return actualDate
    }
    l, _ := time.LoadLocation("Asia/Ho_Chi_Minh")
    _, _, d := actualDate.In(l).Date()
    mapped := time.Date(
        s.ExtendedPeriod.RecordYear,
        time.Month(s.ExtendedPeriod.RecordMonth),
        d, 0, 0, 0, 0, l,
    ).UTC()
    return mapped
}

func (s *EventRaw) IsExtendedPeriod() bool {
    return s.ExtendedPeriod != nil && s.ExtendedPeriod.Enabled
}
```

### 4.2 ContentFlowRaw — Thêm flag isExtended

**File**: `backend/internal/model/mg/content_flow.go`

```go
type ContentFlowRaw struct {
    // ... existing fields ...
    IsExtended bool `bson:"isExtended,omitempty"`
}
```

### 4.3 ContentAnalyticDailyRaw — Thêm flag isExtended

**File**: `backend/internal/model/mg/content_analytic_daily.go`

```go
type ContentAnalyticDailyRaw struct {
    // ... existing fields ...
    IsExtended bool `bson:"isExtended,omitempty"`
}
```

### 4.4 EventRewardRaw — Thêm flag isExtended

**File**: `backend/internal/model/mg/event_reward.go`

```go
type EventRewardRaw struct {
    // ... existing fields ...
    IsExtended bool `bson:"isExtended,omitempty" json:"isExtended,omitempty"`
}
```

### 4.5 ContentRaw — Thêm flag isExtended

**File**: `backend/internal/model/mg/content.go`

```go
type ContentRaw struct {
    // ... existing fields ...
    IsExtended bool `bson:"isExtended,omitempty"`
}
```

> **Tổng model changes**: Chỉ thêm 1 field `IsExtended bool` vào 4 collections + 1 struct `ExtendedPeriodConfig` trong EventRaw. Không đụng vào field nào hiện có.

---

## 5. Luồng chi tiết

### 5.1 Luồng Creator Submit Video

```
Creator submit video (3/3/2026)
│
▼
content.Create()
│
├── Kiểm tra event.IsValid() ──────── ✅ Pass (admin đã đẩy endAt)
├── Kiểm tra event.IsExtendedPeriod()
│   │
│   ├── TRUE:
│   │   ├── content.Date = event.GetRecordingDate(time.Now())  → 3/12/2025
│   │   ├── content.IsExtended = true
│   │   └── content.CreatedAt = time.Now()                     → 3/3/2026 (giữ nguyên)
│   │
│   └── FALSE:
│       └── Hoạt động bình thường (date = time.Now())
│
├── Tạo ContentRaw ─────── Insert vào DB
│
└── Gọi UpdateAnalyticEventDaily()
    ├── Query: { event: ID, date: 3/12/2025 }
    ├── ContentRaw có date=3/12/2025 → đếm vào bucket 12/2025
    └── Upsert EventAnalyticDailyRaw cho ngày 3/12/2025
```

**File cần sửa**: `backend/pkg/public/service/content.go` — hàm `Create()`, dòng 138:

```go
// TRƯỚC:
Date: util.TimeStartOfDayInHCM(time.Now()),

// SAU:
Date: util.TimeStartOfDayInHCM(event.GetRecordingDate(time.Now())),
```

Thêm flag:

```go
IsExtended: event.IsExtendedPeriod(),
```

---

### 5.2 Luồng Crawl & Đếm View

```
Schedule Crawl (chạy 2 lần/ngày)
│
▼
Tìm active campaigns ──── Query: { status: "active", startAt <= now, endAt > now }
│                          (Campaign đã được admin mở lại → nằm trong kết quả)
▼
Tìm content cần crawl ─── Query: { event: ID, status: { $in: [approved, waiting] } }
│                          (Bao gồm cả content isExtended=true)
▼
Gửi URL → Content Catcher (external service)
│
▼
Nhận kết quả: { view: 15000, like: 200, comment: 50 }
│
▼
CreateFlow() ─────────────────────────────────────────────────────────
│
├── Kiểm tra event.IsExtendedPeriod()
│   │
│   ├── TRUE → timeOverride = event.GetRecordingDate(time.Now())
│   │          isExtended = true
│   │
│   └── FALSE → timeOverride = nil (bình thường)
│
├── CreateView(ctx, content, 15000, timeOverride)
│   │
│   ├── getContentTotalValue() ── Lấy total hiện tại từ ContentAnalyticDaily
│   │   │                         (aggregate TẤT CẢ records, bao gồm extended)
│   │   │                         → currentView = 14500
│   │   │
│   │   └── delta = 15000 - 14500 = 500
│   │
│   └── Insert ContentFlowRaw:
│       ├── Date:       3/12/2025      (mapped)
│       ├── Value:      500            (delta)
│       ├── NewValue:   15000
│       ├── OldValue:   14500
│       ├── IsExtended: true
│       └── CreatedAt:  3/3/2026       (thời gian thực - tracking)
│
├── CreateLike() ── Tương tự, isExtended = true
├── CreateComment() ── Tương tự, isExtended = true
│
├── Update content statistic ── (view.total = 15000 — absolute, không phụ thuộc date)
│
├── ContentAnalyticDaily().Update() ──────────────────────────────
│   │
│   │  ┌─────────────────────────────────────────────────────────┐
│   │  │ Aggregate ContentFlowRaw WHERE:                         │
│   │  │   date = 3/12/2025                                      │
│   │  │   content = contentID                                   │
│   │  │   isExtended = true         ← FILTER RIÊNG             │
│   │  └─────────────────────────────────────────────────────────┘
│   │
│   ├── Tìm ContentAnalyticDailyRaw: { date: 3/12/2025, content: ID, isExtended: true }
│   │
│   ├── CHƯA CÓ → Tìm analyticYesterday:
│   │   │   { content: ID, isExtended: true, date < 3/12/2025 }
│   │   │   → Không tìm thấy (chưa có extended record nào trước đó)
│   │   │   → Begin = 0
│   │   │
│   │   └── Insert ContentAnalyticDailyRaw:
│   │       ├── Date:       3/12/2025
│   │       ├── Month:      12
│   │       ├── Year:       2025
│   │       ├── IsExtended: true
│   │       ├── View:       { Begin: 0, Value: 500, End: 500 }
│   │       └── CreatedAt:  3/3/2026
│   │
│   └── ĐÃ CÓ → Update record hiện tại:
│       └── Re-aggregate tất cả extended flows cho ngày đó
│           View: { Begin: 0, Value: 750, End: 750 }  (500 + 250 từ crawl trước)
│
└── Tạo Extended EventRewardRaw ──────────────────────────────────
    │
    └── Upsert: { event: ID, content: ID, date: 3/12/2025, isExtended: true }
        ├── Date:       3/12/2025
        ├── Cash:       0              ← KHÔNG TÍNH TIỀN
        ├── IsExtended: true
        ├── Statistic:
        │   ├── TotalView:        500  (delta view trong extended period)
        │   ├── TotalCashView:    0
        │   ├── TotalLike:        20
        │   ├── TotalCashLike:    0
        │   └── TotalComment:     5
        │       TotalCashComment: 0
        └── CreatedAt:  3/3/2026
```

**Files cần sửa**:
- `backend/internal/service/content_flow.go` — `CreateFlow()`, `CreateView()`, `CreateLike()`, `CreateComment()`
- `backend/internal/service/content_analytic_daily.go` — `Update()`

---

### 5.3 Luồng Aggregate Analytics (Tự động)

```
RecheckEventAnalyticDaily (chạy mỗi 4 giờ)
│
▼
Iterate active events
│
▼
UpdateAnalyticEventDaily(event, date)
│
├── Aggregate ContentRaw WHERE { event: ID, date: q.FromAt }
│   │  → Bao gồm cả content isExtended=true
│   │  → Đếm content theo source (TikTok, YouTube, ...)
│   └── → TotalCreator, TotalContent, TotalContentPending, ...
│
├── Aggregate EventRewardRaw WHERE { event: ID, date: q.FromAt }
│   │  → Bao gồm cả extended rewards (cash=0)
│   │  → Sum view/like/comment
│   └── → Cash vẫn đúng vì extended cash = 0
│
└── Upsert EventAnalyticDailyRaw { event: ID, date: q.FromAt }
    ├── Statistic.View.Total = gốc + extended (tự động sum)
    ├── Statistic.Cash.Total = chỉ gốc (extended = 0)
    ├── Statistic.Tiktok.TotalContent = gốc + extended
    ├── Month: 12
    └── Year: 2025
```

**Không cần sửa code** — `UpdateAnalyticEventDaily` aggregate tất cả records cho event+date, tự động bao gồm extended data.

---

### 5.4 Luồng DeleteContentFlow (Bảo vệ Extended)

```
DeleteContentFlow (chạy hàng ngày)
│
▼
Query ContentAnalyticDailyRaw:
│  {
│    auditStatus: "valid",
│    isExtended: { $ne: true },     ← BỎ QUA EXTENDED
│    date: { $lte: now - 30 ngày }
│  }
│
├── Extended docs: BỊ SKIP ──────── Data extended tồn tại mãi mãi
│
└── Normal docs: Xử lý bình thường
    ├── Backup flows → content-flow-backup
    └── Delete flows gốc
```

**File cần sửa**: `backend/internal/service/content_analytic_daily.go` — `DeleteContentFlow()`

---

### 5.5 Luồng Audit (Bỏ qua Extended)

```
Audit() (chạy hàng ngày)
│
▼
Query ContentAnalyticDailyRaw:
│  {
│    auditStatus: "pending",
│    isExtended: { $ne: true },     ← BỎ QUA EXTENDED
│    date: { $lt: today }
│  }
│
├── Extended docs: BỎ QUA
│
└── Normal docs: Kiểm tra View.Value == sum(flows)
    ├── Match → auditStatus = "valid"
    └── Mismatch → auditStatus = "invalid"
```

**File cần sửa**: `backend/internal/service/content_analytic_daily.go` — `Audit()`

---

## 6. Tổng hợp files cần sửa

### Backend Models (thêm field)

| File | Thay đổi |
|---|---|
| `backend/internal/model/mg/event.go` | Thêm `ExtendedPeriod *ExtendedPeriodConfig`, method `GetRecordingDate()`, `IsExtendedPeriod()` |
| `backend/internal/model/mg/content.go` | Thêm `IsExtended bool` |
| `backend/internal/model/mg/content_flow.go` | Thêm `IsExtended bool` |
| `backend/internal/model/mg/content_analytic_daily.go` | Thêm `IsExtended bool` |
| `backend/internal/model/mg/event_reward.go` | Thêm `IsExtended bool` |

### Backend Services (sửa logic)

| File | Hàm | Thay đổi |
|---|---|---|
| `backend/pkg/public/service/content.go` | `Create()` | Date mapping + set `isExtended` khi tạo content |
| `backend/internal/service/content_flow.go` | `CreateFlow()` | Inject `timeOverride` + set `isExtended` trên flows |
| `backend/internal/service/content_flow.go` | `CreateView/Like/Comment()` | Set `isExtended` trên flow records |
| `backend/internal/service/content_analytic_daily.go` | `Update()` | Filter flows by `isExtended`, tìm `analyticYesterday` trong chain đúng |
| `backend/internal/service/content_analytic_daily.go` | `DeleteContentFlow()` | Skip extended records |
| `backend/internal/service/content_analytic_daily.go` | `Audit()` | Skip extended records |
| `backend/internal/service/event_schema.go` | `UpdateRewardTypeByStatisticContent()` | Tạo extended reward (cash=0) thay vì reward thường |

### Backend Admin

| File | Hàm | Thay đổi |
|---|---|---|
| `backend/pkg/admin/handler/event.go` | API endpoint | Thêm API bật/tắt extended period |
| `backend/pkg/admin/service/event.go` | Service | Logic enable/disable extended period |

---

## 7. Data Flow tổng quan

```
                    ┌──────────────────────┐
                    │    Admin Web Panel    │
                    │                      │
                    │  1. Đẩy endAt ra     │
                    │  2. Bật Extended      │
                    │     Period            │
                    │     month=12          │
                    │     year=2025         │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐   ┌───────────────┐   ┌───────────────────┐
   │   Creator    │   │  Crawl Job    │   │ RecheckAnalytic   │
   │   Submit     │   │  (2 lần/ngày) │   │ (mỗi 4 giờ)      │
   └──────┬──────┘   └───────┬───────┘   └─────────┬─────────┘
          │                   │                     │
          ▼                   ▼                     │
   ┌─────────────┐   ┌───────────────┐              │
   │ ContentRaw  │   │ContentFlowRaw │              │
   │             │   │               │              │
   │ date: 12/25 │   │ date: 12/25   │              │
   │ isExtended  │   │ isExtended    │              │
   └──────┬──────┘   │ KHÔNG XÓA     │              │
          │          └───────┬───────┘              │
          │                  │                      │
          │                  ▼                      │
          │          ┌────────────────┐              │
          │          │ContentAnalytic │              │
          │          │DailyRaw       │              │
          │          │               │              │
          │          │ date: 12/25   │              │
          │          │ isExtended    │              │
          │          │ chain riêng   │              │
          │          └───────┬───────┘              │
          │                  │                      │
          │                  ▼                      │
          │          ┌───────────────┐               │
          │          │EventRewardRaw │               │
          │          │               │               │
          │          │ date: 12/25   │               │
          │          │ isExtended    │               │
          │          │ cash: 0đ      │               │
          │          └───────┬───────┘               │
          │                  │                       │
          ▼                  ▼                       ▼
   ┌─────────────────────────────────────────────────────┐
   │              EventAnalyticDailyRaw                   │
   │              UserEventAnalyticDailyRaw               │
   │                                                      │
   │  Aggregate: ContentRaw + EventRewardRaw              │
   │  → Sum tự động bao gồm extended data                │
   │  → View tăng ✅   Cash không đổi ✅                  │
   │  → date: 12/2025, month: 12, year: 2025             │
   └─────────────────────────────────────────────────────┘
```

---

## 8. Ví dụ Data thực tế

### Trước khi bật Extended Period (data gốc 2025)

**ContentAnalyticDailyRaw** (cho 1 video submit 1/10/2025):
```json
{
  "content": "abc123",
  "date": "2025-12-30T17:00:00Z",
  "isExtended": false,
  "view": { "begin": 9000, "value": 1000, "end": 10000 },
  "like": { "begin": 180, "value": 20, "end": 200 },
  "month": 12,
  "year": 2025
}
```

### Sau khi bật Extended Period (data mới 2026, ghi nhận 2025)

**ContentFlowRaw** (crawl ngày 3/3/2026):
```json
{
  "content": "abc123",
  "date": "2025-12-02T17:00:00Z",
  "value": 500,
  "newValue": 10500,
  "oldValue": 10000,
  "isExtended": true,
  "createdAt": "2026-03-03T10:30:00Z"
}
```

**ContentAnalyticDailyRaw** (extended doc riêng):
```json
{
  "content": "abc123",
  "date": "2025-12-02T17:00:00Z",
  "isExtended": true,
  "view": { "begin": 0, "value": 500, "end": 500 },
  "like": { "begin": 0, "value": 15, "end": 15 },
  "month": 12,
  "year": 2025
}
```

**ContentFlowRaw** (crawl ngày 3/4/2026, cùng map về 3/12/2025):
```json
{
  "content": "abc123",
  "date": "2025-12-02T17:00:00Z",
  "value": 300,
  "newValue": 10800,
  "oldValue": 10500,
  "isExtended": true,
  "createdAt": "2026-04-03T10:30:00Z"
}
```

**ContentAnalyticDailyRaw** (cùng doc extended, được update):
```json
{
  "content": "abc123",
  "date": "2025-12-02T17:00:00Z",
  "isExtended": true,
  "view": { "begin": 0, "value": 800, "end": 800 },
  "like": { "begin": 0, "value": 25, "end": 25 },
  "month": 12,
  "year": 2025
}
```

**EventRewardRaw** (extended, cash=0):
```json
{
  "event": "event456",
  "content": "abc123",
  "date": "2025-12-02T17:00:00Z",
  "isExtended": true,
  "cash": 0,
  "statistic": {
    "totalView": 800,
    "totalCashView": 0,
    "totalLike": 25,
    "totalCashLike": 0,
    "totalComment": 10,
    "totalCashComment": 0
  },
  "createdAt": "2026-03-03T10:30:00Z"
}
```

---

## 9. Các trường hợp biên (Edge Cases)

### 9.1 Content mới submit trong extended period

- Không có data gốc trong 2025
- `analyticYesterday` (filtered by `isExtended: true`) → không tìm thấy → `Begin = 0`
- Chain Begin/End bắt đầu từ 0 → **OK**

### 9.2 Content cũ (2025) tiếp tục được crawl view

- Có data gốc (isExtended: false) trong 2025
- Extended chain hoàn toàn độc lập (isExtended: true) → `Begin = 0`
- `getContentTotalValue()` aggregate TẤT CẢ ContentAnalyticDaily (cả gốc + extended) → tính delta đúng
- Data gốc KHÔNG bị đụng → **OK**

### 9.3 Crawl chạy nhiều tháng, date collision

- 1/3/2026 và 1/4/2026 đều map về 1/12/2025
- Flows dồn vào cùng bucket, aggregate sum đúng
- Extended flows không bị xóa bởi `DeleteContentFlow` → tích lũy mãi → **OK**

### 9.4 Tắt Extended Period

- Admin set `ExtendedPeriod.Enabled = false`
- Mọi hoạt động trở lại bình thường
- Data extended đã tạo vẫn còn trong DB (không bị xóa)
- Có thể query riêng bằng `isExtended: true` nếu cần xem lại

### 9.5 Report/Export cần tách riêng data gốc vs extended

- Filter `isExtended: { $ne: true }` → chỉ data gốc
- Filter `isExtended: true` → chỉ data extended
- Không filter → tổng hợp tất cả (behavior mặc định)

---

## 10. Checklist Implementation

- [ ] **Model**: Thêm `ExtendedPeriodConfig` vào `EventRaw`
- [ ] **Model**: Thêm `IsExtended bool` vào `ContentRaw`, `ContentFlowRaw`, `ContentAnalyticDailyRaw`, `EventRewardRaw`
- [ ] **Service**: Sửa `content.Create()` — date mapping + isExtended
- [ ] **Service**: Sửa `CreateFlow()` — inject timeOverride + isExtended cho flows
- [ ] **Service**: Sửa `ContentAnalyticDaily.Update()` — filter by isExtended, chain riêng
- [ ] **Service**: Sửa `DeleteContentFlow()` — skip `isExtended: true`
- [ ] **Service**: Sửa `Audit()` — skip `isExtended: true`
- [ ] **Service**: Sửa `UpdateRewardTypeByStatisticContent()` — tạo extended reward (cash=0)
- [ ] **Admin API**: Thêm endpoint bật/tắt extended period cho event
- [ ] **Admin UI**: Thêm toggle extended period trong trang event detail
- [ ] **Testing**: Test submit content trong extended period
- [ ] **Testing**: Test crawl view cho content extended
- [ ] **Testing**: Test DeleteContentFlow không xóa extended
- [ ] **Testing**: Test EventAnalyticDaily aggregate bao gồm extended
- [ ] **Testing**: Test report filter gốc vs extended
