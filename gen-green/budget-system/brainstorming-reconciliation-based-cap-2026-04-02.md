# Brainstorming: Cap enforce tại Đối soát (Reconciliation-based Cap) — Gen-Green

**Date:** 2026-04-02
**Objective:** Phân tích cơ chế giới hạn thưởng (cap) được enforce tại bước Đối soát, không phải realtime
**Tiền đề:** Event chạy xuyên suốt, thanh toán từng kỳ. Cap gắn theo kỳ đối soát.

---

## 1. Ý tưởng cốt lõi

**Reward vẫn tính bình thường** (crawl hàng ngày, không đổi gì). **Lúc đối soát**, mới apply cap:

```
Crawl (không đổi)           Đối soát (enforce cap)           Kết quả
┌──────────────┐           ┌──────────────────────┐         ┌──────────────────┐
│ Video A:     │           │ Cap/video/kỳ: 1M view │         │ Trả: 500k VND    │
│ 2M view mới  │──────────▶│ → chỉ trả 1M view     │────────▶│ Overflow: 500k   │
│ = 1M VND     │           │ → 500k VND            │         │ (lưu riêng)      │
└──────────────┘           │                       │         └──────────────────┘
                           │ User X tổng: 8M VND   │         ┌──────────────────┐
                           │ Cap/user/kỳ: 5M VND   │────────▶│ Trả: 5M VND      │
                           │ → chỉ trả 5M          │         │ Overflow: 3M     │
                           └──────────────────────┘         └──────────────────┘
```

**Nguyên tắc:**
- Crawl/reward pipeline = **KHÔNG THAY ĐỔI** (zero risk)
- Cap chỉ được apply khi **Processing reconciliation items**
- Phần dư (overflow) **không mất** — lưu riêng trên ReconciliationItem

---

## 2. Ba Model từ Business

### Model A: Cap view/video/kỳ
```
Đơn giá: 0.5đ/view
Cap: tối đa 1,000,000 view/video/kỳ đối soát
Không giới hạn số video
```
- Video có 2M view pending → chỉ trả 1M view = 500,000 VND
- 1M view còn lại → overflow

### Model B: Cap view/video/kỳ + giới hạn số video
```
Đơn giá: 10đ/view
Cap: tối đa 1,000,000 view/video/kỳ đối soát
Giới hạn: tối đa 10 video/kỳ đối soát
```
- Như Model A + chỉ đối soát tối đa 10 video có view cao nhất (hoặc đăng trước)
- Video thứ 11+ → toàn bộ vào overflow

### Model C: Cap tiền/user/kỳ
```
Đơn giá: 15đ/view
Cap: tối đa 50,000,000 VND/user/kỳ đối soát
```
- User có 80M pending → chỉ trả 50M
- 30M còn lại → overflow

---

## 3. Flow chi tiết

### Bước 1: Crawl (KHÔNG ĐỔI)

```
Hàng ngày:
  Crawl video metrics → tính delta view/like/comment
  → Tạo/Update EventReward (status = pending)
  → EventReward.Cash = deltaView * cashPerView + ...
  (Không check cap, không giới hạn)
```

### Bước 2: Admin tạo Đối soát

```
Admin tạo Reconciliation:
  - Conditions.FromAt: ngày bắt đầu kỳ (vd: 2026-03-01)
  - Conditions.ToAt: ngày kết thúc kỳ (vd: 2026-03-31)
  - Conditions.Events: [event_id]
  - *** MỚI: Caps config ***
    - MaxViewPerVideo: 1,000,000 (Model A,B)
    - MaxVideoPerUser: 10 (Model B, optional)
    - MaxCashPerUser: 50,000,000 (Model C, optional)
```

### Bước 3: Processing (THAY ĐỔI CHÍNH Ở ĐÂY)

Hiện tại `ProcessingContent()` gom reward pending → tạo ReconciliationItem với `TotalCash = TotalCashPending` (không cap).

**Sau khi có cap:**

```
ProcessingContent():
  1. Gom tất cả EventReward pending trong [FromAt → ToAt] cho event
     (như hiện tại — group by content)

  2. *** MỚI: Query lịch sử các kỳ trước ***
     Cho mỗi video: videoPaidBefore = sum(ReconciliationItem.completed
                                         where content.ID = video
                                         AND reconciliation.event = event)
     Cho mỗi user:  userPaidBefore = sum(ReconciliationItem.completed
                                         where user = user
                                         AND reconciliation.event = event)

  3. *** MỚI: Apply Video Cap ***
     Nếu MaxViewPerVideo > 0:
       totalViewAllCycles = videoPaidViewBefore + item.TotalViewPending
       maxViewThisCycle = MaxViewPerVideo
       viewToPayThisCycle = min(item.TotalViewPending, maxViewThisCycle)

       // Nếu video đã được trả qua nhiều kỳ trước và "bão hoà"
       // thì viewToPayThisCycle có thể là MaxViewPerVideo
       // vì mỗi kỳ reset cap mới

       cappedCash = viewToPayThisCycle * cashPerView
       overflow = item.TotalCashPending - cappedCash

  4. *** MỚI: Apply Video Count Cap ***
     Nếu MaxVideoPerUser > 0:
       Sắp xếp video của user theo: view cao nhất → thấp nhất
       Chỉ lấy top N video (N = MaxVideoPerUser)
       Video còn lại → toàn bộ cash vào overflow

  5. *** MỚI: Apply User Cap ***
     Nếu MaxCashPerUser > 0:
       userTotalThisCycle = sum(cappedCash tất cả video của user)
       Nếu userTotalThisCycle > MaxCashPerUser:
         → Cắt bớt từ video cuối cùng (thấp nhất)
         → Phần dư → overflow

  6. Tạo ReconciliationItem:
     p.TotalCash = cappedCash       // Số tiền thực trả
     p.Overflow = overflow           // Số tiền dư (mới)
     p.OverflowView = overflowView   // Số view dư (mới)
     p.CapApplied = "video" | "user" | "video_count" | "none" // (mới)
```

### Bước 4: Running (ÍT THAY ĐỔI)

Running duyệt items → tạo CashFlow. Logic **cơ bản giữ nguyên**, nhưng:
- `item.TotalCash` đã được cap từ Processing → Running chỉ xử lý số đã cap
- Overflow đã được lưu riêng → không ảnh hưởng CashFlow

### Bước 5: Overflow xử lý thế nào?

**Phương án 1: Chỉ lưu, không làm gì**
- Overflow = data cho báo cáo: "Video này thực tế đạt 2M view nhưng chỉ trả 1M"
- Admin xem để quyết định tăng cap kỳ sau

**Phương án 2: Carry-over sang kỳ sau** (phức tạp hơn, có thể phase sau)
- Kỳ sau, overflow từ kỳ trước được cộng vào pending
- Nhưng vẫn bị cap mới của kỳ sau

**Recommend: Phương án 1 cho V1.** Đơn giản, an toàn. Carry-over là tính năng nâng cao.

---

## 4. Ví dụ Minh hoạ — Toàn bộ lifecycle

### Setup
```
Event: "Thử thách TikTok Q1-2026" (chạy xuyên suốt)
Schema: 0.5đ/view
```

### Kỳ 1: Tháng 1 (đối soát 5/2)
```
Admin tạo đối soát: FromAt=1/1, ToAt=31/1
Caps: MaxViewPerVideo = 1,000,000 | MaxCashPerUser = 5,000,000

Creator A:
  Video 1: 2,000,000 view pending = 1,000,000 VND
  Video 2: 800,000 view pending = 400,000 VND
  Video 3: 500,000 view pending = 250,000 VND

Processing apply cap:
  Video 1: cap 1M view → trả 500,000 VND, overflow 500,000 VND
  Video 2: 800k < 1M cap → trả 400,000 VND, overflow 0
  Video 3: 500k < 1M cap → trả 250,000 VND, overflow 0
  User total: 1,150,000 < 5M cap → OK

Kết quả kỳ 1:
  Creator A nhận: 1,150,000 VND
  Overflow: 500,000 VND (Video 1)
```

### Kỳ 2: Tháng 2 (đối soát 5/3)
```
Admin tạo đối soát: FromAt=1/2, ToAt=28/2
Cùng cap: MaxViewPerVideo = 1,000,000 | MaxCashPerUser = 5,000,000

Creator A:
  Video 1: thêm 1,500,000 view mới (delta tháng 2) = 750,000 VND pending
  Video 2: thêm 3,000,000 view mới = 1,500,000 VND pending
  Video 4 (mới đăng): 600,000 view = 300,000 VND pending

Processing apply cap:
  Video 1: 1.5M view delta → cap 1M → trả 500,000, overflow 250,000
  Video 2: 3M view delta → cap 1M → trả 500,000, overflow 1,000,000
  Video 4: 600k < 1M → trả 300,000, overflow 0
  User total: 1,300,000 < 5M cap → OK

Kết quả kỳ 2:
  Creator A nhận: 1,300,000 VND
  Overflow: 1,250,000 VND (Video 1: 250k + Video 2: 1M)
```

### Ví dụ User Cap hit (Model C)
```
Creator B (hot creator):
  10 video, mỗi video 5M view delta = 2,500,000 VND/video
  Tổng: 25,000,000 VND pending

Cap: MaxCashPerUser = 5,000,000

Processing:
  Sắp xếp video theo view → apply video cap (nếu có) → tổng = 25M
  User cap 5M → chỉ trả 5M
  Overflow: 20M

Cách cắt:
  Trả 2 video đầu (5M) → hết user cap
  8 video còn lại → toàn bộ overflow
  HOẶC: chia đều (500k/video) — cần quyết định chính sách
```

---

## 5. Câu hỏi thiết kế cần quyết định

### Q1: Cap đơn vị gì? View hay Tiền?

| View cap | Tiền cap |
|----------|----------|
| Business dễ hiểu: "1M view/video" | Code đơn giản: so sánh VND trực tiếp |
| Cần convert: view → VND khi xử lý | Không cần convert |
| Model A,B dùng view | Model C dùng tiền |
| Phù hợp khi đơn giá đồng nhất | Phù hợp khi có milestone/bonus |

**Recommend:** Cho admin chọn 1 trong 2 khi tạo đối soát. Code xử lý cả 2: view cap → convert sang VND trước khi enforce.

### Q2: Khi hit user cap, cắt video nào?

**Phương án A:** Cắt từ video có view thấp nhất
- Ưu: video tốt nhất được trả đầy đủ
- Con: video nhỏ mất toàn bộ thưởng

**Phương án B:** Chia đều proportionally
- Mỗi video được % tương ứng
- Ưu: công bằng
- Con: phức tạp, creator khó hiểu

**Phương án C:** Cắt video đăng sau (theo thời gian)
- Video đăng trước được ưu tiên
- Ưu: creator biết trước video nào được trả
- Con: video mới luôn bị thiệt

**Recommend:** Phương án A (cắt view thấp nhất) — đơn giản, minh bạch, khuyến khích video chất lượng.

### Q3: Cap config ở đâu?

**Phương án A:** Trên ReconciliationRaw (mỗi đợt đối soát set riêng)
- Ưu: linh hoạt, admin thay đổi cap từng kỳ
- Con: admin phải nhập mỗi lần

**Phương án B:** Trên EventRaw (default), Reconciliation override
- Ưu: set 1 lần, đối soát tự inherit
- Con: thêm field trên Event

**Recommend:** Phương án B — Event có default cap, đối soát inherit + cho phép override.

### Q4: "Từ đầu event" cụ thể là gì?

Khi tính `videoPaidBefore`:
- Query tất cả ReconciliationItem.completed cho video này, **across tất cả đợt đối soát trước** của cùng event
- Đây là lịch sử tham khảo, **KHÔNG ảnh hưởng cap kỳ này**
- Mỗi kỳ có cap riêng, **reset** mỗi kỳ

→ "Từ đầu event" = context để hiểu tổng đã trả. Cap vẫn là **per-kỳ**.

### Q5: Video mới đăng giữa kỳ?

Video đăng ngày 15/1, kỳ 1 là 1/1→31/1:
- Crawl từ 15/1→31/1 → reward pending
- Đối soát kỳ 1 gom: chỉ delta từ 15/1→31/1
- Cap apply bình thường (có thể view ít vì chỉ 15 ngày)
- Kỳ 2 sẽ có nhiều view hơn (30 ngày crawl)

→ Không có vấn đề. Delta tự nhiên phân bố theo thời gian.

### Q6: Đối soát nhiều lần trong 1 kỳ?

Nếu admin tạo 2 đợt đối soát cho cùng date range:
- Đợt đối soát 1 đã trả 500k cho Video A
- Đợt đối soát 2: `videoPaidBefore` = 500k → cap remaining = 500k (nếu cap 1M)

→ Tự động handle. Query `ReconciliationItem.completed` là source of truth.

---

## 6. Data Model Changes

### ReconciliationRaw — thêm Caps
```go
type ReconciliationCaps struct {
    // Model A,B: cap view/video/kỳ
    MaxViewPerVideo int64   `bson:"maxViewPerVideo,omitempty" json:"maxViewPerVideo,omitempty"`

    // Model B: giới hạn số video/user/kỳ
    MaxVideoPerUser int     `bson:"maxVideoPerUser,omitempty" json:"maxVideoPerUser,omitempty"`

    // Model C: cap tiền/user/kỳ
    MaxCashPerUser  float64 `bson:"maxCashPerUser,omitempty" json:"maxCashPerUser,omitempty"`
}

// Trên ReconciliationRaw:
Caps *ReconciliationCaps `bson:"caps,omitempty" json:"caps,omitempty"`
```

### EventRaw — thêm Default Caps (optional, phase sau)
```go
// Default caps cho tất cả đối soát của event này
DefaultCaps *ReconciliationCaps `bson:"defaultCaps,omitempty" json:"defaultCaps,omitempty"`
```

### ReconciliationItemRaw — thêm Overflow
```go
// Phần dư bị cap
Overflow     float64 `bson:"overflow,omitempty" json:"overflow,omitempty"`
OverflowView int64   `bson:"overflowView,omitempty" json:"overflowView,omitempty"`

// Cap nào đã apply
CapApplied   string  `bson:"capApplied,omitempty" json:"capApplied,omitempty"`
// "video_view" | "video_count" | "user_cash" | "none"
```

---

## 7. Ưu điểm và Nhược điểm

### Ưu điểm
1. **Crawl pipeline KHÔNG ĐỔI** — zero risk, zero downtime
2. **Admin linh hoạt** — mỗi đợt đối soát có thể set cap khác nhau
3. **Overflow không mất** — data có giá trị cho báo cáo
4. **Backward compatible** — Caps = nil → hoạt động như cũ
5. **Align với business flow** — cap gắn với hành động đối soát, đúng mental model team
6. **Đơn giản khi implement** — chỉ thay đổi ProcessingContent(), không cần Redis Lock hay entity mới

### Nhược điểm
1. **Creator thấy reward cao rồi bị cắt** — cần UI thông báo rõ
2. **Cap enforce muộn** — từ lúc crawl đến đối soát có thể 1-30 ngày
3. **Phụ thuộc admin** — admin phải tạo đối soát đều đặn, nếu quên thì không enforce
4. **Không có "van khoá tổng"** (Bpe) — event vô hạn + đối soát đều → tổng chi không giới hạn

### Cách giảm nhược điểm

| Nhược điểm | Giảm thiểu |
|-----------|------------|
| Creator thấy reward bị cắt | UI: "Ước tính: X. Tối đa kỳ này: Y" (trước đối soát) |
| Enforce muộn | Chấp nhận — đối soát là điểm kiểm soát, không phải realtime |
| Admin quên đối soát | Reminder/alert + có thể auto-tạo đối soát (phase sau) |
| Không có Bpe | Phase sau: thêm Bpe tổng budget event, check lúc đối soát |

---

## 8. So sánh với Approach Realtime (brainstorming trước)

| Khía cạnh | Reconciliation-based (hiện tại) | Realtime (brainstorm trước) |
|-----------|--------------------------------|---------------------------|
| Thay đổi crawl pipeline | **Không** | Có (thêm Redis Lock, budget check) |
| Risk khi deploy | **Thấp** | Trung bình-Cao |
| Thời điểm enforce | Lúc đối soát (delay) | Lúc crawl (instant) |
| Creator UX | Thấy reward → bị cắt (cần UI) | Thấy cap realtime (tốt hơn) |
| Admin flexibility | **Cao** (cap khác mỗi kỳ) | Thấp (cap cố định trên Event) |
| Complexity | **Thấp** | Cao (PaymentCycle entity, Lock...) |
| Backward compatible | **100%** (Caps=nil → như cũ) | Cần migration |

**Kết luận:** Reconciliation-based phù hợp hơn cho Gen-Green V1 vì:
- Không cần thay đổi crawl pipeline (đang ổn định, 150k creators)
- Align với cách team vận hành (đối soát định kỳ)
- Ship nhanh hơn, risk thấp hơn
- Realtime enforce có thể làm phase sau nếu cần

---

## 9. Recommended Next Steps

1. **Quyết định Q1-Q6** ở mục 5 (đặc biệt Q1: view hay tiền, Q2: cắt video nào)
2. **Viết PRD** cho approach này
3. **Implement ProcessingContent()** changes
4. **Thêm UI admin:** caps config khi tạo đối soát
5. **Thêm UI creator:** hiển thị cap và overflow (phase sau)

---

*Generated: 2026-04-02*
*Tiếp nối từ: brainstorming-budget-payment-cycle-2026-04-02.md*
