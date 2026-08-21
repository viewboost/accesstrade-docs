BÁO CÁO: XỬ LÝ SAI LỆCH SỐ LIỆU CHIẾN DỊCH


TÌNH HÌNH

Từ ngày 17/07/2026, hệ thống ngừng cập nhật lượt xem cho chiến dịch. Đến
ngày 01/08/2026 — sau khi chiến dịch đã kết thúc ngày 31/07 — hệ thống thu
thập lại một lần. Toàn bộ lượt xem tích luỹ của giai đoạn 17/07–01/08 được
ghi dồn vào ngày 01/08, là ngày nằm ngoài kỳ chiến dịch. Thưởng tương ứng
cũng được ghi nhận ở ngày 01/08.

Số liệu không mất. Thưởng không mất. Cả hai đang nằm ngoài kỳ chiến dịch.


GIẢI PHÁP

Dời toàn bộ lượt xem và thưởng đang nằm ở ngày 01/08/2026 về ngày
31/07/2026 — ngày kết thúc thật của chiến dịch.

Dời nguyên số: không tính lại, không tạo mới, không thay đổi giá trị. Chỉ
thay đổi ngày ghi nhận.


ĐẦU VÀO CỦA MỖI LẦN CHẠY

- Mã chiến dịch cần xử lý
- Ngày nguồn (ngày bị ghi tràn): 01/08/2026
- Ngày đích (ngày kết thúc chiến dịch): 31/07/2026

Mỗi lần chạy xử lý đúng một chiến dịch.


THAO TÁC

1. Dời toàn bộ lượt xem thu thập được và thưởng theo lượt xem từ ngày
   01/08/2026 sang ngày 31/07/2026.
2. Dời toàn bộ thưởng theo cột mốc liên quan từ ngày 01/08/2026 sang ngày
   31/07/2026.

Cụ thể những gì được dời:

- Lượt xem, lượt thích, bình luận của từng video. Cộng vào số của ngày
  31/07, không ghi đè.
- Bản ghi thu thập gốc từ các nền tảng. Dời theo để cơ chế kiểm tra chất
  lượng số liệu không đánh dấu ngày 31/07 là bất thường.
- Thưởng theo lượt xem của từng creator trên từng video. Nếu ngày 31/07 đã
  có khoản cùng loại thì cộng thêm vào khoản đó, nếu chưa có thì dời nguyên
  khoản sang.
- Thưởng theo cột mốc (đạt mốc lượt xem, đạt mốc số lượng video). Dời sang
  ngày 31/07, không xóa và không tạo lại.
- Báo cáo tổng hợp theo ngày của chiến dịch và của từng creator. Tính lại
  cho cả hai ngày. Sau khi tính lại, số của ngày 01/08 về 0.
- Bảng thành tích tích luỹ của từng creator. Cập nhật lại cho khớp.

Mỗi khoản thưởng được dời đều lưu con trỏ về khoản gốc và ngày gốc, để đối
soát sau này truy ngược được.


CƠ CHẾ AN TOÀN

- Mặc định chạy thử, không ghi vào dữ liệu thật.
- Muốn ghi thật phải khai báo rõ trong lệnh chạy.
- Tự dừng nếu phát hiện khoản đã thanh toán ở ngày 01/08.
- Tự dừng nếu phát hiện số liệu bị ghi vào các ngày sau 01/08, tức là tràn
  nhiều hơn một ngày — nằm ngoài phạm vi xử lý của công cụ này.
- Tự dừng nếu phát hiện bản ghi trùng lặp.
- Sao lưu toàn bộ dữ liệu trước khi ghi.
- Lưu lịch sử vĩnh viễn: ai chạy, lúc nào, tham số gì, kết quả ra sao.


CÁC BƯỚC THỰC HIỆN

1. Sao lưu toàn bộ dữ liệu liên quan.
2. Chạy thử, không ghi vào dữ liệu thật.
3. Xuất bản đối chiếu TRƯỚC – SAU theo từng ngày, kèm dòng tổng chi phí.
4. Gửi bản đối chiếu để quý công ty xác nhận.
5. Thực thi sau khi được xác nhận. Không tự động chạy.
6. Kiểm tra kết quả và gửi lại bản xác nhận.


KẾT QUẢ MONG ĐỢI

Áp dụng cho các chiến dịch được chạy. Các chiến dịch khác không bị ảnh hưởng.

- Tất cả lượt xem và thưởng sẽ ở ngày 31/07 thay vì ngày 01/08.
- Lượt xem và thưởng của ngày 01/08 sẽ luôn bằng 0.
- Các màn hình thống kê và báo cáo sẽ thấy số ở ngày 31/07 thay vì
  ngày 01/08.
- Báo cáo chiến dịch không còn ngày nằm ngoài kỳ.
- Tổng lượt xem của chiến dịch không đổi.
- Tổng chi phí của chiến dịch không đổi.
- Số tiền của từng creator không đổi, chỉ đổi ngày ghi nhận.
- Thưởng cột mốc của creator giữ nguyên, không mất mốc đã đạt.
- Mỗi khoản thưởng được dời đều truy ngược được về khoản gốc và ngày gốc,
  phục vụ đối soát.
- Thưởng được ghi nhận đúng ngày trong kỳ chiến dịch. Việc chi trả thực
  hiện ở kỳ thanh toán kế tiếp.


RỦI RO

1. Phân bổ theo ngày sẽ không phản ánh thực tế.
   - Toàn bộ lượt xem của giai đoạn 17/07–01/08 dồn vào một ngày duy nhất
     là 31/07.
   - Biểu đồ theo ngày sẽ thấy các ngày 17/07–30/07 gần như bằng 0 và ngày
     31/07 là một đỉnh rất cao.
   - Không khắc phục được. Trong giai đoạn gián đoạn, hệ thống không ghi
     được lượt xem phát sinh từng ngày nên không có căn cứ để chia lại.
   - Chúng tôi chọn giữ tổng đúng thay vì đoán một cách chia không có
     cơ sở.
   - Tổng lượt xem và tổng chi phí là con số dùng để đối soát. Biểu đồ theo
     ngày trong giai đoạn này chỉ nên đọc ở mức tham khảo.

2. Nếu phát hiện khoản đã thanh toán ở ngày 01/08, hệ thống dừng lại.
   Chúng tôi sẽ trao đổi riêng trước khi làm bất cứ điều gì.

3. Báo cáo có thể lệch tạm thời trong lúc chạy. Sẽ chạy ngoài giờ cao điểm.

4. Toàn bộ dữ liệu được sao lưu trước khi xử lý. Việc khôi phục thực hiện
   thủ công từ bản sao lưu, không có thao tác hoàn tác tự động.


NGOÀI PHẠM VI

- Không khôi phục được phân bổ lượt xem theo từng ngày của giai đoạn
  17/07–31/07.
- Không điều chỉnh các khoản đã thanh toán.
- Không chi trả hồi tố vào kỳ thanh toán đã đóng.
- Các biên bản đối soát đã lập trước đó không tự động cập nhật theo. Mọi
  khoản được dời đều truy ngược được để đối chiếu.
- Không thay đổi thể lệ hay mức thưởng của chiến dịch.
- Không xử lý trường hợp tràn nhiều hơn một ngày.
- Xử lý nguyên nhân gốc để hệ thống không ghi nhận số liệu sau ngày kết
  thúc chiến dịch: hạng mục kỹ thuật riêng, làm song song.
- Mỗi lần chạy xử lý một chiến dịch. Các chiến dịch khác không bị đụng.


MỐC THỜI GIAN

Bản đối chiếu ở Bước 3 dự kiến gửi trước ngày [___].
Bước 5 chờ xác nhận từ quý công ty.
