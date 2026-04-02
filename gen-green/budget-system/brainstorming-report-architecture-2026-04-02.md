# Brainstorming: Kiến trúc Report khi có Cap — Gen-Green

**Date:** 2026-04-02
**Objective:** Thiết kế lại cách report hoạt động khi có cơ chế cap tại đối soát. Nghĩ từ zero — nếu hệ thống chưa tồn tại, report nên làm thế nào?
**Context:** Khi có cap, 1 video tạo ra 2 con số: performance (raw) và payout (capped). Analytics hiện tại chỉ có 1 layer — aggregate từ EventReward. Cần tìm cách report cả 2 mà không phá hệ thống đang chạy.

---

## 1. Bản chất vấn đề

Khi có cap, **1 sự kiện tạo ra 2 con số khác nhau**:

```
Video đạt 2M view × 0.5đ = 1,000,000đ   ← "performance" (creator làm được)
Cap 1M view × 0.5đ       =   500,000đ   ← "payout" (thực trả)
Overflow                  =   500,000đ   ← phần cắt
```

Đây **không phải bug** — đây là 2 metric khác nhau phục vụ 2 mục đích khác nhau.

---

## 2. Nhìn ra ngoài: Các hệ thống tương tự

### Payroll (lương có thuế)
```
Gross salary:  20,000,000đ    ← "earned" (performance)
Tax:           -2,000,000đ
Insurance:       -500,000đ
Net salary:    17,500,000đ    ← "payout" (thực nhận)
```
- HR report: xem **gross** (chi phí công ty)
- Nhân viên: xem **net** (tiền nhận)
- Kế toán: xem **cả hai** + breakdown deductions
- **Cách làm:** Mỗi payslip lưu cả gross, deductions, net

### Affiliate network (commission cap)
```
Raw commission: $5,000       ← "earned"
Monthly cap:    $3,000
Payout:         $3,000       ← "payout"
Holdback:       $2,000       ← "overflow"
```
- Publisher: thấy cả earned + cap + payout
- Advertiser: chỉ thấy payout (chi phí thực)
- **Cách làm:** Transaction log ghi raw + adjustments + final

### YouTube Partner Program
```
Estimated revenue: $1,200
YouTube cut (45%): -$540
Tax withholding:   -$180
Creator payout:    $480
```
- **Cách làm:** Mỗi bước là 1 adjustment. Report = aggregate ở layer nào tùy audience.

---

## 3. Pattern chung: Raw → Adjustments → Final

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   RAW       │ ──▶ │   ADJUSTMENTS    │ ──▶ │   FINAL     │
│  (earned)   │     │  (cap/tax/fee)   │     │  (payout)   │
└─────────────┘     └──────────────────┘     └─────────────┘
```

**Không ai sửa raw.** Raw là sự thật (performance). Adjustments là business rules. Final = raw - adjustments.

Report = **chọn nhìn ở layer nào:**
- "Hiệu suất creator" → raw
- "Chi phí thực tế" → final
- "Bao nhiêu bị cap" → adjustments

---

## 4. Áp dụng vào Gen-Green

### Hiện tại: 1 layer duy nhất

```
EventReward.Cash ──── aggregate ────▶ EventAnalyticDaily.Cash
                                      UserEventAnalyticDaily.Cash
  (vừa là raw, vừa là final)          (Pending/Completed/Transferred)
```

### Khi có cap: 2 layer

```
EventReward.Cash                     ← RAW (performance)
  │
  │ status: pending → completed
  │ (cash KHÔNG đổi)
  │
ReconciliationItem                   ← FINAL (payout)
  ├── TotalCash  (tiền thực trả)
  ├── Overflow   (phần bị cap)
  └── CapApplied (cap nào apply)
```

**Vấn đề:** Analytics aggregate từ EventReward → `Cash.Completed` = raw (chưa cap). Nhưng "đã đối soát" thực sự nên = payout (sau cap).

---

## 5. Bốn phương án

### Phương án A: Tách Analytics thành 2 bảng

```
EventAnalyticDaily          (giữ nguyên — raw performance)
  └── nguồn: EventReward

EventPayoutDaily            (MỚI — chi phí thực)
  └── nguồn: ReconciliationItem
```

| Ưu | Nhược |
|----|-------|
| Không đụng hệ thống hiện tại | Thêm 1 bảng + aggregate mới |
| 2 bảng = 2 góc nhìn rõ ràng | UI phải biết bảng nào cho report nào |
| Analytics cũ vẫn đúng (raw) | |

**Populate EventPayoutDaily khi nào?**
Sau Running() hoàn tất → aggregate ReconciliationItem → ghi vào EventPayoutDaily.

### Phương án B: Thêm field "payout" vào Analytics hiện có

```go
type EventAnalyticCash struct {
    // Giữ nguyên — raw (từ EventReward)
    Pending     float64   // chờ đối soát (raw)
    Completed   float64   // đã đối soát (raw)
    Transferred float64   // đã thanh toán (raw)

    // MỚI — actual payout (từ ReconciliationItem)
    PaidCompleted   float64   // tiền thực trả sau cap
    PaidTransferred float64   // tiền thực đã thanh toán
    Overflow        float64   // phần bị cap cắt
}
```

| Ưu | Nhược |
|----|-------|
| 1 bảng, 1 nơi query | Sửa model → ảnh hưởng tất cả nơi dùng |
| Dễ so sánh raw vs payout | Field nhiều, ý nghĩa phức tạp |

### Phương án C: Sửa EventReward.Cash khi đối soát

```
Running() → EventReward.Cash = cappedCash
         → EventReward.RawCash = cash gốc (mới)
```

Analytics tự động đúng vì aggregate từ EventReward.Cash (đã capped).

| Ưu | Nhược |
|----|-------|
| Analytics code KHÔNG ĐỔI | **Phá vỡ ý nghĩa EventReward.Cash** |
| Đơn giản nhất | Cần migration thêm RawCash cho data cũ |
| | Mất raw performance trong EventReward |

### Phương án D: Không sửa Analytics — report cap từ ReconciliationItem

```
Analytics hiện tại: giữ nguyên = raw performance
Report "đã trả":   query trực tiếp ReconciliationItem
Report "overflow":  query trực tiếp ReconciliationItem.Overflow
```

| Ưu | Nhược |
|----|-------|
| **KHÔNG ĐỔI GÌ** hệ thống hiện tại | Report "đã trả" phải aggregate riêng |
| ReconciliationItem đã có data cần | 2 nguồn data → UI phức tạp hơn |
| Separation of concerns rõ ràng | Không có sẵn daily breakdown cho payout |

---

## 6. So sánh

| | A: 2 bảng | B: Thêm field | C: Sửa Reward | D: Query trực tiếp |
|---|---|---|---|---|
| Đổi Analytics model | Không | **Có** | Không | Không |
| Đổi EventReward | Không | Không | **Có** | Không |
| Đổi Running() | Không | Có | Có | Không |
| Bảng mới | EventPayoutDaily | Không | Không | Không |
| Migration data cũ | Không | Không | **Có** | Không |
| Report performance | Analytics (raw) | Analytics.Completed | RawCash | Analytics (raw) |
| Report chi phí thực | PayoutDaily | PaidCompleted | Cash (capped) | ReconciliationItem |
| Complexity | Trung bình | Trung bình | Thấp | **Thấp nhất** |
| Risk | Thấp | Trung bình | **Cao** | **Thấp nhất** |

---

## 7. Key Insights

### Insight 1: "EventReward là Performance Log, ReconciliationItem là Payout Log — đừng trộn"

**Nguyên tắc Ledger Separation trong tài chính:**
- **Journal** = ghi nhận sự kiện xảy ra (EventReward: creator đạt 2M view = 1M VND)
- **Ledger** = ghi nhận tiền di chuyển (ReconciliationItem: trả 500k, overflow 500k)

Không sửa journal để khớp ledger. Report = view khác nhau trên journal + ledger.

### Insight 2: "Report cho ai quyết định nhìn layer nào"

| Audience | Câu hỏi | Layer | Nguồn |
|----------|---------|-------|-------|
| Admin (marketing) | "Creator hoạt động tốt không?" | Raw | EventReward |
| Admin (tài chính) | "Chi bao nhiêu thực tế?" | Final | ReconciliationItem |
| Admin (strategy) | "Cap có quá chặt không?" | Adjustment | ReconciliationItem.Overflow |
| Creator | "Tôi nhận bao nhiêu?" | Final | CashFlow |
| Creator | "Video nào bị cap?" | Adjustment | ReconciliationItem |

### Insight 3: "Chờ đối soát = raw (chưa cap), đã đối soát = final (sau cap)"

Trước đối soát, chưa biết cap bao nhiêu → chỉ có raw.
Sau đối soát, cap đã apply → có final.

Đây là **tự nhiên**: "chờ đối soát" = ước tính, "đã đối soát" = xác nhận. Hai số khác nhau là đúng logic nghiệp vụ.

### Insight 4: "Analytics hiện tại không sai — chỉ thiếu context"

`Cash.Pending` = raw pending → **đúng** (chưa ai cap, đó là performance thực).
`Cash.Completed` = raw completed → **đúng nếu hiểu là performance**, sai nếu hiểu là payout.

→ Không cần sửa analytics. Cần **thêm label** và **thêm nguồn data cho payout**.

---

## 8. Recommend

### V1: Phương án D (thay đổi tối thiểu)

```
Analytics hiện tại → giữ nguyên = raw performance
  "Tiền chờ đối soát" = EventReward pending → ĐÂY LÀ ƯỚC TÍNH (trước cap)
  "Tiền đã đối soát (raw)" = EventReward completed → PERFORMANCE

Report "đã trả" → query ReconciliationItem.TotalCash
  "Tiền đã trả" = sum(ReconciliationItem.TotalCash where status=completed)

Report "overflow" → query ReconciliationItem.Overflow
  "Tiền tiết kiệm nhờ cap" = sum(ReconciliationItem.Overflow)
```

**Thay đổi cần làm:**
1. ProcessingContent() — thêm cap logic + ghi Overflow (đã plan ở brainstorm trước)
2. Admin UI — report "đã trả" query từ ReconciliationItem thay vì Analytics
3. Label trên UI — phân biệt "ước tính (trước cap)" vs "thực trả (sau cap)"

### Nâng cấp: Phương án A (nếu cần daily breakdown)

Nếu admin cần xem payout **theo ngày** (không chỉ theo đợt đối soát):
- Thêm `EventPayoutDaily` populate sau mỗi Running()
- Aggregate từ ReconciliationItem group by date

---

## 9. Cách hiển thị report mới

### Admin — Event Detail

```
Tổng quan thử thách: "Thử thách TikTok Q1"
┌─────────────────────────────────────────────────────┐
│  Performance (view thực tế)                         │
│  ████████████████████████████ 5,000,000 view        │
│  ├── Chờ đối soát:  2,000,000 view                  │
│  ├── Đã đối soát:   2,500,000 view                  │
│  └── Đã thanh toán:   500,000 view                  │
│                                                     │
│  Chi phí                                            │
│  Ước tính (trước cap):      2,500,000 VND           │
│  Thực trả (sau cap):        1,800,000 VND           │
│  Tiết kiệm nhờ cap:           700,000 VND           │
│                                                     │
│  Chờ đối soát (ước tính):   1,000,000 VND           │
│  Chờ đối soát (sau cap):      ~800,000 VND *        │
│  * Ước tính dựa trên cap hiện tại                   │
└─────────────────────────────────────────────────────┘
```

### Creator — Dashboard

```
Hoa hồng của bạn — Kỳ tháng 3
┌─────────────────────────────────────────┐
│  Tối đa mỗi video/kỳ: 1,000,000 view   │
│  Tối đa mỗi kỳ: 5,000,000 VND          │
│                                         │
│  Video 1:  2M view → trả 1M (cap)       │
│  Video 2:  800k view → trả 800k         │
│  Video 3:  500k view → trả 500k         │
│                                         │
│  Tổng kỳ này: 1,150,000 / 5,000,000    │
│  ████░░░░░░░░░░░░░░░░  23%             │
└─────────────────────────────────────────┘
```

---

*Generated: 2026-04-02*
*Tiếp nối từ: brainstorming-reconciliation-based-cap-2026-04-02.md*
