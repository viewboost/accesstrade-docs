# Option A — Quick Start MVP cho AccessTrade

> **Phiên bản tài liệu:** 2026-05-04
>
> **Thời gian:** 4 tuần làm việc — phần phục vụ event (landing + form + trang creator) PHẢI go-live tuần 1-2 để kịp event 7/5. CRM internal cho Care làm sau ở tuần 3-4.
>
> **Tận dụng:** influence-meter (Diso đã có) + codebase demo `vcreator.demo.accesstrade.click`

---

## Mục tiêu Option A

Trong 4 tuần, deliver được 4 mảng chính phục vụ song song hai mục đích:

1. **Landing page sự kiện** — chuẩn bị cho event Creator For Vietnam ngày 7/5
2. **Form đăng ký + tài khoản creator** — thu thập creator + lưu vào DB tập trung, creator có tài khoản để xem lại sau
3. **Trang creator (sau đăng ký)** — creator xem thông tin chung của mình, không phải full data như Care thấy trong CRM
4. **CRM quản lý creator (cho team Care)** — thay Excel, có list + detail + chi tiết kênh social đầy đủ từ influence-meter

> **Ưu tiên thứ tự:** Mảng 1, 2, 3 phục vụ event 7/5 → ưu tiên tuần 1-2. Mảng 4 (CRM) là internal tool cho Care → tuần 3-4 sau khi đã có data từ event.

---

## Phạm vi cụ thể

### 1. Landing page sự kiện (Public)
- 1 trang scroll: hero + value prop + agenda + danh sách event/campaign + CTA đăng ký
- Adapt từ codebase demo `vcreator.demo.accesstrade.click` để tiết kiệm thời gian
- Responsive mobile-first, test trên Chrome/Safari/iOS/Android
- **Danh sách event/campaign HARDCODE** trong code (config JSON tĩnh), KHÔNG dynamic từ API `ambassador.koc.com.vn`. Khi AT cần update danh sách phải redeploy. Tích hợp ambassador API sẽ làm ở đợt sau.

### 2. Form đăng ký + tài khoản creator (Public)
- Form **2 bước** (gộp từ 3 bước trong demo cho gọn):
  - Step 1: Họ tên, phone, email, **mật khẩu**
  - Step 2: Social handles (Facebook/Instagram/TikTok/YouTube) + consent
- Validation client-side
- Submit → backend dedupe handle → lưu DB → gửi email confirm với **link kích hoạt tài khoản**
- Sau khi click link kích hoạt:
  - Tài khoản active
  - Auto đăng nhập + chuyển đến trang creator
- **Đăng nhập lại** (lần sau): email + mật khẩu trên trang `/login`
- Page thank-you basic (KHÔNG có wow tier prediction để tiết kiệm scope)

### 3. Trang creator (Sau đăng ký, cần đăng nhập)

Sau khi creator đăng ký + kích hoạt qua email, có một trang riêng cho creator xem lại profile mình đã đăng ký. Mục đích: cho creator cảm giác chuyên nghiệp + xem lại thông tin bất kỳ lúc nào, KHÔNG phải xem full data như Care.

**Hiển thị:**
- Tên + avatar tổng hợp
- Danh sách kênh social đã đăng ký (icon + handle + link external + số follower)
- Trạng thái đăng ký + ngày tham gia event
- Hướng dẫn bước tiếp theo (chờ Care liên hệ qua Zalo trong 48h)
- Nút thêm/sửa kênh social (tuỳ thời gian, có thể defer)

**KHÔNG hiển thị:**
- Engagement rate chi tiết, performance score
- Recent content + thumbnail bài đăng
- Audience demographics
- Bất kỳ data internal nào của Care

URL: `/me` — yêu cầu đăng nhập.

### 4. CRM Creator Management (Internal Admin — dành cho Care)
- **Login admin:** 1 role duy nhất, JWT, hardcode 2-3 admin
- **Creator List page:**
  - Table với columns: handle, tên, source, channels, ngày đăng ký
  - Filter: source, ngày
  - Search: handle hoặc tên
  - Pagination + sort
- **Trang chi tiết creator (read-only) — 3 tabs:**
  - Tab Profile: thông tin cá nhân (tên, phone, email, source, ngày đăng ký)
  - Tab Channels: chi tiết đầy đủ từng kênh social (header platform + engagement summary + recent content top 10 + nút Refresh data)
  - Tab Registration history: lịch sử đăng ký + email status

---

## Dữ liệu hiển thị từ influence-meter

Cam kết về **dữ liệu thực tế** sẽ thấy trên trang chi tiết creator → Tab Channels cho mỗi creator (4 nền tảng: TikTok, YouTube, Facebook, Instagram).

Backend hạ tầng:
- HTTP client gọi influence-meter API
- Cache Redis 1 ngày để tránh gọi quá nhiều
- Endpoint: `GET /creators/:id/channels/:platform/influence-data`

### Profile cơ bản
- Tên, handle, avatar, bio, mô tả
- Số follower (hoặc subscriber với YouTube), số đang follow
- Tổng số content đã đăng
- Chuyên mục (category)
- Ngày tạo tài khoản, tuổi tài khoản

### Engagement metrics
- **Engagement rate (%)** — công thức theo từng platform
- Avg views per post/video
- Avg likes per post
- Tổng comments, tổng shares (với platform có share)
- Tần suất đăng bài (posts/tuần)
- Performance score 0-100 (nếu có lịch sử campaign)

### Recent content (top 10-20 bài gần nhất)
- Content ID + permalink
- View / like / comment / share count
- Hashtags (TikTok/IG)
- Music title (TikTok)
- Reactions breakdown Like/Love/Haha/... (Facebook)
- Thumbnail URL
- Ngày đăng

### KHÔNG có trong Option A (sẽ làm đợt sau)
- ❌ Audience demographics (age/gender/country) — Sprint 6 influence-meter chưa active
- ❌ Brand-safety ML detection — đang plan
- ❌ Data completeness scoring — đang plan
- ❌ Threads platform — chưa có scraper
- ❌ Verified badge / Quốc gia / Ngôn ngữ — influence-meter chưa cover đầy đủ và chính xác cho 4 platform

> **Tham chiếu chi tiết:** [../data-commitment.md](../data-commitment.md) liệt kê đầy đủ trường data và phân biệt REAL vs PLANNED.

---

## NGOÀI scope (KHÔNG làm trong Option A)

| Không có | Hệ quả |
|---|---|
| ❌ **Wow welcome page** | Creator chỉ thấy thank-you basic |
| ❌ **Profile card share** | Không có OG image + public link `/welcome/[handle]` |
| ❌ **Lifecycle state machine (M2)** | Không có 7 giai đoạn V2 |
| ❌ **Phân công Care (M5)** | Không có round-robin assignment |
| ❌ **Task Console (M6)** | Không có queue tác vụ |
| ❌ **Conversation tracking (M7)** | Không lưu lịch sử chat Zalo |
| ❌ **Multi-tenant (M13)** | Chỉ 1 admin pool, không TCB/VinFast riêng |
| ❌ **Notification (M14)** | Không có in-app + email notification |
| ❌ **Tier scoring (M3)** | Chỉ hiển thị data thô, không chấm điểm |
| ❌ **SLA timer (M4)** | Không có timer + escalation |
| ❌ **Reporting + Vault + Sourcing** | Toàn bộ Phase 1B + Phase 2 |
| ❌ **Sync danh sách event từ ambassador API** | Hardcode JSON tĩnh trong code, update phải redeploy |
| ❌ **Audience demographics + brand-safety ML** | Influence-meter chưa active các module này |
| ❌ **Verified badge / Quốc gia / Ngôn ngữ creator** | Influence-meter chưa cover đầy đủ 4 platform |
| ❌ **Import CSV creator** | Care phải nhập tay từng creator hoặc creator tự đăng ký qua form |

---

## Tổng quan công sức

| Vai trò | Hours | Rate ($/h) | Cost (USD) | % Total |
|---|---:|---:|---:|---:|
| Backend | 75h | $15 | $1.125 | 31% |
| FE Creator | 46h | $15 | $690 | 19% |
| FE Admin | 43h | $15 | $645 | 18% |
| QC | 39h | $11 | $429 | 12% |
| DevOps | 16h | $17 | $272 | 7% |
| Design | 16h | $11 | $176 | 5% |
| PM | 10h | $20 | $200 | 5% |
| BA | 7h | $11 | $77 | 2% |
| SA | 2h | $17 | $34 | 1% |
| **TỔNG** | **254h** | — | **$3.648** | **100%** |

**Quy đổi VND** (rate 26.000/USD): **~94,85 triệu VND**

> **Báo giá khởi tạo cho AT:** **80.000.000đ** (xem [pricing.csv](./pricing.csv)) — Diso giảm giá ~14,85tr (~15,7%) so với effort thực tế để build relationship dài hạn với AT.

---

## Timeline 4 tuần

**Ưu tiên:** Phục vụ event 7/5 trước (tuần 1-2), CRM Care sau (tuần 3-4).

| Tuần | Công việc | Deliverable cuối tuần |
|---|---|---|
| **Tuần 1** | Setup hạ tầng + Discovery + Landing + Form UI 2 bước (kèm mật khẩu) | Landing + form đăng ký xem được, demo nội bộ |
| **Tuần 2** | Form backend + Email kích hoạt + Trang creator `/me` + Login | **GO-LIVE PHẦN EVENT trước 5/5** — creator đăng ký, kích hoạt, đăng nhập lại xem profile |
| **Tuần 3** | Auth admin + CRM Creator List + Trang chi tiết creator (Profile + Channels + History) | Care có CRM, list creator, xem chi tiết |
| **Tuần 4** | Influence-meter integration + Tab Channels chi tiết + QA + Deploy + Bàn giao | CRM full data influence-meter, bàn giao Care |

**Mốc cứng:** Phần event (mảng 1+2+3) phải go-live **trước 5/5/2026** để kịp event 7/5. CRM internal có thể go-live tuần 4 sau event.

---

## Team đề xuất

Với 254h trong 4 tuần (≈ 64h/tuần effort), team chuẩn:

| Vai trò | FTE | Note |
|---|---|---|
| 1 Backend dev | ~70% | Lead phần CRM + IM integration |
| 1 Frontend dev | ~50% | Chia sẻ giữa event-fe và admin |
| 1 PM/BA part-time | ~15% | Workshop discovery + sprint coordination |
| 1 QC part-time | ~25% | QA phân vào từng task |
| 1 Designer freelance | 1 tuần đầu | Adapt branding + landing assets |
| DevOps freelance | 1-2 ngày | Setup infra + deploy |

**Tổng FTE quy đổi:** ~1.5 người fulltime trong 4 tuần.

---

## Bàn giao

Cuối tuần 4, Diso bàn giao cho AccessTrade:

- **Tài liệu hướng dẫn sử dụng** (link online): User guide cho Care + creator + API doc
- **Demo session online:** 1 buổi walkthrough toàn bộ flow + Q&A, có video record
- **Production system:** Đã go-live, monitoring 1 tuần đầu để hotfix critical
- **Source code + access:** Repo + credentials hạ tầng

---

## Chi phí vận hành hằng tháng (sau go-live)

### Mô hình hạ tầng
- AT cung cấp **hạ tầng AWS** theo cách chuẩn của các dự án khác đang chạy ở AT (Diso không phụ trách chi phí hosting)
- Diso **miễn phí phí khởi tạo influence-meter** cho dự án này
- Diso miễn phí **chi phí vận hành tháng đầu tiên** khi khởi tạo

### Các khoản chi phí định kỳ

| Khoản | Chi phí / tháng | Bao gồm |
|---|---:|---|
| **Sử dụng influence-meter** | 10.000.000đ (chưa VAT) | Tối đa 500 profile / tháng. Tính từ tháng đầu tiên. |
| **Vận hành hệ thống** | 10.000.000đ | 1 PM + 1 Dev + 1 QC, ~8h/người/tháng để xử lý vấn đề phát sinh. **Miễn phí tháng đầu**. |

### Cam kết tối thiểu

AT cam kết sử dụng dịch vụ tối thiểu **3 tháng** sau khi go-live.

| Khoản mục | Số tiền |
|---|---:|
| Chi phí khởi tạo (build MVP 4 tuần) | 80.000.000đ |
| Chi phí vận hành 2 tháng (tháng 1 free, tháng 2-3) | 20.000.000đ |
| Chi phí influence-meter 3 tháng | 30.000.000đ |
| **TỔNG cam kết 3 tháng** | **130.000.000đ** |

> **Giảm giá khởi tạo:** Effort thực tế theo tasks.csv là 254h × rate role = $3.648 ≈ **94.848.000đ** (rate 26.000 VND/USD). Báo giá AT **80.000.000đ** → Diso giảm **14.848.000đ (~15,7%)** để build relationship dài hạn.
>
> **Ghi chú:** Sau 3 tháng cam kết, AT có thể tiếp tục thuê hằng tháng (10tr vận hành + 10tr influence-meter = 20tr/tháng) hoặc thoả thuận lại. Nếu sử dụng vượt 500 profile/tháng cho influence-meter, tính thêm theo bậc thang (báo giá riêng).

---

## Rủi ro

### Rủi ro 1: Influence-meter API có thể không đủ data ở tất cả platform
**Hậu quả:** Tab Channels trên trang chi tiết creator sẽ thiếu một số trường tuỳ platform. Ví dụ Facebook có thể thiếu reactions breakdown, YouTube có thể thiếu hashtags, Instagram có thể chưa có engagement rate ổn định.
**Giảm thiểu:**
- Audit influence-meter API ngay tuần 1, lập danh sách trường nào REAL vs MISSING cho từng platform
- UI design chấp nhận trường thiếu → hiển thị "—" hoặc ẩn thay vì error
- Cập nhật [../data-commitment.md](../data-commitment.md) thật chi tiết theo kết quả audit, để AT không bị bất ngờ khi nghiệm thu

### Rủi ro 2: Event 7/5 thay đổi nội dung phút chót
**Hậu quả:** Landing copy/assets phải sửa gấp
**Giảm thiểu:** Lock content tuần 1 với BA. Mọi thay đổi sau tuần 2 tính phụ phí.

### Rủi ro 3: Care chưa quen tool, dùng Excel song song
**Hậu quả:** Data fragment, không có giá trị thực
**Giảm thiểu:** Tài liệu hướng dẫn + demo cuối tuần 4. Diso có thể hỗ trợ on-site 1 tuần (ngoài scope, tính phụ phí).

### Rủi ro 4: AT yêu cầu thêm scope giữa chừng
**Hậu quả:** Slip deadline + Diso lỗ thêm
**Giảm thiểu:** Lock scope bằng văn bản tuần 1. Mọi change request đánh giá impact + báo giá riêng.

---

## Tài liệu liên quan

- [tasks.csv](./tasks.csv) — chi tiết 9 task group theo từng vai trò
- [pricing.csv](./pricing.csv) — báo giá khởi tạo + cam kết 3 tháng (import vào Excel)
- [../data-commitment.md](../data-commitment.md) — cam kết chi tiết dữ liệu từ influence-meter
- **🎬 MVP Demo (clickable, 6 màn hình):** https://vcreator.demo.accesstrade.click/mvp-demo — landing → register → activate → /me → admin login → CRM creator detail
- **Trang MVP overview (interactive):** https://vcreator.demo.accesstrade.click/mvp
- **Demo tham chiếu (4 phase đầy đủ):** https://vcreator.demo.accesstrade.click/
- **Influence-meter (Diso):** internal API doc cần lấy trước tuần 1
