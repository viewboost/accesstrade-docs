# Gap #16 — vCreator/Ambassador thiếu hệ thống đánh giá creator (review + rating) — phần tiếp nối của gap #2

> **Priority**: 🟠 **P1** (sau gap #15, trước gap #31)
> **Source**: Initial gap-analysis #16
> **Direction port**: TCB → vCr/Amb (phần tiếp nối của gap #2 InfluencerProfile)
> **Last verified**: 2026-05-07
> **Dependency**: Phải có gap #2 (InfluencerProfile) phase 1 hoàn thành trước

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Sau khi creator hoàn thành campaign, **brand cần đánh giá chất lượng làm việc** của creator để:
- Có signal trust khi book lại creator cùng cho campaign mới
- Brand khác xem rating khi quyết định chọn creator
- Filter creator có rating cao trong khi browse pool creator
- Track performance creator theo thời gian (trung bình tăng/giảm)

**Không có review/rating** = brand đánh giá creator dựa trên cảm tính + memory cá nhân. Khi pool creator lớn (hàng nghìn creator), brand không thể nhớ hết → khó book lại creator giỏi.

## Hiện trạng 3 sản phẩm

### TCB — Có hệ thống đầy đủ ✅
- **5 tiêu chí review** (1-5 sao mỗi tiêu chí, optional):
  - Content Quality (chất lượng nội dung)
  - Professionalism (tính chuyên nghiệp)
  - Communication (giao tiếp)
  - On-Time Delivery (đúng hạn)
  - Performance Rating (hiệu quả tổng thể)
- **OverallRating tự động tính** = trung bình các tiêu chí có rating
- **Review text optional** (brand viết thêm nhận xét)
- **Visibility flag**: `private` (chỉ brand thấy) hoặc `public` (mọi brand thấy)
- **RatingCache** aggregate per-creator: trung bình rating qua tất cả reviews + tổng số reviews
- **Time-decay weight** (lưu ý: TCB có code mock, có thể chưa hoàn thiện 100%)

### vCreator + Ambassador — Không có gì ❌
- KHÔNG có collection `profile_review`
- KHÔNG có collection `rating_cache`
- KHÔNG có service review/rating
- KHÔNG có khái niệm "đánh giá creator"

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Có khái niệm review creator?** | ✅ Có | ❌ Không | ❌ Không |
| **5 tiêu chí đánh giá** | ✅ Có | — | — |
| **OverallRating tự tính** | ✅ Có | — | — |
| **RatingCache aggregate per-creator** | ✅ Có | — | — |
| **Time-decay weight** (review cũ giảm trọng số) | ✅ Có | — | — |
| **Visibility private/public** | ✅ Có | — | — |
| **Filter creator theo rating** | ✅ Có | — | — |
| **Cross-campaign aggregation** | ✅ Có | — | — |

## Hệ quả khi không có (vCreator/Ambassador)

1. **Brand đánh giá cảm tính**: không có dữ liệu chấm điểm → khó so sánh khách quan
2. **Khó book lại creator giỏi**: với pool lớn, brand không nhớ creator nào tốt → mất cơ hội repeat business
3. **Không có signal trust giữa các brand**: brand mới không biết creator nào uy tín → tin vào marketing self-claim
4. **Không có công cụ feedback creator**: creator không biết mình điểm yếu chỗ nào → không cải thiện được
5. **Không filter creator theo chất lượng**: phải duyệt từng creator một, không có shortcut "rating ≥ 4 sao"

## Mối quan hệ với gap #2 (InfluencerProfile)

**Gap #16 là phần tiếp nối của gap #2** — không thể tách rời:
- ProfileReview liên kết qua `ProfileID` → cần collection `influencer_profile` ở Ambassador/vCreator trước (gap #2)
- RatingCache cũng theo `ProfileID` → cần InfluencerProfile làm root entity
- Brand portal browse creator (gap #2) sẽ filter theo rating (gap #16) — nên có rating thì mới đầy đủ giá trị brand portal

→ **Thứ tự triển khai bắt buộc**:
1. Gap #2 phase 1: Ambassador port InfluencerProfile (2-3 tuần) — BẮT BUỘC
2. Gap #16 cho Ambassador (~2 tuần) — sau khi gap #2 phase 1 xong
3. Gap #2 phase 2: vCreator port InfluencerProfile (~1 tháng)
4. Gap #16 cho vCreator (~2 tuần) — sau khi gap #2 phase 2 xong

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port hệ thống review + rating từ TCB sang Ambassador và vCreator, **làm sau gap #2 từng phase**.

**3 Options triển khai**:

### Option A (recommended) — Port standalone sau gap #2 từng phase
- Sau khi gap #2 phase 1 hoàn thành (Ambassador có InfluencerProfile) → port gap #16 cho Ambassador (~2 tuần)
- Sau khi gap #2 phase 2 hoàn thành (vCreator có InfluencerProfile) → port gap #16 cho vCreator (~2 tuần)
- **Effort**: 2 phases × 2 tuần = 4 tuần real time (sau khi gap #2 đã xong)
- **Pros**: clean integration, không phình scope gap #2
- **Cons**: brand portal Ambassador phase 1 chưa có filter rating

### Option B — Combine với gap #2 thành 1 task lớn
- Port InfluencerProfile + Review + Rating cùng 1 lần
- **Effort**: gap #2 phase 1 từ 2-3 tuần → 4-5 tuần
- **Pros**: brand portal Ambassador hoàn chỉnh ngay
- **Cons**: scope gap #2 phình to, deploy risk cao hơn

### Option C — Skip cho vCreator
- Chỉ port cho Ambassador (creator economy có brand thật)
- vCreator B2B workplace, không có brand external → không cần review
- **Effort**: 2 tuần (chỉ Ambassador)
- **Pros**: tiết kiệm effort
- **Cons**: nếu vCreator long-term tham gia creator pool unification (gap #2 phase 3) → vẫn cần rating consistent

**Đề xuất default**: **Option A** — port standalone sau gap #2 từng phase. Đảm bảo gap #2 deploy stable trước khi thêm rating layer.

## Cần product/business confirm trước khi triển khai

1. **Brand portal Ambassador** có cần filter creator theo rating ngay phase 1 không, hay defer phase 2?
2. **TCB review system production**: đang chạy thật không, hay chỉ scaffolding chưa wire (cần verify thêm — code có comment "Phase 02 mock" gợi ý partial implementation)?
3. **vCreator có brand external không**? Nếu B2B workplace internal-only → review không có ý nghĩa → skip vCreator
4. **Time-decay weight**: TCB có nhưng có vẻ chưa hoàn thiện — port không hay simplify (rating đơn giản không decay)?
5. **Visibility private/public**: business model vCr/Amb có khái niệm này không? Mặc định public hết được không?
6. **5 tiêu chí TCB** có phù hợp Ambassador không? Hay Ambassador cần custom criteria (vd: "Engagement", "Brand Fit")?

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có **2 collections + 2 services**:
- `profile_review` — store reviews (627 LOC service `review.go`)
- `rating_cache` — aggregated rating per-profile (cached, recompute trigger by event)
- `service/review.go` — CRUD reviews (Submit, Get, List, Edit)
- `service/rating_aggregation.go` — recompute cached rating

vCr/Amb hoàn toàn không có gì (0 LOC, 0 collections).

## Verify code

### TCB ProfileReview model

```go
// internal/model/mg/profile_review.go
type ProfileReview struct {
    ID, CampaignID, ProfileID, BrandID, ReviewerUserID primitive.ObjectID

    // 5 tiêu chí (1-5 stars, optional)
    ContentQuality, Professionalism, Communication, OnTimeDelivery, PerformanceRating *int

    // Auto-calculated
    OverallRating float64

    // Optional
    ReviewText *string

    // Metadata
    Visibility string  // "private" | "public"
    Status     string  // "active" | "deleted"

    CreatedAt, UpdatedAt time.Time
}
```

### TCB RatingCache model

```go
// internal/model/mg/rating_cache.go
type RatingCache struct {
    ProfileID string
    AvgOverall, AvgContentQuality, AvgProfessionalism, AvgCommunication, AvgOnTime, AvgPerformance float64
    TotalReviews int
    LastRecalculatedAt time.Time
}
```

### TCB Review service interface

```go
// internal/service/review.go
type ReviewServiceInterface interface {
    SubmitReview(ctx, req SubmitReviewRequest, userID, brandID string) (*ProfileReview, error)
    GetReview(ctx, reviewID string) (*ProfileReview, error)
    ListReviews(ctx, profileID string, page, limit int) (*ListReviewsResult, error)
    EditReview(ctx, reviewID string, req UpdateReviewRequest, userID string) (*ProfileReview, error)
}
```

### TCB Rating Aggregation service

```go
// internal/service/rating_aggregation.go
type AggregationService interface {
    RecalculateProfileRating(ctx, profileID string) error
    GetCachedRating(ctx, profileID string) (*RatingCache, error)
}
```

**Lưu ý**: Code có comment:
```go
// reviewDAO will be injected by Phase 02 during integration (Phase 07)
// For now, we use direct MongoDB queries as mock
```

→ Service rating aggregation **chưa hoàn thiện 100%** — TCB đã build incremental, có dấu vết phases. Khi port cần verify TCB production có dùng thật không.

### TCB Admin handler

- `pkg/admin/handler/review.go` — admin review CRUD endpoints
- `pkg/admin/router/review.go` — router
- `pkg/admin/router/routevalidation/review.go` — validation

### vCr/Amb status

```bash
# vCreator
ls vcreator/backend/internal/model/mg/ | grep -iE "review|rating" → 0 results
ls vcreator/backend/internal/service/ | grep -iE "review|rating" → 0 results

# Ambassador — same
```

→ Không có gì.

## Đề xuất implementation

### Phase 1: Schema (~1-2 ngày mỗi sản phẩm)

1. **Tạo collection `profile_review`** với 13 fields giống TCB
2. **Tạo collection `rating_cache`** với 9 fields giống TCB
3. **Index trên** `profile_id`, `brand_id`, `campaign_id`, `created_at` cho query nhanh
4. **Foreign key**: `profile_id` reference `influencer_profile.id` (cần gap #2 hoàn thành trước)

### Phase 2: Service review (~3-5 ngày)

5. **Copy `review.go`** từ TCB (~627 LOC, 4 fns)
6. **Adapt**:
   - Permission check (TCB dùng brand role, vCr/Amb có thể khác)
   - Validate `profile_id` exists trong `influencer_profile` collection
   - Validate `campaign_id` exists trong `event` collection (vCr/Amb dùng event thay vì campaign)
7. **Trigger recalculate rating**: sau mỗi SubmitReview/EditReview → call `RatingAggregation().RecalculateProfileRating(profileID)`

### Phase 3: Service rating aggregation (~2-3 ngày)

8. **Copy `rating_aggregation.go`** từ TCB
9. **Hoàn thiện logic** (TCB có comment "mock" → có thể chưa wire đầy đủ):
   - Query tất cả reviews active của profile
   - Tính trung bình per criteria
   - Optional: time-decay weight (review > 6 tháng giảm 50%, > 1 năm giảm 80%)
   - Update RatingCache
10. **Cron**: optional — schedule recompute định kỳ cho profiles inactive (không có review mới gần đây nhưng cần refresh sau time-decay)

### Phase 4: Admin handler + brand portal integration (~3-5 ngày)

11. **Copy 3 admin handler files** từ TCB
12. **Brand portal**:
    - Trang list creator: thêm column "Rating" hiển thị từ RatingCache
    - Filter "rating ≥ 4 sao" trong search
    - Trang detail creator: hiển thị danh sách reviews + average rating
13. **Brand UI submit review**: form 5 sao + text optional (sau khi campaign kết thúc)

### Phase 5: Test + rollout (~2-3 ngày)

14. **Unit test** review service (validation, permission, aggregation)
15. **Integration test**: tạo profile → submit reviews → verify cache updated
16. **Smoke test** với 1 brand thật

**Total effort**: ~2 tuần mỗi sản phẩm.

## Risks + mitigations

1. **TCB code có comment "mock" chưa wire** → port có thể inherit bug
   - **Mitigation**: verify TCB review system production trước khi port. Nếu chưa wire → fix tại TCB trước, sau đó port stable version sang vCr/Amb
2. **`ProfileID` reference InfluencerProfile** → cần gap #2 phase tương ứng hoàn thành trước
   - **Mitigation**: chỉ start gap #16 sau khi gap #2 phase đó deploy production OK
3. **Visibility private/public** có thể khác business model vCr/Amb
   - **Mitigation**: discuss với product. Default `public` nếu vCr/Amb không có concept private
4. **Permission check brand** (TCB dùng `BrandID` riêng, vCr/Amb có thể dùng `Partner`)
   - **Mitigation**: adapt theo target — Ambassador dùng `Partner`, vCreator dùng `Workplace`

## Effort estimate

| Phase | Effort |
|---|---|
| 1: Schema | 1-2 ngày |
| 2: Service review | 3-5 ngày |
| 3: Service rating aggregation | 2-3 ngày |
| 4: Admin handler + brand portal | 3-5 ngày |
| 5: Test + rollout | 2-3 ngày |
| **Tổng mỗi sản phẩm** | **~2 tuần** |

→ Có thể làm song song 2 sản phẩm sau khi gap #2 từng phase tương ứng đã hoàn thành.

## Files referenced

**TCB (source of truth)**:
- `internal/model/mg/profile_review.go` — ProfileReview struct
- `internal/model/mg/rating_cache.go` — RatingCache struct
- `internal/service/review.go` (~627 LOC) — Review CRUD service
- `internal/service/rating_aggregation.go` — RatingCache recalculate
- `pkg/admin/handler/review.go` — admin review handler
- `pkg/admin/router/review.go` — router
- `pkg/admin/router/routevalidation/review.go` — validation

**vCr/Amb (target — chưa có)**:
- KHÔNG có collection `profile_review`
- KHÔNG có collection `rating_cache`
- KHÔNG có service review/rating
- KHÔNG có admin handler

## Liên quan đến gap khác

- **Gap #2 (InfluencerProfile)** — DEPENDENCY BẮT BUỘC. Gap #16 không làm trước được vì cần `profile_id` reference
- **Gap #15 (Reconciliation)** — không tied trực tiếp, có thể làm song song nếu có resource

## Lịch sử phân loại

- **Initial gap-analysis**: P1 (Total 13) — "TCB Profile Review + Rating, vCr/Amb không có concept rating creator → brand không có signal trust"
- **2026-05-07 user clarify**: *"Cái này cũng clear, là phần tiếp nối của #02, có thể ở p1, sau #15, trước #31"*
- **Position**: P1 thứ 2 (sau gap #15 top, trước gap #31)
- **Score**: 13 (giữ nguyên — BV=4, Risk=3, Effort=2, XProd=4)

### Bài học methodology

- Gap có dependency tight với gap khác → cần ghi rõ trong header (`Dependency: gap #2 phase X`)
- Khi business intent rõ ràng (user "đã eval kỹ"), trust user decision không hỏi thêm options
- Code TCB có comment "Phase 02 mock" — nhắc dev verify production status trước khi port (tránh bug inherit)
