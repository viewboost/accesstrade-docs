# Brainstorming: Enhanced Affiliate Link Generation

**Date:** 2026-04-08
**Objective:** Thiết kế nâng cấp chức năng tạo affiliate link — cho phép user nhập custom original URL, thêm UTM params, tạo short link optional, và xem link history
**Context:** V1 chỉ tạo 1 link/user/campaign (idempotent) từ `pub2CampaignUrl`. Pub2 API đã hỗ trợ `original_url`, UTM params, `available_tracking_domains`. Reference UI từ AccessTrade Pub2 (ảnh stepper: Select Product → Get Link → Create Content → On Sale)

## Techniques Used
1. SCAMPER — Creative variations trên codebase hiện tại
2. Reverse Brainstorming — Tìm failure modes → derive solutions
3. Starbursting — Question all assumptions (Who/What/Where/When/Why/How)

---

## Ideas Generated

### Category 1: Link Generation Form (10 ideas)

1. **Original URL input** pre-fill `pub2CampaignUrl`, user override được — deep link sản phẩm cụ thể
2. **Domain selector** dropdown từ Pub2 `available_tracking_domains` (response đã có field này)
3. **UTM builder** accordion — collapse mặc định, 4 fields: source, medium, campaign, content
4. **Checkbox "Tạo link rút gọn"** — optional (Pub2 luôn trả short link, nhưng UI cho user chọn hiển thị)
5. **Link naming** — input "Đặt tên link" (e.g. "Shopee Tết", "FB post 5/3") cho dễ nhận diện
6. **URL validation** — frontend check format + backend check domain thuộc merchant campaign
7. **"Hướng dẫn lấy link sản phẩm"** — tooltip hướng dẫn copy URL từ Shopee/Lazada
8. **Pre-filled UTM suggestions** — utm_source auto-suggest: "facebook", "tiktok", "instagram", "blog"
9. **Quick generate** — nút "Tạo nhanh" (dùng default URL + no UTM) bên cạnh form đầy đủ
10. **Form validation UX** — realtime validate URL format, hiện preview domain, disable submit khi invalid

### Category 2: Link History (8 ideas)

11. **Link history table** dưới form — show: name, short link, ngày tạo, status badge (Working/Expired)
12. **Search by name** — search input filter links theo tên user đặt
13. **Copy button per link** — icon copy bên cạnh mỗi short link (giống ảnh)
14. **Link detail expand** — click ">" → xem full original URL, UTM params, long link
15. **Grid layout 2 cột** cho link cards (giống ảnh) — responsive 1 cột mobile
16. **Status badge** — derive từ campaign status: "Working" (active), "Expired" (campaign hết hạn)
17. **Sort by date** — mới nhất trước (default)
18. **Infinite scroll / pagination** cho link history dài

### Category 3: Data Model Changes (6 ideas)

19. **AffiliateLinkRaw mở rộng** — thêm: `name`, `originalUrl`, `utmSource`, `utmMedium`, `utmCampaign`, `utmContent`, `domain`
20. **Bỏ idempotent 1:1** — cho phép nhiều link/user/campaign (unique by `userId + campaignId + originalUrl + utmSource + utmMedium`)
21. **Hoặc: unique by auto-gen** — không enforce uniqueness, mỗi lần generate = new link (đơn giản hơn)
22. **Index MongoDB** — compound index `{userId: 1, affiliateCampaignId: 1, createdAt: -1}` cho query history
23. **Link status computed** — không lưu field status riêng, derive từ campaign status (JOIN query hoặc populate)
24. **UTM fields optional** — `omitempty` tất cả, chỉ lưu khi user nhập

### Category 4: Backend API Changes (5 ideas)

25. **GenerateLink request body** — thêm optional fields: `originalUrl`, `name`, UTM params
26. **Backward compatible** — nếu `originalUrl` empty → dùng `pub2CampaignUrl` (default behavior V1)
27. **URL validation middleware** — check URL format, length limit, block javascript: / data: schemes
28. **Rate limit** — max 20 links/user/campaign/day (prevent spam)
29. **Response enrichment** — trả thêm `availableTrackingDomains` cho frontend render domain selector

### Category 5: UX & Flow (5 ideas)

30. **Inline form trong campaign detail** — thay nút "Lấy link" bằng expandable form (không navigate away)
31. **Post-generate success state** — sau tạo link → show link + copy button + "Tạo thêm link" option
32. **Mobile-first form** — stacked layout, large touch targets, minimal fields visible
33. **Recent links widget** — show 3 link gần nhất ngay khi mở campaign (không cần scroll xuống history)
34. **Empty state** — khi chưa có link: illustration + "Tạo link affiliate đầu tiên của bạn"

---

## Key Insights

### Insight 1: Bỏ idempotent 1:1, cho phép multi-link per campaign
**Source:** SCAMPER (Modify) + Starbursting (How)
**Impact:** High | **Effort:** Medium
**Why it matters:** Core change — hiện tại `GenerateLink` check existing và return cũ. Cần bỏ check này, mỗi lần gọi Pub2 = new link. Uniqueness không cần enforce vì mỗi link có khác original URL / UTM.
**Implementation:** Bỏ `FindOne(userId+campaignId)` check trong `internal/service/affiliate.go:182-189`. Mỗi lần gọi = insert new link.

### Insight 2: Original URL input với default + validation
**Source:** SCAMPER (Substitute) + Reverse Brainstorming (failure: invalid URL)
**Impact:** High | **Effort:** Low
**Why it matters:** Deep link sản phẩm cụ thể convert tốt hơn 3-5x so với homepage. Pub2 API đã hỗ trợ `original_url`. Chỉ cần frontend input + backend pass-through.
**Implementation:** Frontend form input pre-fill `pub2CampaignUrl`. Backend `GenerateLinkRequest.OriginalURL` nhận từ user request thay vì hardcode. Validate URL format + scheme (http/https only).

### ~~Insight 3: UTM builder~~ — DEFERRED
**Source:** SCAMPER (Eliminate) + Reverse Brainstorming (failure: UTM quá phức tạp)
**Impact:** N/A | **Effort:** N/A
**Status:** DEFERRED — Pub2 API doc ghi rõ UTM fields "Tạm thời không quan tâm" (api-reference.md:181). Truyền UTM vào bị ignore, response không reflect. **Không đưa vào UI cho đến khi Pub2 confirm hỗ trợ.**

### Insight 4: Link naming + history search
**Source:** SCAMPER (Combine) + Reverse Brainstorming (failure: link history không usable)
**Impact:** High | **Effort:** Low
**Why it matters:** Khi user tạo 10+ links, không có tên → không phân biệt được. Name + search = usable management. Giống ảnh reference "Tap to name".
**Implementation:** Thêm `name` field vào `AffiliateLinkRaw` + request body. Optional, default = campaign title + timestamp. Search by name dùng `$regex` trên MongoDB.

### Insight 5: Link history inline, không tách page riêng
**Source:** Starbursting (Where) + reference ảnh
**Impact:** Medium | **Effort:** Medium
**Why it matters:** User flow tự nhiên: tạo link → xem link vừa tạo + link cũ → copy. Không cần navigate đi chỗ khác. V2 trang FR-006 (link management) vẫn cần — nhưng campaign detail page cũng phải có inline history.
**Implementation:** Section "Lịch sử tạo link" dưới form generate. Grid 2 cột cards. Filter theo campaign hiện tại.

### Insight 6: Domain selector từ Pub2 response
**Source:** SCAMPER (Adapt) + Starbursting (What)
**Impact:** Low | **Effort:** Low
**Why it matters:** Pub2 `GenerateLinkResponse.Data.AvailableTrackingDomains` đã trả list domains. Giống ảnh reference "Domain" dropdown. Cho user chọn domain ưa thích cho short link.
**Implementation:** Cần research: Pub2 generate link API có nhận `domain` param không? Nếu có → frontend dropdown. Nếu không → chỉ hiển thị informational.

---

## Statistics
- Total ideas: 34
- Categories: 5
- Key insights: 6
- Techniques applied: 3

---

## Thiết Kế Đề Xuất

### UI Layout (Campaign Detail Page — sau APPROVED)

```
┌─────────────────────────────────────────────┐
│ Tạo link affiliate                          │
├─────────────────────────────────────────────┤
│                                             │
│ Original link  [https://shopee.vn/...    ]  │  ← pre-fill pub2CampaignUrl, editable
│ ⓘ Hướng dẫn lấy link sản phẩm              │
│                                             │
│ Đặt tên link   [Link Shopee Tết         ]  │  ← optional
│                                             │
│ ── UTM: DEFERRED (Pub2 chưa hỗ trợ) ──     │
│                                             │
│ ☐ Tạo link rút gọn                         │
│                                             │
│            [   Tạo link affiliate   ]       │  ← primary CTA
│                                             │
├─────────────────────────────────────────────┤
│ Lịch sử tạo link          🔍 Tìm theo tên  │
├─────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ Link Shopee Tết │ │ Link FB post    │    │
│ │ https://go.is.. │ │ https://go.is.. │    │
│ │ 📋 08/04/2026   │ │ 📋 05/04/2026   │    │
│ │ ● Working       │ │ ● Working       │    │
│ └─────────────────┘ └─────────────────┘    │
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ Link mặc định   │ │                 │    │
│ │ https://go.is.. │ │                 │    │
│ │ 📋 01/04/2026   │ │                 │    │
│ │ ● Working       │ │                 │    │
│ └─────────────────┘ └─────────────────┘    │
└─────────────────────────────────────────────┘
```

### Data Model Changes

```go
// AffiliateLinkRaw — ENHANCED
type AffiliateLinkRaw struct {
    ID                  AppID     `bson:"_id"`
    UserID              AppID     `bson:"userId"`
    AffiliateCampaignID AppID     `bson:"affiliateCampaignId"`
    SSOUserID           int       `bson:"ssoUserId"`
    Name                string    `bson:"name,omitempty"`          // NEW: user-defined name
    OriginalUrl         string    `bson:"originalUrl,omitempty"`   // NEW: custom URL (default = pub2CampaignUrl)
    AffiliateLink       string    `bson:"affiliateLink"`
    ShortAffiliateLink  string    `bson:"shortAffiliateLink"`
    Sub1                string    `bson:"sub1"`
    Sub4                string    `bson:"sub4"`
    UtmSource           string    `bson:"utmSource,omitempty"`     // NEW
    UtmMedium           string    `bson:"utmMedium,omitempty"`     // NEW
    UtmCampaign         string    `bson:"utmCampaign,omitempty"`   // NEW
    UtmContent          string    `bson:"utmContent,omitempty"`    // NEW
    CreatedAt           time.Time `bson:"createdAt"`
}
```

### API Changes

```
POST /api/public/affiliate-campaigns/:id/generate-link

Request Body (NEW — currently no body):
{
  "originalUrl": "https://shopee.vn/product/123",  // optional, default = pub2CampaignUrl
  "name": "Link Shopee Tết",                        // optional
  "utmSource": "facebook",                          // optional
  "utmMedium": "post",                              // optional
  "utmCampaign": "tet2026",                         // optional
  "utmContent": "banner_1",                          // optional
  "createShortLink": true                            // optional, default true
}

Response (enhanced):
{
  "_id": "...",
  "name": "Link Shopee Tết",
  "originalUrl": "https://shopee.vn/product/123",
  "affiliateLink": "https://...",
  "shortAffiliateLink": "https://go.isclix.com/...",
  "utmSource": "facebook",
  ...
  "createdAt": "2026-04-08T..."
}
```

### Backend Changes Summary

| File | Change |
|------|--------|
| `internal/model/mg/affiliate.go` | Thêm 5 fields vào `AffiliateLinkRaw` |
| `internal/service/affiliate.go` | Bỏ idempotent check, nhận params từ caller, pass UTM to Pub2 |
| `pkg/public/model/request/affiliate.go` | Thêm `GenerateLinkBody` struct |
| `pkg/public/handler/affiliate.go` | Parse request body, validate URL |
| `pkg/public/service/affiliate.go` | Pass new params to internal service |
| `pkg/public/model/response/affiliate.go` | Thêm new fields vào response |

---

## Recommended Next Steps

1. **Quyết định design approach** — Inline form (đề xuất) vs wizard stepper vs separate page
2. **Verify Pub2 domain param** — Pub2 generate link API có nhận domain param không? Test thử
3. **PRD V1.5** — Document enhanced link generation as PRD update (hoặc tách PRD mới)
4. **Implementation order:**
   - Phase A: Backend (model + API changes) ~1-2 ngày
   - Phase B: Frontend form + link history ~3-4 ngày
   - Phase C: Polish (UTM suggestions, domain selector, mobile) ~1-2 ngày

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Pub2 generate link API có nhận `domain` param không? | Engineering | Open |
| 2 | Rate limit: cho phép bao nhiêu link/user/campaign? | Product | Open |
| 3 | Short link luôn tạo hay optional checkbox? | Product | Open |
| 4 | Link history hiện ở campaign detail hay chỉ ở trang link management (V2)? | Product + Design | Open |
| 5 | URL validation: chỉ check format hay check domain thuộc merchant? | Engineering | Open |
| 6 | UTM: Pub2 doc ghi "Tạm thời không quan tâm" — khi nào hỗ trợ? | Pub2 team | **Answered: DEFERRED** |

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Brainstorming session: 2026-04-08*
*Input: Reference UI (AccessTrade Pub2 link builder) + current codebase analysis*
*34 ideas, 5 categories, 6 key insights*
