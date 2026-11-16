# CN-06 · Mức thưởng cuối kỳ và trao quà

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-06.1 Mục đích

Thể lệ trả thưởng theo **tổng điểm hợp lệ** tại thời điểm tổng kết, sau khi BTC đối soát và xác nhận kết quả. Người tham gia đạt mức cao vẫn nhận phần thưởng của các mức thấp hơn.

| Mức | Điểm tích lũy | Phần thưởng | Số lượng |
|---|---|---|---|
| Mức 1 | Trên 200 điểm | 01 điểm vé SFC | 2.000 |
| Mức 2 | Trên 400 điểm | Voucher thanh toán vé SFC 500.000 VNĐ | 500 |
| Mức 3 | Trên 600 điểm | 2.000.000 VNĐ | 100 |
| Mức 4 | Trên 1.500 điểm | 3.000.000 VNĐ | 10 |

Hệ thống hiện chưa có bước tính tổng điểm từng người, xét mức, giữ số suất, và theo dõi việc trao quà. Chức năng này thêm các bước đó vào đối soát.

Ví dụ: nhân viên có 650 điểm đạt Mức 1, 2, 3 và chưa đạt Mức 4; "trên" nghĩa là lớn hơn, nên đúng 600 điểm chưa đạt Mức 3.

## CN-06.2 Phạm vi

**Trong phạm vi**
- Tổng điểm hợp lệ của từng người trong bản đối soát.
- Xét mức thưởng, nhận cộng dồn, hết suất.
- Bước kiểm trước khi trao.
- Theo dõi mỗi người đã đạt mức nào và đã trao quà chưa.
- Danh sách trao quà cho Operation (Excel).

**Ngoài phạm vi**
- Tự động gửi quà, voucher hay chuyển tiền: Operation và bên Vietjet trao. Thưởng tiền mặt chuyển thẳng vào lương bên Vietjet, hệ thống này không chi trả và không vận hành thuế.
- Điểm sau khi trao thưởng, chu kỳ, thu hồi điểm: thuộc [CN-07](./prd-cn07-diem-sau-trao-thuong.md).
- Thông báo mới cho người tham gia khi đạt mức: người tham gia xem ở app (CN-08).

## CN-06.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md) | Kỳ đối soát; các khoản đã hoàn thành của CN-02 là nguồn của tổng điểm |
| [CN-05](./prd-cn05-bang-xep-hang-thang.md) | Điểm thưởng TOP đã cộng nằm trong tổng điểm hợp lệ |
| [CN-07](./prd-cn07-diem-sau-trao-thuong.md) | Chu kỳ xét thưởng và điều chỉnh điểm sau đối soát |
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Người tham gia xem mức đã đạt |

## CN-06.4 Luồng

1. Admin › Đối soát › tạo kỳ đối soát cuối kỳ cho sự kiện.
2. **Lấy danh sách**: hệ thống tính tổng điểm hợp lệ của từng người và xếp vào các mức (CN06-BR01, 02, 03).
3. BTC kiểm danh sách ở tab **Tổng điểm và mức thưởng**, từ chối dòng nếu cần, rồi **duyệt kỳ** (CN06-BR06).
4. Sau khi duyệt, người đạt mức vào danh sách trao quà. Admin xuất danh sách cho Operation, rồi đánh dấu **Đã trao** theo từng dòng khi quà đã đến tay người nhận (CN06-BR08, 09).

## CN-06.5 Quy tắc nghiệp vụ

**Tổng điểm và mức**

| Mã | Quy tắc |
|---|---|
| **CN06-BR01** | **Tổng điểm hợp lệ** của một người trong chu kỳ = tổng điểm các khoản thưởng ở trạng thái **Đã hoàn thành** (CN-02), cộng khoản thưởng thêm đã hoàn thành (kể cả điểm TOP của CN-05), trừ các khoản điều chỉnh của CN-07 |
| **CN06-BR02** | Người tham gia đạt Mức N khi tổng điểm hợp lệ **lớn hơn** mốc của mức (đúng bằng mốc chưa đạt). Mốc: 200, 400, 600, 1.500 |
| **CN06-BR03** | Đạt mức cao thì đạt cả các mức thấp hơn (nhận cộng dồn). Ví dụ 1.600 điểm đạt đủ bốn mức |

**Số suất**

| Mã | Quy tắc |
|---|---|
| **CN06-BR04** | Mỗi mức có số suất: Mức 1 là 2.000, Mức 2 là 500, Mức 3 là 100, Mức 4 là 10. Số suất tính cho chu kỳ xét thưởng |
| **CN06-BR05** | Số người đạt một mức vượt số suất thì ưu tiên người **đạt mốc sớm hơn**. Thời điểm đạt mốc là ngày của khoản thưởng làm tổng điểm của người đó vượt mốc, tính theo ngày đăng bài lên nền tảng của khoản đó. Hai người cùng ngày thì xét tiếp theo số bài hợp lệ nhiều hơn. Người không được suất của mức cao vẫn được các mức thấp hơn nếu mức đó còn suất |

**Kiểm và trao**

| Mã | Quy tắc |
|---|---|
| **CN06-BR06** | Kỳ đối soát cuối kỳ có tab **Tổng điểm và mức thưởng**, mỗi người một dòng: người tham gia, tổng điểm hợp lệ, các mức đạt, các mức được suất. Luồng duyệt, từ chối từng dòng, từ chối cả kỳ, xuất file giữ như các tab khác |
| **CN06-BR07** | Dòng bị từ chối thì người đó không vào danh sách trao quà của kỳ |
| **CN06-BR08** | Mỗi người, mỗi mức được suất có trạng thái **Chưa trao** hoặc **Đã trao**. Mới vào danh sách là Chưa trao |
| **CN06-BR09** | Admin đánh dấu **Đã trao** theo từng dòng hoặc nhiều dòng một lúc. Ai đánh dấu và lúc nào được ghi lại |
| **CN06-BR10** | **Danh sách cho Operation** (Excel) gồm: người nhận, mức đạt, loại quà (vé SFC, voucher, tiền mặt), trạng thái trao. Mỗi mức được suất là một dòng |

## CN-06.6 Kịch bản kiểm thử

**Dữ liệu chung:** chu kỳ có các người U1 650 điểm, U2 1.600 điểm, U3 200 điểm, U4 201 điểm, tất cả khoản đã hoàn thành.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN06-TC01 | Tổng điểm | Lấy danh sách kỳ cuối kỳ | Mỗi người một dòng với đúng tổng điểm | BR01, 06 |
| CN06-TC02 | Đúng mốc | Xem U3 (200) và U4 (201) | U3 không đạt mức nào; U4 đạt Mức 1 | BR02 |
| CN06-TC03 | Cộng dồn | Xem U1 (650) và U2 (1.600) | U1 đạt Mức 1, 2, 3; U2 đạt cả bốn mức | BR03 |
| CN06-TC04 | Chỉ khoản đã hoàn thành | U1 có thêm khoản Chờ đối soát 100 điểm | Tổng điểm của U1 vẫn 650 | BR01 |
| CN06-TC05 | Thưởng TOP | U1 có khoản thưởng thêm TOP hoàn thành 100 điểm | Tổng điểm U1 = 750 | BR01 |
| CN06-TC06 | Hết suất | Mức 4 còn 1 suất; U2 và U5 (1.600) cùng vượt 1.500, U2 vượt mốc sớm hơn | Chỉ U2 được suất Mức 4; U5 vẫn được Mức 1, 2, 3 | BR04, 05 |
| CN06-TC07 | Cùng ngày | Hai người cùng vượt mốc một ngày, người A 30 bài hợp lệ, người B 28 bài | Người A được suất | BR05 |
| CN06-TC08 | Từ chối dòng | Từ chối dòng U1 trước khi duyệt | U1 không vào danh sách trao quà | BR07 |
| CN06-TC09 | Trạng thái trao | Duyệt kỳ, đánh dấu Đã trao dòng Mức 1 của U1 | Mức 1 của U1 Đã trao; Mức 2, 3 vẫn Chưa trao; có ghi người và thời điểm | BR08, 09 |
| CN06-TC10 | Danh sách Operation | Xuất danh sách | Mỗi mức được suất là một dòng, có loại quà và trạng thái | BR10 |
