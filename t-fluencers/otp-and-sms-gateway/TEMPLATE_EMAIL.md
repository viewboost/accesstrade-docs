# Email Templates — AT Gateway (AccessTrade)

Tài liệu mô tả từng `template_code` gửi qua email gateway của AccessTrade: cần truyền `template_data` nào, và thông tin HTML/nội dung hiện tại tương ứng.

## Cách gửi

Tất cả email đi qua một func duy nhất:

```go
internalservice.Otp().SendEmailAccessTrade(ctx, modelmg.EmailGatewayPayload{
    TemplateCode: constants.EmailTemplateCode...,   // template_code
    SendTos:      []string{"user@example.com"},     // send_tos
    Data:         map[string]interface{}{ ... },     // gộp tất cả field động
})
```

- Func `SendEmailAccessTrade` gọi `buildEmailTemplateData()` → `switch TemplateCode` để nhặt đúng field từ `Data` và build `template_data`.
- Chỉ các key có trong `Data` mới được đưa vào `template_data` (thiếu/thừa đều không vỡ), nên caller cần truyền đủ key mà template HTML cần.
- Body gửi lên gateway: `{ "template_code", "template_data", "send_tos", "remark" }`.
- Endpoint: `POST {AT_GATEWAY_END_POINT}/v1.0/partner/email/send`.

> **Lưu ý key naming**: `template_data` dùng **camelCase** (`userName`, `eventCode`, ...). Các file HTML hiện tại là Go `html/template` dùng **PascalCase** (`{{.UserName}}`, `{{.EventCode}}`). Bảng dưới map rõ hai bên. Khi tạo template thật trên gateway, đặt biến theo cột **`template_data` key**.

## Khung HTML chung

Mọi template dùng chung khung email: nền `#f3f5f7`, card trắng bo góc 12px, header nền đen `#0b0d0f` (logo `email_logo.png` + 3 icon social X/Facebook/Instagram), hero banner `email_banner.png`, footer `© {{.Year}} {{.Company}}. All rights reserved.`. Ảnh host tại `https://media.tfluencer.vn/public/`. Font Arial, lang `vi`.

Vì vậy hầu hết template đều cần thêm `year` và `company` trong `template_data` (cho footer), và các link ảnh cố định trong template.

---

## 1. OTP Verification

| | |
|---|---|
| **Const** | `constants.EmailTemplateCodeOTPVerification` |
| **template_code** | `TFLUENCER_EMAIL_OTP_VERIFICATION` |
| **remark** | Gui OTP xac thuc email cho nguoi dung |
| **Nguồn HTML hiện tại** | *(chưa có template Go nội bộ — là email OTP thuần, gateway render)* |

**template_data:**

| key | kiểu | mô tả |
|---|---|---|
| `code` | string | mã OTP |

> **HTML hiện tại**: chưa có HTML nội bộ, gateway render.

---

## 2. Budget Alerts (75% / 95% / 100% / Threshold)

4 template_code dùng chung bộ field. Nguồn HTML: `budget.go` (`Budget75PercentTemplate`, `Budget95PercentTemplate`, `Budget100PercentTemplate`) và `threshold.go` (`ThresholdTemplate`).

| Const | template_code | HTML nguồn |
|---|---|---|
| `EmailTemplateCodeBudget75Percent` | `TFLUENCER_EMAIL_BUDGET_75_PERCENT` | `budget.go` → `Budget75PercentTemplate` |
| `EmailTemplateCodeBudget95Percent` | `TFLUENCER_EMAIL_BUDGET_95_PERCENT` | `budget.go` → `Budget95PercentTemplate` |
| `EmailTemplateCodeBudget100Percent` | `TFLUENCER_EMAIL_BUDGET_100_PERCENT` | `budget.go` → `Budget100PercentTemplate` |
| `EmailTemplateCodeBudgetThreshold` | `TFLUENCER_EMAIL_BUDGET_THRESHOLD` | `threshold.go` → `ThresholdTemplate` |

**remark:** `Gui email canh bao nguong ngan sach`

**template_data (build từ `buildEmailTemplateData`):**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `percent` | `{{.Percent}}` | float32 | % ngân sách đã dùng |
| `eventName` | `{{.EventName}}` | string | tên thử thách |
| `eventCode` | `{{.EventCode}}` | string | mã thử thách (hiển thị trong `{{if .EventCode}}`) |
| `userName` | `{{.UserName}}` | string | tên người nhận |
| `year` | `{{.Year}}` | string | năm (footer) |
| `company` | `{{.Company}}` | string | tên công ty (footer) |
| `linkEvent` | `{{.LinkEvent}}` | string | link chi tiết chương trình (CTA chính) |
| `linkHome` | `{{.LinkHome}}` | string | link khám phá thử thách mới (CTA phụ) |
| `linkPolicy` | `{{.LinkPolicy}}` | string | link chính sách ngân sách |

### Nội dung từng ngưỡng

**75% — `Budget75PercentTemplate`**
- Subject: `T-Fluencers | %s đang nóng lên! 🔥 Cập nhật mới dành cho bạn` (`%s` = eventLabel)
- Cảnh báo đã dùng 75% ngân sách phí quảng cáo, kêu gọi đăng video nhanh. Nhấn màu cam `#dc6803`.
- CTA: "Xem chi tiết chương trình" (`linkEvent`, nền đen) + "Khám phá thử thách mới" (`linkHome`, nền trắng viền).

#### HTML hiện tại (`Budget75PercentTemplate` — budget.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>T-Fluencers - Cập nhật mức phí quảng cáo chương trình</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 830px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img
                    src="https://media.tfluencer.vn/public/email_logo.png"
                    alt="Logo"
                    width="234"
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_x.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_f.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_i.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <p
              style="
                margin: 0 0 20px;
                font-size: 24px;
                color: #181d27;
                font-weight: 700;
              "
            >
              T-Fluencers | {{if .EventCode}}[{{.EventCode}}] {{end}}{{.EventName}} đang nóng lên! 🔥 Cập nhật mới
              dành cho bạn
            </p>
            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:user@gmail.com"
                style="color: #1570ef; text-decoration: underline"
                >{{.UserName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              <span style="color: #dc6803; font-weight: 700"
                >75% ngân sách phí quảng cáo đã được sử dụng! 🔥</span
              >
              <br>
              Chương trình đang nóng lên từng ngày! Hãy đăng video và lan tỏa
              thật nhanh để nhận phí quảng cáo trước khi ngân sách chạm ngưỡng cuối
              cùng.
              <br>
              Bạn có thể xem thêm
              <a href="{{.LinkPolicy}}" style="font-weight: 700; color: #1570ef"
                >chính sách và quy định ngân sách</a
              >
              của chương trình tại liên kết bên dưới để nắm rõ cách tính phí quảng cáo.
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.LinkEvent}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      margin-right: 10px;
                    "
                    >Xem chi tiết chương trình</a
                  >
                </td>
                <td>
                  <a
                    href="{{.LinkHome}}"
                    style="
                      display: inline-block;
                      background: #ffffff;
                      color: #414651;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      border: 1px solid #d5d7da;
                    "
                    >Khám phá thử thách mới</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
            Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

**95% — `Budget95PercentTemplate`**
- Subject: `T-Fluencers | %s đã đạt 95% ngân sách phí quảng cáo! ⚡`
- Đạt 95%, chương trình tạm dừng nhận video mới nhưng video cũ vẫn tính phí. Nhấn màu đỏ `#d92d20`. CTA giống 75%.

#### HTML hiện tại (`Budget95PercentTemplate` — budget.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>T-Fluencers - Cập nhật mức phí quảng cáo chương trình</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 830px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img
                    src="https://media.tfluencer.vn/public/email_logo.png"
                    alt="Logo"
                    width="234"
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_x.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_f.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_i.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <p
              style="
                margin: 0 0 20px;
                font-size: 24px;
                color: #181d27;
                font-weight: 700;
              "
            >
              T-Fluencers | {{if .EventCode}}[{{.EventCode}}] {{end}}{{.EventName}} đã đạt 95% ngân sách phí quảng cáo!⚡
            </p>
            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:user@gmail.com"
                style="color: #1570ef; text-decoration: underline"
                >{{.UserName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              <span style="font-weight: 700; color: #d92d20"
                >Ngân sách phí quảng cáo của <b>{{.EventName}}</b> trên
                <b>T-Fluencers</b> đã đạt <b>95%</b>! ⚡</span
              >
              <br />
              Hiện chương trình đã <b>tạm dừng nhận video mới</b>, nhưng đừng lo
              — video bạn đã đăng vẫn tiếp tục được tính phí quảng cáo khi lượt xem
              tăng. Tiếp tục chia sẻ để <b>tối đa</b> phần phí quảng cáo trước khi ngân
              sách chạm ngưỡng cuối cùng.
              <br />
              Bạn có thể xem thêm
              <a href="{{.LinkPolicy}}" style="font-weight: 700; color: #1570ef"
                >chính sách và quy định ngân sách</a
              >
              của chương trình tại liên kết bên dưới để nắm rõ cách tính phí quảng cáo.
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.LinkEvent}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      margin-right: 10px;
                    "
                    >Xem chi tiết chương trình</a
                  >
                </td>
                <td>
                  <a
                    href="{{.LinkHome}}"
                    style="
                      display: inline-block;
                      background: #ffffff;
                      color: #414651;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      border: 1px solid #d5d7da;
                    "
                    >Khám phá thử thách mới</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
            Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

**100% — `Budget100PercentTemplate`**
- Subject: `T-Fluencers | %s đã chạm mốc 100%! 🎉`
- Đã dùng 100% ngân sách, cảm ơn, hành trình khép lại, mời chuẩn bị hành trình tiếp theo. Nhấn đỏ `#d92d20`. CTA giống trên.

#### HTML hiện tại (`Budget100PercentTemplate` — budget.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>T-Fluencers - Cập nhật mức phí quảng cáo chương trình</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 830px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img
                    src="https://media.tfluencer.vn/public/email_logo.png"
                    alt="Logo"
                    width="234"
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_x.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_f.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_i.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <p
              style="
                margin: 0 0 20px;
                font-size: 20px;
                color: #181d27;
                font-weight: 700;
                line-height: 1.4;
              "
            >
              T-Fluencers | {{if .EventCode}}[{{.EventCode}}] {{end}}<b>{{.EventName}}</b> đã chạm mốc 100%! 🎉
            </p>
            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:user@gmail.com"
                style="color: #1570ef; text-decoration: underline"
                >{{.UserName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 12px;
                font-size: 14px;
                color: #d92d20;
                font-weight: 700;
                line-height: 22px;
              "
            >
              100% ngân sách phí quảng cáo của <b>{{.EventName}}</b> trên <b>T-Fluencers</b> đã được sử dụng! 🎉
            </p>
            <p
              style="
                margin: 0 0 14px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Hành trình này đã khép lại — cảm ơn bạn đã lan toả hết mình cùng <b>T-Fluencers</b>!
            </p>
            <p
              style="
                margin: 0 0 14px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Đừng quên xem lại
              <a href="{{.LinkPolicy}}" style="font-weight: 700; color: #1570ef; text-decoration: underline;"
                >chính sách và quy định ngân sách</a
              >
              để nắm rõ cách tính phí quảng cáo và kết quả cuối cùng của chương trình.
            </p>
            <p
              style="
                margin: 0 0 24px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Cùng chuẩn bị cho hành trình tiếp theo — nơi những thử thách mới và phần phí quảng cáo hấp dẫn đang chờ bạn chinh phục!
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.LinkEvent}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      margin-right: 10px;
                    "
                    >Xem chi tiết chương trình</a
                  >
                </td>
                <td>
                  <a
                    href="{{.LinkHome}}"
                    style="
                      display: inline-block;
                      background: #ffffff;
                      color: #414651;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                      border: 1px solid #d5d7da;
                    "
                    >Khám phá thử thách mới</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
            Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

**Threshold — `ThresholdTemplate`** *(cảnh báo cho admin/người thiết lập ngưỡng)*
- Subject: `Cảnh báo ngưỡng ngân sách` (tĩnh)
- Tiêu đề `<h2>` màu cam `#f79009` + icon tam giác cảnh báo. **Stat grid 3 ô**: Ngưỡng ngân sách, Chi tiêu hiện tại (cam), Tỷ lệ sử dụng (cam). CTA "Xem chi tiết →" (nền đen). Card hẹp `max-width: 680px`.
- HTML threshold dùng bộ placeholder RIÊNG (struct `ThresholdTemplatePayload`), khác 3 template budget ở trên:

  | HTML placeholder | mô tả |
  |---|---|
  | `{{.EmailAddress}}` | email người nhận |
  | `{{.RecipientName}}` | tên người nhận |
  | `{{.EventCode}}` | mã thử thách (trong `{{if}}`) |
  | `{{.ProgramName}}` | tên chương trình |
  | `{{.Threshold}}` | ngưỡng ngân sách |
  | `{{.CurrentSpend}}` | chi tiêu hiện tại |
  | `{{.PercentUsed}}` | tỷ lệ sử dụng (%) |
  | `{{.DetailsURL}}` | link chi tiết (CTA) |
  | `{{.Year}}`, `{{.Company}}` | footer |

  > Field `LogoURL`, `Time`, `ThumbnailURL`, `Status`, `Note` có trong struct nhưng **không** dùng trong HTML threshold (một số chỉ xuất hiện ở plainText).

#### HTML hiện tại (`ThresholdTemplate` — threshold.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Cảnh báo ngân sách</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 680px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img 
                    src="https://media.tfluencer.vn/public/email_logo.png" 
                    alt="Logo" 
                    width="234" 
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_x.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_f.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_i.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <h2
              style="
                margin: 0 0 8px 0;
                font-size: 20px;
                font-weight: 700;
                color: #f79009;
                display: flex;
                align-items: center;
                gap: 8px;
              "
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M12.8126 1.66837C12.2953 1.43834 11.7047 1.43834 11.1874 1.66837C10.7878 1.84602 10.5283 2.15894 10.3477 2.41391C10.1701 2.66461 9.98004 2.99303 9.77096 3.35422L1.50381 17.6339C1.2939 17.9964 1.10315 18.3258 0.973806 18.6054C0.842356 18.8895 0.699752 19.2714 0.745201 19.7074C0.804012 20.2715 1.09955 20.7841 1.55827 21.1176C1.91276 21.3753 2.31476 21.4433 2.62652 21.4719C2.93327 21.5 3.31392 21.5 3.73281 21.5H20.2671C20.686 21.5 21.0667 21.5 21.3734 21.4719C21.6852 21.4433 22.0872 21.3753 22.4417 21.1176C22.9004 20.7841 23.1959 20.2715 23.2547 19.7074C23.3002 19.2714 23.1576 18.8895 23.0261 18.6054C22.8968 18.3258 22.7061 17.9964 22.4962 17.6339L14.229 3.35419C14.0199 2.99301 13.8298 2.66459 13.6522 2.41391C13.4716 2.15894 13.2121 1.84602 12.8126 1.66837ZM13 9C13 8.44772 12.5523 8 12 8C11.4477 8 11 8.44772 11 9V13C11 13.5523 11.4477 14 12 14C12.5523 14 13 13.5523 13 13V9ZM12 16C11.4477 16 11 16.4477 11 17C11 17.5523 11.4477 18 12 18H12.01C12.5623 18 13.01 17.5523 13.01 17C13.01 16.4477 12.5623 16 12.01 16H12Z"
                  fill="#F79009"
                /></svg
              >Cảnh báo ngân sách: Chương trình đạt ngưỡng
            </h2>

            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:{{.EmailAddress}}"
                style="color: #1570ef; text-decoration: underline"
                >{{.RecipientName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Chương trình <strong>{{if .EventCode}}[{{.EventCode}}] {{end}}{{.ProgramName}}</strong> đã đạt ngưỡng ngân sách mà bạn đã thiết lập.
            </p>

            <!-- STAT GRID -->
            <table
              width="100%"
              cellspacing="0"
              cellpadding="0"
              style="border-collapse: collapse; margin-bottom: 16px"
            >
              <tr>
                <td width="33.33%" style="padding: 6px">
                  <table
                    width="100%"
                    style="
                      border: 1px solid #eaecf0;
                      border-radius: 12px;
                      padding: 16px;
                    "
                  >
                    <tr>
                      <td>
                        <div
                          style="
                            font-size: 12px;
                            font-weight: 500;
                            margin-bottom: 6px;
                          "
                        >
                          Ngưỡng ngân sách
                        </div>
                        <div
                          style="
                            font-size: 22px;
                            font-weight: 600;
                            color: #1d2939;
                          "
                        >
                          {{.Threshold}}
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>

                <td width="33.33%" style="padding: 6px">
                  <table
                    width="100%"
                    style="
                      background-color: #fffaeb;
                      border: 1px solid #dc6803;
                      border-radius: 12px;
                      padding: 16px;
                    "
                  >
                    <tr>
                      <td>
                        <div
                          style="
                            font-size: 12px;
                            font-weight: 500;
                            margin-bottom: 6px;
                          "
                        >
                          Chi tiêu hiện tại
                        </div>
                        <div
                          style="
                            font-size: 22px;
                            font-weight: 600;
                            color: #dc6803;
                          "
                        >
                          {{.CurrentSpend}}
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>

                <td width="33.33%" style="padding: 6px">
                  <table
                    width="100%"
                    style="
                      background-color: #fffaeb;
                      border: 1px solid #dc6803;
                      border-radius: 12px;
                      padding: 16px;
                    "
                  >
                    <tr>
                      <td>
                        <div
                          style="
                            font-size: 12px;
                            font-weight: 500;
                            margin-bottom: 6px;
                          "
                        >
                          Tỷ lệ sử dụng
                        </div>
                        <div
                          style="
                            font-size: 22px;
                            font-weight: 600;
                            color: #dc6803;
                          "
                        >
                          {{.PercentUsed}}%
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>

            <!-- CTA BUTTON -->
            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.DetailsURL}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                    "
                    >Xem chi tiết →</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
          Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

> ⚠️ **Cần thống nhất**: hiện `buildEmailTemplateData` gộp cả 4 ngưỡng vào một bộ key (`percent, eventName, eventCode, userName, year, company, linkEvent, linkHome, linkPolicy`). Template threshold trên gateway nếu dùng bộ field riêng (`threshold, currentSpend, percentUsed, detailsUrl, programName, recipientName, emailAddress`) thì cần bổ sung nhánh `pick(...)` riêng cho `EmailTemplateCodeBudgetThreshold`. Xem mục [Việc cần làm](#việc-cần-làm).

---

## 3. User Social — Kết quả phê duyệt kênh

Nguồn HTML: `user_social.go`. Chọn approved/rejected theo `Status`.

| Const | template_code | HTML nguồn |
|---|---|---|
| `EmailTemplateCodeUserSocialApprove` | `TFLUENCER_EMAIL_USER_SOCIAL_APPROVED` | `UserSocialApprovedTemplate` |
| `EmailTemplateCodeUserSocialReject` | `TFLUENCER_EMAIL_USER_SOCIAL_REJECTED` | `UserSocialRejectedTemplate` |

**remark:** `Gui email ket qua phe duyet kenh`

**template_data:**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `company` | `{{.Company}}` | string | tên công ty (footer) |
| `userName` | `{{.UserName}}` | string | tên influencer |
| `year` | `{{.Year}}` | string | năm (footer) |
| `linkAction` | `{{.LinkAction}}` | string | link CTA |
| `reason` | `{{.Reason}}` | string | lý do (chỉ dùng ở template rejected) |
| `status` | `{{.Status}}` | string | trạng thái (dùng để chọn template) |

### Nội dung

**Approved — `UserSocialApprovedTemplate`**
- Subject: `[T-Fluencers] Chúc mừng bạn đã đăng ký thành công`
- `<h2>` màu xanh `#079455` + icon check tròn: "Kênh đã được duyệt". Chúc mừng + hướng dẫn tuân thủ nguyên tắc cộng đồng. CTA "Tham gia thử thách ngay →" (`linkAction`, nền đen). Placeholder dùng: `userName`, `linkAction`, `year`, `company`.

#### HTML hiện tại (`UserSocialApprovedTemplate` — user_social.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Chúc mừng! Kênh bạn đã được duyệt</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 680px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img 
                    src="https://media.tfluencer.vn/public/email_logo.png" 
                    alt="Logo" 
                    width="234" 
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_x.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_f.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_i.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <h2
              style="
                margin: 0 0 8px 0;
                font-size: 20px;
                font-weight: 700;
                color: #079455;
                display: flex;
                align-items: center;
                gap: 8px;
              "
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M12 1C5.92487 1 1 5.92487 1 12C1 18.0751 5.92487 23 12 23C18.0751 23 23 18.0751 23 12C23 5.92487 18.0751 1 12 1ZM17.2071 9.70711C17.5976 9.31658 17.5976 8.68342 17.2071 8.29289C16.8166 7.90237 16.1834 7.90237 15.7929 8.29289L10.5 13.5858L8.20711 11.2929C7.81658 10.9024 7.18342 10.9024 6.79289 11.2929C6.40237 11.6834 6.40237 12.3166 6.79289 12.7071L9.79289 15.7071C10.1834 16.0976 10.8166 16.0976 11.2071 15.7071L17.2071 9.70711Z"
                  fill="#079455"
                />
              </svg>

              Kênh đã được duyệt
            </h2>

            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:user@gmail.com"
                style="color: #1570ef; text-decoration: underline"
                >{{.UserName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
            Chúc mừng! Kênh của bạn đã được duyệt
            <br>
            Sau quá trình xem xét, chúng tôi vui mừng thông báo rằng kênh của bạn đã được phê duyệt.
            <br>
            Từ giờ, bạn có thể bắt đầu đăng tải nội dung, kết nối với cộng đồng và tận dụng các tính năng đặc biệt dành cho kênh đã xác minh.
            <br>
            Hãy đảm bảo rằng bạn tuân thủ đầy đủ các nguyên tắc cộng đồng và chính sách nội dung để duy trì trạng thái phê duyệt.
            <br>
            Chào mừng bạn đến với T-Fluencers!
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.LinkAction}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                    "
                    >Tham gia thử thách ngay →</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
		  Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

**Rejected — `UserSocialRejectedTemplate`**
- Subject: `[T-Fluencers] Xin lỗi! Kênh của bạn đã không được phê duyệt`
- `<h2>` màu đỏ `#d92d20` + icon cảnh báo tròn: "Kênh đã bị từ chối". Hiển thị `reason`, khuyến khích cập nhật hồ sơ và gửi lại. CTA "Xem lại hồ sơ →" (`linkAction`, nền đen). Placeholder dùng: `userName`, `reason`, `linkAction`, `year`, `company`.

#### HTML hiện tại (`UserSocialRejectedTemplate` — user_social.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Xin lỗi! Kênh của bạn đã không được phê duyệt</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 680px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img 
                    src="https://media.tfluencer.vn/public/email_logo.png" 
                    alt="Logo" 
                    width="234" 
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_x.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_f.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img 
                      src="https://media.tfluencer.vn/public/email_ic_i.png" 
                      alt="Twitter" 
                      width="20" 
                      height="20"
                      style="display: block;"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <h2
              style="
                margin: 0 0 8px 0;
                font-size: 20px;
                font-weight: 700;
                color: #d92d20;
                display: flex;
                align-items: center;
                gap: 8px;
              "
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M12 1C5.92487 1 1 5.92487 1 12C1 18.0751 5.92487 23 12 23C18.0751 23 23 18.0751 23 12C23 5.92487 18.0751 1 12 1ZM13 8C13 7.44772 12.5523 7 12 7C11.4477 7 11 7.44772 11 8V12C11 12.5523 11.4477 13 12 13C12.5523 13 13 12.5523 13 12V8ZM12 15C11.4477 15 11 15.4477 11 16C11 16.5523 11.4477 17 12 17H12.01C12.5623 17 13.01 16.5523 13.01 16C13.01 15.4477 12.5623 15 12.01 15H12Z"
                  fill="#D92D20"
                />
              </svg>

              Kênh đã bị từ chối
            </h2>

            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào,
              <a
                href="mailto:user@gmail.com"
                style="color: #1570ef; text-decoration: underline"
                >{{.UserName}}</a
              >
            </p>

            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
            Sau khi xem xét, chúng tôi rất tiếc phải thông báo rằng kênh của bạn hiện chưa được duyệt.
            <br>
            Lý do: {{.Reason}}
            <br>
            Một số tiêu chí trong hồ sơ hoặc nội dung kênh chưa đáp ứng yêu cầu phê duyệt ở thời điểm này.
            <br>
            Bạn hoàn toàn có thể cập nhật lại thông tin và gửi yêu cầu duyệt lần sau khi đã sẵn sàng.
            <br>
            Cảm ơn bạn đã quan tâm và đồng hành cùng T-Fluencers!
            </p>

            <!-- CTA BUTTON -->
            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.LinkAction}}"
                    style="
                      display: inline-block;
                      background: #101828;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                    "
                    >Xem lại hồ sơ →</a
                  >
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
		  Bạn nhận email này vì đã đăng ký tham gia T-Fluencers
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

---

## 4. Staff — Mời tham gia & Đặt lại mật khẩu

Nguồn HTML: `staff_auth.go`. CTA nền xanh `#1570ef` (khác các CTA đen ở trên). Card `max-width: 830px`. **Không có plainText.**

### 4.1 Staff Invite

| | |
|---|---|
| **Const** | `constants.EmailTemplateCodeStaffInvite` |
| **template_code** | `TFLUENCER_EMAIL_STAFF_INVITE` |
| **remark** | Gui email moi tham gia he thong |
| **HTML nguồn** | `staffInviteTemplate` (render qua `RenderInviteStaffEmail`) |
| **Subject hiện tại** | `InviteStaffEmailSubject(company)` = `[{company}] Bạn được mời tham gia hệ thống` |

**template_data:**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `recipientName` | `{{.RecipientName}}` | string | tên người được mời |
| `inviterName` | `{{.InviterName}}` | string | tên người mời |
| `company` | `{{.Company}}` | string | tên công ty |
| `acceptUrl` | `{{.AcceptURL}}` | string | link chấp nhận lời mời (CTA) |
| `expiryHours` | `{{.ExpiryHours}}` | int | số giờ link hết hạn |
| `year` | `{{.Year}}` | string | năm (footer) |

Nội dung: mời staff vào hệ thống quản trị. Tiêu đề "Bạn được mời tham gia {company}", `inviterName` đã mời, hướng dẫn chấp nhận + thiết lập mật khẩu. CTA "Chấp nhận lời mời →". Ghi chú hết hạn sau `expiryHours` giờ.

#### HTML hiện tại (`staffInviteTemplate` — staff_auth.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{.Company}} - Lời mời tham gia hệ thống</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 830px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img
                    src="https://media.tfluencer.vn/public/email_logo.png"
                    alt="Logo"
                    width="234"
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_x.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_f.png"
                      alt="Facebook"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_i.png"
                      alt="Instagram"
                      width="20"
                      height="20"
                      style="display: block"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <p
              style="
                margin: 0 0 20px;
                font-size: 24px;
                color: #181d27;
                font-weight: 700;
              "
            >
              Bạn được mời tham gia {{.Company}}
            </p>
            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào, <strong>{{.RecipientName}}</strong>
            </p>
            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              <strong>{{.InviterName}}</strong> đã mời bạn tham gia hệ thống quản trị <strong>{{.Company}}</strong>.
              Nhấn vào nút bên dưới để chấp nhận lời mời và thiết lập mật khẩu cho tài khoản của bạn.
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.AcceptURL}}"
                    style="
                      display: inline-block;
                      background: #1570ef;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                    "
                    >Chấp nhận lời mời &#8594;</a
                  >
                </td>
              </tr>
            </table>

            <p
              style="
                margin: 20px 0 0;
                font-size: 12px;
                color: #667085;
                line-height: 20px;
              "
            >
              Link hết hạn sau {{.ExpiryHours}} giờ. Nếu bạn không nhận được lời mời này, hãy bỏ qua email này.
            </p>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
            Bạn nhận email này vì được mời tham gia {{.Company}}
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
          </td>
        </tr>
      </table>
    </center>
  </body>
</html>
```

</details>

### 4.2 Staff Forgot Password

| | |
|---|---|
| **Const** | `constants.EmailTemplateCodeStaffForgotPass` |
| **template_code** | `TFLUENCER_EMAIL_STAFF_FORGOT_PASSWORD` |
| **remark** | Gui email dat lai mat khau |
| **HTML nguồn** | `staffForgotPasswordTemplate` (render qua `RenderForgotPasswordEmail`) |
| **Subject hiện tại** | `ForgotPasswordEmailSubject(company)` = `[{company}] Yêu cầu đặt lại mật khẩu` |

**template_data:**

| key | HTML placeholder | kiểu | mô tả |
|---|---|---|---|
| `recipientName` | `{{.RecipientName}}` | string | tên người nhận |
| `company` | `{{.Company}}` | string | tên công ty |
| `resetUrl` | `{{.ResetURL}}` | string | link đặt lại mật khẩu (CTA) |
| `expiryMinutes` | `{{.ExpiryMinutes}}` | int | số phút link hết hạn |
| `year` | `{{.Year}}` | string | năm (footer) |

Nội dung: xác nhận yêu cầu đặt lại mật khẩu. CTA "Đặt lại mật khẩu →". Ghi chú hết hạn sau `expiryMinutes` phút.

#### HTML hiện tại (`staffForgotPasswordTemplate` — staff_auth.go)

<details>
<summary>Xem HTML</summary>

```html
<!DOCTYPE html>
<html lang="vi" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{.Company}} - Đặt lại mật khẩu</title>
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      width: 100% !important;
      background-color: #f3f5f7;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <center style="width: 100%; background-color: #f3f5f7; padding: 24px 0">
      <table
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
        width="100%"
        style="
          max-width: 830px;
          background: #fff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        "
      >
        <!-- HEADER -->
        <tr>
          <td
            style="
              background-color: #0b0d0f;
              padding: 16px 20px;
              color: #fff;
              font-size: 14px;
            "
          >
            <table width="100%">
              <tr>
                <td align="left">
                  <img
                    src="https://media.tfluencer.vn/public/email_logo.png"
                    alt="Logo"
                    width="234"
                    height="32"
                    style="display: block;"
                  />
                </td>
                <td align="right">
                  <a
                    href="https://x.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_x.png"
                      alt="Twitter"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.facebook.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_f.png"
                      alt="Facebook"
                      width="20"
                      height="20"
                      style="display: block;"
                    />
                  </a>
                  <a
                    href="https://www.instagram.com/"
                    style="margin-left: 12px; display: inline-block"
                  >
                    <img
                      src="https://media.tfluencer.vn/public/email_ic_i.png"
                      alt="Instagram"
                      width="20"
                      height="20"
                      style="display: block"
                    />
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- HERO IMAGE -->
        <tr>
          <td>
            <img
              src="https://media.tfluencer.vn/public/email_banner.png"
              alt="TFluencers - Tạo trend hay, Lời đều tay"
              style="width: 97%; height: auto; display: block; padding: 10px;"
            />
          </td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td style="padding: 24px">
            <p
              style="
                margin: 0 0 20px;
                font-size: 24px;
                color: #181d27;
                font-weight: 700;
              "
            >
              Yêu cầu đặt lại mật khẩu
            </p>
            <p
              style="
                margin: 0 0 8px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Xin chào, <strong>{{.RecipientName}}</strong>
            </p>
            <p
              style="
                margin: 0 0 20px;
                font-size: 14px;
                color: #344054;
                line-height: 22px;
              "
            >
              Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn tại <strong>{{.Company}}</strong>.
              Nhấn vào nút bên dưới để đặt lại mật khẩu.
            </p>

            <table
              role="presentation"
              cellspacing="0"
              cellpadding="0"
              border="0"
            >
              <tr>
                <td>
                  <a
                    href="{{.ResetURL}}"
                    style="
                      display: inline-block;
                      background: #1570ef;
                      color: #fff;
                      font-size: 14px;
                      font-weight: 600;
                      padding: 12px 20px;
                      border-radius: 8px;
                      text-decoration: none;
                    "
                    >Đặt lại mật khẩu &#8594;</a
                  >
                </td>
              </tr>
            </table>

            <p
              style="
                margin: 20px 0 0;
                font-size: 12px;
                color: #667085;
                line-height: 20px;
              "
            >
              Nếu bạn không yêu cầu, hãy bỏ qua email này. Link hết hạn sau {{.ExpiryMinutes}} phút.
            </p>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td
            style="
              padding: 18px 24px 22px;
              text-align: center;
              font-size: 12px;
              color: #535862;
              border-top: 1px solid #98a2b3;
            "
          >
            Bạn nhận email này vì đã có tài khoản tại {{.Company}}
          <br>
          <span style="color:#9ca3af;font-size:12px;">© {{.Year}} {{.Company}}. All rights reserved.</span>
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

| template_code | Data keys | HTML nguồn | Có plainText |
|---|---|---|---|
| `TFLUENCER_EMAIL_OTP_VERIFICATION` | `code` | — | — |
| `TFLUENCER_EMAIL_BUDGET_75_PERCENT` | percent, eventName, eventCode, userName, year, company, linkEvent, linkHome, linkPolicy | `Budget75PercentTemplate` | ✅ |
| `TFLUENCER_EMAIL_BUDGET_95_PERCENT` | *(như trên)* | `Budget95PercentTemplate` | ✅ |
| `TFLUENCER_EMAIL_BUDGET_100_PERCENT` | *(như trên)* | `Budget100PercentTemplate` | ✅ |
| `TFLUENCER_EMAIL_BUDGET_THRESHOLD` | *(hiện dùng như trên — xem cảnh báo)* | `ThresholdTemplate` | ✅ |
| `TFLUENCER_EMAIL_USER_SOCIAL_APPROVED` | company, userName, year, linkAction, reason, status | `UserSocialApprovedTemplate` | ✅ |
| `TFLUENCER_EMAIL_USER_SOCIAL_REJECTED` | *(như trên)* | `UserSocialRejectedTemplate` | ✅ |
| `TFLUENCER_EMAIL_STAFF_INVITE` | recipientName, inviterName, company, acceptUrl, expiryHours, year | `staffInviteTemplate` | ❌ |
| `TFLUENCER_EMAIL_STAFF_FORGOT_PASSWORD` | recipientName, company, resetUrl, expiryMinutes, year | `staffForgotPasswordTemplate` | ❌ |

---

## Việc cần làm

1. **Tạo template thật trên gateway AccessTrade** cho từng `template_code` ở trên, dùng đúng bộ biến ở cột `template_data` key.
2. **Threshold có bộ field riêng**: nếu template threshold trên gateway dùng `threshold, currentSpend, percentUsed, detailsUrl, programName, recipientName, emailAddress` thay vì bộ budget chung, cần tách nhánh `pick(...)` riêng cho `EmailTemplateCodeBudgetThreshold` trong `buildEmailTemplateData` (`backend/internal/service/otp.go`).
3. **Wire call site**: hiện các luồng budget / user social / staff vẫn gửi qua SMTP (`internalsmtp.SendEmail`). Khi chuyển sang gateway, thay bằng `SendEmailAccessTrade` với `TemplateCode` + `Data` tương ứng.
4. **subject** cho email non-OTP hiện được sinh ở code Go; qua gateway subject thường thuộc về template — xác nhận subject đặt ở template hay truyền qua `template_data`.
