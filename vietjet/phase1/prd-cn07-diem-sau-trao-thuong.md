# CN-07 · Điểm sau trao thưởng, chu kỳ và thu hồi điểm

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-07.1 Mục đích

Sau khi trao thưởng ([CN-06](./prd-cn06-muc-thuong-cuoi-ky.md)) hệ thống phải quy định ba việc:

1. Điểm của người tham gia thay đổi thế nào sau khi nhận quà.
2. Khi sang **chu kỳ** mới, điểm xét thưởng tính lại ra sao.
3. Khi phát hiện gian lận sau đối soát, điểm bị thu hồi thế nào.

Ví dụ: nhân viên 650 điểm nhận Mức 3, vẫn thấy 650 điểm và Mức 3 được đánh dấu đã nhận. Sang tháng sau điểm xét thưởng bắt đầu lại từ 0. Một bài của người này bị phát hiện gian lận 100 điểm sau đối soát: điểm giảm 100.

## CN-07.2 Phạm vi

**Trong phạm vi**
- Giữ nguyên điểm sau khi trao thưởng và đánh dấu mức đã nhận.
- Chu kỳ xét thưởng và mốc chốt chu kỳ.
- Điều chỉnh trừ điểm sau đối soát.

**Ngoài phạm vi**
- Thu lại quà đã trao: quà không trao tự động nên không có bước thu hồi trong hệ thống.
- Tìm gian lận: BTC phát hiện và quyết định.

## CN-07.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) | Mức đã nhận, tổng điểm hợp lệ và số suất theo chu kỳ |
| [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md) | Khoản đã đối soát là nguồn của điểm bị điều chỉnh |

## CN-07.4 Điểm sau khi trao thưởng

| Mã | Quy tắc |
|---|---|
| **CN07-BR01** | Trao thưởng không trừ điểm. Người tham gia đạt Mức 3 với 650 điểm vẫn có 650 điểm |
| **CN07-BR02** | Mức đã nhận được đánh dấu theo CN06-BR08. Mức đã nhận không bị xét lại khi người đó có thêm điểm |
| **CN07-BR03** | Điểm đã kiếm được lưu lại sau khi chu kỳ kết thúc, để dùng cho việc khác về sau. Chức năng này không dùng điểm đã kiếm cho việc gì khác |

## CN-07.5 Chu kỳ

**Chu kỳ** là khoảng thời gian xét thưởng của sự kiện: tổng điểm hợp lệ, mức thưởng và số suất của [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) đều tính **trong một chu kỳ**. Độ dài chu kỳ (mỗi tháng hay cả chương trình) là thiết lập của sự kiện.

| Mã | Quy tắc |
|---|---|
| **CN07-BR04** | Sang chu kỳ mới, tổng điểm xét thưởng của mỗi người tính lại từ 0. Chỉ các khoản có ngày tính thuộc chu kỳ mới được cộng vào |
| **CN07-BR05** | Admin **chốt chu kỳ** sau khi chi trả xong: hệ thống ghi mốc chốt (ngày và người chốt). Khoản có ngày tính sau mốc thuộc chu kỳ kế tiếp |
| **CN07-BR06** | Khi chốt, Admin xuất được **danh sách đã chi trả** của chu kỳ: người nhận, mức, loại quà, trạng thái trao |
| **CN07-BR07** | Không chốt chu kỳ khi còn dòng ở trạng thái **Chưa trao** chưa xử lý. Hệ thống báo số dòng còn lại để Admin xem |
| **CN07-BR08** | Chu kỳ đã chốt không sửa được khoản thưởng của nó. Phát hiện sai sót thì xử lý bằng điều chỉnh điểm ở CN-07.6 |

## CN-07.6 Thu hồi điểm sau đối soát

Khoản thưởng đã **Đã hoàn thành** không đổi trạng thái khi bài bị từ chối về sau ([CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) tình huống B). Điểm của khoản đó muốn bị trừ thì Admin tạo **điều chỉnh trừ điểm**.

| Mã | Quy tắc |
|---|---|
| **CN07-BR09** | Admin tạo điều chỉnh trừ điểm cho một người: số điểm, bài liên quan (nếu có), lý do (bắt buộc). Điểm trừ không vượt quá tổng điểm hợp lệ hiện có của người đó |
| **CN07-BR10** | Điều chỉnh làm tổng điểm hợp lệ giảm (CN06-BR01). Số dư điểm hiển thị cho người tham gia cũng giảm tương ứng |
| **CN07-BR11** | Điều chỉnh không sửa hay xóa khoản thưởng gốc; có lịch sử điều chỉnh (ai tạo, lúc nào, lý do) xem được ở Admin |
| **CN07-BR12** | Sau điều chỉnh, người tham gia không còn đạt mức nào đó nữa mà mức đó **đã được trao** thì dòng của mức này được gắn nhãn **Cần xem xét** trong danh sách trao quà. Hệ thống không tự thu hồi quà, Operation xử lý |
| **CN07-BR13** | Mức chưa trao mà không còn đạt thì bị loại khỏi danh sách trao quà |

## CN-07.7 Kịch bản kiểm thử

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN07-TC01 | Giữ điểm | U1 650 điểm nhận Mức 3 (đã trao) | U1 vẫn 650 điểm, Mức 3 đã nhận | BR01, 02 |
| CN07-TC02 | Có thêm điểm | U1 thêm 20 điểm sau khi nhận Mức 3 | Mức 3 vẫn đã nhận, không trao lại | BR02 |
| CN07-TC03 | Chu kỳ mới | Chốt chu kỳ tháng 11; U1 có bài mới ngày 05/12, 50 điểm | Tổng điểm xét thưởng tháng 12 của U1 = 50 | BR04, 05 |
| CN07-TC04 | Điểm đã kiếm giữ lại | Sau TC03, xem tổng điểm đã kiếm của U1 | Còn ghi nhận phần điểm của chu kỳ trước | BR03 |
| CN07-TC05 | Chốt khi còn Chưa trao | Chốt chu kỳ khi còn 3 dòng Chưa trao | Báo còn 3 dòng, không cho chốt | BR07 |
| CN07-TC06 | Danh sách đã chi | Chốt chu kỳ, xuất danh sách | File có người nhận, mức, loại quà, trạng thái | BR06 |
| CN07-TC07 | Sửa khoản chu kỳ đã chốt | Sửa khoản thưởng của chu kỳ đã chốt | Không sửa được | BR08 |
| CN07-TC08 | Trừ điểm | Admin trừ 100 điểm của U1 (650), lý do gian lận | Tổng điểm U1 = 550; có dòng lịch sử điều chỉnh | BR09, 10, 11 |
| CN07-TC09 | Trừ quá số điểm | Trừ 700 điểm với U1 650 điểm | Bị từ chối | BR09 |
| CN07-TC10 | Mất mức đã trao | Mức 3 đã trao cho U1; trừ 100 làm U1 còn 550 | Dòng Mức 3 của U1 gắn **Cần xem xét**; quà không bị hệ thống thu hồi | BR12 |
| CN07-TC11 | Mất mức chưa trao | Như TC10 nhưng Mức 3 chưa trao | Dòng Mức 3 bị loại khỏi danh sách trao quà | BR13 |
