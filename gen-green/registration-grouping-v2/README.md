# Gen-Green Employee Registry & Import — V2 Documentation

> Tài liệu cho V2 (Employee Registry + Import Pipeline) — đã ship trên branch `hotfix/group-users` của project `accesstrade-projects/vcreator/`.

---

## 📚 Đọc theo thứ tự nào?

| Vai trò | Đọc file nào trước |
|---------|---------------------|
| **HR Vin / PM / QA / non-tech** | [overview-v2-import-logic.md](overview-v2-import-logic.md) — flowchart + ví dụ thực tế + FAQ |
| **Dev / Tech Lead / Architect** | [prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md) — full spec đã ship |
| **Test V2 trên môi trường dev** | Section [Test Workflow](#-test-workflow-2-bước) bên dưới |
| **Hiểu V2 build trên V1 thế nào** | [prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md) → [overview.md](overview.md) → đến V2 |

---

## 📁 Files trong thư mục này

### 📖 Documentation

| File | Mục đích | Audience |
|------|---------|----------|
| **[overview-v2-import-logic.md](overview-v2-import-logic.md)** | Giải thích logic import dễ hiểu — 8 action types, flowchart match, 2 chế độ rà soát, workflow đầy đủ, FAQ | HR, PM, QA |
| **[prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md)** | PRD v2.3 sau khi đã ship — 17 FRs + 5 NFRs + 8 endpoints + known limitations | Dev, Tech Lead |
| **[overview.md](overview.md)** | Bối cảnh business V1+V2 tổng (legacy, dùng tham khảo context) | All |
| **[prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md)** | PRD V1 — popup cập nhật profile + workplace cascading + admin verify manual | Dev (V1 prerequisite) |

### 📊 Excel Files

| File | Dùng để làm gì |
|------|----------------|
| **[VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx)** | Template HR Vin cung cấp — chứa header + dropdown đơn vị (cột J). HR copy template này, điền data từ dòng 5 trở đi. |
| **[sample-import-step1-initial.xlsx](sample-import-step1-initial.xlsx)** | File test bước 1 — baseline. 7 rows: 2 user Match A + 5 nhân viên mới. Upload với toggle "Rà soát nghỉ việc" **TẮT** rồi Apply. |
| **[sample-import-step2-mixed.xlsx](sample-import-step2-mixed.xlsx)** | File test bước 2 — cover full 8 actions. Upload sau khi Apply file 1, **BẬT** toggle "Rà soát nghỉ việc". Preview sẽ thấy đầy đủ counters auto_verified/cancelled/transferred/missing/etc. |

---

## 🧪 Test Workflow 2 bước

Để demo đầy đủ 8 action types trên dev/staging:

### Bước 1 — Tạo registry baseline
1. Mở admin → trang `Danh sách nhân viên` (`/employee-registry`)
2. Click `Import Excel` → upload [sample-import-step1-initial.xlsx](sample-import-step1-initial.xlsx)
3. Toggle `Rà soát nhân viên nghỉ việc`: **TẮT** (file delta mode)
4. Modal đóng → redirect preview page
5. Counters expected: `auto_verified=2, new_record=5, total=7`
6. Click `Apply` → confirm modal → registry insert 7 records, 2 user verified

### Bước 2 — Mixed scenarios cover full 8 actions
1. Quay lại trang `Danh sách nhân viên`
2. Click `Import Excel` → upload [sample-import-step2-mixed.xlsx](sample-import-step2-mixed.xlsx)
3. Toggle `Rà soát nhân viên nghỉ việc`: **BẬT** (full-dump mode)
4. Modal đóng → preview page hiển thị counters expected:

| Counter | Expected | Action |
|---------|----------|--------|
| 🟡 Tự xác minh | 2 | User Match A khác chưa apply ở step 1 |
| 🔴 Xung đột | 2 | 1 phone match code khác + 1 code match phone khác |
| 🟠 Điều chuyển | 2 | BASE002 + user verified workplace khác file 1 |
| 🟠 Nghi ngờ nghỉ | 3 | BASE003/004/005 vắng so với step 1 |
| 🟢 Thêm mới | 4 | 3 NEW + 1 DUPCODE_X1 dòng đầu |
| ⚪ Không đổi | 2 | Match A user-cfa2cc6cd3 + BASE001 y hệt step 1 |
| ⚫ Lỗi format | 4 | 3 validation errors + 1 duplicate |
| **Tổng** | **19** | |

5. Tick checkbox `Xác nhận lên lịch nghỉ việc 3 nhân viên` (hoặc bỏ qua nếu muốn skip terminate)
6. Click `Apply` → modal confirm liệt kê chi tiết hành động
7. Apply → status=`completed`, redirect về `Danh sách nhân viên`

### Test thêm các tình huống

- **Cancel preview:** sau bước 2 thay vì Apply → click `Hủy` → confirm → status=`cancelled`. Vào lại preview vẫn xem được snapshot.
- **Block concurrent import:** khi đang có đợt preview chưa Apply, upload file khác → 409 Conflict, message yêu cầu Apply hoặc Hủy đợt cũ.
- **Rollback:** sau Apply file 2, vào preview → click `Rollback` → revert tất cả changes.
- **Grace period:** Apply với confirm terminate → user bị flag `pending_removal`, `staffRemovalScheduledAt = +7d`. Cron daily 00:00 sẽ tự gỡ staff tag sau 7 ngày.

---

## 🔗 Liên quan

- **Plans:** [`plans/`](../registration-grouping/plans/) (V1 folder — chứa kế hoạch đợt 1 + đợt 2+3)
- **Code repo:** `accesstrade-projects/vcreator/` branch `hotfix/group-users`
- **Commits chính:**
  - `3dbcf8c3` Phase A+B (Foundations + List API)
  - `9524a648` Phase C (Excel parser)
  - `c5b319a6` Phase D+E (Match engine + Dry-run preview)
  - `6c1f2260` Phase F (Apply + Rollback + UI)
  - `a974a495` Phase G (Cron + Register hook + Notification)
  - `29ef26d7` Phase H + Polish (Async + Cancel + UX cleanup + bug fixes)

---

## 📌 Sự khác nhau V1 vs V2

| Aspect | V1 ([prd-v1](prd-registration-v1-2026-04-12.md)) | V2 ([prd-v2](prd-registration-v2-2026-04-12.md)) |
|--------|------|------|
| Verify staff | Admin manual click duyệt từng người | Auto-match từ file HR + admin Apply batch |
| Source of truth | User tự khai mã NV (không validate) | Employee Registry HR-managed |
| Lifecycle | Chỉ verify/reject | + Transferred + Missing + Grace 7d + Rollback |
| Audit | Per-action audit log | + ImportHistory + ImportChange snapshot + actor_type |
| Workflow | 1-step (popup → admin duyệt) | 2-step (upload → preview → apply) |

V2 KHÔNG thay V1 — V2 build TRÊN V1. Popup, workplace cascading, admin verify thủ công vẫn còn dùng được. V2 chỉ thêm pipeline tự động khi HR có file Excel.
