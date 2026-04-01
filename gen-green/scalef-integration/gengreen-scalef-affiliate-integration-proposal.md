# Phương án Tích hợp Scalef Affiliate vào Gen-Green

> **Tài liệu dành cho:** Team Gen-Green, Team Scalef, Ban quản lý dự án
> **Ngày:** 2026-03-31
> **Người soạn:** AccessTrade (đơn vị vận hành chung)
> **Trạng thái:** Đề xuất — chờ phản hồi từ các bên
> **Tham chiếu:** Mô hình [Ambassador ↔ Pub2](../pub2-affiliate-integration/prd-affiliate-integration-2026-03-25.md) (đã triển khai thành công)

---

## 1. Bối cảnh

### Mô hình đã thành công: Ambassador ↔ Pub2

Ambassador đã tích hợp hệ thống affiliate của Pub2 (AccessTrade), cho phép influencer:

1. Liên kết tài khoản AccessTrade (SSO, đã có sẵn)
2. Xem các chiến dịch affiliate gắn trong campaign
3. Tham gia chiến dịch (join) → hệ thống tạo hợp đồng
4. Tạo link affiliate → chia sẻ → thu commission khi có đơn hàng
5. Xem báo cáo hiệu suất (click, conversion, doanh số, hoa hồng)

**Bây giờ, áp dụng mô hình tương tự cho Gen-Green ↔ Scalef.**

### Điểm giống và khác

| | Ambassador ↔ Pub2 | Gen-Green ↔ Scalef |
|--|-------------------|---------------------|
| **Nền tảng chính** | Ambassador (influencer marketing) | Gen-Green (content creation) |
| **Nền tảng affiliate** | Pub2 (AccessTrade) | Scalef (nền tảng affiliate riêng của Vin) |
| **Số lượng user** | Vài nghìn influencer | ~150,000 creators |
| **User đã có trên affiliate?** | Một số đã có tài khoản AT | ~1,000 đã có tài khoản Scalef |
| **Liên kết tài khoản** | SSO OAuth2 với AccessTrade | Cần xây dựng (liên kết với Scalef) |
| **Ai vận hành chung** | AccessTrade | AccessTrade |
| **Thanh toán & thuế** | Riêng từng platform | Cần tổng hợp (cùng AccessTrade chi trả) |

### Vấn đề cần giải quyết

**Gen-Green có 150K creators đang kiếm tiền từ nội dung. Scalef là nền tảng affiliate của Vin. Nếu tích hợp Scalef vào Gen-Green, creator có thêm nguồn thu nhập thứ 2 — hoa hồng affiliate — mà không cần rời khỏi Gen-Green.**

Đồng thời, vì AccessTrade chi trả thu nhập và kê khai thuế TNCN cho cả 2 nền tảng, cần đảm bảo:
- Nhận diện đúng "cùng 1 người" giữa 2 hệ thống
- Tổng hợp thu nhập từ 2 nguồn để tính thuế chính xác

---

## 2. Tổng quan giải pháp

### Concept chính

> Chiến dịch affiliate (từ Scalef) được **gắn vào campaign/event trên Gen-Green**. Creator vào chi tiết campaign → thấy chiến dịch affiliate → tham gia → tạo link → chia sẻ → kiếm hoa hồng.

Giống hệt cách Ambassador làm với Pub2 — affiliate không đứng riêng lẻ, mà nằm trong ngữ cảnh campaign hiện tại.

### Luồng hoạt động tổng thể

```
                         ADMIN                                    CREATOR
                           │                                         │
              ┌────────────┴────────────┐               ┌───────────┴──────────┐
              ▼                         ▼               ▼                      ▼
     Tạo chiến dịch            Gắn chiến dịch     Liên kết tài          Vào chi tiết
     affiliate trên            affiliate vào       khoản Scalef          campaign
     Gen-Green Admin           campaign/event      (1 lần duy nhất)      trên Gen-Green
              │                         │               │                      │
              └────────────┬────────────┘               │                      │
                           ▼                            │                      ▼
                    Chiến dịch affiliate                 │            Thấy mục "Chiến dịch
                    hiển thị trong                       │            Affiliate" bên trong
                    campaign                             │                      │
                                                        │                      ▼
                                                        └──────────►  Tham gia chiến dịch
                                                                      (Join Campaign)
                                                                              │
                                                                              ▼
                                                                      Chờ duyệt / Được duyệt
                                                                              │
                                                                              ▼
                                                                      Tạo link affiliate
                                                                              │
                                                                              ▼
                                                                      Chia sẻ link
                                                                              │
                                                                              ▼
                                                                      Có người mua hàng
                                                                              │
                                                                              ▼
                                                                      Nhận hoa hồng
                                                                      + Xem báo cáo
```

---

## 3. Chi tiết từng bước

### 3.1. Liên kết tài khoản Scalef (1 lần duy nhất)

**Hiện tại:** Creator trên Gen-Green và publisher trên Scalef là 2 tài khoản riêng biệt.

**Sau tích hợp:** Creator cần liên kết tài khoản Scalef trước khi tham gia affiliate. Giống cách Ambassador yêu cầu liên kết tài khoản AccessTrade.

**Cách liên kết:**

| Bước | Mô tả |
|------|-------|
| 1 | Creator vào chiến dịch affiliate → thấy banner "Để tham gia, bạn cần liên kết tài khoản Scalef" |
| 2 | Bấm "Liên kết ngay" → chuyển sang trang xác thực Scalef |
| 3 | Đăng nhập / xác minh tài khoản Scalef |
| 4 | Hệ thống lưu liên kết: Gen-Green user ID ↔ Scalef user ID |
| 5 | Từ giờ, mọi thao tác affiliate đều dùng Scalef ID này |

**Nếu creator chưa có tài khoản Scalef:**
- Tạo tài khoản Scalef mới ngay trong luồng liên kết
- Thông tin từ Gen-Green (tên, SĐT, email) được điền sẵn → giảm bước nhập liệu

**Bảo mật:**
- Scalef ID được lưu ở backend Gen-Green, không gửi từ frontend (tránh giả mạo)
- Giống cách Ambassador inject `sso_user_id` từ backend khi gọi Pub2

### 3.2. Xử lý user hiện có (~1,000 user Scalef)

Trước khi go-live, cần khớp 1,000 user Scalef hiện tại với user Gen-Green tương ứng:

| Tình huống | Cách xử lý |
|-----------|-----------|
| Creator Gen-Green đã có tài khoản Scalef | Tự động liên kết (khớp qua CCCD hoặc SĐT) |
| Publisher Scalef chưa có trên Gen-Green | Tạo tài khoản Gen-Green hoặc chờ user tự liên kết |
| Không khớp được tự động | Chuyển admin xem xét |

**Chiến lược:** Lấy 1,000 user Scalef dò trong 150,000 user Gen-Green (bên ít khớp vào bên nhiều). Ưu tiên khớp bằng CCCD/Mã số thuế (chính xác nhất), sau đó SĐT, cuối cùng email.

### 3.3. Admin tạo và quản lý chiến dịch affiliate

Admin Gen-Green tạo chiến dịch affiliate trên Admin panel, rồi gắn vào campaign/event hiện tại.

**Tạo chiến dịch:**

| Thông tin | Mô tả |
|----------|-------|
| Tên chiến dịch | Tiêu đề hiển thị cho creator |
| Mô tả | Chi tiết chương trình, thể lệ, hướng dẫn |
| Banner | Ảnh đại diện chiến dịch |
| Hoa hồng | Mức commission (ví dụ: "100.000đ/đơn hàng") |
| Thưởng thêm | Bonus nếu có (ví dụ: "+1.000.000đ khi đạt 50 đơn") |
| Thời gian | Ngày bắt đầu — kết thúc |
| Scalef Campaign ID | Liên kết với chiến dịch trên hệ thống Scalef |
| Trạng thái | Bật / Tắt (mặc định: Tắt khi mới tạo) |

**Gắn vào campaign/event:**
- 1 chiến dịch affiliate có thể gắn vào nhiều campaign/event
- 1 campaign/event có thể có nhiều chiến dịch affiliate
- Chỉ gắn được campaign/event cùng đối tác (partner)

### 3.4. Creator tham gia chiến dịch (Join Campaign)

Trước khi tạo link, creator phải tham gia (join) chiến dịch. Backend Gen-Green gọi Scalef API để tạo hợp đồng.

**Luồng:**

```
Creator bấm "Tham gia chiến dịch"
       ↓
Backend Gen-Green gọi Scalef API (Join Campaign)
       ↓
Scalef trả về trạng thái hợp đồng:
       ↓
   ┌──────────────────────────────────────────┐
   │ "Đang chờ duyệt"  → Chưa tạo link được │
   │ "Đã được duyệt"   → Có thể tạo link    │
   │ "Bị từ chối"       → Không tham gia được │
   └──────────────────────────────────────────┘
```

### 3.5. Creator tạo link affiliate

Sau khi được duyệt, creator tạo link affiliate cho chiến dịch. Backend Gen-Green gọi Scalef API tạo link.

| Bước | Mô tả |
|------|-------|
| 1 | Creator bấm "Tạo link affiliate" |
| 2 | Backend gọi Scalef API với Scalef user ID (inject từ backend) |
| 3 | Nhận link dài + link rút gọn |
| 4 | Hiển thị link, nút copy, nút chia sẻ |
| 5 | Link được lưu lại trên Gen-Green để xem lại |

**Tracking:** Mỗi link chứa thông tin:
- `sub1`: Scalef user ID (nhận diện creator)
- `sub2`: "gengreen" (nhận diện platform, tách biệt với Ambassador dùng "ambassador")

### 3.6. Creator xem báo cáo

Creator xem hiệu suất affiliate ngay trong Gen-Green:

| Báo cáo | Nội dung |
|---------|---------|
| Lượt click | Số người bấm vào link, theo ngày |
| Đơn hàng (Conversion) | Số đơn hàng phát sinh từ link |
| Doanh số | Tổng giá trị đơn hàng |
| Hoa hồng | Tổng commission kiếm được |
| Chi tiết đơn | Danh sách từng đơn hàng, trạng thái, giá trị |

Backend Gen-Green proxy gọi Scalef API khi creator xem báo cáo (dữ liệu realtime từ Scalef, không cache).

---

## 4. Thanh toán & Thuế TNCN

### Vấn đề

Một creator có thể nhận thu nhập từ 2 nguồn:

| Nguồn | Loại thu nhập | Ví dụ |
|-------|-------------|-------|
| Gen-Green | Thanh toán nội dung | 5 triệu/tháng |
| Scalef | Hoa hồng affiliate | 3 triệu/tháng |
| **Tổng** | | **8 triệu/tháng** |

AccessTrade kê khai thuế TNCN hộ creator ở **cả 2 nền tảng**. Nếu tính thuế riêng từng nguồn → có thể áp sai bậc thuế → rủi ro pháp lý. **Phải tổng hợp thu nhập trước, tính thuế sau.**

### Giải pháp

```
Thu nhập Gen-Green ──┐
                      ├──→  Tổng hợp  ──→  Tính thuế  ──→  Thanh toán
Thu nhập Scalef  ────┘    (theo CCCD/     (theo bậc       (1 lần/tháng
                           Mã số thuế)    luật định)      đã trừ thuế)
```

**Cách nhận diện "cùng 1 người":** Dựa trên CCCD / Mã số thuế — thông tin pháp lý mà AccessTrade đã có (vì cần cho kê khai thuế). Đây là lý do cần liên kết tài khoản Gen-Green ↔ Scalef.

**Lợi ích cho creator:**
- 1 lần thanh toán gộp thay vì 2 lần riêng
- 1 bảng kê thuế chính xác
- Không cần tự tổng hợp thu nhập

### Thiết kế linh hoạt cho tương lai

Hệ thống thanh toán và kê khai thuế được thiết kế theo kiểu module:

| Thành phần | Ai sở hữu | Thay đổi được? |
|-----------|-----------|---------------|
| Dữ liệu user (CCCD, MST, bank) | Vin | Không — luôn thuộc Vin |
| Liên kết user Gen-Green ↔ Scalef | Vin platform | Không — độc lập với đơn vị vận hành |
| Logic tính thuế | Tách riêng | Không — ai vận hành cũng dùng được |
| Module thanh toán | Thay đổi được | **Có** — hiện tại: AT, sau có thể đổi |
| Module kê khai thuế | Thay đổi được | **Có** — cần pháp nhân kê khai |

Nếu sau này Vin tự vận hành thanh toán hoặc đổi đơn vị — chỉ cần thay module thanh toán, không ảnh hưởng đến tích hợp affiliate hay liên kết user.

---

## 5. Kiến trúc tổng thể (dành cho cả 3 team)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     Scalef (Affiliate Platform)             │
│                     ───────────────────────                 │
│                     API Join Campaign                       │
│                     API Tạo Link                            │
│                     API Báo cáo (click, đơn, hoa hồng)     │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    Scalef API (có xác thực)
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                                                             │
│                Gen-Green Backend (Go)                        │
│                ──────────────────────                        │
│                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│   │ Scalef       │  │ Affiliate    │  │ Liên kết user    │ │
│   │ API Client   │  │ Service      │  │ Gen-Green ↔      │ │
│   │ (gọi Scalef) │  │ (business    │  │ Scalef           │ │
│   │              │  │  logic)      │  │                  │ │
│   └──────────────┘  └──────────────┘  └──────────────────┘ │
│                                                             │
│   ┌────────────────────────────────────────────────────┐    │
│   │                    MongoDB                          │    │
│   │  affiliate_campaigns │ affiliate_contracts          │    │
│   │  affiliate_links     │ campaign_affiliate_mappings  │    │
│   └────────────────────────────────────────────────────┘    │
│                                                             │
└────────────┬───────────────────────────────┬────────────────┘
             │                               │
      REST API                        REST API
             │                               │
┌────────────┴────────────┐    ┌─────────────┴──────────────┐
│  Gen-Green Frontend     │    │  Gen-Green Admin            │
│  (Creator)              │    │  (Quản trị viên)            │
│                         │    │                             │
│  - Xem affiliate trong  │    │  - Tạo chiến dịch affiliate│
│    chi tiết campaign    │    │  - Gắn vào campaign/event  │
│  - Liên kết Scalef     │    │  - Quản lý danh sách       │
│  - Tham gia chiến dịch  │    │  - Xem trạng thái         │
│  - Tạo & copy link     │    │                             │
│  - Xem báo cáo         │    │                             │
└─────────────────────────┘    └─────────────────────────────┘
```

**Điểm quan trọng:**
- Gen-Green Backend đóng vai trò **trung gian** — creator không gọi trực tiếp Scalef
- Scalef user ID được inject từ backend, không gửi từ frontend (bảo mật)
- 4 bảng dữ liệu mới trên Gen-Green, không sửa dữ liệu hiện tại

---

## 6. Yêu cầu phối hợp từ các bên

### Team Gen-Green cần làm

| # | Hạng mục | Mô tả |
|---|---------|-------|
| G1 | Xây dựng Scalef API Client | Module gọi Scalef API (join, tạo link, báo cáo) có xác thực |
| G2 | Affiliate Service | Logic quản lý chiến dịch, hợp đồng, link, báo cáo |
| G3 | Liên kết tài khoản Scalef | Luồng liên kết Gen-Green user ↔ Scalef user |
| G4 | Frontend — Section affiliate | Hiển thị chiến dịch affiliate trong chi tiết campaign |
| G5 | Frontend — Tạo link & báo cáo | UI tạo link, copy, xem báo cáo |
| G6 | Admin — Quản lý chiến dịch | CRUD chiến dịch affiliate, gắn vào campaign/event |
| G7 | 4 bảng MongoDB mới | affiliate_campaigns, affiliate_contracts, affiliate_links, campaign_affiliate_mappings |

### Team Scalef cần cung cấp

| # | Hạng mục | Mô tả |
|---|---------|-------|
| S1 | API specs | Tài liệu API cho: join campaign, tạo link, báo cáo (click, conversion, doanh số, hoa hồng, chi tiết đơn) |
| S2 | Xác thực API | Cơ chế xác thực (HMAC, API key, OAuth?) + credentials cho Gen-Green |
| S3 | Danh sách user hiện có | Export 1,000 user (CCCD, SĐT, email) để chạy khớp ban đầu |
| S4 | Luồng liên kết tài khoản | API hoặc SSO để Gen-Green user liên kết/tạo tài khoản Scalef |
| S5 | Sandbox / Staging | Môi trường test để Gen-Green phát triển và kiểm thử |
| S6 | Error codes | Danh sách mã lỗi và cách xử lý |

### AccessTrade (quản lý chung) cần phối hợp

| # | Hạng mục | Mô tả |
|---|---------|-------|
| A1 | Chạy khớp user ban đầu | Khớp 1,000 Scalef user với 150K Gen-Green user |
| A2 | Tổng hợp thuế TNCN | Gộp thu nhập Gen-Green + Scalef theo MST/CCCD |
| A3 | Thanh toán hợp nhất | 1 chu kỳ thanh toán, 1 bảng kê cho creator |
| A4 | Theo dõi & đối soát | Kiểm tra liên kết user, đối soát thu nhập hàng tháng |

---

## 7. Phương án triển khai — 3 giai đoạn

### Giai đoạn 1: Nền tảng (Tuần 1–2)

**Mục tiêu:** Xây dựng cơ sở hạ tầng tích hợp, khớp user hiện có.

| Việc cần làm | Team |
|-------------|------|
| Scalef cung cấp API specs + sandbox | Scalef |
| Gen-Green xây Scalef API Client | Gen-Green |
| Gen-Green xây luồng liên kết tài khoản Scalef | Gen-Green |
| Gen-Green tạo 4 bảng MongoDB mới | Gen-Green |
| AccessTrade khớp 1,000 user Scalef ↔ Gen-Green | AccessTrade |
| Kiểm tra khớp user, xử lý ngoại lệ | Cả 3 team |

### Giai đoạn 2: Tính năng chính (Tuần 3–4)

**Mục tiêu:** Creator có thể tham gia chiến dịch affiliate, tạo link, xem báo cáo.

| Việc cần làm | Team |
|-------------|------|
| Admin: Tạo & quản lý chiến dịch affiliate | Gen-Green |
| Admin: Gắn chiến dịch affiliate vào campaign/event | Gen-Green |
| Frontend: Hiển thị affiliate trong chi tiết campaign | Gen-Green |
| Frontend: Tham gia chiến dịch (join) | Gen-Green |
| Frontend: Tạo link + copy + chia sẻ | Gen-Green |
| Frontend: Xem báo cáo (click, đơn, hoa hồng) | Gen-Green |
| Test end-to-end trên staging | Cả 3 team |

### Giai đoạn 3: Vận hành & tối ưu (Liên tục)

| Việc cần làm | Team |
|-------------|------|
| Go-live, theo dõi lỗi | Cả 3 team |
| Tổng hợp thu nhập + thanh toán hợp nhất | AccessTrade |
| Đối soát hàng ngày/tháng | AccessTrade |
| Tối ưu UX dựa trên phản hồi creator | Gen-Green |
| Mở rộng chiến dịch mới trên Scalef | Scalef |

```
Tuần 1–2                Tuần 3–4                  Liên tục
   │                       │                         │
   ▼                       ▼                         ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  GIAI ĐOẠN 1     │  │  GIAI ĐOẠN 2     │  │  GIAI ĐOẠN 3     │
│  Nền tảng        │  │  Tính năng chính │  │  Vận hành        │
│                  │  │                  │  │                  │
│ - API Client     │  │ - Admin CRUD     │  │ - Go-live        │
│ - Liên kết user  │  │ - Join campaign  │  │ - Thanh toán     │
│ - Khớp 1K user   │  │ - Tạo link       │  │   tổng hợp       │
│ - DB mới         │  │ - Báo cáo        │  │ - Đối soát       │
│                  │  │ - Test E2E       │  │ - Tối ưu         │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 8. Lợi ích cho từng bên

### Cho Creator (150K users tiềm năng)

| Trước | Sau |
|-------|-----|
| Chỉ kiếm tiền từ nội dung | Thêm nguồn thu từ hoa hồng affiliate |
| Muốn làm affiliate phải đăng ký platform khác | Tham gia ngay trong Gen-Green |
| 2 bảng kê thuế nếu làm cả 2 | 1 bảng kê tổng hợp, đúng bậc |
| 2 lần thanh toán riêng | 1 lần thanh toán gộp |

### Cho Team Gen-Green

| Trước | Sau |
|-------|-----|
| Creator chỉ có 1 lý do ở lại (content) | Thêm affiliate = thêm lý do gắn bó |
| Không có affiliate feature | Có sẵn mô hình (copy từ Ambassador-Pub2) |
| Không biết creator nào làm affiliate | Thấy toàn bộ hoạt động affiliate |

### Cho Team Scalef

| Trước | Sau |
|-------|-----|
| Chỉ 1,000 publishers | Tiếp cận 150K creators tiềm năng |
| Phải tự thu hút publisher | Gen-Green giới thiệu affiliate cho creator |
| Publisher đăng ký rời rạc | Tự động liên kết, điền sẵn thông tin |

### Cho Ban quản lý / AccessTrade

| Trước | Sau |
|-------|-----|
| Kê khai thuế riêng → rủi ro sai bậc | Tổng hợp → đúng luật |
| 2 hệ thống thanh toán | 1 chu kỳ, giảm chi phí |
| Creator income = content only | Creator income = content + affiliate (tăng giá trị platform) |

---

## 9. Rủi ro và biện pháp

| # | Rủi ro | Mức độ | Biện pháp |
|---|--------|--------|-----------|
| 1 | Scalef API chưa sẵn sàng hoặc thiếu tài liệu | Cao | Yêu cầu API specs + sandbox sớm nhất (điều kiện tiên quyết) |
| 2 | Khớp sai user giữa 2 hệ thống | Trung bình | Ưu tiên khớp bằng CCCD/MST, có cơ chế gỡ liên kết |
| 3 | Creator chưa muốn tham gia affiliate | Thấp | Không ép buộc — affiliate là tính năng tùy chọn |
| 4 | Tính thuế sai trong giai đoạn chuyển đổi | Cao | Chạy thử nghiệm thuế trước go-live |
| 5 | Scalef API thay đổi sau go-live | Trung bình | Scalef Client module tách biệt, dễ cập nhật |
| 6 | Thay đổi đơn vị vận hành thanh toán | Trung bình | Thiết kế module, dữ liệu thuộc Vin |

---

## 10. Câu hỏi cần các team trả lời

### Cho Team Scalef

1. Scalef API specs đã có sẵn chưa? Gồm những API nào? Xác thực bằng gì?
2. Có sandbox/staging để Gen-Green phát triển và test không?
3. Luồng liên kết tài khoản: SSO, OAuth, hay API đăng ký trực tiếp?
4. Danh sách error codes khi join campaign, tạo link?
5. Có plan mở rộng API nào trong thời gian tới không (tránh breaking changes)?

### Cho Team Gen-Green

1. Campaign/event model hiện tại có trường nào cần bổ sung?
2. Có sẵn module HTTP client nào tái sử dụng được (retry, timeout, circuit breaker)?
3. Timeline dev team available để bắt đầu Phase 1?

### Cho Ban quản lý

1. Xác nhận: AccessTrade vẫn là đơn vị chi trả và kê khai thuế cho cả Gen-Green + Scalef?
2. Chu kỳ thanh toán hiện tại của 2 nền tảng có giống nhau không (cùng ngày/tháng)?
3. Có cần báo cáo tổng hợp cross-platform cho management không?

---

## 11. Bước tiếp theo

1. **Scalef cung cấp API specs** — đây là điều kiện tiên quyết, không có thì không bắt đầu được
2. **3 team review tài liệu này** — phản hồi trong 1 tuần
3. **Họp alignment** — thống nhất API specs, timeline, phân công
4. **AccessTrade soạn tài liệu kỹ thuật chi tiết** (PRD + Architecture) sau khi có API specs từ Scalef

---

*Tài liệu tham chiếu: [PRD Ambassador-Pub2 Affiliate Integration](../pub2-affiliate-integration/prd-affiliate-integration-2026-03-25.md) | [Architecture Ambassador-Pub2](../pub2-affiliate-integration/architecture-affiliate-integration-2026-03-25.md)*
*Tổng hợp từ phiên brainstorming ngày 2026-03-31*
