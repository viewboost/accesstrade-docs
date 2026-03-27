# VCreator V-App Mini App — Overview

## 1. Bối cảnh

V-App (ứng dụng mobile của đối tác) muốn tích hợp VCreator dưới dạng **Mini App WebView**. Creator sử dụng V-App có thể truy cập VCreator trực tiếp trong app mà không cần cài app riêng.

## 2. Phạm vi dự án

### Frontend (Build mới dựa trên source cũ)
- Xây dựng lại giao diện từ source code **vcreator/frontend-green** (UmiJS 3 + React + TypeScript)
- Tối ưu cho WebView mobile (responsive, không có navigation bar native)
- Bỏ các tính năng không cần thiết cho context mini app (ví dụ: OAuth social login — thay bằng token-based auth)
- Giữ nguyên core features: dashboard, events, content posting, earnings, withdraw, KYC, notifications

### Backend (Bổ sung trên vcreator/backend hiện tại)
- Chạy chung với hệ thống VCreator hiện tại (Go + Echo + MongoDB)
- Bổ sung module **V-App Authentication**: nhận token từ URL WebView, xác thực với V-App server
- Bổ sung cơ chế **Account Matching**: phát hiện tài khoản V-App mới trùng với tài khoản VCreator cũ (match theo phone, email, social ID)
- Bổ sung API endpoints phục vụ riêng cho mini app context

## 3. Yêu cầu chính

### 3.1 Authentication qua WebView Token
- V-App load WebView với URL chứa token: `https://miniapp.vcreator.vn?token=xxx`
- Backend xác thực token với V-App server (API callback hoặc JWT verification)
- Tạo session VCreator từ thông tin user V-App
- Token có TTL, cần cơ chế refresh

### 3.2 Account Matching (Phát hiện tài khoản trùng)
- Khi user V-App vào lần đầu, kiểm tra xem đã có tài khoản VCreator chưa
- Tiêu chí match: số điện thoại, email, social account ID (TikTok, Facebook, Google)
- Nếu match: hiển thị confirm merge/link account
- Nếu không match: tạo tài khoản VCreator mới, liên kết với V-App user ID
- Xử lý edge cases: 1 V-App user match nhiều VCreator accounts, conflict data khi merge

### 3.3 Frontend WebView
- Build lại từ frontend-green, adapt cho WebView context
- Xử lý communication giữa WebView và native app (postMessage bridge nếu cần)
- Deep link handling từ native app
- Không có back button native — cần navigation UI trong WebView
- Loading states, error handling phù hợp mobile WebView

## 4. Phạm vi API

Dựa trên API reference hiện tại của VCreator (59 endpoints), mini app sẽ sử dụng hầu hết các endpoint hiện có, bổ sung thêm:

| Nhóm | Endpoints mới | Mô tả |
|------|--------------|-------|
| V-App Auth | 3-4 endpoints | Token verification, session create, refresh, logout |
| Account Matching | 3-4 endpoints | Check match, confirm merge, link account, unlink |
| WebView Bridge | 1-2 endpoints | App config cho WebView context, native bridge info |

## 5. WebView ↔ Native Bridge

Chạy trong WebView nghĩa là nhiều tính năng **không hoạt động trực tiếp** như trên browser thông thường. V-App native cần cung cấp bridge (postMessage) để WebView giao tiếp với thiết bị:

| Tính năng | Lý do cần bridge | Ưu tiên |
|-----------|-----------------|---------|
| **Upload ảnh** (avatar, KYC/CCCD, bài đăng) | WebView không đáng tin cậy với file picker/camera trên nhiều thiết bị | Critical |
| **Back button** | Android hardware back = close WebView, không phải navigate back | Critical |
| **Push Notification** | WebView không có FCM context | Critical |
| **Copy to clipboard** | `navigator.clipboard` bị restrict trong WebView | High |
| **Mở link ngoài** | `window.open` bị block hoặc mở trong WebView (mất context) | High |
| **Download file** | `<a download>` không work trong WebView | High |
| **Share** | Cần native share sheet | High |

> Chi tiết protocol và danh sách đầy đủ: xem [Architecture.md](Architecture.md) mục 5.

> **Lưu ý:** Effort build bridge phía V-App native KHÔNG tính trong báo giá. V-App team tự implement. Báo giá chỉ tính phần WebView (JS) side.

## 6. Rủi ro Tech Stack (Node.js 14 EOL)

Source code frontend-green hiện chạy **Node.js 14.17.3** — đã **End-of-Life từ tháng 4/2023**, không còn security patches. Với ứng dụng liên quan tài chính (rút tiền, KYC), đây là rủi ro cần lưu ý.

**Khuyến nghị:** Upgrade lên Node 18 LTS (+60~80h effort). Chi tiết phân tích và 3 phương án xử lý: xem [Architecture.md](Architecture.md) mục 10.

## 7. Giả định & Ràng buộc

- V-App cung cấp API documentation để verify token và lấy user info
- **V-App team implement native bridge** (image picker, back button, clipboard, share...) theo protocol thống nhất
- V-App team hỗ trợ integration testing trên native app (cả Android & iOS)
- Database schema VCreator hiện tại đủ linh hoạt để thêm V-App user mapping
- Không thay đổi business logic hiện tại của VCreator — chỉ thêm lớp auth + matching mới
- Mini app dùng chung backend, không deploy riêng

## 8. Báo giá tổng hợp

Dự án chia làm **3 phase** triển khai tuần tự. Phase 1 là MVP bắt buộc, Phase 2–3 có thể trì hoãn tùy nhu cầu.

| Phase | Nội dung | Giờ | Chi phí | Timeline |
|-------|----------|-----|---------|----------|
| **Phase 1 — MVP** | Auth, account matching cơ bản, 6 trang core, bridge critical | 364h | **$5,204** | 3–4 tuần |
| **Phase 2 — Enhancement** | Trang phụ, admin tools, edge cases, bridge mở rộng | 175h | **$2,461** | 2 tuần |
| **Phase 3 — Advanced** | Upgrade Node 18, performance, push notification | 77h | **$1,095** | 2 tuần |
| **Tổng** | | **616h** | **$8,760** | **~2 tháng** |

### Phase 1 — MVP ($5,204): Mini app chạy được

Bao gồm toàn bộ chức năng cần thiết để user V-App sử dụng VCreator:
- Xác thực token từ V-App, tạo session tự động
- Phát hiện tài khoản trùng (theo SĐT, email), cho phép merge hoặc tạo mới
- 6 trang core: Dashboard, Events/Campaign, Content posting, KYC/CCCD, Bank, Withdraw
- Bridge WebView ↔ Native cho 4 chức năng critical: chọn ảnh, nút back, đóng WebView, mở link ngoài
- QA, UAT, deploy production, tài liệu API + hướng dẫn tích hợp

### Phase 2 — Enhancement ($2,461): Trải nghiệm đầy đủ

Bổ sung sau khi Phase 1 go-live:
- Trang Notification, Profile/Settings, Statistics
- Account matching nâng cao: match bằng TikTok/Facebook ID, xử lý multi-match, unlink
- Bridge mở rộng: copy clipboard, share, download file
- Admin panel quản lý V-App users, webhook, monitoring/alerting
- QA regression + UAT round 2

### Phase 3 — Advanced ($1,095): Giải quyết nợ kỹ thuật

- Upgrade Node.js 14 → 18 LTS (xử lý rủi ro bảo mật EOL)
- Tối ưu bundle size, lazy loading, code splitting
- Test sâu trên nhiều thiết bị/OS
- Push notification qua native bridge

> Chi tiết từng feature: xem [BaoGia.csv](BaoGia.csv). Tổng hợp theo role + timeline: xem [Summary.csv](Summary.csv).

> **Lưu ý:** Báo giá chỉ tính effort phía VCreator (WebView + Backend). Effort phía V-App native (implement bridge, load WebView) do V-App team tự thực hiện.

## 9. Deliverables

1. **Frontend WebView App** — build từ frontend-green, tối ưu cho mobile WebView
2. **Backend V-App Auth Module** — xác thực token, quản lý session
3. **Backend Account Matching Module** — phát hiện & merge tài khoản trùng
4. **API Documentation** — endpoints mới cho V-App integration
5. **Integration Guide** — hướng dẫn V-App team tích hợp WebView
