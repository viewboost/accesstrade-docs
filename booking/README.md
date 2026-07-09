# 📁 Dự án Booking trên Ambassador

> Dự án xây mô hình **KOC Booking** dựa trên hệ thống **Ambassador** (Go + MongoDB).
> Tài liệu đi theo quy trình: **đề bài gốc → đánh giá → chốt scope → chi tiết sprint.**

---

## 🧭 Đọc theo thứ tự

| # | Tài liệu | Nội dung |
|---|----------|----------|
| ① | [01-de-bai-goc.md](01-de-bai-goc.md) | **Đề bài gốc** — mô hình Booking yêu cầu (chuyển thể từ request gốc) + so sánh đối thủ |
| ② | [02-danh-gia-tung-module.md](02-danh-gia-tung-module.md) | **Đánh giá từng module** — đi qua từng module: giải nghĩa thuật ngữ, mức khớp Ambassador, điểm cần làm rõ |
| ③ | [03-scope-phase-1.md](03-scope-phase-1.md) | **Scope Phase 1 (Quick win)** — mục tiêu, user story, scope/out-of-scope, câu hỏi business |
| ④ | [04-sprint-1.md](04-sprint-1.md) | **Sprint 1 chi tiết** — 3 chức năng (Import / Quản lý DS / Lọc-shortlist-export) + user story |
| ⑤ | [05-phase-2-core-flow.md](05-phase-2-core-flow.md) | **Phase 2 — Core flow** — Brief · luồng invite (mời→nhận→ký) + các case · E-contract per-job |
| ⑥ | [06-phase-3-automation.md](06-phase-3-automation.md) | **Phase 3 — Automation** — Payment tracking · Brand portal (clone TCB) · Auto-report (link+email) |

---

## ⚡ Tóm tắt nhanh

- **Booking trên Ambassador** triển khai theo **4 phase**. Phase 1 = marketplace **tra cứu** creator (chưa có booking giao dịch).
- **Phase 1 ≈ 2 sprint:**
  - **Sprint 1** — Import creator từ Excel · Quản lý danh sách creator · Lọc + shortlist + export.
  - **Sprint 2** — Creator đăng ký tài khoản + mapping với hồ sơ đã import.
- **Nền tảng:** dựng admin mới (Next.js, port từ techcombank dashboard), đăng nhập bằng link, model creator độc lập tài khoản người dùng.

---

## 📌 Câu hỏi cần business chốt (xuyên suốt)

| # | Câu hỏi |
|---|---------|
| 1 | Nguồn dữ liệu creator cũ ở đâu, ai chuẩn bị/làm sạch? |
| 2 | Kho creator dùng chung hay riêng theo từng khách hàng? |
| 3 | Creator sau import hiển thị ngay hay chờ duyệt? |
| 4 | Các điểm nghiệp vụ trong từng module (xem [02](02-danh-gia-tung-module.md)) |
