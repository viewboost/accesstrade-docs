# Gen-Green — Roadmap

> **Cập nhật:** 2026-04-13

---

## Timeline

| Phase | Feature | Deadline | Status |
|-------|---------|----------|--------|
| **P1** | Registration V1 + Dashboard Upgrade cơ bản | **22/04** | Đang thiết kế |
| **P2** | Scalef V1: Liên kết tài khoản | **15/05** | Đang làm việc với Scalef |
| **P3** | Scalef V2: Setup campaign, lấy link | **15/05** | Đang làm việc với Scalef |
| **P4** | VCreator Dashboard v2 | **31/05** | Chờ P1 |
| **P5** | Nâng cấp V2/V3/V4 | **T6/2026** | Backlog |

```
  T4                    T5                         T6
  13    22              15              31
  ├──────┤              │               │
  │  P1  │              │               │
  │      ├──────────────┤               │
  │      │   P2 + P3    │               │
  │      ├──────────────┼───────────────┤
  │      │         P4                   │
  │      │                              ├──────── P5 ...
  └──────┴──────────────┴───────────────┘
```

---

## P1 — Registration V1 + Dashboard Upgrade (→ 22/04)

Phân loại CBNV/Creator + thu thập SĐT/Email. Nền tảng cho mọi feature sau.

- Form 2 bước: info cơ bản + toggle nhân viên + grouped select 57 cơ sở
- Popup mandatory cho user cũ (dismiss 2 lần → bắt buộc)
- Admin: filter cơ sở làm việc, cột phân loại, export chọn cột

PRD: [Registration V1](registration-grouping/prd-registration-v1-2026-04-12.md) · [Dashboard Upgrade](admin-dashboard-upgrade/prd-admin-dashboard-upgrade-2026-04-12.md)

---

## P2 — Scalef V1: Liên kết tài khoản (→ 15/05)

Creator Gen-Green liên kết tài khoản Scalef qua OAuth SSO.

- So khớp CCCD/SĐT/Email, user chọn khi xung đột, OTP xác thực
- Bidirectional profile update, reject → ticket tự động
- **Status:** Đang làm việc với Scalef — confirm API (SSO, userinfo, profile update)

PRD: [Scalef V1](scalef-integration/prd-scalef-integration-v1-2026-04-12.md)

---

## P3 — Scalef V2: Campaign & Link (→ 15/05)

Creator tham gia chiến dịch affiliate, tạo link, xem kết quả — ngay trong Gen-Green.

- Danh sách chiến dịch, join campaign, tạo affiliate link
- Dashboard affiliate cơ bản: click, đơn, hoa hồng
- **Target:** 1K user generate doanh thu, 50 tỷ/năm

---

## P4 — VCreator Dashboard v2 (→ 31/05)

Dashboard analytics mới thay admin cũ. Next.js 16, clone từ TCB Dashboard.

- 4 module: Thống kê (13 widgets), Nội dung, Creator, Xuất dữ liệu
- Filter Partner (ADV) + CBNV/cơ sở, Dark/Light theme

PRD: [Dashboard v2](vcreator-dashboard/prd-vcreator-dashboard-v2-2026-04-12.md) · [Clone plan](vcreator-dashboard/clone-plan.md)

---

## P5 — Nâng cấp V2/V3/V4 (T6/2026)

| Feature | Mô tả |
|---------|-------|
| Registration V2 | Employee registry + import pipeline từ HR |
| Registration V3 | HR upload trực tiếp + API sync tự động |
| Scalef V3 | Vin Creator Portal — 1 tài khoản, 1 thanh toán, 1 bảng kê thuế |
| Budget System | Cap ngân sách thử thách, creator, video + cảnh báo |
| Fractional Reward | Thưởng thập phân (0.1đ–0.9đ), floor khi thanh toán |

