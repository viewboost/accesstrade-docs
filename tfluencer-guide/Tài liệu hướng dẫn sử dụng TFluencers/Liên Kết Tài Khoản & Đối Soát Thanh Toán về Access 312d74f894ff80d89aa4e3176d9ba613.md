# Liên Kết Tài Khoản & Đối Soát Thanh Toán về AccessTrade

## **🎯 Tổng Quan Hệ Thống**

### **Mục Đích Chính**

Hệ thống cung cấp 2 tính năng chính:

### **1️⃣ Liên Kết Tài Khoản (Account Linking)**

- Cho phép người dùng TFluencers  liên kết tài khoản với hệ thống **AccessTrade (AT Core)**
- Tự động tạo mới hoặc ghép nối tài khoản hiện có
- Xử lý các trường hợp cập nhật thông tin (đặc biệt là số điện thoại)

### **2️⃣ Đối Soát & Thanh Toán (Payment Reconciliation)**

- Đẩy dữ liệu hoa hồng chiến dịch từ TFluencers → AT Core
- Kiểm tra trạng thái thanh toán
- Quản lý thông tin người dùng (EKYC, MST, tài khoản ngân hàng)

### **Các Bên Liên Quan**

```
Scalef (Partner)
    ↓ (API Request)
Publisher BE (PUB) - Gateway
    ↓ (Forward Request)
MP Core (AT) - Xử lý Logic
    ↓ (Database)
User Profile & Payment System
```

---

# Các bước thực hiện ekyc (cho user)

## 1) 📝 Bước “Thông tin”: Xác nhận thông tin & ký hợp đồng

### 1.1 Kiểm tra thông tin hiển thị

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image.png)

Tại màn “Xác nhận thông tin”, bạn kiểm tra 3 nhóm:

- **Thông tin định danh**: Họ và tên
- **Thông tin thanh toán**: Ngân hàng, số tài khoản (nhận thanh toán).
- **Thông tin cơ bản**: Địa chỉ, số điện thoại, email.

### 1.2 Xác nhận và ký

- Tích chọn cam kết (nếu có), ví dụ: “Thông tin của bạn được hoàn toàn bảo mật…”.
- Bấm Tiếp tục.

**Kết quả mong đợi**: Hệ thống chuyển sang bước tiếp theo trên thanh tiến trình.

## 2) 🔗 Bước “Liên kết tài khoản”: Liên kết AccessTrade

### 2.1 Thực hiện liên kết

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image%201.png)

- Vào bước **Liên kết tài khoản**.
- Bấm **Liên kết tài khoản AccessTrade**.
- Hệ thống sẽ gọi lên hệ thống **AccessTrade** để thực hiện liên kết.

### 2.2 Nguyên tắc liên kết (bắt buộc)

Việc liên kết sẽ dùng **email + số điện thoại đã được verify**, với điều kiện:

- Email và số điện thoại thuộc **chính bạn** (cùng 1 người).
- Email/số điện thoại này **chưa từng được người khác sử dụng** để liên kết trước đó.

### 2.3 Hoàn tất liên kết

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image%202.png)

- Thực hiện theo hướng dẫn trên trang AccessTrade (đăng nhập/xác nhận liên kết nếu có).
- Sau khi liên kết thành công, bạn quay lại trang “Thỏa thuận sử dụng”.
- Bước **Liên kết tài khoản** sẽ hiển thị hoàn tất và bạn tiếp tục sang **Xác thực danh tính**.

## 3) 🪪 Bước “Xác thực danh tính”: Thực hiện eKYC

### 3.1 Mở bước eKYC

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image%203.png)

- Vào bước **Xác thực danh tính**.
- Màn hình hiển thị khu vực eKYC dạng **“Nhúng từ FPT”**.

Nếu khu vực “Nhúng từ FPT” chưa hiện nội dung:

- Chờ **5–10 giây** để tải.
- Nếu vẫn trống, hãy **refresh** hoặc đổi **trình duyệt/mạng**.

### 3.2 Thực hiện eKYC

Làm theo hướng dẫn trên widget eKYC (thường gồm):

- Chụp ảnh giấy tờ (CCCD/CMND/Hộ chiếu).
- Xác thực khuôn mặt (selfie/liveness).

Lưu ý để tránh bị từ chối:

- Ảnh giấy tờ rõ, đủ 4 góc, không lóa, không che số.
- Mặt đủ sáng, không che mặt, giữ mặt trong khung theo hướng dẫn.

### 3.3 Trường hợp eKYC thất bại

- Bấm **Thử lại** và thực hiện lại theo hướng dẫn trên màn hình.

## 4) ✅ Bước “Xác nhận”

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image%204.png)

- Kiểm tra lại các thông tin hiển thị (nếu có).
- Bấm tiếp tục để gửi hồ sơ/hợp đồng đi duyệt.
    
    ## 5) 🎉 Bước “Hoàn thành”
    
- Khi đến bước **Hoàn thành**, bạn đã hoàn tất quy trình và hệ thống bắt đầu xử lý duyệt.
- Bạn có thể xem trạng thái tại **Danh sách hợp đồng điện tử**.

## 🗂️ Theo dõi trạng thái tại “Danh sách hợp đồng điện tử”

![image.png](Li%C3%AAn%20K%E1%BA%BFt%20T%C3%A0i%20Kho%E1%BA%A3n%20&%20%C4%90%E1%BB%91i%20So%C3%A1t%20Thanh%20To%C3%A1n%20v%E1%BB%81%20Access/image%205.png)

Các trạng thái có thể hiển thị:

- **Chờ duyệt**: Hồ sơ/hợp đồng đã gửi, đang chờ duyệt.
- Đang xử lý: Hệ thống đang kiểm tra/xác minh/đồng bộ.
- **Đã duyệt**: Hồ sơ/hợp đồng đã được chấp nhận.
- Huỷ: Hồ sơ/hợp đồng không được chấp nhận

## ⚠️ Lỗi thường gặp & cách xử lý nhanh

### Bấm liên kết AccessTrade nhưng không mở trang

- Dùng Chrome.
    - Tắt chặn popup.
    - Tải lại trang.
    - Đổi mạng (WiFi/4G).
    
    ### Báo email/số điện thoại đã được sử dụng
    
    - Kiểm tra lại email/SĐT đang dùng có đúng của bạn không.
    - Nếu vẫn lỗi, liên hệ hỗ trợ và cung cấp email/SĐT để kiểm tra trùng liên kết.
    
    ### “Nhúng từ FPT” trống
    
    - Chờ tải, refresh, đổi trình duyệt/mạng.
    
    ### Không bật được camera
    
    - Cấp quyền camera cho trình duyệt.
    - Đóng app khác đang dùng camera.

---

# Luồng thanh toán tập trung về AT

## 🧭 Mục tiêu

Đảm bảo lệnh rút tiền (RT) được **xử lý đúng trạng thái** và **chỉ đẩy thông tin sang hệ thống AT** khi admin thực hiện bước **Chuyển tiền**.

## ✅ Luồng thao tác chuẩn (Admin TF)

## 1) Tạo lệnh rút tiền (RT)

- Admin TF thực hiện **tạo lệnh rút tiền** trên hệ thống TF.
- Lệnh RT được tạo ở trạng thái ban đầu theo quy trình của TF.

## 2) Lấy danh sách & xử lý lệnh

- Admin TF nhấn **“Lấy Danh sách”**.
- Hệ thống cập nhật **trạng thái lệnh RT → “Đã xử lý”**.

**Lưu ý quan trọng:**

- Ở bước này, **thông tin RT CHƯA được đẩy qua hệ thống AT**.
- Nghĩa là dashboard phía AT **chưa nhận/hiển thị dữ liệu** của lệnh RT tại thời điểm này.

## 3) Chuyển tiền (đẩy dữ liệu sang AT)

- Admin TF nhấn **“Chuyển tiền”**.
- Hệ thống cập nhật **trạng thái withdraw → “transfering”**.
- Tại thời điểm trạng thái chuyển sang **transfering**, hệ thống mới **đẩy thông tin lệnh sang dashboard bên AT**.

## 🔎 Tóm tắt trạng thái & thời điểm đồng bộ AT

| Bước | Thao tác | Trạng thái | Dữ liệu đẩy sang AT |
| --- | --- | --- | --- |
| 1 | Tạo lệnh | (trạng thái tạo) | Chưa |
| 2 | Lấy Danh sách | RT → Đã xử lý | Chưa |
| 3 | Chuyển tiền | withdraw → transfering | Có (đẩy sang AT) |