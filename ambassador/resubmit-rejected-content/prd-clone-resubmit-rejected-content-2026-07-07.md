# PRD: Clone tính năng "Resubmit link đã bị reject" từ Gen-Green sang Ambassador

## 1. Bối cảnh & Vấn đề (giống Gen-Green)

Ambassador hiện chặn **toàn cục** việc submit một link đã tồn tại trong DB. Check tại [content.go:335-340](../../../ambassabor/backend/pkg/public/service/content.go#L335-L340) chỉ query theo `contentId`, **không** phân biệt:
- Trạng thái (`waiting_approved` / `approved` / `rejected`)
- Event / partner nào

```go
// Hiện tại — pkg/public/service/content.go:335-340
_ = daomongodb.ContentDAO().GetShare().FindOne(ctx, checkExists, bson.M{
    "contentId": contentInfo.ID,
})
if !checkExists.ID.IsZero() {
    return errors.New(locale.ContentKeyLinkUsed)
}
```

**Hệ quả nghiệp vụ**: Creator submit nhầm link vào event A, bị admin reject → **không thể** submit lại link đó vào event B (dù event B hoàn toàn phù hợp). Creator mất cơ hội nhận thưởng cho content hợp lệ.

## 2. Mục tiêu

Cho phép creator submit lại một link ở event khác **nếu**:
1. Partner sở hữu event đó có **bật** feature flag `allowResubmitRejectedContent`, VÀ
2. Tất cả bản ghi trước đó của link này (trong cùng partner) đều đã bị `rejected`.

Partner không bật flag → giữ nguyên behavior cũ (chặn toàn cục theo partner).

## 3. Non-goals

- Không đổi logic khi link còn `waiting_approved` / `approved` ở bất kỳ event nào → vẫn chặn.
- Không đổi flow duyệt/reject của admin (chỉ **thêm guard** un-reject).
- Không xây UI cảnh báo lịch sử submit của link (phase sau).
- Không bật flag mặc định cho partner nào — **opt-in** từng partner.
- Không đổi flow crawl metadata / check hashtag.

## 4. User Story

**Là** một creator trên Ambassador, **tôi muốn** submit một link vào event B ngay cả khi link đó đã từng bị admin reject ở event A, **để** tôi không mất cơ hội nhận thưởng cho content hợp lệ của mình.

## 5. Yêu cầu chức năng (Functional Requirements)

### FR-1: Partner-level feature flag
Thêm cấu hình **per-partner** `allowResubmitRejectedContent` (boolean, default `false`):
- Quản lý ở level `Partner` (mỗi partner 1 giá trị riêng) — thêm vào [PartnerRaw](../../../ambassabor/backend/internal/model/mg/partner.go#L15).
- Chỉnh sửa được qua admin UI (form edit partner có sẵn — [pkg/admin/service/partner.go:258](../../../ambassabor/backend/pkg/admin/service/partner.go#L258) `Update`).
- Mặc định `false` → giữ behavior hiện tại.

### FR-2: Relax duplicate check (conditional by partner)
Khi creator submit content với `contentId = X` vào `event = E` (thuộc `partner = P`):

**Nếu `P.allowResubmitRejectedContent = false`** (default):

| Trường hợp bản ghi hiện có của `contentId = X` (cùng partner P) | Kết quả |
|---|---|
| Có bất kỳ bản ghi nào (mọi status) | **REJECT** (behavior hiện tại) |
| Không có bản ghi nào | **ALLOW** |

**Nếu `P.allowResubmitRejectedContent = true`**:

| Trường hợp bản ghi hiện có của `contentId = X` (cùng partner P) | Kết quả |
|---|---|
| Tồn tại ≥ 1 bản ghi có `status ∈ {waiting_approved, approved}` | **REJECT** |
| Tất cả bản ghi đều `status = rejected` VÀ thuộc event khác E | **ALLOW** (behavior mới) |
| Có bản ghi `status = rejected` thuộc **cùng** event E | **REJECT** (chống spam submit-reject cùng event) |
| Không có bản ghi nào | **ALLOW** |

**Scope mặc định**: query duplicate check scope trong cùng `partner` (mỗi partner là 1 tenant độc lập). `event.Partner` đã có sẵn khi submit ([content.go:136](../../../ambassabor/backend/pkg/public/service/content.go#L136)).

### FR-3: Guard ở admin un-reject flow
Trong [ChangeStatus](../../../ambassabor/backend/pkg/admin/service/content.go#L190): khi admin chuyển 1 content từ `rejected` → `approved` / `waiting_approved`, nếu đã tồn tại bản ghi **active** khác cùng `contentId` (cùng partner, đã được creator resubmit thành công ở event khác) → **phải chặn**. Guard này **áp dụng bất kể partner flag** (rủi ro double-count vẫn có khi admin thao tác thủ công).

### FR-4: Error message
Giữ nguyên `locale.ContentKeyLinkUsed` ([internal/locale/event.go:97](../../../ambassabor/backend/internal/locale/event.go#L97)) cho các case vẫn bị reject. Thêm key mới `ContentKeyActiveDuplicateExists` cho guard un-reject.

## 6. Yêu cầu phi chức năng (Non-Functional)

- **NFR-1 Performance**: Query duplicate phải dùng index. Content collection đã có `contentId` index đơn ([index.go:92](../../../ambassabor/backend/internal/module/database/mongodb/index.go#L92)) và `(event, status)`; cần thêm compound `(partner, contentId)`.
- **NFR-2 Concurrency safety**: Không có unique index trên `contentId`. Hai request song song cùng `contentId` có thể cùng pass check. **Recommendation**: thêm **partial unique index** `{partner, contentId}` where `status ≠ rejected`. Cần bổ sung helper (xem §8).
- **NFR-3 Backward compatibility**: Bản ghi rejected cũ không cần migrate. Logic mới hoạt động trên dữ liệu hiện tại.

## 7. Implementation Plan — Stories

| # | Story | Deliverable | Est |
|---|---|---|---|
| 1 | Thêm `PartnerOptions` struct + field `Options` vào `PartnerRaw` | Model change (nil = default false, không backfill) | 0.25d |
| 2 | Thêm helper `newPartialUniqueIndex` + index `(partner, contentId)` | Index module + verify dev DB | 0.5d |
| 3 | Conditional duplicate check ở creator submit | Load partner + sửa query theo flag ([content.go:335](../../../ambassabor/backend/pkg/public/service/content.go#L335)) + unit test 2 branch | 0.75d |
| 4 | Guard admin un-reject | Check active duplicate trong `ChangeStatus` + locale key `ContentKeyActiveDuplicateExists` + unit test | 0.5d |
| 5 | Admin API update partner options | Mở rộng `PartnerUpsertBody` + `Update`/`Create` + audit log | 0.5d |
| 6 | Admin UI toggle flag | Toggle trong form partner settings + confirm dialog + call API | 0.5d |
| 7 | Integration test end-to-end | flag off (behavior cũ); flag on các case allow/block; guard un-reject | 0.5d |
| 8 | (Optional) Audit log khi creator resubmit rejected link | Ghi audit entry khi detect resubmit | 0.5d |

**Order**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8. **Total**: ~3.5-4 ngày công (không tính story 8).

## 8. Acceptance Criteria

**Partner flag management**
- [ ] Admin bật/tắt được `allowResubmitRejectedContent` qua UI partner settings
- [ ] Flag mặc định `false` cho tất cả partner
- [ ] Audit log mỗi lần toggle; confirm dialog khi bật (warning gian lận)

**Partner flag OFF (behavior cũ)**
- [ ] Submit link đã `rejected` ở event khác (cùng partner) → **fail** `ContentKeyLinkUsed`
- [ ] Submit link đang `approved` → **fail** `ContentKeyLinkUsed`

**Partner flag ON**
- [ ] Submit link vào event B, link đã `rejected` ở event A (cùng partner) → **success**
- [ ] Submit link vào event B, link đang `waiting_approved`/`approved` ở event A → **fail** `ContentKeyLinkUsed`
- [ ] Submit lại vào **cùng** event A sau khi bị reject → **fail** (chống spam)

**Admin un-reject guard (bất kể flag)**
- [ ] Un-reject content ở event A khi content đã active ở event B → **fail** `ContentKeyActiveDuplicateExists`
- [ ] Un-reject content ở event A, không có active dup → **success**

**Concurrency & data integrity**
- [ ] 2 request song song cùng `(partner, contentId)`, cùng event → chỉ 1 insert thành công (partial unique index)
- [ ] Partial unique index `(partner, contentId)` where `status ≠ rejected` tồn tại sau deploy
- [ ] Không có reward double-count trong reconciliation sau 1 tuần monitor

## 9. Open Questions

- **Q1**: Có cần audit log riêng khi creator resubmit link đã reject (Story 8 optional)?
- **Q2**: Có hiển thị cảnh báo cho creator trước khi submit link đã từng reject (UX transparency)? — mặc định out of scope.
