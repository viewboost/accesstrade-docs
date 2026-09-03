# ĐỀ XUẤT DỰ ÁN — Booking KOC trên nền CreatorOS

**Diso × AccessTrade** · Bản đề xuất v2 · 2026-07

> ⚠️ Tài liệu có báo giá — **chỉ chia sẻ nội bộ AT + Diso**. Không đăng công khai.

---

## 1. Giới thiệu dự án

### 1.1. Bối cảnh
AccessTrade đang mở rộng sang mô hình **Booking KOC** (đặt KOC theo giá/gói, duyệt nội dung trước khi đăng). Đây là nghiệp vụ phức tạp hơn content-campaign hiện tại — đặc biệt ở **giá per-KOC, đối soát tiền, và duyệt-trước-đăng** — đòi hỏi một nền tài chính vững.

### 1.2. Đề xuất
Diso đề xuất triển khai **Booking trên CreatorOS** — nền tảng creator-marketing Diso đã phát triển và vận hành thật, với **sổ cái đối soát khép kín, cách ly dữ liệu tầng hạ tầng, và kiểm thử tự động** — theo **mô hình THUÊ NỀN** (không chuyển giao source).

Booking chạy như **một hệ mới độc lập** (sân mới), **không ảnh hưởng Ambassador đang chạy**.

> **Phạm vi đề xuất này = Booking.** Ambassador hiện hành tiếp tục theo **hợp đồng riêng (giữ nguyên)**. Việc migrate Ambassador sang CreatorOS là **định hướng tương lai, thoả thuận giá riêng** khi hai bên sẵn sàng (§2.4).

### 1.3. Nguyên tắc
- **Tích hợp thẳng vào hạ tầng AccessTrade** — Core/eKYC, SSO, at-core, Content Catcher (crawl), multichannel (SMS/Zalo/email), API giải ngân — qua lớp adapter, không thay thế.
- **Không rủi ro**: Booking là greenfield; AccessTrade đo kết quả thật trước khi mở rộng.
- **Quý công ty giữ quyền kiểm soát**: sở hữu deployment + dữ liệu; source đặt escrow đảm bảo không phụ thuộc.

---

## 2. Phạm vi chức năng

### 2.1. Nền tảng (có sẵn — dùng ngay)
| Nhóm | Chức năng |
|---|---|
| Đa-tenant & bảo mật | Cách ly dữ liệu từng ADV ở **tầng cơ sở dữ liệu** · RBAC · nhật ký kiểm toán bất biến |
| Xương tiền | **Sổ cái 2-vế khép kín** (đối soát khớp by-construction) · ngân sách 3-tầng · giữ/chi 2-pha · thu hồi/clawback |
| Chất lượng | **1.184 kiểm thử tự động** (~2 phút) · 15 "chốt kiến trúc" máy tự canh → sửa không tái phát bug |
| Vận hành | Hàng đợi/worker nền · thông báo đa kênh · xuất báo cáo/đối soát |

### 2.2. Booking (chức năng chính)
| Chức năng | Mô tả |
|---|---|
| Marketplace tự-đăng-ký | Creator xem job → **apply theo từng kênh** → duyệt hồ sơ theo SLA |
| **Duyệt trước khi đăng (pre-publish)** | Nộp demo → duyệt kịch bản/nội dung → mới cho đăng bài |
| Giá & thanh toán | Đồng-giá + **đàm phán/final-giá per-KOC** · chi per-video hoặc theo gói · phí phụ |
| Nghiệm thu & chi tiền | Duyệt nội dung/thời gian/số lượng → chi tiền, **đối soát khớp** |
| Hợp đồng điện tử | E-contract per-job, gate eKYC |
| Trao đổi | Creator ↔ người duyệt **trên hệ thống** (thay Zalo), có lịch sử |

### 2.3. Tích hợp dịch vụ AccessTrade & bên thứ ba (khối việc chính của khởi tạo)
Đã đối chiếu source Ambassador. Một phần lớn công việc khởi tạo là **nối CreatorOS vào các dịch vụ sẵn có** — dùng lại, không thay thế:

**Dịch vụ nền tảng AccessTrade** (ký HMAC):
| Dịch vụ | Vai trò |
|---|---|
| **AccessTrade Core** (econtract) | Cổng eKYC + ký hợp đồng điện tử |
| **FPT.ai** | Định danh/OCR CCCD + **chữ ký điện tử hợp đồng** (qua Core/Identification của AT) |
| **AccessTrade SSO** | Liên kết tài khoản publisher AccessTrade |
| **at-core** | Làm giàu hồ sơ + metrics + chấm điểm creator (kèm webhook) |
| **Content Catcher** | Crawl bài đăng: Facebook/Instagram/TikTok/YouTube/Threads/Shopee |
| **Multichannel gateway** | SMS + Zalo ZNS + email/OTP |
| **API Giải ngân (payout)** | Chi tiền tự động cho creator qua hạ tầng giải ngân của AccessTrade |

**Đăng nhập:** email/password + **social OAuth (Google/TikTok/Facebook/Instagram)** — SSO AccessTrade dùng để liên kết.
**Bên thứ ba:** MinIO/S3 (lưu trữ) · Firebase (push) · AWS SES (email) · Google Drive (backup) · Telegram (cảnh báo vận hành).
**Ngoài phạm vi:** Pub2 Affiliate — AccessTrade đã có **scaleF** *(có thể bổ sung nếu Quý công ty yêu cầu)*.

> Kiến trúc CreatorOS theo **adapter/cổng cắm** — mỗi dịch vụ là một adapter riêng, không đụng lõi. Đây là lý do nhúng nhanh và không rủi ro tới phần nghiệp vụ.

### 2.4. Migrate Ambassador — định hướng tương lai (deal riêng)
**Không nằm trong phạm vi & báo giá đề xuất này.** Khi Booking chạy ổn định, hai bên có thể bàn riêng việc chuyển Ambassador sang CreatorOS (ADV mới lên trước, migrate dần các tenant, giữ pool KOC thống nhất qua SSO chung).

### 2.5. Ngoài phạm vi (giai đoạn sau)
- Agency/Vendor (quản lý pool, khoán quota, hoa hồng, phạt vi phạm)
- Brand Portal (ADV tự thao tác)

---

## 3. Mô hình triển khai

```
Khởi động ──► Tích hợp dịch vụ AT + dựng nền ──► Booking go-live ──► Vận hành
              (sân mới — KHÔNG đụng Ambassador đang chạy)
```

- Booking là **greenfield** — hỏng cũng không ảnh hưởng hệ đang chạy.
- Migrate Ambassador: định hướng tương lai, deal riêng (§2.4).

---

## 4. Báo giá

### 4.1. Phí duy trì

| Hạng mục | Mức / tháng |
|---|---|
| Vận hành + bảo trì + nâng cấp nền Booking | **50.000.000đ / tháng** |

> Bao gồm: vận hành, **bảo trì (fix tận gốc — mô hình thuê, không đếm task)**, cập nhật tính năng nền, hỗ trợ theo SLA. Hạn mức cụ thể (số tenant, số yêu cầu thay đổi/tháng) chốt trong phụ lục hợp đồng.

### 4.2. Phí khởi tạo (một lần)
Bao gồm **tích hợp toàn bộ dịch vụ AccessTrade** (Core/eKYC · SSO · at-core · Content Catcher · SMS/Zalo · API giải ngân) + dựng nền Booking + go-live.

| Phương án | Phí khởi tạo |
|---|---|
| Tiêu chuẩn (thanh toán theo mốc: khởi động → go-live) | **500.000.000đ** |
| **Cam kết sử dụng ≥ 12 tháng** | **200.000.000đ** *(ưu đãi)* |

> Cam kết dài hạn được ưu đãi phí khởi tạo — Diso đồng hành đường dài, chi phí đầu tư ban đầu chia sẻ qua thời gian vận hành.

### 4.3. Ngoài phạm vi báo giá này
- **Ambassador** — tiếp tục theo **hợp đồng hiện hành (130.000.000đ/tháng, giữ nguyên)**.
- **Migrate Ambassador → CreatorOS** — thoả thuận giá riêng khi triển khai.

---

## 5. Cam kết & điều khoản

| Khoản | Cam kết |
|---|---|
| **Sở hữu & không khoá** | AccessTrade giữ **deployment + toàn bộ dữ liệu**; **source đặt escrow** (bên thứ 3) — nếu Diso ngừng vận hành, AT được quyền tiếp quản; core SSO/eKYC/payout **vẫn thuộc AT** |
| **Bảo trì** | Mô hình thuê → Diso được trả để **nền chạy tốt**, nên **fix dứt điểm**, chủ động cải tiến (không phải đếm task) |
| **SLA** | Thời gian phản hồi/khắc phục theo cấp độ sự cố — chi tiết phụ lục |
| **Bảo mật dữ liệu** | Tuân thủ NĐ13; cách ly dữ liệu từng ADV ở tầng hạ tầng |
| **Timeline** | Đề xuất chi tiết sau khi chốt phạm vi Booking |

---

## 6. Bước tiếp theo

1. **Demo đối soát** trên chính dữ liệu của AccessTrade — chứng minh khớp.
2. Chốt **phạm vi + timeline Booking** + phương án phí khởi tạo (500tr / 200tr-cam-kết-1-năm).
3. Thống nhất **hạn mức SLA + điều khoản hợp đồng** (phụ lục).
4. Ký thoả thuận → khởi động.

---

*Diso × AccessTrade — Đề xuất Booking trên CreatorOS · 2026-07 · Bản v2 (nháp).*
*Liên hệ: [điền].*
