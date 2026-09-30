# Email Templates — AT Gateway (AccessTrade) — Ambassador Admin Portal

Tài liệu bàn giao 2 template email của luồng mời nhân sự và đặt lại mật khẩu trang quản trị Ambassador, để AccessTrade tạo trên email gateway. Viết theo khuôn tài liệu bàn giao của T-Fluencers: [`t-fluencers/otp-and-sms-gateway/TEMPLATE_EMAIL.md`](../../t-fluencers/otp-and-sms-gateway/TEMPLATE_EMAIL.md) mục 4 — **cùng bộ biến, cùng cú pháp**, chỉ khác thương hiệu.

PRD: [prd-moi-nhan-su-va-mat-khau-2026-09-29.md](./prd-moi-nhan-su-va-mat-khau-2026-09-29.md) (FR-015, FR-016) · Tech spec: [mục 7](./techspec-moi-nhan-su-va-mat-khau-2026-09-29.md)

## Cách gửi

Cả hai email đi qua một hàm (`backend/pkg/admin/service/staff_auth_mail.go`):

```go
sendStaffAuthEmail(ctx, templateCode, to, data)   // template_code, send_tos, template_data
```

- Body gửi lên gateway: `{ "template_code", "template_data", "send_tos" }` — cùng khuôn với email OTP đang chạy thật của Ambassador (`AMBASSADOR_EMAIL_OTP_VERIFICATION`).
- Endpoint: `POST {ACCESS_TRADE_SMS_END_POINT}/v1.0/partner/email/send`.
- Gateway trả HTTP 200 kèm `status` trong body; backend chỉ coi là gửi được khi `status == "success"`.

> **Lưu ý key naming**: `template_data` dùng **camelCase** (`recipientName`, `acceptUrl`, ...). Placeholder trong HTML dùng format chuẩn của gateway `%key%` (`%recipientName%`, `%acceptUrl%`), khớp thẳng với `template_data` key. **Giữ nguyên chữ hoa/thường** khi tạo template: backend gửi đúng các key ở cột `template_data` key bên dưới.

## Khung HTML chung

Theo khung email OTP đang chạy của Ambassador: nền `#f3f5f7`, card trắng bo góc 12px rộng tối đa 600px, header nền đen `#0b0d0f` hiện tên `%company%` (không dùng ảnh), nút CTA nền đen, footer `© %year% %company%. All rights reserved.`. Font Arial, lang `vi`. Không có ảnh host ngoài.

Khác khung T-Fluencers ở chỗ không có logo, icon mạng xã hội và banner (các ảnh đó là thương hiệu T-Fluencers).

---

## 1. Staff Invite

| | |
|---|---|
| **Const** | `constants.EmailTemplateStaffInvite` |
| **template_code** | `AMBASSADOR_EMAIL_STAFF_INVITE` |
| **Tương ứng bên TCB** | `TECHCOMBANK_EMAIL_STAFF_INVITE` |
| **remark** | Gui email moi tham gia trang quan tri |
| **HTML nguồn** | [`email-templates/staff_invite_email.html`](./email-templates/staff_invite_email.html) |
| **Subject** | `[%company%] Bạn được mời tham gia hệ thống` |

**template_data:**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `recipientName` | `%recipientName%` | string | tên người được mời |
| `company` | `%company%` | string | tên công ty — hiện là "AccessTrade" |
| `acceptUrl` | `%acceptUrl%` | string | link nhận lời mời (CTA) — **chứa token dùng một lần** |
| `expiryHours` | `%expiryHours%` | string | số giờ link hết hạn — hiện là "48" |
| `year` | `%year%` | string | năm (footer) |

> Khác TCB một biến: **không dùng `inviterName`**. Chỉ tài khoản cao nhất của AccessTrade được mời, và tên tài khoản đó trong DB là "Root" — thư sẽ ghi "Root đã mời bạn". Câu mời vì vậy ghi cố định "Admin %company%". Backend hiện vẫn gửi khoá `inviterName` trong `template_data`; template không tham chiếu nên bỏ qua.

Nội dung: mời nhân sự vào trang quản trị. "Admin %company%" đã mời, bấm nút để tự đặt mật khẩu và kích hoạt tài khoản. CTA "Nhận lời mời". Kèm đường dẫn dạng chữ phòng khi nút không bấm được. Ghi chú: dùng một lần, hết hạn sau `expiryHours` giờ.

#### HTML

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Lời mời tham gia trang quản trị</title>
  </head>
  <body style="margin: 0; padding: 0; width: 100% !important; background-color: #f3f5f7; font-family: Arial, Helvetica, sans-serif;">
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
        style="max-width: 600px; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);">
        <!-- HEADER -->
        <tr>
          <td style="background-color: #0b0d0f; padding: 16px 20px; color: #fff; font-size: 18px; font-weight: bold; text-align: center;">
            %company%
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 32px 24px">
            <h2 style="margin: 0 0 24px 0; font-size: 24px; font-weight: 700; color: #101828; text-align: center;">
              Lời mời tham gia trang quản trị
            </h2>

            <p style="margin: 0 0 16px; font-size: 16px; color: #344054; line-height: 24px;">
              Xin chào <b>%recipientName%</b>,
            </p>

            <p style="margin: 0 0 24px; font-size: 16px; color: #344054; line-height: 24px;">
              <b>Admin %company%</b> đã mời bạn tham gia trang quản trị. Bấm nút bên dưới để tự đặt mật khẩu và kích hoạt tài khoản.
            </p>

            <div style="text-align: center; margin-bottom: 24px;">
              <a href="%acceptUrl%" target="_blank"
                style="display: inline-block; background: #0b0d0f; color: #fff; font-size: 16px; font-weight: 700; text-decoration: none; padding: 14px 32px; border-radius: 8px;">
                Nhận lời mời
              </a>
            </div>

            <p style="margin: 0 0 16px; font-size: 14px; color: #667085; line-height: 20px;">
              Nếu nút không bấm được, hãy sao chép đường dẫn sau vào trình duyệt:<br />
              <a href="%acceptUrl%" target="_blank" style="color: #175cd3; word-break: break-all;">%acceptUrl%</a>
            </p>

            <p style="margin: 0; font-size: 14px; color: #667085; line-height: 20px;">
              Đường dẫn chỉ dùng được một lần và hết hạn sau %expiryHours% giờ. Nếu bạn không chờ lời mời này, hãy bỏ qua email — tài khoản sẽ không được kích hoạt.
            </p>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="padding: 24px; text-align: center; font-size: 12px; color: #667085; border-top: 1px solid #eaecf0; background-color: #f9fafb;">
            <p style="margin: 0 0 8px;">Email này được gửi tự động. Vui lòng không trả lời email này.</p>
            <p style="margin: 0;">© %year% %company%. All rights reserved.</p>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

---

## 2. Staff Reset Password

| | |
|---|---|
| **Const** | `constants.EmailTemplateStaffResetPassword` |
| **template_code** | `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD` |
| **Tương ứng bên TCB** | `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD` |
| **remark** | Gui email dat lai mat khau |
| **HTML nguồn** | [`email-templates/staff_reset_password_email.html`](./email-templates/staff_reset_password_email.html) |
| **Subject** | `[%company%] Yêu cầu đặt lại mật khẩu` |

**template_data:**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `recipientName` | `%recipientName%` | string | tên người nhận |
| `company` | `%company%` | string | tên công ty — hiện là "AccessTrade" |
| `resetUrl` | `%resetUrl%` | string | link đặt lại mật khẩu (CTA) — **chứa token dùng một lần** |
| `expiryMinutes` | `%expiryMinutes%` | string | số phút link hết hạn — hiện là "60" |
| `year` | `%year%` | string | năm (footer) |

Nội dung: xác nhận yêu cầu đặt lại mật khẩu. CTA "Đặt mật khẩu mới". Kèm đường dẫn dạng chữ. Ghi chú: dùng một lần, hết hạn sau `expiryMinutes` phút; không yêu cầu thì bỏ qua, mật khẩu giữ nguyên.

#### HTML

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Đặt lại mật khẩu trang quản trị</title>
  </head>
  <body style="margin: 0; padding: 0; width: 100% !important; background-color: #f3f5f7; font-family: Arial, Helvetica, sans-serif;">
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
        style="max-width: 600px; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);">
        <!-- HEADER -->
        <tr>
          <td style="background-color: #0b0d0f; padding: 16px 20px; color: #fff; font-size: 18px; font-weight: bold; text-align: center;">
            %company%
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 32px 24px">
            <h2 style="margin: 0 0 24px 0; font-size: 24px; font-weight: 700; color: #101828; text-align: center;">
              Đặt lại mật khẩu
            </h2>

            <p style="margin: 0 0 16px; font-size: 16px; color: #344054; line-height: 24px;">
              Xin chào <b>%recipientName%</b>,
            </p>

            <p style="margin: 0 0 24px; font-size: 16px; color: #344054; line-height: 24px;">
              Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản quản trị của bạn. Bấm nút bên dưới để đặt mật khẩu mới.
            </p>

            <div style="text-align: center; margin-bottom: 24px;">
              <a href="%resetUrl%" target="_blank"
                style="display: inline-block; background: #0b0d0f; color: #fff; font-size: 16px; font-weight: 700; text-decoration: none; padding: 14px 32px; border-radius: 8px;">
                Đặt mật khẩu mới
              </a>
            </div>

            <p style="margin: 0 0 16px; font-size: 14px; color: #667085; line-height: 20px;">
              Nếu nút không bấm được, hãy sao chép đường dẫn sau vào trình duyệt:<br />
              <a href="%resetUrl%" target="_blank" style="color: #175cd3; word-break: break-all;">%resetUrl%</a>
            </p>

            <p style="margin: 0; font-size: 14px; color: #667085; line-height: 20px;">
              Đường dẫn chỉ dùng được một lần và hết hạn sau %expiryMinutes% phút. Nếu bạn không yêu cầu, hãy bỏ qua email — mật khẩu hiện tại vẫn giữ nguyên.
            </p>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="padding: 24px; text-align: center; font-size: 12px; color: #667085; border-top: 1px solid #eaecf0; background-color: #f9fafb;">
            <p style="margin: 0 0 8px;">Email này được gửi tự động. Vui lòng không trả lời email này.</p>
            <p style="margin: 0;">© %year% %company%. All rights reserved.</p>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

---

## Bảng tổng hợp

| template_code | Subject | Data keys | Bản TCB tương ứng |
|---|---|---|---|
| `AMBASSADOR_EMAIL_STAFF_INVITE` | `[%company%] Bạn được mời tham gia hệ thống` | recipientName, company, acceptUrl, expiryHours, year | `TECHCOMBANK_EMAIL_STAFF_INVITE` |
| `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD` | `[%company%] Yêu cầu đặt lại mật khẩu` | recipientName, company, resetUrl, expiryMinutes, year | `TECHCOMBANK_EMAIL_STAFF_FORGOT_PASSWORD` |

## Điền form đăng ký template của AccessTrade

Điền form 2 lần, mỗi template một lần.

| Ô trên form | Lấy từ |
|---|---|
| Mã template | cột `template_code` |
| Tiêu đề email | dòng **Subject** — có biến `%company%` |
| Nội dung email | khối **HTML** của template đó, dán nguyên văn từ `<!DOCTYPE html>` tới `</html>` |
| Mô tả / ghi chú (nếu có) | dòng **remark** |

## Yêu cầu với AccessTrade

1. `acceptUrl` và `resetUrl` chứa token đăng nhập dùng một lần — đề nghị **không ghi giá trị hai biến này vào log hoặc lịch sử gửi** mà bên thứ ba đọc được.
2. Nếu mã template được cấp khác 2 mã đề nghị ở trên, báo lại để backend cập nhật (`backend/internal/constants/email_template.go`).
3. Cho biết giới hạn tần suất gửi của API (nếu có): chức năng mời hàng loạt gửi tối đa 50 email mỗi lượt, 10 email song song.

## Việc cần làm

1. **AccessTrade tạo 2 template** theo bảng trên.
2. **Backend**: cập nhật 2 hằng mã template nếu AT cấp mã khác.
3. **DevOps**: khai `ADMIN_WEB_HOST` cho service backend-admin (dev: `https://admin-ambassador.diso.vn`) — thiếu thì backend dừng trước khi gọi gateway.
4. **Kiểm**: mời một email trên dev, xem thư tới đúng bố cục và các biến được thay đủ.
