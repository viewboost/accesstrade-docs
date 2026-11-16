# CN-03 · Hiển thị điểm thay cho tiền

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-03.1 Mục đích

Chương trình thưởng bằng **điểm**, không phải tiền. Hệ thống hiện hiển thị mọi khoản thưởng bằng đơn vị "đ" và có các màn dành cho thanh toán tiền. Chức năng này đổi cách hiển thị cho đúng chương trình.

Hệ thống chỉ lưu con số, không lưu đơn vị. Chữ "đ" chỉ được thêm lúc hiển thị, nên chức năng này không đổi dữ liệu đã lưu.

Ví dụ: số dư 150.000đ hiện thành 150.000 điểm; cột "Tổng tiền" ở màn đối soát thành "Tổng điểm".

## CN-03.2 Phạm vi

**Trong phạm vi**
- App người tham gia: mọi chỗ hiện số thưởng.
- Admin: danh sách, báo cáo, thống kê, màn đối soát, màn ngân sách.
- File Excel xuất từ Admin.
- Màn **Thông tin thanh toán** và các lối dẫn tới màn này ở app người tham gia.

**Ngoài phạm vi**
- Đổi tên trường dữ liệu, API, hoặc dữ liệu đã lưu.
- Đổi bố cục màn hình: thuộc [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md).
- Màn hoa hồng affiliate, mã số thuế, định danh, hợp đồng điện tử: thuộc CN-08.

## CN-03.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md), [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md) | Các màn của hai chức năng này hiển thị theo CN-03 |
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Các màn người tham gia hiển thị điểm theo quy tắc ở đây |

## CN-03.4 Quy tắc hiển thị

| Mã | Quy tắc |
|---|---|
| **CN03-BR01** | Số thưởng hiện dạng `{số} điểm`, nhóm hàng nghìn bằng dấu chấm. Ví dụ `150.000 điểm`. Không còn chữ "đ", "VNĐ", "VND" đi kèm số thưởng |
| **CN03-BR02** | Số rút gọn (nghìn, triệu, tỷ) vẫn rút gọn như hiện nay và có chữ "điểm" |
| **CN03-BR03** | Nhãn nói về tiền được đổi sang điểm theo bảng CN-03.5 |
| **CN03-BR04** | Áp dụng cho toàn bộ app người tham gia, toàn bộ Admin và mọi file Excel xuất ra. Không có chế độ giữ "đ" ở nơi nào |
| **CN03-BR05** | Giá trị lưu và API giữ nguyên. Chỉ đổi chữ hiển thị và tiêu đề cột |
| **CN03-BR06** | Khi chỗ nào cần mô tả số tiền thật (nếu còn, ví dụ phần chuyển khoản cũ), giữ chữ tiền và báo để quyết định riêng, không tự đổi |

## CN-03.5 Bảng đổi nhãn

| Nhãn hiện tại | Nhãn mới |
|---|---|
| Tiền thưởng | Điểm thưởng |
| Tổng tiền | Tổng điểm |
| Kiếm được | Điểm |
| Số tiền (khoản thưởng) | Số điểm |
| Tổng tiền thưởng | Tổng điểm thưởng |

Các nhãn còn lại có nghĩa là thưởng bằng tiền được đổi tương tự theo CN03-BR03.

## CN-03.6 Màn Thông tin thanh toán

Điểm không đổi thành tiền để rút. Thưởng tiền mặt của Mức 3 và Mức 4 được chuyển thẳng vào lương bên Vietjet, hệ thống này không chi trả và không vận hành thuế. Vì vậy màn **Thông tin thanh toán** (tài khoản ngân hàng, đợi thanh toán, kỳ thanh toán, lịch sử thanh toán) không còn dành cho người tham gia.

| Mã | Quy tắc |
|---|---|
| **CN03-BR07** | Menu hồ sơ của người tham gia không còn mục **Thanh toán** |
| **CN03-BR08** | Người tham gia vào thẳng đường dẫn của màn Thông tin thanh toán thì được đưa về trang chủ |
| **CN03-BR09** | Các chỗ dẫn người dùng tới màn này (nút, lời nhắc, bước trong luồng khác) bị ẩn. Các câu nhắc "để nhận được tiền thanh toán" bị bỏ |
| **CN03-BR10** | Không có nút hay chữ "rút tiền" nào ở app người tham gia |

## CN-03.7 Kịch bản kiểm thử

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN03-TC01 | Số thưởng ở app | Người tham gia có 150.000 điểm; mở trang cá nhân, danh sách bài đăng, bảng xếp hạng | Mọi số thưởng hiện `điểm`, không có "đ" | BR01 |
| CN03-TC02 | Số rút gọn | Tổng điểm của chương trình là 1.500.000 | Hiện dạng rút gọn kèm chữ điểm | BR02 |
| CN03-TC03 | Admin | Mở danh sách khoản thưởng, thống kê, ngân sách, đối soát | Nhãn và số hiện theo điểm | BR01, 03, 04 |
| CN03-TC04 | File xuất | Xuất file đối soát và file thưởng thêm | Tiêu đề cột và số hiển thị theo điểm | BR04 |
| CN03-TC05 | Dữ liệu không đổi | So số lưu trước và sau | Giá trị bằng nhau | BR05 |
| CN03-TC06 | Mục Thanh toán | Mở menu hồ sơ | Không có mục Thanh toán | BR07 |
| CN03-TC07 | Vào thẳng đường dẫn | Mở đường dẫn màn Thông tin thanh toán | Về trang chủ | BR08 |
| CN03-TC08 | Lời nhắc | Người tham gia chưa có thông tin thanh toán | Không còn lời nhắc nào về nhận tiền thanh toán | BR09 |
