# Bảng xếp hạng theo tuần

> Cho phép mỗi campaign chọn xếp hạng creator theo phần phát sinh trong tuần hiện tại (thứ Hai đến Chủ nhật) thay vì con số luỹ kế từ ngày campaign bắt đầu. Admin bật/tắt trong form event, mặc định giữ nguyên hành vi cũ. Giải quyết bài toán thứ hạng đóng băng ở các campaign chạy dài, khiến creator vào sau không có động lực tham gia.

**Ngày:** 06/08/2026
**Trạng thái:** Đã triển khai — chờ bật cho campaign thật
**Đối tượng đọc:** Business, Ops, PM, khách hàng (brand)
**Phạm vi:** Module bảng xếp hạng — Ambassador (áp dụng frontend Parasola)

---

## 1. Bối cảnh — thứ hạng đóng băng ở campaign chạy dài

Bảng xếp hạng trên trang chủ campaign hiện xếp theo con số luỹ kế từ ngày campaign bắt đầu. Với campaign chạy vài tháng, bảng gần như không đổi từ tuần này sang tuần khác.

Creator tham gia từ tuần đầu đã tích luỹ hàng trăm nghìn lượt xem. Một creator vào sau, dù làm tốt trong bảy ngày, cũng chỉ thêm được vài chục nghìn. Khoảng cách đó không đóng lại được bằng nỗ lực, nên họ nhìn bảng một lần rồi thôi.

Ở chiều ngược lại, creator cũ ngừng đăng bài vẫn giữ nguyên thứ hạng. Bảng không phân biệt được người đang hoạt động với người đã bỏ cuộc, nên nó không còn phản ánh điều gì đang thực sự diễn ra.

Yêu cầu đến từ khách hàng qua kênh nội bộ ngày 05/08/2026:

> "Mấy camp nhà mình đang cho hiển thị mặc định là theo cả chiến dịch từ khi chạy đến thời điểm hiện tại, nhưng khách muốn cho hiển thị theo từng tuần được không, để creator thi đua theo tuần."

## 2. Tại sao làm theo hướng "cấu hình ở cấp campaign"?

Ba hướng đã cân nhắc.

**Đổi thẳng toàn hệ thống sang xếp theo tuần.** Loại ngay: các campaign đang chạy sẽ đổi hành vi mà khách không được báo trước, và không phải khách nào cũng muốn.

**Cho creator tự chuyển giữa hai chế độ trên trang.** Nghe linh hoạt nhưng sai bản chất: đây là luật thi đua của campaign, do brand đặt ra, không phải tuỳ chọn xem của người dùng. Nếu creator tự chọn được thì mỗi người nhìn một bảng khác nhau, và câu "tuần này ai dẫn đầu" mất nghĩa.

**Cấu hình ở cấp campaign, admin đặt.** Đây là hướng đã chọn. Mỗi campaign một luật thi đua, brand quyết định qua đội vận hành. Campaign chưa cấu hình thì giữ nguyên như cũ, nên triển khai không ảnh hưởng ai.

Hướng này cũng khớp với cách hệ thống `creator-os` mô hình hoá cùng bài toán — kỳ xếp hạng là thuộc tính của bảng, không phải tham số người xem.

## 3. Có gì mới?

**Ô chọn "Kỳ xếp hạng" trong form campaign.** Hai lựa chọn: *Toàn thời gian* và *Theo tuần*. Nằm ở tab Tuỳ chọn, cạnh các cấu hình campaign sẵn có. Đội vận hành tự đổi, không cần nhờ kỹ thuật.

**Bảng xếp hạng hiển thị khung thời gian đang tính.** Khi bật kỳ tuần, dưới tiêu đề bảng xuất hiện dòng `Tuần này · 03/08 – 09/08`. Đây không phải chi tiết trang trí: thiếu nó thì creator chỉ thấy các con số nhỏ đi mà không hiểu vì sao, và toàn bộ mục đích của tính năng biến mất.

**Bảng làm mới ngay đầu tuần.** Đúng 00:00 thứ Hai giờ Việt Nam, bảng bắt đầu một kỳ mới từ số không cho tất cả mọi người.

**Tiền thưởng không đổi.** Bảng xếp hạng reset theo tuần nhưng tiền là tiền thật đã kiếm, vẫn luỹ kế từ đầu campaign.

## 4. Lợi ích kỳ vọng

Creator vào giữa campaign có cơ hội thật. Mỗi thứ Hai mọi người xuất phát lại cùng lúc, nên nỗ lực trong tuần được phản ánh ngay vào thứ hạng.

Creator cũ phải duy trì hoạt động mới giữ được hạng. Bảng trở thành thước đo ai đang làm việc, không phải ai đã làm việc.

Brand có cột mốc để truyền thông. Một campaign ba tháng có mười hai cuộc đua thay vì một, mỗi tuần một câu chuyện "ai dẫn đầu" để nhắc lại.

Đội vận hành bật/tắt theo từng campaign mà không cần chờ đợt phát hành.

## 5. Chi phí và rủi ro

**Bảng vắng vào sáng thứ Hai.** Đầu tuần mới chưa ai phát sinh lượt xem nào nên bảng rỗng. Hiện tại bảng rỗng thì cả khối bị ẩn khỏi trang, tức là creator mở trang sẽ thấy mục quen thuộc biến mất cho tới lượt chạy đầu tiên của tác vụ thống kê. Đây là câu hỏi còn để ngỏ ở mục 8.

**Tuần đầu của campaign có thể ngắn hơn bảy ngày.** Tuần cắt theo lịch, nên campaign khởi động vào thứ Tư sẽ có "tuần 1" chỉ năm ngày. Nếu brand trao thưởng theo tuần thì tuần đầu không công bằng.

**Không hiển thị được lượt xem tách theo nền tảng.** Một số giao diện partner hiện icon TikTok/Facebook/Threads kèm số riêng từng nền tảng. Nguồn dữ liệu dùng cho kỳ tuần không lưu chi tiết đó, nên các giao diện ấy chưa dùng được kỳ tuần. Parasola không vướng vì bảng của nó là hai cột lượt xem và tiền.

**Số liệu có độ trễ tới mười phút.** Đánh đổi để giảm tải cho hệ thống, do bảng nằm ở trang công khai ai cũng xem được. Dữ liệu gốc cũng chỉ thay đổi khi tác vụ thống kê chạy nên độ trễ này không đáng kể trong thực tế.

## 6. Phạm vi không ảnh hưởng

Campaign chưa cấu hình kỳ chạy y hệt như trước, không đổi một con số nào.

Cách tính tiền thưởng không đổi. Số tiền creator nhận được không phụ thuộc kỳ xếp hạng.

Cấu hình bật/tắt bảng xếp hạng và ẩn/hiện số tiền theo partner vẫn hoạt động độc lập — xem `../prd-partner-leaderboard-config-2026-04-02.md`.

Các giao diện partner khác Parasola chưa đổi gì.

## 7. Hướng mở rộng (sau phase 1)

Hiển thị thứ hạng của chính người đang xem, kể cả khi họ nằm ngoài danh sách hiển thị. Đây là thứ tạo động lực mạnh nhất trong một cuộc thi đua — *"bạn đang hạng 23, còn 4 ngày"* — và hạ tầng đã sẵn sàng.

Xem lại bảng xếp hạng của các tuần đã qua.

Kỳ theo tháng, nếu có campaign cần nhịp dài hơn.

Trao thưởng tự động cho top của mỗi tuần.

Mở rộng nhãn kỳ sang các giao diện partner còn lại.

## 8. Câu hỏi còn để ngỏ

**Bảng rỗng đầu tuần nên ẩn hay hiện?** Đề xuất giữ khối và hiện dòng "Tuần này chưa có ai ghi điểm". Mất hẳn một mục quen thuộc gây hoang mang hơn một dòng chữ. Cần PM chốt.

**Tuần lịch hay bảy ngày kể từ ngày mở campaign?** Hiện dùng tuần lịch vì creator hiểu ngay không cần giải thích. Chỉ nên đổi nếu brand xác nhận có trao thưởng theo tuần. Cần khách xác nhận.

**Khối số tiền cá nhân có cần ghi rõ là luỹ kế không?** Bảng xếp hạng theo tuần đứng cạnh con số tiền luỹ kế mà không có gì phân biệt, creator có thể hiểu nhầm. Đề xuất gắn nhãn cho khối tiền, không đổi cách tính. Cần PM chốt.

## 9. Tài liệu liên quan

- [`prd.md`](./prd.md) — yêu cầu chi tiết kèm tiêu chí nghiệm thu
- [`tech-spec.md`](./tech-spec.md) — thiết kế kỹ thuật
- [`../prd-partner-leaderboard-config-2026-04-02.md`](../prd-partner-leaderboard-config-2026-04-02.md) — cấu hình hiển thị bảng xếp hạng theo partner
