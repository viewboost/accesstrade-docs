# Gap #21 — Ambassador có hệ thống Mission/Gamification (nhiệm vụ + thưởng + level), TCB/vCreator không có

> **Priority**: 🟡 **P2** (reclassified P3→P2 2026-05-10 — user confirm cần giữ trong backlog)
> **Source**: Initial gap-analysis #21
> **Direction port**: Ambassador → vCreator/TCB (selective, cần product confirm)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Ambassador có **Mission system** — gamification layer cho creator: thay vì chỉ "post bài → nhận thưởng" thường, creator có thể nhận **nhiệm vụ cụ thể** (hashtag + view threshold + time window) → hoàn thành → unlock thưởng cố định + tăng level.

Tên cũ "WildRift" đến từ business gốc: hệ thống được thiết kế ban đầu phục vụ campaign game **Wild Rift (LoL Mobile của Riot)**, nhưng giờ là feature generic — bất kỳ partner nào dùng Ambassador đều có thể tạo mission.

TCB và vCreator **không có** feature này.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Mission system có?** | ❌ | ❌ | ✅ ~1327 LOC backend |
| Hashtag-based completion check | ❌ | ❌ | ✅ |
| View threshold + time window (vd "10k view trong 7 ngày") | ❌ | ❌ | ✅ |
| Level (độ khó tăng dần 1-N) | ❌ | ❌ | ✅ |
| Cover image multi-platform | ❌ | ❌ | ✅ |
| Display window khác Active window (preview trước khi mở) | ❌ | ❌ | ✅ |
| Mission category + partner grouping | ❌ | ❌ | ✅ |

## Hệ quả

- **TCB**: B2B finance (campaign đẩy thẻ tín dụng / sản phẩm bank) → gamification kiểu "đạt 10k view trong 7 ngày" không phù hợp business
- **vCreator**: B2B brand (Trường Sinh, CaSe) → tương tự, không phải gaming/entertainment → không cần
- **Ambassador**: gaming/entertainment-friendly (Wild Rift partnership) → mission system match business

→ Gap này **không phải bug**, là **business model difference**. Defer port trừ khi TCB/vCr có khách hàng campaign gaming/entertainment.

## Giải pháp (cần product confirm)

**Khi nào port?**
- TCB/vCr có khách hàng campaign gaming, entertainment, hoặc loyalty program
- Product muốn unify reward engine có gamification layer optional

**Effort dự kiến**: ~3-4 tuần mỗi sản phẩm (port ~1327 LOC backend + admin frontend + public flow + integrate reward engine).

**Cần product confirm**:
1. TCB/vCr có khách hàng nào yêu cầu gamification không?
2. Nếu port, mission có là feature optional (toggle per-partner) hay default?
3. Tích hợp như thế nào với reward engine hiện tại (mission reward cộng với campaign reward, hay thay thế)?

→ **P2 vì**: feature có giá trị business rõ trong domain entertainment/gaming/loyalty, nhưng TCB/vCr business model hiện tại không match. Backlog đợi product alignment.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Ambassador có Mission feature ~1327 LOC: 1 model + admin service 576 LOC + public service 713 LOC. TCB/vCreator không có gì tương đương.

## Verify code

### Ambassador (source of truth)

**Model** — `internal/model/mg/mission.go` (38 LOC):
```go
type MissionRaw struct {
    ID              AppID
    Name            string                   // tiêu đề
    Description     string                   // mô tả
    Cover           []*FilePhotoWithPlatform // ảnh cover theo platform (FB/TikTok/...)
    Level           int8                     // độ khó 1-N
    StartAt, EndAt  time.Time                // thời gian active
    DisplayStartAt, DisplayEndAt time.Time   // thời gian hiển thị (có thể khác active — preview)
    Status          string                   // active/inactive/draft
    Reward          int64                    // thưởng cố định
    Type            string                   // loại mission
    Hashtag         []string                 // hashtag yêu cầu
    ApplyForSources []string                 // platform (TikTok, FB, IG, ...)
    NumberOfViews   *int64                   // điều kiện view (optional)
    NumberOfDays    *int64                   // điều kiện time window (optional)
    Category        AppID                    // group
    Partner         AppID                    // brand owner
    Order           int8                     // ordering trong list
    CreatedAt, UpdatedAt time.Time
}
```

**Services**:
- `pkg/admin/service/mission.go` (576 LOC) — CRUD + approve flow + lifecycle
- `pkg/public/service/mission.go` (713 LOC) — creator list/detail/submit + completion check
- Handler + router + locale + DAO đầy đủ 3 layer

**Caller pattern**: creator submit content với hashtag → service check completion (hashtag match + view threshold + time window) → trigger reward.

### TCB status

```bash
find techcombank/backend -name "*mission*" → ❌ KHÔNG có
```

### vCreator status

```bash
find vcreator/backend -name "*mission*" → ❌ KHÔNG có
```

## Đề xuất implementation (nếu approved)

### Phase 1: Product alignment (1 tuần)
- Confirm khách hàng TCB/vCr có nhu cầu gamification
- Quyết định mission là feature toggle per-partner hay default
- Define tích hợp với reward engine: mission reward độc lập hay overlay với campaign reward

### Phase 2: Backend port (2 tuần mỗi sản phẩm)
- Copy `MissionRaw` model + DAO
- Port admin service ~576 LOC (CRUD + approve)
- Port public service ~713 LOC (list/detail/completion check)
- Adapt với reward engine target

### Phase 3: Admin frontend (1 tuần mỗi sản phẩm)
- Mission management page
- Cover upload multi-platform
- Hashtag + condition config UI

### Phase 4: Public/creator UX (1 tuần)
- Mission list cho creator
- Progress tracking (view count vs threshold)
- Notification khi hoàn thành

**Total**: ~3-4 tuần mỗi sản phẩm.

## Risks + mitigations

1. **Business model mismatch**: TCB B2B finance không phù hợp gamification gaming-style
   - **Mitigation**: feature toggle per-partner, không default enable
2. **Double reward**: nếu mission overlay với campaign reward → creator có thể nhận 2 lần
   - **Mitigation**: define rõ trong reward engine (flag `RewardSource`: mission vs campaign)
3. **Completion check performance**: mission cần check view threshold mỗi creator → query nặng nếu nhiều mission active
   - **Mitigation**: cron daily aggregate, không real-time

## Files referenced

**Ambassador (source of truth)**:
- `internal/model/mg/mission.go` (38 LOC)
- `internal/locale/mission.go`
- `pkg/admin/service/mission.go` (576 LOC)
- `pkg/admin/handler/mission.go`
- `pkg/admin/router/mission.go`
- `pkg/admin/model/{request,response}/mission.go`
- `pkg/public/service/mission.go` (713 LOC)
- `pkg/public/handler/mission.go`
- `pkg/public/router/mission.go`
- `pkg/public/router/routevalidation/mission.go`

**TCB/vCreator (target — chưa có)**:
- KHÔNG có file `*mission*` ở backend
- KHÔNG có frontend admin/public mission

## Lịch sử phân loại

- **Initial**: P3 (Total 5) — đánh giá "Ambassador-specific business model, KHÔNG port"
- **Reclassified P3→P2 (2026-05-10)**: User confirm cần giữ trong backlog với mô tả đầy đủ. Lý do: feature có business value rõ trong domain gamification/loyalty, defer port nhưng giữ visibility cho khi product có khách hàng phù hợp.
