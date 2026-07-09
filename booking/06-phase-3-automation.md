# Phase 3 — Automation (Payment tracking · Brand portal · Auto-report)

> Phase 3 = tự động hóa + minh bạch. Phụ thuộc dữ liệu Phase 2 sinh ra (booking / content / hợp đồng / thanh toán).
> 3 phần: theo dõi thanh toán · brand portal để ADV xem report · báo cáo tự động (link + email).

---

## 1. Payment tracking — theo dõi thanh toán

**Mục tiêu:** creator (và brand qua portal) theo dõi trạng thái thanh toán từng booking — từ lúc nội dung được duyệt tới khi tiền về tài khoản. **Gate bắt buộc: chỉ thanh toán khi hợp đồng đã ký.**

### Nền tảng đã có
- Hạ tầng thanh toán trưởng thành: **đối soát** (gom khoản thành đợt) · **chuyển khoản** · **rút tiền** · **sổ cái dòng tiền** (số dư từng creator theo từng khách hàng).
- Hợp đồng đã có trạng thái + thời điểm ký.

### Khoảng trống phải xây
- **Gate HĐ chưa cắm** — hợp đồng hiện chưa liên kết với luồng thanh toán; chưa có bước kiểm tra "đã ký" trước khi chi.
- **Thiếu liên kết dữ liệu** — dòng tiền/rút tiền chưa gắn `booking_id`/`content_id`/`contract_id`.
- **Creator chưa có cách xem** trạng thái thanh toán — hiện chỉ admin thấy.

### Sơ đồ trạng thái (theo booking)

```
[Nội dung duyệt]          [HĐ ký xong]            [Vào đối soát]
       │                       │                        │
       ▼                       ▼                        ▼
pending_contract ──ký──▶ contract_signed ──gom đợt──▶ payment_pending
 (chưa ký, chưa chi)     (đã ký, chờ đối soát)        (đang đối soát,
                                                       cửa sổ giữ tiền T+N)
                                                            │
                              ┌─────────────────────────────┤
                              ▼                             ▼
                       payment_rejected            payment_confirmed
                       (đối soát loại/hoàn)         (đủ điều kiện chi)
                                                            │
                                                    ─chuyển khoản─▶
                                                            ▼
                                                   payment_completed
                                                   (tiền đã về TK creator)
```

### Gate HĐ signed — vị trí cắm
- Cắm vào **bước quyết toán đối soát** (KHÔNG vào rút tiền — đúng thiết kế đã chốt).
- Điều kiện sang `payment_confirmed`: **(1)** hợp đồng của booking đó **đã ký** (trạng thái approved + có thời điểm ký); **(2)** đã qua cửa sổ giữ tiền T+N (chống hoàn/hủy).
- HĐ chưa ký → khoản giữ ở `contract_signed`, không cho chi.

### Ai thấy gì

| Trạng thái | Creator | Brand (portal) | Admin |
|------------|---------|----------------|-------|
| pending_contract | "Chờ ký HĐ" | tổng chờ ký | đầy đủ |
| contract_signed | "Đã ký, chờ đối soát" | tổng chờ đối soát | đầy đủ |
| payment_pending | "Đang đối soát" + ngày dự kiến | tổng đang xử lý | đầy đủ + thao tác |
| payment_confirmed | "Sắp chi trả" | tổng sắp chi | đầy đủ |
| payment_completed | ngày tiền về + số tiền | tỷ lệ đã chi | đầy đủ |
| payment_rejected | lý do | tổng bị loại | đầy đủ |

**MUST:** liên kết booking/contract vào dòng tiền · cắm gate HĐ tại đối soát · API cho creator xem trạng thái · enum 6 trạng thái thanh toán.

---

## 2. Brand Portal — clone từ techcombank dashboard

**Bối cảnh:** TCB dashboard (cùng stack) đã có sẵn các màn report/analytics → clone được. **Brand hiện CHƯA có tài khoản** (Phase 1-2 đi concierge/email) → Phase 3 là **cổng self-service đầu tiên cho brand**.

### Clone tới đâu

| Tái dùng (~60%) | Phải xây lại / thay |
|-----------------|---------------------|
| Bộ UI (component, chart, filter bar, date range, KPI cards, bảng) | **Tầng đăng nhập** — TCB giả định mọi user là nhân viên nội bộ; brand là người ngoài |
| Logic export, hook query | **Lọc data theo brand** ở mọi query |
| Đa ngôn ngữ | **Kiểm tra quyền** — brand chỉ thấy data của mình |

### Brand login (brand chưa có account) — luồng MỜI

> ⚠️ Đây là **công ẩn lớn nhất** của Phase 3.

1. Admin/concierge **tạo lời mời** cho brand (gắn khách hàng + email + vai trò).
2. Brand nhận email → đặt mật khẩu / kích hoạt → tạo **tài khoản brand** (loại mới, tách biệt nhân viên nội bộ).
3. Đăng nhập sau đó bằng email/mật khẩu.
4. Token mang thông tin brand → mọi API **tự lọc theo brand**.

> Dùng **mời** (không phải tự đăng ký công khai) vì brand đã được duyệt từ Phase 1-2; cổng self-service đầu tiên cần kiểm soát chặt ai vào.

### Data scope theo brand (MUST)
- **Loại tài khoản brand mới** (tách nhân viên nội bộ) — brand_id, email, vai trò.
- **Mọi query report lọc theo brand**: booking, content, analytics, thanh toán, danh sách creator.
- RBAC tối thiểu 2 vai: **Brand Admin** (xem report + cấu hình auto-report + quản người dùng brand) · **Brand Viewer** (chỉ xem).

### Các màn report (clone, lọc theo brand)

| Màn | Nội dung | Mức |
|-----|----------|-----|
| **Tổng quan** | KPI cards (booking, content approved/rejected, view/like/comment, tỷ lệ thanh toán) + chart theo thời gian | MUST |
| **Creator** | Bảng creator của brand + drill-down hiệu suất | MUST |
| **Nội dung** | Bảng content + trạng thái duyệt + metric | MUST |
| **Thanh toán** | Trạng thái thanh toán theo booking (6 trạng thái + gate HĐ) | MUST |
| **Chiến dịch** | Breakdown theo campaign | SHOULD |
| **Export** | Xuất Excel/PDF | SHOULD |
| **Cấu hình** | Bật/tắt auto-report, tần suất, email nhận | SHOULD |

---

## 3. Auto-report ADV — link + email định kỳ

**Mục tiêu (đúng insight):** gửi **email** số liệu tóm tắt + **link** mở report đầy đủ trên brand portal, theo lịch định kỳ.

### Nền tảng đã có
- **Lịch định kỳ** (scheduler) + **gửi email** + hệ template HTML + **xuất Excel**.
- *(Hiện chỉ có template email xác thực — chưa có template báo cáo.)*

### Cơ chế

```
[Lịch định kỳ — ngày/tuần]  ──▶  Lọc brand có auto-report = BẬT
        │
        ▼
Mỗi brand: tổng hợp số liệu theo (brand, khoảng ngày)
        │
        ▼
Lưu bản ghi report + sinh LINK  /brand-portal/reports/{id}
        │
        ▼
Render email HTML (số liệu tóm tắt + nút "Mở report")  ──▶  Gửi email tới brand
```

### Số liệu trong report (MUST)
- Tổng view / like / comment trong kỳ.
- Số content approved / rejected / pending.
- Trạng thái thanh toán (tổng / tỷ lệ đã chi).
- *(per-campaign — SHOULD)*

### Link xem report — cần đăng nhập
- Link mở report **yêu cầu đăng nhập brand portal** — vì chứa **dữ liệu tài chính + đa khách hàng** (nhạy cảm), không để link công khai.
- *(Nếu cần gửi cho người ngoài chưa có tài khoản → cân nhắc token-link có thời hạn — câu hỏi business.)*

**MUST:** job định kỳ sinh report · template email báo cáo · link mở report (cần login).

---

## 4. Phụ thuộc Phase 2 (điều kiện tiên quyết)

> Phase 3 **không chạy được** nếu Phase 2 chưa có:
- **Booking gắn khách hàng** (`partner_id`) — để brand portal lọc đúng + gate đúng.
- **Liên kết booking ↔ content ↔ hợp đồng** — để theo dõi thanh toán + report.

→ Cần xác nhận Phase 2 đã chốt model booking gắn khách hàng + liên kết content/contract.

---

## 5. Câu hỏi cần business chốt

| # | Câu hỏi |
|---|---------|
| 1 | **Cửa sổ giữ tiền** (T+N) trước khi confirm thanh toán là bao nhiêu ngày? |
| 2 | Gate HĐ: booking nhiều content/mốc → HĐ ký 1 lần phủ toàn bộ, hay từng content riêng? |
| 3 | Brand login: mời + email/mật khẩu là đủ, hay cần OAuth/SSO ngay? RBAC mấy vai? |
| 4 | Auto-report link: brand luôn phải đăng nhập, hay cần **token-link** cho người ngoài? Thời hạn token? |
| 5 | Tần suất auto-report mặc định (ngày/tuần/tháng)? Ai cấu hình (admin hay brand)? Gửi nhiều email? |
| 6 | Report: brand xem **chi tiết số tiền từng creator**, hay chỉ tổng/tỷ lệ (payout là dữ liệu nhạy cảm)? |
| 7 | Export report: Excel / PDF / cả hai? Cần đóng dấu thời gian để đối chiếu chính thức không? |
| 8 | Phase 2 đã chốt booking gắn khách hàng + liên kết content/contract chưa? *(điều kiện tiên quyết)* |

---

*Phân tích Phase 3 — verify hệ thống hiện có + thiết kế. Chờ review + trả lời câu hỏi business.*
