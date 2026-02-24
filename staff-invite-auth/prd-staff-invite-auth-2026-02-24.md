# PRD: Staff Invite & Auth Self-Service

**Project:** Techcombank Dashboard
**Version:** 1.0
**Date:** 2026-02-24
**Author:** Product Manager
**Status:** Draft

**Related Documents:**
- Business Brief: `docs/staff-invite-auth/business-brief.md`
- Technical Plan: `plans/staff-invite-auth-selfservice.md`

---

## 1. Executive Summary

Thay thế quy trình onboarding nhân viên thủ công (admin tạo mật khẩu → gửi qua kênh ngoài) bằng hệ thống **token-based invitation** tự động. Đồng thời trao quyền cho nhân viên tự quản lý tài khoản (đăng nhập, quên/đổi mật khẩu) mà không phụ thuộc vào admin.

---

## 2. Business Objectives

| # | Mục tiêu | Chỉ số thành công |
|---|----------|------------------|
| BO-1 | Loại bỏ rủi ro bảo mật từ việc chia sẻ mật khẩu qua kênh ngoài | 0 mật khẩu được tạo/gửi thủ công sau khi ra mắt |
| BO-2 | Giảm tải cho admin trong việc quản lý tài khoản nhân viên | Giảm 100% yêu cầu reset mật khẩu gửi đến admin |
| BO-3 | Cải thiện trải nghiệm onboarding nhân viên mới | Nhân viên kích hoạt tài khoản trong vòng 48h sau khi nhận lời mời |
| BO-4 | Tăng visibility cho admin về trạng thái tài khoản nhân viên | Admin thấy trạng thái real-time cho 100% tài khoản |

---

## 3. User Personas

### Persona 1: Admin Hệ thống
- **Vai trò:** Quản trị viên có quyền root, quản lý danh sách nhân viên
- **Pain point:** Phải tạo mật khẩu thủ công, gửi qua Zalo/Gmail, xử lý yêu cầu reset mật khẩu thường xuyên
- **Mục tiêu:** Onboard nhân viên nhanh, an toàn; có thể theo dõi ai đã vào hệ thống

### Persona 2: Nhân viên mới
- **Vai trò:** Người vừa được thêm vào hệ thống, chưa có tài khoản Dashboard
- **Pain point:** Phải nhận mật khẩu qua kênh không chuyên, không biết cách đăng nhập Dashboard
- **Mục tiêu:** Kích hoạt tài khoản đơn giản, tự đặt mật khẩu bảo mật

### Persona 3: Nhân viên hiện tại
- **Vai trò:** Đã có tài khoản, dùng Dashboard thường xuyên
- **Pain point:** Quên mật khẩu phải chờ admin reset; không tự đổi được mật khẩu
- **Mục tiêu:** Tự xử lý tài khoản độc lập, không cần liên hệ admin

---

## 4. Scope

### Trong phạm vi (In Scope)
- Staff invitation system qua email (token-based)
- Invite status tracking trên Admin Panel
- Re-invite action cho token hết hạn
- Trang đăng nhập riêng cho Dashboard (email + password)
- Accept invite flow (đặt mật khẩu lần đầu)
- Forgot password flow (email → reset link)
- Reset password flow (từ email link)
- Change password tại Settings > Bảo mật

### Ngoài phạm vi (Out of Scope)
- Bulk invite (nhiều nhân viên cùng lúc) — Phase 3, optional
- Social login (Google, Microsoft SSO)
- Two-factor authentication (2FA)
- Admin Panel login thay đổi — vẫn giữ nguyên hệ thống đăng nhập riêng
- Audit log cho các thao tác thay đổi mật khẩu

---

## 5. Functional Requirements

### EPIC-001: Invite Management (Admin Panel)

---

#### FR-001: Gửi lời mời nhân viên

**Priority:** Must Have

**Description:**
Admin có thể mời nhân viên mới bằng cách nhập email, tên và vai trò. Hệ thống tự động gửi email chứa link kích hoạt.

**Acceptance Criteria:**
- [ ] Có button "Mời nhân viên" trên trang quản lý Staff trong Admin Panel
- [ ] Form mời gồm các trường: Email (bắt buộc), Tên (bắt buộc), Vai trò (tùy chọn)
- [ ] Sau khi submit, hệ thống tạo tài khoản với trạng thái chưa kích hoạt
- [ ] Email mời được gửi trong vòng 60 giây sau khi admin xác nhận
- [ ] Email chứa link kích hoạt hợp lệ trong 48 giờ
- [ ] Admin thấy thông báo "Đã gửi lời mời tới [email]" sau khi gửi thành công
- [ ] Nếu email đã tồn tại trong hệ thống, hiển thị lỗi phù hợp

**Dependencies:** Không có

---

#### FR-002: Xem trạng thái lời mời

**Priority:** Must Have

**Description:**
Admin có thể xem trạng thái kích hoạt của từng nhân viên trực tiếp trên danh sách Staff.

**Acceptance Criteria:**
- [ ] Cột/badge trạng thái hiển thị trên bảng danh sách nhân viên
- [ ] Ba trạng thái hiển thị: Pending (vàng), Accepted (xanh), Expired (đỏ)
- [ ] Trạng thái cập nhật real-time khi nhân viên chấp nhận lời mời
- [ ] Nhân viên chưa được mời (tạo bằng cách cũ) không hiển thị badge invite

**Dependencies:** FR-001

---

#### FR-003: Gửi lại lời mời

**Priority:** Should Have

**Description:**
Admin có thể gửi lại email mời cho nhân viên có trạng thái Expired hoặc Pending.

**Acceptance Criteria:**
- [ ] Nút "Gửi lại" xuất hiện trong actions menu cho nhân viên có status Expired hoặc Pending
- [ ] Khi gửi lại, token cũ bị vô hiệu hóa, token mới được tạo với expiry 48h mới
- [ ] Email mới được gửi với link mới
- [ ] Admin thấy xác nhận gửi thành công

**Dependencies:** FR-001, FR-002

---

### EPIC-002: Dashboard Authentication

---

#### FR-004: Trang đăng nhập Dashboard

**Priority:** Must Have

**Description:**
Nhân viên có thể đăng nhập trực tiếp vào Dashboard bằng email và mật khẩu mà không cần qua Admin Panel.

**Acceptance Criteria:**
- [ ] Trang `/login` tồn tại với form Email + Mật khẩu
- [ ] Hiển thị thông báo lỗi rõ ràng khi đăng nhập sai (không tiết lộ thông tin về tài khoản)
- [ ] Sau khi đăng nhập thành công, redirect về trang trước (returnUrl) hoặc trang chủ
- [ ] Có link "Quên mật khẩu?" dẫn đến trang forgot password
- [ ] Hỗ trợ tiếng Việt và tiếng Anh (i18n)
- [ ] Trang login có thể truy cập mà không cần xác thực

**Dependencies:** Không có

---

#### FR-005: Chấp nhận lời mời & đặt mật khẩu lần đầu

**Priority:** Must Have

**Description:**
Nhân viên mới có thể kích hoạt tài khoản bằng cách đặt mật khẩu qua link trong email mời.

**Acceptance Criteria:**
- [ ] Trang `/accept-invite?token=xxx` hiển thị tên và email nhân viên được lấy từ token
- [ ] Form yêu cầu nhập Mật khẩu mới và Xác nhận mật khẩu
- [ ] Mật khẩu phải đáp ứng yêu cầu độ mạnh tối thiểu 8 ký tự
- [ ] Sau khi đặt mật khẩu thành công, tài khoản được kích hoạt và tự động đăng nhập
- [ ] Hiển thị lỗi khi token không hợp lệ, với hướng dẫn liên hệ admin
- [ ] Hiển thị lỗi khi token hết hạn, với hướng dẫn liên hệ admin

**Dependencies:** FR-001

---

#### FR-006: Quên mật khẩu

**Priority:** Must Have

**Description:**
Nhân viên có thể yêu cầu link đặt lại mật khẩu qua email khi quên mật khẩu.

**Acceptance Criteria:**
- [ ] Trang `/forgot-password` có form nhập email
- [ ] Sau khi submit, luôn hiển thị: "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn trong vài phút" (kể cả khi email không tồn tại)
- [ ] Email reset password được gửi đến địa chỉ đã đăng ký với link hợp lệ trong 1 giờ
- [ ] Chỉ nhân viên đang active mới nhận được email reset
- [ ] Giới hạn 3 yêu cầu/email/giờ để tránh lạm dụng

**Dependencies:** FR-004

---

#### FR-007: Đặt lại mật khẩu từ email

**Priority:** Must Have

**Description:**
Nhân viên có thể đặt mật khẩu mới từ link trong email reset password.

**Acceptance Criteria:**
- [ ] Trang `/reset-password?token=xxx` có form nhập Mật khẩu mới và Xác nhận
- [ ] Mật khẩu mới phải đáp ứng yêu cầu tối thiểu 8 ký tự
- [ ] Sau khi reset thành công, redirect về `/login` với thông báo thành công
- [ ] Hiển thị lỗi khi token không hợp lệ hoặc hết hạn, có link quay lại `/forgot-password`
- [ ] Sau khi reset, tất cả phiên đăng nhập cũ bị vô hiệu hóa

**Dependencies:** FR-006

---

#### FR-008: Đổi mật khẩu (đang đăng nhập)

**Priority:** Should Have

**Description:**
Nhân viên đang đăng nhập có thể chủ động đổi mật khẩu tại trang Cài đặt.

**Acceptance Criteria:**
- [ ] Mục "Bảo mật" xuất hiện trong trang Cài đặt (Settings)
- [ ] Form gồm: Mật khẩu hiện tại, Mật khẩu mới, Xác nhận mật khẩu mới
- [ ] Phải nhập đúng mật khẩu hiện tại mới được phép đổi
- [ ] Mật khẩu mới phải đáp ứng yêu cầu tối thiểu 8 ký tự
- [ ] Hiển thị thông báo thành công sau khi đổi
- [ ] Sau khi đổi, phiên đăng nhập hiện tại vẫn còn hiệu lực

**Dependencies:** FR-004

---

#### FR-011: Đăng xuất

**Priority:** Must Have

**Description:**
Nhân viên có thể đăng xuất khỏi Dashboard, xóa phiên đăng nhập hiện tại một cách an toàn.

**Acceptance Criteria:**
- [ ] Có nút/action "Đăng xuất" trên giao diện Dashboard (ví dụ: menu avatar/profile)
- [ ] Sau khi đăng xuất, JWT token bị xóa khỏi client (localStorage/cookie)
- [ ] Backend vô hiệu hóa token trong Redis (server-side invalidation)
- [ ] Sau khi đăng xuất, redirect về trang `/login`
- [ ] Truy cập các trang được bảo vệ sau khi đăng xuất sẽ bị redirect về `/login`
- [ ] Không thể reuse token cũ sau khi đăng xuất

**Dependencies:** FR-004

---

### EPIC-003: Email Communication

---

#### FR-009: Email mời nhân viên

**Priority:** Must Have

**Description:**
Email mời được gửi tự động với nội dung rõ ràng, đúng thương hiệu.

**Acceptance Criteria:**
- [ ] Email có chủ đề: "[Techcombank] Bạn được mời tham gia hệ thống"
- [ ] Nội dung bao gồm: tên người được mời, tên người mời, nút CTA "Chấp nhận lời mời"
- [ ] Cảnh báo rõ: "Link hết hạn sau 48 giờ"
- [ ] Design phù hợp với thương hiệu (logo, màu sắc)
- [ ] Hỗ trợ tiếng Việt

**Dependencies:** FR-001

---

#### FR-010: Email đặt lại mật khẩu

**Priority:** Must Have

**Description:**
Email hướng dẫn đặt lại mật khẩu được gửi tự động sau khi nhân viên yêu cầu.

**Acceptance Criteria:**
- [ ] Email có chủ đề: "[Techcombank] Yêu cầu đặt lại mật khẩu"
- [ ] Nội dung bao gồm nút CTA "Đặt lại mật khẩu" với link hợp lệ
- [ ] Cảnh báo rõ: "Link hết hạn sau 1 giờ"
- [ ] Ghi chú: "Nếu bạn không yêu cầu, hãy bỏ qua email này"
- [ ] Design phù hợp với thương hiệu

**Dependencies:** FR-006

---

## 6. Non-Functional Requirements

---

#### NFR-001: Bảo mật Token

**Priority:** Must Have

**Description:**
Tất cả các token (invite, reset) phải được tạo và lưu trữ một cách an toàn.

**Acceptance Criteria:**
- [ ] Token được tạo bằng `crypto/rand` 32 bytes → base64url encoding
- [ ] Token được hash (bcrypt) trước khi lưu vào database
- [ ] Raw token chỉ xuất hiện trong email link, không bao giờ lưu dạng plaintext
- [ ] Token chỉ sử dụng được một lần — xóa sau khi dùng

**Rationale:** Ngăn chặn tấn công brute-force và database leak expose tokens.

---

#### NFR-002: Thời gian hết hạn Token

**Priority:** Must Have

**Description:**
Token phải có thời gian sống giới hạn để giảm thiểu rủi ro khi bị lộ.

**Acceptance Criteria:**
- [ ] Invite token: hết hạn sau 48 giờ
- [ ] Reset password token: hết hạn sau 1 giờ
- [ ] Hệ thống kiểm tra expiry trước khi chấp nhận token

**Rationale:** Giới hạn thời gian tấn công nếu email bị xâm phạm.

---

#### NFR-003: Rate Limiting

**Priority:** Must Have

**Description:**
Các endpoint công khai phải được giới hạn tốc độ request để chống lạm dụng.

**Acceptance Criteria:**
- [ ] `POST /staffs/forgot-password`: tối đa 3 requests/email/giờ
- [ ] `POST /staffs/invite/verify`: tối đa 10 requests/IP/phút
- [ ] Trả về HTTP 429 khi vượt giới hạn

**Rationale:** Chống brute-force và email flooding.

---

#### NFR-004: Email Enumeration Prevention

**Priority:** Must Have

**Description:**
Hệ thống không được tiết lộ thông tin về sự tồn tại của email trong cơ sở dữ liệu.

**Acceptance Criteria:**
- [ ] `POST /staffs/forgot-password` luôn trả về HTTP 200 dù email có tồn tại hay không
- [ ] Response message không tiết lộ trạng thái email

**Rationale:** Ngăn kẻ tấn công liệt kê danh sách email hợp lệ.

---

#### NFR-005: Session Invalidation

**Priority:** Must Have

**Description:**
Khi mật khẩu thay đổi, tất cả phiên đăng nhập cũ phải bị vô hiệu hóa.

**Acceptance Criteria:**
- [ ] `ResetPassword`: xóa tất cả JWT tokens trong Redis
- [ ] `UpdatePassword` (force-reset bởi admin): xóa tất cả JWT tokens trong Redis

**Rationale:** Đảm bảo tài khoản bị xâm phạm được bảo vệ ngay sau khi đổi mật khẩu.

---

#### NFR-006: Hiệu năng Email

**Priority:** Should Have

**Description:**
Email phải được gửi trong thời gian hợp lý.

**Acceptance Criteria:**
- [ ] Email gửi thành công trong vòng 60 giây kể từ khi trigger
- [ ] Xử lý thất bại gửi email không block response API (async)

**Rationale:** Trải nghiệm người dùng — không để nhân viên chờ đợi.

---

#### NFR-007: Password Policy

**Priority:** Must Have

**Description:**
Mật khẩu phải đáp ứng yêu cầu bảo mật cơ bản.

**Acceptance Criteria:**
- [ ] Tối thiểu 8 ký tự
- [ ] Thông báo lỗi rõ ràng khi mật khẩu không đáp ứng yêu cầu

**Rationale:** Đảm bảo tài khoản không dễ bị tấn công bằng mật khẩu yếu.

---

#### NFR-008: Internationalization (i18n)

**Priority:** Must Have

**Description:**
Tất cả các trang auth phải hỗ trợ đa ngôn ngữ (tiếng Việt và tiếng Anh).

**Acceptance Criteria:**
- [ ] Tất cả trang nằm trong `[locale]` route (vi/en)
- [ ] Link trong email mặc định sử dụng locale `/vi/`
- [ ] Tất cả text, label, error message đều có bản dịch tiếng Việt và tiếng Anh

**Rationale:** Phù hợp với cấu trúc i18n hiện tại của Dashboard.

---

## 7. Epics & Traceability Matrix

### EPIC-001: Invite Management (Admin Panel)

**Mô tả:** Trang Admin Panel có đầy đủ công cụ để admin gửi lời mời, theo dõi trạng thái và xử lý các trường hợp cần gửi lại.

**Functional Requirements:** FR-001, FR-002, FR-003, FR-009

**Story Count Estimate:** 4–6 stories

**Priority:** Must Have

**Business Value:** Loại bỏ hoàn toàn quy trình onboarding thủ công; admin có visibility đầy đủ về trạng thái tài khoản.

---

### EPIC-002: Dashboard Authentication

**Mô tả:** Dashboard có hệ thống xác thực riêng, nhân viên đăng nhập trực tiếp và tự quản lý tài khoản mà không cần admin.

**Functional Requirements:** FR-004, FR-005, FR-006, FR-007, FR-008, FR-011

**Story Count Estimate:** 7–9 stories

**Priority:** Must Have

**Business Value:** Nhân viên tự chủ hoàn toàn trong quản lý tài khoản; giảm tải cho admin.

---

### EPIC-003: Email Communication

**Mô tả:** Hệ thống email tự động cho toàn bộ luồng auth — invite, reset password — đúng thương hiệu và an toàn.

**Functional Requirements:** FR-009, FR-010

**Story Count Estimate:** 2–3 stories

**Priority:** Must Have

**Business Value:** Giao tiếp chuyên nghiệp, đúng thương hiệu với nhân viên.

---

### Traceability Matrix

| Epic | Tên Epic | Functional Requirements | Story Estimate | Priority |
|------|----------|------------------------|----------------|----------|
| EPIC-001 | Invite Management | FR-001, FR-002, FR-003, FR-009 | 4–6 | Must Have |
| EPIC-002 | Dashboard Authentication | FR-004, FR-005, FR-006, FR-007, FR-008, FR-011 | 7–9 | Must Have |
| EPIC-003 | Email Communication | FR-009, FR-010 | 2–3 | Must Have |

**Tổng stories ước tính:** 13–18 stories

---

## 8. Key User Flows

### Flow 1: Onboarding nhân viên mới

```
Admin mở Admin Panel
  → Vào trang Quản lý Nhân viên
  → Nhấn "Mời nhân viên"
  → Điền Email + Tên + Vai trò → Submit
  → Hệ thống tạo tài khoản (inactive) + gửi email mời
  → Admin thấy trạng thái "Pending" trên bảng

Nhân viên nhận email
  → Nhấn "Chấp nhận lời mời"
  → Trang /accept-invite: điền mật khẩu mới
  → Tài khoản kích hoạt → tự động đăng nhập vào Dashboard
  → Admin thấy trạng thái chuyển sang "Accepted"
```

### Flow 2: Quên mật khẩu

```
Nhân viên vào /login
  → Nhấn "Quên mật khẩu?"
  → Nhập email → Submit
  → Nhận email với link reset (hiệu lực 1h)
  → Nhấn link → trang /reset-password
  → Đặt mật khẩu mới → Submit
  → Redirect về /login với thông báo thành công
  → Đăng nhập bình thường
```

### Flow 3: Đổi mật khẩu chủ động

```
Nhân viên đang đăng nhập
  → Vào Settings → Bảo mật
  → Nhập mật khẩu hiện tại + mật khẩu mới
  → Submit → Thành công
```

### Flow 4: Đăng xuất

```
Nhân viên đang đăng nhập
  → Nhấn avatar/profile menu → Chọn "Đăng xuất"
  → Token bị xóa (client) + vô hiệu hóa (server)
  → Redirect về /login
```

---

## 9. Dependencies

### Internal
- SendGrid module đã có trong hệ thống (`backend/internal/module/sendgird/`)
- MongoDB cho lưu trữ token fields
- Redis cho rate limiting và session management
- JWT authentication infrastructure đã có

### External
- **SendGrid API** — Dịch vụ gửi email (đã có, không cần thêm)
- **DASHBOARD_URL** env var — Cần thêm vào backend config để tạo link trong email

---

## 10. Assumptions

1. SendGrid được cấu hình và hoạt động bình thường trong production
2. Nhân viên có địa chỉ email hợp lệ và truy cập được
3. Admin Panel giữ nguyên hệ thống đăng nhập riêng — không bị ảnh hưởng bởi scope này
4. Dashboard URL ổn định và có thể cấu hình qua env var
5. Các nhân viên hiện tại (tạo bằng cách cũ) tiếp tục đăng nhập bình thường qua Admin login

---

## 11. Open Questions

| # | Câu hỏi | Owner | Deadline |
|---|---------|-------|----------|
| OQ-1 | Password policy có cần thêm yêu cầu (chữ hoa/số/ký tự đặc biệt) không? | Product | Trước khi dev Phase 2 |
| OQ-2 | Có cần gửi email chào mừng (welcome email) sau khi nhân viên accept invite không? | Product | Trước khi dev EPIC-003 |
| OQ-3 | Số lượng nhân viên cần invite tối đa trong 1 lần — bulk invite có vào scope không? | Product | Trước khi finalize scope |

---

## 12. Prioritization Summary

| Loại | Must Have | Should Have | Could Have | Tổng |
|------|-----------|-------------|------------|------|
| Functional Requirements | 9 (FR-001,002,004,005,006,007,009,010,011) | 2 (FR-003, FR-008) | 0 | 11 |
| Non-Functional Requirements | 6 (NFR-001–005, 007, 008) | 1 (NFR-006) | 0 | 8 |

---

## 13. Stakeholders

| Vai trò | Tên/Nhóm | Trách nhiệm |
|---------|----------|-------------|
| Product Owner | — | Phê duyệt PRD, quyết định scope |
| Operations/Admin | — | Người dùng chính (Admin Panel), test acceptance |
| Development Team | — | Implement theo technical plan |
| QA | — | Viết và chạy test cases theo ACs |

---

*PRD Version 1.0 — 2026-02-24*
*Technical implementation plan: `plans/staff-invite-auth-selfservice.md`*
*Business brief: `docs/staff-invite-auth/business-brief.md`*
