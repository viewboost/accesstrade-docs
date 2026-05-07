# Roadmap — Creator VN

> **Cập nhật:** 2026-05-05

Lộ trình triển khai Creator VN chia thành **3 phase** — mỗi phase tự đứng được, có decision gate riêng. AT có thể stop bất kỳ phase nào nếu không thấy value.

---

## 🎯 Phase 1 — Cổng đăng ký + CRM cơ bản (5 tuần)

**Mục tiêu:** Phục vụ event 7/5/2026 + thay Excel cho team Care.

**Deliverable:**
- Frontend Creator VN clone từ Ambassador (theo pattern hdbank/lusso) — landing + đăng ký + campaign list/detail
- Module đăng ký user-socials clone từ TCB + tích hợp influence-meter để enrich profile
- Dashboard CRM v1 clone từ TCB — Creator List + Trang chi tiết (3 tabs)
- Conditional validation user-social trên submit content (Creator VN require, các FE khác giữ nguyên)
- Backend admin endpoints + bulk import xlsm
- Production deploy + bàn giao + training Care

**Effort:** 8 task groups, ~232h
**Báo giá:** **100tr VND** (90tr build + 10tr khởi tạo IM, vận hành miễn phí, Design AT lo)

---

## 🎯 Phase 2 — CRM Platform đầy đủ (estimate sau)

**Mục tiêu:** CRM dùng chung cho Creator VN + Ambassador + T-Fluencers + partner mới — gom 3 jobs (Affiliate + Ambassador + MCN) thành 1 hệ thống.

**6 cụm tính năng — 30 use case:**
1. Quản lý hồ sơ Creator (5 features)
2. Phân công & Công việc Care (5 features)
3. Theo dõi tiến độ & Quy trình KOC (5 features)
4. Phân hạng VIP & Quyền lợi (5 features)
5. Trao đổi & Lịch sử quan hệ (5 features) — bao gồm anti-poach
6. Báo cáo & Cổng thương hiệu (5 features) — Dashboard KPI cho AM + brand portal

**Báo giá:** Sẽ pitch sau khi AT confirm scope chi tiết.

---

## 🎯 Phase 3 — Sourcing & Outreach tự động (estimate sau)

**Mục tiêu:** Đảo chiều inbound → outbound. AT chủ động tìm creator phù hợp campaign, không chờ creator đăng ký.

**6 cụm tính năng — 38 use case:**
1. Quét & Làm giàu pool creator (6 features) — pool 5K+ creator/tuần
2. Chấm điểm & Sàng lọc (6 features) — 5 tiêu chí scoring
3. BD gửi yêu cầu tìm creator (6 features) — BD Request workflow
4. Duyệt & Kiểm soát chất lượng (5 features) — Lead/Compliance review
5. Gửi tin ngỏ lời hợp tác (8 features) — Zalo OA outreach + warm-up + suppression
6. Theo dõi chuyển đổi & Tối ưu (7 features) — UTM + funnel + ROI

**Báo giá:** Sẽ pitch sau khi Phase 2 go-live + có data thực để estimate chính xác.

---

## ⏰ Mốc cứng Phase 1

- **5/5/2026:** Frontend Creator VN go-live (creator có thể đăng ký)
- **7/5/2026:** Event "Creator For Vietnam" — kéo creator vào đăng ký
- **30/5/2026:** Dashboard CRM v1 production-ready, Care chuyển từ Excel sang CRM
