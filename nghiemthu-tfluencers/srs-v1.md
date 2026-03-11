# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM

### Dự án: **Techcombank Influencer Platform**

**Phiên bản:** 1.2

**Ngày phát hành:** 08/11/2025

---

# I. Giới thiệu

# 1. Mục tiêu

Tài liệu này mô tả chi tiết yêu cầu nghiệp vụ, yêu cầu chức năng và mô hình vận hành của **hệ thống Techcombank Influencer Platform**, bao gồm các module, quy trình và hành vi liên quan đến việc quản lý chiến dịch truyền thông, nhà sáng tạo nội dung (influencer), ngân sách, cơ chế đối soát – chi trả hoa hồng và quy trình duyệt nội dung.

Mục tiêu của tài liệu là thống nhất giữa:

- **Techcombank (TCB)** – đơn vị **sở hữu và định hướng hệ thống**,
- **AccessTrade (AT)** – đơn vị **phát triển và vận hành chính**,
    
    về phạm vi chức năng, mô hình tổ chức, trách nhiệm của từng bên, và cách thức hệ thống hỗ trợ các hoạt động truyền thông – sáng tạo nội dung của Techcombank một cách tự động, minh bạch và có thể mở rộng.
    

# 2. Mô tả

**Techcombank Influencer Platform** là nền tảng công nghệ được **AccessTrade (AT)** phát triển và vận hành theo yêu cầu, chính sách và tiêu chuẩn kỹ thuật do **Techcombank (TCB)** đề ra.

Hệ thống hỗ trợ triển khai các chương trình truyền thông, giúp Techcombank hợp tác với cộng đồng Influencer nhằm lan tỏa thông điệp thương hiệu và khuyến khích sáng tạo nội dung về sản phẩm, dịch vụ của ngân hàng.

Trong mô hình vận hành:

- **Techcombank (TCB)** giữ vai trò **chủ sở hữu và định hướng tổng thể**.
    
    TCB xây dựng yêu cầu, mục tiêu và chính sách chiến dịch; tiếp nhận báo cáo vận hành từ AT; và **duyệt chi ngân sách** cho các chương trình sau khi AT hoàn tất đối soát.
    
    TCB **không trực tiếp thao tác hoặc thanh toán cho Influencer**, mà chỉ **chuyển khoản cho AT** theo kết quả đã được duyệt.
    
- **AccessTrade (AT)** là **đơn vị vận hành chính** của nền tảng.
    
    AT phát triển, quản trị hệ thống, vận hành chiến dịch, phê duyệt nội dung, tính toán hoa hồng, **thực hiện đối soát và báo cáo định kỳ cho TCB** (bao gồm kết quả chiến dịch và tổng số tiền hoa hồng cần chi trả).
    
    Sau khi TCB phê duyệt và thanh toán, AT sẽ **chi trả hoa hồng cho từng Influencer**
    
- **Influencer** là **người dùng cuối** của hệ thống.
    
    Influencer đăng ký, liên kết tài khoản mạng xã hội, tham gia các chiến dịch, đăng nội dung và nhận hoa hồng do AT chi trả.
    
- **3rd Party Provider** là **đơn vị cung cấp dịch vụ kỹ thuật phụ trợ**, như phân tích dữ liệu mạng xã hội, CDN hoặc cloud, hỗ trợ hệ thống trong việc xác minh danh tính và thống kê hiệu quả nội dung.

Cấu trúc kỹ thuật hệ thống bao gồm:

1. **Cổng Influencer (Web/App):** nơi Influencer đăng ký, tham gia chiến dịch và theo dõi hoa hồng.
2. **Cổng quản trị (Admin Panel):** dành cho đội vận hành AT để quản lý chiến dịch, duyệt nội dung, đối soát và lập báo cáo cho TCB.
3. **Dịch vụ nền (Backend/API):** đảm nhận xử lý nghiệp vụ, lưu trữ dữ liệu và kết nối đến các dịch vụ kỹ thuật bên thứ ba.

# **3. Mô hình vận hành và đối tượng sử dụng**

## **3.1 Tổng quan**

Techcombank Influencer Platform được vận hành theo mô hình **“Techcombank định hướng – AccessTrade vận hành – Creator tham gia”**.

Toàn bộ quy trình kỹ thuật và vận hành do AccessTrade chịu trách nhiệm triển khai, còn Techcombank đóng vai trò định hướng, kiểm soát và theo dõi thông qua báo cáo hệ thống.

---

## **3.2 Vai trò và phạm vi sử dụng**

| Bên tham gia | Vai trò | Phạm vi trách nhiệm |
| --- | --- | --- |
| **Techcombank (TCB)** | Chủ sở hữu và đơn vị định hướng | - Xây dựng yêu cầu, nội dung và chính sách chiến dịch.
- Giám sát hiệu quả thông qua báo cáo định kỳ của AT.
- **Duyệt chi và chuyển ngân sách cho AT** dựa trên báo cáo đối soát đã xác nhận.
- Không trực tiếp thao tác hoặc chi trả cho Influencer. |
| **AccessTrade (AT)** | Đơn vị phát triển và vận hành chính | - Phát triển, bảo trì và quản trị hệ thống.
- Cấu hình chiến dịch, phê duyệt nội dung, tính toán hoa hồng.
- **Thực hiện đối soát và báo cáo định kỳ cho TCB** (bao gồm kết quả, ngân sách và số tiền hoa hồng).
- **Nhận ngân sách từ TCB và chi trả hoa hồng cho Influencer**.
- Quản lý dữ liệu, người dùng và tích hợp dịch vụ kỹ thuật bên thứ ba. |
| **Influencer** | Người tham gia chương trình dưới dạng cộng tác viên | - Đăng ký tài khoản, liên kết mạng xã hội (TikTok, YouTube, v.v.).
- Tham gia thử thách, đăng nội dung, theo dõi kết quả và **nhận hoa hồng từ AT**.
- Tuân thủ điều khoản sử dụng và chính sách vận hành công bố bởi AT. |
| **3rd Party Provider** | Nhà cung cấp dịch vụ kỹ thuật | - Cung cấp API, dữ liệu và hạ tầng (eKYC, social data, CDN, cloud).
- Hỗ trợ xác minh dữ liệu và thống kê hiệu quả nội dung.
- Không truy cập trực tiếp giao diện hệ thống hoặc dữ liệu người dùng. |

## **3.3 Sơ đồ mô hình vận hành**

![diagram (3).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(3).svg)

---

## **3.4 Nguyên tắc vận hành tổng quát**

1. **Techcombank (TCB)** giữ vai trò **định hướng và giám sát tổng thể**, không trực tiếp thao tác hoặc xử lý dữ liệu người dùng.
2. **AccessTrade (AT)** là **đơn vị vận hành duy nhất**, chịu trách nhiệm toàn bộ về kỹ thuật, nội dung và thanh toán trong hệ thống.
3. **Influencer** tham gia chương trình theo **thỏa thuận điện tử (Terms of Use)** ký kết với AT, và nhận hoa hồng từ AT theo chính sách công khai.
4. **3rd Party Provider** cung cấp dịch vụ kỹ thuật theo **hợp đồng riêng với AT**, không có quan hệ pháp lý trực tiếp với TCB.

# II. Yêu cầu chức năng

Hệ thống Techcombank Influencer Platform bao gồm hai nhóm người dùng chính:

- **Influencer** – người tham gia các chiến dịch truyền thông, đăng ký, đăng nội dung và nhận hoa hồng.
- **Admin** – nhóm quản trị hệ thống, bao gồm **Admin của AccessTrade (AT)** và **Admin của Techcombank (TCB)**.

Trong đó

- **Admin – AT** chịu trách nhiệm vận hành, cấu hình chiến dịch, phê duyệt nội dung, đối soát và chi trả hoa hồng.
- **Admin – TCB** có quyền truy cập ở chế độ giám sát, xem báo cáo, phê duyệt ngân sách và theo dõi kết quả chiến dịch.

Phần mô tả chức năng bên dưới thể hiện các nghiệp vụ ở góc độ **Admin nói chung**, với quyền hạn cụ thể được áp dụng linh hoạt theo từng nhóm người dùng thực tế.

# 1. Đăng nhập bằng Google / TikTok

## Mục tiêu

Cho phép người dùng truy cập vào hệ thống bằng tài khoản Google hoặc TikTok, không cần tạo tài khoản thủ công.

Đảm bảo tính xác thực, bảo mật và tuân thủ quy định về dữ liệu cá nhân.

## Phạm vi áp dụng

- Nền tảng: giao diện ứng dụng người dùng

## Luồng nghiệp vụ

### Các bước thực hiện

1. **Người dùng** chọn một trong hai tùy chọn:
    - Đăng nhập bằng Google
    - Đăng nhập bằng TikTok
2. **Ứng dụng** gửi yêu cầu xác thực OAuth đến máy chủ của Google hoặc TikTok.
3. **Nền tảng Google/TikTok** hiển thị màn hình xin quyền truy cập các thông tin cơ bản như:
    - Email
    - Tên hiển thị
    - Ảnh đại diện (avatar)
4. **Người dùng** đồng ý cấp quyền cho ứng dụng.
5. **Google/TikTok** trả về **Authorization Code** cho ứng dụng.
6. **Frontend** gửi **Authorization Code** đến **Backend** của hệ thống.
7. **Backend** gửi mã này đến API của Google/TikTok để **đổi lấy Access Token**.
8. Sau khi nhận được **Access Token**, **Backend** sử dụng token này để lấy **thông tin người dùng** (email, tên, avatar).
9. **Backend** kiểm tra trong cơ sở dữ liệu:
    - Nếu người dùng đã tồn tại → tiến hành đăng nhập.
    - Nếu người dùng chưa tồn tại → tạo tài khoản mới với thông tin từ Google/TikTok.
10. **Backend** tạo **session** hoặc **JWT token** để duy trì trạng thái đăng nhập.
11. **Frontend** nhận phản hồi đăng nhập thành công và chuyển người dùng về giao diện chính của hệ thống.

---

## Sơ đồ luồng

![diagram.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram.svg)

## Dữ liệu người dùng liên quan

| Trường dữ liệu | Nguồn | Mục đích | Lưu trữ | Ghi chú bảo mật |
| --- | --- | --- | --- | --- |
| `provider_user_id` | OAuth | Nhận diện duy nhất người dùng theo nền tảng
Dùng để định danh tài khoản | DB | Dạng hash |
| `provider` | Hệ thống | Quản lý loại đăng nhập | DB | “google” hoặc “tiktok” |
| `email` | Google/TikTok |  | DB | Không chia sẻ với bên thứ ba |
| `display_name` | Google/TikTok | Hiển thị thông tin cá nhân | DB | Cho phép người dùng chỉnh sửa |
| `avatar_url` | Google/TikTok | Hiển thị ảnh đại diện | DB | Có thể xóa hoặc cập nhật |
| `access_token` | OAuth | Xác thực 1 lần với Google/TikTok | Không lưu | Dùng tạm thời (1 lần) |

## Bảo mật và quyền riêng tư

- Không lưu `access_token` sau khi đăng nhập thành côngý.
- Khi người dùng xóa tài khoản, toàn bộ dữ liệu liên kết OAuth bị xóa.
- Tuân thủ **Nghị định 13/2023 (VN)** và **GDPR (EU)** về xử lý dữ liệu cá nhân.

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Người dùng từ chối cấp quyền | OAuth trả về lỗi `access_denied` | Hiển thị thông báo và dừng tiến trình |
| OAuth trả về lỗi timeout / invalid_token | Token hết hạn hoặc không hợp lệ | Hiển thị thông báo “Phiên đăng nhập thất bại” |
| Backend không kết nối được với OAuth server | Sự cố mạng hoặc rate limit | Retry tối đa 3 lần, sau đó thông báo lỗi hệ thống |

# 2. Cập nhật thông tin hồ sơ cá nhân

## Mục tiêu

Cho phép người dùng xem và cập nhật thông tin cá nhân của tài khoản, bao gồm họ tên, giới tính, ngày sinh, ảnh đại diện và email.

Hệ thống phải đảm bảo tính toàn vẹn, bảo mật dữ liệu và xác thực thông tin đầu vào.

## Phạm vi áp dụng

- Áp dụng cho người dùng sau khi đã đăng nhập.
- Giao diện nằm trong phần “Thông tin tài khoản” hoặc “Hồ sơ cá nhân”.
- Các trường thông tin đều có thể chỉnh sửa

## Luồng nghiệp vụ

### Các bước thực hiện

1. **Người dùng** truy cập trang “Thông tin tài khoản”.
2. **Hệ thống** hiển thị các thông tin cá nhân hiện tại, bao gồm:
    - Ảnh đại diện
    - Tên hiển thị
    - Giới tính
    - Ngày sinh
    - Email
3. **Người dùng** có thể:
    - Tải lên ảnh đại diện mới.
    - Sửa tên hiển thị.
    - Chọn lại giới tính.
    - Cập nhật ngày sinh.
    - Thay đổi email
4. Khi nhấn nút **“Lưu thay đổi”**:
    - Frontend gửi yêu cầu cập nhật đến API
    - Backend kiểm tra các điều kiện hợp lệ:
        - Tên và email không được để trống.
        - Định dạng email hợp lệ.
        - Nếu có cập nhật ảnh, chỉ chấp nhận định dạng JPG/PNG, dung lượng ≤ 5MB.
5. **Backend** lưu thông tin vào cơ sở dữ liệu.
6. **Hệ thống** trả phản hồi thành công và hiển thị thông báo “Cập nhật thành công”.

## Sơ đồ luồng

![diagram (4).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(4).svg)

## Quy tắc và ràng buộc dữ liệu

| Trường | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| --- | --- | --- | --- |
| Ảnh đại diện | File (JPG, PNG) | Không | Giới hạn 5MB |
| Tên hiển thị | Text | Có | Không để trống |
| Giới tính | Enum (`Nam`, `Nữ`, `Khác`) | Không | Tùy chọn |
| Ngày sinh | Date (`dd/mm/yyyy`) | Không | Không bắt buộc nhập |
| Email | Text (định dạng email) | Có |  |

---

## Bảo mật và quyền riêng tư

- Tuân thủ **Nghị định 13/2023 (VN)** và **GDPR (EU)** về xử lý dữ liệu cá nhân.

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Thiếu tên hoặc email | Người dùng để trống trường bắt buộc | Hiển thị thông báo lỗi và không cho lưu |
| Email không hợp lệ | Sai định dạng email | Hiển thị lỗi “Email không hợp lệ” |
| Ảnh đại diện quá lớn | File vượt quá 5MB hoặc sai định dạng | Hiển thị lỗi upload |

# 3. Đăng ký kênh social

## **Mục tiêu**

Cho phép người dùng đăng ký và xác thực hồ sơ mạng xã hội (social profile) trước khi tham gia thử thách, nhằm đảm bảo hệ thống ghi nhận đúng thông tin kênh và xác định đủ điều kiện tham gia.

## **Phạm vi áp dụng**

- Áp dụng cho người dùng đã đăng nhập và hoàn tất hồ sơ cá nhân.
- Triển khai trên nền tảng website dành cho Influencer.
- Hỗ trợ 5 nền tảng mạng xã hội: TikTok, YouTube, Facebook, Instagram, Threads.

Người dùng có thể đăng ký một hoặc nhiều hồ sơ social khác nhau, mỗi hồ sơ được xác thực và duyệt độc lập theo quy trình tương ứng của từng nền tảng.

## 3.1. Đăng ký hồ sơ **TikTok**

### **Luồng nghiệp vụ**

- Người dùng chọn **TikTok** trong danh sách nền tảng.
- **Hệ thống hiển thị hướng dẫn đăng ký TikTok**, bao gồm:
    - Bước xác thực qua OAuth 2.0.
    - Thông báo rằng hệ thống sẽ tự động lấy thông tin kênh sau khi người dùng cấp quyền.
- Hệ thống chuyển hướng sang trang xác thực OAuth 2.0 của TikTok.
- Người dùng đăng nhập TikTok và cấp quyền truy cập thông tin kênh.
- TikTok trả về `Authorization Code`.
- Ứng dụng gửi mã này đến Backend để đổi lấy `Access Token`.
- Backend dùng token để gọi API TikTok, lấy các thông tin:
    - Tên kênh
    - ID kênh
    - Ảnh đại diện
    - Số lượng người theo dõi
- Hệ thống kiểm tra điều kiện hợp lệ (ví dụ: ≥ X followers).
- Nếu đạt → lưu hồ sơ với trạng thái **“Đã duyệt (APPROVED)”**.
- Nếu không đạt → lưu hồ sơ với trạng thái **“Không hợp lệ (REJECTED)”** và thông báo cho người dùng

### **Sơ đồ luồng**

![diagram (1).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(1).svg)

## 3.2. Đăng ký hồ sơ **YouTube**

### **Luồng nghiệp vụ**

- Người dùng chọn **YouTube** trong danh sách nền tảng.
- **Hệ thống hiển thị hướng dẫn đăng ký YouTube**, bao gồm:
    - Nhập đường dẫn đến kênh YouTube của người dùng (ví dụ: `https://www.youtube.com/@username`).
    - **Yêu cầu thêm hashtag định danh** do chương trình quy định (ví dụ: `#TCB_xxxxx`) vào phần mô tả kênh.
- Người dùng nhập **đường dẫn kênh YouTube**.
- Backend tiếp nhận link và tự động thu thập thông tin công khai từ YouTube API (metadata):
    - Tên kênh
    - ID kênh
    - Ảnh đại diện
    - Số lượng người theo dõi
- Hệ thống kiểm tra điều kiện hợp lệ (ví dụ: ≥ X followers).
- Hệ thống trả kết quả **ngay lập tức** cho người dùng:
    - Hợp lệ → “Đã duyệt (APPROVED)”
    - Không hợp lệ → “Không hợp lệ (REJECTED)” kèm lý do.

### **Sơ đồ luồng**

![diagram (2).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(2).svg)

## 3.3. Đăng ký hồ sơ **Facebook / Instagram / Threads**

### **Luồng nghiệp vụ**

- Người dùng chọn nền tảng (Facebook, Instagram, hoặc Threads).
- **Hệ thống hiển thị hướng dẫn đăng ký**, bao gồm:
    - Nhập đường dẫn đến hồ sơ hoặc trang cá nhân.
    - **Bắt buộc thêm hashtag định danh** (ví dụ: `#AT_xxxxx`) vào phần mô tả hồ sơ để xác minh quyền sở hữu.
- Người dùng nhập **đường dẫn hồ sơ cá nhân hoặc trang**.
- Backend lưu hồ sơ với trạng thái ban đầu là **“Đang chờ duyệt (PENDING)”**.
- Hệ thống thực hiện kiểm duyệt **thủ công hoặc bán tự động** sau:
    - Crawl hồ sơ → kiểm tra sự tồn tại của hashtag cá nhân.
    - Kiểm tra số lượng người theo dõi ≥ X.
- Kết quả được cập nhật **chậm nhất sau 01 ngày làm việc**.
- Sau khi duyệt:
    - Hợp lệ → “Đã duyệt (APPROVED)”
    - Không hợp lệ → “Không hợp lệ (REJECTED)” kèm lý do.

### **Sơ đồ luồng**

![diagram (3).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(3)%201.svg)

## Quy tắc và ràng buộc dữ liệu

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| --- | --- | --- | --- |
| Nền tảng | Enum (TIKTOK, YOUTUBE, FACEBOOK, INSTAGRAM, THREADS) | Có | Lựa chọn 1 trong 5 nền tảng hỗ trợ |
| URL hồ sơ | Text (URL) | Có | Bắt buộc với tất cả trừ TikTok |
| Hashtag cá nhân | Text | Có (với YouTube, Facebook, Instagram, Threads) | Dùng để xác minh quyền sở hữu |
| Follower count | Number | Tự động lấy (TikTok, YouTube) / kiểm duyệt sau (khác) | Phải ≥ X followers |
| Trạng thái duyệt | Enum (PENDING, APPROVED, REJECTED) | Có | Do hệ thống xác định |

### Bảo mật và quyền riêng tư

- Không lưu `access_token` TikTok sau khi xác thực.
- Thông tin hồ sơ được lưu ở dạng link và metadata, không chứa nội dung bài viết.
- Toàn bộ thao tác duyệt và cập nhật trạng thái được ghi log (thời gian, user_id, platform, hành động).
- Tuân thủ Nghị định 13/2023 (VN) và GDPR (EU) về xử lý dữ liệu cá nhân.

### Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Thiếu thông tin bắt buộc | Người dùng chưa chọn nền tảng hoặc chưa nhập URL | Hiển thị thông báo lỗi và yêu cầu bổ sung |
| OAuth thất bại (TikTok) | Người dùng từ chối hoặc lỗi xác thực | Hiển thị thông báo “Xác thực TikTok thất bại” |
| Thiếu hashtag định danh | Hồ sơ thiếu hashtag yêu cầu | Hiển thị cảnh báo và yêu cầu chỉnh sửa mô tả |
| Follower count không đủ | Hồ sơ chưa đạt ngưỡng tối thiểu | Hiển thị thông báo “Kênh chưa đủ điều kiện tham gia” |
| Link hồ sơ không hợp lệ | URL sai định dạng hoặc không truy cập được | Hiển thị thông báo lỗi và chặn lưu |

# 4. Tham gia thử thách

## Mục tiêu

Cho phép người dùng gửi bài dự thi (bài đăng, video, nội dung tham gia) cho một thử thách cụ thể, nhằm ghi nhận lượt tham gia, theo dõi kết quả và tính hoa hồng theo quy định của chương trình.

## Phạm vi áp dụng

- Áp dụng cho người dùng đã đăng nhập và có ít nhất **một hồ sơ social hợp lệ (đã duyệt)**.
- Người dùng chỉ có thể tham gia thử thách còn trong thời gian đăng ký.
- Áp dụng cho tất cả nền tảng đã hỗ trợ: TikTok, YouTube, Facebook, Instagram, Threads.

## Luồng nghiệp vụ

- Người dùng truy cập trang chi tiết thử thách.
- Hệ thống hiển thị thông tin thử thách:
    - Mô tả, thể lệ, thời gian bắt đầu – kết thúc.
    - Các yêu cầu cụ thể về hashtag, định dạng bài đăng, hoặc nền tảng bắt buộc (nếu có).
- Người dùng nhấn “**Tham gia thử thách**”.
- **Hệ thống hiển thị danh sách các hồ sơ social đã được duyệt.**
    - Người dùng chọn **một hồ sơ** phù hợp để tham gia (ví dụ: kênh TikTok đã duyệt).
    - Nếu người dùng chưa có hồ sơ nào được duyệt → hệ thống hiển thị thông báo “Vui lòng đăng ký và chờ duyệt hồ sơ social trước khi tham gia thử thách”.
- Người dùng nhập link video muốn tham gia tương ứng với hồ sơ đã chọn
- Hệ thống kiểm tra:
    - Link hợp lệ, truy cập được.
    - Nền tảng của bài đăng trùng với hồ sơ đã chọn.
    - Có chứa hashtag bắt buộc của chương trình (ví dụ: #AT_Challenge).
- Nếu hợp lệ → lưu bài tham gia vào hệ thống, gán trạng thái **“Đang chờ duyệt (PENDING)”**.
- Bộ phận kiểm duyệt hoặc hệ thống tự động xác thực nội dung (qua API hoặc crawler).
- Sau khi duyệt:
    - Hợp lệ → cập nhật trạng thái **“Đã duyệt (APPROVED)”** và bắt đầu tính thống kê (view, like, comment…).
    - Không hợp lệ → **“Từ chối (REJECTED)”**, hiển thị lý do cho người dùng.

# Sơ đồ luồng

![diagram (4).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(4)%201.svg)

## **Quy tắc và ràng buộc dữ liệu**

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| --- | --- | --- | --- |
| Thử thách ID | UUID | Có | Thử thách mà người dùng tham gia |
| Hồ sơ social ID | UUID | Có | Phải có trạng thái “APPROVED” |
| URL bài dự thi | Text (URL) | Có | Đường dẫn hợp lệ tới bài đăng |
| Nền tảng | Enum (TIKTOK, YOUTUBE, FACEBOOK, INSTAGRAM, THREADS) | Có | Phải trùng với hồ sơ social |
| Hashtag bắt buộc | Text | Có | Kiểm tra tồn tại trong bài đăng |
| Trạng thái bài tham gia | Enum (PENDING, APPROVED, REJECTED) | Có | Do hệ thống xác định |
| Thời gian tham gia | Datetime | Có | Ghi nhận lúc người dùng gửi bài |

## **Bảo mật và quyền riêng tư**

- Chỉ lưu metadata bài dự thi (URL, thời gian, trạng thái, thống kê cơ bản).
- Không lưu nội dung bài đăng gốc hoặc dữ liệu riêng tư người dùng.
- Thao tác kiểm duyệt, phê duyệt được log chi tiết (user_id, staff_id, timestamp).
- Tuân thủ quy định về bảo vệ dữ liệu cá nhân (Nghị định 13/2023, GDPR).

## **Các kịch bản lỗi**

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có hồ sơ social được duyệt | Người dùng chưa đăng ký hoặc đang chờ duyệt hồ sơ | Hiển thị thông báo và chặn gửi bài |
| Link bài dự thi không hợp lệ | Sai định dạng hoặc không truy cập được | Hiển thị cảnh báo và yêu cầu nhập lại |
| Hashtag bắt buộc không tồn tại | Bài đăng thiếu hashtag quy định | Hiển thị lỗi và hướng dẫn chỉnh sửa |
| Nền tảng không khớp | Hồ sơ đã chọn không cùng nền tảng với bài đăng | Hiển thị thông báo “Chọn đúng hồ sơ tương ứng nền tảng” |
| Hết thời gian tham gia | Thử thách đã kết thúc | Ẩn nút “Tham gia thử thách” và hiển thị thông báo |
| Lỗi hệ thống / kết nối | Backend không phản hồi | Hiển thị “Lỗi kết nối, vui lòng thử lại sau” |

# 5. Theo dõi thử thách đã tham gia

## Mục tiêu

Cho phép người dùng xem lại toàn bộ thông tin về các thử thách đã tham gia, bao gồm danh sách thử thách, video đã gửi, trạng thái hợp lệ, và các mốc hoa hồng đã đạt được.

Hệ thống giúp người dùng dễ dàng theo dõi tiến độ, đối chiếu kết quả và quản lý lịch sử tham gia thử thách.

## Phạm vi áp dụng

Chức năng áp dụng cho người dùng đã đăng nhập trên nền tảng web, sau khi hoàn tất đăng ký tham gia ít nhất một thử thách.

## Luồng nghiệp vụ

- Người dùng truy cập trang **Thử thách của tôi**.
- Hệ thống hiển thị danh sách các thử thách mà người dùng đã tham gia.
- Người dùng chọn một thử thách để xem chi tiết.
- Hệ thống hiển thị:
    - Thông tin thử thách (tên, thời gian, trạng thái).
    - Danh sách video đã gửi tham gia.
    - Thông số của từng video (link, lượt xem, lượt tương tác, trạng thái hợp lệ).
    - Các mốc hoa hồng mà người dùng đã đạt được.

## Sơ đồ luồng

![TheoDoiThuThach.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/TheoDoiThuThach.svg)

## Bảo mật và quyền riêng tư

- Chỉ người dùng đã đăng nhập mới có thể truy cập thông tin thử thách của chính họ.
- Hệ thống không lưu nội dung video, chỉ lưu link và metadata.
- Các hoạt động truy cập được ghi log để phục vụ kiểm tra khi cần thiết.

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có thử thách nào đã tham gia | Người dùng chưa từng gửi video tham gia thử thách | Hiển thị thông báo “Bạn chưa tham gia thử thách nào” |
| Lỗi lấy danh sách thử thách | Backend hoặc cơ sở dữ liệu không phản hồi | Hiển thị thông báo “Không thể tải danh sách, vui lòng thử lại sau” |

# 6. Cập nhật thông số video định kỳ

## Mục tiêu

Tự động thu thập và cập nhật số liệu thống kê (views, reactions) cho các video mà người dùng đã gửi tham gia thử thách, nhằm phục vụ việc tính điểm, xếp hạng và hoa hồng.

## Phạm vi áp dụng

Chức năng chạy nền trên hệ thống backend, không có giao diện người dùng.

Áp dụng cho tất cả các video hợp lệ của các thử thách còn hiệu lực.

## Luồng nghiệp vụ

- Hệ thống lập lịch thực thi (cron job) **nhiều lần trong ngày. H**ệ thống tự động xác định khung giờ phù hợp để tránh quá tải hoặc trùng tác vụ và vẫn đảm bảo mỗi video được lấy thông số ít nhất 2 lần mỗi ngày
- Backend lấy danh sách các video cần cập nhật thống kê.
- Backend gửi yêu cầu đến **Video Metadata Service (AccessTrade)** để lấy dữ liệu mới nhất.
- Dịch vụ trả về thông tin: lượt xem (views), lượt tương tác (reactions).
- Backend ghi log lại kết quả của lượt truy vấn (bao gồm thời gian, video ID, kết quả trả về).
- Backend cập nhật thông số vào cơ sở dữ liệu video.
- Hệ thống đồng thời cập nhật các bảng báo cáo thống kê: **daily**, **weekly**, và **monthly report tracking**.

## Sơ đồ luồng

![CapNhatThongSoView.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/CapNhatThongSoView.svg)

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có video cần cập nhật | Không có video thỏa điều kiện | Ghi log và kết thúc tác vụ |
| Dịch vụ Video Metadata không phản hồi | Không thể lấy thông tin video | Retry 3 lần, sau đó ghi log lỗi, Alert cho admin |
| Dữ liệu trả về rỗng hoặc sai định dạng | Không có trường view/reaction | Bỏ qua video đó và ghi log cảnh báo |

# 7. Tính hoa hồng định kỳ

## Mục tiêu

Tự động tính toán hoa hồng của người dùng dựa trên hiệu suất và kết quả của các video đã gửi tham gia thử thách.

Hệ thống đảm bảo mỗi video được kiểm tra ít nhất **2 lần mỗi ngày** để đảm bảo tính chính xác của dữ liệu hoa hồng.

## Phạm vi áp dụng

Chức năng chạy ngầm trên hệ thống **backend**, không có giao diện người dùng.

Áp dụng cho các video hợp lệ trong các thử thách còn hoạt động và có cơ cấu hoa hồng được định nghĩa.

## Luồng nghiệp vụ

- Hệ thống lập lịch thực thi (cron job) **nhiều lần trong ngày. H**ệ thống tự động xác định khung giờ phù hợp để tránh quá tải hoặc trùng tác vụ và vẫn đảm bảo mỗi video được xử lý ít nhất 2 lần mỗi ngày
- Backend lấy danh sách tất cả các thử thách có **cơ cấu hoa hồng** (reward structure).
- Backend lấy danh sách video hợp lệ thuộc các thử thách đó.
- Hệ thống **so khớp video với cơ cấu hoa hồng** để xác định điều kiện đạt hoa hồng.
- Nếu video thỏa điều kiện: hệ thống tính hoa hồng tương ứng và cập nhật vào cơ sở dữ liệu.
- Nếu không thỏa điều kiện: ghi nhận trạng thái “chưa đạt”.
- Tất cả kết quả tính toán đều được ghi log để phục vụ kiểm tra và truy vết.

## Sơ đồ luồng

![TinhThuongDinhKy.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/TinhThuongDinhKy.svg)

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có thử thách hợp lệ | Không tìm thấy cơ cấu hoa hồng đang hoạt động | Ghi log và kết thúc job |
| Không có video hợp lệ | Không có video thỏa điều kiện kiểm tra | Ghi log và bỏ qua |
| Lỗi khi so khớp video với thử thách | Dữ liệu bị thiếu hoặc sai liên kết | Ghi log lỗi và bỏ qua video đó |
| Lỗi tính toán giá trị hoa hồng | Quy tắc hoa hồng không hợp lệ hoặc dữ liệu không đủ | Ghi log lỗi và alert cho admin |

# 8. Duyệt / Hủy hồ sơ social

## **Mục tiêu**

Cho phép quản trị viên xem danh sách các hồ sơ social đã đăng ký và thực hiện duyệt hoặc hủy (reject) những hồ sơ không đạt yêu cầu, nhằm đảm bảo chỉ các hồ sơ hợp lệ được phép tham gia thử thách.

## **Phạm vi áp dụng**

- Áp dụng cho **Admin** có quyền quản lý người dùng và hồ sơ social.
- Áp dụng với tất cả các nền tảng mạng xã hội: TikTok, YouTube, Facebook, Instagram, Threads.
- Hồ sơ ở trạng thái `PENDING` có thể được duyệt hoặc từ chối.
- Hồ sơ ở trạng thái `APPROVED` có thể bị hủy duyệt (`REJECTED`) khi phát hiện vi phạm.

## **Luồng nghiệp vụ**

1. Quản trị viên truy cập trang “Quản lý hồ sơ social”.
2. Hệ thống hiển thị danh sách hồ sơ đã đăng ký, gồm các thông tin:
    - Người tạo (Creator)
    - Nền tảng
    - Tên hồ sơ / đường dẫn hồ sơ
    - Hashtag định danh
    - Follower count
    - Trạng thái hiện tại (`PENDING`, `APPROVED`, `REJECTED`)
    - Thời gian đăng ký / cập nhật
3. Quản trị viên có thể lọc danh sách theo nền tảng, trạng thái, thời gian hoặc người dùng.
4. Quản trị viên chọn hồ sơ cần xử lý và thực hiện một trong các hành động sau:
    - **Duyệt hồ sơ (Approve):**
        - Kiểm tra thông tin hiển thị, xác nhận đủ điều kiện.
        - Cập nhật trạng thái `APPROVED`.
    - **Từ chối hồ sơ (Reject):**
        - Nhập lý do từ chối (bắt buộc).
        - Cập nhật trạng thái `REJECTED`.
    - **Hủy duyệt (Revoke Approval):**
        - Chỉ áp dụng với hồ sơ đã được duyệt.
        - Nhập lý do hủy (ví dụ: phát hiện vi phạm, kênh bị khóa).
        - Cập nhật trạng thái `REJECTED`.
5. Hệ thống gửi thông báo cập nhật trạng thái đến cho người dùng
6. Hệ thống lưu toàn bộ thao tác vào lịch sử hoạt động để truy xuất sau này.

## Sơ đồ luồng

![diagram (7).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(7).svg)

## **Quy tắc và ràng buộc dữ liệu**

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| --- | --- | --- | --- |
| SocialProfileID | UUID | Có | Hồ sơ được xử lý |
| Action | Enum(`APPROVE`, `REJECT`, `REVOKE`) | Có | Loại thao tác |
| Reason | Text | Có (khi từ chối / hủy duyệt) | Ghi rõ lý do |
| AdminID | UUID | Có | Người thực hiện hành động |
| UpdatedAt | Datetime | Có | Thời gian duyệt / hủy |

## **Bảo mật và quyền riêng tư**

- Chỉ Admin có vai trò hợp lệ mới được thực hiện thao tác duyệt hoặc hủy.
- Tất cả thao tác duyệt, từ chối, hủy đều được ghi lại vào **Audit Log** để truy xuất.
- Hồ sơ chỉ được hiển thị ở chế độ xem, không cho phép chỉnh sửa dữ liệu gốc.
- Hệ thống chỉ gửi thông báo về kết quả duyệt, không tiết lộ thông tin nội bộ.

## **Các kịch bản lỗi**

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Hồ sơ không tồn tại | ID không hợp lệ hoặc đã bị xóa | Hiển thị lỗi “Hồ sơ không tồn tại” |
| Không có quyền thao tác | Admin không có quyền duyệt | Hiển thị “Không có quyền thực hiện hành động này” |
| Lý do bị bỏ trống | Khi từ chối / hủy duyệt nhưng không nhập lý do | Chặn thao tác và yêu cầu nhập lý do |
| Lỗi hệ thống | Không thể cập nhật DB | Hiển thị “Thao tác không thành công, vui lòng thử lại” |

# 9. Duyệt và hủy video

## Mục tiêu

Cho phép người dùng có quyền quản trị (Admin hoặc Cộng tác viên) quản lý các video người dùng gửi lên hệ thống, bao gồm duyệt các video hợp lệ và hủy các video không đáp ứng yêu cầu.

## Phạm vi áp dụng

Áp dụng cho trang quản trị (Admin Panel).

Chỉ dành cho các tài khoản có quyền: **Admin** hoặc **Cộng tác viên (Moderator)**.

## Luồng nghiệp vụ

- Người dùng truy cập trang **Danh sách video** trong khu vực quản trị.
- Hệ thống hiển thị danh sách các video đã gửi, bao gồm thông tin cơ bản:
    - ID video, người gửi, nền tảng, link video, ngày gửi, trạng thái hiện tại.
- Người dùng có thể lọc video theo:
    - Trạng thái (chờ duyệt, đã duyệt, đã hủy).
    - Thời gian gửi bài.
    - Nền tảng (TikTok, YouTube,…).
    - Thông số (lượt xem, lượt tương tác, …).
- Người dùng có thể chọn **một hoặc nhiều video** để thao tác:
    - **Duyệt video:** chuyển trạng thái video sang “Đã duyệt”.
    - **Hủy video:** yêu cầu nhập **lý do hủy**, lưu lại lý do và cập nhật trạng thái “Đã hủy”.
- Hệ thống ghi log hành động để phục vụ kiểm tra (bao gồm người thao tác, thời gian, hành động và video liên quan).

## Sơ đồ luồng

![DuyetVideo.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/DuyetVideo.svg)

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có quyền thao tác | Người dùng không phải Admin hoặc Cộng tác viên | Hiển thị thông báo “Không có quyền truy cập” |
| Video không tồn tại | Video bị xóa hoặc không tìm thấy | Hiển thị thông báo lỗi và ghi log |

# 10. Đối soát hoa hồng

## Mục tiêu

Cho phép **Admin** thực hiện đối soát hoa hồng của người dùng tham gia thử thách.

Hệ thống hỗ trợ đối soát tự động dựa trên dữ liệu hoa hồng đã tính toán, giúp đảm bảo tính chính xác, minh bạch và giảm thao tác thủ công.

## Phạm vi áp dụng

- Áp dụng cho tài khoản có **role: Admin**.
- Thực hiện trong **giao diện quản trị (Admin Panel)**.
- Chỉ các hoa hồng **chưa được đối soát** trước đó mới được xử lý.

---

## Luồng nghiệp vụ

- Admin truy cập trang **Đối soát hoa hồng**.
- Hệ thống hiển thị danh sách các đợt đối soát trước (nếu có) và cho phép tạo mới.
- Khi **tạo mới đối soát**, Admin thực hiện:
    1. Chọn **thử thách** cần đối soát.
    2. Chọn **loại hoa hồng** (theo view / theo nhiệm vụ).
    3. Chọn **thời gian đối soát** (từ ngày – đến ngày).
- Hệ thống:
    - Lấy dữ liệu các **hoa hồng chưa được đối soát** trong phạm vi trên.
    - Tự động tính toán thống kê và hiển thị kết quả tổng hợp:
        - Tổng số user.
        - Tổng số video.
        - Tổng số tiền hoa hồng tạm tính.
- Admin có thể xem chi tiết danh sách hoa hồng
    - Admin có thể **xuất file Excel** để kiểm tra thủ công.
    - Admin có thể **chọn một hoặc nhiều hoa hồng** để xử lý:
        - **Xác nhận** → chuyển trạng thái sang “Đã xác nhận”.
        - **Hủy** → yêu cầu nhập **lý do hủy**.
- Sau khi hoàn tất xử lý, Admin có thể **kết thúc đợt đối soát**.
    - **Hệ thống khóa đợt đối soát**, không cho phép thao tác thêm.
    - **Hệ thống tự động tính toán và cập nhật số dư hoa hồn của người dùng**, bao gồm:
        - **Cộng** các khoản hoa hồng “đã xác nhận” vào mục **Hoa hồng đã đối soát** cho người dùng
    - **Cập nhật log đối soát và thay đổi số dư** để phục vụ kiểm toán.

## Sơ đồ luồng

![DoiSoatThuong.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/DoiSoatThuong.svg)

## Cấu trúc dữ liệu xuất Excel

### A. Loại hoa hồng **theo view**

| Trường | Mô tả |
| --- | --- |
| ID user | Mã người dùng |
| Tên user | Tên hiển thị của người dùng |
| ID video | Mã video tham gia |
| Link video | Đường dẫn video |
| View đầu kỳ | Số view tại thời điểm đầu kỳ đối soát |
| View trong kỳ | Số view phát sinh trong kỳ |
| View cuối kỳ | Số view cuối kỳ |
| Mốc | Mốc đạt được (theo quy định thử thách) |
| Số tiền | Số tiền tương ứng với mốc |
| Trạng thái | Đang chờ, đã xác nhận, đã hủy |
| Ghi chú | Thông tin bổ sung hoặc lý do hủy |

### B. Loại hoa hồng **theo nhiệm vụ**

| Trường | Mô tả |
| --- | --- |
| ID user | Mã người dùng |
| Tên user | Tên hiển thị |
| Số tiền | Số tiền tính theo nhiệm vụ |
| Trạng thái | Đang chờ, đã xác nhận, đã hủy |
| Ghi chú | Thông tin bổ sung hoặc lý do hủy |

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có quyền thao tác | Người dùng không phải Admin | Hiển thị thông báo “Không có quyền thực hiện” |
| Thiếu thông tin bắt buộc | Chưa chọn thử thách, loại hoa hồng hoặc thời gian | Hiển thị thông báo lỗi |
| Không có dữ liệu để đối soát | Không tìm thấy hoa hồng hợp lệ trong phạm vi chọn | Hiển thị thông báo “Không có dữ liệu để đối soát” |

# 11. Giới thiệu thông tin hợp tác giữ T-Fluencers và AccessTrade

### Mục tiêu

Khi tham gia chương trình hợp tác giữa **T-Fluencers** và **AccessTrade**, người dùng sẽ thấy một trang giới thiệu về chương trình và thông tin hợp đồng điện tử. Nếu muốn tham gia, họ chỉ cần nhấn một nút để mở **trang cộng tác viên trên AccessTrade**, nơi tất cả việc ký hợp đồng diễn ra, bao gồm **cung cấp thông tin, xác thực điện tử, xem lại và tải xuống hợp đồng**.

Người dùng **không ký hợp đồng trực tiếp trên T-Fluencers**; mọi dữ liệu ký kết đều được thực hiện và lưu trữ hoàn toàn trên **AccessTrade**. Để liên kết với tài khoản T-Fluencers, **ctv.scalef.com sẽ lưu trữ một mã định danh do T-Fluencers tạo**, giúp nhận biết user tương ứng. Sau khi ký xong, T-Fluencers sẽ nhận thông báo trạng thái hợp đồng và hiển thị kết quả phù hợp, mang đến trải nghiệm **liền mạch, an toàn và minh bạch**.

## Phạm vi áp dụng

- Trang giao diện người dùng thể hiện thông tin về hợp tác giữa T-Fluencers và AccessTrade
- Trang giao diện người dùng của AccessTrade thể hiện các luồng ký và quản trị hợp đồng điện tử

## Luồng nghiệp vụ

- Người dùng truy cập trang giới thiệu
- Trang web hiển thị đầy đủ thông tin hợp tác giữa T-Fluencers và AccessTrade, có điểm chạm để mở ra trang cộng tác viên của AccessTrade
- Người dùng được truy cập giao diện trang cộng tác viên và thực hiện các thao tác ký hợp đồng điện tử, cung cấp thông tin thanh toán,…

## Sơ đồ luồng

![diagram (5).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(5).svg)

# 12. Thanh toán cho người dùng

## Mục tiêu

Cho phép **Admin** tạo và quản lý các đợt thanh toán cho người dùng dựa trên số tiền hoa hồng đã được đối soát nhưng chưa được thanh toán.

Đảm bảo quá trình thanh toán minh bạch, có thể kiểm tra, xuất dữ liệu và lưu log giao dịch.

## Phạm vi áp dụng

- Áp dụng cho người dùng có vai trò **Admin**.
- Triển khai trên hệ thống **Admin Panel**.

## Luồng nghiệp vụ

- Admin truy cập trang **Thanh toán cho người dùng**.
- Hệ thống hiển thị danh sách các đợt thanh toán đã được tạo (nếu có) và cho phép **tạo mới đợt thanh toán**.
- Khi tạo mới:
    - Hệ thống tự động tổng hợp danh sách người dùng có **số tiền hoa hồng chưa được thanh toán** (đã đối soát).
    - Hệ thống hiển thị thông tin tổng hợp gồm:
        - Tổng số người dùng.
        - Tổng số hoa hồng.
        - Tổng tiền cần thanh toán.
- Admin có thể **xem chi tiết danh sách thanh toán** hoặc **tải file Excel** bao gồm:
    - ID user
    - Tổng tiền hoa hồng cần thanh toán
    - Trạng thái
    - Ghi chú
- Admin có thể lựa chọn **một hoặc nhiều dòng thanh toán** để thao tác:
    - **Xác nhận thanh toán** → chuyển trạng thái sang “Đã thanh toán”.
    - **Hủy thanh toán** → nhập **lý do hủy**.
- Sau khi hoàn tất xử lý, Admin có thể **kết thúc đợt thanh toán**.
    - Khi kết thúc:
        1. **Hệ thống khóa đợt thanh toán**, không cho phép thao tác thêm.
        2. **Hệ thống tự động** cập nhật số tiền **chưa thanh toán** và **đã thanh toán** trong thông số của người dùng
        3. **Lưu log chi tiết giao dịch thanh toán** để phục vụ kiểm toán và báo cáo tài chính.
- Hệ thống ghi nhận thông tin người thao tác và thời điểm hoàn tất thanh toán.

## Sơ đồ luồng

![ThanhToan.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/ThanhToan.svg)

## Bảo mật và quyền riêng tư

- Chỉ **Admin** có quyền tạo hoặc kết thúc đợt thanh toán.
- Tất cả thao tác được ghi log chi tiết (user thao tác, thời gian, hành động).
- Thông tin tài khoản ngân hàng chỉ hiển thị ở cấp quản trị, không chia sẻ ra ngoài.

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Không có dữ liệu hoa hồng cần thanh toán | Không tìm thấy người dùng nào có hoa hồng chưa thanh toán | Hiển thị thông báo “Không có dữ liệu để thanh toán” |
| Hủy thanh toán không nhập lý do | Admin không nhập lý do khi hủy | Hiển thị thông báo lỗi yêu cầu nhập lý do |

# 13. Quản lý file dữ liệu

## Mục tiêu

Cho phép **Admin** tải xuống các file dữ liệu (file đối soát, file thanh toán) dưới dạng **Excel**.

Hệ thống đảm bảo quá trình tạo file diễn ra an toàn, có trạng thái rõ ràng, và link tải xuống được bảo mật.

## Phạm vi áp dụng

- Áp dụng cho người dùng có **vai trò Admin**.
- Hoạt động trên hệ thống **Admin Panel**.
- File được sinh ra từ dữ liệu trong hệ thống (đối soát hoặc thanh toán).
- Các file sau khi được tạo có thể truy cập lại từ danh sách quản lý file.

## Luồng nghiệp vụ

- Admin thực hiện thao tác **tải file dữ liệu** (ví dụ: file đối soát hoặc file thanh toán).
- Hệ thống tạo một **lượt tạo file** mới với trạng thái ban đầu là **“Đang tạo”**.
- Hệ thống chạy **tiến trình nền (background job)** để:
    - Truy vấn dữ liệu cần xuất.
    - Tạo file Excel tương ứng.
    - Lưu file vào hệ thống lưu trữ nội bộ
    - Cập nhật trạng thái request thành **“Thành công”** khi hoàn tất.
- Admin có thể truy cập trang **Danh sách file dữ liệu** để xem:
    - Loại file (Đối soát / Thanh toán).
    - Ngày tạo.
    - Người tạo.
    - Trạng thái file (Đang tạo / Thành công / Lỗi).
- Khi file ở trạng thái **“Thành công”**, Admin có thể chọn **Tải về**.
- Khi tải:
    - Hệ thống tạo **link tải file bảo mật**, chỉ có hiệu lực trong **30 giây**.
    - Hệ thống ghi log thao tác tải file (user, thời điểm, IP).
- Khi hết thời gian hiệu lực, link tải tự động vô hiệu hóa, cần tạo lại nếu muốn tải tiếp.

## Sơ đồ luồng

![QuanLyFile.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/QuanLyFile.svg)

## Bảo mật và quyền riêng tư

- Chỉ **Admin** được phép truy cập và tải các file dữ liệu.
- Link tải file có hiệu lực **30 giây**, sau đó tự động hết hạn.
- Dữ liệu file chứa thông tin nhạy cảm (user, video, hoa hồng), chỉ dùng nội bộ.
- Hệ thống ghi log chi tiết mọi thao tác tạo và tải file.
- Các file được lưu trữ an toàn, không công khai ra bên ngoài.

## Các kịch bản lỗi

| Tình huống | Mô tả | Hành động hệ thống |
| --- | --- | --- |
| Lỗi khi tạo file | Quá trình tạo file thất bại do lỗi dữ liệu hoặc server | Cập nhật trạng thái “Lỗi”, hiển thị thông báo thất bại |
| Tải file khi file chưa sẵn sàng | File vẫn đang ở trạng thái “Đang tạo” | Hiển thị thông báo “File đang được tạo, vui lòng thử lại sau” |
| Link tải hết hạn | Link tải vượt quá thời gian hiệu lực | Hiển thị thông báo “Link đã hết hạn, vui lòng tạo lại link tải” |
| Không có quyền tải | Người dùng không có quyền Admin | Hiển thị thông báo “Bạn không có quyền truy cập file này” |

# 14. Quản lý ngân sách thử thách

## **Mục tiêu**

Cho phép Admin cấu hình và theo dõi ngân sách của từng chiến dịch/thử thách.

Hệ thống tự động giám sát mức sử dụng ngân sách dựa trên tổng hoa hồng đã đối soát hoặc đã chi trả. Khi đạt các mốc quy định, hệ thống gửi cảnh báo và thực hiện giới hạn thao tác tương ứng, nhằm đảm bảo chiến dịch không vượt quá ngân sách được duyệt.

## Phạm vi áp dụng

Triển khai trên **hệ thống Admin Panel**

Tác vụ giám sát được chạy tự động trên **backend scheduler**

Thông báo được gửi cho Admin qua email, cho influencer qua giao diện landing page, kênh thông báo và email

## Luồng nghiệp vụ

### Cấu hình ngân sách

1. Admin truy cập trang **Chi tiết chiến dịch (Campaign Detail)**.
2. Hệ thống hiển thị trường **Ngân sách (Budget)** nếu chưa được khai báo.
3. Admin nhập hoặc cập nhật giá trị ngân sách (VNĐ)

### Giám sát và cảnh báo ngân sách

1. Hệ thống thực hiện tính toán ngân sách sau mỗi lần tính hoa hồng, ngay trước khi lưu lại hoa hồng của người dùng
2. Hệ thống tính toán tổng hoa hồng đã phát sinh cộng với hoa hồng dự kiến của lượt thưởng
3. Nếu hoa hồng tính ra vượt mức cảnh báo sẽ đánh dấu trạng thái cho thử thách
    - Vượt 75%, đánh dấu cảnh báo (warning)
    - Vượt 95%, đánh dấu ngừng nhận bài đăng mới
    - Vượt 100%, đánh dấu ngừng tính hoa hồng
    
    Riêng với khi vượt mức 100%, hoa hồng dự kiến sẽ không được lưu cho người dùng
    
4. Hệ thống gửi cảnh báo đến Admin và Influencer theo từng trạng thái

## Sơ đồ luồng

![diagram.svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram%201.svg)

.

# III. CONCEPTUAL DATA MODEL

## 1. Entities

| Entity | Mô tả ngắn |
| --- | --- |
| User | Tài khoản người dùng (creator tiềm năng) |
| OAuthAccount | Liên kết đăng nhập OAuth (Google/TikTok) của User |
| UserContract | Thông tin hợp đồng điện tử và dữ liệu chi trả của User |
| Creator | Đánh dấu user là creator; dùng trong nghiệp vụ campaign/reward |
| SocialProfile | Lưu thông tin hồ sơ mạng xã hội mà người dùng đăng ký để tham gia thử thách. |
| Campaign | Chiến dịch/thử thách |
| CampaignReward | Cấu trúc/luật thưởng hoa hồng thuộc một campaign |
| Content | Bài tham gia (video/link) của creator cho campaign |
| Reward | Kết quả tính hoa hồng cho creator theo CampaignReward |
| ReconciliationItem | Dòng dữ liệu trong một đợt đối soát |
| ReconciliationBatch | Đợt đối soát do Admin khởi tạo |
| PaymentItem | Dòng thanh toán cho một user trong một đợt |
| PaymentBatch | Đợt thanh toán do Admin tạo |
| AdminUser | Tài khoản quản trị (duyệt, đối soát, thanh toán) |
| File | Metadata các tệp (avatar, cover, CCCD, hợp đồng, export...) |

## 1. Conceptual

### User

| **Field** | **Key** | **Ghi chú/PII** |
| --- | --- | --- |
| ID | PK |  |
| Name |  | PII |
| Phone |  | PII |
| Email |  | PII |
| Avatar |  | Tham chiếu File (nếu dùng) |
| Birthday |  | PII |
| Gender |  |  |
| ReferralCode |  |  |
| Status |  | ACTIVE/INACTIVE/BANNED/DELETED |

### OAuthAccount

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| UserID | FK → User.ID |  |
| Provider |  | GOOGLE/TIKTOK |
| ProviderUserID | UNIQUE |  |

### UserContract

| **Field** | **Key** | **Ghi chú/PII** |
| --- | --- | --- |
| ID | PK |  |
| UserID | FK → User.ID |  |
| PhoneNumber |  | PII (JSON) |
| TaxInfo |  | PII (JSON) |
| BankInfo |  | PII (JSON) |
| IdentityInfo |  | PII (JSON) |
| SignedDate |  | DateTime |

### Creator

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| UserID | FK → User.ID |  |
| JoinedAt |  | DateTime |

### Social Profile

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| CreatorID | FK | Tham chiếu đến Creator |
| Platform |  | TIKTOK / YOUTUBE / FACEBOOK / INSTAGRAM / THREADS |
| ProfileURL |  | Đường dẫn đến hồ sơ mạng xã hội (bắt buộc với non-TikTok) |
| ProfileName |  | Tên hiển thị của hồ sơ |
| ProfileIDExternal |  | ID hồ sơ hoặc kênh từ mạng xã hội |
| AvatarURL |  | Ảnh đại diện của hồ sơ |
| HashtagIdentity |  | Hashtag định danh quy định bởi chương trình (bắt buộc với non-TikTok) |
| FollowerCount |  | Số lượng người theo dõi (auto lấy với TikTok, YouTube) |
| Status |  | PENDING / APPROVED / REJECTED |
| RejectedReason |  | Lý do từ chối (nếu có) |

### Campaign

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| Slug |  | Unique |
| Type |  | ViewBased, Other |
| Title |  |  |
| Description |  |  |
| Covers |  | Image List |
| StartTime |  |  |
| EndTime |  |  |
| Status |  | DRAFT/ACTIVE/ENDED/CANCELLED |
| Budget |  |  |
| Budget Status |  | A75, A95, A100 |

### CampaignReward

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| Id | PK |  |
| CampaignID | FK → Campaign.ID |  |
| Type |  | BY_VIEW/BY_TASK |
| RewardAmount |  |  |
| RewardRule |  | JSON mốc/điều kiện |
| Title |  |  |
| Description |  |  |
| Status |  | ACTIVE/INACTIVE |

### Content

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| CampaignID | FK → Campaign.ID |  |
| CreatorId | FK → Creator.ID |  |
| Platform |  | TIKTOK / YOUTUBE / FACEBOOK / INTSTAGRAM / THREADS |
| Url |  | Link public |
| SubmittedTime |  |  |
| Metadata |  | JSON |
| Status |  | PENDING/APPROVED/REJECTED |
| ApprovedBy |  |  |
| ApprovedAt |  |  |
| RejectedAt |  |  |
| RejectedBy |  |  |
| RejectedReason |  |  |

### Reward

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| CreatorId | FK → Creator.ID |  |
| CampaignRewardID | FK → CampaignReward.Id |  |
| CampaignRewardType |  | Phải khớp CampaignReward.Type |
| ContentId | FK → Content.Id |  |
| Status |  | PENDING/ELIGIBLE/RECONCILED/PAID/CANCELLED |
| Amount |  |  |

### ReconciliationItem

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| CreatorId | FK → Creator.ID |  |
| CampaignId | FK → Campaign.ID |  |
| CampaignRewardId | FK → CampaignReward.Id |  |
| CampaignRewardType |  | Phải khớp CampaignReward.Type |
| ReconciliationBatchId | FK → ReconciliationBatch.Id |  |
| RewardId | FK → Reward.ID | Nullable |
| Status |  | PENDING/CONFIRMED/CANCELLED |

### ReconciliationBatch

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| Id | PK |  |
| CampaignId | FK → Campaign.ID |  |
| EndTime |  | Mốc kết thúc kỳ đối soát |
| CampaignRewardType |  |  |

### PaymentItem

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| Id | PK |  |
| UserId | FK → User.ID |  |
| PaymentBatchId | FK → PaymentBatch.Id |  |
| Amount |  |  |
| Status |  | PENDING/PAID/CANCELLED/FAILED |

### PaymentBatch

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| Id | PK |  |
| TotalAmount |  |  |
| TotalItem |  |  |
| TotalUser |  |  |
| Status |  | DRAFT/PROCESSING/COMPLETED/CANCELLED |
| CreatedBy | FK → AdminUser.Id |  |
| CreatedTime |  |  |

### AdminUser

| **Field** | **Key** | **Ghi chú/PII** |
| --- | --- | --- |
| Id | PK |  |
| Email |  | PII |
| Password |  | PII (Hashed) |
| Role |  | SUPERADMIN/ADMIN/MODERATOR |
| Status |  |  |

### File

| **Field** | **Key** | **Ghi chú** |
| --- | --- | --- |
| ID | PK |  |
| Type |  | AVATAR/COVER/ID_DOC/CONTRACT/EXPORT/OTHER |
| Name |  | Tên hiển thị gốc |
| CreatedBy | FK → User.Id hoặc AdminUser.Id |  |
| CreatedTime |  |  |

## 3. Quan hệ giữa các entities

![diagram (3).svg](T%C3%80I%20LI%E1%BB%86U%20%C4%90%E1%BA%B6C%20T%E1%BA%A2%20Y%C3%8AU%20C%E1%BA%A6U%20PH%E1%BA%A6N%20M%E1%BB%80M/diagram_(3)%202.svg)

## 4. Các Entities khác

| Entity | Mô tả ngắn |
| --- | --- |
| Notification | Gửi thông báo đến người dùng |
| Article | Quản lý bài viết dạng blog và thông báo hệ thống |
| AuditLog | Ghi nhận toàn bộ hành động của Admin và User trong hệ thống |
| AmountAudit | Theo dõi lịch sử cộng tiền, đối soát và thanh toán hoa hồng cho creator |
| Configuration | Quản lý cấu hình chung của toàn hệ thống |
| ContentAnalytic | Thống kê các chỉ số của content theo ngày, tuần, tháng |
| ContentCrawlAudit | Ghi nhận các lượt gọi Video Metadata Service |
| CampaignAnalytic | Thống kê các chỉ số của campaign theo ngày, tuần, tháng |
| FileDownloadAudit | Theo dõi lịch sử tải file quan trọng (hợp đồng, export data) |
| Banner | Quản lý banner hiển thị trên landing page |
| OTPAudit | Ghi nhận mã OTP đã tạo và đã sử dụng |
| ReferralAudit | Theo dõi lịch sử nhập mã giới thiệu của user |
| Role | Quản lý vai trò Admin User và phân quyền liên quan |
| UserNotificationInfo | Quản lý thông tin thiết bị để gửi notification đến user |
| CreatorSegment | Phân nhóm creator phục vụ lọc sự kiện và gửi thông báo |

## 5. PII & bảo mật

### 5.1 Phân loại dữ liệu

**Public (Công khai)**

- Định nghĩa: Dữ liệu không chứa thông tin cá nhân, được phép công bố rộng rãi.
- Ví dụ:
    - Nội dung marketing, banner, bài viết/tin tức công khai
    - Thông tin sản phẩm/dịch vụ
- Yêu cầu bảo vệ:
    - Không thuộc phạm vi NĐ 13/2023
    - Thực hành an toàn hệ thống cơ bản (CDN, WAF, kiểm soát chỉnh sửa)

**Internal (Nội bộ)**

- Định nghĩa: Dữ liệu phục vụ vận hành, đã ẩn danh hoặc không định danh được cá nhân.
- Ví dụ:
    - Cấu hình hệ thống, tham số kỹ thuật
    - Rule hoa hồng/chính sách nội bộ
    - Thống kê tổng hợp không định danh
- Yêu cầu bảo vệ:
    - Giới hạn truy cập nội bộ theo vai trò
    - Nhật ký thay đổi cấu hình, sao lưu định kỳ

**Confidential (Dữ liệu cá nhân cơ bản)**

- Định nghĩa: Dữ liệu nhận diện cá nhân theo NĐ 13/2023; không thuộc nhóm nhạy cảm.
- Ví dụ:
    - Họ tên, email, số điện thoại, địa chỉ, ngày sinh, avatar
    - Tài khoản người dùng, lịch sử đăng nhập, log tải file
    - Dữ liệu hoa hồng/đối soát/thanh toán ở mức người dùng (không gồm số tài khoản ngân hàng/thẻ)
- Biện pháp bảo vệ chính:
    1. Kiểm soát truy cập và phân quyền chặt chẽ
    2. Nhật ký truy xuất/audit log đầy đủ
    3. Cơ chế đáp ứng quyền của chủ thể dữ liệu (xem, sửa, xóa)
    4. Sao lưu và khôi phục
    - Lưu ý: Không bắt buộc mã hóa ở mức cơ sở dữ liệu, nhưng khuyến nghị mã hóa khi truyền.

**Restricted (Dữ liệu cá nhân nhạy cảm)**

- Định nghĩa: Dữ liệu khi bị lộ có thể ảnh hưởng trực tiếp đến quyền, lợi ích hợp pháp của cá nhân; yêu cầu bảo vệ tăng cường.
- Ví dụ:
    - Ảnh/scan giấy tờ định danh: CCCD/CMND, hộ chiếu, bằng lái
    - Hợp đồng PDF có chữ ký/đóng dấu
    - Thông tin tài chính nhạy cảm: số tài khoản ngân hàng, số thẻ
    - Sinh trắc học: khuôn mặt, vân tay (nếu có)
- Biện pháp bảo vệ bắt buộc:
    1. Mã hóa dữ liệu khi lưu trữ và khi truyền
    2. Hạn chế tối thiểu người được truy cập; tách biệt lưu trữ
    3. Quy trình xóa an toàn; kiểm soát tải xuống/chia sẻ
    4. Đánh giá tác động xử lý dữ liệu (khi cần)
    5. Đầy đủ biện pháp của nhóm Confidential

### 5.2 Ma trận dữ liệu chính và lớp bảo vệ

| Thực thể | Trường dữ liệu | Phân loại | Biện pháp bảo vệ |
| --- | --- | --- | --- |
| User | Name, Phone, Email, Birthday, Avatar | Confidential – dữ liệu cá nhân cơ bản | - Không bắt buộc mã hóa at-rest, nhưng khuyến nghị AES-256 at-rest; 
- TLS 1.2+ in-transit |
| OAuthAccount | Provider, ProviderUserID, expiresAt, scopes (không lưu access_token) | Confidential – dữ liệu cá nhân cơ bản | - UNIQUE(provider, provider_user_id) 
- Không lưu access_token |
| UserContract | PhoneNumber, TaxInfo, BankInfo, IdentityInfo, ContractFileId | Restricted | Mã hóa cột tại DB; file lưu trong private storage; chữ ký số/đóng dấu thời gian cho file; lưu snapshot phục vụ chi trả và kiểm toán |
| Reward / ReconciliationItem / PaymentItem | Số tiền, trạng thái, tham chiếu tới user/content, thông tin tham chiếu giao dịch | Restricted | - Truy cập giới hạn cho admin
- Ghi log đầy đủ mọi thao tác |
| File (Type = ID_DOC, CONTRACT, EXPORT) | File binary, metadata, type | Restricted | - Lưu trong private bucket với server‑side encryption
- Phát link tạm (signed URL); 
- Quét malware
- Ghi log truy xuất |

### 5.3 Chuẩn mã hóa và khóa

- Truyền tải: sử dụng TLS 1.2 trở lên kèm HSTS; bắt buộc mTLS cho toàn bộ giao tiếp dịch vụ nội bộ.
- Lưu trữ CSDL: bật mã hóa cấp đĩa (TDE) và mã hóa cột đối với trường PII nhạy cảm bằng AES‑256; quản lý khóa bằng KMS/HSM theo cơ chế envelope encryption; tách quyền quản trị khóa và quyền vận hành hệ thống.
- Lưu trữ tệp: áp dụng SSE‑KMS; bucket ở chế độ private, Block Public Access, truy cập qua VPC Endpoint; phát presigned URL TTL 30 giây, một lần dùng.
- Bí mật/Token: lưu trữ trong secrets manager/vault; kích hoạt phiên bản hóa và audit; xoay định kỳ 90 ngày; cấm ghi vào biến môi trường cố định, repository và log CI/CD.

### 5.4 Truy cập và phân quyền

- Áp dụng RBAC kết hợp ABAC theo vai trò và phạm vi campaign; mặc định cấp quyền tối thiểu (least privilege) và cấp quyền tạm thời theo phiên (just‑in‑time).
- Các thao tác nhạy cảm (xuất file dữ liệu, khóa/kết thúc batch, xem tệp ID_DOC/CONTRACT) yêu cầu xác thực tăng cường (MFA re‑check) và phê duyệt 4‑eyes đối với export thanh toán.
- Tài khoản break‑glass được tạo riêng, bị vô hiệu hóa mặc định, chỉ kích hoạt theo quy trình phê duyệt; đổi thông tin xác thực mỗi 90 ngày; toàn bộ phiên sử dụng được ghi log và rà soát.

### 5.5 Logging, giám sát và kiểm toán

- Ghi AuditLog bất biến (append‑only) cho: đăng nhập/đăng xuất Admin, duyệt/hủy content, thay đổi CampaignReward/RewardRule, tạo/kết thúc ReconciliationBatch/PaymentBatch, tạo/tải file, thay đổi UserContract/BankInfo/TaxInfo.
- Ẩn PII trong log: không ghi đầy đủ email/phone/CCCD; thay bằng token/ID; log ở định dạng có cấu trúc, kèm request_id, actor_id, thời gian UTC.
- FileDownloadAudit bắt buộc lưu: user, thời điểm, IP, user‑agent, file_id, checksum, kết quả; hệ thống cảnh báo khi có hành vi bất thường (tải lặp, ngoài giờ, IP lạ).
- Tích hợp giám sát và cảnh báo theo ngưỡng SLA; sự kiện bảo mật kích hoạt quy trình ứng phó sự cố.

### 5.6 Lưu trữ và vòng đời dữ liệu

- OTP: TTL 10 phút; lưu dạng băm kèm thời điểm; tự động xóa sau khi hết hạn hoặc sử dụng.
- OAuth: không lưu access_token
- ID_DOC (ảnh CCCD): lưu ở storage private; thời hạn lưu 5 năm kể từ lần chi trả cuối; hết hạn tiến hành purge khỏi storage và backup theo lịch.
- Hợp đồng (PDF + metadata): lưu 10 năm.
- File export (đối soát/thanh toán): lưu 30 ngày; hết hạn tự động xóa; mọi bản tải về đều qua link tạm.
- Log bảo mật/audit: lưu tối thiểu 1 năm; bản ghi tài chính/đối soát/thanh toán: lưu tối thiểu 10 năm.

### 5.7 Bảo vệ tải tệp và nội dung

- Chỉ chấp nhận: JPG/JPEG/PNG/PDF; giới hạn kích thước ID_DOC ≤ 10 MB, CONTRACT ≤ 10 MB, EXPORT ≤ 20 MB.
- Quét malware với mỗi tệp tải lên; loại bỏ metadata EXIF; đóng dấu watermark/time‑stamp và actor_id trên CONTRACT/EXPORT khi hiển thị và khi tải xuống.
- Bật Content Security Policy; chống SSRF bằng allowlist domain khi crawl metadata; cấm truy xuất IP nội bộ; áp hạn mức crawl 10 yêu cầu/giây mỗi user và 1000 yêu cầu/phút toàn hệ thống.

### 5.8 Tuân thủ và quyền riêng tư

- Tuân thủ Nghị định 13/2023 (VN). Cơ sở pháp lý: Contract (chi trả/đối soát), Legitimate Interest (phòng chống gian lận, vận hành)
- Hệ thống lưu Consent/Preference gồm: phiên bản chính sách, thời điểm đồng ý, phạm vi; giao diện cho phép rút lại consent và thay đổi tùy chọn.
- Cung cấp cơ chế DSAR (yêu cầu truy cập/xóa/chỉnh sửa dữ liệu) với SLA phản hồi tối đa 30 ngày; toàn bộ yêu cầu và xử lý được ghi vào AuditLog.
- Ký thỏa thuận xử lý dữ liệu (DPA) với các bên thứ ba; dữ liệu chứa PII được lưu trữ trong khu vực DC/VPC đã định; mọi dòng chuyển dữ liệu xuyên biên giới phải được ghi nhận và kiểm soát.

# IV. Yêu cầu thiết kế

| **#** | **Mục** | **Yêu cầu (nội dung cần có trong Figma)** | **Tiêu chí chấp nhận (cách kiểm tra)** |
| --- | --- | --- | --- |
| 1 | **Cấu trúc tệp & Giao nộp** | Tên file theo dạng: `App – Tính năng – vX.Y – YYYY-MM-DD`. Các trang gồm: **Cover**, **Flows**, **Screens**, **Components**, **Archive**. Trang Cover hiển thị thông tin người phụ trách, trạng thái và ghi chú phát hành (Release note). | Tất cả các trang bắt buộc đều có; trang Cover có phiên bản, người phụ trách, trạng thái và 1 trang ghi chú phát hành. |
| 2 | **Tuân thủ thương hiệu** | Chỉ sử dụng bảng màu và font chữ đã được phê duyệt; không dùng mã HEX tùy ý. Dùng đúng phiên bản logo và khoảng cách an toàn. Hình ảnh và CTA (nút kêu gọi hành động) tuân theo phong cách thương hiệu. | Khớp với hướng dẫn thương hiệu đính kèm; kiểm tra trực quan nhanh về màu sắc, font chữ, và cách dùng logo. |
| 4 | **Khả năng đọc & vùng chạm (A11y)** | Độ tương phản văn bản đạt **WCAG 2.1 AA (≥4.5:1)**. Vùng cảm ứng ≥ **44×44 px**; khoảng cách giữa các vùng cảm ứng ≥8 px. Thể hiện rõ các trạng thái focus/hover/pressed. | Ảnh chụp màn hình hoặc ghi chú ngắn xác nhận độ tương phản; kiểm tra kích thước trong Dev Mode. |
| 5 | **Trạng thái & Trường hợp đặc biệt** | Với các màn hình chính, bao gồm: **Loading**, **Empty**, **Error**, **No-permission**. Biểu mẫu hiển thị lỗi nội tuyến và thông điệp mẫu. | Có **Bảng trạng thái (State Matrix)** trong file (liệt kê trạng thái + nội dung mẫu). |
| 6 | **Luồng người dùng** | Prototype chạy theo luồng **Bắt đầu → Kịch bản chính → ≥1 Kịch bản phụ (Edge path)**. Với animation, ghi chú rõ trigger/target/thời lượng trong mô tả khung. | Prototype chạy trọn vẹn, không có liên kết bị lỗi. |
| 7 | **Hỗ trợ responsive** | Cung cấp **phiên bản di động (≥375px)** và ít nhất **1 phiên bản màn hình lớn (1024/1440px)** cho các màn hình chính. Grid/khoảng cách tuân theo quy tắc **4/8 px**. | Các màn hình chính tồn tại ở cả hai kích thước; ghi chú nếu có ngoại lệ về khoảng cách. |
| 8 | **Bàn giao cho dev (Dev Mode & xuất file)** | Bật Dev Mode; đo đạc rõ ràng (font/khoảng cách/bo góc). Xuất file sẵn sàng (SVG + 1x/2x/3x), đặt tên theo dạng `component_state@2x`. Khung chứa **tiêu chí chấp nhận** và **sự kiện analytics** (tên/tham số). | Dev không cần suy đoán kích thước; có preset xuất file; danh sách sự kiện hiển thị rõ. |
| 10 | **Bình luận & Hoàn tất** | Bình luận đã được giải quyết hoặc theo dõi rõ ràng; không có bình luận “mồ côi”. Dấu footer trên các khung chính: `Design vX.Y – Ready for Dev – Date`. | Có ghi chú phát hành trên trang Cover; không còn bình luận chặn tiến trình. |