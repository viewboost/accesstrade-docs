# Hướng Dẫn Sử Dụng Tính Năng Blacklist và Auto-Approved Rules

# 

## 📋 Giới Thiệu

Tính năng này giúp quản lý nội dung của các influencer thông qua hai cơ chế chính:

- **Blacklist Keywords**: Chặn các từ khóa cấm trong nội dung
- **Auto-Approved Rules**: Tự động phê duyệt nội dung khi đáp ứng tiêu chí

---

## 1️⃣ Quản Lý Blacklist Keywords (Từ Khóa Cấm)

### 1.1 Truy Cập Chức Năng

- Đăng nhập vào Admin Panel
- Chuyển đến mục **Blacklist Keywords** (/blacklist-keyword)

### 1.2 Thêm Từ Khóa Cấm Mới

**Cách 1: Thêm thủ công**

1. Nhấn nút **"Create New"** hoặc **"Thêm từ khóa"**
2. Nhập từ khóa cần cấm
3. Nhấn **"Lưu"**

**Cách 2: Import từ Excel**

1. Nhấn nút **"Import"**
2. Tải file Excel chứa danh sách từ khóa
3. Hệ thống sẽ tự động:
    - Phát hiện trùng lặp
    - Loại bỏ các ký tự đặc biệt
    - Chuẩn hóa dữ liệu
4. Xác nhận và hoàn tất

### 1.3 Quản Lý Từ Khóa Đã Thêm

- **Tìm kiếm**: Sử dụng ô tìm kiếm để tìm từ khóa nhanh chóng
- **Chỉnh sửa**: Nhấn vào từ khóa để cập nhật mức độ phạt
- **Bật/Tắt**: Chuyển trạng thái để kích hoạt hoặc vô hiệu hóa từ khóa

### 1.4 Cách Hoạt Động

Khi nội dung chứa từ khóa cấm:

- ✅ Hệ thống tự động phát hiện (kể cả từ đồng nghĩa, viết tắt)
- 📊 Trừ điểm tương ứng khỏi bài viết
    
    ![image.png](H%C6%B0%E1%BB%9Bng%20D%E1%BA%ABn%20S%E1%BB%AD%20D%E1%BB%A5ng%20T%C3%ADnh%20N%C4%83ng%20Blacklist%20v%C3%A0%20Auto-Appr/image.png)
    
- 🏷️ Gắn tag `content_blacklist` cho nội dung
- 📋 Đưa vào hàng chờ review thủ công

---

## 2️⃣ Cấu Hình Auto-Approved Rules (Quy Tắc Tự Động Phê Duyệt)

### 2.1 Truy Cập Chức Năng

- Vào **Chi tiết sự kiện** (Event Detail)
- Tìm phần **"Auto-Approve Rules"**

### 2.2 Tạo Quy Tắc Tự Động Phê Duyệt

1. **Nhấn "Thêm quy tắc"**
2. **Cấu hình các điều kiện** (tất cả phải đáp ứng):
    
    
    | Điều Kiện | Ý Nghĩa |
    | --- | --- |
    | **Điểm tối thiểu** | Bài viết phải đạt bao nhiêu điểm trở lên |
    | **Liên quan đến sự kiện** | Nội dung phải liên quan đến chủ đề sự kiện |
    | **Không chứa từ cấm** | Không được xuất hiện từ khóa blacklist |
    | **Lượt tương tác tối thiểu** | Số like, comment, share phải từ bao nhiêu |
    | **Lượt xem tối thiểu** | Bài viết phải được xem tối thiểu bao nhiêu lần |
3. **Áp dụng cho nền tảng**: Chọn nền tảng muốn áp dụng quy tắc:
    - Instagram
    - TikTok
    - Facebook
    - YouTube
    - Nền tảng khác
4. **Nhấn "Lưu quy tắc"**

### 2.3 Ví Dụ Cấu Hình

**Ví dụ 1: Chiến dịch Marketing cơ bản**

`✓ Điểm tối thiểu: 70
✓ Liên quan sự kiện: Có
✓ Không chứa từ cấm: Bắt buộc
✓ Lượt tương tác: ≥ 100
✓ Nền tảng: Instagram, TikTok`

**Ví dụ 2: Chiến dịch Premium (yêu cầu cao)**

`✓ Điểm tối thiểu: 85
✓ Liên quan sự kiện: Có
✓ Không chứa từ cấm: Bắt buộc
✓ Lượt tương tác: ≥ 500
✓ Lượt xem: ≥ 5000
✓ Nền tảng: Tất cả`

### 2.4 Cách Hoạt Động

Khi influencer submit nội dung:

1. 🔍 Hệ thống kiểm tra với tất cả quy tắc Auto-Approve
2. ✅ Nếu nội dung đáp ứng **TẤT CẢ** điều kiện trong 1 quy tắc → **Tự động phê duyệt**
3. ❌ Nếu không đáp ứng → **Chuyển để review thủ công**

---

## 3️⃣ Quy Tắc Logic

### Auto-Approve Rules

- **Trong 1 quy tắc**: `AND` (phải đáp ứng TẤT CẢ điều kiện)
- **Giữa các quy tắc**: `OR` (chỉ cần đáp ứng 1 quy tắc)

**Ví dụ**: Nếu có 2 quy tắc:

- Quy tắc 1: Điểm ≥ 80 + Lượt tương tác ≥ 500
- Quy tắc 2: Điểm ≥ 70 + Lượt xem ≥ 10000

→ Nội dung sẽ tự động phê duyệt nếu đáp ứng **Quy tắc 1 HOẶC Quy tắc 2**

---

## 4️⃣ Theo Dõi & Báo Cáo

### Xem Danh Sách Nội Dung

- **Tự động phê duyệt**: Danh sách nội dung được phê duyệt tự động
- **Chứa từ cấm**: Danh sách nội dung vi phạm blacklist
- **Đang review**: Nội dung chờ phê duyệt thủ công

### Thống Kê

- Số nội dung tự động phê duyệt
- Số nội dung bị từ chối do từ cấm
- Tỷ lệ phê duyệt tự động vs thủ công

---

## 5️⃣ Mẹo Sử Dụng

✨ **Tối ưu hóa quy tắc**:

- Bắt đầu với điều kiện khắt khe, sau đó nới lỏng nếu quá nhiều nội dung cần review
- Kiểm tra định kỳ hiệu quả của các quy tắc
- Cập nhật blacklist dựa trên nội dung bị từ chối nhiều lần

⚠️ **Lưu ý**:

- Từ khóa sẽ được chuẩn hóa (loại dấu, chuyển thường/hoa)
- Kiểm tra engagement/views được cập nhật tự động theo lịch định kỳ
- Quy tắc mới sẽ áp dụng cho nội dung submit sau đó

---

## 6️⃣ Hỗ Trợ

Nếu gặp vấn đề:

- Kiểm tra lại cấu hình quy tắc
- Xem log hệ thống để biết chi tiết lý do từ chối
- Liên hệ Admin để cập nhật danh sách từ khóa cấm