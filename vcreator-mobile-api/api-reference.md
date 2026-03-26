# VCreator Mobile App - API Reference

> Tài liệu API cho mobile app, được trích xuất từ source code `vcreator/frontend-green`.
> Ngày tạo: 2026-03-26

## Tổng quan

- **Tổng số endpoints**: 58
- **Base URL (Dev)**: `https://api.dev-vcreator.koc.asia`
- **Base URL (Prod)**: `https://api.viewboost.vn`
- **Upload URL (Dev)**: `https://dev-ambassador-file.koc.asia/api/file`
- **Upload URL (Prod)**: `https://file.viewboost.vn`
- **Timeout**: 30 giây (30000ms)

## Authentication

- Bearer token trong header `Authorization`
- Login qua Google, Facebook, TikTok

## Default Headers

| Header | Value |
|---|---|
| `os-name` | Tên OS (iOS/Android) |
| `os-version` | Phiên bản OS |
| `PLATFORM` | `Mobile` |
| `DEVICE-TYPE` | Loại thiết bị |
| `App-Version` | Phiên bản app |
| `Authorization` | `Bearer {token}` |

---

## 1. User (20 endpoints)

### Authentication

| # | Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|---|
| 1 | POST | `/users/login-with-google` | Đăng nhập bằng Google | Google auth token |
| 2 | POST | `/users/login-with-facebook` | Đăng nhập bằng Facebook | Facebook auth data |
| 3 | POST | `/users/login-with-tiktok` | Đăng nhập bằng TikTok | TikTok auth data |
| 4 | POST | `/users/logout` | Đăng xuất | Device/session data |

### User Profile

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 5 | GET | `/users/me` | Lấy thông tin user hiện tại | - |
| 6 | PUT | `/users/update` | Cập nhật thông tin user | User data object |
| 7 | PUT | `/users/me/avatars` | Cập nhật avatar | Avatar file |

### OTP & Xác thực

| # | Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|---|
| 8 | POST | `/users/request-otp` | Yêu cầu OTP | Phone/email |
| 9 | POST | `/users/verify-otp` | Xác thực OTP | OTP code |

### Định danh (KYC)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 10 | POST | `/users/identification` | Tạo định danh mới | ID verification data |
| 11 | PUT | `/users/identification/{id}` | Cập nhật định danh | ID verification update |
| 12 | GET | `/users/identification/me` | Lấy thông tin định danh | - |
| 13 | POST | `/users/identification/image` | Scan ảnh CMND/CCCD | ID image file |

### Hợp đồng

| # | Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|---|
| 14 | POST | `/users/contract/info` | Tạo/cập nhật thông tin hợp đồng | Contract info |
| 15 | POST | `/users/contract/estimate` | Ước tính hợp đồng | Estimation params |
| 16 | GET | `/users/contract/pre-signed` | Lấy hợp đồng pre-signed | - |

### Liên kết mạng xã hội

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 17 | POST | `/users/socials/link` | Liên kết tài khoản MXH | Social account data |
| 18 | GET | `/users/socials` | Danh sách MXH đã liên kết | Query params |

### Referral

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 19 | POST | `/users/referral` | Nhập mã giới thiệu | Referral code |
| 20 | GET | `/users/by-referral-code` | Lấy thông tin người giới thiệu | `code` query param |

### Device

| # | Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|---|
| 21 | POST | `/users/device` | Đăng ký device token (push notification) | Device token |

---

## 2. Bank & Tài chính (8 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 22 | GET | `/users/bank-cards` | Danh sách thẻ ngân hàng | - |
| 23 | POST | `/users/bank-cards` | Thêm thẻ ngân hàng | Bank card details |
| 24 | PUT | `/users/bank-cards/{id}` | Cập nhật thẻ ngân hàng | Card data |
| 25 | DELETE | `/users/bank-cards/{id}` | Xóa thẻ ngân hàng | - |
| 26 | PUT | `/users/bank-cards/{id}/set-default` | Đặt thẻ mặc định | - |
| 27 | GET | `/bank` | Danh sách ngân hàng | Filter params |
| 28 | GET | `/banks/{brandId}/branch` | Danh sách chi nhánh | Branch query params |
| 29 | GET | `/users/cash-flow` | Lịch sử dòng tiền | Date range, pagination |

---

## 3. Event & Campaign (10 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 30 | GET | `/events` | Danh sách events | Pagination, filter |
| 31 | GET | `/events/current` | Event đang diễn ra | - |
| 32 | GET | `/events/by-slug` | Chi tiết event theo slug | `slug` query param |
| 33 | GET | `/events/{id}/schemas` | Schema của event | - |
| 34 | POST | `/events/{id}/content` | Tạo nội dung cho event | Content data |
| 35 | GET | `/events/{id}/content/me` | Nội dung đã tạo của tôi | Query params |
| 36 | GET | `/events/{id}/content` | Danh sách nội dung event | Query params |
| 37 | GET | `/events/{id}/leaderboards` | Bảng xếp hạng | Filter params |
| 38 | GET | `/events/statistic` | Thống kê event | Statistic filters |
| 39 | GET | `/events/user-newest` | User mới nhất tham gia | Filter params |

---

## 4. Event Bonus (2 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 40 | GET | `/event-bonus` | Danh sách event bonus | Filter params |
| 41 | GET | `/event-bonus/{id}` | Chi tiết event bonus | - |

---

## 5. Withdraw - Rút tiền (3 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 42 | POST | `/withdraw-cash` | Tạo yêu cầu rút tiền | Amount, bank card ID |
| 43 | GET | `/withdraw-cash` | Danh sách lệnh rút tiền | Status, date, pagination |
| 44 | GET | `/withdraw-cash/{withdrawId}` | Chi tiết lệnh rút tiền | - |

---

## 6. Notification (2 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 45 | GET | `/notifications` | Danh sách thông báo | Pagination, filter |
| 46 | GET | `/notifications/{notificationId}` | Đọc thông báo (đánh dấu đã đọc) | - |

---

## 7. Partner (4 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 47 | GET | `/partners` | Danh sách đối tác | - |
| 48 | GET | `/partners/content-features` | Tính năng nội dung đối tác | - |
| 49 | GET | `/partners/by-slug` | Chi tiết đối tác theo slug | `slug` query param |
| 50 | GET | `/quick-actions` | Danh sách quick actions | Filter params |

---

## 8. User Statistic (4 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 51 | GET | `/user-statistic` | Tổng quan thống kê user | Statistic filters |
| 52 | GET | `/user-statistic/contents` | Thống kê nội dung | Content stat filters |
| 53 | GET | `/user-statistic/invitees` | Danh sách người được mời | Pagination params |
| 54 | GET | `/user-statistic/invitees/statistic` | Thống kê người được mời | Invitee stat filters |

---

## 9. Content & Media (3 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 55 | GET | `/articles/{articleId}` | Chi tiết bài viết | - |
| 56 | GET | `/news` | Danh sách tin tức | Category, pagination |
| 57 | POST | `/photo` (Upload endpoint) | Upload ảnh | File (multipart/form-data) |

---

## 10. System (2 endpoints)

| # | Method | Endpoint | Mô tả | Request Body/Params |
|---|---|---|---|---|
| 58 | GET | `/app-data` | Cấu hình app (bootstrap data) | - |
| - | GET | `/system-bank-cards` | Danh sách thẻ ngân hàng hệ thống | Query params |

---

## Tổng kết theo nhóm

| Nhóm | Số endpoints | Ghi chú |
|---|---|---|
| User & Auth | 21 | Login, profile, KYC, contract, social, referral |
| Bank & Tài chính | 8 | Quản lý thẻ, danh sách NH, dòng tiền |
| Event & Campaign | 12 | Events, content, leaderboard, bonus |
| Withdraw | 3 | Rút tiền |
| Notification | 2 | Thông báo |
| Partner | 4 | Đối tác |
| User Statistic | 4 | Thống kê |
| Content & Media | 3 | Bài viết, tin tức, upload |
| System | 2 | App config, system bank cards |
| **Tổng** | **59** | |
