# CN-06 · Xuất kết quả xếp hạng cuối chương trình

**Date:** 2026-11-17 · **Author:** Vinh Nguyễn · **Version:** 0.4 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-06.1 Mục đích

Thể lệ trả thưởng theo **tổng điểm hợp lệ** tại thời điểm tổng kết chương trình, sau khi BTC đối soát và xác nhận kết quả. Người tham gia đạt mức cao vẫn nhận phần thưởng của các mức thấp hơn.

| Mức | Điểm tích lũy | Phần thưởng | Số lượng |
|---|---|---|---|
| Mức 1 | Trên 200 điểm | 01 điểm vé SFC | 2.000 |
| Mức 2 | Trên 400 điểm | Voucher thanh toán vé SFC 500.000 VNĐ | 500 |
| Mức 3 | Trên 600 điểm | 2.000.000 VNĐ | 100 |
| Mức 4 | Trên 1.500 điểm | 3.000.000 VNĐ | 10 |

Theo Vietjet, **mỗi chương trình tự chạy**: bảng xếp hạng, điểm và đối soát trao giải đều theo chương trình. Theo thể lệ hiện tại, mỗi tháng tạo một chương trình (sự kiện) riêng, điểm không cộng dồn giữa các chương trình, và số suất của từng mức tính cho từng chương trình.

Việc trao quà do **Operation tự làm bên ngoài hệ thống**. Hệ thống chỉ cần, khi chương trình kết thúc và điểm đã đối soát (gồm cả điểm thưởng TOP hàng tháng đã cộng), **xuất một file xếp hạng người tham gia** theo tổng điểm, lấy đủ số người cần tặng quà hoặc dư một chút.

Ví dụ: hết chương trình, Admin bấm **Xuất kết quả cuối chương trình**, nhập lấy 2.200 người, nhận file xếp hạng theo tổng điểm. Hai người cùng 650 điểm thì người đăng bài đạt đủ 650 điểm trước xếp trên.

## CN-06.2 Phạm vi

**Trong phạm vi**
- File xếp hạng toàn chương trình theo tổng điểm hợp lệ.
- Tiêu chí phụ khi bằng điểm: ai đạt tổng điểm đó trước.
- Số người lấy do Admin nhập; cột mức đạt để Operation đỡ phải tính lại.

**Ngoài phạm vi**
- Trao quà, theo dõi đã trao hay chưa, danh sách trao quà: Operation làm bên ngoài. Thưởng tiền mặt chuyển thẳng vào lương bên Vietjet, hệ thống này không chi trả và không vận hành thuế.
- Trừ điểm sau đối soát: không làm ([CN-07](./prd-cn07-diem-sau-trao-thuong.md)). Gian lận phát hiện trước đối soát cuối chương trình thì từ chối bài.
- Thông báo mới cho người tham gia khi đạt mức: người tham gia xem ở app (CN-08).

## CN-06.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md) | Các khoản đã hoàn thành của CN-02 là nguồn của tổng điểm |
| [CN-05](./prd-cn05-bang-xep-hang-thang.md) | Điểm thưởng TOP đã cộng nằm trong tổng điểm hợp lệ; dùng chung cách xếp bằng điểm |
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Người tham gia xem mức đã đạt |

## CN-06.4 Luồng

1. Cuối chương trình (tháng): BTC tải file TOP (CN-05), cộng điểm thưởng TOP bằng **Thưởng thêm**, đối soát như các khoản khác.
2. BTC từ chối các bài gian lận (nếu có) và đối soát xong mọi khoản (CN-02).
3. Admin › sự kiện › **Bảng xếp hạng** › **Xuất kết quả cuối chương trình**, nhập số người cần lấy.
4. Hệ thống tạo file và gửi như các file xuất khác. Operation dùng file để tặng quà.

## CN-06.5 Quy tắc nghiệp vụ

**Tổng điểm, mức**

| Mã | Quy tắc |
|---|---|
| **CN06-BR01** | **Tổng điểm hợp lệ** của một người trong cả chương trình = tổng điểm các khoản thưởng ở trạng thái **Đã hoàn thành** (CN-02), cộng khoản thưởng thêm đã hoàn thành (kể cả điểm TOP của CN-05) |
| **CN06-BR02** | Người tham gia đạt Mức N khi tổng điểm hợp lệ **lớn hơn** mốc của mức (đúng bằng mốc chưa đạt). Mốc: 200, 400, 600, 1.500 |
| **CN06-BR03** | Đạt mức cao thì đạt cả các mức thấp hơn (nhận cộng dồn). Ví dụ 1.600 điểm đạt đủ bốn mức |

**Xếp hạng**

| Mã | Quy tắc |
|---|---|
| **CN06-BR04** | Xếp theo tổng điểm hợp lệ giảm dần. Chỉ người có tổng điểm lớn hơn 0 vào file |
| **CN06-BR05** | Bằng điểm thì người **đạt tổng điểm đó sớm hơn** xếp trên. Thời điểm đạt = **giờ đăng bài lên mạng xã hội** của khoản thưởng hợp lệ gần nhất làm nên tổng điểm của người đó (khoản gần nhất tính theo giờ đăng bài). Bài không có giờ đăng thì dùng giờ gửi bài vào hệ thống. Khoản thưởng thêm không gắn bài (điểm TOP) tính theo ngày ghi nhận của khoản đó. Vẫn bằng thì xếp theo mã người dùng nhỏ hơn để thứ tự không đổi giữa các lần xuất |
| **CN06-BR06** | Bài bị từ chối **trước khi đối soát** thì khoản của bài về trạng thái từ chối, không được tính vào tổng điểm và vào thời điểm đạt. Khoản đã **Đã hoàn thành** không đổi khi bài bị từ chối sau đó ([CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) tình huống B1), nên file vẫn tính khoản đó; sai sót phát hiện sau đối soát do Operation xử lý tay bên ngoài (CN-07 không làm) |

**File**

| Mã | Quy tắc |
|---|---|
| **CN06-BR07** | Tab **Bảng xếp hạng** của sự kiện có nút **Xuất kết quả cuối chương trình**, tách khỏi nút Tải file theo kỳ (CN-05). Admin nhập **số người cần lấy**, mặc định bằng số suất Mức 1 cộng 10% (2.200). Bấm thì hệ thống tạo file Excel và gửi như các file xuất khác |
| **CN06-BR08** | File lấy đủ số người đã nhập. Người đứng sát ranh giới mà bằng cả điểm lẫn thời điểm đạt với người cuối cùng thì lấy cả nhóm, nên có thể nhiều hơn số đã nhập |
| **CN06-BR09** | Các cột: Hạng, Mã người dùng, Tên, Mã nhân viên, Email, Tổng điểm, Thời điểm đạt tổng điểm, Số bài hợp lệ, **Mức đạt** (theo mốc điểm, CN06-BR02, BR03), **Mức được suất** (theo hạng so với số suất: Mức 1 là 2.000 người đầu, Mức 2 là 500, Mức 3 là 100, Mức 4 là 10; chỉ tính người đã đạt mức đó). Dòng đầu ghi thời điểm xuất và số người lấy Mã nhân viên lấy từ mã đã xác thực của người dùng ở đối tác của sự kiện, trống nếu chưa có. Email che theo quyền của người xuất. Tên, mã nhân viên, email được thoát ký tự công thức Excel. Thời điểm đạt hiện "Không xác định" khi khoản không có giờ hợp lệ (xếp cuối nhóm cùng điểm). So thời gian tới giây. Khoản Thưởng thêm 0 điểm hoặc âm không tính. Cột **Ghi chú** ghi các người bằng cả điểm lẫn giờ ở ranh giới số suất của mức đã đạt (mức cao liệt kê trước) để BTC xét tay |
| **CN06-BR10** | Trước khi xuất, nếu sự kiện còn khoản thưởng chưa đối soát xong (chờ duyệt, chờ đối soát), hệ thống **cảnh báo số khoản còn lại** nhưng vẫn cho xuất. File ghi rõ chỉ tính khoản đã hoàn thành |
| **CN06-BR11** | Chỉ người có quyền xuất dữ liệu của sự kiện mới xuất được. Nhân sự thuộc đối tác khác không xuất được kết quả của sự kiện không thuộc đối tác của họ |
| **CN06-BR12** | Điểm chỉ tích lũy trong chương trình của nó, kể cả điểm thưởng TOP của chương trình đó. Điểm của chương trình này không cộng vào chương trình khác, và file kết quả chỉ nói về một chương trình |

## CN-06.6 Kịch bản kiểm thử

**Dữ liệu chung:** chương trình có U1 650 điểm, U2 1.600 điểm, U3 200 điểm, U4 201 điểm, tất cả khoản đã hoàn thành.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN06-TC01 | Tổng điểm | Xuất kết quả | Mỗi người một dòng với đúng tổng điểm; xếp giảm dần | BR01, 04 |
| CN06-TC02 | Đúng mốc | Xem U3 (200) và U4 (201) | U3 không đạt mức nào; U4 đạt Mức 1 | BR02 |
| CN06-TC03 | Cộng dồn | Xem U1 (650) và U2 (1.600) | U1 đạt Mức 1, 2, 3; U2 đạt cả bốn mức | BR03, 09 |
| CN06-TC04 | Chỉ khoản đã hoàn thành | U1 có thêm khoản Chờ đối soát 100 điểm | Tổng điểm của U1 vẫn 650; có cảnh báo còn khoản chưa đối soát | BR01, 10 |
| CN06-TC05 | Thưởng TOP | U1 có khoản thưởng thêm TOP hoàn thành 100 điểm | Tổng điểm U1 = 750 | BR01 |
| CN06-TC06 | Bằng điểm | U6 và U7 cùng 700 điểm; bài cuối của U7 đăng lúc 09:00 ngày 12/11, của U6 lúc 18:00 ngày 12/11 | U7 xếp trên U6 | BR05 |
| CN06-TC07 | Theo giờ đăng chứ không theo giờ duyệt | Như TC06 nhưng BTC duyệt bài của U6 trước bài của U7 | U7 vẫn xếp trên U6 | BR05 |
| CN06-TC08 | Bài bị từ chối trước đối soát | U7 có bài làm đạt 700 điểm bị từ chối khi khoản còn chờ đối soát | Tổng điểm U7 giảm; thời điểm đạt tính lại theo các khoản còn hợp lệ | BR05, 06 |
| CN06-TC09 | Vẫn bằng | Hai người cùng điểm và cùng giờ | Người có mã nhỏ hơn xếp trên, lần xuất sau giữ nguyên thứ tự | BR05 |
| CN06-TC10 | Số người lấy | Nhập 100 khi có 5.000 người | File có 100 người đầu; nếu người thứ 100 và 101 bằng cả điểm lẫn giờ thì lấy cả hai | BR07, 08 |
| CN06-TC11 | Mức được suất | Có 20 người trên 1.500 điểm | Chỉ 10 người đầu có Mức 4 ở cột Mức được suất; cả 20 người vẫn có Mức đạt = 4 | BR09 |
| CN06-TC12 | Quyền | Nhân sự đối tác khác bấm Xuất | Bị từ chối | BR11 |
| CN06-TC13 | Điểm không cộng qua chương trình | U1 có 300 điểm ở chương trình tháng 11 và 400 điểm ở chương trình tháng 12 | File của mỗi chương trình ghi riêng (300 và 400), không có tổng 700 | BR12 |
| CN06-TC14 | Bài bị từ chối sau đối soát | Khoản của bài đã Đã hoàn thành; bài bị từ chối sau đó | Khoản vẫn tính trong file; không đổi tổng điểm | BR06 |
