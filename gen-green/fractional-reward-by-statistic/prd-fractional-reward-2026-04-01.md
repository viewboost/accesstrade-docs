# PRD: Hỗ trợ thưởng by-statistic giá trị thập phân (0.1đ - 0.9đ)

**Project:** Gen-Green (VCreator)
**Date:** 2026-04-01
**Author:** Product Manager
**Status:** Draft
**Version:** 3.0

---

## 1. Executive Summary

Cho phép Admin setup thưởng by-statistic với giá trị thập phân 1 chữ số (0.1đ → 0.9đ) cho `CashPerView`, `CashPerLike`, `CashPerComment`. Hiện tại hệ thống dùng `float64` mà **không có rounding** nên khi nhập giá trị lẻ sẽ gây sai lệch khi thanh toán.

**Thay đổi cốt lõi:** Giữ nguyên giá trị thập phân xuyên suốt hệ thống — **KHÔNG làm tròn** ở bất kỳ bước trung gian nào (reward, cashflow, statistic, reconciliation). Chỉ làm tròn (floor) **duy nhất tại bước thanh toán cho user** (transfer/withdraw). Điều này đảm bảo độ chính xác tối đa trong tính toán nội bộ và chỉ mất tối đa 0.9đ tại thời điểm user thực sự nhận tiền.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Cho phép setup thưởng linh hoạt hơn (0.1đ/view thay vì chỉ số nguyên) | Admin có thể tạo schema với CashPer* = 0.1 → 0.9 |
| 2 | Đảm bảo chính xác tối đa trong tính toán nội bộ | Không mất dữ liệu thập phân ở các bước trung gian |
| 3 | Thanh toán cho user luôn là số nguyên VND | Chỉ floor khi transfer/withdraw — user nhận số tròn |

---

## 3. User Personas

| Persona | Vai trò | Nhu cầu |
|---------|---------|---------|
| **Admin/Staff** | Setup event schema, reconciliation, transfer | Nhập CashPerView = 0.5đ, reconciliation chạy đúng |
| **Creator (User)** | Xem balance, rút tiền | Thanh toán tròn số, không mất tiền lẻ |
| **Finance/Kế toán** | Đối soát, export báo cáo | Tổng tiền khớp, thanh toán chính xác |

---

## 4. Data Flow Analysis

Trước khi đọc Functional Requirements, cần hiểu money flow trong hệ thống:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MONEY FLOW (nguồn → thanh toán)             │
│                                                                 │
│  NGUỒN SINH CASH (chỉ 2 loại):                                 │
│                                                                 │
│  1. By-Statistic reward (CashPer* × count):                    │
│     reward.Cash = TotalCashLike + TotalCashComment              │
│                   + TotalCashView                               │
│     → Tạo số lẻ khi CashPer* = 0.x                             │
│     → GIỮ NGUYÊN giá trị thập phân                              │
│                                                                 │
│  2. Milestone reward (CashMilestone gán thẳng):                 │
│     reward.Cash = schema.CashReward.CashMilestone               │
│     → GIỮ NGUYÊN giá trị                                        │
│                                                                 │
│  TRUNG GIAN (giữ nguyên thập phân xuyên suốt):                 │
│                                                                 │
│  reward.Cash (có thể lẻ, ví dụ 500.5)                          │
│    → reconciliation.TotalCash = $sum(reward.Cash) = float64     │
│      → cashflow.Value = TotalCash = float64                     │
│        → newBalance = old + Value = float64                     │
│        → GetRemaining() = $sum(Values) = float64                │
│          → UserStatistic.CashRemaining = float64                │
│          → UserStatistic.TotalCash* = float64                   │
│                                                                 │
│  THANH TOÁN (DUY NHẤT floor ở đây):                             │
│                                                                 │
│  transfer/withdraw:                                              │
│    → withdraw.Cash = pfloat.CashFloor(cashRemaining)            │
│    → export int64(pfloat.CashFloor(...))                        │
│                                                                 │
│  Kết luận: KHÔNG floor ở bất kỳ bước trung gian nào.            │
│  Chỉ floor KHI THANH TOÁN cho user.                              │
└─────────────────────────────────────────────────────────────────┘
```

**Các nguồn tiền khác (không bị ảnh hưởng bởi feature này):**
- `EventBonus.Amount` — admin nhập số nguyên trực tiếp, không qua tính toán CashPer*
- `withdraw.Cash` (user tự rút) — frontend gửi số nguyên
- `CashTax` — đã dùng `math.Round`, luôn integer

---

## 5. Functional Requirements

### FR-001: Admin nhập CashPer* giá trị thập phân

**Priority:** Must Have

**Description:**
Admin có thể setup `CashPerView`, `CashPerLike`, `CashPerComment` với giá trị từ 0.1 đến bất kỳ, step 0.1 (1 chữ số thập phân).

**Acceptance Criteria:**
- [ ] Admin nhập CashPerView = 0.5 → hệ thống chấp nhận
- [ ] Admin nhập CashPerView = 0.55 → hệ thống reject (quá 1 chữ số thập phân)
- [ ] Admin nhập CashPerView = 0 → chấp nhận (vô hiệu metric đó)
- [ ] Admin nhập CashPerView = -1 → reject
- [ ] Validation message rõ ràng: "Giá trị phải là bội số của 0.1"

**File cần cập nhật:**

| File | Thay đổi |
|------|----------|
| `pkg/admin/model/request/event_schema.go` | Thêm validation cho `CashReward`: >= 0, step 0.1 (max 1 decimal) |

---

### FR-002: Utility function `CashFloor` + áp dụng tại bước thanh toán

**Priority:** Must Have

**Description:**
Tạo function `CashFloor(v float64) float64` trong package `internal/util/pfloat` (đã có sẵn utility float). Function này wrap `math.Floor` — khi cần đổi rounding logic sau này chỉ sửa 1 chỗ.

**Nguyên tắc: KHÔNG làm tròn ở bất kỳ bước trung gian nào.** Giá trị thập phân được giữ nguyên xuyên suốt từ reward → cashflow → statistic → reconciliation. Chỉ làm tròn (floor) **duy nhất khi thực hiện thanh toán cho user** (transfer/withdraw).

**Lý do:**
- Giữ độ chính xác tối đa trong tính toán nội bộ
- Tránh mất mát tích lũy khi floor nhiều lần
- Chỉ mất tối đa 0.9đ tại thời điểm user thực sự nhận tiền
- VND không có xu → floor chỉ cần thiết khi chuyển thành tiền thật

**Acceptance Criteria:**
- [ ] `pfloat.CashFloor(500.5)` = 500, `pfloat.CashFloor(2.1)` = 2, `pfloat.CashFloor(500.0)` = 500
- [ ] `CashPerView=0.5, views=1001` → `reward.Cash = 500.5` (giữ nguyên thập phân)
- [ ] `CashMilestone=50000` → `reward.Cash = 50000.0` (không thay đổi)
- [ ] Downstream giữ nguyên thập phân: cashflow value = 500.5, user statistic = float64
- [ ] Chỉ khi thanh toán: `withdraw.Cash = pfloat.CashFloor(cashRemaining)` = 500
- [ ] Export int64: `int64(pfloat.CashFloor(...))` — floor trước khi cast

**Files cần cập nhật:**

| File | Thay đổi |
|------|----------|
| `internal/util/pfloat/float.go` | Thêm `func CashFloor(v float64) float64 { return math.Floor(v) }` |
| Transfer/withdraw service | `pfloat.CashFloor()` tại bước tính `withdraw.Cash` khi thanh toán cho user |
| Export service (int64 cast) | `int64(pfloat.CashFloor(...))` trước khi cast float64 → int64 |

**Tại sao KHÔNG floor ở nguồn sinh cash (reward)?**

Vì floor sớm sẽ gây mất tiền tích lũy. Ví dụ:
- User có 10 rewards, mỗi cái `CashPerView=0.5, views=1001` → mỗi reward = 500.5đ
- Nếu floor tại nguồn: 10 × 500 = 5,000đ (mất 5đ)
- Nếu floor tại thanh toán: floor(10 × 500.5) = floor(5,005) = 5,005đ (không mất gì)
- Trường hợp lẻ hơn: floor(5,005.5) = 5,005đ (chỉ mất 0.5đ — 1 lần duy nhất)

---

### FR-003: Reconciliation float comparison (Code Quality)

**Priority:** Must Have (upgraded từ Should Have vì data giờ có thập phân)

**Description:**
Hiện tại reconciliation dùng `!=` để so sánh 2 giá trị `float64`. Vì data giờ giữ nguyên thập phân xuyên suốt, **bắt buộc** phải dùng so sánh có tolerance thay vì `!=` để tránh false rejection do floating-point precision.

**Acceptance Criteria:**
- [ ] Thay `!=` bằng so sánh có tolerance (`math.Abs(a-b) > epsilon`) hoặc `pfloat.CashFloor()` cả 2 vế
- [ ] Existing integer data không bị ảnh hưởng
- [ ] Data thập phân (ví dụ 500.5 vs 500.5) compare đúng

**File cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `pkg/admin/service/reconciliation_running.go` | L226 | Dùng tolerance comparison hoặc `pfloat.CashFloor()` cả 2 vế |

---

## 6. Non-Functional Requirements

### NFR-001: Monetary Rounding Rules (DATA PRECISION)

**Priority:** Must Have

**Description:**
Quy tắc rounding cho hệ thống monetary:

```
┌──────────────────────────────────────────────────────────────┐
│                 MONETARY ROUNDING RULES                      │
│                                                              │
│  Nguyên tắc: KHÔNG làm tròn ở bất kỳ bước trung gian nào.  │
│  Chỉ floor KHI THANH TOÁN cho user qua pfloat.CashFloor().  │
│  Lý do: Giữ chính xác tối đa, chỉ mất tối đa 0.9đ khi     │
│  user thực sự nhận tiền.                                     │
│                                                              │
│  1. CashPerView/Like/Comment: cho phép 1 decimal (0.1→0.9)  │
│  2. Thành phần trung gian (TotalCashView...): GIỮ NGUYÊN    │
│  3. reward.Cash (by-statistic): GIỮ NGUYÊN thập phân        │
│  4. reward.Cash (milestone): GIỮ NGUYÊN                     │
│  5. cashflow, statistic, reconciliation: GIỮ NGUYÊN float64 │
│  6. transfer/withdraw (THANH TOÁN): pfloat.CashFloor() ↓    │
│  7. export int64: pfloat.CashFloor() trước khi cast ↓       │
│  8. Tax: giữ nguyên math.Round() (convention thuế)           │
│  9. Bonus: Amount do admin nhập, không liên quan feature     │
│                                                              │
│  Tất cả floor đều qua pfloat.CashFloor().                   │
│  Đổi logic rounding → sửa 1 function duy nhất.              │
└──────────────────────────────────────────────────────────────┘
```

**Rationale:**
- VND không có đơn vị xu → số thập phân vô nghĩa khi thanh toán thực tế
- **Floor (DOWN)** là chuẩn tài chính: không trả thừa
- Giữ thập phân xuyên suốt → tránh mất tiền tích lũy (floor nhiều lần mất nhiều hơn)
- float64 (IEEE 754) đủ precision cho monetary values VND
- Chỉ floor 1 lần tại cuối cùng → user chỉ mất tối đa 0.9đ

**Acceptance Criteria:**
- [ ] `reward.Cash` giữ nguyên giá trị thập phân (ví dụ 500.5)
- [ ] Intermediate values (TotalCashView, TotalCashLike, cashflow.Value, statistic...) giữ nguyên float64
- [ ] Chỉ `transfer/withdraw` mới gọi `pfloat.CashFloor()` — thanh toán cho user
- [ ] Export int64 gọi `pfloat.CashFloor()` trước khi cast
- [ ] Tax vẫn dùng `math.Round` (convention thuế khác với payout)
- [ ] Mọi chỗ floor cash đều gọi `pfloat.CashFloor()` — không gọi `math.Floor` trực tiếp

---

### NFR-002: Backward Compatibility

**Priority:** Must Have

**Description:**
Thay đổi phải tương thích ngược — event schemas hiện tại với CashPer* = số nguyên phải hoạt động bình thường.

**Acceptance Criteria:**
- [ ] Schema CashPerView=1 → reward.Cash = 1001.0 (giữ nguyên, vẫn đúng)
- [ ] Schema CashPerView=10 → không bị ảnh hưởng
- [ ] Existing data trong DB không cần migration
- [ ] Thanh toán cho existing data: `pfloat.CashFloor(1001.0) = 1001` (backward compatible)

---

### NFR-003: Performance

**Priority:** Should Have

**Description:**
`math.Floor()` thêm vào không ảnh hưởng hiệu năng đáng kể.

**Acceptance Criteria:**
- [ ] `pfloat.CashFloor()` là O(1) — negligible overhead
- [ ] Không thêm query hoặc aggregate step mới

---

## 7. Epics

### EPIC-001: Validation & Admin Setup

**Description:** Cho phép admin nhập CashPer* với 1 decimal, validate input.

**Functional Requirements:** FR-001

**Story Count Estimate:** 1

**Priority:** Must Have

---

### EPIC-002: CashFloor Utility + Floor tại thanh toán

**Description:** Tạo `pfloat.CashFloor()` utility function, áp dụng tại bước transfer/withdraw và export int64 cast. Không floor ở bất kỳ bước trung gian nào.

**Functional Requirements:** FR-002

**Story Count Estimate:** 1

**Priority:** Must Have

---

### EPIC-003: Reconciliation Float Comparison

**Description:** Fix float `!=` comparison trong reconciliation — bắt buộc vì data giờ có thập phân.

**Functional Requirements:** FR-003

**Story Count Estimate:** 1

**Priority:** Must Have

---

## 8. Traceability Matrix

| Epic | FRs | NFRs | Story Est. | Priority |
|------|-----|------|------------|----------|
| EPIC-001: Validation & Admin Setup | FR-001 | NFR-002 | 1 | Must |
| EPIC-002: CashFloor Utility + Floor tại thanh toán | FR-002 | NFR-001, NFR-003 | 1 | Must |
| EPIC-003: Reconciliation Float Comparison | FR-003 | — | 1 | Must |
| **Total** | **3 FRs** | **3 NFRs** | **~3 stories** | |

---

## 9. Dependencies

**Internal:**
- Backend vcreator (`accesstrade-projects/vcreator/backend`)
- Admin frontend (schema setup form — thêm `step={0.1}` cho InputNumber)

**External:**
- Không có — thay đổi hoàn toàn nội bộ backend

---

## 10. Assumptions

1. Existing data trong DB không cần migration (floor chỉ thêm tại bước thanh toán)
2. Frontend Green Creator cần hiển thị tiền format integer (floor giá trị hiển thị nếu cần)
3. Admin UI (Ant Design) dùng `step={0.1}` + `precision={1}` cho InputNumber
4. Go `math.Floor` truncate về phía âm vô cùng — với số dương, equivalent với bỏ phần thập phân
5. IEEE 754 float64 đủ precision cho monetary values VND (exact integer đến 2^53)
6. MongoDB `$sum` aggregation trên float64 values đủ chính xác cho use case này
7. Hệ thống chấp nhận các giá trị trung gian (balance, statistic) là float64 có thập phân

---

## 11. Out of Scope

- Chuyển đổi toàn bộ monetary system sang int64 (dài hạn)
- MongoDB Decimal128 migration
- Thay đổi tax calculation logic (đã có math.Round)
- Hỗ trợ hơn 1 chữ số thập phân (0.01đ)
- Migration script cho existing data
- Floor ở bước trung gian (reward, cashflow, statistic, reconciliation) — KHÔNG floor ở đây

---

## 12. Resolved Questions

| # | Câu hỏi | Kết luận | Lý do |
|---|---------|---------|-------|
| 1 | Floor ở đâu? | **Chỉ khi thanh toán** (transfer/withdraw) + export int64 cast | Giữ thập phân xuyên suốt, chỉ floor khi user thực sự nhận tiền. Tránh mất tiền tích lũy. |
| 2 | Cần migration script cho data cũ? | **Không cần** | Data hiện tại = integer × integer = integer. Thêm floor tại thanh toán không ảnh hưởng. |
| 3 | Admin UI step 0.1 có ảnh hưởng UX? | **Tích cực** | Thêm `step={0.1}` + `precision={1}` cho InputNumber. Admin vẫn nhập số nguyên bình thường. |
| 4 | Reconciliation float `!=` có bị lỗi? | **Bắt buộc fix** | Data giờ có thập phân → `!=` sẽ gặp vấn đề floating-point precision. Phải dùng tolerance comparison. |
| 5 | reward.Cash có cần floor? | **KHÔNG** | Giữ nguyên thập phân. Floor sớm gây mất tiền tích lũy (10 rewards × 0.5đ lost = 5đ). |
| 6 | Downstream có cần floor? | **KHÔNG** | Giữ float64 xuyên suốt. Chỉ floor tại bước cuối cùng khi thanh toán. |
| 7 | Frontend hiển thị số lẻ? | **Cần xử lý hiển thị** | Frontend format integer khi hiển thị cho user. Backend trả float64 — frontend tự format. |

---

## 13. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Floor khi thanh toán gây user mất tối đa 0.9đ | Low | VND không có xu, 0.9đ negligible. Chỉ mất 1 lần tại thanh toán (không tích lũy). |
| Floating-point precision khi aggregate nhiều giá trị lẻ | Low | float64 có 15-17 significant digits — đủ cho VND. MongoDB `$sum` cũng dùng double. |
| Frontend/API hiển thị số lẻ cho user | Medium | Frontend cần format integer khi hiển thị cash. Kiểm tra tất cả cash display points. |
| Reconciliation `!=` fail với data thập phân | High | FR-003 bắt buộc fix — dùng tolerance comparison. |
| Ai đó sau này thêm nguồn cash mới | Medium | `pfloat.CashFloor()` dễ grep/audit. Document rõ nguyên tắc "chỉ floor khi thanh toán". |

---

## Appendix A: Tại sao KHÔNG floor ở bước trung gian

**PRD v2.1 đề xuất floor tại nguồn sinh cash (reward.Cash).** v3.0 thay đổi: **không floor ở bất kỳ bước trung gian nào**, chỉ floor khi thanh toán.

**Lý do:**
- Floor sớm gây mất tiền tích lũy. Ví dụ: 10 rewards × floor(500.5) = 10 × 500 = 5,000đ. Nhưng floor(10 × 500.5) = floor(5,005) = 5,005đ. User mất 5đ thay vì 0đ.
- Giữ thập phân xuyên suốt đảm bảo aggregate chính xác hơn
- Chỉ cần floor 1 lần tại cuối cùng → user chỉ mất tối đa 0.9đ

| Bước | Hành động | Lý do |
|------|-----------|-------|
| `reward.Cash` (nguồn) | GIỮ NGUYÊN thập phân | Không mất tiền tích lũy |
| `cashflow.Value` | GIỮ NGUYÊN | Nhận từ reward, giữ float64 |
| `UserStatistic.TotalCash*` | GIỮ NGUYÊN | Aggregate float64, chưa cần tròn |
| `reconciliation.TotalCash` | GIỮ NGUYÊN | So sánh bằng tolerance (FR-003) |
| `transfer/withdraw` | **FLOOR** qua `pfloat.CashFloor()` | Thanh toán thực tế cho user |
| `export int64 cast` | **FLOOR** qua `pfloat.CashFloor()` | Cast float64 → int64 cần tròn |

---

## Appendix B: Code Impact Summary (Updated v3.0)

**Total files cần thay đổi: ~4-5 files (tùy codebase)**

| # | File | Thay đổi | Effort | Priority |
|---|------|----------|--------|----------|
| 1 | `internal/util/pfloat/float.go` | Thêm `CashFloor()` function | S | Must |
| 2 | `pkg/admin/model/request/event_schema.go` | Thêm validation CashPer*: >= 0, step 0.1 | S | Must |
| 3 | Transfer/withdraw service | `pfloat.CashFloor()` khi tính tiền thanh toán cho user | S | Must |
| 4 | Export service (int64 cast) | `int64(pfloat.CashFloor(...))` trước khi cast | S | Must |
| 5 | `pkg/admin/service/reconciliation_running.go` | Tolerance comparison thay `!=` | S | Must |

**So với v2.1:** Bỏ floor tại `event_schema.go` (3 chỗ) và `schedule.go` (1 chỗ). Thêm floor tại transfer/withdraw và export.

---

*Generated by BMAD Method v6 - Product Manager*
*Date: 2026-04-01 | Updated: 2026-04-09*
*Changelog:*
*- v3.0 — Thay đổi chiến lược: KHÔNG floor ở bất kỳ bước trung gian nào. Chỉ floor khi thanh toán cho user (transfer/withdraw). Reconciliation nâng lên Must Have.*
*- v2.1 — Thêm `pfloat.CashFloor()` utility function, cover milestone reward (3 chỗ).*
*- v2.0 — Simplified based on data flow analysis. Reduced scope from 28 locations to source-only.*
