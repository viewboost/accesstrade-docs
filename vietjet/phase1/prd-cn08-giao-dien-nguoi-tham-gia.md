# CN-08 · Giao diện người tham gia

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-08.1 Mục đích

App người tham gia hiện được làm cho chương trình thưởng theo lượt xem và tiền: màn cá nhân hiện "Tổng view", mốc thưởng tính theo lượt xem, bảng xếp hạng theo lượt xem, cùng các màn hoa hồng, thuế, hợp đồng. Chức năng này điều chỉnh app sang chương trình thưởng bằng **điểm** và **quà theo mức**.

**Chưa có thiết kế giao diện.** PRD này mô tả nội dung và hành vi của từng màn, không mô tả bố cục và hình thức. Thiết kế làm riêng và phải khớp PRD.

## CN-08.2 Phạm vi

**Trong phạm vi:** các màn của app người tham gia nêu ở CN-08.4 đến CN-08.9.

**Ngoài phạm vi**
- Đổi chữ "đ" thành "điểm" và màn Thông tin thanh toán: [CN-03](./prd-cn03-hien-thi-diem.md).
- Đăng nhập và đăng ký: [CN-09](./prd-cn09-dang-nhap-email-vietjet.md).
- Thông báo mới cho người tham gia: đã có thông báo trong ứng dụng, không thêm thông báo mới.
- Giới hạn số bài mỗi ngày: không có.

## CN-08.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) | Nguồn dữ liệu điểm của từng bài và trạng thái bài |
| [CN-03](./prd-cn03-hien-thi-diem.md) | Cách hiện số điểm |
| [CN-05](./prd-cn05-bang-xep-hang-thang.md) | Bảng xếp hạng tháng và điểm thưởng TOP |
| [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) | Mức thưởng và mức đã đạt |

## CN-08.4 Trang cá nhân "Thử thách của tôi"

| Hiện trạng | Thay đổi |
|---|---|
| Ô thống kê ghi "Tổng view", có "Tạm tính" và "Được duyệt" | Ô ghi **Tổng điểm** gồm: điểm hợp lệ (khoản Đã hoàn thành và Chờ đối soát), điểm **chờ duyệt**, điểm thưởng TOP tháng đã cộng (nếu có) |
| Khối "Mốc nhận thưởng" tính theo lượt xem, thưởng bằng tiền | Thay bằng **Mức thưởng** (CN-08.6) |

| Mã | Quy tắc |
|---|---|
| **CN08-BR01** | Tổng điểm hiện trên app là điểm hợp lệ của người trong chương trình đang xem: khoản **Đã hoàn thành** và **Chờ đối soát** (như bảng CN-08.4). Điểm của bài chờ duyệt hiện riêng, không cộng vào tổng điểm hợp lệ. Khác với file kết quả cuối chương trình ([CN06-BR01](./prd-cn06-muc-thuong-cuoi-ky.md)) chỉ tính khoản đã hoàn thành |
| **CN08-BR02** | Thống kê số bài: đã duyệt, chờ duyệt, từ chối hiện cạnh tổng điểm |

## CN-08.5 Danh sách bài đăng

| Hiện trạng | Thay đổi |
|---|---|
| Mỗi bài hiện lượt xem, thích, bình luận | Mỗi bài hiện **điểm của bài** |
| Trạng thái bài (chờ duyệt, từ chối) đã có | Giữ nguyên |

| Mã | Quy tắc |
|---|---|
| **CN08-BR03** | Bài chờ duyệt hiện điểm chờ duyệt; bài đã duyệt hiện điểm của bài (ví dụ `+50 điểm`); bài bị từ chối **không** hiện điểm (CN-01.4) |
| **CN08-BR04** | Không còn hiện lượt xem, thích, bình luận làm chỉ số thưởng. Cách sắp xếp "Views cao nhất" ở danh sách bài đăng của sự kiện được bỏ |
| **CN08-BR05** | Bài bị từ chối hiện lý do từ chối như hiện nay. Câu mặc định không nhắc "lượt view" |

## CN-08.6 Mức thưởng

| Mã | Quy tắc |
|---|---|
| **CN08-BR06** | Khối **Mức thưởng** hiện bốn mức theo [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md): mốc điểm (trên 200, 400, 600, 1.500), phần thưởng, số lượng |
| **CN08-BR07** | Mỗi mức có trạng thái **Đã đạt** hoặc **Chưa đạt** theo tổng điểm của người xem. Hệ thống không theo dõi việc trao quà (Operation trao bên ngoài) nên không có trạng thái Đã nhận |
| **CN08-BR08** | Khối hiện ở trang chi tiết sự kiện (cho mọi người xem) và ở trang cá nhân (kèm trạng thái của người đó) |

## CN-08.7 Bảng xếp hạng tháng

| Hiện trạng | Thay đổi |
|---|---|
| Xếp theo lượt xem hoặc tiền thưởng; cột "Views", "Kiếm được" | Xếp theo **điểm**; một cột **Điểm** |
| Có nhãn kỳ tuần/tháng | Dùng kỳ **cả chương trình** (mỗi tháng là một chương trình riêng) |

| Mã | Quy tắc |
|---|---|
| **CN08-BR09** | Bảng hiện thứ hạng, người tham gia, điểm trong kỳ |
| **CN08-BR10** | TOP 1, 2, 3 có nhãn kèm điểm thưởng bổ sung (500, 200, 100) theo [CN-05](./prd-cn05-bang-xep-hang-thang.md) |
| **CN08-BR11** | Bảng và khối "TOP" ở trang chủ được gọi tên rõ để không nhầm với danh sách bài đăng mới nhất |

## CN-08.8 Số liệu tổng quan, màn gửi bài, câu chữ

| Mã | Quy tắc |
|---|---|
| **CN08-BR12** | Các ô tổng hợp ở trang chủ và đầu trang sự kiện thay "Lượt xem", "Tiền thưởng" bằng **số bài được duyệt** và **tổng điểm đã ghi nhận** |
| **CN08-BR13** | Màn **Gửi bài đăng**: hiện hashtag bắt buộc của chương trình (#Vietjet, #ChienBinhVietjetHybrid) kèm nút sao chép; nhắc bài phải để chế độ công khai; sau khi gửi báo bài **chờ BTC duyệt, được duyệt mới có điểm**. Câu nhắc "tính thưởng", "số lượt view" được đổi sang "tính điểm" |
| **CN08-BR14** | Bỏ các câu chữ của sản phẩm cũ (ví dụ "KOC Ambassador", "Dành cho nhà sáng tạo nội dung") |
| **CN08-BR15** | Menu người tham gia có lối vào **Điểm của tôi**, **Mức thưởng**, **Bảng xếp hạng**; trang tất cả bài đăng của sự kiện có lối vào từ menu |

## CN-08.9 Các màn không phù hợp thưởng bằng điểm

Thưởng tiền mặt chuyển thẳng vào lương bên Vietjet, hệ thống này không chi trả và không vận hành thuế. **Bên này không ký hợp đồng điện tử.** Các màn và lời nhắc sau không còn dành cho người tham gia:

| Màn / nội dung | Việc làm |
|---|---|
| Quản lý hoa hồng affiliate, chương trình affiliate | Ẩn khỏi menu và đường dẫn |
| Mã số thuế, khai báo thuế | Ẩn |
| Hợp đồng điện tử | Ẩn hoàn toàn, gồm mọi bước của luồng đó (thông tin thanh toán, xác thực danh tính, mã số thuế, ký hợp đồng) |
| Thông tin định danh | Ẩn |
| Dải nhắc đầu trang "liên kết hệ thống hợp đồng để nhận tiền thanh toán" | Bỏ |
| Màn Thông tin thanh toán | Theo [CN-03](./prd-cn03-hien-thi-diem.md) mục CN-03.6 |

| Mã | Quy tắc |
|---|---|
| **CN08-BR16** | Vào thẳng đường dẫn của màn đã ẩn thì được đưa về trang chủ |

## CN-08.10 Tiến độ tới mức kế tiếp (đề xuất)

Thể lệ không có màn này; đề xuất thêm để người tham gia biết còn bao nhiêu điểm tới mức kế tiếp.

| Mã | Quy tắc |
|---|---|
| **CN08-BR17** | Trang cá nhân hiện mức kế tiếp chưa đạt và số điểm còn thiếu, ví dụ "Bạn có 380 điểm, còn 21 điểm nữa để đạt Mức 2" |
| **CN08-BR18** | Người đã đạt Mức 4 hiện "Đã đạt mức cao nhất" |
| **CN08-BR19** | Giao diện **không hiện số điểm cộng dồn qua các chương trình** của một người (tổng cả đời, số dư tích lũy). Mỗi màn chỉ hiện điểm của chương trình đang xem. Dữ liệu cộng dồn vẫn được lưu trong hệ thống, chỉ không hiển thị |

## CN-08.11 Kịch bản kiểm thử

**Dữ liệu chung:** người tham gia U1 có 3 bài TikTok đã duyệt (mỗi bài 50 điểm), 1 bài chờ duyệt (50 điểm), 1 bài bị từ chối.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN08-TC01 | Tổng điểm | U1 mở trang cá nhân | Tổng điểm 150; chờ duyệt 50; số bài: 3 duyệt, 1 chờ, 1 từ chối | BR01, 02 |
| CN08-TC02 | Điểm từng bài | Mở Danh sách bài đăng | 3 bài `+50 điểm`; bài chờ có điểm chờ duyệt; bài từ chối không có điểm và có lý do | BR03, 05 |
| CN08-TC03 | Không còn chỉ số xem | Xem một bài | Không có lượt xem, thích, bình luận làm chỉ số thưởng | BR04 |
| CN08-TC04 | Mức thưởng | U1 450 điểm xem khối Mức thưởng | Mức 1 và Mức 2 Đã đạt; Mức 3 và 4 Chưa đạt | BR06, 07 |
| CN08-TC05 | Không hiện điểm cộng dồn qua chương trình | U1 có 300 điểm ở chương trình tháng 11 và 400 điểm ở chương trình tháng 12; mở từng chương trình | Mỗi chương trình chỉ hiện điểm của nó, không có tổng 700 ở bất kỳ màn nào | BR19 |
| CN08-TC06 | Bảng xếp hạng | Mở bảng xếp hạng tháng 11 | Cột Điểm; TOP 1, 2, 3 có nhãn +500, +200, +100 | BR09, 10 |
| CN08-TC07 | Tổng quan | Mở trang chủ | Ô hiện số bài được duyệt và tổng điểm, không có "Lượt xem", "Tiền thưởng" | BR12 |
| CN08-TC08 | Gửi bài | Mở Gửi bài đăng, gửi link | Thấy hashtag bắt buộc, nhắc công khai; sau gửi thấy bài chờ BTC duyệt | BR13 |
| CN08-TC09 | Màn đã ẩn | Mở menu hồ sơ; vào thẳng đường dẫn Mã số thuế | Menu không còn các mục ẩn; đường dẫn đưa về trang chủ | CN-08.9, BR16 |
| CN08-TC10 | Tiến độ (đề xuất) | U1 380 điểm | Hiện "còn 21 điểm nữa để đạt Mức 2" | BR17 |
