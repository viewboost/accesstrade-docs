# VCreator Global Platform — Project Overview

**Ngày:** 2026-03-02
**Phiên bản:** 1.0
**Đối tượng:** Business stakeholders, Management, Non-technical team

---

## 1. Tổng Quan Dự Án

### VCreator là gì?

VCreator là nền tảng quản lý KOC (Key Opinion Creator) — kết nối **Brands** (nhãn hàng) với **Creators** (người sáng tạo nội dung) trên các mạng xã hội như TikTok, Facebook, Instagram, YouTube...

**Quy trình hoạt động:**

```
Brand đăng Campaign → Creator tham gia → Creator tạo content trên mạng xã hội
→ Content được duyệt → Views/engagement được tracking → Creator nhận hoa hồng
```

### Hiện tại: VCreator Vietnam

- Đang hoạt động tại **Việt Nam**
- Hỗ trợ TikTok, Facebook, Instagram, Threads, YouTube, Zalo
- Quy trình: Đăng ký → eKYC → Tham gia campaign → Tạo content → Nhận tiền

### Dự án mới: VCreator Global

**Mục tiêu:** Mở rộng VCreator ra **đa quốc gia**, bắt đầu với **Philippines**, sau đó là Indonesia, CIS/EU.

**Quyết định quan trọng:** Xây dựng hệ thống **hoàn toàn mới** (không nâng cấp từ source cũ) — đảm bảo nền tảng được thiết kế cho quy mô toàn cầu ngay từ đầu.

---

## 2. Vì Sao Cần VCreator Global?

| Lý do | Giải thích |
|-------|-----------|
| **Mở rộng thị trường** | Tiếp cận creators và brands tại nhiều quốc gia → tăng doanh thu |
| **Quy mô kinh tế** | 1 nền tảng phục vụ nhiều nước → giảm chi phí phát triển & vận hành so với build riêng per country |
| **Chuẩn hóa** | Thêm mỗi quốc gia mới chỉ cần **cấu hình**, không cần code lại |
| **Ưu thế cạnh tranh** | Platform đa quốc gia → thu hút brands lớn muốn chạy campaign nhiều nước cùng lúc |
| **Cross-country creators** | Creator VN có thể mở rộng sang PH và ngược lại → nhiều cơ hội hơn |

---

## 3. Ai Sử Dụng Hệ Thống?

### 3.1 Creator / KOC (Người sáng tạo nội dung)

Đây là **end user chính** — những người tạo content trên mạng xã hội và nhận hoa hồng.

**Hành trình Creator trên VCreator Global:**

```
1. ĐĂNG KÝ        → Login bằng TikTok/Google, chọn quốc gia
2. XÁC MINH (KYC) → Upload giấy tờ theo yêu cầu quốc gia đó
3. TÌM CAMPAIGN   → Browse campaigns đang chạy ở quốc gia mình
4. TẠO CONTENT    → Quay video/chụp ảnh, đăng lên mạng xã hội
5. SUBMIT          → Paste link content lên platform
6. THEO DÕI       → Xem thu nhập, trạng thái duyệt content
7. RÚT TIỀN       → Rút tiền về ngân hàng hoặc ví điện tử (GCash...)
```

**Điểm đặc biệt ở Global:**
- **1 tài khoản dùng cho tất cả quốc gia** — login 1 lần, switch giữa các nước
- Mỗi quốc gia có **profile riêng**: giấy tờ KYC, tài khoản ngân hàng, thu nhập, thuế — tất cả tách biệt
- Thu nhập hiển thị bằng **tiền tệ địa phương** (₱ cho Philippines, ₫ cho Việt Nam)
- Giao diện **đa ngôn ngữ**: Filipino, Tiếng Việt, English

### 3.2 Local Ops (Nhân viên vận hành — mỗi nước)

Đội ngũ **duyệt nội dung** và **hỗ trợ creator** hàng ngày tại mỗi quốc gia.

**Công việc chính:**
- Duyệt content do Creator submit (approve / reject / yêu cầu sửa)
- Xét duyệt hồ sơ KYC (giấy tờ tùy thân, tài khoản ngân hàng)
- Quản lý danh sách creators (tìm kiếm, xem chi tiết, tạm khóa nếu vi phạm)
- Gửi thông báo cho creators

**Giới hạn quan trọng:** Local Ops **chỉ thấy dữ liệu quốc gia mình** — không xem được quốc gia khác.

### 3.3 Local Finance (Kế toán — mỗi nước)

Đội ngũ quản lý **tài chính, đối soát, thanh toán** cho creators tại mỗi quốc gia.

**Công việc chính:**
- **Đối soát (Reconciliation):** Tạo batch đối soát theo kỳ → review thu nhập creators → chốt tỷ giá → phê duyệt
- **Thanh toán:** Execute chuyển tiền cho creators (ngân hàng, GCash...)
- **Xử lý lỗi:** Retry thanh toán thất bại, hoàn tiền vào balance
- **Báo cáo:** Dashboard doanh thu, tổng hợp thuế, xuất báo cáo Excel

**Về tỷ giá:**
- **Tỷ giá tham chiếu**: Hiển thị realtime cho creators tham khảo (≈ USD)
- **Tỷ giá chốt**: Khi đối soát, Finance chốt tỷ giá cố định cho cả batch → **không thể sửa** sau khi chốt (nếu sai → tạo batch điều chỉnh mới)

### 3.4 Local Admin (Quản lý quốc gia)

**Quản lý toàn bộ hoạt động** của 1 quốc gia. Có tất cả quyền của Ops + Finance, cộng thêm:

**Công việc chính:**
- **Quản lý Campaign:** Tạo campaign, thiết lập phần thưởng, thiết lập ngân sách, quy trình duyệt campaign
- **Quản lý Partner/Brand:** Cấu hình thương hiệu, giao campaign cho partner
- **Quản lý Team:** Mời nhân viên, giao role (Ops hoặc Finance)
- **Dashboard:** Xem KPIs tổng quan quốc gia (creators, campaigns, doanh thu)
- **Quản lý nội dung CMS:** T&C, bài viết, hướng dẫn — đa ngôn ngữ
- **Import/Export:** Import creators hàng loạt, xuất báo cáo

### 3.5 Global Admin (Quản trị toàn hệ thống — HQ Việt Nam)

Đội ngũ **quản lý cấp cao** tại HQ, giám sát tất cả quốc gia.

**Công việc chính:**
- **Dashboard tổng hợp:** Xem doanh thu tất cả quốc gia (quy đổi USD), so sánh performance giữa các nước
- **"Vào vai Local" (Acting as Local):** Khi cần hỗ trợ/can thiệp, Global Admin có thể "vào" 1 quốc gia cụ thể — **bắt buộc nhập lý do**, mọi hành động đều **được ghi log**
- **Cấu hình quốc gia:** Thiết lập tiền tệ, ngôn ngữ, thuế, KYC, cổng thanh toán... cho mỗi nước
- **Quản lý tài khoản Admin:** Tạo/phân quyền admin cho từng quốc gia
- **Bật/tắt tính năng:** Bật/tắt tính năng cho từng quốc gia (VD: GCash chỉ bật cho Philippines)
- **Kiểm toán (Audit):** Xem log toàn bộ hệ thống — ai làm gì, ở đâu, khi nào
- **Báo cáo cross-country:** So sánh doanh thu, creators, campaigns giữa các nước

---

## 4. Cấu Trúc Hệ Thống (Giải Thích Đơn Giản)

### 4.1 Cấu trúc tổ chức

```
                    ┌──────────────────────────────┐
                    │       GLOBAL ADMIN            │
                    │  Dashboard tổng hợp (USD)     │
                    │  Cấu hình quốc gia            │
                    │  Kiểm toán toàn hệ thống      │
                    └──────────┬───────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
     │ PHILIPPINES  │   │  VIETNAM    │   │ INDONESIA   │
     │              │   │             │   │ (tương lai) │
     │ Admin: Maria │   │ Admin: Minh │   │             │
     │ Finance: Ana │   │ Finance: Hà │   │             │
     │ Ops: Jose    │   │ Ops: Tuấn   │   │             │
     │              │   │             │   │             │
     │ Tiền: ₱ PHP  │   │ Tiền: ₫ VND │   │ Tiền: Rp IDR│
     │ Thuế: WHT    │   │ Thuế: TNCN  │   │             │
     │ KYC: PhilID  │   │ KYC: CCCD   │   │             │
     │ Pay: GCash   │   │ Pay: Bank   │   │             │
     └─────────────┘   └─────────────┘   └─────────────┘
```

### 4.2 Ba lớp hệ thống

| Lớp | Mô tả | Ví dụ |
|-----|-------|-------|
| **Platform Core (Nền tảng)** | Hạ tầng chung dùng cho tất cả quốc gia | Phân tách dữ liệu mỗi nước, đa ngôn ngữ, tỷ giá, thuế, bật/tắt tính năng |
| **Creator App** | Tính năng cho Creator/KOC | Đăng ký, KYC, tìm campaign, submit content, theo dõi thu nhập, rút tiền |
| **Admin Panel** | Tính năng cho đội ngũ vận hành | Duyệt content, đối soát, thanh toán, quản lý campaign, báo cáo |

---

## 5. Nguyên Tắc Thiết Kế Quan Trọng

### 5.1 An toàn dữ liệu — "Không ai xem nhầm data nước khác"

Đây là nguyên tắc **số 1** của hệ thống:
- Đội vận hành Philippines **không thể** xem dữ liệu creators Việt Nam
- Đội vận hành Việt Nam **không thể** xem dữ liệu creators Philippines
- Chỉ Global Admin mới xem được dữ liệu tổng hợp — và mọi hành động đều được ghi log

### 5.2 Minh bạch tài chính — "Mọi con số đều rõ ràng"

- Thu nhập Creator hiển thị bằng **tiền địa phương** (₱, ₫)
- Phân biệt rõ: **đã xác nhận** (đã đối soát) vs **đang chờ** (chưa đối soát)
- Thuế: hiển thị rõ công thức **Thu nhập gộp → Thuế → Thu nhập thực nhận**
- Tỷ giá: phân biệt **tham chiếu** (thay đổi liên tục) vs **chốt** (cố định khi đối soát)

### 5.3 Kiểm toán — "Ai làm gì, khi nào, ở đâu"

- Mọi hành động quan trọng đều được ghi log: duyệt content, phê duyệt KYC, thực hiện thanh toán, chốt tỷ giá, thay đổi cấu hình...
- Đặc biệt: Global Admin "vào vai Local" → **tất cả** hành động trong session đó được ghi log chi tiết (lý do, thời gian, hành động cụ thể)
- Log không thể sửa hoặc xóa

### 5.4 Đa ngôn ngữ — "Mỗi người dùng ngôn ngữ của mình"

- Creator Philippines thấy giao diện Filipino hoặc English
- Creator Việt Nam thấy giao diện Tiếng Việt
- Admin panel cũng đa ngôn ngữ — đội vận hành local dùng ngôn ngữ địa phương
- Nội dung campaign, T&C, hướng dẫn đều có nhiều ngôn ngữ

### 5.5 Mở rộng dễ dàng — "Thêm quốc gia = cấu hình, không phải code lại"

- Thêm quốc gia mới: Global Admin cấu hình (tiền tệ, ngôn ngữ, thuế, KYC, cổng thanh toán)
- Bật/tắt tính năng per quốc gia (VD: GCash chỉ Philippines)
- Không cần thay đổi code khi thêm nước mới

---

## 6. Báo Giá Tổng Quan

### 6.1 Phân bổ theo module

| Module | Mô tả | Giờ | % |
|--------|-------|-----|---|
| **Platform Core** | Nền tảng chung: đa quốc gia, đa ngôn ngữ, tỷ giá, thuế, hạ tầng | 1,194h | 19% |
| **Creator App** | Tính năng cho Creator: đăng ký, KYC, campaign, content, thu nhập, rút tiền | 2,084h | 34% |
| **Admin Panel** | Tính năng vận hành: duyệt content, đối soát, thanh toán, quản lý, báo cáo | 2,940h | 47% |
| **TỔNG** | | **6,218h** | **100%** |

### 6.2 Phân bổ theo nhóm công việc

| Vai trò | Giờ | Giải thích |
|---------|-----|-----------|
| DevOps | 74h | Thiết lập hạ tầng, CI/CD, monitoring |
| Solution Architect | 396h | Thiết kế kiến trúc hệ thống |
| Backend Engineer | 2,212h | Xây dựng API, logic nghiệp vụ, database |
| Frontend Engineer | 1,840h | Xây dựng giao diện người dùng |
| QC/Tester | 698h | Kiểm thử, đảm bảo chất lượng |
| Designer | 60h | Thiết kế UI/UX |
| Business Analyst | 346h | Phân tích yêu cầu, viết specs |
| Project Manager | 592h | Quản lý dự án, phối hợp team |
| **TỔNG** | **6,218h** | |

### 6.3 Phân bổ theo Phase

| Phase | Nội dung | Giờ | % |
|-------|----------|-----|---|
| **Phase 1 (Core)** | Tất cả tính năng cốt lõi để go-live Philippines | 4,694h | 75% |
| **Phase 2 (Enhancement)** | Tính năng nâng cao, tối ưu, tính năng bổ sung | 1,524h | 25% |

### 6.4 Timeline ước tính

| Scenario | Quy mô team | Thời gian | Ghi chú |
|----------|-------------|-----------|---------|
| **Team nhỏ** | ~8-9 người | 6.5 - 7 tháng | Phù hợp budget thấp |
| **Team vừa** | ~12-14 người | 4.5 - 5 tháng | Cân bằng chi phí và tốc độ |
| **Team lớn** | ~18-20 người | 3 - 3.5 tháng | Nhanh nhưng cần phối hợp tốt |

> **Lưu ý:** Chưa bao gồm buffer rủi ro (thường +15-20%), UAT với business, và thời gian vendor setup/training per country.

---

## 7. Roadmap — Kế Hoạch Triển Khai

### Phase 1: Nền tảng + Philippines Go-Live

**Mục tiêu:** Xây dựng toàn bộ nền tảng và go-live Philippines.

```
Tháng 1-2: Platform Core
├── Hạ tầng đa quốc gia (phân tách dữ liệu, cấu hình mỗi nước)
├── Hệ thống user chung (1 account, nhiều nước)
├── Đa ngôn ngữ (Filipino, Tiếng Việt, English)
├── Tỷ giá + thuế mỗi nước
└── Hệ thống bật/tắt tính năng

Tháng 2-4: Creator App + Admin Panel (Phase 1)
├── Creator: Đăng ký, KYC, Campaigns, Content, Thu nhập, Rút tiền
├── Admin: Duyệt content, KYC review, Campaign CRUD, Dashboard
├── Finance: Đối soát, Thanh toán, Báo cáo
└── Global Admin: Dashboard tổng, Cấu hình, Audit

Tháng 4-5: Philippines Setup & Testing
├── Cấu hình Philippines (tiền ₱, thuế WHT, KYC PhilID, GCash)
├── Tích hợp cổng thanh toán Philippines
├── UAT với đội vận hành Philippines
└── Go-live Philippines
```

### Phase 2: Nâng cao + Chuẩn bị mở rộng

**Mục tiêu:** Bổ sung tính năng nâng cao, chuẩn bị cho nước tiếp theo.

```
Tháng 5-7:
├── Facebook Login
├── GCash e-wallet integration
├── Acting-as-Local cho Global Admin
├── Cross-country reports
├── Campaign clone, leaderboard, advanced analytics
├── Annual tax summary export
└── Chuẩn bị Indonesia setup
```

### Phase 3 (Tương lai): Vietnam Migration + Mở rộng

```
├── Migrate dữ liệu VN cũ sang Global Platform
├── Chuyển 11 branded apps sang hệ thống mới
├── Indonesia go-live
└── Các quốc gia tiếp theo (CIS, EU...)
```

---

## 8. Rủi Ro Chính & Giải Pháp

| # | Rủi ro | Mức độ | Giải pháp |
|---|--------|--------|-----------|
| 1 | **Rò rỉ dữ liệu giữa quốc gia** — Team PH xem được data VN | Cao | 3 lớp bảo vệ: giao diện + API + database đều filter theo quốc gia. Kiểm thử tự động. Alert khi phát hiện bất thường. |
| 2 | **Chốt tỷ giá sai** — Finance nhập sai rate, thanh toán sai cho hàng trăm creators | Cao | Hệ thống tự kiểm tra rate (nếu lệch >5% so với market → cảnh báo). Preview tổng tiền trước khi chốt. Nếu sai → tạo batch điều chỉnh (không sửa batch cũ). |
| 3 | **Timeline aggressive** — 6,218h là khối lượng lớn | Trung bình | Chia phase rõ ràng. Phase 1 tập trung tính năng cốt lõi (75%). Phase 2 là nâng cao. |
| 4 | **Compliance khác nhau mỗi nước** — KYC, thuế, privacy mỗi nước mỗi khác | Trung bình | Country Config cho phép cấu hình riêng mỗi nước. Research compliance TRƯỚC khi phát triển. |
| 5 | **VN Migration** — Chuyển dữ liệu production VN sang hệ thống mới | Trung bình | Để SAU Philippines go-live (Phase 3). Chạy song song 2 hệ thống trong giai đoạn chuyển tiếp. |
| 6 | **Đội vận hành local chưa quen** — Team PH mới, chưa biết dùng platform | Thấp | Admin panel đa ngôn ngữ (Filipino). Hướng dẫn sử dụng in-app. Training materials mỗi nước. |

---

## 9. Câu Hỏi Cần Business Chốt

Một số quyết định **cần business/product owner trả lời** trước khi phát triển:

| # | Câu hỏi | Ảnh hưởng |
|---|---------|-----------|
| 1 | **Partner Admin riêng?** Có cần role riêng cho partner manager (chỉ xem data brand mình) hay dùng Local Admin? | Ảnh hưởng hệ thống phân quyền |
| 2 | **Quy trình duyệt đối soát?** Finance tạo batch → ai phê duyệt? Finance tự duyệt hay cần Local Admin ký? | Ảnh hưởng quy trình tài chính |
| 3 | **MFA bắt buộc?** Có bắt buộc xác thực 2 lớp cho admin, đặc biệt Finance và Global Admin? | Ảnh hưởng bảo mật |
| 4 | **KYC có thể hoãn?** Cho Creator browse/join campaign trước, KYC khi muốn rút tiền? (Hiện VN bắt KYC sớm) | Ảnh hưởng tỷ lệ đăng ký mới |
| 5 | **Phương thức thanh toán Philippines?** GCash, bank transfer, hay cả hai? Vendor nào? | Ảnh hưởng rút tiền PH |
| 6 | **Admin panel mobile?** Đội Ops có cần duyệt content trên mobile/tablet? | Ảnh hưởng scope thiết kế |
| 7 | **Tech stack?** Tiếp tục Go + React hay chuyển sang stack khác cho hệ thống mới? | Ảnh hưởng toàn bộ effort dev |

---

## 10. Tài Liệu Chi Tiết (Tham Khảo)

| Tài liệu | Nội dung | File |
|-----------|----------|------|
| **ADR (Architecture Decision Records)** | 6 quyết định kiến trúc quan trọng (ADR-000 ~ ADR-005) | `adr-platform-core.md` |
| **Báo giá Creator** | 42 tính năng Creator, ước lượng giờ chi tiết | `baogia/VCreator-Global-Creator-BaoGia.csv` |
| **Báo giá Platform Core** | 19 tính năng nền tảng, ước lượng giờ chi tiết | `baogia/VCreator-Global-PlatformCore-BaoGia.csv` |
| **Báo giá Admin** | 69 tính năng Admin, ước lượng giờ chi tiết | `baogia/VCreator-Global-Admin-BaoGia.csv` |
| **Brainstorming Creator** | 50 user stories Creator chi tiết | `../../.bmad/brainstorming-vcreator-global-creator-stories-2026-03-02.md` |
| **Brainstorming Admin** | 67 user stories Admin chi tiết | `../../.bmad/brainstorming-vcreator-global-admin-stories-2026-03-02.md` |
| **Brainstorming Tổng** | Phân tích tổng quan 10 modules, SWOT | `../../.bmad/brainstorming-vcreator-global-2026-03-02.md` |

---

## Tóm Tắt 1 Trang

> **VCreator Global** mở rộng nền tảng KOC management từ Việt Nam ra đa quốc gia, bắt đầu với Philippines.
>
> **Hệ thống phục vụ 5 nhóm người dùng:** Creator (tạo content, nhận tiền), Local Ops (duyệt content, quản lý creators), Local Finance (đối soát, thanh toán), Local Admin (quản lý quốc gia), Global Admin (giám sát toàn hệ thống).
>
> **3 nguyên tắc cốt lõi:** An toàn dữ liệu giữa các nước, minh bạch tài chính, kiểm toán mọi hành động.
>
> **Quy mô:** 6,218 giờ (Platform Core 1,194h + Creator 2,084h + Admin 2,940h). Timeline 3.5 - 7 tháng tùy quy mô team.
>
> **Lộ trình:** Phase 1 (Philippines go-live) → Phase 2 (tính năng nâng cao) → Phase 3 (migrate VN + mở rộng Indonesia, CIS/EU).

---

*Tài liệu được tổng hợp từ phân tích brainstorming, kiến trúc kỹ thuật, và báo giá chi tiết.*
*Ngày tạo: 2026-03-02*
