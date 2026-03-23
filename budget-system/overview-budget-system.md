# Hệ thống Quản lý Ngân sách (Budget System) — Ambassador Platform

> Tài liệu tổng quan dành cho Business Team. Không yêu cầu kiến thức kỹ thuật.
>
> Cập nhật: 2026-03-22

---

## 1. Vấn đề hiện tại

Hiện tại, Ambassador Platform **chưa có cơ chế kiểm soát ngân sách tự động**. Cụ thể:

| Vấn đề | Hậu quả |
|--------|---------|
| Không giới hạn tổng chi cho mỗi chiến dịch | Chiến dịch có thể chi vượt ngân sách mà không ai biết |
| Không giới hạn thu nhập mỗi creator | 1 creator có thể "ăn" hết ngân sách chiến dịch |
| Không giới hạn thu nhập mỗi video | 1 video viral có thể chiếm hết phần của creator |
| Bonus và hoa hồng gộp chung | Khó đối soát, không biết ngân sách thực chi bao nhiêu |
| Creator thấy được tổng ngân sách chiến dịch | Thông tin nhạy cảm của brand bị lộ |

**Tóm lại:** Hệ thống đang "mở cửa" — tiền ra nhưng không có van khóa.

---

## 2. Giải pháp: Ngân sách 3 tầng

Hệ thống mới sẽ kiểm soát chi tiêu theo **3 cấp độ lồng nhau**:

```
Tầng 1: Ngân sách Chiến dịch (Event Budget)
   └── Tầng 2: Giới hạn mỗi Creator (User Cap)
         └── Tầng 3: Giới hạn mỗi Video (Video Cap)
```

### Tầng 1 — Ngân sách Chiến dịch

> *"Chiến dịch này được chi tối đa bao nhiêu?"*

- Admin đặt tổng ngân sách khi tạo chiến dịch (ví dụ: **100 triệu VND**)
- Khi hết ngân sách → **tự động dừng tính hoa hồng** cho bài mới
- Creator vẫn đăng bài được, nhưng sẽ thấy cảnh báo "Chiến dịch đã hết ngân sách"

### Tầng 2 — Giới hạn mỗi Creator

> *"Mỗi creator kiếm tối đa bao nhiêu từ chiến dịch này?"*

- Admin đặt mức trần cho mỗi creator (ví dụ: **5 triệu VND/người**)
- Đảm bảo **phân bổ công bằng** — không ai độc chiếm ngân sách
- Creator thấy rõ: "Bạn đã nhận 3 triệu / tối đa 5 triệu"

### Tầng 3 — Giới hạn mỗi Video

> *"Mỗi video kiếm tối đa bao nhiêu?"*

- Admin đặt mức trần cho mỗi video (ví dụ: **2 triệu VND/video**)
- **Khuyến khích creator đăng nhiều video** thay vì chỉ 1 video viral
- Brand được nhiều nội dung hơn từ cùng một ngân sách

**Ví dụ minh họa:**

| Không có Video Cap | Có Video Cap (2 triệu/video) |
|---|---|
| Creator A đăng 1 video viral → kiếm 5 triệu (hết cap) | Video 1: 2 triệu (đạt cap video) |
| Không có động lực đăng thêm | Video 2: 1.5 triệu |
| Brand chỉ có 1 nội dung | Video 3: 1.5 triệu (đạt cap user = 5 triệu) |
| | Brand có **3 nội dung** |

---

## 3. Bonus tách riêng khỏi ngân sách

| Loại | Tính vào ngân sách? | Bị giới hạn bởi cap? |
|------|---------------------|----------------------|
| **Hoa hồng** (theo view, like, comment) | **Có** — trừ vào ngân sách chiến dịch | Có (event, user, video cap) |
| **Bonus** (thưởng thêm từ admin) | **Không** — theo dõi riêng | Không bị cap nào giới hạn |

**Lý do:** Bonus là khoản thưởng khuyến khích, nếu tính vào ngân sách sẽ làm ngân sách cháy nhanh gấp đôi và giảm ý nghĩa khuyến khích.

**Báo cáo sẽ tách rõ:** "Chi hoa hồng: 80 triệu | Chi bonus: 15 triệu | Tổng: 95 triệu"

---

## 4. Khi ngân sách hết thì sao?

| Hoạt động | Ngân sách còn | Ngân sách hết |
|-----------|:------------:|:-------------:|
| Creator đăng bài mới | Bình thường | Vẫn được, có **cảnh báo** |
| Hệ thống đếm view/like | Bình thường | **Vẫn tiếp tục** (giữ data) |
| Tính hoa hồng | Tính bình thường | **Dừng** |
| Bonus | Vẫn tính | **Vẫn tính** (tách riêng) |
| Đối soát | Bình thường | Bình thường (cho phần đã tính) |

**Nguyên tắc:** Dữ liệu view/engagement vẫn có giá trị cho báo cáo. Chỉ dừng chi tiền, không dừng thu thập dữ liệu.

---

## 5. Creator thấy gì?

### Nguyên tắc bảo mật thông tin

| Thông tin | Creator thấy? | Lý do |
|-----------|:-----------:|-------|
| Giới hạn cá nhân (user cap) | **Thấy** | Để creator biết còn kiếm được bao nhiêu |
| Giới hạn mỗi video (video cap) | **Thấy** | Để creator chiến lược đăng bài |
| Số tiền đã nhận + chi tiết mỗi video | **Thấy** | Minh bạch |
| Bonus (tách riêng) | **Thấy** | Minh bạch |
| Tổng ngân sách chiến dịch | **Không** | Thông tin nhạy cảm của brand |
| Ngân sách còn lại của chiến dịch | **Không** | Thông tin nhạy cảm |
| Thu nhập của creator khác | **Không** | Bảo mật cá nhân |

### Giao diện Creator sẽ hiển thị

**Khi còn ngân sách:**
```
Hoa hồng của bạn
  Tối đa mỗi chiến dịch: 5,000,000 VND
  Tối đa mỗi video:      2,000,000 VND
  ████████████░░░░░░░░  60%
  Đã nhận: 3,000,000 VND (2 video)
  Còn lại: 2,000,000 VND

  Bonus (không tính vào giới hạn): +500,000 VND
```

**Khi hết ngân sách chiến dịch:**
```
Chiến dịch đã hết ngân sách
  Bài đăng mới sẽ không được tính hoa hồng.
  Bài đã đăng trước đó vẫn được thanh toán đầy đủ.
```

---

## 6. Tác động lên quy trình Đối soát

### Hiện tại (chưa có budget)
```
Tạo đối soát → Duyệt từng item → Chuyển tiền → Hoàn tất
                 (không check ngân sách)
```

### Sau khi có budget
```
Tạo đối soát → Duyệt từng item → Kiểm tra ngân sách → Chuyển tiền → Hoàn tất
                                    ↓
                              Nếu hết ngân sách
                              → Từ chối item
                              → Hoàn lại ngân sách
```

**Thay đổi chính:**
- Khi **duyệt** (approve) 1 item → hệ thống tự động kiểm tra ngân sách còn đủ không
- Nếu đủ → trừ ngân sách → duyệt
- Nếu không đủ → từ chối → thông báo cho admin
- Khi **từ chối** (reject) 1 item đã duyệt → ngân sách tự động **hoàn lại**

**Báo cáo đối soát sẽ thêm:**
- Tổng hoa hồng đã duyệt vs ngân sách chiến dịch
- Tổng bonus (tách riêng)
- Danh sách item bị từ chối vì hết ngân sách

---

## 7. Tác động lên quy trình Admin

### 7.1 Tạo chiến dịch
- Thêm 3 trường mới: **Ngân sách chiến dịch**, **Giới hạn/creator**, **Giới hạn/video**
- Cả 3 đều tùy chọn (bỏ trống = không giới hạn)
- Hệ thống tự kiểm tra: Giới hạn/video ≤ Giới hạn/creator ≤ Ngân sách chiến dịch

### 7.2 Sửa chiến dịch
- Có thể **tăng** ngân sách bất kỳ lúc nào
- Có thể **giảm** ngân sách, nhưng không thấp hơn số đã chi
- Ví dụ: Đã chi 60 triệu → không thể giảm xuống dưới 60 triệu

### 7.3 Theo dõi chiến dịch
- Trang danh sách: Badge trạng thái ngân sách (Còn / Gần hết / Đã hết)
- Trang chi tiết: Thanh tiến trình ngân sách, phân tách hoa hồng vs bonus
- Cảnh báo email khi ngân sách đạt 75%, 95%, 100% (phase sau)

### 7.4 Ngân sách đối tác (Partner Budget)
- Đã có sẵn: Tổng ngân sách các chiến dịch của 1 đối tác ≤ ngân sách đối tác
- Khi tạo/sửa chiến dịch → hệ thống tự kiểm tra không vượt ngân sách đối tác

---

## 8. Lộ trình triển khai

### Phase 1 — Nền tảng (ưu tiên cao nhất)
| Hạng mục | Mô tả |
|----------|-------|
| Ngân sách 3 tầng | Event Budget + User Cap + Video Cap |
| Tự động chặn hoa hồng | Khi hết ngân sách → dừng tính |
| Tách Bonus | Theo dõi riêng, không ảnh hưởng ngân sách |
| Đối soát kiểm tra ngân sách | Approve/Reject tự động check |
| Sửa bug hiện có | Fix lỗi reset ngân sách khi sửa chiến dịch |
| Bảo mật thông tin | Creator không thấy tổng ngân sách chiến dịch |

### Phase 2 — Trải nghiệm
| Hạng mục | Mô tả |
|----------|-------|
| Giao diện Creator | Thanh tiến trình, chi tiết mỗi video |
| Badge trạng thái | Trên danh sách chiến dịch |
| Ước tính lượt xem | Hiển thị dựa trên ngân sách / đơn giá mỗi view |
| Cảnh báo email Admin | Khi ngân sách đạt 75%, 95%, 100% |

### Phase 3 — Mở rộng (khi cần)
| Hạng mục | Mô tả |
|----------|-------|
| Ngân sách Brand | Tổng ngân sách cho cả brand (khi chuyển self-serve) |
| Dự báo & Analytics | Tốc độ tiêu ngân sách, dự đoán ngày hết |
| Báo cáo nâng cao | Export đối soát có budget breakdown |

---

## 9. Rủi ro nếu KHÔNG triển khai

| Rủi ro | Xác suất | Hậu quả |
|--------|:--------:|---------|
| Chi vượt ngân sách chiến dịch | **Cao** | Lỗ tài chính, tranh chấp với brand |
| 1 creator chiếm hết ngân sách | **Cao** | Creator khác không nhận được hoa hồng, mất công bằng |
| Brand biết tổng ngân sách bị lộ cho creator | **Đang xảy ra** | Mất niềm tin, ảnh hưởng đàm phán |
| Đối soát duyệt vượt ngân sách | **Trung bình** | Không phát hiện overspend cho đến khi chuyển tiền |
| Sửa ngân sách chiến dịch mất dữ liệu đã chi | **Đang xảy ra** | Ngân sách hiển thị sai, mất kiểm soát |

---

## 10. Câu hỏi thường gặp (FAQ)

**Q: Creator có bị mất tiền khi ngân sách hết không?**
A: Không. Bài đã đăng và hoa hồng đã được tính trước khi hết ngân sách → vẫn được thanh toán đầy đủ. Chỉ bài mới đăng SAU khi hết mới không được tính.

**Q: Bonus có bị ảnh hưởng bởi ngân sách không?**
A: Không. Bonus hoạt động hoàn toàn độc lập. Ngay cả khi ngân sách hết, admin vẫn có thể cấp bonus cho creator.

**Q: Có thể tăng ngân sách giữa chừng không?**
A: Có. Admin có thể tăng bất kỳ lúc nào. Hệ thống sẽ tự động mở lại tính hoa hồng.

**Q: Creator có biết tại sao không nhận được hoa hồng không?**
A: Có. Giao diện sẽ hiển thị rõ ràng: "Bạn đã đạt mức tối đa" (user cap) hoặc "Chiến dịch đã hết ngân sách" (event budget).

**Q: Ngân sách đối tác (Partner Budget) có thay đổi gì không?**
A: Cơ chế hiện tại giữ nguyên. Tổng ngân sách các chiến dịch của 1 đối tác vẫn phải ≤ ngân sách đối tác.

---

## Tài liệu liên quan

| Tài liệu | Nội dung | Đối tượng |
|-----------|----------|-----------|
| [brainstorming-budget-system-2026-03-16.md](brainstorming-budget-system-2026-03-16.md) | Brainstorm thiết kế ban đầu | Tech team |
| [brainstorming-budget-impact-analysis-2026-03-22.md](brainstorming-budget-impact-analysis-2026-03-22.md) | Phân tích tác động lên hệ thống | Tech team |
| **Tài liệu này** | Tổng quan cho business | Business team |

---

*Tài liệu được tạo: 2026-03-22*
*Cập nhật lần cuối: 2026-03-22*
