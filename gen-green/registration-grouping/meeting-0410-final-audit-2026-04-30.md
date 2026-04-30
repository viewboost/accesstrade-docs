# Meeting 0410 — Final Audit (2026-04-30)

**Source:** [meeting-notes/0410.md](../meeting-notes/0410.md)
**Audit by:** Re-check sau loạt commits Tab Content + Tab Creator + Export

---

## Hạng mục 1: Tab Nội dung (`/content`)

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Filter cơ sở làm việc 3 layer cascading | 35-37 | ✅ Done |
| Cột "Phân loại creator" (CBNV / Không phải CBNV) | 37-39 | ✅ Done — column "Loại tài khoản" |
| Cột "Cơ sở làm việc" trên video | 47-51 | ✅ Done |
| Cột "Hashtag cá nhân" | 51-53 | ✅ Done |

**→ Hạng mục 1: ĐỦ.**

---

## Hạng mục 2: Tab Creator (`/user-partner`)

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Filter "Nơi làm việc" 3 layer cascading | 57 | ✅ Done |
| Filter Phân loại creator (CBNV / Không phải CBNV) | (implicit) | ✅ Done |
| Cột Tên | 63 | ✅ Done |
| Cột Hashtag cá nhân | 63 | ✅ Done |
| Cột Tổng view của creator | 63 | ✅ Done (FR-V3-009) |
| Cột Tổng tiền | 63 | ✅ Done (Tiền còn lại) |
| Cột Tổng tiền đã rút | 63 | ✅ Done (Đã rút thành công) |
| Cột Tổng số video creator đã nộp | 63 | ✅ Done (FR-V3-010) |
| Ẩn cột "Ngày tạo", giữ "Ngày tham gia" | 65-67 | ✅ Done |

**Iteration sau meeting (post-fix):**
- Bỏ cột "Phân loại" riêng, gộp vào cột "Cơ sở làm việc" cho gọn UX
- Layout fix: Tên + STT pin trái, Action pin phải, scroll ngang

**→ Hạng mục 2: ĐỦ HẾT 9 yêu cầu meeting.**

---

## Hạng mục 3: Export Column Picker

### 3.1 Tab Nội dung (`/content` export)

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Cho phép chọn cột lúc export | 79-93 (Speaker 4 propose) | ✅ Done |
| Default: tất cả check, admin tự bỏ tick (Speaker 4 proposal mới — **khác PRD V1 FR-029** spec gốc) | 83 | ✅ Done — match Speaker 4 propose |
| BE support 25 cột (đầy đủ) | 91 | ✅ Done — `contentColumns []` |
| Cột mới: Cơ sở làm việc, Hashtag, Phân loại | 47-53, 71 | ✅ Done — 3 cột mới có badge "MỚI" |

**→ Hạng mục 3.1: ĐỦ.**

### 3.2 Tab Creator (`/user-partner` export) ⚠️ CHƯA LÀM

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Cho phép chọn cột lúc export tab Creator | 71-73 (Speaker 3) | ❌ **Chưa** — column picker chỉ apply `type=CONTENT`, không apply `USER_PARTNER` |
| Bỏ cột "Đối tác VinWonder" trong export | 71-73 | ❌ Chưa verify export user-partner shape |
| Thêm cột Phân loại / Nơi làm việc / Hashtag vào export | (implicit) | ❌ Chưa |

**→ Hạng mục 3.2: THIẾU. Effort ~4h.**

---

## Hạng mục 4: Admin Analytics Dashboard ❌ Chưa làm

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Visualize số liệu (vd "bao nhiêu CBNV Phú Quốc tham gia chương trình ABC") không phải kéo Excel | 121-125 | ❌ Chưa |
| Màn hình thống kê nhiều bộ lọc (CBNV, cơ sở, sự kiện) | 127-145 | ❌ Chưa |
| Mockup giao diện tổng thể trước khi code | 167 (Speaker 1 cam kết) | ❌ Chưa có mockup |
| 3 mockups: form đăng ký, liên kết tài khoản, dashboard admin | 957-959 | ❌ Chưa |

**→ Hạng mục 4: HOÀN TOÀN CHƯA LÀM** — gap critical, cần PRD + designer mockup.

---

## Hạng mục 5: Form đăng ký + SSO

| Yêu cầu meeting | Source line | Status |
|---|---|---|
| Email + SĐT bắt buộc cho tất cả Green Creator | 933, 939 | ✅ Done (PRD V1 FR-005..007) |
| Toggle CBNV → conditional render workplace | 939 | ✅ Done |
| Đổi social login → form đăng ký truyền thống | 941-947 | ❌ Defer V2+ (PRD V1 §4.2 Out of Scope) |
| SSO 2 hệ thống Skelet ↔ Gen-Green | 231-239, 717 | ❌ Defer V2+ |

**→ Hạng mục 5: ĐỦ những gì PRD V1 commit. Còn lại defer.**

---

## Tổng kết audit

| # | Hạng mục | Status |
|---|---|---|
| 1 | Tab Nội dung filter + cột | ✅ 4/4 Done |
| 2 | Tab Creator filter + cột | ✅ 9/9 Done |
| 3.1 | Export Tab Nội dung column picker | ✅ Done |
| 3.2 | Export Tab Creator column picker | ❌ **Chưa** |
| 4 | Admin Analytics Dashboard | ❌ **Critical gap** |
| 5 | Form + SSO (V2+ defer) | ✅ Theo PRD V1 |

**Tổng:** 13/16 yêu cầu meeting đã làm. **Còn 3 items:**

1. **Export Tab Creator column picker** (~4h) — extend column picker cho `type=USER_PARTNER`
2. **Admin Analytics Dashboard nâng cấp** (~18h) — cần mockup + PRD spec mới
3. (5: defer V2+ — không tính trong scope hiện tại)

---

## Items priority

| Priority | Item | Effort |
|---|---|---|
| 🟠 Medium | Export `/user-partner` column picker + 3 cột mới (Phân loại / Nơi làm việc / Hashtag) | 4h |
| 🔴 High | Mockup + PRD Analytics Dashboard | 8h plan + 16h impl |
| 🟡 Defer | SSO Skelet ↔ Gen-Green | session riêng V4+ |
| 🟡 Defer | Form đăng ký truyền thống | session riêng V4+ |

---

## Đánh giá tổng

**Đã làm chuẩn theo meeting:**
- Tab Nội dung 100%
- Tab Creator 100% (9 yêu cầu chi tiết)
- Export Tab Nội dung 100%

**Chưa làm:**
- Export Tab Creator (FR-V3-013/014 trong PRD V3 vẫn pending)
- Analytics Dashboard cam kết Speaker 1 — quan trọng nhất, cần ưu tiên
