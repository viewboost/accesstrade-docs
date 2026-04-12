# PRD: Tích hợp Scalef — Phase 1 (Liên kết Tài khoản)

**Project:** Gen-Green × Scalef Integration
**Date:** 2026-04-12
**Version:** 1.0 (Phase 1)
**Author:** Product Manager
**Status:** Draft
**Demo:** `demo-gen-green` → `/lien-ket-scalef`

---

## 1. Executive Summary

Cho phép creator Gen-Green liên kết tài khoản Scalef (nền tảng affiliate) để tham gia chiến dịch bán hàng, tạo link affiliate và kiếm hoa hồng — tất cả ngay trong Gen-Green.

Phase 1 tập trung vào **luồng liên kết tài khoản**: creator đăng nhập Scalef, hệ thống so khớp thông tin (CCCD, SĐT, email), user lựa chọn thông tin muốn giữ khi có xung đột, xác thực OTP, liên kết thành công.

**Nguyên tắc cốt lõi:**
- Không bên nào là "source of truth" — user lựa chọn thông tin muốn giữ khi xung đột
- Bên nào chưa có thì lấy theo bên đã có
- CCCD là khóa matching đầu tiên (identity)
- Update thông tin ở cả 2 bên (bidirectional) — giao diện chung cho cả Gen-Green → Scalef và Scalef → Gen-Green

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Creator Gen-Green tham gia affiliate không cần rời nền tảng | Creator liên kết Scalef thành công ngay trong Gen-Green |
| 2 | Mở rộng nguồn thu cho 150K creators | Số creator liên kết Scalef tăng, target 1K user generate doanh thu |
| 3 | Đảm bảo đúng identity khi liên kết (1 người = 1 tài khoản) | 0% trường hợp liên kết sai người (CCCD mismatch) |
| 4 | Giải quyết xung đột thông tin mà không cần admin | >90% conflict resolution tự phục vụ (user chọn + OTP) |
| 5 | Hỗ trợ migration 1K publisher Scalef hiện tại | 1K user Scalef legacy có path vào Gen-Green |

---

## 3. User Personas

| Persona | Mô tả | Nhu cầu |
|---------|-------|---------|
| **Creator Gen-Green** | Đã có tài khoản Gen-Green, muốn tham gia affiliate | Liên kết Scalef nhanh, ít bước, hiểu rõ data nào được share |
| **Publisher Scalef (legacy)** | Đã có tài khoản Scalef (~1K), chưa có Gen-Green | Liên kết Gen-Green hoặc tạo account Gen-Green từ data Scalef |
| **Admin** | Quản lý nền tảng | Xem lịch sử liên kết, gỡ liên kết khi cần, xử lý edge case |

---

## 4. Scope

### In Scope (Phase 1)

- Luồng liên kết tài khoản Gen-Green ↔ Scalef (bidirectional)
- So khớp CCCD/SĐT/Email giữa 2 bên
- UI conflict resolution: user chọn thông tin giữ lại
- OTP xác thực khi update SĐT/Email
- Giao diện chung cho cả 2 chiều (Gen-Green → Scalef và Scalef → Gen-Green)
- Lưu trạng thái liên kết + lịch sử

### Out of Scope (Phase 2+)

| Feature | Phase |
|---------|-------|
| Dashboard affiliate (xem hoa hồng, đơn hàng) | Phase 2 |
| Tạo link affiliate trong Gen-Green | Phase 2 |
| Tham gia chiến dịch affiliate | Phase 2 |
| Hợp nhất tài khoản (Vin Creator Portal) | Phase 3 |
| Bỏ auth riêng Scalef (1 cửa đăng nhập) | Phase 3 |

---

## 5. Functional Requirements

### EPIC-001: Luồng liên kết (OAuth + Matching)

#### FR-001: Entry point liên kết trên Gen-Green

**Priority:** Must Have

**Description:**
Creator thấy thông tin về chương trình affiliate trên Gen-Green và có nút "Liên kết tài khoản Scalef". Entry point ở: Settings → Tài khoản liên kết, Tab Affiliate, Banner trong chiến dịch.

**Acceptance Criteria:**
- [ ] Nút "Liên kết Scalef" hiển thị ở Settings → Tài khoản liên kết
- [ ] Banner giới thiệu affiliate hiển thị trên dashboard/chiến dịch
- [ ] Nếu đã liên kết → hiển thị trạng thái "Đã liên kết" + thời gian
- [ ] Nếu chưa liên kết → hiển thị nút "Liên kết ngay"

---

#### FR-002: Đăng nhập Scalef (OAuth SSO)

**Priority:** Must Have

**Description:**
Redirect user sang SSO Scalef để đăng nhập. Scalef xử lý auth xong redirect về Gen-Green với authorization code.

**Acceptance Criteria:**
- [ ] Redirect sang SSO Scalef với `client_id=gengreen`
- [ ] Scalef user đăng nhập → redirect về Gen-Green callback URL kèm `code`
- [ ] Backend Gen-Green đổi code → access token (backend-to-backend)
- [ ] Backend gọi Scalef `/userinfo` → nhận: Scalef User ID, CCCD, SĐT, Email, Tên
- [ ] Thông tin nhạy cảm (CCCD, SĐT, email) không đi qua browser

**Dependencies:** Scalef SSO endpoint + `/userinfo` API

---

#### FR-003: Consent — Đồng ý chia sẻ thông tin

**Priority:** Must Have

**Description:**
Trước khi so khớp, hiển thị màn consent cho user biết thông tin nào được chia sẻ giữa 2 bên: Họ tên, CCCD, SĐT, Email.

**Acceptance Criteria:**
- [ ] Màn consent hiển thị rõ danh sách thông tin được chia sẻ
- [ ] Có nút "Đồng ý" và "Từ chối"
- [ ] Từ chối → quay về trang trước, không chia sẻ data
- [ ] Ghi nhận consent timestamp

---

#### FR-004: Check 1-đối-1

**Priority:** Must Have

**Description:**
Kiểm tra ràng buộc 1 Gen-Green user ↔ 1 Scalef user. Nếu vi phạm → từ chối liên kết.

**Acceptance Criteria:**
- [ ] Gen-Green user đã liên kết Scalef user khác → REJECT trước khi sang SSO
- [ ] Scalef user đã liên kết Gen-Green user khác → REJECT sau khi nhận userinfo
- [ ] Thông báo lỗi rõ ràng cho user

---

#### FR-005: Matching CCCD (Identity check)

**Priority:** Must Have

**Description:**
CCCD là khóa matching đầu tiên. Dùng để xác nhận "cùng 1 người" giữa 2 hệ thống.

**Acceptance Criteria:**
- [ ] Cả 2 bên đều có CCCD và giống nhau → PASS, tiến vào so field tiếp
- [ ] Cả 2 bên đều có CCCD và khác nhau → REJECT (không phải cùng người)
- [ ] 1 bên có, 1 bên thiếu → bỏ qua check CCCD, dùng SĐT/Email fallback
- [ ] Cả 2 bên đều thiếu CCCD → dùng SĐT/Email fallback
- [ ] Chuẩn hóa trước khi compare: bỏ khoảng trắng, chỉ giữ số

---

### EPIC-002: Conflict Resolution (Lựa chọn thông tin)

#### FR-006: So khớp thông tin

**Priority:** Must Have

**Description:**
So sánh từng field giữa Gen-Green và Scalef: SĐT, Email. Hiển thị kết quả dạng bảng: Khớp / Lệch / Bổ sung.

**Acceptance Criteria:**
- [ ] Bảng so sánh 2 cột (Gen-Green vs Scalef) cho mỗi field
- [ ] Badge: "Khớp" (xanh), "Lệch" (vàng), "Bổ sung" (xám — 1 bên trống)
- [ ] Chuẩn hóa trước khi so: SĐT → +84, Email → lowercase, CCCD → chỉ số
- [ ] CCCD hiển thị masked (chỉ 4 số cuối)

---

#### FR-007: Giao diện lựa chọn thông tin

**Priority:** Must Have

**Description:**
Với mỗi field lệch, user chọn giữ thông tin bên nào (Gen-Green hoặc Scalef). Với field 1 bên trống → auto-fill từ bên có, không cần user chọn.

**Acceptance Criteria:**
- [ ] Mỗi field lệch hiển thị 2 option (card chọn): Gen-Green value vs Scalef value
- [ ] User bấm chọn → highlight option đang chọn
- [ ] Field đã khớp → không hiện, bỏ qua
- [ ] Field 1 bên trống → auto-fill, thông báo "Sẽ bổ sung từ [bên có data]"
- [ ] Nếu CCCD khớp mà cả phone lẫn email đều lệch → bắt chọn cả 2

---

#### FR-008: OTP xác thực khi update

**Priority:** Must Have

**Description:**
Khi user chọn thông tin từ bên kia (cần update bên mình), bắt buộc OTP xác thực trước khi ghi.

**Acceptance Criteria:**
- [ ] Chọn SĐT từ Scalef → update Gen-Green → OTP gửi về SĐT mới
- [ ] Chọn Email từ Scalef → update Gen-Green → magic link / OTP gửi về email mới
- [ ] OTP hết hạn sau 5 phút
- [ ] Tối đa 5 lần nhập sai → lock 15 phút
- [ ] Nếu không có field nào cần update (tất cả khớp hoặc auto-fill) → skip OTP

---

#### FR-009: Check unique trước commit

**Priority:** Must Have

**Description:**
Trước khi ghi update, check SĐT/Email mới có đang thuộc user khác (ở cả 2 hệ thống) không.

**Acceptance Criteria:**
- [ ] SĐT đã thuộc Gen-Green user khác → REJECT với thông báo rõ
- [ ] Email đã thuộc Gen-Green user khác → REJECT
- [ ] SĐT/Email đã thuộc Scalef user khác → REJECT
- [ ] Thông báo hướng dẫn liên hệ support nếu bị reject

---

#### FR-010: Bidirectional update

**Priority:** Must Have

**Description:**
Update thông tin ở cả 2 bên theo lựa chọn của user. Ví dụ: chọn giữ email Gen-Green → update Scalef; chọn giữ SĐT Scalef → update Gen-Green.

**Acceptance Criteria:**
- [ ] Update Gen-Green profile thành công
- [ ] Gọi Scalef API update profile thành công
- [ ] Nếu 1 bên fail → rollback bên kia (saga/compensate)
- [ ] Ghi log: old value, new value, source, timestamp, actor

**Dependencies:** Scalef API `PUT /users/:id/profile` (cần confirm với team Scalef)

---

### EPIC-003: Hoàn tất & Trạng thái

#### FR-011: Liên kết thành công

**Priority:** Must Have

**Description:**
Sau khi matching + resolve + update xong → đánh dấu liên kết thành công. Hiển thị thông tin tài khoản hợp nhất + danh sách chiến dịch affiliate có sẵn.

**Acceptance Criteria:**
- [ ] Lưu `scalef_user_id`, `scalef_linked_at`, `scalef_link_method='oauth'` vào Gen-Green user
- [ ] Màn "Liên kết thành công" hiển thị profile hợp nhất
- [ ] Hiển thị danh sách chiến dịch affiliate sẵn sàng tham gia
- [ ] Nút "Chạy lại demo từ đầu" (chỉ ở demo)

---

#### FR-012: Reject + Hỗ trợ

**Priority:** Must Have

**Description:**
Mọi trường hợp reject hiển thị lý do rõ ràng + nút gửi yêu cầu hỗ trợ (auto-tạo ticket).

**Acceptance Criteria:**
- [ ] Thông báo reject hiển thị lý do cụ thể (theo bảng lý do)
- [ ] Nút "Gửi yêu cầu hỗ trợ" → auto-tạo ticket (Gen-Green User ID, Scalef User ID, lý do, timestamp)
- [ ] User không cần nhập gì — ticket tự động
- [ ] Hẹn phản hồi 3 ngày làm việc

**Bảng lý do reject:**

| Check | Điều kiện | User thấy |
|-------|-----------|-----------|
| 1-đối-1 (GG) | Gen-Green user đã liên kết Scalef user khác | "Tài khoản Gen-Green đã liên kết với tài khoản Scalef khác." |
| 1-đối-1 (SF) | Scalef user đã liên kết Gen-Green user khác | "Tài khoản Scalef này đã liên kết với tài khoản Gen-Green khác." |
| CCCD | 2 bên đều có CCCD và khác nhau | "Thông tin CCCD không khớp giữa 2 tài khoản." |
| Unique | SĐT/Email đã thuộc user khác | "SĐT/Email này đã được sử dụng bởi tài khoản khác." |

---

#### FR-013: Pending link state (resumable)

**Priority:** Should Have

**Description:**
Lưu trạng thái liên kết đang xử lý để user có thể resume nếu bị gián đoạn (refresh browser, mất mạng).

**Acceptance Criteria:**
- [ ] Bảng `pending_scalef_link`: user_id, scalef_user_id, scalef_snapshot, step, created_at
- [ ] TTL 15 phút — hết hạn tự xóa
- [ ] User quay lại trong TTL → resume từ bước đang dở
- [ ] Hết TTL → bắt đầu lại từ đầu

---

#### FR-014: Lịch sử liên kết

**Priority:** Should Have

**Description:**
Ghi log tất cả hoạt động liên kết: linked, unlinked, rejected, profile_updated.

**Acceptance Criteria:**
- [ ] Bảng `scalef_link_history`: gen_green_user_id, scalef_user_id, action, method, reject_reason, performed_by, timestamp
- [ ] Admin xem được lịch sử liên kết của user
- [ ] Ghi log cả profile update (old/new value, source)

---

### EPIC-004: Legacy Migration (1K user Scalef)

#### FR-015: Entry point từ phía Scalef

**Priority:** Should Have

**Description:**
1K publisher Scalef hiện tại có thể liên kết Gen-Green từ phía Scalef (chiều ngược). Dùng chung UI conflict resolution.

**Acceptance Criteria:**
- [ ] Nút "Liên kết Gen-Green" trên Scalef → OAuth sang Gen-Green
- [ ] Sau OAuth, đổ vào cùng flow matching/resolve/OTP
- [ ] Nếu chưa có Gen-Green account → hướng dẫn đăng ký Gen-Green trước

---

#### FR-016: Batch migration (admin)

**Priority:** Could Have

**Description:**
Admin batch tạo Gen-Green account từ data Scalef cho 1K user legacy. Gửi email thông báo kèm link set password.

**Acceptance Criteria:**
- [ ] Admin upload danh sách Scalef user ID cần migrate
- [ ] Hệ thống tạo Gen-Green account từ Scalef data (tên, SĐT, email, CCCD)
- [ ] Gửi email "Tài khoản Gen-Green đã được tạo" kèm link set password
- [ ] Tự động liên kết Scalef ↔ Gen-Green sau khi user set password

---

### EPIC-005: Field Update Policy & Security

#### FR-017: Phân loại field theo risk level

**Priority:** Must Have

**Description:**
Phân loại field update theo mức độ rủi ro. Low-risk: user tự update + OTP. High-risk: route admin.

**Acceptance Criteria:**

| Field | Risk | Update policy |
|-------|------|---------------|
| SĐT | Low | User chọn + OTP verify |
| Email | Low | User chọn + magic link / OTP verify |
| CCCD | High | CCCD khác → REJECT. Không cho user tự update CCCD |
| Tên pháp lý | High | Route admin review nếu conflict |
| MST | High | Route admin review |

---

#### FR-018: Data normalization

**Priority:** Must Have

**Description:**
Chuẩn hóa data trước mọi phép so sánh.

**Acceptance Criteria:**
- [ ] CCCD: bỏ khoảng trắng, chỉ giữ số. "012 345 678 901" → "012345678901"
- [ ] SĐT: đưa về +84, bỏ khoảng trắng. "0912 345 678" → "+84912345678"
- [ ] Email: lowercase, bỏ khoảng trắng. "User@Gmail.COM " → "user@gmail.com"

---

## 6. Non-Functional Requirements

### NFR-001: Security — Data không qua browser

**Priority:** Must Have

Thông tin nhạy cảm (CCCD, SĐT, Email) chỉ truyền backend-to-backend. Browser chỉ thấy authorization code (chuỗi random). Scalef `/userinfo` gọi từ Gen-Green backend.

---

### NFR-002: Security — OTP

**Priority:** Must Have

OTP 6 số, hết hạn 5 phút. Tối đa 5 lần nhập sai → lock 15 phút. Rate limit gửi OTP: 1 lần/60 giây.

---

### NFR-003: Security — Idempotent + Rollback

**Priority:** Must Have

Update profile phải idempotent. Nếu update Gen-Green OK nhưng Scalef fail → compensate rollback Gen-Green. Retry background job cho eventual consistency.

---

### NFR-004: Performance — Linking flow

**Priority:** Should Have

Toàn bộ flow liên kết (sau khi login Scalef xong) hoàn tất < 10 giây. So khớp + check unique < 2 giây.

---

### NFR-005: Reliability — Scalef API

**Priority:** Must Have

Scalef API timeout → graceful fallback + thông báo user "Thử lại sau". Retry 3 lần với backoff. Không để user kẹt ở trạng thái trung gian.

---

### NFR-006: Audit — Logging

**Priority:** Must Have

Ghi log mọi hoạt động: liên kết, reject, gỡ liên kết, profile update. Mỗi log entry: actor, action, old_value, new_value, source, timestamp.

---

## 7. Data Model

### User model — thêm fields

| Field | Type | Mô tả |
|-------|------|-------|
| `scalef_user_id` | string, nullable | ID tài khoản Scalef đã liên kết |
| `scalef_linked_at` | datetime, nullable | Thời điểm liên kết |
| `scalef_link_method` | enum, nullable | `oauth` / `batch` / `admin` |

### Bảng pending_scalef_link

| Field | Type | Mô tả |
|-------|------|-------|
| `id` | ObjectId | |
| `user_id` | string | Gen-Green user ID |
| `scalef_user_id` | string | Scalef user ID |
| `scalef_snapshot` | object | Tên, CCCD, SĐT, Email từ Scalef |
| `step` | enum | `compared` / `awaiting_otp` / `awaiting_email_verify` / `committed` |
| `created_at` | datetime | TTL 15 phút |

### Bảng scalef_link_history

| Field | Type | Mô tả |
|-------|------|-------|
| `id` | ObjectId | |
| `gen_green_user_id` | string | |
| `scalef_user_id` | string | |
| `action` | enum | `linked` / `unlinked` / `rejected` / `profile_updated` |
| `method` | enum | `oauth` / `batch` / `admin` |
| `reject_reason` | string, nullable | Lý do reject |
| `changes` | object, nullable | `{field, old_value, new_value, source}` |
| `performed_by` | string | User ID hoặc Admin ID |
| `timestamp` | datetime | |

---

## 8. Epics & Traceability

| Epic | FRs | Stories (est.) | Priority |
|------|-----|----------------|----------|
| EPIC-001: Luồng liên kết | FR-001 → FR-005 | 5-7 | Must Have |
| EPIC-002: Conflict Resolution | FR-006 → FR-010 | 5-7 | Must Have |
| EPIC-003: Hoàn tất & Trạng thái | FR-011 → FR-014 | 4-5 | Must Have |
| EPIC-004: Legacy Migration | FR-015 → FR-016 | 2-3 | Should Have |
| EPIC-005: Field Policy & Security | FR-017 → FR-018 | 2-3 | Must Have |

**Tổng:** 5 epics · 18 FRs · 6 NFRs · 18-25 stories

---

## 9. Prioritization

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | 14 | 5 |
| Should Have | 3 | 1 |
| Could Have | 1 | 0 |

---

## 10. Dependencies

### Có sẵn
- Gen-Green backend (Go) + user model
- Scalef SSO endpoint (OAuth2)

### Cần từ Scalef
| Dependency | Mô tả |
|-----------|-------|
| `GET /userinfo` | Trả về Scalef User ID, CCCD, SĐT, Email, Tên |
| `PUT /users/:id/profile` | Update SĐT/Email Scalef (bidirectional update) |
| Sandbox/staging environment | Để test luồng end-to-end |

### Cần backend Gen-Green
| Dependency | Mô tả |
|-----------|-------|
| OTP service (SĐT) | Gửi + verify OTP |
| Email verification service | Gửi magic link / OTP |
| Unique check SĐT/Email | Query trên user collection |

---

## 11. Assumptions

1. Scalef đồng ý cung cấp SSO + `/userinfo` + update profile API
2. CCCD có ở Scalef user (vì liên quan payout) — nếu thiếu thì fallback SĐT/Email
3. Gen-Green không phải tất cả user đều có CCCD
4. Scalef sẽ chặn đăng ký mới trong tương lai gần → không cần luồng "tạo Scalef account"
5. 1K user Scalef legacy cần migration path trước khi Scalef đóng đăng ký

---

## 12. Open Questions

1. **Scalef update API**: Scalef có hỗ trợ `PUT /users/:id/profile` không? (cần confirm)
2. **Saga rollback**: Chấp nhận eventual consistency hay hard rollback khi 1 bên fail?
3. **Tên pháp lý conflict**: Nếu tên khác nhau (Unicode vs ASCII) → có route admin không?
4. **Timeline Scalef chặn đăng ký**: Cụ thể sprint nào? Ảnh hưởng batch migration.
5. **CCCD sai format / test data**: "000000000000" có coi là hợp lệ không?

---

## 13. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| Phase 1a | 1 tuần | OAuth flow + Matching + Conflict UI + OTP |
| Phase 1b | 1 tuần | Bidirectional update + Rollback + Audit log |
| Phase 1c | 0.5 tuần | Legacy entry point + Pending state + Test E2E |
| **Tổng Phase 1** | **~2.5 tuần** | |

**Target:** Trước đầu tháng 5/2026

---

## 14. User Flows

### Flow 1: Creator Gen-Green liên kết Scalef (happy path)

```
Creator bấm "Liên kết Scalef"
  → Consent: đồng ý chia sẻ thông tin
  → Redirect sang SSO Scalef → đăng nhập
  → Return về Gen-Green
  → Backend lấy userinfo từ Scalef
  → Check 1-đối-1: OK
  → Match CCCD: khớp ✓
  → So SĐT: khớp ✓ / Email: lệch
  → User chọn giữ email nào
  → OTP verify email mới
  → Update cả 2 bên
  → Liên kết thành công ✓
```

### Flow 2: Tất cả khớp (1 click)

```
CCCD khớp + SĐT khớp + Email khớp
  → Skip conflict resolution + OTP
  → Liên kết thành công ngay ✓
```

### Flow 3: CCCD khác (reject)

```
CCCD Gen-Green ≠ CCCD Scalef
  → REJECT: "Thông tin CCCD không khớp"
  → Nút "Gửi yêu cầu hỗ trợ" → auto-ticket
```
