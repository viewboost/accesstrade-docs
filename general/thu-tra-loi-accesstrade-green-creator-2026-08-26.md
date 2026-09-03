Kính gửi Quý đối tác,

Cảm ơn Quý đối tác đã phản ánh sớm và cụ thể. Chúng tôi đã tiếp nhận ngay và kiểm tra các endpoint mà Quý đối tác nêu:

- */events/{id}/leaderboards*
- */events/{id}/content*
- */events/user-newest*
- */events/statistic*

Đúng là các endpoint này hiện đang trả dữ liệu mà chưa qua bước đăng nhập. Chúng tôi xem đây là việc cần ưu tiên xử lý, và xin trả lời cụ thể hai câu hỏi Quý đối tác đặt ra.

**1. Nhóm dữ liệu đang để công khai và lý do**

Phần lớn những gì các endpoint này trả ra là dữ liệu được chủ đích công khai, phục vụ trang giới thiệu và trải nghiệm thi đua của creator:

- Số liệu tổng của nền tảng (tổng lượt xem, tổng số nội dung, số người tham gia): dùng làm minh chứng quy mô trên landing để thu hút creator mới.
- Bảng xếp hạng (tên hiển thị, ảnh đại diện, thành tích): tạo hiệu ứng thi đua, giữ chân creator.
- Tiến độ ngân sách của chiến dịch: để creator biết chiến dịch sắp đạt hạn mức mà tăng tốc sản xuất nội dung.

Những số liệu mang tính tổng hợp này bản thân chúng tôi vẫn muốn giữ công khai, vì đó là một phần giá trị của sản phẩm.

**2. Phần dữ liệu nhạy cảm bị lẫn vào, và phương án tách**

Điểm đúng mà Quý đối tác chỉ ra là bên cạnh các số liệu tổng hợp nói trên, gói dữ liệu trả về còn đi kèm một số thông tin lẽ ra không nên công khai:

- Con số thu nhập chi tiết của từng creator (đã nhận, đang chờ, đã chuyển), vốn không hiển thị trên giao diện.
- Thu nhập theo từng bài viết cụ thể.
- Ảnh đại diện: đây là ảnh đại diện mạng xã hội mà chính creator đang dùng công khai (không phải ảnh riêng tư do hệ thống lưu); tuy nhiên đường dẫn hiện trỏ thẳng tới tài khoản Google/TikTok gốc.

Nguyên nhân là trong quá trình phát triển, một cấu trúc dữ liệu đã được dùng chung cho cả màn công khai lẫn màn cá nhân, nên một vài trường của màn cá nhân đi theo ra ngoài dù giao diện không dùng tới. Đây chính là phần chúng tôi sẽ tách.

Cũng xin thông tin thêm để Quý đối tác yên tâm: chúng tôi đã rà và xác nhận các thông tin định danh nhạy cảm hơn như số điện thoại, giấy tờ tùy thân, thông tin hợp đồng và tài khoản ngân hàng không nằm trong các endpoint này, tất cả đều yêu cầu đăng nhập mới truy cập được.

Về phương án tách bạch cụ thể:

- Bốn endpoint nêu trên vẫn giữ công khai để phục vụ đúng chức năng bảng xếp hạng và số liệu tổng, nhưng chúng tôi sẽ chuẩn hóa lại để chỉ trả những trường mà giao diện cần (tên hiển thị, ảnh, lượt xem, thứ hạng, số liệu tổng).
- Toàn bộ trường thu nhập của cá nhân được đưa về sau lớp đăng nhập, theo nguyên tắc mỗi người chỉ xem được dữ liệu của chính mình.
- Ảnh đại diện: tuy đây là ảnh công khai creator đang dùng trên mạng xã hội, chúng tôi vẫn sẽ đưa qua ảnh do hệ thống lưu để không phát tán đường dẫn tài khoản gốc ra ngoài.
- Để tránh sót, chúng tôi sẽ không dừng lại ở bốn endpoint này, mà rà soát toàn diện toàn bộ hệ thống, đảm bảo không còn điểm nào khác đưa dữ liệu cá nhân ra kênh công khai.

**3. Tiến độ và đầu mối**

Chúng tôi xác định đây là việc ưu tiên và đã bắt tay xử lý ngay. Trước hết là tách các trường thu nhập cá nhân khỏi kênh công khai, sau đó là phần rà soát toàn diện và các bước củng cố còn lại. Chúng tôi sẽ cử một đầu mối theo sát xuyên suốt và cập nhật tiến độ cho Quý đối tác trong quá trình xử lý, cũng như xác nhận lại khi hoàn tất.

**Cập nhật tiến độ (27/08/2026):** Chúng tôi đã hoàn tất phần trọng yếu và triển khai lên hệ thống thật — toàn bộ trường thu nhập chi tiết của từng creator đã được tách khỏi các endpoint công khai (bảng xếp hạng, danh sách nội dung), và màn số liệu cá nhân đã được siết lại. Hiện chúng tôi đang hoàn tất nốt việc đưa ảnh đại diện qua ảnh do hệ thống lưu (thay cho đường dẫn tài khoản Google/TikTok) và siết lại cấu hình truy cập; sẽ xác nhận với Quý đối tác ngay khi xong.

Một lần nữa cảm ơn Quý đối tác đã phát hiện và báo sớm. Chúng tôi tiếp nhận với tinh thần cầu thị và sẽ xử lý dứt điểm.

Trân trọng,
ACCESSTRADE
