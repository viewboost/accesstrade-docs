# Gap #20 — Affiliate suite (campaign + contract + links + tracking) — Ambassador có, vCreator đang làm, TCB cần chốt sale

> **Priority**: 🟠 **P1** (reclassified P2→P1 2026-05-10 — vCreator đang implement, TCB chờ chốt sale)
> **Source**: Initial gap-analysis #20
> **Direction port**: Ambassador → vCreator (đang làm) → TCB (sau chốt sale)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

**Affiliate suite** = bộ công cụ cho creator/influencer kiếm tiền qua link affiliate (track click → conversion → commission). Bao gồm:
- **Affiliate Campaign**: brand tạo campaign (vd: "Bán laptop mùa tựu trường, hoa hồng 5%")
- **Affiliate Contract**: hợp đồng giữa creator và campaign (định nghĩa % commission)
- **Affiliate Link**: link cá nhân hóa creator để track traffic
- **Tracking**: log click + conversion từ external pub2 system (Scalef API ở vCr, internal pub2 ở Amb)
- **Settlement/Reporting**: báo cáo doanh thu + thanh toán định kỳ

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Affiliate suite có?** | ❌ Chưa có | 🟡 **Đang làm** (Scalef integration) | ✅ Có (~1275 LOC backend) |
| Models | — | ✅ 5 models (campaign, link, contract, event_campaign, support_ticket) | ✅ ~5 models (campaign, link, contract, mapping, pub2_log) |
| Backend service (internal + admin + public) | — | ~951 LOC (đang phát triển) | ~1275 LOC (mature) |
| Tích hợp external | — | **Scalef API** (mới) | **pub2 internal API** (legacy) |
| Frontend admin | — | ✅ `services/affiliate-campaign.ts` | ✅ `services/affiliate-campaign.ts` |
| Tracking/conversion ready? | — | 🟡 Đang làm (recent commits: reporting + conversion tracking) | ✅ Production-ready |

## Hệ quả

- **vCreator**: đang đầu tư build affiliate (commits gần đây: paginated campaign listing, mandatory enrollment check, conversion tracking) → cần đảm bảo pattern thống nhất với Amb để dễ học/maintain
- **TCB**: chưa có → khi sales chốt được khách hàng B2B muốn affiliate (vd Techcombank đẩy thẻ tín dụng qua creator) thì port là pre-requisite. Effort lớn → cần dự phòng trước trong roadmap
- **Cross-product**: 3 sản phẩm dùng 2 external system khác nhau (Scalef vs pub2) → khó share infrastructure

## Giải pháp

**Hiện tại**: vCreator đang tự implement affiliate dựa trên Scalef API, KHÔNG copy 1:1 từ Ambassador (vì pub2 là Ambassador-internal). Tham khảo pattern Ambassador về:
- 5 models structure (campaign / contract / link / mapping / pub2_log)
- 3-layer service (internal + admin + public)
- API logging cho external integration (pub2_log ở Amb → Scalef_log ở vCr)
- Approve flow: creator enroll campaign → admin approve → tạo link

**Tương lai khi TCB chốt sale**:
- Quyết định dùng external system nào (Scalef như vCr, hay accesstrade pub system, hay tự build)
- Effort dự kiến: ~6-8 tuần (port 5 models + 3-layer service + frontend admin + integrate external API)

**Cần product/sales confirm**:
1. TCB roadmap có affiliate trong Q3/Q4 2026 không?
2. Nếu có, dùng external partner nào (Scalef, accesstrade, ...)?
3. vCreator nên synchronize pattern với Ambassador để dễ maintain hay cứ phát triển tự do theo Scalef?

→ **P1 vì**: vCr đang invest nhiều effort vào feature này (~1 quý active development), TCB chốt sale là blocker cho roadmap → cần track tiến độ + đảm bảo design consistent.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Ambassador có affiliate suite mature (~1275 LOC backend, 5 models, pub2 integration). vCreator đang phát triển song song dùng Scalef API (~951 LOC, scope tương tự nhưng external khác). TCB chưa có gì.

## Verify code

### Ambassador (mature, source of pattern)

**Models** — `internal/model/mg/affiliate.go` (128 LOC):
- `AffiliateCampaignRaw` — campaign mapping với pub2
- `AffiliateContractRaw` — hợp đồng creator × campaign
- `AffiliateLinkRaw` — link cá nhân hóa
- `CampaignAffiliateMappingRaw` — mapping campaign event ↔ affiliate
- `Pub2ApiLogRaw` — log mọi request/response Pub2 API

**Services**:
- `internal/service/affiliate.go` (399 LOC) — core logic
- `pkg/public/service/affiliate.go` (475 LOC) — creator-facing
- `pkg/admin/service/affiliate.go` (273 LOC) — admin
- `internal/module/pub2/` — client + models cho external pub2

### vCreator (đang phát triển)

**Models** — 5 files trong `internal/model/mg/`:
- `affiliate.go` — base
- `affiliate_event_campaign.go`
- `affiliate_link.go`
- `affiliate_contract.go`
- `affiliate_support_ticket.go` (Amb không có)

**Services**:
- `internal/service/affiliate.go` (149 LOC)
- `pkg/admin/service/affiliate.go` (282 LOC)
- `pkg/public/service/affiliate.go` (520 LOC)

**External integration**: Scalef API (KHÔNG dùng pub2 như Amb).

**Recent commits chứng minh đang active**:
- `f1d1ac09` proxy endpoint list affiliate payment invoices từ Scalef
- `8e5993a5` integrate Scalef core user ID + paginated campaign listing
- `6a6db6fc` pagination campaign listing by user
- `fe8b8522` mandatory campaign enrollment check trước khi generate link
- `60def478` affiliate reporting + conversion tracking với Scalef API

### TCB

```bash
find techcombank/backend -name "*affiliate*" → ❌ KHÔNG có (chỉ có 2 file HTML legacy ở dashboard public/)
```

## Đề xuất implementation (TCB, sau khi chốt sale)

### Phase 0: Sales + product alignment (1-2 tuần)
- Confirm TCB có khách hàng B2B đòi affiliate
- Quyết định external partner: Scalef (consistent vCr) hay khác

### Phase 1: Models + DAO (1 tuần)
- Port 5 models từ Amb hoặc vCr (tùy partner external)
- Setup MongoDB collections + indexes

### Phase 2: Services 3-layer (3-4 tuần)
- Internal service (core logic)
- Admin service (CRUD campaign + contract + approve)
- Public service (creator enroll + generate link + report)

### Phase 3: External integration (2-3 tuần)
- Pub2/Scalef client với API logging
- Webhook handler cho conversion tracking
- Reconciliation với reward engine

### Phase 4: Frontend admin (1-2 tuần)
- Campaign management page
- Contract approval flow
- Settlement report view

**Total**: ~6-8 tuần TCB.

## Risks + mitigations

1. **Inconsistent pattern**: vCr (Scalef) vs Amb (pub2) sẽ phân kỳ về lâu dài
   - **Mitigation**: vCr nên cố gắng giữ tên model/service giống Amb để khi TCB port có lựa chọn rõ ràng
2. **Sales chưa chốt → TCB block**: roadmap TCB không thể plan cứng
   - **Mitigation**: track #20 ở P1 để khi sales close deal có sẵn detail design
3. **Reconciliation complexity**: affiliate conversion + main campaign reward → có thể double-pay creator
   - **Mitigation**: thiết kế flag `RewardSource` (campaign vs affiliate) trong reward engine

## Files referenced

**Ambassador (source of pattern)**:
- `internal/model/mg/affiliate.go` (128 LOC)
- `internal/service/affiliate.go` (399 LOC)
- `pkg/public/service/affiliate.go` (475 LOC)
- `pkg/admin/service/affiliate.go` (273 LOC)
- `internal/module/pub2/` (client)

**vCreator (đang phát triển)**:
- `internal/model/mg/affiliate*.go` (5 files)
- `internal/service/affiliate.go` (149 LOC)
- `pkg/admin/service/affiliate.go` (282 LOC)
- `pkg/public/service/affiliate.go` (520 LOC)
- Frontend: `admin/src/services/affiliate-campaign.ts`

**TCB (chưa có)**:
- KHÔNG có file `*affiliate*` ở backend
- Chỉ có 2 file HTML legacy: `dashboard/public/affiliate-{center,dashboard}.html`

## Lịch sử phân loại

- **Initial**: P2 (Total 8) — đánh giá nhầm là "Ambassador-only, KHÔNG port được"
- **Reclassified P2→P1 (2026-05-10)**: User confirm:
  - vCreator **đang làm** (verified bằng git log: 5+ commits gần đây, ~951 LOC active development)
  - TCB **chờ chốt sale** mới làm
  - → P1 vì có active development + sales-driven blocker
