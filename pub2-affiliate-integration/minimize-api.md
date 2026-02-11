# Tài liệu API tích hợp AccessTrade Pub2

## Tổng quan

Tài liệu này mô tả các API cần thiết mà **AccessTrade Pub2** cần cung cấp để tích hợp vào hệ thống Ambassador.

**Mục tiêu:**
- Đồng bộ định danh user giữa hai hệ thống
- Lấy link affiliate theo campaign và user
- Lấy báo cáo hiệu suất (click, đơn hàng, doanh thu/hoa hồng)
- Cấu hình và ánh xạ campaign giữa hai bên

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
│  │                      Pub2 API Layer                              │    │
│  │  • Publisher Management  • Campaign Data  • Reports & Stats     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │  Ambassador   │  │  Tfluencers   │  │   Vcreator    │
        │   Platform    │  │   Platform    │  │   Platform    │
        └───────────────┘  └───────────────┘  └───────────────┘
                │                   │                   │
                └───────────────────┴───────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  Shared Components    │
                        ├───────────────────────┤
                        │ • User Management     │
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
                        └───────────────────────┘
```

### Luồng dữ liệu chính

```
1. USER MAPPING
   Ambassador/Tfluencers/Vcreator → [API 1] → Pub2
   ┌──────────────┐                          ┌──────────────┐
   │ Platform User│ ─── external_user_id ──→ │ Pub2 Publisher│
   │      ID      │ ←── pub2_user_id ─────── │      ID      │
   └──────────────┘                          └──────────────┘

2. CAMPAIGN REFERENCE
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

3. LINK GENERATION
   Platform → [API 4] → Pub2
   ┌────────────────────────────┐
   │ User + Campaign            │
   │ ──────────────────────────→│
   │                            │
   │ ←─────────────────────────│
   │   Affiliate Link           │
   └────────────────────────────┘

4. REPORTING (2 phương thức)

   A. On-demand (Real-time)
   User Request → Platform → [API 5,6,7] → Pub2
   ┌─────────────────────────────────────┐
   │ User click "Xem báo cáo"            │
   │   ↓                                 │
   │ Platform gọi API Pub2               │
   │   ↓                                 │
   │ Hiển thị data real-time cho user    │
   └─────────────────────────────────────┘

   B. Scheduled Sync (Background)
   Cron Job → Platform → [API 5,6,7] → Pub2
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
| **Pub2** | Affiliate Network | Single platform | • Quản lý merchants & campaigns<br>• Tracking clicks & conversions<br>• Tính toán hoa hồng<br>• Cung cấp API dữ liệu |
| **Ambassador** | Influencer/Creator Platform | **Multi-tenant**<br>(nhiều brands) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Phục vụ nhiều brands khác nhau |
| **Tfluencers** | Influencer/Creator Platform | Enterprise<br>(1 brand) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Dành riêng cho 1 brand enterprise |
| **Vcreator** | Influencer/Creator Platform | Enterprise<br>(1 brand) | • Quản lý influencers/creators<br>• Tạo campaigns nội bộ<br>• Hiển thị performance<br>• Dành riêng cho 1 brand enterprise |

**Lưu ý:**
- **Ambassador, Tfluencers, Vcreator** có cùng chức năng và vai trò (Influencer/Creator Management Platform)
- **Sự khác biệt chính:**
  - **Ambassador**: Multi-tenant platform, phục vụ nhiều brands/merchants cùng lúc (SaaS model)
  - **Tfluencers & Vcreator**: Single-tenant platform, mỗi instance dành riêng cho 1 brand enterprise cụ thể

### Điểm tích hợp chính

1. **Authentication**: Pub2 cấp API Key cho từng platform
2. **Publisher Mapping**: Mỗi platform đồng bộ users của mình sang Pub2
3. **Campaign Reference**:
   - Admin tự soạn thảo nội dung campaign trên platform (Ambassador/Tfluencers/Vcreator)
   - Admin vào dashboard Pub2 để xem thông tin campaign và lấy `campaign_id`
   - Admin nhập `pub2_campaign_id` vào platform để liên kết campaign
4. **Link Generation**: Platforms gọi Pub2 để tạo affiliate links
5. **Reporting**: Platform lấy dữ liệu báo cáo từ Pub2 theo 2 cách:
   - **On-demand**: Platform gọi API khi user request (xem báo cáo)
   - **Scheduled sync**: Platform chạy cron job định kỳ (VD: mỗi 1 giờ) để đồng bộ dữ liệu về database
6. **Display**: Platforms hiển thị dữ liệu cho end users

---

## 1. Cơ chế Authentication

AccessTrade Pub2 cần hỗ trợ một trong các phương thức authentication sau:

### 1.1. Platform API Key Authentication ⭐ RECOMMENDED

**Mô tả:** Sử dụng API Key dành riêng cho từng nền tảng đối tác

**Cách thức:**
- Pub2 cấp một API Key cho toàn bộ nền tảng đối tác (Ambassador/Tfluencers/Vcreator)
- API Key được truyền qua header `X-API-Key: {api_key}`
- Nền tảng đối tác sử dụng `external_user_id` để xác định publisher cụ thể trong mỗi API call

**Ưu điểm:**
- ✅ Đơn giản hóa việc quản lý authentication
- ✅ Chỉ cần một API Key cho toàn bộ nền tảng
- ✅ **Publisher (Influencer/Creator) không cần biết đến token**
- ✅ **Publisher không cần tạo tài khoản hoặc login vào Pub2**
- ✅ Platform quản lý toàn bộ authentication flow

**Nhược điểm:**
- ⚠️ Cần bảo mật API Key cẩn thận (lưu encrypted trong môi trường)
- ⚠️ Phụ thuộc vào `external_user_id` để phân biệt publisher

**Use case:**
```
Influencer "Alice" trên Ambassador Platform:
├─ Alice login vào Ambassador Platform (email/password)
├─ Alice tạo affiliate link trong Platform
└─ Ambassador Platform gọi Pub2 API:
    Headers: X-API-Key: amb_prod_xxxxx
    Body: { external_user_id: "alice_123", campaign_id: "camp_456" }
    → Pub2 trả về link cho Alice
    → Alice KHÔNG cần biết gì về Pub2 authentication
```

---

### 1.2. OAuth 2.0 Authentication (Advanced)

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

**Required Pub2 API Endpoints:**
```
1. GET  /oauth/authorize        - Authorization endpoint
2. POST /oauth/token            - Token exchange & refresh endpoint
3. POST /oauth/revoke           - Token revocation endpoint (optional)
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

### So sánh & Khuyến nghị

| Tiêu chí | Platform API Key | OAuth 2.0 ⭐ |
|----------|------------------|-----------|
| **Độ phức tạp implement** | ⭐ Đơn giản | ⭐⭐⭐ Phức tạp |
| **UX cho Influencer** | ⭐⭐⭐ Tốt nhất | ⭐⭐ Tốt (1 step linking) |
| **Bảo mật** | ⭐⭐ Tốt | ⭐⭐⭐ Tốt nhất |
| **GDPR Compliance** | ⭐⭐ OK | ⭐⭐⭐ Tốt nhất |
| **Onboarding friction** | ✅ Zero | ⚠️ 1 extra step |
| **Token management** | Platform quản lý | Auto refresh |
| **Token expiration** | API key không expire | Auto refresh |
| **Tình trạng** | Cần implement mới | ✅ **Đã có sẵn trên Pub2** |

**⭐ KHUYẾN NGHỊ: Sử dụng OAuth 2.0 Authentication**

**Lý do:**
- ✅ Pub2 đã có sẵn infrastructure OAuth 2.0
- ✅ Không cần implement thêm authentication layer mới
- ✅ Bảo mật cao nhất (industry standard)
- ✅ GDPR/PDPA compliant
- ✅ Token tự động refresh → Influencer không bị logout
- ✅ User có thể revoke access bất cứ lúc nào

**Trade-off:**
- ⚠️ Influencer cần thực hiện bước linking 1 lần (acceptable UX)
- ⚠️ Platform cần implement OAuth flow (standard, có nhiều library)

**Khi nào chọn Platform API Key:**
- Nếu Pub2 chưa có OAuth infrastructure
- Nếu cần go-live rất nhanh (< 2 tuần)
- Nếu số lượng influencer ít (< 100 users)

---

## 2. Danh sách API cần thiết

### API 1: Tạo/Ánh xạ Publisher

**Mục đích:** Đồng bộ thông tin publisher từ hệ thống đối tác sang Pub2

**⚠️ QUAN TRỌNG - Sử dụng lại authentication có sẵn của Platform:**

**Platform đã có JWT authentication:**
- ✅ Login endpoint: `POST /users/login` (file: `pkg/public/handler/user.go`)
- ✅ JWT middleware: `internal/middleware/jwt.go`
- ✅ Token expiry: 7 ngày
- ✅ API này chỉ để **đồng bộ** user đã login → Pub2

**Flow thực tế - Sử dụng authentication có sẵn:**

```
┌─────────────────────────────────────────────────────────────────┐
│ BƯỚC 1: User login Platform (đã có sẵn)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ POST /users/login                                               │
│ Body: { email: "alice@example.com", password: "***" }          │
│                                                                 │
│ Response (từ code có sẵn):                                     │
│ {                                                               │
│   id: "675abc123",                                              │
│   token: "eyJhbGci...",  // JWT (exp: 7 days)                  │
│   isFirstLogin: false                                           │
│ }                                                               │
│                                                                 │
│ → User authenticated, frontend lưu token                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BƯỚC 2: User click "Kích hoạt Affiliate"                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Frontend: POST /users/activate-affiliate                        │
│ Headers: Authorization: Bearer {platform_jwt_token}             │
│                                                                 │
│ Backend (handler mới cần implement):                            │
│ ┌─────────────────────────────────────────────────────┐        │
│ │ 1. Middleware verify JWT → Extract user_id          │        │
│ │ 2. Get user từ MongoDB (email, name, phone)         │        │
│ │ 3. Check table influencer_pub2_accounts:            │        │
│ │    IF exists → Return pub2_user_id                  │        │
│ │    ELSE → Continue step 4                           │        │
│ │                                                      │        │
│ │ 4. Call Pub2 API:                                   │        │
│ │    POST /api/v1/publishers/mapping                  │        │
│ │    Headers: X-API-Key: {platform_api_key}          │        │
│ │    Body: {                                          │        │
│ │      external_user_id: user.ID,                    │        │
│ │      email: user.Email,                            │        │
│ │      full_name: user.Name,                         │        │
│ │      phone: user.Phone                             │        │
│ │    }                                                │        │
│ │                                                      │        │
│ │ 5. Pub2 Response:                                   │        │
│ │    { pub2_user_id: "PUB_12345", ... }              │        │
│ │                                                      │        │
│ │ 6. Save to MongoDB:                                 │        │
│ │    db.influencer_pub2_accounts.insertOne({         │        │
│ │      influencer_id: user.ID,                       │        │
│ │      pub2_user_id: "PUB_12345",                    │        │
│ │      linked_at: NOW()                              │        │
│ │    })                                               │        │
│ │                                                      │        │
│ │ 7. Return to frontend:                              │        │
│ │    { success: true, pub2_user_id: "PUB_12345" }    │        │
│ └─────────────────────────────────────────────────────┘        │
│                                                                 │
│ → User sẵn sàng tạo affiliate links                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BƯỚC 3: Các lần sau - Tạo affiliate link                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ POST /campaigns/{id}/generate-link                              │
│ Headers: Authorization: Bearer {platform_jwt_token}             │
│                                                                 │
│ Backend:                                                        │
│ 1. Verify JWT → user_id                                        │
│ 2. Get pub2_user_id from influencer_pub2_accounts              │
│ 3. Call Pub2 API 4 (tạo link)                                  │
│ 4. Return affiliate link                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Code cần implement (Go backend):**

```go
// File: pkg/public/handler/user.go (thêm handler mới)

// ActivateAffiliate godoc
// @tags Users
// @summary ActivateAffiliate - Kích hoạt tính năng affiliate
// @id user-activate-affiliate
// @security ApiKeyAuth
// @accept json
// @produce json
// @success 200 {object} response.ActivateAffiliateResponse
// @router /users/activate-affiliate [post]
func (u userImpl) ActivateAffiliate(c echo.Context) error {
	var (
		cc     = echocustom.EchoGetCustomCtx(c)
		ctx    = cc.GetRequestCtx()
		userId = cc.GetCurrentUserID() // Từ JWT middleware
		s      = service.User()
	)

	// Check đã link chưa
	mapping := s.GetPub2Mapping(ctx, userId)
	if mapping != nil {
		return cc.Response200(echo.Map{
			"pub2_user_id":  mapping.Pub2UserID,
			"already_linked": true,
		}, "Affiliate đã được kích hoạt")
	}

	// Tạo mapping mới
	pub2UserId, err := s.CreatePub2Mapping(ctx, userId)
	if err != nil {
		return cc.Response400(nil, err.Error())
	}

	return cc.Response200(echo.Map{
		"pub2_user_id":  pub2UserId,
		"already_linked": false,
	}, "Kích hoạt affiliate thành công")
}
```

```go
// File: pkg/public/router/user.go (thêm route)

g.POST("/activate-affiliate", h.ActivateAffiliate, a.RequiredLogin)
```

**HTTP Method:** `POST`

**URL đề xuất:** `/api/v1/publishers/mapping`

**Headers:**
```
X-API-Key: {api_key}  # Platform API key, KHÔNG phải user token
Content-Type: application/json
```

**Request Payload:**
```json
{
  "external_user_id": "string",  // Platform user ID
  "email": "string",              // User email (để match với Pub2)
  "full_name": "string",
  "phone": "string"               // Optional, để match với Pub2
}
```

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "pub2_user_id": "string",      // Pub2's internal publisher ID
    "external_user_id": "string",  // Platform's user ID (echo back)
    "email": "string",
    "full_name": "string",
    "status": "active",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

**Response Error (400/409):**
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
- ✅ **Idempotent**: Gọi nhiều lần với cùng `external_user_id` không tạo duplicate
- ✅ **Auto-matching**: Nếu email đã tồn tại trong Pub2 → Link với existing publisher
- ✅ **Auto-creation**: Nếu email chưa tồn tại → Tạo publisher mới trên Pub2
- ⚠️ **Platform authentication**: Platform đã handle user login, API này chỉ sync data

---

### API 2: Lấy thông tin Publisher

**Mục đích:** Lấy thông tin chi tiết của publisher đã được ánh xạ

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/publishers/{external_user_id}`

**Headers:**
```
X-API-Key: {api_key}
```

**Path Parameters:**
- `external_user_id`: ID của publisher trong hệ thống đối tác

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "pub2_user_id": "string",
    "external_user_id": "string",
    "email": "string",
    "full_name": "string",
    "status": "active",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

**Response Error (404):**
```json
{
  "success": false,
  "error": {
    "code": "PUBLISHER_NOT_FOUND",
    "message": "Publisher not found"
  }
}
```

---

### API 3: Lấy thông tin chi tiết Campaign (Optional)

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
X-API-Key: {api_key}
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
→ Gọi API 3: GET /api/v1/campaigns/pub2_camp_456
→ Nếu 404: Thông báo admin nhập sai campaign_id
→ Nếu 200: Hiển thị tên campaign từ Pub2 để admin confirm

Bước 3: Khi user yêu cầu tạo affiliate link
→ Platform gọi API 4 với pub2_campaign_id="pub2_camp_456"
→ Pub2 trả về affiliate link
→ Platform hiển thị link cho user kèm theo nội dung campaign nội bộ
```

---

### API 4: Lấy Link Affiliate

**Mục đích:** Tạo link affiliate cho một publisher cụ thể với một campaign cụ thể

**HTTP Method:** `POST`

**URL đề xuất:** `/api/v1/affiliate-links`

**Headers:**
```
X-API-Key: {api_key}
Content-Type: application/json
```

**Request Payload:**
```json
{
  "external_user_id": "string",
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
    "external_user_id": "string",
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

### API 5: Lấy báo cáo Click

**Mục đích:** Lấy thống kê số lượt click theo publisher và campaign

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem báo cáo (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để đồng bộ về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/clicks`

**Headers:**
```
X-API-Key: {api_key}
```

**Query Parameters:**
- `external_user_id`: ID publisher (bắt buộc)
- `campaign_id`: ID campaign (optional, để trống = tất cả campaigns)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)
- `group_by`: nhóm theo (day, campaign, default: day)

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

### API 6: Lấy báo cáo Conversion (Đơn hàng)

**Mục đích:** Lấy thống kê đơn hàng và doanh thu theo publisher và campaign

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem báo cáo (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để đồng bộ về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/conversions`

**Headers:**
```
X-API-Key: {api_key}
```

**Query Parameters:**
- `external_user_id`: ID publisher (bắt buộc)
- `campaign_id`: ID campaign (optional)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)
- `status`: filter theo status (pending, approved, rejected, all)
- `group_by`: nhóm theo (day, campaign, status, default: day)

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

### API 7: Lấy báo cáo tổng hợp

**Mục đích:** Lấy báo cáo tổng hợp hiệu suất (click + conversion) của publisher

**Phương thức sử dụng:**
- **On-demand**: Gọi khi user request xem dashboard tổng quan (real-time)
- **Scheduled sync**: Gọi định kỳ (cron job) để cập nhật metrics về database

**HTTP Method:** `GET`

**URL đề xuất:** `/api/v1/reports/overview`

**Headers:**
```
X-API-Key: {api_key}
```

**Query Parameters:**
- `external_user_id`: ID publisher (bắt buộc)
- `campaign_id`: ID campaign (optional)
- `from_date`: ngày bắt đầu (YYYY-MM-DD, bắt buộc)
- `to_date`: ngày kết thúc (YYYY-MM-DD, bắt buộc)

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "publisher": {
      "pub2_user_id": "string",
      "external_user_id": "string"
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

### API 8: Webhook để nhận thông báo (Optional - giai đoạn 2)

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
    "external_user_id": "string",
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

## 3. Yêu cầu kỹ thuật chung

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

### 3.5. Security

- Chỉ hỗ trợ HTTPS
- API Key phải được rotate định kỳ (khuyến nghị 6 tháng/lần)
- IP Whitelist (optional)
- Request signature verification cho webhook

### 3.6. Environment

- **Sandbox:** `https://sandbox.pub2.accesstrade.vn`
- **Production:** `https://pub2.accesstrade.vn`

---

## 4. Kế hoạch triển khai

| Giai đoạn | API cần thiết | Timeline |
|-----------|---------------|----------|
| Phase 1 | API 1, 2, 3, 4 | Week 1-2 |
| Phase 2 | API 5, 6, 7 | Week 3 |
| Phase 3 | API 8 (Webhook) | Week 4+ |

---

## 5. Checklist xác nhận từ Pub2

- [ ] Xác nhận phương thức authentication (Publisher Token hoặc Platform API Key)
- [ ] Cung cấp API Key sandbox để test
- [ ] Xác nhận URL endpoint chính xác
- [ ] Xác nhận schema response chi tiết
- [ ] Cung cấp tài liệu SLA và rate limit
- [ ] Cung cấp sample data để test
- [ ] Hỗ trợ môi trường sandbox để test tích hợp

---

*Phiên bản: v2.0 - Tài liệu API chi tiết cho tích hợp*