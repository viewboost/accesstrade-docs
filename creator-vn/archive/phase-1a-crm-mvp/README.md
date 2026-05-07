# Giai đoạn 1A — CRM Phiên bản Khả dụng Tối thiểu

> **Thời gian:** Tuần 3 đến Tuần 6 (15/5 → 15/6/2026)
> **Demo CRM:** https://vcreator.demo.accesstrade.click/mockup

---

## Bối cảnh

Sau sự kiện ngày 7/5, AccessTrade kỳ vọng có hơn năm trăm creator mới đăng ký. Nếu không có CRM, việc quản lý số creator này bằng Excel sẽ vỡ trận trong vài ngày: ai phụ trách creator nào, đã liên hệ chưa, đang ở giai đoạn nào của quy trình V2 — không ai biết rõ.

Giai đoạn 1A xây dựng phiên bản tối thiểu của CRM, đủ để toàn bộ đội Creator Care chuyển sang sử dụng và bỏ Excel. Mục tiêu cuối giai đoạn là không còn ai trong đội phải mở bảng tính.

Đây là phiên bản nền móng. Các tính năng nâng cao như chấm điểm tự động, đồng hồ SLA, bảo vệ quan hệ sẽ được bổ sung trong Giai đoạn 1B.

---

## Bảy module triển khai

| Module | Tên ngắn | Mục đích chính |
|---|---|---|
| [M1](./m1-creator-identity.md) | Quản lý Định danh Creator | Lưu hồ sơ creator chuẩn hóa, đồng bộ với influence-meter |
| [M2](./m2-lifecycle.md) | Vòng đời Quản lý đa luồng | Theo dõi creator đang ở bước nào trong bảy quy trình V2 |
| [M5](./m5-owner-workload.md) | Phân công Sở hữu và Khối lượng Công việc | Phân công người phụ trách phù hợp, cân bằng tải |
| [M6](./m6-task-console.md) | Hộp thoại Tác vụ | Giao diện chính người phụ trách làm việc hằng ngày |
| [M7](./m7-outreach-comm.md) | Lưu trữ Trao đổi | Mọi tin nhắn và cuộc gọi với creator được lưu tập trung |
| [M13](./m13-multi-tenant.md) | Đa Thuê bao và Phân quyền | Nền móng phân quyền theo vai trò |
| [M14](./m14-notification.md) | Thông báo và Cảnh báo | Hệ thống nhắc việc trong ứng dụng và qua email |

---

## Câu chuyện một ngày của người phụ trách (sau Giai đoạn 1A)

Buổi sáng, Linh là người phụ trách Senior Care đăng nhập CRM. Cô vào "My Queue" để xem hàng đợi tác vụ hôm nay.

Trong hàng đợi cô thấy bốn mươi bảy creator đang chờ cô xử lý, được sắp xếp theo độ ưu tiên (creator VIP Candidate ở đầu). Cô bấm vào @beautyquynh, hệ thống mở trang chi tiết creator — trang chi tiết hiển thị toàn bộ thông tin: tên, ngành, số follower, đang ở bước nào của quy trình V2, lịch sử tin nhắn với cô.

Cô bấm "Mở chat", trang Conversation hiện ra với toàn bộ lịch sử tin nhắn Zalo OA giữa cô và creator. Cô gõ phản hồi mới qua giao diện CRM, tin nhắn được gửi qua Zalo OA và lưu lại trong hệ thống.

Buổi trưa, Linh đi ăn. Trong khi cô vắng mặt, một creator mới được hệ thống tự động phân cho cô vì cô có khoảng trống công việc và là chuyên gia ngành mỹ phẩm.

Buổi chiều, cô check thông báo — có một creator vừa hoàn thành onboarding, một creator phản hồi tin nhắn của cô. Mọi thứ đã ở đúng chỗ trong CRM, không cần mở Zalo cá nhân hay Excel.

Cô không bao giờ phải mở Excel nữa.

---

## Tích hợp tổng thể

Bảy module phối hợp với nhau theo dòng chảy:

```
Creator đăng ký từ sự kiện (Phase 0)
        ↓
M1 ghi nhận hồ sơ + đồng bộ với influence-meter
        ↓
M2 đặt creator vào trạng thái "New"
        ↓
M5 tự động phân công người phụ trách phù hợp ngành
        ↓
M14 gửi thông báo tới người phụ trách
        ↓
Người phụ trách vào M6 Task Console xem hàng đợi
        ↓
Bấm vào creator → mở trang chi tiết creator (M1 + M2 hiển thị)
        ↓
Bấm "Open chat" → vào M7 Conversation Thread
        ↓
Phản hồi creator → tin nhắn lưu lại trong M7
        ↓
M2 cập nhật trạng thái creator (Contacted, Applied, Approved...)
        ↓
M14 gửi thông báo cho các bước tiếp theo
        ↓
M13 đảm bảo người phụ trách chỉ thấy creator của mình (trừ Lead)
```

---

## Mục tiêu đo lường giai đoạn

| Chỉ số | Mục tiêu |
|---|---|
| Năng suất xử lý của mỗi người phụ trách (so với Excel) | Tăng gấp 2× |
| Tỷ lệ creator được phân công trong vòng 24 giờ | Trên 90% |
| Tỷ lệ áp dụng của đội Creator Care | 100% (không ai dùng Excel) |
| Tỷ lệ tập trung hóa trao đổi vào hệ thống | Trên 95% |

---

## Vai trò liên quan

- **Người phụ trách (Creator Care):** Người dùng chính hằng ngày, thao tác trên M6 Task Console
- **Người phụ trách cấp cao (Senior Care):** Chuyên xử lý creator VIP Candidate
- **Trưởng nhóm (Lead):** Theo dõi tổng thể, có quyền xem creator của tất cả người phụ trách
- **Đội Diso:** Vận hành hệ thống, hỗ trợ kỹ thuật, đào tạo team Care

---

## Liên quan trong demo

- **Demo Hub:** https://vcreator.demo.accesstrade.click/mockup
- **Creator List:** https://vcreator.demo.accesstrade.click/mockup/creators
- **Trang chi tiết creator:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- **My Queue (M6):** https://vcreator.demo.accesstrade.click/mockup/console
- **Conversation Thread (M7):** https://vcreator.demo.accesstrade.click/mockup/conversations/conv-beautyquynh-1
