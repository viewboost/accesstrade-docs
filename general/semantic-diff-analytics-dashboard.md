# Semantic Diff — Analytics & Dashboard Group

> **Generated**: 2026-05-07
> **Files trong scope**: `dashboard_analytics.go`, `global_dashboard.go`, `rating_aggregation.go`

| Service | TCB | vCreator | Ambassador |
|---|---:|---:|---:|
| dashboard_analytics.go | **1731 LOC** | ❌ | ❌ |
| global_dashboard.go | 309 LOC | ❌ | ❌ |
| rating_aggregation.go | 186 LOC | ❌ | ❌ |
| **Tổng** | **2226 LOC** | **0** | **0** |

---

## TL;DR

Cả nhóm này **TCB-only**. Không có gì để diff — chỉ describe TCB đang có gì.

3 service phục vụ **TCB Dashboard (Next.js mới)** — đã thấy trong matrix v2 là module dashboard hoàn toàn mới. Service backend tương ứng đã được implement đầy đủ.

→ Đây là **đặc điểm phân biệt lớn nhất** của TCB: không sản phẩm nào trong AccessTrade ecosystem có analytics layer ngang ngửa.

---

## 1. `service/dashboard_analytics.go` (1731 LOC, 12 hàm)

### Hàm public chính

| Hàm | Mục đích |
|---|---|
| `GetDashboardKPIs` | Aggregate KPIs (creators, contents, views, approval rate) cho 1 date range |
| `GetDashboardKPIsWithComparison` | Như trên + compare với period trước (delta + trend) |
| `GetPlatformBreakdown` | Số liệu chia theo platform (TikTok/Facebook/IG/YouTube) — chỉ content count |
| `GetPlatformBreakdownWithMetrics` | Như trên + views/likes/comments per platform |
| `GetCreatorLeaderboard` | Top creators theo metric (pagination) |
| `GetCreatorSegments` | Breakdown creator theo segment (size buckets, demographic) |
| `GetCreatorKPIs` | KPI per creator + trend |
| `GetApprovalAnalytics` | Approval rate, rejection reasons, optional per-platform breakdown |
| `GetTimelineTrends` | Time-series data (line chart) |
| `GetTransfers` | Lịch sử transfers (payout) trong period |
| `ExportAnalytics` | Export CSV/XLSX (dùng excelize lib) |

### Cấu trúc response

3 dạng response chính:
1. **KPI cards**: scalar metrics + trend (vs previous period) → cho dashboard widget
2. **Breakdown lists**: array of {category, metrics} → cho table/chart
3. **Time-series**: array of {date, value} → cho line/bar chart

### Ý nghĩa nghiệp vụ

Đây là backend cho **TCB T-Fluencers Dashboard** (Next.js 16, đã thấy trong inventory). Dashboard có 4 tab: Overview / Creators / Contents / Performance — mỗi tab gọi 1-2 hàm trong service này.

Tính năng đặc biệt:
- **Period comparison**: tự động tính period trước (vd: "tháng trước cùng kỳ") để show trend.
- **Platform breakdown**: hỗ trợ multi-platform analytics (4 platform).
- **Export CSV/XLSX**: dùng `excelize` lib (Go) → admin tải báo cáo cho stakeholder.

### Vì sao TCB-only

- vCreator có frontend page `statistic` nhưng backend chỉ aggregate ở `user.go.UpdateStatistic` (per-user, không phải global dashboard).
- Ambassador có `affiliate-commission` page nhưng không có dashboard cấp platform.
- TCB build dashboard riêng (Next.js) cho stakeholder TCB → cần backend layer riêng.

---

## 2. `service/global_dashboard.go` (309 LOC, 2 hàm)

### Hàm public

| Hàm | Mục đích |
|---|---|
| `GetGlobalDashboard(scope)` | Top-level dashboard cho admin / partner-level view |
| `GlobalDashboard()` | Entry point (constructor) |

### Response shape

```go
type GlobalDashboardResponse struct {
    Scope       string                // "platform" | "partner"
    LastUpdated time.Time
    Creators    GlobalCreatorMetrics  // total, new, activeRate, churnRate + trends
    Campaigns   []GlobalCampaignData  // top campaigns trong portfolio
    Budget      GlobalBudgetMetrics   // budget allocation overview
}
```

### Ý nghĩa nghiệp vụ

Khác với `dashboard_analytics` (focus content/creator metrics), `global_dashboard` cho **C-level view**:
- **Creator health**: total, new, active rate, churn rate
- **Campaign portfolio**: top campaigns đang chạy
- **Budget overview**: budget allocated / spent / remaining

Có cả **scope** parameter ("platform" vs "partner") → cùng 1 endpoint, partner xem được data của partner mình, admin xem toàn platform.

→ Đây là dashboard **báo cáo executive**. Sử dụng Redis cache (`internal/module/redis`) → cho phép refresh nhanh, không phải aggregate realtime mỗi request.

---

## 3. `service/rating_aggregation.go` (186 LOC, 3 hàm)

### Hàm public

| Hàm | Mục đích |
|---|---|
| `RecalculateProfileRating(profileID)` | Tính lại rating cho 1 profile từ tất cả review của profile đó |
| `GetCachedRating(profileID)` | Get rating đã cache (RatingCache model) |
| `RatingAggregation()` | Constructor |

### Logic chính

- Lấy tất cả `Review` documents với `profileID`, status=approved.
- Tính weighted average với **time-decay weight** (review cũ có weight thấp hơn review mới).
- Aggregate ra 5 sub-ratings: Content Quality, Professionalism, Communication, On-Time Delivery, Performance.
- Lưu vào `RatingCache` model → tránh recalculate mỗi request.

### Ý nghĩa nghiệp vụ

TCB có hệ thống **review profile creator** (xem service `review.go` trong group Targeting & Matching). Ratings được dùng cho:
- Hiển thị trên influencer profile page
- Filtering trong influencer search
- Auto-approval condition (creator rating cao có thể auto-approve campaign)

Time-decay design: review cách 1 năm có weight ~0.5 so với review tuần này → fair với creator đã cải thiện.

→ Feature này tied với **review engine của TCB**. Không có ở vCr/Amb (không có concept review/rating creator).

---

## 4. Models phát hiện thú vị

Các model được service này dùng (TCB-only):
- **`RatingCacheRaw`** — cache rating per profile (sub-ratings + last updated)
- **`PerformanceData`** — performance metrics raw data (creator-level)

→ 2 model này KHÔNG có ở vCr/Amb. Cả `dashboard_analytics` chủ yếu query từ collections **đã có ở 3 dự án** (`UserRaw`, `ContentRaw`, `EventRewardRaw`, `CashFlowRaw`) — tức là vCr/Amb có đủ data để build dashboard tương tự, nhưng chưa implement layer aggregate.

---

## 5. Câu hỏi business mở

1. **Dashboard Next.js có port sang vCr/Amb không?** Đây là decision strategic đã raise ở matrix v2 section "Recommendations". Backend service đã đầy đủ → port chỉ cần config DB connection + adapt models nếu schema khác.
2. **Rating system có dùng thật ở TCB không?** Service tồn tại nhưng cần check admin có flow tạo review không (xem `review.go` group Targeting).
3. **Global dashboard scope = "partner"** — dùng cho UC nào? Có phải multi-tenant cho TCB partner (chi nhánh khác nhau) hay là legacy code?
4. **Approval analytics** trong dashboard_analytics có phải duplicate với `content_flow.go` (group Content) không? Hay là dimension khác (analytics view vs operational view)?

---

## 6. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Dashboard analytics layer** | ✅ Full (1731 LOC, 12 endpoints) | ❌ | ❌ |
| **Executive dashboard** | ✅ (309 LOC, 2 scope) | ❌ | ❌ |
| **Profile rating engine** | ✅ (186 LOC, time-decay) | ❌ | ❌ |
| **Frontend dashboard** | ✅ Next.js 16 (T-Fluencers) | ❌ | ❌ |

**Tổng đánh giá**: Đây là **TCB monopoly tuyệt đối**. Không có gì port từ vCr/Amb (cả 2 không có gì). Direction port duy nhất: TCB → 2 sản phẩm còn lại nếu họ cần dashboard.

**Effort port nếu cần**:
- Backend: ~2226 LOC service + 2 models — khả thi (~1-2 tuần dev)
- Frontend: dashboard Next.js là project riêng (~17 routes + components) — phức tạp hơn (~3-4 tuần)
