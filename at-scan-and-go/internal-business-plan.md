# Scan & Go: Mô hình kinh doanh & Kế hoạch triển khai

**Tài liệu nội bộ - Dành cho Business Team**
**Ngày:** 2026-03-21

---

## 1. Tổng quan mô hình

### Scan & Go là gì?

User đến cửa hàng → quét QR thanh toán → deal **tự động ghi nhận** → user nhận cashback.

Không cần mở app riêng, không cần chọn deal trước, không cần activate. Chỉ cần thanh toán.

### Vai trò của chúng ta

```
Chúng ta = Deal Aggregator (Trung gian deal, KHÔNG trung gian thanh toán)

  ┌────────────┐       ┌────────────┐       ┌────────────┐
  │  MERCHANT  │──deal──>  PLATFORM  │──deal──>   USER    │
  │  (tạo deal,│       │  (chúng ta)│       │  (nhận     │
  │   trả      │       │            │       │   cashback)│
  │   commission)      └─────┬──────┘       └────────────┘
  └────────────┘             │
                        share deal
                             │
                             ▼
                       ┌────────────┐       ┌────────────┐
                       │   MOMO     │──deal──>  USER     │
                       │  (xử lý   │       │  MOMO      │
                       │   payment, │       │  (35M+)    │
                       │   show deal)       └────────────┘
                       └────────────┘
```

**Chúng ta KHÔNG touch tiền.** MoMo xử lý thanh toán. Chúng ta chỉ:
1. Deal với merchant → lấy deal
2. Phân phối deal → cho user (qua app chúng ta + qua MoMo)
3. Track giao dịch → tính commission
4. Trả reward cho user → cashback/voucher

### Tại sao không cần giấy phép trung gian thanh toán?

Chúng ta hoạt động như **affiliate marketing platform** (giống ShopBack, Cashbac):
- Không nhận tiền từ user
- Không chuyển tiền cho merchant
- Chỉ nhận commission từ merchant (qua MoMo settlement)
- Trả reward cho user từ commission đã nhận

---

## 2. Cơ chế cốt lõi: Đăng ký nhận webhook giao dịch tại Merchant

### Tại sao đây là điều kiện tiên quyết?

Scan & Go hoạt động được khi và chỉ khi: **AT-Scan-and-Go nhận được thông báo từ MoMo mỗi khi có giao dịch tại merchant đã deal.** Không có cái này → không track được gì.

### Flow đăng ký (Authen Merchant)

```
BƯỚC 1: BD deal với Highland Coffee
  → Highland đồng ý: commission 3%

BƯỚC 2: AT-Scan-and-Go đăng ký với MoMo
  → "Tôi là partner của Highland (momo_merchant_id: HIGHLAND_001)"
  → "Gửi webhook mọi giao dịch tại HIGHLAND_001 cho tôi"

BƯỚC 3: Merchant xác nhận trên MoMo Merchant Portal
  → "Đúng, tôi cho phép AT-Scan-and-Go nhận thông tin giao dịch"

BƯỚC 4: MoMo kích hoạt
  → Từ giờ, mọi giao dịch tại HIGHLAND_001 → MoMo webhook → AT-Scan-and-Go
```

### Tại sao merchant phải xác nhận?

MoMo không thể cho bất kỳ ai đăng ký nhận webhook giao dịch của merchant mà không có sự đồng ý. Các cơ chế xác nhận có thể:

| Cơ chế | Mô tả |
|---|---|
| Merchant approve trên MoMo Portal | Merchant vào portal MoMo → bấm "Cho phép AT-Scan-and-Go" |
| Merchant cấp API key cho AT-Scan-and-Go | Merchant chia sẻ merchant_secret_key → AT-Scan-and-Go dùng để đăng ký |
| 3-party agreement | MoMo tạo hợp đồng 3 bên: AT-Scan-and-Go ↔ MoMo ↔ Merchant |

### Webhook data AT-Scan-and-Go nhận được

```json
{
  "trans_id": "TXN_123456",
  "merchant_id": "HIGHLAND_001",
  "amount": 500000,
  "status": "SUCCESS",
  "momo_user_id": "USER_A_HASH",
  "payment_method": "MOMO_WALLET | BANK_TRANSFER",
  "source_bank": "VCB",
  "timestamp": "2026-03-21T10:30:00+07:00"
}
```

---

## 3. Hai tình huống thanh toán & Cách xử lý

### Tổng quan

```
  S1: Merchant CÓ MoMo Merchant Account (~60% merchant)
  ─────────────────────────────────────────────────────
  User (MoMo hoặc bank) → thanh toán → MoMo biết merchant
  → Webhook đầy đủ → AT-Scan-and-Go track được
  → Phase 2: Linked Account → zero friction

  S2: Merchant KHÔNG CÓ MoMo Account (chỉ có QR bank)
  ─────────────────────────────────────────────────────
  User → thanh toán → tiền qua Napas → Bank merchant
  → MoMo không biết merchant → không có webhook tự động
  → NHƯNG: AT-Scan-and-Go QR giải quyết được!

  ┌─────────────────────────────────────────────────┐
  │  AT-Scan-and-Go QR GIẢI QUYẾT CẢ 2 TÌNH HUỐNG  │
  │  Nguyên lý chung: Đưa user vào flow có tracking │
  │  TRƯỚC KHI thanh toán                            │
  └─────────────────────────────────────────────────┘
```

### S1: Merchant CÓ MoMo Merchant Account (BEST CASE)

```
User thanh toán tại MoMo Merchant (dùng MoMo wallet hoặc bank app)
→ MoMo biết MERCHANT (có merchant_id)
→ Webhook có merchant_id + amount + momo_user_id (nếu user dùng MoMo)
→ AT-Scan-and-Go match → ghi nhận deal → cashback!
```

| User dùng | MoMo biết | Tracking |
|---|---|---|
| MoMo wallet | user_id + merchant_id | **100% chính xác** |
| Bank app | merchant_id (không biết user) | **Cần QR AT-Scan-and-Go** để biết user |

**Phase 1:** User quét QR AT-Scan-and-Go → AT-Scan-and-Go biết user → gọi Payment Gateway (có `partner_ref_id`) → track 100%
**Phase 2 (Linked Account):** User link MoMo ↔ AT-Scan-and-Go 1 lần → sau đó quét QR MoMo gốc → auto track = zero friction

### S2: Merchant KHÔNG CÓ MoMo Merchant Account (chỉ có QR bank)

```
Merchant chỉ có QR VietQR ngân hàng
→ Nếu user tự quét QR bank → tiền đi: MoMo/Bank → Napas → Bank merchant
→ MoMo KHÔNG biết merchant này → không có webhook
→ AT-Scan-and-Go KHÔNG THỂ đăng ký webhook (không có momo_merchant_id)
```

**Giải pháp: GIỐNG S1** — AT-Scan-and-Go QR đặt tại cửa hàng, đưa user vào flow có tracking.

### Giải pháp chung cho cả S1 và S2: AT-Scan-and-Go QR

Dù merchant có hay không có MoMo Account, flow user trải nghiệm **gần như giống nhau:**

```
User quét QR AT-Scan-and-Go → AT-Scan-and-Go biết user + merchant
→ Chuyển qua MoMo thanh toán → Webhook → Track!
```

Chỉ khác phía nhận tiền:
- S1: Tiền vào MoMo Merchant Account
- S2: Tiền qua Napas vào Bank Account merchant

#### Cách 1 (Best case): MoMo deeplink + tracking params

```
QR tại cửa hàng chứa MoMo deeplink có thêm tracking params:

  S1: momo://pay?receiver=MOMO_HIGHLAND_001    ← MoMo Merchant ID
                 &utm_source=at-scan-and-go
                 &utm_campaign=DEAL_001
                 &partner_ref=PLT_xxx

  S2: momo://pay?receiver=VCB_123456789        ← Bank account number
                 &utm_source=at-scan-and-go
                 &utm_campaign=DEAL_001
                 &partner_ref=PLT_xxx

Flow:
  User quét QR (camera) → Mở MoMo app trực tiếp (deeplink)
  → MoMo hiển thị: receiver + nhập số tiền
  → User xác nhận → Thanh toán
  → MoMo gửi webhook (có partner_ref) → AT-Scan-and-Go ghi nhận

Ưu điểm:
  ✅ User quét 1 lần → mở thẳng MoMo → thanh toán. NHANH NHẤT
  ✅ Không qua web trung gian
  ✅ Cùng 1 flow cho cả S1 và S2
Yêu cầu MoMo:
  Deeplink hỗ trợ nhận utm/partner params + trả lại trong webhook
```

#### Cách 2 (Fallback): AT-Scan-and-Go web redirect

```
QR tại cửa hàng chứa AT-Scan-and-Go URL:

  https://at-scan-and-go.com/pay/HIGHLAND?ref=PLT_xxx

Flow:
  User quét QR (camera) → Mở web AT-Scan-and-Go
  → AT-Scan-and-Go show: "Highland Coffee • Cashback 5%"
  → AT-Scan-and-Go biết user (login/cookie) + biết merchant
  → Bấm "Thanh toán qua MoMo"
  → AT-Scan-and-Go gọi Payment Gateway (S1) hoặc redirect deeplink (S2)
  → User xác nhận trên MoMo → Thanh toán
  → MoMo webhook → AT-Scan-and-Go ghi nhận

Ưu điểm:
  ✅ Không cần MoMo hỗ trợ gì đặc biệt
  ✅ AT-Scan-and-Go kiểm soát hoàn toàn, biết user + merchant trước khi pay
  ✅ Có thể show deal info, cashback amount cho user thấy
Nhược điểm:
  ⚠️ Thêm 1 bước (mở web) so với Cách 1
  ⚠️ Cần user login/đã đăng nhập AT-Scan-and-Go
```

#### Cách 3 (Dài hạn, chỉ S2): Merchant mở MoMo Merchant Account

```
BD hỗ trợ merchant đăng ký MoMo Merchant Account
→ Chuyển S2 → S1 (giải quyết tận gốc)
→ MoMo thêm merchant mới (lợi ích cho MoMo)
```

### Tổng hợp

| Cách | Áp dụng | UX | MoMo effort |
|---|---|---|---|
| **Cách 1** Deeplink + params | S1 + S2 | Tốt nhất (1 bước) | Thấp |
| **Cách 2** Web redirect | S1 + S2 | Tốt (2 bước) | Zero |
| **Cách 3** Merchant mở MoMo account | Chỉ S2 | N/A | N/A |
| **Linked Account** (Phase 2) | Chỉ S1 | Zero friction | Trung bình |

### Chiến lược onboard merchant

```
BD team khi tiếp cận merchant:

  Merchant ĐÃ CÓ MoMo Merchant Account?
    → YES → Onboard ngay. Dán QR AT-Scan-and-Go. S1 flow.
    → Phase 2: Linked Account → user quét QR gốc cũng track được

  Merchant CHƯA CÓ MoMo Merchant Account?
    → VẪN ONBOARD ĐƯỢC! Dán QR AT-Scan-and-Go. S2 flow (cùng UX).
    → Song song: hỗ trợ merchant đăng ký MoMo Account → chuyển thành S1
```

---

## 4. Cách hoạt động Scan & Go — theo từng tình huống

### 4.1 S1: User MoMo → MoMo Merchant (Best case)

**Phase 1: User quét QR AT-Scan-and-Go tại cửa hàng**

```
BƯỚC 1: User đến Highland Coffee
        Thấy QR sticker "Quét nhận cashback 5%"

BƯỚC 2: User quét QR bằng camera điện thoại
        → Mở web AT-Scan-and-Go: "Highland Coffee • Cashback 5% • Bill từ 100K"
        → Bấm "Thanh toán qua MoMo"

BƯỚC 3: AT-Scan-and-Go gọi MoMo Payment Gateway API
        → POST /v2/gateway/api/create
        → {partner_ref_id: "PLT_xxx", merchant_id: "HIGHLAND_001", amount}

BƯỚC 4: MoMo app mở → User xác nhận → Thanh toán bằng MoMo wallet

BƯỚC 5: MoMo webhook → AT-Scan-and-Go
        → {trans_id, amount, status, partner_ref_id, momo_user_id}
        → Match: partner_ref_id → biết user + merchant + deal
        → Ghi nhận commission → User nhận notification cashback

TỔNG THỜI GIAN: ~15 giây
API MoMo: Payment Gateway (có sẵn) → MoMo effort = ZERO
```

**Phase 2: User đã link MoMo ↔ AT-Scan-and-Go (Linked Account)**

```
User đến Highland Coffee
  → Quét QR MoMo gốc (hoặc QR AT-Scan-and-Go — đều được)
  → Thanh toán bằng MoMo wallet như bình thường
  → MoMo nhận diện: user đã link + merchant có deal
  → MoMo webhook → AT-Scan-and-Go: {merchant_id, hashed_momo_user_id, amount}
  → AT-Scan-and-Go match user → ghi nhận → cashback!

User KHÔNG CẦN LÀM GÌ KHÁC ngoài thanh toán.
API MoMo: OAuth + Transaction subscription → MoMo effort = Trung bình
```

---

### 4.2 S2: Merchant KHÔNG có MoMo Account — CÙNG FLOW với S1

**Vấn đề:** Merchant chỉ có QR ngân hàng. Không có momo_merchant_id → không đăng ký webhook thông thường được.

**Giải pháp:** Cùng nguyên lý với S1 — QR AT-Scan-and-Go tại cửa hàng, đưa user vào flow có tracking.

**Cách 1 (Best case): MoMo deeplink + tracking params**

```
QR sticker AT-Scan-and-Go chứa MoMo deeplink (khác S1 chỉ ở receiver):

  momo://pay?receiver=VCB_123456789        ← Bank account (thay vì MoMo Merchant ID)
            &utm_source=at-scan-and-go
            &utm_campaign=DEAL_001
            &partner_ref=PLT_xxx

BƯỚC 1: User quét QR → MoMo app mở trực tiếp (1 bước!)
BƯỚC 2: MoMo hiển thị: chuyển tới VCB_123456789 → User nhập số tiền
BƯỚC 3: User xác nhận → Thanh toán (MoMo → Napas → Bank merchant)
BƯỚC 4: MoMo webhook (có partner_ref) → AT-Scan-and-Go track!

UX: Giống hệt S1 — user không biết sự khác biệt
```

**Cách 2 (Fallback): AT-Scan-and-Go web redirect — giống hệt S1**

```
BƯỚC 1-2: Giống S1 (quét QR → mở web → bấm thanh toán)
BƯỚC 3: AT-Scan-and-Go redirect → MoMo deeplink (receiver = bank account)
BƯỚC 4: MoMo → Napas → Bank merchant
BƯỚC 5: Webhook → AT-Scan-and-Go track!
```

**Cách 3 (Dài hạn): Hỗ trợ merchant mở MoMo Account → chuyển thành S1**

**Lưu ý:** Linked Account (Phase 2) KHÔNG áp dụng cho S2 vì không có momo_merchant_id.

---

### 4.3 Tổng hợp: So sánh S1 vs S2

| | S1 (MoMo Merchant) | S2 (Bank Merchant) |
|---|---|---|
| **Phase 1: QR AT-Scan-and-Go** | ✅ Deeplink/redirect → Payment Gateway | ✅ Deeplink/redirect → Napas |
| **Phase 2: Linked Account** | ✅ Zero friction, auto track | ❌ Không áp dụng |
| **Receiver trong deeplink** | momo_merchant_id | bank_account_number |
| **User experience** | Giống nhau | Giống nhau |

**Điểm mấu chốt:**
- S1 và S2 **cùng 1 flow từ phía user** — chỉ khác receiver phía sau
- AT-Scan-and-Go QR là giải pháp xuyên suốt cả 2 tình huống
- Phase 2 Linked Account chỉ nâng cấp S1 (zero friction). S2 vẫn cần QR AT-Scan-and-Go
- Nếu user tự quét QR gốc (không phải QR AT-Scan-and-Go) → chấp nhận miss → chiến lược: QR AT-Scan-and-Go ghi rõ "Quét để nhận cashback"

---

## 5. Dòng tiền & Commission

### Ví dụ cụ thể

```
User thanh toán 500,000đ tại Highland Coffee

Highland đã set commission: 3% (thỏa thuận với BD team)
Commission pool: 500,000 × 3% = 15,000đ

Chia sẻ:
  Highland giữ lại:     485,000đ
  MoMo nhận:              3,000đ  (20% commission)
  Chúng ta nhận:          7,500đ  (50% commission)  ← DOANH THU
  User nhận cashback:     4,500đ  (30% commission)
```

### Commission thay đổi theo kênh

| Kênh | Ai mang khách | MoMo | Chúng ta | User |
|---|---|---|---|---|
| **Kênh AT-Scan-and-Go** | Chúng ta | 15% | 55% | 30% |
| **Kênh MoMo** | MoMo | 35% | 35% | 30% |

→ Ai mang khách thì nhận nhiều hơn. User luôn nhận 30%.

### Commission theo ngành (đề xuất)

| Ngành | Commission rate | Ghi chú |
|---|---|---|
| F&B (cà phê, nhà hàng) | 2-3% | Margin thấp, bù bằng volume cao |
| Retail (thời trang, điện tử) | 3-5% | Margin cao hơn |
| Dịch vụ (spa, gym, salon) | 5-8% | Margin cao, frequency thấp |
| Siêu thị, tiện lợi | 1-2% | Volume rất cao, margin mỏng |

### Dòng tiền settlement

```
Ngày 1:   User thanh toán 500K → MoMo xử lý → Merchant nhận tiền
Ngày 1:   MoMo webhook → AT-Scan-and-Go ghi nhận → Commission PENDING
Ngày 7:   Đối soát daily → Commission VALIDATED
Ngày 14:  Hết refund window → Commission FINALIZED
Ngày 15:  MoMo settlement → chuyển commission cho AT-Scan-and-Go
Ngày 16:  AT-Scan-and-Go trả cashback cho user (vào MoMo wallet hoặc voucher)
```

**Quan trọng:** Commission hold 14 ngày để tránh fraud (user mua rồi refund lấy cashback).

---

## 6. Mô hình doanh thu

### Nguồn doanh thu

| # | Nguồn | Mô tả | Timeline |
|---|---|---|---|
| 1 | **Commission** | 50-55% commission từ mỗi giao dịch qua deal | Phase 1 |
| 2 | **Promoted deals** | Merchant trả thêm để deal hiển thị nổi bật | Phase 2 |
| 3 | **Data insights** | Bán báo cáo spending behavior cho merchant/brand | Phase 3 |
| 4 | **Subscription** | Merchant trả phí cố định/tháng + commission thấp hơn | Phase 2 |

### Unit economics (ước tính)

```
Giả sử: 1,000 giao dịch/ngày × trung bình 300K/giao dịch × commission 2.5%

Revenue/ngày:
  Total commission:     1,000 × 300K × 2.5% = 7,500,000đ
  AT-Scan-and-Go nhận (50%):  3,750,000đ
  Trả user (30%):      2,250,000đ
  MoMo nhận (20%):     1,500,000đ

Revenue/tháng (AT-Scan-and-Go): ~112,500,000đ (~112M)

Chi phí/tháng (ước tính):
  Team (5 người):       100,000,000đ
  Infra + hosting:        5,000,000đ
  Marketing:             20,000,000đ
  QR sticker + vận hành: 10,000,000đ
  Tổng:                 135,000,000đ

→ Break-even: ~1,200 giao dịch/ngày
→ Target Month 6: 2,000 giao dịch/ngày = lãi ~40M/tháng
```

---

## 7. Kế hoạch triển khai

### Phase 1: MVP Scan & Go (Tháng 1-3)

**Mục tiêu:** Chạy pilot 20 merchant, chứng minh model hoạt động

| Tuần | Đầu việc | Ai làm |
|---|---|---|
| 1-2 | Ký hợp tác MoMo, nhận Partner Account + API credentials | BD + Tech |
| 2-4 | Build web checkout + MoMo Payment Gateway integration | Tech |
| 2-4 | Thiết kế QR sticker, in ấn | Design + Ops |
| 3-5 | BD onboard 20 merchant pilot (F&B HCM/HN) | BD |
| 4-5 | Build merchant portal (đăng ký, tạo deal, xem analytics) | Tech |
| 5-6 | Build user app/web (đăng ký, xem reward, lịch sử) | Tech |
| 6-8 | Soft launch: deploy QR tại 20 merchant | Ops + BD |
| 8-12 | Thu thập data, optimize, đánh giá KPI | All |

**KPI Phase 1:**
- 20 merchant active
- 500+ giao dịch/tháng
- Tracking accuracy > 95%
- User satisfaction > 4/5

**Tech stack cần build:**
- Web checkout page (mobile-first)
- MoMo API integration (Payment Gateway + webhook)
- QR code generator (dynamic QR per merchant)
- Transaction tracking engine
- Commission ledger (pending → confirmed → finalized)
- Merchant dashboard
- User reward portal
- Reconciliation engine (đối soát daily)
- Anti-fraud rules

### Phase 2: Scale + Linked Account (Tháng 4-6)

**Mục tiêu:** 100 merchant, true zero-friction Scan & Go

| Đầu việc | Mô tả |
|---|---|
| Linked Account | User link MoMo ↔ AT-Scan-and-Go → quét QR nào cũng track |
| MoMo deal display | MoMo show deal trong app → kênh MoMo hoạt động |
| Deal catalog API | API để MoMo pull deal catalog |
| Disbursement | Trả cashback trực tiếp vào MoMo wallet user |
| Scale merchant | BD mở rộng 100 merchant, thêm ngành retail, dịch vụ |
| Promoted deals | Merchant trả thêm để đẩy deal lên top |

**KPI Phase 2:**
- 100 merchant active
- 3,000+ giao dịch/tháng
- Linked account rate > 40%

### Phase 3: MoMo Mini App + Multi-PSP (Tháng 7-12)

| Đầu việc | Mô tả |
|---|---|
| MoMo Mini App | App trong MoMo → reach 35M+ users |
| Multi-PSP | Tích hợp ZaloPay, VNPay (cùng model) |
| Analytics | Báo cáo nâng cao cho merchant |
| Mở rộng toàn quốc | 500+ merchant |

**KPI Phase 3:**
- 500+ merchant
- 10,000+ giao dịch/tháng
- Revenue: 200M+/tháng

---

## 8. Đầu việc & Nguồn lực

### Team cần thiết (Phase 1)

| Vai trò | Số lượng | Trách nhiệm |
|---|---|---|
| **BD / Sales** | 2 | Deal merchant, onboard, maintain relationship |
| **Backend Engineer** | 1-2 | API integration MoMo, transaction engine, commission |
| **Frontend / Mobile** | 1 | Web checkout, user app, merchant portal |
| **Design** | 1 (part-time) | QR sticker, web UI, brand |
| **Ops** | 1 | Deploy QR, reconciliation, support |
| **Tổng** | **5-6** | |

### Budget Phase 1 (3 tháng)

| Hạng mục | Chi phí | Ghi chú |
|---|---|---|
| Nhân sự | 300M | 5 người × 20M × 3 tháng |
| In ấn QR sticker | 5M | 20 merchant × 50 sticker × 5K |
| Hosting / infra | 10M | Cloud, domain, SSL |
| Marketing launch | 20M | Social media, merchant co-marketing |
| Cashback budget | 30M | Subsidize cashback ban đầu để attract user |
| Contingency | 15M | |
| **Tổng** | **380M** | ~3.8 tỷ cho 3 tháng |

---

## 9. Rủi ro & Biện pháp

| Rủi ro | Mức độ | Biện pháp |
|---|---|---|
| MoMo từ chối hoặc delay | Trung bình | Phase 1 dùng API có sẵn, effort MoMo = 0. Backup: tích hợp VNPay/ZaloPay |
| Merchant không muốn dán QR mới | Trung bình | BD thuyết phục bằng ROI. Subsidy QR + setup miễn phí |
| User fraud (mua → refund → giữ cashback) | Cao | Hold commission 14 ngày. Velocity check. Min amount |
| MoMo tự build cạnh tranh | Trung bình | Moat = merchant BD network + cross-platform (Phase 3) |
| Commission margin quá mỏng | Trung bình | Thêm revenue: promoted deals, subscription, data |
| Regulatory (NHNN) | Thấp | Không touch tiền = không cần giấy phép. Nhưng nên xin ý kiến pháp lý |

---

## 10. Tại sao mô hình này khả thi?

1. **MoMo có sẵn tất cả API cần thiết** → không cần chờ MoMo build gì
2. **Không cần giấy phép** → hoạt động như affiliate platform
3. **Asset nhẹ** → không cần hạ tầng payment, không cần vốn lớn
4. **Proven model** → ShopBack (SEA), Dosh (US), Cardlytics (US) đã chứng minh
5. **Win-win-win** → Merchant tăng khách, User nhận cashback, MoMo tăng volume
6. **Scalable** → Thêm merchant = thêm revenue, gần như linear

---

*Tài liệu nội bộ - Không chia sẻ bên ngoài*
