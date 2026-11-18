# CN-02 · Đối soát khoản thưởng theo bài

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.2 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-02.1 Mục đích

Các khoản thưởng của [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) được đối soát và chi qua kỳ đối soát như các loại thưởng khác. Mỗi khoản gắn với **một bài**, và một người có nhiều bài thì có nhiều khoản. Vì vậy các khoản này hiện ở **tab riêng** trong kỳ đối soát, không dùng tab Milestone (mỗi người một dòng cho mỗi mốc).

Hiện trạng: các khoản đi chung tab Milestone. Chức năng này tách ra tab riêng.

## CN-02.2 Phạm vi

**Trong phạm vi**
- Tab **Thưởng theo bài** trong chi tiết kỳ đối soát.
- Lấy danh sách, duyệt và chi, từ chối từng dòng.
- Xuất Excel và số liệu tổng của kỳ có thêm nhóm này.

**Ngoài phạm vi**
- Kiểm thưởng cuối kỳ theo tổng điểm: thuộc [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md).
- Xuất kết quả cuối chương trình: thuộc [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md).

## CN-02.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) | Tạo và quản lý trạng thái các khoản thưởng được đối soát ở đây |
| [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) | Đối soát cuối kỳ dùng chung kỳ đối soát này; khoản Đã hoàn thành của CN-02 là nguồn của tổng điểm |
| [CN-03](./prd-cn03-hien-thi-diem.md) | Cách hiện số điểm ở các tab |

## CN-02.4 Luồng

1. Admin › Đối soát › tạo kỳ cho sự kiện.
2. **Lấy danh sách**: hệ thống gom các khoản đủ điều kiện (CN02-BR02) thành các dòng ở tab **Thưởng theo bài**.
3. **Duyệt**: hệ thống kiểm lại từng dòng rồi chi (CN02-BR05).

## CN-02.5 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN02-BR01** | Chi tiết kỳ đối soát có tab **Thưởng theo bài**. Mỗi khoản một dòng, gồm: người tham gia, bài (link), nhiệm vụ, số điểm, trạng thái dòng. Một người có hai bài thì có hai dòng |
| **CN02-BR02** | Khoản vào danh sách khi: đang **Chờ đối soát**, điểm lớn hơn 0, bài còn được duyệt, ngày ghi nhận khoản không quá mốc chốt của kỳ, người nhận không bị khóa |
| **CN02-BR03** | Khoản **không** vào danh sách khi: Chờ duyệt, Từ chối, 0 điểm, hoặc bài không còn được duyệt |
| **CN02-BR04** | Một khoản chỉ nằm trong một dòng của một kỳ. Hai kỳ cùng lúc không gom trùng một khoản |
| **CN02-BR05** | **Duyệt kỳ**: với mỗi dòng, hệ thống kiểm khoản còn Chờ đối soát, số điểm khớp và bài còn được duyệt. Đủ điều kiện thì điểm vào số dư người tham gia, khoản chuyển **Đã hoàn thành** và người tham gia nhận thông báo thưởng. Không đủ thì dòng chuyển **Từ chối** kèm lý do ("Thông tin thưởng không chính xác" hoặc "Thông tin nội dung không chính xác") và không chi |
| **CN02-BR06** | Từ chối từng dòng và từ chối cả kỳ hoạt động như các tab khác của kỳ đối soát |
| **CN02-BR07** | File Excel xuất của kỳ và số liệu tổng của kỳ bao gồm các dòng của tab này |

## CN-02.6 Kịch bản kiểm thử

**Dữ liệu chung:** theo CN-01.8; có các khoản: bài A 50 điểm, bài B 25 điểm (cùng người U1), một khoản 0 điểm, một khoản của bài đã bị từ chối, một khoản Chờ duyệt.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN02-TC01 | Tab mới | Tạo kỳ đối soát, Lấy danh sách | Có tab **Thưởng theo bài**; tab Milestone không chứa các khoản này | BR01 |
| CN02-TC02 | Điều kiện vào danh sách | Như dữ liệu chung | Tab chỉ có 2 dòng (50 và 25), mỗi dòng có link bài; 3 khoản còn lại không vào | BR02, 03 |
| CN02-TC03 | Hai bài cùng người | Xem dòng của U1 | Hai dòng riêng, không gộp | BR01 |
| CN02-TC04 | Hai kỳ cùng lúc | Tạo hai kỳ cùng sự kiện, Lấy danh sách đồng thời | Mỗi khoản chỉ nằm trong một kỳ | BR04 |
| CN02-TC05 | Duyệt kỳ | Duyệt kỳ ở TC02 | Hai khoản **Đã hoàn thành**; số dư U1 tăng 75; U1 nhận thông báo thưởng | BR05 |
| CN02-TC06 | Bài bị từ chối sau khi lập kỳ | Lấy danh sách, từ chối bài A, rồi duyệt kỳ | Dòng của bài A bị **Từ chối** ("Thông tin nội dung không chính xác"), không chi; dòng bài B vẫn chi | BR05 |
| CN02-TC07 | Từ chối một dòng | Từ chối dòng của bài B trước khi duyệt | Dòng bài B không chi; dòng khác vẫn chi | BR06 |
| CN02-TC08 | Xuất Excel | Xuất file của kỳ | File có các dòng thưởng theo bài | BR07 |
