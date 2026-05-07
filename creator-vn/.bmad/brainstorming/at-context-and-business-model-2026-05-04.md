# Bối cảnh AT & Business Model Creator VN

> **Loại tài liệu:** Brainstorming output từ chat với AT
> **Ngày:** 2026-05-04
> **Mục đích:** Lưu insight từ trao đổi với AT để align scope, business model, kiến trúc trước khi viết roadmap chính thức.

---

## 🎯 Bối cảnh AT đưa ra (chat với Diso ngày 2026-05-04)

### Lần 1 — 3 nhu cầu cốt lõi

1. **Cào dữ liệu social** (đã hợp tác Metric POC thành công)
   - Mục đích: outreach tới KOC tiềm năng, gửi lời mời
   - Trạng thái: Đã có infrastructure, sẽ ghép vào hệ thống mới

2. **KOC đăng ký tham gia**
   - Đã có module KOC profile (cào đủ thông tin creator để phê duyệt tham gia dự án)
   - Bản chất: form đăng ký + thu thập profile

3. **Hệ thống chăm sóc + quản lý quan hệ KOC** (đang thiếu)
   - Quản lý các kênh kết nối
   - **Ngăn chặn AM nghỉ việc lấy luôn quan hệ với KOC** ← critical concern
   - Bản chất: là **các quyền lợi được thiết kế để đảm bảo KOC được hưởng** khi tham gia hoạt động cùng hệ thống

### Lần 2 — Plan cho event 7/5

> "7/5 có 1 bản kéo creator vào luôn có profile onboard như TCB. Sau đó plan phát triển hoàn thiện trong 1 tháng."

**Hệ quả:**
- 7/5 launch: cổng đăng ký + onboarding flow như TCB (đã proven)
- Sau 7/5: hoàn thiện CRM trong 1 tháng

### Lần 3 — Architecture insight

> "Về cơ bản OK vì chị thấy nó đơn giản là 1 trang ambassador như Tfluencer, rút ngắn thời gian phải đi design lại hệ thống."
>
> "Có 1 điểm là nó sẽ gom tất cả các job lại:
> 1. Affiliate
> 2. Ambassador
> 3. TAP/Shopee MCN"
>
> "Đúng rồi, như kiến trúc đầu năm em có vẽ. Cái Aff đã nối được vào rồi đúng không. Nối cả trang này vào https://mcn.accesstrade.vn"

**Hệ quả lớn:**
- Creator VN = **mặt tiền hợp nhất 3 jobs** (Aff + Ambassador + MCN)
- Creator đăng ký 1 lần → tự động vào Aff + MCN + Ambassador campaigns
- **Phải follow architecture đầu năm Diso đã vẽ** (cần tìm lại doc này)
- Phần Aff đã nối → MCN cũng phải nối tiếp pattern đó
- Domain MCN: `mcn.accesstrade.vn`

### Lần 4 — Định vị tool

> "Em nhớ con ambassador.koc.com.vn không? Bản chất em hình dung mình sẽ **nâng cấp con này, gắn CRM vào cho nó**."
>
> "**CRM chỉ gồm operation portal thôi. Còn Creator portal vẫn là creator portal.**"

**Hệ quả critical:**
- Không build platform mới — **upgrade ambassador.koc.com.vn**
- Tách rõ:
  - **Operation Portal** (mới — cho team Care/AM/BD) — Diso build
  - **Creator Portal** (giữ nguyên — creator dùng Ambassador hiện có)
- KHÔNG build trang `/me` mới
- KHÔNG build form đăng ký mới — reuse `POST /users/socials/link` của Ambassador

### Lần 5 — Plan 2 giai đoạn

> "7/5: launch cổng đăng ký"
>
> "Sau đó là hệ thống CRM quản lý, assign PIC quản lý creator"
>
> "Hệ thống CRM này:
> - **Giai đoạn 1** sẽ launch phần quản lý creator đăng ký vào hệ thống
> - **Giai đoạn 2** sẽ launch phần sourcing creator (outreach: tìm kiếm creator từ social)"

**Hệ quả:**
- AT nghĩ theo **2 sprint**, không phải 4 phases
- Sprint 1: Quản lý creator đăng ký (inbound)
- Sprint 2: Sourcing automation (outbound)

### Lần 6 — Phản hồi mockup Diso

> "Mockup ổn đó, nghiên cứu thêm thằng **CreatorIQ** cho phần sourcing."
>
> "Phần triển khai cho 7/5 chưa cho vào."
>
> "Phần quản trị các campaign để hiển thị được vid thế có thể ở ngày 7/5."
>
> "**Dồn phần dashboard quản trị KPI cho AM vào sprint 2.**"

**Hệ quả:**
- Sprint 1 thêm: phần quản trị campaign (admin) để hiển thị video creator tại event 7/5
- Sprint 2 thêm: Dashboard KPI cho AM (defer từ Sprint 1)
- Sprint 2 cần research **CreatorIQ** làm benchmark UX cho sourcing

### Lần 7 — Campaign list ở creator portal

> "Cái phần để hiển thị campaign lên ở trang creator for VN kéo creator vào đăng ký ấy. Giống cách để em hiện được các campaign trên trang ambassador.koc.com.vn."
>
> "Bản chất nó chính là **campaign list vs campaign detail ở sprint 2**."
>
> "Em mockup."

**Hệ quả:**
- Sprint 2 build: Campaign list + detail trên creator portal
- Pattern: copy từ ambassador.koc.com.vn (đã có sẵn)

### Lần 8 — Revenue share model ⚡

> "Doanh thu sẽ có revenue share."
>
> "Doanh thu ước tính 30B - 60B / năm"
>
> "Lợi nhuận gộp 20%"
>
> "10% là MCN"
>
> "Ambassador từ 25%"
>
> "ScaleF Aff = 11%"

**Decode:**

| Bên | Tỷ lệ | Tính trên |
|---|---:|---|
| MCN | 10% | Lợi nhuận gộp |
| Ambassador | 25% | Lợi nhuận gộp |
| ScaleF Aff | 11% | Lợi nhuận gộp |
| **Tổng share** | **46%** | |
| AT giữ lại | **54%** | (từ brand) |

### Lần 9 (chốt model với Diso) ⚡

> "**Diso build CRM với phí khởi tạo + revenue share.**"
>
> "**Còn cái AT đưa là AT giữ lại từ brand.**"

**→ Hai dòng tiền tách bạch:**

```
[Brand] → AT (commission từ campaign)
            │
            ├── 10% chia MCN
            ├── 25% chia Ambassador
            ├── 11% chia ScaleF Aff
            └── 54% AT giữ lại

[AT] → Diso (cho việc build CRM)
            │
            ├── Phí khởi tạo (build cost)
            └── Revenue share (% lợi nhuận từ phần AT giữ lại)
```

---

## 💼 Business Model Diso ↔ AT

### Diso receives:

1. **Phí khởi tạo (one-time)** — thanh toán theo milestone build
2. **Revenue share** — % của phần AT giữ lại từ brand (54% lợi nhuận gộp)

### Doanh thu ước tính (cho Diso)

**Conservative scenario (30B doanh thu/năm):**
- Lợi nhuận gộp: 30B × 20% = 6B
- AT giữ lại sau share đối tác: 6B × 54% = 3.24B
- Diso revenue share (giả sử 10-20%): **324M – 648M/năm**

**Optimistic scenario (60B doanh thu/năm):**
- Lợi nhuận gộp: 60B × 20% = 12B
- AT giữ lại: 12B × 54% = 6.48B
- Diso revenue share (10-20%): **648M – 1.3B/năm**

> **Note:** % revenue share của Diso chưa được AT confirm. Cần đàm phán riêng. 10-20% là estimate market practice.

### Implication cho Diso

1. **Incentive align với AT** — Diso càng build tool tốt, creator/brand càng dùng nhiều, revenue càng cao, Diso hưởng càng nhiều
2. **Long-term commitment** — Diso không phải vendor "build xong rồi đi", mà là partner dài hạn
3. **Quality bar cao** — vì revenue share, Diso có động lực đầu tư vào polish, performance, scale
4. **Phí khởi tạo có thể flex** — Diso có thể giảm phí khởi tạo để đổi lấy revenue share cao hơn (hoặc ngược lại)

---

## 🏗️ Kiến trúc System (theo confirmation AT)

### Domain pattern

```
ambassador.koc.com.vn   → Campaign management (có sẵn — sẽ upgrade)
mcn.accesstrade.vn      → MCN portal (có sẵn — Diso nối vào)
{aff platform}          → Affiliate (đã nối)
crm.koc.com.vn          → CRM Operation Portal (Diso build mới)
api-at-core.diso.vn     → at-core API (có sẵn ở Diso domain)
```

### 3 jobs hợp nhất

```
[Creator đăng ký 1 lần] → ambassador.koc.com.vn
                              ↓
              ┌───────────────┼───────────────┐
              │               │               │
         Affiliate       Ambassador        MCN
         (đã nối)       (campaigns)    (mcn.accesstrade.vn)
              ↓               ↓               ↓
         (commission)   (campaign jobs)  (TAP/Shopee MCN)
                              ↓
            [Operation Portal: CRM mới] ← Diso build
            (cho Care, AM, BD, Compliance)
```

### 2 portal tách bạch

| Portal | Domain | User | Owner build |
|---|---|---|---|
| **Creator Portal** | ambassador.koc.com.vn | Creator (KOC) | Đã có (Ambassador) |
| **Operation Portal** | crm.koc.com.vn (mới) | AT staff (Care/AM/BD/Compliance) | Diso build mới |

---

## 📅 Reframed Roadmap (2 Sprint)

### Sprint 1 — Foundation + Launch (deadline 7/5 + 1 tháng)

**Trước 7/5 (4 tuần):**
- Upgrade ambassador.koc.com.vn:
  - Trang campaign cho event "Creator For Vietnam"
  - Form đăng ký kéo creator vào (reuse OAuth + LinkUserSocial)
  - Onboarding flow giống TCB
- **Phần quản trị campaign** để hiển thị video creator tại event 7/5
- CRM Operation Portal (initial):
  - Creator List + Detail
  - Tab Channels với data influence-meter
  - Bulk import từ xlsm
  - Assign PIC

**Sau 7/5 (4 tuần — hoàn thiện):**
- Lifecycle state machine (8 status A + 10 status B từ xlsm)
- Per-Care queue (sheet "Creator Nhung")
- **Anti-poach module** (M16 Relationship Vault) — ưu tiên cao theo concern AT
- **Quyền lợi creator catalog** — track quyền lợi đã claim per creator
- SLA Timer (8h/12h/24h/48h/72h theo tier)
- Multi-MCN tracking 3 cột Meta/Shopee/TAP riêng

**KHÔNG có Sprint 1:**
- ❌ Sourcing automation (Sprint 2)
- ❌ Campaign list/detail trên creator portal (Sprint 2)
- ❌ Dashboard KPI cho AM (Sprint 2 — AT confirmed defer)

**Effort estimate:** ~400h

---

### Sprint 2 — Scale + Differentiate (~3 tháng)

**4 trụ cột:**

1. **Sourcing automation (theo CreatorIQ benchmark):**
   - Metric POC integration (đã có infra)
   - Scoring 5 criteria
   - Sourcing Inbox + Lead/Compliance approval
   - Outreach Zalo OA (warm-up + suppression)
   - BD Request workflow

2. **Campaign list + detail trên creator portal:**
   - Pattern: copy từ ambassador.koc.com.vn
   - Creator click "Join" → vào pipeline tracking

3. **Dashboard KPI cho AM:**
   - KPI per AM (creator active, GMV, SLA breach)
   - Leaderboard
   - Goal tracking
   - Performance review monthly

4. **MCN integration (mcn.accesstrade.vn):**
   - Status MCN per platform (3 cột riêng)
   - Auto join MCN khi creator approved
   - Track commission từ MCN

**Effort estimate:** ~900h

---

## 🚧 Câu hỏi mở (cần AT confirm tiếp)

### 1. Tỷ lệ revenue share Diso?
- Diso ăn % nào của phần 54% AT giữ lại?
- Có cap maximum/minimum?
- Tính trên revenue hay net profit?
- Áp dụng cho toàn dự án hay split per module?

### 2. Phí khởi tạo cụ thể?
- 80tr như báo giá option-a-50tr cũ?
- Hay điều chỉnh theo scope mới (gom 3 jobs, không build creator portal)?
- Thanh toán milestone nào (kick-off / mid / go-live / production stable)?

### 3. Architecture đầu năm
- Doc/diagram nào Diso đã vẽ?
- Ai đang giữ?
- Cần để follow đúng pattern Aff đã nối + MCN sẽ nối

### 4. Sprint 1 deliverable cho 7/5
- Mini: Chỉ trang campaign event + form đăng ký
- Compromise: Trang campaign + form go-live 5/5; CRM alpha 7/5; production cuối tháng
- Full: Trang + form + CRM complete (4 tuần khít)

### 5. Phạm vi MCN integration
- Sprint 1 chỉ display MCN status?
- Hay đầy đủ join + commission tracking?
- Có cần build webhook 2-way từ mcn.accesstrade.vn không?

---

## 🎯 Insights chính cho roadmap

### Insight 1: Reframe scope Phase 0 hiện tại
- Plan cũ (option-a-50tr): 254h build landing + form + /me + CRM mới
- Plan mới: ~150h chỉ build CRM Operation Portal + integrate vào ambassador.koc.com.vn có sẵn
- **Tiết kiệm ~100h ≈ 38tr** vì không build creator portal

### Insight 2: Anti-poach là feature P0 (ưu tiên Sprint 1)
- AT chat lần 1 nhấn mạnh: "ngăn chặn AM nghỉ việc lấy luôn quan hệ vs KOC"
- Plan cũ defer M16 Relationship Vault sang Phase 1B
- Plan mới: M16 vào **Sprint 1 hoàn thiện (tuần 5-8)** — không defer

### Insight 3: Quyền lợi catalog là module mới
- Plan cũ chưa có module này
- AT chat: "bản chất là các quyền lợi được thiết kế để đảm bảo KOC được hưởng"
- Plan mới: build "Benefits Catalog" trong Sprint 1 hoàn thiện
  - Track 6 nguồn lực (học bổng, sample, travel, Mega Live slot, GMV Max, ưu tiên)
  - Per creator: claim history, eligibility check
  - Tied to Tier (VIP unlock all, Normal limited)

### Insight 4: Revenue share thay đổi business calculus
- Diso không phải vendor outsource → là partner
- Có thể flex phí khởi tạo thấp hơn để bảo đảm dự án go-live thành công
- Long-term: Diso có incentive build platform tốt → revenue tăng → Diso hưởng theo

### Insight 5: 3-jobs architecture là north star
- Mọi quyết định kỹ thuật phải align với "1 creator đăng ký, 3 jobs tự động active"
- Không build silo theo job (Aff vs Ambassador vs MCN)
- Single source of truth = creator master ở at-core

---

## 📚 Tài liệu liên quan

- [resources/program-overview.md](../../resources/program-overview.md) — Slide chương trình Creator For Vietnam
- [resources/koc-management-process-v2.md](../../resources/koc-management-process-v2.md) — Quy trình 7 process KOC V2
- [resources/vip-criteria.md](../../resources/vip-criteria.md) — Tiêu chí phân tier
- [resources/pipeline-tracking/](../../resources/pipeline-tracking/) — Data thực 10 creator + 8 pipeline assignments
- [option-a-50tr/overview.md](../../option-a-50tr/overview.md) — Plan cũ (sẽ adjust theo brainstorm này)

---

## 🔄 Next steps

1. **AT confirm tỷ lệ revenue share** → Diso prepare contract proposal
2. **Tìm doc kiến trúc Diso đầu năm** → align technical design
3. **Research CreatorIQ** → output design spec cho Sprint 2 sourcing
4. **Viết roadmap.md final** → master plan với 2 Sprint
5. **Update option-a-50tr/overview.md** → reflect new scope (giảm landing + creator portal, focus CRM Operation Portal + anti-poach + benefits)
