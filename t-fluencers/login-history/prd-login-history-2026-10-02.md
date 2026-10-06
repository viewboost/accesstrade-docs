# Product Requirements Document: Lịch sử đăng nhập — T-Fluencers

**Project:** T-Fluencers (Techcombank) — Backend, Admin Portal
**Date:** 2026-10-06 (bản đầu 2026-10-02)
**Author:** Nguyễn Đăng Định
**Reviewer:** Chưa review. Chờ phân công Product Owner (TCB) và Security
**Version:** 2.0
**Project Level:** Level 1
**Status:** Draft — còn 2 Open Question (mục 13.1)
**Phạm vi:** Đưa tính năng Lịch sử đăng nhập của Ambassador sang T-Fluencers theo đúng khuôn của Ambassador: cùng dữ liệu, cùng điểm ghi, cùng API, cùng quyền, cùng màn tra cứu. Không thay đổi hành vi của các luồng đăng nhập hiện có.

---

## Document Overview

PRD cho việc đưa tính năng **Lịch sử đăng nhập** của Ambassador sang T-Fluencers. Ở Ambassador, tính năng được phát triển theo ticket ONEAT-4842 (PR #1523) và đã có trên `release`.

**Bản 2.0 thay thế toàn bộ bản 1.0.** Bản 1.0 viết lại tính năng theo SRS nghiệm thu T-Fluencers: không lưu email, thêm trường phương thức và loại tài khoản, quyền xem riêng. Ngày 2026-10-06, team quyết định **làm theo Ambassador** để hai sản phẩm có cùng một tính năng. Danh sách thay đổi so với bản 1.0 ở Phụ lục D.

Hiện trạng được xác minh trên mã nguồn ngày 2026-10-06:

- **T-Fluencers** (`viewboost/techcombank`): `release` `88d189e0` (cây mã trùng `e3dc982d`, 2026-09-17)
- **Ambassador** (`AT-Core/ambassador`): `release` `46de14a53` (2026-10-02)

### Nguyên tắc

**Làm theo Ambassador.** Giữ nguyên lược đồ dữ liệu, cách ghi nhận, API, quyền xem và màn tra cứu của Ambassador `release`.

Chỉ khác Ambassador ở 2 điểm, vì T-Fluencers không làm được như Ambassador (mục 2.3):

1. Bỏ trường và bộ lọc Đối tác (ADV): T-Fluencers không có dữ liệu để suy ra ADV
2. Ghi thêm 2 luồng cấp phiên nhân sự mà Ambassador không có: nhận lời mời và SSO sang Dashboard

Những chỗ bản Ambassador lệch SRS nghiệm thu T-Fluencers được ghi lại ở mục 2.4 và mang lên OQ-2 để Security quyết định. PRD này không tự sửa các chỗ đó.

**Related Documents:**

- SRS T-Fluencers: `nghiemthu-tfluencers/srs-v1.md` — §5.1 (phân loại dữ liệu), §5.4 (phân quyền), §5.5 (logging), §5.6 (thời hạn lưu)
- PRD Mời nhân sự T-Fluencers: `staff-invite-auth/prd-staff-invite-auth-2026-02-24.md` — nguồn của luồng nhận lời mời và SSO exchange
- Mã nguồn tham chiếu (Ambassador `release`): `backend/internal/model/mg/login_history.go`, `backend/internal/service/login_history.go`, `backend/internal/util/user_agent.go`, `backend/pkg/admin/service/audit.go`, `admin/src/pages/login-history/`

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Creator** | Người dùng cuối của T-Fluencers, đăng nhập ở web creator (`frontend`) |
| **Nhân sự** (staff) | Tài khoản đăng nhập Admin Portal hoặc Dashboard |
| **Root** | Nhân sự có cờ `isRoot` |
| **Admin** | Nhân sự có vai trò mã `admin`, gắn hoặc không gắn ADV |
| **ADV** | Advertiser — đối tác/thương hiệu. Trong mã nguồn là `partner` |
| **Admin Portal** | Ứng dụng quản trị `admin` (umi 3, antd 4) |
| **Dashboard** | Ứng dụng phân tích cho thương hiệu `dashboard`. Đăng nhập qua cùng API với Admin Portal |
| **SSO exchange** | Luồng chuyển phiên từ Admin Portal sang Dashboard: Admin Portal xin mã dùng một lần (`/staffs/auth/generate-code`), Dashboard đổi mã lấy token phiên (`/staffs/auth/exchange`) |
| **Sự kiện đăng nhập** | Một lần hệ thống cấp token phiên mới cho một tài khoản sau khi xác thực thành công. Là đơn vị ghi nhận của tính năng |
| **Điểm cấp phiên** | Hàm backend phát hành token phiên. T-Fluencers có 9 điểm, tính năng ghi ở 5 điểm (Phụ lục B) |
| **User-Agent (UA)** | Header trình duyệt gửi kèm request, mô tả trình duyệt, hệ điều hành, thiết bị |
| **Append-only** | Bản ghi chỉ được thêm, không được sửa hay xoá qua ứng dụng |
| **PII** | Personally Identifiable Information — dữ liệu định danh cá nhân |
| **IP spoofing** | Giả mạo địa chỉ IP bằng cách tự gửi header `X-Forwarded-For` |
| **Silent failure** | Lỗi xảy ra mà không có cảnh báo, chỉ để lại dòng in ra stdout |

---

## 1. Executive Summary

T-Fluencers hiện không có màn nào cho biết một tài khoản đăng nhập lúc nào, từ IP và thiết bị nào. Collection `audit-logins` có ghi các lần thử đăng nhập của nhân sự, nhưng chỉ để đếm cho rate limiting: không có User-Agent, không ghi creator, không xem được từ giao diện (mục 2.1).

Ambassador đã có tính năng Lịch sử đăng nhập. PRD đưa nguyên tính năng đó sang T-Fluencers:

```
Nhân sự đăng nhập (mật khẩu, nhận lời mời, SSO Dashboard)
Creator đăng nhập (Google, TikTok)
  → Hệ thống cấp token như hiện tại (không đổi hành vi, không chờ ghi)
  → Ghi bất đồng bộ một bản ghi: ID tài khoản, email, username, vai trò,
    IP, thiết bị, model, hệ điều hành, trình duyệt, thời điểm

Root / Admin mở Admin Portal → menu "Lịch sử đăng nhập"
  → Lọc theo User ID, Username, Email, khoảng thời gian
  → Danh sách mới nhất trước, có phân trang
```

**Phạm vi:** backend admin, backend public và Admin Portal. Không làm màn hình trên Dashboard.

---

## 2. Bối cảnh

### 2.1 Hiện trạng T-Fluencers — đã verify trên mã nguồn

Đường dẫn tính từ thư mục gốc repo `techcombank`; đường dẫn backend bỏ tiền tố `backend/`. Số dòng theo nhánh triển khai (mục 17) khi có thay đổi, còn lại theo `release`.

| Thành phần | Hiện trạng | Bằng chứng |
|---|---|---|
| Lịch sử đăng nhập trên `release` | ❌ Không có. Bản 1.0 vào `release` qua PR #771 rồi đã revert (PR #772) | `release` `88d189e0` |
| Lịch sử đăng nhập trên `develop` | Có bản 1.0 (PR #773, 2026-10-05). Bản 2.0 thay thế bản này | `develop` `b74764b6` |
| `audit-logins` (có sẵn) | Ghi mọi lần **thử** đăng nhập của nhân sự (`login_admin`) và đổi mã SSO (`auth_exchange`): IP, email hoặc 8 ký tự đầu của mã. Không có User-Agent, không ghi creator, không hiển thị ở đâu. Chỉ dùng để đếm cho rate limiting | `internal/model/mg/audit_login.go`; `pkg/admin/service/staff.go:158`; `pkg/admin/handler/staff.go:297`; `internal/service/check_rate_limit.go:68` |
| Đọc User-Agent | `GetUserAgent()` hạ toàn bộ chuỗi về chữ thường. Thư viện `uap-go` so khớp có phân biệt hoa thường nên trả `Unknown`. Ambassador đã gặp lỗi này và sửa thẳng hàm (mục 2.2); T-Fluencers sửa giống vậy. Nơi khác dùng hàm này: chỉ ghi `user-devices.userAgent`, không có chỗ nào đọc | `internal/echo/echo.go:230`; `pkg/public/service/user.go:2045` |
| Xác định IP client | `c.RealIP()`, chưa cấu hình `IPExtractor` → đọc `X-Forwarded-For` do client gửi, có thể giả mạo | `internal/echo/echo.go` (`GetHeaders`) |
| Điểm cấp phiên nhân sự | 3 điểm: đăng nhập mật khẩu (Admin Portal và Dashboard cùng gọi), nhận lời mời (cấp phiên ngay sau khi đặt mật khẩu), SSO exchange | `pkg/admin/service/staff.go:181`, `:788`, `:930` |
| Điểm cấp phiên creator | 6 endpoint công khai: Google, TikTok, Facebook, Instagram, mật khẩu, đăng ký | `pkg/public/router/user.go:21-26` |
| Web creator | Chỉ có nút Google (luôn hiện) và TikTok (hiện khi bật cờ `app.enableTikTok`). Nút Facebook đã bị comment. Không gọi Instagram, mật khẩu, đăng ký | `frontend/src/components/layout/main/header/components/modal-login.tsx:152`, `:164`, `:175` |
| Dữ liệu mạng xã hội của creator | Dữ liệu Google, TikTok lưu trong `users` được mã hoá AES | `pkg/public/service/user.go:1742`, `:1915` |
| Phân quyền nhân sự | `IsAdmin` cho qua Root và mọi nhân sự vai trò `admin`, kể cả Admin của ADV | `pkg/admin/router/routeauth/auth.go:205` |
| ADV theo tên miền | Model `partner` không có trường `allowDomains` | `internal/model/mg/partner.go` |

### 2.2 Tham chiếu Ambassador (ONEAT-4842)

Repo `ambassador`, nhánh `release` `46de14a53`.

| Thành phần | Ambassador | Bằng chứng |
|---|---|---|
| Dữ liệu | Collection `login-histories`: `userId`, `email`, `username`, `role`, `partnerId`, `partnerName`, `device`, `model`, `platform`, `browser`, `ipAddress`, `loginAt`, `createdAt`, `updatedAt` | `internal/model/mg/login_history.go` |
| Ghi nhân sự | Hàm `Login` (email + mật khẩu): `role = "admin"`, `email` = email nhân sự | `pkg/admin/service/staff.go:137` |
| Ghi creator | TikTok: `email` = email tài khoản, `username` = username TikTok. Google: `email` = email Google (không có thì email tài khoản). `role = "creator"`. Facebook, mật khẩu, đăng ký cấp token nhưng không ghi | `pkg/public/service/user.go:1650`, `:1785`; không ghi: `:699`, `:1931`, `:1981` |
| Cách ghi | Goroutine chạy sau khi xác thực thành công; IP rỗng → `Unknown`; lỗi ghi in ra stdout | `internal/service/login_history.go` |
| ADV của creator | Suy từ tên miền: 3 tên miền ghi cứng → ADV `accesstrade`; còn lại tra `allowDomains` | `pkg/public/service/user.go:1809` |
| Phân tích UA | `uap-go`. `device` = `Mobile` nếu hệ điều hành iOS/Android hoặc thiết bị iPhone/iPad/iPod, còn lại `Desktop`; không xác định → `Unknown`. `GetUserAgent()` giữ nguyên hoa thường | `internal/util/user_agent.go:23`; `internal/echo/echo.go:234` |
| API | `GET /audits/login-histories`, quyền `IsAdmin`; lọc `userId`, `username`, `email`, `partner`, `fromAt`/`toAt`; sắp xếp `loginAt` giảm dần; mặc định 20 bản ghi/trang | `pkg/admin/router/audit.go:19`; `pkg/admin/handler/audit.go:63` |
| Index | (`userId`, `loginAt`), (`email`, `loginAt`), (`username`, `loginAt`), (`partner`, `loginAt`), (`loginAt`) | `internal/module/database/mongodb/index.go:330` |
| Màn hình | Menu "Lịch sử đăng nhập", `access: 'isAdminAccess'`; 5 bộ lọc, 11 cột | `admin/config/routes.ts:238`; `admin/src/pages/login-history/` |

### 2.3 Khác biệt so với Ambassador

| # | Điểm | Ambassador | T-Fluencers | Lý do |
|---|---|---|---|---|
| 1 | ADV | Trường `partnerId`/`partnerName`, cột và bộ lọc Đối tác | Bỏ cả trường, cột, bộ lọc, index | Partner của T-Fluencers không có `allowDomains`. Giữ lại thì cột luôn trống |
| 2 | Điểm ghi của nhân sự | 1 điểm: `Login` | 3 điểm: `Login`, `AcceptInvite`, `ExchangeAuthCode` — cùng khuôn bản ghi với `Login` | Ambassador `release` không có luồng cấp phiên nào tương ứng. Không ghi thì nhân sự vào Dashboard qua SSO hoặc lần đầu qua lời mời không để lại dấu vết |

### 2.4 Đối chiếu SRS nghiệm thu T-Fluencers

Làm theo Ambassador thì có 3 chỗ không khớp SRS. Bản 1.0 đã xử lý 3 chỗ này. Bản 2.0 giữ nguyên hành vi của Ambassador và chuyển cả 3 sang OQ-2 để Security quyết định.

| Mục SRS | Nội dung | Bản 2.0 | Trạng thái |
|---|---|---|---|
| §5.5 | Ghi audit log append-only cho đăng nhập/đăng xuất Admin | Ghi đủ 3 điểm cấp phiên nhân sự (FR-001); không có API sửa xoá (NFR-002). Đăng xuất: OQ-1 | Đáp ứng phần đăng nhập |
| §5.5 | "Ẩn PII trong log: không ghi đầy đủ email/phone/CCCD; thay bằng token/ID" | Lưu nguyên email và username như Ambassador (FR-003). Đáng lưu ý: chính T-Fluencers đang mã hoá dữ liệu Google/TikTok trong `users` (mục 2.1) | **Lệch** — OQ-2 |
| §5.1, §5.4 | Lịch sử đăng nhập là dữ liệu Confidential; least privilege | Quyền `IsAdmin` như Ambassador: Admin của ADV cũng xem được IP, thiết bị, email của mọi tài khoản (FR-005) | **Lệch** — OQ-2 |
| §5.5 | Đủ dấu vết để truy vết | 4 endpoint creator (Facebook, Instagram, mật khẩu, đăng ký) cấp token mà không ghi, như Ambassador (FR-002). Web creator không dùng 4 endpoint này, nhưng gọi thẳng API thì vẫn được | **Lệch một phần** — R-3 |
| §5.6 | Lưu log bảo mật tối thiểu 1 năm | Không có TTL hay job xoá (NFR-003) | Đáp ứng |

---

## 3. Business Objectives

| # | Mục tiêu | Chỉ số thành công (KPI) | Cách đo |
|---|---|---|---|
| BO-1 | Hai sản phẩm có cùng một tính năng | Lược đồ dữ liệu, tham số API, bộ lọc, cột màn hình trùng Ambassador `release`, trừ 2 khác biệt ở mục 2.3 | Đối chiếu Phụ lục C khi review code |
| BO-2 | Đáp ứng yêu cầu ghi đăng nhập Admin của SRS §5.5 | 100% lần cấp phiên cho nhân sự có bản ghi tương ứng | Đối chiếu số response thành công của 3 endpoint cấp phiên nhân sự trong access log với số bản ghi `role = admin`, trong 7 ngày đầu sau phát hành |
| BO-3 | Truy vết được sự cố tài khoản | Trả lời được "đăng nhập lúc nào, từ IP nào, thiết bị nào" cho một tài khoản bất kỳ chỉ bằng màn Lịch sử đăng nhập | Chạy kịch bản Flow 1 khi nghiệm thu |
| BO-4 | Không ảnh hưởng trải nghiệm đăng nhập | 0 lần đăng nhập thất bại do ghi lịch sử | Theo dõi lỗi đăng nhập 7 ngày sau phát hành |

---

## 4. User Personas

### Persona 1: Admin vận hành

- **Vai trò:** Root hoặc Admin (gồm cả Admin của ADV — FR-005)
- **Pain point:** Creator báo mất tài khoản, hoặc audit log có thao tác lạ — không có dữ liệu để xác minh ai đã đăng nhập
- **Mục tiêu:** Tìm được lịch sử đăng nhập của một tài khoản trong vài thao tác

### Persona 2: Security / kiểm toán TCB

- **Vai trò:** Rà soát định kỳ, nghiệm thu hệ thống theo SRS
- **Pain point:** Chưa có bằng chứng ghi log đăng nhập Admin theo §5.5
- **Mục tiêu:** Xem các lần đăng nhập của nhân sự trong một khoảng thời gian; dữ liệu không sửa được

---

## 5. Scope

### Trong phạm vi (In Scope)

- Ghi sự kiện đăng nhập thành công tại 5 điểm cấp phiên: 3 của nhân sự, Google và TikTok của creator
- Lược đồ dữ liệu của Ambassador, bỏ trường ADV
- API danh sách có lọc, phân trang, quyền `IsAdmin`
- Màn "Lịch sử đăng nhập" trên Admin Portal theo khuôn Ambassador
- Index cho các bộ lọc

### Ngoài phạm vi (Out of Scope)

| Hạng mục | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|
| Ghi 4 endpoint creator: Facebook, Instagram, mật khẩu, đăng ký | Trung bình. Gọi thẳng API (không qua web) lấy được phiên mà không để lại dấu vết (R-3) | Web creator bật lại nút Facebook, hoặc Security yêu cầu. Ambassador cũng chưa ghi các endpoint này |
| Trường và bộ lọc ADV | Thấp | Partner của T-Fluencers có cách nhận diện ADV cho creator |
| Ẩn PII (chỉ lưu ID), giới hạn Admin của ADV | Theo OQ-2 | OQ-2 kết luận phải sửa |
| Ghi đăng xuất của nhân sự | Chưa đáp ứng đủ §5.5 | Theo kết luận OQ-1 |
| Ghi đăng nhập thất bại | Thấp. `audit-logins` đã ghi lần thử đăng nhập của nhân sự cho rate limiting, nhưng không hiển thị | Security cần xem các lần thử thất bại trên giao diện |
| Lưu User-Agent gốc, phương thức đăng nhập, loại tài khoản (có ở bản 1.0) | Thấp. Không phân biệt được SSO với đăng nhập mật khẩu; không lọc riêng được nhân sự (R-6) | Vận hành cần các bộ lọc này. Nên làm ở cả hai sản phẩm |
| Tự động xoá bản ghi cũ (TTL) | Thấp. Collection tăng dần, ước tính dưới 2 GB/năm (giả định 1) | Dung lượng vượt ngưỡng DevOps đặt ra. Mọi cơ chế xoá phải giữ ≥ 12 tháng (NFR-003) |
| Ghi nhật ký người xem Lịch sử đăng nhập | Thấp–trung bình. §5.1 yêu cầu nhật ký truy xuất cho dữ liệu Confidential | Nghiệm thu yêu cầu cụ thể |
| Màn lịch sử trên Dashboard; người dùng tự xem lịch sử của mình; xuất file; cảnh báo đăng nhập bất thường | Thấp | Có yêu cầu nghiệp vụ |
| Cấu hình nguồn IP thật | Cao với độ tin cậy của cột IP (R-1) | Phụ thuộc D-1 (DevOps) |

---

## 6. Functional Requirements

### EPIC-001: Login Event Capture

---

#### FR-001: Ghi đăng nhập của nhân sự

**Priority:** Must Have

**Description:**
Mỗi lần backend admin cấp token phiên cho nhân sự, hệ thống ghi một sự kiện đăng nhập theo khuôn `Login` của Ambassador.

**Business Rules:**

- Ba điểm cấp phiên:

  | Điểm cấp phiên | Endpoint | Ambassador |
  |---|---|---|
  | Đăng nhập email + mật khẩu (Admin Portal, Dashboard) | `POST /staffs/login` | Có ghi |
  | Nhận lời mời và đặt mật khẩu | `POST /staffs/invite/accept` | Không có luồng này (mục 2.3 #2) |
  | Chuyển phiên từ Admin Portal sang Dashboard | `POST /staffs/auth/exchange` | Không có luồng này (mục 2.3 #2) |

- `role = "admin"` cho **mọi** nhân sự, kể cả Root, Cộng tác viên, Quản lý chiến dịch — như Ambassador
- `email` = email của nhân sự; `username` để trống
- Chỉ ghi khi token đã được cấp. Request bị từ chối (sai mật khẩu, bị rate limiting, token mời hết hạn, mã SSO sai) không ghi

**Acceptance Criteria:**

- [ ] Đăng nhập thành công ở Admin Portal: có 1 bản ghi `role = admin`, đúng `email`, `userId` = ID nhân sự
- [ ] Đăng nhập thành công ở Dashboard: có 1 bản ghi, thiết bị/trình duyệt là của máy mở Dashboard
- [ ] Chuyển từ Admin Portal sang Dashboard qua SSO: có 1 bản ghi
- [ ] Nhận lời mời và đặt mật khẩu: có 1 bản ghi
- [ ] Sai mật khẩu, bị chặn 429, mã SSO không hợp lệ: không phát sinh bản ghi
- [ ] Root, Cộng tác viên đăng nhập: `role = admin`

**Dependencies:** FR-003, NFR-001

---

#### FR-002: Ghi đăng nhập của creator

**Priority:** Must Have

**Description:**
Ghi đăng nhập creator ở đúng 2 điểm Ambassador đang ghi: Google và TikTok.

**Business Rules:**

| Endpoint | `email` | `username` |
|---|---|---|
| `POST /users/login-with-tiktok` | Email của tài khoản (nếu có) | Username TikTok |
| `POST /users/login-with-google` | Email Google; không có thì email của tài khoản | Trống |

- `role = "creator"`
- Lần đăng nhập đầu tiên (tự tạo tài khoản) được ghi như mọi lần khác
- Không ghi `login-with-facebook`, `login-with-instagram`, `login`, `register` (mục 5, R-3)

**Acceptance Criteria:**

- [ ] Đăng nhập Google trên web creator: 1 bản ghi `role = creator`, `email` = email Google
- [ ] Đăng nhập TikTok trên web creator: 1 bản ghi `role = creator`, `username` = username TikTok
- [ ] Đăng nhập bị từ chối (token mạng xã hội không hợp lệ): không phát sinh bản ghi

**Dependencies:** FR-003, NFR-001

---

#### FR-003: Nội dung một bản ghi

**Priority:** Must Have

**Description:**
Collection `login-histories`, lược đồ của Ambassador bỏ trường ADV.

**Business Rules:**

| Trường | Nội dung |
|---|---|
| `userId` | ID nhân sự (`staffs`) hoặc creator (`users`) |
| `email` | Theo FR-001, FR-002; không có thì không lưu trường |
| `username` | Theo FR-002; không có thì không lưu trường |
| `role` | `admin` / `creator` |
| `ipAddress` | IP client theo cấu hình hiện hành; rỗng → `Unknown` |
| `device` | `Mobile` / `Desktop` / `Unknown` — quy tắc ở mục 2.2 |
| `model`, `platform`, `browser` | Phân tích bằng `uap-go` từ User-Agent (giữ nguyên hoa thường, mục 2.1); không xác định → `Unknown` |
| `loginAt`, `createdAt`, `updatedAt` | Thời điểm ghi, UTC |

- Không lưu User-Agent gốc, token, header khác hay nội dung request

**Acceptance Criteria:**

- [ ] Đăng nhập từ Chrome trên macOS: `device = Desktop`, `model = Mac`, `platform = Mac OS X`, `browser = Chrome`
- [ ] Đăng nhập từ Safari trên iPhone: `device = Mobile`, `model = iPhone`, `platform = iOS`
- [ ] Request không có User-Agent: các trường phân tích là `Unknown`, đăng nhập vẫn thành công
- [ ] Bản ghi không có `partnerId`, `partnerName`

**Dependencies:** —

---

### EPIC-002: Login History Review

---

#### FR-004: API danh sách lịch sử đăng nhập

**Priority:** Must Have

**Description:**
`GET /audits/login-histories` trả danh sách sự kiện đăng nhập theo bộ lọc, như Ambassador.

**Business Rules:**

- Bộ lọc, đều tuỳ chọn, kết hợp theo điều kiện AND:

  | Tham số | Ý nghĩa |
  |---|---|
  | `userId` | Đúng một tài khoản |
  | `email` | Khớp nguyên văn với `email` trong bản ghi (phân biệt hoa thường) |
  | `username` | Khớp nguyên văn với `username` trong bản ghi |
  | `fromAt`, `toAt` | Khoảng ngày theo `loginAt`, tính theo ngày giờ Việt Nam, gồm cả ngày cuối |

- Sắp xếp theo `loginAt` giảm dần
- Phân trang theo số trang (`page` bắt đầu từ 0); `limit` mặc định 20
- Không kiểm định dạng tham số, như Ambassador: `userId` sai định dạng → danh sách rỗng
- Phản hồi: `{ data, total, limit }`, mỗi phần tử gồm các trường của FR-003 trừ `createdAt`, `updatedAt` (Phụ lục A)
- Chỉ đọc; không có API sửa hay xoá (NFR-002)

**Acceptance Criteria:**

- [ ] Không lọc: trả 20 bản ghi mới nhất, kèm tổng số
- [ ] Lọc `userId`, `email`, `username`: chỉ trả bản ghi khớp
- [ ] Lọc email không tồn tại: danh sách rỗng, không báo lỗi
- [ ] Lọc khoảng ngày: chỉ trả bản ghi có `loginAt` trong khoảng (theo ngày giờ Việt Nam)
- [ ] `page=1&limit=1`: trả bản ghi thứ hai

**Dependencies:** FR-005, NFR-004

---

#### FR-005: Quyền xem

**Priority:** Must Have

**Description:**
Dùng quyền `IsAdmin` như Ambassador, ở cả API lẫn giao diện.

**Business Rules:**

- Được xem: Root và mọi nhân sự vai trò `admin`, **kể cả Admin của ADV**
- Không được xem: Cộng tác viên, Quản lý chiến dịch
- Admin Portal: route dùng `access: 'isAdminAccess'`; người không có quyền không thấy menu, mở thẳng đường dẫn thì thấy trang 403
- Lệch SRS §5.1, §5.4 — chờ OQ-2

**Acceptance Criteria:**

- [ ] Root, Admin (gắn hoặc không gắn ADV): thấy menu, gọi API được
- [ ] Cộng tác viên, Quản lý chiến dịch: không thấy menu; gọi API nhận 403; mở thẳng `/login-history` thấy trang 403
- [ ] Chưa đăng nhập: bị từ chối như mọi API admin khác

**Dependencies:** OQ-2

---

#### FR-006: Màn "Lịch sử đăng nhập" trên Admin Portal

**Priority:** Must Have

**Description:**
Màn tra cứu theo khuôn Ambassador, bỏ bộ lọc và cột Đối tác.

**Business Rules:**

- Menu cấp 1 "Lịch sử đăng nhập", đặt ngay sau menu "Nhân viên"; route `/login-history`
- Bộ lọc: User ID, Username, Email, Thời gian đăng nhập (khoảng ngày)
- 10 cột, theo thứ tự:

  | Cột | Trường |
  |---|---|
  | User ID | `userId` |
  | Email | `email` |
  | Username | `username` |
  | Vai trò | `role` (hiển thị nguyên giá trị: `admin`, `creator`) |
  | Địa chỉ IP | `ipAddress` |
  | Thiết bị | `device` |
  | Model | `model` |
  | Platform | `platform` |
  | Trình duyệt | `browser` |
  | Thời gian đăng nhập | `loginAt`, giờ Việt Nam, `DD/MM/YYYY HH:mm:ss` |

- Phân trang 20 dòng
- API lỗi: hiển thị thông báo lỗi của API

**Acceptance Criteria:**

- [ ] Mở màn: thấy danh sách mới nhất trước, có phân trang
- [ ] Giờ hiển thị theo GMT+7
- [ ] Lọc theo từng tiêu chí và kết hợp nhiều tiêu chí: kết quả khớp FR-004
- [ ] Không có cột, bộ lọc Đối tác

**Dependencies:** FR-004, FR-005

---

## 7. Non-Functional Requirements

---

#### NFR-001: Không ảnh hưởng đăng nhập

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Việc ghi chạy trong goroutine sau khi token đã sinh; API đăng nhập không chờ thao tác ghi
- [ ] MongoDB lỗi khi ghi: đăng nhập vẫn thành công, phản hồi không đổi
- [ ] Ghi thất bại: in ra stdout kèm ID tài khoản và nguyên nhân, như Ambassador

**Rationale:** Lịch sử đăng nhập là dữ liệu phụ trợ, không được trở thành điểm lỗi của đăng nhập. Ghi lỗi chỉ in ra stdout là silent failure (R-4); giữ như Ambassador theo nguyên tắc của PRD.

---

#### NFR-002: Append-only

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Không có API sửa hay xoá bản ghi lịch sử đăng nhập
- [ ] Mã ứng dụng chỉ có thao tác thêm và đọc trên collection này

**Rationale:** SRS §5.5.

---

#### NFR-003: Thời hạn lưu tối thiểu 12 tháng

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Không có TTL index hay job xoá với thời hạn dưới 12 tháng
- [ ] Collection nằm trong phạm vi sao lưu định kỳ của MongoDB như các collection khác

**Rationale:** SRS §5.6. Ambassador cũng không có TTL.

---

#### NFR-004: Index

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Có index: (`userId`, `loginAt` giảm dần), (`email`, `loginAt` giảm dần), (`username`, `loginAt` giảm dần), (`loginAt`)
- [ ] Không có index `partner` (trường này không tồn tại)

**Rationale:** Như Ambassador, bỏ index ADV. Index được tạo khi backend khởi động.

---

#### NFR-005: Độ tin cậy của địa chỉ IP

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Sau khi DevOps cấu hình nguồn IP thật (D-1): request tự gửi `X-Forwarded-For` giả không làm thay đổi IP được ghi
- [ ] Trước khi có D-1: hướng dẫn vận hành ghi rõ cột IP có thể bị giả mạo

**Rationale:** Đổi nguồn IP ảnh hưởng cả rate limiting đăng nhập và mọi nơi gọi `RealIP()`, nên DevOps chủ trì, không làm trong tính năng này.

---

#### NFR-006: Backward Compatibility

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Request và response của các API cấp phiên không đổi
- [ ] Admin Portal, Dashboard, web creator không cần phát hành lại để đăng nhập tiếp tục hoạt động
- [ ] Rollback backend không ảnh hưởng dữ liệu khác

---

#### NFR-007: Kiểm thử tự động

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Unit test phân tích User-Agent: Chrome trên macOS, Safari trên iPhone, Chrome trên Android, User-Agent rỗng, User-Agent không nhận dạng được
- [ ] Test `GetHeaders()` giữ nguyên hoa thường ở `UserAgent`
- [ ] Test tích hợp với MongoDB thật: nội dung bản ghi nhân sự và creator, từng bộ lọc của FR-004, sắp xếp, phân trang, index

---

## 8. Key User Flows

### Flow 1: Điều tra tài khoản creator nghi bị chiếm

```
Creator báo không đăng nhập được, hoặc thấy bài đăng lạ
Admin mở màn Người dùng → lấy ID (hoặc email) của creator
  → Mở Lịch sử đăng nhập → nhập User ID → chọn 30 ngày gần nhất
  → Thấy một lần đăng nhập TikTok lúc 02:13 từ IP lạ, thiết bị khác thường lệ
  → Xử lý theo quy trình sự cố
```

### Flow 2: Rà soát đăng nhập nhân sự

```
Security mở Lịch sử đăng nhập
  → Nhập email của nhân sự cần rà; khoảng thời gian = tháng trước
  → Rà các lần đăng nhập ngoài giờ, IP ngoài văn phòng
```

Không có bộ lọc riêng cho nhân sự (R-6): rà toàn bộ nhân sự phải lọc lần lượt theo từng email, hoặc lọc theo khoảng thời gian rồi đọc cột Vai trò.

### Flow 3: Ghi nhận (hệ thống)

```
Request đăng nhập → xác thực thành công → sinh token
  → Trả response cho client (không chờ)
  → Song song: phân tích User-Agent → ghi bản ghi
       ghi lỗi → in stdout, bỏ qua
```

---

## 9. Epics & Traceability Matrix

| Epic | Tên Epic | Functional Requirements | Non-Functional Requirements | Business Objectives | Story Estimate | Priority |
|---|---|---|---|---|---|---|
| EPIC-001 | Login Event Capture | FR-001, 002, 003 | NFR-001, 002, 003, 005, 006, 007 | BO-1, BO-2, BO-4 | 2–3 | Must Have |
| EPIC-002 | Login History Review | FR-004, 005, 006 | NFR-004, 007 | BO-1, BO-3 | 2–3 | Must Have |

**Tổng stories ước tính:** 4–6 stories

---

## 10. Kế hoạch phát hành & Rollback

### Thứ tự phát hành

| Bước | Nội dung | Điều kiện |
|---|---|---|
| 1 | PR #774 vào `develop`; deploy dev; QC theo Acceptance Criteria | — |
| 2 | Dọn dữ liệu bản 1.0 trên môi trường dev (mục 17) | Trước khi QC |
| 3 | Đưa vào `release` | AT nghiệm thu xong; OQ-2 đã có kết luận |
| 4 | DevOps cấu hình nguồn IP thật (D-1) | Độc lập |

**Nhánh:** nhánh triển khai cắt từ `release` và đã chứa commit hoàn tác bản revert `cdbf9e36` (PR #772). Nhờ vậy, khi nghiệm thu xong có thể PR thẳng nhánh này vào `release`. Không merge lại `feat/login-history` (bản 1.0) vào `release`: Git coi nhánh đó đã nằm trong lịch sử, nên sẽ không mang code lên.

### Rollback

- **Backend:** phát hành lại bản trước → ngừng ghi. Collection giữ nguyên, không ảnh hưởng chức năng khác
- **Admin Portal:** rollback độc lập; menu biến mất
- **Dữ liệu:** không có migration

---

## 11. Dependencies

### Internal

- MongoDB — collection `login-histories` và 4 index (NFR-004)
- Thư viện `github.com/ua-parser/uap-go` — Ambassador đang dùng
- Module audit admin (`pkg/admin/router/audit.go`) — nơi đặt endpoint
- Middleware `IsAdmin` có sẵn

### External

| # | Phụ thuộc | Bên thực hiện | Mức độ |
|---|---|---|---|
| D-1 | Cấu hình `IPExtractor` theo chuỗi proxy thật của T-Fluencers | DevOps | Khuyến nghị — quyết định NFR-005; tác động cả rate limiting đăng nhập |
| D-2 | Kết luận OQ-1, OQ-2 | Product Owner TCB, Security | OQ-2 bắt buộc trước khi đưa vào `release` |

---

## 12. Assumptions

1. Lượng đăng nhập dưới 10.000 lần/ngày, tương đương dưới 2 GB/năm kể cả index. Cần DevOps xác nhận bằng access log
2. Creator chỉ đăng nhập qua web; web chỉ dùng Google và TikTok (mục 2.1)
3. Admin Portal tiếp tục dùng umi 3

---

## 13. Open Questions & Resolved Questions

### 13.1 Open Questions

| # | Câu hỏi | Đề xuất | Tác động | Owner | Hạn |
|---|---|---|---|---|---|
| OQ-1 | Có ghi đăng xuất của nhân sự trong đợt này không (SRS §5.5)? | Không, tách đợt sau. Đăng xuất của nhân sự hiện chỉ xoá token ở trình duyệt, không gọi backend | Nếu làm: thêm API `POST /staffs/logout` và sửa cả Admin Portal lẫn Dashboard | Product Owner TCB, Security | Trước nghiệm thu |
| OQ-2 | Security có chấp nhận 2 chỗ lệch SRS của khuôn Ambassador không: (a) lưu nguyên email, username trong bản ghi (§5.5); (b) Admin của ADV xem được lịch sử của mọi tài khoản (§5.1, §5.4)? | Hỏi Security trước khi vào `release`. Nếu không chấp nhận: dùng lại thiết kế bản 1.0 cho chỗ bị từ chối (chỉ lưu ID, tra email lúc hiển thị; quyền chỉ Root và Admin không gắn ADV) | (a) cần migration dữ liệu đã ghi; (b) chỉ đổi middleware và `access` | Product Owner TCB, Security | Trước khi đưa vào `release` |

### 13.2 Resolved Questions

| # | Câu hỏi | Quyết định | Căn cứ |
|---|---|---|---|
| RQ-1 | Làm theo Ambassador hay theo SRS như bản 1.0? | Làm theo Ambassador | Quyết định của team, 2026-10-06 |
| RQ-2 | Ghi 2 luồng nhân sự Ambassador không có (nhận lời mời, SSO)? | Có, cùng khuôn bản ghi với `Login` | 2026-10-06; SRS §5.5 yêu cầu ghi đăng nhập Admin |
| RQ-3 | Giữ trường, cột, bộ lọc ADV? | Không | 2026-10-06; mục 2.3 #1 |
| RQ-4 | Ghi 4 endpoint creator mà Ambassador không ghi? | Không | Làm theo Ambassador; web creator không dùng (mục 2.1) |
| RQ-5 | Thời hạn lưu? | Không xoá; tối thiểu 12 tháng | SRS §5.6 |

---

## 14. Risks & Mitigation

| # | Rủi ro | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|---|
| R-1 | IP bị giả mạo vì chưa cấu hình nguồn IP thật | Cao | Kết luận điều tra sai | D-1 |
| R-2 | Nghiệm thu không đạt vì lệch SRS §5.5 (PII), §5.1/§5.4 (quyền) | Trung bình | Phải sửa lại sau khi đã lên `release`; nếu đổi cách lưu email thì cần migration | OQ-2 trước khi vào `release` |
| R-3 | Gọi thẳng 4 endpoint creator không ghi (Facebook, Instagram, mật khẩu, đăng ký) để lấy phiên mà không để lại dấu vết | Thấp | Lịch sử thiếu mà giao diện không cho biết | Theo dõi; khi bật lại một trong các endpoint trên web phải thêm ghi nhận. Cân nhắc tắt endpoint không dùng (việc riêng) |
| R-4 | Ghi thất bại kéo dài mà không ai biết (lỗi chỉ in ra stdout) | Thấp | Lịch sử thiếu | Theo dõi log container; đổi sang logger hệ thống ở cả hai sản phẩm nếu cần |
| R-5 | Collection tăng không giới hạn | Chắc chắn, tốc độ thấp | Dung lượng tăng, đếm tổng chậm dần | Theo dõi dung lượng; thêm TTL ≥ 12 tháng khi cần |
| R-6 | Không lọc riêng nhân sự, không phân biệt SSO với đăng nhập mật khẩu | Chắc chắn | Rà soát nhân sự tốn công hơn (Flow 2) | Chấp nhận theo RQ-1; mục 5 |

---

## 15. Prioritization Summary

| Loại | Must Have | Should Have | Could Have | Tổng |
|---|---|---|---|---|
| Functional Requirements | 6 (FR-001 → FR-006) | 0 | 0 | 6 |
| Non-Functional Requirements | 5 (NFR-001, 002, 003, 006, 007) | 2 (NFR-004, 005) | 0 | 7 |

---

## 16. Stakeholders

| Vai trò | Tên/Nhóm | Trách nhiệm |
|---|---|---|
| Product Owner | TCB — chưa phân công | Phê duyệt PRD; kết luận OQ-1, OQ-2 |
| Security / kiểm toán | TCB — chưa phân công | Kết luận OQ-2; nghiệm thu theo SRS §5 |
| Admin vận hành | VFDC | Người dùng chính của màn tra cứu |
| Development Team | DISO | Phát triển theo PRD |
| QA | — | Viết và chạy test case theo Acceptance Criteria |
| DevOps | — | D-1; theo dõi dung lượng collection |

---

## 17. Trạng thái triển khai

| Hạng mục | Trạng thái |
|---|---|
| Bản 1.0 | PR #771 vào `release` bị merge nhầm, đã revert (PR #772). PR #773 đã vào `develop` (2026-10-05) |
| Bản 2.0 | PR #774 vào `develop` (nhánh `feat/login-history-ambassador-parity`, cắt từ `release` `88d189e0`; commit `0bce3df1` hoàn tác bản revert `cdbf9e36`, `41d0976f`, `83299f8e` làm theo Ambassador). Chưa vào `release` |
| Kiểm chứng bản 2.0 | Backend build sạch. Test các package bị chạm: 5 test đỏ, trùng đúng 5 test đỏ sẵn có trên `release`. Test tích hợp MongoDB thật đạt (NFR-007). Typecheck Admin Portal không phát sinh lỗi mới |
| Dữ liệu bản 1.0 trên dev | Môi trường dev đã chạy bản 1.0 có thể còn bản ghi theo lược đồ cũ (`accountId`, `accountType`, `method`). Trên màn mới, các dòng này hiện trống cột User ID, Email, Username. Cần xoá trước khi QC. Production chưa từng chạy bản 1.0 |
| Hành vi kế thừa từ Ambassador | Màn Admin Portal chép nguyên bản Ambassador. Đổi hai ô lọc liên tiếp trong vòng 300 ms thì chỉ ô sau được áp dụng (debounce chỉ giữ lần gọi cuối) — Ambassador cũng vậy |

---

## Phụ lục A: API

| Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/audits/login-histories` | Danh sách sự kiện đăng nhập | `IsAdmin` (FR-005) |

**Tham số:** `page`, `limit`, `userId`, `email`, `username`, `fromAt`, `toAt` (định dạng `YYYY-MM-DDTHH:mm:ss.SSSZ`).

**Ví dụ phản hồi:**

```json
{
  "data": [
    {
      "_id": "6720f1c2a8b4e51d3c9f0a11",
      "userId": "65f0c3d2e4b0a1b2c3d4e5f6",
      "email": "nguyen.van.a@example.com",
      "username": "",
      "role": "admin",
      "device": "Desktop",
      "model": "Mac",
      "platform": "Mac OS X",
      "browser": "Chrome",
      "ipAddress": "203.0.113.24",
      "loginAt": "2026-10-06T03:15:42Z"
    }
  ],
  "total": 1,
  "limit": 20
}
```

---

## Phụ lục B: Điểm cấp phiên của T-Fluencers

| # | Loại | Endpoint | Hàm | Ghi lịch sử | Ambassador |
|---|---|---|---|---|---|
| 1 | Nhân sự | `POST /staffs/login` | `staffImpl.Login` (`pkg/admin/service/staff.go:182`) | Có | Có ghi |
| 2 | Nhân sự | `POST /staffs/invite/accept` | `staffImpl.AcceptInvite` (`:789`) | Có | Không có luồng này |
| 3 | Nhân sự | `POST /staffs/auth/exchange` | `staffImpl.ExchangeAuthCode` (`:932`) | Có | Không có luồng này |
| 4 | Creator | `POST /users/login-with-google` | `userImpl.LoginWithGoogle` (`pkg/public/service/user.go:1984`) | Có | Có ghi |
| 5 | Creator | `POST /users/login-with-tiktok` | `userImpl.LoginWithTiktok` (`:1834`) | Có | Có ghi |
| 6 | Creator | `POST /users/login-with-facebook` | `userImpl.LoginWithFacebook` (`:973`) | Không | Không ghi |
| 7 | Creator | `POST /users/login-with-instagram` | `userImpl.LoginWithInstagram` (`:396`) | Không | Không có |
| 8 | Creator | `POST /users/login` | `userImpl.LoginWithPassword` (`:2085`) | Không | Không ghi |
| 9 | Creator | `POST /users/register` | `userImpl.Register` (`:2132`) | Không | Không ghi |

---

## Phụ lục C: Đối chiếu Ambassador ↔ T-Fluencers 2.0

| Hạng mục | Ambassador | T-Fluencers 2.0 |
|---|---|---|
| Trường dữ liệu | `userId`, `email`, `username`, `role`, `partnerId`, `partnerName`, `device`, `model`, `platform`, `browser`, `ipAddress`, `loginAt`, `createdAt`, `updatedAt` | Như Ambassador, bỏ `partnerId`, `partnerName` |
| Giá trị `role` | `admin` / `creator` | Như Ambassador |
| Điểm ghi | Nhân sự: `Login`. Creator: Google, TikTok | Như Ambassador, thêm `AcceptInvite`, `ExchangeAuthCode` |
| Tham số API | `page`, `limit`, `userId`, `email`, `username`, `partner`, `fromAt`, `toAt` | Như Ambassador, bỏ `partner` |
| Quyền | `IsAdmin` / `isAdminAccess` | Như Ambassador |
| Index | `userId`, `email`, `username`, `partner` (kèm `loginAt`), `loginAt` | Như Ambassador, bỏ index `partner` |
| Bộ lọc màn hình | User ID, Username, Email, Đối tác, Thời gian | Như Ambassador, bỏ Đối tác |
| Cột màn hình | 11 cột | 10 cột, bỏ Đối tác |
| Nguồn User-Agent | `GetUserAgent()` giữ hoa thường | Như Ambassador (sửa `GetUserAgent()` của T-Fluencers) |

---

## Phụ lục D: Thay đổi so với bản 1.0

| Hạng mục | Bản 1.0 | Bản 2.0 |
|---|---|---|
| Nguyên tắc | Lấy Ambassador làm tham chiếu, sửa theo SRS và sửa lỗi Ambassador | Làm theo Ambassador; chỉ khác 2 điểm bắt buộc (mục 2.3) |
| Định danh tài khoản | `accountId` + `accountType`; email, tên tra lúc hiển thị | `userId`; lưu `email`, `username` trong bản ghi |
| Vai trò | Mã vai trò thật (`root`, `admin`, `collaborator`, …) | `admin` / `creator` |
| Phương thức đăng nhập | Trường `method` (8 giá trị) | Bỏ |
| User-Agent gốc, `deviceId` | Có lưu | Bỏ |
| Điểm ghi | 9 điểm | 5 điểm (Phụ lục B) |
| Quyền xem | Root + Admin không gắn ADV | `IsAdmin` (cả Admin của ADV) |
| Bộ lọc API | `accountId`, `email` (tra tài khoản, không phân biệt hoa thường), `accountType`, `method`, `ip`, khoảng ngày | `userId`, `email`, `username` (khớp nguyên văn), khoảng ngày |
| Kiểm tham số | Kiểm định dạng, `limit` tối đa 100 | Không kiểm, như Ambassador |
| Ghi lỗi | Logger hệ thống, timeout 5 giây, chặn panic | In stdout, như Ambassador |
| Index | `accountId`, `-loginAt/_id`, `ipAddress`, `accountType` | `userId`, `email`, `username`, `loginAt` |
| Màn hình | Cột Tài khoản (tên + email + ID), Loại, Phương thức, tooltip User-Agent; nhãn tiếng Việt | 10 cột như Ambassador, hiển thị nguyên giá trị |
| Đọc User-Agent | Thêm `RawUserAgent`, giữ `GetUserAgent()` chữ thường | Sửa `GetUserAgent()` giữ hoa thường như Ambassador |
| Mục 2.1 | Ghi "không có dấu vết đăng nhập nào" — sai, đã có `audit-logins` | Sửa (mục 2.1) |

---

## Lịch sử thay đổi

| Version | Ngày | Người thực hiện | Nội dung |
|---|---|---|---|
| 1.0 | 2026-10-02 | Nguyễn Đăng Định | Bản đầu tiên |
| 2.0 | 2026-10-06 | Nguyễn Đăng Định | Đổi nguyên tắc sang làm theo Ambassador (RQ-1). Viết lại FR-001 → FR-006, NFR; thêm mục 2.4 đối chiếu SRS, OQ-2 mới, Phụ lục C, D. Sửa mục 2.1: T-Fluencers đã có `audit-logins` |

---

*PRD Version 2.0 — 2026-10-06*
*Tech spec: chưa có*
