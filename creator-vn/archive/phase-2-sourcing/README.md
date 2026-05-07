# Giai đoạn 2 — Tìm kiếm Creator Chủ động

> **Thời gian:** Tuần 11 đến Tuần 17 (16/7 → 31/8/2026)

---

## Bối cảnh

Sau Giai đoạn 1B, CRM đã hoàn thiện phần inbound — quản lý creator tự đăng ký từ sự kiện và các kênh marketing. Tuy nhiên, AccessTrade muốn tăng tốc hơn nữa: thay vì chờ creator đến, sẽ chủ động đi tìm.

Giai đoạn 2 đảo chiều dòng chảy. Đội Phát triển Kinh doanh (BD) có thể nhập yêu cầu cụ thể — ví dụ "Tìm 50 creator beauty 50K-200K cho campaign Innisfree mới" — và hệ thống sẽ:
- Quét hàng nghìn creator trên TikTok, Instagram, Facebook
- Chấm điểm để tìm ra những người phù hợp nhất
- Tự động gửi tin nhắn ngỏ lời hợp tác qua Zalo OA
- Theo dõi tỷ lệ phản hồi và chuyển đổi
- Khi creator đồng ý tham gia, chuyển vào CRM Phase 1 để tiếp tục chăm sóc

Đây là giai đoạn dài và phức tạp nhất, đòi hỏi sự cẩn trọng cao về compliance để không bị Zalo OA flag spam.

---

## Bảy lớp triển khai

Phase 2 không chia thành module riêng lẻ như Phase 1. Thay vào đó, hệ thống được tổ chức thành bảy lớp xếp chồng nhau, mỗi lớp xử lý một bước trong pipeline:

| Lớp | Tên | Mục đích chính |
|---|---|---|
| [1](./layer-1-ingestion.md) | Thu thập dữ liệu | Quét creator từ TikTok, Instagram, Facebook (dùng Metric POC có sẵn) |
| [2](./layer-2-enrichment.md) | Làm giàu hồ sơ | Bổ sung dữ liệu chi tiết qua influence-meter |
| [3](./layer-3-scoring.md) | Chấm điểm lead | Tính điểm phù hợp 0-100 dựa trên 5 tiêu chí |
| [4](./layer-4-sourcing-inbox.md) | Hộp thư tìm kiếm | Giao diện cho người phụ trách review và duyệt |
| [5](./layer-5-outreach.md) | Ngỏ lời hợp tác | Gửi tin nhắn cá nhân hoá qua Zalo OA |
| [6](./layer-6-bd-request.md) | Công cụ yêu cầu BD | Form cho BD nhập nhu cầu, AI đề xuất danh sách |
| [7](./layer-7-attribution.md) | Theo dõi chuyển đổi | Đo hiệu quả từ outreach đến creator active |

---

## Câu chuyện một ngày của BD (sau Giai đoạn 2)

Đức là BD phụ trách campaign TCB Visa Q4. Brand TCB cần thêm 50 creator phù hợp ngành finance hoặc lifestyle Gen Z trong 14 ngày tới.

Đức vào CRM, mở "BD Request". Form hiện ra:
- Brand: TCB
- Industry: Finance, Lifestyle
- Follower range: 50K-200K
- Geographic: Việt Nam
- Quantity needed: 50 creator
- Deadline: 14 ngày
- Special requirements: Audience age 22-30, content tiếng Việt

Đức bấm "Submit Request". Hệ thống chạy AI suggest, trong vòng 5 giây trả về 150 creator phù hợp (3 lần số yêu cầu để Đức có lựa chọn).

Mỗi creator có:
- Score breakdown 5 tiêu chí
- Lý do được suggest (ví dụ "Audience nữ 22-28, finance-related content history")
- Engagement rate, GMV history nếu đã có với AT
- Thumbnail kênh chính

Đức review nhanh, chọn 75 creator (lọc bớt những người không match). Bấm "Approve all → push to outreach".

Hệ thống chuyển 75 creator vào outreach queue. Compliance review tự động (auto-pass cho creator không có flag rủi ro). 70 creator được approve cho outreach.

Sau 24 giờ, hệ thống đã gửi tin nhắn cho 70 creator qua Zalo OA, dùng template đã được personalize cho TCB campaign. 12 creator phản hồi đồng ý quan tâm. Chuyển vào CRM Phase 1, được auto-assign cho người phụ trách Care.

Đức theo dõi dashboard: 70 outreached, 12 responded (17% response rate, vượt mục tiêu 8%), 6 đã active sau 7 ngày (8.5% conversion). Brand TCB được báo cáo đã có 6 creator mới sẵn sàng cho campaign.

---

## Pipeline tổng thể

```
Metric POC scrapers crawl liên tục
        ↓
[Lớp 1] Hard-filter ngay khi ingest (≥10K follower, VN content)
        ↓
[Lớp 2] influence-meter làm giàu profile
        ↓
[Lớp 3] Chấm điểm 0-100, 5 tiêu chí, classify industry/tier
        ↓
Lưu vào pool sourcing
        ↓
        ↓ Khi BD nhập request:
[Lớp 6] BD Request form → AI match top N → BD chọn subset
        ↓
[Lớp 4] Sourcing Inbox → Lead Care review (24h SLA) → Compliance check
        ↓
[Lớp 5] Outreach queue → Zalo OA personalized template
        ↓ Theo lịch warm-up + suppression list
[Lớp 7] Track response, conversion, sentiment
        ↓
Creator phản hồi đồng ý → chuyển sang CRM Phase 1
        ↓
M2 lifecycle bắt đầu, M5 phân công, M14 thông báo
```

---

## Mục tiêu đo lường giai đoạn

| Chỉ số | Mục tiêu |
|---|---|
| Số creator được thu thập mỗi tuần | Trên 5.000 hồ sơ |
| Tỷ lệ creator vượt qua bộ lọc chấm điểm | 10% đến 15% |
| Tỷ lệ phản hồi tin nhắn ngỏ lời hợp tác | Trên 8% |
| Tỷ lệ chuyển đổi từ lead tìm kiếm sang creator hoạt động | Trên 3% |
| Thời gian xử lý yêu cầu của BD | Dưới 24 giờ |

---

## Vai trò liên quan

- **BD AccessTrade:** Người dùng chính của BD Request workflow, hưởng lợi nhất từ tự động hoá
- **Lead Care:** Review approval cascade, giám sát chất lượng outreach
- **Compliance:** Cấu hình rule auto-pass, sample manual audit
- **Đội kỹ thuật Diso:** Vận hành crawler, scoring engine, tích hợp Zalo OA Business

---

## Rủi ro lớn nhất và cách giảm thiểu

Giai đoạn 2 có nhiều rủi ro hơn các giai đoạn trước. Bốn rủi ro lớn nhất:

### Rủi ro 1: Zalo OA bị flag spam
**Hậu quả:** Mất luôn kênh Zalo OA của AccessTrade, ảnh hưởng cả Phase 1
**Giảm thiểu:** Manual approval gate bắt buộc 6 tháng đầu. Warm-up sequence (Tuần 1: 50/ngày, Tuần 2: 100, Tuần 3: 200). Cool-down ngay khi nhận cảnh báo từ Zalo. Opt-out link mandatory trong mọi tin nhắn.

### Rủi ro 2: Crawler bị TikTok/Instagram block IP
**Hậu quả:** Ngưng pipeline thu thập creator
**Giảm thiểu:** Multi-region proxy rotation. Tận dụng infrastructure đã có của Metric POC. Kết hợp official APIs khi có thể (TikTok Marketing API).

### Rủi ro 3: Tỷ lệ phản hồi thấp khiến BD nản
**Hậu quả:** BD bỏ tool, quay lại tìm thủ công
**Giảm thiểu:** Score breakdown UI minh bạch để BD trust. ROI dashboard hằng ngày cho BD. Liên tục cải tiến template dựa trên A/B test.

### Rủi ro 4: Cùng creator bị nhiều BD outreach làm họ block AT
**Hậu quả:** Mất quan hệ với toàn bộ pool creator
**Giảm thiểu:** Cross-BD suppression — 1 creator được outreach một lần, fail = lock 90 ngày toàn AT. Thông báo BD khác trước khi họ submit request trùng creator.

---

## Tài liệu tham khảo

Tài liệu brainstorm đầy đủ về kiến trúc Phase 2: `.bmad/brainstorming/phase-2-sourcing-architecture-2026-05-01.md`
