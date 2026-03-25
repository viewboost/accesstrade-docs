# Import content

# **1. Tạo Campaign Không Tính Thưởng**

### **1.1 Truy cập**

- Vào menu Sự kiện **→ Tạo Sự kiện mới**.

### **1.2 Thiết lập thông tin chung**

- Nhập đầy đủ các thông tin cơ bản của campaign:
    - Tên campaign, thời gian chạy, mô tả, hình ảnh,…
    - **Chọn loại: Sự kiện không tính thưởng**

### **1.3  Đối với campaign này:**

- **Không tính thưởng cho video**
- **Không cần tạo nhiệm vụ (task)** cho campaign.

# **2. User Submit Video Cho Campaign Không Tính Thưởng**

### **2.1 Quyền thực hiện**

- Người dùng (creator) submit như campaign bình thường.

### **2.2 Lưu ý hệ thống**

- Không kiểm tra hashtag.
- Không kiểm tra nhiệm vụ.
- Không gắn reward rule.
- Chỉ lưu content đơn thuần.

**Admin không cần thao tác gì trong bước này.**

# **3. Admin Import Content (Thêm Video Cho Creator)**

Chức năng này giúp Admin tự thêm video vào hệ thống mà **không phụ thuộc User submit**.

### **3.1 Truy cập**

- Vào menu **Content → Import Content / Thêm Content**.

![image.png](Import%20content/image.png)

### **3.2 Các bước thao tác**

![image.png](Import%20content/image%201.png)

### **Bước 1: Chọn Creator**

- Tìm & chọn creator có sẵn.
- Nếu creator chưa tồn tại → bấm **Tạo mới bên menu Creator**

### **Bước 2: Chọn Social Profile**

- Chọn nền tảng (TikTok, Facebook, YouTube…).
- Nếu chưa có social profile:
    - Nhấn **Tạo Social Profile mới (menu Hồ sơ)**

### **Bước 3: Nhập danh sách link video**

- Dán danh sách video theo dạng **array** (mỗi link 1 dòng).

### **Bước 4: Xử lý**

- Nhấn **Xác nhận** để import.

### **3.4 Kết quả hiển thị sau import**

- Số lượng link hợp lệ.
- Số lượng link lỗi.
- Danh sách video đã tạo.

# **4. Tạo Creator & Social Profile (Dành cho Admin)**

### **4.1 Tạo Creator**

![image.png](Import%20content/image%202.png)

- Vào **Creator → Tạo mới**.
- Điền thông tin cơ bản:
    - Tên creator
    - Email (tuỳ chọn)
    - **staffCode** – nếu creator là nhân viên Techcombank.

### **4.2 Tạo Social Profile**

![image.png](Import%20content/image%203.png)

- Khi tạo mới hoặc chỉnh sửa creator → vào tab Social.
- Nhấn **Thêm Social Profile**.
- Chọn nền tảng (TikTok/YouTube/Facebook…).
- Nhập thông tin **bắt buộc**:
    - **ID kênh (platform_user_id)**
- Lưu lại.

> Lưu ý: ID kênh không được trùng (mỗi nền tảng chỉ được 1 ID duy nhất).
> 

---

# **5. Xem Lịch Sử Import Content**

![image.png](Import%20content/image%204.png)

### **5.1 Truy cập**

- Vào menu: **Content → Lịch sử Import**.

### **5.2 Nội dung hiển thị**

- Admin thực hiện.
- Thời gian import.
- Danh sách các link đã nhập.
- Trạng thái từng link:
    - Thành công (success)
    - Lỗi (fail)
- Tổng số video được tạo mới.

### **5.3 Mục đích**

- Giúp admin theo dõi lịch sử thao tác.
- Kiểm tra lỗi import để xử lý.
- Đảm bảo tính minh bạch và truy vết.