**Subject:** Re: [DISO] Kế hoạch triển khai Tháng 9/2026 (Dự kiến)

Dear team AT,

DISO xin phản hồi từng mục trong email của AT.

---

**1. Creator Portal dùng chung — Phân tích & thiết kế**

Đầu ra của hạng mục này là hai tài liệu dưới đây. **Project Overview cũng chính là bản plan** của hạng mục:

- **Project Overview (đã chốt)**
  https://github.com/viewboost/accesstrade-docs/blob/main/ambassador/partner-app-config/project-overview-creator-app-2026-09-07.md

- **PRD đợt 1 (đang review)**
  https://github.com/viewboost/accesstrade-docs/blob/main/ambassador/partner-app-config/prd-partner-app-config-2026-09-03.md

Project Overview được đo trực tiếp trên source code ambassador ngày 07/09/2026, gồm:

- Hiện trạng 15 thư mục frontend, phân theo bốn tầng sức khoẻ kèm số commit riêng của từng app
- Nhịp phát sinh fork: 10 fork mới trong 20 tháng, chưa chậm lại
- Ba hậu quả của mô hình fork, có dẫn chứng bằng tiêu đề commit thực tế
- Chi phí một lần onboard theo quy trình hiện tại
- Đề xuất và phạm vi kỹ thuật cho `backend/`, ứng dụng mới và `admin/`
- Bảng đối chiếu ops setup được những gì trước và sau dự án
- Roadmap 4 bước, rủi ro, và chỉ số thành công

Phần thiết kế chi tiết nằm trong PRD: **mục 4 — Functional Requirements** (PC-001 → PC-017) và **mục 7 — Kiến trúc**.

---

**2. Feature chính — Creator Portal dùng chung: solution và task công việc**

- **Solution**: PRD **mục 7 (Kiến trúc)** và **mục 8 (Implementation Scope)** — nêu cụ thể thay đổi ở `backend/`, ứng dụng mới, `admin/` và hạ tầng, kèm danh sách *"Không thực hiện"* để khoá phạm vi.

- **Task công việc**: PRD **mục 6** — chia thành 3 bước. Bước 2 (dựng khung và lớp cấu hình) được tách thành **8 epic E1–E8**, mỗi epic ghi rõ phụ thuộc vào epic nào.

Hai mốc nghiệm thu đã ghi trong tài liệu:

- **Bước 2**: chạy được với một ADV mẫu nội bộ — chưa migrate ADV thật nào. Mốc này tách bạch *"khung chạy được"* khỏi *"ADV thật chạy được"*.
- **Bước 3**: migrate 01 ADV mẫu, chọn `hdbank` vì branding đơn giản nhất trong 5 ADV đang sống, đồng thời là bản gốc mà `lusso` và `parasola` được copy ra nên cấu hình sạch nhất.

*Lưu ý khi đọc hai tài liệu:* Project Overview ngày 07/09 là bản chốt mới nhất và thay thế hướng kỹ thuật nêu trong PRD đợt 1 ngày 03/09 ở phần nền tảng frontend — bản chốt **giữ `umi`, không đổi sang Next.js**. DISO sẽ cập nhật PRD cho khớp ngay trong đợt review này.

---

**3. T-Fluencers — đánh giá việc tính toán không sử dụng crawl profile**

DISO xác nhận hạng mục này **chưa được thực hiện và chưa có tài liệu đánh giá** gửi AT. Đây là thiếu sót của DISO.

DISO sẽ gửi bản đánh giá **trước ngày 18/09/2026**.

---

**4. Về tiến độ gửi kế hoạch**

DISO ghi nhận việc chậm gửi kế hoạch ba tháng liên tiếp và xin lỗi team. DISO cam kết thực hiện đúng mốc AT đưa ra:

- **Plan tuần** — gửi trước 12h thứ 6 hàng tuần.
  Bản gần nhất: trước **12h thứ 6, ngày 11/09/2026**.

- **Plan tháng** — gửi trước thứ 5 của tuần cuối tháng.
  Kế hoạch tháng 10: trước **thứ 5, ngày 24/09/2026**.
  Kế hoạch tháng 11: trước **thứ 5, ngày 29/10/2026**.

---

Nếu AT cần DISO làm rõ thêm mục nào trong hai tài liệu trên, nhờ team phản hồi để DISO bổ sung trong đợt review PRD đang mở.

Trân trọng,
**DISO Team**
