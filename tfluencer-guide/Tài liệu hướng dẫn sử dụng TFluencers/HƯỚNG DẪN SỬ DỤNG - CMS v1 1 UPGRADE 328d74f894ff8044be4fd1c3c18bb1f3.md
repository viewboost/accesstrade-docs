# HƯỚNG DẪN SỬ DỤNG - CMS v1.1 UPGRADE

## **1. Chuẩn Hóa Lý Do Từ Chối Nội Dung**

### **1.1 Tổng Quan**

Trước đây, admin nhập lý do từ chối nội dung dưới dạng text tự do, dẫn đến:

- Cùng lý do nhập khác cách: "Missing hashtag", "thiếu #", "ko có hashtag" → 4 lý do khác nhau
- Dữ liệu thống kê không chính xác
- Khó phân tích xu hướng từ chối

**Giải pháp:** Sử dụng Rejection Tags (lý do từ chối được chuẩn hóa)

### **1.2 Danh Sách Rejection Tags**

Hệ thống cung cấp 9 lý do từ chối tiêu chuẩn:

| Tag ID | Tên Tag | Mô Tả | Ví Dụ |
| --- | --- | --- | --- |
| 1 | `missing_hashtag` | Thiếu hashtag | Bài viết không có #campaign |
| 2 | `wrong_content` | Nội dung sai/không liên quan | Bài viết nói về topic khác |
| 3 | `poor_quality` | Chất lượng kém | Ảnh mờ, text lỗi chính tả |
| 4 | `policy_violation` | Vi phạm chính sách | Spam, nội dung nhạy cảm |
| 5 | `wrong_platform` | Nền tảng sai | Post lên Facebook thay vì Instagram |
| 6 | `missing_mention` | Thiếu mention/tag | Quên mention brand hoặc influencer |
| 7 | `wrong_timing` | Thời gian sai | Post trước/sau deadline campaign |
| 8 | `duplicate` | Nội dung trùng lặp | Bài viết giống bài khác |
| 9 | `other` | Lý do khác | Không thuộc các lý do trên |

### **1.3 Cách Sử Dụng - Từ Chối Nội Dung**

### **Bước 1: Truy Cập Nội Dung Cần Phê Duyệt**

```
Dashboard > Content Management > Pending Approval
hoặc
Admin Panel > Moderation Queue
```

### **Bước 2: Chọn Nội Dung Cần Từ Chối**

- Nhấp vào bài viết trong danh sách
- Click nút **"Reject"** hoặc **"Từ Chối"** (thường màu đỏ)

### **Bước 3: Điền Form Từ Chối**

Một modal/popup sẽ xuất hiện với 2 trường:

**A. Rejection Tag** (Bắt Buộc ✓)

```
┌─────────────────────────────────┐
│ Lý Do Từ Chối *                 │
│ [Dropdown ▼]                    │
│ - missing_hashtag               │
│ - wrong_content                 │
│ - poor_quality                  │
│ - policy_violation              │
│ - wrong_platform                │
│ - missing_mention               │
│ - wrong_timing                  │
│ - duplicate                     │
│ - other                         │
└─────────────────────────────────┘
```

**B. Rejection Comment** (Tùy Chọn)

```
┌────────────────────────────────────┐
│ Bình Luận Bổ Sung (Optional)       │
│ [Text Area - Nhập mô tả chi tiết]  │
│                                    │
│ (Ví dụ: "Ảnh không rõ, cần chỉnh   │
│  sửa lại. Hãy upload ảnh HD")     │
│                                    │
│ Ký tự: 0/500                       │
└────────────────────────────────────┘
```

### **Bước 4: Chọn Lý Do Từ Chối**

1. Nhấp vào dropdown "Lý Do Từ Chối"
2. Chọn lý do phù hợp nhất
3. **Lưu ý:** Nếu chọn "other", bắt buộc phải nhập Comment

### **Bước 5: (Tùy Chọn) Thêm Bình Luận Chi Tiết**

1. Click vào trường "Rejection Comment"
2. Nhập thêm thông tin chi tiết để creator hiểu rõ hơn
3. Ví dụ: "Ảnh quá mờ, cần độ nét cao hơn. Hãy dùng camera chất lượng tốt hơn"

### **Bước 6: Submit**

1. Kiểm tra lại thông tin
2. Nhấp nút **"Confirm Reject"** hoặc **"Từ Chối"**
3. Nếu có lỗi, hệ thống sẽ thông báo (ví dụ: "Vui lòng chọn lý do từ chối")

### **Bước 7: Xác Nhận Thành Công**

- Modal đóng
- Trang được làm mới
- Bài viết chuyển sang trạng thái "Rejected"
- Creator sẽ nhận được thông báo

### **1.4 Creator Xem Lý Do Từ Chối**

### **Creator App/Website**

```
My Submissions > [Bài viết bị reject]
```

**Thông tin hiển thị:**

- Status: ❌ Rejected
- Rejection Reason: "Missing Hashtag"
- Rejection Details: "Ảnh không rõ, cần chỉnh sửa lại"
- Rejected At: 19/03/2025 14:30
- Rejected By: Admin Name

### **Cách Creator Cải Thiện**

1. Đọc kỹ lý do từ chối + comment chi tiết
2. Chỉnh sửa bài viết theo yêu cầu
3. Nộp lại bài viết
4. Chờ phê duyệt

### **1.5 Xem Thống Kê Rejection Tags**

### **Điều Hướng**

```
Dashboard > Analytics > Content Rejection
hoặc
Admin Panel > Reports > Rejection Statistics
```

### **Xem Biểu Đồ**

```
┌─────────────────────────────────────────┐
│ Content Rejection Statistics (Mar 2025) │
├─────────────────────────────────────────┤
│ missing_hashtag      ████ 12            │
│ wrong_content        ██████ 18          │
│ poor_quality         ███████ 21         │
│ policy_violation     ██ 6               │
│ wrong_platform       ███ 9              │
│ missing_mention      ████ 13            │
│ wrong_timing         █ 3                │
│ duplicate            ██ 7               │
│ other                █ 2                │
└─────────────────────────────────────────┘

Total Rejections: 91
Approval Rate: 78.5%
```

### **Lợi Ích**

- Xác định vấn đề phổ biến nhất
- Hướng dẫn creator về yêu cầu
- Cải thiện quy trình phê duyệt

### **1.6 Sửa Lại Lý Do Từ Chối (Nếu Cần)**

### **Bước 1: Chọn Nội Dung Đã Reject**

```
Dashboard > All Content > [Chọn bài reject]
```

### **Bước 2: Sửa Rejection Reason**

- Click nút **"Edit Rejection"** (nếu có)
- Hoặc chọn mục "Rejection Details"

### **Bước 3: Cập Nhật**

- Thay đổi Rejection Tag nếu cần
- Cập nhật Comment
- Click **"Save"**

### **Bước 4: Xác Nhận**

- Lịch sử thay đổi được ghi lại
- Creator sẽ nhận thông báo về thay đổi (tuỳ cấu hình)

---

## **2. Hiển Thị Event Code Trên Dashboard**

### **2.1 Tổng Quan**

**Vấn đề cũ:**

- Teams operations làm việc với Event Codes: "2025-T12-TCMERS-PYC4-Usage"
- Dashboard chỉ hiển thị Event Name: "Tết Campaign 2025"
- Phải tìm kiếm code thủ công → mất thời gian

**Giải pháp:** Hiển thị cả Event Code trên dashboard

### **2.2 Event Code Là Gì?**

Event Code là mã định danh duy nhất của mỗi campaign/event.

```
Ví dụ:
Event Name: "Tết Campaign 2025"
Event Code: "2025-T12-TCMERS-PYC4-Usage"

Cấu trúc: [Year]-[Month]-[Brand]-[Campaign]-[Type]
- 2025: Năm
- T12: Tháng 12 (hoặc Tết)
- TCMERS: Tên brand (viết tắt)
- PYC4: Campaign ID
- Usage: Loại event
```

### **2.3 Nơi Hiển Thị Event Code**

### **A. Campaign Selector / Filter**

**Vị trí:** Dashboard > Create Content / Campaign Filter

**Cách nhìn:**

```
┌──────────────────────────────────────┐
│ Select Campaign                      │
├──────────────────────────────────────┤
│ ☐ Tết Campaign 2025                  │
│   Code: 2025-T12-TCMERS-PYC4-Usage  │
│                                      │
│ ☐ Spring Sale 2025                   │
│   Code: 2025-SPR-ABC-SALE-ENGAGE    │
│                                      │
│ ☐ Summer Flash Deal                  │
│   Code: 2025-SUM-XYZ-FLASH-CONV     │
└──────────────────────────────────────┘
```

### **B. Content Filter Panel**

**Vị Trí:** Dashboard > Content Management > Filter

```
┌─────────────────────────────────┐
│ Filter Content                  │
├─────────────────────────────────┤
│ Event Name / Code               │
│ [Search... code or name ▼]      │
│                                 │
│ Matching:                       │
│ • Tết 2025 (2025-T12-...)      │
│ • Tết Quê (2025-T12-...)       │
└─────────────────────────────────┘
```

### **C. Portfolio / Content List Table**

**Vị Trí:** Dashboard > My Content / Content List

```
┌────────┬────────────────┬────────────────────────────┬────────┐
│ Status │ Campaign Name  │ Event Code                 │ Date   │
├────────┼────────────────┼────────────────────────────┼────────┤
│ ✓      │ Tết 2025      │ 2025-T12-TCMERS-PYC4-Usage│ Mar 19 │
│ ✓      │ Spring Sale    │ 2025-SPR-ABC-SALE-ENGAGE  │ Mar 15 │
│ ⏳     │ Summer Deal    │ 2025-SUM-XYZ-FLASH-CONV   │ Mar 10 │
│ ❌     │ Old Campaign   │ 2024-Q4-OLD-CAMP-ENDED    │ Jan 05 │
└────────┴────────────────┴────────────────────────────┴────────┘
```

### **2.4 Cách Sử Dụng**

### **Tìm Kiếm Theo Event Code**

1. Truy cập Dashboard > Content Management
2. Click vào field "Filter / Search"
3. Nhập Event Code (ví dụ: "2025-T12-")
4. Hệ thống tự động lọc nội dung liên quan

```
Tìm kiếm: "2025-T12"
Kết quả:
- Tết Campaign 2025 (2025-T12-TCMERS-PYC4-Usage)
- Tết Special (2025-T12-OTHER-SPEC-PROMO)
```

### **Copy Event Code**

- Hover chuột vào Event Code
- Sẽ hiển thị biểu tượng "📋 Copy"
- Nhấp để copy code vào clipboard

### **Liên Kết Với Operations Team**

- Ops team có thể dễ dàng chia sẻ Event Code
- Creator/Admin tìm campaign bằng code
- Giảm nhầm lẫn khi có nhiều campaign cùng tên

### **2.5 Lợi Ích**

- ⏱️ Tiết kiệm thời gian tìm kiếm
- 🎯 Chính xác cao: không nhầm lẫn campaign cùng tên
- 📊 Hỗ trợ operations workflow tốt hơn
- 🔗 Dễ dàng quản lý cross-team

---

## **3. Phân Loại Event Theo Tag**

### **3.1 Tổng Quan**

**Vấn đề cũ:**

- Số lượng events tăng nhanh
- Danh sách dài, khó tìm event cần thiết
- Không thể lọc theo mục đích (brand awareness vs conversion)

**Giải pháp:** Thêm Event Tags để phân loại events theo mục đích

### **3.2 Danh Sách Event Tags**

| Tag | Mô Tả | Ví Dụ |
| --- | --- | --- |
| `brand_awareness` | Tăng nhận diện thương hiệu | Campaign quảng cáo brand |
| `product_launch` | Ra mắt sản phẩm mới | Launch smartphone mới |
| `seasonal` | Campaign theo mùa/lễ tết | Tết, Noel, Black Friday |
| `always_on` | Campaign thường xuyên | Flash sale hàng ngày |
| `internal` | Campaign nội bộ | Training, event team |
| `engagement` | Tăng tương tác | Contest, giveaway |
| `conversion` | Chuyển đổi thành bán hàng | Sale campaign, khuyến mại |

### **3.3 Cách Sử Dụng - Phân Loại Event**

### **A. Tạo/Chỉnh Sửa Event**

**Bước 1:** Vào phần tạo event

```
Dashboard > Campaigns > Create New Event
```

**Bước 2:** Điền thông tin event

```
┌──────────────────────────────┐
│ Event Name: Tết 2025        │
│ Event Code: 2025-T12-...    │
│ Start Date: 01/02/2025      │
│ End Date: 15/02/2025        │
└──────────────────────────────┘
```

**Bước 3:** Chọn Event Tags (mới)

```
┌────────────────────────────────┐
│ Event Classification Tags *    │
├────────────────────────────────┤
│ ☐ brand_awareness              │
│ ☑ seasonal          (✓ Chọn)   │
│ ☐ product_launch               │
│ ☐ always_on                    │
│ ☐ internal                     │
│ ☑ engagement        (✓ Chọn)   │
│ ☐ conversion                   │
└────────────────────────────────┘
```

**Bước 4:** Lưu

- Click **"Save"** hoặc **"Create Event"**
- Event được tạo với tags đã chọn

### **B. Lọc Events Theo Tag**

**Vị trí:** Dashboard > Campaigns / Events

```
┌─────────────────────────────────┐
│ Filter by Event Tag             │
├─────────────────────────────────┤
│ ☐ All Events                    │
│ ☐ brand_awareness               │
│ ☑ seasonal          (✓ Đang lọc)│
│ ☐ product_launch               │
│ ☐ always_on                     │
│ ☐ internal                      │
│ ☑ engagement        (✓ Đang lọc)│
│ ☐ conversion                    │
└─────────────────────────────────┘

Results: 8 events matching "seasonal" + "engagement"
```

**Cách sử dụng:**

1. Nhấp vào 1 hoặc nhiều tags cần lọc
2. Danh sách events tự động cập nhật
3. Chỉ hiển thị events có tag được chọn
4. Click "Clear" để xóa lọc

### **3.4 Bảng Thống Kê Event By Tag**

**Vị Trí:** Dashboard > Analytics > Event Classification

```
┌─────────────────────────────────────┐
│ Events by Type (2025)               │
├─────────────────────────────────────┤
│ brand_awareness        ███████ 12    │
│ seasonal               ██████ 8      │
│ product_launch         ████ 6        │
│ always_on              ██████ 10     │
│ internal               █ 2           │
│ engagement             ███████ 11    │
│ conversion             █████ 9       │
│                                     │
│ Total Events: 58                    │
└─────────────────────────────────────┘
```

### **3.5 Workflow - Planning Campaign**

**Scenario:** Marketing Manager lên kế hoạch Q2

1. **Bước 1:** Xem tất cả events Q2
    
    ```
    Dashboard > Campaigns > Filter by Q2 2025
    ```
    
2. **Bước 2:** Xem events theo mục đích
    
    ```
    Filter by "conversion" tags
    → Xem 5 conversion campaigns
    ```
    
3. **Bước 3:** So sánh performance
    
    ```
    Compare results: seasonal vs conversion
    → Xem tag nào có performance tốt hơn
    ```
    
4. **Bước 4:** Lập kế hoạch
    
    ```
    Dự toán resources cho từng tag
    - seasonal: 40% resources
    - engagement: 30% resources
    - conversion: 30% resources
    ```
    

### **3.6 Lợi Ích**

- 🎯 Dễ dàng tìm events theo mục đích
- 📊 Phân tích performance theo loại campaign
- 📈 Lập kế hoạch resources tốt hơn
- 🔄 Tái sử dụng templates cho cùng loại event
- 👥 Team dễ hiểu cấu trúc campaign

---

## **4. Tóm Tắt Các Thay Đổi**

### **Bảng So Sánh Trước/Sau**

| Tính Năng | Trước | Sau |
| --- | --- | --- |
| **Lý Do Từ Chối** | Text tự do (duplicates) | 9 tags chuẩn hóa |
| **Event Code** | Chỉ xem ở backend | Hiển thị trên dashboard |
| **Event Filter** | Chỉ lọc theo tên | Lọc theo tag + code + tên |
| **Thống Kê Event** | Chỉ đếm số lượng | Phân loại theo mục đích |

### **Timeline Implementation**

- **Tuần 1-2:** Phát triển Rejection Tags (4-5 ngày)
- **Tuần 2:** Hiển thị Event Code (0.5-1 ngày)
- **Tuần 2-3:** Event Classification Tags (2-3 ngày)
- **Tuần 3:** QA + Deployment (1-2 ngày)

**Tổng thời gian:** 7-9 ngày làm việc

### **Support & Feedback**

- Nếu có câu hỏi, liên hệ team support
- Report bug qua: `support@company.com`
- Feature request: `product@company.com`

---

## **Phụ Lục A: Keyboard Shortcuts**

| Tính Năng | Shortcut |
| --- | --- |
| Mở form Reject | `Ctrl + Shift + R` |
| Save form | `Ctrl + S` |
| Clear filter | `Ctrl + Shift + C` |
| Copy Event Code | `Ctrl + Shift + K` |

## **Phụ Lục B: FAQ**

### **Q1: Creator có thể thay đổi Rejection Tag không?**

**A:** Không. Chỉ Admin có quyền thay đổi. Creator có thể thấy lý do từ chối và comment chi tiết, sau đó chỉnh sửa nội dung để nộp lại.

### **Q2: Nếu chọn "Other" thì Comment bắt buộc?**

**A:** Có. Khi chọn "Other", bạn phải nhập Comment để mô tả lý do cụ thể.

### **Q3: Event Code có thể thay đổi sau khi tạo không?**

**A:** Không khuyến khích. Event Code nên là định danh cố định. Nếu cần thay đổi, liên hệ Admin.

### **Q4: Một event có thể có nhiều tags không?**

**A:** Có. Ví dụ: "Tết 2025" có thể là cả "seasonal" lẫn "engagement".

### **Q5: Rejection Statistics có include duplicate rejections không?**

**A:** Chỉ tính những rejection lần cuối cùng. Nếu creator nộp lại và bị reject lần 2 với tag khác, chỉ tag lần 2 được tính.

---

**Tài liệu này được cập nhật lần cuối: 19/03/2025** **Phiên bản: CMS v1.1 Upgrade**