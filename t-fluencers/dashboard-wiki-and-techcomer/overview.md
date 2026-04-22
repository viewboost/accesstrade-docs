# Bản nâng cấp Dashboard T-Fluencers — Tháng 4/2026

**Thời gian:** 15/04/2026
**Đối tượng:** Account Manager, Marketing, Ops, Finance — những người dùng dashboard hằng ngày mà không cần hiểu chi tiết kỹ thuật.

---

## Tại sao phải nâng cấp?

Dashboard T-Fluencers vừa qua có 2 vấn đề khiến mọi người đau đầu:

**1. Nhìn số nhưng không chắc số nghĩa gì.**
Ví dụ "Tổng phí quảng cáo" — có bao gồm video đã hủy không? Có bao gồm tiền tạm tính hay chỉ tiền đã đối soát? Hỏi 5 người ra 5 câu trả lời. Hệ quả: báo cáo sai, quyết định sai.

**2. Không phân biệt được Techcomer (CBNV TCB) với Mass (Influencer bên ngoài).**
Lãnh đạo muốn biết trong nhóm tham gia thử thách, có bao nhiêu là CBNV nội bộ? CBNV hiệu quả hơn hay Influencer bên ngoài hiệu quả hơn? Câu hỏi đơn giản nhưng dashboard cũ trả lời không nổi.

→ Đợt này team giải quyết cả hai.

---

## Có gì mới?

### 1. Wiki giải thích từng con số — bấm là hiểu ngay

Cạnh hầu hết các con số quan trọng trên dashboard giờ có một **icon chữ "i" nhỏ**.

Bấm vào → hiện popup giải thích:
- Con số đó là gì.
- Có bao gồm video đã hủy không (đa số là không).
- Có công thức tính cụ thể.
- Phần "Trend" (tăng/giảm) so với kỳ trước nghĩa là gì.

Ngoài ra trên thanh header có nút **"Wiki"** — bấm vào là mở ra một bảng tổng hợp **toàn bộ** các chỉ số của dashboard trong 1 chỗ. Phù hợp cho người mới onboard, hoặc khi cần tra cứu nhanh nhiều con số.

**Đầu bảng Wiki có ghi chú màu vàng** — nguyên tắc chung:

> Các số về video, lượt xem, phí quảng cáo đều **không tính video đã hủy**. Chỉ tính: chờ duyệt, đã duyệt, đã đối soát.

Nghĩa là các con số nhìn thấy đã là "số sạch".

### 2. Phân loại Techcomer vs Mass

Từ giờ mỗi Influencer được xếp vào một trong hai nhóm:

- **Techcomer** — CBNV Techcombank đã được xác minh.
- **Mass** — tất cả Influencer còn lại, kể cả các tài khoản đang chờ xác minh.

Ở đâu cũng thấy sự phân biệt này:

**Trong bảng Danh sách Influencer:**
- Có một cột mới tên "Nhóm".
- Techcomer hiện badge đỏ với icon cặp táp 🧳.
- Mass hiện badge xám.
- Bấm header cột để sắp xếp hoặc lọc theo nhóm.

**Trên thanh filter (trên cùng dashboard):**
- Dropdown "Influencer" giờ có 4 lựa chọn:
  - **Tất cả Influencer** — mặc định.
  - **Techcomer** — chỉ xem CBNV.
  - **Mass** — chỉ xem Influencer ngoài.
  - **Tùy chọn** — chọn tay từng người (như cũ).
- Chọn xong bấm Áp dụng → toàn bộ dashboard cập nhật theo lựa chọn.

**Trên 4 card KPI ở tab Influencer (Tổng số Influencer / Video / Lượt xem / Phí QC):**
- Dưới mỗi con số chính có thêm một **pill nhỏ**: `🧳 2 · 29%`.
- Nghĩa là: trong tổng số đó, Techcomer đóng góp 2 đơn vị (29%).
- Phần còn lại tự hiểu là Mass.

### 3. Sửa số "bị sai" nhẹ ở tab Influencer

Trước đây khi filter theo Techcomer, pill có khi hiển thị "99%" thay vì "100%". Lý do kỹ thuật là hệ thống có thể nhầm khi một user thuộc nhiều partner. Đợt này đã fix — số liệu giờ chính xác tuyệt đối.

### 4. Giấu chỉ số "Tỷ lệ nghỉ" vì đang sai công thức

Chỉ số "Tỷ lệ nghỉ" trước đây tính sai (lấy `100% - Tỷ lệ hoạt động` mà không đúng bản chất "những người từng active nhưng đã nghỉ").

→ Đã ẩn khỏi dashboard. Sẽ bật lại sau khi team backend sửa công thức.

### 5. Dọn chữ nghĩa cho nhất quán

Toàn bộ dashboard giờ dùng:
- **Techcomer** (thay cho Nhân viên / NV TCB / Employee trước đây).
- **Mass** (thay cho Khách / Guest).

Wiki mô tả đều viết theo giọng nghiệp vụ, không có thuật ngữ kỹ thuật.

---

## Chưa có gì (nhưng sẽ cân nhắc sau)

Team đã brainstorm một số ý tưởng nhưng chưa làm trong đợt này:

- **Biểu đồ "Hiệu quả Techcomer vs Mass"** dạng bar so sánh song song trên cùng trục.
- **Card riêng "Tỷ lệ hoạt động Techcomer"** — % CBNV thực sự tham gia.
- **Badge ⭐ đánh dấu Techcomer vào top 3** — phục vụ nhu cầu compliance/audit.
- **Đường riêng cho Techcomer trong biểu đồ Timeline** để thấy xu hướng tăng/giảm theo thời gian.

Các mục này phụ thuộc nhu cầu thực tế khi dùng — cứ phản hồi, team sẽ làm tiếp.

---

## Một vài câu hỏi còn để ngỏ

1. Pill `🧳 2 · 29%` hiện đang **ẩn phần Mass** (người xem tự trừ ra). Mọi người thấy ổn chưa, hay muốn hiện cả Mass cho rõ?
2. Khi filter Techcomer mà không ai có hoạt động, dashboard trống toàn số 0 — có cần hiển thị một thông báo "Không có Techcomer nào phát sinh hoạt động trong kỳ" không?
3. Có nhu cầu gắn badge ⭐ cho Techcomer khi vào top 3 leaderboard không (cho audit/compliance)?

---

## Đọc thêm

- **Chi tiết kỹ thuật:** [`prd.md`](./prd.md) — dành cho PM/Dev, liệt kê đầy đủ 17 yêu cầu chức năng + 6 yêu cầu phi chức năng.
- **Buổi brainstorm:** [`/.bmad/brainstorming-tcb-dashboard-isstaff-metrics-2026-04-15.md`](../../../../.bmad/brainstorming-tcb-dashboard-isstaff-metrics-2026-04-15.md)

---

*Có thắc mắc hoặc thấy chỗ nào khó hiểu trên dashboard, cứ phản hồi qua team T-Fluencers — mọi feedback sẽ ghi nhận cho bản cập nhật sau.*
