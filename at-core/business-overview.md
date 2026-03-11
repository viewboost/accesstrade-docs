# at-core Business Overview

> Tài liệu mô tả tổng quan dự án at-core dành cho stakeholders (non-tech).
>
> Cập nhật: 2026-03-11

---

## 1. at-core là gì?

**at-core** là nền tảng trung tâm quản lý influencer profile, kết nối giữa các đối tác (partner) và dịch vụ phân tích influencer.

Nói đơn giản: at-core là **"sổ cái chung"** về thông tin influencer mà nhiều bên cùng đóng góp và sử dụng, nhưng mỗi bên chỉ thấy dữ liệu phù hợp với mình.

### Vai trò chính

| Vai trò | Mô tả |
|---------|--------|
| **Profile Hub** | Nơi tập trung, lưu trữ và chuẩn hóa thông tin influencer từ nhiều nguồn |
| **Cổng kết nối Partner** | Cung cấp API cho các đối tác (Techcombank, Vinfast, Ambassabor...) truy cập dữ liệu influencer |
| **Cầu nối tới Vendor phân tích** | Gọi tới dịch vụ phân tích & chấm điểm influencer (Influence Meter) để làm giàu dữ liệu |
| **Quản trị dữ liệu** | Cho phép đội Operations kiểm tra, sửa chữa và xác minh thông tin influencer |

---

## 2. Các bên liên quan

### 2.1 Partner (Đối tác)

Partner là các tổ chức sử dụng at-core để tìm kiếm và quản lý influencer cho chiến dịch marketing của họ.

| Partner | Loại | Mô tả |
|---------|------|--------|
| **Techcombank (TCB)** | Brand | Ngân hàng, sử dụng influencer cho chiến dịch truyền thông. Là partner đầu tiên, đã tích hợp |
| **Vinfast** | Brand | Hãng xe, dự kiến tích hợp trong tương lai |
| **Ambassabor** | Creator Portal | Nền tảng để influencer (creator) tự đăng ký, tự quản lý profile. Không phải brand |

**Đặc điểm quan trọng:**
- Mỗi partner có tài khoản riêng (API Key + Partner ID)
- Mỗi partner có hạn mức sử dụng (quota) theo gói đăng ký
- Partner không thể truy cập dữ liệu riêng của partner khác

### 2.2 Vendor

| Vendor | Vai trò |
|--------|---------|
| **Influence Meter (IM)** | Dịch vụ phân tích & chấm điểm influencer. at-core gửi yêu cầu tới IM để lấy dữ liệu phân tích (engagement score, audience demographics, content analysis...) |

> at-core không biết và không quan tâm IM lấy dữ liệu từ đâu (crawl, API, hay nguồn khác). at-core chỉ gửi yêu cầu và nhận kết quả.

### 2.3 Nội bộ

| Vai trò | Mô tả |
|---------|--------|
| **Operations Team** | Đội ngũ vận hành, có quyền xem, sửa, xác minh thông tin influencer trên at-core |
| **Admin** | Quản trị hệ thống, import influencer hàng loạt, quản lý partner, cấu hình hệ thống |

---

## 3. Profile Hub - Trung tâm dữ liệu Influencer

### 3.1 Vấn đề cần giải quyết

Trước khi có Profile Hub, thông tin influencer bị phân tán:
- Techcombank lưu influencer trong database riêng
- Ambassabor lưu creator trong database riêng
- Dữ liệu crawl từ mạng xã hội lưu ở nơi khác
- Không ai có bức tranh đầy đủ về 1 influencer

**Hệ quả:** Dữ liệu trùng lặp, không nhất quán, khó mở rộng khi thêm partner mới.

### 3.2 Giải pháp: Profile Hub tập trung

at-core trở thành **nơi duy nhất** lưu trữ thông tin influencer. Các partner đóng góp dữ liệu vào và lấy dữ liệu ra từ at-core.

```
                    ┌─────────────────────────┐
   Techcombank ────►│                         │◄──── Influence Meter
                    │                         │      (vendor phân tích)
   Vinfast ────────►│     at-core             │
                    │     PROFILE HUB         │
   Ambassabor ────►│                         │◄──── Admin Import
   (creator tự     │  "Sổ cái chung"         │      (CSV, thủ công)
    đăng ký)       │                         │
                    │                         │◄──── Operations
                    └────────┬────────────────┘      (sửa & xác minh)
                             │
                    Cung cấp dữ liệu cho
                    tất cả partner
```

### 3.3 Nguồn dữ liệu & Độ tin cậy

Không phải mọi nguồn dữ liệu đều đáng tin như nhau. at-core sử dụng **hệ thống độ tin cậy theo từng trường dữ liệu**:

| Nguồn | Độ tin cậy | Ví dụ |
|-------|------------|-------|
| **API mạng xã hội** (qua Influence Meter) | Cao nhất | Số followers từ TikTok API |
| **Operations xác minh** | Rất cao | Nhân viên AT xác nhận "influencer X thuộc ngành beauty" |
| **Partner đã xác minh** | Cao | TCB xác nhận "đã booking influencer X, performance tốt" |
| **Partner gửi vào** | Khá | TCB submit thông tin influencer mới |
| **Crawl từ mạng xã hội** (qua Influence Meter) | Trung bình | Dữ liệu thu thập tự động, có thể sai (fake followers, engagement ảo) |
| **Creator tự khai** (qua Ambassabor) | Thấp nhất | Influencer tự khai giá booking, tự mô tả ngành |

**Nguyên tắc:** Khi có xung đột giữa các nguồn, dữ liệu có độ tin cậy cao hơn sẽ được ưu tiên hiển thị. Operations team có thể can thiệp khi cần.

---

## 4. Phân quyền dữ liệu - "Ai thấy gì?"

Đây là nguyên tắc cốt lõi của hệ thống: **dữ liệu được chia thành 3 tầng**, mỗi tầng có quy tắc truy cập riêng.

### 4.1 Ba tầng dữ liệu

| Tầng | Nội dung | Ai thấy | Ví dụ |
|------|----------|---------|-------|
| **Base Profile** (công khai) | Thông tin cơ bản của influencer | Tất cả partner | Tên, handle, số followers, ngành, engagement rate |
| **Private Enrichment** (riêng tư) | Dữ liệu mà partner đóng góp | Chỉ partner đó | Giá booking, lịch sử campaign, đánh giá nội bộ |
| **Ops Verified** (đã xác minh) | Dữ liệu AT đã xác minh | Tất cả partner | Xác nhận tài khoản thật, vị trí địa lý chính xác |

### 4.2 Ví dụ thực tế

Influencer **@ngoctrinhfashion** có profile trên at-core:

| Dữ liệu | Giá trị | Ai thấy |
|----------|---------|---------|
| Followers | 1.2 triệu | Tất cả (Base Profile) |
| Ngành | Fashion | Tất cả (Base Profile) |
| Engagement rate | 3.2% | Tất cả (Base Profile) |
| Giá booking | 50 triệu/post | Chỉ TCB (TCB đã booking, biết giá thật) |
| Số campaign đã chạy với TCB | 3 | Chỉ TCB |
| Creator tự khai rate | 40 triệu/post | Chỉ Ambassabor |
| Xác nhận tài khoản thật | Verified | Tất cả (Ops Verified) |
| Vị trí | HCM | Tất cả (Ops Verified) |

**Tại sao thiết kế như vậy?**
- **Base Profile** là thông tin công khai, ai cũng crawl được → chia sẻ để giảm chi phí
- **Private Enrichment** là tài sản cạnh tranh của từng partner → bảo vệ tuyệt đối. Nếu TCB biết Ambassabor cho phép partner khác xem giá booking của họ, TCB sẽ không muốn đóng góp dữ liệu nữa
- **Ops Verified** là giá trị mà AccessTrade tạo ra → chia sẻ để tăng giá trị nền tảng

---

## 5. Quan hệ Partner - Profile: "Danh sách của tôi"

Mỗi partner chỉ thấy **danh sách influencer liên quan đến mình**, không phải toàn bộ database.

### 5.1 Cách xác định "của tôi"

| Hành động | Tạo quan hệ | Ví dụ |
|-----------|-------------|-------|
| Partner gửi influencer vào | **Đã đóng góp** (Contributed) | TCB submit influencer qua API |
| Creator đăng ký trên Ambassabor | **Đã đóng góp** (Contributed) | Creator link TikTok account trên Ambassabor |
| Partner lưu influencer từ Pool | **Đã lưu** (Bookmarked) | TCB tìm trên Pool, lưu influencer vào danh sách |
| Partner booking influencer | **Đã booking** (Booked) | TCB booking influencer cho campaign |

### 5.2 Danh sách của từng partner

| Partner | "Danh sách của tôi" gồm | Có thể tìm thêm từ Pool? |
|---------|-------------------------|--------------------------|
| **TCB** | Influencer TCB đã submit + lưu + booking | Có (TCB là brand, cần discover influencer mới) |
| **Ambassabor** | Chỉ creator đã đăng ký trên Ambassabor | Không (Ambassabor là creator portal, không phải brand) |
| **Vinfast** | Influencer Vinfast đã submit + lưu + booking | Có |

### 5.3 Pool (Kho influencer chung)

Pool là tập hợp **Base Profile** của tất cả influencer có trạng thái công khai. Các brand partner (TCB, Vinfast) có thể tìm kiếm trên Pool để phát hiện influencer mới.

- Pool chỉ hiển thị thông tin cơ bản (Base Profile)
- Không hiển thị Private Enrichment của bất kỳ partner nào
- Partner tìm thấy influencer phù hợp → lưu vào "danh sách của tôi" → bắt đầu làm việc

---

## 6. Luồng hoạt động chính

### 6.1 Partner gửi influencer mới

```
Partner (TCB) gửi thông tin influencer
    ↓
at-core tiếp nhận, tạo/cập nhật profile
    ↓
at-core gửi yêu cầu tới Influence Meter để phân tích
    ↓
Influence Meter trả về dữ liệu phân tích (score, engagement...)
    ↓
at-core cập nhật profile với dữ liệu phân tích
    ↓
Profile sẵn sàng trong danh sách của TCB + Pool (nếu công khai)
```

### 6.2 Creator tự đăng ký (qua Ambassabor)

```
Creator đăng ký trên Ambassabor, link tài khoản mạng xã hội
    ↓
Ambassabor gọi at-core API để tạo profile
    ↓
at-core tạo profile + gửi yêu cầu phân tích tới Influence Meter
    ↓
Profile xuất hiện trong:
  - Danh sách của Ambassabor (creator đã đăng ký)
  - Pool công khai (brand partners có thể tìm thấy)
```

### 6.3 Operations xác minh & sửa dữ liệu

```
Operations team mở Admin Dashboard
    ↓
Xem profile influencer (tất cả nguồn dữ liệu)
    ↓
Phát hiện dữ liệu sai (ví dụ: crawl ghi sai ngành)
    ↓
Sửa trường dữ liệu + ghi lý do sửa
    ↓
Hệ thống lưu lịch sử thay đổi (ai sửa, khi nào, giá trị cũ/mới, lý do)
    ↓
Dữ liệu đã xác minh hiển thị cho tất cả partner
```

### 6.4 Brand tìm influencer mới

```
Brand (TCB) tìm kiếm trên Pool: "influencer beauty, >100K followers, HCM"
    ↓
at-core trả về danh sách Base Profile phù hợp
    ↓
TCB xem chi tiết, lưu influencer vào "danh sách của tôi"
    ↓
TCB có thể gửi yêu cầu matching (chấm điểm phù hợp với campaign)
    ↓
at-core gọi Influence Meter để tính matching score
    ↓
Trả kết quả cho TCB
```

---

## 7. Gói dịch vụ & Hạn mức

Mỗi partner đăng ký gói dịch vụ với hạn mức sử dụng hàng tháng:

| Gói | Hạn mức/tháng | Đối tượng |
|-----|---------------|-----------|
| **Free** | 10 yêu cầu | Dùng thử |
| **Basic** | 50 yêu cầu | Partner nhỏ |
| **Premium** | 200 yêu cầu | Partner trung bình |
| **Enterprise** | Không giới hạn | Partner lớn (TCB, Vinfast) |

---

## 8. Tóm tắt giá trị

| Giá trị | Mô tả |
|---------|--------|
| **Một nơi duy nhất** | Tất cả thông tin influencer tập trung tại at-core, không phân tán |
| **Dữ liệu chính xác hơn** | Nhiều nguồn đóng góp + operations xác minh > chỉ dựa vào crawl |
| **Bảo vệ dữ liệu partner** | Dữ liệu riêng của mỗi partner được cách ly hoàn toàn |
| **Mở rộng dễ dàng** | Thêm partner mới = kết nối vào hệ thống có sẵn, không cần xây lại |
| **Vận hành hiệu quả** | Sửa dữ liệu 1 chỗ, tất cả partner đều thấy bản cập nhật |
| **Minh bạch** | Mọi thay đổi dữ liệu đều được ghi lại đầy đủ (ai, khi nào, tại sao) |

---

## Thuật ngữ

| Thuật ngữ | Giải thích |
|-----------|------------|
| **Partner** | Tổ chức sử dụng at-core (TCB, Vinfast, Ambassabor) |
| **Vendor** | Dịch vụ bên ngoài mà at-core sử dụng (Influence Meter) |
| **Profile** | Bản ghi thông tin của 1 influencer trên at-core |
| **Base Profile** | Thông tin cơ bản, công khai của influencer |
| **Private Enrichment** | Dữ liệu riêng mà partner đóng góp, chỉ partner đó thấy |
| **Ops Verified** | Dữ liệu đã được đội Operations xác minh |
| **Pool** | Kho influencer công khai, brand partners có thể tìm kiếm |
| **Matching** | Chấm điểm mức độ phù hợp giữa influencer và campaign |
| **Enrichment** | Quá trình làm giàu dữ liệu profile (gửi tới Influence Meter phân tích) |
| **Quota** | Hạn mức sử dụng dịch vụ hàng tháng |

---

*Tài liệu thuộc dự án at-core - AccessTrade Projects*
