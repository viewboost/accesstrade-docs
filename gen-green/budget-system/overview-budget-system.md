# Hệ thống Quản lý Ngân sách (Budget System) — Gen-Green Platform

> Tài liệu tổng quan dành cho Business Team. Không yêu cầu kiến thức kỹ thuật.
>
> Cập nhật: 2026-04-02

---

## 1. Vấn đề hiện tại

Gen-Green hiện **chưa có cơ chế kiểm soát ngân sách tự động**. Cụ thể:

| Vấn đề | Hậu quả |
|--------|---------|
| Không giới hạn tổng chi cho mỗi thử thách | Thử thách có thể chi vượt ngân sách dự kiến mà không ai biết |
| Không giới hạn thu nhập mỗi creator | 1 creator có thể "ăn" hết ngân sách thử thách |
| Không giới hạn thu nhập mỗi video | 1 video viral có thể chiếm hết phần của creator |
| Không có cảnh báo khi ngân sách sắp hết | Admin chỉ phát hiện khi đã quá muộn |
| Bonus và hoa hồng gộp chung | Khó đối soát, không biết ngân sách thực chi bao nhiêu |

**Tóm lại:** Hệ thống đang "mở cửa" — tiền ra nhưng không có van khóa.

---

## 2. Cách hệ thống thưởng hiện tại hoạt động (trước Budget)

Để hiểu Budget System, trước tiên cần hiểu luồng thưởng hiện tại:

```
Creator đăng video  →  Hệ thống cào metrics hàng ngày  →  Tính hoa hồng  →  Admin đối soát  →  Creator nhận tiền
     (Content)              (View, Like, Comment)           (EventReward)      (Reconciliation)      (Withdraw)
```

### 2.1 Cách tính hoa hồng

Admin cấu hình **đơn giá** cho mỗi thử thách (EventSchema):

| Loại tương tác | Ví dụ đơn giá |
|----------------|---------------|
| Mỗi lượt xem (View) | 0.5 VND/view |
| Mỗi lượt thích (Like) | 5 VND/like |
| Mỗi bình luận (Comment) | 10 VND/comment |

**Ví dụ:** Video có 10,000 views, 500 likes, 50 comments:
```
Hoa hồng = (10,000 × 0.5) + (500 × 5) + (50 × 10)
         = 5,000 + 2,500 + 500
         = 8,000 VND
```

**Đặc điểm quan trọng:** Hoa hồng được **tính lại mỗi ngày** khi metrics tăng (view tăng → tiền tăng). Đây không phải tính 1 lần mà là **tích lũy liên tục**.

### 2.2 Các loại thưởng

| Loại | Cách tính | Ví dụ |
|------|-----------|-------|
| **Hoa hồng theo metrics** (Statistic) | Tự động theo view/like/comment | 0.5đ/view × 10,000 views = 5,000đ |
| **Milestone** | Cố định khi đạt mốc | Đăng đủ 3 video ≥ 1,000 views → thưởng 200,000đ |
| **Bonus** | Admin tạo thủ công | Admin thưởng thêm 100,000đ cho creator |

### 2.3 Luồng thanh toán

```
Reward (pending)  →  Đối soát (Reconciliation)  →  Duyệt  →  CashFlow  →  Transfer  →  Rút tiền (Withdraw)
```

- **Đối soát:** Admin tạo batch, hệ thống gom tất cả reward pending → tạo danh sách items để review
- **Transfer:** Tạo đợt chuyển tiền, hệ thống tạo lệnh rút cho từng creator
- **Rút tiền:** Creator nhận tiền vào tài khoản ngân hàng

---

## 3. Giải pháp: Ngân sách 3 tầng

Hệ thống mới sẽ kiểm soát chi tiêu theo **3 cấp độ lồng nhau**:

```
Tầng 1: Ngân sách Thử thách (Event Budget — Bpe)
   └── Tầng 2: Giới hạn mỗi Creator (User Cap — Bpu)
         └── Tầng 3: Giới hạn mỗi Video (Video Cap — Bpc)
```

### Tầng 1 — Ngân sách Thử thách (Bpe)

> *"Thử thách này được chi tối đa bao nhiêu?"*

- Admin đặt tổng ngân sách khi tạo thử thách (ví dụ: **100 triệu VND**)
- Hệ thống theo dõi realtime: Total, Used (đã chi), Remain (còn lại)
- Khi hết ngân sách → **tự động dừng tính hoa hồng** cho nội dung mới
- Khi đạt 95% → **chặn nộp video mới**, vẫn tính reward cho video cũ
- Khi đạt 100% → **chặn tất cả**, reward mới = 0đ

### Tầng 2 — Giới hạn mỗi Creator (Bpu)

> *"Mỗi creator kiếm tối đa bao nhiêu từ thử thách này?"*

- Admin đặt mức trần cho mỗi creator (ví dụ: **5 triệu VND/người**)
- Đảm bảo **phân bổ công bằng** — không ai độc chiếm ngân sách
- Khi đạt trần → dừng tính hoa hồng cho creator đó, creator khác vẫn kiếm được

### Tầng 3 — Giới hạn mỗi Video (Bpc)

> *"Mỗi video kiếm tối đa bao nhiêu?"*

- Admin đặt mức trần cho mỗi video (ví dụ: **2 triệu VND/video**)
- **Khuyến khích creator đăng nhiều video** thay vì chỉ dựa vào 1 video viral
- Đối tác được nhiều nội dung hơn từ cùng một ngân sách

**Ví dụ minh họa:**

| Không có Video Cap | Có Video Cap (2 triệu/video) |
|---|---|
| Creator A đăng 1 video viral → kiếm 5 triệu (hết cap user) | Video 1: 2 triệu (đạt cap video) |
| Không có động lực đăng thêm | Video 2: 1.5 triệu |
| Đối tác chỉ có 1 nội dung | Video 3: 1.5 triệu (đạt cap user = 5 triệu) |
| | Đối tác có **3 nội dung** |

### Cách 3 tầng phối hợp

Khi tính reward, hệ thống kiểm tra **cả 3 cấp** và lấy **giá trị nhỏ nhất**:

```
Ngân sách khả dụng = min(
    Tầng 1: Event Budget còn lại,
    Tầng 2: User Cap còn lại,
    Tầng 3: Video Cap còn lại
)
```

**Ví dụ:** Event Budget còn 3 triệu, User Cap còn 1 triệu, Video Cap còn 2 triệu → Khả dụng = 1 triệu (giới hạn bởi User Cap).

---

## 4. Chia nhỏ phần thưởng (Budget Split)

Khi ngân sách không đủ cho toàn bộ reward nhưng vẫn > 0, hệ thống **chia nhỏ** thay vì chặn hoàn toàn:

| Tình huống | Xử lý |
|-----------|-------|
| Reward = 500k, Budget còn 500k | Trả đủ 500k |
| Reward = 500k, Budget còn 300k | Trả 300k (primary) + ghi nhận 200k overflow (cash = 0) |
| Reward = 500k, Budget còn 0đ | Reward = 0đ, đánh dấu budget exceeded |

**Thứ tự ưu tiên** khi chia: Milestone → Like → Comment → View

Phần overflow được ghi nhận riêng (overbudgetCash) — giúp admin biết performance thực tế của creator, hỗ trợ quyết định tăng budget.

---

## 5. Bonus tách riêng khỏi ngân sách

| Loại | Tính vào ngân sách? | Bị giới hạn bởi cap? |
|------|---------------------|----------------------|
| **Hoa hồng** (theo view, like, comment) | **Có** — trừ vào ngân sách thử thách | Có (event, user, video cap) |
| **Milestone** (thưởng đạt mốc) | **Có** — trừ vào ngân sách | Có (event cap, user cap) |
| **Bonus** (thưởng thêm từ admin) | **Không** — theo dõi riêng | Không bị cap nào giới hạn |

**Lý do:** Bonus là khoản thưởng khuyến khích đặc biệt. Nếu tính vào ngân sách sẽ làm ngân sách cháy nhanh và giảm ý nghĩa khuyến khích.

**Báo cáo sẽ tách rõ:** "Chi hoa hồng: 80 triệu | Chi bonus: 15 triệu | Tổng: 95 triệu"

---

## 6. Khi ngân sách hết thì sao?

| Hoạt động | Ngân sách còn | Gần hết (≥95%) | Hết (100%) |
|-----------|:------------:|:-------------:|:----------:|
| Creator đăng video mới | Bình thường | **Chặn** | **Chặn** |
| Hệ thống đếm view/like | Bình thường | Bình thường | **Vẫn tiếp tục** (giữ data) |
| Tính hoa hồng cho video cũ | Bình thường | Bình thường | **Dừng** (cash = 0) |
| Bonus | Vẫn tính | Vẫn tính | **Vẫn tính** (tách riêng) |
| Đối soát | Bình thường | Bình thường | Bình thường (cho phần đã tính) |

**Nguyên tắc:**
- Dữ liệu view/engagement vẫn có giá trị cho báo cáo — chỉ dừng chi tiền, không dừng thu thập dữ liệu
- Tại 95%: chặn nộp video mới để tránh creator đăng rồi không nhận được thưởng
- Tại 100%: chặn tất cả reward mới

---

## 7. Các mốc cảnh báo tự động

| Mốc | Hành vi hệ thống |
|-----|-------------------|
| **75%** | Ghi nhận milestone tracking, thử thách vẫn hoạt động bình thường |
| **95%** | Chặn nộp video mới, reward vẫn chạy cho video cũ |
| **100%** | Chặn tất cả, reward mới = 0đ, gửi cảnh báo Telegram |

Admin có thể tạo thêm các **mốc theo dõi tùy chỉnh** (Budget Campaign) — ví dụ: mốc 50 triệu, mốc 80 triệu — để theo dõi tiến độ chi tiêu.

---

## 8. Creator thấy gì?

### Nguyên tắc bảo mật thông tin

| Thông tin | Creator thấy? | Lý do |
|-----------|:-----------:|-------|
| Giới hạn cá nhân (user cap) | **Thấy** | Để creator biết còn kiếm được bao nhiêu |
| Giới hạn mỗi video (video cap) | **Thấy** | Để creator chiến lược đăng bài |
| Số tiền đã nhận + chi tiết mỗi video | **Thấy** | Minh bạch |
| Bonus (tách riêng) | **Thấy** | Minh bạch |
| Tổng ngân sách thử thách | **Không** | Thông tin nhạy cảm của đối tác |
| Ngân sách còn lại của thử thách | **Không** | Thông tin nhạy cảm |
| Thu nhập của creator khác | **Không** | Bảo mật cá nhân |

### Giao diện Creator sẽ hiển thị

**Khi còn ngân sách:**
```
Hoa hồng của bạn
  Tối đa mỗi thử thách: 5,000,000 VND
  Tối đa mỗi video:     2,000,000 VND
  ████████████░░░░░░░░  60%
  Đã nhận: 3,000,000 VND (2 video)
  Còn lại: 2,000,000 VND

  Bonus (không tính vào giới hạn): +500,000 VND
```

**Khi hết ngân sách thử thách:**
```
Thử thách đã hết ngân sách
  Video mới sẽ không được tính hoa hồng.
  Video đã đăng trước đó vẫn được thanh toán đầy đủ.
```

---

## 9. Tác động lên quy trình hiện tại

### 9.1 Tính hoa hồng (Reward)

**Hiện tại:**
```
Crawl metrics → Tính cash = views × đơn giá + likes × đơn giá + ... → Tạo/Update EventReward
                (không giới hạn)
```

**Sau khi có budget:**
```
Crawl metrics → Acquire Lock (Redis) → Đọc ngân sách mới nhất
              → Tính cash dự kiến
              → Kiểm tra 3 tầng: Event > User > Video
              → Nếu đủ: tạo reward full
              → Nếu thiếu: chia nhỏ (split) → primary reward + overflow
              → Nếu hết: reward = 0đ + đánh dấu exceeded
              → Release Lock
```

**Lock (Redis)** đảm bảo khi crawl nhiều platform cùng lúc (TikTok, YouTube, Facebook) cho cùng thử thách, không bị chi vượt do race condition.

### 9.2 Đối soát (Reconciliation)

Không thay đổi lớn — reward đã được kiểm soát từ bước tính hoa hồng. Đối soát chỉ duyệt những reward đã được hệ thống cap sẵn.

### 9.3 Admin tạo/sửa Thử thách

- Thêm 3 trường mới: **Ngân sách thử thách (Bpe)**, **Giới hạn/creator (Bpu)**, **Giới hạn/video (Bpc)**
- Cả 3 đều tùy chọn (bỏ trống hoặc 0 = không giới hạn, hoạt động như cũ)
- Validation: `Bpc ≤ Bpe` và `Bpu ≤ Bpe`
- Khi đã có reward: **không cho sửa budget** (tránh xung đột dữ liệu)
- Sửa event không reset ngân sách đã chi (fix bug so với Ambassador)

---

## 10. Khác biệt so với Ambassador

Gen-Green và Ambassador chia sẻ cùng thiết kế budget 3 tầng, nhưng có một số khác biệt:

| Khía cạnh | Ambassador | Gen-Green |
|-----------|-----------|-----------|
| **Scale** | Hàng trăm influencer | ~150,000 creator |
| **Loại thử thách** | Chiến dịch marketing (campaign) | Thử thách nội dung (event) |
| **Đơn giá** | Thường ≥ 1đ/view | Hỗ trợ đơn giá lẻ (0.1đ–0.9đ/view) |
| **Quy tắc làm tròn** | Làm tròn từng bước | Chỉ `math.Floor()` ở tổng cuối (giữ precision trung gian) |
| **Sửa budget sau reward** | Cho phép tăng/giảm (≥ Used) | Chặn hoàn toàn khi đã có reward |
| **Auto-block tại 95%** | Chỉ cảnh báo | Chặn nộp video mới |
| **Budget Campaign** | Không có | Mốc milestone tùy chỉnh cho admin |

---

## 11. Rủi ro nếu KHÔNG triển khai

| Rủi ro | Xác suất | Hậu quả |
|--------|:--------:|---------|
| Chi vượt ngân sách thử thách | **Cao** | Lỗ tài chính, tranh chấp với đối tác |
| 1 creator chiếm hết ngân sách | **Cao** | Creator khác không nhận được hoa hồng, mất công bằng |
| Đối tác thấy ngân sách bị chi không kiểm soát | **Trung bình** | Mất niềm tin, ảnh hưởng hợp tác |
| 1 video viral tiêu hết budget | **Trung bình** | Đối tác chỉ nhận được 1 nội dung thay vì nhiều |
| Admin không phát hiện budget cạn kịp thời | **Cao** | Creator đăng rồi không nhận thưởng → khiếu nại |

---

## 12. Câu hỏi thường gặp (FAQ)

**Q: Creator có bị mất tiền khi ngân sách hết không?**
A: Không. Video đã đăng và hoa hồng đã được tính trước khi hết ngân sách → vẫn được thanh toán đầy đủ. Chỉ video mới đăng SAU khi hết mới không được tính.

**Q: Bonus có bị ảnh hưởng bởi ngân sách không?**
A: Không. Bonus hoạt động hoàn toàn độc lập. Ngay cả khi ngân sách hết, admin vẫn có thể cấp bonus.

**Q: Đơn giá lẻ (0.5đ/view) có bị làm tròn sai không?**
A: Không. Hệ thống chỉ làm tròn (math.Floor) ở bước cuối cùng khi ra tổng tiền. Các bước trung gian giữ nguyên precision. Ví dụ: 0.5đ × 1,001 views = 500.5đ → làm tròn = 500đ (chỉ 1 lần).

**Q: Thử thách cũ (đang chạy, không có budget) có bị ảnh hưởng không?**
A: Không. Giá trị Bpe/Bpu/Bpc = 0 nghĩa là unlimited — hệ thống hoạt động y hệt hiện tại. Chỉ thử thách nào admin cấu hình budget mới bị kiểm soát.

**Q: Tại sao không cho sửa budget khi đã có reward?**
A: Để tránh xung đột dữ liệu phức tạp. Với scale 150,000 creator, việc recalculate toàn bộ reward khi thay đổi cap giữa chừng rất rủi ro. Admin nên set budget đúng từ đầu.

**Q: Overflow reward (phần vượt cap) có ý nghĩa gì?**
A: Admin có thể xem tổng overflow để biết performance thực tế. Nếu thấy overflow cao → có thể tạo thử thách mới với budget lớn hơn.

---

## Tài liệu liên quan

| Tài liệu | Nội dung | Đối tượng |
|-----------|----------|-----------|
| [Ambassador Budget Overview](../../budget-system/overview-budget-system.md) | Tổng quan budget cho Ambassador | Business team |
| [Ambassador PRD V2 (chi tiết kỹ thuật)](../../budget-system/prd-budget-v2.md) | PRD kỹ thuật đầy đủ — thiết kế tham khảo | Tech team |
| [Fractional Reward PRD](../fractional-reward-by-statistic/prd-fractional-reward-2026-04-01.md) | Hỗ trợ đơn giá lẻ (0.1đ–0.9đ) | Tech team |
| **Tài liệu này** | Tổng quan budget cho Gen-Green | Business team |

---

*Tài liệu được tạo: 2026-04-02*
