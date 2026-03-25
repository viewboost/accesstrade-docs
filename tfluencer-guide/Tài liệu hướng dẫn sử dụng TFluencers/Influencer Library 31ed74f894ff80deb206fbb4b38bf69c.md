# Influencer Library

# **HDSD Danh Sách Profile Influencer - Hướng Dẫn Chi Tiết**

**Phiên bản:** v1.0 **Ngày cập nhật:** Tháng 3, 2026 **Mục đích:** Hướng dẫn sử dụng mục "Hồ Sơ" (Profiles) trong Thư Viện Influencer

---

## **🎯 Tổng Quan Giao Diện**

### **Cấu Trúc Chính**

```
┌─────────────────────────────────────────────────────────────────────┐
│ Danh Sách Profile Influencer (Hồ Sơ)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ [Filter] [Filter] [Filter] [Filter]        [🔍 Tìm theo tên]       │
│ Nền tảng  Tier    Engagement  Trạng thái                            │
│                                                                       │
├────────────────────────────────────────────────────────────────────┤
│ BẢNG DANH SÁCH:                                                    │
│                                                                       │
│ Nền Tảng │ Tên Tài Khoản │ Người Theo Dõi │ Tỷ Lệ Eng │ Lượt Xem │ Hành Động
│ ─────────┼───────────────┼────────────────┼──────────┼──────────┼──────────
│ 🔴 FB    │ Hang Pham     │ 9K             │ 0%       │ 0        │ Xem kênh
│ 🔴 YT    │ Noodle & Pals │ 2.3M           │ 0.08%    │ 2.1M     │ Xem kênh
│ 🔴 YT    │ Myn Xinh      │ 170K           │ 1.43%    │ 15K      │ Xem kênh
│ ...
└────────────────────────────────────────────────────────────────────┘
```

### **Các Thành Phần Chính**

| Phần | Chức Năng |
| --- | --- |
| **Filter Nền Tảng** | Chọn Facebook, YouTube, Instagram, TikTok |
| **Filter Tier** | Lọc theo loại influencer (Nano, Micro, Mid, Macro, Mega) |
| **Filter Engagement** | Lọc theo tỷ lệ tương tác |
| **Filter Trạng Thái** | Lọc theo trạng thái (Approved, Pending, Rejected) |
| **Thanh Tìm Kiếm** | Tìm theo tên hoặc @handle của influencer |
| **Bảng Danh Sách** | Hiển thị danh sách influencer với thông tin cơ bản |

---

## **🔍 Các Công Cụ Filter**

### **1️⃣ Filter Nền Tảng (Platform)**

```
Nền tảng ▼
├─ Facebook 📘
├─ YouTube 🔴
├─ Instagram 📷
├─ TikTok 🎵
└─ Tất cả (không filter)
```

**Mục đích:** Chọn nền tảng mà bạn muốn tìm influencer

**Cách sử dụng:**

- Click dropdown "Nền tảng"
- Chọn 1 nền tảng hoặc chọn "Tất cả"
- Danh sách sẽ tự động cập nhật

**Ví dụ:**

```
- Chọn: YouTube
  → Hiển thị: Tất cả influencer có kênh YouTube

- Chọn: Facebook
  → Hiển thị: Tất cả influencer có page Facebook
```

---

### **2️⃣ Filter Tier (Loại Influencer)**

```
Tier ▼
├─ NANO (1K - 10K) 📱
├─ MICRO (10K - 100K) 👥
├─ MID (100K - 500K) ⭐
├─ MACRO (500K - 1M) 🌟
├─ MEGA (1M+) 👑
└─ Tất cả (không filter)
```

**Mục đích:** Lọc theo kích thước của influencer (số lượng followers)

**Cách sử dụng:**

- Click dropdown "Tier"
- Chọn loại bạn cần
- Danh sách sẽ lọc ra những influencer thuộc tier đó

**Ví dụ:**

```
Chọn: MICRO
→ Hiển thị: Tất cả influencer có 10K - 100K followers

Chọn: MID
→ Hiển thị: Tất cả influencer có 100K - 500K followers
```

---

### **3️⃣ Filter Engagement (Tỷ Lệ Tương Tác)**

```
Engagement ▼
├─ Cao (> 3%)
├─ Trung bình (1% - 3%)
├─ Thấp (< 1%)
└─ Tất cả (không filter)
```

**Mục đích:** Lọc theo chất lượng tương tác của followers

**Cách sử dụng:**

- Click dropdown "Engagement"
- Chọn mức engagement mà bạn muốn
- Danh sách sẽ chỉ hiển thị những influencer khớp

**Ví dụ:**

```
Chọn: Cao (> 3%)
→ Hiển thị: Những influencer có followers tương tác tốt

Chọn: Trung bình (1% - 3%)
→ Hiển thị: Những influencer có engagement bình thường
```

---

### **4️⃣ Filter Trạng Thái (Status)**

```
Trạng thái ▼
├─ ✅ Approved (Đã duyệt)
├─ ⏳ Pending (Chờ duyệt)
├─ ❌ Rejected (Từ chối)
└─ Tất cả (không filter)
```

**Mục đích:** Lọc theo trạng thái xét duyệt của hồ sơ

**Cách sử dụng:**

- Click dropdown "Trạng thái"
- Chọn trạng thái bạn cần
- Danh sách sẽ cập nhật

**Ý nghĩa từng trạng thái:**

- ✅ **Approved**: Hồ sơ đã được xét duyệt, có thể hợp tác ngay
- ⏳ **Pending**: Hồ sơ đang chờ xét duyệt
- ❌ **Rejected**: Hồ sơ bị từ chối, không phù hợp

---

### **5️⃣ Tìm Kiếm Theo Tên (@handle)**

```
🔍 Tìm theo tên hoặc @handle...
```

**Mục đích:** Tìm nhanh influencer cụ thể

**Cách sử dụng:**

- Click vào ô tìm kiếm
- Nhập tên hoặc @handle (không cần @)
- Danh sách sẽ lọc real-time

**Ví dụ:**

```
Nhập: "Hang Pham"
→ Hiển thị: Tất cả influencer có tên chứa "Hang Pham"

Nhập: "huyen ut"
→ Hiển thị: Influencer có @handle là "huyen ut"
```

---

## **📋 Cách Đọc Bảng Danh Sách**

### **Cột Dữ Liệu**

```
┌─────────┬──────────────┬─────────────────┬─────────────┬──────────────┬────────────┐
│ Nền Tảng│ Tên Tài Khoản│ Người Theo Dõi  │ Tỷ Lệ Eng.  │ Lượt Xem TB  │ Hành Động  │
├─────────┼──────────────┼─────────────────┼─────────────┼──────────────┼────────────┤
│  🔴 FB  │ Hang Pham    │ 9K              │ 0%          │ 0            │ Xem kênh  │
│  🔴 YT  │ Noodle&Pals  │ 2.3M            │ 0.08%       │ 2.1M         │ Xem kênh  │
│  🔴 YT  │ Myn Xinh     │ 170K            │ 1.43%       │ 15K          │ Xem kênh  │
└─────────┴──────────────┴─────────────────┴─────────────┴──────────────┴────────────┘
```

### **1. Nền Tảng (Platform)**

```
🔴 = Facebook
🔴 = YouTube
📷 = Instagram
🎵 = TikTok
```

### **2. Tên Tài Khoản (Account Name)**

```
Tên chính thức hoặc @handle của influencer
Ví dụ: "Hang Pham", "huyen ut"
```

### **3. Người Theo Dõi (Followers)**

```
Số lượng followers/subscribers hiện tại
Ví dụ: 9K = 9,000 people
       2.3M = 2,300,000 people
```

### **4. Tỷ Lệ Engagement (Eng. Rate)**

```
Phần trăm lượt tương tác (like, comment, share)
Công thức: (Total Engagement / Total Views) × 100%

Ví dụ:
- 0%    = Không có tương tác (followers không thực, không quan tâm)
- 1.43% = Engagement bình thường
- 3.78% = Engagement tốt (followers tương tác nhiều)
```

### **5. Lượt Xem Trung Bình (Avg Views)**

```
Số lượng views trung bình mỗi video/post
Ví dụ:
- 0      = Không có video, hoặc followers không xem
- 2.1M   = Trung bình mỗi video được xem 2.1 triệu lần (rất cao)
```

### **6. Hành Động (Action)**

```
Nút "Xem kênh" → Click để xem chi tiết hồ sơ influencer
```

---

## **🔗 Xem Chi Tiết Hồ Sơ Influencer**

### **Cách Truy Cập**

**Cách 1:** Click nút "Xem kênh" ở cuối mỗi hàng

```
┌─────────────────────────────────┐
│ Hang Pham | 9K | 0% | 0 | [Xem kênh] ← Click vào đây
└─────────────────────────────────┘
```

**Cách 2:** Click vào tên influencer

```
┌─────────────────────────────────┐
│ [Hang Pham] ← Click vào tên này
└─────────────────────────────────┘
```

---

### **Trang Chi Tiết Hồ Sơ**

Sau khi click, bạn sẽ thấy trang chi tiết với các thông tin:

### **Phần 1: Thông Tin Cơ Bản**

```
┌────────────────────────────────────────────┐
│ [Avatar] Hang Pham    🔴 Facebook          │
│          Influencer: huyen ut               │
│          CTY TNHH HPNUTS - CUNG CẤP...      │
│          https://www.facebook.com/hang...   │
├────────────────────────────────────────────┤
│ Tabs: Tổng quan | Đánh giá                │
└────────────────────────────────────────────┘
```

**Các trường:**

- **Tên** (Name): Hang Pham
- **Nền tảng** (Platform): Facebook
- **Handle**: huyen ut (tài khoản chính thức)
- **Mô tả** (Bio): Mô tả về công ty/cá nhân
- **Link**: Đường dẫn đến kênh chính thức

---

### **Phần 2: Thống Kê Tổng Quan**

```
┌─────────────┬──────────┬──────────┬──────────┐
│ 8.6K        │ 0        │ 0%       │ 56.5     │
│ Người theo  │ Lượt xem │ Tương    │ Score    │
│ dõi         │ trung bình│ tác     │ (Good)   │
└─────────────┴──────────┴──────────┴──────────┘
```

**Giải thích:**

- **Người theo dõi (8.6K)**: Tổng số followers hiện tại
- **Lượt xem trung bình (0)**: Views trung bình mỗi post (có thể 0 do chưa crawl)
- **Tương tác (0%)**: Engagement rate hiện tại
- **Score (56.5 - Good)**: Điểm đánh giá tổng thể của influencer (0-100)
    - 90-100: 🌟 Xuất sắc
    - 80-89: ✅ Rất tốt
    - 70-79: ✅ Tốt
    - 60-69: ⚠️ Chấp nhận được
    - <60: ❌ Không phù hợp

---

### **Phần 3: Thông Tin Profile**

```
┌──────────────────────────────────┐
│ Thông tin Profile                │
├──────────────────────────────────┤
│ Ngành nghề / Lĩnh vực:           │
│ Entertainment | Music | Film      │
│                                   │
│ Nền tảng hoạt động:              │
│ 🔴 Facebook                      │
│                                   │
│ Quốc gia:                        │
│ CA (Canada)                      │
└──────────────────────────────────┘
```

**Các trường:**

- **Ngành nghề** (Category): Entertainment, Music, Film, etc.
- **Nền tảng hoạt động** (Platforms): Các nền tảng có kênh
- **Quốc gia** (Country): Quốc gia của influencer

---

### **Phần 4: Thông Tin Đối Tượng (Demographics)**

```
┌──────────────────────────────────────────┐
│ Thông Tin Đối Tượng                      │
├──────────────────┬──────────────────────┤
│ Độ tuổi (Age)    │ Giới tính (Gender)   │
│ ██████░░░░ 18-24 │ ██████░░░░ Nam      │
│                  │ ███░░░░░░░ Nữ       │
└──────────────────┴──────────────────────┘
```

**Ý nghĩa:**

- **Độ tuổi**: Phân bố độ tuổi của followers
    - 18-24: Followers chủ yếu ở độ tuổi này
    - 25-34, 35-44, v.v.
- **Giới tính**: Tỷ lệ nam/nữ trong followers
    - Nam: Phần trăm followers nam
    - Nữ: Phần trăm followers nữ

**Cách sử dụng:**

```
Ví dụ: Bạn muốn quảng cáo sản phẩm dành cho nữ
→ Chọn influencer có giới tính followers phần lớn là nữ
```

---

### **Phần 5: Các Kênh Khác của Influencer**

```
┌─────────────────────────────────────────────────────┐
│ Các profile khác của Influencer này                 │
├─────────────────────────────────────────────────────┤
│
│ ┌──────────────────────────┐ ┌──────────────────────┐
│ │ 🔴 YouTube              │ │ 🔴 YouTube          │
│ │ TH Official Channel      │ │ FOREST STUDIO       │
│ │ https://www.youtube...   │ │ https://www.youtube│
│ │                          │ │                    │
│ │ Người theo dõi: 248K     │ │ Người theo dõi:1.1M│
│ │ Tương tác: 0%            │ │ Tương tác: 0%      │
│ │ Lượt xem TB: 0           │ │ Lượt xem TB: 0     │
│ │ [Xem Profile]            │ │ [Xem Profile]      │
│ └──────────────────────────┘ └──────────────────────┘
│
│ ┌──────────────────────────┐ ┌──────────────────────┐
│ │ 📘 Facebook              │ │ 🔴 YouTube          │
│ │ Atus                     │ │ Nốc Nhà Review      │
│ │ https://www.facebook...  │ │ https://www.youtube│
│ │                          │ │                    │
│ │ Người theo dõi: 100K     │ │ ...                │
│ │ ...                      │ │                    │
│ └──────────────────────────┘ └──────────────────────┘
│
└─────────────────────────────────────────────────────┘
```

**Giải thích:**

- Influencer có thể có **nhiều kênh** trên các nền tảng khác nhau
- Mỗi kênh được hiển thị dưới dạng thẻ (card)
- Mỗi card chứa: Nền tảng, Tên kênh, Link, Followers, Engagement, Views, nút "Xem Profile"

**Thông tin mỗi kênh:**

```
┌─────────────────────────────┐
│ Platform Badge (🔴, 📘, etc)│
├─────────────────────────────┤
│ Channel Name: TH Official   │
│ Link: https://youtube.com/..│
│                              │
│ Người theo dõi: 248K        │
│ Tương tác: 0%               │
│ Lượt xem TB: 0              │
│                              │
│ [Xem Profile]  ← Click xem  │
└─────────────────────────────┘
```

---

## **📊 Thông Tin Các Kênh Đa Nền Tảng**

### **Khi Influencer Có Nhiều Kênh**

**Tình Huống:** Một creator có thể hoạt động trên nhiều nền tảng:

- Kênh YouTube chính: 248K followers
- Kênh YouTube khác (studio): 1.1M followers
- Kênh Facebook: 100K followers
- v.v.

**Cách Xem:**

1. **Từ danh sách chính**

```
Trong bảng danh sách chính, bạn sẽ thấy creator có nhiều dòng
(nếu có nhiều kênh):

┌─────────┬──────────────┬──────┐
│ Platform│ Channel Name │ Followers
├─────────┼──────────────┼──────┤
│ 🔴 YT   │ TH Official  │ 248K │
│ 🔴 YT   │ FOREST STU   │ 1.1M │
│ 📘 FB   │ Atus         │ 100K │
└─────────┴──────────────┴──────┘
```

1. **Từ trang chi tiết**

```
Khi bạn vào chi tiết 1 kênh, bạn sẽ thấy tất cả kênh khác
của cùng creator dưới phần "Các profile khác"
```

### **Cách Lựa Chọn Kênh Phù Hợp**

```
Chiến dịch: Quảng cáo sản phẩm YouTube
→ Chọn creator có kênh YouTube lớn (248K hoặc 1.1M)

Chiến dịch: Quảng cáo trên Facebook
→ Chọn kênh Facebook của creator (100K followers)
```

---

## **📝 Các Trường Dữ Liệu Chi Tiết**

### **Thông Tin Tài Khoản**

| Trường | Ý Nghĩa | Ví Dụ |
| --- | --- | --- |
| **Tên** | Tên chính thức của creator | Hang Pham, Myn Xinh |
| **@Handle** | Tài khoản/username | huyen ut, angel_wing |
| **Nền tảng** | Mạng xã hội | Facebook, YouTube, TikTok |
| **Link** | URL đến kênh | [https://facebook.com/hangpham68](https://facebook.com/hangpham68) |
| **Bio** | Mô tả tài khoản | CTY TNHH HPNUTS... |

### **Thống Kê Tương Tác**

| Trường | Ý Nghĩa | Cách Tính |
| --- | --- | --- |
| **Followers** | Số người theo dõi | Từ API nền tảng |
| **Engagement** | Tỷ lệ tương tác | (Likes + Comments) / Views × 100% |
| **Avg Views** | Lượt xem trung bình | Tổng views / Số videos |
| **Score** | Điểm đánh giá chung | Thuật toán nội bộ |

### **Thông Tin Đối Tượng**

| Trường | Ý Nghĩa | Ví Dụ |
| --- | --- | --- |
| **Độ tuổi** | Phân bố tuổi followers | 18-24: 45%, 25-34: 35% |
| **Giới tính** | Tỷ lệ nam/nữ | Nam: 60%, Nữ: 40% |
| **Quốc gia** | Vị trí địa lý chính | CA, US, VN |
| **Ngành hàng** | Lĩnh vực nội dung | Entertainment, Music, Gaming |

---

## **💡 Mẹo Sử Dụng Hiệu Quả**

### **Mẹo 1: Lọc Thông Minh**

```
Để tìm influencer tốt nhất:

1. Filter Nền tảng = YouTube
2. Filter Tier = MICRO (10K - 100K)
3. Filter Engagement = Cao (> 3%)
4. Kết quả: Những influencer YouTube MICRO có engagement tốt
```

### **Mẹo 2: Kiểm Tra Followers "Thật"**

```
Dấu hiệu followers GIẢ:
- Followers lớn nhưng Engagement = 0%
  VD: 2.3M followers nhưng 0.08% engagement
  → Có thể followers mua hoặc bots

Dấu hiệu followers THẬT:
- Followers cao và Engagement > 1-2%
  VD: 170K followers, 1.43% engagement
  → Followers tương tác thực
```

### **Mẹo 3: So Sánh Nhiều Kênh**

```
Nếu creator có nhiều kênh:
- Kênh 1: 100K followers, 2% engagement ✅
- Kênh 2: 1M followers, 0.08% engagement ❌

→ Chọn kênh 1 vì engagement tốt hơn
```

### **Mẹo 4: Chọn Theo Ngành Hàng**

```
Bạn bán: Mỹ phẩm skincare
→ Tìm influencer chuyên về:
   - Beauty
   - Entertainment + Beauty
   - Fashion (vì chung audience nữ)

Không nên chọn: Gaming, Tech (audience khác)
```

### **Mẹo 5: Ghi Chú Khi Xem**

```
Khi xem chi tiết influencer:
1. Xem Score (56.5 = Good) → Thích hợp không?
2. Xem Engagement → Followers tương tác không?
3. Xem Demographics → Đối tượng khớp không?
4. Xem các kênh khác → Có kênh nào phù hợp hơn?
5. Ghi chú → Lý do chọn/không chọn
```

### **Mẹo 6: Xuất Danh Sách (Nếu Có)**

```
Sau khi lọc xong:
1. Chọn những influencer phù hợp
2. Nhấn nút "Xuất" (nếu có)
3. Lưu danh sách Excel để:
   - Gửi cho team
   - Liên hệ influencer
   - Theo dõi tiến độ
```

---

## **⚠️ Những Lỗi Thường Gặp**

### **Lỗi 1: Chọn Influencer Vì Followers Lớn**

```
❌ SAI:
Chọn: BLACKPINK (100M followers)
Lý do: Followers rất lớn

✅ ĐÚNG:
Chọn: Noodle & Pals (2.3M followers)
Lý do: Followers phù hợp, engagement ổn

Vì sao:
- Followers lớn = Giá cao = Budget vượt
- Engagement lớn creators = kết quả tốt hơn
```

### **Lỗi 2: Bỏ Qua Engagement Rate**

```
❌ SAI:
- Followers: 2.3M
- Engagement: 0.08% ← LỚP (followers có thể fake)
- Giá cả: Rất cao

✅ ĐÚNG:
- Followers: 170K
- Engagement: 1.43% ← TỐT (followers thực)
- Giá cả: Hợp lý
```

### **Lỗi 3: Không Xem Demographics**

```
❌ SAI:
Bán sản phẩm cho nữ → Chọn creator có 60% followers nam

✅ ĐÚNG:
Bán sản phẩm cho nữ → Chọn creator có 70%+ followers nữ
```

### **Lỗi 4: Chỉ Nhìn Một Kênh**

```
❌ SAI:
Creator chỉ có 100K trên Facebook → Tạm

✅ ĐÚNG:
Check tất cả kênh → Có YouTube 1.1M?
→ Chọn YouTube thay vì Facebook
```

---

## **📌 Quy Trình Nhanh: Tìm Influencer Phù Hợp**

### **Step 1: Xác Định Nhu Cầu**

```
Nền tảng? TikTok
Tier? MICRO (10-100K)
Ngành? Entertainment
```

### **Step 2: Áp Dụng Filter**

```
1. Filter Nền tảng = TikTok
2. Filter Tier = MICRO
3. Filter Engagement = Cao (>3%)
```

### **Step 3: Xem Danh Sách**

```
Bảng hiển thị danh sách kết quả
→ Tìm những người có engagement cao
```

### **Step 4: Xem Chi Tiết**

```
Click "Xem kênh" → Kiểm tra:
- Score có tốt?
- Demographics phù hợp?
- Có kênh phù hợp khác?
```

### **Step 5: Ghi Chú & Lưu**

```
Ghi chú tên, link, lý do chọn
Lưu vào danh sách để liên hệ sau
```

---

## **📞 Hỗ Trợ**

**Nếu gặp vấn đề:**

- Không thấy filter → Refresh trang (F5)
- Danh sách trống → Kiểm tra filter có quá hạn chế?
- Score không update → Có thể dữ liệu cũ, chạy lại sync

---

**Phiên bản v1.0 - Tháng 3, 2026** **Hướng dẫn sử dụng Profiles (Hồ Sơ) - Influencer Library Admin**