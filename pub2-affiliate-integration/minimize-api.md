# Tài liệu API tích hợp AccessTrade Pub2

**📊 Google Sheets:** [Danh sách API - Vui lòng comment trực tiếp](https://docs.google.com/spreadsheets/d/1HpRvj9IzCg0LHbhp2UMp2CVZkkyUFcQXi5YZYeeTOnY/edit?gid=319978358#gid=319978358)

## Tổng quan

Tài liệu này mô tả các API cần thiết mà **AccessTrade Pub2** cần cung cấp để tích hợp vào hệ thống Ambassador.

**Mục tiêu:**
- Liên kết tài khoản publisher qua OAuth 2.0 (không cần API mapping riêng)
- Lấy link affiliate theo campaign và user
- Lấy báo cáo hiệu suất (click, đơn hàng, doanh thu/hoa hồng)
- Validate campaign info (optional)

**Tổng số API:** 6 APIs (1 optional)
- 5 OAuth Endpoints (Authorization flow)
- 1 Campaign Info API (Optional)
- 1 Link Generation API
- 3 Report APIs (Clicks, Conversions, Overview)
- 1 Webhook API (Optional - Phase 4)

---

## Sơ đồ tổng quan hệ thống

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AccessTrade Pub2                                  │
│                     (Affiliate Network)                                  │
│                                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │  Publishers │  │  Campaigns   │  │  Merchants  │  │   Reports    │  │
│  │   (Users)   │  │  (Offers)    │  │  (Brands)   │  │  (Analytics) │  │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────────┘  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                 Pub2 OAuth + API Layer                           │    │
│  │  • OAuth 2.0 Server  • Publisher APIs  • Campaign Data           │    │
│  │  • Reports & Analytics  • Token Management                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │ OAuth 2.0     │ OAuth 2.0     │ OAuth 2.0
                    │ + Bearer      │ + Bearer      │ + Bearer
                    ▼               ▼               ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │  Ambassador   │  │  Tfluencers   │  │   Vcreator    │
        │   Platform    │  │   Platform    │  │   Platform    │
        │               │  │               │  │               │
        │ OAuth Client  │  │ OAuth Client  │  │ OAuth Client  │
        └───────────────┘  └───────────────┘  └───────────────┘
                │                   │                   │
                └───────────────────┴───────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  Shared Components    │
                        ├───────────────────────┤
                        │ • OAuth Integration   │
                        │ • Token Management    │
                        │ • User Mapping        │
                        │ • Campaign Mapping    │
                        │ • Link Generation     │
                        │ • Report Sync         │
                        │ • Analytics Display   │
                        └───────────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │   End Users           │
                        │  (Influencers/        │
                        │   Ambassadors)        │
                        │                       │
                        │ → Authorize once      │
                        │ → Auto token refresh  │
                        └───────────────────────┘
```

### Luồng dữ liệu chính

```
1. OAUTH AUTHORIZATION (1 lần duy nhất)
   Influencer → Platform → Pub2 OAuth → Platform
   ┌──────────────────────────────────────────────────┐
   │ 1. User click "Liên kết Pub2"                    │
   │ 2. Platform redirect → Pub2 OAuth login          │
   │ 3. User login + authorize                        │
   │ 4. Pub2 redirect → Platform với code             │
   │ 5. Platform exchange code → access_token         │
   │ 6. Platform lưu tokens cho user                  │
   └──────────────────────────────────────────────────┘

2. USER IDENTIFICATION (Tự động từ OAuth)
   Platform lưu pub2_user_id từ OAuth token
   ┌──────────────┐                          ┌──────────────┐
   │ Platform User│ ←── OAuth /user/me ────  │ Pub2 Publisher│
   │ + OAuth token│     (pub2_user_id)       │      ID      │
   └──────────────┘                          └──────────────┘

3. CAMPAIGN REFERENCE
   Step 1: Admin vào Pub2 Dashboard để xem campaigns
   ┌──────────────────┐
   │ Admin            │
   │   ↓              │
   │ Pub2 Dashboard   │ ← Manual: Xem campaigns, copy campaign_id
   └──────────────────┘

   Step 2: Admin tạo campaign trên Platform + nhập pub2_campaign_id
   ┌─────────────────────────────────────────┐
   │ Platform Campaign (Admin tự tạo)       │
   │ • Title, Description, Content          │
   │ • Terms & Conditions                   │
   │ • pub2_campaign_id (manual input)      │
   └─────────────────────────────────────────┘

4. LINK GENERATION
   Platform → [API 2] → Pub2
   ┌────────────────────────────┐
   │ User + Campaign            │
   │ ──────────────────────────→│
   │                            │
   │ ←─────────────────────────│
   │   Affiliate Link           │
   └────────────────────────────┘

5. REPORTING (2 phương thức)

   A. On-demand (Real-time)
   User Request → Platform → [API 3,4,5] → Pub2
   ┌─────────────────────────────────────┐
   │ User click "Xem báo cáo"            │
   │   ↓                                 │
   │ Platform gọi API Pub2               │
   │   ↓                                 │
   │ Hiển thị data real-time cho user    │
   └─────────────────────────────────────┘

   B. Scheduled Sync (Background)
   Cron Job → Platform → [API 3,4,5] → Pub2
   ┌─────────────────────────────────────┐
   │ Cron job chạy mỗi 1 giờ            │
   │   ↓                                 │
   │ Platform gọi API lấy data mới       │
   │   ↓                                 │
   │ Lưu vào Platform Database           │
   │   ↓                                 │
   │ User xem data từ Platform DB        │
   └─────────────────────────────────────┘
```

### Vai trò các bên

| Hệ thống | Vai trò | Đặc điểm | Trách nhiệm |
|----------|---------|----------|-------------|
| **Pub2** | Affiliate Network | Single platform | • Quản lý merchants & campaigns<br>• Tracking clicks & conversions<br>• Tính toán hoa hồng<br>• Cung cấp OAuth2 + API dữ liệu |
| **Ambassador** | Influencer/Creator Platform | **Multi-tenant**<br>(nhiều brands) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Phục vụ nhiều brands khác nhau |
| **Tfluencers** | Influencer/Creator Platform | Enterprise<br>(1 brand) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Dành riêng cho 1 brand enterprise |
| **Vcreator** | Influencer/Creator Platform | Enterprise<br>(1 brand) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Dành riêng cho 1 brand enterprise |

**Lưu ý:**
- **Ambassador, Tfluencers, Vcreator** có cùng chức năng và vai trò (Influencer/Creator Management Platform)
- **Sự khác biệt chính:**
  - **Ambassador**: Multi-tenant platform, phục vụ nhiều brands/merchants cùng lúc (SaaS model)
  - **Tfluencers & Vcreator**: Single-tenant platform, mỗi instance dành riêng cho 1 brand enterprise cụ thể

### Điểm tích hợp chính

1. **Authentication**: OAuth 2.0 - Influencers authorize Platform truy cập Pub2 account
2. **Publisher Identification**: Platform lưu `pub2_user_id` từ OAuth token response, không cần API mapping riêng
3. **Campaign Reference**:
   - Admin tự soạn thảo nội dung campaign trên platform (Ambassador/Tfluencers/Vcreator)
   - Admin vào dashboard Pub2 để xem thông tin campaign và lấy `campaign_id`
   - Admin nhập `pub2_campaign_id` vào platform để liên kết campaign
4. **Link Generation**: Platforms gọi Pub2 API với access token để tạo affiliate links
5. **Link Generation**: Platforms gọi Pub2 API 2 với Bearer token để tạo affiliate links
6. **Reporting**: Platform lấy dữ liệu báo cáo từ Pub2 theo 2 cách:
   - **On-demand**: Platform gọi API 3-5 khi user request (xem báo cáo)
   - **Scheduled sync**: Platform chạy cron job định kỳ (VD: mỗi 1 giờ) để đồng bộ dữ liệu về database
7. **Display**: Platforms hiển thị dữ liệu cho end users

---

## 1. Cơ chế Authentication

AccessTrade Pub2 cần hỗ trợ OAuth 2.0 authentication để đảm bảo bảo mật và user consent.

### 1.1. OAuth 2.0 Authentication ⭐ RECOMMENDED

**Mô tả:** Sử dụng OAuth 2.0 để liên kết tài khoản Publisher với Platform, có cơ chế refresh token tự động

**Cách thức:**

**Bước 1: Authorization (Liên kết tài khoản lần đầu)**
```
1. Influencer click "Liên kết tài khoản Affiliate" trong Platform
2. Platform redirect đến Pub2 OAuth endpoint:

   GET https://pub2.accesstrade.vn/oauth/authorize
     ?client_id=platform_app_id
     &redirect_uri=https://platform.io/oauth/callback
     &response_type=code
     &scope=publisher.read,affiliate.manage
     &state=random_csrf_token

3. Influencer login vào Pub2 (nếu chưa có session)
4. Influencer authorize Platform truy cập tài khoản Pub2
5. Pub2 redirect về Platform với authorization code:

   GET https://platform.io/oauth/callback
     ?code=AUTH_CODE_123
     &state=random_csrf_token

6. Platform exchange code để lấy tokens:

   POST https://pub2.accesstrade.vn/oauth/token
   Body: {
     grant_type: "authorization_code",
     code: "AUTH_CODE_123",
     client_id: "platform_app_id",
     client_secret: "platform_secret",
     redirect_uri: "https://platform.io/oauth/callback"
   }

   Response: {
     access_token: "ACCESS_TOKEN_XYZ",
     refresh_token: "REFRESH_TOKEN_ABC",
     expires_in: 3600,
     token_type: "Bearer",
     scope: "publisher.read,affiliate.manage",
     pub2_user_id: "PUB_12345"
   }

7. Platform lưu tokens vào database:

   influencer_pub2_accounts {
     influencer_id: "alice_123",
     pub2_user_id: "PUB_12345",
     access_token: "encrypted(ACCESS_TOKEN_XYZ)",
     refresh_token: "encrypted(REFRESH_TOKEN_ABC)",
     token_expires_at: "2026-02-11T14:00:00Z",
     link_method: "oauth",
     link_status: "active"
   }
```

**Bước 2: Sử dụng Access Token**
```
Platform gọi Pub2 API thay mặt influencer:

POST https://pub2.accesstrade.vn/api/v1/affiliate-links
Headers:
  Authorization: Bearer ACCESS_TOKEN_XYZ
  Content-Type: application/json
Body: {
  campaign_id: "camp_456",
  sub_id: "video_789"
}
```

**Bước 3: Refresh Token (Tự động)**
```
Khi access_token hết hạn (expires_in: 3600 giây = 1 giờ):

1. Platform phát hiện token expired (hoặc check token_expires_at)
2. Platform tự động gọi refresh endpoint:

   POST https://pub2.accesstrade.vn/oauth/token
   Body: {
     grant_type: "refresh_token",
     refresh_token: "REFRESH_TOKEN_ABC",
     client_id: "platform_app_id",
     client_secret: "platform_secret"
   }

   Response: {
     access_token: "NEW_ACCESS_TOKEN",
     refresh_token: "NEW_REFRESH_TOKEN",  // Có thể giữ nguyên hoặc rotate
     expires_in: 3600,
     token_type: "Bearer"
   }

3. Platform cập nhật tokens trong database:

   UPDATE influencer_pub2_accounts
   SET access_token = encrypt("NEW_ACCESS_TOKEN"),
       refresh_token = encrypt("NEW_REFRESH_TOKEN"),
       token_expires_at = NOW() + INTERVAL '1 hour',
       updated_at = NOW()
   WHERE influencer_id = "alice_123"

4. Platform retry API call với token mới
```

**Ưu điểm:**
- ✅ Bảo mật cao nhất (industry standard OAuth 2.0)
- ✅ **Explicit user consent** (GDPR/PDPA compliant)
- ✅ **Token tự động refresh** → Influencer không bị logout
- ✅ User có thể revoke access bất cứ lúc nào
- ✅ Không cần chia sẻ password
- ✅ Phân quyền rõ ràng (scopes)

**Nhược điểm:**
- ⚠️ Phức tạp hơn để implement
- ⚠️ Influencer phải thực hiện thêm bước linking (1 lần duy nhất)
- ⚠️ Cần UI flow để handle authorization

**Complete OAuth Flow Example:**

```bash
# Step 1: User clicks "Liên kết tài khoản Pub2" trên Platform
# Platform redirects to:
https://sso.accesstrade.vn/oauth/authorize
  ?client_id=tcb_prod_12345
  &redirect_uri=https://tcb.creator.vn/oauth/callback
  &response_type=code
  &scope=publisher.read,affiliate.manage
  &state=csrf_protection_xyz

# Step 2: User login Pub2 (nếu chưa login)
# Step 3: User authorize Platform

# Step 4: Pub2 redirects back với authorization code
https://tcb.creator.vn/oauth/callback
  ?code=AUTH_CODE_ABC123
  &state=csrf_protection_xyz

# Step 5: Platform backend exchanges code for tokens
POST https://sso.accesstrade.vn/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=AUTH_CODE_ABC123
&client_id=tcb_prod_12345
&client_secret=SECRET_KEY
&redirect_uri=https://tcb.creator.vn/oauth/callback

# Step 6: Pub2 returns tokens
{
  "access_token": "eyJhbGci...",
  "refresh_token": "def502...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "publisher.read affiliate.manage",
  "pub2_user_id": "PUB_12345"
}

# Step 7: Platform lưu tokens vào database
# Step 8: Platform gọi API với access_token
GET https://api.pub2.accesstrade.vn/api/v1/publishers/PUB_12345
Authorization: Bearer eyJhbGci...
```

**Required Pub2 API Endpoints:**
```
1. GET  /oauth/authorize        - Authorization endpoint
2. POST /oauth/token            - Token exchange & refresh endpoint
3. GET  /oauth/user/me          - Get user info endpoint
4. POST /oauth/revoke           - Token revocation endpoint (optional)
```

**OAuth Flow Diagram:**
```
┌─────────────────────────────────────────────────────────────┐
│ LIÊN KẾT TÀI KHOẢN (1 lần duy nhất)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Platform UI                  Pub2 OAuth                    │
│  ┌──────────────┐            ┌──────────────┐              │
│  │ [Liên kết    │            │              │              │
│  │  Affiliate]  │───(1)─────→│ Login Page   │              │
│  │              │            │              │              │
│  │              │            │ Email: ___   │              │
│  │              │            │ Pass:  ___   │              │
│  │              │            │              │              │
│  │              │            │ [Authorize]  │              │
│  │              │←──(2)──────│              │              │
│  │              │   code     │              │              │
│  │              │            └──────────────┘              │
│  │              │                                           │
│  │ Backend      │            Pub2 Token API                 │
│  │ ─────(3)────→            ──────(4)─────→                │
│  │   exchange code          returns tokens                 │
│  │              │                                           │
│  │ ✓ Đã liên kết│                                           │
│  └──────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TẠO AFFILIATE LINK (Tự động dùng token)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. User click "Tạo link"                                   │
│  2. Platform lấy access_token từ DB                         │
│  3. Platform gọi Pub2 API với Bearer token                  │
│  4. Pub2 trả về affiliate link                              │
│  5. Platform hiển thị link cho user                         │
│                                                             │
│  → User KHÔNG biết gì về OAuth flow này                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOKEN REFRESH (Tự động, background)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cron job chạy mỗi 30 phút:                                 │
│  1. Lấy tất cả tokens sắp hết hạn (< 5 phút)               │
│  2. Gọi refresh endpoint cho từng token                     │
│  3. Cập nhật tokens mới vào database                        │
│                                                             │
│  → Influencer không bao giờ bị logout                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Lý do chọn OAuth 2.0

**⭐ KHUYẾN NGHỊ: Sử dụng OAuth 2.0 Authentication**

**Ưu điểm:**
- ✅ **Bảo mật cao nhất** - Industry standard OAuth 2.0
- ✅ **Explicit user consent** - GDPR/PDPA compliant
- ✅ **Token tự động refresh** → Influencer không bị logout
- ✅ **User control** - Có thể revoke access bất cứ lúc nào
- ✅ **Không chia sẻ password** - Secure delegation
- ✅ **Phân quyền rõ ràng** - Scopes xác định permissions
- ✅ **Audit trail** - Track được user authorization history

**Cách thức hoạt động:**
- Influencer click "Liên kết tài khoản Pub2" trong Platform
- Platform redirect đến Pub2 OAuth login page
- Influencer authorize Platform truy cập tài khoản Pub2
- Pub2 trả về access_token & refresh_token
- Platform lưu tokens và tự động refresh khi hết hạn
- Platform sử dụng access_token để gọi Pub2 APIs thay mặt Influencer

**Token Management:**
- Platform backend lưu trữ `access_token` và `refresh_token` cho mỗi influencer
- Platform tự động refresh token khi gần hết hạn (< 5 phút)
- Platform sử dụng access_token để gọi Pub2 APIs thay mặt influencer
- Influencer KHÔNG cần quản lý token, chỉ cần authorize 1 lần

**Required Pub2 Support:**
- OAuth 2.0 Authorization Server (RFC 6749 compliant)
- Auto token refresh mechanism (refresh_token grant)
- Token revocation endpoint (optional)
- Scope-based permissions
- CORS support cho OAuth callbacks

---

## 2. OAuth 2.0 Endpoints

Pub2 cần cung cấp các OAuth endpoints sau:

### OAuth 1: Authorization Endpoint

**Mục đích:** Redirect influencer đến trang login & authorization của Pub2

**HTTP Method:** `GET`

**URL đề xuất:** `/oauth/authorize`

**Query Parameters:**
- `client_id`: OAuth client ID của platform (TCB/AMB/VF)
- `redirect_uri`: Callback URL của platform
- `response_type`: `code` (Authorization Code flow)
- `scope`: Permissions requested (VD: `publisher.read,affiliate.manage`)
- `state`: CSRF protection token

**Example:**
```
GET https://sso.accesstrade.vn/oauth/authorize
  ?client_id=tcb_prod_12345
  &redirect_uri=https://tcb.creator.vn/oauth/callback
  &response_type=code
  &scope=publisher.read,affiliate.manage
  &state=random_csrf_token_xyz
```

**User Experience:**
- Pub2 hiển thị login page (nếu chưa login)
- Sau khi login, hiển thị consent screen
- User authorize → Redirect về platform với `code`

---

### OAuth 2: Token Exchange Endpoint

**Mục đích:** Exchange authorization code để lấy access_token

**HTTP Method:** `POST`

**URL đề xuất:** `/oauth/token`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Authorization Code Grant):**
```
grant_type=authorization_code
&code={authorization_code}
&client_id={client_id}
&client_secret={client_secret}
&redirect_uri={redirect_uri}
```

**Response Success (200):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": "publisher.read affiliate.manage",
  "pub2_user_id": "PUB_12345"
}
```

---

### OAuth 3: Token Refresh Endpoint

**Mục đích:** Refresh access token khi hết hạn

**HTTP Method:** `POST`

**URL đề xuất:** `/oauth/token`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Refresh Token Grant):**
```
grant_type=refresh_token
&refresh_token={refresh_token}
&client_id={client_id}
&client_secret={client_secret}
```

**Response Success (200):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": "publisher.read affiliate.manage"
}
```

**Lưu ý:**
- Platform tự động refresh token khi gần hết hạn (< 5 phút)
- Refresh token có thể rotate (Pub2 trả về refresh_token mới)

---

### OAuth 4: Get User Info Endpoint

**Mục đích:** Lấy thông tin publisher sau khi authorize

**HTTP Method:** `GET`

**URL đề xuất:** `/oauth/user/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response Success (200):**
```json
{
  "principal": {
    "id": 12345,
    "username": "alice_publisher",
    "email": "alice@example.com",
    "firstName": "Alice",
    "lastName": "Nguyen",
    "phone": "+84912345678",
    "dateOfBirth": "1995-01-15",
    "gender": 1,
    "address": "123 Le Loi, HCM"
  }
}
```

---

### OAuth 5: Token Revocation Endpoint (Optional)

**Mục đích:** User revoke access token

**HTTP Method:** `POST`

**URL đề xuất:** `/oauth/revoke`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
token={access_token or refresh_token}
&client_id={client_id}
&client_secret={client_secret}
```

**Response Success (200):**
```json
{
  "success": true
}
```

---

### OAuth Scopes

Pub2 cần hỗ trợ các scopes sau:

| Scope | Mô tả | Permissions |
|-------|-------|-------------|
| `publisher.read` | Đọc thông tin publisher | GET /publishers, GET /oauth/user/me |
| `affiliate.manage` | Quản lý affiliate links | POST /affiliate-links, GET /reports/* |
| `campaign.read` | Đọc campaigns | GET /campaigns/* |

---

## 3. Danh sách API cần thiết

**⚠️ LƯU Ý QUAN TRỌNG:**
- **TẤT CẢ** các API bên dưới đều yêu cầu OAuth 2.0 authentication
- Header bắt buộc: `Authorization: Bearer {access_token}`
- Access token được lấy từ OAuth flow (xem section 2)
- Pub2 tự động identify publisher từ access_token
- Platform backend quản lý token lifecycle (refresh, revoke, etc.)

**⚠️ KHÔNG CẦN Publisher Mapping API:**
- OAuth `/user/me` (OAuth 4) đã trả đủ thông tin publisher (id, email, username, phone, etc.)
- Platform lưu `pub2_user_id` từ OAuth token response vào database
- Các API bên dưới tự động identify publisher từ Bearer token
- Pub2 không cần API riêng để mapping external_user_id → Đơn giản hóa tích hợp

---

### API 1: Lấy thông tin chi tiết Campaign (Optional)

**Mục đích:** Lấy thông tin chi tiết của một campaign cụ thể trên Pub2 để hiển thị hoặc validation

**Use case:**
- Admin đã có `pub2_campaign_id` (lấy từ Pub2 Dashboard)
- Platform cần validate campaign_id có tồn tại không
- Platform muốn hiển thị thông tin campaign từ Pub2 (tên, mô tả, commission rate)

**Lưu ý:** API này là **OPTIONAL**. Nếu không cần validate hoặc hiển thị thông tin từ Pub2, có thể bỏ qua API này.

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/campaigns/{campaign_id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Path Parameters:**
- `campaign_id`: ID của campaign trên Pub2

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "campaign_id": "string",
    "campaign_name": "string",
    "merchant_name": "string",
    "category": "string",
    "commission_rate": "string",
    "status": "active",
    "description": "string",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
}
```

**Response Error (404):**
```json
{
  "success": false,
  "error": {
    "code": "CAMPAIGN_NOT_FOUND",
    "message": "Campaign not found"
  }
}
```

**Ví dụ luồng tạo campaign trên Platform:**

```
Bước 1: Admin đăng nhập Pub2 Dashboard
→ Xem danh sách campaigns
→ Copy campaign_id: "pub2_camp_456"

Bước 2: Admin tạo campaign trên Platform (Ambassador/Tfluencers/Vcreator)
Platform Campaign {
  id: "platform_campaign_123",
  title: "Chương trình đại sứ thương hiệu Shopee Tết 2025",
  description: "Tham gia ngay để nhận hoa hồng hấp dẫn...",
  terms: "Điều khoản tham gia chương trình...",
  start_date: "2025-01-01",
  end_date: "2025-02-28",

  // Admin nhập manual pub2_campaign_id
  pub2_campaign_id: "pub2_camp_456",

  // Các thông tin khác do Platform quản lý
  target_audience: "Influencers có > 10k followers",
  kpi_requirements: "Tối thiểu 100 clicks/tháng"
}

Bước 2.5 (Optional): Platform validate campaign_id
→ Gọi API 1: GET /api/v1/campaigns/pub2_camp_456
→ Nếu 404: Thông báo admin nhập sai campaign_id
→ Nếu 200: Hiển thị tên campaign từ Pub2 để admin confirm

Bước 3: Khi user yêu cầu tạo affiliate link
→ Platform gọi API 2 với pub2_campaign_id="pub2_camp_456"
→ Pub2 trả về affiliate link
→ Platform hiển thị link cho user kèm theo nội dung campaign nội bộ
```

---

### API 2: Lấy Link Affiliate

**Mục đích:** Tạo link affiliate cho campaign - Publisher được identify tự động từ Bearer token

**HTTP Method:** `POST`

**URL đề xuất:** `/api/v1/affiliate-links`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Payload:**
```json
{
  "campaign_id": "string",
  "product_url": "string (optional)",
  "sub_id": "string (optional)"
}
```

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "affiliate_link": "string",
    "campaign_id": "string",
    "pub2_user_id": "string",
    "tracking_params": {
      "sub_id": "string",
      "utm_source": "string",
      "utm_medium": "string"
    },
    "expires_at": "2025-12-31T23:59:59Z"
  }
}
```

**Response Error (400/404):**
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

**Lưu ý:**
- Link có thể được tái sử dụng (idempotent)
- `product_url`: URL sản phẩm gốc cần tạo link affiliate
- `sub_id`: tracking ID tùy chỉnh của đối tác

---

### API 3: Lấy báo cáo Click

**Mục đích:** Lấy thống kê số lượt click theo publisher và campaign

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem báo cáo (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để đồng bộ về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/clicks`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `campaign_id`: ID campaign (optional, để trống = tất cả campaigns)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)
- `group_by`: nhóm theo (day, campaign, default: day)

**Lưu ý:** Publisher được identify tự động từ Bearer token, không cần truyền `external_user_id`

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_clicks": 1000,
      "unique_clicks": 850
    },
    "details": [
      {
        "date": "2025-01-01",
        "campaign_id": "string",
        "campaign_name": "string",
        "clicks": 100,
        "unique_clicks": 85
      }
    ]
  }
}
```

---

### API 4: Lấy báo cáo Conversion (Đơn hàng)

**Mục đích:** Lấy thống kê đơn hàng và doanh thu theo publisher và campaign

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem báo cáo (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để đồng bộ về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/conversions`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `campaign_id`: ID campaign (optional)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)
- `status`: filter theo status (pending, approved, rejected, all)
- `group_by`: nhóm theo (day, campaign, status, default: day)

**Lưu ý:** Publisher được identify tự động từ Bearer token, không cần truyền `external_user_id`

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_orders": 50,
      "total_revenue": 100000000,
      "total_commission": 5000000,
      "pending_orders": 10,
      "approved_orders": 35,
      "rejected_orders": 5
    },
    "details": [
      {
        "date": "2025-01-01",
        "campaign_id": "string",
        "campaign_name": "string",
        "order_id": "string",
        "order_value": 2000000,
        "commission": 100000,
        "status": "approved",
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-02T10:00:00Z"
      }
    ]
  }
}
```

**Giải thích fields:**
- `total_revenue`: Tổng giá trị đơn hàng (VNĐ)
- `total_commission`: Tổng hoa hồng nhận được (VNĐ)
- `status`: pending (chờ duyệt), approved (đã duyệt), rejected (bị từ chối)

---

### API 5: Lấy báo cáo tổng hợp

**Mục đích:** Lấy báo cáo tổng hợp hiệu suất (click + conversion) của publisher

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem dashboard tổng quan (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để cập nhật metrics về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/overview`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `campaign_id`: ID campaign (optional)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)

**Lưu ý:** Publisher được identify tự động từ Bearer token, không cần truyền `external_user_id`

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "publisher": {
      "pub2_user_id": "string"
    },
    "period": {
      "from_date": "2025-01-01",
      "to_date": "2025-01-31"
    },
    "metrics": {
      "clicks": {
        "total": 1000,
        "unique": 850
      },
      "conversions": {
        "total_orders": 50,
        "conversion_rate": 5.0,
        "total_revenue": 100000000,
        "total_commission": 5000000,
        "avg_order_value": 2000000,
        "avg_commission": 100000
      },
      "status_breakdown": {
        "pending": {
          "orders": 10,
          "revenue": 20000000,
          "commission": 1000000
        },
        "approved": {
          "orders": 35,
          "revenue": 70000000,
          "commission": 3500000
        },
        "rejected": {
          "orders": 5,
          "revenue": 10000000,
          "commission": 500000
        }
      }
    },
    "campaigns": [
      {
        "campaign_id": "string",
        "campaign_name": "string",
        "clicks": 200,
        "orders": 10,
        "revenue": 20000000,
        "commission": 1000000
      }
    ]
  }
}
```

---

### API 6: Webhook để nhận thông báo (Optional - giai đoạn 2)

**Mục đích:** Pub2 push thông báo real-time khi có sự kiện conversion

**HTTP Method:** `POST`

**URL:** Do đối tác cung cấp

**Headers:**
```
X-Webhook-Signature: {hmac_signature}
Content-Type: application/json
```

**Request Payload:**
```json
{
  "event": "conversion.approved",
  "timestamp": "2025-01-01T10:00:00Z",
  "data": {
    "pub2_user_id": "string",
    "campaign_id": "string",
    "order_id": "string",
    "order_value": 2000000,
    "commission": 100000,
    "status": "approved",
    "created_at": "2025-01-01T10:00:00Z"
  }
}
```

**Event types:**
- `conversion.created`: Đơn hàng mới được tạo
- `conversion.approved`: Đơn hàng được duyệt
- `conversion.rejected`: Đơn hàng bị từ chối

**Response Expected (200):**
```json
{
  "success": true
}
```

---

## 4. Yêu cầu kỹ thuật chung

### 3.1. Response Format

Tất cả API phải trả về JSON với format chuẩn:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### 3.2. HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid API key)
- `403`: Forbidden (không có quyền truy cập)
- `404`: Not Found
- `409`: Conflict (duplicate resource)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

### 3.3. Rate Limiting

- Giới hạn: 1000 requests/hour per API key
- Header response khi bị rate limit:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1640000000
  ```

### 3.4. API Versioning

- Sử dụng URL versioning: `/api/v1/...`
- Thông báo trước 3 tháng khi deprecate API version

### 4.5. Security

- Chỉ hỗ trợ HTTPS
- OAuth 2.0 với PKCE (Proof Key for Code Exchange) - recommended
- Access token expiry: 1 giờ (3600 giây)
- Refresh token expiry: 30 ngày
- CSRF protection qua `state` parameter
- Token encryption in transit & at rest
- Request signature verification cho webhook (HMAC SHA-256)

### 4.6. Environment

**Sandbox:**
- OAuth: `https://sso-sandbox.accesstrade.vn`
- API: `https://api-sandbox.pub2.accesstrade.vn`

**Production:**
- OAuth: `https://sso.accesstrade.vn`
- API: `https://api.pub2.accesstrade.vn`

---

## 5. Kế hoạch triển khai

| Giai đoạn | Endpoints cần thiết | Timeline |
|-----------|---------------------|----------|
| Phase 1 | OAuth 1-5 (Authorization flow + User info) | Week 1-2 |
| Phase 2 | API 1-2 (Campaign info + Link generation) | Week 2-3 |
| Phase 3 | API 3-5 (Reports: Clicks, Conversions, Overview) | Week 3-4 |
| Phase 4 | API 6 (Webhook - Optional) | Week 5+ |

---

## 6. Checklist xác nhận từ Pub2

### OAuth 2.0 Setup
- [ ] Xác nhận OAuth 2.0 endpoints (authorize, token, user/me)
- [ ] Cung cấp OAuth client credentials cho từng platform:
  - [ ] Techcombank: `client_id`, `client_secret`
  - [ ] Ambassador: `client_id`, `client_secret`
  - [ ] Vinfast: `client_id`, `client_secret`
- [ ] Xác nhận supported scopes
- [ ] Xác nhận token expiry settings (access: 1h, refresh: 30 days)
- [ ] Test OAuth flow trên sandbox environment

### API Endpoints
- [ ] Xác nhận API base URL (sandbox & production)
- [ ] Cung cấp API documentation chi tiết (OpenAPI/Swagger)
- [ ] Xác nhận schema response cho từng endpoint
- [ ] Xác nhận error codes và error messages
- [ ] Cung cấp sample data để test

### Technical Requirements
- [ ] Xác nhận rate limiting (requests/hour per token)
- [ ] Cung cấp tài liệu SLA (uptime, response time)
- [ ] Webhook endpoint requirements và signature verification
- [ ] IP whitelist requirements (nếu có)
- [ ] Hỗ trợ môi trường sandbox đầy đủ chức năng

---

*Phiên bản: v2.0 - Tài liệu API chi tiết cho tích hợp*