# Báo cáo: xử lý sai lệch số liệu chiến dịch

## 1. Tình hình

Từ 17/07/2026 hệ thống ngừng cập nhật lượt xem cho chiến dịch. Ngày 01/08/2026 — sau khi chiến dịch đã kết thúc 31/07 — hệ thống thu thập lại một lần và ghi dồn toàn bộ lượt xem tích luỹ của cả giai đoạn vào đúng ngày 01/08, là ngày nằm ngoài kỳ. Thưởng tương ứng cũng nằm ở ngày 01/08.

Số liệu và thưởng không mất, chỉ nằm sai ngày.

## 2. Giải pháp

Dời toàn bộ lượt xem và thưởng của ngày 01/08 về ngày 31/07 — ngày kết thúc thật của chiến dịch. Dời nguyên số: không tính lại, không tạo mới, không đổi giá trị. Chỉ đổi ngày ghi nhận.

Mỗi lần chạy xử lý một chiến dịch, với ba tham số: mã chiến dịch, ngày nguồn (01/08/2026), ngày đích (31/07/2026).

**Phạm vi đợt này: chỉ các chiến dịch có ngày kết thúc 31/07/2026.** Các chiến dịch kết thúc sau mốc đó, nếu gặp tình trạng tương tự, sẽ được rà soát và xử lý ở đợt riêng kèm báo cáo riêng. Đợt này không đụng tới chúng.

## 3. Những gì được dời

- **Lượt xem, lượt thích, bình luận của từng video.** Cộng vào số của ngày 31/07, không ghi đè.
- **Bản ghi thu thập gốc từ các nền tảng.** Dời theo, để cơ chế kiểm tra chất lượng số liệu không đánh dấu ngày 31/07 là bất thường.
- **Thưởng theo lượt xem của từng creator trên từng video.** Cộng vào khoản cùng loại ở ngày 31/07 nếu đã có; chưa có thì dời nguyên khoản sang.
- **Thưởng theo cột mốc.** Dời sang ngày 31/07, không xóa và không tạo lại, để creator không mất mốc đã đạt.
- **Các bảng số liệu tổng hợp của chiến dịch và của từng creator.** Tính lại, sau đó số của ngày 01/08 về 0.

Mọi khoản thưởng bị tác động đều ghi lại ngày ghi nhận ban đầu và mã lần chạy. Khoản được dời nguyên vẹn giữ nguyên mã khoản thưởng, nên hồ sơ đối soát cũ vẫn trỏ đúng khoản đó.

## 4. Các bước thực hiện

1. Sao lưu toàn bộ dữ liệu liên quan.
2. Chạy thử. Công cụ mặc định không ghi vào dữ liệu thật; muốn ghi phải khai báo rõ trong lệnh chạy.
3. Đối chiếu kết quả chạy thử: tổng lượt xem và tổng chi phí trước – sau, số liệu của từng ngày. Không khớp thì dừng và rà lại.
4. Thực thi. Công cụ tự dừng nếu phát hiện khoản đã thanh toán ở ngày 01/08, hoặc phát hiện bản ghi trùng lặp.
5. Kiểm tra lại và gửi quý công ty bản xác nhận kết quả kèm số liệu trước – sau.

Công cụ cũng dừng nếu phát hiện số liệu còn bị ghi vào các ngày sau 01/08. Trường hợp đó nghĩa là phạm vi sự cố rộng hơn một ngày; xử lý riêng ngày 01/08 sẽ vẫn còn ngày nằm ngoài kỳ, nên cần thống nhất lại cách xử lý trước khi chạy.

Mỗi lần chạy được lưu lịch sử vĩnh viễn: ai chạy, lúc nào, tham số gì, kết quả ra sao.

## 5. Kết quả kỳ vọng

Áp dụng cho các chiến dịch có ngày kết thúc 31/07/2026 được chạy trong đợt này. Các chiến dịch khác không bị ảnh hưởng, và cũng chưa được xử lý.

- Lượt xem và thưởng nằm ở ngày 31/07; ngày 01/08 bằng 0. Mọi màn hình thống kê và báo cáo đều thấy như vậy, không còn ngày nằm ngoài kỳ.
- Tổng lượt xem, tổng chi phí của chiến dịch và số tiền của từng creator đều **không đổi**. Chỉ ngày ghi nhận đổi.
- Thưởng cột mốc của creator giữ nguyên, không mất mốc đã đạt.
- Mọi khoản thưởng bị tác động đều truy ngược được về ngày ghi nhận ban đầu.
- Thưởng được ghi nhận đúng ngày trong kỳ. Việc chi trả thực hiện ở kỳ thanh toán kế tiếp.

## 6. Rủi ro

**Phân bổ theo ngày không phản ánh thực tế.** Toàn bộ lượt xem của giai đoạn 17/07–01/08 dồn vào một ngày 31/07, nên biểu đồ theo ngày sẽ thấy các ngày 17/07–30/07 gần như bằng 0 và ngày 31/07 là một đỉnh rất cao.

Không khắc phục được: giai đoạn gián đoạn không có dữ liệu từng ngày nên không có căn cứ để chia lại. Chúng tôi giữ tổng đúng thay vì đoán một cách chia không có cơ sở. Tổng lượt xem và tổng chi phí là con số dùng để đối soát; biểu đồ theo ngày trong giai đoạn này chỉ nên đọc ở mức tham khảo.

**Có khoản đã thanh toán ở ngày 01/08.** Công cụ dừng lại, chúng tôi trao đổi riêng trước khi làm bất cứ điều gì.

**Số liệu lệch tạm thời trong lúc chạy.** Sẽ chạy ngoài giờ cao điểm.

## 7. Ngoài phạm vi

- Không chia lại lượt xem theo từng ngày cho giai đoạn 17/07–31/07.
- Không điều chỉnh khoản đã thanh toán, không chi trả hồi tố vào kỳ đã đóng.
- Hồ sơ đối soát đã lập trước đó không tự cập nhật theo. Các khoản được dời đều truy ngược được để đối chiếu.
- Không thay đổi thể lệ hay mức thưởng của chiến dịch.
- **Các chiến dịch có ngày kết thúc sau 31/07/2026 không thuộc đợt này**, kể cả khi gặp tình trạng tương tự. Sẽ có đợt và báo cáo riêng.
- Không xử lý trường hợp tràn nhiều hơn một ngày.
- Khôi phục từ bản sao lưu thực hiện thủ công, không có thao tác hoàn tác tự động.
- Xử lý nguyên nhân gốc để hệ thống không ghi nhận số liệu sau ngày kết thúc chiến dịch: hạng mục kỹ thuật riêng, làm song song.

## 8. Mốc thời gian

Dự kiến hoàn tất trước ngày `[___]`. Bản xác nhận kết quả gửi ngay sau khi chạy xong.
