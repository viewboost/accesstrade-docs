# Product Requirements Document: Account Linking (Gen-Green ↔ Scalef)

**Date:** 2026-05-04
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Identity Integration (OAuth SSO + Conflict Resolution)
**Project Level:** Level 3
**Status:** Draft
**Platform:** Gen-Green (`accesstrade-projects/vcreator/`) ↔ Scalef

---

## Document Overview

PRD này định nghĩa requirements cho **Account Linking Phase 1** — flow liên kết tài khoản giữa Gen-Green (creator) và Scalef (publisher), bao gồm OAuth SSO, matching CCCD/SĐT/Email, conflict resolution UI cho creator chọn thông tin giữ lại, OTP verify khi update SĐT/Email.

**Đây là prerequisite cho Phase 2 (FE Creator Affiliate)** — không có `scalef_user_id` trên user thì không gọi được Scalef join campaign / generate link / report.

**Related Documents:**
- Overview: [account-linking-overview.md](account-linking-overview.md)
- PRD gốc Phase 1 Scalef: [`scalef-integration/prd-scalef-integration-v1-2026-04-12.md`](../scalef-integration/prd-scalef-integration-v1-2026-04-12.md) — base reference
- Scalef SSO spec: [scalef-api.md](scalef-api.md) — section 0 (OAuth Authorization Code Flow)
- Mockup live: https://demo-ambassador.accesstrade.click/lien-ket-scalef
- Mockup source: [`demo-gen-green/src/app/lien-ket-scalef/`](../../../demo-gen-green/src/app/lien-ket-scalef/)
- Phase 2 phụ thuộc: [PRD FE Creator](prd-fe-creator-2026-05-04.md)

**Lưu ý quan trọng — code vcreator hiện tại:**
vcreator backend hiện đã có 2 endpoint liên kết Scalef cũ ([`pkg/public/router/user.go:55-56`](../../../vcreator/backend/pkg/public/router/user.go)):
- `POST /users/link-account` (form email + phone)
- `POST /users/update-phone-number` (OTP confirm)

Flow này **KHÔNG đúng** với spec PRD (thiếu OAuth SSO, thiếu CCCD matching, thiếu conflict resolution UI, thiếu pending state resumable). **Phải làm lại** theo spec mới — flow cũ có thể được kept tạm thời cho legacy nhưng path chính dùng OAuth.

---

## Executive Summary

Cho phép creator Gen-Green liên kết tài khoản Scalef (nền tảng affiliate) để tham gia chiến dịch bán hàng, tạo link affiliate và kiếm hoa hồng — tất cả ngay trong Gen-Green.

Phase 1 tập trung vào **luồng liên kết tài khoản**: creator đăng nhập Scalef qua OAuth SSO, hệ thống so khớp thông tin (CCCD, SĐT, email), creator lựa chọn thông tin muốn giữ khi có xung đột, xác thực OTP, liên kết thành công.

**Nguyên tắc cốt lõi:**
- **CCCD là khóa identity** — matching đầu tiên để xác nhận "cùng 1 người". CCCD khác → reject.
- **Không bên nào "đúng" hơn** — user chọn giữ thông tin bên nào khi xung đột.
- **Bên nào trống thì lấy bên có** — auto-fill, không bắt user chọn.
- **OTP bắt buộc khi update** — chọn SĐT/Email từ Scalef → phải verify OTP trước khi update Gen-Green.
- **Update 2 chiều (bidirectional)** — sync data sang cả 2 bên theo lựa chọn user.
- **Data nhạy cảm không qua browser** — CCCD, SĐT, Email truyền backend-to-backend.

**Strategy implementation:**
- Mockup demo-gen-green đã chạy được (5 steps conflict / 3 steps no-conflict) → FE clone từ đó.
- BE cần build OAuth client + matching engine + OTP verify + bidirectional update.
- Reuse OTP service hiện có của vcreator (`internal/service/otp.go`).

---

## Product Goals

### Business Objectives

1. **Mở khoá doanh thu affiliate cho 150K creators Gen-Green** — không có linking thì không có Phase 2.
2. **Đảm bảo identity 1-1 đúng** — 0% case linking sai người (CCCD mismatch).
3. **Giải quyết xung đột tự phục vụ** — > 90% conflict resolution không cần admin (user chọn + OTP).
4. **Hỗ trợ migration 1.000 publisher Scalef hiện tại** — có path vào Gen-Green trước khi Scalef chặn đăng ký mới.
5. **Giải quyết bài toán thuế TNCN** — AccessTrade chi trả cho cả 2 bên, hệ thống nhận diện "cùng 1 người" để tính thuế đúng.

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Conversion linking flow (start → done) | ≥ 70% | 1 tháng sau launch |
| Self-service conflict resolution rate | ≥ 90% | 1 tháng |
| Linking sai người (CCCD mismatch leak) | 0% | Forever |
| Time-to-link (sau OAuth login) | < 2 phút | — |
| Tỉ lệ resume từ pending state | ≥ 50% | 1 tháng |
| 1K legacy publisher Scalef có path migrate | 100% | Trước khi Scalef chặn đăng ký |

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

Each requirement includes:
- **ID**: Unique identifier
- **Priority**: Must Have / Should Have / Could Have (MoSCoW)
- **Description**: What the system should do
- **Acceptance Criteria**: How to verify it's complete

---

### FR-001: Entry point liên kết trên Gen-Green

**Priority:** Must Have

**Description:**
Creator thấy nút/banner liên kết Scalef ở nhiều điểm chạm trên Gen-Green. Tất cả dẫn về cùng 1 flow OAuth.

**Acceptance Criteria:**

**Authorization:** Mọi creator đăng nhập đều có thể bấm liên kết. Không yêu cầu role đặc biệt.

**Điểm chạm:**
- [ ] Trang đăng nhập Gen-Green: nút "Đăng nhập bằng Scalef" cạnh Google/Apple
- [ ] Trang đăng ký Gen-Green: nút "Đăng ký bằng Scalef"
- [ ] Settings → Tài khoản liên kết: trạng thái "Chưa liên kết" + nút "Liên kết"
- [ ] Tab Affiliate trong dashboard: banner giới thiệu (nếu có affiliate active)
- [ ] Chi tiết Event có affiliate liên kết: banner "Liên kết Scalef để kiếm hoa hồng" (Phase 2 — FE Creator FR-008)
- [ ] Bấm "Tham gia chiến dịch" / "Tạo link" mà chưa link → popup chặn (Phase 2)

**Trạng thái hiển thị:**
- [ ] Chưa link: hiển thị nút "Liên kết ngay"
- [ ] Đã link: hiển thị "Đã liên kết — username Scalef" + ngày liên kết + KHÔNG có nút gỡ (chỉ admin gỡ được)

**Dependencies:** None

---

### FR-002: Đăng nhập Scalef (OAuth SSO)

**Priority:** Must Have

**Description:**
Redirect user sang Scalef SSO theo flow OAuth2 Authorization Code. Backend Gen-Green xử lý token exchange backend-to-backend, không lộ credentials.

**Acceptance Criteria:**

**Step 1 — Generate state (chống CSRF):**
- [ ] Backend generate `state` random (UUID hoặc 32-byte hex), lưu vào session/cache
- [ ] State có TTL 15 phút

**Step 2 — Redirect sang Scalef:**
- [ ] URL: `https://<sso-domain>/oauth/authorize?provider=&client_id=GENGREEN_CLIENT_ID&scope=user_info&response_type=code&redirect_uri=<gen_green_callback>&state=<state>`
- [ ] `provider` để trống (user nhập username/password Scalef)
- [ ] `scope=user_info` (chỉ cần thông tin user)

**Step 3-5 — User đăng nhập Scalef (handled by Scalef):**

**Step 6 — Callback xử lý:**
- [ ] Receive `code` + `state` qua redirect_uri
- [ ] Verify `state` match state đã lưu → mismatch reject (CSRF)
- [ ] State chỉ dùng 1 lần — verify xong xoá ngay

**Step 7 — Exchange code → access token:**
- [ ] Backend POST `https://<sso-domain>/oauth/token` với `grant_type=authorization_code`, `code`, `redirect_uri`, `Authorization: Basic base64(client_id:client_secret)`
- [ ] Parse response → lấy `access_token`, `refresh_token`, `user_id`, `user_name`, `phone`, `email`

**Step 8 — Lưu token + lấy thông tin user:**
- [ ] Token store backend (Redis hoặc DB) với TTL theo `expires_in`
- [ ] Nếu cần CCCD (chưa có trong response token) → call thêm Scalef API hoặc xử lý qua bước matching không bắt buộc CCCD (xem FR-005)
- [ ] **Thông tin nhạy cảm KHÔNG đi qua browser** — chỉ authorization code (random string) qua browser

**Error handling:**
- [ ] State mismatch → 403 + log security event
- [ ] Code invalid / expired → redirect về Gen-Green với error message
- [ ] Scalef timeout → fallback "Thử lại sau" + retry button

**Dependencies:** Scalef SSO endpoint live + credentials cấp cho Gen-Green tenant

---

### FR-003: Consent — Đồng ý chia sẻ thông tin

**Priority:** Must Have

**Description:**
Trước khi BE thực hiện matching, FE hiển thị màn consent cho user biết thông tin nào được chia sẻ giữa 2 bên.

**Acceptance Criteria:**
- [ ] Màn consent hiển thị danh sách thông tin sẽ share: Họ tên, CCCD, SĐT, Email
- [ ] Mô tả ngắn từng item (CCCD: "để xác minh cùng người", SĐT/Email: "để liên hệ + tracking")
- [ ] 2 nút: "Đồng ý chia sẻ" (primary) + "Từ chối" (secondary)
- [ ] Từ chối → quay về Gen-Green, KHÔNG chia sẻ data, KHÔNG link
- [ ] Đồng ý → ghi nhận `consent_at` timestamp + tiếp Step matching
- [ ] CCCD luôn masked trong UI (chỉ hiển thị 4 số cuối)

**Dependencies:** FR-002 (sau OAuth thành công)

---

### FR-004: Check 1-đối-1

**Priority:** Must Have

**Description:**
Kiểm tra ràng buộc 1 Gen-Green user ↔ 1 Scalef user. Vi phạm → reject ngay.

**Acceptance Criteria:**
- [ ] **Check trước khi sang Scalef:** Gen-Green user hiện tại đã có `scalef_user_id` set → reject với message "Tài khoản Gen-Green đã liên kết Scalef khác"
- [ ] **Check sau OAuth callback:** Scalef user_id trả về đã thuộc Gen-Green user khác trong `users` collection → reject với message "Tài khoản Scalef này đã liên kết Gen-Green khác"
- [ ] Reject screen hiển thị nút "Gửi yêu cầu hỗ trợ" (FR-012)
- [ ] Log security event để admin xem được pattern abuse

**Dependencies:** FR-002

---

### FR-005: Matching CCCD (Identity check)

**Priority:** Must Have

**Description:**
CCCD là khóa matching đầu tiên — xác nhận "cùng 1 người" giữa 2 hệ thống. CCCD khác giữa 2 bên = không phải cùng người = reject.

**Acceptance Criteria:**

**Logic matching:**
- [ ] Cả 2 bên đều có CCCD và **giống nhau** → PASS, tiến vào FR-006 (so SĐT/Email)
- [ ] Cả 2 bên đều có CCCD và **khác nhau** → REJECT (không phải cùng người)
- [ ] 1 bên có CCCD, 1 bên không → bỏ qua check CCCD, dùng SĐT/Email fallback (FR-006)
- [ ] Cả 2 bên đều thiếu CCCD → bỏ qua, dùng SĐT/Email fallback

**Chuẩn hóa trước khi compare:**
- [ ] Bỏ khoảng trắng, ký tự đặc biệt
- [ ] Chỉ giữ số
- [ ] VD `"012 345 678 901"` → `"012345678901"`

**Reject path:**
- [ ] Hiển thị màn reject với lý do: "Thông tin CCCD không khớp giữa 2 tài khoản"
- [ ] Nút "Gửi yêu cầu hỗ trợ" (FR-012)

**Edge cases:**
- [ ] CCCD `"000000000000"` (test data) → coi là invalid, không pass
- [ ] CCCD < 12 số → coi là invalid (CMND 9 số → admin override only, không tự matching)

**Dependencies:** FR-003

**Open question:** Scalef SSO `/oauth/token` response hiện chỉ trả `phone + email`, **không có CCCD**. Cần Scalef bổ sung field CCCD hoặc Gen-Green skip CCCD check (chỉ dùng SĐT/Email fallback). Note ở Open Questions.

---

### FR-006: So khớp thông tin (Comparison)

**Priority:** Must Have

**Description:**
So sánh từng field giữa Gen-Green và Scalef: SĐT, Email. Hiển thị bảng so sánh dạng "Khớp / Lệch / Bổ sung".

**Acceptance Criteria:**

**Chuẩn hóa trước khi compare:**
- [ ] SĐT: đưa về format `+84xxxxxxxxx`, bỏ khoảng trắng. VD `"0912 345 678"` → `"+84912345678"`
- [ ] Email: lowercase, bỏ khoảng trắng. VD `"User@Gmail.COM "` → `"user@gmail.com"`

**UI bảng so sánh:**
- [ ] 2 cột: Gen-Green vs Scalef
- [ ] Mỗi field 1 dòng, kèm badge:
  - **Khớp** (xanh) — 2 bên giống nhau
  - **Lệch** (vàng) — 2 bên khác nhau
  - **Bổ sung** (xám) — 1 bên trống
- [ ] CCCD masked (chỉ 4 số cuối) — KHÔNG hiển thị full
- [ ] Nếu tất cả khớp → tự động chuyển sang FR-011 (skip FR-007/008)
- [ ] Nếu có lệch hoặc bổ sung → tiếp FR-007

**Dependencies:** FR-005

---

### FR-007: Giao diện lựa chọn thông tin (Conflict Resolution)

**Priority:** Must Have

**Description:**
Với mỗi field lệch giữa 2 bên, user chọn giữ thông tin bên nào (Gen-Green hay Scalef). Field 1 bên trống → auto-fill từ bên có, không bắt user chọn.

**Acceptance Criteria:**

**UI cho field lệch:**
- [ ] Mỗi field lệch hiển thị 2 card chọn (radio):
  - Card 1: Giá trị Gen-Green
  - Card 2: Giá trị Scalef
- [ ] User bấm chọn 1 card → highlight
- [ ] Default: chọn Gen-Green (an toàn — không update sang Scalef nếu user không chủ động)

**UI cho field bổ sung (1 bên trống):**
- [ ] Hiển thị "Sẽ bổ sung [SĐT/Email] từ [Gen-Green/Scalef]"
- [ ] Auto-fill, không có UI chọn
- [ ] Vẫn cần OTP verify nếu data sang bên trống (FR-008)

**Skip case:**
- [ ] Field đã khớp → KHÔNG hiển thị, skip
- [ ] Tất cả field khớp → bypass màn này, chuyển thẳng FR-011

**CCCD đặc biệt:**
- [ ] Nếu CCCD lệch → đã reject ở FR-005, không vào màn này
- [ ] Nếu CCCD 1 bên trống → bổ sung tự động (không cho user override CCCD)

**Dependencies:** FR-006

---

### FR-008: OTP xác thực khi update

**Priority:** Must Have

**Description:**
Khi user chọn data từ Scalef (cần update Gen-Green) hoặc auto-fill từ Scalef, bắt buộc OTP verify trước khi ghi.

**Acceptance Criteria:**

**Trigger OTP:**
- [ ] User chọn SĐT từ Scalef → update Gen-Green → OTP gửi về **SĐT mới** (Scalef value)
- [ ] User chọn Email từ Scalef → update Gen-Green → magic link / OTP gửi về **Email mới**
- [ ] Auto-fill từ Scalef (Gen-Green trống) → OTP về SĐT/Email mới
- [ ] Skip OTP nếu user chọn giữ Gen-Green value (không update gì)
- [ ] Skip OTP nếu auto-fill từ Gen-Green sang Scalef (chỉ update bên Scalef)

**OTP rules:**
- [ ] OTP 6 chữ số
- [ ] Hết hạn sau **5 phút**
- [ ] Tối đa **5 lần nhập sai** → lock 15 phút
- [ ] Rate limit: 1 OTP / 60 giây / SĐT/Email

**UI:**
- [ ] Input 6 ô số riêng biệt (auto-focus next)
- [ ] Countdown 5 phút
- [ ] Nút "Gửi lại OTP" (disabled 60s sau lần gửi cuối)
- [ ] Hiển thị SĐT/Email được verify (masked: `+84*****5678` / `h***@gmail.com`)

**Reuse:**
- [ ] Reuse OTP service hiện có của vcreator: `internal/service/otp.go` (`SendOTPAccessTrade`, `VerifyOTP`)
- [ ] Reuse endpoint patterns: `POST /users/profile/request-otp`, `POST /users/profile/verify-otp`

**Dependencies:** FR-007

---

### FR-009: Check unique trước commit

**Priority:** Must Have

**Description:**
Trước khi ghi update, check SĐT/Email mới có đang thuộc user khác (ở cả Gen-Green và Scalef) không.

**Acceptance Criteria:**
- [ ] SĐT mới đã thuộc Gen-Green user khác → REJECT với "SĐT này đã được dùng bởi tài khoản khác"
- [ ] Email mới đã thuộc Gen-Green user khác → REJECT
- [ ] SĐT mới đã thuộc Scalef user khác → REJECT
- [ ] Email mới đã thuộc Scalef user khác → REJECT
- [ ] Reject screen kèm nút "Gửi yêu cầu hỗ trợ" (FR-012)
- [ ] Check trong **transaction** với commit để tránh race condition

**Dependencies:** FR-008

---

### FR-010: Bidirectional update + Saga rollback

**Priority:** Must Have

**Description:**
Update thông tin ở cả 2 bên (Gen-Green ↔ Scalef) theo lựa chọn user. Nếu 1 bên fail → rollback bên kia (saga compensate).

**Acceptance Criteria:**

**Logic update:**
- [ ] User chọn data Gen-Green → update Scalef qua API `PUT /users/{id}/profile` (Scalef cung cấp)
- [ ] User chọn data Scalef → update Gen-Green local DB
- [ ] Field khớp → không update gì

**Saga pattern:**
- [ ] Update Gen-Green local trước (transaction)
- [ ] Gọi Scalef API update
- [ ] Nếu Scalef OK → commit Gen-Green transaction
- [ ] Nếu Scalef fail → rollback Gen-Green local + log error
- [ ] Background retry job 3 lần với exponential backoff cho eventual consistency
- [ ] Nếu retry hết → notification admin xử lý thủ công

**Audit:**
- [ ] Ghi `scalef_link_history`: field, old_value, new_value, source (gengreen/scalef), timestamp, actor

**Dependencies:** FR-009, Scalef `PUT /users/{id}/profile` API

**Open question:** Scalef `PUT /users/{id}/profile` API spec chưa xác nhận hỗ trợ. Cần Scalef confirm.

---

### FR-011: Liên kết thành công

**Priority:** Must Have

**Description:**
Sau matching + resolve + update xong → đánh dấu liên kết thành công. Hiển thị màn confirmation + entry point Phase 2.

**Acceptance Criteria:**

**Lưu data:**
- [ ] Update `users` collection: `scalef_user_id`, `scalef_linked_at`, `scalef_link_method='oauth'`
- [ ] Ghi `scalef_link_history` với action `linked`

**Màn confirmation:**
- [ ] Title: "Liên kết thành công 🎉"
- [ ] Hiển thị profile hợp nhất (tên, CCCD masked, SĐT, Email)
- [ ] Hiển thị "Bạn có thể bắt đầu kiếm hoa hồng affiliate" + nút CTA
- [ ] (V2) Hiển thị danh sách chiến dịch affiliate sẵn sàng tham gia
- [ ] Nút "Bắt đầu" → redirect về trang trước flow linking (preserve context)

**Phase 2 unlock:**
- [ ] User giờ có `scalef_user_id` → middleware FE Creator (Phase 2 NFR-003) cho phép join campaign / generate link

**Dependencies:** FR-010

---

### FR-012: Reject + Hỗ trợ

**Priority:** Must Have

**Description:**
Mọi trường hợp reject (FR-004 / FR-005 / FR-009 / Scalef error) hiển thị cùng 1 màn — lý do rõ ràng + auto-tạo support ticket.

**Acceptance Criteria:**

**UI reject screen:**
- [ ] Title: "Không thể liên kết"
- [ ] Body: lý do cụ thể theo bảng dưới
- [ ] Icon warning
- [ ] Nút "Gửi yêu cầu hỗ trợ" (primary) + "Quay lại" (secondary)

**Bảng lý do:**

| Check | Trigger | Message |
|-------|---------|---------|
| 1-đối-1 (GG) | FR-004: GG user đã link Scalef khác | "Tài khoản Gen-Green đã liên kết Scalef khác." |
| 1-đối-1 (SF) | FR-004: Scalef user đã link GG khác | "Tài khoản Scalef này đã liên kết Gen-Green khác." |
| CCCD mismatch | FR-005: CCCD 2 bên khác | "Thông tin CCCD không khớp giữa 2 tài khoản." |
| Unique violation | FR-009: SĐT/Email đã dùng | "SĐT/Email này đã được sử dụng bởi tài khoản khác." |
| Scalef error | OAuth/API timeout, code invalid | "Hệ thống Scalef đang gặp sự cố. Vui lòng thử lại sau." |

**Auto-ticket:**
- [ ] Bấm "Gửi yêu cầu hỗ trợ" → BE auto tạo ticket với metadata:
  - Gen-Green User ID
  - Scalef User ID (nếu có từ OAuth)
  - Reject reason
  - Timestamp
  - Snapshot data (CCCD/SĐT/Email — masked trong ticket UI nhưng full trong DB)
- [ ] Hẹn phản hồi 3 ngày làm việc
- [ ] User KHÔNG cần nhập gì thêm
- [ ] Ticket gửi qua hệ thống support hiện có (email + Telegram bot — reuse `internal/module/telegram/`)

**Dependencies:** FR-004, FR-005, FR-009

---

### FR-013: Pending link state (resumable)

**Priority:** Should Have

**Description:**
Lưu trạng thái linking đang xử lý để user có thể resume nếu bị gián đoạn (refresh browser, mất mạng, đóng tab giữa chừng).

**Acceptance Criteria:**

**Bảng `pending_scalef_link`:**
- [ ] Schema: `user_id`, `scalef_user_id`, `scalef_snapshot` (tên, CCCD, SĐT, Email từ Scalef), `step` (consent/compared/awaiting_otp/awaiting_email_verify), `created_at`
- [ ] TTL **15 phút** — hết tự xoá (MongoDB TTL index)
- [ ] Unique index `user_id` (1 user chỉ 1 pending link)

**Resume logic:**
- [ ] User quay lại trong 15' → fetch pending state → resume từ `step`:
  - `consent` → render lại màn consent
  - `compared` → render lại màn so khớp
  - `awaiting_otp` → render lại màn OTP (giữ SĐT/Email được verify)
  - `awaiting_email_verify` → tương tự
- [ ] Hết 15' → bắt đầu lại từ đầu (delete pending, redirect Step 1)

**Cleanup:**
- [ ] Khi link thành công (FR-011) → delete pending
- [ ] Khi user reject consent → delete pending
- [ ] Khi reject ở bất kỳ check nào → delete pending

**Dependencies:** FR-003

---

### FR-014: Lịch sử liên kết (Audit log)

**Priority:** Should Have

**Description:**
Ghi log mọi hoạt động linking: linked, unlinked, rejected, profile_updated. Dùng để admin truy vết + dispute resolution.

**Acceptance Criteria:**

**Bảng `scalef_link_history`:**

| Field | Type | Mô tả |
|-------|------|-------|
| `_id` | ObjectId | |
| `gen_green_user_id` | ObjectId | |
| `scalef_user_id` | string | |
| `action` | enum | `linked` / `unlinked` / `rejected` / `profile_updated` |
| `method` | enum | `oauth` / `batch` / `admin` |
| `reject_reason` | string, nullable | Theo bảng FR-012 |
| `changes` | object, nullable | `{field, old_value, new_value, source}` cho profile_updated |
| `performed_by` | ObjectId | User ID hoặc Admin ID |
| `timestamp` | datetime | |

**Use cases:**
- [ ] Admin xem được history theo `gen_green_user_id` hoặc `scalef_user_id`
- [ ] Filter theo action / method / time range
- [ ] Export CSV cho audit

**TTL:** Không có (giữ vĩnh viễn — compliance + dispute)

**Reuse:**
- [ ] Reuse audit framework hiện có: `internal/service/audit.go` nếu cover đủ schema, hoặc tạo collection riêng `scalef_link_history`

**Dependencies:** FR-011, FR-012, FR-010

---

### FR-015: Entry point từ phía Scalef (Reverse linking)

**Priority:** Should Have

**Description:**
1.000 publisher Scalef hiện tại có thể liên kết Gen-Green từ phía Scalef (chiều ngược). Dùng chung UI conflict resolution + matching engine.

**Acceptance Criteria:**
- [ ] Scalef có nút "Liên kết Gen-Green" → OAuth Gen-Green qua Gen-Green SSO endpoint
- [ ] Sau OAuth callback ở Scalef, đổ vào cùng flow matching/resolve/OTP của Gen-Green
- [ ] Nếu publisher Scalef chưa có Gen-Green account → redirect sang đăng ký Gen-Green trước, sau đó auto-link
- [ ] UI conflict resolution dùng chung component với chiều xuôi (FR-007)

**Out of scope V1:** Scalef → Gen-Green SSO endpoint cần Gen-Green build (nếu chưa có). Có thể defer sang V1.5.

**Dependencies:** FR-002 (mirror flow), Gen-Green SSO endpoint

---

### FR-016: Batch migration (admin)

**Priority:** Could Have

**Description:**
Admin batch tạo Gen-Green account từ data Scalef cho 1.000 publisher legacy. Gửi email thông báo kèm link set password.

**Acceptance Criteria:**
- [ ] Admin upload CSV danh sách Scalef user IDs cần migrate
- [ ] BE call Scalef API lấy data từng user (tên, SĐT, Email, CCCD)
- [ ] Tạo Gen-Green account placeholder với data Scalef (status `pending_setup`)
- [ ] Gửi email "Tài khoản Gen-Green đã được tạo cho bạn" kèm magic link set password
- [ ] User click magic link → set password → account active → auto-link Scalef ↔ Gen-Green
- [ ] Audit `scalef_link_history` với `method='batch'`, `performed_by=<admin_id>`
- [ ] Dashboard admin: xem progress migration (X/1000 done, Y failed)

**Dependencies:** FR-014, Admin permission

---

### FR-017: Phân loại field theo risk level

**Priority:** Must Have

**Description:**
Phân loại field update theo mức rủi ro. Low-risk: user tự update + OTP. High-risk: route admin review.

**Acceptance Criteria:**

| Field | Risk | Update policy |
|-------|------|---------------|
| SĐT | Low | User chọn + OTP verify (FR-008) |
| Email | Low | User chọn + OTP/magic link verify |
| CCCD | High | CCCD khác → REJECT (FR-005). User KHÔNG được tự update CCCD. |
| Tên pháp lý | High | Conflict → route admin review (KHÔNG cho user override) |
| MST (mã số thuế) | High | Route admin review |

**UI:**
- [ ] FR-007 conflict resolution chỉ hiển thị field low-risk (SĐT, Email)
- [ ] Field high-risk lệch → reject hoặc skip với note "Liên hệ admin để cập nhật"

**Dependencies:** FR-005, FR-007

---

### FR-018: Data normalization

**Priority:** Must Have

**Description:**
Chuẩn hoá data trước mọi phép so sánh để tránh false-mismatch do format khác nhau.

**Acceptance Criteria:**
- [ ] CCCD: bỏ khoảng trắng + ký tự đặc biệt, chỉ giữ số. `"012 345 678 901"` → `"012345678901"`
- [ ] SĐT: parse về format `+84xxxxxxxxx`. Hỗ trợ input format: `0xxx`, `+84xxx`, `84xxx`, có khoảng trắng/dấu `-`
- [ ] Email: lowercase + trim. `"User@Gmail.COM "` → `"user@gmail.com"`
- [ ] Tên: trim trailing spaces, KHÔNG normalize Unicode (giữ accent tiếng Việt)
- [ ] Centralized utility — reuse cho cả matching (FR-006) và unique check (FR-009)

**Dependencies:** None (utility cho các FR khác)

---

## Non-Functional Requirements

Non-Functional Requirements (NFRs) define **how** the system performs.

---

### NFR-001: Security — Data không qua browser

**Priority:** Must Have

**Description:**
Thông tin nhạy cảm (CCCD, SĐT, Email, access_token) chỉ truyền backend-to-backend.

**Acceptance Criteria:**
- [ ] Browser chỉ thấy `state` + `code` (random strings)
- [ ] OAuth `/oauth/token` exchange backend-to-backend (KHÔNG ở frontend)
- [ ] Scalef user info (CCCD/SĐT/Email) lấy backend, render trong UI có masking
- [ ] CCCD luôn masked trong UI (4 số cuối)
- [ ] Access token KHÔNG lộ ra console / localStorage / cookies non-httpOnly
- [ ] Logs masked sensitive fields (CCCD masked, SĐT mask 4 số giữa, Email mask local part)

**Rationale:**
Compliance + nếu browser/JS bị compromise (XSS, malicious extension), không lộ identity creator.

---

### NFR-002: Security — OTP

**Priority:** Must Have

**Description:**
OTP đủ secure để tránh brute force + abuse.

**Acceptance Criteria:**
- [ ] OTP 6 chữ số (10^6 = 1M combinations)
- [ ] Hết hạn 5 phút
- [ ] Tối đa 5 lần nhập sai → lock 15 phút (per-user-per-target)
- [ ] Rate limit gửi OTP: 1 lần / 60 giây / SĐT|Email
- [ ] Rate limit gửi OTP toàn hệ thống: 100/phút (chống abuse SMS gateway)
- [ ] OTP generated bằng cryptographically secure random (NOT `Math.random()`)
- [ ] Lưu OTP hash (bcrypt/argon2) thay vì plaintext trong DB

**Rationale:**
SMS OTP là vector tấn công phổ biến (SIM swap, brute force).

---

### NFR-003: Security — Saga + Idempotent + Rollback

**Priority:** Must Have

**Description:**
Update profile phải idempotent + có rollback khi 1 bên fail.

**Acceptance Criteria:**
- [ ] Update Gen-Green local có `idempotency_key` (UUID per request) — request lại cùng key không tạo update trùng
- [ ] Saga: GG update → Scalef update → confirm GG. Nếu Scalef fail → rollback GG (compensating transaction)
- [ ] Background retry job 3 lần với exponential backoff (1s, 2s, 4s) cho transient error
- [ ] Sau retry hết → log critical + admin notification (Telegram bot)
- [ ] State machine có 4 trạng thái: `pending_gg / pending_sf / committed / rolled_back`

**Rationale:**
Profile update cross-system → eventual consistency là OK, nhưng phải có rollback rõ ràng để không lệch data.

---

### NFR-004: Performance — Linking flow

**Priority:** Should Have

**Description:**
Toàn bộ flow đủ nhanh để không drop user.

**Acceptance Criteria:**
- [ ] Toàn bộ flow (sau OAuth login) hoàn tất < **10 giây** (không tính thời gian user nhập OTP)
- [ ] Matching + check unique: < 2 giây
- [ ] OAuth token exchange: < 3 giây (network bound)
- [ ] Each Scalef API call: < 5 giây timeout
- [ ] Page render mỗi step: < 1.5 giây first paint

**Rationale:**
Linking flow là conversion-critical. Mỗi giây delay = drop off rate tăng.

---

### NFR-005: Reliability — Scalef API resilience

**Priority:** Must Have

**Description:**
Scalef API có thể chậm/timeout/lỗi — không để user kẹt.

**Acceptance Criteria:**
- [ ] Scalef timeout (5s) → fallback "Thử lại sau" + retry button
- [ ] Retry 3 lần với exponential backoff (1s, 2s, 4s)
- [ ] Circuit breaker: sau 5 fail consecutive → open circuit 1 phút (theo pattern Ambassador NFR-004)
- [ ] User KHÔNG bị kẹt ở trạng thái trung gian — pending state luôn resumable (FR-013)
- [ ] Error message user-friendly tiếng Việt, KHÔNG raw Scalef error code

**Rationale:**
Linking flow phụ thuộc Scalef. Scalef downtime = Gen-Green linking downtime — phải graceful.

---

### NFR-006: Audit — Logging mọi action

**Priority:** Must Have

**Description:**
Ghi log mọi hoạt động linking để compliance + dispute.

**Acceptance Criteria:**
- [ ] Log: linked, unlinked, rejected, profile_updated, otp_sent, otp_verified, oauth_callback
- [ ] Mỗi log entry: `actor`, `action`, `old_value` (nếu có), `new_value` (nếu có), `source`, `timestamp`, `request_id`
- [ ] Log mask sensitive fields (CCCD, SĐT full, Email local part)
- [ ] Logs lưu vĩnh viễn cho action `linked/unlinked/profile_updated` (compliance)
- [ ] Logs OTP có TTL 90 ngày (chỉ debug)

**Rationale:**
Identity-related actions là payment-critical. Phải truy vết được.

---

### NFR-007: Compatibility — Existing Gen-Green system

**Priority:** Must Have

**Description:**
Không phá vỡ tính năng hiện có khi thêm linking.

**Acceptance Criteria:**
- [ ] User model thêm fields mới (`scalef_user_id`, `scalef_linked_at`, `scalef_link_method`) — backward compatible (nullable)
- [ ] 2 endpoint cũ (`POST /users/link-account`, `POST /users/update-phone-number`) **GIỮ tạm** cho backward compat 1 release, sau đó mark deprecated
- [ ] OTP service (`internal/service/otp.go`) reuse, không tạo mới
- [ ] Telegram notification (`internal/module/telegram/`) reuse cho admin alerts

**Rationale:**
Avoid regression. vcreator có 150K active users.

---

### NFR-008: Mobile responsive

**Priority:** Must Have

**Description:**
70%+ creator dùng mobile.

**Acceptance Criteria:**
- [ ] Mọi page hoạt động ≥ 320px width
- [ ] Bảng so sánh (FR-006) responsive: desktop 2 cột ngang, mobile stack dọc
- [ ] Conflict resolution card (FR-007) full-width mobile
- [ ] OTP input mobile-friendly (numeric keyboard auto)
- [ ] Touch target ≥ 44x44px

**Rationale:**
Mobile-first.

---

## Epics

---

### EPIC-001: OAuth SSO + Matching

**Description:**
Backbone của linking flow — OAuth flow đến Scalef, exchange code → token, matching CCCD + check 1-1.

**Functional Requirements:**
- FR-001 (Entry points)
- FR-002 (OAuth SSO)
- FR-003 (Consent)
- FR-004 (Check 1-1)
- FR-005 (CCCD matching)
- FR-018 (Data normalization)

**Story Count Estimate:** 7-9

**Priority:** Must Have

**Business Value:**
Không có epic này = không có linking. Backbone toàn flow.

---

### EPIC-002: Conflict Resolution

**Description:**
UI cho creator chọn data khi xung đột + OTP verify + check unique + bidirectional update với rollback.

**Functional Requirements:**
- FR-006 (So khớp)
- FR-007 (Lựa chọn)
- FR-008 (OTP verify)
- FR-009 (Check unique)
- FR-010 (Bidirectional update)
- FR-017 (Field risk classification)

**Story Count Estimate:** 7-9

**Priority:** Must Have

**Business Value:**
Self-service conflict resolution = giảm 90% tải admin.

---

### EPIC-003: Hoàn tất, Reject & State Management

**Description:**
Màn confirmation, reject screen với auto-ticket, pending state resumable, audit log.

**Functional Requirements:**
- FR-011 (Liên kết thành công)
- FR-012 (Reject + Hỗ trợ)
- FR-013 (Pending state)
- FR-014 (Audit log)

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:**
UX cuối flow + recoverability + compliance.

---

### EPIC-004: Legacy Migration

**Description:**
Path migrate 1.000 publisher Scalef hiện tại — reverse linking từ Scalef + batch migration admin.

**Functional Requirements:**
- FR-015 (Reverse linking)
- FR-016 (Batch migration admin)

**Story Count Estimate:** 3-5

**Priority:** Should Have / Could Have

**Business Value:**
Không lost 1K publisher legacy. Có thể defer nếu Scalef chưa chặn đăng ký mới.

---

## User Stories (High-Level)

### EPIC-001 stories

- **US-001:** As a creator chưa link Scalef, I want to bấm nút "Liên kết Scalef" từ Settings so that bắt đầu flow linking dễ dàng.
- **US-002:** As a creator, I want to thấy màn consent rõ ràng thông tin nào được chia sẻ so that biết mình đang đồng ý gì trước khi share.
- **US-003:** As a creator có CCCD khớp với Scalef, I want to flow tự động pass qua matching so that không phải làm thêm bước nào.
- **US-004:** As a creator có CCCD khác Scalef, I want to thấy reject screen rõ ràng so that biết mình không phải user của Scalef đó.
- **US-005:** As a creator đã link Scalef khác, I want to bị chặn ngay lập tức + thông báo rõ so that không vào loop confusion.

### EPIC-002 stories

- **US-006:** As a creator có SĐT lệch giữa 2 bên, I want to chọn giữ SĐT bên nào so that quyết định được số nào là chính.
- **US-007:** As a creator chọn SĐT mới từ Scalef, I want to verify OTP về SĐT mới đó so that confirm tôi sở hữu số đó.
- **US-008:** As a creator có Email Gen-Green nhưng Scalef trống, I want to auto-fill từ Gen-Green sang Scalef so that không phải nhập lại.
- **US-009:** As a creator có SĐT mới đã thuộc user Gen-Green khác, I want to thấy reject + suggest support so that biết cách xử lý.
- **US-010:** As BE dev, I want to update profile saga có rollback so that không lệch data khi 1 bên fail.

### EPIC-003 stories

- **US-011:** As a creator vừa link xong, I want to thấy màn "Liên kết thành công" + nút bắt đầu kiếm hoa hồng so that biết tiếp theo làm gì.
- **US-012:** As a creator bị reject, I want to bấm "Gửi yêu cầu hỗ trợ" auto-tạo ticket so that không phải nhập lại thông tin.
- **US-013:** As a creator refresh browser giữa flow, I want to resume từ bước đang dở so that không phải làm lại từ đầu.
- **US-014:** As an admin, I want to xem `scalef_link_history` của user so that truy vết khi có dispute.

### EPIC-004 stories (Should/Could Have)

- **US-015:** As a publisher Scalef hiện có, I want to bấm "Liên kết Gen-Green" từ Scalef portal so that không phải tự đăng ký Gen-Green.
- **US-016:** As an admin, I want to upload CSV batch tạo Gen-Green account cho 1K publisher Scalef so that migration nhanh.

---

## User Personas

| Persona | Mô tả | Nhu cầu |
|---------|-------|---------|
| **Creator Gen-Green** | Đã có account Gen-Green, chưa biết Scalef. Đa số creator base. | Linking nhanh, ít bước, hiểu data nào share. |
| **Publisher Scalef legacy** | Đã có Scalef (~1K), chưa có Gen-Green | Path vào Gen-Green dễ dàng (reverse linking hoặc batch tạo) |
| **CBNV Vingroup** | Cán bộ nhân viên Vingroup được kích hoạt affiliate đầu tiên | Tin tưởng, làm theo hướng dẫn. Không dễ confused. |
| **Admin Gen-Green** | Quản lý nền tảng | Xem history, xử lý ticket reject, batch migration |

---

## User Flows

### Flow 1: Happy path — Tất cả khớp (3 bước, ~30s)

```
Creator bấm "Liên kết Scalef" từ Settings
  → Màn consent → Đồng ý
  → Sang SSO Scalef → Login bằng tài khoản Scalef
  → Return Gen-Green với code + state
  → BE verify state, exchange code → token, lấy user info
  → Check 1-1 PASS, CCCD khớp, SĐT khớp, Email khớp
  → Skip màn so khớp + lựa chọn (auto)
  → Update users: scalef_user_id + scalef_linked_at
  → Màn "Liên kết thành công 🎉" + nút "Bắt đầu kiếm hoa hồng"
```

### Flow 2: Conflict — SĐT lệch, chọn Scalef + OTP (5 bước, ~2 phút)

```
... (giống Flow 1 đến callback) ...
  → CCCD khớp ✓, SĐT lệch (GG: +84912345678, SF: +84987654321)
  → Màn so khớp hiển thị badge Lệch SĐT
  → Màn lựa chọn: 2 card SĐT
  → User chọn SĐT Scalef (+84987654321)
  → OTP gửi về +84987654321
  → User nhập OTP → verify pass
  → Check unique: +84987654321 chưa thuộc GG user khác
  → Saga: update GG (phone: +84987654321) → Scalef profile (no change vì source là Scalef)
  → Audit log
  → Màn "Liên kết thành công"
```

### Flow 3: Reject — CCCD khác

```
... (callback) ...
  → CCCD GG: 012345678901, CCCD SF: 999999999999
  → Reject screen: "Thông tin CCCD không khớp giữa 2 tài khoản"
  → Nút "Gửi yêu cầu hỗ trợ" → auto-ticket {GG_ID, SF_ID, lý do, timestamp}
  → User thấy "Đã gửi yêu cầu, hẹn phản hồi 3 ngày"
```

### Flow 4: Resume — Refresh browser giữa OTP

```
User đang ở màn OTP (step=awaiting_otp), refresh browser
  → FE detect /lien-ket-scalef path → fetch pending state từ BE
  → BE check pending_scalef_link còn TTL → trả snapshot + step
  → FE render lại màn OTP với SĐT/Email cần verify
  → User nhập OTP tiếp → continue normal
```

### Flow 5: Reverse — Publisher Scalef link Gen-Green

```
Publisher Scalef đã có account, chưa có Gen-Green
  → Bấm "Liên kết Gen-Green" trên Scalef portal
  → OAuth Gen-Green SSO → publisher chưa có Gen-Green
  → Redirect đăng ký Gen-Green → tạo account mới với data Scalef pre-fill
  → Sau đăng ký → auto-link
  → Màn "Liên kết thành công"
```

---

## Dependencies

### Internal Dependencies

- **Gen-Green auth + session framework** (existing)
- **OTP service** (existing — `internal/service/otp.go`)
- **Telegram notification module** (existing — `internal/module/telegram/`)
- **User model** — thêm 3 fields (`scalef_user_id`, `scalef_linked_at`, `scalef_link_method`)
- **Audit framework** (existing — `internal/service/audit.go`)
- **MongoDB** — 2 collection mới (`pending_scalef_link`, `scalef_link_history`)
- **Redis** — store OAuth state với TTL 15 phút
- **Phase 2 FE Creator** — depend FR-011 unlock

### External Dependencies

- **Scalef SSO OAuth** theo spec [scalef-api.md](scalef-api.md) section 0:
  - `GET /oauth/authorize`
  - `POST /oauth/token`
  - `POST /oauth/social-token` (optional, cho social grant)
  - `GET /user/me` (nếu cần CCCD)
- **Scalef profile update API** — `PUT /users/{id}/profile` (CHƯA confirm — Open Question)
- **Scalef sandbox/staging** — test E2E
- **Scalef credentials** — `client_id` + `client_secret` cho Gen-Green tenant

---

## Assumptions

1. **Scalef SSO đã production** — OAuth Authorization Code flow đã verified ở Scalef.
2. **Scalef có CCCD trên user profile** — nếu không có → Gen-Green skip CCCD check (chỉ dùng SĐT/Email fallback). Cần Scalef confirm.
3. **Scalef hỗ trợ profile update API** — `PUT /users/{id}/profile` — CHƯA confirm.
4. **Scalef sắp chặn đăng ký mới** → batch migration cần làm trước thời điểm đó (FR-016).
5. **Creator base biết Scalef là gì** hoặc onboarding Phase 2 sẽ giải thích.
6. **Mobile chiếm ≥ 70%** creator base.
7. **CBNV Vingroup là user đầu tiên** ("đánh từ trong đánh ra") — internal trust cao, dễ test E2E.
8. **CCCD format VN** (12 số, có thể có bản 9 số CMND cũ).

---

## Out of Scope

> Áp dụng nguyên tắc: scope V1 chỉ làm những gì critical cho linking flow. Các chức năng nâng cao defer V2+.

| Feature | Lý do | Phase |
|---------|-------|-------|
| Affiliate dashboard / commission / generate link | Phase 2 (FE Creator) — depend Phase 1 done | Phase 2 |
| Withdraw hoa hồng affiliate | Phase 3 (gộp với cashflow) | Phase 3 |
| Hợp nhất tài khoản (Vin Creator Portal — 1 cửa đăng nhập) | Phase 3 | Phase 3 |
| Bỏ auth riêng Scalef (Scalef tắt portal riêng) | Phase 3 | Phase 3 |
| Admin gỡ liên kết tự động (auto-unlink) | Out of scope V1 — chỉ admin manual gỡ qua tool riêng | Future |
| User tự gỡ liên kết | Out of scope — chỉ admin gỡ được (data history protection) | Future |
| Multiple Scalef accounts per Gen-Green | Out of scope — strict 1-1 | Forever |
| Tên pháp lý conflict resolution UI | High-risk field — admin review only (FR-017) | V2 |
| MST (mã số thuế) update | High-risk — admin review only | V2 |
| Magic link Email verification (thay OTP email) | V1 dùng OTP code email cho consistent UX. Magic link có thể V2. | V2 |

---

## Open Questions

> **⚠️ Phải làm việc với Scalef dev team để clear trước khi kick-off implementation.**

### Cần Scalef dev clear

1. **Scalef SSO trả CCCD trong response không?**
   - Hiện tại `/oauth/token` response trả `user_id, user_name, phone, email` — KHÔNG có CCCD.
   - **Cần biết:** Có thể bổ sung CCCD vào response token / `/user/me` không? Hay Gen-Green phải skip CCCD check?
   - **Tác động:** Nếu không có CCCD → FR-005 chỉ dùng SĐT/Email fallback → giảm độ chắc chắn identity.

2. **Scalef profile update API:**
   - `PUT /users/{id}/profile` đã có chưa? Authorize bằng access_token user hay system token?
   - Validate field nào? Có rate limit không?
   - **Tác động:** FR-010 bidirectional update phụ thuộc 100% vào API này.

3. **Reverse linking (FR-015):**
   - Scalef có entry point trên portal để publisher bấm "Liên kết Gen-Green" không?
   - Gen-Green có cần expose SSO endpoint riêng cho Scalef gọi không?

4. **Scalef rate limit OAuth:**
   - Limit token exchange / phút?
   - Limit user info fetch?

5. **`client_id` cho Gen-Green tenant:**
   - Scalef cấp khi nào? Staging credentials đã sẵn sàng?

### Cần internal Gen-Green clear

6. **Migration legacy strategy (FR-016):**
   - Timeline Scalef chặn đăng ký mới — sprint nào? Cần biết để prioritize FR-016.
   - 1K publisher đó hiện hoạt động active hay đa số inactive?

7. **Tên pháp lý conflict (FR-017 high-risk):**
   - Khi tên 2 bên khác Unicode vs ASCII (VD: "Hùng" vs "Hung") → reject hay route admin?
   - Currently PRD: route admin. Confirm với product?

8. **CCCD edge cases:**
   - `"000000000000"` test data → coi invalid?
   - CCCD 9 số (CMND cũ) → admin override only?

---

## Approval & Sign-off

### Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Product Owner | TBD | Approve scope + priorities |
| Engineering Lead (BE) | TBD | OAuth + saga + Scalef integration |
| Engineering Lead (FE) | TBD | Clone từ demo-gen-green + adapt design |
| Design Lead | TBD | Conflict resolution UX |
| QA Lead | TBD | E2E test với Scalef sandbox + 5 flows |
| Security Lead | TBD | Review OAuth flow + saga + OTP |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead (BE)
- [ ] Engineering Lead (FE)
- [ ] Design Lead
- [ ] QA Lead
- [ ] Security Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-04 | vinhnguyen | Initial PRD. Format theo BMAD template. Refactor từ PRD gốc `scalef-integration/prd-scalef-integration-v1-2026-04-12.md` (18 FRs / 6 NFRs gốc) → 18 FRs / 8 NFRs / 4 Epics. Bám Scalef SSO spec mới (OAuth Authorization Code Flow). Reference mockup demo-gen-green. Note vcreator BE hiện có 2 endpoint linking cũ (form-based) — phải làm lại theo OAuth. |

---

## Next Steps

### Phase 3: Architecture

Run `/architecture` để thiết kế chi tiết:
- Backend Go: OAuth client module, matching engine, saga orchestrator, OTP integration
- MongoDB schema: User fields, `pending_scalef_link`, `scalef_link_history`
- Redis: state storage cho CSRF
- Frontend: clone từ `demo-gen-green/src/components/steps/*` + adapt design system Gen-Green
- Integration: Scalef SSO endpoints + profile update API + sandbox setup

### Phase 4: Sprint Planning

Sau khi architecture xong + Scalef dev clear 8 open questions:
- Break 4 epics thành stories chi tiết (~22-30 stories)
- Estimate effort
- Plan sprint (~2.5 tuần effort theo overview)
- Kick-off implementation, ưu tiên EPIC-001 BE (OAuth foundation)

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | OAuth SSO + Matching | FR-001, FR-002, FR-003, FR-004, FR-005, FR-018 | 7-9 |
| EPIC-002 | Conflict Resolution | FR-006, FR-007, FR-008, FR-009, FR-010, FR-017 | 7-9 |
| EPIC-003 | Hoàn tất, Reject & State Management | FR-011, FR-012, FR-013, FR-014 | 5-7 |
| EPIC-004 | Legacy Migration | FR-015, FR-016 | 3-5 |

**Total estimated stories:** 22-30

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 14 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-017, FR-018 |
| Should Have | 3 | FR-013, FR-014, FR-015 |
| Could Have | 1 | FR-016 |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 6 | NFR-001, NFR-002, NFR-003, NFR-005, NFR-006, NFR-007, NFR-008 |
| Should Have | 1 | NFR-004 |

### MVP Scope (V1 — Must Have only)

V1 launch khi đủ:
- OAuth + matching đầy đủ (EPIC-001)
- Conflict resolution + OTP + saga (EPIC-002)
- Confirmation + reject + audit (EPIC-003 — bỏ pending state resumable nếu cần ship sớm)

**V1 effort:** ~2.5 tuần (theo overview).

### V1.5/V2 Scope (Should Have)

- FR-013 Pending state resumable
- FR-014 Audit log full
- FR-015 Reverse linking
- FR-016 Batch migration (Could Have — ưu tiên thấp)

---

## Appendix C: Data Model Reference

### User model — fields mới

| Field | Type | Mô tả |
|-------|------|-------|
| `scalef_user_id` | string, nullable | Scalef user ID (`user_id` từ OAuth response) |
| `scalef_linked_at` | datetime, nullable | Thời điểm linking thành công |
| `scalef_link_method` | enum, nullable | `oauth` / `batch` / `admin` |

### Collection: `pending_scalef_link`

| Field | Type | Mô tả |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | Gen-Green user (unique) |
| `scalef_user_id` | string | |
| `scalef_snapshot` | object | `{name, cccd, phone, email}` từ Scalef |
| `step` | enum | `consent` / `compared` / `awaiting_otp` / `awaiting_email_verify` / `committed` |
| `created_at` | datetime | |

**Indexes:**
- `user_id` unique
- TTL index trên `created_at` (15 phút)

### Collection: `scalef_link_history`

| Field | Type | Mô tả |
|-------|------|-------|
| `_id` | ObjectId | |
| `gen_green_user_id` | ObjectId | |
| `scalef_user_id` | string | |
| `action` | enum | `linked` / `unlinked` / `rejected` / `profile_updated` |
| `method` | enum | `oauth` / `batch` / `admin` |
| `reject_reason` | string, nullable | |
| `changes` | object, nullable | `{field, old_value, new_value, source}` |
| `performed_by` | ObjectId | User ID hoặc Admin ID |
| `request_id` | string | Trace ID |
| `timestamp` | datetime | |

**Indexes:**
- `(gen_green_user_id, timestamp desc)`
- `(scalef_user_id, timestamp desc)`
- `(action, timestamp desc)`

**TTL:** Vĩnh viễn (compliance)

---

## Appendix D: OAuth State + Saga State Machine

### OAuth State (CSRF protection)

Stored in Redis:
```
key: oauth_state:{user_id}
value: {state: "<random>", redirect_to: "<original_path>", created_at}
TTL: 15 phút
```

Verify: callback compare `state` query param với value Redis. Match → consume (delete) → continue. Mismatch → reject 403.

### Saga State Machine (FR-010)

```
[init] → pending_gg → pending_sf → committed
              ↓             ↓
         rolled_back ← compensating
```

| State | Mô tả | Next |
|-------|-------|------|
| `init` | Pending state created | `pending_gg` |
| `pending_gg` | Update Gen-Green local OK, đang call Scalef | `pending_sf` (Scalef OK) hoặc `rolled_back` (Scalef fail) |
| `pending_sf` | Cả 2 bên OK, đang commit | `committed` |
| `committed` | Done | (final) |
| `compensating` | Đang rollback Gen-Green | `rolled_back` |
| `rolled_back` | Done với rollback | (final) |

Background retry job: scan state `compensating` chưa kết thúc > 5 phút → retry compensate.

---

## Appendix E: Reuse từ vcreator codebase

| Component | Path | Reuse status |
|-----------|------|--------------|
| OTP service | `internal/service/otp.go` | ✅ Reuse cho FR-008 |
| User model | `internal/model/mg/user.go` | ✅ Add 3 fields, không breaking |
| Audit framework | `internal/service/audit.go` | ✅ Reuse cho FR-014 / NFR-006 |
| Telegram bot | `internal/module/telegram/` | ✅ Reuse cho admin alerts (saga fail, reject ticket) |
| Pub_BE HMAC client | `internal/module/pub_be/` | ⚠️ Format HMAC khác (4-part vs Pub2 3-part) — KHÔNG reuse cho Scalef OAuth, cần tạo module riêng `internal/module/scalef/` |
| Existing linking endpoints | `pkg/public/router/user.go:55-56` | ⚠️ KHÔNG reuse — flow form-based khác hẳn OAuth. Mark deprecated, kept 1 release cho backward compat. |
| Auth + session framework | `pkg/public/router/routeauth/` | ✅ Reuse |
| MinIO storage | `internal/module/minio/` | Không liên quan linking |

### vcreator BE cần build mới

- `internal/module/scalef/oauth.go` — OAuth client (authorize URL builder, token exchange, user info fetch)
- `internal/module/scalef/profile.go` — Scalef profile update API client
- `internal/service/scalef_linking.go` — Matching engine + saga orchestrator
- `pkg/public/handler/scalef_linking.go` — Public handlers (initiate, callback, consent, resolve, otp, confirm)
- `pkg/public/router/scalef_linking.go` — Routes
- 2 collection mới: `pending_scalef_link`, `scalef_link_history`
- Migration script: User schema add 3 fields
