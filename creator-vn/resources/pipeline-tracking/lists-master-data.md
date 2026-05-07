# Lists Master Data — Danh mục giá trị hợp lệ

> **Nguồn:** `Creator Pipeline Tracking Delivery 2026 2.xlsm` (sheet "Lists master data")
> **Cập nhật:** 2026-05-04
> **Vai trò:** Enum/dropdown values dùng trong tất cả sheet — đảm bảo data consistency

---

## Lifecycle Status (8 giá trị)

Trạng thái tổng quan của creator với AT:

| # | Status | Ý nghĩa |
|---|---|---|
| 1 | **New** | Lead mới vừa thu thập |
| 2 | **Contacted** | Đã liên hệ creator |
| 3 | **Applied** | Creator đã đăng ký/apply |
| 4 | **Approved** | Đã duyệt hồ sơ |
| 5 | **Active** | Đang chạy campaign hoặc đang hoạt động |
| 6 | **Inactive** | Tạm dừng hoạt động |
| 7 | **Rejected** | Bị từ chối khi review |
| 8 | **Blacklisted** | Đưa vào blacklist (case nghiêm trọng) |

> Có thêm trạng thái `Ready` xuất hiện trong Creator Master nhưng không có trong list — có thể là `Approved + Setup Done`.

---

## List/Campaign Status (10 giá trị)

Trạng thái creator trong 1 campaign/list cụ thể:

| # | Status | Ý nghĩa |
|---|---|---|
| 1 | **Shortlisted** | Đã được đưa vào danh sách rút gọn |
| 2 | **Invited** | Đã gửi lời mời tham gia campaign |
| 3 | **Interested** | Creator quan tâm |
| 4 | **Accepted** | Đã chấp nhận tham gia |
| 5 | **Need Setup** | Cần setup platform/account trước khi chạy |
| 6 | **In Progress** | Đang chạy campaign |
| 7 | **Activated** | Đã activate (có content/đơn) |
| 8 | **Completed** | Hoàn thành campaign |
| 9 | **Paused** | Tạm dừng campaign này |
| 10 | **Removed** | Bị remove khỏi campaign |

---

## Tier (5 giá trị)

Phân loại để quyết định SLA và mức độ chăm sóc:

| # | Tier | Ý nghĩa |
|---|---|---|
| 1 | **VIP** | Tier cao nhất, senior owner, SLA ngắn |
| 2 | **Gold** | Tiềm năng tốt, cần nuôi dưỡng để lên VIP |
| 3 | **Normal** | Mức tiêu chuẩn |
| 4 | **New** | Chưa đánh giá, mới vào pool |
| 5 | **Watchlist** | Có rủi ro drama / performance kém |

---

## Định danh (sub-classification)

| Loại | Mô tả |
|---|---|
| `>100M PUB com` | Publisher với commission > 100M (top tier) |
| `>50M Pub com + tiềm năng` | Pub > 50M + nổi tiếng / follow > 100K |
| `mới` | Lead mới chưa đánh giá |
| `có rủi ro drama/...` | Creator có dấu hiệu watchlist |

---

## Platform (5 giá trị)

| Platform | Note |
|---|---|
| **Shopee** | Shopee Affiliate / Shopee Video |
| **TikTok/TAP** | TikTok content + TAP (TikTok Affiliate Program) |
| **Fanpage/Meta** | Facebook Fanpage hoặc personal page |
| **Livestream** | Livestream channel (Lazada Live, TikTok Live...) |
| **Multi-platform** | Hoạt động trên nhiều platform |

---

## Creator Type (5 giá trị)

| Type | Mô tả |
|---|---|
| **KOC** | Key Opinion Consumer — micro/nano review |
| **KOL** | Key Opinion Leader — macro influencer |
| **Fanpage** | Page chuyên bán hàng / nội dung |
| **Livestreamer** | Chuyên live commerce |
| **Agency Creator** | Creator quản lý qua agency |

---

## SLA Status (3 giá trị)

| Status | Ý nghĩa |
|---|---|
| **On Track** | Đúng tiến độ |
| **At Risk** | Có nguy cơ vượt SLA |
| **Overdue** | Đã vượt SLA, cần escalate |

---

## Next Action (12 giá trị)

Action tiếp theo Care cần làm với creator:

| # | Action |
|---|---|
| 1 | Research |
| 2 | Contact |
| 3 | Follow-up |
| 4 | Review |
| 5 | Setup platform |
| 6 | Send guideline |
| 7 | Send sample |
| 8 | Activate |
| 9 | Optimize |
| 10 | Scale |
| 11 | Reactivate |
| 12 | Pause |
| 13 | Remove |

---

## Vertical / Niche (10 giá trị)

| Vertical |
|---|
| Beauty |
| FMCG |
| F&B |
| Banking |
| Travel |
| Mom & Baby |
| Health |
| Auto |
| Fashion |
| Electronics |

---

## Tài liệu liên quan

- [mapping-guide.md](./mapping-guide.md) — Quy tắc mapping giữa 3 status concept
- [dashboard-snapshot.md](./dashboard-snapshot.md) — Funnel + KPI hiện tại
- [creator-master.csv](./creator-master.csv) — Master data sample
