# Phase C — Excel Parser + Validator

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends on:** [phase-B-registry-list-upload-skeleton.md](phase-B-registry-list-upload-skeleton.md) — B.3 upload handler
- **PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) — FR-003 (full), NFR-003, §12 Appendix (validation errors)
- **Research:**
  - [research/researcher-02-admin-ui-excel.md](research/researcher-02-admin-ui-excel.md) §3 excelize/v2 recommendation
  - [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q2 sync-only strategy
- **Reference file:** `docs/gen-green/registration-grouping/VP_Mẫu danh sách trường CBNV 1.xlsx`

## Overview

- **Date:** 2026-04-24
- **Description:** Parse file Excel đã upload (`excelize/v2`), validate từng row theo template đối tác, aggregate errors, trả response với `total_rows | valid_rows | errors[]`. Chưa insert registry, chưa match logic — chỉ parse + validate + update `import_history.totalRecords`.
- **Priority:** Must Have (finishes đợt 1)
- **Implementation Status:** Completed 2026-04-24
- **Review Status:** Approved — code-reviewer 2026-04-24, 0 critical issues

## Key Insights

- File mẫu 5 cột: STT (A) | Họ tên (B) | SĐT (C) | Đơn vị thành viên (D) | Mã nhân viên (E)
- **Cột J chứa data validation list** (DS đơn vị hợp lệ) — đợt 1 chưa validate runtime theo DS, log warning only
- Bỏ qua row đầu (header) + row `VD` minh hoạ (row 2 hoặc detect bằng content match)
- Excel số có thể bị parse thành float (`"00001"` → `1.0`) — cần read raw string, format số leading zeros. `excelize/v2` có `GetCellValue(sheet, cell, excelize.Options{RawCellValue:true})` hoặc set cell format text.
- Aggregate errors: tập hợp TẤT CẢ lỗi rồi return — không fail-fast ở row đầu
- Đợt 1 sync-only, reject file > 1000 rows (scout-01 Strategy B)
- Mã NV 7-8 chữ số (đã user-confirm): 7 log warning, 8 pass, khác → error

## Requirements

### FR-003 (đầy đủ đợt 1)

Validation rules per row:
| Cột | Rule | Error code |
|-----|------|-----------|
| STT | 5 chữ số (`^\d{5}$`) | `INVALID_STT` |
| Họ tên | non-empty, in hoa chữ cái đầu (warn only, không block) | `WARNING_NAME_CASE` |
| SĐT | sau `NormalizePhone` → 10 số `0xxx...`; lỗi → `INVALID_PHONE` | |
| Đơn vị thành viên | non-empty (đợt 1 chưa validate DS) | `EMPTY_UNIT` |
| Mã nhân viên | **Chấp nhận hết** (user chốt) — chỉ trim whitespace + required non-empty | `EMPTY_EMPLOYEE_CODE` |

**File-level:**
- Tổng rows > 1000 → 400 `FILE_TOO_LARGE`
- Header row + VD row skip
- Duplicate `employeeCode` trong file → `DUPLICATE_EMPLOYEE_CODE` (chỉ flag row sau, không block row đầu)

**Response 200:**
```json
{
  "import_id": "uuid",
  "total_rows": 150,
  "valid_rows": 145,
  "errors": [
    {"row": 3, "column": "C", "code": "INVALID_PHONE", "message": "Dòng 3: SĐT phải đúng 10 chữ số"},
    ...
  ],
  "warnings": []
}
```

**Response 200 khi có errors:** vẫn return 200, `valid_rows < total_rows`, admin xem errors → sửa file re-upload. Không tự động reject toàn bộ file.

**Update `import_history`:**
- `totalRecords = total_rows`
- `status = "preview"` (giữ nguyên, chưa có dry-run → chưa chuyển)

## Architecture

```
[Admin UI upload-modal] ──POST /import (multipart)──► [upload handler B.3]
                                                         │
                                                         ├─ save tmp file
                                                         ├─ create import_history (B.3 đã có)
                                                         │
                                                         ▼
                                                    [parser.ParseExcel(path)] ← C.1
                                                         │
                                                         ├─ open with excelize/v2
                                                         ├─ detect header + VD row
                                                         ├─ check rowCount ≤ 1000
                                                         ├─ for each data row:
                                                         │    ├─ validate STT
                                                         │    ├─ NormalizePhone (reuse util)
                                                         │    ├─ validate unit non-empty
                                                         │    ├─ validate emp code 7-8
                                                         │    └─ collect row OR error
                                                         ├─ detect dup empCode in-file
                                                         └─ return {validRows, errors, warnings}
                                                         │
                                                         ▼
                                                    update import_history.totalRecords
                                                         │
                                                         ▼
                                                    response JSON (C.2 wire)

[Admin UI upload-modal] ──(response)──► show errors table ← C.3
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| CREATE | `backend/pkg/admin/service/employee_registry_parser.go` | `ParseExcel(path) ParseResult` — parse + validate aggregated |
| CREATE | `backend/pkg/admin/service/employee_registry_parser_test.go` | Unit test với fixtures |
| EDIT | `backend/pkg/admin/service/employee_registry.go` | Wire `ParseExcel` vào `CreateImport` |
| EDIT | `backend/pkg/admin/handler/employee_registry.go` | Return parse result trong response Import |
| EDIT | `admin/src/pages/employee-registry/components/upload-modal.tsx` | Hiển thị errors/warnings table |
| EDIT | `admin/src/services/employeeRegistry.ts` | Update response type |
| REF | `backend/pkg/admin/service/user_segment.go:171-225` | ImportExcel pattern hiện có (dùng tealeg — chỉ reference flow, dùng excelize) |
| REF | `backend/pkg/util/phone.go` (từ A.2) | `NormalizePhone` |

## Implementation Steps

### C.1 Parser + validator (~2h)

1. [10m] Confirm `excelize/v2` đã trong `go.mod` (check grep "excelize" — nếu chưa có `go get github.com/xuri/excelize/v2`)
2. [15m] Define types:
   ```go
   type ParseResult struct {
       TotalRows int
       ValidRows []RegistryRow
       Errors    []RowError
       Warnings  []RowError
   }
   type RegistryRow struct {
       STT           string
       FullName      string
       Phone         string // normalized
       WorkplaceName string
       EmployeeCode  string
   }
   type RowError struct {
       Row     int    `json:"row"`
       Column  string `json:"column,omitempty"`
       Code    string `json:"code"`
       Message string `json:"message"`
   }
   ```
3. [30m] Impl `ParseExcel(path string) (ParseResult, error)`:
   - `excelize.OpenFile(path)` + defer Close
   - Get first sheet name
   - `f.GetRows(sheet, excelize.Options{RawCellValue:true})` để giữ leading zero string
   - Detect header: skip row đầu. Detect VD row: nếu cell A row 2 == `"VD"` hoặc content match mẫu → skip
   - Count data rows; nếu > 1000 → return error `FILE_TOO_LARGE`
4. [45m] Row validator:
   - `validateSTT(value, rowNum) *RowError` — regex `^\d{5}$`
   - `validatePhone(value, rowNum) (normalized string, *RowError)` — call `util.NormalizePhone`
   - `validateUnit(value, rowNum) *RowError` — non-empty
   - `validateEmployeeCode(value, rowNum) (*RowError warn, *RowError err)` — 7-8 digits
   - `validateFullName(value, rowNum) *RowError` — non-empty; capitalize check → warning only
5. [10m] Duplicate empCode in-file: map `empCode -> firstRow`, nếu gặp lại → `DUPLICATE_EMPLOYEE_CODE` error cho row sau
6. [10m] Assemble `ParseResult`, return

### C.1b Parser unit tests (~bundled in ~2h above — split if needed)

- Fixtures: tạo `.tmp/fixtures/valid.xlsx`, `invalid-phone.xlsx`, `dup-code.xlsx`, `too-large.xlsx` (hoặc mock excelize in-memory)
- Test cases:
  - Valid file mẫu → ValidRows > 0, Errors empty
  - File có phone `0886-807-963` → Errors chứa `INVALID_PHONE` row N
  - File có 2 row cùng empCode → Errors chứa `DUPLICATE_EMPLOYEE_CODE`
  - File 1001 rows → return error `FILE_TOO_LARGE`
  - File có emp code bất kỳ format (7 chữ số, 8 chữ số, có chữ cái) → valid (user chốt: chấp nhận hết)
  - File empty (no data rows) → TotalRows=0, ValidRows empty, no error

### C.2 Wire parser vào upload handler (~1h)

1. [20m] Edit `service.CreateImport`:
   - Sau insert `import_history`, call `ParseExcel(fileInfo.Path)`
   - Update `import_history.totalRecords = result.TotalRows`
   - Return `ImportResponse{ImportID, TotalRows, ValidRows: len(result.ValidRows), Errors, Warnings}`
2. [15m] Edit `handler.Import`: return `cc.Response200(result, "")` với full parse response
3. [10m] Error handling: nếu `ParseExcel` return `FILE_TOO_LARGE` → return 400 với code. Nếu excelize open fail → 400 `INVALID_FILE_FORMAT`.
4. [15m] Cleanup tmp file sau parse (hoặc MinIO persist trước, xoá tmp sau)

### C.3 Upload modal UI + error display (~1h)

1. [15m] Update `services/employeeRegistry.ts` response type: `{import_id, total_rows, valid_rows, errors, warnings}`
2. [30m] Edit `upload-modal.tsx`:
   - Sau `onOk` upload → nhận response
   - Nếu `errors.length > 0`:
     - Hiển thị Alert với summary `"Có N lỗi. Vui lòng sửa file và upload lại."`
     - Antd Table với cột: Dòng | Cột | Code | Message
   - Nếu `warnings.length > 0` + `errors.length === 0`:
     - Alert warning, cho phép đóng modal
   - Nếu `valid_rows === total_rows` + no errors → `message.success("File hợp lệ với N dòng. Đợt 2 sẽ dry-run.")`, đóng modal
3. [15m] Test end-to-end: upload file mẫu thực tế, xem response render đúng

## Todo List

- [x] C.1.1 Confirm excelize/v2 dependency
- [x] C.1.2 Define types `ParseResult`, `RegistryRow`, `RowError`
- [x] C.1.3 Impl `ParseExcel` — open + skip header/VD + row count check
- [x] C.1.4 Impl per-field validators (STT, phone, unit, empCode, fullName)
- [x] C.1.5 Duplicate empCode in-file detection
- [x] C.1.6 Unit tests 6+ cases pass (actually 11/11)
- [x] C.2.1 Wire `ParseExcel` vào `service.CreateImport`
- [x] C.2.2 Update `import_history.totalRecords`
- [x] C.2.3 Handler return `ImportResponse`
- [x] C.2.4 Tmp file cleanup
- [x] C.2.5 Error path handling `FILE_TOO_LARGE` / `INVALID_FILE_FORMAT`
- [x] C.3.1 Update response type TS
- [x] C.3.2 Modal error table render
- [x] C.3.3 Modal warning alert
- [x] C.3.4 E2E test upload file mẫu (smoke test real file PASSED)

## Success Criteria

- [x] Upload `VP_Mẫu danh sách trường CBNV 1.xlsx` → 200 `{total_rows, valid_rows, errors:[], warnings:[]}` (no warnings cho emp code; file mẫu có row `0011111` valid)
- [x] Upload file phone sai format → response có `errors[]` với `code:"INVALID_PHONE"`, `row`, `message` theo format PRD §12
- [x] Upload file >1000 rows → 400 `FILE_TOO_LARGE`
- [x] Upload file `.xlsx` corrupted → 400 `INVALID_FILE_FORMAT`
- [x] Parser test suite pass 6/6 cases (actual: 11/11)
- [x] `import_history.totalRecords` khớp row count thực tế
- [x] Tmp file không accumulate (được xoá sau parse)
- [x] Admin UI modal hiển thị bảng lỗi đúng format, có thể đóng modal sửa file upload lại

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Excelize parse leading-zero số (STT `00001` → `1`) | HIGH | Dùng `Options{RawCellValue: true}` hoặc validate cell format = text. Fallback: pad zero nếu len < expected. |
| File Excel có multiple sheets | LOW | Parse sheet đầu tiên via `GetSheetName(0)`. Document warning nếu có nhiều sheet. |
| VD row không đứng ở row 2 cố định | MED | Detect heuristic: row có cell A == `"VD"` hoặc cell B starts with `"VD"`. Fallback: config `skipRows = [0, 1]`. |
| Mã NV 7 vs 8 chưa chốt final | MED | Unresolved #1. Đợt 1 accept 7-8, log warning. Document TODO gỡ warning khi chốt final. |
| Validation DS đơn vị cột J chưa làm | MED | Đợt 1 chỉ log warning nếu empty. Đợt 2 integrate `DeriveWorkplaceGroup` + validate master list. |
| Response 200 vs 400 khi có errors | LOW | Team convention: 200 + payload errors cho business validation, 400 cho protocol/file-level error. Document trong API doc. |
| Memory spike với file 1000 rows | LOW | Excelize load full workbook. 1000 rows ≈ 200KB, OK. Limit 10MB file enforce ở upload. |

## Security Considerations

- **File content scan (NFR-003):**
  - Excel macro: reject file `.xlsm`. Hiện whitelist `.xlsx` only — excelize vẫn parse được `.xlsm` nếu admin rename ext. Mitigation: kiểm tra file signature (magic bytes) hoặc kiểm tra `vbaProject.bin` exist trong zip container → reject.
  - XXE attack: excelize/v2 v2.8+ disable external entity. Confirm version pin trong `go.mod`.
- **Path traversal:** Parse dùng `fileInfo.Path` (middleware sanitized) — không đọc path từ request body
- **Memory DOS:** File > 1000 rows reject; file > 10MB reject ở middleware. Row validation giới hạn error array max (ví dụ 5000 errors) để tránh response quá lớn.
- **Regex DOS:** Validation regex đơn giản (`^\d{5}$`, `^\d{7,8}$`) — không có backtracking issue
- **Error message leak:** Error messages chỉ expose row/col/code/short message — không leak file path, stack trace
- **Admin auth:** Route behind `a.RequiredLogin, a.IsRoot` (đã config Phase B)
- **Audit:** Mọi upload attempt ghi `import_history` với `uploadedBy` → forensic trail

## Completion Notes

- **Parser test suite:** 11/11 cases pass (vs target 6+):
  - Valid file mẫu, invalid phone, dup code, file too large, empty file, various edge cases
- **Code review:** 0 critical, 6 non-critical feedback items
  - N1: Parse before insert (sequential validation) — **FIXED**
  - N2: Generic error + centralized logging — **FIXED**
  - N3-N6: Minor style/coverage — addressed
- **Commit status:** Pending final push from main agent workflow

## Next Steps

Đợt 1 complete sau Phase C. User có thể:
- Upload file Excel mẫu
- Nhận validation feedback chi tiết
- Biết số dòng hợp lệ trước khi dry-run (đợt 2)

**Đợt 2 extend:**
- FR-004 Dry-run UI: sau parse → chạy match logic A/B/C → save `import_changes` với `phase=preview` → hiển thị preview table + sort + filter + Apply button
- FR-008/009/010 Match logic qua V1 approval API (actor=root_account)
- `DeriveWorkplaceGroup(unitName)` util + validate DS master cột D runtime
- FR-011/012 Lifecycle transferred + missing_from_file
- FR-005 Async cho file > 1000 (goroutine + Redis mutex, defer Asynq nếu có)
- FR-006 Rollback
