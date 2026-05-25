# Ambassador — Frontend per-Partner ↔ Sự kiện (đối chiếu)

> Đối chiếu folder frontend trong `accesstrade-projects/ambassabor/` với sự kiện thực tế trên API.
> Mỗi folder FE là một **build per-partner** (white-label, phân biệt qua `APP_NAME`/`PARTNER_ID` trong `config/`).
> Mốc thời gian: hôm nay **2026-05-21**. Các folder partner cùng commit `2026-04-14` (chỉ `frontend`=05-17, `lusso`=04-17).

## Bảng đối chiếu Frontend ↔ Event

| Folder FE | APP_NAME | Partner trên API | Event gần nhất (endAt) | #active / #total | Đánh giá status |
|---|---|---|---|---|---|
| `frontend` | KOC Ambassador (chung) | ACCESSTRADE | 2026-12-31 | 12/15 | 🟢 **Đang chạy** — FE chung, Creator For Việt Nam còn active |
| `creatorvn` | KOC Ammbassador | ACCESSTRADE (biến thể) | 2026-12-31 | 12/15 | 🟢 **Đang chạy** — dùng chung pool ACCESSTRADE |
| `hdbank` | HDBank Creator | HDBank | 2026-04-15 | 8/10 | 🟡 **Vừa hết** — event cuối (FIFA WC) end 15/04, trong T4 |
| `lusso` | Lusso Saigon Ambassador | MEGALIVE - LUSSO ON AIR | 2026-05-06 | 2/3 | 🟡 **Vừa hết** — Livestream/Video LUSSO end 06/05 |
| `turborg` | Tuborg Creators | Tuborg | 2026-07-31 | 2/2 | 🟢 **Đang chạy** — 2 event dài hạn đến 31/07 |
| `vpbank` | VPBank Prime+ | VPbank | 2026-11-23 | 13/13 | 🟢 **Đang chạy** — GO VIRAL mới mở 19/05, kéo đến 09/2026 |
| `vng` | VNGGames Creators | VNGGames | 2025-11-25 | 40/40 | ⚪ **Cũ** — event cuối end 11/2025, không có gì trong T4–T5/2026 |
| `wildrift` | WILD Creators | _(không có trên API)_ | — | — | ⚪ **Không có event** — có thể VNGGames Wild Rift, chưa tạo campaign |
| `tpbank` | TPBANK - Creator | TPBank | 2025-12-31 | 5/6 | ⚪ **Cũ** — các chiến dịch "TẠM DỪNG", end cuối 12/2025 |
| `mbbank` | MB Studio | MB studio | 2025-12-04 | 13/16 | ⚪ **Cũ** — phần lớn "đã dừng", không có T4–T5/2026 |
| `anker` | Anker Innovations | Anker Innovations | 2026-01-18 | 2/3 | ⚪ **Cũ** — event cuối end 01/2026 |
| `flamingo` | Flamingo Creators | Flamingo | 2025-12-29 | 1/1 | ⚪ **Cũ** — end 12/2025 |
| `vnpay` | VNPAY | VNPAY Taxi | 2024-12-08 | 1/2 | ⚪ **Cũ** — end 12/2024 |
| `yody` | YODY | Yody | 2024-12-31 | 0/14 | ⚪ **Ngừng** — toàn bộ 14 event inactive, end ≤ 2024 |
| `creator-vietnam` | _(không rõ)_ | ACCESSTRADE? | — | — | ⚠️ Cần xác nhận — không có config APP_NAME rõ ràng |

### Kết luận: FE còn "active" tương ứng có sự kiện active (gồm cả vừa hết trong T4–T5)

**🟢 Đang chạy (event active, endAt ≥ hôm nay):**
- `frontend` + `creatorvn` (ACCESSTRADE — Creator For Việt Nam)
- `vpbank` (VPBank — GO VIRAL, mới nhất)
- `turborg` (Tuborg — dài hạn đến 07/2026)

**🟡 Active nhưng vừa kết thúc trong T4–T5 (vẫn nên tính là "live gần đây"):**
- `hdbank` (HDBank — FIFA WC, end 15/04)
- `lusso` (MEGALIVE LUSSO — end 06/05)

**⚪ Cũ / không có sự kiện trong T4–T5/2026 (FE còn trong repo nhưng partner không hoạt động):**
- `vng`, `tpbank`, `mbbank`, `anker`, `flamingo`, `vnpay`, `yody`, `wildrift`

### Partner CÓ event trong T4–T5 nhưng CHƯA có folder FE riêng
> (đang dùng `frontend` chung hoặc chưa build white-label)

KATINAT (end 18/07, 14 active ⭐), Traphaco, Lazada, Nha Khoa Parkway, VitaDairy,
Highlands Coffee, Aristino, Con Cưng, Hội Mê Phở, FPT Shop, VNSHOP, Vietnam Airlines,
Nation Care, BlueStone _(inactive)_, TIKI _(inactive)_.

→ Đáng chú ý: **KATINAT** là nhãn hoạt động mạnh nhất (14 event active, mới nhất đến 18/07) nhưng **chưa có folder FE riêng**.

---

# Ambassador — Sự kiện theo Partner (Tháng 4–5/2026)

> Nguồn: `GET /api/admin/events` (ambassador.koc.com.vn) — chụp ngày **2026-05-21**.
> Tổng cộng **204 events** trong hệ thống. Tất cả đều type `view_boost`.
> Tiêu chí lọc dưới đây: sự kiện có khoảng thời gian (startAt → endAt) **giao với 01/04–31/05/2026**.

## 1. Đang CHẠY tại thời điểm chụp (2026-05-21, status=active, endAt ≥ hôm nay)

| Partner | Sự kiện | Bắt đầu | Kết thúc |
|---|---|---|---|
| Traphaco | TRAPHACO AMBASSADOR - ĐẠI SỨ TRAPHACO | 2026-05-19 | 2026-06-30 |
| VPbank | VPBANK GO VIRAL - DEAL XỊN MỖI NGÀY, KIẾM TIỀN LIỀN TAY | 2026-05-19 | 2026-09-30 |
| VPbank | VPBANK GO VIRAL POST - DEAL XỊN MỖI NGÀY, KIẾM TIỀN LIỀN TAY | 2026-05-19 | 2026-09-30 |
| VPbank | Test (event test, end xa 2026-11) | 2024-09-30 | 2026-11-23 |
| Highlands Coffee | HighlandsĐI Referral | 2026-05-17 | 2026-06-18 |
| KATINAT | CHIẾN DỊCH: Trải nghiệm Không Gian, Check-in Cùng KATINAT | 2026-04-17 | 2026-07-18 |
| KATINAT | CHIẾN DỊCH: Cùng Tằm - Dâu tằm chín mọng… | 2026-05-13 | 2026-06-05 |
| KATINAT | KATINAT VIRAL THREADS: Cùng Tằm - Dâu tằm chín mọng… | 2026-05-13 | 2026-05-21 (hết hôm nay) |
| Con Cưng | CON CƯNG KHAI TRƯƠNG 220+ CỬA HÀNG MIỀN BẮC | 2026-05-06 | 2026-05-21 (hết hôm nay) |
| Nha Khoa Parkway | Mẹ chăm nụ cười nhỏ, con mở thế giới to | 2026-05-14 | 2026-06-15 |
| Nha Khoa Parkway | Đồng hành chăm sóc răng miệng cho cả gia đình | 2026-05-14 | 2026-06-15 |
| Lazada | VIRAL POST: LAZADA TRỢ GIÁ ĐỘC QUYỀN - HOÀN TIỀN SIÊU "ĐẢ" | 2026-05-14 | 2026-06-17 |
| Lazada | VIRAL VIDEO: LAZADA TRỢ GIÁ ĐỘC QUYỀN - HOÀN TIỀN SIÊU "ĐÃ" | 2026-05-14 | 2026-06-17 |
| VitaDairy | GỬI TRAO DINH DƯỠNG… CÙNG SỮA OGGI | 2026-04-15 | 2026-06-16 |
| Aristino | BST XUÂN HÈ 2026 ARISTINO - TIẾP NỐI HUYỀN THOẠI | 2026-04-14 | 2026-05-31 |
| Hội Mê Phở | Biến tấu đơn giản với Phở Cung Đình… | 2026-04-21 | 2026-05-24 |
| ACCESSTRADE | CHƯƠNG TRÌNH CREATOR FOR VIỆT NAM | 2026-05-05 | 2026-12-31 |
| Tuborg | CHƠI PHẢI TỚI! | 2025-05-19 | 2026-07-31 |
| Tuborg | SĂN THÊM NẮP - TRÚNG GẤP TRĂM | 2025-05-19 | 2026-07-31 |

## 2. Có hoạt động trong T4–T5 nhưng ĐÃ KẾT THÚC trước 2026-05-21 (active, end đã qua)

| Partner | Sự kiện | Bắt đầu | Kết thúc |
|---|---|---|---|
| Aristino | NƯỚC HOA NAM ARISTINO PARIS AMBASSADOR | 2026-04-08 | 2026-05-20 |
| FPT Shop | CHIẾN DỊCH RẺ HƠN KHI MUA KÈM SIM | 2026-05-05 | 2026-05-20 |
| Highlands Coffee | HIGHLANDSĐI AMBASSADOR | 2026-04-22 | 2026-05-11 |
| KATINAT | NON SÔNG LIỀN MỘT DẢI… DỆT GẤM VÓC TỰ HÀO (chiến dịch) | 2026-04-17 | 2026-05-09 |
| KATINAT | NON SÔNG LIỀN MỘT DẢI… (viral threads) | 2026-04-17 | 2026-05-09 |
| KATINAT | Cùng KATINAT khám phá Matcha Bắp-bi (chiến dịch) | 2026-03-17 | 2026-04-09 |
| KATINAT | Cùng KATINAT khám phá Matcha Bắp-bi (viral threads) | 2026-03-17 | 2026-04-11 |
| MEGALIVE - LUSSO ON AIR | CHIẾN DỊCH LIVESTREAM \| LUSSO SAIGON | 2026-03-17 | 2026-05-06 |
| MEGALIVE - LUSSO ON AIR | CHIẾN DỊCH VIDEO \| LUSSO SAIGON | 2026-03-17 | 2026-05-06 |
| Vietnam Airlines | Vietnam Airlines Ambassador | 2026-03-23 | 2026-04-23 |
| VNSHOP | VNSHOP AMBASSADOR: SÁNG TẠO VIDEO… | 2026-02-28 | 2026-04-24 |
| HDBank | Cùng thẻ HDBank Visa đi Mỹ xem FIFA World Cup 2026 | 2026-01-31 | 2026-04-15 |
| Nation Care | NATIONAL CARE CREATORS \| DINH DƯỠNG TRAO ĐI XA… | 2026-01-13 | 2026-04-01 |
| ACCESSTRADE | Test referral ambass (event test) | 2025-08-31 | 2026-05-01 |

## 3. Có thời gian giao T4–T5 nhưng đang INACTIVE (không kích hoạt)

| Partner | Sự kiện | Bắt đầu | Kết thúc |
|---|---|---|---|
| BlueStone | CHIẾN DỊCH BLUESTONE - BỀN BỈ SẺ CHIA | 2026-05-14 | 2026-08-15 |
| Con Cưng | CON CƯNG KOC CAMP 2026 | 2026-04-19 | 2026-05-31 |
| TIKI | TIKI AMBASSADOR | 2026-05-19 | 2026-12-31 |
| Lazada | LAZADA - TMALL CREATORS - VIRAL THREADS TẾT | 2026-01-01 | 2026-05-31 |

## Tổng kết theo Partner (có sự kiện giao T4–T5/2026)

**Partner còn sự kiện ĐANG CHẠY (active, chưa kết thúc):**
- KATINAT (2 còn chạy, mạnh nhất về số lượng)
- VPbank (3, gồm 1 event test)
- Nha Khoa Parkway (2)
- Lazada (2 active)
- Tuborg (2, dài hạn đến 2026-07)
- Traphaco, Highlands Coffee, VitaDairy, Aristino, Con Cưng, ACCESSTRADE, Hội Mê Phở (mỗi bên ≥1)

**Partner chỉ có sự kiện đã kết thúc trong T4–T5 (không còn chạy):**
- Aristino (nước hoa — đã end 20/05), FPT Shop, Highlands Coffee (HIGHLANDSĐI),
  MEGALIVE - LUSSO ON AIR, Vietnam Airlines, VNSHOP, HDBank, Nation Care, ACCESSTRADE (test)

**Partner inactive:** BlueStone, Con Cưng (KOC Camp), TIKI, Lazada (Tết)

### Ghi chú
- Hai event "Test" / "Test referral ambass" của VPbank và ACCESSTRADE là dữ liệu test, nên loại khi báo cáo kinh doanh.
- Một số partner có nhiều campaign song song (KATINAT, VNGGames ở các tháng khác, Lazada) — đây là các nhãn hoạt động liên tục nhất trên platform.
