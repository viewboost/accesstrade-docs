# VCreator V-App Mini App — Báo giá Phase 1 (MVP)

## 1. Bối cảnh

V-App (ứng dụng mobile của đối tác) muốn tích hợp VCreator dưới dạng **Mini App WebView**. Creator sử dụng V-App có thể truy cập VCreator trực tiếp trong app mà không cần cài app riêng.

Báo giá này thiết kế lại giao diện cho mobile WebView thay vì clone từ source frontend-green. Điều này đảm bảo trải nghiệm mobile-native, phù hợp context Mini App.

## 2. Phạm vi — Phase 1 (MVP)

Báo giá tách thành **3 mục chính**:

| Mục | Nội dung | Giờ | Chi phí | % |
|-----|----------|-----|---------|---|
| **A. Integration** | Backend auth, account matching, middleware, bridge protocol | 157h | **$2,235** | 34% |
| **B. Thay đổi thiết kế** | Design + wireframe + FE rebuild + bridge impl + push notification | 279h | **$3,831** | 59% |
| **C. Deploy & Tài liệu** | Deployment, tài liệu kỹ thuật | 28h | **$400** | 7% |
| **Tổng Phase 1** | | **464h** | **$6,466** | 100% |

---

## 3. Mục A — Integration (Backend + API)

Nền tảng kỹ thuật để mini app hoạt động: xác thực, quản lý tài khoản, middleware. Mỗi feature đều bao gồm QC testing.

### A1. V-App Authentication & Integration (105h / $1,497)

Toàn bộ backend cần thiết để V-App kết nối với VCreator: xác thực token, quản lý session, middleware, config, database.

| Feature | Mô tả |
|---------|-------|
| Token Verification API | POST /vapp/auth/verify — Nhận token từ URL WebView, verify với V-App server, trả JWT |
| Token Refresh | POST /vapp/auth/refresh — Refresh JWT khi sắp hết hạn |
| Session Management | Redis session store, login state, logout cleanup |
| V-App Server Integration | HTTP client gọi V-App API: verify token, get user info |
| V-App Config API | GET /vapp/config — Feature flags, maintenance mode, version |
| V-App Middleware | JWT verification trên mọi request, inject user context |
| Database Migration | Collection vapp_user_mappings + indexes |

**WebView ↔ Native Bridge:** Toàn bộ bridge actions cho Mini App.

| Action | Mục đích | Ưu tiên |
|--------|----------|---------|
| pickImage | Upload ảnh KYC/CCCD, avatar, bài đăng | Critical |
| back | Android hardware back = navigate back (không close WebView) | Critical |
| close | Đóng WebView, quay lại V-App | Critical |
| openExternal | Mở link ngoài trong browser | Critical |
| copyToClipboard | Copy referral code, link chia sẻ | High |
| share | Native share sheet (event, content, referral) | High |
| downloadFile | Tải hợp đồng, receipt | High |
| getDeviceInfo | OS, version, model cho analytics | Medium |
| onNotification | Nhận push notification từ native → deep link tới page | High |

> Bridge native side do V-App team implement. Báo giá chỉ tính phần WebView (JS) side.

### A2. Account Matching (52h / $738)

Khi user V-App vào lần đầu, kiểm tra đã có tài khoản VCreator chưa (theo SĐT, email). Cho phép merge hoặc tạo mới.

| Feature | Mô tả |
|---------|-------|
| Account Lookup | Tìm VCreator account match theo phone (+84 normalize), email |
| Account Merge | Link V-App user vào VCreator account cũ, giữ nguyên data |
| New Account Creation | Tạo VCreator account mới nếu không match hoặc user từ chối merge |

---

## 4. Mục B — Thay đổi thiết kế (279h / $3,831)

Thiết kế UI/UX mới cho mobile WebView rồi implement. Mỗi màn hình bao gồm **design + implement + QC** gộp chung.

| # | Hạng mục | Giờ | Mô tả |
|---|----------|-----|-------|
| 11 | **Project Setup & Config** | 28h | Fork frontend-green, cấu hình WebView build, xóa OAuth/desktop code |
| 12 | **Design System & UI Kit** | 39h | Thiết kế + implement UI Kit: typography, colors, spacing, components, theme |
| 13 | **Navigation & Layout** | 24h | Thiết kế + implement header, tab nav, safe area, page transitions |
| 14 | **Màn hình Auth** | 22h | Thiết kế + implement loading verify token, error states, auto-refresh JWT |
| 15 | **Màn hình Account Matching** | 24h | Thiết kế + implement flow match/merge/tạo mới tài khoản |
| 16 | **Màn hình Dashboard** | 18h | Thiết kế + implement dashboard mobile (stats, activity, quick actions) |
| 17 | **Màn hình Events & Campaign** | 24h | Thiết kế + implement events list, detail, content posting |
| 18 | **Màn hình KYC/CCCD** | 21h | Thiết kế + implement KYC flow (camera/upload via bridge) |
| 19 | **Màn hình Bank & Withdraw** | 18h | Thiết kế + implement bank CRUD + withdraw flow |
| 20 | **WebView ↔ Native Bridge** | 29h | Bridge đầy đủ: pickImage, back, close, openExternal, copy, share, download, getDeviceInfo |
| 21 | **Push Notification & Deep Link** | 24h | FCM qua native bridge, deep link routing, device token registration |
| 22 | **Design Review & Iteration** | 8h | Review 2 round với stakeholder, feedback incorporation |

---

## 5. Mục C — Deploy & Tài liệu (28h / $400)

### Deployment (12h / $178)

- Staging → Production deploy
- DNS/CDN config
- Basic monitoring setup

### Tài liệu (16h / $222)

| Tài liệu | Nội dung |
|-----------|----------|
| API Documentation | OpenAPI spec cho auth + matching endpoints, request/response examples |
| V-App Integration Guide | WebView URL format, token spec, bridge protocol reference |
| Design Handoff | Figma export, component specs, icon & asset library |

---

## 6. Phân bổ nhân sự

### Đơn giá

| Role | Rate |
|------|------|
| DevOps | $17/h |
| SA | $17/h |
| BE | $15/h |
| FE | $15/h |
| QC | $11/h |
| Design | $11/h |
| BA | $11/h |
| PM | $17/h |

### Phân bổ theo mục

| Role | Mục A | Mục B | Mục C | Tổng (h) | Chi phí | % |
|------|-------|-------|-------|-----------|---------|---|
| DevOps | 2 | 1 | 2 | 5 | $85 | 1% |
| SA | 13 | 12 | 3 | 28 | $476 | 7% |
| BE | 82 | 6 | 5 | 93 | $1,395 | 22% |
| FE | 0 | 138 | 3 | 141 | $2,115 | 33% |
| QC | 32 | 40 | 2 | 74 | $814 | 13% |
| Design | 0 | 45 | 2 | 47 | $517 | 8% |
| BA | 13 | 19 | 6 | 38 | $418 | 6% |
| PM | 15 | 18 | 5 | 38 | $646 | 10% |
| **Tổng** | **157** | **279** | **28** | **464** | **$6,466** | **100%** |

---

## 7. Timeline

### Option khuyến nghị: Team 5 người (~3-4 tuần)

| Tuần | Thời gian | Nội dung |
|------|-----------|----------|
| **Tuần 1** | D+0 ~ D+5 | Design System + UI Kit / BE Auth + Core APIs |
| **Tuần 2** | D+5 ~ D+10 | Wireframe/Mockup 6 trang / BE Account Matching / FE Setup + Design System impl |
| **Tuần 3** | D+10 ~ D+16 | FE implement 6 trang theo design / Design review / QC test song song |
| **Tuần 4** | D+16 ~ D+20 | Push Notification + Bridge hoàn thiện / UAT / Deploy |

### Các option team

| Option | Team | Timeline | Ghi chú |
|--------|------|----------|---------|
| A. Tối thiểu | 4 người (Design×1, BE×1, FE×1) | ~D+22 (4-5 tuần) | Design chạy trước, FE bắt đầu khi có UI Kit |
| **B. Khuyến nghị** | **5 người (Design×1, BE×1, FE×1.5)** | **~D+18 (3-4 tuần)** | **Design + BE song song. FE có support** |
| C. Nhanh nhất | 6 người (Design×1, BE×1.5, FE×2) | ~D+15 (3 tuần) | Design sprint 1 tuần đầu |

---

## 8. Giả định & Ràng buộc

- V-App cung cấp API documentation để verify token và lấy user info **trước D+0**
- V-App team implement native bridge theo protocol thống nhất
- V-App team hỗ trợ integration testing trên native app (Android & iOS)
- Design review cần stakeholder phản hồi trong 2-3 ngày mỗi round
- Database schema VCreator hiện tại đủ linh hoạt để thêm V-App user mapping
- Không thay đổi business logic hiện tại của VCreator
- Mini app dùng chung backend, không deploy riêng

## 9. Deliverables

1. **Design Package** — UI Kit, wireframe, mockup cho 6 trang core + auth flow (Figma)
2. **Frontend WebView App** — Build mới theo design, tối ưu cho mobile WebView
3. **Backend V-App Auth Module** — Xác thực token, quản lý session
4. **Backend Account Matching Module** — Phát hiện & merge tài khoản trùng
5. **API Documentation** — Endpoints mới cho V-App integration
6. **Integration Guide** — Hướng dẫn V-App team tích hợp WebView
7. **Design Handoff** — Component specs, assets, style guide

---

> Chi tiết từng feature: xem [BaoGia.csv](BaoGia.csv). Tổng hợp theo role + timeline: xem [Summary.csv](Summary.csv).
