# Gap #37 — Chuẩn hóa lý do từ chối content (rejection tags) — chỉ TCB có, vCreator/Ambassador chưa có

> **Priority**: 🟡 **P2** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: TCB → vCreator + Ambassador
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi admin reject content của creator, lý do từ chối hiện tại:
- **TCB**: có **danh sách tag chuẩn hóa** (14 tag predefined: broken_link, missing_cta, wrong_content, ...) + comment tự do (cho tag "other"). Mỗi content lưu `RejectionTags []string` + `RejectionComment string`. Có aggregate pipeline thống kê reject reason theo tag.
- **vCreator + Ambassador**: KHÔNG có hệ thống tag — chỉ có `RejectedBy` + `RejectedAt`. Lý do reject (nếu có) chỉ là free-text trong field khác hoặc không lưu rõ ràng.

→ Hệ quả: TCB **thống kê được** "tháng này có 30% content bị reject vì missing_hashtag, 20% vì wrong_content" → cải thiện chất lượng creator. vCreator/Amb **không thống kê được** xu hướng reject → không có insight để training/feedback.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Field `Content.RejectionTags []string` | ✅ | ❌ | ❌ |
| Field `Content.RejectionComment string` | ✅ | ❌ | ❌ |
| Master list 14 tag chuẩn hóa (i18n vi/en) | ✅ | ❌ | ❌ |
| Validation `IsValidRejectionTag()` | ✅ | ❌ | ❌ |
| API `GET /admin/rejection-tags` (cho dropdown UI) | ✅ | ❌ | ❌ |
| Aggregate analytics theo tag (`approval_analytics.go`) | ✅ | ❌ | ❌ |
| Legacy fallback grouping by free-text reason | ✅ | — | — |

## Hệ quả

- **vCreator + Ambassador**: ops không biết creator hay phạm lỗi gì nhất → không feedback hệ thống được → chất lượng content không cải thiện
- **Cross-product**: nếu cả 3 sản phẩm dùng chung master list → có thể compare metrics rejection cross-product
- **Không phải bug active**, là enhancement giúp ops/PM có data ra quyết định

## Liên quan các gap khác

- **Gap #15 (Reconciliation engine)**: TCB đã dùng `buildRejectReason` trong reconciliation_checklist (có 3 references). Khi vCr/Amb port reconciliation (gap #15) → có thể wire reject reason cùng lúc.
- **Gap #2 (InfluencerProfile)**: rejection rate là một signal cho creator scoring/rating

## Giải pháp

### Phase 1: vCreator (~3-5 ngày)
1. **Constants** (~30 phút):
   - Copy file `internal/constants/rejection_tags.go` (~65 LOC) — 14 tag predefined + helpers
2. **Model migration** (~1 giờ):
   - Thêm field `RejectionTags []string` + `RejectionComment string` vào `Content` struct
3. **Admin handler** (~1-2 giờ):
   - Thêm endpoint `GET /admin/rejection-tags` trả static list cho frontend
   - Update `RejectContent` API: nhận `rejectionTags`, `rejectionComment` trong body, validate qua `IsValidRejectionTag`
4. **Frontend admin** (~1 ngày):
   - Reject dialog: multi-select tag (i18n) + comment field (required nếu chọn "other")
   - i18n vi/en
5. **Aggregate pipeline analytics** (~1 ngày):
   - Copy `approval_analytics.go` aggregate (handle cả tag list lẫn legacy reason fallback)
   - Dashboard widget: "top 5 reject reasons last 30 days"
6. **Test** (~0.5 ngày)

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1

**Total**: ~1-2 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P2

- **Business value rõ**: data-driven feedback creator → tăng chất lượng content theo thời gian
- **Effort thấp**: ~150 LOC tổng (constants + struct + handler + analytics) — TCB đã có pattern production-ready
- **Không urgent**: không phải bug active, là enhancement
- **Independent**: không depend on gap khác để bắt đầu, nhưng pair tốt với #15 (reconciliation port)

→ Nice-to-have, làm khi có sprint trống hoặc làm chung wave với #15.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có 14 rejection tag chuẩn hóa (i18n vi/en) + field `Content.RejectionTags` + analytics aggregate pipeline. vCr/Amb chỉ có `RejectedBy`/`RejectedAt` — không có tag, không có analytics.

## Verify code

### TCB (source of truth)

**Constants** — `internal/constants/rejection_tags.go` (65 LOC):
```go
type RejectionTag struct {
    Key     string `json:"key"`
    LabelVI string `json:"label_vi"`
    LabelEN string `json:"label_en"`
}

const RejectionTagOther = "other" // special tag requires comment

var RejectionTags = []RejectionTag{
    {"broken_link", "Link lỗi / không truy cập được", "Broken or inaccessible link"},
    {"missing_cta", "Thiếu/sai lời kêu gọi hành động (CTA)", "Missing or incorrect CTA"},
    {"wrong_content", "Sai chủ đề chương trình", "Content doesn't match campaign topic"},
    {"missing_link", "Thiếu link ở bio/comment/caption", "Missing link in bio/comment/caption"},
    {"wrong_brand_name", "Sai tên thương hiệu", "Incorrect brand name usage"},
    {"wrong_info", "Sai thông tin (thời gian, hạn mức...)", "Incorrect information (timing, amount...)"},
    {"poor_quality", "Chất lượng kém (âm thanh, hình ảnh)", "Poor quality (audio/visual)"},
    {"brand_inappropriate", "Không phù hợp hình ảnh thương hiệu", "Inappropriate for brand image"},
    {"missing_hashtag", "Thiếu hashtag", "Missing hashtag"},
    {"missing_disclaimer", "Thiếu disclaimer/khuyến cáo", "Missing disclaimer text"},
    {"duplicate", "Nội dung trùng lặp", "Duplicate content"},
    {"ineligible", "Không đủ điều kiện tham gia", "Not eligible to participate"},
    {"no_reason", "Chưa có lý do", "No reason provided"},
    {RejectionTagOther, "Lý do khác", "Other reason"},
}

func IsValidRejectionTag(key string) bool { ... }
func GetRejectionTagLabels(keys []string, lang string) []string { ... }
```

**Model** — `internal/model/mg/content.go:53-54`:
```go
RejectionTags    []string `bson:"rejectionTags,omitempty" json:"rejectionTags,omitempty"`
RejectionComment string   `bson:"rejectionComment,omitempty" json:"rejectionComment,omitempty"`
// (trong cùng struct với RejectedBy, RejectedAt đã có)
```

**Admin handler** — `pkg/admin/handler/content.go`:
- Line 22-24: cache static response (`rejectionTagsOnce sync.Once + rejectionTagsCache`)
- Line 56-57: interface method `GetRejectionTags(c) error`
- Line 474-486: handler implementation `GET /admin/rejection-tags`

**Analytics** — `internal/module/database/mongodb/aggregate_pipeline/approval_analytics.go`:
- Line 30, 189-224: tag-based analytics với fallback grouping by free-text reason cho legacy data
- Line 384-385: tương tự cho 1 pipeline khác (multiple aggregate flavors)

**Reconciliation usage** — `internal/service/reconciliation_checklist.go:586, 598-599, 758`:
```go
func (s *checklistImpl) buildRejectReason(cl *modelmg.ReconciliationChecklistResultRaw) string { ... }
// Build reject reason string từ failed checklist items → wire vào reject content flow
```

### vCreator status

```bash
# Constants
ls vcreator/backend/internal/constants/rejection_tags.go → ❌ KHÔNG có

# Model
grep "RejectionTags\|RejectionComment" vcreator/backend/internal/model/mg/content.go → ❌ KHÔNG có
# Chỉ có:
RejectedBy AppID     `bson:"rejectedBy,omitempty"`
RejectedAt time.Time `bson:"rejectedAt"`

# Note: vCreator có field `User.StaffRejectReason` nhưng đây là cho user/staff approval flow,
# KHÔNG phải cho content reject.
```

### Ambassador status

```bash
ls ambassabor/backend/internal/constants/rejection_tags.go → ❌ KHÔNG có
# Tương tự vCreator: chỉ có RejectedBy + RejectedAt, không có tag/comment
```

## Đề xuất implementation

### Phase 1: vCreator (~3-5 ngày)

1. **Constants** (~30 phút):
   ```bash
   cp tcb/internal/constants/rejection_tags.go vcr/internal/constants/rejection_tags.go
   ```
   Adapt package name nếu khác.

2. **Model migration** (~1 giờ):
   ```go
   // vcreator/backend/internal/model/mg/content.go (thêm sau line 46)
   RejectionTags    []string `bson:"rejectionTags,omitempty" json:"rejectionTags,omitempty"`
   RejectionComment string   `bson:"rejectionComment,omitempty" json:"rejectionComment,omitempty"`
   ```
   Migration data cũ: nullable, không backfill (data cũ không có tag → analytics fallback grouping by free-text reason như TCB legacy pattern).

3. **Admin handler** (~1-2 giờ):
   - Endpoint `GET /admin/rejection-tags` (static cache với `sync.Once`)
   - Update reject content API: validate `RejectionTags` qua `IsValidRejectionTag`, require comment nếu chứa `RejectionTagOther`

4. **Frontend admin** (~1 ngày):
   - Reject dialog: `MultiSelect` component cho tags + `TextArea` cho comment
   - Validate: nếu chọn "other" → require comment
   - i18n vi/en

5. **Analytics** (~1 ngày):
   - Copy aggregate pipeline `approval_analytics.go` adapt với schema vCr
   - Dashboard widget cho ops view top reject reasons

6. **Test** (~0.5 ngày):
   - Unit test validation
   - Integration test: reject với valid tag, invalid tag, "other" missing comment
   - Aggregate test: cả new tag + legacy reason fallback

### Phase 2: Ambassador (~3-5 ngày)
Tương tự Phase 1.

**Total**: ~1-2 tuần.

## Risks + mitigations

1. **Master list 14 tag có phù hợp business vCr/Amb không?**: TCB là B2B finance, có tag "wrong_brand_name", "missing_disclaimer" — vCr/Amb business B2B brand/gaming có thể cần tag khác
   - **Mitigation**: review master list với product mỗi sản phẩm, có thể tách thành config per-product hoặc accept là 14 tag base + extend
2. **Migration data cũ**: vCr/Amb có content reject cũ chỉ với `RejectedBy/RejectedAt` không có tag → analytics chỉ thống kê được data sau release
   - **Mitigation**: chấp nhận, dùng pattern legacy fallback của TCB (grouping by free-text reason nếu có) hoặc skip data cũ
3. **i18n**: cần localization vi/en như TCB
   - **Mitigation**: hỗ trợ vi/en như TCB, có thể extend "ph" cho vCreator-PH sau (gap separate)
4. **Duplicate code 3 sản phẩm**: 14 tag list duplicate
   - **Mitigation**: chấp nhận hiện tại, long-term có thể move lên at-core shared package (gap separate)

## Files referenced

**TCB (source of truth)**:
- `internal/constants/rejection_tags.go` (65 LOC — master list + helpers)
- `internal/model/mg/content.go:53-54` (RejectionTags + RejectionComment fields)
- `pkg/admin/handler/content.go:22-24, 56-57, 474-486` (GET /rejection-tags endpoint)
- `internal/module/database/mongodb/aggregate_pipeline/approval_analytics.go` (analytics with legacy fallback)
- `internal/service/reconciliation_checklist.go:586, 598-599, 758` (buildRejectReason for reconciliation flow)

**vCreator (target — chưa có)**:
- KHÔNG có `internal/constants/rejection_tags.go`
- KHÔNG có fields `RejectionTags`, `RejectionComment` trong `Content` struct
- Chỉ có `User.StaffRejectReason` (khác scope — cho user approval, không phải content)

**Ambassador (target — chưa có)**:
- Tương tự vCreator

## Lịch sử phân loại

- **2026-05-10 (initial P2)**: User self-listed gap. Quote: "Chuẩn hóa lí do từ chối content -> đánh tag hủy để sau này còn thống kê, TCB mới có" + "P2".
  - Lý do P2: business value rõ (data-driven feedback creator), effort thấp (~150 LOC), không urgent. Pair tốt với #15 (reconciliation port).
