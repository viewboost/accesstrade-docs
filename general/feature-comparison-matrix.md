# Feature Comparison Matrix — TCB / vCreator / Ambassador

> **Generated**: 2026-05-07
> **Verified**: 2026-05-07 (re-built từ filesystem ground truth via Python script — xem [verification-report.md](./verification-report.md))
> **Mục đích**: xác định feature nào cần đồng bộ giữa 3 sản phẩm AccessTrade.

**Legend**: ✅ có | ❌ không có | 🆕 mới (chỉ TCB)

---

## Bird's-eye view

| Layer | TCB | vCreator | Ambassador |
|---|---:|---:|---:|
| Backend services | **29** | 15 | 16 |
| MongoDB models | ~85 | ~68 | ~66 |
| API route groups | ~32 | ~24 | ~30 |
| Admin pages | **29** | 23 | 26 |
| Frontend pages | 20 | 17 | **25** |
| Dashboard pages | **17 🆕** | — | — |

**Quan sát**:
- TCB phình ở **backend** (gần 2× services + models so với 2 sản phẩm còn lại)
- Ambassador phình ở **frontend** (creator-facing với affiliate flow đặc trưng)
- vCreator gọn nhất, "chuẩn" cho core platform

---

## 1. Backend Services Matrix (32 services tổng cộng — verified)

| Service | TCB | vCreator | Ambassador | Ghi chú |
|---|:---:|:---:|:---:|---|
| audit | ✅ | ✅ | ✅ | Core |
| cashflow | ✅ | ✅ | ✅ | Core (TCB mở rộng nhiều) |
| content | ✅ | ✅ | ✅ | Core |
| content_analytic_daily | ✅ | ✅ | ✅ | Core |
| content_flow | ✅ | ✅ | ✅ | Core |
| event | ✅ | ✅ | ✅ | Core |
| event_schema | ✅ | ✅ | ✅ | Core |
| notification | ✅ | ✅ | ✅ | Core |
| otp | ✅ | ✅ | ✅ | Core |
| user | ✅ | ✅ | ✅ | Core |
| user_social | ✅ | ✅ | ✅ | Core |
| video | ✅ | ✅ | ✅ | Core |
| withdraw | ✅ | ✅ | ✅ | Core |
| load_data | ✅ | ❌ | ✅ | TCB + Ambassador |
| user_social_partner | ✅ | ❌ | ✅ | TCB + Ambassador (multi-tenant) |
| **budget** | 🆕 | ❌ | ❌ | **TCB-only** |
| **check_rate_limit** | 🆕 | ❌ | ❌ | **TCB-only** |
| **dashboard_analytics** | 🆕 | ❌ | ❌ | **TCB-only** |
| **filtered_campaigns** | 🆕 | ❌ | ❌ | **TCB-only** |
| **global_dashboard** | 🆕 | ❌ | ❌ | **TCB-only** |
| **influencer** | 🆕 | ❌ | ❌ | **TCB-only** |
| **rating_aggregation** | 🆕 | ❌ | ❌ | **TCB-only** |
| **reconciliation_checklist** | 🆕 | ❌ | ❌ | **TCB-only** |
| **reconciliation_snapshot** | 🆕 | ❌ | ❌ | **TCB-only** |
| **reconciliation_snapshot_job** | 🆕 | ❌ | ❌ | **TCB-only** |
| **review** | 🆕 | ❌ | ❌ | **TCB-only** |
| **segment** | 🆕 | ❌ | ❌ | **TCB-only** |
| **tracking_request_crawl** | 🆕 | ❌ | ❌ | **TCB-only** |
| **upload_avatar_social** | 🆕 | ❌ | ❌ | **TCB-only** |
| registry_match | ❌ | ✅ | ❌ | **vCreator-only** |
| staff | ❌ | ✅ | ❌ | **vCreator-only** |
| affiliate | ❌ | ❌ | ✅ | **Ambassador-only** |

**Tổng kết** (verified):
- **13 service Core** chia sẻ cả 3 → an toàn để sync
- **2 service TCB+Ambassador** (load_data, user_social_partner) — vCreator thiếu
- **14 service TCB-only** → đa số là feature mới
- **2 vCreator-only**: registry_match, staff
- **1 Ambassador-only**: affiliate

---

## 2. Admin Pages Matrix (37 pages tổng — verified)

| Admin Page | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| article | ✅ | ✅ | ✅ |
| configuration | ✅ | ✅ | ✅ |
| content | ✅ | ✅ | ✅ |
| dashboard | ✅ | ✅ | ✅ |
| data | ✅ | ✅ | ✅ |
| event | ✅ | ✅ | ✅ |
| event-statistic | ✅ | ✅ | ✅ |
| identification | ✅ | ✅ | ✅ |
| login | ✅ | ✅ | ✅ |
| news | ✅ | ✅ | ✅ |
| notification | ✅ | ✅ | ✅ |
| partner | ✅ | ✅ | ✅ |
| quick-action | ✅ | ✅ | ✅ |
| reconciliation | ✅ | ✅ | ✅ |
| segment | ✅ | ✅ | ✅ |
| staff | ✅ | ✅ | ✅ |
| tag | ✅ | ✅ | ✅ |
| transfer | ✅ | ✅ | ✅ |
| user | ✅ | ✅ | ✅ |
| user-partner | ✅ | ✅ | ✅ |
| bonus | ❌ | ✅ | ✅ |
| **analytics-dashboard** | 🆕 | ❌ | ❌ |
| **blacklist-keyword** | 🆕 | ❌ | ❌ |
| **content-import** | 🆕 | ❌ | ❌ |
| **dashboard-external** | 🆕 | ❌ | ❌ |
| **event-bonus** | 🆕 | ❌ | ❌ |
| **event-category** | 🆕 | ❌ | ❌ |
| **influencer** | 🆕 | ❌ | ❌ |
| **influencer-management** | 🆕 | ❌ | ❌ |
| **manage-code** | 🆕 | ❌ | ❌ |
| department | ❌ | ✅ | ❌ |
| employee-registry | ❌ | ✅ | ❌ |
| affiliate-campaign | ❌ | ❌ | ✅ |
| category | ❌ | ❌ | ✅ |
| common_configs | ❌ | ❌ | ✅ |
| gifts | ❌ | ❌ | ✅ |
| mission | ❌ | ❌ | ✅ |

**Tổng kết admin** (verified):
- **20 page core** chia sẻ cả 3 (chiếm 54% của TCB)
- **9 page TCB-only**: analytics-dashboard, blacklist-keyword, content-import, dashboard-external, event-bonus, event-category, influencer, influencer-management, manage-code
- **2 page vCreator-only**: department, employee-registry (organizational hierarchy)
- **5 page Ambassador-only**: affiliate-campaign, category, common_configs, gifts, mission
- **1 page vCreator+Ambassador (no TCB)**: bonus (TCB tách riêng thành event-bonus)

---

## 3. Frontend Pages Matrix (31 pages tổng — verified)

| Frontend Page | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| 404 | ✅ | ✅ | ✅ |
| account | ✅ | ✅ | ✅ |
| article | ✅ | ✅ | ✅ |
| bank | ✅ | ✅ | ✅ |
| common-article | ✅ | ✅ | ✅ |
| connect-tiktok | ✅ | ✅ | ✅ |
| content | ✅ | ✅ | ✅ |
| contract | ✅ | ✅ | ✅ |
| guide | ✅ | ✅ | ✅ |
| home | ✅ | ✅ | ✅ |
| login-tiktok | ✅ | ✅ | ✅ |
| main-home | ✅ | ✅ | ✅ |
| notification | ✅ | ✅ | ✅ |
| partner-home | ✅ | ✅ | ✅ |
| profile | ✅ | ✅ | ✅ |
| statistic | ❌ | ✅ | ✅ |
| **contact** | ✅ | ❌ | ❌ |
| **creator-info** | ✅ | ❌ | ❌ |
| **events-by-category** | ✅ | ❌ | ❌ |
| **login-google** | ✅ | ❌ | ❌ |
| **qa** | ✅ | ❌ | ❌ |
| bonus | ❌ | ✅ | ❌ |
| affiliate-campaigns | ❌ | ❌ | ✅ |
| affiliate-campaign-detail | ❌ | ❌ | ✅ |
| affiliate-commission | ❌ | ❌ | ✅ |
| affiliate-links | ❌ | ❌ | ✅ |
| campaigns | ❌ | ❌ | ✅ |
| ekyc | ❌ | ❌ | ✅ |
| identity-info | ❌ | ❌ | ✅ |
| support | ❌ | ❌ | ✅ |
| tax-code | ❌ | ❌ | ✅ |

**Tổng kết frontend** (verified):
- **15 page core** chia sẻ cả 3
- **5 page TCB-only**: contact, creator-info, events-by-category, login-google, qa
- **1 page vCreator-only**: bonus
- **9 page Ambassador-only**: affiliate suite (4) + campaigns + ekyc + identity-info + support + tax-code
- **1 page vCreator+Ambassador**: statistic (TCB chuyển vào dashboard mới)

---

## 4. TCB Dashboard (Next.js — completely new)

**KHÔNG TỒN TẠI ở vCreator/Ambassador.** Module hoàn toàn mới của TCB.

| Route | Mục đích |
|---|---|
| `/[locale]/login`, `/forgot-password`, `/reset-password`, `/accept-invite` | Auth flow (4 routes) |
| `/analytics` | Main KPI dashboard (Overview/Creators/Contents/Performance tabs) |
| `/campaigns`, `/campaigns/create`, `/campaigns/[id]` | Campaign management |
| `/contents`, `/contents/[id]` | Content management |
| `/influencers`, `/influencers/[id]` | Influencer browsing & detail |
| `/profiles`, `/profiles/[id]` | Profile management |
| `/performance` | Performance analytics |
| `/exports` | Data export |
| `/settings` | System settings |

**Tech stack mới**: Next.js 16 + React 19 + TanStack Query/Table + Zustand + shadcn/ui + next-intl (i18n)

→ **Decision point cho việc đồng bộ**: Dashboard này có nên port sang vCreator/Ambassador không? Hay TCB-exclusive mãi?

---

## 5. Domain Coverage Matrix (high-level)

Tổng hợp theo domain nghiệp vụ:

| Domain | TCB | vCreator | Ambassador | Sync priority |
|---|:---:|:---:|:---:|:---:|
| **Auth & User** (login, OTP, profile, KYC) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Content management** (CRUD, flow, moderation) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Campaign/Event** (CRUD, reward, schema) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Social integration** (TikTok, Google) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Notification** (push, admin) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Withdrawal & Cashflow** (basic) | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Article & News** | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ |
| **Reconciliation** | ✅ service+model+admin | 🟡 model+admin only | 🟡 model+admin only | 🟡 vCr/Amb có UI nhưng không có service workflow → có thể dead UI hoặc CRUD đơn giản |
| **Multi-tenant Partner** | ✅ partner | 🟡 workplace hierarchy | ✅ Partner model | 🟡 3 implementation khác nhau |
| **User segmentation** | ✅ service+model+admin | 🟡 admin page only | 🟡 admin page only | 🟡 Cần verify vCr/Amb có dùng thật không |
| **Transfer (payments)** | ✅ | ✅ | ✅ | 🟢 Đã đồng bộ (admin + service infrastructure) |
| **Statistic page (creator)** | ❌ (đã chuyển sang dashboard) | ✅ | ✅ | 🟢 Hoặc TCB porting xuống dashboard |
| **Budget allocation** | 🆕 | ❌ | ❌ | 🔴 TCB-only |
| **Reconciliation workflow** (checklist + snapshot) | 🆕 | ❌ | ❌ | 🔴 TCB-only — engine evaluation phức tạp |
| **Analytics dashboard** (KPI, trends) | 🆕 | ❌ | ❌ | 🔴 TCB-only — Next.js dashboard mới |
| **Campaign matching engine** | 🆕 | ❌ | ❌ | 🔴 TCB-only |
| **Influencer profile management** | 🆕 | ❌ | ❌ | 🔴 TCB-only |
| **Content review/moderation service** | 🆕 | ❌ | ❌ | 🔴 TCB-only |
| **Content moderation tools** (blacklist-keyword, manage-code, content-import) | 🆕 | ❌ | ❌ | 🔴 TCB-only |
| **Affiliate program** (campaign + commission + links) | ❌ | ❌ | ✅ | 🔵 Ambassador-only |
| **Mission/Gift redemption** | ❌ | ❌ | ✅ | 🔵 Ambassador-only |
| **Workplace/Department/Employee Registry** | ❌ | ✅ | ❌ | 🟣 vCreator-only (B2B org hierarchy) |
| **Registry match engine** | ❌ | ✅ | ❌ | 🟣 vCreator-only (import V2) |

---

## 6. Recommendations — Where to start syncing

### 🟢 Group A — Đã đồng bộ tốt (KHÔNG cần làm gì)
**13 services + 20 admin pages + 15 frontend pages** core. Stable, có thể refactor thành shared lib nhưng không urgent.

### 🟡 Group B — Đồng bộ một phần (CẦN ALIGN)
1. **Reconciliation**: Cả 3 đều có model + admin page, nhưng chỉ TCB có service workflow đầy đủ → quyết định:
   - vCr/Amb có dùng admin reconciliation thật không?
   - Nếu dùng thì phải port service xuống
   - Nếu không thì xem xét dọn dẹp dead UI
2. **User segmentation**: Tương tự — vCreator/Ambassador có admin page `segment` nhưng không có service. Verify dead UI hoặc port từ TCB.
3. **Multi-tenant**: TCB partner ↔ vCreator workplace ↔ Ambassador Partner — 3 implementation khác nhau cho cùng concept. Long-term cần thống nhất.
4. **Statistic page**: vCr/Amb có frontend page riêng, TCB đã chuyển vào dashboard mới. Cân nhắc port TCB statistic vào frontend cũ hoặc port frontend cũ sang dashboard.

### 🔴 Group C — TCB-specific, quyết định strategic
1. **Budget management** — port hay không?
2. **Analytics Dashboard (Next.js)** — TCB-exclusive vs port sang vCr/Amb vs build chung trong at-core.
3. **Reconciliation engine** — phức tạp (3 services, 6 models, 30+ methods).
4. **Influencer/profile review** — useful cho Ambassador (affiliate context) không?
5. **Content moderation tools** (blacklist-keyword, auto-approve-rule, manage-code, content-import) — useful cho all → cân nhắc backport.

### 🔵 Group D — Sản phẩm-specific giữ riêng
1. **Ambassador**: affiliate suite (campaign, commission, links), gift redemption, mission, ekyc, tax-code — đặc trưng business model affiliate.
2. **vCreator**: workplace hierarchy (brand/company/unit), department/employee-registry, registry_match — đặc trưng B2B.

---

## 7. Đề xuất bước tiếp theo

### Bước 1 — Confirm "Group B" alignment (1-2 ngày)
- Verify: vCreator/Ambassador có thực sự dùng admin pages `reconciliation`, `segment`, `transfer` không? Hay là dead code copy từ fork.
- Quick check: tìm route handler / controller trong backend xem có wire không.

### Bước 2 — Strategic decision với stakeholder
Họp với PM/tech lead để chốt 4 câu hỏi:
1. TCB Dashboard (Next.js) có cần port không?
2. Reconciliation workflow có cần port không?
3. Budget management có dùng cho vCreator/Ambassador không?
4. Multi-tenant nên unify (1 implementation chung) hay giữ 3 cái?

### Bước 3 — Detailed PRD per item cần sync
Sau khi chốt Bước 2, viết PRD riêng cho từng item Group B/C cần đồng bộ.

### Bước 4 — Long-term: shared codebase strategy
Nếu Group A quá lớn (chiếm gần 50% codebase), cân nhắc extract thành `at-core` library hoặc monorepo.

---

## Source files

- [inventory-techcombank.md](./inventory-techcombank.md) — 458 dòng, 29 services, 85 models
- [inventory-vcreator.md](./inventory-vcreator.md) — 250 dòng, 15 services, 68 models
- [inventory-ambassador.md](./inventory-ambassador.md) — 250 dòng, 16 services, 66+ models
- [services-detailed.md](./services-detailed.md) — **Detailed inventory**: LOC + exported functions per service, grouped by domain. Cho biết file nào synced (LOC giống), file nào đã divergent (LOC khác).
- [verification-report.md](./verification-report.md) — kết quả spot-check + corrections

> **Verification status**: Matrix này đã được rebuild **100% từ ground truth filesystem** (không trust phân loại của agent). Counts khớp với `find` actual. Caveat duy nhất: descriptions từ agent có thể chưa hoàn toàn chính xác — verify thêm cần đọc code thật.
