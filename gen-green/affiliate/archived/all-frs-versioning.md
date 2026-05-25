# All Functional Requirements — Gen-Green Affiliate

**Date:** 2026-05-12
**Author:** vinhnguyen
**Mục đích:** Tổng hợp toàn bộ FR từ 3 PRD để chia v1/v2 dễ quản lý.

**Source PRDs:**
1. [prd-admin-setup-2026-05-04.md](prd-admin-setup-2026-05-04.md) — Admin Setup (5 FRs)
2. [prd-account-linking-2026-05-04.md](prd-account-linking-2026-05-04.md) — Account Linking (18 FRs)
3. [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md) — FE Creator (12 FRs)
4. [prd-fe-creator-2026-05-04.v2-trimmed.md](prd-fe-creator-2026-05-04.v2-trimmed.md) — FE Creator trimmed (10 FRs, bỏ FR-006/007)

**Tổng:** 35 FRs (hoặc 33 nếu dùng FE Creator trimmed)

---

## Cách dùng

Mỗi FR có 4 cột để bạn tick:
- **Track**: thuộc PRD nào
- **Priority gốc**: Must / Should / Could (theo PRD hiện tại)
- **V1?**: [ ] tick nếu vào V1
- **V2?**: [ ] tick nếu vào V2
- **Bỏ?**: [ ] tick nếu bỏ luôn

Suggest v1/v2 cuối mỗi bảng (mình đề xuất sẵn dựa trên priority gốc + critical path).

---

## Track 1: Admin Setup (5 FRs)

> PRD độc lập với Scalef API — start sớm nhất được.

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-001 | Admin tạo Affiliate Campaign | Must | ☐ | ☐ | ☐ |
| FR-002 | Admin quản lý danh sách (list, search, filter) | Must | ☐ | ☐ | ☐ |
| FR-003 | Liên kết Affiliate Campaign ↔ Event (mapping many-to-many) | Must | ☐ | ☐ | ☐ |
| FR-004 | Backend CRUD APIs + mapping endpoints | Must | ☐ | ☐ | ☐ |
| FR-005 | Search & Autocomplete Event khi liên kết | Must | ☐ | ☐ | ☐ |

**Suggest:** Toàn bộ 5 FR vào V1 (đều Must Have, không có gì để defer).

---

## Track 2: Account Linking (18 FRs)

> Phase 1 — prerequisite cho FE Creator. Không link = không gọi được Scalef.

### EPIC-001: OAuth SSO + Matching

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-001 | Entry point liên kết (Settings, login, Event detail banner...) | Must | ☐ | ☐ | ☐ |
| FR-002 | Đăng nhập Scalef (OAuth2 Authorization Code Flow) | Must | ☐ | ☐ | ☐ |
| FR-003 | Consent — đồng ý chia sẻ thông tin (CCCD/SĐT/Email) | Must | ☐ | ☐ | ☐ |
| FR-004 | Check 1-đối-1 (1 GG user ↔ 1 Scalef user) | Must | ☐ | ☐ | ☐ |
| FR-005 | Matching CCCD (identity check, khác CCCD → reject) | Must | ☐ | ☐ | ☐ |
| FR-018 | Data normalization (chuẩn hóa CCCD/SĐT/Email trước compare) | Must | ☐ | ☐ | ☐ |

### EPIC-002: Conflict Resolution

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-006 | So khớp thông tin (bảng compare Khớp/Lệch/Bổ sung) | Must | ☐ | ☐ | ☐ |
| FR-007 | UI lựa chọn thông tin khi conflict (chọn giữ bên nào) | Must | ☐ | ☐ | ☐ |
| FR-008 | OTP xác thực khi update SĐT/Email | Must | ☐ | ☐ | ☐ |
| FR-009 | Check unique trước commit (SĐT/Email chưa thuộc user khác) | Must | ☐ | ☐ | ☐ |
| FR-010 | Bidirectional update + Saga rollback | Must | ☐ | ☐ | ☐ |
| FR-017 | Phân loại field theo risk level (low: SĐT/Email; high: CCCD/Tên/MST) | Must | ☐ | ☐ | ☐ |

### EPIC-003: Hoàn tất, Reject & State Management

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-011 | Liên kết thành công — confirmation + unlock Phase 2 | Must | ☐ | ☐ | ☐ |
| FR-012 | Reject screen + auto-tạo support ticket | Must | ☐ | ☐ | ☐ |
| FR-013 | Pending state resumable (refresh browser không mất tiến độ) | Should | ☐ | ☐ | ☐ |
| FR-014 | Audit log `scalef_link_history` (compliance + dispute) | Should | ☐ | ☐ | ☐ |

### EPIC-004: Legacy Migration

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-015 | Entry point từ phía Scalef (Reverse linking — Scalef → GG) | Should | ☐ | ☐ | ☐ |
| FR-016 | Batch migration admin (CSV upload 1K publisher legacy) | Could | ☐ | ☐ | ☐ |

**Suggest:**
- **V1:** FR-001 → FR-012, FR-017, FR-018 (14 Must Have)
- **V2:** FR-013 (resume), FR-014 (audit), FR-015 (reverse linking)
- **Defer / Could Have:** FR-016 (chỉ làm khi sắp deadline Scalef chặn đăng ký mới)

---

## Track 3: FE Creator (12 FRs gốc — hoặc 10 nếu trimmed)

> Phase 2 — UI cho creator dùng affiliate. Depend Account Linking V1 done.

### EPIC-001: Affiliate Discovery

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-001 | Section affiliate trong Event detail | Must | ☐ | ☐ | ☐ |
| FR-002 | Affiliate Item Card (UI card trong section) | Must | ☐ | ☐ | ☐ |
| FR-003 | Trang chi tiết Affiliate Campaign (banner, mô tả, action states) | Must | ☐ | ☐ | ☐ |
| ~~FR-007~~ | ~~Trang Browse all chiến dịch (`/affiliate-campaigns`)~~ | Must | ☐ | ☐ | ☑ (đã đánh dấu bỏ ở trimmed PRD) |

### EPIC-002: Join + Generate Link Flow

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-004 | Tham gia chiến dịch (Join + retry PENDING/REJECTED) | Must | ☐ | ☐ | ☐ |
| FR-005 | Tạo link affiliate (modal, custom URL, name optional) | Must | ☐ | ☐ | ☐ |
| ~~FR-006~~ | ~~Trang "Link affiliate của tôi" (`/affiliate-links`)~~ | Must | ☐ | ☐ | ☑ (đã đánh dấu bỏ ở trimmed PRD) |

### EPIC-003: Touchpoint Liên kết Scalef

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-008 | Touchpoint Banner + Popup chặn action khi chưa link Scalef | Must | ☐ | ☐ | ☐ |

### EPIC-004: Backend Foundation

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-010 | Service layer FE (`services/affiliate.ts` + interfaces) | Must | ☐ | ☐ | ☐ |
| FR-011 | BE Proxy Scalef APIs (HMAC client + public endpoints + storage) | Must | ☐ | ☐ | ☐ |

### EPIC-005: Commission Dashboard (V2 trong PRD gốc)

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-009 | Trang "Hoa hồng của tôi" (3 KPI cards + orders list, no chart, no tab) | Should | ☐ | ☐ | ☐ |

### EPIC-006: Analytics & Polish

| ID | Tên | Priority gốc | V1? | V2? | Bỏ? |
|----|-----|:---:|:---:|:---:|:---:|
| FR-012 | Tracking events (Firebase/GTM funnel events) | Should | ☐ | ☐ | ☐ |

**Suggest:**
- **V1:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-008, FR-010, FR-011 (8 Must Have, đã bỏ FR-006/007)
- **V2:** FR-009 (commission dashboard), FR-012 (analytics)

---

## Tổng quan đề xuất V1 / V2 / Defer

### V1 — MVP (bắt buộc launch được affiliate flow end-to-end)

| Track | FR count V1 | Effort estimate |
|-------|:---:|---|
| Admin Setup | 5 (toàn bộ) | ~7d (~1.5 tuần) |
| Account Linking | 14 (Must Have) | ~2.5 tuần |
| FE Creator (trimmed) | 8 | ~6.5d |
| **Tổng V1** | **27 FRs** | **~5 tuần** (3 track có thể overlap) |

**V1 launch criteria:**
- Admin tạo được catalog ≥ 20 campaigns + map vào Event
- Creator OAuth link Scalef (kèm conflict resolution + OTP)
- Creator browse → join → generate link end-to-end qua Event
- Touchpoint linking smooth

### V2 — Enhancement (sau V1 ~2-3 tuần)

| Track | FR count V2 | Effort estimate |
|-------|:---:|---|
| Account Linking | 3 (FR-013, FR-014, FR-015) | ~1 tuần |
| FE Creator | 2 (FR-009 commission, FR-012 analytics) | ~5d |
| **Tổng V2** | **5 FRs** | **~2 tuần** |

**V2 value:**
- Recoverability (pending state resume) — giảm drop off
- Audit log đầy đủ cho dispute/compliance
- Commission dashboard — minh bạch thu nhập → retention
- Analytics — đo activation rate

### Defer / Out of scope

| FR | Lý do defer |
|----|-------------|
| Account Linking FR-016 (Batch migration) | Chỉ làm khi gần deadline Scalef chặn đăng ký. Could Have. |
| FE Creator FR-006 (My Links) | Đã quyết bỏ. Link hiển thị tại campaign detail. |
| FE Creator FR-007 (Browse all) | Đã quyết bỏ. Creator chỉ vào affiliate qua Event. |

---

## Decision Matrix (điền vào để chốt)

Sau khi bạn tick V1/V2/Bỏ ở các bảng trên, mình tạo PRD V1 và PRD V2 riêng để dev follow.

**Câu hỏi cần bạn quyết:**

1. **Account Linking FR-013 (Pending state resume):** V1 hay V2?
   - Pro V1: refresh browser giữa flow là edge case xảy ra thường xuyên, drop off lớn nếu không có
   - Pro V2: extra complexity (TTL collection, state machine), launch sớm hơn được nếu defer

2. **Account Linking FR-014 (Audit log đầy đủ):** V1 hay V2?
   - Pro V1: dispute xảy ra ngay khi launch, không có log = không xử lý được
   - Pro V2: minimum log có thể inline trong saga (FR-010), full audit defer được

3. **Account Linking FR-015 (Reverse linking):** V1.5 hay V2 hay bỏ?
   - Depend timeline 1K publisher Scalef có cần migrate gấp không

4. **FE Creator FR-009 (Commission dashboard):** V1 hay V2?
   - Pro V1: creator cần thấy được hoa hồng để retention
   - Pro V2: launch nhanh với MVP "tạo được link" trước

5. **FE Creator FR-012 (Analytics tracking):** V1 hay V2?
   - Pro V1: cần data từ ngày đầu để đo funnel
   - Pro V2: dev sau cũng track được retroactively từ logs server-side

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-12 | vinhnguyen | Initial — tổng hợp 35 FRs từ 3 PRD. Suggest V1 (27 FRs), V2 (5 FRs), Defer (3 FRs). |
