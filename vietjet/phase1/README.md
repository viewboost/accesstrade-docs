# Chiến binh Vietjet Hybrid — Phase 1

**Author:** Vinh Nguyễn
**Cập nhật:** 2026-11-16
**Phạm vi:** App người tham gia (Ambassador Vietjet) và Admin

Thư mục này chứa các PRD của phase 1. **Mỗi chức năng một file**, đọc độc lập; file này là mục lục chung.

## 1. Mục tiêu phase 1

Cán bộ nhân viên Vietjet đăng bài lên mạng xã hội và gửi link về hệ thống. BTC duyệt bài, người tham gia tích điểm theo từng bài và nhận thưởng theo tổng điểm cuối kỳ. Thể lệ chương trình: [bản gốc](https://docs.google.com/document/d/1F9rp4qd4KlchqKSQSZj4wzlScA_17utaqg996wBGnko/edit?tab=t.0).

## 2. Danh sách chức năng

| Mã | Chức năng | Tài liệu | Trạng thái |
|---|---|---|---|
| CN-01 | Điểm cố định cho mỗi bài được duyệt (kèm điều kiện kích hoạt sự kiện) | [prd-cn01-diem-co-dinh-moi-bai.md](./prd-cn01-diem-co-dinh-moi-bai.md) | Đã viết |
| CN-02 | Đối soát khoản thưởng theo bài | [prd-cn02-doi-soat-thuong-theo-bai.md](./prd-cn02-doi-soat-thuong-theo-bai.md) | Đã viết |
| CN-03 | Hiển thị điểm thay cho tiền (chữ "điểm", màn Thông tin thanh toán) | [prd-cn03-hien-thi-diem.md](./prd-cn03-hien-thi-diem.md) | Đã viết |
| CN-04 | Kiểm tra trùng nội dung video | [prd-cn04-kiem-tra-trung-noi-dung.md](./prd-cn04-kiem-tra-trung-noi-dung.md) | Đã viết |
| CN-05 | Bảng xếp hạng tháng: tải file và thưởng bổ sung TOP | [prd-cn05-bang-xep-hang-thang.md](./prd-cn05-bang-xep-hang-thang.md) | Đã viết |
| CN-06 | Mức thưởng cuối kỳ và trao quà (tổng điểm, mức 1–4, hết suất) | [prd-cn06-muc-thuong-cuoi-ky.md](./prd-cn06-muc-thuong-cuoi-ky.md) | Đã viết |
| CN-07 | Điểm sau trao thưởng, chu kỳ và thu hồi điểm | [prd-cn07-diem-sau-trao-thuong.md](./prd-cn07-diem-sau-trao-thuong.md) | Đã viết |
| CN-08 | Giao diện người tham gia | [prd-cn08-giao-dien-nguoi-tham-gia.md](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Đã viết |
| CN-09 | Đăng nhập bằng email Vietjet và đăng ký bằng mã nhân viên | [prd-cn09-dang-nhap-email-vietjet.md](./prd-cn09-dang-nhap-email-vietjet.md) | Đã viết |

**Tài liệu tham chiếu** (hành vi có sẵn của hệ thống, không phải chức năng mới):

| Tài liệu | Nội dung |
|---|---|
| [ref-nen-tang-loai-bai.md](./ref-nen-tang-loai-bai.md) | Nền tảng và loại bài hệ thống nhận, cách đặt điểm bài post và video, cách nhận biết loại bài, hashtag chương trình |
| [qa-kiem-thu-tron-luong.md](./qa-kiem-thu-tron-luong.md) | Kiểm thử trọn luồng từ đăng bài đến nhận thưởng, nối các kịch bản của các chức năng |

## 3. Quy ước mã

| Loại | Dạng mã | Ví dụ |
|---|---|---|
| Chức năng | `CN-xx` | CN-01 |
| Mục của một PRD | `CN-xx.y` | CN-01.4 |
| Quy tắc nghiệp vụ | `CNxx-BRnn` | CN01-BR05 |
| Kịch bản kiểm thử | `CNxx-TCnn` | CN01-TC07 |

Tài liệu khác tham chiếu bằng mã đầy đủ (ví dụ `CN01-BR05`), không dùng số thứ tự mục.

## 4. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Điểm** | Đơn vị thưởng của chương trình. Trong hệ thống 1 điểm = 1 đ; hiển thị là "điểm" theo CN-03 |
| **Bài** | Một bài đăng hoặc video người tham gia gửi link về hệ thống. Trong Admin gọi là nội dung |
| **Nguồn** | Nền tảng kèm loại bài (TikTok, Facebook Reels, Facebook Post...). Xem [ref-nen-tang-loai-bai.md](./ref-nen-tang-loai-bai.md) |
| **Nhiệm vụ** | Một quy tắc thưởng của sự kiện, quản lý ở tab **Nhiệm vụ** của sự kiện trong Admin |
| **Khoản thưởng** | Một dòng thưởng của một người, gắn với một bài và một nhiệm vụ |
| **Trạng thái khoản** | **Chờ duyệt** (bài chưa được duyệt) · **Chờ đối soát** (bài đã duyệt, tên kỹ thuật `pending`) · **Đã hoàn thành** (đã đối soát và chi) · **Từ chối** |
| **Đối soát** | Admin › Đối soát: tạo kỳ, lấy danh sách, duyệt; duyệt xong điểm vào số dư người tham gia |
| **Ngân sách** | Ba hạn mức của sự kiện: **chiến dịch**, **creator** (mỗi người tham gia), **nội dung** (mỗi bài). Cấu hình ở tab Ngân sách |
| **Số suất** | Giới hạn tổng số khoản mà một nhiệm vụ được trả (ô "Số lượng" của nhiệm vụ) |
