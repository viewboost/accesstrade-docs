# PRD: Hỗ trợ thưởng by-statistic giá trị thập phân (0.1đ - 0.9đ)

**Project:** Gen-Green (VCreator)
**Date:** 2026-04-01
**Author:** Product Manager
**Status:** Draft
**Version:** 2.0

---

## 1. Executive Summary

Cho phép Admin setup thưởng by-statistic với giá trị thập phân 1 chữ số (0.1đ → 0.9đ) cho `CashPerView`, `CashPerLike`, `CashPerComment`. Hiện tại hệ thống dùng `float64` mà **không có rounding** nên khi nhập giá trị lẻ sẽ gây sai lệch tại `reward.Cash`.

**Thay đổi cốt lõi:** Thêm `math.Floor` **1 lần duy nhất** tại nguồn sinh cash — `reward.Cash` (kết quả cuối của by-statistic reward). Toàn bộ downstream (cashflow, user statistic, reconciliation, export, transfer) nhận giá trị đã integer nên **không cần thay đổi**.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Cho phép setup thưởng linh hoạt hơn (0.1đ/view thay vì chỉ số nguyên) | Admin có thể tạo schema với CashPer* = 0.1 → 0.9 |
| 2 | Đảm bảo chính xác tài chính khi dùng giá trị lẻ | Chênh lệch balance vs aggregate = 0đ (exact) |
| 3 | Export/hiển thị tiền luôn là số nguyên VND | UI và Excel không hiển thị số thập phân cho cash fields |

---

## 3. User Personas

| Persona | Vai trò | Nhu cầu |
|---------|---------|---------|
| **Admin/Staff** | Setup event schema, reconciliation, transfer | Nhập CashPerView = 0.5đ, reconciliation chạy đúng |
| **Creator (User)** | Xem balance, rút tiền | Số dư hiển thị tròn, rút hết được |
| **Finance/Kế toán** | Đối soát, export báo cáo | Tổng tiền khớp, export Excel không lẻ |

---

## 4. Data Flow Analysis

Trước khi đọc Functional Requirements, cần hiểu money flow trong hệ thống:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MONEY FLOW (nguồn → downstream)             │
│                                                                 │
│  NGUỒN SINH CASH (chỉ 2 loại):                                 │
│                                                                 │
│  1. By-Statistic reward (CashPer* × count):                    │
│     reward.Cash = TotalCashLike + TotalCashComment              │
│                   + TotalCashView                               │
│     → ĐÂY LÀ CHỖ DUY NHẤT tạo số lẻ khi CashPer* = 0.x      │
│     → CẦN math.Floor() ở đây                                   │
│                                                                 │
│  2. Milestone reward (CashMilestone gán thẳng):                 │
│     reward.Cash = schema.CashReward.CashMilestone               │
│     → Admin nhập số nguyên → không tạo số lẻ                   │
│     → Không cần floor                                           │
│                                                                 │
│  DOWNSTREAM (tự động integer nếu nguồn đã integer):            │
│                                                                 │
│  reward.Cash (integer)                                          │
│    → reconciliation.TotalCash = $sum(reward.Cash) = integer     │
│      → cashflow.Value = TotalCash = integer                     │
│        → newBalance = old + Value = integer                     │
│        → GetRemaining() = $sum(Values) = integer                │
│          → UserStatistic.CashRemaining = integer                │
│          → UserStatistic.TotalCash* = integer                   │
│          → transfer.cashRemaining = integer                     │
│            → withdraw.Cash = integer                            │
│              → export int64(integer) = correct                  │
│                                                                 │
│  Kết luận: Floor TẠI NGUỒN → downstream tự đúng.               │
│  Không cần floor ở 28 chỗ downstream.                           │
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

### FR-002: Reward calculation floor kết quả cuối

**Priority:** Must Have

**Description:**
Khi tính reward by-statistic, các thành phần trung gian (`TotalCashView`, `TotalCashLike`, `TotalCashComment`) giữ nguyên precision. Chỉ floor **1 lần** tại `reward.Cash` (tổng cuối cùng) về số nguyên. Đây là **thay đổi duy nhất** cần thiết cho reward — toàn bộ downstream (cashflow, statistic, reconciliation, export, transfer) nhận giá trị đã integer nên tự động đúng.

**Acceptance Criteria:**
- [ ] `CashPerView=0.5, views=1001` → `TotalCashView=500.5` (giữ nguyên) → `reward.Cash = math.Floor(500.5) = 500`
- [ ] `CashPerView=0.3, views=10` → `TotalCashView=3.0` → `reward.Cash = 3`
- [ ] `CashPerView=0.7, views=3` → `TotalCashView=2.1` → `reward.Cash = math.Floor(2.1) = 2`
- [ ] Nhiều thành phần: `TotalCashView=500.5 + TotalCashLike=100.3 + TotalCashComment=50.7` → `reward.Cash = math.Floor(651.5) = 651`
- [ ] Downstream tự đúng: cashflow value = 651 (integer), user statistic = integer, export = integer

**Files cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `internal/service/event_schema.go` | L284 | `reward.Cash = math.Floor(...)` trong `UpdateRewardTypeByStatisticContent()` |
| `internal/service/event_schema.go` | L689 | `reward.Cash = math.Floor(...)` trong `CheckPassSchemaWithContent()` |

**Tại sao không cần floor ở downstream?**

Vì `reward.Cash` là **nguồn gốc duy nhất** sinh ra số lẻ khi dùng CashPer* thập phân. Sau khi floor ở đây:
- `cashflow.Value` = `reward.Cash` (đã integer) → `newBalance` = integer + integer = integer
- `GetRemaining()` = MongoDB `$sum` của integer values = integer
- `UserStatistic.TotalCash*` = aggregate của integer `reward.Cash` = integer
- `reconciliation.TotalCash` = aggregate của integer `reward.Cash` = integer
- `transfer.cashRemaining` = `GetPartnerRemaining()` = integer
- `export int64(float64)` với float64 = integer → cast chính xác

---

### FR-003: Reconciliation float comparison (Code Quality)

**Priority:** Should Have

**Description:**
Hiện tại reconciliation dùng `!=` để so sánh 2 giá trị `float64`. Dù sau khi fix FR-002 data sẽ là integer (so sánh đúng), đây vẫn là **bad practice** — bất kỳ thay đổi nào trong tương lai tạo ra cash lẻ sẽ gây false rejection. Nên fix cho defensive.

**Acceptance Criteria:**
- [ ] Thay `!=` bằng so sánh có tolerance hoặc floor cả 2 vế
- [ ] Existing integer data không bị ảnh hưởng

**File cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `pkg/admin/service/reconciliation_running.go` | L226 | `math.Floor(totalCashPending) != math.Floor(item.TotalCash)` |

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
│  Nguyên tắc: Floor TẠI NGUỒN, không floor downstream.       │
│  Lý do: Tiền thực — không trả user nhiều hơn số có.         │
│                                                              │
│  1. CashPerView/Like/Comment: cho phép 1 decimal (0.1→0.9)  │
│  2. Thành phần trung gian (TotalCashView...): KHÔNG floor    │
│  3. reward.Cash (final sum): math.Floor() → số nguyên ↓     │
│     → Đây là điểm DUY NHẤT cần floor cho feature này        │
│  4. Downstream (cashflow, statistic, reconciliation,         │
│     export, transfer): KHÔNG CẦN floor — nhận integer        │
│     từ reward.Cash nên tự đúng                               │
│  5. Tax: giữ nguyên math.Round() hiện tại (convention thuế)  │
│  6. Milestone: CashMilestone gán thẳng, admin nhập integer   │
│  7. Bonus: Amount do admin nhập, không liên quan feature     │
│                                                              │
│  Floor MỘT LẦN tại nguồn sinh cash,                         │
│  KHÔNG cần floor ở mọi downstream.                           │
└──────────────────────────────────────────────────────────────┘
```

**Rationale:**
- VND không có đơn vị xu → số thập phân vô nghĩa ở kết quả cuối
- **Floor (DOWN)** là chuẩn tài chính: không trả thừa
- `reward.Cash` là nguồn gốc duy nhất tạo số lẻ khi dùng CashPer* decimal
- Downstream chỉ cộng/trừ/aggregate integer → kết quả luôn integer
- float64 (IEEE 754) biểu diễn chính xác integer đến 2^53 — đủ cho VND

**Acceptance Criteria:**
- [ ] `reward.Cash` (by-statistic) luôn là số nguyên sau floor
- [ ] Intermediate values (TotalCashView, TotalCashLike...) được phép lẻ
- [ ] Tax vẫn dùng `math.Round` (convention thuế khác với payout)
- [ ] Downstream không cần thay đổi code

---

### NFR-002: Backward Compatibility

**Priority:** Must Have

**Description:**
Thay đổi phải tương thích ngược — event schemas hiện tại với CashPer* = số nguyên phải hoạt động bình thường.

**Acceptance Criteria:**
- [ ] Schema CashPerView=1 → reward vẫn tính đúng (`math.Floor(1001.0) = 1001`)
- [ ] Schema CashPerView=10 → không bị ảnh hưởng bởi rounding
- [ ] Existing data trong DB không cần migration

---

### NFR-003: Performance

**Priority:** Should Have

**Description:**
`math.Floor()` thêm vào không ảnh hưởng hiệu năng đáng kể.

**Acceptance Criteria:**
- [ ] `math.Floor()` là O(1) — negligible overhead
- [ ] Không thêm query hoặc aggregate step mới
- [ ] Chỉ thêm 2 dòng code trong toàn bộ codebase

---

## 7. Epics

### EPIC-001: Validation & Admin Setup

**Description:** Cho phép admin nhập CashPer* với 1 decimal, validate input.

**Functional Requirements:** FR-001

**Story Count Estimate:** 1

**Priority:** Must Have

---

### EPIC-002: Reward Calculation Floor

**Description:** Thêm `math.Floor()` tại `reward.Cash` — 2 dòng code duy nhất cần thay đổi.

**Functional Requirements:** FR-002

**Story Count Estimate:** 1

**Priority:** Must Have

---

### EPIC-003: Reconciliation Code Quality

**Description:** Fix float `!=` comparison trong reconciliation — defensive, không bắt buộc cho feature nhưng nên làm.

**Functional Requirements:** FR-003

**Story Count Estimate:** 1

**Priority:** Should Have

---

## 8. Traceability Matrix

| Epic | FRs | NFRs | Story Est. | Priority |
|------|-----|------|------------|----------|
| EPIC-001: Validation & Admin Setup | FR-001 | NFR-002 | 1 | Must |
| EPIC-002: Reward Calculation Floor | FR-002 | NFR-001, NFR-003 | 1 | Must |
| EPIC-003: Reconciliation Code Quality | FR-003 | — | 1 | Should |
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

1. Existing data trong DB không cần migration (rounding chỉ áp dụng cho new calculations)
2. Frontend Green Creator hiện đã hiển thị tiền dạng format integer — chỉ cần backend trả đúng
3. Admin UI (Ant Design) dùng `step={0.1}` + `precision={1}` cho InputNumber
4. Go `math.Floor` truncate về phía âm vô cùng — với số dương, equivalent với bỏ phần thập phân
5. IEEE 754 float64 biểu diễn chính xác integer đến 2^53 (~9 × 10^15) — đủ cho mọi monetary value VND
6. MongoDB `$sum` aggregation trên các integer-valued float64 trả về exact integer

---

## 11. Out of Scope

- Chuyển đổi toàn bộ monetary system sang int64 (dài hạn)
- MongoDB Decimal128 migration
- Frontend Green Creator UI changes (backend trả đúng là đủ)
- Thay đổi tax calculation logic (đã có math.Round)
- Hỗ trợ hơn 1 chữ số thập phân (0.01đ)
- Migration script cho existing data
- Floor ở downstream (cashflow, statistic, export, transfer) — không cần vì nguồn đã integer

---

## 12. Resolved Questions

| # | Câu hỏi | Kết luận | Lý do |
|---|---------|---------|-------|
| 1 | Cần floor ở bao nhiêu chỗ? | **2 chỗ** (reward.Cash) | Trace data flow cho thấy reward.Cash là nguồn duy nhất sinh số lẻ. Downstream nhận integer nên tự đúng. Không cần floor ở 28 chỗ như plan ban đầu. |
| 2 | Cần migration script cho data cũ? | **Không cần** | Data hiện tại = integer × integer = integer → `math.Floor(500.0) = 500` không thay đổi kết quả. |
| 3 | Admin UI step 0.1 có ảnh hưởng UX? | **Tích cực** | Thêm `step={0.1}` + `precision={1}` cho InputNumber. Admin vẫn nhập số nguyên bình thường. |
| 4 | Reconciliation float `!=` có bị lỗi? | **Không bắt buộc fix** nhưng nên | Dù data integer → compare đúng, nhưng `!=` cho float64 là bad practice. Fix cho defensive. |
| 5 | Milestone reward có cần floor? | **Không** | `CashMilestone` gán thẳng từ admin input (số nguyên), không qua tính toán CashPer*. |
| 6 | Bonus, withdraw, export có cần floor? | **Không** | Tất cả downstream nhận integer từ reward.Cash. `$sum(integers) = integer`, `int64(integer) = correct`. |

---

## 13. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Floor gây user mất tối đa 0.9đ/reward | Low | VND không có xu, 0.9đ negligible. Practice chuẩn ngành. |
| Existing data có cash lẻ trong DB | Low | Data cũ = integer × integer = integer. Verify bằng query: `db.event_rewards.find({$expr:{$ne:["$cash",{$round:"$cash"}]}}).count()` |
| Ai đó sau này thêm nguồn cash mới không floor | Medium | Reconciliation `!=` fix (FR-003) sẽ catch. Document rounding rule trong code comment. |

---

## Appendix A: Tại sao KHÔNG cần floor ở downstream

**PRD v1.0 đề xuất floor ở 28 chỗ across 10 files.** Sau khi trace data flow, xác nhận chỉ cần 2 chỗ. Đây là lý do cho từng nhóm bị loại:

| Nhóm | PRD v1.0 đề xuất | Lý do loại |
|------|-------------------|------------|
| `cashflow.newBalance` | `math.Floor(oldBalance + value)` | `value` = `reward.Cash` đã integer → sum integer = integer |
| `UserStatistic.TotalCash*` | Floor 4 fields | Aggregate từ `reward.Cash` (integer) + `bonus.Amount` (admin nhập integer) = integer |
| `UserPartnerStatistic` | Floor 4 fields | Tương tự UserStatistic |
| `reconciliation_processing.TotalCash` | `math.Floor(item.TotalCashPending)` | Aggregate từ `reward.Cash` (integer) = integer |
| `transfer.cashRemaining` | `math.Floor(cashRemaining)` | `GetPartnerRemaining()` = `$sum` integer cashflow values = integer |
| Export int64 cast (3 files) | `int64(math.Floor(...))` | `int64(500.0) = 500` — cast integer float64 về int64 chính xác |
| Float→int64 statistic cast | `int64(math.Floor(totalLike))` | `totalLike` là count từ DB, luôn integer sẵn |

---

## Appendix B: Code Impact Summary (Updated)

**Total files cần thay đổi: 2 (Must Have) + 1 (Should Have)**

| # | File | Thay đổi | Effort | Priority |
|---|------|----------|--------|----------|
| 1 | `pkg/admin/model/request/event_schema.go` | Thêm validation CashPer*: >= 0, step 0.1 | S | Must |
| 2 | `internal/service/event_schema.go` | `math.Floor(reward.Cash)` — 2 dòng | S | Must |
| 3 | `pkg/admin/service/reconciliation_running.go` | Floor cả 2 vế trước `!=` — 1 dòng | S | Should |

**Tổng code locations: 4 dòng | So với v1.0: giảm từ 28 chỗ / 10 files → 4 chỗ / 3 files**

---

*Generated by BMAD Method v6 - Product Manager*
*Date: 2026-04-01 | Updated: 2026-04-06*
*Changelog: v2.0 — Simplified based on data flow analysis. Reduced scope from 28 locations to 4.*
