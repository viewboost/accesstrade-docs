# Lớp 6 — Công cụ Yêu cầu BD

---

## Mục đích

Lớp 6 là giao diện chính cho đội Phát triển Kinh doanh (BD) chủ động yêu cầu hệ thống tìm creator phù hợp cho campaign cụ thể. Đây là điểm vào (entry point) của workflow sourcing — không có BD request thì không có outreach.

Mục tiêu: BD nhập yêu cầu trong vòng 2 phút, nhận top suggestion trong 5 giây, chọn subset để push xuống approval cascade. Quá trình minh bạch, BD hiểu rõ tại sao creator này được suggest.

---

## Người dùng chính

- **BD AccessTrade:** Người dùng chính, nhập request thường xuyên
- **Lead Care:** Theo dõi BD request volume, hỗ trợ BD viết request tốt hơn
- **Brand (gián tiếp):** Hưởng lợi từ tốc độ phản hồi nhanh khi cần tìm creator

---

## Câu chuyện sử dụng

Đức là BD phụ trách campaign TCB Visa Q4. Brand TCB cần thêm 50 creator phù hợp ngành finance hoặc lifestyle Gen Z trong 14 ngày.

Đức vào CRM, mở "BD Request". Form hiện ra với các trường:
- **Brand:** TCB (chọn từ dropdown campaign đang active)
- **Industry:** Finance, Lifestyle (multi-select)
- **Follower range:** 50K-200K (slider)
- **Geographic:** Việt Nam (default)
- **Quantity needed:** 50 creator
- **Deadline:** 14 ngày
- **Special requirements:** "Audience age 22-30, content tiếng Việt" (free text)

Đức bấm "Submit Request". Hệ thống chạy AI suggest, trong 5 giây trả về 150 creator phù hợp (3x số yêu cầu để Đức có lựa chọn).

Mỗi creator hiển thị:
- Thumbnail kênh chính
- Score breakdown 5 tiêu chí (xem ở Lớp 3)
- Lý do được suggest: "Audience nữ 22-28, finance-related content history, tier prediction Gold"
- Engagement rate, GMV history nếu đã có với AT
- Cảnh báo nếu creator đang được BD khác outreach (cross-BD warning)

Đức review nhanh, lọc ra 75 creator phù hợp nhất. Bấm "Approve all → push to outreach".

75 creator chuyển sang Lớp 4 Sourcing Inbox cho Lead Phương review. Đức nhận notification "Batch BD-TCB-2026-08-15 đã submit, chờ Lead approval, dự kiến outreach trong 24h".

3 ngày sau, Đức vào dashboard cá nhân:
- 70 outreached
- 12 responded (17% — vượt mục tiêu 8%)
- 6 active sau 7 ngày (8.5% conversion)

Brand TCB được báo cáo có 6 creator mới sẵn sàng cho campaign.

---

## Tính năng cốt lõi

### BD Request form
- Brand selector (link với campaign active)
- Industry, follower range, geographic filters
- Quantity needed, deadline
- Special requirements (free text, AI parse)
- Save draft, reuse template

### AI suggest engine
- Trả về top N creator (mặc định 3x quantity)
- Score breakdown minh bạch
- Lý do suggest cho từng creator
- Sắp xếp theo match score
- Filter sau khi suggest (tinh chỉnh)

### Cross-BD coordination
- Cảnh báo nếu creator đang trong outreach của BD khác
- Cảnh báo nếu creator đã active trong CRM
- Suggest BD liên hệ trực tiếp BD khác trước khi submit trùng
- Lock creator khi đã được claim

### BD dashboard
- Tất cả request đã submit của BD
- Trạng thái từng batch (pending review, in outreach, completed)
- Response rate, conversion rate theo batch
- ROI tổng theo brand

### Request templates
- Save request thành template để reuse
- Template chia sẻ nội bộ giữa các BD
- Best practice templates do Lead Care recommend

### Approval workflow
- Submit → Lead Care review (24h SLA) → Compliance check → Outreach
- BD nhận notification mỗi bước
- BD có thể withdraw request nếu cần

---

## Tích hợp

- **Lớp 3 scoring:** dùng score để rank suggestion
- **Lớp 4 inbox:** push approved batch sang
- **Campaign management (ambassador.koc.com.vn):** đồng bộ campaign list
- **CRM Phase 1 (M16 vault):** check creator đã được claim chưa

---

## Đo lường

- Thời gian BD nhập request đến khi nhận suggestion, mục tiêu dưới 5 giây
- Tỷ lệ creator được BD chọn / tổng suggestion, theo dõi để cải thiện AI
- Số BD request mỗi tuần, mục tiêu tăng đều
- BD trust score (khảo sát hằng tháng), mục tiêu trên 4/5
- Tỷ lệ request bị reject ở Lead Care, mục tiêu dưới 10%
