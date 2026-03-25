# Đối soát tự động

# **HƯỚNG DẪN SỬ DỤNG - HỆ THỐNG ĐỐI SOÁT TỰ ĐỘNG V2/V3**

## **Giới Thiệu Chung**

### **Hệ Thống Là Gì?**

Hệ thống đối soát tự động giúp bạn **xác minh tuân thủ chiến dịch video** một cách nhanh chóng và chính xác. Thay vì kiểm tra thủ công từng video, hệ thống sẽ tự động thu thập dữ liệu, phân tích và đưa ra gợi ý để bạn duyệt duyệt.

### **Lợi Ích Chính**

✅ **Tiết kiệm thời gian**: Giảm 80%+ thời gian đối soát ✅ **Tự động hóa**: Không cần kiểm tra thủ công từng video ✅ **Chính xác cao**: Dựa trên dữ liệu thực tế và logic xác minh rõ ràng ✅ **Kiểm soát tốt**: Vẫn có thể ghi đè quyết định nếu cần ✅ **Lịch sử đầy đủ**: Ghi lại tất cả hoạt động kiểm tra và thay đổi

---

## **Các Tính Năng Chính**

### **1️⃣ Tính Năng V2: Chụp Ảnh Dữ Liệu**

- **Tự động thu thập dữ liệu**: Sau khi chiến dịch kết thúc, hệ thống tự động chụp ảnh dữ liệu video hàng ngày
- **Hiển thị số lượng xem**: Bạn có thể xem số lượng views hiện tại và các hashtag trong giao diện đối soát
- **Dừng thu thập**: Hệ thống dừng chụp ảnh khi:
    - Đóng đối soát, hoặc
    - Phần thưởng hết hạn chờ xử lý
- **Xuất dữ liệu**: Có thể xuất dữ liệu chụp ảnh kèm theo kết quả danh sách kiểm tra

### **2️⃣ Tính Năng V3: Tự Động Đánh Giá**

- **Tạo danh sách kiểm tra**: Hệ thống tự động tạo các mục kiểm tra dựa trên loại phần thưởng
- **Trạng thái 3 mức**: Mỗi mục có thể là:
    - ✅ **Đạt** - Đáp ứng tiêu chuẩn
    - ❌ **Không đạt** - Vi phạm tiêu chuẩn
    - ⚠️ **Chưa xác minh** - Cần kiểm tra thêm
- **Gợi ý tự động**: Hệ thống phân tích và gợi ý:
    - Phê duyệt tự động
    - Từ chối tự động
    - Cần kiểm tra thêm

---

## **Quy Trình Làm Việc**

```
┌─────────────────────────────────────────────────────────────┐
│ CHIẾN DỊCH KẾT THÚC                                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ HỆ THỐNG TỰ ĐỘNG                                            │
│ • Chụp ảnh dữ liệu hàng ngày (V2)                          │
│ • Tạo danh sách kiểm tra (V3)                              │
│ • Đánh giá và gợi ý quyết định                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ ADMIN REVIEW (BẠN)                                          │
│ • Xem gợi ý của hệ thống                                   │
│ • Kiểm tra chi tiết từng mục                               │
│ • Phê duyệt hoặc từ chối                                   │
│ • (Tùy chọn) Ghi đè quyết định nếu cần                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ KỲ DUYỆT DUYỆT HOÀN THÀNH                                   │
│ • Ghi lại tất cả quyết định                                │
│ • Lưu lịch sử đầy đủ                                       │
│ • Xuất báo cáo (tùy chọn)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## **Hướng Dẫn Chi Tiết**

### **📖 BƯỚC 1: Truy Cập Giao Diện Đối Soát**

1. Đăng nhập vào hệ thống
2. Vào mục **"Đối Soát"** hoặc **"Reconciliation"**
3. Chọn chiến dịch cần đối soát
4. Chờ hệ thống tải dữ liệu (⏱️ tối đa 2 giây cho 500 video)

### **📖 BƯỚC 2: Xem Danh Sách Kiểm Tra**

Giao diện sẽ hiển thị danh sách các video với các mục kiểm tra:

| Video | Kiểm Tra | Kết Quả | Ghi Chú |
| --- | --- | --- | --- |
| Video 1 | Truy cập được | ✅ | Thành công |
| Video 1 | Hashtag đầy đủ | ✅ | Có tất cả |
| Video 1 | Lượng xem | ⚠️ | Cảnh báo |
| Video 2 | Truy cập được | ❌ | Video bị xóa |
| ... | ... | ... | ... |

### **📖 BƯỚC 3: Xem Gợi Ý của Hệ Thống**

Hệ thống sẽ gợi ý:

**🟢 Phê Duyệt Tự Động (Auto-Approve)**

- Tất cả mục đều ✅ Đạt
- Không có lỗi bắt buộc
- → Bạn có thể nhanh chóng bấm "Phê duyệt"

**🔴 Từ Chối Tự Động (Auto-Reject)**

- Một hoặc nhiều mục ❌ Không đạt
- Có lỗi bắt buộc
- → Bạn có thể nhanh chóng bấm "Từ chối"

**🟡 Cần Kiểm Tra Thêm (Needs Review)**

- Có mục ⚠️ Chưa xác minh
- Có cảnh báo
- → Cần bạn xem xét kỹ trước quyết định

### **📖 BƯỚC 4: Thực Hiện Hành Động**

### **Phê Duyệt Nhanh (Quick Approve)**

1. Nếu gợi ý là "Phê duyệt tự động"
2. Bấm nút **"Phê Duyệt"** (hoặc Approve)
3. Xác nhận → Hoàn tất

### **Từ Chối Nhanh (Quick Reject)**

1. Nếu gợi ý là "Từ chối tự động"
2. Bấm nút **"Từ Chối"** (hoặc Reject)
3. Xác nhận → Hoàn tất

### **Kiểm Tra Chi Tiết (Manual Review)**

1. Nếu có mục ⚠️ **Chưa xác minh**
2. Bấm vào video để xem chi tiết
3. Kiểm tra dữ liệu thực tế (truy cập, hashtag, lượng xem)
4. **Chọn hành động**:
    - Đánh dấu mục thành ✅ Đạt (nếu OK)
    - Đánh dấu mục thành ❌ Không đạt (nếu có vấn đề)
5. Bấm **"Lưu"** để cập nhật

---

## **Các Tiêu Chí Kiểm Tra (Dành Cho Phần Thưởng Dựa Trên Lượng Xem)**

### **✅ Kiểm Tra 1: Khả Năng Truy Cập Video**

- **Mục tiêu**: Video có thể mở được không?
- **Cách kiểm tra**: Hệ thống tự động kiểm tra
- **Kết quả**:
    - ✅ **Đạt**: Video truy cập thành công
    - ❌ **Không đạt**: Video bị xóa/khóa/riêng tư

### **✅ Kiểm Tra 2: Hashtag Đầy Đủ**

- **Mục tiêu**: Video có tất cả hashtag bắt buộc không?
- **Cách kiểm tra**: Hệ thống so sánh hashtag trong dữ liệu chụp ảnh
- **Kết quả**:
    - ✅ **Đạt**: Có tất cả hashtag bắt buộc
    - ⚠️ **Chưa xác minh**: Cần bạn xác nhận thêm
    - ❌ **Không đạt**: Thiếu hashtag bắt buộc

### **✅ Kiểm Tra 3: Toàn Vẹn Lượng Xem**

- **Mục tiêu**: Lượng xem hiện tại ≥ lượng xem khi ghi danh?
- **Cách kiểm tra**: So sánh dữ liệu lịch sử với dữ liệu hiện tại
- **Kết quả**:
    - ✅ **Đạt**: Lượng xem không giảm
    - ⚠️ **Cảnh báo**: Lượng xem không tăng như kỳ vọng (cần review)
    - ❌ **Không đạt**: Lượng xem giảm

---

## **Các Tình Huống Xử Lý**

### **📌 Tình Huống 1: Tất Cả Mục Đều Đạt ✅**

**Gợi ý hệ thống**: 🟢 Phê Duyệt Tự Động

**Cách xử lý**:

1. Xem lại gợi ý (mất 10 giây)
2. Bấm "Phê duyệt"
3. Xác nhận
4. Xong!

---

### **📌 Tình Huống 2: Có Mục Không Đạt ❌**

**Gợi ý hệ thống**: 🔴 Từ Chối Tự Động

**Cách xử lý**:

1. Xem mục nào không đạt
2. Nếu đồng ý với gợi ý:
    - Bấm "Từ Chối"
    - Xác nhận
3. Nếu muốn ghi đè (vì có lý do đặc biệt):
    - Bấm "Ghi đè quyết định"
    - Nhập lý do (tối thiểu 10 ký tự)
    - Ví dụ: "Video đã được khôi phục, hãy chấp nhận"
    - Bấm "Lưu"

---

### **📌 Tình Huống 3: Có Mục Chưa Xác Minh ⚠️**

**Gợi ý hệ thống**: 🟡 Cần Kiểm Tra Thêm

**Cách xử lý**:

1. Bấm vào video để xem chi tiết
2. Kiểm tra dữ liệu thực tế:
    - Video có truy cập được không?
    - Hashtag có đầy đủ không?
    - Lượng xem như nào?
3. Dựa vào kiểm tra, quyết định:
    - ✅ Đạt (nếu OK)
    - ❌ Không đạt (nếu có vấn đề)
4. Bấm "Lưu"
5. Sau đó quyết định phê duyệt hoặc từ chối tổng thể

---

### **📌 Tình Huống 4: Cần Ghi Đè Quyết Định**

**Khi nào ghi đè?**

- Video thực sự tốt nhưng hệ thống gợi ý từ chối
- Video có vấn đề nhưng có lý do chính đáng để chấp nhận
- Lỗi kỹ thuật tạm thời

**Cách ghi đè**:

1. Bấm "Ghi đè quyết định" (Override)
2. Chọn quyết định mới:
    - Phê duyệt (nếu muốn chấp nhận)
    - Từ chối (nếu muốn từ chối)
3. Nhập **lý do** (tối thiểu 10 ký tự)
    - Ví dụ: "Hashtag đã được sửa, hãy chấp nhận"
    - Ví dụ: "Video là quảng cáo không hợp lệ, cần từ chối"
4. Bấm "Lưu"
5. **Lưu ý**: Tất cả ghi đè sẽ được ghi lại trong lịch sử

---

### **📌 Tình Huống 5: Phê Duyệt/Từ Chối Hàng Loạt**

**Khi nào sử dụng?**

- Nhiều video cùng trạng thái
- Cần xử lý nhanh

**Cách thực hiện**:

1. Chọn nhiều video (ticked checkbox)
2. Bấm "Phê duyệt hàng loạt" hoặc "Từ chối hàng loạt"
3. Xác nhận
4. Xong!

---

## **Lưu Ý Quan Trọng**

### **⏱️ Thời Gian Xử Lý**

- **Thu thập dữ liệu**: Tối đa 4 giờ cho 50,000 video
- **Tải giao diện**: Tối đa 2 giây cho 500 video
- **Duyệt duyệt**: Thường 1-2 tuần tùy chiến dịch

### **🔒 An Toàn Dữ Liệu**

- ✅ **Dữ liệu chụp ảnh không bao giờ bị xóa** - được lưu giữ vĩnh viễn
- ✅ **Lịch sử đầy đủ** - tất cả hoạt động được ghi lại
- ✅ **Kiểm soát truy cập** - chỉ admin được phép duyệt duyệt
- ⚠️ **Không thể hủy**: Một khi phê duyệt/từ chối, không thể quay lại (liên hệ admin nếu cần sửa)

### **❌ Không Được Phép**

- ❌ Xóa dữ liệu chụp ảnh
- ❌ Phê duyệt trong khi có mục bắt buộc không đạt
- ❌ Từ chối mà không có lý do
- ❌ Ghi đè mà không nhập lý do đầy đủ

### **✅ Thực Hành Tốt**

- ✅ Luôn kiểm tra gợi ý của hệ thống trước khi quyết định
- ✅ Nếu không chắc chắn, kiểm tra chi tiết trước
- ✅ Ghi lý do rõ ràng khi ghi đè
- ✅ Xuất báo cáo hàng ngày để theo dõi tiến độ
- ✅ Liên hệ team kỹ thuật nếu thấy lỗi hệ thống

---

## **📞 Hỗ Trợ & Liên Hệ**

| Vấn Đề | Liên Hệ |
| --- | --- |
| Hỏi về cách sử dụng | Xem lại hướng dẫn này hoặc hỏi team |
| Video bị lỗi trong hệ thống | Liên hệ team kỹ thuật |
| Cần ghi đè quyết định | Bấm "Ghi đè" và nhập lý do |
| Lịch sử hoạt động | Xem mục "Audit Log" trong chi tiết đối soát |
| Cần xuất báo cáo | Bấm "Xuất dữ liệu" (Export) |

---

## **📊 Ví Dụ Cụ Thể**

### **Ví Dụ 1: Phê Duyệt Video Bình Thường**

```
Video: "TikTok Dance Challenge #1"
├─ Kiểm Tra 1: Truy cập được? ✅ Đạt
├─ Kiểm Tra 2: Hashtag đầy đủ? ✅ Đạt
└─ Kiểm Tra 3: Lượng xem hợp lệ? ✅ Đạt

Gợi ý hệ thống: 🟢 PHEE DUYỆT TỰ ĐỘNG

Hành động của bạn:
1. Bấm "Phê Duyệt"
2. Xác nhận
3. ✅ Xong

Kết quả: Video được chấp nhận, phần thưởng sẽ được phát
```

### **Ví Dụ 2: Từ Chối Video Bị Xóa**

```
Video: "Product Review Video #5"
├─ Kiểm Tra 1: Truy cập được? ❌ KHÔNG ĐẠT (Video bị xóa)
├─ Kiểm Tra 2: Hashtag đầy đủ? ✅ Đạt
└─ Kiểm Tra 3: Lượng xem hợp lệ? ✅ Đạt

Gợi ý hệ thống: 🔴 TỪ CHỐI TỰ ĐỘNG (Video không thể truy cập)

Hành động của bạn:
1. Bấm "Từ Chối"
2. Xác nhận
3. ✅ Xong

Kết quả: Video bị từ chối, người dùng không nhận phần thưởng
```

### **Ví Dụ 3: Kiểm Tra Video Có Cảnh Báo**

```
Video: "Unboxing Video #7"
├─ Kiểm Tra 1: Truy cập được? ✅ Đạt
├─ Kiểm Tra 2: Hashtag đầy đủ? ✅ Đạt
└─ Kiểm Tra 3: Lượng xem hợp lệ? ⚠️ CẢNH BÁO (Tăng chậm)

Gợi ý hệ thống: 🟡 CẦN KIỂM TRA THÊM

Hành động của bạn:
1. Bấm vào video để xem chi tiết
2. Kiểm tra: Lượng xem tăng từ 1000 → 1200 (2 tuần)
3. Quyết định: Tăng chậm nhưng hợp lệ
4. Đánh dấu: ✅ Đạt
5. Bấm "Lưu"
6. Bấm "Phê Duyệt"
7. Xác nhận
8. ✅ Xong

Kết quả: Video được chấp nhận
```

### **Ví Dụ 4: Ghi Đè Quyết Định**

```
Video: "Contest Submission #3"
├─ Kiểm Tra 1: Truy cập được? ❌ KHÔNG ĐẠT (Hashtag sai)
├─ Kiểm Tra 2: Hashtag đầy đủ? ❌ KHÔNG ĐẠT
└─ Kiểm Tra 3: Lượng xem hợp lệ? ✅ Đạt

Gợi ý hệ thống: 🔴 TỪ CHỐI TỰ ĐỘNG

Hành động của bạn (vì bạn biết video đã được sửa):
1. Bấm "Ghi đè quyết định" (Override)
2. Chọn: Phê duyệt
3. Nhập lý do: "Người dùng đã sửa hashtag theo yêu cầu, xác nhận đã OK"
4. Bấm "Lưu"
5. ✅ Xong

Kết quả: Video được chấp nhận (với ghi chú về ghi đè)
Lịch sử: Ghi đè được lưu lại cho kiểm tra sau
```

---

**Cập nhật lần cuối**: 26/02/2026 **Phiên bản**: V2/V3 Reconciliation System **Dành cho**: Admin - Đối soát chiến dịch