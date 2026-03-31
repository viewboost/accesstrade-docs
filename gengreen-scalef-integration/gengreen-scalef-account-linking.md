# Phương án Liên kết Tài khoản Gen-Green ↔ Scalef

> **Tài liệu dành cho:** Team Gen-Green, Team Scalef, Ban quản lý dự án
> **Ngày:** 2026-03-31
> **Người soạn:** AccessTrade (đơn vị vận hành chung)
> **Trạng thái:** Đề xuất — chờ phản hồi từ các bên
> **Liên quan:** [Phương án tích hợp Scalef Affiliate vào Gen-Green](./gengreen-scalef-affiliate-integration-proposal.md)
> **Tham chiếu:** [Ambassador ↔ Pub2 (mô hình gốc)](../pub2-affiliate-integration/prd-affiliate-integration-2026-03-25.md)

---

## 1. Tại sao cần liên kết tài khoản?

Gen-Green (nền tảng nội dung, ~150K creators) và Scalef (nền tảng affiliate, ~1,000 publishers) là 2 hệ thống riêng biệt, mỗi bên có hệ thống user riêng.

Để creator trên Gen-Green có thể tham gia chiến dịch affiliate trên Scalef (và ngược lại), hệ thống cần biết **"tài khoản Gen-Green này tương ứng với tài khoản Scalef nào"**.

Ngoài ra, vì AccessTrade chi trả thu nhập và kê khai thuế TNCN cho cả 2 nền tảng, liên kết tài khoản còn giúp:
- Tổng hợp thu nhập từ 2 nguồn cho cùng 1 người
- Tính thuế TNCN chính xác theo tổng thu nhập
- 1 lần thanh toán, 1 bảng kê thuế

---

## 2. Tổng quan các hình thức liên kết

Có **3 hình thức** để liên kết tài khoản giữa 2 nền tảng, phục vụ các nhóm user khác nhau:

| Hình thức | Dành cho ai | Mô tả |
|----------|------------|-------|
| **A. Liên kết thủ công** | User đã có tài khoản cả 2 bên | User chủ động liên kết 2 tài khoản hiện có |
| **B. Đăng nhập bằng tài khoản bên kia** | User mới muốn đăng ký nhanh | Dùng tài khoản Gen-Green để đăng nhập Scalef, hoặc ngược lại |
| **C. Khớp tự động (batch)** | 1,000 user Scalef hiện có | Hệ thống tự khớp user 2 bên dựa trên CCCD/SĐT (chạy 1 lần trước go-live) |

```
┌─────────────────────────────────────────────────────────────┐
│              3 hình thức liên kết tài khoản                 │
│                                                             │
│  ┌─────────────────┐ ┌──────────────────┐ ┌─────────────┐  │
│  │  A. Liên kết    │ │  B. Đăng nhập    │ │ C. Khớp     │  │
│  │  thủ công       │ │  bằng tài khoản  │ │ tự động     │  │
│  │                 │ │  bên kia         │ │ (batch)     │  │
│  │  User đã có     │ │                  │ │             │  │
│  │  cả 2 tài khoản │ │  User mới        │ │ 1,000 user  │  │
│  │                 │ │  đăng ký nhanh   │ │ Scalef      │  │
│  │  → Xác minh     │ │                  │ │ hiện có     │  │
│  │  → Liên kết     │ │  → Tạo tài khoản │ │             │  │
│  │                 │ │    tự động       │ │ → Chạy 1    │  │
│  │                 │ │  → Liên kết ngay │ │   lần       │  │
│  └─────────────────┘ └──────────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Hình thức A — Liên kết thủ công

### Dành cho ai?

User đã có tài khoản trên cả Gen-Green và Scalef, muốn liên kết 2 tài khoản lại.

### Luồng: Từ Gen-Green liên kết sang Scalef

```
Creator đang trên Gen-Green
       │
       ▼
Vào mục "Tài khoản liên kết" hoặc bấm "Liên kết Scalef" khi xem chiến dịch affiliate
       │
       ▼
Chuyển sang trang đăng nhập Scalef (OAuth / SSO)
       │
       ▼
Đăng nhập tài khoản Scalef hiện có
       │
       ▼
Scalef xác nhận → trả về Scalef User ID
       │
       ▼
Gen-Green lưu liên kết: Gen-Green User ID ↔ Scalef User ID
       │
       ▼
Thông báo: "Liên kết thành công"
```

### Luồng: Từ Scalef liên kết sang Gen-Green

```
Publisher đang trên Scalef
       │
       ▼
Vào mục "Tài khoản liên kết" → bấm "Liên kết Gen-Green"
       │
       ▼
Chuyển sang trang đăng nhập Gen-Green (OAuth / SSO)
       │
       ▼
Đăng nhập tài khoản Gen-Green hiện có
       │
       ▼
Gen-Green xác nhận → trả về Gen-Green User ID
       │
       ▼
Scalef lưu liên kết: Scalef User ID ↔ Gen-Green User ID
       │
       ▼
Thông báo: "Liên kết thành công"
```

### Điểm chạm (touchpoint) trên Gen-Green

Giống Ambassador — nhắc creator liên kết tại các điểm tự nhiên:

| Vị trí | Cách hiển thị |
|--------|--------------|
| Trang chi tiết campaign (có affiliate) | Banner: "Để tham gia affiliate, hãy liên kết tài khoản Scalef" + nút "Liên kết ngay" |
| Khi bấm "Tham gia chiến dịch" mà chưa liên kết | Popup: "Bạn cần liên kết tài khoản Scalef trước" + nút "Liên kết ngay" |
| Trang cài đặt tài khoản | Mục "Tài khoản liên kết" — hiển thị trạng thái liên kết Scalef |

### Quy tắc

- **1 tài khoản Gen-Green chỉ liên kết với 1 tài khoản Scalef** (và ngược lại)
- Nếu tài khoản Scalef đã liên kết với Gen-Green user khác → từ chối, thông báo lỗi
- Liên kết có thể gỡ bởi admin (khi bị nhầm)
- Mọi liên kết/gỡ liên kết đều ghi lại lịch sử (ai, lúc nào, bằng cách nào)

---

## 4. Hình thức B — Đăng nhập bằng tài khoản bên kia

### Tại sao cần?

Khi một user mới đến Scalef hoặc Gen-Green, thay vì phải tạo tài khoản mới + điền lại thông tin + liên kết thủ công, có thể **đăng nhập thẳng bằng tài khoản bên kia** — vừa tạo tài khoản vừa liên kết trong 1 bước.

Giống cách nhiều app cho phép "Đăng nhập bằng Google" hoặc "Đăng nhập bằng Facebook" — ở đây là "Đăng nhập bằng Gen-Green" hoặc "Đăng nhập bằng Scalef".

### Luồng B1: Đăng nhập Scalef bằng tài khoản Gen-Green

Dành cho creator Gen-Green muốn bắt đầu làm affiliate trên Scalef.

```
User mới vào Scalef
       │
       ▼
Trang đăng nhập Scalef hiển thị:
  ┌────────────────────────────────┐
  │  Đăng nhập Scalef             │
  │                                │
  │  [Email/SĐT]  [Mật khẩu]     │
  │  [Đăng nhập]                   │
  │                                │
  │  ─── hoặc ───                  │
  │                                │
  │  [Đăng nhập bằng Gen-Green]   │
  └────────────────────────────────┘
       │
       ▼ (bấm "Đăng nhập bằng Gen-Green")
       │
Chuyển sang trang xác thực Gen-Green
       │
       ▼
Đăng nhập Gen-Green (nếu chưa đăng nhập)
       │
       ▼
Gen-Green hỏi: "Cho phép Scalef truy cập thông tin của bạn?"
       │
       ▼ (Đồng ý)
       │
Scalef nhận thông tin từ Gen-Green:
  - Tên, SĐT, email, ảnh đại diện
  - Gen-Green User ID (để liên kết)
       │
       ▼
   ┌───────────────────────────────────────────────┐
   │ Đã có tài khoản Scalef khớp SĐT/email?       │
   │                                               │
   │ CÓ → Đăng nhập tài khoản đó + liên kết       │
   │ KHÔNG → Tạo tài khoản Scalef mới + liên kết  │
   └───────────────────────────────────────────────┘
       │
       ▼
Vào Scalef, tài khoản đã liên kết Gen-Green
```

### Luồng B2: Đăng nhập Gen-Green bằng tài khoản Scalef

Dành cho publisher Scalef muốn bắt đầu tạo nội dung trên Gen-Green.

```
User mới vào Gen-Green
       │
       ▼
Trang đăng nhập Gen-Green hiển thị:
  ┌────────────────────────────────┐
  │  Đăng nhập Gen-Green          │
  │                                │
  │  [Email/SĐT]  [Mật khẩu]     │
  │  [Đăng nhập]                   │
  │                                │
  │  ─── hoặc ───                  │
  │                                │
  │  [Đăng nhập bằng Scalef]      │
  └────────────────────────────────┘
       │
       ▼ (bấm "Đăng nhập bằng Scalef")
       │
Chuyển sang trang xác thực Scalef
       │
       ▼
Đăng nhập Scalef (nếu chưa đăng nhập)
       │
       ▼
Scalef hỏi: "Cho phép Gen-Green truy cập thông tin của bạn?"
       │
       ▼ (Đồng ý)
       │
Gen-Green nhận thông tin từ Scalef:
  - Tên, SĐT, email, ảnh đại diện
  - Scalef User ID (để liên kết)
       │
       ▼
   ┌───────────────────────────────────────────────┐
   │ Đã có tài khoản Gen-Green khớp SĐT/email?    │
   │                                               │
   │ CÓ → Đăng nhập tài khoản đó + liên kết       │
   │ KHÔNG → Tạo tài khoản Gen-Green mới + liên kết│
   └───────────────────────────────────────────────┘
       │
       ▼
Vào Gen-Green, tài khoản đã liên kết Scalef
```

### Thông tin được chia sẻ khi đăng nhập

| Thông tin | Gen-Green → Scalef | Scalef → Gen-Green |
|----------|-------------------|-------------------|
| Họ tên | V | V |
| Số điện thoại | V | V |
| Email | V | V |
| Ảnh đại diện | V | V |
| CCCD / MST | V (nếu đã xác minh) | V (nếu đã xác minh) |
| Tài khoản ngân hàng | Không (user tự nhập) | Không (user tự nhập) |
| Mật khẩu | Không bao giờ | Không bao giờ |

**Nguyên tắc:** Chỉ chia sẻ thông tin cần thiết để tạo tài khoản. Thông tin nhạy cảm (bank, mật khẩu) không bao giờ chia sẻ.

### Lợi ích

| Không có "Đăng nhập bằng..." | Có "Đăng nhập bằng..." |
|------|------|
| Đăng ký mới → điền form → xác minh SĐT → xác minh email → liên kết thủ công | Bấm 1 nút → đồng ý → xong |
| 5-10 phút, bỏ cuộc cao | 30 giây, tỷ lệ hoàn thành cao |
| Dễ nhập sai thông tin → khớp user sai | Thông tin chính xác từ nguồn gốc |

---

## 5. Hình thức C — Khớp tự động (batch, chạy 1 lần)

### Dành cho ai?

~1,000 user Scalef hiện có. Trước khi go-live, cần khớp sẵn với user Gen-Green tương ứng để:
- Creator đã có Scalef không cần liên kết lại thủ công
- Thu nhập từ trước được tổng hợp đúng người

### Cách khớp

Lấy 1,000 user Scalef → dò trong 150,000 user Gen-Green (bên ít khớp vào bên nhiều).

**Ưu tiên khớp:**

| Bước | Thông tin | Độ tin cậy | Hành động |
|------|----------|-----------|----------|
| 1 | CCCD / Mã số thuế | Rất cao | Tự động liên kết |
| 2 | Số điện thoại (nếu bước 1 không khớp) | Cao | Tự động liên kết |
| 3 | Email (nếu bước 1+2 không khớp) | Trung bình | Chuyển admin xem xét |
| 4 | Không khớp gì | — | Ghi nhận, chờ user tự liên kết |

### Chuẩn hóa dữ liệu trước khi khớp

| Thông tin | Chuẩn hóa | Ví dụ |
|----------|----------|-------|
| Số điện thoại | Đưa về format +84, bỏ khoảng trắng | "0912 345 678" → "+84912345678" |
| Email | Viết thường, bỏ khoảng trắng | "User@Gmail.COM " → "user@gmail.com" |
| CCCD | Bỏ khoảng trắng, chỉ giữ số | "012 345 678 901" → "012345678901" |
| Họ tên | Bỏ dấu cách thừa, viết hoa chữ đầu | "  nguyễn  văn  a " → "Nguyễn Văn A" |

### Xử lý các tình huống đặc biệt

| Tình huống | Cách xử lý |
|-----------|-----------|
| Cùng CCCD, khác SĐT | Tự động liên kết — CCCD là chính xác nhất |
| Cùng CCCD, khác email | Tự động liên kết — giữ email của mỗi bên |
| Cùng SĐT, khác tên | Chuyển admin xem xét |
| Cùng email, khác CCCD | **Không liên kết** — có thể là 2 người khác nhau |
| 1 user Scalef khớp nhiều user Gen-Green | Chuyển admin xem xét |

### Kết quả dự kiến

```
1,000 user Scalef
       ↓
   Chuẩn hóa dữ liệu
       ↓
   Khớp với 150,000 user Gen-Green
       ↓
   ┌────────────────────────────────────────────┐
   │ Khớp CCCD/SĐT → Tự động liên kết          │  ~700–800 users
   │ Chỉ khớp email → Admin xem xét            │  ~100–200 users
   │ Không khớp → Chờ user tự liên kết          │  ~50–100 users
   └────────────────────────────────────────────┘
```

### Ai làm gì

| Bên | Trách nhiệm |
|-----|-------------|
| Scalef | Xuất danh sách 1,000 user (CCCD, SĐT, email, tên) theo format chuẩn |
| Gen-Green | Cung cấp API tra cứu user theo CCCD/SĐT/email |
| AccessTrade | Chạy khớp, xử lý ngoại lệ, báo cáo kết quả cho 2 team review |

---

## 6. Dữ liệu liên kết

### Mỗi bên cần lưu gì?

**Phía Gen-Green** — thêm vào thông tin user:

| Trường | Mô tả |
|--------|-------|
| `scalef_user_id` | ID tài khoản Scalef đã liên kết |
| `scalef_linked_at` | Thời điểm liên kết |
| `scalef_link_method` | Cách liên kết: "manual" / "oauth" / "batch" |

**Phía Scalef** — thêm vào thông tin user:

| Trường | Mô tả |
|--------|-------|
| `gengreen_user_id` | ID tài khoản Gen-Green đã liên kết |
| `gengreen_linked_at` | Thời điểm liên kết |
| `gengreen_link_method` | Cách liên kết: "manual" / "oauth" / "batch" |

### Quy tắc liên kết

| Quy tắc | Giải thích |
|---------|-----------|
| **1:1 nghiêm ngặt** | 1 Gen-Green user chỉ liên kết 1 Scalef user, và ngược lại |
| **Không tự động gỡ** | Chỉ admin mới có quyền gỡ liên kết |
| **Có lịch sử** | Mọi liên kết/gỡ đều ghi lại: ai làm, lúc nào, bằng cách nào |
| **Không ảnh hưởng tài khoản gốc** | Gỡ liên kết không xóa tài khoản bên nào — chỉ ngắt kết nối |

---

## 7. Đồng bộ thông tin sau khi liên kết

### Đồng bộ gì?

Sau khi liên kết, một số thông tin nên được đồng bộ để đảm bảo nhất quán:

| Thông tin | Hướng đồng bộ | Ghi chú |
|----------|--------------|--------|
| Trạng thái KYC/eKYC | Bên đã xác minh → bên chưa | 1 lần xác minh, dùng cho cả 2 |
| Cập nhật SĐT | 2 chiều | User đổi SĐT bên này → cập nhật bên kia |
| Cập nhật email | 2 chiều | Tương tự |
| Khóa / vô hiệu tài khoản | 2 chiều (thông báo) | Bên này khóa → bên kia nhận cảnh báo |
| Xóa tài khoản | 1 chiều (thông báo) | Bên này xóa → bên kia gỡ liên kết, không xóa |
| Thu nhập / giao dịch | Không đồng bộ | Mỗi bên giữ dữ liệu riêng, AT tổng hợp khi tính thuế |

### Đồng bộ khi nào?

| Thời điểm | Cách thức |
|----------|----------|
| User cập nhật profile | Gửi thông báo sang bên kia (gần như tức thì) |
| User bị khóa/xóa | Gửi thông báo sang bên kia |
| Hàng ngày | Kiểm tra đối soát tự động — phát hiện sai lệch |

---

## 8. Thanh toán & Thuế TNCN

### Vì sao liên kết tài khoản quyết định việc tính thuế?

AccessTrade kê khai thuế TNCN hộ creator ở cả Gen-Green và Scalef. Thuế TNCN tính theo **tổng thu nhập** — không phải theo từng nguồn riêng.

| Ví dụ | Không liên kết | Có liên kết |
|-------|---------------|-------------|
| Thu nhập Gen-Green | 5 triệu → thuế A | 5 triệu |
| Thu nhập Scalef | 3 triệu → thuế B | 3 triệu |
| **Tổng** | Tính thuế riêng → có thể sai bậc | **8 triệu → thuế đúng bậc** |

**Liên kết tài khoản = biết "cùng 1 người" = tổng hợp thu nhập đúng = thuế đúng.**

### Cách AccessTrade tổng hợp

```
Hàng tháng:

  Lấy danh sách user đã liên kết
       ↓
  Gộp thu nhập Gen-Green + Scalef theo CCCD/MST
       ↓
  Tính thuế TNCN trên tổng thu nhập
       ↓
  Thanh toán 1 lần, 1 tài khoản ngân hàng, đã trừ thuế
       ↓
  Xuất 1 bảng kê thuế cho mỗi người
```

### User chưa liên kết thì sao?

- Vẫn nhận thanh toán bình thường từ mỗi bên riêng
- Nhưng thuế có thể bị tính sai bậc (vì AT không biết là cùng 1 người)
- Hệ thống sẽ nhắc user liên kết — nhưng không ép buộc

---

## 9. Yêu cầu kỹ thuật từ các bên

### Team Gen-Green cần xây

| # | Hạng mục | Mô tả |
|---|---------|-------|
| G1 | **OAuth Provider** | Cho phép Scalef dùng "Đăng nhập bằng Gen-Green" — cung cấp endpoint authorize, token, userinfo |
| G2 | **OAuth Client (Scalef)** | Cho phép Gen-Green user đăng nhập/liên kết bằng tài khoản Scalef |
| G3 | **Trang liên kết tài khoản** | UI trong cài đặt: hiển thị trạng thái liên kết, nút liên kết/gỡ |
| G4 | **Touchpoint banners** | Banner nhắc liên kết tại chi tiết campaign + popup khi join affiliate |
| G5 | **API tra cứu user** | Cho phép AccessTrade tra cứu user theo CCCD/SĐT/email (phục vụ batch matching) |
| G6 | **Lưu trữ liên kết** | Thêm fields `scalef_user_id`, `scalef_linked_at`, `scalef_link_method` vào user model |
| G7 | **Webhook đồng bộ** | Gửi thông báo khi user cập nhật profile / bị khóa / bị xóa |

### Team Scalef cần xây

| # | Hạng mục | Mô tả |
|---|---------|-------|
| S1 | **OAuth Provider** | Cho phép Gen-Green dùng "Đăng nhập bằng Scalef" — cung cấp endpoint authorize, token, userinfo |
| S2 | **OAuth Client (Gen-Green)** | Cho phép Scalef user đăng nhập/liên kết bằng tài khoản Gen-Green |
| S3 | **Trang liên kết tài khoản** | UI trong cài đặt: hiển thị trạng thái liên kết Gen-Green |
| S4 | **Xuất danh sách user** | Export 1,000 user (CCCD, SĐT, email, tên) theo format chuẩn cho batch matching |
| S5 | **Lưu trữ liên kết** | Thêm fields `gengreen_user_id`, `gengreen_linked_at`, `gengreen_link_method` |
| S6 | **Webhook đồng bộ** | Gửi thông báo khi user cập nhật profile / bị khóa / bị xóa |
| S7 | **API tạo tài khoản** | Cho phép tạo tài khoản publisher mới từ bên ngoài (khi user Gen-Green chưa có Scalef) |

### AccessTrade cần làm

| # | Hạng mục | Mô tả |
|---|---------|-------|
| A1 | Chạy batch matching | Khớp 1,000 Scalef user ↔ Gen-Green user trước go-live |
| A2 | Xử lý ngoại lệ | Review các trường hợp khớp không chắc chắn |
| A3 | Tổng hợp thuế | Gộp thu nhập 2 nguồn theo CCCD/MST |
| A4 | Đối soát liên kết | Kiểm tra định kỳ: liên kết có chính xác không |

---

## 10. Phương án triển khai

### Giai đoạn 1: Liên kết cơ bản (Tuần 1–2)

| Việc | Team | Ghi chú |
|------|------|--------|
| Gen-Green xây OAuth Provider | Gen-Green | Để Scalef dùng "Đăng nhập bằng Gen-Green" |
| Scalef xây OAuth Provider | Scalef | Để Gen-Green dùng "Đăng nhập bằng Scalef" |
| Gen-Green xây luồng liên kết thủ công | Gen-Green | Trang cài đặt + touchpoint banners |
| Scalef xây luồng liên kết thủ công | Scalef | Trang cài đặt |
| AccessTrade chạy batch matching | AccessTrade | Khớp 1,000 user Scalef |
| Cả 3 team review kết quả matching | Tất cả | Xác nhận trước khi go-live |

### Giai đoạn 2: Đăng nhập cross-platform (Tuần 3–4)

| Việc | Team | Ghi chú |
|------|------|--------|
| Scalef thêm nút "Đăng nhập bằng Gen-Green" | Scalef | Trang đăng nhập + đăng ký |
| Gen-Green thêm nút "Đăng nhập bằng Scalef" | Gen-Green | Trang đăng nhập + đăng ký |
| Tự động tạo tài khoản khi đăng nhập cross-platform | Cả 2 | Nếu chưa có tài khoản bên kia |
| Bật đồng bộ profile 2 chiều | Cả 2 | SĐT, email, KYC status |
| Test end-to-end | Tất cả | |

### Giai đoạn 3: Vận hành (Liên tục)

| Việc | Team |
|------|------|
| Đối soát liên kết hàng ngày | AccessTrade |
| Tổng hợp thuế hàng tháng | AccessTrade |
| Xử lý yêu cầu gỡ liên kết từ user | Admin (AT) |
| Monitor tỷ lệ liên kết, tỷ lệ đăng nhập cross-platform | Tất cả |

---

## 11. Rủi ro và biện pháp

| # | Rủi ro | Mức độ | Biện pháp |
|---|--------|--------|-----------|
| 1 | Liên kết sai người (batch matching) | Cao | Ưu tiên CCCD/MST, email-only chuyển admin review |
| 2 | User từ chối liên kết (lo ngại bảo mật) | Trung bình | Giải thích rõ lợi ích, không ép buộc, cho phép gỡ |
| 3 | OAuth implementation phức tạp | Trung bình | Dùng chuẩn OAuth 2.0, có thể dùng thư viện có sẵn |
| 4 | Đồng bộ profile bị conflict (SĐT khác nhau 2 bên) | Trung bình | Bên cập nhật sau cùng thắng + thông báo bên kia |
| 5 | 1 user cố tình liên kết tài khoản người khác | Cao | OAuth bắt buộc đăng nhập — không thể liên kết nếu không có mật khẩu |
| 6 | Scalef/Gen-Green chưa có OAuth Provider | Cao | Đây là điều kiện tiên quyết — cần ưu tiên xây dựng |

---

## 12. Câu hỏi cần trả lời

### Cho Team Scalef

1. Scalef hiện có hệ thống OAuth/SSO chưa? Nếu chưa, timeline xây dựng?
2. User Scalef đăng nhập bằng gì? (email/SĐT + mật khẩu? SSO?)
3. Có trường CCCD/MST trong user model không?
4. Có sẵn API tạo tài khoản publisher từ bên ngoài không?

### Cho Team Gen-Green

1. Gen-Green hiện có hệ thống OAuth Provider chưa? (cho phép app bên ngoài đăng nhập bằng Gen-Green)
2. User Gen-Green đăng nhập bằng gì? (SĐT + OTP? Email + mật khẩu? Firebase Auth?)
3. Có trường CCCD/MST trong user model không? Tỷ lệ user đã điền?
4. Có sẵn webhook/event system khi user thay đổi profile không?

### Cho Ban quản lý

1. Có yêu cầu pháp lý nào về chia sẻ dữ liệu user giữa 2 nền tảng không? (PDPA, consent)
2. Có cần user đồng ý (consent) trước khi batch matching không?
3. Ưu tiên triển khai: liên kết thủ công trước hay đăng nhập cross-platform trước?

---

## 13. Tóm tắt

| Hình thức | Ai dùng | Khi nào | Effort |
|----------|---------|--------|--------|
| **A. Liên kết thủ công** | User đã có cả 2 tài khoản | Bất cứ lúc nào | Thấp |
| **B. Đăng nhập bằng tài khoản bên kia** | User mới | Lúc đăng ký / đăng nhập | Trung bình (cần OAuth) |
| **C. Khớp tự động (batch)** | 1,000 user Scalef hiện có | 1 lần trước go-live | Thấp |

**Kết quả mong đợi:**
- 100% user Scalef hiện có được liên kết hoặc có cơ chế tự liên kết
- User mới đăng ký 1 bên có thể dùng tài khoản bên kia — 30 giây thay vì 10 phút
- Thu nhập 2 nguồn được tổng hợp chính xác cho kê khai thuế
- Hệ thống linh hoạt — thay đổi đơn vị vận hành không ảnh hưởng liên kết user

---

*Tài liệu tham chiếu: [Tích hợp Scalef Affiliate vào Gen-Green](./gengreen-scalef-affiliate-integration-proposal.md) | [Ambassador-Pub2 PRD](../pub2-affiliate-integration/prd-affiliate-integration-2026-03-25.md)*
*Tổng hợp từ phiên brainstorming ngày 2026-03-31*
