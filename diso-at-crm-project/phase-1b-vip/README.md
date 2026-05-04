# Giai đoạn 1B — Phân nhánh VIP và Bảo vệ Quan hệ

> **Thời gian:** Tuần 7 đến Tuần 10 (16/6 → 15/7/2026)
> **Demo:** https://vcreator.demo.accesstrade.click/mockup

---

## Bối cảnh

Sau Giai đoạn 1A, đội Creator Care đã chuyển hoàn toàn sang CRM. Excel đã được loại bỏ. Tuy nhiên, mỗi người phụ trách vẫn giới hạn ở khoảng năm mươi creator do phải tự nhớ ai cần liên hệ khi nào, ai đang ở tier nào, ai đang gần vỡ deadline.

Giai đoạn 1B bổ sung tầng thông minh để cho phép một người phụ trách cấp cao chăm sóc trên 50 creator một cách dễ dàng. Hệ thống tự động chấm điểm phân hạng, đặt đồng hồ SLA, cảnh báo khi có rủi ro. Người phụ trách chuyển từ vai trò "ghi chép thủ công" sang "ra quyết định chiến lược".

Giai đoạn này cũng giải quyết một bài toán doanh nghiệp lớn: chống mất quan hệ creator khi nhân sự nghỉ việc. Module Quản lý Tài sản Quan hệ là tính năng signature của giai đoạn này.

---

## Sáu module triển khai

| Module | Tên ngắn | Mục đích chính |
|---|---|---|
| [M3](./m3-tier-scoring.md) | Hệ thống Chấm điểm Phân hạng | Tự động phân tier creator (Normal/Gold/VIP/Watchlist) |
| [M4](./m4-sla-timer.md) | Đồng hồ SLA và Leo thang | Đảm bảo creator được phản hồi trong thời gian cam kết |
| [M10](./m10-performance-sync.md) | Đồng bộ Hiệu suất | Lấy dữ liệu GMV/đơn hàng từ Shopee, TikTok, ambassador |
| [M11](./m11-performance-care.md) | Bảng điều khiển Chăm sóc Hiệu suất | Hỗ trợ ra quyết định Scale/Optimize/Pause |
| [M16](./m16-relationship-vault.md) | Quản lý Tài sản Quan hệ | Bảo vệ quan hệ creator khỏi việc mất khi nhân sự nghỉ |
| [M15](./m15-reporting.md) | Báo cáo và Xuất dữ liệu | Pre-built reports + custom query + xuất Excel |

---

## Câu chuyện một ngày của Lead (sau Giai đoạn 1B)

Tám giờ sáng, Phương (Lead Creator Care) đăng nhập CRM. Cô vào Reports Dashboard.

Cô thấy KPI tổng quan đội: 48 active people, 250+ creator đang được chăm sóc, 22% đã đạt VIP tier, GMV tuần này 2.8 tỷ. SLA compliance toàn đội 92% — tốt hơn target 90%.

Cô vào SLA Risk Dashboard, thấy ba creator đang có nguy cơ vỡ SLA dưới 2 giờ. Một thuộc Linh, một thuộc Trang. Cô nhắn nhở qua chat nội bộ.

Cô chuyển sang AM Detail của Mai. Mai đang trong giai đoạn offboarding (sẽ nghỉ việc tuần sau). Cô thấy hai mươi tám creator của Mai đang chờ bàn giao. M16 đã tự động đề xuất kế hoạch handoff: phân phối đều cho ba người phụ trách khác dựa trên ngành và workload. Cô review, đồng ý, bấm "Approve all".

Hệ thống tự động:
- Khóa quyền truy cập Zalo cá nhân của Mai
- Audit toàn bộ conversation đảm bảo không có tin nhắn ngoài hệ thống
- Tạo lịch giới thiệu creator với người phụ trách mới qua Zalo OA chính thức
- Lên kế hoạch theo dõi tỷ lệ giữ chân creator trong 90 ngày sau bàn giao

Cô vào Performance Care Dashboard, thấy năm creator đang có dấu hiệu performance giảm. Cô flag để các người phụ trách Care bắt đầu chiến dịch reactivation.

Cuối ngày, cô xuất báo cáo tuần ra Excel để chia sẻ với leadership.

---

## Tích hợp tổng thể với Giai đoạn 1A

Sáu module mới kết hợp với bảy module cũ tạo thành hệ thống hoàn chỉnh:

```
Creator vào CRM (M1, từ 1A)
        ↓
M3 chấm điểm phân hạng tự động → tier (Normal/Gold/VIP/Watchlist)
        ↓
M5 phân công người phụ trách dựa trên tier (1A) + scoring data (1B)
        ↓
M4 khởi động đồng hồ SLA tương ứng tier × lifecycle state
        ↓
Người phụ trách làm việc trên Console (M6, từ 1A)
        ↓
M7 lưu trao đổi → M16 tích lũy Relationship Capital
        ↓
M10 đồng bộ hiệu suất từ Shopee/TikTok/ambassador
        ↓
M11 phát hiện anomaly → đề xuất action (Scale/Optimize/Pause)
        ↓
M14 thông báo cảnh báo khi cần (1A) + M15 báo cáo định kỳ (1B)
        ↓
Khi nhân sự nghỉ việc:
   → M16 kích hoạt offboarding workflow
   → Audit conversation, lock channel, handoff với ceremony
   → Creator không bị mất
```

---

## Mục tiêu đo lường giai đoạn

| Chỉ số | Mục tiêu |
|---|---|
| Tỷ lệ chuyển đổi từ VIP Tiềm năng sang VIP Chính thức | Tăng gấp 2× |
| Tỷ lệ tuân thủ SLA bốn đến tám giờ cho VIP | Trên 90% |
| Năng suất xử lý của mỗi người phụ trách so với Excel | Tăng gấp 3× |
| Tỷ lệ giữ chân creator khi người phụ trách cũ nghỉ việc | 100% |

---

## Vai trò liên quan

- **Người phụ trách Care và Senior Care:** Hưởng lợi nhiều nhất từ tự động hóa
- **Trưởng nhóm Lead:** Có công cụ quản lý tổng thể, theo dõi hiệu suất
- **HR và Legal:** Tham gia thiết kế chính sách M16 anti-poach
- **Đội kỹ thuật Diso:** Vận hành scoring engine, tích hợp dữ liệu Shopee/TikTok

---

## Liên quan trong demo

- **AM Offboarding (M16 signature):** https://vcreator.demo.accesstrade.click/mockup/ams/am-mai/offboarding
- **SLA Risk Dashboard (M4):** https://vcreator.demo.accesstrade.click/mockup/sla
- **Reports Dashboard (M15):** https://vcreator.demo.accesstrade.click/mockup/dashboard
- **Creator Detail xem đầy đủ tier + lifecycle + relationship:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
