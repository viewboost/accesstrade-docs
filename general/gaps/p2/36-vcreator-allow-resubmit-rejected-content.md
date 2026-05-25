# Gap #36 — vCreator cho phép user submit lại link ở camp khác khi link đó bị từ chối ở camp cũ; TCB/Ambassador không có

> **Priority**: 🟡 **P2** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: vCreator → TCB + Ambassador (selective)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi creator submit 1 link content (vd: link bài TikTok) vào campaign A và **bị admin reject** (ví dụ vì hashtag sai, hoặc nội dung không phù hợp campaign A), creator có thể muốn **submit lại chính link đó vào campaign B khác** (vì nội dung phù hợp với campaign B).

→ Đây là **business case hợp lệ** vì cùng bài đăng có thể fit nhiều campaign khác nhau.

vCreator có feature này (toggle per-partner: `AllowResubmitRejectedContent`). Khi bật:
- Cho phép submit lại link đã reject vào campaign khác
- Vẫn block re-submit vào **chính campaign cũ** (chống spam, decision D1)
- Vẫn block nếu link đang waiting/approved ở campaign nào đó (tránh double tracking)

TCB và Ambassador **không có** concept này — link bị reject là block luôn cross-campaign.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Service `content_duplicate.go` | ❌ | ✅ 47 LOC | ❌ |
| Field `Partner.Options.AllowResubmitRejectedContent` | ❌ | ✅ | ❌ |
| Toggle per-partner | ❌ | ✅ | ❌ |
| Anti-spam: block resubmit cùng camp | ❌ (block cross-product luôn) | ✅ (chỉ block cùng event) | ❌ (block cross-product luôn) |
| Block waiting/approved ở camp khác | (mặc định block tất cả) | ✅ | (mặc định block tất cả) |

## Hệ quả

- **TCB/Ambassador**: creator submit nhầm camp A, bị reject → mất luôn cơ hội dùng link đó ở camp B → frustration, complaint support
- **Workaround hiện tại** (TCB/Amb): creator phải post lại bài mới để có URL mới → tốn effort + làm giảm chất lượng content
- **vCreator**: đã có pattern production-tested với anti-spam guards → port sang TCB/Amb không nhiều risk

## Liên quan các gap khác

- Independent từ các gap khác. Không depend on #2/#8 nào.
- Có thể làm chung wave với feature parity user-facing flow

## Giải pháp

### Phase 1: TCB (~3-5 ngày)
1. Thêm field `AllowResubmitRejectedContent bool` vào `PartnerOpts` struct + getter `GetAllowResubmitRejectedContent()`
2. Tạo file `pkg/public/service/content_duplicate.go` (~47 LOC) — copy từ vCreator:
   - `dupCheckErrorKey(allowResubmit)` — trả locale key phù hợp
   - `buildDuplicateCheckFilter(allowResubmit, partnerID, eventID, contentID)` — MongoDB filter
3. Wire vào content submit flow: gọi `buildDuplicateCheckFilter` thay vì check raw `contentId`
4. Admin frontend: thêm toggle trong partner config
5. Locale: thêm 2 message keys `ContentKeyActiveDuplicateExists` + `ContentKeyLinkUsed`
6. Test: 3 case — submit lại same camp (block), submit khác camp với feature off (block), submit khác camp với feature on (pass)

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1, adapt với schema Ambassador

**Total**: ~1-2 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P2

- **Có business value rõ**: giảm friction cho creator khi submit nhầm camp
- **Effort thấp**: ~50 LOC + frontend toggle, đã có pattern production
- **Không urgent**: không phải bug active, là enhancement
- **Toggle per-partner**: không break existing flow (default off)

→ Nice-to-have, làm khi có resource sprint trống.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

vCreator có 47 LOC trong `content_duplicate.go` + field `Partner.Options.AllowResubmitRejectedContent` cho phép resubmit cross-camp với anti-spam guards. TCB/Ambassador không có file này, không có flag — block tất cả duplicate cross-product.

## Verify code

### vCreator (source of truth)

**Field model** — `internal/model/mg/partner.go:16, 36-40`:
```go
type PartnerOpts struct {
    AllowResubmitRejectedContent bool `bson:"allowResubmitRejectedContent,omitempty" json:"allowResubmitRejectedContent"`
}

// nil-safe accessor
func (r *PartnerRaw) GetAllowResubmitRejectedContent() bool {
    if r == nil || r.Options == nil { return false }
    return r.Options.AllowResubmitRejectedContent
}
```

**Service** — `pkg/public/service/content_duplicate.go` (47 LOC):
```go
// Returns locale key for duplicate-detected error
func dupCheckErrorKey(allowResubmit bool) string {
    if allowResubmit {
        return locale.ContentKeyActiveDuplicateExists
    }
    return locale.ContentKeyLinkUsed
}

// MongoDB filter: detect blocking duplicate before insert
func buildDuplicateCheckFilter(allowResubmit bool, partnerID, eventID modelmg.AppID, contentID string) bson.M {
    if !allowResubmit {
        // Legacy: block ANY record with same contentId (cross-partner included)
        return bson.M{"contentId": contentID}
    }
    // New: scoped to partner, block if:
    // (A) active record exists in this partner (waiting_approved / approved), OR
    // (B) rejected record exists in SAME event (anti-spam — decision D1)
    // → Rejected records in OTHER events PASS THROUGH (new capability)
    return bson.M{
        "partner":   partnerID,
        "contentId": contentID,
        "$or": []bson.M{
            {"status": bson.M{"$in": []string{
                constants.StatusWaitingApproved,
                constants.StatusApproved,
            }}},
            {
                "status": constants.StatusRejected,
                "event":  eventID,
            },
        },
    }
}
```

**Test coverage** — `pkg/public/service/content_duplicate_test.go` + `internal/model/mg/partner_test.go` (TestPartnerRawGetAllowResubmitRejectedContent).

**Caller** — `pkg/admin/service/partner.go:260`:
```go
oldAllow := partner.GetAllowResubmitRejectedContent()
// Audit log khi admin toggle flag
```

### TCB status

```bash
ls techcombank/backend/pkg/public/service/content_duplicate.go → ❌ KHÔNG có
grep -rn "allowResubmit\|AllowResubmit" techcombank/backend → ❌ KHÔNG có
```

### Ambassador status

```bash
ls ambassabor/backend/pkg/public/service/content_duplicate.go → ❌ KHÔNG có
grep -rn "allowResubmit\|AllowResubmit" ambassabor/backend → ❌ KHÔNG có
```

## Đề xuất implementation

### Phase 1: TCB (~3-5 ngày)

1. **Model migration** (~30 phút):
   ```go
   // internal/model/mg/partner.go
   type PartnerOpts struct {
       // ... existing fields
       AllowResubmitRejectedContent bool `bson:"allowResubmitRejectedContent,omitempty"`
   }

   func (r *PartnerRaw) GetAllowResubmitRejectedContent() bool {
       if r == nil || r.Options == nil { return false }
       return r.Options.AllowResubmitRejectedContent
   }
   ```

2. **Service** (~2-3 giờ):
   - Tạo `pkg/public/service/content_duplicate.go` copy từ vCr
   - Adapt với constants/locale TCB

3. **Wire vào submit flow** (~1 ngày):
   - Locate content submit handler/service
   - Replace raw `contentId` check bằng `buildDuplicateCheckFilter`
   - Pass `allowResubmit = partner.GetAllowResubmitRejectedContent()`

4. **Admin frontend** (~1 ngày):
   - Toggle "Cho phép submit lại link đã reject ở camp khác" trong partner config page
   - i18n vi/en

5. **Locale** (~30 phút):
   - `ContentKeyActiveDuplicateExists` — message khi link đang active (waiting/approved)
   - `ContentKeyLinkUsed` — message legacy (block tất cả)

6. **Test E2E** (~1 ngày):
   - 3 cases: same camp resubmit, cross-camp với flag off, cross-camp với flag on
   - Test admin toggle audit log

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1

**Total**: ~1-2 tuần.

## Risks + mitigations

1. **Index uniqueness**: nếu DB có unique index trên `contentId` → break khi cho phép resubmit
   - **Mitigation**: vCreator hiện dùng pre-insert app check + post-insert unique-index backstop. Cần verify TCB/Amb có index như nào, có thể cần migration drop unique index hoặc đổi thành compound (contentId, partner, status filter).
2. **Anti-spam cùng camp**: phải đảm bảo creator không spam resubmit cùng camp sau reject
   - **Mitigation**: copy đúng pattern vCr (block nếu rejected + cùng event). Test rõ.
3. **Admin chưa đào tạo**: admin TCB không quen toggle này → có thể bật mặc định nhầm
   - **Mitigation**: default off, có audit log, document clear.
4. **Conflict với reconciliation**: nếu link được reward ở camp B sau khi reject ở camp A → reconciliation phải hiểu link xuất hiện 2 lần là hợp lệ
   - **Mitigation**: verify reconciliation engine có scope theo (partner, event) chứ không phải chỉ contentId.

## Files referenced

**vCreator (source of truth)**:
- `internal/model/mg/partner.go:16, 36-40` (field + getter)
- `internal/model/mg/partner_test.go` (test cases)
- `pkg/public/service/content_duplicate.go` (47 LOC)
- `pkg/public/service/content_duplicate_test.go` (test coverage)
- `pkg/admin/service/partner.go:260` (audit log toggle)
- `internal/locale/...` (2 message keys)

**TCB/Ambassador (target — chưa có)**:
- KHÔNG có `pkg/public/service/content_duplicate.go`
- KHÔNG có field `AllowResubmitRejectedContent` trong PartnerOpts
- KHÔNG có locale keys ContentKeyActiveDuplicateExists / ContentKeyLinkUsed

## Lịch sử phân loại

- **2026-05-10 (initial P2)**: User self-listed gap. Quote: "VCreator - Cho phép user submit lại link ở 1 camp khác khi link đó bị từ chối ở camp cũ" + "P2".
  - Lý do P2: business value rõ (giảm friction creator) + effort thấp (~50 LOC + frontend) + không urgent.
  - Toggle per-partner default off, không break existing flow.
