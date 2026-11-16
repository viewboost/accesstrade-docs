# CN-09 · Đăng nhập bằng email Vietjet và đăng ký bằng mã nhân viên

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-09.1 Mục đích

Chương trình chỉ dành cho cán bộ nhân viên Vietjet. Hệ thống hiện cho đăng nhập bằng tài khoản mạng xã hội (TikTok, Facebook, Google) và hỏi mã nhân viên ở một bước riêng sau khi đăng nhập. Chức năng này thêm:

1. Đăng nhập bằng **email**, chỉ cho phép email thuộc **tên miền của Vietjet**.
2. Màn **đăng ký yêu cầu nhập mã nhân viên** ngay lúc đăng ký.

Ví dụ: nhân viên dùng email công ty Vietjet đăng ký, nhập mã nhân viên và vào được chương trình. Người dùng email Gmail cá nhân bị từ chối.

## CN-09.2 Phạm vi

**Trong phạm vi**
- Đăng nhập và đăng ký bằng email.
- Danh sách tên miền email được phép (allow list).
- Nhập mã nhân viên ở màn đăng ký.

**Ngoài phạm vi**
- Xác minh mã nhân viên với danh sách của HR Vietjet: mã nhân viên kiểm theo quy tắc sẵn có của hệ thống (CN09-BR05).
- Thay đổi hoặc gỡ mã nhân viên của tài khoản đã đăng ký: giữ theo hành vi sẵn có (phải nhờ bộ phận hỗ trợ).

## CN-09.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Các màn của app sau khi đăng nhập |

## CN-09.4 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN09-BR01** | Màn đăng nhập có lựa chọn **đăng nhập bằng email** |
| **CN09-BR02** | Chỉ email có **tên miền thuộc danh sách tên miền được phép** mới đăng ký và đăng nhập được. So khớp không phân biệt hoa thường |
| **CN09-BR03** | Email ngoài danh sách bị từ chối kèm thông báo rõ: email phải là email công ty Vietjet |
| **CN09-BR04** | Danh sách tên miền được phép do Admin cấu hình; để trống thì không email nào được phép đăng ký bằng email |
| **CN09-BR05** | Màn **đăng ký** bắt buộc nhập **mã nhân viên** cùng lúc. Không nhập thì không hoàn tất đăng ký. Mã đã gắn với tài khoản khác thì bị từ chối (một mã một tài khoản), theo quy tắc mã nhân viên sẵn có |
| **CN09-BR06** | Email phải được xác thực (người dùng bấm vào liên kết hoặc nhập mã gửi tới email) trước khi vào chương trình |
| **CN09-BR07** | Người đã có tài khoản mạng xã hội và mã nhân viên từ trước vẫn đăng nhập như cũ, không bị bắt đăng ký lại |
| **CN09-BR08** | Các cách đăng nhập khác (TikTok, Facebook, Google) vẫn còn nếu không có quyết định bỏ; tài khoản đăng nhập bằng cách đó vẫn phải có mã nhân viên mới tham gia được chương trình |

## CN-09.5 Kịch bản kiểm thử

**Dữ liệu chung:** danh sách tên miền được phép có tên miền Vietjet; mã nhân viên NV001 chưa ai dùng.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN09-TC01 | Đăng ký đúng | Đăng ký bằng email Vietjet, nhập NV001, xác thực email | Tạo tài khoản, vào được chương trình | BR01, 05, 06 |
| CN09-TC02 | Email ngoài danh sách | Đăng ký bằng email Gmail | Bị từ chối, thông báo phải dùng email Vietjet | BR02, 03 |
| CN09-TC03 | Hoa thường | Đăng ký bằng email có chữ hoa trong tên miền | Vẫn được chấp nhận | BR02 |
| CN09-TC04 | Thiếu mã nhân viên | Đăng ký bằng email Vietjet, để trống mã | Không hoàn tất, báo thiếu mã nhân viên | BR05 |
| CN09-TC05 | Mã đã dùng | Người thứ hai đăng ký với NV001 | Bị từ chối, báo mã đã được dùng | BR05 |
| CN09-TC06 | Chưa xác thực email | Đăng ký xong, chưa xác thực | Chưa vào được chương trình | BR06 |
| CN09-TC07 | Danh sách trống | Xóa hết tên miền trong cấu hình | Mọi email bị từ chối | BR04 |
| CN09-TC08 | Tài khoản cũ | Người đã có tài khoản mạng xã hội và mã nhân viên đăng nhập | Vào như trước | BR07 |
| CN09-TC09 | Đăng nhập mạng xã hội chưa có mã | Đăng nhập TikTok, chưa có mã nhân viên | Phải nhập mã nhân viên mới tham gia được | BR08 |
