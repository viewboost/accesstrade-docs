# PRD: Hỗ trợ thưởng by-statistic giá trị thập phân (0.1đ - 0.9đ)

**Project:** Gen-Green (VCreator)
**Date:** 2026-04-01
**Author:** Product Manager
**Status:** Draft
**Version:** 1.0

---

## 1. Executive Summary

Cho phép Admin setup thưởng by-statistic với giá trị thập phân 1 chữ số (0.1đ → 0.9đ) cho `CashPerView`, `CashPerLike`, `CashPerComment`. Hiện tại hệ thống dùng `float64` mà **không có rounding** nên khi nhập giá trị lẻ sẽ gây sai lệch tích lũy ở reward, balance, reconciliation và export.

**Thay đổi cốt lõi:** Thêm rounding rule — chỉ round **1 lần duy nhất** tại kết quả cuối (`reward.Cash`), dùng `math.Floor` (round DOWN) vì đây là tiền thực — không trả user nhiều hơn số tiền thực có. Giữ nguyên precision ở các thành phần trung gian.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Cho phép setup thưởng linh hoạt hơn (0.1đ/view thay vì chỉ số nguyên) | Admin có thể tạo schema với CashPer* = 0.1 → 0.9 |
| 2 | Đảm bảo chính xác tài chính khi dùng giá trị lẻ | Chênh lệch balance vs aggregate = 0đ (exact) |
| 3 | Reconciliation không bị reject sai do float drift | 0% false rejection từ float comparison |
| 4 | Export/hiển thị tiền luôn là số nguyên VND | UI và Excel không hiển thị số thập phân cho cash fields |

---

## 3. User Personas

| Persona | Vai trò | Nhu cầu |
|---------|---------|---------|
| **Admin/Staff** | Setup event schema, reconciliation, transfer | Nhập CashPerView = 0.5đ, reconciliation chạy đúng |
| **Creator (User)** | Xem balance, rút tiền | Số dư hiển thị tròn, rút hết được |
| **Finance/Kế toán** | Đối soát, export báo cáo | Tổng tiền khớp, export Excel không lẻ |

---

## 4. Functional Requirements

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
- `pkg/admin/model/request/event_schema.go` — thêm validation rule

---

### FR-002: Reward calculation round kết quả cuối

**Priority:** Must Have

**Description:**
Khi tính reward by-statistic, các thành phần trung gian (`TotalCashView`, `TotalCashLike`, `TotalCashComment`) giữ nguyên precision. Chỉ round **1 lần** tại `reward.Cash` (tổng cuối cùng) về số nguyên.

**Acceptance Criteria:**
- [ ] `CashPerView=0.5, views=1001` → `TotalCashView=500.5` (giữ nguyên) → `reward.Cash = math.Floor(500.5) = 500`
- [ ] `CashPerView=0.3, views=10` → `TotalCashView=3.0` → `reward.Cash = 3`
- [ ] `CashPerView=0.7, views=3` → `TotalCashView=2.1` → `reward.Cash = math.Floor(2.1) = 2`
- [ ] Nhiều thành phần: `TotalCashView=500.5 + TotalCashLike=100.3 + TotalCashComment=50.7` → `reward.Cash = math.Floor(651.5) = 651`

**Files cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `internal/service/event_schema.go` | L284 | `reward.Cash = math.Floor(...)` trong `UpdateRewardTypeByStatisticContent()` |
| `internal/service/event_schema.go` | L689 | `reward.Cash = math.Floor(...)` trong `CheckPassSchemaWithContent()` |

---

### FR-003: Cash flow balance không drift

**Priority:** Must Have

**Description:**
Khi cộng dồn balance trong cash flow, `newBalance` phải được round về số nguyên để tránh sai lệch tích lũy qua nhiều transactions.

**Acceptance Criteria:**
- [ ] `oldBalance=1000, value=500.5` → `newBalance = math.Floor(1500.5) = 1500` (không phải 1500.4999...)
- [ ] Sau 1000 transactions liên tục với value lẻ → balance vẫn là số nguyên
- [ ] `GetRemaining()` và `GetPartnerRemaining()` trả về giá trị đã floor

**File cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `internal/service/cashflow.go` | L61 | `newBalance := math.Floor(oldBalance + payload.Value)` |

---

### FR-004: Reconciliation so sánh cash không mismatch

**Priority:** Must Have

**Description:**
Khi reconciliation recheck cash, phải round cả 2 vế trước khi so sánh, tránh false rejection do float drift.

**Acceptance Criteria:**
- [ ] `totalCashPending=500.5000001` vs `item.TotalCash=500.5` → pass (không reject sai)
- [ ] Reconciliation items với cash lẻ vẫn được process bình thường
- [ ] Log warning nếu chênh lệch > 1đ trước floor (phát hiện lỗi thật)

**Files cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `pkg/admin/service/reconciliation_running.go` | L226 | `math.Floor(totalCashPending) != math.Floor(item.TotalCash)` |
| `pkg/admin/service/reconciliation_processing.go` | L203 | `TotalCash: math.Floor(item.TotalCashPending)` |

---

### FR-005: Export Excel hiển thị số nguyên

**Priority:** Should Have

**Description:**
Tất cả export CSV/Excel liên quan đến tiền phải hiển thị số nguyên VND, không hiển thị phần thập phân.

**Acceptance Criteria:**
- [ ] Export event analytic: cash columns hiển thị "500" không phải "500.5"
- [ ] Export user partner: cash columns hiển thị số nguyên
- [ ] Export transfer: cash, tax, actualCash hiển thị số nguyên

**Files cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `pkg/admin/service/export_event_analytic.go` | L325-328 | `int64(math.Floor(r.Cash.Pending))` thay vì `int64(r.Cash.Pending)` |
| `pkg/admin/service/export_user_partner.go` | L173-177 | `int64(math.Floor(...))` thay vì `int64(...)` |
| `pkg/admin/service/export_transfer.go` | L195-197 | `FormatFloat(..., 'f', 0, 64)` thay vì `'f', -1` |

---

### FR-006: User statistic hiển thị số nguyên

**Priority:** Should Have

**Description:**
`UserStatistic` được lưu trong DB và hiển thị cho user phải là số nguyên tròn.

**Acceptance Criteria:**
- [ ] `CashTotal`, `CashRemaining`, `TotalCashPending`, `TotalCashCompleted` luôn là số nguyên sau khi update
- [ ] UI hiển thị "10,500đ" không phải "10,500.5đ"

**File cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `internal/service/user.go` | L219-223 | Floor `TotalCashPending`, `TotalCashCompleted`, `CashTotal` |

---

### FR-007: Float→Int cast an toàn

**Priority:** Should Have

**Description:**
Mọi chỗ cast `float64 → int64` cho statistic counts phải dùng `math.Round()` trước khi cast để tránh truncation.

**Acceptance Criteria:**
- [ ] `int64(math.Floor(99.999))` = 99, `int64(math.Floor(100.0))` = 100 — consistent với floor policy
- [ ] Áp dụng cho TotalLike, TotalComment, TotalView trong reward statistic

**Files cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `internal/service/event_schema.go` | L255, 257, 259 | `int64(math.Floor(totalLike))` trong `UpdateRewardTypeByStatisticContent()` |
| `internal/service/event_schema.go` | ~L660 | Same trong `CheckPassSchemaWithContent()` |

---

### FR-008: Transfer round cashRemaining

**Priority:** Should Have

**Description:**
Khi auto-transfer tạo withdraw cho user, `cashRemaining` phải round trước khi dùng.

**Acceptance Criteria:**
- [ ] User có balance 10500.5 → transfer withdraw amount = `math.Floor(10500.5)` = 10500 (round DOWN, không bao giờ rút quá số dư)
- [ ] User còn dư tối đa 0.9đ → gộp vào lần transfer sau
- [ ] Không tạo withdraw với cash = 0đ (khi cashRemaining < 1)

**File cần cập nhật:**

| File | Dòng | Thay đổi |
|------|------|----------|
| `pkg/admin/service/transfer_processing.go` | L82-90 | `math.Floor(cashRemaining)` trước khi tạo withdraw (DOWN — tránh rút quá số dư) |

---

## 5. Non-Functional Requirements

### NFR-001: Monetary Rounding Rules (DATA PRECISION)

**Priority:** Must Have

**Description:**
Quy tắc rounding cho toàn bộ hệ thống monetary:

```
┌──────────────────────────────────────────────────────────────┐
│                 MONETARY ROUNDING RULES                      │
│                                                              │
│  Nguyên tắc tổng: Khi ra tới cash → Floor (round DOWN) hết  │
│  Lý do: Tiền thực — không trả user nhiều hơn số có.         │
│                                                              │
│  1. CashPerView/Like/Comment: cho phép 1 decimal (0.1→0.9)  │
│  2. Thành phần trung gian (TotalCashView...): KHÔNG floor    │
│  3. reward.Cash (final sum): math.Floor() → số nguyên ↓     │
│  4. cash_flows.newBalance: math.Floor() → số nguyên ↓       │
│  5. UserStatistic.Cash*: math.Floor() → số nguyên ↓         │
│  6. So sánh 2 float cash: floor cả 2 vế trước khi compare  │
│  7. Export/Display: luôn hiển thị số nguyên VND              │
│  8. Tax: giữ nguyên math.Round() hiện tại (tax round gần    │
│     nhất — đây là convention thuế, khác với cash payout)     │
│  9. Transfer cashRemaining: math.Floor() → không rút quá dư │
│                                                              │
│  Floor MỘT LẦN tại điểm final output,                       │
│  KHÔNG floor từng thành phần trung gian.                     │
└──────────────────────────────────────────────────────────────┘
```

**Rationale:**
- VND không có đơn vị xu → số thập phân vô nghĩa ở kết quả cuối
- **Floor (DOWN)** là chuẩn tài chính: không trả thừa, phần lẻ tích lũy dần và được gộp khi đủ 1đ
- float64 (IEEE 754) không chính xác 100% → cần floor tại output
- Floor 1 lần tại final sum để giảm thiểu accumulated error
- Tax giữ `math.Round` vì convention thuế round gần nhất (khác với payout)

**Acceptance Criteria:**
- [ ] Không có cash field nào tại output level (reward.Cash, newBalance, UserStatistic) có giá trị lẻ
- [ ] Intermediate values (TotalCashView, TotalCashLike...) được phép lẻ
- [ ] Mọi comparison giữa 2 cash values đều floor trước
- [ ] Tax vẫn dùng `math.Round` (convention thuế khác với payout)

---

### NFR-002: Backward Compatibility

**Priority:** Must Have

**Description:**
Thay đổi phải tương thích ngược — event schemas hiện tại với CashPer* = số nguyên phải hoạt động bình thường.

**Acceptance Criteria:**
- [ ] Schema CashPerView=1 → reward vẫn tính đúng (1 * views = views)
- [ ] Schema CashPerView=10 → không bị ảnh hưởng bởi rounding
- [ ] Existing data trong DB không cần migration

---

### NFR-003: Performance

**Priority:** Should Have

**Description:**
`math.Round()` thêm vào không ảnh hưởng hiệu năng đáng kể.

**Acceptance Criteria:**
- [ ] `math.Round()` là O(1) — negligible overhead
- [ ] Không thêm query hoặc aggregate step mới
- [ ] Schedule job RunCheckPassSchemaStatistic không chậm hơn quá 1%

---

## 6. Epics

### EPIC-001: Validation & Admin Setup

**Description:** Cho phép admin nhập CashPer* với 1 decimal, validate input.

**Functional Requirements:** FR-001

**Story Count Estimate:** 2

**Priority:** Must Have

---

### EPIC-002: Reward Calculation Rounding

**Description:** Thêm math.Round() tại reward.Cash (final sum) và fix float→int cast.

**Functional Requirements:** FR-002, FR-007

**Story Count Estimate:** 2

**Priority:** Must Have

---

### EPIC-003: Cash Flow & Balance Integrity

**Description:** Round newBalance trong cash flow, round user statistic.

**Functional Requirements:** FR-003, FR-006

**Story Count Estimate:** 2

**Priority:** Must Have

---

### EPIC-004: Reconciliation & Transfer Fix

**Description:** Fix float comparison trong reconciliation, round transfer cashRemaining.

**Functional Requirements:** FR-004, FR-008

**Story Count Estimate:** 3

**Priority:** Must Have

---

### EPIC-005: Export & Display

**Description:** Fix export Excel và hiển thị UI để luôn show số nguyên VND.

**Functional Requirements:** FR-005

**Story Count Estimate:** 2

**Priority:** Should Have

---

## 7. Traceability Matrix

| Epic | FRs | NFRs | Story Est. | Priority |
|------|-----|------|------------|----------|
| EPIC-001: Validation & Admin Setup | FR-001 | NFR-002 | 2 | Must |
| EPIC-002: Reward Calculation Rounding | FR-002, FR-007 | NFR-001, NFR-003 | 2 | Must |
| EPIC-003: Cash Flow & Balance Integrity | FR-003, FR-006 | NFR-001 | 2 | Must |
| EPIC-004: Reconciliation & Transfer Fix | FR-004, FR-008 | NFR-001 | 3 | Must |
| EPIC-005: Export & Display | FR-005 | NFR-001 | 2 | Should |
| **Total** | **8 FRs** | **3 NFRs** | **~11 stories** | |

---

## 8. Prioritization Summary

| Priority | FRs | NFRs | Total |
|----------|-----|------|-------|
| Must Have | 4 (FR-001→004) | 2 (NFR-001, 002) | 6 |
| Should Have | 4 (FR-005→008) | 1 (NFR-003) | 5 |
| Could Have | 0 | 0 | 0 |

---

## 9. Dependencies

**Internal:**
- Backend vcreator (`accesstrade-projects/vcreator/backend`)
- Admin frontend (schema setup form)

**External:**
- Không có — thay đổi hoàn toàn nội bộ backend

---

## 10. Assumptions

1. `math.Round()` (Go standard lib) dùng banker's rounding — đủ chính xác cho VND
2. Existing data trong DB không cần migration (rounding chỉ áp dụng cho new calculations)
3. Frontend Green Creator hiện đã hiển thị tiền dạng format integer — chỉ cần backend trả đúng
4. Admin UI (Ant Design) dùng `step={0.1}` + `precision={1}` cho InputNumber — đã confirm UX tích cực

---

## 11. Out of Scope

- Chuyển đổi toàn bộ monetary system sang int64 (dài hạn)
- MongoDB Decimal128 migration
- Frontend Green Creator UI changes (backend trả đúng là đủ)
- Thay đổi tax calculation logic (đã có math.Round)
- Hỗ trợ hơn 1 chữ số thập phân (0.01đ)
- Migration script cho existing data

---

## 12. Resolved Questions

| # | Câu hỏi | Kết luận | Lý do |
|---|---------|---------|-------|
| 1 | Transfer round UP hay DOWN khi `cashRemaining` lẻ? | **`math.Floor` (DOWN)** | Tránh rút quá số dư → withdraw fail. User còn dư tối đa 0.9đ, gộp lần transfer sau. Pattern chuẩn tài chính. |
| 2 | Cần migration script cho data cũ? | **Không cần** | Data hiện tại = integer × integer = integer → không lẻ. `math.Round(500.0) = 500` không thay đổi kết quả. Verify bằng query: `db.event_rewards.find({$expr:{$ne:["$cash",{$round:"$cash"}]}}).count()` |
| 3 | Admin UI step 0.1 có ảnh hưởng UX? | **Tích cực** | Thêm `step={0.1}` + `precision={1}` cho InputNumber. Admin vẫn nhập số nguyên bình thường. Nút +/- tăng/giảm 0.1 rõ ràng hơn. Thêm tooltip "Hỗ trợ giá trị thập phân (VD: 0.5đ/view)". |

---

## 13. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Floor gây user mất tối đa 0.9đ/reward | Low | VND không có xu, 0.9đ negligible. Phần lẻ tích lũy tự nhiên qua nhiều rewards. |
| Existing data có cash lẻ trong DB | Low | Data cũ = integer × integer = integer. Verify bằng query, không cần migration. |
| Floor liên tục làm user mất tiền tích lũy | Low | Trung bình mất 0.5đ/reward. Với 100 rewards = mất ~50đ — chấp nhận được. Đây là practice chuẩn ngành. |

---

## Appendix A: Rounding Rules Reference (cho Architecture/Tech Spec)

Tài liệu chi tiết về rounding rules được ghi ở **NFR-001** trong PRD này. Khi viết Architecture hoặc Tech Spec, tham chiếu:

> **Xem:** PRD `prd-fractional-reward-2026-04-01.md` → NFR-001: Monetary Rounding Rules

Đây là cách chuẩn để note rounding rules:
- **Business rule** (VND phải tròn, round ở đâu) → **PRD / NFR**
- **Implementation detail** (file nào, dòng nào, dùng hàm gì) → **Architecture / Tech Spec**
- **Data definition** (field nào precision bao nhiêu) → **Data Dictionary** (nếu có)

Trong PRD này đã bao gồm cả 3 level để tiện tham chiếu.

---

## Appendix B: Code Impact Summary

**Total files cần thay đổi: 7**

| # | File | Thay đổi | Effort |
|---|------|----------|--------|
| 1 | `pkg/admin/model/request/event_schema.go` | Thêm validation 1 decimal | S |
| 2 | `internal/service/event_schema.go` | Round `reward.Cash` (2 chỗ) + round int64 cast (6 chỗ) | S |
| 3 | `internal/service/cashflow.go` | Round `newBalance` (1 chỗ) | S |
| 4 | `internal/service/user.go` | Round user statistic totals (4 fields) | S |
| 5 | `pkg/admin/service/reconciliation_running.go` | Round cả 2 vế comparison (1 chỗ) | S |
| 6 | `pkg/admin/service/reconciliation_processing.go` | Round TotalCash (1 chỗ) | S |
| 7 | `pkg/admin/service/transfer_processing.go` | Floor cashRemaining (1 chỗ) | S |
| 8 | `pkg/admin/service/export_event_analytic.go` | Round trước int64 cast (4 chỗ) | S |
| 9 | `pkg/admin/service/export_user_partner.go` | Round trước int64 cast (5 chỗ) | S |
| 10 | `pkg/admin/service/export_transfer.go` | Format precision (3 chỗ) | S |

**Tổng code locations: ~28 chỗ | Tất cả effort: Small**

---

*Generated by BMAD Method v6 - Product Manager*
*Date: 2026-04-01*
