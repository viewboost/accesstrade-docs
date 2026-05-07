# Dashboard Snapshot — Pilot KPI

> **Nguồn:** `Creator Pipeline Tracking Delivery 2026 2.xlsm` (sheet "Dashboard")
> **Cập nhật:** 2026-05-04
> **Vai trò:** Snapshot chỉ số pipeline tại thời điểm chạy pilot — minh hoạ cách dashboard tracking sẽ trông

---

## AT Publisher CRM — Tracking Pipeline Template

> **Simplified model:** A = Creator Lifecycle Status | B = List/Campaign Status | C = Tier
> **Excluded:** Content & Payment modules quản lý ở module khác

---

## Creator Lifecycle Funnel

Phân bổ creator theo Lifecycle Status (Sheet A — Creator Master):

| Status | Count |
|---|---:|
| New | 1 |
| Contacted | 1 |
| Applied | 1 |
| Approved | 1 |
| Ready | 2 |
| Active | 3 |
| Inactive | 1 |
| Rejected | 0 |
| Blacklisted | 0 |
| **TỔNG** | **10** |

---

## List/Campaign Funnel

Phân bổ assignments theo List/Campaign Status (Sheet B — Pipeline Tracking):

| Status | Count |
|---|---:|
| Shortlisted | 0 |
| Invited | 1 |
| Interested | 0 |
| Accepted | 1 |
| Need Setup | 2 |
| In Progress | 2 |
| Activated | 1 |
| Completed | 0 |
| Paused | 1 |
| Removed | 0 |
| **TỔNG** | **8** |

---

## Tier View

Phân bổ creator theo tier (Sheet C — Tier):

| Tier | Creators |
|---|---:|
| VIP | 3 |
| Gold | 3 |
| Normal | 2 |
| New | 1 |
| Watchlist | 1 |
| **TỔNG** | **10** |

---

## Pilot KPI Snapshot

| Metric | Definition | Value | Target | Status |
|---|---|---:|---:|---|
| **Total Creators** | Count rows in Creator Master | 10 | 50 | 🟡 Need more |
| **Active Creators** | Lifecycle = Active | 3 | 20 | 🟡 Need more |
| **VIP Active** | Tier = VIP and Lifecycle = Active | 2 | 5 | 🟡 Need more |
| **Activated Pipeline** | List/Campaign Status = Activated | 1 | 10 | ✅ OK |
| **Overdue SLA** | SLA Status = Overdue | 3 | 0 | 🔴 Fix |
| **Total GMV** | Sum Pipeline GMV | 215.000.000đ | – | 🔵 Tracking |

---

## Insights cho team CRM at-core

### 1. Funnel đang hoạt động đúng
- 10 creator phân bổ đều qua các stage: 1 New → 1 Contacted → 1 Applied → 1 Approved → 2 Ready → 3 Active
- Chưa có Rejected/Blacklisted (tốt — chưa cần escalate compliance)

### 2. Tier distribution rất concentrated VIP/Gold
- 60% creator là VIP+Gold (6/10) — phù hợp với pilot focus tệp tier cao
- Chỉ 1 New + 1 Watchlist — đang quản lý chặt

### 3. SLA breach là vấn đề ưu tiên
- **3/10 creator đang Overdue SLA** — cần fix ngay
- Khi build CRM, **SLA dashboard + alert** phải là feature P0

### 4. Multi-list assignment chưa cao
- 10 creator nhưng chỉ 8 pipeline assignments → ~20% creator chưa vào campaign nào
- Khi scale lên, cần kiểm tra creator nào không có active pipeline

### 5. GMV concentrated
- Total GMV pilot 215M trên 10 creator — avg 21.5M/creator
- Theo Pipeline data: top contributor là `Fanpage Ăn Gì Hôm Nay` (P001, GMV 120M)

---

## Tài liệu liên quan

- [creator-master.csv](./creator-master.csv) — Source data 10 creator
- [campaign-pipeline.csv](./campaign-pipeline.csv) — 8 pipeline assignments
- [mapping-guide.md](./mapping-guide.md) — Quy tắc mapping A/B/C
- [lists-master-data.md](./lists-master-data.md) — Enum values
