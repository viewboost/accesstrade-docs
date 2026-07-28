# Booking trên CreatorOS — Roadmap chung

> Bước tiếp theo của [booking-tren-creator-os.md](./booking-tren-creator-os.md). Mục tiêu: chốt **mô hình cốt lõi** + **thứ tự triển khai** trước khi phân rã task chi tiết.
>
> **2 ràng buộc đã chốt với founder (2026-07-17):**
> 1. **"Ambassador" = content-campaign trong creator-os** (`CampaignType.CONTENT`) — CÙNG codebase. Nâng cấp dùng chung xây thẳng vào module content-campaign TRƯỚC, booking kế thừa code thật (đúng tinh thần "gò về một mối").
> 2. **Ưu tiên luồng "creator tự làm" trước** (marketplace đồng-giá, creator tự đăng ký → nộp demo → nộp bài). **Agency/vendor đẩy về phase sau.**

---

## 1. Mô hình cốt lõi

### 1.1. Ba tầng kiến trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 3 — LÕI BOOKING (xây mới, booking-riêng)                        │
│   BookingDeal (cost/price + phí + trạng thái deal + gói)             │
│   Negotiation · Package payment · Financial Firewall · Agency(sau)   │
├─────────────────────────────────────────────────────────────────────┤
│ TẦNG 2 — KHUNG CAMPAIGN DÙNG CHUNG (nâng cấp cho CẢ content + booking)│
│   Campaign · CampaignVersion · CampaignEnrollment(per-kênh) · Budget  │
│   + Pre-publish demo approval · Brief builder · Video-in-submission   │
├─────────────────────────────────────────────────────────────────────┤
│ TẦNG 1 — HẠ TẦNG NỀN (tái dùng gần nguyên)                           │
│   eKYC · Contract e-sign · Storage(video) · Payout/Ledger · RBAC/RLS  │
│   Notification · SocialAccount đa kênh · Audit                        │
└─────────────────────────────────────────────────────────────────────┘
```

**Nguyên tắc:** *tái dùng "danh từ hạ tầng" (Tầng 1) · nâng cấp "khung dùng chung" ở Tầng 2 để content-campaign hưởng trước · xây mới "động từ booking" ở Tầng 3.* Tầng 2 là nơi hiện thực hoá "nâng cấp đi cùng ambassador".

### 1.2. Sơ đồ thực thể (entity map)

```
Campaign (type = CONTENT | BOOKING)              ← reuse; type mở rộng
  ├─ CampaignVersion.config                       ← reuse; +brief, +priceMode, +tier price-band, +fees, +package
  ├─ CampaignBudget (hard-cap)                    ← reuse nguyên
  └─ CampaignEnrollment (creator + socialAccount) ← reuse; sàng lọc apply/invite/approve THEO KÊNH
        │
        ├─ Submission(kind = DEMO)  ⭐MỚI stage    ← pre-publish: upload video demo → duyệt (dùng lại review pipeline + storage)
        ├─ Submission(kind = LIVE)                 ← reuse: nộp URL bài đã đăng → nghiệm thu
        │
        └─ BookingDeal  ⭐MỚI (chỉ type=BOOKING)   ← cost(giá KOC) + price(giá client) + fees[] + trạng thái deal + gói/deliverable
              ├─ Contract(type=BOOKING)  ⭐+FK      ← reuse e-sign; thêm liên kết deal↔contract
              └─ Payout (package milestone)  ⭐+     ← reuse ledger; thêm giải ngân theo giá deal khi nghiệm thu

Agency + creator_users  ⭐MỚI (PHASE SAU)          ← pool ownership + fixed-fee/quota + phạt 8% + hoa hồng
```

### 1.3. Spine "creator tự làm" (luồng ưu tiên)

```
Creator thấy job (đồng-giá)
   → tự đăng ký THEO KÊNH  (CampaignEnrollment: APPLY_APPROVE)
   → admin duyệt hồ sơ (SLA)             [reuse enrollment + +SLA]
   → nhận brief                          [+brief builder]
   → upload DEMO video                   [+demo submission, reuse storage]
   → admin/brand duyệt demo (pre-publish)[+demo approval, reuse review pipeline]
   → ĐĂNG bài + nộp URL (LIVE)           [reuse submission]
   → nghiệm thu (nội dung/thời gian/số lượng, KHÔNG view) [reuse review]
   → chi tiền per-video                  [reuse payout/ledger]
```

> Ở phase đầu **đồng-giá**: `BookingDeal.cost` = giá niêm yết của campaign (deal tự tạo, KHÔNG đàm phán). Đàm phán/final-giá là lớp thêm ở Phase 2 — spine không đổi, chỉ bật thêm bước.

### 1.4. Trạng thái BookingDeal (thống nhất 2 loại)

```
(đồng-giá)                          (deal-giá — Phase 2 bật thêm nhánh trái)
                    ┌── OFFERED → NEGOTIATING → AGREED ──┐
  [auto] AGREED ────┴────────────────────────────────────┴──→ DEMO_PENDING
     → DEMO_APPROVED → PUBLISHED → VERIFIED → PAID
                                        └→ (thiếu/không đạt) → PARTIAL/PENALIZED
```

---

## 2. Phân loại nâng cấp — Shared (đi cùng content-campaign) vs Booking-riêng

### 2.1. 🟦 Shared — nâng cấp module content-campaign TRƯỚC, cả 2 cùng hưởng

> Đây là phần trả lời trực tiếp "cái nào làm trên ambassador trước rồi qua booking sau".

| # | Nâng cấp | Vì sao content-campaign cũng cần | Booking dùng lại |
|---|---|---|---|
| S1 | **Pre-publish demo/kịch bản approval** | Brand lớn (TCB/VPBank/Vin) yêu cầu duyệt-trước-đăng — meeting xác nhận | Bước demo trong spine booking |
| S2 | **Brief builder có cấu trúc** (do/don't, deliverable, hashtag, usage-rights, timeline) | Content campaign brief hiện sơ sài | Brief booking |
| S3 | **Video/asset upload vào submission** (không chỉ URL) | Content cũng cần proof/asset đôi khi | Upload demo video |
| S4 | **Enrollment SLA + channel scoring** (duyệt có hạn giờ, chấm kênh hợp campaign) | Sàng lọc content cũng cần | Sàng lọc booking |
| S5 | **Notification SLA/deadline reminder** | Nhắc hạn nộp/duyệt cho cả 2 | Nhắc hạn demo/đăng |

→ **5 hạng mục này build vào content-campaign trước** → vừa cải thiện sản phẩm đang có, vừa là nền cho booking. Đây là "đòn bẩy kép".

### 2.2. 🟥 Booking-riêng — content-campaign KHÔNG cần

| # | Chức năng | Ghi chú |
|---|---|---|
| R1 | **Giá per-creator (cost) + phí phụ** (card, image-usage, exclusivity, rush) | Content là đồng-giá theo metric |
| R2 | **Negotiation / final-giá** (báo giá → deal → admin chốt) | Chỉ deal-giá |
| R3 | **Package payment** (đủ N deliverable → giải ngân theo giá deal) | Khác reward-milestone-view |
| R4 | **Financial Firewall** (cost KOC vs price client, role cứng) | Chỉ có nghĩa khi có price > cost |
| R5 | **BookingDeal entity + state machine** | Xương sống booking |
| R6 | **Agency/Vendor** (pool ownership, fixed-fee/quota, phạt 8%, hoa hồng) | **ĐẨY PHASE SAU** |
| R7 | **Brand portal** (ADV tự thao tác) | **ĐẨY PHASE SAU** (AT đóng vai brand) |

---

## 3. Roadmap chung (phasing)

> Sizing tương đối (S/M/L) — chưa phải estimate chi tiết (để bước phân rã). Thứ tự bám: **creator tự làm trước → deal-giá → agency → brand portal.**

### Phase 0 — Nền dùng chung trên content-campaign  ·  size **M**
**Mục tiêu:** nâng cấp module content-campaign (Tầng 2) — sản phẩm hiện có tốt lên + tạo nền cho booking.
- S1 Pre-publish demo approval (state + review pipeline reuse)
- S2 Brief builder có cấu trúc
- S3 Video-in-submission (upload asset, không chỉ URL)
- S4 Enrollment SLA + channel scoring · S5 Notification SLA
**Reuse:** B (mở rộng nhẹ trên khung sẵn có). **Shared:** 100% dùng chung.
**DoD:** content-campaign chạy được luồng "gửi demo → duyệt → mới cho nộp bài".

### Phase 1 — Booking creator tự làm (đồng-giá) MVP  ·  size **L**  ·  ⭐ ƯU TIÊN
**Mục tiêu:** hiện thực spine "creator tự làm" với booking đồng-giá, admin tối thiểu.
- `CampaignType.BOOKING` + config booking trong version (priceMode=FIXED, tier price-band tham khảo)
- Marketplace: creator xem job → **tự đăng ký theo kênh** → admin duyệt (reuse enrollment + Phase 0 SLA)
- **BookingDeal** (bản tối giản: cost = giá niêm yết, auto-AGREED) — R5 ở mức cơ bản
- Luồng demo → duyệt → đăng → nộp URL → nghiệm thu (reuse Phase 0 + submission)
- Chi **per-video** (reuse payout/ledger) · e-contract per-job cơ bản (Contract type=BOOKING + FK)
**Reuse:** A+B nhiều; C ít (chỉ BookingDeal tối giản). **Deferred:** đàm phán, phí phụ, package, agency.
**DoD:** một creator tự đăng ký job đồng-giá → nộp demo → được duyệt → đăng → được chi tiền, end-to-end.

### Phase 2 — Deal-giá + phí + gói + firewall  ·  size **L**
**Mục tiêu:** phủ luồng deal-giá (AT sale-direct/creator báo giá) + đầy đủ mô hình tiền.
- R2 Negotiation + admin **final-giá** (bật nhánh OFFERED→NEGOTIATING→AGREED)
- R1 Phí phụ mở rộng (card, image-usage, exclusivity, rush) trên BookingDeal
- R3 Package payment (đủ N → giải ngân theo giá deal; auto per-video + bonus)
- **R4 Financial Firewall** — thiết kế cột cost/price + 2 permission `finance:cost:read`/`finance:price:read` **NGAY khi price xuất hiện** (rẻ lúc này, đắt nếu vá sau)
**Reuse:** C là chính. **DoD:** deal-giá chốt qua hệ thống, cost/price tách theo role, chi theo gói.

### Phase 3 — Agency / Vendor  ·  size **L**  ·  (đẩy sau theo chỉ đạo)
- R6: `creator_users` (bỏ UNIQUE `Creator.accountId`) — 1 account đại diện N creator
- Pool ownership (ghi nhận "KOC đến từ agency nào") · fixed-fee/quota · **phạt 8% giá trị vi phạm** · hoa hồng · ẩn với ADV
**DoD:** agency đăng nhập, quản lý pool, nhận KPI khoán, đối soát phạt/hoa hồng.

### Phase 4 — Brand portal  ·  size **M**  ·  (đẩy sau)
- ADV tự xem/duyệt kịch bản top-KOC, dashboard, export. (Hiện AT đóng vai brand → chưa cần.)

```
Phase 0 ──▶ Phase 1 (creator tự làm, đồng-giá) ──▶ Phase 2 (deal-giá+firewall) ──▶ Phase 3 (agency) ──▶ Phase 4 (brand)
  nền chung        ⭐ ƯU TIÊN                          tiền đầy đủ                   (sau)            (sau)
```

---

## 4. Lý do sắp thứ tự & phần hoãn

- **Creator tự làm (Phase 1) trước** vì gần content-campaign nhất (reuse cao nhất, ít C nhất) → ra giá trị nhanh, ít rủi ro. Đúng chỉ đạo founder.
- **Phase 0 trước Phase 1** vì demo-approval + brief là nền booking *và* nâng content-campaign — làm 1 lần lợi 2.
- **Financial Firewall (R4) thiết kế sớm** (Phase 2, ngay khi có `price`) dù agency ở Phase 3 — tách cost/price từ đầu rẻ, vá sau đắt (doc nội bộ `pmax-security-impact-analysis §B.3` đã cảnh báo).
- **Agency (Phase 3) & Brand portal (Phase 4) hoãn** theo chỉ đạo — nhưng `creator_users` là thay đổi schema nền (bỏ UNIQUE), nên **để lỗ hổng thiết kế sẵn** ở Phase 1 (không code, nhưng không chặn đường) để Phase 3 không phải refactor lớn.

## 5. Bước tiếp theo (đề xuất)

Phân rã **chi tiết Phase 0 + Phase 1** trước (data-model cụ thể cho `Submission(kind=DEMO)` + `BookingDeal` tối giản + `CampaignType.BOOKING` config; API; task theo convention creator-os 6 bước DoD). Các phase sau phân rã khi tới gần.

---
*Tạo 2026-07-17. Ràng buộc: ambassador=content-campaign (cùng codebase); creator-self-serve ưu tiên; agency/brand hoãn. Chưa phân rã task nhỏ (bước kế).*
