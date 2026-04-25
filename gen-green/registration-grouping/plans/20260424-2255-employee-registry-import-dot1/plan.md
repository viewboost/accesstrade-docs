# Gen-Green Employee Registry & Import — Đợt 1

**Date:** 2026-04-24 | **Branch:** `hotfix/group-users` | **Project:** `accesstrade-projects/vcreator/`
**PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) v2.2
**Scope:** Phase 0 refactor V1 + FR-001 + FR-002 + FR-003 (upload/parse/validate) + FR-007 + FR-015 (schema only)

---

## 1. Overview

Xây móng cho V2 Employee Registry & Import pipeline trong đợt 1: (1) foundations (models, DAO, indexes, util); (2) admin list API + UI khởi tạo; (3) upload Excel + parse + validate (chưa match, chưa dry-run, chưa insert registry). Đợt 1 KHÔNG touch match logic A/B/C, dry-run table, lifecycle — các phần đó đẩy đợt 2.

**Acceptance đợt 1:**
- Admin upload file Excel mẫu `VP_Mẫu danh sách trường CBNV 1.xlsx` → nhận response với `errors[]` (nếu sai format) hoặc `valid_rows_count` (nếu pass) + `import_id` ghi `status=preview`
- Admin mở page Employee Registry thấy filter/search/pagination UI với empty state (chưa insert registry rows trong đợt này)
- Phase 0 refactor KHÔNG break V1 `VerifyStaff` flow — existing handler tiếp tục gọi không truyền actor, default lấy root staff

---

## 2. Phases

### Phase A — Foundations (~6h) [x]

**File:** [phase-A-foundations.md](phase-A-foundations.md)
**Progress:** [█████████] 100% — completed 2026-04-24

- A.1 Refactor V1 `VerifyStaff` + `createAudit` accept optional `actor modelmg.StaffInfo` (~1h) — BLOCKS nothing else except regression test
- A.2 `NormalizePhone` util + unit test (`pkg/util/phone.go`) (~1h)
- A.3 Models + DAO: `EmployeeRegistryRaw`, `ImportHistoryRaw`, `ImportChangeRaw` (~3h)
- A.4 Collection consts + MongoDB indexes (~1h)

Parallel: A.2 / A.3 / A.4 file-disjoint — chạy song song 3 agents. A.1 tách agent riêng.

---

### Phase B — Registry List API + Admin UI + Upload Skeleton (~6h) [x]

**File:** [phase-B-registry-list-upload-skeleton.md](phase-B-registry-list-upload-skeleton.md)
**Progress:** [█████████] 100% — completed 2026-04-24
**Depends:** Phase A (A.3 model, A.4 collection)

- B.1 Backend `GET /v1/admin/employee-registry` list API + route + handler + service (~3h)
- B.2 Admin UI page skeleton + filter + table + service client (~3h)
- B.3 Upload handler skeleton `POST /v1/admin/employee-registry/import` (multipart, trả `import_id`) (~1h)

Parallel: B.1 và B.2 file-disjoint. B.3 tách agent, depend A.3.

---

### Phase C — Excel Parser + Validator (~4h) [x]

**File:** [phase-C-excel-parser-validator.md](phase-C-excel-parser-validator.md)
**Progress:** [█████████] 100% — completed 2026-04-24
**Depends:** Phase B (B.3 upload handler)

- C.1 Excel parser (`excelize/v2`) + row validator với aggregate errors (~2h)
- C.2 Wire parser vào upload handler, response `{import_id, total_rows, valid_rows, errors[]}` (~1h)
- C.3 Upload modal UI + error display (~1h)

Sequential: C.1 → C.2 → C.3. Parser phải xong trước khi wire vào handler.

---

## 3. Dependency Graph

```
Phase A (6h)
 ├─ A.1 (refactor V1) ──────────────► regression test V1
 ├─ A.2 (phone util)    ────┐
 ├─ A.3 (models+DAO)    ────┤─── Phase B ────► Phase C
 └─ A.4 (collection+idx)────┘
                             B.1 (list API)  ┐
                             B.2 (admin UI)  │ ─► C.1 parser ─► C.2 wire ─► C.3 modal
                             B.3 (upload skel)┘
```

---

## 4. Acceptance Criteria (đợt 1 toàn cục)

- [x] V1 regression: existing verify/reject staff flow work bình thường
- [x] Model `EmployeeRegistryRaw` + collection `employee-registries` + unique index `employeeCode`
- [x] Model `ImportHistoryRaw` + `ImportChangeRaw` + 2 collections + indexes
- [x] `NormalizePhone("+84886807963")` → `"0886807963"`; reject length ≠ 10
- [x] `GET /v1/admin/employee-registry?page=1&pageSize=20` return `{list:[], pagination:{total:0,...}}`
- [x] Admin UI `/employee-registry` render filter + empty table + menu "Danh sách nhân viên"
- [x] `POST /v1/admin/employee-registry/import` multipart upload:
  - File ≤ 10MB, `.xlsx` only
  - File > 1000 rows → 400 `{code:"FILE_TOO_LARGE", message:"File quá lớn (>1000 dòng). Vui lòng chia nhỏ — async support sẽ có ở đợt 2."}`
  - File hợp lệ → 200 `{import_id, total_rows, valid_rows, errors:[{row, column, code, message}, ...]}`
  - `import_history` được tạo với `status=preview`, `total_records`
- [x] Phase 0 tạo helper `internalservice.Staff().GetRoot(ctx)` + refactor `VerifyStaff(..., actor *modelmg.StaffInfo)` — nil actor → fallback `GetRoot()`. `opshub_webhook.go:161` cũng refactor dùng helper.
- [x] Admin UI dùng **DVA + Umi pattern** (không React hooks) — `model.ts` có `namespace`, `effects`, page dùng `connect()` từ `umi`
- [x] File Excel gốc được persist lên MinIO bucket `employee-registry-imports` (private, presigned). `import_history.file_path` lưu key.
- [x] `import_history.file_checksum` được compute SHA256 và store (không warn dedup ở đợt 1)

---

## 5. Estimate

**~16h dev time (~2 ngày).** Phase A full parallel 3 agents = 3h wall, A.1 riêng 1h → A total ~3h wall. B full parallel 2 agents = 3h wall, B.3 add 1h → B total ~4h wall. C sequential 4h. **Tổng wall-time ~11h** nếu vận hành parallel tốt.

---

## 6. Out of Scope (defer đợt 2)

- FR-004 Dry-run UI full preview table + sort + filter + Apply button
- FR-008/009/010 Auto-match 3 kịch bản A/B/C
- FR-011/012/013 Lifecycle (transferred, missing_from_file, terminate, grace period)
- FR-014 Notification khi status đổi
- FR-005 Async processing (>1000 rows). Đợt 1 reject file lớn.
- FR-006 Rollback import
- `workplace-units` validation cột D (chỉ log warning nếu không match, không reject)
- `DeriveWorkplaceGroup` util (defer vì chưa cần cho parse+validate stage)

---

## 7. Decisions (user-confirmed 2026-04-24)

1. **Mã NV**: CHẤP NHẬN HẾT. Không validate format, chỉ check required + trim whitespace. Loại bỏ warning 7 vs 8 chữ số.
2. **Validation cột D workplace** (Đơn vị thành viên): defer đợt 2. Đợt 1 chỉ trim + non-empty, không check theo `workplace-units.name`.
3. **Phone DB format user cũ**: KHÔNG migrate. Đợt 2 khi match sẽ normalize runtime cả 2 vế trước compare.
4. **Root staff helper**: Verify xong — **chưa có helper**, chỉ 1 call site raw query `bson.M{"isRoot":true}` ở [opshub_webhook.go:161](../../../../vcreator/backend/pkg/public/service/opshub_webhook.go#L161). Phase 0 **tạo helper mới** `internalservice.Staff().GetRoot(ctx) (*modelmg.StaffRaw, error)` (hoặc util tương đương), refactor call site hiện có dùng helper. Import sau này dùng chung.
5. **File checksum (NFR-004)**: Đợt 1 **chỉ compute + store** SHA256 vào `import_history.file_checksum`. Dedup warn UI đẩy đợt 2. Không đụng UI đợt 1.
6. **Persist file Excel lên MinIO**: YES. Bucket `employee-registry-imports` (private, presigned). Path lưu `import_history.file_path`. Phase B/C include bucket config + upload step.
7. **Admin UI stack**: **DVA + Umi 3.5.20** (verify qua `admin/package.json` + `admin/src/pages/user/model.ts` có `namespace` + `effects *getDetail`). Scout-01 đã sai. Phase B refactor dùng DVA model pattern (`model.ts` với `namespace`, `effects`, `reducers`; page dùng `connect()` từ `umi`).

---

## 8. Remaining Unresolved (cần đối tác confirm, không block đợt 1)

- **Format cột J validation list của file Excel đối tác** — Runtime đọc từ file hay dùng DS master DB? → Chốt đợt 2 khi làm dry-run.
- **Frequency import** (monthly full-dump hay ad-hoc delta?) — Ảnh hưởng logic detect "missing_from_file" đợt 3. → Hỏi HR Vin.
