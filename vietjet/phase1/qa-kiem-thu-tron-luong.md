# QA · Kiểm thử trọn luồng từ đăng bài đến nhận thưởng

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## QA.1 Mục đích

Kiểm thử cả luồng của chương trình, nối các chức năng CN-01 đến CN-09. Tài liệu này không có quy tắc mới; mỗi bước dẫn tới kịch bản chi tiết của chức năng tương ứng.

## QA.2 Dữ liệu chuẩn

- Sự kiện đang chạy nhận TikTok, Facebook Reels, Facebook Post. Nhiệm vụ **Cố định mỗi bài được duyệt**: TikTok 50, Facebook Reels 50, Facebook Post 25. Bảng quy đổi theo thể lệ chương trình đang chạy.
- Bốn mức thưởng theo thể lệ (trên 200, 400, 600, 1.500 điểm). Mỗi tháng là một chương trình riêng: bảng xếp hạng kỳ **cả chương trình**, xếp theo điểm thưởng.
- Người tham gia U1 (email công ty Vietjet, có mã nhân viên), U2, U3.

## QA.3 Luồng chính

| Bước | Hành động | Kết quả mong đợi | Chi tiết ở |
|---|---|---|---|
| 1 | U1 đăng ký bằng email Vietjet và mã nhân viên | Vào được chương trình | CN09-TC01 |
| 2 | U1 gửi 4 video TikTok và 2 bài Facebook Post | Danh sách bài đăng hiện 6 bài chờ duyệt, điểm chờ duyệt 250 | CN01-TC01, CN08-TC02 |
| 3 | BTC duyệt cả 6 bài | 6 khoản **Chờ đối soát**; U1 có tổng 250 điểm, đạt Mức 1 (trên 200) | CN01-TC10, CN08-TC04 |
| 4 | Tạo kỳ đối soát theo bài, Lấy danh sách | Tab **Thưởng theo bài** có 6 dòng của U1 | CN02-TC01, 02, 03 |
| 5 | Duyệt kỳ đối soát | 6 khoản **Đã hoàn thành**, điểm vào số dư | CN02-TC05 |
| 6 | Xem bảng xếp hạng chương trình và tải file TOP | Có U1 trong bảng; file đủ danh sách | CN05-TC01, 02 |
| 6a | BTC xác nhận TOP, nhập **Thưởng thêm** 500/200/100, đối soát khoản Thưởng thêm | Điểm TOP của U1 (nếu TOP) thành **Đã hoàn thành** | CN-05.6 |
| 6b | Bật tùy chọn cộng Thưởng thêm vào bảng xếp hạng | Bảng hiện điểm gồm TOP, khớp file cuối chương trình | CN05-TC07, 08, 09 |
| 7 | Hết chương trình, Xuất kết quả cuối chương trình | U1 một dòng: tổng 250 điểm, Mức đạt = 1 | CN06-TC01, 02 |
| 8 | Kiểm file: bằng điểm thì người đăng bài sớm hơn xếp trên | Thứ tự đúng theo giờ đăng bài | CN06-TC06, 07 |
| 9 | U1 xem app | Mức 1 hiện Đã đạt; mọi số hiện "điểm" | CN08-TC04, CN03-TC01 |

## QA.4 Các nhánh phải chạy

| Nhánh | Kịch bản |
|---|---|
| Bài bị từ chối trước khi đối soát, rồi duyệt lại | CN01-TC06, 07 |
| Bài bị từ chối sau khi lập kỳ, trước khi duyệt kỳ | CN02-TC06 |
| Bài bị từ chối sau khi đối soát (khoản vẫn tính, xử lý tay) | CN01-TC08, 09; CN06-TC14 |
| Hết suất của nhiệm vụ | CN01-TC14 |
| Hết ngân sách | CN01-TC15 đến 19 |
| Bài nghi trùng | CN04-TC01 đến 04 |
| Mức được suất khi nhiều người cùng đạt | CN06-TC11 |
| Gian lận phát hiện trước đối soát cuối: từ chối bài thì điểm mất | CN01-TC06, CN06-TC08 |
| Điểm không cộng qua chương trình | CN06-TC13 |
| Email ngoài tên miền, thiếu mã nhân viên | CN09-TC02, 04 |
| Màn ẩn không vào được | CN03-TC06, 07; CN08-TC09 |
