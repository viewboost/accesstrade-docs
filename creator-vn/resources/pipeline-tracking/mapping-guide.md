# Mapping Guide — Lifecycle Status × List/Campaign Status × Tier

> **Nguồn:** `Creator Pipeline Tracking Delivery 2026 2.xlsm` (sheet "Mapping Guide")
> **Cập nhật:** 2026-05-04
> **Vai trò:** Định nghĩa 3 trạng thái độc lập + quy tắc đồng bộ giữa chúng

---

## 3 khái niệm cốt lõi

### A. Creator Lifecycle Status

- **Where used:** Creator Master sheet
- **Meaning:** Creator's overall relationship with AT
- **Allowed values:**
  ```
  New → Contacted → Applied → Approved → Ready → Active → Inactive / Rejected / Blacklisted
  ```

### B. List/Campaign Status

- **Where used:** Pipeline Tracking sheet
- **Meaning:** Creator's status in a specific list/campaign/program
- **Allowed values:**
  ```
  Shortlisted → Invited → Interested → Accepted → Need Setup → In Progress → Activated → Completed / Paused / Removed
  ```

### C. Tier

- **Where used:** Creator Master + Pipeline snapshot
- **Meaning:** Classification for SLA and care policy, **not a status**
- **Allowed values:**
  ```
  VIP / Gold / Normal / New / Watchlist
  ```

---

## Quy tắc mapping A từ B

| Rule | Khi nào | Hệ quả lên A | Lý do |
|---|---|---|---|
| 1 | Bất kỳ B nào = `Accepted` / `In Progress` / `Activated` | A nên là `Active` | **Active có priority** nếu creator đang làm việc trong ít nhất một list/campaign |
| 2 | B = `Need Setup` | A nên là `Approved` hoặc `Ready` | `Need Setup` = creator muốn join nhưng platform/setup chưa hoàn tất |
| 3 | Tất cả B = `Completed` và **không có campaign mới** | A có thể giữ `Active` hoặc chuyển `Inactive` sau X ngày | X được set theo operating policy |

---

## Module bị loại trừ khỏi template

- **Content Status** → quản lý ở module khác
- **Payout Status** → quản lý ở module khác

> Template Pipeline Tracking này **chỉ tracking lifecycle + campaign assignment + tier**, không tracking content publishing và payout.

---

## Tài liệu liên quan

- [lists-master-data.md](./lists-master-data.md) — Danh mục giá trị hợp lệ cho từng field
- [dashboard-snapshot.md](./dashboard-snapshot.md) — KPI + funnel hiện tại của pilot
- [creator-master.csv](./creator-master.csv) — Master data 10 creator
- [campaign-pipeline.csv](./campaign-pipeline.csv) — Pipeline assignments hiện tại
