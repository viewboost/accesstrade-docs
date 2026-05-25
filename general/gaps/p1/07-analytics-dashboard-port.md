# Gap #07 — TCB Next.js Analytics Dashboard (executive view) — TCB-only, vCr/Amb chỉ có dashboard cũ trong admin

> **Priority**: 🟠 **P1** (reclassified P2→P1 2026-05-10 — user confirm strategic value sau khi clarify scope)
> **Source**: Initial gap-analysis #7
> **Direction port**: TCB → vCr/Amb (strategic, cần stakeholder confirm)
> **Last verified**: 2026-05-10

**Lưu ý phân biệt 2 dashboard**:
- **Dashboard cũ** (admin Umi `pages/dashboard`) — cả 3 sản phẩm đều có. **vCreator có filter 3 tầng workplace** (Brand → Company → Unit) là bản cải tiến hơn TCB/Ambassador (chỉ filter 1 tầng Partner).
- **Dashboard mới Next.js** (`dashboard/` standalone app) — **TCB-only**, executive view ~10 sections. Đây là gap chính của ticket này.

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

TCB có **dashboard executive Next.js** (app standalone riêng) cho ops/management theo dõi toàn bộ hệ thống: campaign performance, content analytics, top creator, top brand, export báo cáo, ... — đây là feature lớn được build riêng cho khách hàng TCB enterprise.

vCreator và Ambassador chỉ có **dashboard cũ trong admin Umi** (1 page với pie chart) — đủ xem tổng quan cơ bản nhưng không có executive view đa-section.

> **Note**: Dashboard cũ ở admin Umi thì vCreator có filter 3 tầng workplace (Brand → Company → Unit) — cải tiến hơn TCB/Amb (chỉ 1 tầng Partner). Tuy nhiên đây không phải scope gap này. Gap này nói về Dashboard Next.js executive — TCB-only.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Dashboard executive Next.js standalone?** | ✅ `dashboard/` app | ❌ | ❌ |
| Dashboard cũ trong admin Umi | ✅ (basic) | ✅ (basic, **+ filter 3 tầng workplace**) | ✅ (basic, copy vCr nhưng 1 tầng) |
| Số tab/section dashboard executive | ~10 (analytics, campaigns, contents, performance, profiles, exports, ...) | — | — |
| Backend dashboard service (executive) | `dashboard_analytics.go` (1731 LOC) + `global_dashboard.go` (309) + `export_dashboard.go` (815) ≈ 2855 LOC | ❌ | ❌ |
| Aggregate pipelines chuyên biệt | ✅ `event_analytic_dashboard.go`, `global_dashboard.go` | ❌ | ❌ |
| Export báo cáo Excel/CSV (async job) | ✅ | ❌ | ❌ |
| Filter đa chiều (brand × campaign × time × creator) | ✅ | ❌ (chỉ basic ở dashboard cũ) | ❌ |

## Hệ quả

- vCr/Amb: ops/management muốn xem tổng quan đa chiều → phải query DB tay hoặc xuất Excel manual
- Khách hàng enterprise (như TCB) đòi dashboard executive → vCr/Amb không sẵn sàng
- Không có audit trail "ai xem báo cáo gì khi nào" như TCB

## Giải pháp (cần stakeholder confirm)

Đây là **strategic decision**, không phải easy port:
- Frontend: TCB dashboard là Next.js app standalone, không thể nhét vào admin Umi của vCr/Amb được — cần build riêng
- Backend: ~2855 LOC service + aggregate pipelines TCB-specific (filter theo brand/campaign concept của TCB, có thể không match concept của vCr workplace)

**Effort dự kiến**: 4-6 tuần mỗi sản phẩm (port backend services + build frontend app riêng).

**Cần product confirm trước khi làm**:
1. vCr/Amb có khách hàng enterprise đòi executive dashboard chưa?
2. Concept filter (brand/campaign) của TCB có map sang workplace của vCr / partner của Amb được không?
3. Có dùng chung dashboard infrastructure 3 sản phẩm hay mỗi product làm riêng?

→ **P2 vì**: không phải bug, không có incident — đây là feature gap dài hạn cần product roadmap quyết định trước.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB dashboard = Next.js app `dashboard/` (frontend chuyên biệt) + 3 backend services (~2855 LOC) + 2 aggregate pipelines MongoDB. vCr/Amb chỉ có 1 page admin với pie chart, dùng `content_analytic_daily` + `event_analytic_daily` cron daily.

## Verify code

### TCB (source of truth)

**Frontend** — `accesstrade-projects/techcombank/dashboard/`:
- Next.js 15+ standalone app (separate package từ admin)
- Sections: `analytics/`, `campaigns/`, `contents/`, `exports/`, `influencers/`, `performance/`, `profiles/`, `settings/`
- Components: `charts/`, `tables/`, `tabs/`, `filters/`, `wiki/`
- i18n: vi/en

**Backend**:
- `internal/service/dashboard_analytics.go` — **1731 LOC** — main analytics service
- `internal/service/global_dashboard.go` — **309 LOC** — global metrics
- `pkg/admin/service/export_dashboard.go` — **815 LOC** — export báo cáo (async job + polling)
- `internal/module/asynq/dashboard.go` — async job cho export
- `internal/module/database/mongodb/aggregate_pipeline/event_analytic_dashboard.go`
- `internal/module/database/mongodb/aggregate_pipeline/global_dashboard.go`

### vCreator status

**Frontend** — `accesstrade-projects/vcreator/admin/src/pages/dashboard/`:
- 1 file `index.tsx` (Umi/Antd)
- Components: chỉ 1 file `filter.tsx`
- Render: pie chart + RcStatisticBox

**Backend**:
- KHÔNG có `dashboard_analytics.go` / `global_dashboard.go` / `export_dashboard.go`
- Có `internal/service/content_analytic_daily.go` (cron tổng hợp daily)
- Có model `event_analytic_daily.go` + `content_analytic_daily.go` + `user_event_analytic_daily.go`
- Public service `user_statistic.go` (creator self-stats, không phải executive view)

### Ambassador status

Cấu trúc giống hệt vCreator (copy-paste pattern):
- `admin/src/pages/dashboard/index.tsx` — code identical với vCr
- Backend: tương tự vCr, không có dashboard service riêng

## Đề xuất implementation (nếu approved)

### Phase 1: Product alignment (1-2 tuần)
- Confirm khách hàng enterprise có đòi không
- Map concept brand/campaign TCB → workplace vCr / partner Amb
- Decide: standalone dashboard app vs nhét vào admin existing

### Phase 2: Backend port (3-4 tuần)
- Port `dashboard_analytics.go` adapt với schema target
- Port `export_dashboard.go` + asynq job
- Port aggregate pipelines

### Phase 3: Frontend (2-3 tuần)
- Nếu standalone: setup Next.js app + i18n + components
- Nếu admin existing: build trong Umi (effort thấp hơn nhưng UX kém hơn)

**Total**: ~4-6 tuần mỗi sản phẩm.

## Risks + mitigations

1. **Concept mismatch**: TCB filter theo brand × campaign × content category. vCr workplace 3-tier, Amb partner đơn cấp.
   - **Mitigation**: thiết kế lại filter layer, không port 1:1.
2. **Aggregate pipeline performance**: TCB pipelines query lượng data lớn → đã optimize cho TCB schema. Port sang vCr/Amb cần re-test performance.
   - **Mitigation**: load test với data prod trước rollout.
3. **Frontend tech stack**: TCB dashboard là Next.js, vCr/Amb admin là Umi — 2 stack khác nhau.
   - **Mitigation**: chấp nhận 2 codebase frontend, hoặc rewrite về Umi (effort thêm).

## Files referenced

**TCB (source of truth)**:
- `dashboard/src/app/[locale]/` (10+ sections)
- `backend/internal/service/dashboard_analytics.go` (1731 LOC)
- `backend/internal/service/global_dashboard.go` (309 LOC)
- `backend/pkg/admin/service/export_dashboard.go` (815 LOC)
- `backend/internal/module/asynq/dashboard.go`
- `backend/internal/module/database/mongodb/aggregate_pipeline/event_analytic_dashboard.go`
- `backend/internal/module/database/mongodb/aggregate_pipeline/global_dashboard.go`

**vCreator/Ambassador (target)**:
- `admin/src/pages/dashboard/index.tsx` (1 page basic)
- KHÔNG có dashboard service riêng

## Lịch sử phân loại

- **Initial**: P2 (Total 10) — frontend + backend đều phức tạp, cần stakeholder confirm
- **2026-05-10 (P2→P1)**: User confirm sau khi clarify scope (phân biệt dashboard cũ admin Umi vs Dashboard Next.js executive). Dashboard Next.js là feature chiến lược, không phải nice-to-have. Note thêm: dashboard cũ vCreator có filter 3 tầng workplace là bản cải tiến hơn TCB/Amb — nhưng không thuộc scope gap này.
