# Thưởng thêm - Event bonus

# **HDSD - Quản Lý Thưởng Sự Kiện (Event Bonus)**

## **📋 Mục Lục**

1. [Tổng Quan](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#t%E1%BB%95ng-quan)
2. [Các Tính Năng Chính](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#c%C3%A1c-t%C3%ADnh-n%C4%83ng-ch%C3%ADnh)
3. [Hướng Dẫn Sử Dụng](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-s%E1%BB%AD-d%E1%BB%A5ng)
4. [Quy Trình Trạng Thái](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#quy-tr%C3%ACnh-tr%E1%BA%A1ng-th%C3%A1i)
5. [Hướng Dẫn Nhập Dữ Liệu Excel](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-nh%E1%BA%ADp-d%E1%BB%AF-li%E1%BB%87u-excel)
6. [API Endpoints](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#api-endpoints)
7. [Cấu Trúc Dữ Liệu](https://file+.vscode-resource.vscode-cdn.net/Users/thanhtrung/Desktop/workspace/HDSD_EVENT_BONUS.md#c%E1%BA%A5u-tr%C3%BAc-d%E1%BB%AF-li%E1%BB%87u)

---

## **Tổng Quan**

### **Event Bonus là gì?**

**Event Bonus** (Thưởng Sự Kiện) là một module quản lý hệ thống cho phép cấp phát thưởng cho người dùng dựa trên các sự kiện cụ thể. Mỗi thưởng được liên kết với:

- **Một sự kiện (Event)** - xác định loại thưởng
- **Một người dùng (User)** - người nhận thưởng
- **Một đối tác (Partner)** - tổ chức cấp thưởng
- **Một số tiền (Amount)** - giá trị thưởng
- **Một ngày hết hạn (ToAt)** - thời hạn sử dụng thưởng

### **Vị Trí trong Hệ Thống**

- **Frontend Admin Panel**: `/event-bonus`
- **Backend Service**: `viewboost/pkg/admin/service/event_bonus.go`
- **Database**: Collection `event_bonus` trong MongoDB

---

## **Các Tính Năng Chính**

### **1. Xem Danh Sách Thưởng 📊**

- Hiển thị danh sách tất cả các thưởng sự kiện
- Phân trang (20 items/trang mặc định)
- Sắp xếp theo ngày tạo (mới nhất trước)

**Bộ Lọc Sẵn Có:**

- `status` - Trạng thái thưởng (pending, approved, rejected, completed)
- `event` - Lọc theo Event ID
- `user` - Lọc theo User ID
- `partner` - Lọc theo Partner ID
- `reconciliation` - Lọc theo Reconciliation ID
- `createdBy` - Lọc theo Staff tạo
- `fromAt` - Lọc từ ngày (ISO format)
- `toAt` - Lọc đến ngày (ISO format)
- `keyword` - Tìm kiếm theo ghi chú

### **2. Tạo Thưởng Mới ➕**

Cấp phát thưởng mới cho người dùng.

**Thông tin cần nhập:**

- **Event** (bắt buộc) - Chọn sự kiện liên quan
- **User** (bắt buộc) - Chọn người nhận thưởng
- **Partner** (bắt buộc) - Tổ chức cấp thưởng
- **Amount** (bắt buộc) - Số tiền thưởng (số thực)
- **ToAt** (bắt buộc) - Ngày hết hạn (định dạng ISO: YYYY-MM-DD)
- **Note** (tùy chọn) - Ghi chú về thưởng

**Quyền:**

- Staff thường: Chỉ được tạo thưởng cho Partner của mình
- Root staff: Có thể tạo cho bất kỳ Partner nào

**Trạng thái mặc định:** `pending` (chờ duyệt)

### **3. Chỉnh Sửa Thưởng ✏️**

Cập nhật thông tin thưởng (chỉ khi chưa hoàn thành).

**Có thể thay đổi:**

- `Amount` - Số tiền thưởng
- `ToAt` - Ngày hết hạn
- `Note` - Ghi chú

**Không được thay đổi:**

- Event, User, Partner (đã cố định)
- Trạng thái `completed` - không thể chỉnh sửa

### **4. Quản Lý Trạng Thái 🔄**

Duyệt hoặc từ chối thưởng, theo dõi quá trình xử lý.

**Chuyển đổi Trạng Thái:**

```
pending ──────────→ approved ──────────→ completed
   ↓                    ↓
   └────────→ rejected ←─┘
```

**Chi tiết từng trạng thái:**

| Trạng Thái | Mô Tả | Thao Tác Có Thể Làm |
| --- | --- | --- |
| **Pending** | Chờ duyệt | Duyệt → Approved, Từ chối → Rejected, Chỉnh sửa |
| **Approved** | Đã duyệt | Từ chối → Rejected, Xem chi tiết |
| **Rejected** | Đã từ chối | Chỉ xem chi tiết, không thay đổi được |
| **Completed** | Đã hoàn thành | Chỉ xem chi tiết, không thay đổi được |

### **5. Nhập Dữ Liệu từ Excel 📥**

Nhập số lượng lớn thưởng từ file Excel một lần.

**Định dạng File:**

- Format: `.xlsx` (Excel 2007+)
- Sheet: Có thể nhiều sheet
- Cột bắt buộc (6 cột):
    1. **Cột 1** - Ignored (thường là STT)
    2. **Cột 2** - Event ID
    3. **Cột 3** - User ID
    4. **Cột 4** - Amount (số thực)
    5. **Cột 5** - ExpiredAt (DD/MM/YYYY HH:MM:SS)
    6. **Cột 6** - Note (ghi chú)

**Ví dụ:**

```
STT | Event ID | User ID | Amount | ExpiredAt | Note
1   | 507... | 608... | 100000 | 31/12/2024 23:59:59 | Thưởng tham gia
2   | 507... | 609... | 150000 | 31/12/2024 23:59:59 | Thưởng quán quân
```

**Quy Trình:**

1. Chuẩn bị file Excel theo định dạng
2. Nhấn nút "Nhập từ Excel" trên trang Event Bonus
3. Chọn file từ máy
4. Hệ thống sẽ xác thực từng dòng
5. Nếu có lỗi, hiển thị dòng lỗi và lý do
6. Chỉ các dòng hợp lệ mới được import

**Kiểm Tra Dữ Liệu:**

- Kiểm tra Event có tồn tại
- Kiểm tra User có tồn tại
- Kiểm tra Amount là số hợp lệ
- Kiểm tra ExpiredAt có format đúng (DD/MM/YYYY HH:MM:SS)
- Kiểm tra quyền Partner

---

## **Hướng Dẫn Sử Dụng**

### **Bước 1: Truy Cập Trang Quản Lý Thưởng**

1. Đăng nhập vào Admin Panel
2. Truy cập `/event-bonus` hoặc chọn menu "Event Bonus"
3. Hiển thị danh sách các thưởng hiện có

### **Bước 2: Xem Danh Sách và Lọc**

```
Giao diện:
┌─────────────────────────────────────────────────────┐
│ Filter                                   Create | Import │
│ [Event] [User] [Status] [Partner] [Date Range]      │
├─────────────────────────────────────────────────────┤
│ Bảng Dữ Liệu                                         │
│ ID | Event | User | Amount | Status | Actions      │
│ ...                                                  │
└─────────────────────────────────────────────────────┘
```

**Cách sử dụng Filter:**

- Chọn Filter → Nhập giá trị → Tìm kiếm tự động
- Hỗ trợ search keyword trong ghi chú
- Có thể kết hợp nhiều bộ lọc

### **Bước 3: Tạo Thưởng Mới**

1. Nhấn nút **"Tạo"** (+ icon)
2. Điền form:
    
    ```
    Event:    [Chọn Event]        (bắt buộc)
    User:     [Chọn User]         (bắt buộc)
    Partner:  [Chọn Partner]      (bắt buộc)
    Amount:   [Nhập số tiền]      (bắt buộc)
    ToAt:     [Chọn ngày hết hạn](bắt buộc)
    Note:     [Nhập ghi chú]      (tùy chọn)
    ```
    
3. Nhấn **"Lưu"**
4. Thưởng sẽ được tạo với trạng thái `pending`

### **Bước 4: Chỉnh Sửa Thưởng**

1. Trên bảng dữ liệu, tìm dòng cần sửa
2. Nhấn icon **Sửa** (pencil icon)
3. Cập nhật các trường:
    - Amount
    - ToAt
    - Note
4. Nhấn **"Cập nhật"**

**⚠️ Lưu ý:**

- Chỉ có thể sửa thưởng với trạng thái `pending` hoặc `approved`
- Không thể sửa `Event`, `User`, `Partner`

### **Bước 5: Duyệt Thưởng**

1. Chọn thưởng cần duyệt (trạng thái `pending`)
2. Nhấn nút **"Duyệt"**
3. Xác nhận thao tác
4. Trạng thái thay đổi thành `approved`

### **Bước 6: Từ Chối Thưởng**

1. Chọn thưởng cần từ chối
2. Nhấn nút **"Từ chối"** (reject)
3. Nhập **Lý do từ chối** (bắt buộc)
4. Nhấn **"Xác nhận"**
5. Trạng thái thay đổi thành `rejected`

### **Bước 7: Xem Chi Tiết**

1. Nhấn vào dòng thưởng hoặc icon **Chi tiết**
2. Hiển thị tất cả thông tin:
    - ID thưởng
    - Thông tin Event
    - Thông tin User
    - Thông tin Partner
    - Số tiền
    - Ngày hết hạn
    - Trạng thái & lý do
    - Ghi chú
    - Người tạo & ngày tạo
    - Ngày cập nhật

---

## **Quy Trình Trạng Thái**

### **Sơ Đồ Trạng Thái**

```
                    ┌─────────────────────────┐
                    │    Tạo Thưởng Mới       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │    PENDING    │ ◄─────────────────┐
                         │  (Chờ duyệt)  │                  │
                         └───────┬───────┘                  │
                                 │                          │
                    ┌────────────┴────────────┐              │
                    │                         │              │
                    ▼                         ▼              │
          ┌─────────────────┐       ┌──────────────┐        │
          │   APPROVED      │       │   REJECTED   │        │
          │  (Đã duyệt)     │       │ (Đã từ chối) │        │
          └────────┬────────┘       └──────────────┘        │
                   │                       │                │
                   │ (Hoàn thành)          │ (Chỉ xem)     │
                   ▼                       │                │
          ┌─────────────────┐              │                │
          │   COMPLETED     │              │                │
          │ (Đã hoàn thành) │              │                │
          └─────────────────┘              │                │
                                           │                │
                                           └────────────────┘
                                        (Quay lại trang danh sách)
```

### **Mô Tả Chi Tiết Mỗi Trạng Thái**

**1. PENDING (Chờ duyệt)**

- Thưởng vừa được tạo hoặc được tạo lại
- Có thể chỉnh sửa
- Chờ người quản lý duyệt

**2. APPROVED (Đã duyệt)**

- Người quản lý đã duyệt thưởng
- Vẫn có thể từ chối nếu chưa vào đối soát
- Nếu đã vào đối soát, không thể thay đổi

**3. REJECTED (Đã từ chối)**

- Thưởng bị từ chối với lý do cụ thể
- Không thể phục hồi
- Chỉ có thể xem chi tiết

**4. COMPLETED (Đã hoàn thành)**

- Thưởng đã được xử lý hoàn toàn
- Không thể thay đổi
- Chỉ có thể xem chi tiết

---

## **Hướng Dẫn Nhập Dữ Liệu Excel**

### **Chuẩn Bị File Excel**

**Bước 1: Tạo File Excel**

```
Tạo file `.xlsx` mới với các cột:

Cột 1: STT (bỏ qua)
Cột 2: Event ID
Cột 3: User ID
Cột 4: Amount
Cột 5: ExpiredAt
Cột 6: Note
```

**Bước 2: Nhập Dữ Liệu**

```
| STT | Event ID      | User ID       | Amount  | ExpiredAt          | Note                |
|-----|---------------|---------------|---------|--------------------|--------------------|
| 1   | 507abc123     | 608def456     | 100000  | 31/12/2024 23:59:59| Thưởng tham gia    |
| 2   | 507abc123     | 609xyz789     | 150000  | 31/12/2024 23:59:59| Thưởng quán quân   |
| 3   | 507abc123     | 610pqr012     | 50000   | 31/12/2024 23:59:59| Thưởng khuyến khích|
```

**Bước 3: Kiểm Tra Dữ Liệu**

- ✅ Đảm bảo Event ID tồn tại trong hệ thống
- ✅ Đảm bảo User ID tồn tại trong hệ thống
- ✅ Amount là số thực (có thể có dấu phẩy)
- ✅ ExpiredAt theo format: `DD/MM/YYYY HH:MM:SS` (giờ theo múi giờ +7)
- ✅ Note không quá 255 ký tự

### **Quá Trình Import**

**Bước 1: Mở Trang Event Bonus**

```
Admin Panel → Event Bonus (/event-bonus)
```

**Bước 2: Nhấn "Nhập từ Excel"**

```
┌──────────────────────────────────────┐
│     Tạo    │    Nhập từ Excel        │
└──────────────────────────────────────┘
```

**Bước 3: Chọn File**

```
┌─────────────────────────────────────┐
│ Hộp thoại Nhập từ Excel              │
│                                      │
│ [Chọn file]  [file.xlsx]            │
│                                      │
│           [Nhập]  [Hủy]             │
└─────────────────────────────────────┘
```

**Bước 4: Hệ Thống Xử Lý**

- Mở file Excel
- Đọc tất cả các sheet
- Kiểm tra từng dòng dữ liệu
- Tạo thưởng cho các dòng hợp lệ
- Ghi lại các dòng lỗi

**Bước 5: Xem Kết Quả**

```
Nếu thành công:
✅ "Import thành công: 3/3 dòng"

Nếu có lỗi:
❌ "Import thất bại: Sheet 1, Row 5: Event không tồn tại"

Kết quả:
✅ 2 dòng thành công
❌ 1 dòng lỗi
```

### **Xử Lý Lỗi Import**

| Lỗi | Nguyên Nhân | Cách Khắc Phục |
| --- | --- | --- |
| "Không đủ cột dữ liệu" | File có ít hơn 6 cột | Thêm cột còn thiếu |
| "Event không tồn tại" | Event ID sai/không có | Kiểm tra Event ID |
| "User không tồn tại" | User ID sai/không có | Kiểm tra User ID |
| "Amount không hợp lệ" | Amount không phải số | Sửa thành số |
| "ExpiredAt không hợp lệ" | Format ngày sai | Sửa sang DD/MM/YYYY HH:MM:SS |
| "Không có quyền với event" | Không phải Partner của Event | Chỉ staff root hoặc staff đó partner mới được import |

### **Lưu Ý Khi Import**

- 📌 **Timezone:** Các thời gian được xem là múi giờ Việt Nam (+7)
- 📌 **Từng dòng được kiểm tra:** Một dòng lỗi không ảnh hưởng đến các dòng khác
- 📌 **Dữ liệu không bị xóa:** Import là thêm mới, không xóa dữ liệu cũ
- 📌 **Trạng thái mặc định:** Tất cả import với trạng thái `pending`
- 📌 **Quyền:** Phải có quyền với Partner tương ứng

---

### **Quyền Cấp Thưởng**

| Thao Tác | Root Staff | Partner Staff | Ghi Chú |
| --- | --- | --- | --- |
| Xem danh sách | ✅ Tất cả | ✅ Partner mình | Chỉ thấy thưởng của partner mình |
| Tạo thưởng | ✅ Bất kỳ | ✅ Partner mình | Phải là partner của event |
| Chỉnh sửa | ✅ Bất kỳ | ✅ Partner mình | Chỉ sửa thưởng của partner mình |
| Duyệt/Từ chối | ✅ Bất kỳ | ✅ Partner mình | Chỉ duyệt/từ chối của partner mình |
| Import Excel | ✅ Bất kỳ | ✅ Partner mình | Kiểm tra quyền event |

### **Hạn Chế & Quy Tắc**

1. **Không thể chỉnh sửa Event, User, Partner** - Đã cố định khi tạo
2. **Không thể chỉnh sửa thưởng Completed** - Đã xử lý xong
3. **Không thể từ chối thưởng trong Reconciliation** - Đang đối soát
4. **Trạng thái Rejected là tối cuối** - Không thể phục hồi
5. **Dữ liệu không bị xóa** - Chỉ lưu trữ trong Database

---

## **Thường Gặp & Giải Pháp**

### **❓ Làm sao để xóa một thưởng sai?**

**Giải pháp:** Không thể xóa. Hãy từ chối thưởng đó với lý do "Tạo sai" hoặc liên hệ admin để xóa trực tiếp trong database.

### **❓ Tại sao không thể thay đổi Event của thưởng?**

**Giải pháp:** Event là cơ sở để xác định Partner và quyền hạn. Nếu cần, hãy từ chối thưởng cũ và tạo thưởng mới với Event đúng.

### **❓ Import Excel gặp lỗi dữ liệu, làm sao?**

**Giải pháp:**

1. Xem lỗi cụ thể: "Sheet X, Row Y: Lỗi gì"
2. Sửa file Excel theo gợi ý
3. Nhập lại

### **❓ Có thể import file có nhiều sheet không?**

**Giải pháp:** Có, hệ thống sẽ đọc tất cả các sheet và import dữ liệu từ tất cả.

### **❓ Thưởng bị từ chối, có thể phục hồi không?**

**Giải pháp:** Không thể phục hồi. Phải tạo thưởng mới.

---

## **Liên Hệ & Hỗ Trợ**

Nếu gặp vấn đề hoặc cần hỗ trợ:

- 📧 Email: [support@techcombank.com](mailto:support@techcombank.com)
- 📞 Hotline: [Số điện thoại]
- 💬 Slack: #event-bonus-support

---

**Cập nhật lần cuối:** 2024 **Phiên bản:** 1.0