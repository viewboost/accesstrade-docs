# Pipeline Tracking — Data thực đang chạy

> **Nguồn gốc:** `creator-vn/Creator Pipeline Tracking Delivery 2026 2.xlsm`
> **Cập nhật:** 2026-05-04
> **Vai trò:** Đây là **dữ liệu thực** mà team Creator Care AccessTrade đang quản lý bằng Excel. Là gốc tham chiếu khi build CRM — schema + lifecycle + tier + status enum phải khớp với cách team đang vận hành.

---

## Cấu trúc folder

```
pipeline-tracking/
├── README.md                              ← file này
├── mapping-guide.md                       ← Quy tắc mapping A/B/C status
├── lists-master-data.md                   ← Enum values cho mọi field
├── dashboard-snapshot.md                  ← KPI + funnel pilot hiện tại
├── creator-master.csv                     ← 10 creator đang track (master)
├── campaign-pipeline.csv                  ← 8 pipeline assignments (campaign-creator mapping)
├── creator-nhung.csv                      ← Master view của Care Nhung (10 creator)
└── creator-nhung-pipeline.csv             ← Pipeline view của Care Nhung
```

---

## 7 sheet gốc trong Excel → format đầu ra

| Sheet gốc | Format đầu ra | File |
|---|---|---|
| Mapping Guide | Markdown (taxonomy) | [mapping-guide.md](./mapping-guide.md) |
| Lists master data | Markdown (enum tables) | [lists-master-data.md](./lists-master-data.md) |
| Dashboard | Markdown (KPI summary) | [dashboard-snapshot.md](./dashboard-snapshot.md) |
| Creator Master | CSV (data thô) | [creator-master.csv](./creator-master.csv) |
| Campaign Pipeline Tracking | CSV (data thô) | [campaign-pipeline.csv](./campaign-pipeline.csv) |
| Creator Nhung | CSV (per-care view) | [creator-nhung.csv](./creator-nhung.csv) |
| Creator Nhung Campaign Pipeline | CSV (per-care pipeline) | [creator-nhung-pipeline.csv](./creator-nhung-pipeline.csv) |

---

## Mô hình data đơn giản

Template dùng **3 concept độc lập** + quy tắc mapping:

```
┌─────────────────────────────────────────────────────────────┐
│  A. Creator Lifecycle Status (relationship với AT)          │
│     New → Contacted → Applied → Approved → Ready → Active   │
│     → Inactive / Rejected / Blacklisted                     │
└─────────────────────────────────────────────────────────────┘
                              ↕ (mapping rules)
┌─────────────────────────────────────────────────────────────┐
│  B. List/Campaign Status (creator trong 1 campaign cụ thể)  │
│     Shortlisted → Invited → Interested → Accepted →         │
│     Need Setup → In Progress → Activated → Completed /      │
│     Paused / Removed                                        │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│  C. Tier (SLA + care policy, KHÔNG phải status)             │
│     VIP / Gold / Normal / New / Watchlist                   │
└─────────────────────────────────────────────────────────────┘
```

**Loại trừ khỏi template này:**
- ❌ Content Status (quản lý ở module khác)
- ❌ Payout Status (quản lý ở module khác)

---

## Schema fields

### Creator Master — 22 columns

```
Creator ID, Creator Name, Channel URL, Main Platform, Creator Type,
Tier, Lifecycle Status, Owner, Main Vertical,
Platform Setup Ready, MCN/TAP Joined, Last Activity Date, Notes,
Sub Vertical / Product Fit, Followers / Subscribers, Avg Views / Post,
Avg Engagement Rate, GMV 30D, Orders 30D, CR,
Audience Persona, Content Format Strength
```

### Creator Nhung — 24 columns

Giống Creator Master nhưng **tách MCN status** thành 3 cột riêng:
- `MCN Meta` — đã join MCN của Meta?
- `MCN Shopee Joined` — đã join Shopee MCN?
- `MCN TAP Joined` — đã join TikTok TAP?

→ Suggest: schema này (3 cột riêng) **chính xác hơn** cho production CRM, vì creator có thể join 1 platform mà chưa join các platform khác.

### Campaign Pipeline — 18 columns

```
Pipeline ID, Creator ID, Creator Name, Campaign/List/Program,
Platform, Tier at Assignment, List/Campaign Status, Owner,
Start Date, Due Date, SLA Target (hrs), SLA Status, Next Action,
Performance Note, GMV, Orders, CR, Last Updated
```

**Lưu ý quan trọng:**
- `Tier at Assignment` — **snapshot tier tại thời điểm assign**, không phải tier hiện tại
- Khi creator lên/xuống tier, các pipeline đã assign vẫn giữ `Tier at Assignment` ban đầu (audit trail)
- `SLA Target (hrs)` — số giờ cam kết, ví dụ 8h cho VIP / 24h cho Normal / 48h cho Need Setup / 72h cho ngoài SLA

---

## Insight quan trọng cho CRM design

### 1. Per-Care view rất quan trọng
Sheet "Creator Nhung" là **filtered view của 1 Care duy nhất** (Owner = Nhung). Trong CRM cần:
- Mỗi Care có dashboard cá nhân (My Queue / My Creators)
- Filter sẵn theo Owner

### 2. Tier ≠ Status — đừng confuse
Tier là **classification để quyết định SLA và policy**, không phải status workflow. Một creator VIP có thể đang ở status `Inactive` (vẫn là VIP nhưng chưa active campaign).

### 3. Một creator nhiều assignments cùng lúc
Creator có thể có nhiều record trong Pipeline (1 Master → N Pipeline). Schema CRM:
- `creators` table (master)
- `pipeline_assignments` table (creator_id × campaign_id)

### 4. Owner là ở 2 cấp
- **Owner ở Creator Master** = Care chính của creator
- **Owner ở Pipeline** = người phụ trách creator cho campaign cụ thể (có thể khác Care chính)

### 5. SLA rules cụ thể từ data thực

| Tier at Assignment | SLA Target hours |
|---|---:|
| VIP | 8h–12h |
| Gold | 24h |
| Normal | 24h–48h |
| Watchlist | 72h (lỗi nghiêm trọng 24h) |
| Need Setup | 48h |

→ Khi build M4 SLA Timer, lấy bảng này làm baseline.

### 6. GMV format không nhất quán
- Master sheet: số nguyên `60,000,000`
- Nhung pipeline: viết tắt `2.6B`, `66M`, `79K`

→ CRM cần **chuẩn hoá format** → store integer (đơn vị VND), display formatted.

### 7. Multi-MCN tracking là nhu cầu thật
Sheet Nhung tách 3 cột MCN cho thấy Care cần biết creator đã join Shopee/TikTok TAP/Meta MCN chưa — không chỉ "đã join hay chưa". CRM cần:
- 3 boolean flags riêng cho từng platform MCN
- Hoặc bảng `creator_platform_setup` với platform + status + joined_at

---

## Câu hỏi để hỏi AT khi build CRM

1. **Status `Ready` xuất hiện trong Creator Master** nhưng không có trong Lists master — có phải `Approved + Setup Done`? Hay là status riêng?
2. **`Need Setup` tại sao SLA 48h** trong khi `Approved` có lifecycle khác? Có phải chờ creator chủ động setup?
3. **Một creator có thể bị Blacklisted nhưng vẫn còn pipeline `Paused`** không? (data hiện tại chưa có case này)
4. **Owner reassignment** — khi Care nghỉ việc, ai inherit creator của họ? Auto round-robin hay manual assign?
5. **Tier downgrade** — VIP rớt xuống Gold trong điều kiện nào? Có thay đổi pipeline đang chạy không?

---

## Tài liệu liên quan

- [../koc-management-process-v2.md](../koc-management-process-v2.md) — Quy trình 7 process đầy đủ với phân nhánh VIP
- [../vip-criteria.md](../vip-criteria.md) — Tiêu chí phân tier
- [../program-overview.md](../program-overview.md) — Tổng quan chương trình Creator For Vietnam
- [../sources.md](../sources.md) — Tài liệu nguồn cho quy trình KOC
