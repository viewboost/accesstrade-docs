# M1 — Quản lý Định danh Creator

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/creators

---

## Mục đích

Module M1 là nền móng dữ liệu của toàn bộ CRM. Mọi module khác đều cần biết "creator này là ai", và M1 chính là nơi trả lời câu hỏi đó.

Khác với một bảng dữ liệu thông thường, M1 không lưu trữ toàn bộ thông tin chi tiết của creator (việc đó đã có influence-meter làm). Thay vào đó, M1 đóng vai trò một bộ kết nối nhẹ: lưu ID creator, các mã định danh trên các nền tảng (Shopee, TikTok, Meta), người phụ trách hiện tại, và các thẻ thuộc workflow.

Cách phân tách này cho phép hai đội độc lập làm việc: đội influence-meter tiếp tục cải thiện chất lượng dữ liệu chấm điểm, còn đội CRM tập trung vào quy trình chăm sóc creator, không bị bottleneck lẫn nhau.

---

## Người dùng chính

Module M1 hoạt động ngầm phía sau, không có giao diện riêng cho người dùng cuối. Tuy nhiên, dữ liệu của M1 được sử dụng bởi mọi vai trò:

- Người phụ trách Care xem hồ sơ creator
- Trưởng nhóm tìm kiếm và lọc creator
- BD truy vấn creator phù hợp campaign

---

## Câu chuyện sử dụng

Khi creator @beautyquynh đăng ký từ sự kiện, hệ thống ngay lập tức gọi M1 để tạo bản ghi mới. M1 nhận thông tin tối thiểu (handle, số điện thoại, email), sau đó gọi sang influence-meter để truy xuất thêm dữ liệu công khai: số follower thật, ngành hàng, engagement rate.

Sau khi influence-meter trả về dữ liệu, M1 cache lại các trường cần thiết cho workflow CRM (hiển thị trong trang chi tiết creator, dùng để chấm điểm). Các trường khác như chi tiết audience demographics vẫn ở influence-meter, M1 chỉ truy xuất khi thực sự cần.

Khi creator được phân công cho người phụ trách Linh, M1 ghi nhận quan hệ "creator này thuộc Linh". Khi Linh chuyển công việc cho người khác, M1 cập nhật đồng thời lưu lịch sử để phục vụ tính năng chống mất quan hệ trong M16 ở Giai đoạn 1B.

---

## Tính năng cốt lõi

### Lưu trữ định danh tối thiểu
- Tên creator, handle các kênh chính
- Số điện thoại, email
- Avatar và thông tin hiển thị cơ bản
- Ngày gia nhập hệ thống AccessTrade

### Đồng bộ với influence-meter
- Tự động gọi influence-meter khi tạo creator mới
- Truy xuất các trường cần cho workflow (follower, ngành, engagement, brand-safety)
- Cache trong CRM để hiển thị nhanh
- Đồng bộ lại định kỳ (hằng tuần) để cập nhật số liệu mới

### Quản lý mã định danh trên các nền tảng
- AccessTrade Publisher ID
- Shopee Affiliate ID
- TikTok TAP ID
- Meta Business ID
- MCN affiliation
- Các mã này được lưu để các module khác sử dụng khi cần đối chiếu giữa các hệ thống

### Theo dõi quyền sở hữu
- Người phụ trách hiện tại của creator
- Lịch sử thay đổi người phụ trách (ai từng quản lý, từ khi nào đến khi nào, lý do chuyển)
- Thuộc nhóm pool nào (general, TCB pool, VinFast pool)

### Hệ thống thẻ workflow
- Các thẻ phục vụ vận hành CRM (đang trong campaign nào, status gì)
- Khác với thẻ thông tin profile (do influence-meter quản lý)
- Cho phép lọc và tìm kiếm theo workflow context

### Resolver giải quyết xung đột dữ liệu
- Khi influence-meter cập nhật số follower mới, M1 nhận event để re-tier creator
- Khi creator tự sửa thông tin trên Welcome Page, M1 đồng bộ ngược lại influence-meter
- Tránh tình trạng dữ liệu lệch giữa hai hệ thống

---

## Tích hợp

- **Với influence-meter:** Đồng bộ hai chiều dữ liệu hồ sơ creator. influence-meter là nguồn sự thật về dữ liệu profile, M1 là nguồn sự thật về context CRM
- **Với M3 Tier Engine:** Cung cấp dữ liệu hồ sơ để chấm điểm phân hạng
- **Với M5 Owner Workload:** Cung cấp thông tin ngành để phân công đúng người chuyên môn
- **Với M16 Relationship Vault (Giai đoạn 1B):** Cung cấp lịch sử ownership để theo dõi tài sản quan hệ
- **Với ambassador.koc.com.vn:** Lấy danh sách chiến dịch creator đang tham gia (chỉ đọc, không quản lý)

---

## Đo lường thành công

- Tỷ lệ đồng bộ thành công với influence-meter, mục tiêu trên 99%
- Thời gian từ khi creator đăng ký đến khi sẵn sàng trong CRM, mục tiêu dưới 30 giây
- Số lượng creator được lưu trong CRM (theo dõi tăng trưởng pool)
- Tỷ lệ trùng lặp dữ liệu, mục tiêu dưới 1%

---

## Liên quan trong demo

- **Creator List:** https://vcreator.demo.accesstrade.click/mockup/creators
- **Trang chi tiết creator:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- Trên trang chi tiết creator, phần "Profile" và "Identity" là dữ liệu của M1 (đồng bộ từ influence-meter)
- Phần "Owner" và "Lifecycle" là dữ liệu của M1 nhưng do CRM tự quản lý
