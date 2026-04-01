# Xác nhận đối tác trong quy trình đối soát

> Tài liệu mô tả tính năng mới: thêm bước **"Đối tác xác nhận"** vào quy trình đối soát (reconciliation), giúp tách bạch giữa duyệt nội bộ (Ops) và xác nhận từ đối tác (Techcombank).

**Ngày:** 01/04/2026  
**Trạng thái:** Đề xuất  
**Đối tượng đọc:** Business, Ops, PM, Dev

---

## 1. Bối cảnh

### Quy trình hiện tại

Khi một Influencer đăng bài cho thử thách T-Fluencers, quy trình duyệt và trả thưởng diễn ra như sau:

```
Influencer đăng bài
    ↓
Ops duyệt bài đăng (approved / rejected)
    ↓
Hệ thống ghi nhận thưởng tạm (reward pending)
    ↓
Đối soát: Admin kiểm tra checklist
    ↓
Chốt thưởng và thanh toán
```

### Vấn đề

- Ops duyệt bài xong = bài đạt chất lượng. Nhưng **đối tác cũng cần xác nhận** bài đăng trước khi chốt thưởng
- Hiện tại **đối tác không có bước xác nhận nào** trong quy trình — toàn bộ do Ops quyết định
- Khi đối tác không xác nhận một bài, **bài đăng không bị hủy** (vẫn approved), chỉ là **chưa được chốt thưởng** cho đợt đối soát đó
- Nếu một bài đăng đã từng được đối tác xác nhận ở lần đối soát trước, thì lần sau **không cần gửi lại** cho đối tác nữa

---

## 2. Giải pháp đề xuất

### Ý tưởng chính

Thêm **1 mục kiểm tra mới** vào checklist đối soát: **"Đối tác xác nhận"** (Partner Confirm).

Checklist đối soát hiện tại đã có 4 mục kiểm tra tự động/thủ công. Giải pháp này thêm mục thứ 5 — đơn giản, không phá vỡ quy trình hiện tại.

### Checklist đối soát: trước và sau

| # | Mục kiểm tra | Cách đánh giá | Hiện tại | Mới |
|---|---|---|---|---|
| 1 | Video còn truy cập được? | Hệ thống tự kiểm tra | Co | Co |
| 2 | Hashtag đầy đủ? | Hệ thống tự kiểm tra | Co | Co |
| 3 | Lượt xem không giảm? | Hệ thống tự kiểm tra | Co | Co |
| 4 | Admin xác nhận | Ops kiểm tra thủ công | Co | Co |
| 5 | **Đối tác xác nhận** | **Thủ công / Tự động** | - | **Moi** |

---

## 3. Cách hoạt động

### Lần đối soát đầu tiên (content chưa từng được đối tác xác nhận)

```
Hệ thống chạy checklist tự động:
  ✅ Video truy cập được
  ✅ Hashtag đầy đủ
  ✅ Lượt xem ổn
  ✅ Admin xác nhận
  ⏳ Đối tác xác nhận → "Chờ xác nhận" (cần người duyệt thủ công)

→ Kết quả: "Cần xem xét" — chưa thể chốt thưởng
→ Ops gửi file đối soát cho đối tác → Đối tác phản hồi OK / Không OK cho từng bài
→ Ops cập nhật kết quả:
    • Đối tác OK → "Đối tác xác nhận" = Đạt → chốt thưởng bình thường
    • Đối tác không OK → "Đối tác xác nhận" = Chờ → KHÔNG chốt thưởng đợt này,
      nhưng bài đăng VẪN APPROVED, không bị hủy
      (có thể gửi lại cho đối tác ở đợt đối soát sau)
```

### Lần đối soát tiếp theo (content đã từng được đối tác xác nhận)

```
Hệ thống chạy checklist tự động:
  ✅ Video truy cập được
  ✅ Hashtag đầy đủ
  ✅ Lượt xem ổn
  ✅ Admin xác nhận
  ✅ Đối tác xác nhận → TỰ ĐỘNG ĐẠT (vì đã xác nhận ở lần trước)

→ Kết quả: "Tự động duyệt" — không cần gửi lại cho đối tác
→ Chốt thưởng nhanh hơn
```

### Điểm quan trọng

> **Đối tác không xác nhận ≠ bài bị hủy.**
> Bài đăng vẫn giữ trạng thái "đã duyệt" (approved). Chỉ là thưởng chưa được chốt ở đợt đối soát này. Bài có thể được gửi lại cho đối tác ở đợt sau.

### Tóm tắt logic

| Tình huống | Kết quả mục "Đối tác xác nhận" | Ảnh hưởng |
|---|---|---|
| Content **lần đầu** đối soát | ⏳ Chờ xác nhận | Cần Ops gửi đối tác duyệt |
| Đối tác **OK** | ✅ Đạt | Chốt thưởng bình thường |
| Đối tác **không OK** | ⏳ Giữ nguyên chờ | Không chốt thưởng đợt này, bài vẫn approved |
| Content **đã từng** được đối tác OK (cùng thử thách) | ✅ Tự động đạt | Không cần gửi lại |
| Content đã OK ở **thử thách khác** | ⏳ Chờ xác nhận | Mỗi thử thách xác nhận riêng |

---

## 4. Tác động đến các bên

### Đối với Influencer

- Bài được Ops duyệt → vẫn thấy **"Đã duyệt"** như bình thường
- Bài không được đối tác xác nhận → **không bị hủy**, Influencer không bị ảnh hưởng trực tiếp
- Sau khi đối tác xác nhận và chốt thưởng → nhận thưởng như bình thường
- Có thể hiển thị thêm trạng thái "Chờ đối soát" / "Đã xác nhận thưởng" nếu muốn tăng minh bạch (tùy chọn, không bắt buộc)

### Đối với Ops

- Quy trình đối soát thêm 1 bước: gửi đối tác xác nhận → cập nhật kết quả
- **Lần đầu**: cần gửi file và chờ phản hồi
- **Lần sau**: hệ thống tự động pass → giảm công việc
- Vẫn có thể dùng Quick Approve / Override như trước

### Đối với đối tác (Techcombank)

- Có tiếng nói chính thức trong quy trình đối soát
- Nhận file đối soát (Excel) → phản hồi approve/reject cho từng bài
- Không cần đăng nhập hệ thống (MVP: phản hồi qua email/file)

### Đối với hệ thống

- Thay đổi nhỏ: chỉ thêm 1 mục vào checklist, không thay đổi quy trình đối soát
- Không ảnh hưởng: trạng thái bài đăng, ngân sách, dòng tiền, thanh toán
- Tương thích ngược: dữ liệu cũ không bị ảnh hưởng

---

## 5. Quy trình vận hành đề xuất

### Bước 1: Ops hoàn tất đối soát nội bộ
- Tạo đợt đối soát
- Chạy checklist tự động (4 mục cũ tự evaluate)
- Duyệt/từ chối các mục cần review
- Mục "Đối tác xác nhận" sẽ ở trạng thái **Chờ** (trừ khi auto-pass)

### Bước 2: Gửi đối tác xác nhận
- Export file Excel đối soát (đã có sẵn chức năng)
- Gửi cho đối tác qua email/công cụ hiện tại
- Đối tác review và phản hồi: OK hoặc Không OK (kèm lý do) cho từng bài

### Bước 3: Cập nhật kết quả
- Ops nhận phản hồi từ đối tác
- Bài đối tác OK → cập nhật "Đối tác xác nhận" = Đạt → eligible chốt thưởng
- Bài đối tác không OK → giữ "Chờ xác nhận" → **không chốt thưởng đợt này, bài vẫn approved**
  - Bài này có thể được gửi lại cho đối tác ở đợt đối soát tiếp theo
  - Hoặc Ops có thể override nếu có thỏa thuận riêng

### Bước 4: Chốt thưởng
- Tất cả 5 mục checklist đã resolve
- Chốt thưởng và thanh toán như bình thường

---

## 6. Câu hỏi cần xác nhận

| # | Câu hỏi | Ghi chú |
|---|---|---|
| 1 | Đối tác phản hồi bằng cách nào? | MVP: qua file Excel/email. Sau: có thể làm portal riêng |
| 2 | Thời hạn đối tác phản hồi bao lâu? | Ví dụ: 7 ngày. Quá hạn thì xử lý thế nào? |
| 3 | Bài đối tác không OK → xử lý thế nào? | Đề xuất: giữ chờ, gửi lại đợt sau. Hay cần flow riêng? |
| 4 | Cần thông báo Influencer khi đối tác xác nhận không? | Giúp Influencer biết tiến độ, nhưng có thể phức tạp thêm |
| 5 | Scope auto-pass: cùng thử thách hay toàn hệ thống? | Đề xuất: cùng thử thách (mỗi thử thách xác nhận riêng) |

---

## 7. Lợi ích kỳ vọng

- **Đối tác có tiếng nói**: chính thức xác nhận từng bài trước khi chi tiền thưởng
- **Giảm rủi ro**: tránh trả thưởng cho content mà đối tác chưa đồng ý
- **Không hủy bài đăng**: đối tác không OK chỉ ảnh hưởng thưởng, không ảnh hưởng bài đăng đã duyệt
- **Tối ưu lần sau**: content đã xác nhận → auto-pass, giảm thời gian đối soát lặp lại
- **Không phá vỡ quy trình hiện tại**: chỉ thêm 1 bước kiểm tra, mọi thứ khác giữ nguyên
