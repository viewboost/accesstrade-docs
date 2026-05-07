# Lớp 4 — Hộp thư Tìm kiếm

---

## Mục đích

Lớp 4 là giao diện chính cho người phụ trách Lead Care và Compliance review các creator đang chờ outreach. Giống như M6 Task Console ở Phase 1A, nhưng dành cho creator chưa được liên hệ lần nào (chưa có owner, chưa có lịch sử trong AT).

Mỗi BD request sau khi được approve sẽ tạo ra một batch creator chờ outreach. Sourcing Inbox hiển thị tất cả batch này, cho phép Lead review nhanh, chỉnh sửa, hoặc reject trước khi push xuống Lớp 5 outreach.

---

## Người dùng chính

- **Lead Care:** Review các batch outreach từ BD, đảm bảo chất lượng
- **Compliance:** Sample audit các creator có flag rủi ro
- **BD:** Theo dõi trạng thái batch của mình

---

## Câu chuyện sử dụng

Đức (BD) submit request "50 creator beauty 50K-200K cho Innisfree". Hệ thống AI suggest 150, Đức chọn 75, push approval. 

Lead Phương vào Sourcing Inbox, thấy batch mới "BD-Innisfree-2026-07-20" với 75 creator chờ review. Cô bấm vào batch.

Trang detail hiển thị 75 creator dạng list:
- Mỗi creator có thumbnail, handle, score breakdown
- Filter theo ngành, follower range, score
- Bulk actions: approve all, reject some, request more info

Cô review nhanh, thấy 5 creator có flag brand-safety (pass scan AT nhưng vẫn cảnh báo). Cô bấm "Send to Compliance for review" cho 5 creator này. 70 creator còn lại cô bấm "Approve for outreach".

Compliance Bảo vào tab "Pending review", thấy 5 creator. Anh review từng người. 4 OK, 1 thực sự có vấn đề (creator có scandal cũ). Anh approve 4, reject 1 với lý do "scandal Q2 2024 chưa rõ giải quyết".

Cuối cùng có 74 creator được approve, push vào Lớp 5 outreach queue.

---

## Tính năng cốt lõi

### Danh sách lead theo batch
- Mỗi BD request = một batch riêng
- Filter theo ngành, tier, status
- Search theo handle hoặc tên

### BD review queue
- Tất cả batch đang chờ Lead approve
- Sắp xếp theo deadline (BD đã đặt thời hạn)
- Cảnh báo batch sắp vỡ deadline

### Approval cascade
- Lead Care review (24h SLA)
- Compliance check tự động (auto-pass theo rule)
- Sample manual cho 10% trường hợp
- Brand approval optional (nếu campaign cụ thể yêu cầu)

### Bulk actions
- Approve all với một lần bấm
- Reject hàng loạt với lý do
- Re-route sang BD khác

### Sourcing history
- Lưu lại tất cả batch đã xử lý
- Theo dõi tỷ lệ approve/reject theo BD
- Dùng để cải thiện AI suggestion

### Performance tracking
- Số batch processed theo tuần
- Thời gian xử lý trung bình
- Tỷ lệ creator approve

---

## Đo lường

- Thời gian từ khi BD submit đến khi outreach gửi đi, mục tiêu dưới 24 giờ
- Tỷ lệ creator approve sau review, mục tiêu trên 80%
- Tỷ lệ Compliance flag vấn đề thực sự, theo dõi để cải thiện auto-pass rule
