# PRD: Đăng ký và Phân nhóm Tài khoản — V2 (Employee Registry & Import)

**Project:** Gen-Green Registration & Account Grouping
**Date:** 2026-04-12 → rewritten 2026-04-25 reflecting shipped code
**Version:** 2.3 (post-implementation, branch `hotfix/group-users`)
**Status:** ✅ Implemented — đợt 1 + 2 + 3 done
**Prerequisite:** [PRD V1](prd-registration-v1-2026-04-12.md) đã go-live
**File mẫu HR:** [VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx)
**File test 2-step:** [step1-initial](sample-import-step1-initial.xlsx) · [step2-mixed](sample-import-step2-mixed.xlsx)

> **PRD này** mô tả V2 đã ship — không phải spec dự định ban đầu. Đối chiếu với code thực tế trong `accesstrade-projects/vcreator/`.
> **Audience:** Dev, QA, PM, HR Vin (đọc Section 2-4 đủ hiểu chức năng).
> **Non-tech overview:** [overview-v2-import-logic.md](overview-v2-import-logic.md).

---

## 1. Executive Summary

V2 xây Employee Registry + Import Pipeline trên nền V1 (user popup khai mã NV, admin verify manual). Mục tiêu:

1. Tạo "nguồn sự thật" về danh sách nhân viên từ HR Vin
2. Auto-match user Gen-Green vs file HR → giảm verify thủ công
3. Quản lý lifecycle: điều chuyển, nghỉ việc, grace period
4. Audit trail đầy đủ cho mọi thao tác

**Outcome:** Admin upload file Excel → preview 9 actions → bấm Apply → user được verify/reject/transferred + cron daily xử lý nghỉ việc sau 7 ngày grace period.

---

## 2. Architecture Overview

### 2.1 Data Model (3 collections)

| Collection | Mục đích |
|-----------|---------|
| `employee-registries` | Danh sách nhân viên chính thức từ HR (master data) |
| `import-histories` | Mỗi đợt upload file = 1 record với status, counters, file metadata |
| `import-changes` | Per-row action (preview/applied/cancelled/rolled_back) cho audit + rollback |

### 2.2 Tech Stack

- **Backend:** Go 1.24, Echo, MongoDB (driver v1.x), `xuri/excelize/v2`, `redsync/v4`, `robfig/cron/v3`
- **Admin:** React + DVA + Umi 3.5.20 + Ant Design Pro
- **Storage:** MinIO bucket `PrivateFile` với prefix `employee-registry-imports/`
- **Cron:** Daily 00:00 (staff removal) + 01:00 (TTL cleanup preview 24h)

### 2.3 9 Action Types

```
┌──────────────────────┬───────┬──────────┬──────────────────────────────┐
│ Action               │ Color │ Priority │ Behavior                      │
├──────────────────────┼───────┼──────────┼──────────────────────────────┤
│ cancelled_mismatch   │ 🔴 Red │ 1        │ Reject user, clear staff fields│
│ transferred          │ 🟠 Org │ 2        │ Update workplace, giữ verified│
│ registry_updated     │ 🔵 Blu │ 3        │ Update registry phone/workplace (HR đính chính, chưa user claim) │
│ missing_from_file    │ 🟠 Org │ 4        │ Schedule removal +7d (opt)   │
│ auto_verified        │ 🟡 Ylw │ 5        │ Set verified, link registry  │
│ new_record           │ 🟢 Grn │ 6        │ Insert registry mới           │
│ no_match             │ ⚪ Gry │ 7        │ Insert registry (fallback)    │
│ unchanged            │ ⚪ Gry │ 8        │ No-op                         │
│ invalid              │ ⚫ Blk │ 9        │ Skip khi apply                │
└──────────────────────┴───────┴──────────┴──────────────────────────────┘
```

Logic match chi tiết → [overview-v2-import-logic.md §3](overview-v2-import-logic.md).

---

## 3. Functional Requirements (đã ship)

### EPIC 1 — Employee Registry CRUD

#### FR-001: Bảng Employee Registry ✅
- Schema: `employeeCode` (unique index), `fullName`, `phone` (normalized), `workplaceName`, `workplaceGroup`, `status` enum, `genGreenUserId`, `importedAt`, `importId`, `lastSeenImportId`
- Phone luôn normalize về `0xxxxxxxxx`
- Phone DB cũ vẫn match được (variants `0xxx` / `xxx` / `+84xxx`)

#### FR-002: Admin xem danh sách registry ✅
- **Endpoint:** `GET /v1/admin/employee-registry?page=&pageSize=&q=&workplace=&status=&matched=`
- **Page:** `/employee-registry` — filter dropdown, search, pagination, button "Import Excel" + "Lịch sử import"
- DVA model `employeeRegistryModel`

### EPIC 2 — Import Pipeline

#### FR-003: Upload + Parse + Validate Excel ✅
- **Endpoint:** `POST /v1/admin/employee-registry/import` (multipart, field `file` + `detectMissing`)
- File size ≤10MB, ext `.xlsx` only (server-side validate)
- Parser layout-aware: skip leading empty rows + header (chứa "STT"/"Họ tên") + VD row + metadata row
- Column offset auto-detect (cột STT có thể ở A hoặc B tuỳ template)
- Validation per cell:
  - STT: 5 chữ số
  - Họ tên: required, soft warning nếu chữ cái đầu không in hoa
  - SĐT: normalize qua util.NormalizePhone, must `0xxxxxxxxx` 10 số
  - Đơn vị: required (đợt sau validate theo workplace-units master)
  - Mã NV: required, **chấp nhận mọi format**
  - Duplicate empCode trong file → flag dòng sau
- Errors aggregate, không fail-fast
- Errors persist thành `ImportChangeRaw{action:invalid, phase:preview, reason:"[CODE] message"}` để admin xem trong preview

#### FR-004: Dry-run Preview với full table ✅
- **Endpoint:** `GET /v1/admin/employee-registry/imports/:importId/preview?action[]=&workplace=&q=&page=&pageSize=&sortByPriority=`
- **Page:** `/employee-registry/imports/:importId/preview`
- UI compact: counter pills inline (không cards) + filter dropdown + 9-column table
- Sort default theo priority (impact descending)
- Buttons trên top bar: **Hủy** / **Apply** (di chuyển từ footer lên đầu)
- Snapshot mode khi status ≠ preview: ẩn Apply, badge status

#### FR-005: Async Processing >1000 Rows ✅
- File >1000 rows → spawn goroutine với `redsync.Mutex` lock 30 phút theo `importId`
- Status: `processing` → `preview` (success) hoặc `failed`
- UI poll `GET /imports/:importId/status` mỗi 3s, hiển thị Progress bar
- `processedRows = totalRows` khi done (jump 0%→100%, không real progress per batch)
- Panic recovery → set status=failed

#### FR-006: Rollback Import ✅
- **Endpoint:** `POST /v1/admin/employee-registry/imports/:importId/rollback`
- Điều kiện: status = `completed` hoặc `completed_with_errors`
- Revert mọi changes của importId qua `oldValue`/`newValue` đã lưu
- Update status = `rolled_back`, đổi phase = `rolled_back`
- ⚠️ Warning trong UI: rollback có thể overwrite user-modified profile sau apply

#### FR-018: Cancel Preview (mới — không có trong PRD ban đầu) ✅
- **Endpoint:** `POST /v1/admin/employee-registry/imports/:importId/cancel`
- Điều kiện: status = `preview`
- Set status = `cancelled`, đổi phase = `cancelled`
- Records giữ lại làm audit trail
- UI: button "Hủy" → confirm dialog → call API → redirect `/imports`

### EPIC 3 — Match Engine

#### FR-007: Phone Normalize Util ✅
- `util.NormalizePhone(raw) (string, error)`
- Strip whitespace, dash, plus, parens
- Strip prefix `+84` / `84` (11 ký tự) → leading `0`
- Validate `^0\d{9}$` 10 chữ số
- Test: 17 cases pass

#### FR-008: Match Engine + Bulk Query ✅
- `MatchEngine.GenerateChanges(ctx, parseRows, importID)` build per-row action
- 2 bulk queries:
  - `EmployeeRegistryDAO.Find(employeeCode IN [codes])` → hash map
  - `UserDAO.Find(phone.number IN [variants])` với 3 variants per parser phone
- In-memory match → ~200ms cho 1000 rows
- Logic 4 case (đã fix bug ngữ nghĩa `no_match` lúc test):
  - `!hasReg && !hasUser` → new_record
  - `!hasReg && hasUser`:
    - code+phone khớp → **auto_verified** (registry sẽ insert)
    - phone khớp, code khác → cancelled_mismatch (code_mismatch)
    - code khớp, phone khác → cancelled_mismatch (phone_mismatch)
    - cả khác → new_record
  - `hasReg && !hasUser`:
    - phone & workplace registry khớp file → unchanged
    - phone hoặc workplace khác file → **registry_updated** (HR đính chính cho mã NV chưa user claim, apply sẽ update registry data)
  - `hasReg && hasUser` → auto_verified hoặc transferred (workplace) hoặc cancelled_mismatch

#### FR-009: Register Hook (FR-009) ✅
- `MatchEngine.LookupSingle(ctx, empCode, phone)` được gọi trong `CompleteProfile` (public service)
- 3 kịch bản A/B/C:
  - A → `staffStatus=verified`, link genGreenUserId, push notification auto_verified
  - B → return error inline 400 "Thông tin không khớp dữ liệu HR..."
  - C → fallback `staffStatus=pending`
- Graceful degrade nếu LookupSingle fail (network, DB) → fallback pending, không block user register

#### FR-010: Apply Trigger ✅
- **Endpoint:** `POST /v1/admin/employee-registry/imports/:importId/apply` (body `{confirmTerminate: bool}`)
- Atomic state machine: `FindOneAndUpdate{status:"preview" → "processing"}` để chống concurrent apply
- Loop từng change phase=preview → gọi V1 API tương ứng:
  - `auto_verified` → `userService.VerifyStaff(action="verify", actor=root)`
  - `cancelled_mismatch` → `userService.VerifyStaff(action="reject", reason, actor=root)`
  - `transferred` → `userService.UpdateWorkplace(actor=root)` (build mới Phase F.2)
  - `registry_updated` → `EmployeeRegistryDAO.UpdateOne` (update phone/workplaceName từ file mới, không động user)
  - `missing_from_file` → `userService.ScheduleStaffRemoval(scheduledAt=now+7d)` **chỉ khi confirmTerminate=true**, ngược lại skip
  - `new_record` → `EmployeeRegistryDAO.InsertOne`
  - `no_match`, `unchanged` → no-op
  - `invalid` → skip
- Đổi phase: preview → applied
- Update `import_history.status=completed`
- Notification push qua `internalservice.Notification().Push()` async goroutine

### EPIC 4 — Lifecycle Management

#### FR-011: Transferred Detection ✅
- Wired trong MatchEngine `buildChange` → so workplace user vs row file
- Apply qua `UpdateWorkplace` API (mới)

#### FR-012: Missing from File với 2-Layer Confirm ✅
- **Layer 1 — Toggle "Rà soát nghỉ việc" lúc upload:** Default OFF (delta mode). Bật khi full-dump tháng.
  - `CreateImportInput.DetectMissing bool` → chỉ chạy `detectMissingFromFile` khi true
  - Frontend Checkbox với hint "Bật khi file đầy đủ tháng. Tắt nếu file delta"
- **Layer 2 — Checkbox confirm trong preview:** Hiện khi `missingFromFile > 0`. Admin tick = lên lịch terminate, không tick = skip records này khi apply.
- **Case orphan registry (post-ship fix):** Apply `missing_from_file` cho record không có user claim (`genGreenUserId=null`) → terminate registry record NGAY (không qua grace period vì không có user để gỡ tag). Tránh loop missing flag ở các import sau khi orphan record không bao giờ được terminate.

#### FR-013: Grace Period 7 Ngày ✅
- `UserRaw.StaffRemovalScheduledAt *time.Time` field
- Constant `StaffStatusPendingRemoval = "pending_removal"`
- Cron scan `staffRemovalScheduledAt < now() AND staffStatus=pending_removal` → gỡ staff tag, clear workplace, account_type=creator.
- **Cron schedule + grace period configurable qua env (post-ship):**
  - `STAFF_REMOVAL_CRON` (default `0 0 8 * * *` — daily 08:00 VN, tránh 00:00 khó debug)
  - `STAFF_REMOVAL_GRACE_PERIOD` (default `168h` = 7 ngày). Dev có thể set `2m`/`5m` để test nhanh.
- **Cron auto-terminate registry (post-ship fix):** Khi cron gỡ staff tag user, đồng thời terminate các registry record link với user đó (`genGreenUserId=userID + status=active` → `status=terminated` + unset `genGreenUserId`). Tránh stale "Đã khớp" badge ở admin UI cho user đã chuyển về creator.
- File: `pkg/admin/service/staff_removal_cron.go` + register trong `pkg/admin/schedule/init.go` (đọc env config).

#### FR-014: Notification Wire-up ✅
- 5 constants mới trong `internal/constants/notification.go`:
  - `NotificationTypeAutoVerified`
  - `NotificationTypeCancelledMismatch`
  - `NotificationTypeWorkplaceUpdated`
  - `NotificationTypeStaffRemovedScheduled`
  - `NotificationTypeStaffRemoved`
- Helper `pushImportNotification` trong `employee_registry_apply.go` (async goroutine, pattern V1)
- Wire vào 4 action successful: auto_verified, cancelled_mismatch (reason), workplace_updated (newValue=brandCode), staff_removed_scheduled

### EPIC 5 — Audit & History

#### FR-015: Import History List + Detail ✅
- **Endpoint:** `GET /v1/admin/employee-registry/imports?page=&pageSize=&status=&dateFrom=&dateTo=`
- **Page:** `/employee-registry/imports` — table list + button Rollback inline
- **Page detail:** click vào import → `/imports/:importId/preview` (snapshot mode nếu đã apply/cancel)
- Breadcrumb 2-level: `Danh sách nhân viên › Lịch sử import`
- Button "Import Excel" trong header → mở UploadModal

#### FR-016: Audit ActorType ✅
- `AuditRaw.ActorType string` field (V1 refactor)
- Constants: `human_admin` | `root_account` | `user_self`
- `internalservice.Staff().GetRoot(ctx)` helper wrap query `bson.M{"isRoot":true}`
- `VerifyStaff(..., actor *StaffInfo)` accept optional actor, nil → fallback root
- Refactor `opshub_webhook.go:161` dùng helper

#### FR-017: Block Concurrent Import (mới) ✅
- `findPendingImport(ctx)` query `status IN [preview, processing]`
- Nếu found → CreateImport return `ErrPendingImportExists` → handler trả 409 với code `PENDING_IMPORT_EXISTS`
- Message: "Đã có 1 đợt import chưa hoàn tất. Vui lòng Apply hoặc Hủy đợt đó trước khi tạo đợt mới."

---

## 4. UI/UX Decisions (đã ship)

### 4.1 Upload Modal
- File picker `.xlsx` only, max 10MB, validate `beforeUpload`
- Checkbox "Rà soát nhân viên nghỉ việc" với hint dài
- Async path: progress bar + polling 3s + redirect preview khi done
- Sync path: redirect ngay sang preview (kể cả có errors → admin xem chi tiết qua filter)
- KHÔNG hiển thị errors trong modal nữa (trước đây block, giờ luôn redirect preview)

### 4.2 Preview Page Layout
```
[Breadcrumb: Danh sách NV › Lịch sử import › Preview <8-char>]  [← Quay lại]
[(Top bar) Hủy | Apply (N thay đổi) | Status text]
[Counter pills: Tổng | Xung đột:1 | Điều chuyển:2 | Nghi ngờ:3 | Tự xác minh:5 | Thêm mới:4 | Không khớp:0 | Không đổi:2 | Lỗi format:4]
[Filter: action multi-select | workplace | search]
[Table 9 cột — pagination 50/page]
```

- Counter cards cũ (8 boxes lớn) → **đã refactor thành text inline** (compact)
- Apply/Hủy chuyển từ footer lên top bar
- Snapshot mode khi status ≠ preview: ẩn Apply, badge "✓ Đã áp dụng" / "⊘ Đã hủy" / "↺ Đã rollback" / "✕ Thất bại"
- Apply confirm modal liệt kê chi tiết action sẽ chạy, đặc biệt nếu skip missing thì show "BỎ QUA N nhân viên"
- Hủy preview → confirm dialog → status=cancelled

### 4.3 Header Pattern Pages
- Trang chính `/employee-registry`: button "Lịch sử import" + "Import Excel"
- Trang `/employee-registry/imports`: button "Quay lại" + "Import Excel" (cùng UploadModal)
- Sidebar menu: chỉ "Danh sách nhân viên" (Lịch sử import ẩn, vào qua button)

---

## 5. Non-Functional Requirements (đã verify)

### NFR-001: Performance
- Bulk match 1000 rows: 2 queries + in-memory hash → ~200ms
- Preview API: `aggregateCounters` + paginated find ≤300ms
- Async processing: file 10k rows ~5 phút (redsync TTL 30 phút buffer)

### NFR-002: Reliability — Atomicity
- Apply per-record commit (1 user fail không block khác)
- Failed records logged riêng, success records persist
- `FindOneAndUpdate` atomic chống concurrent apply

### NFR-003: Security
- Admin endpoint: `RequiredLogin + IsRoot` middleware
- File upload: ext `.xlsx` only, size ≤10MB, MinIO key randomized (no path traversal)
- Excel XXE: excelize/v2 v2.8+ disable external entity
- Error messages: generic cho client, log chi tiết server-side
- BSON injection: struct binding qua bson tags, escape regex cho search

### NFR-004: Data Integrity
- File checksum SHA256 store (chưa wire dedup UI — defer)
- Import per-record audit qua `import_changes` + `actor_type`
- Idempotent operations: re-run dry-run xoá preview cũ trước insert

### NFR-005: Phone Format Consistency
- Mọi phone normalize về `0xxxxxxxxx` trước compare
- Match với 3 variants để bao quát DB legacy: `0xxx` / `xxx` / `+84xxx`

---

## 6. API Endpoints (final)

| Method | Path | Mục đích |
|--------|------|---------|
| GET | `/v1/admin/employee-registry` | List registry + filter + search |
| POST | `/v1/admin/employee-registry/import` | Upload file Excel (multipart) |
| GET | `/v1/admin/employee-registry/imports` | List import history |
| GET | `/v1/admin/employee-registry/imports/:importId/status` | Poll status async |
| GET | `/v1/admin/employee-registry/imports/:importId/preview` | Preview changes |
| POST | `/v1/admin/employee-registry/imports/:importId/apply` | Apply (body confirmTerminate) |
| POST | `/v1/admin/employee-registry/imports/:importId/rollback` | Rollback applied |
| POST | `/v1/admin/employee-registry/imports/:importId/cancel` | Hủy preview |

---

## 7. Files Changed (commit references)

Branch `hotfix/group-users`:

| Commit | Phase | Scope |
|--------|-------|-------|
| `3dbcf8c3` | A + B | Models + DAO + indexes + phone util + list API + admin UI scaffold + upload skeleton |
| `9524a648` | C | Excel parser + validator + modal errors |
| `c5b319a6` | D + E | Match engine + dry-run + preview API |
| `6c1f2260` | F | Apply + Rollback + UI preview/history |
| `a974a495` | G | Cron grace period + register hook + notification |
| (uncommitted) | H + bug fixes + UX | Async + Cancel + match phone variants + missing toggle + UI compact |

---

## 8. Test Workflow (2 file Excel mẫu)

### Step 1 — Upload baseline
- File: [sample-import-step1-initial.xlsx](sample-import-step1-initial.xlsx)
- 7 rows: 2 Match A + 5 baseline NV
- Toggle "Rà soát nghỉ việc": **OFF**
- Apply → registry có baseline data

### Step 2 — Mixed scenarios (cover full 9 actions)
- File: [sample-import-step2-mixed.xlsx](sample-import-step2-mixed.xlsx)
- 16 rows mix
- Toggle "Rà soát nghỉ việc": **ON** (full-dump test)
- Preview expected counters:
  - auto_verified: 2
  - cancelled_mismatch: 2
  - transferred: 2
  - new_record: 4
  - unchanged: 2
  - missing_from_file: 3 (BASE003/004/005 vắng từ file 1)
  - invalid: 4

---

## 9. Out of Scope V2 (defer V3 nếu cần)

- Multi-select workplace (kiêm nhiệm)
- HR Vin tự upload trực tiếp (không qua admin AT)
- API sync tự động từ HRIS Vin
- CCCD/email trong registry (đối tác chưa cung cấp)
- File checksum dedup warn UI
- Real-progress goroutine batched processedRows (hiện tại jump 0%→100%)
- Export preview Excel
- Rollback transactional (hiện tại per-record best-effort)
- Multi-pod safety cho cron (chưa có redsync mutex cho `RunStaffRemovalCron`)

---

## 10. Known Limitations

1. **Rollback overwrite risk:** Sau apply, nếu user thay đổi profile (vd đổi phone), rollback sẽ revert lên giá trị cũ → mất user-modified data. UI confirm dialog có warning.
2. **Missing detect false positive:** HR gửi file delta mà admin BẬT toggle → tất cả non-listed staff bị flag. Mitigated: admin có thể skip checkbox confirm → không terminate.
3. **Cron daily 00:00 timing:** Confirm terminate lúc 23:55 → grace thực tế còn 6d 5min. Acceptable.
4. **Notification spam:** 1000 rows = 1000 goroutines push notify. Chấp nhận với volume HR (1-2 lần/tháng).
5. **Multi-pod cron:** Nếu deploy multi-pod, `RunStaffRemovalCron` chạy song song trên các pod → có thể double-process. Need redsync wrap (defer V3).

---

## 11. References

- [overview-v2-import-logic.md](overview-v2-import-logic.md) — non-tech overview cho HR/PM/QA
- [overview.md](overview.md) — bối cảnh business V1+V2 tổng
- [PRD V1](prd-registration-v1-2026-04-12.md) — popup + workplace cascading + manual verify
- Plans:
  - [Đợt 1 plan](plans/20260424-2255-employee-registry-import-dot1/plan.md)
  - [Đợt 2+3 plan](plans/20260425-0038-employee-registry-v2-finish/plan.md)
