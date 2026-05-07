---
title: "[DISO] Kế hoạch triển khai Tháng 5/2026"
date: 2026-05-07
---

> **Gợi ý Subject:** [DISO] Kế hoạch triển khai Tháng 5/2026

Dear team,

DISO gửi team bản **cập nhật Kế hoạch triển khai Tháng 5/2026**, gồm danh sách hạng mục, mô tả, deadline, workload ước tính và trạng thái hiện tại của từng dự án.

## 📋 Changelog – Các thay đổi so với bản kế hoạch trước

1. **Bổ sung 01 hạng mục phát sinh sau nghiệm thu**: *VCreator – Admin – Fix issue sau nghiệm thu* (7h, đã Done) — fix thứ tự hàng khi export và lỗi file export 1 cell/0 row mở thẳng bằng trình duyệt.
2. **Chính thức loại VCreator – Affiliate Center v2 khỏi kế hoạch tháng 5**, dời sang **đầu tháng 6/2026** để tập trung hoàn thiện Affiliate Center v1 đúng deadline 15/05.
3. **Điều chỉnh workload hạng mục VCreator – Affiliate Center v1 – Liên kết tài khoản ScaleF & GenGreen** từ **72h → 56h**: hai bên đã thống nhất **không xử lý nghiệp vụ giải quyết xung đột thông tin** trong v1 do đánh giá không khả thi ở thời điểm hiện tại.
4. **Chính thức bổ sung 01 hạng mục Onboard ADV mới** vào tháng 5 (29h, deadline 28/05).

Chi tiết như sau:

---

# KẾ HOẠCH THÁNG 5/2026

## 1. Dự án VCreator

| STT | Hạng mục | Mô tả | PRD | Deadline | Workload (giờ) | Trạng thái |
|-----|----------|-------|-----|----------|----------------|------------|
| 1 | Import danh sách nhân viên, duyệt nhân viên tự động | Cho phép admin import hàng loạt nhân viên (CBNV) qua file, hệ thống tự động duyệt và phân bổ vào cơ sở làm việc theo cấu trúc 3 tầng (Brand / Company / Unit), hỗ trợ điều chuyển nhân viên giữa các phòng ban. Hạng mục P5 cam kết với ADV, được đẩy lên triển khai sớm cùng nghiệp vụ Employee Registry. | [PRD](https://github.com/viewboost/accesstrade-docs/blob/main/gen-green/registration-grouping/prd-registration-v2-2026-04-12.md) | 30/05 | 38 | ✅ Done |
| 2 | Estimate Onboard Gen-Green Philippines | Phân tích yêu cầu, estimate workload và báo cáo phương án triển khai cho việc mở rộng hệ thống sang thị trường Philippines. | [Estimation](https://docs.google.com/spreadsheets/d/1cCt9rlEPfKIZpCg6tODQyvS2fMye5mV9xcr18o_c5Zo/edit?gid=0#gid=0) / [Yêu cầu ban đầu](https://docs.google.com/spreadsheets/d/1Tk9-2PJBOesZRj8H4eDqTiR6IqWWBarB0Vn0A_YJ7IQ/edit?gid=72901499#gid=72901499) | 22/05 | 12 | ✅ Done |
| 3 | Admin Dashboard v3 | Bổ sung các thông tin vào dashboard theo yêu cầu từ Bình VinPearl. Cho phép lựa chọn các trường dữ liệu phù hợp khi export. | [PRD v3](https://github.com/viewboost/accesstrade-docs/blob/main/gen-green/registration-grouping/prd-registration-v3-2026-04-30.md) | 06/05 | 16 | ✅ Done |
| 4 | Admin – Fix issue sau nghiệm thu | Sửa các lỗi cũ đã tồn tại nhưng phát hiện khi nghiệm thu:<br>- Export cần lấy thứ tự hàng giống khi hiển thị.<br>- Fix lỗi khi export cho có 1 cell hoặc không có row nào thì đang mở thẳng bằng trình duyệt. | [File nghiệm thu](#) | 06/05 | 7 | ✅ Done |
| 5 | Affiliate Center v1 | Cho phép admin setup các chương trình affiliate, liên kết với các Ambassador Campaign. Hiển thị lên cho Creator có thể đăng ký tham gia và lấy link. | [PRD admin](https://github.com/viewboost/accesstrade-docs/blob/main/gen-green/affiliate/admin-setup-overview.md) / [PRD creator](https://github.com/viewboost/accesstrade-docs/blob/main/gen-green/affiliate/fe-display-generate-link-report-overview.md) | 15/05 | 64 | 🟡 In Progress |
| 6 | Affiliate Center v1 – Liên kết tài khoản ScaleF & GenGreen (phía GenGreen Only) | Liên kết tài khoản ScaleF với GenGreen, xử lý các vấn đề khi có xung đột thông tin.<br>**Ghi chú:** Workload điều chỉnh từ 72h → 56h do hai bên đã thống nhất **không xử lý nghiệp vụ giải quyết xung đột thông tin** (không khả thi ở thời điểm hiện tại); phần scope này được loại khỏi v1. | [PRD](https://github.com/viewboost/accesstrade-docs/blob/main/gen-green/scalef-integration/prd-scalef-integration-v1-2026-04-12.md) | 15/05 | 56 | 🟡 In Progress |
| | **Tổng VCreator** | | | | **193** | |

## 2. Dự án Ambassador

| STT | Hạng mục | Mô tả | PRD | Deadline | Workload (giờ) | Trạng thái |
|-----|----------|-------|-----|----------|----------------|------------|
| 7 | Onboard ADV | Tiếp nhận và onboard 1 ADV mới trong tháng 5 (chính thức bổ sung vào kế hoạch). | – | 28/05 | 29 | ⚪ Not Started |
| | **Tổng Ambassador** | | | | **29** | |

> 🔢 **Tổng workload Tháng 5/2026: ~222 giờ**

---

## Đề xuất bù trừ giờ vượt tiêu chuẩn tháng 4/2026

Tháng 4/2026, DISO đã triển khai vượt tiêu chuẩn cam kết tổng cộng **205 giờ**, chi tiết:

| Hạng mục | BE | FE | QC | PM | Tổng (giờ) |
|----------|---:|---:|---:|---:|-----------:|
| Số giờ bù trừ vượt chuẩn tháng 4 | 108 | 38 | 48 | 17 | **205** |

DISO đề xuất AT xem xét **phương án bù trừ 205h vượt chuẩn tháng 4** sang các tháng tiếp theo. Mong team phản hồi giúp về hướng xử lý.

---

## ✅ Đề nghị xác nhận kế hoạch

Nhờ team **xác nhận lại bản kế hoạch Tháng 5/2026** ở trên để DISO làm **cơ sở nghiệm thu cuối tháng 5**. Mọi thay đổi phát sinh sau khi xác nhận hai bên sẽ thống nhất và cập nhật lại bằng văn bản.

---

**Lưu ý:** Chi tiết kế hoạch triển khai, phân bổ nguồn lực và các tài liệu liên quan, team xem tại: **[LINK](#)**

Báo cáo tiến độ tuần sẽ gửi riêng vào đầu mỗi tuần. Trong quá trình triển khai, nếu có vướng mắc, thay đổi scope hoặc cần điều chỉnh deadline, DISO sẽ chủ động cập nhật và trao đổi với các bên liên quan kịp thời.

Cảm ơn team đã phối hợp.

Thanks & Regards,
**DISO Team**
