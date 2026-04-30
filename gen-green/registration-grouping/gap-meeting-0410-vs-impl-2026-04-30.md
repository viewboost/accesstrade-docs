# Gap: Meeting 0410 vs Implementation hiện tại

**Date:** 2026-04-30
**Source:** [meeting-notes/0410.md](../meeting-notes/0410.md)
**Mục đích:** Đối chiếu yêu cầu HR/operation team trong meeting với code thực tế. Liệt kê chỗ làm sai/thiếu.

---

## Bối cảnh meeting

3 hạng mục cần update:

1. **Tab Nội dung (admin)** — filter + cột mới
2. **Tab Creator (admin)** — filter + cột mới
3. **Export data** — column picker
4. **Màn hình thống kê (analytics)** — nhiều bộ lọc hơn (Speaker 2 đề cập)

---

## Hạng mục 1: Tab Nội dung (`/content` admin)

### Yêu cầu meeting

| Yêu cầu | Nguồn |
|---|---|
| Filter cơ sở làm việc của CBNV (3 layer cascading) | Speaker 3, line 35-37 |
| Cột "Phân loại" — CBNV / Không phải CBNV | Speaker 3, line 37-39 |
| Cột "Cơ sở làm việc" trên video — vd "VinWonder Phú Quốc" | Speaker 3, line 47-51 |
| Cột "Hashtag cá nhân" — đỡ phải mapping từ tab Creator | Speaker 3, line 51-53 |

### Implementation hiện tại

- ✅ Filter 3 layer cascading: `/content/components/filter.tsx` có WorkplaceFilter
- ✅ Cột Phân loại: `/content/components/table.tsx` có "Loại tài khoản" tag CBNV/Không phải CBNV
- ✅ Cột Cơ sở làm việc: render `Brand - Company - Unit`
- ✅ Cột Hashtag: render `createdBy.hashtag`

**→ Hạng mục 1: ĐỦ.**

---

## Hạng mục 2: Tab Creator (`/user-partner` admin)

### Yêu cầu meeting

| Yêu cầu | Nguồn |
|---|---|
| Filter "Nơi làm việc" cascading 3 layer | Speaker 3, line 57 |
| Filter Phân loại CBNV / Không phải CBNV | (implicit từ context) |
| Cột Tên creator | Speaker 3, line 63 |
| Cột Hashtag cá nhân | Speaker 3, line 63 |
| Cột Tổng view | Speaker 3, line 63 |
| Cột **Tổng tiền** | Speaker 3, line 63 — meeting yêu cầu |
| Cột **Tổng tiền đã rút** | Speaker 3, line 63 |
| Cột **Tổng số video creator đã nộp** | Speaker 3, line 63 |
| Ẩn cột "Ngày tạo", giữ "Ngày tham gia" | Speaker 3, line 65-67 |

### Implementation hiện tại (sau commit `0cbf1b2c`)

- ✅ Filter 3 layer + Phân loại: vừa làm
- ✅ Cột Tên + Hashtag + Cơ sở: có
- ⚠️ **Cột Tổng view: KHÔNG CÓ** — meeting yêu cầu, chưa add
- ✅ Cột Cash remaining + Cash withdraw success: có (gần với "tổng tiền" + "tổng tiền đã rút")
- ⚠️ **Cột Tổng số video đã nộp/tham gia: KHÔNG CÓ**
- ✅ Ẩn createdAt, giữ joinedAt

**→ Hạng mục 2: THIẾU 2 cột (Tổng view, Tổng video) so với meeting.**

---

## Hạng mục 3: Export Column Picker

### Yêu cầu meeting

| Yêu cầu | Nguồn |
|---|---|
| Tab Nội dung — bỏ tick mặc định: ID video, Thumbnail, Đối tác/Mã sự kiện, Tích cực/Trung lập/Tiêu cực | Speaker 3, line 41-47 |
| Tab Nội dung — tick sẵn cột mới: Cơ sở làm việc, Hashtag cá nhân | Speaker 3, line 47-53 |
| Tab Creator — bỏ tick: Đối tác VinWonder | Speaker 3, line 71-73 |
| Tab Creator — tick sẵn: Nơi làm việc, Hashtag cá nhân, Phân loại | (implicit) |
| Anh Tĩnh đề xuất: cho phép chọn cột lúc export, thay vì xóa cột vĩnh viễn | Speaker 4, line 79-93 |

### Implementation hiện tại (sau commit `3591dece`)

- ✅ Tab Nội dung: column picker dialog có sẵn 25 checkbox
- ✅ Cột mới Phân loại / Cơ sở / Hashtag có badge "MỚI"
- ⚠️ **Default preset SAI:** user yêu cầu bỏ tick mặc định (theo PRD FR-029) — tôi implement "tất cả checked" theo user override sau đó. **Match user override gần đây**, nhưng KHÔNG match meeting gốc. Cần confirm lại.
- ❌ **Tab Creator export: KHÔNG CÓ column picker** — meeting yêu cầu cả 2 tab. Tôi chỉ làm /content theo user clarify hôm nay.
- ❌ **Tab Creator các cột mới (Nơi làm việc, Hashtag, Phân loại) trong export: chưa add**

**→ Hạng mục 3: ĐỦ /content, THIẾU /user-partner export.**

---

## Hạng mục 4: Màn hình thống kê (analytics)

### Yêu cầu meeting

| Yêu cầu | Nguồn |
|---|---|
| Speaker 2 muốn xem nhanh số liệu (vd "bao nhiêu CBNV Phú Quốc tham gia chương trình ABC") **không phải kéo data Excel** | Speaker 2, line 121-125 |
| Speaker 1 (Vĩnh) thừa nhận: bảng thống kê hiện tại chưa hoàn thiện, sẽ sửa nhiều cho admin tiện dụng + nhiều bộ lọc | Speaker 1, line 127-145 |
| Speaker 2 yêu cầu Vĩnh **compile lại requirement** + **tạo mockup giao diện tổng thể** trước khi làm | Speaker 2, line 151-167 |
| Speaker 1 cam kết: "trước khi làm sẽ tổng hợp lại + lên mockup" | Speaker 1, line 167 |
| 3 mockups cần làm: form đăng ký nhân viên, luồng liên kết tài khoản, dashboard admin | Speaker 4, line 957-959 |

### Implementation hiện tại

- ❌ **Mockup dashboard admin: KHÔNG CÓ** trong codebase / docs
- ❌ **Màn hình analytics nâng cấp với nhiều filter (CBNV, cơ sở...): CHƯA LÀM**
- ⚠️ Trang admin có sẵn `event-analytic-daily` etc. nhưng chưa filter theo workplace/CBNV

**→ Hạng mục 4: HOÀN TOÀN CHƯA LÀM** — đây là **gap lớn nhất** so với meeting.

---

## Hạng mục 5 (bonus): Form đăng ký + Liên kết tài khoản

### Yêu cầu meeting

| Yêu cầu | Nguồn |
|---|---|
| Email + SĐT bắt buộc cho **tất cả** Green Creator (kể cả không phải CBNV) | Speaker 4, line 933 |
| Toggle "Có phải CBNV?" → Chỉ khi tick CÓ thì mới hiện workplace 3-tier | Speaker 2, line 939 |
| Đổi từ social login fast-track → quay về form đăng ký truyền thống | Speaker 4, line 941-947 |
| Liên kết account 2 hệ thống (Skelet ↔ Gen-Green) thành 1 SSO | Speaker 1, line 231-239 |

### Implementation hiện tại

- ✅ Email + SĐT required với verify OTP (FR-005, FR-006, FR-007)
- ✅ Toggle CBNV conditional render workplace
- ⚠️ **Vẫn dùng social login OAuth Google** — meeting yêu cầu đổi sang form truyền thống. NHƯNG đây là **defer V2+** trong PRD V1 §4.2 Out of Scope: "Form đăng ký truyền thống (thay đổi auth flow)"
- ❌ **SSO 2 hệ thống Skelet/Gen-Green: CHƯA LÀM** — defer

**→ Hạng mục 5: ĐỦ những gì PRD V1 commit. Còn lại defer V2+.**

---

## Tổng kết

| # | Hạng mục meeting | Status |
|---|---|---|
| 1 | Tab Nội dung filter + cột | ✅ Done |
| 2 | Tab Creator filter + cột | ⚠️ Thiếu 2 cột (Tổng view, Tổng video) |
| 3 | Export column picker | ⚠️ Done /content, thiếu /user-partner |
| 4 | **Mockup + Analytics dashboard nâng cấp** | ❌ **Hoàn toàn chưa làm** |
| 5 | Form + SSO | ✅ Theo PRD V1 (V2+ defer) |

---

## Critical gap

**#4 — Analytics dashboard nâng cấp** là cam kết Speaker 1 (Vĩnh) trong meeting:
- "Mình sửa nhiều để mình đưa cái màn hình thống kê nó ra một cái màn hình tiện dụng hơn. Nhiều bộ lọc."
- "Trước khi làm thì mình sẽ tổng hợp lại rồi mình lên một cái mockup."

Nhưng:
- ❌ Chưa có mockup
- ❌ Chưa có code
- ❌ PRD V1 không có epic riêng cho hạng mục này (chỉ có EPIC-005, 006, 007 cho list/export, không nâng cấp analytics dashboard)

→ **Recommend:** Tạo PRD/spec riêng cho "Admin Analytics Dashboard Upgrade" + thiết kế mockup, sau đó implement. Effort lớn (~16h+).

---

## Items priority cập nhật

| Pri | Item | Effort |
|---|---|---|
| 🔴 High | **Mockup + spec Analytics Dashboard upgrade** (Hạng mục 4) | 8h plan + 16h impl |
| 🟠 Medium | Bổ sung 2 cột `/user-partner` table: Tổng view, Tổng video | 2h |
| 🟠 Medium | Mở rộng column picker cho `/user-partner` export | 4h |
| 🟡 Low | Defer V2+ items (SSO Skelet/Gen-Green, form đăng ký truyền thống) | session riêng |
