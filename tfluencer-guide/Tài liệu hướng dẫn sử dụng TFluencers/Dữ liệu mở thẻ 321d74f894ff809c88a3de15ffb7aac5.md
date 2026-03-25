# Dữ liệu mở thẻ

# **📖 Hướng Dẫn Sử Dụng - Tính Năng Dữ Liệu Mở Thẻ**

---

## **🎯 Giới Thiệu**

Tính năng **Dữ liệu mở thẻ** cho phép bạn:

- ✅ **Xem** danh sách các thẻ được mở (Merchant/Non-Merchant)
- ✅ **Lọc** dữ liệu theo khoảng thời gian, kênh, mã TF
- ✅ **Import** dữ liệu từ file CSV
- ✅ **Xem lịch sử** import
- ✅ **Tìm kiếm** thông tin nhanh chóng

---

## **🔧 Các Thành Phần Chính**

### **1. Thanh Lọc (Filter Bar) - Ở phía trên cùng**

```
[Từ ngày: dd/mm/yyyy] [Đến ngày: dd/mm/yyyy] [Lọc theo mã TF: ____] [Kênh: ▼ Tất cả kênh]
```

### **2. Nút Chức Năng**

- 🔵 **Import CSV** - Tải dữ liệu từ file Excel
- ⏰ **Lịch sử import** - Xem các lần tải dữ liệu trước đó

### **3. Bảng Dữ Liệu (Data Table)**

```
| Ngày       | Kênh           | Mã TF | Nhân viên    |
|------------|----------------|-------|-------------|
| 31/12/2025 | Merchant       | TF54  | huongtt40   |
| 31/12/2025 | Non-Merchant   | TF43  | trangnt141  |
| 30/12/2025 | Merchant       | TF40  | anhnh66     |
```

### **4. Phân Trang (Pagination) - Ở cuối bảng**

```
◀ 1 2 3 4 5 ▶  |  Hiển thị 25 dòng/trang
```

---

## **📋 Cách Sử Dụng**

### **Bước 1: Truy cập tính năng**

1. **Đăng nhập** vào hệ thống
2. Trên menu bên trái, chọn **"Dữ liệu mở thẻ"**
3. Bạn sẽ thấy danh sách dữ liệu mở thẻ mặc định

```
Lưu ý: Lần đầu tiên, hệ thống sẽ hiển thị dữ liệu 30 ngày gần nhất
```

---

### **Bước 2: Lọc dữ liệu theo ngày**

### **Lọc theo khoảng ngày cụ thể:**

**Mục đích:** Bạn muốn xem dữ liệu từ ngày 20/12/2025 đến 31/12/2025

**Các bước:**

1. Nhấp vào ô **"Từ ngày"** (ô đầu tiên)
    
    ```
    Ô sẽ sáng lên, bạn có thể nhập hoặc chọn từ lịch
    ```
    
2. Nhập ngày: `20/12/2025` (theo định dạng ngày/tháng/năm)
    - Hoặc: Nhấp vào icon **📅** để chọn ngày từ lịch
3. Nhấp vào ô **"Đến ngày"**
4. Nhập ngày: `31/12/2025`
5. Bảng dữ liệu sẽ **tự động cập nhật** để hiển thị chỉ dữ liệu trong khoảng này

```
📌 Ví dụ:
- Muốn xem dữ liệu tháng 12/2025
  → Từ: 01/12/2025
  → Đến: 31/12/2025

- Muốn xem dữ liệu 1 tuần (01-07/12/2025)
  → Từ: 01/12/2025
  → Đến: 07/12/2025
```

### **Lọc chỉ từ ngày bắt đầu:**

- Nhập chỉ **"Từ ngày"**, để trống "Đến ngày"
- Kết quả: Hiển thị dữ liệu từ ngày đó đến ngày hiện tại

### **Xóa bộ lọc ngày:**

- Xóa text trong cả 2 ô
- Bảng sẽ quay lại dữ liệu mặc định

---

### **Bước 3: Lọc theo Kênh (Merchant/Non-Merchant)**

**Mục đích:** Bạn chỉ muốn xem dữ liệu Merchant hoặc Non-Merchant

**Các bước:**

1. Nhấp vào dropdown **"Tất cả kênh"** (cái có mũi tên ▼)
2. Chọn một trong các tùy chọn:
    
    ```
    ☐ Tất cả kênh      (hiển thị cả Merchant + Non-Merchant)
    ☐ Merchant         (chỉ hiển thị Merchant)
    ☐ Non-Merchant     (chỉ hiển thị Non-Merchant)
    ```
    
3. Bảng dữ liệu sẽ cập nhật ngay

```
📌 Ví dụ:
- Bạn chỉ quan tâm dữ liệu Merchant
  → Click dropdown → Chọn "Merchant"
  → Bảng chỉ hiển thị dòng có "Merchant" trong cột "Kênh"
```

---

### **Bước 4: Lọc theo Mã TF (Thẻ)**

**Mục đích:** Tìm dữ liệu của một thẻ cụ thể, ví dụ TF54

**Các bước:**

1. Nhấp vào ô **"Lọc theo mã TF"**
2. Nhập mã TF, ví dụ: `TF54`
3. Bảng sẽ tự động lọc và chỉ hiển thị dòng có mã TF = TF54
4. Để xóa lọc, xóa text trong ô

```
📌 Ví dụ:
- Tìm dữ liệu thẻ TF40
  → Nhập "TF40"
  → Bảng chỉ hiển thị thẻ TF40

- Nếu không tìm thấy
  → Bảng trống hoặc thông báo "Không tìm thấy"
```

---

### **Bước 5: Kết hợp nhiều bộ lọc**

**Mục đích:** Tìm dữ liệu chỉ của Merchant TF54 trong tháng 12/2025

**Các bước:**

1. Nhập **"Từ ngày"**: `01/12/2025`
2. Nhập **"Đến ngày"**: `31/12/2025`
3. Chọn **"Kênh"**: `Merchant`
4. Nhập **"Mã TF"**: `TF54`

**Kết quả:** Bảng sẽ hiển thị **chỉ** dữ liệu thỏa **tất cả 4 điều kiện trên**

```
📌 Lợi ích: Giúp bạn tìm được dữ liệu chính xác mà không cần lục từng dòng
```

---

### **Bước 6: Xem dữ liệu trên nhiều trang**

**Mục đích:** Nếu có > 100 dòng dữ liệu, chúng được chia thành nhiều trang

**Các bước:**

1. Ở cuối bảng, bạn sẽ thấy:
    
    ```
    ◀ 1  2  3  4  5  ▶
    ```
    
2. **Chuyển trang tiếp theo:**
    - Nhấp vào số `2`, `3`, v.v. → Bảng hiển thị dữ liệu trang đó
    - Hoặc nhấp vào mũi tên **▶** (trang tiếp theo)
3. **Quay lại trang trước:**
    - Nhấp vào mũi tên **◀**
4. **Thay đổi số dòng mỗi trang:**
    - Tìm dropdown **"Hiển thị 25 dòng/trang"**
    - Chọn: 10, 25, 50, hoặc 100 dòng
    
    ```
    Chọn 100 dòng: Xem được nhiều dữ liệu hơn trong 1 trang
    Chọn 10 dòng:  Trang nhanh nhưng cần chuyển trang nhiều lần
    ```
    

---

## **🚀 Các Tính Năng Chi Tiết**

### **1. Import Dữ Liệu từ File CSV (Excel)**

**Mục đích:** Bạn có file Excel danh sách thẻ mở mới, muốn đưa vào hệ thống

**Chuẩn bị file Excel:**

1. Mở Excel hoặc Google Sheets
2. Tạo bảng với **4 cột bắt buộc:**
    
    ```
    Ngày       | Kênh           | Mã TF | Nhân viên
    01/12/2025 | Merchant       | TF54  | huongtt40
    02/12/2025 | Non-Merchant   | TF40  | anhnh66
    03/12/2025 | Merchant       | TF43  | trangnt141
    ```
    
3. **Format cột "Ngày":** `dd/mm/yyyy` (ví dụ: 31/12/2025)
4. **Format cột "Kênh":** Chỉ nhập "Merchant" hoặc "Non-Merchant" (chữ hoa/thường không quan trọng)
5. **Format cột "Mã TF":** Nhập mã thẻ, ví dụ TF54, TF40
6. **Format cột "Nhân viên":** Nhập username của nhân viên

**Lưu file:**

- Lưu dưới dạng **.CSV** hoặc **.XLSX**
- Tên file có thể là: `mo_the_thang_12.csv`

**Import vào hệ thống:**

1. Trên trang Dữ liệu mở thẻ, nhấp vào nút **🔵 Import CSV** (nút xanh)
    
    ```
    Sẽ có dialog/cửa sổ yêu cầu chọn file
    ```
    
2. Nhấp vào **"Chọn file"** hoặc kéo thả file vào
3. Chọn file Excel/CSV của bạn từ máy tính
4. Nhấp **"Upload"** hoặc **"Import"**
5. **Chờ thông báo thành công:**
    
    ```
    ✅ Import thành công! 100 records được thêm.
    ```
    
6. Bảng sẽ **tự động cập nhật** với dữ liệu mới

```
📌 Mẹo:
- Nên kiểm tra kỹ dữ liệu trước khi import
- Nếu có lỗi, hệ thống sẽ báo chi tiết (ví dụ: "Hàng 5 sai định dạng ngày")
- Xem lịch sử import để biết import lần nào thành công/thất bại
```

---

### **2. Xem Lịch Sử Import**

**Mục đích:** Kiểm tra các lần tải dữ liệu trước đó

**Các bước:**

1. Nhấp vào **⏰ Lịch sử import**
2. Bạn sẽ thấy bảng:
    
    ```
    | Ngày Import | Thời gian | Status | Số records | Người import |
    |-------------|----------|--------|-----------|-------------|
    | 31/12/2025  | 14:30:45 | ✅ Thành công | 100 | bạn |
    | 30/12/2025  | 10:15:20 | ✅ Thành công | 50  | bạn |
    | 29/12/2025  | 09:45:10 | ⚠️ Có lỗi    | 40/50 | bạn |
    ```
    
3. **Nhấp vào một dòng** để xem chi tiết:
    - Số dòng import thành công
    - Số dòng thất bại
    - Lỗi chi tiết (nếu có)
    - Có thể download log lỗi

---

### **3. Tìm Kiếm và Sắp Xếp**

**Tìm kiếm nhanh trong bảng:**

- Có ô search ở trên bảng không?
- Nhập từ khóa (ví dụ: "Merchant" hoặc "TF54")
- Bảng sẽ **filter tức thì**

**Sắp xếp dữ liệu:**

- Nhấp vào **header cột** (Ngày, Kênh, Mã TF, Nhân viên)
- Dữ liệu sẽ sắp xếp tăng (A→Z) hoặc giảm (Z→A)
- Nhấp lại để đảo chiều sắp xếp

```
📌 Ví dụ:
- Nhấp "Ngày" → Sắp xếp từ cũ đến mới
- Nhấp lại "Ngày" → Sắp xếp từ mới đến cũ
- Nhấp "Mã TF" → Sắp xếp A-Z theo mã TF
```

---

## **❓ Câu Hỏi Thường Gặp**

### **Q1: Định dạng ngày là gì?**

**A:** Định dạng là `dd/mm/yyyy`

```
Đúng:  31/12/2025  (ngày 31, tháng 12, năm 2025)
Sai:   12/31/2025
Sai:   2025-12-31
```

---

### **Q2: Làm thế nào để xem tất cả dữ liệu (không lọc)?**

**A:**

- Xóa tất cả các ô lọc
- Hoặc nhấp "Reset" hoặc "Xóa bộ lọc"

---

### **Q3: File CSV phải có header (tiêu đề cột) không?**

**A:**

- **Nên có** (Ngày, Kênh, Mã TF, Nhân viên)
- Hệ thống sẽ tự bỏ qua hàng đầu tiên
- Nếu không, sẽ nhập nhầm tên cột thành dữ liệu

---

### **Q4: File CSV quá lớn sẽ sao?**

**A:**

- Nếu > 10MB, hệ thống có thể từ chối
- **Giải pháp:** Tách file thành nhiều file nhỏ hơn
- Ví dụ: Chia theo tháng, tuần hoặc theo số lượng (1000 dòng/file)

---

### **Q5: Nếu import trùng dữ liệu (import 2 lần cùng file)?**

**A:**

- Hệ thống sẽ **không** tạo duplicate
- Dữ liệu cũ sẽ được **cập nhật** hoặc **bỏ qua**
- Kiểm tra lịch sử import để biết chắc

---

### **Q6: Có thể export dữ liệu ra Excel không?**

**A:**

- Hiện tại có thể **copy** dữ liệu từ bảng
- Hoặc tìm nút **"Export CSV"** nếu có
- **Mẹo:** Select tất cả → Copy → Paste vào Excel

---

### **Q7: Làm sao để tìm dữ liệu của 1 nhân viên cụ thể?**

**A:**

- Hiện tại không có lọc theo "Nhân viên"
- **Giải pháp:**
    1. Export dữ liệu ra Excel
    2. Dùng Filter trong Excel để lọc theo nhân viên
    3. Hoặc báo cho IT team để thêm tính năng này

---

### **Q8: Tại sao bảng trống sau khi lọc?**

**A:** Có thể là:

1. Không có dữ liệu thỏa điều kiện lọc
2. Mã TF nhập sai hoặc không tồn tại
3. Khoảng ngày sai

**Cách kiểm tra:**

- Xóa bộ lọc, xem dữ liệu gốc
- Thử lọc từng điều kiện một

---

## **🔧 Xử Lý Lỗi**

### **Lỗi 1: "Format ngày sai"**

```
❌ Lỗi: Định dạng ngày không đúng
✅ Giải pháp: Nhập theo dd/mm/yyyy, ví dụ 31/12/2025
```

### **Lỗi 2: "File CSV không hợp lệ"**

```
❌ Lỗi: Upload file thất bại
✅ Giải pháp:
   - Kiểm tra file có đúng 4 cột: Ngày, Kênh, Mã TF, Nhân viên không?
   - Lưu file dưới dạng CSV hoặc XLSX
   - Kiểm tra không có ký tự đặc biệt lạ trong tên
```

### **Lỗi 3: "Không tìm thấy dữ liệu"**

```
❌ Lỗi: Bảng trống sau khi lọc
✅ Giải pháp:
   - Xóa bộ lọc, kiểm tra dữ liệu gốc
   - Thử lọc từng tiêu chí riêng lẻ
   - Kiểm tra mã TF có tồn tại không
```

### **Lỗi 4: "Server đang bận"**

```
❌ Lỗi: Thông báo "Trang đang tải..." quá lâu (> 3 giây)
✅ Giải pháp:
   - Chờ thêm vài giây
   - Refresh trang (F5)
   - Báo cho IT team nếu vẫn lỗi
```

### **Lỗi 5: "Không thể upload file (quá lớn)"**

```
❌ Lỗi: File > 10MB
✅ Giải pháp:
   - Chia file thành nhiều file nhỏ hơn
   - Import từng file một
   - Hoặc yêu cầu IT team tăng giới hạn file
```

---

## **📞 Liên Hệ Hỗ Trợ**

**Nếu bạn gặp vấn đề không giải quyết được:**

1. **Chụp ảnh màn hình** hiển thị lỗi
2. **Ghi lại:**
    - Bạn đang cố làm gì?
    - Lỗi gì?
    - Khi nào xảy ra?
3. **Liên hệ:**
    - IT Team: [support@techcombank.com.vn](mailto:support@techcombank.com.vn)
    - Hoặc gọi: 0212.356.7890 (ext. 1234)

---

## **💡 Mẹo Sử Dụng Hiệu Quả**

### **Mẹo 1: Chuẩn bị dữ liệu trước**

- Kiểm tra file CSV trước khi import
- Dùng Excel để validate định dạng
- Tránh typo trong mã TF hoặc tên nhân viên

### **Mẹo 2: Import theo từng tháng/quý**

- Thay vì import 1 file 10,000 dòng
- Chia thành 4 file theo quý → Dễ quản lý lỗi

### **Mẹo 3: Kiểm tra lịch sử import**

- Sau mỗi import, xem lịch sử
- Nếu có lỗi, tải log chi tiết để sửa

### **Mẹo 4: Dùng bộ lọc để kiểm tra**

- Lọc theo kênh → Kiểm tra tỷ lệ Merchant/Non-Merchant
- Lọc theo tháng → Kiểm tra dữ liệu theo từng giai đoạn

### **Mẹo 5: Cập nhật thường xuyên**

- Nhập dữ liệu ngay sau khi thẻ được mở
- Tránh delay → Dữ liệu luôn chính xác

---

## **📚 Tài Liệu Liên Quan**

- **Template File CSV:** [Download mẫu file](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/link_to_template)
- **Danh sách mã TF:** [Xem danh sách](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/link_to_codes)
- **Video hướng dẫn:** [Xem video](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/link_to_video)

---

**Cập nhật lần cuối:** 11/03/2026 **Phiên bản tài liệu:** 1.0