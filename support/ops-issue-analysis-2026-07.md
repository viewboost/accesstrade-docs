# Report tuần 27/07 → 31/07/2026 — Phân tích issue tháng 7 & Đề xuất tính năng cho Ops

## 2. Phân tích issue tháng 7 — nhóm sự cố tái diễn

> Toàn bộ ~229 record mang ngày import 27/7 (không phải ngày phát sinh thật) → lọc theo nội dung. **Đề xuất bổ sung cột "Ngày phát sinh thật" để thống kê chính xác.**

| Nhóm sự cố | Số ca T7 | Tần suất | Playbook |
|---|---|---|---|
| **Lệch view / đối soát / thông số** (content ≠ đối soát ≠ landing, đếm trùng, đứt chuỗi) | ~18 | 🔴 Rất cao | PB-1 |
| **View có tính nhưng không cộng thưởng / thiếu tiền** (miss reward, hết budget, tạm tính sai) | ~9 | 🔴 Cao | PB-3 |
| **Liên kết tài khoản / crawl profile** (không LK được TikTok/Threads/FB, báo trùng, phải F5) | ~11 | 🔴 Cao | PB-4 |
| **Nộp bài / crawler vendor failed** (FB 28% / TikTok 10% / Threads 3% / YT ~2%) | ~8 | 🟠 Cao | PB-4 |
| **HĐ / eKYC / đồng bộ thông tin** (tên sai, ký lại, hủy HĐ, trùng CCCD) | ~12 | 🟠 Cao | PB-5, PB-11 |
| **Thanh toán / rút tiền** (không đổi trạng thái, trùng kỳ T4→T5, thiếu tên NH) | ~7 | 🔴 Cao (tài chính) | PB-8 |
| **Duyệt/Hủy hàng loạt không chạy** (bulk action không feedback) | ~4 | 🟡 TB | PB-2 |
| **FE partner / "Có lỗi xảy ra" / hiển thị** (token session, avatar/cover/logo, BXH) | ~13 | 🟠 Cao | PB-6, PB-7, PB-10 |

> 📌 **Nhận định:** Đây không phải sự cố ngẫu nhiên — 4 nhóm (lệch view, thiếu thưởng, liên kết TK, HĐ/eKYC) tái phát xuyên suốt tháng trên nhiều partner khác nhau (Lusso, Parkway, Katinat, Aristino, Flamingo, VPBank, Parasola…). Bản chất là **lỗi nền tảng crawl/đối soát**, không phải cấu hình lẻ → cần xử lý gốc thay vì migration thủ công từng ca.

---

## 3. Đề xuất tính năng để Ops tự kiểm tra (giảm log lên board Technical)

| Mã | Tính năng | Xóa/giảm nhóm | Ưu tiên |
|---|---|---|---|
| **R1** | **Job audit lệch view tự động** · cảnh báo (so 3 nguồn: nội dung ↔ đối soát ↔ thông số) | Lệch view + thiếu thưởng | 🔴 P0 |
| **R3** | **Cột "View được tính thưởng"** trong mọi file export đối soát | Ops tự giải thích partner | 🔴 P0/P1 |
| **R8** | **Fix gốc RT kẹt Nháp** (đồng bộ field `at`) + job đối chiếu thanh toán trùng kỳ + acc read-only | Thanh toán trùng / RT kẹt | 🔴 P0 (tài chính) |

> 🔎 **R8 — Nguyên nhân gốc đã xác định:** File RT treo mãi ở trạng thái **Nháp** là do user **thiếu field `at`** trong bảng `user` — vì user liên kết tài khoản `at` ở **màn Liên kết** thay vì **màn ký hợp đồng**. → Cần đồng bộ field `at` cho **cả 2 luồng** + **migrate** cho các user đang thiếu `at` để gỡ các RT đang kẹt.

> 💡 Cột **"Đã tham khảo playbook nào chưa"** đã có sẵn trên board nhưng đang trống → đề xuất bắt buộc Ops điền để đo hiệu quả playbook (không tốn dev).
