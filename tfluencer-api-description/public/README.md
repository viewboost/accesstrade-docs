# Public API Documentation

## Thông tin chung

| Mục | Giá trị |
|-----|---------|
| Base URL | `{{BASE_URL}}` |
| Content-Type | `application/json` |

> Thay `{{BASE_URL}}` bằng URL server thực tế. VD: `https://api.viewboost.vn`

---

## Headers

### Headers bắt buộc

| Header | Giá trị | Khi nào cần |
|--------|---------|-------------|
| `Authorization` | `Bearer {{TOKEN}}` | API yêu cầu đăng nhập |
| `X-Device-ID` | `{{DEVICE_ID}}` | **Luôn gửi kèm** khi có `Authorization`. Phải khớp `deviceId` trong JWT, nếu không → 401 |
| `Content-Type` | `application/json` | Các API POST/PUT |

### Headers tuỳ chọn

| Header | Giá trị mẫu | Mô tả |
|--------|-------------|-------|
| `Accept-Language` | `vi` / `en` | Ngôn ngữ response. Mặc định `vi` |
| `App-Version` | `1.0.0` | Phiên bản app |
| `OS-NAME` | `web` / `ios` / `android` | Hệ điều hành |
| `OS-VERSION` | `16.0` | Phiên bản OS |
| `PLATFORM` | `web` / `mobile` | Nền tảng |
| `Device-Model` | `iPhone 15 Pro` | Model thiết bị |
| `Browser-Name` | `Chrome` | Tên trình duyệt |
| `Browser-Version` | `120.0` | Phiên bản trình duyệt |
| `Fcm-Token` | `firebase_token_xxx` | Firebase Cloud Messaging token |
| `Source` | `web` | Nguồn request |

---

## Cơ chế xác thực

1. Middleware `Auth` chạy trên **tất cả** route
2. Nếu **không có** header `Authorization` → request vẫn đi qua, nhưng không có thông tin user
3. Nếu **có** header `Authorization`:
   - Parse JWT token (bỏ prefix `Bearer `)
   - Kiểm tra token hợp lệ, chưa hết hạn
   - So sánh `deviceId` trong token claims với header `X-Device-ID` → **phải khớp**
   - Kiểm tra token trong Redis cache (`user_token:{userId}:{deviceId}:{token}`)
   - Nếu fail → **401 Unauthorized**
4. Route có `RequiredLogin` → phải đăng nhập, nếu không → **401**

---

## Response format

**Thành công (200):**

```json
{
  "data": { ... },
  "code": 200
}
```

Phân trang:

```json
{
  "data": [ ... ],
  "nextPageToken": "base64_string",
  "code": 200
}
```

**Lỗi:**

```json
{
  "data": null,
  "message": "Mô tả lỗi",
  "code": 400
}
```

| HTTP Status | Ý nghĩa |
|-------------|----------|
| `200` | Thành công |
| `400` | Validation lỗi, thiếu param, dữ liệu không hợp lệ |
| `401` | Thiếu/sai token, `X-Device-ID` không khớp |
| `404` | ID sai format ObjectID, resource không tồn tại |
| `429` | Rate limit |

---

## Biến môi trường (Postman / Thunder Client)

| Biến | Mô tả | Ví dụ |
|------|-------|-------|
| `{{BASE_URL}}` | URL server | `https://api.viewboost.vn` |
| `{{TOKEN}}` | JWT token (lấy từ API login) | `eyJhbGciOiJIUzI1NiIs...` |
| `{{DEVICE_ID}}` | Device ID (phải khớp `deviceId` trong token) | `device-abc-123-xyz` |

---

## Danh sách tài liệu API

| File | Nhóm | Mô tả |
|------|------|-------|
| [api-common.md](api-common.md) | Common | Health check, app data, banks, countries, provinces |
| [api-users.md](api-users.md) | Users | Đăng ký, đăng nhập, profile, bank cards, CMND, hợp đồng, socials |
| [api-events.md](api-events.md) | Events | Danh sách event, leaderboard, content, schema |
| [api-partners.md](api-partners.md) | Partners | Danh sách partner, content nổi bật, top influencer |
| [api-news.md](api-news.md) | News & Articles | Tin tức, bài viết |
| [api-notifications.md](api-notifications.md) | Notifications | Danh sách thông báo, đánh dấu đã đọc |
| [api-user-statistic.md](api-user-statistic.md) | User Statistic | Thống kê user, content, người được mời |
| [api-quick-actions.md](api-quick-actions.md) | Quick Actions | Danh sách quick actions |
