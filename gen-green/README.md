# Gen-Green — Tài liệu dự án

> **Demo:** [https://demo-gen-green.diso.vn](https://demo-gen-green.diso.vn)

---

## Tích hợp Scalef — Liên kết Tài khoản

Cho phép creator Gen-Green liên kết tài khoản Scalef (affiliate) để tham gia chiến dịch bán hàng. Luồng: đăng nhập Scalef → so khớp CCCD/SĐT/Email → user chọn thông tin giữ lại → OTP xác thực → liên kết thành công.

| Tài liệu | Mô tả |
|-----------|-------|
| [Overview](scalef-integration/overview.md) | Tổng quan scope Phase 1, nguyên tắc, luồng 5 bước, data model |
| [PRD Phase 1](scalef-integration/prd-scalef-integration-v1-2026-04-12.md) | 18 FRs, 6 NFRs, 5 epics — liên kết tài khoản |

**Demo:** [https://demo-gen-green.diso.vn/lien-ket-scalef](https://demo-gen-green.diso.vn/lien-ket-scalef)

---

## Đăng ký và Phân nhóm Tài khoản

Thu thập thông tin profile cho tất cả creator (họ tên, SĐT, email). Phân loại CBNV (cán bộ nhân viên Vin) và creator bên ngoài. Toggle nhân viên → chọn cơ sở làm việc (57 cơ sở, 6 nhóm) + mã nhân viên.

| Tài liệu | Mô tả |
|-----------|-------|
| [Overview](registration-grouping/overview.md) | Tổng quan: 2 luồng, form, 57 cơ sở, staff verification, import pipeline |
| [PRD V1](registration-grouping/prd-registration-v1-2026-04-12.md) | User tự khai + admin verify: popup, form 2 bước, grouped select |
| [PRD V2](registration-grouping/prd-registration-v2-2026-04-12.md) | Employee registry + import pipeline: 4 luồng, auto-match, lifecycle |

**Demo:** [https://demo-gen-green.diso.vn/dang-ky-phan-nhom](https://demo-gen-green.diso.vn/dang-ky-phan-nhom)

---

## Cải tiến Admin Dashboard

Bổ sung filter CBNV/Cơ sở làm việc, cột phân loại creator, hashtag cá nhân, export chọn cột — trên admin hiện tại. Yêu cầu từ team vận hành (meeting 0410).

| Tài liệu | Mô tả |
|-----------|-------|
| [Overview — Yêu cầu từ Meeting 0410](admin-dashboard-upgrade/overview.md) | Yêu cầu chi tiết từ Bình: tab Nội dung, tab Creator, Analytics, Export chọn cột |
| [PRD — Phân loại CBNV & Export](admin-dashboard-upgrade/prd-admin-dashboard-upgrade-2026-04-12.md) | PRD chức năng upgrade admin dashboard |

**Demo:** [https://demo-gen-green.diso.vn/cai-tien-dashboard](https://demo-gen-green.diso.vn/cai-tien-dashboard)

---

## VCreator Dashboard v2

Dashboard analytics mới thay thế admin UMI cũ. 4 module: Thống kê (13 widgets), Nội dung, Creator, Xuất dữ liệu. Trục filter chính: Partner (ADV). Dark/Light theme.

| Tài liệu | Mô tả |
|-----------|-------|
| [PRD v2](vcreator-dashboard/prd-vcreator-dashboard-v2-2026-04-12.md) | 22 FRs, 6 NFRs, 5 epics — dashboard đầy đủ |
| [Clone Plan](vcreator-dashboard/clone-plan.md) | Kế hoạch triển khai chi tiết, feature mapping, 13 analytics widgets |
| [PRD v1](vcreator-dashboard/prd-vcreator-dashboard-2026-04-01.md) | PRD phiên bản đầu (scope hẹp hơn) |

**Demo:** [https://demo-gen-green.diso.vn/dashboard-moi](https://demo-gen-green.diso.vn/dashboard-moi)
