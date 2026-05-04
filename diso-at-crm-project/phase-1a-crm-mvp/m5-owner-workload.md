# M5 — Phân công Sở hữu và Khối lượng Công việc

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/ams/am-phuong

---

## Mục đích

Khi pool creator scale lên hàng nghìn, câu hỏi "ai phụ trách creator này" trở thành vấn đề lớn. Phân công sai dẫn đến creator bị bỏ rơi (không ai quan tâm) hoặc bị chăm sóc trùng (hai người cùng nhắn). Phân công không cân bằng dẫn đến một số người phụ trách quá tải, một số khác rảnh.

Module M5 giải quyết hai bài toán: phân công đúng người (theo chuyên môn ngành, theo tier creator) và cân bằng tải (không ai bị quá tải).

Module này cũng là nền móng cho việc đo lường hiệu suất từng người phụ trách, làm dữ liệu cho các quyết định nhân sự sau này.

---

## Người dùng chính

- **Trưởng nhóm Creator Care:** Cấu hình quy tắc phân công, theo dõi tải mỗi người
- **Người phụ trách:** Nhìn thấy danh sách creator dưới quyền, biết khả năng của mình
- **Hệ thống tự động:** Phân công các creator mới đến theo quy tắc đã cấu hình

---

## Câu chuyện sử dụng

Trưởng nhóm Phương cấu hình quy tắc cho M5: creator ngành mỹ phẩm được ưu tiên phân cho Linh và Trang vì họ chuyên ngành này. Creator tier VIP Candidate được ưu tiên phân cho Senior Care.

Khi @beautyquynh đăng ký, M5 đọc thông tin: ngành Beauty + tier dự đoán VIP Candidate. M5 chọn Linh (Senior Care chuyên Beauty). Kiểm tra workload Linh: cô đang phụ trách bốn mươi bảy creator, chưa vượt cap năm mươi. M5 phân Quỳnh cho Linh.

Trong tuần, ba mươi creator mới đăng ký. M5 phân tự động theo quy tắc, phân bổ đều giữa năm người phụ trách. Không ai vượt quá năm mươi creator.

Cuối tuần, Phương vào dashboard xem báo cáo. Cô thấy Linh có 12 VIP Candidate trong khi Trang chỉ có 5. Tải VIP của Linh đang cao. Cô điều chỉnh quy tắc để tuần tới chia đều hơn.

Khi Mai (một người phụ trách) thông báo nghỉ việc, M5 đánh dấu cô ở trạng thái "offboarding". Mọi creator của cô được flag để chuẩn bị bàn giao trong Giai đoạn 1B.

---

## Tính năng cốt lõi

### Danh sách người phụ trách (roster)
- Lưu thông tin tất cả người phụ trách: tên, vai trò (Care, Senior, Lead, BD, Compliance), ngành chuyên môn, ngày gia nhập
- Trạng thái: active, đang nghỉ phép, đang offboarding, đã rời

### Quy tắc phân công tự động
- Cấu hình theo nhiều tiêu chí: ngành creator, tier dự đoán, brand pool
- Ví dụ: "Creator ngành Beauty + VIP Candidate → ưu tiên Linh, Trang"
- Ví dụ: "Creator pool TCB → chỉ phân cho người đã được training về banking"

### Bộ cân bằng tải
- Cap tối đa số creator active mỗi người phụ trách (mặc định 50, có thể điều chỉnh)
- Cap riêng cho VIP Candidate (mặc định 12 mỗi người)
- Khi một người vượt cap, hệ thống chuyển creator tiếp theo cho người khác
- Tự động phân bổ lại khi có người nghỉ phép

### Chuyển giao quyền sở hữu
- Cho phép chuyển creator từ người này sang người khác
- Yêu cầu ghi chú lý do chuyển
- Lưu lịch sử để Giai đoạn 1B (M16) xử lý anti-poach
- Tự động thông báo cho cả người chuyển và người nhận

### Đo lường hiệu suất từng người phụ trách
- Số creator đang quản lý (active queue)
- Số VIP Candidate dưới quyền
- Tỷ lệ đáp ứng SLA (sẽ tích hợp với M4 ở Giai đoạn 1B)
- Tỷ lệ chuyển đổi VIP Candidate sang VIP Confirmed
- GMV tạo ra qua các creator dưới quyền (lấy từ ambassador feed)

### Quản lý vắng mặt và offboarding
- Khi người phụ trách nghỉ phép tạm thời, các creator của họ được route tạm thời cho người khác
- Khi nghỉ việc chính thức, kích hoạt luồng offboarding (chi tiết trong M16 ở Giai đoạn 1B)

---

## Tích hợp

- **Với M1 Creator Identity:** Lưu quan hệ ownership giữa creator và người phụ trách
- **Với M2 Lifecycle:** Khi creator chuyển trạng thái cần kỹ năng cao hơn, M5 đề xuất chuyển sang Senior Care
- **Với M3 Tier Engine (Giai đoạn 1B):** Sử dụng tier để quyết định phân công
- **Với M6 Task Console:** Mỗi người phụ trách chỉ thấy creator của mình trong queue
- **Với M16 Relationship Vault (Giai đoạn 1B):** Lịch sử ownership và workflow chuyển giao là nền móng cho anti-poach

---

## Đo lường thành công

- Tỷ lệ creator được phân công trong vòng 24 giờ sau khi vào hệ thống, mục tiêu trên 90%
- Độ lệch chuẩn workload giữa các người phụ trách (càng thấp càng tốt)
- Tỷ lệ chuyển giao thành công khi người phụ trách nghỉ phép, mục tiêu 100%
- Sự hài lòng của người phụ trách với phân công (khảo sát hằng tháng)

---

## Liên quan trong demo

- **AM Detail (Lead view):** https://vcreator.demo.accesstrade.click/mockup/ams/am-phuong
- Trên trang này, có thể xem KPI từng người phụ trách, KOC pool dưới quyền, tỷ lệ tuân thủ SLA
- Phía dưới có sidebar "Switch view" cho phép xem các người phụ trách khác
