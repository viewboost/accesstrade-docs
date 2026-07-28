# Booking trên CreatorOS — Phân tích nghiệp vụ & đánh giá tái sử dụng

> **Mục tiêu tài liệu:** Trả lời câu hỏi của founder — "nếu làm Booking thì dựa vào creator-os như thế nào, tận dụng được bao nhiêu %".
> Đi theo 4 bước: ① viết lại đề bài gốc từ meeting → ② research chuẩn ngành → ③ chức năng lõi cần có → ④ creator-os đã hỗ trợ tới đâu.
>
> **Nguồn:** [meeting-note-0714.md](./meeting-note-0714.md) (trao đổi anh Vĩnh ↔ đội chị Vui/AT về booking) + code thật `pmax-projects/creator-os`.
> **Khác biệt với bộ [01-06]** trong thư mục cha: bộ cũ đóng khung trên nền **Ambassador (Go + Mongo)**; tài liệu này đóng khung lại trên **CreatorOS (TS/NestJS + Postgres RLS)** — nơi đã có sẵn 2 loại campaign (Content-metrics, Affiliate-deferred).

---

## ⚠️ Chuẩn hoá thuật ngữ (đọc trước — tránh hiểu nhầm)

Meeting note dùng một số từ lóng nội bộ dễ gây nhầm khi map sang code:

| Từ trong meeting | Nghĩa thật | Bẫy |
|---|---|---|
| **"KYC"** | = **KOC / Creator** (người sáng tạo nội dung) | ⚠️ KHÔNG phải eKYC/định danh. CreatorOS có module **eKYC thật** — dễ nhầm. Trong tài liệu này gọi thẳng là **Creator (KOC)**. |
| **"KYC portal"** | = **Creator portal** (`apps/portal-creator`) | Một trong 3 hệ thống: KYC portal / brand portal / admin portal |
| **"IT"** | = **đội vận hành nội bộ AT** (AM/ops), KHÔNG phải phòng công nghệ | "IT đàm phán với KYC" = AM đàm phán với creator |
| **"AM"** | Account Manager — người chăm creator | |
| **"ADV"** | Advertiser / nhãn hàng / brand | AT hiện **đóng vai brand** quản lý nhiều campaign |
| **"e-clip"** | đăng clip lên nền tảng (publish) | |
| **"final giá"** | admin chốt lại giá cuối theo thoả thuận 2 bên | Thao tác đặc trưng của booking |

---

## Bước 1 — Đề bài gốc (viết lại từ meeting note)

### 1.1. Bối cảnh & mục tiêu

- AT/Diso muốn **hệ thống hoá quy trình KOC Booking** đang chạy thủ công (Google Sheet + Zalo + Google Drive). Chỉ đạo anh Hưng: *"toàn bộ phải hệ thống hoá, không được làm Excel nữa"*.
- **Ưu tiên số 1:** tối ưu quy trình **nội bộ đội vận hành (IT/AM)** + tận dụng **pool KOC sẵn có của AT**.
- **Phạm vi portal:** chủ yếu **Creator portal + Admin portal**. **Brand portal → hoãn** (AT tự đóng vai brand; ADV thao tác rất ít, chủ yếu chỉ duyệt kịch bản top-KOC, và không thích đăng nhập hệ thống thứ 3 — họ quen xem Google Sheet tổng quan).
- **Định hướng hợp nhất:** founder kết luận *booking không khác Ambassador nhiều* → về lâu dài "gò" Ambassador và Booking về **một mối**. Ambassador đã có hình thức "**trả theo post**" = chính là booking **đồng giá**. Booking chỉ **thêm**: (a) **deal giá per-creator** + (b) bước **final giá**, còn lại là quy trình duyệt nội bộ nhiều bước mà Ambassador thực chất đã có.

### 1.2. Hai loại booking (khác nhau ở cách hình thành giá)

| Loại | Cách định giá | Ai chủ động | Ví dụ | Tương đương |
|---|---|---|---|---|
| **① Đồng giá (public/fixed)** | Giá niêm yết cố định/1 video | **Creator tự đăng ký** (marketplace) — mục tiêu để KOC *chủ động apply* thay vì AT đi tìm | "500k/video", "gói N video" | Ambassador "trả theo post" |
| **② Deal giá (negotiated)** | Đàm phán riêng từng creator, admin **final giá** | **AT sale-direct** từng KOC | KOC báo 5tr; tier-1 dao động 10–20tr; chốt X rồi admin sửa giá | Đặc trưng booking — **phần mới** |

Cả hai đi **chung một hệ thống booking**, chung luồng sàng lọc/duyệt; chỉ khác ở khâu "giá đã cố định sẵn" hay "phải đàm phán + final".

> Tầm nhìn: một campaign có thể **đồng thời** có **giá public** (auto đồng giá) *và* **skin tier customize** (deal riêng cho tier cao).

### 1.3. Luồng nghiệp vụ booking — "quy trình NGƯỢC"

Điểm mấu chốt: booking **duyệt TRƯỚC khi đăng** (pre-publish), ngược với creator thường (đăng xong mới review).

```
①  Sàng lọc / chấm điểm kênh   →  kênh có hợp campaign không?
    (proactive: AT chấm rồi mời • marketplace: KOC tự đăng ký hồ sơ)
②  Creator nộp form request     →  khai kênh (tên/follower/platform), báo giá (nếu apply)
③  Admin duyệt hồ sơ            →  SLA 4–5h làm việc, báo OK/không
④  Đàm phán & CHỐT GIÁ          →  admin "final giá" → update ngược lên Creator portal
⑤  Gửi brief + sản phẩm
⑥  (tuỳ tier) Duyệt kịch bản    →  KOC top / booking >3tr / brand mới: brand check script
⑦  KOC gửi DEMO/clip nháp       →  admin (hoặc brand) duyệt PRE-PUBLISH
⑧  Approve  →  KOC mới được ĐĂNG (e-clip)
⑨  Nghiệm thu                   →  đúng nội dung + đúng thời gian + đủ số lượng;
                                    verify clip đăng == clip demo đã duyệt (người check, không auto)
⑩  Thanh toán                   →  per-video / gói / bonus
```

So sánh với creator thường (Ambassador post-publish): *đăng xong → nhãn hàng + AT vào check ok/không*. Booking chèn thêm cụm ⑥⑦⑧ (duyệt kịch bản + demo trước khi đăng) và ④ (final giá). Founder xác nhận các bank lớn (TCB/VPBank/Vin) cũng chạy đúng luồng pre-publish này (submit link → duyệt case → verify chủ sở hữu → request tham gia campaign → duyệt → mới gửi video).

### 1.4. Mô hình định giá & thanh toán

- **Đơn vị trả:**
  - **Per-video** (phổ biến nhất): e-clip xong trả luôn, "toàn tiền cho video".
  - **Gói** (gói 3 / gói 5 video): phải đủ số lượng mới trả.
  - **Đề xuất kỹ thuật (anh Vĩnh):** *auto trả per-video trước* + *bonus khi đủ N clip* — tách phần "before" và "bonus" để không bị khoá cứng chính sách.
  - **Theo KPI:** mỗi video X tiền, HOẶC đạt KPI đủ N video.
- **Tier (theo follower):** top / macro (>100k) / medium (30–100k) / micro–UGC → mỗi tier có **KHOẢNG giá** (không phải giá cứng), vì còn phụ thuộc frame/chất lượng video/view. **Đàm phán giá TRƯỚC khi làm**; **không** sửa giá theo hiệu quả sau khi đăng.
- **Tiêu chí chấm video:** nội dung (bắt buộc) + đăng đúng thời gian chiến dịch + thời lượng (không gắt). **Không** chấm theo lượt view (khác Ambassador). Có quy định nền tảng.
- **Phí phụ (fees):**
  - **Card fee** (phí card).
  - **Phí sử dụng hình ảnh** (brand dùng hình ảnh KOC để truyền thông kênh thứ 3 / trong X tháng → tính thêm phí).
  - Brief có **yêu cầu đặc biệt** → customize giá.

### 1.5. Ngân sách & tranh chấp

- Brand giao campaign kèm **ngân sách + KPI + timeline**. **Ngân sách KHÔNG được lố** (hard cap tuyệt đối).
- **Tranh chấp khi budget gần cạn** (VD còn 1tr, 2 KOC cùng muốn): **ai được duyệt trước thắng** (hiện control thủ công). Marketplace tương lai: dùng **SLA duyệt** để xử lý công bằng.

### 1.6. Đa kênh (multi-channel)

- 1 KOC có nhiều kênh → mỗi kênh khai báo riêng (tên / follower / platform).
- Mỗi kênh = **một KPI riêng biệt** → **apply & duyệt theo TỪNG kênh** (không yêu cầu đủ 3 kênh mới trả).
- Conflict chỉ khi 2 kênh **trùng nội dung + hình ảnh** → chọn 1 trong các kênh. 3 kênh khác tuyến nội dung → nhận cả 3, ghi nhận 3 clip.

### 1.7. Bốn đối tượng (roles) & Agency/Vendor

**4 đối tượng:** ① Admin (AT ops) · ② Creator/KOC · ③ **Agency/Vendor** · ④ Brand/ADV *(hoãn)*.

**Agency/Vendor** (đội ngoài quản lý pool KOC) — nghiệp vụ phức tạp nhất cần lường trước:
- **Sở hữu / quản lý một pool profile creator.**
- **2 mô hình hợp tác:** (a) **giá theo từng KOC**; (b) **fixed fee theo tháng/quý** cho một **quota** (VD 15–20tr/tháng, gói 50–100 KOC/campaign).
- **Phạt vi phạm 8%** trên **giá trị vi phạm** khi không đạt KPI (VD giao 20 video/300tr, chỉ đạt 18 → *phần thiếu chưa trả* **+** *phạt 8% giá trị vi phạm*). Tiền phạt **không đánh thuế**, hạch toán tách riêng.
- **Ẩn với ADV:** brand không biết agency là ai (AT vẫn report cho ADV theo từng profile).
- **Xung đột ownership:** agency sở hữu profile, nhưng KOC đó về sau **có thể tự join hệ thống** → cần **pool ghi nhận "KOC này đến từ agency nào"** để đối soát hoa hồng agency.
- Bản chất agency ≈ **đội sales nội bộ (KYC-care)**: có KPI, quản lý danh sách KOC mình chăm → cần tầng quản lý nội bộ + phân KPI + đánh giá.
- Agency **ký hợp đồng công ty**, thanh toán qua công ty. Vận hành: agency đóng vai KOC nộp bài **HOẶC** khoán trắng KPI.
- **Nghiệm thu agency:** nghiệm thu từng clip đạt → trả tới đó; thiếu → chưa trả phần thiếu + phạt 8%.

> **Lưu ý dữ liệu:** KOC **không lên hệ thống cũng bình thường** — admin **tự import** hồ sơ (nhiều KOC "mẹ bỉm" không quen dùng mail/drive). Agency cũng vậy. → Hệ thống phải hỗ trợ **admin tạo/nhập hộ profile**.

### 1.8. Nộp bài & lưu trữ video

- Hiện tại: KOC gửi **link video / link Google Drive** (qua Zalo cho AM → AM tải lên Drive cho ADV check).
- Mong muốn: **hệ thống tự tạo thư mục Drive per creator + tự invite**, hoặc cho **upload thẳng lên platform** (hệ thống lo lưu trữ/server/dung lượng).
- **Duyệt tự động trên hệ thống** thay Zalo thủ công.
- **Verify tính toàn vẹn:** admin có trách nhiệm check **clip demo đã duyệt == clip đăng thật** — hiện **chưa auto được**, phải người xem lại.

### 1.9. Ngoài phạm vi / để sau

- **Brand portal** (ADV tự thao tác) → Phase sau. Trước mắt AT đóng vai brand.
- **Free card / affiliate free** → không thuộc booking (auto đăng, không quy trình duyệt) → bỏ qua.
- **Timeline dự án:** chưa chốt (chờ anh Vĩnh ↔ chị Vui thống nhất).

### 1.10. Chốt điểm mấu chốt (để bước 3–4 bám vào)

1. Booking = **campaign type mới** cạnh Content/Affiliate, chia sẻ ~phần lớn khung campaign.
2. Thêm **3 thứ chưa có**: (a) **giá chốt per-creator/per-enrollment** + đàm phán/final giá; (b) **duyệt DEMO pre-publish** (kịch bản → demo → approve → mới đăng); (c) **Agency/Vendor** (role + pool ownership + fixed-fee/quota + phạt 8% + hoa hồng).
3. Tận dụng sẵn: **enrollment apply→approve theo kênh**, **budget hard-cap**, **reward per-content / milestone / tier**, **versioning thể lệ**, **content review**.
4. Fees phụ (card / image-usage) + **package payment** (đủ N mới trả) là các nhánh cần mô hình hoá thêm.

---

## Bước 2 — Chuẩn ngành (research bổ sung)

> Research đa nguồn (Aspire/Grin/CreatorIQ/Upfluence docs + influencer-marketing guides). Bản đầy đủ: [creator-os/plans/reports/260717-influencer-booking-operations-research.md](../../../../pmax-projects/creator-os/plans/reports/260717-influencer-booking-operations-research.md). Dưới đây là phần **liên quan trực tiếp tới booking** + đối chiếu meeting.

### 2.1. Vòng đời chuẩn (8 stage) — khớp với luồng ngược ở §1.3

`Discovery/Shortlist → Outreach/Negotiation → Brief/Contract → Content Creation → Pre-Publish Approval → Publish → Verification/Reporting → Payment (net 15–30)`.

Điểm ngành nhấn mạnh trùng với meeting: **Pre-Publish Approval là stage "critical"** — creator gửi draft → brand review (chuẩn **48h/round, tối đa 2–3 round**) → greenlit → mới đăng. Đây chính là khâu ⑥⑦⑧ ở §1.3.

### 2.2. Booking vs Ambassador vs Affiliate (định vị chuẩn ngành)

| Khía cạnh | **Booking** | **Ambassador** | **Affiliate** |
|---|---|---|---|
| Cấu trúc giá | **Flat rate / deliverable** (đàm phán) | Retainer định kỳ + bonus | % commission trên sales |
| Deliverable | **Cố định** (1 Reel, 3 Stories) | Recurring, mờ | Bất kỳ post có link |
| **Pre-publish approval** | **BẮT BUỘC, chi tiết** | Tối giản (guideline) | Không / spot-check |
| Duyệt nội dung | Từng draft, 2–3 round | Post-publish audit | Không |
| Quan hệ | Giao dịch từng deal | Sâu, chiến lược | Giao dịch |

→ **Xác nhận quan điểm founder**: Ambassador "trả theo post" = một biến thể booking đồng giá; Booking khác chủ yếu ở **pre-publish approval bắt buộc** + **đàm phán giá per-deal**.

### 2.3. Định giá — đối chiếu meeting (validate + enrich)

| Thành phần | Chuẩn ngành | Đối chiếu meeting |
|---|---|---|
| **Base flat rate theo tier follower** | nano 0.5–2tr · micro 2–10tr · mid 10–30tr · macro 30–100tr · mega 100tr+ (VN 2024–26) | ✅ Khớp — meeting: top/macro>100k/medium 30–100k/micro-UGC, mỗi tier là **khoảng giá** |
| **Điều chỉnh** | +30–50% engagement cao · +50% nếu exclusivity · −20–30% creator mới | ✅ Khớp — meeting: giá còn phụ thuộc frame/chất lượng/view → đàm phán |
| **Usage rights / image usage fee** | +0% (1–3th, bundled) → **1–2x** (6–12th) → **2–3x** (vĩnh viễn) base | ✅ **Chính là "phí sử dụng hình ảnh"** meeting nêu (brand dùng hình KOC kênh 3 / X tháng) |
| **"Card fee" / boosting / whitelisting** | +1–3tr/post hoặc 10–20% ad spend | ✅ **Chính là "phí card"** meeting nêu |
| **Exclusivity fee** | +20–50% base (30–90 ngày) | ⚠️ Meeting chưa nhắc → **cần hỏi**: booking AT có ràng độc quyền không |
| **Rush / revision fee** | +20–50%/round vượt (>2–3 round hoặc <5 ngày) | ⚠️ Meeting: "max 2 lần revise" ở bộ cũ; nên chuẩn hoá số round + phí vượt |

**Kết luận:** cấu trúc phí booking chuẩn ngành = `base (theo tier) + [usage rights] + [card/boosting] + [exclusivity] + [rush]`. Meeting đã "chạm" 2 phí phụ chính (card, image-usage) → mô hình dữ liệu phí phụ nên **mở rộng được** chứ đừng hard-code 2 loại.

### 2.4. Agency/Vendor — chuẩn ngành xác nhận gần như 1:1 với meeting

| Điểm | Chuẩn ngành | Meeting |
|---|---|---|
| 2 mô hình hợp đồng | (A) per-creator rate + agency assist · (B) **fixed retainer + quota** ("100tr/th đảm bảo N creator/N post") | ✅ Y hệt: (a) giá theo từng KOC · (b) fix fee/tháng-quý cho gói 50–100 KOC |
| Commission agency | 10–25% (nano/micro cao hơn: 25–30%; mega thấp: 10–15%) | Meeting chưa nêu %, nhưng có "hoa hồng agency" → cần cấu hình được |
| **Penalty KPI** | % contract value theo volume/quality/compliance; **cap ~30%** | ✅ Meeting: **phạt 8% giá trị vi phạm** + phần thiếu chưa trả (8% là mức AT chọn, nằm trong dải ngành) |
| **Ownership** | **Scenario 2 phổ biến VN**: creator sở hữu, agency là *operator* | ✅ Meeting: agency sở hữu pool nhưng KOC có thể tự join → cần ghi nhận "KOC đến từ agency nào" |

→ Nghiệp vụ agency của AT **đúng chuẩn ngành**, không phải yêu cầu dị biệt. Model dữ liệu nên theo **Scenario 2** (creator = chủ sở hữu, agency = operator/nguồn giới thiệu), khớp luôn tinh thần RLS "chủ sở hữu" của creator-os (ADR-0007).

### 2.5. Thanh toán & nghiệm thu

- **2 mô hình chi**: **milestone** (VD 30% ký / 50% duyệt draft / 20% sau khi live 48h) hoặc **pay-per-deliverable** (đăng xong trả luôn, net 0–5). VN thiên **upfront cao hơn** (50–60%) do lo cash-flow; **không dùng escrow** (ma sát cao).
  - Meeting: phổ biến **e-clip xong trả luôn** (= pay-per-deliverable) + **gói phải đủ mới trả** (= milestone theo số lượng). → Cả 2 đều là chuẩn ngành.
- **Điều kiện nghiệm thu**: post còn live (≥7 ngày), metric đúng, đúng disclosure, đủ thời lượng, đăng đúng hạn. Trả thiếu/không trả khi: xoá bài sớm, bot view, sai brief.
  - Meeting: nghiệm thu = đúng nội dung + đúng thời gian + đủ số lượng (**không** chấm view). Khớp, chỉ bỏ tiêu chí view.

### 2.6. Manual vs Platform — cái AT đang đau & cái cần tự động hoá

- **Manual VN hiện tại** (đúng như AT): Google Sheet (rate card, tracker) + **Drive folder per creator nhận video** + Email brief + **Zalo** duyệt. Pain: không tập trung duyệt, loạn version (`final_FINAL_real.mp4`), miss deadline, khó đối soát thanh toán, **không audit trail**.
- **Platform (Aspire tự động ~90%)**: brief builder → **content approval workflow** (upload draft, review inline, version history, deadline timer) → **e-sign contract** → payment automation → analytics API. Turnaround **2–3 ngày** thay vì 7–30 ngày manual.
- → Đây chính là **lý do tồn tại** của dự án booking (chỉ đạo anh Hưng "bỏ Excel"). Các khối cần tự động hoá theo thứ tự đau: **(1) duyệt nội dung tập trung có version + trạng thái**, (2) lưu trữ video thay Drive/Zalo, (3) đối soát/thanh toán, (4) audit trail.

### 2.7. Brief booking chuẩn (checklist trường dữ liệu)

Meta (tên/client/timeline/budget/contact) · Product context · **Do's** (mention/hashtag/tag/giờ đăng) · **Don'ts** (cấm đối thủ trong X ngày, cấm claim vô căn cứ) · **Deliverables** (loại, số lượng, thời lượng, tỉ lệ khung, raw file, usage rights) · Creative direction (tone/style/reference) · **Compliance** (disclosure) · **Approval process** (hạn nộp draft, số round, SLA duyệt) · **Payment terms** (lịch chi, net term) · **Verification** (giữ live ≥7 ngày, KPI). → Dùng làm khung cho "brief builder" của booking campaign.

---

## Bước 3 — Chức năng lõi booking cần có

> Tổng hợp từ §1 (meeting) + §2 (chuẩn ngành), diễn giải ở tầng **nghiệp vụ** (chưa buộc vào creator-os). 10 khối chức năng; đánh dấu ⭐ = trụ cột riêng của booking (không có ở content/affiliate).

| # | Khối chức năng | Nội dung lõi |
|---|---|---|
| **1** | **Job/Campaign booking** | Tạo job: brief, **ngân sách hard-cap**, KPI, timeline, nền tảng, quota. 2 chế độ giá: **đồng giá (public)** + **deal giá (per-creator)**. Bảng **tier theo follower** (top/macro/medium/micro-UGC) → **khoảng giá** tham khảo cho đàm phán. |
| **2** | **Sàng lọc & tuyển chọn** | Chấm điểm kênh hợp campaign. 3 luồng vào: **admin mời (INVITE)** · **creator tự apply (marketplace)** · **auto (đồng giá public)**. Duyệt hồ sơ theo **SLA** (4–5h). **Apply/duyệt theo từng KÊNH.** Xử lý tranh chấp khi budget cạn (ai duyệt trước). |
| **3** ⭐ | **Đàm phán & chốt giá** | Creator báo giá → 2 bên deal → **admin final giá** (per-creator/per-kênh) → đẩy ngược lên creator portal. **Phí phụ mở rộng được**: card fee, image-usage fee, (exclusivity, rush). Không sửa giá theo hiệu quả sau đăng. |
| **4** ⭐ | **Duyệt PRE-PUBLISH** | (tuỳ tier) duyệt **kịch bản** → creator gửi **demo/clip nháp** → admin/brand **duyệt trước** → approve mới cho đăng. Số round + phí vượt round. |
| **5** | **Nộp bài & lưu trữ video** | Creator upload **demo video** + link bài đăng. Hệ thống lo lưu trữ (thay Drive/Zalo thủ công). Version history. |
| **6** ⭐ | **Nghiệm thu & thanh toán** | Nghiệm thu: đúng nội dung + đúng thời gian + đủ số lượng (**không** chấm view). Verify demo-đã-duyệt == bài-đăng. Chi: **per-video** (đăng xong trả) / **gói** (đủ N mới trả) / **auto per-video + bonus khi đủ N**. |
| **7** | **Hợp đồng per-job** | E-contract theo từng deal (không chỉ 1 HĐ chung), ký số 2 bên, gate eKYC. |
| **8** ⭐ | **Agency/Vendor** | Role agency + **pool creator (ownership)** + 2 mô hình (per-KOC / fixed-fee-quota) + **phạt 8% giá trị vi phạm** + hoa hồng + **ẩn với ADV** + ghi nhận "KOC đến từ agency nào". |
| **9** ⭐ | **Financial Firewall** | Tách **cost (giá trả KOC)** vs **price (giá báo client)** theo role cứng — không role nào thấy cả hai. |
| **10** | **Đối tượng & phân quyền** | 4 actor: Admin · Creator/KOC · Agency · Brand *(hoãn portal)*. Admin **tạo/nhập hộ** hồ sơ KOC & agency (nhiều KOC không tự lên hệ thống). |

**Phụ trợ (không phải lõi nhưng cần):** notification + SLA/deadline reminder · audit trail · import hồ sơ hàng loạt · dashboard tổng quan (thay Google Sheet).

---

## Bước 4 — CreatorOS hỗ trợ tới đâu (đánh giá tái sử dụng)

### 4.1. Trả lời trực tiếp giả thuyết của founder

> *"Cảm giác tận dụng được 80%, chỉ cần thêm type campaign mới và 1 vài luồng."*

**Đánh giá: đúng một nửa — cần tách bạch "hạ tầng" và "lõi nghiệp vụ".**

- ✅ **~60–70% HẠ TẦNG PHỤ TRỢ tái dùng tốt**: eKYC, e-contract ký số, storage video, payout/ledger/tax/clawback, RBAC + multi-tenant RLS, **đa kênh + enroll theo kênh**, notification, budget hard-cap, versioning thể lệ, khung campaign. Đây là phần "nặng đô" mà đa số dự án phải xây lại từ đầu → creator-os **đã có sẵn**, đây là lợi thế thật.
- ⚠️ **Nhưng LÕI NGHIỆP VỤ booking gần như phải XÂY MỚI**: 6–7 khối trụ cột (đàm phán/giá per-creator, pre-publish demo, agency, package payment, financial firewall, booking entity/state) **chưa có dòng code nào**. Doc nội bộ đội đã tự xác nhận điều này — [`docs/domain/pmax-security-impact-analysis.md`](../../../../pmax-projects/creator-os/docs/domain/pmax-security-impact-analysis.md): *"creator-os CHƯA có khái niệm 'giá KOL' vs 'giá báo client'... Đây là module MỚI của tầng Pmax/affiliate (booking creator có cost)... CHƯA build... phải thiết kế firewall từ đầu."*

→ **"Thêm type campaign + vài luồng" là cách nói NHẸ đi khối lượng lõi.** `CampaignType.BOOKING` chỉ là 1 dòng enum; nhưng "vài luồng" thực chất = **đàm phán giá + demo pre-publish + agency + package payment + firewall** — mỗi cái là một khối nghiệp vụ + dữ liệu mới. Con số thực tế: **hạ tầng ~65% có sẵn, nhưng phần code phải viết cho booking vẫn là một dự án cỡ vừa** (không phải "chỉ thêm enum").

### 4.2. Bảng đánh giá theo 3 mức (A=tái dùng nguyên · B=mở rộng nhẹ · C=xây mới)

| Mức | Hạng mục creator-os | Dùng cho booking | Bằng chứng (file) |
|---|---|---|---|
| 🟢 **A** | Đa kênh + **enroll theo từng kênh** | Booking apply theo kênh | `SocialAccount` + `CampaignEnrollment.socialAccountId` |
| 🟢 **A** | Upload **video** → object storage (MinIO/S3, transcode, signed URL) | Creator gửi demo video | `File(VIDEO)` + `StorageProviderCode` |
| 🟢 **A** | **eKYC** định danh (gate trả tiền) | Điều kiện chi cho KOC | `KycVerification` (GLOBAL) |
| 🟢 **A** | RBAC + multi-tenant RLS + `tenant_operator` | Phân quyền admin/ops | `seed.ts`, `tenant-operator.service.ts` |
| 🟢 **A** | Notification (in-app/email/**Zalo**/push, template) | Báo duyệt/từ chối/SLA | `Notification` + FCM/Brevo |
| 🟢 **A** | Ledger 2 vế + reconciliation + audit append-only | Đối soát chi | ledger tables |
| 🟡 **B** | Khung **Campaign + Version + Budget hard-cap** | Container job booking + thể lệ versioned | ADR-0009 versioning |
| 🟡 **B** | Duyệt content **sau đăng** (pipeline AUTO→AI→HUMAN) | Nghiệm thu bài đăng | `content/review.service.ts` |
| 🟡 **B** | Payout + tax + **clawback offset** + eligibility gate | Chi + phạt | `payout.service.ts` (clawback offset **đã có** — memory cũ ghi "chưa" là lỗi thời) |
| 🟡 **B** | E-contract ký số 2 bên + template versioned + eKYC gate | HĐ per-job | `Contract` (thiếu FK↔booking) |
| 🟡 **B** | Enrollment state machine (apply→approve/reject, per-channel, audit) | Sàng lọc booking | `enrollment.service.ts` |
| 🔴 **C1** | **Giá deal per-creator** | — | Reward gắn cấp **campaign** (đồng giá), không field giá riêng: `RewardRule.campaignId` unique |
| 🔴 **C2** | **Đàm phán / counter-offer** 2 chiều | — | Enrollment chỉ 1 chiều; grep `negotiat/quote/rate-card` = rỗng |
| 🔴 **C3** | **Agency đại diện N creator** | — | Ép 1 account ↔ 1 creator; agency = "bỏ UNIQUE + thêm `creator_users`" (chưa code): `schema.prisma:1112` |
| 🔴 **C4** | **Pre-publish demo approval** | — | Submission bắt buộc URL bài **đã đăng**; grep `pre-publish/demo` = rỗng |
| 🔴 **C5** | **Package payment** (đủ N mới giải ngân theo giá deal) | — | Chỉ per-accrual gom batch; "milestone" = reward-view-milestone |
| 🔴 **C6** | **Financial Firewall** (cost vs price) | — | `pmax-security-impact-analysis.md` — "module MỚI, chưa build" |
| 🔴 **C7** | **Booking entity + state machine** (offer→accept→demo→revise→publish→verify→pay) | — | Không có model Booking/Job/Deliverable |

### 4.3. Ước lượng % tái sử dụng (theo trọng số công sức)

| Nhóm | Tỉ trọng công sức điển hình | creator-os phủ | Ghi chú |
|---|---|---|---|
| Hạ tầng nền (identity/eKYC/storage/ledger/RBAC/notify/tenant) | ~40% | **~90%** | Lợi thế lớn nhất |
| Khung campaign/enrollment/budget/version/content-review/contract/payout | ~30% | **~70%** | Mở rộng nhẹ (mức B) |
| Lõi nghiệp vụ booking (giá deal/negotiation/agency/pre-publish/package/firewall) | ~30% | **~10%** | Gần như xây mới (mức C) |
| **Tổng (bình quân gia quyền)** | 100% | **~60–65%** | Không phải 80%, nhưng nền rất vững |

### 4.4. Kiến trúc đề xuất — "dựa vào creator-os thế nào"

**Khuyến nghị: KHÔNG nhồi booking vào `RewardRule` cấp campaign. Dùng `Campaign(type=BOOKING)` làm *container*, thêm một tầng "Booking Deal" per-(creator,kênh).**

```
Campaign(type=BOOKING)                      ← tái dùng: budget hard-cap, version/thể lệ, brief, tier price-band (reference)
  └─ CampaignEnrollment (per creator+kênh)  ← tái dùng: sàng lọc apply/invite/approve theo kênh
       └─ ⭐ BookingDeal (MỚI, C1/C2/C5/C7)   ← giá cost chốt, phí phụ[], trạng thái đàm phán, gói/deliverable
            ├─ ⭐ DemoSubmission (MỚI, C4)    ← demo video pre-publish + vòng duyệt (dùng lại storage video A2)
            ├─ ContentSubmission (B, sau đăng) ← nghiệm thu bài đăng (dùng lại review pipeline)
            ├─ Contract(type=BOOKING) (B4)    ← thêm FK deal↔contract
            └─ Payout (B3)                     ← thêm milestone-package theo giá deal
  └─ ⭐ Agency + creator_users (MỚI, C3)      ← pool ownership + fixed-fee/quota + phạt 8% + hoa hồng
  └─ ⭐ Financial Firewall (MỚI, C6)          ← permission finance:cost:read vs finance:price:read (nền RBAC A4)
```

Nguyên tắc: **tái dùng "danh từ hạ tầng" (identity, storage, ledger, contract, notify) + khung campaign/enrollment; xây mới "động từ booking" (chốt giá, đàm phán, duyệt demo, nghiệm thu-gói, agency).** Financial firewall làm **từ đầu** (đúng khuyến nghị doc nội bộ) — chỉ là thêm 2 permission trên nền RBAC sẵn có, rẻ nếu design sớm, đắt nếu vá sau.

### 4.5. ⭐ "Luồng đó upgrade cả content campaign" — điểm cộng hưởng (founder nói đúng)

Founder nhận xét *"luồng booking sẽ upgrade cả content campaign"* và *"Ambassador cũng phải gò vào một mối"* — **đây là insight chuẩn**:

- **Pre-publish demo approval (C4)** khi xây cho booking → **backport được** cho content/Ambassador khi brand lớn (TCB/VPBank/Vin) yêu cầu duyệt-trước-khi-đăng. Meeting xác nhận các bank đã cần đúng luồng này.
- **Giá per-creator (C1)** → mở đường cho content campaign có "skin tier customize" bên cạnh đồng giá.
- **Enrollment đã per-kênh + versioning consent-bound** → nền chung để hợp nhất Ambassador "trả theo post" = booking đồng giá.

→ Nên thiết kế C1/C4 ở tầng **dùng chung** (không hard-code riêng cho type=BOOKING) để hiện thực hoá việc hợp nhất.

### 4.6. Câu hỏi cần business chốt trước khi thiết kế

1. **Booking là `CampaignType` mới hay entity tách rời?** (khuyến nghị: container=Campaign + tầng BookingDeal — §4.4).
2. **Exclusivity fee** có áp dụng không? (chuẩn ngành có; meeting chưa nhắc).
3. **Số round duyệt demo** tối đa + phí vượt round?
4. **Package payment**: khi thiếu (18/20 video) → giảm tuyến tính hay theo bậc? Phạt agency 8% tính trên "giá trị vi phạm" = phần thiếu hay tổng deal?
5. **Agency ownership**: chọn Scenario-2 (creator sở hữu, agency = operator/nguồn) đúng chuẩn ngành + khớp RLS chủ-sở-hữu chứ? Cần `creator_users` (M-N account↔creator).
6. **Financial firewall**: thiết kế cost/price ngay từ đầu (rẻ) — chốt 2 permission `finance:cost:read` / `finance:price:read`.
7. **Brand portal** xác nhận hoãn (AT đóng vai brand) — đồng ý làm Admin + Creator portal trước?

---

## Phụ lục — Nguồn

- Meeting: [meeting-note-0714.md](./meeting-note-0714.md)
- Research chuẩn ngành (đầy đủ): `pmax-projects/creator-os/plans/reports/260717-influencer-booking-operations-research.md`
- Code creator-os: `db/prisma/schema.prisma`, `apps/api/src/modules/{campaign,content,enrollment,payout,contract-storage,ekyc,storage,notification}`, `docs/domain/pmax-security-impact-analysis.md`
- Bộ docs booking cũ (nền Ambassador): [01-de-bai-goc.md](../01-de-bai-goc.md) … [06-phase-3-automation.md](../06-phase-3-automation.md)

*Tài liệu tạo 2026-07-17. Bước 1–2 từ meeting + research đa nguồn; Bước 3–4 đối chiếu code thật creator-os (map có trích dẫn file:line, tự kiểm chứng schema campaign/enrollment/reward).*

