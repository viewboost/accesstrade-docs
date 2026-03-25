# Quản lý mã nhân viên

![image.png](Qu%E1%BA%A3n%20l%C3%BD%20m%C3%A3%20nh%C3%A2n%20vi%C3%AAn/image.png)

## 1. Truy cập chức năng Quản lý mã

### Bước 1: Đăng nhập hệ thống Admin

- Truy cập trang admin với quyền Administrator
- Đăng nhập bằng tài khoản có quyền quản lý

### Bước 2: Vào menu Quản lý mã

- Từ menu bên trái, click vào **"Quản lý mã"**
- Hệ thống sẽ hiển thị danh sách tất cả mã nhân viên

## 2. Giao diện chính

### Các cột thông tin hiển thị:

- **CODE**: Mã nhân viên (demo1, demo2, TEST01,...)
- **ĐỐI TÁC**: Tên đối tác (Techcombank)
- **TRẠNG THÁI**:
    - "Chưa sử dụng" (màu xanh): Mã chưa được sử dụng
    - "Đã sử dụng": Mã đã được sử dụng bởi user
- **NGÀY TẠO**: Thời gian tạo mã (15:15 09/01/2026)
- **ACTION**: Các thao tác có thể thực hiện (xóa, sửa)

### Thanh công cụ:

- **Tạo mới**: Nút đỏ để thêm mã mới
- **Nhập từ Excel**: Nút xanh để import mã từ file Excel
- **Tìm theo mã**: Ô tìm kiếm theo mã code
- **Trạng thái**: Bộ lọc theo trạng thái sử dụng

## 3. Thêm mã nhân viên mới

### Bước 1: Click nút "Tạo mới"

- Click vào nút đỏ **"Tạo mới"** ở góc phải trên

### Bước 2: Nhập thông tin

- **Mã nhân viên**: Nhập mã duy nhất (bắt buộc)
- **Đối tác**: Chọn đối tác từ dropdown
- **Ghi chú**: Thông tin bổ sung (tùy chọn)

### Bước 3: Lưu thông tin

- Click **"Lưu"** để tạo mã mới
- Hệ thống sẽ hiển thị thông báo thành công
- Mã mới sẽ xuất hiện trong danh sách với trạng thái "Chưa sử dụng"

## 4. Import mã từ Excel

### Bước 1: Chuẩn bị file Excel

- Tạo file Excel với các cột:
    - Cột A: Mã nhân viên
- Lưu file với định dạng .xlsx hoặc .xls

### Bước 2: Thực hiện import

- Click nút **"Nhập từ Excel"**
- Chọn **Đối tác** từ dropdown
- Click **"Chọn file"** và chọn file Excel đã chuẩn bị
- Click **"Import"**

### Bước 3: Kiểm tra kết quả

- Hệ thống sẽ hiển thị số lượng mã được import thành công
- Các mã mới sẽ xuất hiện trong danh sách
- Nếu có lỗi, hệ thống sẽ hiển thị chi tiết lỗi

## 5. Tìm kiếm và lọc

### Tìm kiếm theo mã:

- Nhập mã cần tìm vào ô **"Tìm theo mã"**
- Hệ thống sẽ lọc và hiển thị kết quả phù hợp

### Lọc theo trạng thái:

- Click dropdown **"Trạng thái"**
- Chọn:
    - **Tất cả**: Hiển thị tất cả mã
    - **Chưa sử dụng**: Chỉ hiển thị mã chưa sử dụng
    - **Đã sử dụng**: Chỉ hiển thị mã đã sử dụng

## 6. Quản lý mã hiện có

### Xem thông tin chi tiết:

- Click vào dòng mã để xem thông tin chi tiết
- Với mã đã sử dụng, có thể xem thông tin user đã sử dụng

### Xóa mã:

- Click biểu tượng **thùng rác** ở cột ACTION
- **Lưu ý**: Chỉ có thể xóa mã có trạng thái "Chưa sử dụng"
- Mã đã sử dụng không thể xóa để đảm bảo tính toàn vẹn dữ liệu

### Sửa mã:

- Click biểu tượng **chỉnh sửa** ở cột ACTION
- Có thể sửa thông tin ghi chú
- **Lưu ý**: Không thể sửa mã code và đối tác sau khi đã tạo

## 7. Quản lý mã cho sự kiện

### Thêm mã cho sự kiện không dành cho nhân viên:

- Vào phần quản lý sự kiện
- Tại form tạo/sửa sự kiện, ô **"Codes"** luôn hiển thị
- Nhập các mã cách nhau bởi dấu phẩy hoặc xuống dòng
- Lưu sự kiện

### Lưu ý quan trọng:

- Mã sự kiện khác với mã nhân viên
- Mã sự kiện có thể sử dụng cho cả sự kiện dành cho nhân viên và không dành cho nhân viên
- Không có giới hạn số lần sử dụng mã sự kiện

##