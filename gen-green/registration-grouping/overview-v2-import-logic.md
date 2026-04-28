# Overview V2 — Logic Import Nhân Viên

> **Mục đích:** Giải thích cho team kinh doanh, HR, vận hành **mỗi dòng trong file Excel sẽ được hệ thống xử lý thế nào**. Đọc xong document này, người không phải developer hiểu được:
> - Khi nào nhân viên được **tự động duyệt** thành staff?
> - Khi nào bị đánh dấu **nghi ngờ nghỉ việc**?
> - Khi nào bị **xung đột** (cancelled mismatch)?
> - Logic preview + apply hoạt động ra sao?

**Date:** 2026-04-25 | **Project:** Gen-Green | **Branch:** `hotfix/group-users`

---

## 1. 2 nguồn dữ liệu hệ thống đang giữ

Khi xử lý file Excel của HR, hệ thống đối chiếu với 2 bảng dữ liệu hiện tại:

### A. Bảng nhân viên Gen-Green (creator app)
- Người dùng tự đăng ký qua app Gen-Green
- Đã hoặc chưa khai mã nhân viên (qua popup "Cập nhật thông tin")
- Có 4 trạng thái xác minh: `pending` (chờ duyệt), `verified` (đã duyệt), `rejected` (từ chối), `pending_removal` (đợi gỡ staff sau 7 ngày)

### B. Bảng danh sách nhân viên chính thức (Employee Registry)
- Dữ liệu **HR cung cấp** qua các đợt import Excel trước
- Đây là "nguồn sự thật" về ai là nhân viên thật
- Mỗi record có: mã NV, họ tên, SĐT, đơn vị, trạng thái

**Khi import file mới**, hệ thống đối chiếu **mỗi dòng file** với cả 2 bảng A + B → quyết định **action** cho dòng đó.

---

## 2. Flowchart logic match (đơn giản hoá)

```
                    ┌─────────────────────┐
                    │  1 dòng từ file Excel │
                    │  (mã NV + SĐT + ...)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Validate format       │
                    │ (STT 5 số, SĐT 10 số,│
                    │  required fields...)  │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                          │
              ❌ Sai format              ✅ Đúng format
                  │                          │
        ┌─────────▼─────────┐                │
        │ Action: invalid    │                │
        │ Badge: "Lỗi format"│                │
        │ → Skip khi apply   │                │
        └────────────────────┘                │
                                              │
                          ┌───────────────────▼────────────────────┐
                          │ Tra cứu Registry (B) theo mã NV         │
                          │ Tra cứu User Gen-Green (A) theo SĐT     │
                          └───────────────────┬────────────────────┘
                                              │
              ┌──────────────────┬─────────────┴───────────────┬────────────────┐
              │                  │                              │                │
           Reg ❌                Reg ❌                        Reg ✅             Reg ✅
           User ❌               User ✅                       User ❌            User ✅
              │                  │                              │                │
              ▼                  ▼                              ▼                ▼
        ┌──────────┐    ┌──────────────────┐         ┌──────────────┐   ┌──────────────────┐
        │new_record│    │ Mã NV + SĐT khớp │         │  unchanged    │  │ Compare workplace│
        │          │    │ user → ?         │         │  (registry y  │  │  + match details │
        │ "Thêm    │    │                  │         │   hệt)        │  │                  │
        │  mới     │    │ ✅ Khớp →         │         └──────────────┘  │ Workplace giống? │
        │  registry│    │  auto_verified   │                            │ ✅ → unchanged    │
        │  HR"     │    │                  │                            │ ❌ → transferred │
        │          │    │ ❌ Lệch →         │                            └──────────────────┘
        │          │    │  cancelled_mismatch│
        └──────────┘    └──────────────────┘
                                    
              ┌──────────────────────────────────────────────────────────┐
              │ Detect riêng (chỉ khi admin BẬT toggle "Rà soát nghỉ việc"):│
              │                                                            │
              │ Registry (B) có mã NV X, file KHÔNG có →                  │
              │   action: missing_from_file ("Nghi ngờ nghỉ việc")         │
              └──────────────────────────────────────────────────────────┘
```

---

## 3. 8 Action types — định nghĩa cho người dùng cuối

### 🟡 `auto_verified` — "Tự động xác minh"
**Khi nào:**
- Hệ thống thấy: 1 user Gen-Green đã khai mã NV qua popup, và file HR vừa import có **đúng mã NV + đúng SĐT** đó
- Tức HR confirm "đúng người" → tự động duyệt cho user lên `verified`

**Apply làm gì:**
- Đổi `staffStatus` của user: `pending` → `verified`
- Lưu thời điểm verify (`staffVerifiedAt`)
- Notify user: "Mã nhân viên của bạn đã được xác minh tự động ✓"

**Ví dụ thực:**
> User A đăng ký Gen-Green, khai mã NV `EMP001` + SĐT `0901234567`, status = pending.
> HR import file có dòng [`EMP001`, `0901234567`, `Nguyễn A`, `Vinpearl Nha Trang`].
> → Apply → User A tự động lên `verified` + được unlock chiến dịch nội bộ.

---

### 🔴 `cancelled_mismatch` — "Xung đột mã NV/SĐT"
**Khi nào:**
- File HR có 1 dòng mà:
  - **Trường hợp 1:** SĐT trùng với 1 user Gen-Green nhưng mã NV file ≠ mã NV user đã khai
  - **Trường hợp 2:** Mã NV trùng nhưng SĐT khác
- Có khả năng user đã khai sai/mạo danh

**Apply làm gì:**
- Đổi `staffStatus` user về `rejected`
- Clear `employeeCode`, workplace fields của user
- Notify user: "Thông tin không khớp dữ liệu HR. Vui lòng cập nhật lại mã NV/SĐT"

**Ví dụ thực:**
> User B khai mã `EMP002` + SĐT `0902111111`. HR import file có dòng [`EMP002`, `0903999999`, `Trần B`, ...] — code trùng nhưng SĐT khác.
> → Apply → User B bị reject, clear staff fields. Phải khai lại để verify.

---

### 🟠 `transferred` — "Điều chuyển đơn vị"
**Khi nào:**
- Mã NV đã có trong registry HR từ trước (tức user đã verified rồi)
- File HR mới có **đúng mã NV + đúng SĐT** đó nhưng **đơn vị khác** với data registry hiện có

**Apply làm gì:**
- Update `workplaceName` trong registry + của user
- Notify user: "Nơi làm việc đã cập nhật: [tên đơn vị mới]"
- KHÔNG reset trạng thái verified

**Ví dụ thực:**
> Tháng 3 HR import: `EMP003`, `Vinpearl Nha Trang`. User C verified.
> Tháng 4 HR import lại: `EMP003`, `Vinpearl Phú Quốc`. → Transferred → workplace của user C update sang Phú Quốc.

---

### 🟠 `missing_from_file` — "Nghi ngờ nghỉ việc"
**Khi nào:**
- Mã NV X có trong registry HR (active)
- File import KHÔNG chứa mã NV X
- **Quan trọng:** Chỉ phát sinh khi admin **BẬT toggle "Rà soát nhân viên nghỉ việc"** lúc upload

**Lý do cần toggle:** Nếu HR gửi file delta (chỉ vài nhân viên thay đổi), hệ thống không nên tự cho rằng tất cả nhân viên không có trong file = nghỉ việc.

**Apply làm gì:**
- **Yêu cầu admin tick checkbox xác nhận** thêm 1 lần nữa trong preview page (an toàn 2 lớp)
- Nếu admin tick: set `staffRemovalScheduledAt = now + 7 ngày` cho user
- Notify user: "Tài khoản sẽ chuyển về Creator từ ngày [X]"
- Sau 7 ngày, cron daily 00:00 tự động gỡ staff tag
- Nếu admin **không tick** lúc apply → bỏ qua, không xử lý dòng này

**Ví dụ thực:**
> Tháng 3: `EMP004` có trong registry (đang là verified staff).
> Tháng 4: HR upload file đầy đủ tháng, BẬT "Rà soát nghỉ việc". File không có `EMP004` (HR đã loại khỏi danh sách lương).
> → Preview show "Nghi ngờ nghỉ việc: 1". Admin tick checkbox → Apply →
> User EMP004 nhận thông báo "sẽ chuyển Creator từ 2026-05-01" → 7 ngày sau cron tự gỡ.

---

### 🟢 `new_record` — "Thêm mới registry"
**Khi nào:**
- Mã NV chưa có trong registry HR
- KHÔNG có user Gen-Green nào với SĐT/mã NV này (hoặc có nhưng cả 2 thông tin đều không trùng)

**Apply làm gì:**
- Insert record mới vào employee_registry
- KHÔNG touch user nào (vì chưa có)

**Ví dụ thực:**
> HR thêm nhân viên mới `EMP005`. Chưa có ai dùng mã này trên Gen-Green.
> → Apply → Registry có thêm record `EMP005`. Sau này khi nhân viên tạo tài khoản Gen-Green và khai `EMP005` → match A → auto_verified.

---

### ⚪ `no_match` — "Không khớp registry"
**Khi nào:**
- Mã NV chưa có trong registry HR
- Có user Gen-Green với mã + phone khác tình huống match khác

**Hiếm gặp** — chỉ ở edge case. Thường dòng sẽ rơi vào `new_record` hoặc `cancelled_mismatch`.

**Apply làm gì:** Insert registry mới (giống new_record).

---

### ⚪ `unchanged` — "Không thay đổi"
**Khi nào:**
- Mã NV đã có trong registry HR
- File HR import lại với data y hệt (workplace, SĐT, họ tên đều giống)

**Apply làm gì:** No-op. Chỉ là "đã thấy nhân viên này lần nữa, mọi thứ bình thường".

**Ví dụ thực:**
> HR import file tháng 4 y hệt tháng 3 cho nhân viên EMP006.
> → unchanged → Apply không làm gì. Registry giữ nguyên.

---

### 🔵 `registry_updated` — "Cập nhật hồ sơ"
**Khi nào:**
- Mã NV đã có trong registry HR (`hasReg=true`)
- **Chưa có user Gen-Green nào claim mã này** (`hasUser=false`)
- File mới có **phone hoặc workplace** khác registry hiện tại

**Phân biệt với `transferred`:** transferred chỉ apply khi đã có user (cập nhật `user.workplaceUnitName`). registry_updated chỉ update registry data, không động user (vì chưa user nào claim).

**Apply làm gì:** Update registry record (`phone`, `workplaceName`) theo file mới. Source of truth = HR.

**Ví dụ thực:**
> HR import lần 1: BAS có phone `0706006004`. Chưa user nào đăng ký với BAS.
> HR phát hiện sai, sửa file: BAS có phone `0706006008` rồi import lại.
> → registry_updated → Apply update registry `{BAS, phone: 0706006008}`.

**Tại sao cần action này:**
Trước fix, case `hasReg && !hasUser` luôn flag `unchanged` ngay cả khi HR sửa data. Hậu quả: registry giữ data cũ sai. Khi user đăng ký mã đó, match logic dùng data sai → auto-verify nhầm hoặc reject nhầm.

---

### ⚫ `invalid` — "Lỗi format"
**Khi nào:** Dòng không pass validation cơ bản:
- STT không phải 5 chữ số
- SĐT không phải 10 chữ số / chứa ký tự lạ / trống
- Họ tên trống
- Mã nhân viên trống
- Đơn vị trống
- Mã nhân viên trùng dòng khác trong cùng file (DUPLICATE_EMPLOYEE_CODE)

**Apply làm gì:** Skip. Admin sửa file rồi upload lại đợt mới.

---

## 4. 2 chế độ rà soát — Toggle "Rà soát nghỉ việc"

Trên modal upload file, admin chọn 1 trong 2 mode:

### Mode A: ❌ Tắt toggle (default) — "Delta mode"
- **Dùng khi:** HR gửi file chỉ chứa 1 phần nhân viên (vd: nhân viên mới tháng này, chuyển đơn vị, có thay đổi)
- **Hành vi:** Hệ thống chỉ xử lý dòng có trong file. Registry hiện có **không bị flag** missing.

### Mode B: ✅ Bật toggle — "Full-dump mode"
- **Dùng khi:** HR gửi file đầy đủ toàn bộ DS nhân viên trong tháng
- **Hành vi:** Hệ thống so file vs registry → flag tất cả mã NV trong registry mà file không có là `missing_from_file`
- **Lý do bắt buộc admin chủ động bật:** tránh false positive khi nhầm chế độ

---

## 5. Workflow đầy đủ từ upload đến apply

```
[HR gửi file Excel cho Admin]
            │
            ▼
[Admin upload qua trang Danh sách nhân viên / Lịch sử import]
            │
            ▼
   ┌────────────────────┐
   │ Tick Toggle:        │
   │  ☐ Rà soát nghỉ việc│
   └────────┬───────────┘
            │
            ▼
[Hệ thống parse Excel] ─→ Lỗi format? ─Yes→ Vẫn redirect preview, action=invalid
            │
            │ No
            ▼
[Match Engine chạy:
 - Bulk query registry theo mã NV
 - Bulk query user theo SĐT (3 phone variants)
 - Build action cho từng dòng]
            │
            │ + nếu toggle "Rà soát nghỉ việc" BẬT
            ▼
[Thêm action missing_from_file
 cho registry không có trong file]
            │
            ▼
[Save tất cả records vào import_changes
 với phase: preview]
            │
            ▼
[Redirect Admin sang trang Preview]
            │
            ▼
   ┌────────────────────────────────────┐
   │ Preview page hiển thị:               │
   │  - Counter pills 9 actions          │
   │  - Filter dropdown action / đơn vị   │
   │  - Table 9 cột với badge action      │
   │  - Top bar: Hủy / Apply              │
   │  - Footer: Checkbox "Xác nhận nghỉ việc N nhân viên"
   │    (chỉ hiện khi missing > 0)        │
   └────────┬───────────────────────────┘
            │
       ┌────┴────┐
       │          │
   [Hủy]     [Apply]
       │          │
       ▼          ▼
   [Status =     [Modal confirm cuối]
    cancelled]         │
   [import_changes     ▼
    phase = cancelled]
                  ┌────┴────┐
                  │          │
              Skip missing  Tick missing
                  │          │
                  ▼          ▼
   [Apply tất cả action TRỪ missing_from_file]
                            ▼
   [hoặc Apply TẤT CẢ kể cả schedule terminate +7d]
                  │
                  ▼
   [Status = completed]
   [import_changes phase = applied]
   [Redirect về Danh sách nhân viên]
   [Notification gửi cho từng user theo action]
```

---

## 6. Bảo vệ chống nhầm lẫn

### Block đợt import mới khi đợt cũ chưa kết thúc
- Khi `import_history.status = preview` hoặc `processing`: **không thể upload đợt mới**
- Phải Apply hoặc Hủy đợt cũ trước → tránh chồng chéo data, race condition

### Bắt buộc 2 lớp xác nhận cho terminate
- Lớp 1: Bật toggle "Rà soát nghỉ việc" lúc upload (chủ động)
- Lớp 2: Tick checkbox "Xác nhận lên lịch nghỉ việc N nhân viên" trong preview (xác nhận)
- Nếu skip lớp 2 → Apply phần còn lại, KHÔNG terminate ai

### Grace period 7 ngày trước khi gỡ staff tag
- Khi confirm terminate → set `staffRemovalScheduledAt = now + 7 ngày`
- Cron daily 00:00 mới scan + gỡ
- User được notify ngay lúc apply, có 7 ngày để khiếu nại nếu HR nhầm

### Snapshot mode sau khi apply
- Sau Apply hoặc Cancel, vào lại preview page vẫn xem được toàn bộ records (snapshot lịch sử)
- Footer hiển thị badge status thay vì button Apply
- Có thể Rollback (revert tất cả changes) nếu cần

---

## 7. Phone normalization — kỹ thuật ngầm

User trong DB có thể lưu SĐT 3 dạng:
- `0977963755` (10 số leading 0)
- `977963755` (9 số)
- `+84977963755` (full quốc tế)

Hệ thống **tự động chuyển về 1 dạng `0xxxxxxxxx`** trước khi so sánh:
- Match Engine query với cả 3 variants để bao quát mọi format
- Parser strip whitespace, dash, plus, prefix `+84`/`84`

→ HR/Admin không cần lo SĐT format khác nhau giữa file và DB.

---

## 8. Câu hỏi thường gặp

**Q: Tại sao file đối tác mặc định không có data row?**
A: File mẫu chỉ chứa template (header + dòng VD + dropdown đơn vị ở cột J). HR cần copy template và **điền data từ dòng 5 trở đi** (cột B-F). Hệ thống tự skip header + VD row.

**Q: Mã nhân viên có format gì không?**
A: Hệ thống chấp nhận **mọi format** (số, chữ, dash, dấu gạch). Ví dụ `0011111`, `EMP00001`, `EMP-WITH-DASH` đều valid.

**Q: SĐT trong file có cần format chuẩn không?**
A: Không. Hệ thống tự normalize. Có thể nhập `0912345678`, `+84912345678`, `84912345678`, hoặc `0912 345 678` đều OK.

**Q: Nếu HR gửi file delta nhưng quên tắt "Rà soát nghỉ việc"?**
A: Hệ thống flag tất cả nhân viên còn lại là `missing_from_file`. Admin có 2 lựa chọn:
- **Hủy preview** + upload lại với toggle tắt
- **Apply không tick checkbox** confirm terminate → flag bị bỏ qua, vẫn apply phần khác

**Q: Vài record bị lỗi format, có chặn cả file không?**
A: Không. File vẫn được parse, dòng lỗi đánh dấu `invalid` + bỏ qua khi apply. Dòng hợp lệ vẫn xử lý bình thường.

**Q: Sau khi apply, có thể quay lại xem ai được verify, ai bị reject không?**
A: Có. Vào "Lịch sử import" → click vào import → preview page hiện snapshot đầy đủ với tất cả action. Có thể filter, search, export.

**Q: Lỡ apply nhầm thì sao?**
A: Trong preview page có nút "Rollback" — revert tất cả changes của đợt import đó. **Cảnh báo:** nếu user đã thay đổi profile sau apply, rollback có thể overwrite những thay đổi đó.

---

## 9. Liên quan

- [PRD V1](prd-registration-v1-2026-04-12.md) — registration flow + popup profile
- [PRD V2](prd-registration-v2-2026-04-12.md) — full spec V2 chi tiết kỹ thuật
- [Overview V1](overview.md) — bối cảnh business + scope tổng
- File Excel template HR: [VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx)
- File test 2 bước (cover full 9 actions):
  - [sample-import-step1-initial.xlsx](sample-import-step1-initial.xlsx) — baseline (apply lần đầu)
  - [sample-import-step2-mixed.xlsx](sample-import-step2-mixed.xlsx) — mixed scenarios (apply sau step 1)
