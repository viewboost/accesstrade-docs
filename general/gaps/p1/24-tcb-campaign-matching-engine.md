# Gap #24 — TCB Campaign matching engine + filtered_campaigns (đang dang dở, làm xong cần port ngay vCr/Amb)

> **Priority**: 🟠 **P1** (reclassified P3→P1 2026-05-10 — TCB chưa hoàn thiện tuyệt đối, vẫn dang dở. Làm xong cần port ngay 2 bên kia)
> **Source**: Initial gap-analysis #24
> **Direction port**: TCB (đang dang dở) → vCr/Amb (port ngay sau khi TCB ổn định)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

TCB đang phát triển **Campaign Matching Engine** — tự động chấm điểm + ghép influencer phù hợp với campaign theo nhiều chiều (category, budget tier, engagement rate). Brand admin upload danh sách candidate influencer → engine call AT-Core → trả về top match có score breakdown.

→ Đây là feature **AI-assisted creator selection** — thay vì manual review, brand có gợi ý xếp hạng dựa trên data.

**Tình trạng hiện tại**:
- TCB **đang phát triển** (verified bằng git log: nhiều commits gần đây — "implement full campaign CRUD and matching flow with AT-Core integration", "ratio-percentage normalization", "fix nested matching API response format")
- **Chưa hoàn thiện tuyệt đối**, còn dang dở
- vCreator và Ambassador **không có** feature này

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Campaign matching engine có?** | 🟡 **Đang phát triển** (~786 LOC + AT-Core integration) | ❌ | ❌ |
| Multi-dimension scoring (category × tier × engagement) | 🟡 Đang làm | ❌ | ❌ |
| Score breakdown per influencer | 🟡 Đang làm | ❌ | ❌ |
| Latency tracking + error handling per session | 🟡 Đang làm | ❌ | ❌ |
| Filtered campaigns (filter campaign by metrics) | ✅ ~344 LOC | ❌ | ❌ |
| Tích hợp AT-Core (external matching service) | 🟡 Đang làm | ❌ | ❌ |

## Hệ quả

- **TCB ngắn hạn**: feature đang dang dở → còn bug, edge case chưa cover (vd nested API response format vừa fix)
- **vCr/Amb**: brand vẫn manual review từng creator → tốn thời gian ops, không scale được khi có nhiều campaign
- **Cross-product**: TCB là pilot — nếu thành công sẽ là competitive advantage, cần port ngay sang vCr/Amb để 3 sản phẩm parity

## Giải pháp

**Phase 1 (TCB hoàn thiện)**: 
- Fix bug + cover edge cases
- Stable AT-Core integration
- Production-ready scoring

**Phase 2 (port vCr/Amb)**:
- Copy 786 LOC backend (model + service + admin + aggregate pipeline)
- Adapt với schema target (vCr workplace × Amb partner)
- Integrate với AT-Core (hoặc internal matching service nếu khác)

**Effort dự kiến**:
- TCB hoàn thiện: ~2-3 tuần (bug fixes + edge cases)
- vCr/Amb port mỗi sản phẩm: ~3-4 tuần

**Dependency**: AT-Core matching API phải stable. TCB hiện đang fix nested response format → còn risk API contract thay đổi.

→ **P1 vì**: feature có competitive value cao (AI-assisted creator selection), TCB đang invest active development. Khi TCB stabilize → port ngay là **strategic priority** để 3 sản phẩm parity.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có 786 LOC backend Campaign Matching engine (model 89 + admin service 353 + filtered_campaigns service 138 + aggregate pipeline 206) đang dang dở phát triển. Tích hợp AT-Core external matching API. vCr/Amb không có gì tương đương.

## Verify code

### TCB (đang phát triển)

**Model** — `internal/model/mg/campaign_matching.go` (89 LOC):
- `CampaignMatchingSessionRaw` — 1 session matching cho 1 campaign × N influencers
- `MatchingSessionRequest{Influencers, Criteria, Weights}`
- `MatchingSessionResult{Platform, ExternalID, Name, Handle, FollowersCount, EngagementRate, FinalScore, Suitable, Breakdown}`
- `MatchingScoreBreakdown{Category, Tier, Engagement}` — per-dimension scoring
- `MatchingDimensionScore{Raw, Weight, Contribution, Explanation}` — explainable scoring
- `MatchingSessionError` — track failure per influencer

**Services**:
- `pkg/admin/service/campaign_matching.go` (353 LOC) — admin trigger matching session
- `internal/service/filtered_campaigns.go` (138 LOC) — filter campaigns by metrics
- Handler + router + DAO + request/response models đầy đủ

**Aggregate pipeline**:
- `internal/module/database/mongodb/aggregate_pipeline/filtered_campaigns.go` (206 LOC) — MongoDB pipeline cho filter

**External integration**: AT-Core matching API (call qua atcore client).

**Recent commits chứng minh đang active dev**:
- `f404bf00` feat(campaign): implement full campaign CRUD and matching flow with AT-Core integration
- `38fd2a37` feat(campaigns): improve weight input UI and ratio-percentage normalization
- `114aefbf` fix(atcore): parse nested matching API response format
- `f9c800ef` fix(service): use totalViewsNotRejected for filtered campaigns
- `5169f48d` feat: add event code display across backend, dashboard, and admin

### vCreator status

```bash
find vcreator/backend -name "*matching*" → ❌ KHÔNG có
```

### Ambassador status

```bash
find ambassabor/backend -name "*matching*" → ❌ KHÔNG có
```

## Đề xuất implementation

### Phase 1: TCB hoàn thiện (~2-3 tuần)
- Bug fixes các edge case còn lại
- Stabilize AT-Core integration (API contract finalized)
- Add metrics + logging per session
- Production rollout với monitoring

### Phase 2: Port vCr (~3-4 tuần)
- Copy 5 model structs (CampaignMatchingSessionRaw + 4 sub-types)
- Port admin service ~353 LOC
- Adapt với vCr workplace schema (filter theo workplace thay vì partner)
- Integrate AT-Core qua at-core client

### Phase 3: Port Amb (~3-4 tuần)
- Tương tự Phase 2 nhưng với Amb partner schema

**Total**: TCB hoàn thiện 2-3 tuần + vCr/Amb mỗi cái 3-4 tuần.

## Risks + mitigations

1. **AT-Core API chưa stable**: TCB đang fix nested response format → port sớm vCr/Amb có thể bị break theo
   - **Mitigation**: chờ TCB stable rồi mới port. Track AT-Core API version.
2. **Schema mismatch**: TCB filter theo `Partner`, vCr theo `Workplace` 3-tier, Amb theo `Partner` đơn cấp
   - **Mitigation**: thiết kế abstraction layer trong service, không hard-code partner ID
3. **Scoring criteria khác business model**: TCB có category/tier/engagement; vCr có thể cần workplace×department; Amb có thể cần gaming-relevant metrics
   - **Mitigation**: weights configurable per-product, không hard-code dimensions

## Files referenced

**TCB (source of truth, đang dang dở)**:
- `internal/model/mg/campaign_matching.go` (89 LOC)
- `internal/service/filtered_campaigns.go` (138 LOC)
- `internal/module/database/mongodb/aggregate_pipeline/filtered_campaigns.go` (206 LOC)
- `internal/module/database/mongodb/dao/campaign_matching.go`
- `pkg/admin/handler/campaign_matching.go`
- `pkg/admin/service/campaign_matching.go` (353 LOC)
- `pkg/admin/router/campaign_matching.go`
- `pkg/admin/router/routevalidation/campaign_matching.go`
- `pkg/admin/model/{request,response}/campaign_matching.go`

**vCreator/Ambassador (target — chưa có)**:
- KHÔNG có file `*matching*` ở backend

## Lịch sử phân loại

- **Initial**: P3 (Total 7) — đánh giá nhầm "TCB flagship feature riêng (T-Fluencers), KHÔNG port"
- **Reclassified P3→P1 (2026-05-10)**: User confirm:
  - TCB đang phát triển (verified bằng git log: nhiều commits gần đây)
  - Chưa hoàn thiện tuyệt đối, vẫn dang dở
  - Làm xong là **cần port ngay** sang vCr/Amb (strategic priority)
  - → P1 vì có active development + cross-product impact lớn
