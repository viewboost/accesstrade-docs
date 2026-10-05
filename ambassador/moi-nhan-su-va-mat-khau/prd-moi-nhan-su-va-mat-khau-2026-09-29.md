# Product Requirements Document: Mời nhân sự qua email và tự quản lý mật khẩu — Ambassador Admin Portal

**Project:** Ambassador — Admin Portal
**Date:** 2026-09-29
**Author:** Nguyễn Đăng Định
**Reviewer:** Review nội bộ 2026-09-29 (2 lượt). Chờ phân công Product Owner và Security
**Version:** 2.1
**Project Level:** Level 2
**Status:** Final — không còn Open Question; chờ Product Owner và Security phê duyệt
**Phạm vi:** Admin Portal dùng chung cho mọi ADV. Không thay đổi luồng đăng nhập của creator (trừ bản vá HF-2, mục 2.5).

---

## Document Overview

PRD cho hạng mục số 3 của kế hoạch tháng 10/2026 — *"Mời tài khoản và quản lý mật khẩu cho admin, vận hành"*. Tài liệu hợp nhất hai gap đã phân tích: **gap #40** (vòng đời mật khẩu của tài khoản nhân sự) và **gap #12** (bảo vệ endpoint đăng nhập admin), theo đề xuất ghép trong kế hoạch.

Hiện trạng được xác minh trên mã nguồn `AT-Core/ambassador` ngày 2026-09-29, trên hai nhánh: `release` — bản đang chạy production (`ccda54288`, 2026-09-17) — và `develop` (`254dc9c30`, 2026-09-24). `develop` đi trước `release` 189 commit, `release` không có commit riêng. Chỗ nào hai nhánh khác nhau, tài liệu ghi rõ.

### Nguyên tắc

**Lấy T-Fluencers làm tham chiếu.** Tính năng này đã chạy production trên T-Fluencers từ 02/2026 (PRD `staff-invite-auth`). Cơ chế nào đúng thì giữ.

Chỉ đi khác ở ba loại tình huống, mỗi chỗ ghi rõ lý do:

1. **Bắt buộc do kiến trúc** — Ambassador khác T-Fluencers về ứng dụng frontend và mô hình quyền (mục 2.2)
2. **T-Fluencers không có** — thu hồi lời mời, thời điểm nhận lời mời, rate limiting cho quên mật khẩu
3. **Sửa lỗi đã kiểm chứng trên mã nguồn T-Fluencers** — mục 2.3

**Related Documents:**

- Gap #40: `general/gaps/p1/40-staff-account-password-and-invite-flow.md`
- Gap #12: `general/gaps/p3/12-admin-login-security.md`
- PRD tham chiếu (T-Fluencers): `staff-invite-auth/prd-staff-invite-auth-2026-02-24.md`
- PRD liên quan: `ambassador/phan-quyen-van-hanh/prd-phan-quyen-van-hanh-2026-09-25.md` — viết tắt **PQ**
- Kế hoạch tháng 10: `plan/2026-10/2026-10-monthly-plan-email.html`
- Tech spec: [`techspec-moi-nhan-su-va-mat-khau-2026-09-29.md`](./techspec-moi-nhan-su-va-mat-khau-2026-09-29.md)
- Bàn giao template email cho AccessTrade (theo khuôn TCB): [`TEMPLATE_EMAIL.md`](./TEMPLATE_EMAIL.md)
- Mẫu email gửi AccessTrade: [`email-templates/staff_invite_email.html`](./email-templates/staff_invite_email.html), [`email-templates/staff_reset_password_email.html`](./email-templates/staff_reset_password_email.html)

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Root** | Nhân sự có cờ `isRoot`. Là vai trò duy nhất quản lý được tài khoản nhân sự. Theo kế hoạch tháng 10, hệ thống chỉ còn **một** tài khoản Root, do AT giữ |
| **ADV** | Advertiser — đối tác/thương hiệu chạy chương trình trên Ambassador. Trong mã nguồn là `partner` |
| **Nhân sự** (staff) | Tài khoản đăng nhập Admin Portal. Khác với creator (người dùng cuối) |
| **Luồng cũ** | Hai chức năng Root đang dùng: tạo nhân sự kèm mật khẩu do Root đặt, và Root đặt lại mật khẩu cho người khác. Là **cách cấp và đặt mật khẩu**, không phải tài khoản cũ — tắt luồng cũ không ảnh hưởng tài khoản đang có |
| **Lời mời** (invitation) | Tài khoản nhân sự được tạo ở trạng thái chờ, kích hoạt khi người nhận tự đặt mật khẩu qua đường dẫn trong email |
| **Single-use token** | Mã ngẫu nhiên nhúng trong đường dẫn email, mất hiệu lực ngay sau lần dùng đầu tiên |
| **TTL** | Time-to-live — thời hạn hiệu lực của token |
| **Brute-force attack** | Tấn công dò mật khẩu bằng cách thử liên tục nhiều mật khẩu |
| **Account enumeration** | Kỹ thuật dò xem một email có tài khoản hay không, dựa trên khác biệt về nội dung, mã lỗi hoặc thời gian phản hồi |
| **Rate limiting** | Giới hạn số lần gọi một endpoint trong một khoảng thời gian |
| **Fixed window** | Cách đếm rate limiting theo khung thời gian cố định, bắt đầu từ lần đếm đầu tiên |
| **Session invalidation** | Vô hiệu hoá toàn bộ phiên đăng nhập đang mở của một tài khoản |
| **Fail-closed** | Khi thành phần kiểm soát gặp sự cố thì từ chối, thay vì cho đi tiếp |
| **Silent failure** | Lỗi xảy ra nhưng hệ thống vẫn báo thành công |
| **Kill switch** | Cơ chế tắt nhanh một tính năng trên môi trường đang chạy mà không cần phát hành lại |
| **Audit log** | Nhật ký thao tác, ghi người thực hiện, hành động và đối tượng bị tác động |
| **Email template (AT)** | Mẫu email do AccessTrade lưu giữ. Hệ thống chỉ gửi mã template kèm dữ liệu điền vào |
| **Hotfix** | Bản vá lỗi bảo mật; có thể tách PR phát hành lên `release` trước tính năng chính |

---

## 1. Executive Summary

Hiện nay, tài khoản Admin Portal được cấp theo quy trình thủ công: Root tự đặt mật khẩu cho nhân sự mới, rồi gửi mật khẩu qua Zalo hoặc email. Nhân sự quên mật khẩu phải chờ Root đặt lại. Nhân sự không có chức năng tự đổi mật khẩu. Endpoint đăng nhập không giới hạn số lần thử.

Hệ quả là mật khẩu được chia sẻ qua kênh không an toàn và tồn tại trong lịch sử tin nhắn. Root nắm mật khẩu của mọi tài khoản do mình tạo. Rà soát mã nguồn cho PRD này phát hiện thêm ba lỗi đang chạy trên production: hash mật khẩu của mọi nhân sự đọc được qua audit log, mật khẩu dài quá 72 byte làm hỏng tài khoản mà không báo lỗi, và API tạo nhân sự trả về cho Root một phiên đăng nhập của tài khoản vừa tạo. Ba lỗi này được vá trong cùng đợt (HF-1 → HF-3, mục 2.5), có thể phát hành trước tính năng nếu cần.

PRD này thay quy trình thủ công bằng cơ chế mời qua email dùng token, kèm các chức năng tự phục vụ:

```
Root nhập email + vai trò + ADV
  → Hệ thống tạo tài khoản ở trạng thái chờ (chưa có mật khẩu, chưa kích hoạt)
  → Gửi email mời, đường dẫn hiệu lực 48 giờ, dùng một lần
  → Nhân sự tự đặt mật khẩu → tài khoản kích hoạt
  → Đăng nhập tại Admin Portal (email không phân biệt chữ hoa/thường)

Nhân sự quên mật khẩu → tự đặt lại qua email (60 phút, dùng một lần)
Nhân sự đang đăng nhập → tự đổi mật khẩu (bắt buộc mật khẩu hiện tại)
Endpoint đăng nhập, quên mật khẩu, đổi mật khẩu → rate limiting, fail-closed
```

**Phạm vi:** backend và Admin Portal (umi 3). Áp dụng cho mọi ADV. Không có cờ bật/tắt theo ADV vì đây là tính năng của Admin Portal, không phải của một thương hiệu.

---

## 2. Bối cảnh

### 2.1 Hiện trạng Ambassador — đã verify trên mã nguồn

Mặc định là nhánh `release` (production). Dòng nào chỉ đúng trên `develop` có ghi chú.

| Thành phần | Hiện trạng | Bằng chứng |
|---|---|---|
| Quyền quản lý nhân sự | Cả 5 endpoint (tạo, sửa, đặt mật khẩu hộ, bật/tắt, danh sách) chỉ Root gọi được | `pkg/admin/router/staff.go` — group `gSetup` dùng middleware `IsRoot` |
| Tạo nhân sự | Root nhập mật khẩu, tối thiểu 6 ký tự, không giới hạn trên | `pkg/admin/model/request/staff.go` — `StaffRegisterBody.Validate` |
| Phản hồi API tạo nhân sự | Trả về token phiên đăng nhập (8 giờ) của tài khoản vừa tạo. Admin FE không đọc trường này | `pkg/admin/service/staff.go` — `Register`; `admin/src/pages/staff/model.ts` |
| **Hash mật khẩu trong audit log** | Mỗi lần tạo / sửa / đặt mật khẩu / bật-tắt nhân sự, audit ghi nguyên bản ghi nhân sự dạng JSON; trường `Password` không có `json:"-"` nên hash bcrypt nằm trong `audits.data`. `GET /audits` chỉ yêu cầu đăng nhập, không lọc phạm vi — mọi nhân sự, kể cả cộng tác viên, đọc được hash của Root | `internal/model/mg/staff.go`; `pkg/admin/router/audit.go` |
| **Mật khẩu quá 72 byte** | `golang.org/x/crypto` v0.47.0 trả `ErrPasswordTooLong`; `util.HashPassword` bỏ qua lỗi và trả chuỗi rỗng; hash rỗng được lưu — tài khoản không đăng nhập được, không có thông báo lỗi. Áp dụng cho cả nhân sự (tạo, đặt hộ) lẫn creator (đăng ký) | `internal/util/hash.go` |
| Đăng nhập | So khớp email chính xác từng ký tự. Không giới hạn số lần thử. Chỉ chạy bcrypt khi email tồn tại — thời gian phản hồi lộ ra email nào có tài khoản | `pkg/admin/service/staff.go` — `Login` |
| Tính duy nhất của email | Collection `staffs` không có ràng buộc duy nhất. Kiểm tra trùng khi tạo phân biệt chữ hoa/thường. Kiểm tra trùng khi sửa dùng điều kiện `"$nin"` ở cấp gốc — truy vấn không hợp lệ, đếm ra 0, nên chưa từng có tác dụng | `pkg/admin/service/staff.go` — `Register`, `UpdateInfo` |
| Endpoint `POST /staffs/login-with-google` | Route công khai; cả handler lẫn validation chỉ có `panic("implement me")`. Frontend không gọi | `pkg/admin/handler/staff.go`, `routevalidation/staff.go` |
| Mời qua email · Quên / đặt lại mật khẩu · Tự đổi mật khẩu · Rate limiting đăng nhập | ❌ Không có | — |
| Lịch sử đăng nhập | ⚠️ Có trên `develop` từ 2026-09-15, **chưa có trên `release`** — production chưa ghi lịch sử đăng nhập. Trên `develop` chỉ ghi lần thành công, không lọc theo ADV | `internal/service/login_history.go`, commit `8f9faa169` |
| Xác định IP client | `c.RealIP()`, chưa cấu hình `IPExtractor` → đọc header `X-Forwarded-For` do client gửi, có thể giả mạo | `internal/echo/echo.go` |
| Kênh gửi email | API email của AccessTrade (`/v1.0/partner/email/send`), dùng template do AT cấp mã. Module SMTP có trong repo nhưng không được gọi | `internal/constants/email_template.go` |
| Tiến độ cấp template của AT | Template cảnh báo đối soát khai báo từ 2026-08-12, hằng số vẫn ghi "CHƯA ĐƯỢC AccessTrade CẤP" | `internal/constants/email_template.go`, commit `fb3d122d2` |
| Email từ backend admin | Chỉ có một luồng gửi: cảnh báo lệch số liệu khi chi đối soát. Template chưa được cấp nên theo mã nguồn luồng này chưa gửi thành công. Email đang chạy thật duy nhất (OTP) thuộc backend **public**. Khoá `ACCESS_TRADE_SMS_*` không bắt buộc khi khởi động — backend admin thiếu khoá vẫn chạy, chỉ gửi email thất bại | `pkg/admin/service/reconciliation_running.go:121`; `pkg/public/service/user.go`; `internal/config/env.go` |

### 2.2 Khác biệt bắt buộc do kiến trúc

| Điểm | T-Fluencers | Ambassador | Hệ quả |
|---|---|---|---|
| Nơi nhân sự đăng nhập | Ứng dụng `dashboard` (Next.js 16) | Admin Portal (umi 3, antd 4) | Các trang nhận lời mời, quên mật khẩu, đặt lại mật khẩu phải **viết mới** trên Admin Portal; không tái sử dụng được mã frontend của T-Fluencers |
| Kênh email | Dịch vụ email của AT (`smsgw-service`, `/v1.0/partner/email/send`) khi bật `AT_GATEWAY_EMAIL_ENABLE`, template `TECHCOMBANK_EMAIL_STAFF_INVITE` và `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD`; SMTP dự phòng | Cùng dịch vụ email của AT, khác bộ khoá client (`ACCESS_TRADE_SMS_*`) | **Cùng dịch vụ, cùng bộ biến dữ liệu.** Đề nghị AT nhân bản hai template của TCB sang client Ambassador, đổi thương hiệu, thay vì thiết kế mới (D-1). Template có thể gắn theo client — cần AT xác nhận |
| Quyền quản lý nhân sự | Admin theo ADV được mời | Chỉ Root | Giữ nguyên chỉ Root (FR-001) |
| ADV của nhân sự | Bắt buộc; mỗi ADV tối đa một Admin | Tuỳ chọn; không giới hạn số Admin | Không port luật của TCB |

### 2.3 Lỗi của T-Fluencers — sửa, không port

| # | Lỗi trên T-Fluencers | Rủi ro | Cách xử lý trong PRD này |
|---|---|---|---|
| 1 | API tự đổi mật khẩu có trường mật khẩu hiện tại là **tuỳ chọn** | Chiếm được một phiên đăng nhập là đổi được mật khẩu và khoá chủ tài khoản ra ngoài (account takeover) | Bắt buộc mật khẩu hiện tại — FR-010 |
| 2 | Endpoint quên mật khẩu **không có rate limiting** | Gửi email hàng loạt vào hộp thư của nhân sự (email flooding) | FR-012 |
| 3 | Đường dẫn mời được trả về cho admin; thao tác gửi lại tự copy đường dẫn vào clipboard | Đường dẫn tiếp tục được chia sẻ qua kênh chat — đúng vấn đề tính năng cần loại bỏ | Không trả đường dẫn về cho admin — FR-001 |
| 4 | Mời hàng loạt xử lý song song, mỗi dòng tự kiểm tra trùng rồi mới ghi | Hai dòng trùng email trong cùng danh sách tạo ra hai tài khoản | Kiểm tra trùng trong danh sách trước, ghi tuần tự — FR-002 |
| 5 | Rate limiting đăng nhập đếm theo IP, đếm cả lần thành công, khoá 2 giờ, mặc định **tắt** | Một văn phòng dùng chung IP có thể bị khoá toàn bộ; giả mạo IP qua header là vượt được | Đếm lần thất bại theo email là lớp chính — FR-011 |
| 6 | Mời không kiểm tra ADV đích so với ADV của người mời | Admin của ADV này mời được nhân sự vào ADV khác | Không phát sinh vì chỉ Root được mời |

### 2.4 Liên hệ với PRD Phân quyền vận hành (PQ) và kế hoạch tháng 10

| Nguồn | Nội dung | Ảnh hưởng tới PRD này |
|---|---|---|
| **Kế hoạch tháng 10** | "Chỉ còn một tài khoản quyền cao nhất duy nhất, do AT giữ"; phân quyền là "bước đi trước của việc mời tài khoản qua email" | Mọi lời mời do tài khoản Root của AT thực hiện. Biz vận hành không tự mời, mà gửi danh sách cho AT — chức năng mời hàng loạt (FR-002) phục vụ đúng việc này |
| **PQ-011** | Tạo, sửa, đổi mật khẩu, bật/tắt nhân sự giữ nguyên chỉ Root | Căn cứ để chức năng mời chỉ dành cho Root (FR-001). "Đổi mật khẩu" trong PQ-011 là đổi mật khẩu **của người khác**; nhân sự tự đổi mật khẩu của mình (FR-010) không thuộc phạm vi đó |
| **PQ-010** | Không endpoint nào còn ở mức "chỉ cần đăng nhập"; CI báo đỏ khi thiếu khai báo vai trò | Endpoint tự đổi mật khẩu (chỉ cần đăng nhập) và 4 endpoint công khai được khai báo là **ngoại lệ có chủ đích** trong bảng endpoint–vai trò của PQ (Phụ lục A) |
| **PQ-001** | Nhân sự không phải Root mà chưa gắn ADV bị từ chối mọi thao tác (fail-closed) | Sau khi PQ-001 phát hành, ADV là trường bắt buộc khi mời vai trò không phải Root (RQ-4, mục 13.2) |
| **PQ-002** | Nhân sự gắn được nhiều ADV | Form mời chuyển sang chọn nhiều ADV khi PQ-002 phát hành |
| **PQ-008** | Tài khoản có ngày hết hiệu lực | Ngoài phạm vi; có thể bổ sung trường hạn dùng vào form mời ở đợt sau |
| **PQ-009** | Audit log có trường hành động và ADV; đọc audit trong phạm vi ADV | Sự kiện audit của FR-014 chuyển theo cấu trúc PQ-009. Việc giới hạn phạm vi đọc `/audits` thuộc PQ-009 |

PQ thay tài khoản Root dùng chung bằng tài khoản riêng cho từng người, nên số lần cấp tài khoản sẽ tăng. Không có PRD này, mỗi tài khoản mới vẫn là một mật khẩu được chia sẻ qua kênh chat.

### 2.5 Bản vá bảo mật đi kèm (HF-1 → HF-3)

Ba lỗi đang chạy trên production (mục 2.1) không phụ thuộc tính năng mời. Chúng được làm thành các thay đổi riêng (HF-1 → HF-3) trong cùng nhánh của tính năng; khi cần phát hành gấp, tách các thay đổi này ra một PR riêng vào `release`:

| # | Nội dung | Thay đổi |
|---|---|---|
| **HF-1** | Chấm dứt lộ hash mật khẩu qua audit log | Thêm `json:"-"` cho trường `Password`; script `backend/scripts/strip-staff-password-from-audits.js` xoá hash khỏi các bản ghi audit cũ (chạy thử mặc định, có hướng dẫn backup) |
| **HF-2** | Chặn mật khẩu quá 72 byte ở mọi luồng | Kiểm tra 72 byte cho tạo nhân sự, đặt mật khẩu hộ, đăng ký creator; `util.HashPassword` ghi log khi bcrypt lỗi thay vì bỏ qua |
| **HF-3** | Không cấp phiên đăng nhập cho tài khoản vừa tạo | Bỏ token khỏi phản hồi API tạo nhân sự |

Giới hạn phạm vi đọc `/audits` không thuộc hotfix (thuộc PQ-009).

---

## 3. Business Objectives

| # | Mục tiêu | Chỉ số thành công (KPI) | Cách đo |
|---|---|---|---|
| BO-1 | Loại bỏ việc chia sẻ mật khẩu qua kênh không an toàn | Trước khi tắt luồng cũ: ≥ 90% tài khoản không phải Root tạo mới đi qua lời mời. Sau khi tắt luồng cũ (RQ-11): 100% | Tỷ lệ tài khoản mới có trường `inviteStatus` |
| BO-2 | Nhân sự tự khôi phục quyền truy cập, không phụ thuộc Root | Số lần Root đặt mật khẩu hộ giảm ≥ 90% so với 30 ngày trước phát hành | Đếm audit "Đã cập nhật mật khẩu" |
| BO-3 | Rút ngắn thời gian cấp tài khoản khi tiếp nhận ADV mới | ≥ 90% lời mời được nhận trong vòng 48 giờ kể từ lần gửi gần nhất | `acceptedAt − invitedAt` |
| BO-4 | Giảm bề mặt tấn công vào endpoint xác thực | 100% yêu cầu vượt ngưỡng nhận HTTP 429; lần bị chặn được ghi log (NFR-013) | Log/giám sát (NFR-013) |
| BO-5 | Truy vết được việc cấp quyền truy cập | 100% tài khoản tạo qua lời mời có người gửi lời mời gần nhất, thời điểm gửi, thời điểm nhận; lịch sử từng lần gửi có trong audit log | Trường `invitedBy`, `invitedAt`, `acceptedAt`; audit log |

---

## 4. User Personas

### Persona 1: Root — Quản trị hệ thống

- **Vai trò:** Tài khoản quyền cao nhất duy nhất, do AT giữ (kế hoạch tháng 10). Thực hiện mọi thao tác cấp tài khoản
- **Pain point:** Phải tự đặt mật khẩu, gửi qua kênh chat, xử lý yêu cầu đặt lại mật khẩu; không biết ai đã đăng nhập được, ai chưa
- **Mục tiêu:** Cấp tài khoản nhanh và an toàn, cấp hàng loạt theo danh sách biz gửi, theo dõi được trạng thái từng tài khoản

### Persona 2: Nhân sự mới được mời

- **Vai trò:** Nhân sự VFDC, biz vận hành hoặc nhân sự của ADV. Không phải kỹ sư
- **Pain point:** Nhận mật khẩu qua kênh không chính thức, không có hướng dẫn kích hoạt
- **Mục tiêu:** Kích hoạt tài khoản trong vài bước, tự đặt mật khẩu

### Persona 3: Nhân sự hiện hữu

- **Vai trò:** Đã có tài khoản, sử dụng Admin Portal hằng ngày
- **Pain point:** Quên mật khẩu phải chờ Root; nghi mật khẩu bị lộ nhưng không tự đổi được
- **Mục tiêu:** Tự xử lý mọi vấn đề về mật khẩu

### Persona 4: Manager biz vận hành

- **Vai trò:** Phụ trách một hoặc nhiều ADV. Không có quyền Root (PQ); gửi danh sách người cần cấp tài khoản cho AT
- **Pain point:** Mỗi đợt tiếp nhận ADV mới phải chờ cấp từng tài khoản thủ công
- **Mục tiêu:** Nhóm có tài khoản ngay khi bắt đầu vận hành ADV

---

## 5. Scope

### Trong phạm vi (In Scope)

- Mời một nhân sự và mời hàng loạt qua email
- Theo dõi trạng thái lời mời; gửi lại và thu hồi lời mời
- Trang công khai nhận lời mời và đặt mật khẩu lần đầu
- Quên mật khẩu và đặt lại mật khẩu qua email, có rate limiting
- Nhân sự tự đổi mật khẩu khi đã đăng nhập
- Đăng nhập không phân biệt chữ hoa/thường của email; chống account enumeration qua thời gian phản hồi
- Bỏ token khỏi phản hồi API tạo nhân sự; kiểm tra trùng email không phân biệt chữ hoa/thường ở mọi luồng
- Rate limiting cho endpoint đăng nhập (gap #12)
- Vá 3 lỗi bảo mật đang có trên production (HF-1 → HF-3, mục 2.5)
- Gỡ route `POST /staffs/login-with-google`

### Ngoài phạm vi (Out of Scope)

| Hạng mục | Rủi ro tồn dư | Điều kiện kích hoạt |
|---|---|---|
| Xác thực hai lớp (2FA) | Trung bình. Mật khẩu lộ là đủ để đăng nhập | Đối tác lớn yêu cầu trong đợt rà soát bảo mật, hoặc phát sinh sự cố |
| Đăng nhập Google/SSO cho admin | Thấp | Có nhu cầu SSO với tổ chức của đối tác |
| Thay đổi thời hạn phiên đăng nhập (8 giờ) | Thấp | — |
| Ngày hết hiệu lực tài khoản | Trung bình. Tài khoản cấp tạm không tự đóng | Thuộc PQ-008 |
| Nhân sự gắn nhiều ADV | — | Thuộc PQ-002 |
| Giới hạn phạm vi đọc `/audits` và Lịch sử đăng nhập theo ADV | Trung bình. Nhân sự ADV này đọc được nhật ký và lần đăng nhập sai của ADV khác | Thuộc PQ-001, PQ-009 |
| Tắt luồng cũ (tạo kèm mật khẩu cho nhân sự không phải Root, đặt mật khẩu hộ) | Trung bình. Cho tới khi tắt, BO-1 phụ thuộc vào việc Root chủ động dùng luồng mới | Email mời và quên mật khẩu đã chạy thật trên production (RQ-11) |
| Email thông báo "mật khẩu vừa được thay đổi" | Thấp–trung bình. Chủ tài khoản không biết khi mật khẩu bị đổi | Cần thêm một template AT; đề xuất đợt sau |
| Chuẩn hoá Unicode (NFC) cho mật khẩu | Thấp. Mật khẩu có dấu gõ trên hai bộ gõ khác nhau có thể không khớp | Không làm: áp NFC khi đăng nhập sẽ làm hỏng mật khẩu hiện có đang lưu ở dạng khác |
| Ràng buộc duy nhất cho email ở tầng cơ sở dữ liệu | Rất thấp. Chỉ một tài khoản Root tạo nhân sự; hai yêu cầu tạo cùng email cùng lúc gần như không xảy ra, và code đã kiểm tra trùng trước khi tạo | Không làm (RQ-10) |
| Ghi lần đăng nhập thất bại (FR-013) — đặc tả ở Phụ lục E | Thấp. Lần dò mật khẩu bị chặn bởi FR-011 nhưng không để lại dấu vết trong Lịch sử đăng nhập | Tính năng Lịch sử đăng nhập phát hành lên `release` (hiện chỉ có trên `develop`) |
| Tài khoản creator | — | Luồng đăng nhập khác; chỉ có bản vá HF-2 |

---

## 6. Functional Requirements

### EPIC-001: Invite Management

---

#### FR-001: Mời một nhân sự qua email

**Priority:** Must Have

**Description:**
Root mời nhân sự mới bằng email. Hệ thống tạo tài khoản ở trạng thái chờ và gửi email chứa đường dẫn kích hoạt. Root không nhập và không biết mật khẩu của nhân sự.

**Business Rules:**

- Form gồm: Họ tên (bắt buộc), Email (bắt buộc), Vai trò (bắt buộc), ADV (tuỳ chọn tới khi PQ-001 phát hành — RQ-4)
- Chỉ Root thực hiện được (PQ-011, RQ-3). Lời mời không tạo được tài khoản Root
- Tài khoản chờ: chưa có mật khẩu, `active = false`, không đăng nhập được bằng bất kỳ mật khẩu nào
- Email được chuẩn hoá (bỏ khoảng trắng, chuyển chữ thường). Kiểm tra trùng không phân biệt chữ hoa/thường trên toàn bộ tài khoản, kể cả tài khoản đang chờ hoặc đã thu hồi
- Email được kiểm tra cả định dạng lẫn tên miền nhận thư (MX/host), để phát hiện lỗi gõ nhầm trước khi gửi
- API và giao diện **không trả về đường dẫn mời** cho Root, dưới bất kỳ hình thức nào (RQ-1)
- Gửi email thất bại: vẫn giữ tài khoản chờ, trả về `emailSent = false`, giao diện hiển thị cảnh báo tương ứng

**Acceptance Criteria:**

- [ ] Có nút "Mời qua email" trên màn Nhân viên
- [ ] Mời email mới: tài khoản xuất hiện trong danh sách với trạng thái "Chờ nhận"; email được gửi tới người nhận
- [ ] Đăng nhập bằng email vừa mời trước khi nhận lời mời: thất bại với mọi mật khẩu
- [ ] Mời email đã tồn tại (khác chữ hoa/thường): hiển thị lỗi "Email đã tồn tại", không tạo tài khoản
- [ ] Phản hồi API và giao diện không chứa đường dẫn hay token mời
- [ ] Nhân sự không phải Root gọi trực tiếp API mời: bị từ chối

**Dependencies:** FR-015, D-1, D-3

---

#### FR-002: Mời hàng loạt

**Priority:** Should Have

**Description:**
Root mời nhiều nhân sự trong một thao tác, dùng chung một vai trò và một ADV. Phục vụ tình huống biz gửi danh sách khi tiếp nhận ADV mới.

**Business Rules:**

- Vai trò và ADV chọn một lần, áp dụng cho toàn bộ danh sách
- Nhập danh sách mỗi dòng một người, định dạng `email` hoặc `email, Họ tên`; chấp nhận dấu phẩy, chấm phẩy hoặc tab (dán trực tiếp từ Excel). Không có họ tên thì lấy phần trước `@`
- Tối đa **50** người mỗi lần
- Loại bỏ dòng trùng email trong danh sách (không phân biệt chữ hoa/thường) trước khi gửi
- Chỉ kiểm tra định dạng email, **không** tra tên miền: tra MX tuần tự cho 50 email có thể vượt thời gian chờ của proxy. Email sai tên miền sẽ hiện ở kết quả gửi
- Xử lý độc lập từng dòng: một dòng lỗi không làm hỏng các dòng còn lại
- Ghi dữ liệu tuần tự để hai dòng trùng email không cùng tạo được tài khoản; gửi email song song tối đa 10 luồng, mỗi email chờ tối đa 5 giây

**Acceptance Criteria:**

- [ ] Có nút "Mời nhiều" trên màn Nhân viên
- [ ] Trước khi gửi, giao diện hiển thị: số dòng hợp lệ, số dòng trùng bị loại, các dòng không đọc được email
- [ ] Sau khi gửi, hiển thị kết quả từng dòng: "Đã gửi email mời" / "Đã tạo, chưa gửi được email" / lỗi kèm lý do
- [ ] Danh sách 5 dòng gồm 3 hợp lệ, 1 trùng khác chữ hoa, 1 không phải email: tạo đúng 3 lời mời
- [ ] Danh sách chứa email đã tồn tại: dòng đó báo lỗi, các dòng còn lại vẫn được mời
- [ ] Danh sách 51 dòng: không cho gửi, hiển thị giới hạn 50

**Dependencies:** FR-001

---

#### FR-003: Theo dõi trạng thái lời mời

**Priority:** Must Have

**Description:**
Root xem trạng thái lời mời và lịch sử cấp tài khoản của từng nhân sự ngay trên danh sách Nhân viên.

**Business Rules:**

| Trạng thái | Điều kiện | Màu |
|---|---|---|
| Chờ nhận | Đã gửi, token còn hiệu lực | Vàng |
| Hết hạn | Quá TTL, hoặc token đã bị huỷ do đổi email (FR-006) | Xám |
| Đã nhận | Nhân sự đã tự đặt mật khẩu | Xanh lá |
| Đã thu hồi | Root đã thu hồi (FR-005) | Đỏ |
| Tạo thủ công | Tài khoản tạo theo luồng cũ | Mặc định |

- "Hết hạn" là trạng thái suy ra khi trả dữ liệu, không lưu trong cơ sở dữ liệu
- Tooltip trên trạng thái hiển thị: người gửi lời mời gần nhất, thời điểm gửi, hạn token (khi đang chờ), thời điểm nhận

**Acceptance Criteria:**

- [ ] Cột "Lời mời" hiển thị đủ năm trạng thái
- [ ] Tooltip hiển thị đúng người gửi, thời điểm gửi, thời điểm nhận
- [ ] Tài khoản tạo theo luồng cũ hiển thị "Tạo thủ công", không phát sinh lỗi

**Dependencies:** FR-001

---

#### FR-004: Gửi lại lời mời

**Priority:** Must Have

**Description:**
Root gửi lại email mời cho lời mời đang chờ, đã hết hạn hoặc đã thu hồi.

**Business Rules:**

- Cấp token mới với TTL 48 giờ; token cũ mất hiệu lực ngay lập tức
- Cập nhật người gửi và thời điểm gửi theo lần gửi này. Lịch sử từng lần gửi nằm trong audit log
- Không áp dụng cho tài khoản đã kích hoạt
- Điều kiện trạng thái được kiểm tra lại ngay trong câu lệnh cập nhật, tránh race condition với thao tác nhận lời mời

**Acceptance Criteria:**

- [ ] Nút "Gửi lại" hiển thị với lời mời Chờ nhận, Hết hạn, Đã thu hồi
- [ ] Sau khi gửi lại: đường dẫn cũ báo không hợp lệ, đường dẫn mới sử dụng được
- [ ] Sau khi gửi lại: tooltip hiển thị người gửi và thời điểm của lần gửi mới
- [ ] Gửi lại cho tài khoản đã kích hoạt qua API: bị từ chối

**Dependencies:** FR-001

---

#### FR-005: Thu hồi lời mời

**Priority:** Must Have

**Description:**
Root thu hồi lời mời chưa được nhận, ví dụ khi gửi nhầm người hoặc nhân sự không còn tham gia.

**Business Rules:**

- Chỉ thu hồi được lời mời ở trạng thái Chờ nhận hoặc Hết hạn
- Token bị huỷ; bản ghi tài khoản được giữ lại với trạng thái "Đã thu hồi" để phục vụ truy vết
- Mời lại cùng email: dùng chức năng Gửi lại (FR-004)
- Có hộp thoại xác nhận trước khi thu hồi

**Acceptance Criteria:**

- [ ] Sau khi thu hồi, đường dẫn đã gửi báo không hợp lệ
- [ ] Bản ghi vẫn còn trong danh sách với trạng thái "Đã thu hồi"
- [ ] Thu hồi tài khoản đã kích hoạt qua API: bị từ chối

**Dependencies:** FR-001

---

#### FR-006: Ràng buộc với tài khoản chưa nhận lời mời và tính duy nhất của email

**Priority:** Must Have

**Description:**
Ngăn các thao tác của luồng cũ làm sai lệch trạng thái tài khoản đang chờ, và bảo đảm email không trùng ở mọi luồng.

**Business Rules:**

- Tài khoản chưa nhận lời mời (Chờ nhận, Hết hạn, Đã thu hồi) **không** được bật/tắt trạng thái và **không** được đặt mật khẩu hộ
- Sửa email của lời mời đang chờ: token hiện tại bị huỷ, lời mời chuyển sang "Hết hạn"; Root gửi lại tới email mới. Lý do: sửa email thường xuất phát từ gõ nhầm — email mời đã tới người khác, không huỷ token thì người nhận nhầm có thể kích hoạt và chiếm tài khoản
- Tạo nhân sự (luồng cũ) và sửa nhân sự kiểm tra trùng email không phân biệt chữ hoa/thường, loại trừ chính tài khoản đang sửa (sửa lỗi điều kiện `"$nin"`, mục 2.1)

**Acceptance Criteria:**

- [ ] Với tài khoản chưa nhận lời mời: ô trạng thái bị vô hiệu hoá, nút đặt mật khẩu không hiển thị
- [ ] Gọi trực tiếp API bật/tắt hoặc đặt mật khẩu hộ cho tài khoản chưa nhận lời mời: bị từ chối
- [ ] Sửa email lời mời đang chờ: đường dẫn gửi tới email cũ báo không hợp lệ
- [ ] Sửa email nhân sự A thành email (khác chữ hoa) của nhân sự B: bị từ chối

**Dependencies:** FR-001, FR-004

---

#### FR-017: Không cấp phiên đăng nhập khi tạo nhân sự

**Priority:** Must Have

**Description:**
API tạo nhân sự (luồng cũ) không trả token phiên đăng nhập của tài khoản vừa tạo. Trùng nội dung với HF-3.

**Business Rules:**

- Phản hồi chỉ gồm định danh tài khoản
- Không tạo phiên trong Redis cho tài khoản vừa tạo

**Acceptance Criteria:**

- [ ] Phản hồi `POST /staffs/register` không chứa token hợp lệ
- [ ] Màn Nhân viên tạo tài khoản bình thường sau thay đổi

**Dependencies:** HF-3

---

### EPIC-002: Self-Service Authentication

---

#### FR-007: Nhận lời mời và kích hoạt tài khoản

**Priority:** Must Have

**Description:**
Nhân sự mở đường dẫn trong email mời, tự đặt mật khẩu và kích hoạt tài khoản.

**Business Rules:**

- Trang công khai `/accept-invite` trên Admin Portal, không yêu cầu đăng nhập
- Khi mở trang, hệ thống xác thực token. Hợp lệ: hiển thị họ tên, email và form đặt mật khẩu. Hết hạn: thông báo hết hạn và hướng dẫn nhờ quản trị viên gửi lại. Không hợp lệ (sai, đã dùng, đã thu hồi): thông báo không hợp lệ
- Mật khẩu theo NFR-003
- Kích hoạt thành công: chuyển về trang đăng nhập, điền sẵn email. **Không tự động đăng nhập** — mọi phiên đăng nhập đều đi qua endpoint đăng nhập, nơi có rate limiting
- Token dùng một lần; thao tác kích hoạt là một lệnh tìm-và-cập-nhật nguyên tử (atomic), hai yêu cầu đồng thời chỉ một yêu cầu thành công
- Trình duyệt đang lưu phiên của tài khoản khác không ảnh hưởng tới trang; trang không chuyển hướng người dùng sang màn đăng nhập khi gặp lỗi
- Kích hoạt xong thì xoá phiên cũ trên trình duyệt trước khi chuyển về trang đăng nhập — nếu không, trang đăng nhập tự vào lại tài khoản cũ thay vì cho người mới đăng nhập

**Acceptance Criteria:**

- [ ] Mở đường dẫn hợp lệ: hiển thị đúng họ tên và email được mời
- [ ] Đặt mật khẩu rồi đăng nhập bằng mật khẩu đó: thành công
- [ ] Mở lại đường dẫn đã sử dụng: thông báo không hợp lệ
- [ ] Đường dẫn quá 48 giờ: thông báo hết hạn
- [ ] Mở đường dẫn trên trình duyệt đang lưu phiên của tài khoản khác: trang hoạt động bình thường; kích hoạt xong, trang đăng nhập hiện form cho người mới, không vào tài khoản cũ

**Dependencies:** FR-001, NFR-001, NFR-003

---

#### FR-008: Quên mật khẩu

**Priority:** Must Have

**Description:**
Nhân sự yêu cầu email đặt lại mật khẩu mà không cần liên hệ Root.

**Business Rules:**

- Đường dẫn "Quên mật khẩu?" trên trang đăng nhập, mở trang công khai `/forgot-password`
- Hệ thống gửi email chứa đường dẫn đặt lại mật khẩu, TTL **60 phút**, dùng một lần
- Yêu cầu mới thay thế token cũ: chỉ email gần nhất còn hiệu lực
- Chỉ tài khoản đang hoạt động nhận được email. Tài khoản chờ nhận lời mời được xử lý bằng Gửi lại (FR-004)
- Phản hồi giống nhau dù email có tài khoản hay không (NFR-004)

**Acceptance Criteria:**

- [ ] Trang đăng nhập có đường dẫn "Quên mật khẩu?"
- [ ] Yêu cầu hai lần liên tiếp: đường dẫn trong email thứ nhất không còn hiệu lực

**Dependencies:** FR-012, FR-016, NFR-004

---

#### FR-012: Rate limiting endpoint quên mật khẩu

**Priority:** Must Have

**Description:**
Chống email flooding và account enumeration qua endpoint quên mật khẩu. Là điều kiện bắt buộc của FR-008.

**Business Rules:**

| Đối tượng đếm | Ngưỡng |
|---|---|
| Email | 3 yêu cầu / 30 phút |
| IP | 10 yêu cầu / 60 phút |

- Đếm **mọi** yêu cầu, kể cả email không tồn tại, và đếm trước khi tra cứu tài khoản. Nếu chỉ đếm email có tài khoản thì chính cơ chế rate limiting trở thành kênh account enumeration
- Fail-closed như FR-011

**Acceptance Criteria:**

- [ ] Yêu cầu lần thứ 4 trong 30 phút cho cùng email: HTTP 429
- [ ] Hành vi với email không tồn tại giống hệt email có tài khoản

**Dependencies:** FR-008

---

#### FR-009: Đặt lại mật khẩu

**Priority:** Must Have

**Description:**
Nhân sự đặt mật khẩu mới bằng đường dẫn trong email đặt lại mật khẩu.

**Business Rules:**

- Trang công khai `/reset-password`
- Mật khẩu theo NFR-003
- Thành công: vô hiệu hoá toàn bộ phiên đăng nhập của tài khoản (NFR-005) và xoá bộ đếm đăng nhập sai theo email (FR-011)
- Token hết hạn: thông báo hết hạn. Token sai hoặc đã dùng: thông báo không hợp lệ. Cả hai kèm đường dẫn gửi lại yêu cầu

**Acceptance Criteria:**

- [ ] Đặt lại thành công: phiên đang mở ở trình duyệt khác bị đăng xuất
- [ ] Tài khoản đang bị chặn do đăng nhập sai theo email: đặt lại xong đăng nhập được ngay (trừ khi IP đang bị chặn)
- [ ] Đường dẫn quá 60 phút: thông báo hết hạn; đường dẫn đã dùng: thông báo không hợp lệ

**Dependencies:** FR-008, NFR-005

---

#### FR-010: Tự đổi mật khẩu

**Priority:** Must Have

**Description:**
Nhân sự đang đăng nhập tự đổi mật khẩu của mình.

**Business Rules:**

- Mục "Đổi mật khẩu" trong menu tài khoản
- **Bắt buộc mật khẩu hiện tại** (khắc phục lỗi #1, mục 2.3)
- Mật khẩu mới theo NFR-003 và phải khác mật khẩu hiện tại
- Nhập sai mật khẩu hiện tại được tính vào bộ đếm đăng nhập sai theo email (FR-011)
- Khi bộ đếm chạm ngưỡng: vô hiệu hoá **mọi** phiên của tài khoản, kể cả phiên đang thao tác. Nếu không, người chiếm được phiên vẫn ngồi trong hệ thống trong khi chủ tài khoản bị chặn ở cửa đăng nhập
- Thành công: vô hiệu hoá toàn bộ phiên, kể cả phiên hiện tại; chuyển về trang đăng nhập

**Acceptance Criteria:**

- [ ] Gọi API không kèm mật khẩu hiện tại: bị từ chối
- [ ] Nhập sai mật khẩu hiện tại 5 lần trong 15 phút: HTTP 429 và mọi phiên của tài khoản bị đăng xuất
- [ ] Đổi thành công: mọi phiên, kể cả phiên hiện tại, bị đăng xuất

**Dependencies:** FR-011, NFR-003, NFR-005

---

#### FR-018: Đăng nhập không phân biệt chữ hoa/thường và chống account enumeration

**Priority:** Must Have

**Description:**
Email lời mời được lưu dạng chữ thường; bàn phím điện thoại thường tự viết hoa chữ đầu. Đăng nhập phải khớp email không phân biệt chữ hoa/thường, và không để lộ email nào có tài khoản qua thời gian phản hồi.

**Business Rules:**

- Tìm tài khoản theo email không phân biệt chữ hoa/thường
- Dữ liệu cũ chưa có ràng buộc duy nhất: nếu có hơn một tài khoản chỉ khác chữ hoa/thường, quay về so khớp chính xác như trước
- Email không tồn tại: vẫn thực hiện một phép so sánh bcrypt với hash giả, để thời gian phản hồi tương đương email tồn tại

**Acceptance Criteria:**

- [ ] Đăng nhập bằng `An@Example.com` với tài khoản `an@example.com`: thành công
- [ ] Email không tồn tại và email tồn tại sai mật khẩu: chênh lệch trung vị thời gian phản hồi < 50 ms qua 20 lần đo

**Dependencies:** —

---

### EPIC-003: Login Security (gap #12)

---

#### FR-011: Rate limiting endpoint đăng nhập

**Priority:** Must Have

**Description:**
Chặn brute-force attack vào endpoint đăng nhập Admin Portal.

**Business Rules:**

| Đối tượng đếm | Ngưỡng | Vai trò |
|---|---|---|
| Email | 5 lần **thất bại** / 15 phút | Lớp kiểm soát chính |
| IP | 20 lần thất bại / 15 phút | Lớp bổ sung, chỉ hiệu quả khi cấu hình đúng nguồn IP (D-4) |

- Chỉ đếm lần thất bại. Đăng nhập thành công xoá bộ đếm theo email
- Đếm theo fixed window: khung 15 phút bắt đầu từ lần thất bại đầu tiên
- Vượt ngưỡng: từ chối ngay, không kiểm tra mật khẩu, trả HTTP 429 kèm số giây phải chờ (`retryAfterSeconds`)
- **Fail-closed:** không đọc được bộ đếm (Redis lỗi) thì trả HTTP 503 (RQ-5). Mọi request đã đăng nhập vốn tra phiên trong Redis; Redis lỗi thì Portal đã không dùng được, cho qua chỉ để lại khe thử mật khẩu không giới hạn
- Không giảm ngưỡng theo email vì dựa vào lớp IP: IP hiện có thể giả mạo (mục 2.1)

**Acceptance Criteria:**

- [ ] 5 lần sai cùng email: lần thứ 6 bị từ chối kèm thời gian chờ, kể cả khi mật khẩu đúng
- [ ] 4 lần sai rồi 1 lần đúng: bộ đếm theo email về 0

**Dependencies:** Redis, D-4

---

### EPIC-004: Audit & Email Communication

---

#### FR-014: Audit log cho thao tác tài khoản

**Priority:** Must Have

**Description:**
Mọi thao tác trong PRD này được ghi vào audit log của nhân sự (nút ⓘ trên màn Nhân viên).

**Business Rules:**

| Sự kiện | Người thực hiện |
|---|---|
| Gửi lời mời / mời hàng loạt | Root |
| Gửi lại lời mời | Root |
| Thu hồi lời mời | Root |
| Nhận lời mời, tự đặt mật khẩu | Chính nhân sự |
| Đặt lại mật khẩu qua email | Chính nhân sự |
| Tự đổi mật khẩu | Chính nhân sự |

- Dữ liệu audit không chứa hash mật khẩu hoặc hash token (HF-1)
- Khi PQ-009 phát hành, các sự kiện chuyển sang danh mục hành động và trường ADV của PQ-009

**Acceptance Criteria:**

- [ ] Mỗi sự kiện trong bảng tạo một bản ghi audit có tên người thực hiện
- [ ] Nội dung audit không chứa trường mật khẩu hoặc token

**Dependencies:** HF-1; PQ-009 (chuyển đổi cấu trúc)

---

#### FR-015: Email mời

**Priority:** Must Have

**Description:**
Email mời gửi qua API email AccessTrade, template do AT đăng ký.

**Business Rules:**

- Mã template: `AMBASSADOR_EMAIL_STAFF_INVITE` (tạm đặt, chờ AT cấp). Đề nghị AT nhân bản `TECHCOMBANK_EMAIL_STAFF_INVITE` — cùng bộ biến (Phụ lục B)
- Tiêu đề: `[AccessTrade] Bạn được mời tham gia trang quản trị Ambassador`. Người gửi: địa chỉ gửi mặc định của API email AT. Ngôn ngữ: tiếng Việt
- Nội dung: tên người được mời, câu mời ghi cố định "Admin Ambassador" (không hiện tên tài khoản gửi — tài khoản Root trong DB tên là "Root"), nút kích hoạt, đường dẫn dạng văn bản (khi nút không hoạt động), thời hạn hiệu lực, lưu ý bỏ qua nếu không chờ lời mời

**Acceptance Criteria:**

- [ ] Email hiển thị đúng trên Gmail, Outlook (web và di động)
- [ ] Mọi biến trong template khớp dữ liệu hệ thống gửi (có test tự động đối chiếu)

**Dependencies:** D-1

---

#### FR-016: Email đặt lại mật khẩu

**Priority:** Must Have

**Description:**
Email đặt lại mật khẩu gửi qua API email AccessTrade.

**Business Rules:**

- Mã template: `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD` (tạm đặt, chờ AT cấp). Đề nghị AT nhân bản `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD`
- Tiêu đề: `[AccessTrade] Yêu cầu đặt lại mật khẩu trang quản trị Ambassador`. Ngôn ngữ: tiếng Việt
- Nội dung: tên nhân sự, nút đặt lại, đường dẫn dạng văn bản, thời hạn 60 phút, lưu ý mật khẩu hiện tại giữ nguyên nếu không phải người yêu cầu

**Acceptance Criteria:**

- [ ] Email hiển thị đúng trên Gmail, Outlook (web và di động)
- [ ] Mọi biến trong template khớp dữ liệu hệ thống gửi (có test tự động đối chiếu)

**Dependencies:** D-1

---

## 7. Non-Functional Requirements

---

#### NFR-001: Bảo mật token

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Token sinh từ nguồn ngẫu nhiên mật mã (`crypto/rand`), 32 byte, mã hoá base64url
- [ ] Cơ sở dữ liệu chỉ lưu hash SHA-256 của token; token gốc chỉ có trong email
- [ ] Token dùng một lần, bị xoá sau khi sử dụng
- [ ] Token không xuất hiện trong: phản hồi API cho Root, audit log, log ứng dụng staging và production
- [ ] Môi trường develop được ghi đường dẫn ra log **chỉ khi** gửi email thất bại, phục vụ kiểm thử khi template chưa được cấp

**Rationale:** SHA-256 đủ an toàn vì token có entropy 256 bit; cần hash tất định để tra cứu. Token lộ qua log có giá trị tương đương mật khẩu.

---

#### NFR-002: Thời hạn token

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Token mời: TTL 48 giờ
- [ ] Token đặt lại mật khẩu: TTL 60 phút
- [ ] Điều kiện TTL nằm trong chính câu lệnh cập nhật; phân biệt "hết hạn" với "không hợp lệ" bằng một truy vấn phụ chỉ khi cập nhật thất bại

**Rationale:** Giới hạn khoảng thời gian khai thác nếu hộp thư bị xâm nhập. Chỉ người giữ đúng token mới thấy thông báo "hết hạn", nên phân biệt không làm lộ thông tin cho người đoán mò.

---

#### NFR-003: Chính sách mật khẩu

**Priority:** Must Have

**Description:**
Áp dụng cho nhận lời mời, đặt lại mật khẩu và tự đổi mật khẩu. Riêng giới hạn 72 byte áp dụng cho **mọi** luồng, kể cả luồng cũ và creator (HF-2).

**Acceptance Criteria:**

- [ ] Tối thiểu 8 **ký tự** (đếm theo ký tự Unicode, không theo byte)
- [ ] Tối đa 72 **byte** ở mọi luồng đặt mật khẩu. Quá giới hạn thì từ chối với thông báo riêng nêu rõ đơn vị byte (Phụ lục C)
- [ ] Có ít nhất một chữ cái (kể cả chữ có dấu) và một chữ số
- [ ] Frontend và backend đếm cùng đơn vị: ký tự cho giới hạn dưới, byte UTF-8 cho giới hạn trên
- [ ] Luồng cũ (tạo, đặt hộ) giữ tối thiểu 6 ký tự cho tới khi tắt (RQ-11)

**Rationale:** bcrypt không nhận quá 72 byte; bản thư viện đang dùng trả lỗi và hàm băm hiện tại bỏ qua lỗi, lưu hash rỗng (mục 2.1). Chữ có dấu tiếng Việt chiếm 2–3 byte, nên giới hạn phải nói bằng byte.

---

#### NFR-004: Account Enumeration Prevention

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] `POST /staffs/forgot-password` trả cùng nội dung và mã phản hồi dù email có tồn tại hay không
- [ ] Sinh token, ghi cơ sở dữ liệu và gửi email của quên mật khẩu chạy bất đồng bộ
- [ ] Rate limiting đếm trước khi tra cứu tài khoản (FR-012)
- [ ] Đăng nhập với email không tồn tại vẫn thực hiện so sánh bcrypt (FR-018)

**Rationale:** Ngăn kẻ tấn công lập danh sách email nhân sự hợp lệ.

---

#### NFR-005: Session Invalidation

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Đặt lại mật khẩu (FR-009): xoá toàn bộ phiên trong Redis
- [ ] Tự đổi mật khẩu (FR-010): xoá toàn bộ phiên, kể cả phiên hiện tại
- [ ] Nhập sai mật khẩu hiện tại chạm ngưỡng (FR-010): xoá toàn bộ phiên

**Rationale:** Tài khoản bị xâm phạm được bảo vệ ngay khi mật khẩu thay đổi hoặc có dấu hiệu dò mật khẩu.

---

#### NFR-006: Kiểm soát truy cập phía server

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Mọi ràng buộc trong mục 6 được kiểm tra ở backend; ẩn/hiện trên giao diện chỉ phục vụ trải nghiệm
- [ ] Nghiệm thu bằng gọi API trực tiếp, không chỉ thao tác trên giao diện
- [ ] 5 endpoint không yêu cầu vai trò (Phụ lục A) được khai báo là ngoại lệ có chủ đích trong bảng endpoint–vai trò của PQ-010

---

#### NFR-007: Không có silent failure trong gửi email

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] API mời và gửi lại trả về trạng thái gửi email thực tế (`emailSent`)
- [ ] Giao diện không hiển thị "đã gửi" khi email chưa được AT chấp nhận
- [ ] Phản hồi của AT được kiểm tra theo trường `status` trong body, không chỉ theo HTTP status

**Rationale:** Riêng quên mật khẩu gửi bất đồng bộ theo NFR-004, nên lỗi gửi không hiện cho người dùng; bù lại bằng giám sát (NFR-013).

---

#### NFR-008: Backward Compatibility

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Các trường mới trên bản ghi nhân sự đều tuỳ chọn; không cần migration schema
- [ ] Dữ liệu audit cũ chứa hash mật khẩu được dọn bằng script của HF-1 (chạy một lần, có backup)
- [ ] Tài khoản hiện có đăng nhập bình thường, không bị yêu cầu đặt lại mật khẩu
- [ ] Luồng tạo kèm mật khẩu và đặt mật khẩu hộ hoạt động như trước (cho tới khi tắt — RQ-11), trừ giới hạn 72 byte

---

#### NFR-009: Cấu hình và kill switch

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Biến môi trường `ADMIN_WEB_HOST` là tuỳ chọn: thiếu biến, service vẫn khởi động bình thường
- [ ] Thiếu `ADMIN_WEB_HOST`: các chức năng gửi email (mời, mời hàng loạt, gửi lại, quên mật khẩu) trả lỗi cấu hình; với quên mật khẩu, lỗi trả về như nhau cho mọi email
- [ ] Bỏ `ADMIN_WEB_HOST` trên môi trường đang chạy là **kill switch** tắt toàn bộ luồng gửi email, không cần phát hành lại

---

#### NFR-010: Hiệu năng

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Mời một nhân sự: phản hồi < 5 giây khi API email AT phản hồi bình thường
- [ ] Mời hàng loạt 50 nhân sự: ≤ 30 giây kể cả khi API email AT không phản hồi (10 luồng × timeout 5 giây)
- [ ] Mỗi lời gọi API email có timeout: 15 giây (mời lẻ), 5 giây (mời hàng loạt)

---

#### NFR-011: Ngôn ngữ

**Priority:** Must Have

| Tầng | Yêu cầu |
|---|---|
| Backend | Bắt buộc cả `en` và `vi` trong `internal/locale/properties/`. Thiếu file `en/` thì service không khởi động được (`properties.MustLoadFile` gọi `log.Fatal`) |
| Admin Portal | Chỉ tiếng Việt |
| Email | Tiếng Việt |

---

#### NFR-012: Kiểm thử tự động

**Priority:** Must Have

**Acceptance Criteria:**

- [ ] Unit test cho rate limiting: chạm ngưỡng, hết khung thời gian, xoá bộ đếm, fail-closed
- [ ] Unit test cho chính sách mật khẩu: ký tự nhiều byte, giới hạn 72 byte ở luồng mới, luồng cũ và creator
- [ ] Unit test cho sinh và hash token
- [ ] Test đối chiếu biến template email với dữ liệu hệ thống gửi

---

#### NFR-013: Giám sát

**Priority:** Should Have

**Acceptance Criteria:**

- [ ] Ghi log có cấu trúc cho: gửi email thất bại (theo loại email), yêu cầu bị HTTP 429, yêu cầu bị HTTP 503 do không đọc được bộ đếm
- [ ] Cảnh báo khi tỷ lệ gửi email thất bại > 20% trong 1 giờ, hoặc số HTTP 429 của một email > 3 khung liên tiếp (dấu hiệu tấn công có chủ đích)

**Rationale:** Quên mật khẩu gửi bất đồng bộ nên lỗi gửi không hiện ra giao diện; lần bị chặn không ghi vào Lịch sử đăng nhập (FR-013). Giám sát là nơi duy nhất nhìn thấy hai loại sự kiện này.

---

## 8. Key User Flows

### Flow 1: Onboarding nhân sự mới

```
Biz gửi thông tin người cần cấp tài khoản cho AT
Root (AT) mở màn Nhân viên
  → Nhấn "Mời qua email"
  → Nhập Họ tên + Email + Vai trò + ADV → Gửi lời mời
  → Hệ thống tạo tài khoản chờ, gửi email mời
  → Danh sách hiển thị trạng thái "Chờ nhận"

Nhân sự nhận email
  → Nhấn "Chấp nhận lời mời"
  → Trang /accept-invite: đặt mật khẩu
  → Tài khoản kích hoạt → chuyển về /login, email điền sẵn
  → Đăng nhập
  → Danh sách của Root hiển thị trạng thái "Đã nhận"
```

### Flow 2: Tiếp nhận ADV mới — mời hàng loạt

```
Biz gửi danh sách nhân sự của ADV mới cho AT
Root (AT) mở màn Nhân viên
  → Nhấn "Mời nhiều"
  → Chọn Vai trò + ADV
  → Dán danh sách từ Excel → hệ thống hiển thị số dòng hợp lệ, dòng trùng, dòng lỗi
  → Gửi lời mời
  → Bảng kết quả từng dòng: đã gửi / đã tạo nhưng chưa gửi được email / lỗi kèm lý do
  → Dòng chưa gửi được email: Root nhấn "Gửi lại" trên danh sách
```

### Flow 3: Quên mật khẩu

```
Nhân sự vào /login
  → Nhấn "Quên mật khẩu?"
  → Nhập email → Gửi
  → Thông báo chung: "Nếu email thuộc một tài khoản đang hoạt động, bạn sẽ nhận được email hướng dẫn"
  → Nhận email (hiệu lực 60 phút) → mở /reset-password
  → Đặt mật khẩu mới → mọi phiên cũ bị đăng xuất
  → Đăng nhập bằng mật khẩu mới
```

### Flow 4: Tự đổi mật khẩu

```
Nhân sự đang đăng nhập
  → Menu tài khoản → "Đổi mật khẩu"
  → Nhập mật khẩu hiện tại + mật khẩu mới + xác nhận
  → Thành công → mọi phiên bị đăng xuất → về /login
```

### Flow 5: Xử lý lời mời gửi nhầm

```
Root phát hiện gõ sai email
  → Cách 1: Thu hồi lời mời → đường dẫn đã gửi mất hiệu lực
  → Cách 2: Sửa email → token cũ tự huỷ, trạng thái "Hết hạn" → Gửi lại tới email mới
```

### Flow 6: Brute-force attack

```
Kẻ tấn công thử mật khẩu cho email admin
  → Lần 1–5 sai: từ chối
  → Lần 6 trở đi trong khung 15 phút: HTTP 429, không kiểm tra mật khẩu
  → Kẻ tấn công lặp lại mỗi 15 phút: tài khoản bị chặn liên tục; giám sát cảnh báo (NFR-013)
  → Admin thật: dùng "Quên mật khẩu" để đặt lại và gỡ chặn ngay
```

---

## 9. Epics & Traceability Matrix

### EPIC-001: Invite Management

**Mô tả:** Root cấp tài khoản bằng lời mời, theo dõi trạng thái, gửi lại, thu hồi; bảo đảm tính duy nhất của email.
**Functional Requirements:** FR-001 → FR-006, FR-017
**Story Count Estimate:** 7–9 stories
**Priority:** Must Have (FR-002: Should Have)
**Business Value:** BO-1, BO-3, BO-5

---

### EPIC-002: Self-Service Authentication

**Mô tả:** Nhân sự tự kích hoạt tài khoản, tự khôi phục và tự đổi mật khẩu; đăng nhập không phân biệt chữ hoa/thường.
**Functional Requirements:** FR-007, FR-008, FR-009, FR-010, FR-012, FR-018
**Story Count Estimate:** 6–7 stories
**Priority:** Must Have
**Business Value:** BO-1, BO-2

---

### EPIC-003: Login Security (gap #12)

**Mô tả:** Rate limiting cho endpoint đăng nhập. Ghi nhận đăng nhập thất bại (FR-013) nằm ngoài phạm vi (mục 5, Phụ lục E).
**Functional Requirements:** FR-011
**Story Count Estimate:** 1–2 stories
**Priority:** Must Have
**Business Value:** BO-4

---

### EPIC-004: Audit & Email Communication

**Mô tả:** Audit log cho thao tác tài khoản; hai template email trên hệ thống AccessTrade.
**Functional Requirements:** FR-014, FR-015, FR-016
**Story Count Estimate:** 2–3 stories
**Priority:** Must Have
**Business Value:** BO-1, BO-5

---

### Traceability Matrix

| Epic | Tên Epic | Functional Requirements | Non-Functional Requirements | Business Objectives | Story Estimate | Priority |
|---|---|---|---|---|---|---|
| EPIC-001 | Invite Management | FR-001, 002, 003, 004, 005, 006, 017 | NFR-001, 002, 006, 007, 009, 010 | BO-1, BO-3, BO-5 | 7–9 | Must Have |
| EPIC-002 | Self-Service Authentication | FR-007, 008, 009, 010, 012, 018 | NFR-001, 002, 003, 004, 005, 006 | BO-1, BO-2 | 6–7 | Must Have |
| EPIC-003 | Login Security | FR-011 | NFR-006, 013 | BO-4 | 1–2 | Must Have |
| EPIC-004 | Audit & Email Communication | FR-014, 015, 016 | NFR-001, 007, 011 | BO-1, BO-5 | 2–3 | Must Have |

**Tổng stories ước tính:** 16–21 stories

---

## 10. Kế hoạch phát hành & Rollback

### Thứ tự phát hành

| Bước | Nội dung | Điều kiện |
|---|---|---|
| 0 | HF-1 → HF-3 lên `release` (PR riêng nếu cần phát hành trước tính năng); chạy script dọn audit (có backup) | Độc lập với tính năng |
| 1 | Gửi yêu cầu D-1 cho AT (nhân bản template TCB); DevOps khai `ADMIN_WEB_HOST` (D-3) | Ngay khi PRD được duyệt — critical path |
| 2 | Phát hành backend | Có mã template thật từ AT |
| 3 | Phát hành Admin Portal | Sau bước 2 (frontend gọi endpoint mới) |
| 4 | Tắt luồng cũ (RQ-11) | Email mời và quên mật khẩu đã chạy thật trên production |

**Nhánh:** code cắt từ `release` mới nhất; phát hành lên `release` khi cần, sau đó đồng bộ sang `develop` (RQ-8).

### Rollback

- **Kill switch:** bỏ `ADMIN_WEB_HOST` → tắt mời, gửi lại, quên mật khẩu, không cần phát hành lại (NFR-009)
- **Backend:** endpoint mới là bổ sung; phiên bản cũ bỏ qua các trường mới. Rollback bằng phát hành lại bản trước
- **Dữ liệu:** tài khoản chờ tạo bởi lời mời vẫn ở trạng thái chưa kích hoạt khi rollback — không đăng nhập được, không ảnh hưởng tài khoản khác
- **Frontend:** rollback độc lập; nút mới biến mất, luồng cũ vẫn chạy

---

## 11. Dependencies

### Internal

- Redis — bộ đếm rate limiting và phiên đăng nhập (đã có)
- MongoDB — collection `staffs`, `audits`, Lịch sử đăng nhập
- Audit service — `internalservice.Audit()` (đã có)
- PRD Phân quyền vận hành — PQ-001, PQ-002, PQ-009, PQ-010 (mục 2.4)
- Tính năng Lịch sử đăng nhập — có trên `develop` từ 2026-09-15, chưa phát hành lên `release`. Là nền của FR-013 (RQ-9)

### External

| # | Phụ thuộc | Bên thực hiện | Mức độ |
|---|---|---|---|
| D-1 | Cấp mã 2 template email. Đề nghị nhân bản `TECHCOMBANK_EMAIL_STAFF_INVITE`, `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD` (cùng bộ biến), đổi thương hiệu theo mẫu trong `email-templates/` | Team Email AccessTrade | **Critical path** — thiếu thì không gửi được email nào. Nội dung yêu cầu: Phụ lục D |
| D-2 | Không ghi nội dung đường dẫn trong email vào log hoặc lịch sử gửi mà bên thứ ba truy cập được | Team Email AccessTrade | Bắt buộc (NFR-001) |
| D-3 | Khai báo `ADMIN_WEB_HOST` cho develop, staging, production; bảo đảm service **admin** có đủ `ACCESS_TRADE_SMS_*` như service public (tới nay admin chưa gửi email thành công lần nào) | DevOps | Bắt buộc |
| D-4 | Cấu hình `IPExtractor` theo nguồn IP thật. Môi trường develop đứng sau Cloudflare (header `cf-ray`), IP thật ở `CF-Connecting-IP`; production cần xác nhận chuỗi proxy | DevOps | Khuyến nghị — ảnh hưởng lớp IP của FR-011, FR-012; thay đổi cũng tác động tới IP trong Lịch sử đăng nhập và CORS middleware |
| D-5 | SPF/DKIM cho tên miền gửi email | Team Email AccessTrade | Khuyến nghị — giảm tỷ lệ email vào spam |
| D-6 | Chạy script dọn audit của HF-1 trên production | DevOps / DBA | Bắt buộc cho HF-1 |

---

## 12. Assumptions

1. Nhân sự được mời có địa chỉ email hợp lệ và truy cập được
2. API email của AccessTrade phản hồi trong vòng 5 giây trong điều kiện bình thường
3. Admin Portal tiếp tục dùng umi 3 và cơ chế lưu token trong `localStorage`
4. Tài khoản Root tiếp tục được tạo theo luồng cũ; lời mời không tạo tài khoản Root
5. Quy mô nhân sự Admin Portal ở mức hàng trăm tài khoản; truy vấn email không phân biệt chữ hoa/thường không cần index riêng
6. Nhân sự hiện có không cần chuyển sang luồng mới; chỉ tài khoản tạo sau ngày phát hành đi qua lời mời
7. Template TCB trên hệ thống AT đang hoạt động và có thể nhân bản (cần AT xác nhận — D-1)
8. API email của AT chịu được 10 yêu cầu song song, tối đa 50 email mỗi lượt mời hàng loạt (cần AT xác nhận — D-1)

---

## 13. Open Questions & Resolved Questions

### 13.1 Open Questions

Không còn câu hỏi mở.

### 13.2 Resolved Questions

| # | Câu hỏi | Quyết định | Căn cứ |
|---|---|---|---|
| RQ-1 (OQ-1 cũ) | Hiển thị đường dẫn mời cho Root khi email lỗi? | Không. Root dùng "Gửi lại" | Mô tả hạng mục: "hệ thống tự gửi đường dẫn qua email… thay vì nhắn tay qua email hay Zalo" |
| RQ-2 (OQ-5 cũ) | Ghép gap #12 vào đợt này? | Có — EPIC-003 | Quyết định 2026-09-29; không xét theo giờ công hay deadline |
| RQ-3 (OQ-3 cũ) | Vai trò nào được mời? | Chỉ Root | PQ-011; kế hoạch tháng 10 ("chỉ còn một tài khoản quyền cao nhất, do AT giữ"). Muốn mở cho Admin thì sửa PQ-011 trước |
| RQ-4 (OQ-4 cũ) | ADV có bắt buộc khi mời? | Tuỳ chọn tới khi PQ-001 phát hành; bắt buộc với mọi vai trò không phải Root từ thời điểm đó | Hệ quả trực tiếp của PQ-001 (fail-closed). Hôm nay giữ đúng hành vi của luồng tạo cũ |
| RQ-5 | Rate limiting khi Redis lỗi: fail-open hay fail-closed? | Fail-closed (HTTP 503) | Mọi request đã đăng nhập tra phiên trong Redis (`routeauth.Auth`); fail-open không giữ được Portal hoạt động, chỉ mở khe brute-force |
| RQ-6 (OQ-6 cũ) | TTL và ngưỡng rate limiting | TTL 48 giờ / 60 phút; đăng nhập 5 lần sai / 15 phút (email), 20 / 15 phút (IP); quên mật khẩu 3 / 30 phút (email), 10 / 60 phút (IP) | Theo thực hành phổ biến; Security có thể điều chỉnh khi duyệt |
| RQ-7 | Bỏ token trong API tạo nhân sự? | Có — FR-017, HF-3 | Admin FE không đọc trường này; token là phiên hợp lệ 8 giờ của người khác |
| RQ-8 (OQ-7 cũ) | Lộ trình phát hành | Code cắt từ `release` mới nhất, một nhánh duy nhất; phát hành lên `release` khi cần, rồi đồng bộ sang `develop` | Quyết định 2026-09-29 |
| RQ-9 | FR-013 trên nền `release`? | Hoãn — tính năng Lịch sử đăng nhập chưa có trên `release`. Phần mã đã viết được lưu lại để áp khi tính năng đó lên `release` | Hệ quả của RQ-8 |
| RQ-10 (OQ-9 cũ) | Thêm ràng buộc email duy nhất ở cơ sở dữ liệu? | Không | Chỉ một tài khoản Root tạo nhân sự nên gần như không có trường hợp tạo trùng cùng lúc; code đã kiểm tra trùng không phân biệt chữ hoa/thường |
| RQ-11 (OQ-2 cũ) | Khi nào tắt luồng cũ? | Giai đoạn 1 giữ nguyên luồng cũ. Khi email mời và quên mật khẩu đã chạy thật trên production: tắt "đặt mật khẩu hộ"; giữ "tạo kèm mật khẩu" chỉ để tạo tài khoản Root; nhân sự không phải Root bắt buộc đi qua lời mời. Tài khoản đang có không bị ảnh hưởng | Luồng cũ là đường dự phòng khi email chưa gửi được. Giữ mãi thì Root vẫn có thể nắm mật khẩu người khác, trái mục tiêu BO-1. Lời mời không tạo được tài khoản Root nên phải giữ một đường tạo Root |

---

## 14. Risks & Mitigation

| # | Rủi ro | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|---|
| R-1 | AT cấp mã template chậm | Trung bình — có tiền lệ template đối soát chờ từ 2026-08-12; nhưng có thể nhân bản template TCB | Tính năng phát hành nhưng không gửi được email | Gửi D-1 ngay khi duyệt PRD; NFR-007 bảo đảm giao diện phản ánh đúng; kill switch (NFR-009) |
| R-2 | Kẻ tấn công biết email admin, cố ý nhập sai để chặn tài khoản (account lockout) | Trung bình | Chỉ cần 5 yêu cầu mỗi 15 phút là giữ tài khoản bị chặn liên tục | Admin gỡ chặn bằng đặt lại mật khẩu (FR-009); cảnh báo khi một email bị 429 nhiều khung liên tiếp (NFR-013) |
| R-3 | Email mời tới nhầm người | Thấp | Người nhận nhầm kích hoạt và chiếm tài khoản | TTL 48 giờ; thu hồi (FR-005); sửa email tự huỷ token (FR-006) |
| R-4 | Chưa cấu hình nguồn IP thật | Cao | Lớp IP của rate limiting không có hiệu lực | Lớp email là lớp kiểm soát chính, không phụ thuộc IP |
| R-5 | Email vào thư mục spam | Trung bình | Nhân sự không nhận được lời mời | Gửi lại (FR-004); SPF/DKIM (D-5) |
| R-6 | Luồng cũ tồn tại song song | Chắc chắn cho tới khi tắt (RQ-11) | BO-1 chưa đạt 100% | KPI chia hai giai đoạn (BO-1); RQ-11 |
| R-7 | Hash mật khẩu đã lộ qua audit trước khi có HF-1 | Đã xảy ra (chưa rõ có bị khai thác) | Mật khẩu yếu (luồng cũ cho phép 6 ký tự) có thể bị bẻ offline | Phát hành HF-1 ngay; đề nghị Root và nhân sự quyền cao đổi mật khẩu sau khi FR-010 phát hành |
| R-8 | Redis gián đoạn | Thấp | Đăng nhập trả 503 (fail-closed) | Chấp nhận — Portal vốn không dùng được khi Redis gián đoạn; giám sát (NFR-013) |

---

## 15. Prioritization Summary

| Loại | Must Have | Should Have | Could Have | Tổng |
|---|---|---|---|---|
| Functional Requirements | 16 (FR-001, 003–012, 014–018) | 1 (FR-002) | 0 | 17 (FR-013 ngoài phạm vi — Phụ lục E) |
| Non-Functional Requirements | 11 (NFR-001–009, 011, 012) | 2 (NFR-010, 013) | 0 | 13 |

---

## 16. Stakeholders

| Vai trò | Tên/Nhóm | Trách nhiệm |
|---|---|---|
| Product Owner | — | Phê duyệt PRD |
| Root / AT | AT | Người dùng chính của EPIC-001 — thực hiện mời theo danh sách biz gửi |
| Biz vận hành | Manager biz | Gửi danh sách cần cấp tài khoản; nghiệm thu trải nghiệm nhận lời mời và quên mật khẩu |
| Security | — | Duyệt RQ-1, RQ-5, RQ-6, NFR-001, NFR-004; duyệt hotfix HF-1 → HF-3 |
| Development Team | AT-Core | Phát triển theo tech spec |
| QA | — | Viết và chạy test case theo Acceptance Criteria |
| DevOps / DBA | — | D-3, D-4, D-6 |
| Team Email AccessTrade | — | D-1, D-2, D-5 |

---

## 17. Trạng thái triển khai

Bản cài đặt tham chiếu được xây song song với PRD để kiểm chứng tính khả thi. **Đã merge 2026-09-29: PR #253 vào `release`, PR #252 vào `develop`.** Chưa deploy — chờ D-1 (mã template AT) và D-3.

Một nhánh duy nhất: `feat/staff-invite-password`, cắt từ `release` mới nhất (`ccda54288`). Gồm FR-001 → FR-018 (trừ FR-013) và HF-1 → HF-3, chia 3 commit để review riêng:

| Commit | Nội dung |
|---|---|
| `267b9be96` | HF-1 → HF-3 và script dọn audit — tự build và test được một mình |
| `991fa039d` | Backend của tính năng |
| `2baf13649` | Admin Portal |

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| FR-001 → FR-012, FR-015 → FR-018 | ✅ Đã phát triển | Chờ kiểm thử end-to-end với cơ sở dữ liệu và email thật |
| FR-013 | Ngoài phạm vi | Mã đã viết trên nền `develop`, lưu dạng patch; áp lại khi Lịch sử đăng nhập có trên `release` |
| FR-014 | ⚠️ Một phần | Audit ghi bằng câu mô tả; chưa theo danh mục hành động của PQ-009 |
| NFR-013 | ⚠️ Một phần | Đã có log cho gửi email thất bại, yêu cầu bị chặn (429, kèm đối tượng đếm) và lỗi bộ đếm (503). Cảnh báo cần cấu hình trên hệ thống giám sát |
| NFR-012 | ✅ | 18 unit test mới. Toàn bộ test `internal/...`, `pkg/admin/...`, `pkg/public/...` đạt, trừ 2 test đỏ sẵn trên `release` (`TestBuildDuplicateCheckFilter_*`), không liên quan |
| HF-1 → HF-3 | ✅ Đã phát triển | Script dọn audit mới kiểm logic biến đổi, chưa chạy trên cơ sở dữ liệu thật |

**Đã kiểm chứng:** build backend, unit test, biên dịch Admin Portal, typecheck, kiểm tra giao diện trên trình duyệt với dữ liệu giả lập (trang đăng nhập, màn Nhân viên, mời hàng loạt, đổi mật khẩu, ba trang công khai).

**Chưa kiểm chứng:** end-to-end với cơ sở dữ liệu thật; gửi email thật (D-1).

**Đồng bộ sang `develop`:** `develop` đi trước `release` 189 commit. Nhánh `feat/staff-invite-password-develop` (cắt từ `develop` `254dc9c30`, merge nhánh nguồn) đã merge vào `develop` qua PR #252. Chi tiết: tech spec mục 12.

- Xung đột đúng 2 chỗ như dự kiến: hàm `Login` (giữ ghi Lịch sử đăng nhập của `develop`, thêm chặn dò mật khẩu và tra email không phân biệt hoa thường) và phần import của form đăng nhập
- Một lỗi ngữ nghĩa git không báo: `develop` đã bỏ prop `location` khỏi form đăng nhập, nên dòng tự điền email từ trang nhận lời mời sẽ âm thầm không chạy. Đã sửa ngay trên nhánh nguồn — đọc tham số qua `useLocation()` — để hai nhánh dùng chung một dòng
- Vai trò `config_editor` mới của `develop` mời được luôn: luồng mời chọn vai trò theo bản ghi Role như API tạo nhân sự sẵn có
- Kết quả trên nền `develop`: backend build, toàn bộ unit test đạt (trừ 2 test đỏ sẵn), typecheck Admin Portal không phát sinh lỗi mới

---

## Phụ lục A: API

| Method | Endpoint | Mô tả | Quyền | PQ-010 |
|---|---|---|---|---|
| `POST` | `/staffs/invite` | Mời một nhân sự | Root | — |
| `POST` | `/staffs/bulk-invite` | Mời hàng loạt, tối đa 50 | Root | — |
| `POST` | `/staffs/:id/resend-invite` | Gửi lại lời mời | Root | — |
| `POST` | `/staffs/:id/revoke-invite` | Thu hồi lời mời | Root | — |
| `PUT` | `/staffs/me/update-password` | Tự đổi mật khẩu | Đã đăng nhập | Ngoại lệ có chủ đích: mọi vai trò đều cần |
| `POST` | `/staffs/invite/verify` | Xác thực token mời | Công khai | Ngoại lệ: người nhận chưa có tài khoản |
| `POST` | `/staffs/invite/accept` | Nhận lời mời, đặt mật khẩu | Công khai | Ngoại lệ: như trên |
| `POST` | `/staffs/forgot-password` | Yêu cầu email đặt lại mật khẩu | Công khai, rate limiting | Ngoại lệ: người dùng chưa đăng nhập được |
| `POST` | `/staffs/reset-password` | Đặt lại mật khẩu bằng token | Công khai | Ngoại lệ: như trên |
| `GET` | `/audits/login-histories?status=` | Lọc Lịch sử đăng nhập theo kết quả — **ngoài phạm vi cùng FR-013** | Admin | — |

Thay đổi trên endpoint có sẵn: `POST /staffs/login` — rate limiting (FR-011), không phân biệt chữ hoa/thường (FR-018), ghi lần thất bại (FR-013, ngoài phạm vi). `POST /staffs/register` — không trả token (FR-017). `POST /staffs/login-with-google` — gỡ bỏ.

---

## Phụ lục B: Biến template email

Bộ biến trùng với template TCB tương ứng. Trong 2 file mẫu (`email-templates/`), biến viết theo cú pháp của gateway AT là `%tenBien%` — cùng cú pháp với bộ template T-Fluencers đã bàn giao (`t-fluencers/otp-and-sms-gateway/TEMPLATE_EMAIL.md`), nên AT dán thẳng được. Test `TestStaffAuthMailData_MatchesHTMLSamples` đối chiếu biến trong file mẫu với khoá `template_data` backend gửi đi theo cả hai chiều.

| Template | Biến | Ý nghĩa |
|---|---|---|
| `AMBASSADOR_EMAIL_STAFF_INVITE` | `recipientName` | Họ tên người được mời |
| | `acceptUrl` | Đường dẫn nhận lời mời — **chứa token** |
| | `expiryHours` | Số giờ hiệu lực (`48`) |
| | `year` | Năm ở dòng bản quyền. Tên công ty "AccessTrade" ghi cứng trong template |
| `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD` | `recipientName` | Họ tên nhân sự |
| | `resetUrl` | Đường dẫn đặt lại — **chứa token** |
| | `expiryMinutes` | Số phút hiệu lực (`60`) |
| | `year` | Năm ở dòng bản quyền. Tên công ty "AccessTrade" ghi cứng trong template |

---

## Phụ lục C: Thông báo lỗi

| Tình huống | HTTP | Thông báo (tiếng Việt) |
|---|---|---|
| Token mời sai / đã dùng / đã thu hồi | 400 | Đường dẫn mời không hợp lệ. Hãy mở đúng đường dẫn trong email, hoặc nhờ quản trị viên gửi lại lời mời! |
| Token mời hết hạn | 400 | Lời mời đã hết hạn. Hãy nhờ quản trị viên gửi lại lời mời! |
| Token đặt lại sai / đã dùng | 400 | Đường dẫn đặt lại mật khẩu không hợp lệ hoặc đã được sử dụng. Vui lòng yêu cầu lại! |
| Token đặt lại hết hạn | 400 | Đường dẫn đặt lại mật khẩu đã hết hạn. Vui lòng yêu cầu lại! |
| Mật khẩu yếu | 400 | Mật khẩu phải có ít nhất 8 ký tự, gồm cả chữ lẫn số! |
| Mật khẩu quá 72 byte | 400 | Mật khẩu quá dài: tối đa 72 byte (mỗi chữ có dấu tính 2–3 byte)! |
| Xác nhận mật khẩu không khớp | 400 | Mật khẩu xác nhận không khớp! |
| Sai mật khẩu hiện tại | 400 | Mật khẩu hiện tại không đúng! |
| Mật khẩu mới trùng mật khẩu hiện tại | 400 | Mật khẩu mới phải khác mật khẩu hiện tại! |
| Vượt ngưỡng rate limiting | 429 | Bạn đã thử quá nhiều lần. Vui lòng thử lại sau ít phút! (kèm số phút chờ) |
| Không đọc được bộ đếm | 503 | Hệ thống xác thực đang gián đoạn, vui lòng thử lại sau ít phút! |
| Email sai định dạng hoặc tên miền không nhận thư | 400 | Email không hợp lệ hoặc tên miền không nhận thư! |
| Email trùng trong danh sách mời | — (kết quả từng dòng) | Email bị lặp trong danh sách! |
| Danh sách mời rỗng / quá 50 | 400 | Danh sách email mời đang trống! / Mỗi lần mời tối đa 50 email! |
| Gửi lại / thu hồi sai trạng thái | 400 | Tài khoản này không có lời mời đang chờ! / Chỉ thu hồi được lời mời chưa được nhận! |
| Bật/tắt hoặc đặt hộ mật khẩu tài khoản chưa nhận lời mời | 400 | Tài khoản chưa nhận lời mời nên không thể đổi trạng thái hay mật khẩu! |
| Thiếu `ADMIN_WEB_HOST` | 400 | Hệ thống chưa cấu hình địa chỉ trang quản trị (ADMIN_WEB_HOST) nên chưa gửi được đường dẫn! |

---

## Phụ lục D: Yêu cầu gửi các bên

### D-1, D-2 — Team Email AccessTrade

> Ambassador cần 2 template email cho luồng mời nhân sự và đặt lại mật khẩu trang quản trị. Đề nghị nhân bản 2 template đang dùng cho Techcombank — `TECHCOMBANK_EMAIL_STAFF_INVITE` và `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD` — giữ nguyên bộ biến, đổi thương hiệu theo 2 file mẫu đính kèm (`email-templates/`, biến đã viết sẵn theo cú pháp `%tenBien%` của gateway). Đề nghị cấp mã theo quy ước `AMBASSADOR_EMAIL_STAFF_INVITE`, `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD`; tiêu đề theo khuôn template TCB, lần lượt `[AccessTrade] Bạn được mời tham gia trang quản trị Ambassador` và `[AccessTrade] Yêu cầu đặt lại mật khẩu trang quản trị Ambassador`, tiếng Việt. Tài liệu bàn giao đầy đủ theo khuôn TCB: [`TEMPLATE_EMAIL.md`](./TEMPLATE_EMAIL.md). Biến `acceptUrl` và `resetUrl` chứa token đăng nhập dùng một lần — đề nghị không ghi giá trị hai biến này vào log hoặc lịch sử gửi mà bên thứ ba truy cập được. Đề nghị cho biết giới hạn tần suất gửi của API (nếu có): chức năng mời hàng loạt gửi tối đa 50 email mỗi lượt, 10 email song song.

### D-3, D-4 — DevOps

- Khai `ADMIN_WEB_HOST` = địa chỉ Admin Portal (không có dấu `/` cuối) cho develop, staging, production
- Kiểm service **admin** có đủ 4 khoá `ACCESS_TRADE_SMS_END_POINT`, `ACCESS_TRADE_SMS_ACCESS_KEY`, `ACCESS_TRADE_SMS_SECRET_KEY`, `ACCESS_TRADE_SMS_CHANNEL` — cùng giá trị với service public đang gửi email OTP
- Xác nhận chuỗi proxy trước backend production. Nếu là Cloudflare: cấu hình `IPExtractor` đọc `CF-Connecting-IP`, và kiểm lại IP ghi trong Lịch sử đăng nhập cùng CORS middleware

### D-6 — DBA

Chạy script dọn audit của HF-1 theo hướng dẫn trong đầu file `backend/scripts/strip-staff-password-from-audits.js`: chạy thử → backup → chạy thật.

---

## Phụ lục E: FR-013 — ngoài phạm vi

Đặc tả giữ lại để dùng khi đưa FR-013 trở lại phạm vi. Không thuộc phạm vi nghiệm thu của đợt này.

### FR-013: Ghi nhận đăng nhập thất bại

**Priority:** Ngoài phạm vi đợt này (mục 5) — đưa lại vào phạm vi khi tính năng Lịch sử đăng nhập có trên `release` (RQ-9)

**Description:**
Bổ sung lần đăng nhập thất bại vào tính năng Lịch sử đăng nhập để phục vụ giám sát và điều tra sự cố.

**Business Rules:**

- Ghi vào collection Lịch sử đăng nhập, thêm trường `status` (`success` / `failed`). Không tạo collection audit riêng như T-Fluencers
- Chỉ ghi lần sai mật khẩu của **tài khoản đang hoạt động**. Không ghi email không tồn tại, tài khoản bị tắt, hay yêu cầu bị chặn bởi rate limiting — tránh bảng lịch sử bị ghi tràn bằng dữ liệu rác. Số lần bị chặn được theo dõi qua giám sát (NFR-013)
- Bản ghi cũ không có `status` được hiểu là thành công
- Màn Lịch sử đăng nhập có cột "Kết quả" và bộ lọc theo kết quả
- Phạm vi đọc theo ADV thuộc PQ-001 (mục 5)

**Acceptance Criteria:**

- [ ] Sai mật khẩu một tài khoản đang hoạt động: Lịch sử đăng nhập có bản ghi "Sai mật khẩu" kèm IP, thiết bị
- [ ] Lọc "Sai mật khẩu": chỉ trả về lần thất bại
- [ ] Bản ghi có trước ngày phát hành hiển thị "Thành công"

**Dependencies:** FR-011; tính năng Lịch sử đăng nhập (đang ở `develop`, chưa có trên `release`)

---

## Lịch sử thay đổi

| Version | Ngày | Người thực hiện | Nội dung |
|---|---|---|---|
| 2.1 | 2026-10-05 | Nguyễn Đăng Định | Bỏ 6 tiêu chí nghiệm thu: kênh email lỗi (FR-001), mời 50 người khi API email không phản hồi (FR-002), so thời gian phản hồi quên mật khẩu (FR-008), giả mạo `X-Forwarded-For`, Redis lỗi trả 503, thông báo chặn kèm số phút (FR-011). FR-013 chuyển ra ngoài phạm vi, đặc tả dời sang Phụ lục E |
| 2.0 | 2026-09-29 | Nguyễn Đăng Định | Chốt: không còn Open Question. OQ-2 → RQ-11 (tắt luồng cũ khi email đã chạy thật trên production; điều kiện thay cho mốc thời gian) |
| 1.3 | 2026-09-29 | Nguyễn Đăng Định | Bỏ câu hỏi thời hạn lưu Lịch sử đăng nhập (OQ-8) và NFR-014 — ngoài yêu cầu của task; chốt không thêm ràng buộc email ở cơ sở dữ liệu (RQ-10); định nghĩa "Luồng cũ" |
| 1.2 | 2026-09-29 | Nguyễn Đăng Định | Chốt OQ-5 (ghép gap #12), OQ-7 (một nhánh cắt từ `release` mới nhất); FR-013 hoãn; bỏ ước lượng giờ và deadline; đề xuất thời hạn lưu 12 tháng kèm căn cứ |
| 1.1 | 2026-09-29 | Nguyễn Đăng Định | Sau 2 lượt review: sửa kênh email TF, hiện trạng Lịch sử đăng nhập, hành vi bcrypt; thêm 3 lỗi production và hotfix HF-1 → HF-3 (mục 2.5); thêm FR-017, FR-018, NFR-013, NFR-014; chuyển FR-012 sang EPIC-002; fail-closed; KPI đo được; kế hoạch phát hành & rollback; Resolved Questions; Phụ lục C, D; đính kèm mẫu email |
| 1.0 | 2026-09-29 | Nguyễn Đăng Định | Bản đầu tiên |

---

*PRD Version 2.1 — 2026-10-05*
*Tech spec: chưa có*
*Nhánh cài đặt tham chiếu: `feat/staff-invite-password`, cắt từ `release` (repo `ambassador`)*
