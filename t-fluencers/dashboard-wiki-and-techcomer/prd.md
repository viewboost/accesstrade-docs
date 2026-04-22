# PRD — Dashboard Wiki & Phân loại Techcomer

**Date:** 2026-04-15
**Status:** Implemented (retroactive documentation)
**Scope:** T-Fluencers Analytics Dashboard (`/analytics` page)
**Owner:** Product Manager
**Related repos:**
- Backend: `accesstrade-projects/techcombank/backend`
- Frontend: `accesstrade-projects/techcombank/dashboard`

---

## 1. Executive Summary

Dashboard T-Fluencers đang có hai vấn đề nghiệp vụ song song:

1. **Các chỉ số khó đọc** — người xem không chắc mỗi con số nghĩa gì, công thức nào, có tính bài đăng đã hủy hay không; dẫn đến nhầm lẫn khi báo cáo và ra quyết định.
2. **Không phân biệt được CBNV Techcombank (Techcomer) với Influencer bên ngoài (Mass)** — trong khi nghiệp vụ cần theo dõi tỷ lệ tham gia của CBNV nội bộ và so sánh hiệu quả giữa 2 nhóm.

PRD này chuẩn hoá hai khối chức năng đi kèm:
- **Wiki giải thích chỉ số** — hệ thống label + popover + side panel giải thích ý nghĩa và công thức từng chỉ số.
- **Phân loại Techcomer / Mass** — cột "Nhóm" trong bảng, filter dropdown 4-mode, và breakdown inline ở từng KPI card.

## 2. Business Objectives

1. **Giảm sai lệch khi đọc số** — mọi KPI quan trọng đều có (i) icon giải thích công thức + ghi chú loại trừ bài đăng đã hủy.
2. **Cho phép so sánh Techcomer vs Mass** — người quản lý thấy được mỗi nhóm đóng góp bao nhiêu bài đăng, lượt xem, phí quảng cáo.
3. **Theo dõi tỷ lệ tham gia của CBNV** — KPI "Tổng số Influencer" và các card đều phản ánh đóng góp của Techcomer một cách trực quan.
4. **Duy trì consistency dữ liệu** — số trên các card, bảng, widget không mâu thuẫn nhau; những sai lệch còn lại được flag công khai trong code + plan file.

## 3. Success Metrics

| Metric | Baseline | Target |
|---|---|---|
| Số lượt người dùng click vào icon (i) | 0 (chưa có) | ≥ 30% session mở 1 popover |
| Số báo cáo sai do hiểu nhầm "video có bao gồm hủy?" | Xảy ra hằng tuần | 0 sau khi release |
| Khả năng lọc nhanh theo Techcomer | Không có | 1 thao tác bằng dropdown |
| Số dòng KPI khớp với bảng Danh sách Influencer | Chênh vài dòng | Khớp hoặc chỉ chênh do bài đăng bị hủy (documented) |

## 4. User Personas

**P1. Account Manager TCB** — dùng dashboard hằng tuần để báo cáo hiệu quả thử thách lên sếp. Cần hiểu số nhanh, cần phân biệt CBNV tham gia vì ảnh hưởng câu chuyện báo cáo.

**P2. Ops / Finance** — dùng số từ dashboard để đối chiếu chi phí quảng cáo và đối soát. Cần số chính xác, không bao gồm bài đăng đã hủy.

**P3. Marketing lead** — so sánh nhóm Techcomer vs Mass để quyết định phân bổ ngân sách tiếp theo cho kênh nào.

## 5. Scope

### In scope (đã implement)

- Hệ thống Wiki: popover inline + side panel tổng hợp, schema `description / trend / formula / note` cho mỗi chỉ số.
- Định nghĩa canonical Techcomer / Mass ở cả backend Go và frontend TypeScript.
- StaffBadge component dùng chung (bảng + filter + KPI cards).
- Filter dropdown 4 mode (Tất cả / Techcomer / Mass / Tùy chọn) tác động toàn dashboard.
- Cột "Nhóm" trong bảng Danh sách Influencer với sort + filter.
- Breakdown inline trên 4 KPI card của Tab Influencer (Tổng Influencer / Video / Lượt xem / Phí QC).
- Fix bug lookup `user-partners` nhận nhầm row.

### Out of scope (chưa làm trong PRD này)

- Bar "Hiệu quả Techcomer vs Mass" (widget C2 trong brainstorm).
- Card "Tỷ lệ hoạt động Techcomer" (B3).
- Badge ⭐ Techcomer top performer (D1, compliance signal).
- Dataset Timeline chart theo nhóm (C3).
- Tab CBNV riêng biệt.

## 6. Functional Requirements

Ký hiệu:
- **Must** = blocker cho release hiện tại.
- **Should** = quan trọng nhưng có workaround.
- **Could** = nice to have, skip được.

### 6.1 Wiki — Giải thích chỉ số

#### FR-001: Wiki schema chuẩn cho mọi chỉ số (Must)

Mỗi metric trong dashboard có entry i18n theo schema:
- `label` (bắt buộc)
- `description` (bắt buộc)
- `trend` (tùy chọn)
- `formula` (tùy chọn)
- `note` (tùy chọn)

**Acceptance Criteria:**
- [x] File `src/messages/vi/wiki.json` + `en/wiki.json` tồn tại với namespace `wiki`.
- [x] Render đủ 4 khối khi entry khai báo, bỏ qua khối không khai báo.
- [x] `<MetricInfo metricKey="...">` render popover từ schema.

#### FR-002: Icon (i) gắn cạnh mọi KPI chính (Must)

**Acceptance Criteria:**
- [x] 4 KPI card (Tab Overview) có icon (i).
- [x] 4 KPI card (Tab Influencer) có icon (i).
- [x] Mọi cột chứa số của bảng Danh sách Influencer và bảng thử thách có icon (i).
- [x] Widget Timeline / Interaction / Approval / Platform / Reconciliation có icon (i) trên CardTitle.

#### FR-003: Side panel Wiki tổng hợp (Must)

**Acceptance Criteria:**
- [x] Nút "Wiki" ở header mở dialog liệt kê toàn bộ metric, nhóm theo group.
- [x] Banner amber ở đầu panel nhắc nguyên tắc "không bao gồm hủy".
- [x] Các group hiển thị đúng thứ tự: KPI → Ranking → Status → Interaction → Segments → Staff → Payment → Campaign → InfluencerTable → Charts.

#### FR-004: Mô tả phải "ngôn ngữ nghiệp vụ" (Must)

**Acceptance Criteria:**
- [x] Mô tả KHÔNG chứa tên field raw (ví dụ tránh `statusStaff == "employee"` trong wiki).
- [x] Thuật ngữ tiếng Việt nhất quán: "Thử thách" thay "Chiến dịch", "Influencer" không số nhiều, "Techcomer" và "Mass" thay "CBNV" và "Khách" trong PRD này.
- [x] Công thức được viết dạng nghiệp vụ ("Đã dùng ÷ Tổng × 100") thay vì pseudo-code.

#### FR-005: Trend block hiển thị nổi bật (Should)

**Acceptance Criteria:**
- [x] Khi entry có `trend`, popover render khối xanh riêng với icon TrendingUp.
- [x] Whitespace trong description được preserve bằng `whitespace-pre-line`.

### 6.2 Phân loại Techcomer / Mass

#### FR-006: Canonical isStaff helper (Must)

**Acceptance Criteria:**
- [x] BE: `constants.IsStaff(statusStaff string) bool` với unit test 5 case.
- [x] FE: `lib/staff.ts` export `isStaff()`, `staffGroup()`, `STAFF_STATUS` với unit test 8 case.
- [x] Chỉ `employee` được coi là Techcomer; mọi giá trị khác (bao gồm `not_verify`, `not_employee`, `undefined`, `null`) → Mass.

#### FR-007: StaffBadge component (Must)

**Acceptance Criteria:**
- [x] Props: `statusStaff`, `iconOnly`, `className`.
- [x] Techcomer → briefcase icon + nền đỏ pastel; Mass → user icon + nền xám.
- [x] Hỗ trợ tooltip (`title` attribute).

#### FR-008: Cột "Nhóm" trong bảng Danh sách Influencer (Must)

**Acceptance Criteria:**
- [x] Cột mới sau cột Influencer, trước cột Thử thách.
- [x] Render `<StaffBadge>` full label (có text).
- [x] Cột cho phép sort + filter bằng meta filter function `(row, id, value)`.
- [x] Header có icon (i) trỏ vào `staffDefinition` entry.

#### FR-009: Filter dropdown 4 mode (Must)

**Acceptance Criteria:**
- [x] Dropdown mới trong FilterBar với 4 option: Tất cả Influencer / Techcomer / Mass / Tùy chọn.
- [x] Chọn Techcomer/Mass → dropdown gập, không hiển thị list search.
- [x] Chọn Tùy chọn → hiển thị search + list, mỗi row có icon-only StaffBadge.
- [x] State `creatorMode: 'all' | 'staff' | 'guest' | 'custom'` lưu vào `DashboardFilters`.
- [x] Khi apply: mode `staff/guest` được resolve thành explicit `creatorIds` để BE xử lý qua param `userIds` đã có sẵn.

#### FR-010: Breakdown Techcomer inline trên 4 KPI card (Must)

**Acceptance Criteria:**
- [x] Mỗi card (Tổng Influencer / Video / Lượt xem / Phí QC) có pill dưới số chính.
- [x] Pill style: bg đỏ pastel + briefcase icon + `{value} · {pct}%`.
- [x] Mass được ẩn — người xem tự suy ra = Total − Techcomer.
- [x] Pill ẩn khi `total = 0`.

#### FR-011: BE aggregate pipeline theo nhóm (Must)

**Acceptance Criteria:**
- [x] Pipeline `GetCreatorKPIsByStaffBreakdown` trả về trong 1 query: `{ total, staff, guest, totalVideos, staffVideos, guestVideos, totalViews, staffViews, guestViews, totalCash, staffCash, guestCash }`.
- [x] Dùng `$lookup` với `let` + `$match { statusStaff: "employee" }` → không misclassify khi user có nhiều user-partners row.
- [x] Response `CreatorKPIsResponse` expose `TotalStaff`, `TotalStaffVideos`, `TotalStaffViews`, `TotalStaffCash`.

#### FR-012: Lookup user-partners pipeline đúng (Must)

**Acceptance Criteria:**
- [x] `GetCreatorLeaderboardPipeline` cũng dùng `let` pipeline + filter `statusStaff: "employee"`.
- [x] Cả bảng và KPI card dùng cùng rule phân loại → không chênh nhau khi filter Techcomer.

### 6.3 Nguyên tắc "không bao gồm hủy"

#### FR-013: Engagement tính net-net (Must — đã làm BE)

**Acceptance Criteria:**
- [x] Pipeline `GetDashboardKPIPipeline` có `totalLikesRejected`, `totalCommentsRejected`.
- [x] `InteractionMetrics.Likes / Comments` trả net values (comment `// are NET values`).
- [x] Công thức: `(netLikes + netComments) / netViews × 100`.

#### FR-014: Total Influencers (Tab Influencer) chỉ đếm người có bài đăng hợp lệ (Must)

**Acceptance Criteria:**
- [x] Pipeline filter `netVideos > 0` trước khi count.
- [x] Khớp với số dòng bảng Danh sách Influencer (trừ edge case user có filter explicit).

#### FR-015: Ẩn KPI "Tỷ lệ nghỉ" (Must)

**Acceptance Criteria:**
- [x] Card churn ẩn trong `GlobalCreatorKPIs` + TODO comment chỉ công thức đúng.
- [x] Entry `churnRate` bỏ khỏi group `kpi` trong wiki.

### 6.4 FE Filter State Management

#### FR-016: `DashboardFilters.creatorMode` (Must)

**Acceptance Criteria:**
- [x] Type mới `CreatorFilterMode` export từ `types/analytics.ts`.
- [x] `filter-bar.tsx` sync state với initialFilters/URL.
- [x] `hasUnappliedChanges` detect thay đổi creatorMode.

#### FR-017: Resolve mode thành creatorIds trước khi apply (Must)

**Acceptance Criteria:**
- [x] Khi mode = `staff`, `creatorIds` = danh sách Techcomer ID trong snapshot `creators`.
- [x] Khi mode = `guest`, `creatorIds` = danh sách Mass ID.
- [x] Khi mode = `custom`, dùng list người dùng chọn.
- [x] `buildQueryParams` gửi `creatorIds` xuống BE qua `userIds` param.

## 7. Non-Functional Requirements

### NFR-001: i18n nhất quán (Must)

- Mọi label hiển thị phải đi qua `next-intl`, không hard-code string Việt/Anh.
- Cả 2 locale vi/en luôn đồng bộ khi thêm metric mới.

### NFR-002: Performance filter (Should)

- Filter staff/guest resolve ở FE bằng `creators` snapshot (đã fetch). Không gọi thêm API khi đổi mode.
- Breakdown Techcomer ở KPI cards: dùng CHUNG 1 pipeline BE thay vì nhiều query — tiết kiệm round-trip.

### NFR-003: Không break regression dữ liệu cũ (Must)

- Pipeline `$ifNull` guard cho legacy documents thiếu field `totalContentRejected`.
- Tests backend + frontend pass (trừ 2 CPV test pre-existing fail đã được document).

### NFR-004: Schema extensible (Should)

- Thêm metric mới chỉ cần: entry trong `wiki.json` (vi + en), import `<MetricInfo metricKey="...">` ở chỗ hiển thị.
- `StaffBreakdownRow` accept `formatValue` callback → tái dụng được cho currency/number.

### NFR-005: Consistency giữa FE và BE (Must)

- Rule "ai là Techcomer" được code cùng luật ở 2 helper (BE: `IsStaff`, FE: `isStaff`) với cùng test case.
- Kết quả lookup: BE aggregate và FE filter snapshot phải khớp (do cùng source `user-partners.statusStaff=employee`).

### NFR-006: Accessibility (Should)

- StaffBadge có `aria-label` + tooltip.
- Popover Wiki dùng Radix Primitive (keyboard nav built-in).

## 8. Epics

### EPIC-001: Wiki System (Must)

**FRs:** FR-001, FR-002, FR-003, FR-004, FR-005
**Story count:** ~8
**Business value:** Giảm hiểu lầm nghiệp vụ, tự phục vụ khi người mới onboard.

### EPIC-002: Techcomer / Mass Classification (Must)

**FRs:** FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012
**Story count:** ~10
**Business value:** Phân tích đóng góp của CBNV nội bộ; hỗ trợ so sánh hiệu quả 2 nhóm.

### EPIC-003: Exclude Cancelled Posts Everywhere (Must)

**FRs:** FR-013, FR-014, FR-015
**Story count:** ~5
**Business value:** Số liệu khớp định nghĩa nghiệp vụ; không nhầm sang bao gồm bài đăng hủy.

### EPIC-004: Filter State Management (Must)

**FRs:** FR-016, FR-017
**Story count:** ~3
**Business value:** Toàn bộ dashboard phản hồi nhất quán với bộ lọc đã chọn.

## 9. Traceability Matrix

| Epic | Epic Name | FRs | Story estimate |
|---|---|---|---|
| EPIC-001 | Wiki System | FR-001, FR-002, FR-003, FR-004, FR-005 | 8 |
| EPIC-002 | Techcomer / Mass Classification | FR-006 → FR-012 | 10 |
| EPIC-003 | Exclude Cancelled Posts | FR-013, FR-014, FR-015 | 5 |
| EPIC-004 | Filter State Management | FR-016, FR-017 | 3 |

Tổng: **17 FR / 6 NFR / 4 Epic / ~26 story** (đã implement toàn bộ trừ phần được liệt kê ở mục 5 "Out of scope").

## 10. Prioritization Summary

| Priority | FR | NFR |
|---|---|---|
| Must | 16 | 4 |
| Should | 1 (FR-005) | 2 |
| Could | 0 | 0 |

## 11. Key User Flows

### Flow 1: Mới dùng dashboard, muốn biết "Tổng phí QC" là gì
1. Mở tab Overview.
2. Thấy icon (i) cạnh "Tổng phí quảng cáo".
3. Click icon → popover giải thích công thức + ghi chú không bao gồm hủy + đã bao gồm tạm tính.
4. Đóng popover, đọc số với hiểu biết đầy đủ.

### Flow 2: Account Manager muốn xem riêng hiệu quả Techcomer
1. Filter bar → dropdown Influencer → chọn "Techcomer".
2. Bấm Áp dụng → toàn bộ KPI cards + bảng cập nhật theo nhóm Techcomer.
3. Đọc pill "🧳 X · Y%" trên card để xem tỷ trọng trong từng chỉ số.

### Flow 3: Ops cần tra cứu nhanh 1 Influencer cụ thể
1. Dropdown Influencer → chọn "Tùy chọn".
2. Search theo tên, check nhiều row.
3. Các row có icon 🧳 bên trái = Techcomer (không cần mở wiki).
4. Apply → dashboard filter chính xác theo danh sách đã pick.

## 12. Dependencies

### Internal
- Collection MongoDB `user-partners` với `statusStaff` field.
- Collection `user-event-analytic-daily`, `event-analytic-daily` có cấu trúc `statistic.*.rejected`.
- Existing endpoints: `/analytics/creator-kpis`, `/analytics/creators`, `/analytics/dashboard`.
- `next-intl` i18n đã setup, Radix Popover + Dialog đã cài.

### External
- Không có dependency ngoài.

## 13. Assumptions

1. Một Influencer chỉ được coi là Techcomer khi có ít nhất 1 user-partners row với `statusStaff = "employee"`. Các row khác (`not_verify`, `not_employee`, empty) không đủ điều kiện.
2. Backend populate `statistic.like.rejected` / `comment.rejected` trong `event-analytic-daily` từ 2025-10-07 trở đi — không cần backfill cho dashboard hiện tại (default 30 ngày).
3. Không có partner nào ngoài TCB dùng giá trị `statusStaff = "employee"` → filter BE `statusStaff: "employee"` đủ chuẩn xác.

## 14. Open Questions

1. **Có cần ghi rõ số Mass trong pill không?** Hiện ẩn vì `Mass = Total − Techcomer`; người xem tự suy. Stakeholder có ok không?
2. **Khi filter "Techcomer" mà có 0 Influencer phù hợp, có cần empty state riêng không?** Hiện hiển thị các card = 0.
3. **Có cần "Techcomer top performer" flag (⭐) trong leaderboard không?** Brainstorm đề xuất (D1) vì compliance; hiện chưa làm.
4. **Bảng leaderboard (`/analytics/creators`) BE chưa filter theo userIds** — FE tự filter client-side. Có nên fix BE để tiết kiệm data transfer?

## 15. Out-of-scope Items (nhắc lại)

- Widget "Hiệu quả Techcomer vs Mass" (Bar grouped/stacked).
- Card "Tỷ lệ hoạt động Techcomer" độc lập.
- Badge flag Techcomer top performer.
- Timeline dataset theo nhóm.
- Tab dedicated cho Techcomer.

## 16. Related Documents

- Brainstorming: [`/.bmad/brainstorming-tcb-dashboard-isstaff-metrics-2026-04-15.md`](../../../../.bmad/brainstorming-tcb-dashboard-isstaff-metrics-2026-04-15.md)
- Plan implementation: [`dashboard/plans/20260415-1700-isstaff-metrics/plan.md`](../../../techcombank/dashboard/plans/20260415-1700-isstaff-metrics/plan.md)
- Backend metric fixes TODO: [`dashboard/plans/backend-metric-fixes.md`](../../../techcombank/dashboard/plans/backend-metric-fixes.md)
- Commits trên branch `fix/dashboard-0415`:
  - `110cead0` fix engagement + total influencers
  - `242c1ae1` feat wiki + filters
  - `bf9d4851` feat Techcomer / Mass classification
  - `e6464d33` feat show Techcomer share on KPI cards
  - `af9394ee` fix lookup user-partners misclassification

## 17. Stakeholders

- **Product owner:** Team T-Fluencers TCB
- **Engineering:** DISO fullstack team
- **QA:** Manual UAT theo flow ở mục 11
- **Business:** Account Managers, Ops, Marketing lead

---

*Generated retroactively after implementation. See commits & plans for full traceability.*
