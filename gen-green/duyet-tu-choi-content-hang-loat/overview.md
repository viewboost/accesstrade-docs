# Duyệt/Từ chối content hàng loạt — chạy nền (fix "tính năng không chạy")

> Duyệt/từ chối nhiều content cùng lúc trên admin bằng **job chạy nền** thay vì xử lý đồng bộ trong 1 request. Giải quyết lỗi task #8: bấm duyệt/từ chối hàng loạt nhưng content vẫn "chờ duyệt", lỗi lúc gặp lúc không và ngày càng nhiều.

**Ngày:** 17/07/2026
**Trạng thái:** Đã implement (PR #125 → `develop`)
**Đối tượng đọc:** Business, Ops (đội duyệt content), PM, Tech
**Phạm vi:** Module content management — Gen-Green admin

---

## 1. Bối cảnh — duyệt/từ chối hàng loạt "không ăn"

Trên trang **Danh sách content**, Ops chọn nhiều content (tick checkbox) rồi bấm **Duyệt** / **Từ chối** hàng loạt. Nhưng:

- Thao tác **lúc chạy lúc không** — nhiều content vẫn giữ trạng thái **"chờ duyệt"** sau khi bấm.
- Gần đây **tần suất lỗi tăng cao** → đội duyệt mất nhiều thời gian, phải bấm lại từng cái.
- Không biết **content nào** bị lỗi để xử lý lại → phải nhờ tech tra log.

> Ví dụ thực tế (task #8): lô lớn bấm 1 phát, một phần content đổi trạng thái, phần còn lại kẹt "chờ duyệt" mà không có thông báo lỗi rõ ràng — nhìn như "tính năng không chạy".

---

## 2. Vì sao lỗi? — timeout cắt ngang giữa chừng

Cơ chế cũ chạy **đồng bộ trong 1 HTTP request**: bấm hàng loạt → server lặp xử lý từng content ngay trong request đó. Mỗi content lại kéo theo nhiều việc nặng (thu hồi thưởng, cập nhật thống kê, xoá cache, gửi thông báo, recheck cấu hình sự kiện).

→ Lô càng lớn, request càng lâu → **vượt timeout** của hạ tầng → kết nối bị ngắt giữa chừng → các content **chưa xử lý tới** bị bỏ dở, giữ nguyên "chờ duyệt".

- **Lúc gặp lúc không:** chỉ dính khi lô đủ lớn/hệ thống đủ tải để chạm timeout.
- **Tần suất tăng:** data ngày càng nhiều → chọn nhiều content/lần + thao tác xoá cache chậm dần → càng hay chạm timeout.

---

## 3. Có gì đổi?

### 1. Xử lý chạy nền — không còn phụ thuộc timeout

Bấm duyệt/từ chối hàng loạt → hệ thống **tạo 1 job** rồi trả về ngay. Việc xử lý từng content chạy **ngầm phía sau** (không nằm trong request của người dùng) nên **timeout không cắt được** → không còn cảnh xử lý dở dang.

### 2. Thanh tiến độ

Sau khi bấm, admin thấy **tiến độ "X/Y content"** cập nhật liên tục — biết chắc hệ thống đang chạy, không còn "bấm xong đứng hình rồi tưởng hỏng".

### 3. Danh sách content lỗi + lý do

Khi xong, nếu có content xử lý lỗi, hệ thống **hiện popup liệt kê chính xác content nào lỗi + lý do** (vd: thuộc đối tác khác, content không tồn tại). Đúng thứ đội Ops cần: biết cái nào fail để xử lý lại, không phải nhờ tech tra log.

### 4. Không đổi thao tác quen thuộc

Nút bấm, cách chọn content, popup nhập lý do khi từ chối — **giữ nguyên**. Chỉ khác ở chỗ chạy nền + có tiến độ + có danh sách lỗi.

---

## 4. Lợi ích kỳ vọng

### Cho Ops
- ✅ Duyệt/từ chối lô lớn **không còn kẹt "chờ duyệt"** — làm 1 lần là xong.
- ✅ Thấy tiến độ rõ ràng, không phải đoán.
- ✅ Biết chính xác content nào lỗi + lý do → xử lý lại đúng chỗ.

### Cho vận hành (Tech)
- ✅ Không còn phụ thuộc timeout hạ tầng → hết class lỗi "batch không chạy".
- ✅ Tái dùng đúng logic duyệt/từ chối lẻ hiện có (giữ nguyên side-effect thưởng/thông báo/thống kê).
- ✅ Ít phải hỗ trợ tra log thủ công cho Ops.

### Cho người tạo content (Creator)
- ✅ Content được duyệt/từ chối đầy đủ, không sót → trạng thái đúng, nhận thông báo đúng.

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Dev backend (collection job + service chạy nền + API) | 6–8h |
| Dev frontend (gọi API mới + poll tiến độ + popup lỗi) | 3–4h |
| QA (lô nhỏ, lô lớn >50, cross-partner, double-click) | 3h |
| Tổng | ~1.5–2 ngày công |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Job chết giữa chừng (pod restart) | TB | Redis mutex + heartbeat; job không heartbeat coi như chết, không kẹt |
| Double-click tạo 2 job cùng danh sách | Thấp | Idempotent: content đã đúng trạng thái thì bỏ qua (còn khe hẹp gửi thông báo trùng — xem §7) |
| Lô quá lớn gây quá tải | Thấp | Giới hạn 2000 content/lần; nghỉ giữa các lô cho side-effect kịp xử lý |
| Content thuộc đối tác khác | Thấp | Không chặn cả lô; đưa vào danh sách lỗi với lý do rõ ràng |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi:**

- Duyệt/từ chối content **lẻ** (1 content) — giữ nguyên.
- Logic tính thưởng, thông báo, thống kê khi đổi trạng thái — tái dùng nguyên, không sửa.
- Import CSV hủy content hàng loạt (feature khác) — chạy độc lập.
- Cấu trúc bảng content — chỉ thêm 1 collection job mới, không đụng content.
- Endpoint duyệt hàng loạt cũ vẫn còn (chưa gỡ) — gỡ sau khi bản mới chạy ổn.

---

## 7. Câu hỏi còn để ngỏ

1. **Gỡ endpoint cũ** `/contents/batch-status`: gỡ sau khi FE mới chạy ổn định bao lâu?
2. **Chặn double-click**: có cần disable nút khi job đang chạy (đóng luôn khe thông báo trùng) + nút copy danh sách ID lỗi cho Ops không?
3. **Đưa lên main**: bản này đang ở `develop`. Có cần đưa lên `main` (cùng đợt với import-content-to-reject) hay để develop là đủ?
4. **Giới hạn 2000 content/lần** đã hợp lý chưa, hay Ops thường thao tác lớn hơn?

---

## 8. Tài liệu liên quan

- **Pattern tham chiếu:** [Import file để hủy hàng loạt content](../import-content-to-reject/overview.md) — cơ chế "apply chạy nền theo lô" được tái dùng (bỏ phần upload/preview).
- **Tech Spec:** [`tech-spec.md`](./tech-spec.md)
- **PR:** `Vin-VCreator/vcreator#125` (→ `develop`)
- **Task:** #8 — "Tính năng duyệt hàng loạt → lỗi tính năng không chạy"
