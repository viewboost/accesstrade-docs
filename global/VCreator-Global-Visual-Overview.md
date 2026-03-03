# VCreator Global Platform

### Nền tảng KOC Management đa quốc gia

**Phiên bản:** 1.0 · **Ngày:** 2026-03-03 · **Đối tượng:** Business Stakeholders, Partners

---

> **5,148h** tổng effort · **4 modules** chính · **3 phases** triển khai · **Đa quốc gia** từ ngày đầu
>
> *Platform được thiết kế để mở rộng bằng cấu hình — thêm quốc gia mới mà không cần code lại.*

---

## Mục Lục

```mermaid
mindmap
  root((VCreator Global))
    🎯 Cơ Hội
      Mở rộng thị trường
      Economies of Scale
      Cross-country Creators
    📦 Nền Tảng
      Business Model
      4 Modules
      130+ Features
    👥 Người Dùng
      Creator / KOC
      Local Ops & Finance
      Local Admin
      Global Admin
    ⚙️ Quy Trình
      Campaign Lifecycle
      Đối soát & Thanh toán
      KYC & Onboarding
    🌏 Mở Rộng
      Config-based
      574h per country
      PH → ID → CIS/EU
    💰 Đầu Tư
      5,148h total
      3 Phases
      Team 8-10 người
    🛡️ Rủi Ro
      Data Isolation
      Tỷ giá
      Compliance
    📋 Bước Tiếp
      7 câu hỏi cần chốt
      Kick-off checklist
```

---

## 1. Cơ Hội — Vì Sao Cần VCreator Global?

### Bài toán hiện tại

VCreator **đang hoạt động tại Việt Nam** — kết nối Brands với Creators (KOC) trên TikTok, Facebook, Instagram, YouTube...

**Quy trình:**

```mermaid
flowchart LR
    A["🏢 Brand\nđăng Campaign"] --> B["📱 Creator\ntham gia"]
    B --> C["🎬 Creator\ntạo content"]
    C --> D["✅ Content\nđược duyệt"]
    D --> E["📊 Views &\nEngagement tracking"]
    E --> F["💰 Creator\nnhận hoa hồng"]

    style A fill:#4A90D9,color:#fff,stroke:#357ABD
    style B fill:#50C878,color:#fff,stroke:#3DA35D
    style C fill:#FF6B6B,color:#fff,stroke:#EE5A5A
    style D fill:#FFB347,color:#000,stroke:#FFA233
    style E fill:#87CEEB,color:#000,stroke:#6BB3D9
    style F fill:#DDA0DD,color:#000,stroke:#CC8FCC
```

### 5 lý do mở rộng Global

```mermaid
flowchart TD
    CENTER["🌏 VCreator Global"]

    A["📈 Mở rộng thị trường\nTiếp cận creators & brands\ntại nhiều quốc gia"]
    B["💵 Quy mô kinh tế\n1 nền tảng phục vụ nhiều nước\ngiảm chi phí so với build riêng"]
    C["⚙️ Chuẩn hóa\nThêm quốc gia mới\nchỉ cần cấu hình"]
    D["🏆 Ưu thế cạnh tranh\nBrands chạy campaign\nnhiều nước cùng lúc"]
    E["🔗 Cross-country\nCreator VN ↔ PH\nnhiều cơ hội hơn"]

    CENTER --> A
    CENTER --> B
    CENTER --> C
    CENTER --> D
    CENTER --> E

    style CENTER fill:#2C3E50,color:#fff,stroke:#1A252F,stroke-width:3px
    style A fill:#E8F5E9,color:#1B5E20,stroke:#4CAF50
    style B fill:#E3F2FD,color:#0D47A1,stroke:#2196F3
    style C fill:#FFF3E0,color:#E65100,stroke:#FF9800
    style D fill:#F3E5F5,color:#4A148C,stroke:#9C27B0
    style E fill:#FFEBEE,color:#B71C1C,stroke:#F44336
```

### So sánh: Hiện tại vs Global

| | **VCreator VN (hiện tại)** | **VCreator Global (mới)** |
|---|---|---|
| **Phạm vi** | Chỉ Việt Nam | Đa quốc gia (PH, ID, CIS, EU...) |
| **Thêm nước mới** | Build lại từ đầu | Cấu hình — không code lại |
| **Tài khoản Creator** | 1 nước | 1 tài khoản dùng mọi nước |
| **Dữ liệu** | Chung | Tách biệt hoàn toàn giữa các nước |
| **Tiền tệ** | VND | Đa tiền tệ (₱, ₫, Rp, $...) |
| **Ngôn ngữ** | Tiếng Việt | Đa ngôn ngữ (Filipino, EN, VN...) |
| **Brands** | Campaign 1 nước | Campaign nhiều nước cùng lúc |

> **Quyết định quan trọng:** Xây hệ thống **hoàn toàn mới** (không nâng cấp source cũ) — thiết kế cho quy mô toàn cầu ngay từ đầu. Tuy nhiên, **tận dụng ~37% effort** từ source code cũ cùng tech stack.

---

## 2. Nền Tảng — VCreator Global là gì?

### Business Model

```mermaid
flowchart LR
    subgraph BRANDS["🏢 BRANDS"]
        B1["Tạo Campaign"]
        B2["Đặt ngân sách"]
        B3["Theo dõi ROI"]
    end

    subgraph PLATFORM["⚙️ VCREATOR GLOBAL"]
        P1["Matching\nBrand ↔ Creator"]
        P2["Content\nManagement"]
        P3["Đối soát &\nThanh toán"]
    end

    subgraph CREATORS["🎬 CREATORS"]
        C1["Tham gia Campaign"]
        C2["Tạo Content"]
        C3["Nhận hoa hồng"]
    end

    B1 --> P1
    B2 --> P1
    P1 --> C1
    C1 --> C2
    C2 --> P2
    P2 --> B3
    P2 --> P3
    P3 --> C3

    style BRANDS fill:#E3F2FD,color:#000,stroke:#2196F3,stroke-width:2px
    style PLATFORM fill:#FFF3E0,color:#000,stroke:#FF9800,stroke-width:2px
    style CREATORS fill:#E8F5E9,color:#000,stroke:#4CAF50,stroke-width:2px
```

### 4 Modules chính

```mermaid
pie title Phân bổ effort theo module (5,148h)
    "Admin Panel — 1,865h (36%)" : 1865
    "Creator App — 1,356h (26%)" : 1356
    "Brand Portal — 1,236h (24%)" : 1236
    "Platform Core — 691h (14%)" : 691
```

| Module | Giờ | Vai trò |
|---|---|---|
| **Platform Core** | 691h (14%) | Nền tảng chung: đa quốc gia, đa ngôn ngữ, tỷ giá, thuế, hạ tầng |
| **Creator App** | 1,356h (26%) | Cho Creator: đăng ký, KYC, campaign, content, thu nhập, rút tiền |
| **Admin Panel** | 1,865h (36%) | Cho vận hành: duyệt content, đối soát, thanh toán, quản lý, báo cáo |
| **Brand Portal** | 1,236h (24%) | Cho Brands: tạo campaign, budget, analytics, ROI tracking |

---

## 3. Người Dùng — Ai Sử Dụng Hệ Thống?

### Cấu trúc tổ chức

```mermaid
graph TD
    GA["🌐 GLOBAL ADMIN\n(HQ Việt Nam)\n─────────────\nDashboard tổng hợp (USD)\nCấu hình quốc gia\nKiểm toán toàn hệ thống\nBật/tắt tính năng per nước"]

    GA --> PH["🇵🇭 PHILIPPINES"]
    GA --> VN["🇻🇳 VIETNAM"]
    GA --> ID["🇮🇩 INDONESIA\n(tương lai)"]

    subgraph PH_TEAM["Philippines Team"]
        PH --> PH_A["👔 Local Admin\nMaria\n── Quản lý toàn bộ PH"]
        PH_A --> PH_F["💼 Finance\nAna\n── Đối soát, thanh toán"]
        PH_A --> PH_O["📋 Ops\nJose\n── Duyệt content, KYC"]
    end

    subgraph VN_TEAM["Vietnam Team"]
        VN --> VN_A["👔 Local Admin\nMinh\n── Quản lý toàn bộ VN"]
        VN_A --> VN_F["💼 Finance\nHà\n── Đối soát, thanh toán"]
        VN_A --> VN_O["📋 Ops\nTuấn\n── Duyệt content, KYC"]
    end

    PH_INFO["Tiền: ₱ PHP\nThuế: WHT\nKYC: PhilID\nPay: GCash + Bank"]
    VN_INFO["Tiền: ₫ VND\nThuế: TNCN\nKYC: CCCD\nPay: Bank Transfer"]

    PH -.-> PH_INFO
    VN -.-> VN_INFO

    style GA fill:#2C3E50,color:#ECF0F1,stroke:#1A252F,stroke-width:3px
    style PH fill:#3498DB,color:#fff,stroke:#2980B9,stroke-width:2px
    style VN fill:#E74C3C,color:#fff,stroke:#C0392B,stroke-width:2px
    style ID fill:#95A5A6,color:#fff,stroke:#7F8C8D,stroke-width:2px,stroke-dasharray: 5 5
    style PH_INFO fill:#D6EAF8,color:#1A5276,stroke:#3498DB
    style VN_INFO fill:#FADBD8,color:#922B21,stroke:#E74C3C
```

> **Nguyên tắc #1 — Data Isolation:** Đội PH **không thể** xem data VN và ngược lại. Chỉ Global Admin xem tổng hợp — mọi hành động đều ghi log.

### Hành trình Creator

```mermaid
flowchart LR
    S1["1️⃣ ĐĂNG KÝ\n──────\nLogin bằng\nTikTok/Google\nChọn quốc gia"]
    S2["2️⃣ XÁC MINH\n──────\nUpload giấy tờ\ntheo yêu cầu\nquốc gia đó"]
    S3["3️⃣ TÌM CAMPAIGN\n──────\nBrowse campaigns\nđang chạy ở\nquốc gia mình"]
    S4["4️⃣ TẠO CONTENT\n──────\nQuay video\nchụp ảnh\nđăng lên MXH"]
    S5["5️⃣ SUBMIT\n──────\nPaste link\ncontent lên\nplatform"]
    S6["6️⃣ THEO DÕI\n──────\nXem thu nhập\ntrạng thái\nduyệt content"]
    S7["7️⃣ RÚT TIỀN\n──────\nRút về\nngân hàng\nhoặc GCash"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7

    style S1 fill:#4A90D9,color:#fff,stroke:#357ABD
    style S2 fill:#F39C12,color:#fff,stroke:#E67E22
    style S3 fill:#2ECC71,color:#fff,stroke:#27AE60
    style S4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style S5 fill:#9B59B6,color:#fff,stroke:#8E44AD
    style S6 fill:#1ABC9C,color:#fff,stroke:#16A085
    style S7 fill:#E91E63,color:#fff,stroke:#C2185B
```

**Điểm đặc biệt ở Global:**
- **1 tài khoản dùng cho tất cả quốc gia** — login 1 lần, switch giữa các nước
- Mỗi quốc gia có **profile riêng**: giấy tờ KYC, tài khoản ngân hàng, thu nhập, thuế
- Thu nhập hiển thị bằng **tiền tệ địa phương** (₱ cho Philippines, ₫ cho Việt Nam)
- Giao diện **đa ngôn ngữ**: Filipino, Tiếng Việt, English

### Ma trận vai trò & quyền hạn

| Chức năng | Creator | Local Ops | Local Finance | Local Admin | Global Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| Tạo content & submit | ✅ | | | | |
| Xem thu nhập & rút tiền | ✅ | | | | |
| Duyệt content | | ✅ | | ✅ | ✅* |
| Duyệt KYC | | ✅ | | ✅ | ✅* |
| Đối soát & thanh toán | | | ✅ | ✅ | ✅* |
| Quản lý Campaign | | | | ✅ | ✅* |
| Quản lý Team & Role | | | | ✅ | ✅* |
| Cấu hình quốc gia | | | | | ✅ |
| Dashboard tổng hợp | | | | | ✅ |
| Kiểm toán toàn hệ thống | | | | | ✅ |

> *\* Global Admin "vào vai Local" → bắt buộc nhập lý do, mọi hành động được ghi log.*

---

## 4. Quy Trình — Hệ Thống Hoạt Động Như Thế Nào?

### Campaign Lifecycle

```mermaid
sequenceDiagram
    actor Brand as 🏢 Brand
    participant Admin as 👔 Local Admin
    actor Creator as 🎬 Creator
    participant Ops as 📋 Ops Team
    participant Finance as 💼 Finance
    participant Platform as ⚙️ Platform

    Brand->>Admin: Tạo Campaign + ngân sách
    Admin->>Admin: Duyệt Campaign
    Admin->>Platform: Publish Campaign

    Creator->>Platform: Browse & tham gia Campaign
    Platform->>Creator: Xác nhận tham gia

    Creator->>Platform: Submit content (link MXH)
    Platform->>Ops: Thông báo content mới

    Ops->>Ops: Review content
    alt Content đạt
        Ops->>Platform: Approve ✅
        Platform->>Creator: Thông báo: Content được duyệt
        Platform->>Platform: Tracking views & engagement
    else Content chưa đạt
        Ops->>Platform: Reject / Yêu cầu sửa ❌
        Platform->>Creator: Thông báo: Cần chỉnh sửa
    end

    Note over Platform: Cuối kỳ đối soát

    Finance->>Platform: Tạo batch đối soát
    Platform->>Finance: Preview tổng thu nhập creators
    Finance->>Finance: Chốt tỷ giá
    Finance->>Platform: Phê duyệt batch

    Platform->>Platform: Thực hiện thanh toán
    Platform->>Creator: 💰 Chuyển tiền (Bank/GCash)
    Platform->>Creator: Thông báo: Đã thanh toán
```

> **Takeaway:** Toàn bộ quy trình từ Brand tạo campaign → Creator nhận tiền diễn ra trên cùng 1 platform, với nhiều lớp kiểm duyệt đảm bảo chất lượng.

### Quy trình Đối soát & Thanh toán

```mermaid
sequenceDiagram
    actor Finance as 💼 Finance
    participant Platform as ⚙️ Platform
    participant Bank as 🏦 Payment Gateway
    actor Creator as 🎬 Creator

    Finance->>Platform: Tạo Batch đối soát mới
    Platform->>Platform: Tổng hợp thu nhập creators (content đã duyệt trong kỳ)
    Platform->>Finance: Preview: danh sách creators + số tiền

    Finance->>Platform: Chốt tỷ giá (USD → local)
    Note over Platform: Tỷ giá lệch >5% sẽ cảnh báo tự động

    Finance->>Platform: Phê duyệt Batch ✅
    Note over Platform: Batch đã duyệt = Không thể sửa

    Platform->>Platform: Tính thuế per creator (Gross - Tax = Net)
    Platform->>Bank: Gửi lệnh chuyển tiền

    alt Thanh toán thành công
        Bank->>Platform: Xác nhận ✅
        Platform->>Creator: 💰 Tiền về tài khoản
    else Thanh toán thất bại
        Bank->>Platform: Lỗi ❌
        Platform->>Finance: Thông báo — cần Retry
        Finance->>Platform: Retry hoặc hoàn vào balance
    end

    Note over Finance,Platform: Nếu chốt tỷ giá sai<br/>→ Tạo batch điều chỉnh MỚI<br/>(không sửa batch cũ)
```

> **Takeaway:** Minh bạch tài chính — mọi con số rõ ràng, tỷ giá chốt cố định, batch đã duyệt không thể sửa (nếu sai → tạo batch điều chỉnh mới).

### 3 nguyên tắc thiết kế cốt lõi

```mermaid
graph TD
    subgraph P1["🔒 AN TOÀN DỮ LIỆU"]
        D1["3 lớp bảo vệ:\nGiao diện → API → Database\nđều filter theo quốc gia"]
        D2["Đội PH không xem được data VN\nvà ngược lại"]
        D3["Kiểm thử tự động\nAlert khi bất thường"]
    end

    subgraph P2["💰 MINH BẠCH TÀI CHÍNH"]
        F1["Thu nhập bằng tiền địa phương\n₱ PHP / ₫ VND"]
        F2["Phân biệt rõ:\nĐã xác nhận vs Đang chờ"]
        F3["Công thức rõ ràng:\nGross → Thuế → Net"]
    end

    subgraph P3["📝 KIỂM TOÁN"]
        A1["Mọi hành động quan trọng\nđều được ghi log"]
        A2["Global Admin vào vai Local\n→ bắt buộc nhập lý do"]
        A3["Log không thể\nsửa hoặc xóa"]
    end

    style P1 fill:#E8F5E9,color:#1B5E20,stroke:#4CAF50,stroke-width:2px
    style P2 fill:#E3F2FD,color:#0D47A1,stroke:#2196F3,stroke-width:2px
    style P3 fill:#FFF3E0,color:#E65100,stroke:#FF9800,stroke-width:2px
```

---

## 5. Mở Rộng — Thêm Quốc Gia Bằng Cấu Hình

Đây là **điểm mạnh lớn nhất** của VCreator Global: thêm quốc gia mới **không cần code lại** — chỉ cần cấu hình.

### Quy trình thêm quốc gia mới

```mermaid
flowchart TD
    START["🌏 Muốn thêm quốc gia mới?"]

    START --> LEGAL["📋 LEGAL & COMPLIANCE\n(Tuần 1-2)\n──────────────\nNghiên cứu thuế per country\nXác định yêu cầu KYC\nĐánh giá privacy laws\nSoạn T&C, Contract"]

    LEGAL --> CONFIG["⚙️ CẤU HÌNH PLATFORM\n(Tuần 2-3, song song)\n──────────────\nTạo Country Config\nSetup tỷ giá & thuế\nConfig KYC & payment\nBật/tắt features"]

    CONFIG --> CONTENT["📝 NỘI DUNG & ĐỘI NGŨ\n(Tuần 3-4, song song)\n──────────────\nDịch giao diện\nTạo content templates\nTuyển & training local team"]

    CONTENT --> QA["🧪 KIỂM THỬ & GO-LIVE\n(Tuần 4)\n──────────────\nKiểm thử toàn bộ quy trình\nXác minh tách biệt dữ liệu\nUAT với local team\nSoft launch → Go-live"]

    QA --> DONE["✅ QUỐC GIA MỚI\nĐÃ HOẠT ĐỘNG!\n──────────────\n574h · ~4 tuần\nCountry 3+: chỉ 70-80%"]

    style START fill:#2C3E50,color:#ECF0F1,stroke:#1A252F,stroke-width:2px
    style LEGAL fill:#FFF9C4,color:#F57F17,stroke:#FBC02D,stroke-width:2px
    style CONFIG fill:#E3F2FD,color:#0D47A1,stroke:#2196F3,stroke-width:2px
    style CONTENT fill:#F3E5F5,color:#4A148C,stroke:#9C27B0,stroke-width:2px
    style QA fill:#E8F5E9,color:#1B5E20,stroke:#4CAF50,stroke-width:2px
    style DONE fill:#1B5E20,color:#fff,stroke:#0D3F12,stroke-width:3px
```

### Phân bổ effort thêm quốc gia mới (574h)

```mermaid
pie title Effort per country mới (574h)
    "Platform Config — 164h (29%)" : 164
    "Content & i18n — 144h (25%)" : 144
    "QA & Launch — 104h (18%)" : 104
    "Legal & Compliance — 76h (13%)" : 76
    "Payment & Finance — 50h (9%)" : 50
    "Local Ops Setup — 36h (6%)" : 36
```

### Lộ trình mở rộng

```mermaid
flowchart LR
    PH["🇵🇭 Philippines\n(Phase 1)\n──────\nGo-live cùng\nplatform mới"]
    VN["🇻🇳 Vietnam\n(Phase 3)\n──────\nMigrate từ\nhệ thống cũ"]
    ID["🇮🇩 Indonesia\n(Phase 3+)\n──────\nQuốc gia\nthứ 3"]
    CIS["🌍 CIS / EU\n(Tương lai)\n──────\nMở rộng\ntiếp theo"]

    PH --> VN --> ID --> CIS

    style PH fill:#3498DB,color:#fff,stroke:#2980B9,stroke-width:3px
    style VN fill:#E74C3C,color:#fff,stroke:#C0392B,stroke-width:2px
    style ID fill:#F39C12,color:#fff,stroke:#E67E22,stroke-width:2px
    style CIS fill:#95A5A6,color:#fff,stroke:#7F8C8D,stroke-width:2px,stroke-dasharray: 5 5
```

> **Takeaway:** Mỗi quốc gia mới = **574h effort + 4 tuần timeline**. Country thứ 3+ chỉ cần ~70-80% nhờ kinh nghiệm và templates từ các nước trước. **Scale mà không cần code lại.**

---

## 6. Đầu Tư — Effort, Timeline, Team

### Tổng quan effort

| Hạng mục | Build mới | Giảm nhờ reuse | **Còn lại** | **% giảm** |
|---|---:|---:|---:|---:|
| Backend | 2,820h | -1,109h | **1,711h** | 39% |
| Frontend | 2,524h | -879h | **1,645h** | 35% |
| QC/Test | 918h | -372h | **546h** | 41% |
| PM | 736h | -221h | **515h** | 30% |
| SA | 494h | -166h | **328h** | 34% |
| BA | 448h | -154h | **294h** | 34% |
| DevOps | 80h | -24h | **56h** | 30% |
| Design | 88h | -35h | **53h** | 40% |
| **TỔNG** | **8,108h** | **-2,960h** | **5,148h** | **~37%** |

> **Tiết kiệm ~37%** nhờ tận dụng source code cũ cùng tech stack (Go/Echo + React/UmiJS + MongoDB).

### Phân bổ theo role

```mermaid
pie title Phân bổ effort theo role (5,148h)
    "Backend — 1,711h (33%)" : 1711
    "Frontend — 1,645h (32%)" : 1645
    "QC/Test — 546h (11%)" : 546
    "PM — 515h (10%)" : 515
    "SA — 328h (6%)" : 328
    "BA — 294h (6%)" : 294
    "DevOps — 56h (1%)" : 56
    "Design — 53h (1%)" : 53
```

### Timeline — 3 Phases

```mermaid
gantt
    title VCreator Global — Timeline triển khai
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Phase 1 — Core
    Platform Core (Hạ tầng)          :p1_core, 2026-04-01, 30d
    Creator App (Core features)      :p1_creator, after p1_core, 40d
    Admin Panel (Core features)      :p1_admin, 2026-04-20, 50d
    PH Setup & Testing              :p1_ph, after p1_admin, 20d

    section Phase 2 — Enhancement
    Platform Enhancement             :p2_pc, after p1_core, 10d
    Creator Enhancement              :p2_creator, after p1_creator, 20d
    Admin Enhancement                :p2_admin, after p1_admin, 20d
    Brand Portal (Core + Enhance)    :p2_brand, after p1_admin, 50d

    section Phase 3 — Expansion
    Brand Portal Advanced (API)      :p3_api, after p2_brand, 15d
    VN Migration (nếu cần)          :p3_migrate, after p3_api, 30d
    Indonesia Setup                  :p3_id, after p3_migrate, 28d
```

> **Note:** Timeline minh họa dựa trên team ~10 người. Ngày bắt đầu thực tế tùy thuộc thời điểm kick-off.

### Phân bổ effort theo Phase

```mermaid
pie title Effort theo Phase (5,148h — excl. Migration)
    "Phase 1 — Core (2,945h)" : 2945
    "Phase 2 — Enhancement + Brand Portal (2,145h)" : 2145
    "Phase 3 — Advanced (58h)" : 58
```

| Phase | Nội dung | Giờ | % |
|---|---|---:|---:|
| **Phase 1 (Core)** | Platform Core + Creator + Admin → **PH Go-live** | 2,945h | 57% |
| **Phase 2 (Enhancement)** | Enhancement (1,328h) + Brand Portal (817h core) | 2,145h | 42% |
| **Phase 3 (Advanced)** | Brand Portal Advanced — API/Webhook | 58h | 1% |
| *Migration (tách riêng)* | *VN data migration — chỉ khi cần* | *136h* | *—* |

> **Note:** Brand Portal tổng 1,236h được chia: 817h Phase 2A core + 361h Phase 2B enhancement + 58h Phase 3 advanced.

### So sánh Team Size & Timeline

| Scenario | Team | BE | FE | Timeline | Ghi chú |
|---|---|---|---|---|---|
| **A. Team hiện tại** | 8 người | BE×2 | FE×2 | ~5.3 tháng | Khả thi, nhưng kéo dài |
| **B. Tăng nhẹ** | 10 người | BE×3 | FE×3 | ~3.6 tháng | **Cân bằng chi phí & tốc độ** |
| **C. Giữ D+85** | 8-9 người | BE×2.5 | FE×2 | ~4.25 tháng | Chỉ cần thêm 0.5 BE |

> **Khuyến nghị:** Scenario B (10 người, 3.6 tháng) — tối ưu giữa chi phí và tốc độ ra thị trường.

---

## 7. Rủi Ro & Giải Pháp

### Ma trận rủi ro

```mermaid
quadrantChart
    title Rủi Ro — Impact vs Likelihood
    x-axis Low Likelihood --> High Likelihood
    y-axis Low Impact --> High Impact
    quadrant-1 "Theo dõi chặt"
    quadrant-2 "Ưu tiên xử lý"
    quadrant-3 "Chấp nhận"
    quadrant-4 "Giảm thiểu"
    "Rò rỉ data giữa nước": [0.25, 0.92]
    "Chốt tỷ giá sai": [0.35, 0.85]
    "Timeline aggressive": [0.55, 0.52]
    "Compliance khác mỗi nước": [0.45, 0.55]
    "VN Migration phức tạp": [0.40, 0.50]
    "Local team chưa quen": [0.60, 0.30]
```

### Chi tiết rủi ro & giải pháp

| # | Rủi ro | Mức độ | Giải pháp |
|---|---|---|---|
| 1 | **Rò rỉ data giữa quốc gia** | 🔴 Cao | 3 lớp bảo vệ: UI + API + Database filter. Kiểm thử tự động. Alert bất thường. |
| 2 | **Chốt tỷ giá sai** | 🔴 Cao | Tự kiểm tra rate (lệch >5% → cảnh báo). Preview trước khi chốt. Sai → batch điều chỉnh mới. |
| 3 | **Timeline aggressive** | 🟡 TB | Chia phase rõ ràng. Phase 1 = 57% (core). Phase 2 = features bổ sung. |
| 4 | **Compliance khác mỗi nước** | 🟡 TB | Country Config cho phép cấu hình riêng. Research compliance TRƯỚC khi phát triển. |
| 5 | **VN Migration** | 🟡 TB | Để SAU PH go-live (Phase 3). Chạy song song 2 hệ thống. |
| 6 | **Local team chưa quen** | 🟢 Thấp | Admin panel đa ngôn ngữ. Hướng dẫn in-app. Training materials mỗi nước. |

---

## 8. Bước Tiếp Theo

### Câu hỏi cần Business chốt trước khi phát triển

| # | Câu hỏi | Ảnh hưởng | Trạng thái |
|---|---|---|---|
| 1 | **Partner Admin riêng?** Có cần role cho partner manager (chỉ xem data brand mình)? | Hệ thống phân quyền | ⬜ Chưa chốt |
| 2 | **Quy trình duyệt đối soát?** Finance tạo batch → ai phê duyệt? | Quy trình tài chính | ⬜ Chưa chốt |
| 3 | **MFA bắt buộc?** Xác thực 2 lớp cho admin, đặc biệt Finance & Global Admin? | Bảo mật | ⬜ Chưa chốt |
| 4 | **KYC có thể hoãn?** Creator browse/join trước, KYC khi rút tiền? | Tỷ lệ đăng ký mới | ⬜ Chưa chốt |
| 5 | **Phương thức thanh toán PH?** GCash, bank, hay cả hai? Vendor nào? | Rút tiền PH | ⬜ Chưa chốt |
| 6 | **Admin panel mobile?** Ops cần duyệt content trên mobile/tablet? | Scope thiết kế | ⬜ Chưa chốt |
| 7 | **Tech stack?** Tiếp tục Go + React hay stack khác? | Toàn bộ effort dev | ⬜ Chưa chốt |

### Lộ trình kick-off đề xuất

```mermaid
flowchart LR
    Q["📋 Chốt 7 câu hỏi\n(Tuần 1)"]
    K["🚀 Kick-off\n(Tuần 2)"]
    P1["⚙️ Phase 1\nPlatform Core\n+ PH Go-live\n(Tháng 1-4)"]
    P2["📈 Phase 2\nEnhancement\n+ Brand Portal\n(Tháng 4-6)"]
    P3["🌏 Phase 3\nVN Migration\n+ Expansion\n(Tháng 7+)"]

    Q --> K --> P1 --> P2 --> P3

    style Q fill:#FFF9C4,color:#F57F17,stroke:#FBC02D,stroke-width:2px
    style K fill:#E3F2FD,color:#0D47A1,stroke:#2196F3,stroke-width:2px
    style P1 fill:#E8F5E9,color:#1B5E20,stroke:#4CAF50,stroke-width:2px
    style P2 fill:#F3E5F5,color:#4A148C,stroke:#9C27B0,stroke-width:2px
    style P3 fill:#FFEBEE,color:#B71C1C,stroke:#F44336,stroke-width:2px
```

---

## Phụ Lục

### A. Tài liệu chi tiết

| Tài liệu | Nội dung | File |
|---|---|---|
| **Báo giá Platform Core** | 19 tính năng nền tảng | `baogia/PlatformCore.csv` |
| **Báo giá Creator** | 42 tính năng Creator | `baogia/Creator.csv` |
| **Báo giá Admin** | 69 tính năng Admin | `baogia/Admin.csv` |
| **Báo giá Brand Portal** | 50+ tính năng Brand | `baogia/Brand.csv` |
| **Báo giá New Country** | 29 tasks per country mới | `baogia/NewCountry.csv` |
| **Chi tiết Reuse Savings** | Phân tích ~37% giảm effort | `baogia/ReuseSavings.csv` |
| **Tổng hợp Summary** | Overview toàn bộ effort | `baogia/Summary.csv` |

### B. Glossary — Thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| **KOC** | Key Opinion Creator — người sáng tạo nội dung có ảnh hưởng |
| **Campaign** | Chiến dịch quảng cáo do Brand tạo, Creator tham gia |
| **KYC** | Know Your Customer — xác minh danh tính |
| **Đối soát** | Reconciliation — quy trình kiểm tra và xác nhận thu nhập |
| **Data Isolation** | Phân tách dữ liệu — đảm bảo mỗi nước chỉ thấy data của mình |
| **Feature Flags** | Bật/tắt tính năng cho từng quốc gia mà không cần thay đổi code |
| **Batch** | Lô thanh toán — nhóm nhiều khoản thanh toán xử lý cùng lúc |
| **WHT** | Withholding Tax — thuế khấu trừ tại nguồn (áp dụng ở Philippines) |
| **UAT** | User Acceptance Testing — kiểm thử chấp nhận bởi người dùng thực tế |

---

*Tài liệu được tạo dựa trên phân tích brainstorming, kiến trúc kỹ thuật, và báo giá chi tiết.*
*Ngày tạo: 2026-03-03 · Phiên bản: 1.0*
*Source: VCreator-Global-Project-Overview.md + Summary.csv + NewCountry.csv*
