# Hướng dẫn Operation — Bật OpsHub và Duyệt Video trên vCreator

**Cập nhật:** 2026-04-07

---

## Tổng quan

OpsHub là hệ thống kiểm duyệt video tự động bằng AI. Khi bật OpsHub cho một Event trên vCreator, mỗi video mới từ creator sẽ tự động được gửi sang OpsHub để kiểm tra. Kết quả duyệt (duyệt / từ chối / yêu cầu chỉnh sửa) sẽ được trả về vCreator.

---

## Phần 1: Bật OpsHub cho Event

### Điều kiện trước

- Đã có Campaign tương ứng trên OpsHub (liên hệ Admin OpsHub để tạo)
- Có **Campaign ID** (chuỗi ObjectID từ OpsHub, VD: `69c1a2b3c4d5e6f7a8b9c0d1`)

### Các bước setup

1. Đăng nhập **vCreator Admin** (admin.gen-green.global)
2. Vào menu **Event** → chọn Event cần bật OpsHub
3. Vào tab **OpsHub**
4. Cấu hình 3 mục:

#### Gửi nội dung sang OpsHub để review

Bật toggle **ON** để kích hoạt. Khi bật, mọi video mới crawl được trong Event này sẽ tự động gửi sang OpsHub.

#### Campaign ID

Nhập Campaign ID từ OpsHub. Đây là mã liên kết giữa Event trên vCreator và Campaign trên OpsHub.

Nếu không nhập, hệ thống sẽ dùng Project ID mặc định (không khuyến nghị vì mỗi Event nên có campaign riêng).

#### Tự động đổi trạng thái nội dung theo kết quả OpsHub

- **Bật ON:** Khi OpsHub trả kết quả, vCreator tự động cập nhật trạng thái content:
  - OpsHub duyệt → Content chuyển sang **Approved**
  - OpsHub từ chối → Content chuyển sang **Rejected** (kèm lý do)
- **Tắt OFF:** Kết quả OpsHub chỉ gắn tag lên content, không thay đổi trạng thái. Operation phải duyệt thủ công.

**Khuyến nghị:** Giai đoạn đầu nên **tắt** để theo dõi kết quả AI trước. Khi đã tin tưởng độ chính xác thì bật lên.

5. Bấm **Lưu**

---

## Phần 2: Video được xử lý như thế nào

Sau khi bật OpsHub, flow xử lý video diễn ra tự động:

**Bước 1:** Hệ thống crawl được video mới từ creator

**Bước 2:** vCreator tự động gửi video sang OpsHub (kèm link video, caption, hashtag, thông tin creator...)

**Bước 3:** OpsHub kiểm tra:
- Kiểm tra tự động (thời lượng, hashtag, format...) — dưới 1 giây
- AI phân tích nội dung video (xem video, nghe lời nói, đọc caption) — khoảng 30 giây

**Bước 4:** OpsHub trả kết quả về vCreator:
- **Duyệt tự động** → Gắn tag "OpsHub: Auto Approved" (xanh lá)
- **Từ chối tự động** → Gắn tag "OpsHub: Auto Rejected" (đỏ)
- **Cần người duyệt** → Gắn tag sau khi người duyệt trên OpsHub ra quyết định

### Các tag OpsHub trên vCreator

| Tag | Màu | Ý nghĩa |
|-----|-----|---------|
| OpsHub: Auto Approved | Xanh lá | AI + hệ thống tự duyệt |
| OpsHub: Auto Rejected | Đỏ | Hệ thống tự từ chối (vi phạm rõ ràng) |
| OpsHub: Approved | Xanh dương | Người duyệt trên OpsHub đã duyệt |
| OpsHub: Rejected | Hồng | Người duyệt trên OpsHub đã từ chối |
| OpsHub: Request Edit | Cam | Yêu cầu creator chỉnh sửa lại |
| OpsHub: SLA Violated | Tím | Video quá hạn chưa được duyệt |

---

## Phần 3: Xem kết quả duyệt

### Trên danh sách Content

Lọc content theo tag OpsHub để xem nhanh:
- Lọc tag "OpsHub: Auto Rejected" → xem video bị AI từ chối
- Lọc tag "OpsHub: Approved" → xem video đã được duyệt

### Trên chi tiết Content

Mỗi content đã gửi qua OpsHub sẽ có thông tin bổ sung:
- **Verdict:** Kết quả duyệt cuối cùng (approved/rejected)
- **Summary:** Lý do duyệt/từ chối bằng tiếng Việt
- **Feedback to Creator:** Góp ý cho creator (nếu có)

Khi tự động đổi trạng thái bật, content bị từ chối sẽ hiển thị lý do từ chối trong phần trạng thái.

---

## Phần 4: Xử lý các tình huống

### Video bị từ chối sai

1. Vào OpsHub Dashboard → tìm video theo tên/link
2. Xem chi tiết kết quả AI → xác định AI sai ở đâu
3. Nếu cần: liên hệ Admin OpsHub điều chỉnh template (hạ ngưỡng tin cậy, sửa key messages)
4. Bấm **Retry AI** trên OpsHub để chạy lại

### Quá nhiều video cần người duyệt

Nguyên nhân: Ngưỡng tin cậy AI (AI Confidence Threshold) đang cao → AI không đủ tự tin để tự duyệt.

Giải pháp: Liên hệ Admin OpsHub hạ threshold (VD: từ 0.85 xuống 0.70).

### Video bị stuck "AI Processing"

Có thể AI bị lỗi tạm thời (hết quota, timeout). Vào OpsHub Dashboard → bấm **Retry AI**.

### Thay đổi thể lệ campaign

Khi thể lệ thay đổi, cần cập nhật template trên OpsHub:
1. Liên hệ Admin OpsHub
2. Admin tạo template version mới với key messages cập nhật
3. Activate template mới
4. Video mới sẽ dùng template mới, video cũ không bị ảnh hưởng

---

## Checklist cho Operation

- [ ] Nhận Campaign ID từ Admin OpsHub
- [ ] Vào vCreator Admin → Event → tab OpsHub → bật toggle + nhập Campaign ID
- [ ] Quyết định bật/tắt "Tự động đổi trạng thái" (khuyến nghị: tắt giai đoạn đầu)
- [ ] Bấm Lưu
- [ ] Test: chờ 1-2 video mới crawl → kiểm tra tag OpsHub có xuất hiện
- [ ] Theo dõi kết quả AI 1-2 ngày → đánh giá độ chính xác
- [ ] Nếu OK → bật "Tự động đổi trạng thái"

---

*Tài liệu tổng quan: [overview.md](overview.md) | Tài liệu tích hợp developer: [guide-developer-integration.md](guide-developer-integration.md)*
