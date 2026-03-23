# Đề xuất hợp tác: Scan & Go - Deal tự động khi thanh toán QR

**Từ:** [Tên công ty]
**Gửi:** MoMo - Business Partnership
**Ngày:** 2026-03-21

---

## 1. Một câu tóm tắt

> Chúng tôi mang merchant deals đến cho MoMo. User MoMo thanh toán tại merchant → deal tự động ghi nhận → user nhận cashback → **MoMo tăng transaction volume + engagement mà không cần đầu tư BD**.

---

## 2. Mô hình Scan & Go

### User experience

```
TRƯỚC (không có deal):
  User đến cửa hàng → quét QR → thanh toán → xong.

SAU (có Scan & Go):
  User đến cửa hàng → quét QR → thanh toán → CASHBACK 5%! 🎉

  User không cần làm gì khác. Hệ thống tự nhận diện deal.
```

### Ai làm gì?

| Bên | Vai trò | Ví dụ |
|---|---|---|
| **Chúng tôi** | Deal với merchant, quản lý deal catalog, tính commission, trả reward | "Highland Coffee: cashback 3%, bill từ 100K" |
| **MoMo** | Xử lý thanh toán, show deal cho user MoMo, notify giao dịch | Webhook khi user thanh toán tại merchant có deal |
| **Merchant** | Tạo deal, set commission | "Tôi sẵn sàng trả 3% commission để có thêm khách" |
| **User** | Thanh toán bình thường | Quét QR → pay → nhận cashback |

### Chúng tôi KHÔNG touch tiền

- Không nhận tiền từ user, không chuyển tiền cho merchant
- MoMo xử lý toàn bộ payment
- Chúng tôi chỉ nhận commission qua MoMo settlement

---

## 3. Cơ chế cốt lõi: Đăng ký nhận webhook giao dịch tại Merchant

### Cách hoạt động

Để Scan & Go hoạt động, chúng tôi cần đăng ký với MoMo để **nhận webhook mỗi khi có giao dịch tại merchant đã hợp tác**.

```
BƯỚC 1: Chúng tôi deal với Highland Coffee (đã có MoMo Merchant Account)

BƯỚC 2: Đăng ký với MoMo:
  → "Highland (HIGHLAND_001) đồng ý hợp tác. Cho tôi subscribe webhook
     giao dịch tại merchant này."

BƯỚC 3: Highland xác nhận trên MoMo Merchant Portal:
  → "Tôi cho phép [AT-Scan-and-Go] nhận thông tin giao dịch"

BƯỚC 4: MoMo kích hoạt:
  → Mọi giao dịch tại HIGHLAND_001 → MoMo gửi webhook cho AT-Scan-and-Go
```

### Yêu cầu từ MoMo

| # | Yêu cầu | Mô tả |
|---|---|---|
| 1 | **Merchant webhook subscription API** | AT-Scan-and-Go đăng ký listen giao dịch tại danh sách merchant |
| 2 | **Merchant consent flow** | Merchant xác nhận cho phép AT-Scan-and-Go nhận webhook (qua MoMo Portal hoặc API key) |
| 3 | **Webhook data** | Mỗi giao dịch gửi: `trans_id, merchant_id, amount, status, momo_user_id (hashed), payment_method, timestamp` |
| 4 | **Refund webhook** | Notify khi giao dịch bị refund → AT-Scan-and-Go rollback commission |

### Hai tình huống thanh toán & Giải pháp

#### S1: MoMo User + MoMo Merchant (Best case — TRACK TỰ ĐỘNG)

```
User dùng MoMo wallet thanh toán tại MoMo Merchant
→ MoMo biết CẢ HAI BÊN: momo_user_id + merchant_id
→ Webhook đầy đủ data → AT-Scan-and-Go track tự động 100%
→ User KHÔNG CẦN quét QR AT-Scan-and-Go, không cần làm gì đặc biệt
```

**MoMo cần:** Gửi webhook với `momo_user_id` (hashed) + `merchant_id` + `amount`
**Kết quả:** ✅ Track tự động 100% — đúng tinh thần Scan & Go

#### S2: Một bên KHÔNG dùng MoMo → CẦN QR AT-Scan-and-Go

| Sub-case | Vấn đề | MoMo thiếu gì |
|---|---|---|
| **S2a** User dùng bank app | MoMo chỉ nhận tiền từ Napas | Thiếu **user_id** |
| **S2b** Merchant chỉ có QR bank | Tiền đi thẳng qua Napas | Thiếu **merchant_id** |

```
Cả 2 sub-case đều thiếu thông tin → không track tự động được
→ Giải pháp: QR AT-Scan-and-Go tại cửa hàng
→ Đưa user vào flow có tracking TRƯỚC KHI thanh toán
```

#### Giải pháp cho S2: AT-Scan-and-Go QR

**Cách 1 (Best case): MoMo deeplink + tracking params**

```
QR tại cửa hàng chứa MoMo deeplink có thêm tracking params:

  S2a: momo://pay?receiver=MOMO_HIGHLAND_001    ← MoMo Merchant ID
               &utm_source=at-scan-and-go
               &utm_campaign=DEAL_001
               &partner_ref=PLT_xxx

  S2b: momo://pay?receiver=VCB_123456789        ← Bank account number
               &utm_source=at-scan-and-go
               &utm_campaign=DEAL_001
               &partner_ref=PLT_xxx

User quét QR → MoMo mở trực tiếp → thanh toán → webhook có partner_ref → track!
```

**MoMo cần hỗ trợ:** Deeplink nhận thêm `utm_*` / `partner_ref` params và trả lại trong webhook.
**Effort:** Thấp (chỉ thêm params vào deeplink scheme có sẵn)
**UX:** Tốt nhất — user quét 1 lần → mở thẳng MoMo

**Cách 2 (Fallback): AT-Scan-and-Go web redirect**

```
QR tại cửa hàng chứa AT-Scan-and-Go URL:

  https://at-scan-and-go.com/pay/HIGHLAND?ref=PLT_xxx

User quét QR → mở web AT-Scan-and-Go (biết user + merchant)
→ "Highland Coffee • Cashback 5%"
→ Bấm "Thanh toán qua MoMo"
→ AT-Scan-and-Go gọi MoMo Payment Gateway (S2a) hoặc redirect deeplink (S2b)
→ Thanh toán → webhook → track!
```

**MoMo cần hỗ trợ:** Không gì đặc biệt (dùng Payment Gateway / deeplink cơ bản)
**UX:** Tốt, thêm 1 bước so với Cách 1

**Cách 3 (Dài hạn, chỉ S2b): Merchant mở MoMo Merchant Account**

Chúng tôi hỗ trợ merchant đăng ký → chuyển S2b → S1. **MoMo được thêm merchant mới miễn phí BD cost.**

#### Nâng cấp Phase 2: Linked Account (chỉ S1)

```
Với S1 (MoMo User + MoMo Merchant):
  User link MoMo ↔ AT-Scan-and-Go 1 lần (OAuth consent)
  → Sau đó quét QR MoMo gốc, thanh toán bình thường
  → MoMo auto-match: user đã link + merchant có deal
  → Webhook → AT-Scan-and-Go track → cashback!
  → Zero friction hoàn toàn
```

**Lưu ý:** Linked Account chỉ hoạt động với S1. Với S2 (thiếu thông tin 1 phía), vẫn cần QR AT-Scan-and-Go.

### Tóm tắt

| Tình huống | Tracking | QR AT-Scan-and-Go | MoMo effort |
|---|---|---|---|
| **S1** MoMo User + MoMo Merchant | ✅ Tự động qua webhook | Không bắt buộc | Zero (webhook có sẵn) |
| **S2** Một bên không MoMo | ✅ Qua QR AT-Scan-and-Go | **Bắt buộc** | Thấp (deeplink params) |
| **Linked Account** (Phase 2, chỉ S1) | ✅ Zero friction | Không cần | Trung bình |

**Kết luận:** S1 track **tự động** — user thanh toán bình thường, deal tự ghi nhận. S2 track qua **QR AT-Scan-and-Go** — chỉ thêm 1 bước. Merchant có hay không có MoMo Account đều onboard được. MoMo chỉ cần hỗ trợ 1 việc nhỏ cho S2: **cho phép thêm tracking params vào deeplink scheme.** Effort thấp, impact lớn.

---

## 4. Lợi ích cho MoMo

### Lợi ích trực tiếp

| # | Lợi ích | Chi tiết |
|---|---|---|
| 1 | **Tăng transaction volume** | User có lý do thanh toán qua MoMo thay vì tiền mặt/bank app: nhận cashback |
| 2 | **Revenue từ commission** | MoMo nhận 15-35% commission mỗi giao dịch qua deal (tùy kênh) |
| 3 | **Deal content miễn phí** | Chúng tôi cung cấp deal catalog → MoMo show trong app → tăng giá trị cho user |
| 4 | **Thêm merchant** | Merchant chưa có MoMo Merchant Account → chúng tôi hỗ trợ onboard → MoMo thêm merchant |
| 5 | **User engagement** | User mở MoMo thường xuyên hơn để check cashback, tìm deal |

### MoMo nhận bao nhiêu?

```
Ví dụ: 1,000 giao dịch/ngày × 300K trung bình × commission 2.5%

  Commission pool/ngày: 7,500,000đ
  MoMo nhận (20-35%):  1,500,000 - 2,625,000đ/ngày
                      = 45M - 79M/tháng

  Scale lên 10,000 giao dịch/ngày:
  MoMo nhận:          = 450M - 790M/tháng
```

### Chi phí cho MoMo

**Phase 1: ZERO.**

Chúng tôi sử dụng API MoMo có sẵn. MoMo chỉ cần cấp Partner Account.

---

## 5. Flow kỹ thuật theo từng tình huống

### 5.1 S1: MoMo User + MoMo Merchant (TRACK TỰ ĐỘNG — không cần QR)

**Điều kiện:** Merchant có MoMo Merchant Account + User thanh toán bằng MoMo wallet

**Phase 1: Webhook subscription — track tự động**

```
User đến Highland Coffee
  → Quét QR MoMo gốc của merchant (như bình thường)
  → Thanh toán bằng MoMo wallet
  → MoMo biết CẢ HAI: momo_user_id + merchant_id
  → MoMo webhook → AT-Scan-and-Go:
    {trans_id, merchant_id, momo_user_id (hashed), amount, status}
  → AT-Scan-and-Go match: merchant có deal + user đã đăng ký?
  → Ghi nhận commission → User nhận notification cashback

User KHÔNG CẦN LÀM GÌ KHÁC ngoài thanh toán.
API MoMo: Webhook subscription (đăng ký listen tại merchant)
MoMo effort: Thấp
```

**Phase 2: Linked Account — zero friction hoàn toàn**

```
SETUP 1 LẦN:
  User liên kết MoMo ↔ AT-Scan-and-Go (OAuth consent)

SAU ĐÓ:
  User thanh toán bình thường tại bất kỳ merchant có deal
  → MoMo auto-match: user đã link + merchant có deal
  → Webhook → AT-Scan-and-Go → cashback!

API MoMo: OAuth + Transaction subscription + Webhook
MoMo effort: Trung bình (cần cung cấp OAuth + subscription API)
```

**Lưu ý:** QR AT-Scan-and-Go vẫn có thể đặt tại cửa hàng S1 để quảng bá deal, nhưng KHÔNG bắt buộc cho tracking.

---

### 5.2 S2: Một bên KHÔNG dùng MoMo → CẦN QR AT-Scan-and-Go

**Điều kiện:** User dùng bank app (S2a) HOẶC merchant chỉ có QR bank (S2b). Thiếu thông tin 1 phía → cần QR AT-Scan-and-Go.

**Cách 1 (Best case): MoMo deeplink + tracking params**

```
QR sticker AT-Scan-and-Go tại cửa hàng chứa MoMo deeplink:

  S2a: momo://pay?receiver=MOMO_HIGHLAND_001
              &utm_source=at-scan-and-go
              &utm_campaign=DEAL_001
              &partner_ref=PLT_xxx

  S2b: momo://pay?receiver=VCB_123456789
              &utm_source=at-scan-and-go
              &utm_campaign=DEAL_001
              &partner_ref=PLT_xxx

User quét QR → MoMo app mở trực tiếp (1 bước!)
  → Thanh toán → MoMo webhook có partner_ref → AT-Scan-and-Go track!

MoMo cần: Deeplink nhận thêm utm/partner params + trả lại trong webhook
Effort: Thấp (chỉ thêm params vào deeplink scheme có sẵn)
UX: Tốt nhất — user quét 1 lần → thẳng MoMo
```

**Cách 2 (Fallback): AT-Scan-and-Go web redirect**

```
QR sticker AT-Scan-and-Go tại cửa hàng chứa URL:

  https://at-scan-and-go.com/pay/HIGHLAND?ref=PLT_xxx

User quét QR → Mở web AT-Scan-and-Go
  → "Highland Coffee • Cashback 5%"
  → Bấm "Thanh toán qua MoMo"
  → AT-Scan-and-Go gọi Payment Gateway (S2a) hoặc redirect deeplink (S2b)
  → MoMo app mở → Thanh toán → Webhook → AT-Scan-and-Go track!

MoMo cần: Không gì đặc biệt
UX: Tốt, thêm 1 bước web so với Cách 1
```

**Cách 3 (Dài hạn, chỉ S2b): Hỗ trợ merchant mở MoMo Merchant Account**

```
AT-Scan-and-Go hỗ trợ merchant đăng ký MoMo Merchant Account
  → Merchant chuyển từ S2b → S1
  → MoMo được thêm merchant mới miễn phí BD cost
```

**Lưu ý:** Linked Account (Phase 2) KHÔNG áp dụng cho S2 vì thiếu thông tin 1 phía.

---

### 5.3 Tổng hợp: So sánh S1 vs S2

| | S1 (MoMo + MoMo) | S2 (Một bên không MoMo) |
|---|---|---|
| **Tracking** | ✅ Tự động qua webhook | ✅ Qua QR AT-Scan-and-Go |
| **QR AT-Scan-and-Go** | Không bắt buộc (chỉ quảng bá) | **Bắt buộc** (tracking) |
| **Phase 2: Linked Account** | ✅ Zero friction | ❌ Không áp dụng |
| **API MoMo** | Webhook subscription (có sẵn) | Deeplink + webhook params |
| **MoMo effort** | Thấp → Trung bình (Phase 2) | Thấp |

**Điểm mấu chốt:**
- S1 = best case: user thanh toán bình thường → deal tự ghi nhận (đúng tinh thần Scan & Go)
- S2 = cần QR AT-Scan-and-Go, nhưng vẫn đơn giản (chỉ thêm 1 bước quét QR)
- Chiến lược: ưu tiên merchant có MoMo Account → tỷ lệ S1 cao → track tự động nhiều nhất

---

### 5.5 Kênh bổ sung: Deal hiển thị trong app MoMo (Phase 2+)

```
MoMo app hiển thị deal từ AT-Scan-and-Go:

  ┌─────────────────────────────┐
  │  Deals gần bạn              │
  │  ┌─────────────────────┐    │
  │  │ Highland Coffee     │    │
  │  │ Cashback 5%         │    │
  │  │ Bill từ 100K        │    │
  │  └─────────────────────┘    │
  │  ┌─────────────────────┐    │
  │  │ Pizza 4P's          │    │
  │  │ Cashback 3%         │    │
  │  └─────────────────────┘    │
  └─────────────────────────────┘

  User chọn deal → thanh toán → auto track (S1 flow)

  API: AT-Scan-and-Go cung cấp Deal Catalog API
  MoMo pull deal list → hiển thị trong app
```

---

## 6. Mô hình commission

### Chia sẻ commission

```
User thanh toán 500,000đ tại Highland Coffee
Commission rate: 3%
Commission pool: 500,000 × 3% = 15,000đ

  ├── MoMo:      3,000đ  (20%)
  ├── AT-Scan-and-Go:   7,500đ  (50%)
  └── User:       4,500đ  (30%) ← cashback
```

### Tỷ lệ chia theo kênh

| Kênh | Ai mang khách | MoMo nhận | AT-Scan-and-Go nhận | User nhận |
|---|---|---|---|---|
| Kênh AT-Scan-and-Go (QR AT-Scan-and-Go) | AT-Scan-and-Go | 15% | 55% | 30% |
| Kênh MoMo (deal trong MoMo app) | MoMo | 35% | 35% | 30% |
| Kênh MoMo (linked account, user quét QR gốc) | Shared | 25% | 45% | 30% |

> Ai mang khách → nhận nhiều hơn. User luôn nhận 30%.
> Tỷ lệ có thể thương lượng.

### Settlement

```
T+0:   Giao dịch xảy ra     → Commission: PENDING
T+1:   MoMo webhook         → Commission: CONFIRMED
T+14:  Hết refund window    → Commission: FINALIZED
T+15:  MoMo settlement      → chuyển commission cho AT-Scan-and-Go
```

---

## 7. Tích hợp kỹ thuật

### API MoMo chúng tôi sử dụng

| # | API | Mục đích | Kênh |
|---|---|---|---|
| 1 | **Payment Gateway** - create order | Tạo payment request khi user quét QR AT-Scan-and-Go | Kênh AT-Scan-and-Go |
| 2 | **Payment Gateway** - webhook/IPN | Nhận notification giao dịch thành công/thất bại/refund | Cả 2 kênh |
| 3 | **Payment Gateway** - query status | Fallback check trạng thái giao dịch | Cả 2 kênh |
| 4 | **OAuth / User consent** | User link tài khoản MoMo ↔ AT-Scan-and-Go | Kênh MoMo |
| 5 | **Transaction subscription** | Đăng ký listen giao dịch tại merchant list | Kênh MoMo |
| 6 | **Reconciliation** | Đối soát daily | Cả 2 kênh |
| 7 | **Disbursement** | Chuyển cashback vào MoMo wallet user | Cả 2 kênh |
| 8 | **Deep link** | Redirect user từ web → MoMo app thanh toán | Kênh AT-Scan-and-Go |

### Data chúng tôi cần từ webhook

```json
{
  "trans_id": "MoMo transaction ID",
  "partner_ref_id": "PLT_tracking_xxx",
  "merchant_id": "MOMO_MERCHANT_ID",
  "amount": 500000,
  "status": "SUCCESS | FAILED | REFUNDED",
  "payment_method": "WALLET | BANK_TRANSFER",
  "hashed_user_id": "hash_xxx",
  "timestamp": "2026-03-21T10:30:00+07:00"
}
```

**Lưu ý:** Chúng tôi KHÔNG cần thông tin cá nhân user (tên, SĐT, CCCD). Chỉ cần `hashed_user_id` để map với tài khoản AT-Scan-and-Go.

### Data chúng tôi cung cấp cho MoMo

```
Deal Catalog API:
GET /api/deals?city=HCM&category=fnb

Response:
[
  {
    "deal_id": "DEAL_001",
    "merchant_name": "Highland Coffee",
    "momo_merchant_id": "MOMO_HIGHLAND_001",
    "cashback_percent": 5,
    "min_amount": 100000,
    "max_cashback": 50000,
    "valid_until": "2026-06-30",
    "locations": ["Q1", "Q3", "Q7"],
    "category": "fnb"
  }
]
```

---

## 8. Kế hoạch triển khai với MoMo

### Phase 1: Pilot (Tháng 1-3)

| Tuần | Đầu việc | MoMo hỗ trợ | Effort MoMo |
|---|---|---|---|
| 1 | Ký NDA + hợp tác | Ký NDA | Thấp |
| 1-2 | Cấp Partner Account + API credentials | Cấp account sandbox + production | Thấp |
| 2-3 | Technical alignment meeting | 1 buổi với MoMo API team | Thấp |
| 3-8 | AT-Scan-and-Go build + tích hợp | Hỗ trợ kỹ thuật nếu có issue | Thấp |
| 8-12 | Pilot 20 merchant | - | - |

**MoMo effort Phase 1: < 1 tuần tổng cộng**

### Phase 2: Scale (Tháng 4-6)

| Đầu việc | MoMo hỗ trợ | Effort MoMo |
|---|---|---|
| Linked Account | Cung cấp OAuth consent flow + transaction subscription | Trung bình |
| Deal trong MoMo app | Hiển thị deal từ AT-Scan-and-Go deal catalog API | Trung bình |
| Disbursement | Cung cấp API chuyển cashback vào wallet user | Thấp |

### Phase 3: MoMo Mini App (Tháng 7-12)

| Đầu việc | MoMo hỗ trợ | Effort MoMo |
|---|---|---|
| Mini App access | Cấp quyền build Mini App trong MoMo ecosystem | Trung bình |
| Auto-match engine | MoMo auto-match giao dịch linked user + merchant deal | Trung bình |
| Push notification | Notify user khi nhận cashback | Thấp |

---

## 9. Tại sao hợp tác với chúng tôi?

### Chúng tôi mang gì cho MoMo?

| # | Giá trị | Chi tiết |
|---|---|---|
| 1 | **Merchant network** | Chúng tôi có BD team deal trực tiếp merchant. MoMo không cần đầu tư thêm BD |
| 2 | **Deal content** | Deal catalog hấp dẫn → tăng giá trị app MoMo cho user |
| 3 | **Transaction volume** | Mỗi deal = thêm giao dịch qua MoMo (thay vì tiền mặt/bank) |
| 4 | **Merchant onboarding** | Merchant chưa có MoMo → chúng tôi hỗ trợ đăng ký → MoMo thêm merchant |
| 5 | **Revenue share** | MoMo nhận 15-35% commission mỗi giao dịch, zero effort |

### Chúng tôi KHÔNG cạnh tranh với MoMo

- Không build ví điện tử
- Không xử lý thanh toán
- Không thu thập PII user
- Chúng tôi là **deal layer bổ sung** trên hệ sinh thái MoMo

### So sánh: MoMo tự build vs Hợp tác

| Hạng mục | MoMo tự build | Hợp tác với chúng tôi |
|---|---|---|
| BD team deal merchant | Cần tuyển + train | Chúng tôi đã có sẵn |
| Deal management system | Cần develop | Chúng tôi đã có sẵn |
| Time to market | 6-12 tháng | 2-3 tháng |
| Chi phí | Cao (team + dev + ops) | Thấp (revenue share) |
| Risk | Cao (chưa chứng minh) | Thấp (pilot trước) |
| Cross-platform potential | Không (chỉ MoMo) | Có (chúng tôi có thể mang merchant deal cho cả ZaloPay, VNPay → lợi thế cho merchant → dễ acquire) |

---

## 10. Anti-fraud & Bảo mật

| Biện pháp | Mô tả | Ai chịu trách nhiệm |
|---|---|---|
| Settlement delay T+14 | Commission chỉ finalize sau 14 ngày (cover refund) | AT-Scan-and-Go |
| Velocity check | Max N giao dịch/user/merchant/ngày | AT-Scan-and-Go |
| Min amount | Deal chỉ apply cho giao dịch từ X đồng | AT-Scan-and-Go |
| Refund webhook | MoMo notify khi refund → AT-Scan-and-Go rollback commission | MoMo (webhook) + AT-Scan-and-Go (rollback) |
| Daily reconciliation | Đối soát giao dịch MoMo vs AT-Scan-and-Go records | AT-Scan-and-Go (chạy) + MoMo (data) |
| User data privacy | Chỉ dùng hashed_user_id. Không lưu PII | AT-Scan-and-Go |
| Scoped consent | Linked account chỉ track tại merchant có deal | MoMo (enforce) |

---

## 11. Bước tiếp theo

| # | Action | Timeline |
|---|---|---|
| 1 | Meeting kick-off với MoMo Business Partnership | Tuần 1 |
| 2 | Ký NDA | Tuần 1 |
| 3 | MoMo cấp Sandbox Partner Account | Tuần 2 |
| 4 | Technical alignment (AT-Scan-and-Go dev ↔ MoMo API team) | Tuần 2-3 |
| 5 | AT-Scan-and-Go hoàn thành tích hợp sandbox | Tuần 4-6 |
| 6 | MoMo cấp Production Account | Tuần 6 |
| 7 | Pilot 20 merchant | Tuần 7-12 |
| 8 | Review kết quả, quyết định Phase 2 | Tuần 12 |

**Contact:**
- [Tên] - CEO/BD Lead - [SĐT] - [Email]
- [Tên] - CTO/Tech Lead - [SĐT] - [Email]

---

*Tài liệu chuẩn bị cho meeting với MoMo Business Partnership.*
*Số liệu commission là đề xuất ban đầu, có thể thương lượng.*
