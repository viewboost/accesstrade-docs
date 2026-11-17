# CN-05 · Bảng xếp hạng tháng và thưởng bổ sung TOP

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.3 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-05.1 Mục đích

Thể lệ có **thưởng bổ sung hàng tháng** theo Bảng vinh danh:

| Thứ hạng | Điểm thưởng bổ sung | Số lượng |
|---|---|---|
| TOP 1 | 500 điểm | 1 |
| TOP 2 | 200 điểm | 2 |
| TOP 3 | 100 điểm | 3 |

BTC cần danh sách TOP của tháng để xem và xác nhận trước khi cộng điểm. Hệ thống đã có bảng xếp hạng nhưng chưa tải được ra file. Chức năng này thêm **tải file danh sách bảng xếp hạng** ngay trong bảng xếp hạng ở Admin.

Theo Vietjet, **mỗi tháng tạo một chương trình (sự kiện) riêng**, có bảng xếp hạng và điểm riêng. Vì vậy bảng xếp hạng tháng chính là bảng xếp hạng **cả chương trình** của sự kiện đó, kỳ "cả chương trình" (không cần chọn kỳ tuần hoặc tháng).

Ví dụ: cuối chương trình tháng 11, BTC mở bảng xếp hạng của sự kiện tháng 11, bấm **Tải file**, nhận danh sách người xếp hạng.

## CN-05.2 Phạm vi

**Trong phạm vi**
- Nút **Tải file** ở tab **Bảng xếp hạng** của sự kiện trong Admin.
- Nội dung và quyền của file.

**Ngoài phạm vi**
- Cách xếp hạng và cách hiển thị bảng xếp hạng: đã có sẵn (CN-05.3).
- Tự cộng điểm thưởng TOP: BTC cộng bằng chức năng **Thưởng thêm** có sẵn (CN-05.6).
- Hiển thị bảng xếp hạng cho người tham gia: thuộc [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md).

## CN-05.3 Hiện trạng đã có

| Nội dung | Hiện trạng |
|---|---|
| Tab **Bảng xếp hạng** của sự kiện (Admin) | Có. Xem bảng theo kỳ: cả chương trình, tuần hoặc tháng |
| Kỳ xếp hạng | Tuần hoặc tháng, cấu hình ở tab. Trong vài ngày đầu của kỳ mới, bảng vẫn hiện kỳ trước (ân hạn chốt số) |
| Giá trị xếp hạng | Theo cấu hình của sự kiện. Chương trình điểm dùng điểm thưởng để xếp hạng |
| Ghim người lên đầu bảng | Có |

## CN-05.4 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Người tham gia xem bảng xếp hạng tháng theo điểm |
| [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) | Điểm thưởng TOP đã cộng nằm trong tổng điểm hợp lệ |

## CN-05.5 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN05-BR01** | Tab Bảng xếp hạng có nút **Tải file**. Bấm thì hệ thống tạo file Excel của **kỳ đang xem** và gửi như các file xuất khác của Admin |
| **CN05-BR02** | File gồm các cột: Thứ hạng, Người tham gia, Điểm trong kỳ, và dòng đầu ghi khoảng kỳ (từ ngày – đến ngày). Danh sách giống bảng đang hiện (cùng thứ tự, kể cả người được ghim) |
| **CN05-BR03** | File có **toàn bộ** danh sách của kỳ, không chỉ trang đang xem |
| **CN05-BR04** | Chỉ người có quyền xuất dữ liệu của sự kiện mới tải được. Nhân sự thuộc đối tác khác không tải được bảng xếp hạng của sự kiện không thuộc đối tác của họ |
| **CN05-BR05** | Bảng xếp hạng của kỳ chưa chốt số (đang trong ân hạn) vẫn tải được; file ghi rõ kỳ đang hiển thị |
| **CN05-BR06** | Bằng điểm trong kỳ thì người **đạt điểm đó sớm hơn** xếp trên, theo cùng quy tắc của [CN06-BR05](./prd-cn06-muc-thuong-cuoi-ky.md) (giờ đăng bài của khoản thưởng hợp lệ gần nhất trong kỳ; vẫn bằng thì theo mã người dùng nhỏ hơn). Áp dụng cho cả bảng đang hiện và file tải về, để TOP 2 và TOP 3 (2 và 3 suất) không phụ thuộc thứ tự tạo bản ghi |
| **CN05-BR07** | Cấu hình bảng xếp hạng có tùy chọn **Cộng điểm Thưởng thêm vào bảng xếp hạng**, mặc định **tắt** (giữ như hiện nay). Bật thì điểm xếp hạng của một người = điểm các khoản thưởng + điểm **Thưởng thêm** (điểm TOP) đã hoàn thành của người đó trong sự kiện, và thời điểm đạt tổng điểm (CN05-BR06) tính cả khoản Thưởng thêm. Áp dụng cho bảng đang hiện và file tải về, ở cả cấu hình sự kiện và cấu hình đối tác. Tắt khi cần chọn TOP bằng điểm bài đăng; bật sau khi đã cộng điểm TOP để bảng khớp với file kết quả cuối chương trình (CN-06) |

## CN-05.6 Cộng điểm thưởng TOP

Không có chức năng mới. BTC xem file, xác nhận danh sách rồi nhập khoản **Thưởng thêm** cho từng người (nhập tay hoặc nhập từ Excel) với số điểm 500, 200 hoặc 100. Khoản thưởng thêm được đối soát như các khoản thưởng khác.

## CN-05.7 Kịch bản kiểm thử

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN05-TC01 | Tải file chương trình tháng | Mở sự kiện tháng 11 (kỳ cả chương trình), bấm Tải file | Nhận file Excel có khoảng kỳ của chương trình và danh sách đúng thứ tự bảng | BR01, 02 |
| CN05-TC02 | Đủ danh sách | Kỳ có 120 người, bảng hiện 20 người mỗi trang | File có đủ 120 dòng | BR03 |
| CN05-TC03 | Có người ghim | Một người được ghim lên đầu | File có người đó ở đầu, giống bảng | BR02 |
| CN05-TC04 | Quyền | Nhân sự đối tác khác bấm Tải file bảng xếp hạng của sự kiện này | Bị từ chối | BR04 |
| CN05-TC06 | Bằng điểm ở ranh giới TOP | Hai người cùng điểm, một người đăng bài cuối lúc 09:00, người kia lúc 18:00 cùng ngày; chỉ còn 1 suất TOP 3 | Người đăng sớm hơn được xếp trên, ở cả bảng và file | BR06 |
| CN05-TC07 | Tùy chọn tắt | Người A 600 điểm bài, người B 500 điểm bài và 200 điểm Thưởng thêm đã hoàn thành; tùy chọn tắt | A xếp trên B | BR07 |
| CN05-TC08 | Tùy chọn bật | Như TC07, bật tùy chọn | B (700) xếp trên A (600), cả bảng và file | BR07 |
| CN05-TC09 | Thưởng thêm chưa hoàn thành | B có 200 điểm Thưởng thêm đang chờ đối soát; tùy chọn bật | Điểm B chỉ tính khoản đã hoàn thành (500) | BR07 |
| CN05-TC05 | Kỳ chưa chốt | Tải file trong ân hạn đầu kỳ mới | File là kỳ trước và ghi rõ khoảng kỳ | BR05 |
