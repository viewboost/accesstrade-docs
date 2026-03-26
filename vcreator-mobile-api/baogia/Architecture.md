# VCreator V-App Mini App — Architecture

## 1. Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────┐
│                    V-App (Native)                    │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │              WebView Container                 │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │      VCreator Mini App (Frontend)       │  │  │
│  │  │      UmiJS 3 + React + TypeScript       │  │  │
│  │  │      (Build từ frontend-green)          │  │  │
│  │  └──────────────┬──────────────────────────┘  │  │
│  │                 │                             │  │
│  │    postMessage Bridge (native ↔ web)          │  │
│  └───────────────┬───────────────────────────────┘  │
│                  │                                   │
└──────────────────┼───────────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────────┐
│            VCreator Backend (Go + Echo)              │
│            (Chạy chung hệ thống hiện tại)           │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  V-App Auth  │  │   Account    │  │ Existing  │ │
│  │   Module     │  │  Matching    │  │   APIs    │ │
│  │  (MỚI)      │  │  Module(MỚI) │  │ (59 eps)  │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┘ │
│         │                 │                         │
│  ┌──────▼─────────────────▼─────────────────────┐   │
│  │              MongoDB (existing)               │   │
│  │  + vapp_user_mappings collection (MỚI)       │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
└────────────┬────────────────────────────────────────┘
             │ API callback
             ▼
┌─────────────────────┐
│   V-App Server      │
│   (Token verify)    │
└─────────────────────┘
```

## 2. Authentication Flow

```
V-App Native                 WebView/Frontend              VCreator Backend            V-App Server
    │                              │                              │                        │
    │──── Load WebView ───────────>│                              │                        │
    │     URL: ?token=xxx          │                              │                        │
    │                              │── POST /vapp/auth/verify ──>│                        │
    │                              │   { vapp_token: "xxx" }      │                        │
    │                              │                              │── Verify token ───────>│
    │                              │                              │<── User info ──────────│
    │                              │                              │                        │
    │                              │                              │── Check account match  │
    │                              │                              │   (phone/email/social) │
    │                              │                              │                        │
    │                              │<── JWT + match_result ──────│                        │
    │                              │                              │                        │
    │                              │   [Nếu match found]         │                        │
    │                              │── POST /vapp/auth/merge ───>│                        │
    │                              │   { confirm: true }          │── Link accounts ──────│
    │                              │<── JWT (merged session) ────│                        │
    │                              │                              │                        │
    │                              │   [Nếu không match]         │                        │
    │                              │   Auto-create new account    │                        │
    │                              │<── JWT (new session) ───────│                        │
```

## 3. Account Matching Logic

### Tiêu chí match (theo thứ tự ưu tiên)

1. **Phone number** — match chính xác (normalize format +84...)
2. **Email** — match chính xác (lowercase, trim)
3. **Social ID** — TikTok ID, Facebook ID, Google ID

### Quy tắc xử lý

| Scenario | Xử lý |
|----------|--------|
| Không tìm thấy match | Tạo VCreator account mới, link với V-App user |
| Match đúng 1 account | Hiển thị confirm → merge hoặc tạo mới |
| Match nhiều accounts | Hiển thị danh sách → user chọn account để merge |
| User từ chối merge | Tạo account mới, giữ account cũ nguyên |

### Data khi merge
- Giữ nguyên toàn bộ data VCreator cũ (earnings, content, KYC...)
- Thêm V-App user ID vào mapping table
- Login qua V-App token → access session VCreator account đã merge

## 4. Database Schema (Bổ sung)

### Collection: `vapp_user_mappings`
```json
{
  "_id": ObjectId,
  "vapp_user_id": "string",       // ID user trên V-App
  "vcreator_user_id": ObjectId,    // ref → users collection
  "vapp_phone": "string",          // phone từ V-App (để match)
  "vapp_email": "string",          // email từ V-App (để match)
  "vapp_name": "string",           // display name từ V-App
  "match_method": "phone|email|social|manual|none",
  "matched_at": Date,
  "status": "active|unlinked",
  "created_at": Date,
  "updated_at": Date
}
```

### Index
- `vapp_user_id` (unique)
- `vcreator_user_id`
- `vapp_phone`
- `vapp_email`

## 5. WebView ↔ Native Bridge (Phân tích chi tiết)

Mini App chạy trong WebView nên nhiều tính năng của frontend-green **không hoạt động trực tiếp** mà cần native bridge (postMessage) từ V-App. Dưới đây là phân tích từ source code hiện tại:

### 5.1 Phân loại tính năng theo mức độ cần bridge

#### CRITICAL — Không bridge = không hoạt động

| Tính năng | Code hiện tại | Vấn đề trong WebView | Giải pháp Bridge |
|-----------|--------------|---------------------|-----------------|
| **Upload ảnh (Avatar, KYC/CCCD)** | `<input type="file">` + Ant Upload + FileReader + ImgCrop | WebView trên một số thiết bị không trigger file picker, không access camera | Native bridge: `pickImage(source: 'camera'|'gallery')` → trả base64/URI về WebView |
| **Upload ảnh bài đăng** | FormData multipart upload | Cùng vấn đề file picker | Dùng chung bridge `pickImage` |
| **OAuth Social Login** | `window.open()` popup cho TikTok, Google FedCM, Facebook SDK | WebView **không hỗ trợ popup** (`window.open` bị block), Google FedCM không work trong WebView | **Bỏ hoàn toàn** — thay bằng V-App token auth. Nếu cần link social account: native bridge mở OAuth flow → trả token về |
| **Push Notification** | Firebase FCM `getToken()` + `onMessage()` | WebView không có FCM context, không request notification permission | Native bridge: V-App gửi device token → backend. Notification do V-App native handle, bridge `onNotification` để WebView react |
| **Back Button** | `history.goBack()` + browser back | Android hardware back = close WebView thay vì navigate back | Native bridge: intercept back button → `postMessage('back')` → WebView handle navigation. Nếu ở trang đầu → close WebView |

#### HIGH — Cần bridge để UX tốt

| Tính năng | Code hiện tại | Vấn đề trong WebView | Giải pháp Bridge |
|-----------|--------------|---------------------|-----------------|
| **Copy to Clipboard** | `navigator.clipboard.writeText()` + fallback `execCommand('copy')` | `navigator.clipboard` bị restrict trong WebView (require secure context + user gesture) | Native bridge: `copyToClipboard(text)` → native clipboard API |
| **Mở link ngoài** | `window.open(url, '_blank')` (video links, external content, chat) | `window.open` bị block hoặc mở trong chính WebView (mất context) | Native bridge: `openExternal(url)` → native mở Safari/Chrome hoặc in-app browser |
| **Download file** | `fetch()` → blob → `<a download>` click | `<a download>` không work trong WebView | Native bridge: `downloadFile(url, filename)` → native handle download |
| **Share** | Chưa có native share | Cần cho chia sẻ event, referral code | Native bridge: `share(title, text, url)` → native share sheet |

#### MEDIUM — Hoạt động nhưng cần xử lý đặc biệt

| Tính năng | Code hiện tại | Vấn đề trong WebView | Giải pháp |
|-----------|--------------|---------------------|-----------|
| **localStorage** | Token, deviceId, fcmToken, preferences | WebView có thể clear storage khi app bị kill, hoặc isolated storage | Dùng được nhưng cần fallback: token cũng lưu ở native side, sync qua bridge khi cần |
| **Cookie** | Referral code tracking via `document.cookie` | Third-party cookie bị block mặc định trên nhiều WebView | Chuyển referral tracking sang query params hoặc native bridge |
| **Cross-window communication** | `window.addEventListener('storage')` cho TikTok OAuth popup | Không có multi-window trong WebView | **Bỏ** — không cần vì bỏ OAuth popup flow |
| **Video playback** | `react-player` library | Thường work OK, nhưng autoplay bị restrict, fullscreen behavior khác | Test kỹ trên từng OS. Có thể cần native bridge `playVideo(url)` cho fullscreen |
| **Platform detection** | `navigator.userAgent` → headers `os-name`, `PLATFORM`, `DEVICE-TYPE` | UserAgent trong WebView có thể không chính xác | Native bridge: `getDeviceInfo()` → trả OS, version, device model chính xác |

### 5.2 postMessage Protocol đề xuất

```
WebView → Native (request):
{
  "type": "bridge",
  "action": "pickImage" | "copyToClipboard" | "openExternal" | "downloadFile"
           | "share" | "getDeviceInfo" | "close" | "back" | "playVideo",
  "requestId": "uuid",
  "payload": { ... }
}

Native → WebView (response):
{
  "type": "bridge_response",
  "requestId": "uuid",
  "success": true|false,
  "data": { ... },
  "error": "string"
}

Native → WebView (event, không cần request):
{
  "type": "bridge_event",
  "event": "back" | "notification" | "tokenRefresh" | "appResume" | "appPause",
  "data": { ... }
}
```

### 5.3 Bridge Actions tổng hợp

| Action | Direction | Payload | Response | Ưu tiên |
|--------|-----------|---------|----------|---------|
| `pickImage` | Web → Native | `{ source: 'camera'\|'gallery', maxSize?, crop? }` | `{ uri, base64, width, height }` | Critical |
| `copyToClipboard` | Web → Native | `{ text }` | `{ success }` | High |
| `openExternal` | Web → Native | `{ url }` | `{ success }` | High |
| `downloadFile` | Web → Native | `{ url, filename }` | `{ success }` | High |
| `share` | Web → Native | `{ title, text, url }` | `{ success }` | High |
| `getDeviceInfo` | Web → Native | — | `{ os, version, model, appVersion }` | Medium |
| `close` | Web → Native | — | — | Critical |
| `back` | Native → Web | — | — (WebView tự navigate) | Critical |
| `notification` | Native → Web | `{ title, body, data }` | — | High |
| `tokenRefresh` | Native → Web | `{ newToken }` | — | Critical |
| `appResume` | Native → Web | — | — | Medium |
| `appPause` | Native → Web | — | — | Medium |

### 5.4 Yêu cầu từ V-App team

V-App native team cần implement các bridge handler sau:

**Android (Kotlin/Java):**
- `WebView.addJavascriptInterface()` hoặc `WebViewClient.shouldOverrideUrlLoading()`
- Handle `pickImage`, `copyToClipboard`, `openExternal`, `downloadFile`, `share`
- Intercept hardware back button → send `back` event

**iOS (Swift):**
- `WKScriptMessageHandler` cho postMessage
- `UIImagePickerController` / `PHPickerViewController` cho image picker
- Handle universal links

> **Lưu ý:** Effort build bridge phía V-App native **KHÔNG** tính trong báo giá này. V-App team tự implement native side. Báo giá chỉ tính phần WebView (JavaScript) side của bridge.

## 6. Frontend Architecture

### Khác biệt so với frontend-green gốc

| Aspect | frontend-green (gốc) | V-App Mini App |
|--------|----------------------|----------------|
| Auth | Google/TikTok/Facebook OAuth | Token từ V-App URL |
| Navigation | Full browser navigation | In-app navigation (no browser chrome) |
| Layout | Desktop + Mobile responsive | Mobile-only, WebView optimized |
| Header | Logo + menu + login | Simplified header (no login button) |
| Deep link | Standard URL routing | WebView URL scheme + postMessage |
| Back button | Browser back | Native bridge back event + custom UI |
| File upload | `<input type="file">` trực tiếp | Native bridge `pickImage` |
| External links | `window.open('_blank')` | Native bridge `openExternal` |
| Clipboard | `navigator.clipboard` | Native bridge `copyToClipboard` |
| Push notification | Firebase FCM trong browser | Native handle, bridge event |

### Tính năng giữ nguyên (reuse ~70% code)
- Dashboard, Events, Content posting
- Bank management, Withdraw
- KYC/Identification
- Notifications
- User statistics
- Partner pages

### Tính năng bỏ/thay đổi
- OAuth login pages → thay bằng V-App token auth
- OAuth popup flow (TikTok, Google, Facebook) → bỏ hoàn toàn
- Firebase FCM browser → bỏ, native handle
- Cross-window storage events → bỏ
- App download prompts → bỏ
- Desktop layout → bỏ, chỉ giữ mobile

## 7. API Endpoints mới

### V-App Auth
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/vapp/auth/verify` | Verify V-App token, trả JWT + match info |
| POST | `/vapp/auth/refresh` | Refresh VCreator session |
| POST | `/vapp/auth/logout` | Logout, clear session |

### Account Matching
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/vapp/account/match` | Kiểm tra có account VCreator match không |
| POST | `/vapp/account/merge` | Xác nhận merge với account cũ |
| POST | `/vapp/account/create-new` | Tạo account mới (từ chối merge) |
| DELETE | `/vapp/account/unlink` | Hủy liên kết V-App ↔ VCreator |

### WebView Config
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/vapp/config` | Config cho WebView (version, features, flags) |

## 8. Tech Stack

| Layer | Technology | Ghi chú |
|-------|-----------|---------|
| Frontend | UmiJS 3 + React 16 + TypeScript | Fork từ frontend-green |
| Backend | Go 1.22+ + Echo v4 | Bổ sung module trên backend hiện tại |
| Database | MongoDB | Collection mới: vapp_user_mappings |
| Cache | Redis | Session cache cho V-App tokens |
| Deployment | Docker + Nginx | Chung infra VCreator |

## 9. Rủi ro & Mitigation

| # | Rủi ro | Impact | Mitigation |
|---|--------|--------|-----------|
| 1 | V-App token spec chưa rõ | **Cao** — Block toàn bộ auth module | Yêu cầu V-App cung cấp API docs trước D+0 |
| 2 | Account matching sai (false positive) | **Cao** — Merge nhầm data user | User phải confirm thủ công, có unlink |
| 3 | WebView bridge chưa sẵn sàng từ V-App | **Cao** — Block upload ảnh, KYC, notifications | Định nghĩa bridge protocol sớm (D+5), V-App team build song song |
| 4 | File picker không work trên một số thiết bị | **Trung bình** — Không upload được ảnh/CCCD | Fallback: native bridge `pickImage`, test trên nhiều thiết bị |
| 5 | V-App cập nhật native app ảnh hưởng WebView | **Trung bình** — Break integration | Versioned bridge protocol, regression test |
| 6 | WebView performance trên thiết bị yếu | **Trung bình** — UX kém | Lazy loading, code splitting, optimize bundle |

## 10. Rủi ro kỹ thuật: Node.js 14 & Tech Stack cũ

> **Mục này cần đặc biệt lưu ý khi đánh giá dự án.**

### Hiện trạng source code frontend-green

| Component | Phiên bản hiện tại | Phiên bản mới nhất | Trạng thái |
|-----------|-------------------|--------------------|-----------|
| **Node.js** | 14.17.3 (Dockerfile) | 22 LTS | **EOL từ 04/2023** — không còn security patches |
| **UmiJS** | 3.5.20 | 4.x | Phiên bản cũ, community nhỏ |
| **React** | 16.x | 19.x | Cũ 3 thế hệ |

### Rủi ro cụ thể của Node.js 14 EOL

| Rủi ro | Mức độ | Chi tiết |
|--------|--------|---------|
| **Security vulnerabilities** | **Nghiêm trọng** | Node 14 không còn nhận security patches từ 04/2023. Các CVE phát hiện sau đó KHÔNG được vá. Với ứng dụng tài chính (rút tiền, KYC) đây là rủi ro lớn. |
| **Dependency compatibility** | **Cao** | Nhiều npm packages đã drop support Node 14. Cài đặt/update dependencies sẽ gặp lỗi ngày càng nhiều. |
| **Build toolchain** | **Cao** | Webpack, Babel, TypeScript versions mới không support Node 14. Khó fix bug hoặc upgrade bất kỳ dependency nào. |
| **Tuyển dụng & maintain** | **Trung bình** | Developer mới không quen Node 14 + UmiJS 3. Khó tuyển người maintain. |
| **Hosting/Cloud** | **Trung bình** | Một số cloud provider đã/sẽ ngưng support Node 14 runtime. |

### Đề xuất xử lý (3 phương án)

| Phương án | Effort thêm | Rủi ro còn lại | Khuyến nghị |
|-----------|------------|----------------|------------|
| **A. Giữ nguyên Node 14 + UmiJS 3** | +0h | Cao — nợ kỹ thuật lớn, security risk | Chỉ nên chọn nếu timeline cực kỳ gấp |
| **B. Upgrade Node 18 LTS, giữ UmiJS 3** | +60~80h FE | Thấp — giải quyết security, giữ được reuse code | **Khuyến nghị** — balance giữa effort và risk |
| **C. Rewrite sang Next.js + React 18 + Node 20** | +200~250h FE | Rất thấp — stack hiện đại, dễ maintain dài hạn | Chỉ nên nếu có kế hoạch phát triển mini app > 6 tháng |

**Phương án B (khuyến nghị):** Upgrade Node lên 18 LTS, test lại build + dependencies. UmiJS 3.5 có thể chạy trên Node 18 sau khi fix một số breaking changes nhỏ. Effort ước tính +60~80h, chủ yếu là:
- Fix deprecated APIs và breaking changes khi chuyển Node 14 → 18
- Update dependencies không tương thích
- Regression test toàn bộ build + runtime
