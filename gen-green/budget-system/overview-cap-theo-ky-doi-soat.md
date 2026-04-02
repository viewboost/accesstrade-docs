# Giới hạn thưởng theo kỳ đối soát — Gen-Green Platform

> Tài liệu tổng quan. Không yêu cầu kiến thức kỹ thuật.
>
> Cập nhật: 2026-04-02

---

## 1. Bài toán

Gen-Green có một đặc thù: **thử thách thường chạy xuyên suốt**, không có ngày kết thúc rõ ràng. Creator đăng video liên tục, hệ thống đếm view liên tục, và admin **thanh toán từng đợt** (hàng tháng, mỗi 2 tuần...).

### Yêu cầu từ Advertiser (ADV)

Các ADV đã yêu cầu cụ thể các mô hình giới hạn thưởng theo kỳ:

| Mô hình | Đơn giá | Giới hạn mỗi kỳ đối soát |
|---------|---------|--------------------------|
| **A** | 0.5đ/view | Mỗi creator được đối soát tối đa **1 triệu view/video/kỳ**, không giới hạn số video |
| **B** | 10đ/view | Mỗi creator được đối soát tối đa **1 triệu view/video/kỳ** và tối đa **10 video/kỳ** |
| **C** | 15đ/view | Mỗi creator được đối soát tối đa **50 triệu VND/kỳ** |

Hiện tại, hệ thống **chưa hỗ trợ** bất kỳ mô hình nào ở trên — không giới hạn view, không giới hạn số video, không giới hạn tiền/kỳ. Điều này gây ra ba vấn đề:

**Vấn đề 1 — Một creator "ăn" hết ngân sách**

Một creator có video viral 10 triệu view có thể kiếm nhiều hơn toàn bộ creator còn lại cộng lại.

**Vấn đề 2 — Một video chiếm hết phần**

Creator chỉ cần 1 video viral là đủ, không có động lực đăng thêm video mới. Đối tác chỉ nhận được 1 nội dung.

**Vấn đề 3 — Không kiểm soát được chi phí theo kỳ**

Admin không biết mỗi kỳ thanh toán sẽ phải chi bao nhiêu cho đến khi ngồi đối soát.

---

## 2. Cách hệ thống hoạt động hiện tại

Để hiểu giải pháp, trước tiên cần hiểu luồng tiền hiện tại:

```
 ① Creator       ② Hệ thống        ③ Hệ thống         ④ Admin          ⑤ Creator
 đăng video  →  đếm view hàng  →  tính hoa hồng  →  đối soát     →  nhận tiền
                 ngày                                 (duyệt trả)
```

**Chi tiết từng bước:**

**① Creator đăng video** vào thử thách trên TikTok, YouTube, Facebook...

**② Hệ thống đếm view** hàng ngày. Ví dụ: hôm qua 10,000 view, hôm nay 15,000 view → thêm 5,000 view mới.

**③ Tính hoa hồng** dựa trên đơn giá đã cấu hình. Ví dụ: thêm 5,000 view × 0.5đ/view = 2,500đ. Số tiền này **tăng dần mỗi ngày** theo view.

**④ Admin đối soát** — Mỗi tháng (hoặc mỗi 2 tuần), admin tạo một đợt đối soát, xác nhận số tiền và duyệt trả. Đây là bước "ký duyệt" trước khi tiền được chuyển cho creator.

**⑤ Creator nhận tiền** — Tiền được cộng vào tài khoản, creator rút về ngân hàng.

**Điểm quan trọng:** Hoa hồng được tính liên tục mỗi ngày (bước ③), nhưng creator chỉ **thực sự nhận tiền** sau khi admin đối soát (bước ④). Giữa hai bước này có thể là 2-4 tuần.

---

## 3. Giải pháp: Đặt trần thưởng khi đối soát

### Ý tưởng cốt lõi

Hệ thống vẫn **tính hoa hồng bình thường** mỗi ngày (không thay đổi gì). Khi admin **tạo đối soát**, mới áp dụng giới hạn:

```
Hàng ngày (không đổi):
  Video A tăng 2 triệu view → hệ thống ghi nhận 1,000,000đ

Lúc đối soát (áp dụng giới hạn):
  Giới hạn: tối đa 1 triệu view/video/kỳ
  → Chỉ trả cho 1 triệu view = 500,000đ
  → 1 triệu view còn lại ghi nhận riêng (overflow) — không mất, dùng cho báo cáo
```

Như vậy:
- **Trước đối soát:** Hệ thống ghi nhận đầy đủ hiệu suất thực tế của creator (2 triệu view = 1 triệu đồng)
- **Khi đối soát:** Admin đặt trần, hệ thống tự cắt và chỉ duyệt trả phần trong giới hạn
- **Phần dư:** Lưu riêng — admin xem để biết hiệu suất thực tế, quyết định tăng trần nếu cần

### Ba kiểu giới hạn

Tùy loại thử thách, admin chọn 1 hoặc kết hợp nhiều giới hạn:

---

**Kiểu A: Giới hạn view mỗi video**

> *"Mỗi video chỉ được đối soát tối đa 1 triệu view mỗi kỳ"*

```
Ví dụ: Đơn giá 0.5đ/view, trần 1 triệu view/video/kỳ

Video có 2 triệu view trong kỳ:
  → Trả: 1 triệu view × 0.5đ = 500,000đ
  → Dư:  1 triệu view (ghi nhận, không trả)

Video có 800,000 view trong kỳ:
  → Trả: 800,000 view × 0.5đ = 400,000đ (chưa chạm trần)
```

**Tác dụng:** Khuyến khích creator đăng **nhiều video** thay vì chỉ dựa vào 1 video viral. Đối tác nhận được nhiều nội dung hơn.

---

**Kiểu B: Giới hạn view mỗi video + giới hạn số video**

> *"Mỗi video tối đa 1 triệu view/kỳ, và mỗi creator tối đa 10 video/kỳ"*

```
Ví dụ: Đơn giá 10đ/view, trần 1 triệu view/video/kỳ, tối đa 10 video/kỳ

Creator đăng 15 video trong kỳ:
  → Chỉ đối soát 10 video có view cao nhất
  → 5 video còn lại → ghi nhận, không trả kỳ này
```

**Tác dụng:** Giống Kiểu A, thêm chống spam video rác để farm view.

---

**Kiểu C: Giới hạn tiền mỗi creator**

> *"Mỗi creator tối đa 50 triệu VND/kỳ"*

```
Ví dụ: Đơn giá 15đ/view, trần 50 triệu/creator/kỳ

Creator có tổng 80 triệu pending:
  → Trả: 50 triệu
  → Dư:  30 triệu (ghi nhận, không trả)
```

**Tác dụng:** Kiểm soát chi phí tối đa cho mỗi creator, bất kể số video hay view.

---

### Kết hợp nhiều giới hạn

Admin có thể kết hợp. Ví dụ: "tối đa 1 triệu view/video + tối đa 5 triệu/creator/kỳ":

```
Creator A:
  Video 1: 2M view → cap 1M view → 500,000đ
  Video 2: 3M view → cap 1M view → 500,000đ
  Video 3: 800k view             → 400,000đ
  Tổng sau video cap: 1,400,000đ

  Trần creator: 5,000,000đ
  1,400,000 < 5,000,000 → OK, trả đủ

Creator B (hot):
  10 video, mỗi video cap 1M view → 500,000đ/video
  Tổng sau video cap: 5,000,000đ

  Trần creator: 5,000,000đ
  5,000,000 = 5,000,000 → Vừa đúng trần
```

Hệ thống kiểm tra **lần lượt**: giới hạn video trước → giới hạn số video → giới hạn creator. Lấy kết quả nhỏ nhất.

---

## 4. Kỳ đối soát hoạt động thế nào?

### Mỗi kỳ, giới hạn được reset

Giới hạn tính **theo kỳ**, không phải tổng cả đời. Ví dụ:

```
Kỳ tháng 1: Video A có 2M view → trả 1M view (500,000đ), dư 1M
Kỳ tháng 2: Video A thêm 1.5M view mới → trả 1M view (500,000đ), dư 500k
Kỳ tháng 3: Video A thêm 300k view → trả 300k view (150,000đ), không dư
```

Mỗi kỳ, mỗi video lại có "quota" mới. Video viral có thể kiếm tiền qua nhiều kỳ, nhưng **không bao giờ vượt trần trong 1 kỳ**.

### Admin linh hoạt thay đổi giới hạn

Giới hạn được đặt **khi tạo đối soát**, nên admin có thể thay đổi tùy kỳ:
- Kỳ tháng 1: trần 1M view/video (thử nghiệm)
- Kỳ tháng 2: tăng lên 2M view/video (thấy ổn, nới rộng)
- Kỳ tháng 3: giảm còn 500k view/video (ngân sách eo hẹp)

---

## 5. Phần dư (overflow) xử lý thế nào?

Phần dư **không mất**, được lưu riêng cho mỗi đợt đối soát. Mục đích:

**Cho admin:**
- Xem tổng overflow để biết **hiệu suất thực tế** của creator: "Creator này thực ra đạt 80 triệu nhưng chỉ trả 50 triệu"
- Nếu overflow quá cao → cân nhắc **tăng trần** kỳ sau
- Nếu overflow thấp → trần đang phù hợp

**Cho báo cáo đối tác:**
- Tách rõ: "Chi phí thực: 50 triệu | Hiệu suất thực: 80 triệu | Tiết kiệm nhờ trần: 30 triệu"

**Phần dư KHÔNG tự động chuyển sang kỳ sau.** Mỗi kỳ tính độc lập.

---

## 6. Báo cáo sẽ thay đổi thế nào?

Khi có trần, **một video tạo ra hai con số khác nhau**:

| | Hiệu suất (performance) | Thực trả (payout) |
|---|---|---|
| Ý nghĩa | Creator **thực sự đạt được** | Tiền **thực sự trả** |
| Ví dụ | 2M view = 1,000,000đ | 1M view = 500,000đ (trần) |
| Ai cần xem? | Marketing (đánh giá creator) | Tài chính (chi phí thực) |

Đây giống như bảng lương: **lương gross** (công ty chi) khác **lương net** (nhân viên nhận). Cả hai đều đúng, phục vụ mục đích khác nhau.

### Báo cáo sẽ hiển thị hai góc nhìn

**Trước đối soát** — chỉ có hiệu suất (chưa biết trần bao nhiêu):

```
┌──────────────────────────────────────────┐
│  Chờ đối soát (ước tính)                 │
│  Creator A: 1,400,000đ                   │
│  Creator B: 5,000,000đ                   │
│  Tổng: 6,400,000đ                        │
│                                          │
│  * Đây là số ước tính trước khi áp trần  │
└──────────────────────────────────────────┘
```

**Sau đối soát** — có cả hai số:

```
┌──────────────────────────────────────────────────┐
│  Kỳ tháng 1                                      │
│                                                  │
│  Hiệu suất thực tế:     8,400,000đ              │
│  Thực trả (sau trần):   6,400,000đ              │
│  Tiết kiệm nhờ trần:    2,000,000đ              │
│                                                  │
│  Chi tiết:                                       │
│  Creator A: hiệu suất 1,400,000 → trả 1,400,000 │
│  Creator B: hiệu suất 8,000,000 → trả 5,000,000 │
│             (trần creator 5M, dư 3,000,000)      │
└──────────────────────────────────────────────────┘
```

### Quy tắc đơn giản

| Số liệu | Lấy từ đâu | Ghi chú |
|----------|------------|---------|
| **Chờ đối soát** | Hoa hồng tính hàng ngày | Là ước tính, chưa áp trần |
| **Đã trả** | Kết quả đối soát (sau trần) | Là chi phí thực tế |
| **Phần dư** | Kết quả đối soát | Hiệu suất - Thực trả |

---

## 7. Creator thấy gì?

### Trước đối soát

```
Hoa hồng chờ đối soát
  Video 1: 2,000,000 view → ước tính 1,000,000đ
  Video 2:   800,000 view → ước tính   400,000đ
  Tổng ước tính: 1,400,000đ

  ⓘ Giới hạn kỳ này: tối đa 1,000,000 view/video, tối đa 5,000,000đ/kỳ
     Số thực nhận có thể thấp hơn ước tính.
```

### Sau đối soát

```
Kỳ tháng 1 — Đã thanh toán
  Video 1: 2,000,000 view → trả 1,000,000 view = 500,000đ  (đạt trần video)
  Video 2:   800,000 view → trả 800,000 view   = 400,000đ
  Tổng nhận: 900,000đ

  ⓘ Video 1 đạt trần 1,000,000 view/kỳ.
     1,000,000 view còn lại được ghi nhận nhưng không trả kỳ này.
```

### Nguyên tắc minh bạch

| Thông tin | Creator thấy? |
|-----------|:------------:|
| Giới hạn view/video | **Có** |
| Giới hạn tiền/kỳ | **Có** |
| Chi tiết mỗi video: ước tính vs thực nhận | **Có** |
| Phần dư (overflow) mỗi video | **Có** |
| Tổng ngân sách thử thách | **Không** (nhạy cảm) |
| Thu nhập creator khác | **Không** (bảo mật) |

---

## 8. Ví dụ trọn vòng đời — 3 kỳ liên tiếp

### Cài đặt
```
Thử thách: "Green Creator Challenge" (chạy xuyên suốt)
Đơn giá: 0.5đ/view
Trần: 1,000,000 view/video/kỳ | 5,000,000đ/creator/kỳ
```

### Kỳ tháng 1

Creator A đăng 3 video:

| Video | View trong kỳ | Ước tính | Trần video | Thực trả | Dư |
|-------|:------------:|:--------:|:----------:|:--------:|:--:|
| Video 1 | 2,000,000 | 1,000,000đ | 1M view | 500,000đ | 500,000đ |
| Video 2 | 800,000 | 400,000đ | — | 400,000đ | 0 |
| Video 3 | 500,000 | 250,000đ | — | 250,000đ | 0 |
| **Tổng** | **3,300,000** | **1,650,000đ** | | **1,150,000đ** | **500,000đ** |

Trần creator: 5,000,000đ → 1,150,000 < 5M → OK

**Creator A nhận kỳ 1: 1,150,000đ**

### Kỳ tháng 2

Video cũ tiếp tục tăng view, creator đăng thêm Video 4:

| Video | View MỚI trong kỳ | Ước tính | Trần video | Thực trả | Dư |
|-------|:-----------------:|:--------:|:----------:|:--------:|:--:|
| Video 1 | 1,500,000 | 750,000đ | 1M view | 500,000đ | 250,000đ |
| Video 2 | 3,000,000 | 1,500,000đ | 1M view | 500,000đ | 1,000,000đ |
| Video 3 | 200,000 | 100,000đ | — | 100,000đ | 0 |
| Video 4 (mới) | 600,000 | 300,000đ | — | 300,000đ | 0 |
| **Tổng** | **5,300,000** | **2,650,000đ** | | **1,400,000đ** | **1,250,000đ** |

Trần creator: 5,000,000đ → 1,400,000 < 5M → OK

**Creator A nhận kỳ 2: 1,400,000đ**

### Kỳ tháng 3

Admin tăng trần lên 2,000,000 view/video (thấy overflow cao quá):

| Video | View MỚI trong kỳ | Ước tính | Trần video (2M) | Thực trả | Dư |
|-------|:-----------------:|:--------:|:----------------:|:--------:|:--:|
| Video 1 | 500,000 | 250,000đ | — | 250,000đ | 0 |
| Video 2 | 4,000,000 | 2,000,000đ | 2M view | 1,000,000đ | 1,000,000đ |
| Video 4 | 1,200,000 | 600,000đ | — | 600,000đ | 0 |
| **Tổng** | **5,700,000** | **2,850,000đ** | | **1,850,000đ** | **1,000,000đ** |

**Creator A nhận kỳ 3: 1,850,000đ**

Nhận xét: Tăng trần → creator nhận nhiều hơn, overflow giảm.

---

## 9. Các chức năng cần làm lại

Khi có trần, hệ thống xuất hiện **hai con số khác nhau** cho cùng một video:

| | Hiệu suất (performance) | Thực trả (payout) |
|---|---|---|
| Ý nghĩa | Creator **thực sự đạt được** | Tiền **thực sự trả** (sau trần) |
| Ví dụ | 2M view = 1,000,000đ | 1M view = 500,000đ |

Giống bảng lương: **lương gross** (tính được) khác **lương net** (thực nhận). Một số chức năng hiện tại chỉ có 1 con số — cần tách thành 2.

### 9.1 Đối soát (Reconciliation) — Thay đổi lớn nhất

Đây là chức năng **thay đổi nhiều nhất** vì trần được áp dụng chính tại bước này.

#### Tạo đối soát — thêm cấu hình trần

Hiện tại admin tạo đối soát chỉ cần chọn: thời gian (từ ngày → đến ngày) + thử thách.

**Thêm mới:** admin cấu hình trần khi tạo đối soát:

| Cấu hình mới | Ý nghĩa | Bắt buộc? |
|--------------|---------|:---------:|
| Trần view/video/kỳ | Mỗi video tối đa bao nhiêu view được đối soát | Không |
| Trần số video/kỳ | Mỗi creator tối đa bao nhiêu video được đối soát | Không |
| Trần tiền/creator/kỳ | Mỗi creator tối đa bao nhiêu tiền/kỳ | Không |

Nếu không đặt trần nào → hoạt động như cũ (không giới hạn).

#### Xử lý đối soát (Processing) — logic chính

Hiện tại bước Processing gom hoa hồng pending → tạo danh sách items, mỗi item = 1 video với toàn bộ tiền.

**Thay đổi:** Sau khi gom, thêm bước **áp trần** trước khi tạo items:

```
① Gom hoa hồng pending của tất cả video trong kỳ (như hiện tại)

② Áp trần video:
   Video A có 2M view pending → trần 1M view → chỉ ghi nhận 1M view
   Video B có 800k view → chưa chạm trần → ghi nhận đủ

③ Áp trần số video (nếu có):
   Creator có 15 video → trần 10 → chỉ lấy 10 video có view cao nhất
   5 video còn lại → toàn bộ vào overflow

④ Áp trần creator (nếu có):
   Tổng tiền sau bước ② và ③ = 8M → trần 5M → cắt bớt từ video thấp nhất
   3M dư → overflow

⑤ Tạo items đối soát:
   Mỗi item ghi: tiền thực trả + tiền gốc + overflow + loại trần đã áp dụng
```

#### Danh sách đối soát — hiển thị thêm

Hiện tại mỗi item đối soát hiển thị: creator, video, tiền.

**Thêm mới:**

| Cột mới | Ý nghĩa |
|---------|---------|
| Tiền gốc (trước trần) | Tiền tính được nếu không giới hạn |
| Tiền thực trả (sau trần) | Tiền được duyệt trả |
| Overflow | Phần bị trần cắt = Gốc - Thực trả |
| Trần đã áp dụng | "Trần video" / "Trần số video" / "Trần creator" / Không |

**Ví dụ hiển thị:**

```
Đối soát kỳ tháng 1 — Thử thách TikTok
Trần: 1M view/video | 5M VND/creator

┌─────────┬──────────┬───────────┬──────────┬───────────┬───────────┬──────────┐
│ Creator │  Video   │ View gốc  │ View trả │ Tiền gốc  │ Thực trả  │ Overflow │
├─────────┼──────────┼───────────┼──────────┼───────────┼───────────┼──────────┤
│ A       │ Video 1  │ 2,000,000 │ 1,000,000│ 1,000,000 │   500,000 │  500,000 │
│ A       │ Video 2  │   800,000 │   800,000│   400,000 │   400,000 │        0 │
│ A       │ Tổng     │           │          │ 1,400,000 │   900,000 │  500,000 │
├─────────┼──────────┼───────────┼──────────┼───────────┼───────────┼──────────┤
│ B       │ Video 1  │ 5,000,000 │ 1,000,000│ 2,500,000 │   500,000 │2,000,000 │
│ B       │ ...      │    ...    │   ...    │   ...     │   ...     │    ...   │
│ B       │ Tổng     │           │          │ 8,000,000 │ 5,000,000 │3,000,000 │
└─────────┴──────────┴───────────┴──────────┴───────────┴───────────┴──────────┘

Tổng kỳ:  Hiệu suất 9,400,000đ | Thực trả 5,900,000đ | Overflow 3,500,000đ
```

#### Duyệt đối soát (Running) — ít thay đổi

Bước Running duyệt items → tạo CashFlow → cộng tiền cho creator. Logic **cơ bản giữ nguyên**, chỉ khác: `TotalCash` trên mỗi item đã là số **sau trần** (được tính từ bước Processing).

### 9.2 Thống kê thử thách (Event Analytics)

Bảng thống kê hàng ngày ghi nhận view và tiền theo trạng thái. **Cách tính cần thay đổi:**

| Cột thống kê | Hiện tại | Sau khi có trần |
|--------------|---------|----------------|
| View chờ duyệt | Từ hoa hồng (EventReward) | Không đổi — chưa áp trần |
| View đã duyệt | Từ hoa hồng (EventReward) | Không đổi — chưa áp trần |
| **View đã đối soát** | Từ hoa hồng (EventReward) = view gốc | **Từ kết quả đối soát** (ReconciliationItem) = view sau trần |
| **View đã thanh toán** | Từ hoa hồng (EventReward) = view gốc | **Từ kết quả đối soát** = view sau trần |
| Tiền chờ duyệt | Từ hoa hồng = tiền gốc | Không đổi — là ước tính (trước trần) |
| Tiền đã duyệt | Từ hoa hồng = tiền gốc | Không đổi — là ước tính (trước trần) |
| **Tiền đã đối soát** | Từ hoa hồng = tiền gốc | **Từ kết quả đối soát** = tiền sau trần |
| **Tiền đã thanh toán** | Từ hoa hồng = tiền gốc | **Từ kết quả đối soát** = tiền sau trần |

Ngoài ra, **cần thêm cột mới:**

| Cột mới | Ý nghĩa | Nguồn |
|---------|---------|-------|
| View overflow | Số view bị trần cắt | Kết quả đối soát |
| Tiền overflow | Số tiền bị trần cắt | Kết quả đối soát |

**Tóm lại:** "Chờ duyệt" và "đã duyệt" giữ nguyên (là hiệu suất thực). "Đã đối soát" và "đã thanh toán" phải lấy từ kết quả đối soát (là số thực trả, sau trần).

> Cần tạo **bảng thống kê mới** (hoặc thêm cột) để lưu số liệu sau trần, tách biệt với bảng thống kê hiệu suất hiện tại.

### 9.3 Xuất báo cáo thống kê thử thách (Export Event Chart)

Hiện tại, file Excel xuất ra có các cột:

```
Ngày | View chờ duyệt | View đã duyệt | View đã đối soát | View đã thanh toán
     | Tiền chờ duyệt | Tiền đã duyệt | Tiền đã đối soát | Tiền đã thanh toán
```

**Thay đổi:** Cột "đã đối soát" và "đã thanh toán" cần lấy từ nguồn mới (kết quả đối soát), không phải từ bảng thống kê cũ.

**Cân nhắc thêm cột:**

```
... | View đối soát (gốc) | View đối soát (sau trần) | View overflow | ...
    | Tiền đối soát (gốc) | Tiền đối soát (sau trần) | Tiền overflow | ...
```

### 9.4 Xuất báo cáo người dùng (Export User Partner)

Hiện tại có các cột:

```
Lượt xem tổng | Lượt xem chờ duyệt | Lượt xem đã duyệt | Lượt xem đã đối soát | Lượt xem đã thanh toán
Số tiền tổng  | Số tiền chờ duyệt  | Số tiền đã duyệt  | Số tiền đã đối soát  | Số tiền đã thanh toán
```

**Thay đổi:** Tương tự — "đã đối soát" và "đã thanh toán" cần lấy từ kết quả đối soát.

**Cân nhắc thêm cột:**

```
... | Số tiền đã đối soát (gốc) | Số tiền đã đối soát (sau trần) | Overflow | ...
```

### 9.5 Xuất báo cáo đối soát (Export Reconciliation)

Hiện tại xuất chi tiết từng item đối soát. **Cần thêm:**

| Cột mới | Ý nghĩa |
|---------|---------|
| Tiền gốc (trước trần) | Tiền tính được nếu không có trần |
| Tiền thực trả (sau trần) | Tiền được duyệt trả |
| Overflow | Phần bị trần cắt |
| Trần đã áp dụng | "video_view" / "video_count" / "user_cash" |

### 9.6 Thống kê creator (User Event Statistic)

Creator xem thu nhập trên app/web. Hiện tại hiển thị: tiền pending / completed / transferred.

**Thay đổi:**
- "Chờ đối soát" — giữ nguyên (ước tính, trước trần), **thêm ghi chú** "ước tính, có thể thay đổi sau đối soát"
- "Đã đối soát" — cần phản ánh số **sau trần**
- **Thêm hiển thị:** trần áp dụng + phần overflow mỗi video (xem mục 7)

### 9.7 Dashboard admin (Event Statistic)

Dashboard hiển thị tổng quan thử thách: view/tiền theo pending/approved/transfer/cashback.

**Thay đổi:**
- Giữ nguyên pending/approved = hiệu suất thực (trước trần)
- Thêm mục **"Đã trả (sau trần)"** lấy từ kết quả đối soát
- Thêm mục **"Overflow"** để admin thấy bao nhiêu bị trần cắt

### Tóm tắt nguyên tắc chung

> **"Chờ duyệt" và "Đã duyệt"** = hiệu suất thực tế (lấy từ hoa hồng) — **không đổi**
>
> **"Đã đối soát" và "Đã thanh toán"** = tiền thực trả (lấy từ kết quả đối soát) — **cần đổi nguồn**
>
> **Overflow** = hiệu suất - thực trả — **thêm mới**

---

## 10. Tổng kết thay đổi

### Không thay đổi

| Hạng mục | Trạng thái |
|----------|-----------|
| Hệ thống đếm view hàng ngày | Không đổi |
| Cách tính hoa hồng | Không đổi |
| Creator đăng video | Không đổi |
| Quy trình rút tiền | Không đổi |
| Bonus (thưởng thủ công) | Không đổi, không bị trần |

### Thay đổi

| Hạng mục | Thay đổi |
|----------|---------|
| Tạo đối soát | Admin thêm: trần view/video, trần tiền/creator, giới hạn số video |
| Xử lý đối soát | Hệ thống tự áp trần, cắt phần dư |
| Kết quả đối soát | Thêm thông tin: thực trả + phần dư |
| Báo cáo | Tách hai số: hiệu suất (ước tính) và thực trả (sau trần) |
| Creator xem thu nhập | Thêm hiển thị trần và phần dư mỗi video |

---

## 11. Câu hỏi thường gặp

**Q: Creator có bị mất tiền không?**
A: Phần dư được **ghi nhận**, không "biến mất". Nhưng nó không được trả. Admin có thể xem phần dư để cân nhắc tăng trần kỳ sau.

**Q: Nếu admin không đặt trần thì sao?**
A: Mọi thứ hoạt động như hiện tại — không giới hạn, trả hết.

**Q: Trần có ảnh hưởng tới bonus không?**
A: Không. Bonus do admin tạo thủ công, hoàn toàn độc lập, không bị trần nào ảnh hưởng.

**Q: Admin có thể đổi trần giữa chừng không?**
A: Mỗi đợt đối soát có trần riêng. Admin đặt trần khác nhau mỗi kỳ tùy ý.

**Q: Video cũ (đăng từ tháng trước) có bị ảnh hưởng không?**
A: Video cũ vẫn tăng view → vẫn có hoa hồng mới mỗi kỳ. Trần tính trên **view mới trong kỳ**, không phải tổng view từ trước tới giờ.

**Q: "Chờ đối soát" trên báo cáo là số trước hay sau trần?**
A: Là số **trước trần** (ước tính). Số sau trần chỉ có **sau khi đối soát xong**. Hai số khác nhau là bình thường — giống lương gross khác lương net.

---

## Tài liệu liên quan

| Tài liệu | Nội dung |
|-----------|----------|
| [brainstorming-budget-payment-cycle](brainstorming-budget-payment-cycle-2026-04-02.md) | Phân tích 3 approach: Realtime vs Rolling vs Đối soát |
| [brainstorming-reconciliation-based-cap](brainstorming-reconciliation-based-cap-2026-04-02.md) | Chi tiết kỹ thuật approach đối soát |
| [brainstorming-report-architecture](brainstorming-report-architecture-2026-04-02.md) | Kiến trúc report khi có cap |

---

*Tài liệu được tạo: 2026-04-02*
