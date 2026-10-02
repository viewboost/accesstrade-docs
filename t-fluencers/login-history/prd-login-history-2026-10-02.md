# Product Requirements Document: Lịch sử đăng nhập — T-Fluencers

**Project:** T-Fluencers (Techcombank) — Backend, Admin Portal
**Date:** 2026-10-02
**Author:** Nguyễn Đăng Định
**Reviewer:** Chưa review. Chờ phân công Product Owner (TCB) và Security
**Version:** 1.0
**Project Level:** Level 1
**Status:** Draft — còn 2 Open Question (mục 13.1)
**Phạm vi:** Ghi nhận mọi lần đăng nhập thành công của nhân sự và creator; màn tra cứu trên Admin Portal. Không thay đổi hành vi của các luồng đăng nhập hiện có.

---

## Document Overview

PRD cho việc đưa tính năng **Lịch sử đăng nhập** của Ambassador sang T-Fluencers. Ở Ambassador, tính năng được phát triển theo ticket ONEAT-4842 (PR #1523) và đã có trên `release`.

Hiện trạng được xác minh trên mã nguồn ngày 2026-10-02:

- **T-Fluencers** (`viewboost/techcombank`): `develop` `65bb1a8e` (2026-09-14) và `release` `e3dc982d` (2026-09-17). Mọi file tính năng sẽ chạm vào hiện giống hệt nhau trên hai nhánh, nên số dòng dẫn chiếu đúng cho cả hai.
- **Ambassador** (`AT-Core/ambassador`): `release` `d0d7e898a` (2026-10-02).

Đã rà toàn bộ nhánh remote, nhánh local và pull request của repo T-Fluencers: chưa có mã nào ghi hay hiển thị lịch sử đăng nhập.

### Nguyên tắc

**Lấy Ambassador làm tham chiếu.** Giữ nguyên cơ chế ghi nhận, các trường suy ra từ User-Agent và khuôn màn tra cứu của Ambassador.

Chỉ đi khác ở ba loại tình huống, mỗi chỗ ghi rõ lý do:

1. **Bắt buộc do kiến trúc** — T-Fluencers có nhiều điểm cấp phiên hơn và không nhận diện ADV theo tên miền (mục 2.3)
2. **Yêu cầu của SRS nghiệm thu T-Fluencers** — log append-only, ẩn PII, lưu tối thiểu 1 năm, phân quyền tối thiểu (mục 2.5)
3. **Sửa lỗi đã kiểm chứng trên mã nguồn Ambassador** — mục 2.4

**Related Documents:**

- SRS T-Fluencers: `nghiemthu-tfluencers/srs-v1.md` — §5.1 (phân loại dữ liệu), §5.4 (phân quyền), §5.5 (logging), §5.6 (thời hạn lưu)
- PRD Mời nhân sự T-Fluencers: `staff-invite-auth/prd-staff-invite-auth-2026-02-24.md` — nguồn của luồng nhận lời mời và SSO exchange
- PRD Mời nhân sự Ambassador: `ambassador/moi-nhan-su-va-mat-khau/prd-moi-nhan-su-va-mat-khau-2026-09-29.md` (nhánh `docs/prd-moi-nhan-su-ambassador`, chưa vào `main`) — FR-013 ghi đăng nhập thất bại, đang hoãn
- PRD Phân quyền vận hành Ambassador: `ambassador/phan-quyen-van-hanh/prd-phan-quyen-van-hanh-2026-09-25.md` — quyền `login_history.view`
- Mã nguồn tham chiếu (Ambassador): `backend/internal/service/login_history.go`, `backend/internal/util/user_agent.go`, `backend/pkg/admin/service/audit.go`, `admin/src/pages/login-history/`

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Creator** | Người dùng cuối của T-Fluencers, đăng nhập ở web creator (`frontend`) |
| **Nhân sự** (staff) | Tài khoản đăng nhập Admin Portal hoặc Dashboard |
| **Nhân sự nội bộ** | Nhân sự không gắn ADV (trường `partner` rỗng). Trường `type` (`vfdc`/`partner`) có khai báo nhưng không được ghi giá trị, nên không dùng để phân loại |
| **Root** | Nhân sự có cờ `isRoot` |
| **Admin** | Nhân sự có vai trò mã `admin` |
| **ADV** | Advertiser — đối tác/thương hiệu. Trong mã nguồn là `partner` |
| **Admin Portal** | Ứng dụng quản trị `admin` (umi 3, antd 4) |
| **Dashboard** | Ứng dụng phân tích cho thương hiệu `dashboard` (Next.js 16). Đăng nhập qua cùng API với Admin Portal |
| **SSO exchange** | Luồng chuyển phiên từ Admin Portal sang Dashboard: Admin Portal xin mã dùng một lần (`/staffs/auth/generate-code`), Dashboard đổi mã lấy token phiên (`/staffs/auth/exchange`) |
| **Sự kiện đăng nhập** | Một lần hệ thống cấp token phiên mới cho một tài khoản sau khi xác thực thành công. Là đơn vị ghi nhận của tính năng |
| **Điểm cấp phiên** | Hàm backend phát hành token phiên. T-Fluencers có 9 điểm (Phụ lục B) |
| **User-Agent (UA)** | Header trình duyệt gửi kèm request, mô tả trình duyệt, hệ điều hành, thiết bị |
| **Append-only** | Bản ghi chỉ được thêm, không được sửa hay xoá qua ứng dụng |
| **PII** | Personally Identifiable Information — dữ liệu định danh cá nhân |
| **IP spoofing** | Giả mạo địa chỉ IP bằng cách tự gửi header `X-Forwarded-For` |
| **IPExtractor** | Cấu hình của framework Echo quy định lấy IP client từ đâu: kết nối trực tiếp, hay header do proxy tin cậy gắn vào |
| **Fail-open** | Khi thành phần phụ gặp sự cố thì luồng chính vẫn đi tiếp. Ở đây: ghi lịch sử lỗi thì đăng nhập vẫn thành công |
| **Retention** | Thời hạn lưu dữ liệu |

---

## 1. Executive Summary

T-Fluencers hiện không ghi lại lần đăng nhập nào. Khi nghi một tài khoản bị chiếm — creator báo mất tài khoản, hoặc audit log có thao tác lạ của một nhân sự — vận hành không trả lời được tài khoản đó đăng nhập lúc nào, từ IP và thiết bị nào. Dấu vết duy nhất là một khoá Redis lưu thời điểm đăng nhập thành công gần nhất của nhân sự theo từng IP. Khoá này phục vụ rate limiting, bị ghi đè mỗi lần đăng nhập và không xem được từ giao diện.

SRS nghiệm thu T-Fluencers yêu cầu ghi audit log append-only cho đăng nhập/đăng xuất Admin (§5.5), xếp lịch sử đăng nhập vào nhóm dữ liệu cá nhân Confidential (§5.1), và lưu log bảo mật tối thiểu 1 năm (§5.6).

Ambassador đã có tính năng này. PRD đưa tính năng sang T-Fluencers, mở rộng cho đủ 9 điểm cấp phiên, và sửa những chỗ bản Ambassador làm thiếu:

```
Nhân sự / creator đăng nhập thành công (9 điểm cấp phiên)
  → Hệ thống cấp token như hiện tại (không đổi hành vi, không chờ ghi)
  → Ghi bất đồng bộ một bản ghi: tài khoản, vai trò, phương thức, IP,
    User-Agent, thiết bị, hệ điều hành, trình duyệt, thời điểm
    (không lưu bản sao email, tên — SRS §5.5)

Root / Admin nội bộ mở Admin Portal → menu "Lịch sử đăng nhập"
  → Lọc theo tài khoản (ID hoặc email), loại tài khoản, phương thức, IP, khoảng thời gian
  → Danh sách mới nhất trước, có phân trang
```

**Phạm vi:** backend admin, backend public và Admin Portal. Không làm màn hình trên Dashboard.

---

## 2. Bối cảnh

### 2.1 Hiện trạng T-Fluencers — đã verify trên mã nguồn

Đường dẫn tính từ thư mục gốc repo `techcombank`; đường dẫn backend bỏ tiền tố `backend/`.

| Thành phần | Hiện trạng | Bằng chứng |
|---|---|---|
| Lịch sử đăng nhập | ❌ Không có collection, service, API hay màn hình nào, trên mọi nhánh | — |
| Dấu vết đăng nhập hiện có | Redis lưu thời điểm thành công gần nhất theo cặp nhân sự–IP, không hết hạn, ghi đè mỗi lần; chỉ dùng cho rate limiting. Creator không có dấu vết nào | `pkg/admin/service/staff.go:183`; `internal/service/check_rate_limit.go:51` |
| Thông tin request | `HeaderInfo` đã có `UserAgent`, `RemoteIP`, `DeviceID`, `DeviceModel`; mọi hàm đăng nhập đều nhận sẵn `HeaderInfo` | `internal/echo/echo.go:26`, `:87` |
| Xác định IP client | `c.RealIP()`, chưa cấu hình `IPExtractor` → đọc `X-Forwarded-For` do client gửi, có thể giả mạo | `internal/echo/echo.go:94` |
| Điểm cấp phiên nhân sự | 3 điểm: đăng nhập mật khẩu (Admin Portal và Dashboard cùng gọi), nhận lời mời (cấp phiên ngay sau khi đặt mật khẩu), SSO exchange. Hàm tạo nhân sự không cấp token (dòng cấp token đã bị comment) | `pkg/admin/service/staff.go:181`, `:772`, `:913`, `:137`; `admin/src/configs/api.ts:21`; `dashboard/src/lib/auth.ts:223` |
| Điểm cấp phiên creator | 6 điểm: Google, TikTok, Facebook, Instagram, mật khẩu, đăng ký. Web creator đang gọi 3 điểm (Google, TikTok, Facebook); 3 điểm còn lại vẫn là endpoint công khai, gọi trực tiếp được | `pkg/public/service/user.go:396`, `:973`, `:1823`, `:1946`, `:2045`, `:2092`; `pkg/public/router/user.go:21-26`; `frontend/src/configs/api.ts:88`, `:96`, `:152` |
| Đăng xuất | Creator: có API `POST /users/logout`. Nhân sự: không có API; Admin Portal và Dashboard chỉ xoá token ở trình duyệt | `pkg/public/router/user.go:28`; `admin/src/components/RightContent/AvatarDropdown.tsx:39`; `dashboard/src/app/[locale]/settings/page.tsx:64` |
| Phân quyền nhân sự | `IsAdmin` cho qua Root và mọi nhân sự vai trò `admin`, kể cả Admin của ADV. Ba vai trò: `admin`, `collaborator`, `campagin_owner` | `pkg/admin/router/routeauth/auth.go:205`; `internal/constants/staff.go:8-16` |
| Loại nhân sự | Hằng `vfdc`/`partner` có khai báo nhưng không nơi nào dùng; trường `type` luôn được gán rỗng. Admin Portal phân biệt nhân sự gắn ADV bằng `partner` | `internal/constants/staff.go:4-5`; `pkg/admin/service/staff.go:473`; `admin/src/access.ts` (`isFilterPartner`) |
| Module audit admin | Group `/audits` chỉ yêu cầu đăng nhập — endpoint mới đặt trong group này phải gắn thêm kiểm quyền | `pkg/admin/router/audit.go:14` |
| ADV theo tên miền | Model `partner` không có trường `allowDomains` | `internal/model/mg/partner.go` |
| Truy vấn dùng chung | `CommonQuery` có `Partner`, `AssignFromToAtWithField`; chưa có trường lọc email | `internal/util/mgquery/common.go:67`, `:177` |
| Thư viện phân tích UA | Chưa có `github.com/ua-parser/uap-go` | `backend/go.mod` |
| Admin Portal | umi 3.5, antd 4, pro-layout 6; route dùng `access` theo vai trò | `admin/package.json`; `admin/config/routes.ts:195` |

### 2.2 Tham chiếu Ambassador (ONEAT-4842)

| Thành phần | Ambassador | Bằng chứng (repo `ambassador`, nhánh `release`) |
|---|---|---|
| Dữ liệu | Collection `login-histories`: userId, email, username, role (`admin`/`creator`), partnerId, partnerName, device, model, platform, browser, ipAddress, loginAt | `internal/model/mg/login_history.go` |
| Phân tích UA | Thư viện `uap-go`. `device` = `Mobile` nếu hệ điều hành iOS/Android hoặc thiết bị iPhone/iPad/iPod, còn lại `Desktop`; giá trị không xác định → `Unknown` | `internal/util/user_agent.go:23` |
| Ghi nhận | Goroutine chạy sau khi xác thực thành công; lỗi chỉ in ra stdout | `pkg/admin/service/staff.go:137`; `pkg/public/service/user.go:1650`, `:1785` |
| ADV của creator | Suy từ tên miền: 3 tên miền ghi cứng → ADV `accesstrade`; còn lại tra `allowDomains` | `pkg/public/service/user.go:1809` |
| API | `GET /audits/login-histories`, quyền `IsAdmin`; lọc userId, email, username, partner, khoảng thời gian; sắp xếp `loginAt` giảm dần | `pkg/admin/router/audit.go:19`; `pkg/admin/handler/audit.go:63` |
| Màn hình | Menu "Lịch sử đăng nhập", `access: 'isAdminAccess'`; 11 cột | `admin/config/routes.ts:238`; `admin/src/pages/login-history/` |

### 2.3 Khác biệt bắt buộc do kiến trúc

| Điểm | Ambassador | T-Fluencers | Hệ quả |
|---|---|---|---|
| Điểm cấp phiên | Nhân sự: 1. Creator: 5, trong đó 2 có ghi | Nhân sự: 3. Creator: 6 | Ghi ở cả 9 điểm (FR-001, FR-002); thêm trường **phương thức** để phân biệt |
| ADV | Đa ADV, nhận diện theo tên miền | Không có `allowDomains`; web creator dùng một tên miền | Bỏ trường và bộ lọc ADV |
| Ứng dụng của nhân sự | Chỉ Admin Portal | Admin Portal và Dashboard dùng chung một API đăng nhập; có thêm SSO exchange | SSO exchange được ghi như một sự kiện đăng nhập vào Dashboard |
| Nhân sự của ADV | Có, nhưng xem lịch sử theo `IsAdmin` | Admin của ADV qua được `IsAdmin` | Quyền xem phải loại Admin của ADV (FR-005, OQ-2) |

### 2.4 Lỗi của Ambassador — sửa, không port

| # | Lỗi trên Ambassador | Rủi ro | Cách xử lý trong PRD này |
|---|---|---|---|
| 1 | Chỉ đăng nhập TikTok, Google có ghi. Facebook, mật khẩu, đăng ký cấp token mà không ghi (`user.go:699`, `:1931`, `:1981`) | Đường đăng nhập không ghi là đường kẻ tấn công sẽ chọn; lịch sử thiếu mà giao diện không cho biết | Ghi ở mọi điểm cấp phiên; test bao phủ từng điểm — FR-001, FR-002, NFR-007 |
| 2 | Index tạo trên trường `partner`, trong khi dữ liệu ghi ở `partnerId` (`index.go:330`) | Lọc theo ADV phải quét toàn collection | Index khớp đúng trường lọc — NFR-006 |
| 3 | ADV suy từ danh sách tên miền ghi cứng trong mã | Thêm tên miền mới phải phát hành lại; sai mà không báo lỗi | Không port (mục 2.3) |
| 4 | Lưu bản sao email, username vào từng bản ghi | Trái SRS §5.5 của T-Fluencers; dữ liệu cũ khi tài khoản đổi email | Chỉ lưu ID tài khoản; email, tên tra lúc hiển thị — FR-003 |
| 5 | Ghi mọi nhân sự với `role = admin`, kể cả Cộng tác viên | Không biết quyền hạn của tài khoản tại lúc đăng nhập | Ghi mã vai trò thật — FR-001 |
| 6 | Có đoạn mã in toàn bộ header request ra log (đang comment) | Bật lại thì log chứa token phiên, cookie | Không port — NFR-004 |
| 7 | Lỗi ghi chỉ in ra stdout bằng `fmt.Printf` | Ghi thất bại kéo dài mà không ai biết | Log lỗi có cấu trúc qua logger của hệ thống — NFR-001 |

### 2.5 Yêu cầu từ SRS nghiệm thu T-Fluencers

| Mục SRS | Nội dung | Đáp ứng trong PRD |
|---|---|---|
| §5.5 | "Ghi AuditLog bất biến (append-only) cho: đăng nhập/đăng xuất Admin…" | Đăng nhập: FR-001, NFR-002. Đăng xuất: OQ-1 |
| §5.5 | "Ẩn PII trong log: không ghi đầy đủ email/phone/CCCD; thay bằng token/ID" | FR-003 (không lưu bản sao email), NFR-004 |
| §5.1 | Lịch sử đăng nhập là dữ liệu Confidential — kiểm soát truy cập chặt chẽ, nhật ký truy xuất đầy đủ | Kiểm soát truy cập: FR-005. Nhật ký người xem: ngoài phạm vi (mục 5) |
| §5.4 | RBAC, least privilege | FR-005, OQ-2 |
| §5.6 | "Log bảo mật/audit: lưu tối thiểu 1 năm" | NFR-003 |

---

## 3. Business Objectives

| # | Mục tiêu | Chỉ số thành công (KPI) | Cách đo |
|---|---|---|---|
| BO-1 | Đáp ứng yêu cầu ghi đăng nhập Admin của SRS §5.5 | 100% lần cấp phiên cho nhân sự có bản ghi tương ứng | Đối chiếu số response thành công của 3 endpoint cấp phiên nhân sự trong access log với số bản ghi `accountType = staff`, trong 7 ngày đầu sau phát hành |
| BO-2 | Truy vết được sự cố tài khoản | Trả lời được "đăng nhập lúc nào, từ IP nào, thiết bị nào" cho một tài khoản bất kỳ chỉ bằng màn Lịch sử đăng nhập, không cần truy vấn cơ sở dữ liệu | Chạy kịch bản Flow 1 khi nghiệm thu |
| BO-3 | Không bỏ sót đường đăng nhập | 9/9 điểm cấp phiên có ghi nhận | Test tự động (NFR-007) |
| BO-4 | Không ảnh hưởng trải nghiệm đăng nhập | 0 lần đăng nhập thất bại do ghi lịch sử; p95 thời gian phản hồi của API đăng nhập không tăng quá 10% | Log lỗi (NFR-001); so p95 trong 7 ngày trước và sau phát hành |

---

## 4. User Personas

### Persona 1: Admin vận hành nội bộ

- **Vai trò:** Root hoặc Admin không gắn ADV
- **Pain point:** Creator báo mất tài khoản, hoặc audit log có thao tác lạ — không có dữ liệu để xác minh ai đã đăng nhập
- **Mục tiêu:** Tìm được lịch sử đăng nhập của một tài khoản trong vài thao tác

### Persona 2: Security / kiểm toán TCB

- **Vai trò:** Rà soát định kỳ, nghiệm thu hệ thống theo SRS
- **Pain point:** Chưa có bằng chứng ghi log đăng nhập Admin theo §5.5
- **Mục tiêu:** Xem toàn bộ lần đăng nhập của nhân sự trong một khoảng thời gian; dữ liệu không sửa được

### Persona 3: Chủ thể dữ liệu (creator, nhân sự)

- **Vai trò:** Người được ghi nhận; không trực tiếp dùng tính năng
- **Quan tâm:** Dữ liệu đăng nhập của mình chỉ người có thẩm quyền xem được (§5.1)

---

## 5. Scope

### Trong phạm vi (In Scope)

- Ghi sự kiện đăng nhập thành công tại 9 điểm cấp phiên (3 của nhân sự, 6 của creator)
- Các trường: tài khoản, loại tài khoản, vai trò, phương thức, IP, User-Agent gốc và các trường phân tích từ User-Agent, mã thiết bị, thời điểm
- API danh sách có lọc, phân trang, kiểm quyền riêng
- Màn "Lịch sử đăng nhập" trên Admin Portal
- Index cho các bộ lọc

### Ngoài phạm vi (Out of Scope)

| Hạng mục | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|
| Ghi đăng xuất của nhân sự | Chưa đáp ứng đủ §5.5 | Theo kết luận OQ-1 |
| Ghi đăng nhập thất bại | Trung bình. Hành vi dò mật khẩu không để lại dấu vết trong lịch sử (rate limiting `CheckRateLimitLoginAdmin` vẫn chặn) | Security yêu cầu. Dùng lại được thiết kế FR-013 của PRD Mời nhân sự Ambassador |
| Tự động xoá bản ghi cũ (TTL) | Thấp. Collection tăng dần, ước tính dưới 2 GB/năm (giả định 1) | Dung lượng vượt ngưỡng DevOps đặt ra, hoặc TCB ban hành thời hạn lưu tối đa. Mọi cơ chế xoá phải giữ ≥ 12 tháng (NFR-003) |
| Ghi nhật ký người xem Lịch sử đăng nhập | Thấp–trung bình. §5.1 yêu cầu nhật ký truy xuất cho dữ liệu Confidential | Nghiệm thu yêu cầu cụ thể. Nên áp chung cho mọi màn có dữ liệu Confidential, không làm riêng màn này |
| Màn lịch sử trên Dashboard | Thấp | Thương hiệu cần tự xem đăng nhập của nhân sự mình |
| Creator, nhân sự tự xem lịch sử của chính mình | Thấp | Yêu cầu về quyền của chủ thể dữ liệu (§5.1) |
| Xuất file | Thấp | Kiểm toán cần dữ liệu ngoài hệ thống |
| Cảnh báo đăng nhập bất thường (IP lạ, quốc gia lạ, nhiều thiết bị) | Trung bình | Phát sinh sự cố chiếm tài khoản |
| Tra vị trí địa lý theo IP | Thấp | Đi cùng cảnh báo bất thường |
| Cấu hình nguồn IP thật | Cao với độ tin cậy của cột IP (R-1) | Phụ thuộc D-1 (DevOps) |
| Áp ngược các bản sửa mục 2.4 cho Ambassador | Ambassador vẫn bỏ sót 3 đường đăng nhập của creator | Task riêng cho Ambassador |

---

## 6. Functional Requirements

### EPIC-001: Login Event Capture

---

#### FR-001: Ghi đăng nhập của nhân sự

**Priority:** Must Have

**Description:**
Mỗi lần backend admin cấp token phiên cho nhân sự, hệ thống ghi một sự kiện đăng nhập.

**Business Rules:**

- Ba điểm cấp phiên và phương thức tương ứng:

  | Điểm cấp phiên | Endpoint | `method` |
  |---|---|---|
  | Đăng nhập email + mật khẩu (Admin Portal, Dashboard) | `POST /staffs/login` | `password` |
  | Nhận lời mời và đặt mật khẩu | `POST /staffs/invite/accept` | `accept_invite` |
  | Chuyển phiên từ Admin Portal sang Dashboard | `POST /staffs/auth/exchange` | `sso_exchange` |

- Chỉ ghi khi token đã được cấp. Request bị từ chối (sai mật khẩu, bị rate limiting, token mời hết hạn, mã SSO sai) không ghi
- `role` = `root` nếu nhân sự là Root; còn lại là mã vai trò tại thời điểm đăng nhập (`admin`, `collaborator`, `campagin_owner`)
- Điểm cấp phiên nhân sự thêm sau này phải ghi theo cùng quy tắc (NFR-007)

**Acceptance Criteria:**

- [ ] Đăng nhập thành công ở Admin Portal: có 1 bản ghi `accountType = staff`, `method = password`
- [ ] Đăng nhập thành công ở Dashboard: có 1 bản ghi `method = password`, User-Agent là của trình duyệt mở Dashboard
- [ ] Chuyển từ Admin Portal sang Dashboard qua SSO: có 1 bản ghi `method = sso_exchange`
- [ ] Nhận lời mời và đặt mật khẩu: có 1 bản ghi `method = accept_invite`
- [ ] Sai mật khẩu, bị chặn 429, mã SSO không hợp lệ: không phát sinh bản ghi
- [ ] Root đăng nhập: `role = root`. Cộng tác viên đăng nhập: `role = collaborator`

**Dependencies:** FR-003, NFR-001

---

#### FR-002: Ghi đăng nhập của creator

**Priority:** Must Have

**Description:**
Mỗi lần backend public cấp token phiên cho creator, hệ thống ghi một sự kiện đăng nhập.

**Business Rules:**

- Sáu điểm cấp phiên:

  | Endpoint | `method` | Web creator đang dùng |
  |---|---|---|
  | `POST /users/login-with-google` | `google` | Có |
  | `POST /users/login-with-tiktok` | `tiktok` | Có |
  | `POST /users/login-with-facebook` | `facebook` | Có |
  | `POST /users/login-with-instagram` | `instagram` | Không |
  | `POST /users/login` | `password` | Không |
  | `POST /users/register` | `register` | Không |

- Ghi cả 3 endpoint web creator không gọi, vì chúng vẫn công khai và cấp token hợp lệ (RQ-4)
- Lần đăng nhập mạng xã hội đầu tiên (tự tạo tài khoản) được ghi như mọi lần đăng nhập khác, cùng phương thức
- `role` = `creator`

**Acceptance Criteria:**

- [ ] Đăng nhập bằng Google, TikTok, Facebook trên web creator: mỗi lần 1 bản ghi, đúng `method`
- [ ] Gọi trực tiếp `login-with-instagram`, `login`, `register` thành công: mỗi lần 1 bản ghi, đúng `method`
- [ ] Đăng nhập bị từ chối (token mạng xã hội không hợp lệ, sai mật khẩu): không phát sinh bản ghi

**Dependencies:** FR-003, NFR-001

---

#### FR-003: Nội dung một bản ghi

**Priority:** Must Have

**Description:**
Mỗi sự kiện đăng nhập lưu đủ thông tin để truy vết, và chỉ chừng đó.

**Business Rules:**

| Trường | Nội dung | Ghi chú |
|---|---|---|
| `accountId` | ID tài khoản trong `users` hoặc `staffs` | Bắt buộc |
| `accountType` | `staff` / `creator` | |
| `role` | Theo FR-001, FR-002 | Giá trị tại thời điểm đăng nhập |
| `method` | Theo FR-001, FR-002 | Mới so với Ambassador |
| `ipAddress` | IP client theo cấu hình hiện hành; rỗng → `Unknown` | Độ tin cậy phụ thuộc D-1 |
| `userAgent` | User-Agent gốc, tối đa 512 ký tự | Mới — để nhận ra đăng nhập bằng script, và phân tích lại khi thư viện cập nhật |
| `device` | `Mobile` / `Desktop` | Quy tắc như Ambassador (mục 2.2) |
| `model`, `platform`, `browser` | Phân tích bằng `uap-go`; không xác định → `Unknown` | Như Ambassador |
| `deviceId` | Header `x-device-id`, nếu có | Mới — khớp mã thiết bị được gắn vào token phiên |
| `loginAt` | Thời điểm cấp token, lưu theo UTC | |

- Không lưu bản sao email, số điện thoại, tên (SRS §5.5). Màn hình tra email và tên hiện tại theo `accountId` lúc hiển thị (FR-006)
- Không lưu token, các header khác, hay nội dung request

**Acceptance Criteria:**

- [ ] Bản ghi không chứa email, số điện thoại, tên, token
- [ ] Đăng nhập từ Chrome trên macOS: `device = Desktop`, `platform = Mac OS X`, `browser = Chrome`
- [ ] Đăng nhập từ Safari trên iPhone: `device = Mobile`, `model = iPhone`, `platform = iOS`
- [ ] User-Agent dài hơn 512 ký tự: lưu 512 ký tự đầu
- [ ] Request không có User-Agent: các trường phân tích là `Unknown`, đăng nhập vẫn thành công

**Dependencies:** —

---

### EPIC-002: Login History Review

---

#### FR-004: API danh sách lịch sử đăng nhập

**Priority:** Must Have

**Description:**
`GET /audits/login-histories` trả danh sách sự kiện đăng nhập theo bộ lọc.

**Business Rules:**

- Bộ lọc, đều tuỳ chọn, kết hợp theo điều kiện AND:

  | Tham số | Ý nghĩa |
  |---|---|
  | `accountId` | Đúng một tài khoản |
  | `email` | Tìm tài khoản nhân sự và creator có email này (không phân biệt chữ hoa/thường, khớp toàn bộ), rồi lọc theo các ID tìm được. Không có tài khoản nào → danh sách rỗng |
  | `accountType` | `staff` / `creator` |
  | `method` | Một phương thức |
  | `ip` | Khớp toàn bộ địa chỉ IP |
  | `fromAt`, `toAt` | Khoảng thời gian theo `loginAt` |

- Sắp xếp theo `loginAt` giảm dần
- Phân trang theo số trang; mặc định 20 bản ghi mỗi trang, tối đa 100
- Mỗi bản ghi trả kèm email và tên **hiện tại** của tài khoản (tra theo `accountId`). Tài khoản không còn tồn tại: để trống email, tên; vẫn trả ID
- Chỉ đọc; không có API sửa hay xoá (NFR-002)

**Acceptance Criteria:**

- [ ] Không lọc: trả 20 bản ghi mới nhất, kèm tổng số
- [ ] `limit=500`: trả tối đa 100 bản ghi
- [ ] Lọc bằng email khác chữ hoa/thường so với email đã đăng ký: vẫn ra đúng tài khoản
- [ ] Lọc bằng email không tồn tại: danh sách rỗng, không báo lỗi
- [ ] Kết hợp `accountType=staff` và khoảng ngày: chỉ có đăng nhập của nhân sự trong khoảng đó
- [ ] `accountId` hoặc `fromAt` sai định dạng: HTTP 400

**Dependencies:** FR-005, NFR-006

---

#### FR-005: Quyền xem

**Priority:** Must Have

**Description:**
Chỉ nhân sự có thẩm quyền xem được Lịch sử đăng nhập, ở cả API lẫn giao diện.

**Business Rules:**

- Được xem (đề xuất, chờ OQ-2): Root, và Admin **không gắn ADV**
- Không được xem: Admin của ADV, Cộng tác viên, Quản lý chiến dịch
- Lý do không dùng nguyên `IsAdmin` như Ambassador: `IsAdmin` cho qua cả Admin của ADV, trong khi dữ liệu chứa IP và thiết bị của mọi creator và mọi nhân sự, kể cả nhân sự nội bộ và nhân sự ADV khác — trái nguyên tắc least privilege (§5.4)
- Endpoint đặt trong group `/audits` phải gắn kiểm quyền riêng, vì group chỉ yêu cầu đăng nhập (mục 2.1)
- Người không có quyền: không thấy menu; mở thẳng đường dẫn thì thấy trang 403

**Acceptance Criteria:**

- [ ] Root, Admin không gắn ADV: thấy menu, gọi API được
- [ ] Admin của ADV, Cộng tác viên, Quản lý chiến dịch: không thấy menu; gọi API nhận 403; mở thẳng `/login-history` thấy trang 403
- [ ] Chưa đăng nhập: bị từ chối như mọi API admin khác

**Dependencies:** OQ-2

---

#### FR-006: Màn "Lịch sử đăng nhập" trên Admin Portal

**Priority:** Must Have

**Description:**
Màn tra cứu theo khuôn màn của Ambassador.

**Business Rules:**

- Menu cấp 1 "Lịch sử đăng nhập", đặt ngay sau menu "Nhân viên"; route `/login-history`
- Bộ lọc: Email, ID tài khoản, Loại tài khoản, Phương thức, IP, Khoảng thời gian
- Cột:

  | Cột | Nội dung |
  |---|---|
  | Thời điểm | Giờ Việt Nam (GMT+7), `DD/MM/YYYY HH:mm:ss` |
  | Tài khoản | Email (nhân sự) hoặc tên/email (creator); dòng dưới là ID, sao chép được |
  | Loại | Nhân sự / Creator |
  | Vai trò | Root, Admin, Cộng tác viên, Quản lý chiến dịch, Creator |
  | Phương thức | Mật khẩu, Nhận lời mời, SSO Dashboard, Google, TikTok, Facebook, Instagram, Đăng ký |
  | IP | |
  | Thiết bị, Model, Hệ điều hành, Trình duyệt | Như Ambassador. Rê chuột vào cột Trình duyệt thấy User-Agent gốc |

- Phân trang 20 dòng
- Danh sách rỗng: hiển thị "Không có lần đăng nhập nào khớp bộ lọc"

**Acceptance Criteria:**

- [ ] Mở màn: thấy danh sách mới nhất trước, có phân trang
- [ ] Giờ hiển thị theo GMT+7
- [ ] Lọc theo từng tiêu chí và kết hợp nhiều tiêu chí: kết quả khớp FR-004
- [ ] Rê chuột vào cột Trình duyệt: thấy User-Agent gốc
- [ ] Bản ghi của tài khoản không còn tồn tại: cột Tài khoản hiện ID, trang không lỗi

**Dependencies:** FR-004, FR-005

---

## 7. Non-Functional Requirements

---

#### NFR-001: Không ảnh hưởng đăng nhập

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Việc ghi chạy bất đồng bộ sau khi token đã sinh; API đăng nhập không chờ thao tác ghi
- [ ] MongoDB lỗi hoặc chậm khi ghi: đăng nhập vẫn thành công, phản hồi không đổi (fail-open)
- [ ] Thao tác ghi có timeout 5 giây
- [ ] Ghi thất bại: log mức error qua logger của hệ thống, kèm `accountId`, `method` và nguyên nhân; không kèm email, IP, User-Agent

**Rationale:** Lịch sử đăng nhập là dữ liệu phụ trợ, không được trở thành điểm lỗi của đăng nhập. Rủi ro mất bản ghi trong khi đăng nhập vẫn thành công là nhỏ: khi MongoDB gián đoạn, đăng nhập vốn đã thất bại vì phải đọc tài khoản.

---

#### NFR-002: Append-only

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Không có API sửa hay xoá bản ghi lịch sử đăng nhập
- [ ] Mã ứng dụng chỉ có thao tác thêm và đọc trên collection này
- [ ] Mọi script bảo trì tác động tới collection phải qua phê duyệt như thay đổi dữ liệu production

**Rationale:** SRS §5.5. Ràng buộc ở tầng cơ sở dữ liệu (tách user chỉ có quyền insert) cần DBA thực hiện, nằm ngoài phạm vi.

---

#### NFR-003: Thời hạn lưu tối thiểu 12 tháng

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Không có TTL index hay job xoá với thời hạn dưới 12 tháng
- [ ] Collection nằm trong phạm vi sao lưu định kỳ của MongoDB như các collection khác

**Rationale:** SRS §5.6. Đợt này không đặt thời hạn lưu tối đa (mục 5).

---

#### NFR-004: Bảo vệ PII và thông tin bí mật

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Không ghi toàn bộ header request vào log ứng dụng hay cơ sở dữ liệu (header chứa token phiên, cookie)
- [ ] Log ứng dụng của tính năng chỉ dùng ID để định danh tài khoản
- [ ] API chỉ trả dữ liệu cho người có quyền (FR-005)

**Rationale:** SRS §5.1, §5.5. Chặn việc port nhầm đoạn mã in header của Ambassador (mục 2.4 #6).

---

#### NFR-005: Độ tin cậy của địa chỉ IP

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Sau khi DevOps cấu hình nguồn IP thật (D-1): request tự gửi `X-Forwarded-For` giả không làm thay đổi IP được ghi
- [ ] Trước khi có D-1: hướng dẫn vận hành ghi rõ cột IP có thể bị giả mạo

**Rationale:** IP là trường được dùng nhiều nhất khi điều tra. Đổi nguồn IP ảnh hưởng cả rate limiting đăng nhập (`CheckRateLimitLoginAdmin`) và mọi nơi gọi `RealIP()`, nên DevOps chủ trì, không làm trong tính năng này.

---

#### NFR-006: Hiệu năng truy vấn

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Có index: (`accountId`, `loginAt` giảm dần), (`loginAt` giảm dần), (`ipAddress`, `loginAt` giảm dần), (`accountType`, `loginAt` giảm dần)
- [ ] Mỗi tổ hợp lọc của FR-004 dùng được ít nhất một index, kiểm bằng `explain`
- [ ] p95 thời gian phản hồi API danh sách ≤ 1 giây với 5 triệu bản ghi

**Rationale:** Ambassador đặt index lệch tên trường (mục 2.4 #2). Đếm tổng số bản ghi là thao tác tốn nhất khi collection lớn.

---

#### NFR-007: Kiểm thử tự động

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Unit test phân tích User-Agent: Chrome trên macOS, Safari trên iPhone, Chrome trên Android, User-Agent rỗng, User-Agent không nhận dạng được
- [ ] Test cho từng điểm trong 9 điểm cấp phiên: thành công → đúng 1 bản ghi, đúng `method`; thất bại → 0 bản ghi
- [ ] Test quyền của API cho đủ các vai trò trong FR-005

**Rationale:** Lỗi lớn nhất của bản Ambassador là bỏ sót đường đăng nhập (mục 2.4 #1). Test theo danh sách điểm cấp phiên chặn lỗi này tái diễn khi thêm phương thức đăng nhập mới.

---

#### NFR-008: Backward Compatibility

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Request và response của 9 API cấp phiên không đổi
- [ ] Admin Portal, Dashboard, web creator không cần phát hành lại để đăng nhập tiếp tục hoạt động
- [ ] Rollback backend không ảnh hưởng dữ liệu khác

**Rationale:** Cho phép phát hành backend trước, Admin Portal sau, và rollback độc lập.

---

## 8. Key User Flows

### Flow 1: Điều tra tài khoản creator nghi bị chiếm

```
Creator báo không đăng nhập được, hoặc thấy bài đăng lạ
Admin nội bộ mở màn Người dùng → lấy ID creator
  → Mở Lịch sử đăng nhập → nhập ID → chọn 30 ngày gần nhất
  → Thấy một lần đăng nhập Facebook lúc 02:13 từ IP lạ, trình duyệt "Python Requests"
  → Rê chuột xem User-Agent gốc → xác nhận đăng nhập bằng script, không phải trình duyệt
  → Lọc theo IP đó → xem các tài khoản khác đăng nhập từ cùng IP
  → Xử lý theo quy trình sự cố
```

### Flow 2: Rà soát đăng nhập nhân sự định kỳ

```
Security mở Lịch sử đăng nhập
  → Loại tài khoản = Nhân sự; khoảng thời gian = tháng trước
  → Rà các lần đăng nhập ngoài giờ, IP ngoài văn phòng, tài khoản lâu không dùng bỗng đăng nhập
  → Lọc theo Phương thức = SSO Dashboard để xem ai đã vào Dashboard
```

### Flow 3: Ghi nhận (hệ thống)

```
Request đăng nhập → xác thực thành công → sinh token
  → Trả response cho client (không chờ)
  → Song song: phân tích User-Agent → ghi bản ghi
       ghi lỗi → log error, bỏ qua
```

---

## 9. Epics & Traceability Matrix

### EPIC-001: Login Event Capture

**Mô tả:** Ghi một bản ghi cho mỗi lần cấp phiên, ở đủ 9 điểm, không ảnh hưởng đăng nhập.
**Functional Requirements:** FR-001, FR-002, FR-003
**Story Count Estimate:** 3–4 stories
**Priority:** Must Have
**Business Value:** BO-1, BO-3, BO-4

---

### EPIC-002: Login History Review

**Mô tả:** API và màn tra cứu cho người có thẩm quyền.
**Functional Requirements:** FR-004, FR-005, FR-006
**Story Count Estimate:** 3 stories
**Priority:** Must Have
**Business Value:** BO-2

---

### Traceability Matrix

| Epic | Tên Epic | Functional Requirements | Non-Functional Requirements | Business Objectives | Story Estimate | Priority |
|---|---|---|---|---|---|---|
| EPIC-001 | Login Event Capture | FR-001, 002, 003 | NFR-001, 002, 003, 004, 005, 007, 008 | BO-1, BO-3, BO-4 | 3–4 | Must Have |
| EPIC-002 | Login History Review | FR-004, 005, 006 | NFR-004, 006, 007 | BO-2 | 3 | Must Have |

**Tổng stories ước tính:** 6–7 stories

---

## 10. Kế hoạch phát hành & Rollback

### Thứ tự phát hành

| Bước | Nội dung | Điều kiện |
|---|---|---|
| 1 | Backend: ghi nhận ở 9 điểm, API danh sách, index | OQ-2 đã có kết luận |
| 2 | Admin Portal: màn Lịch sử đăng nhập | Sau bước 1 |
| 3 | DevOps cấu hình nguồn IP thật (D-1) | Độc lập; càng sớm thì dữ liệu IP càng tin cậy |

**Nhánh:** theo quy ước repo `techcombank` — PR vào `develop`, đưa sang `release` bằng cherry-pick (như PR #768/#769). `release` có 5 commit riêng (PR #769 — vá bảo mật gap #43, chỉ ở phía public) nhưng không chạm file nào của tính năng.

### Rollback

- **Backend:** phát hành lại bản trước → ngừng ghi. Collection giữ nguyên, không ảnh hưởng chức năng khác
- **Admin Portal:** rollback độc lập; menu biến mất
- **Dữ liệu:** không có migration, không có gì cần hoàn tác

---

## 11. Dependencies

### Internal

- MongoDB — collection mới `login-histories` và 4 index (NFR-006)
- Thư viện `github.com/ua-parser/uap-go` — mới với T-Fluencers, Ambassador đang dùng
- Module audit admin (`pkg/admin/router/audit.go`) — nơi đặt endpoint mới
- Logger của hệ thống — log lỗi ghi (NFR-001)

### External

| # | Phụ thuộc | Bên thực hiện | Mức độ |
|---|---|---|---|
| D-1 | Cấu hình `IPExtractor` theo chuỗi proxy thật của T-Fluencers (xác nhận phía trước có Cloudflare, load balancer hay không) | DevOps | Khuyến nghị — quyết định NFR-005; tác động cả rate limiting đăng nhập |
| D-2 | Kết luận OQ-1, OQ-2 | Product Owner TCB, Security | Bắt buộc — OQ-2 trước khi phát triển FR-005 |

---

## 12. Assumptions

1. Lượng đăng nhập dưới 10.000 lần/ngày, tương đương khoảng 3,7 triệu bản ghi và dưới 2 GB/năm kể cả index. Cần DevOps xác nhận bằng access log
2. Creator chỉ đăng nhập qua trình duyệt. Nếu có ứng dụng di động gọi API đăng nhập, User-Agent của ứng dụng có thể không phân tích được (`Unknown`), nhưng User-Agent gốc vẫn được lưu
3. Admin Portal tiếp tục dùng umi 3
4. Nhân sự nội bộ không gắn ADV; nhân sự của ADV luôn gắn ADV
5. `x-device-id` do client tự sinh, không phải định danh phần cứng; chỉ dùng để đối chiếu phiên

---

## 13. Open Questions & Resolved Questions

### 13.1 Open Questions

| # | Câu hỏi | Đề xuất | Tác động | Owner | Hạn |
|---|---|---|---|---|---|
| OQ-1 | Có ghi đăng xuất của nhân sự trong đợt này không (SRS §5.5)? | Không, tách đợt sau. Hiện đăng xuất của nhân sự chỉ xoá token ở trình duyệt, không gọi backend. Muốn ghi phải thêm API đăng xuất và sửa cả Admin Portal lẫn Dashboard. Phiên hết hạn hay đóng trình duyệt cũng không sinh sự kiện, nên log đăng xuất luôn thiếu, giá trị truy vết thấp hơn log đăng nhập | Nếu làm: thêm 1 FR — API `POST /staffs/logout` ghi sự kiện, 2 frontend gọi API này khi đăng xuất | Product Owner TCB, Security | Trước khi chốt phạm vi |
| OQ-2 | Admin của ADV có được xem Lịch sử đăng nhập không? | Không — chỉ Root và Admin không gắn ADV (FR-005) | Nếu có: dùng nguyên `IsAdmin` như Ambassador, Admin của ADV thấy IP và thiết bị của mọi tài khoản. Giới hạn theo ADV thì không được với creator, vì creator không gắn ADV | Product Owner TCB, Security | Trước khi phát triển FR-005 |

### 13.2 Resolved Questions

| # | Câu hỏi | Quyết định | Căn cứ |
|---|---|---|---|
| RQ-1 | Lưu email, tên trong bản ghi như Ambassador? | Không — chỉ lưu ID, tra email và tên lúc hiển thị | SRS §5.5 |
| RQ-2 | Thời hạn lưu? | Không xoá; tối thiểu 12 tháng | SRS §5.6. Ambassador cũng không làm TTL (PRD Mời nhân sự Ambassador v1.3) |
| RQ-3 | Giữ trường và bộ lọc ADV? | Không | Mục 2.3 |
| RQ-4 | Ghi 3 endpoint creator mà web không gọi? | Có | Endpoint công khai, cấp token hợp lệ; mục 2.4 #1 |
| RQ-5 | SSO exchange có tính là một lần đăng nhập? | Có, với phương thức riêng | Cấp token mới cho một ứng dụng khác; không ghi thì không biết ai đã vào Dashboard |

---

## 14. Risks & Mitigation

| # | Rủi ro | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|---|
| R-1 | IP bị giả mạo vì chưa cấu hình nguồn IP thật | Cao | Kết luận điều tra sai | D-1; lưu User-Agent gốc và `deviceId` làm dấu hiệu bổ sung |
| R-2 | Thêm phương thức đăng nhập mới mà quên ghi | Trung bình — đã xảy ra ở Ambassador | Lịch sử thiếu mà không ai biết | NFR-007; khi review: mọi chỗ sinh token phiên đều phải ghi |
| R-3 | Collection tăng không giới hạn | Chắc chắn, tốc độ thấp | Dung lượng tăng, đếm tổng chậm dần | Theo dõi dung lượng; thêm TTL ≥ 12 tháng khi cần (mục 5) |
| R-4 | Admin của ADV xem được dữ liệu ngoài phạm vi | Tuỳ kết luận OQ-2 | Lộ dữ liệu Confidential | FR-005 |
| R-5 | `uap-go` chậm với User-Agent bất thường (phân tích bằng regex) | Thấp | Tăng CPU khi đăng nhập dồn dập | Chạy ngoài luồng xử lý đồng bộ (NFR-001); bộ phân tích khởi tạo một lần |
| R-6 | Lược đồ dữ liệu khác Ambassador | Chắc chắn | Không dùng chung truy vấn, báo cáo giữa hai sản phẩm | Chấp nhận — hai sản phẩm không dùng chung dữ liệu |

---

## 15. Prioritization Summary

| Loại | Must Have | Should Have | Could Have | Tổng |
|---|---|---|---|---|
| Functional Requirements | 6 (FR-001 → FR-006) | 0 | 0 | 6 |
| Non-Functional Requirements | 6 (NFR-001 → 004, 007, 008) | 2 (NFR-005, 006) | 0 | 8 |

---

## 16. Stakeholders

| Vai trò | Tên/Nhóm | Trách nhiệm |
|---|---|---|
| Product Owner | TCB — chưa phân công | Phê duyệt PRD; kết luận OQ-1, OQ-2 |
| Security / kiểm toán | TCB — chưa phân công | Duyệt FR-005, NFR-002 → NFR-005; nghiệm thu theo SRS §5 |
| Admin vận hành nội bộ | VFDC | Người dùng chính của màn tra cứu |
| Development Team | — | Phát triển theo PRD và tech spec |
| QA | — | Viết và chạy test case theo Acceptance Criteria |
| DevOps | — | D-1; theo dõi dung lượng collection |

---

## 17. Trạng thái triển khai

Chưa phát triển. Chưa có tech spec.

---

## Phụ lục A: API

| Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/audits/login-histories` | Danh sách sự kiện đăng nhập | FR-005 |

**Tham số:** `page`, `limit`, `accountId`, `email`, `accountType`, `method`, `ip`, `fromAt`, `toAt`.

**Ví dụ phản hồi:**

```json
{
  "data": [
    {
      "_id": "6720f1c2a8b4e51d3c9f0a11",
      "accountId": "65f0c3d2e4b0a1b2c3d4e5f6",
      "accountType": "staff",
      "role": "admin",
      "method": "sso_exchange",
      "email": "nguyen.van.a@example.com",
      "name": "Nguyễn Văn A",
      "ipAddress": "203.0.113.24",
      "device": "Desktop",
      "model": "Mac",
      "platform": "Mac OS X",
      "browser": "Chrome",
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
      "deviceId": "d3b07384-d9a0-4f5c-8b1e-2f6a7c1e9b40",
      "loginAt": "2026-10-02T03:15:42Z"
    }
  ],
  "total": 1,
  "limit": 20
}
```

`email` và `name` không lưu trong bản ghi; API tra theo `accountId` lúc trả về (FR-003).

---

## Phụ lục B: Điểm cấp phiên của T-Fluencers

| # | Loại | Endpoint | Hàm (dòng sinh token) | `method` | Ambassador |
|---|---|---|---|---|---|
| 1 | Nhân sự | `POST /staffs/login` | `staffImpl.Login` (`pkg/admin/service/staff.go:181`) | `password` | Có ghi |
| 2 | Nhân sự | `POST /staffs/invite/accept` | `staffImpl.AcceptInvite` (`:772`) | `accept_invite` | Không cấp phiên ở bước này |
| 3 | Nhân sự | `POST /staffs/auth/exchange` | `staffImpl.ExchangeAuthCode` (`:913`) | `sso_exchange` | Không có luồng này |
| 4 | Creator | `POST /users/login-with-google` | `userImpl.LoginWithGoogle` (`pkg/public/service/user.go:1946`) | `google` | Có ghi |
| 5 | Creator | `POST /users/login-with-tiktok` | `userImpl.LoginWithTiktok` (`:1823`) | `tiktok` | Có ghi |
| 6 | Creator | `POST /users/login-with-facebook` | `userImpl.LoginWithFacebook` (`:973`) | `facebook` | **Không ghi** |
| 7 | Creator | `POST /users/login-with-instagram` | `userImpl.LoginWithInstagram` (`:396`) | `instagram` | Endpoint đã tắt |
| 8 | Creator | `POST /users/login` | `userImpl.LoginWithPassword` (`:2045`) | `password` | **Không ghi** |
| 9 | Creator | `POST /users/register` | `userImpl.Register` (`:2092`) | `register` | **Không ghi** |

`staffImpl.Register` (tạo nhân sự) không cấp token — dòng cấp token đã bị comment (`staff.go:137`) — nên không phải điểm cấp phiên.

---

## Phụ lục C: Đối chiếu trường dữ liệu Ambassador ↔ T-Fluencers

| Ambassador | T-Fluencers | Lý do |
|---|---|---|
| `userId` | `accountId` | Gồm cả nhân sự lẫn creator |
| — | `accountType` | Lọc nhanh nhân sự / creator |
| `role` (`admin` / `creator`) | `role` (mã vai trò thật, `root`, `creator`) | Mục 2.4 #5 |
| — | `method` | 9 điểm cấp phiên (mục 2.3) |
| `email`, `username` | — (tra lúc hiển thị) | SRS §5.5 (mục 2.4 #4) |
| `partnerId`, `partnerName` | — | Mục 2.3 |
| `device`, `model`, `platform`, `browser` | Giữ nguyên | |
| — | `userAgent` | FR-003 |
| — | `deviceId` | FR-003 |
| `ipAddress` | Giữ nguyên | |
| `loginAt` | Giữ nguyên | |
| `createdAt`, `updatedAt` | Chỉ `loginAt` | Append-only, không cập nhật |

---

## Lịch sử thay đổi

| Version | Ngày | Người thực hiện | Nội dung |
|---|---|---|---|
| 1.0 | 2026-10-02 | Nguyễn Đăng Định | Bản đầu tiên |

---

*PRD Version 1.0 — 2026-10-02*
*Tech spec: chưa có*
