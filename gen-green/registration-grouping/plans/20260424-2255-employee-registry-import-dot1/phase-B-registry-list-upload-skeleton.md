# Phase B — Registry List API + Admin UI + Upload Skeleton

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends on:** [phase-A-foundations.md](phase-A-foundations.md) — A.3 models + A.4 collection
- **PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) — FR-002, FR-003 (upload skeleton only), NFR-003
- **Research:**
  - [research/researcher-02-admin-ui-excel.md](research/researcher-02-admin-ui-excel.md) §1 admin pattern, §2 upload modal
  - [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q3 route/handler, §Q5 admin UI routing

## Overview

- **Date:** 2026-04-24
- **Description:** List API `GET /v1/admin/employee-registry` + Admin page skeleton (filter/table/pagination) + Upload endpoint skeleton (multipart, validate file, tạo `import_history` record). Chưa parse Excel ở phase này.
- **Priority:** Must Have (block C)
- **Implementation Status:** Completed 2026-04-24
- **Review Status:** Approved 2026-04-24

## Key Insights

- Route register pattern: thêm `employeeRegistry(r)` vào `router.go:9-43` + tạo file `router/employee_registry.go`. Auth middleware `a.RequiredLogin, a.IsRoot`.
- Handler pattern: struct với factory func `EmployeeRegistries() EmployeeRegistryHandler{}` — service method nhận `staffInfo` từ context
- Admin UI: **DVA + Umi 3.5.20** (verify `admin/package.json:64,96` + `admin/src/pages/user/model.ts` có `namespace`, `effects *getDetail` generator syntax). Reuse pattern từ `pages/user/` — tạo `model.ts` DVA + page dùng `connect()` từ `umi`
- Upload middleware `internal/echo/upload_file.go:UploadSingle` đã handle multipart + save tmp + ext/size validate → **reuse**
- Upload handler skeleton **không parse** — chỉ: validate file, compute SHA256 checksum (store only, **KHÔNG dedup warn** ở đợt 1 — defer UI đợt 2), push MinIO bucket `employee-registry-imports` (private, presigned), tạo `ImportHistoryRaw{status:preview}`, return `import_id`
- Parse + validate sẽ làm ở Phase C

## Requirements

### FR-002 Admin list registry
- `GET /v1/admin/employee-registry?page=1&pageSize=20&q=&workplace=&status=&matched=`
- Response: `{list: [...], pagination: {total, page, pageSize}}`
- Filter: `workplaceName` (contains), `status` enum, `matched` bool (genGreenUserId != null)
- Search `q`: regex match trên `employeeCode | fullName | phone`

### FR-003 Upload skeleton
- `POST /v1/admin/employee-registry/import` multipart `file` field
- Validate: `.xlsx` only, size ≤ 10MB, non-empty
- File > 1000 rows (estimate qua rowCount hoặc defer qua Phase C) → phase này chưa check rows, Phase C wire check
- Create `ImportHistoryRaw`: `fileName`, `fileChecksum` (SHA256, **store only, không warn dedup đợt 1**), `filePath` (MinIO path), `uploadedBy` (staff ID from ctx), `timestamp`, `status="preview"`, `totalRecords=0` (update ở Phase C)
- Response: `{import_id, file_name}` — 200 OK

### Admin UI
- Page `/employee-registry` (menu "Danh sách nhân viên")
- Filter bar: search input + workplace select + status dropdown + matched toggle
- Table columns: Mã NV | Họ tên | SĐT | Đơn vị | Status | Matched User (link hoặc "—")
- Pagination footer
- Button "Import Excel" → mở modal upload (modal skeleton, logic thực ở Phase C)

## Architecture

```
[Admin UI] ─── GET /v1/admin/employee-registry ──► [list API]
                                                    ├─ service.GetList(ctx, query)
                                                    │   └─ EmployeeRegistryDAO.Find(filter).Paginate()
                                                    └─ return {list, pagination}

[Admin UI] ─── POST /v1/admin/employee-registry/import (multipart) ──► [upload skel]
                                                    ├─ middleware UploadSingle (ext/size validate, save tmp)
                                                    ├─ compute SHA256 checksum (store only)
                                                    ├─ PutObject MinIO bucket "employee-registry-imports" (private, presigned)
                                                    ├─ ImportHistoryDAO.Insert({status:preview, ...})
                                                    └─ return {import_id}
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| CREATE | `backend/pkg/admin/router/employee_registry.go` | Register routes GET list + POST import |
| CREATE | `backend/pkg/admin/handler/employee_registry.go` | HTTP handlers `GetList`, `Import` |
| CREATE | `backend/pkg/admin/service/employee_registry.go` | Business logic `GetList`, `CreateImport` (skeleton) |
| EDIT | `backend/pkg/admin/router/router.go` | Thêm dòng `employeeRegistry(r)` |
| CREATE | `admin/src/pages/employee-registry/index.tsx` | Main page component |
| CREATE | `admin/src/pages/employee-registry/components/filter.tsx` | Filter bar |
| CREATE | `admin/src/pages/employee-registry/components/table.tsx` | Registry table |
| CREATE | `admin/src/pages/employee-registry/components/upload-modal.tsx` | Upload modal skeleton |
| CREATE | `admin/src/services/employeeRegistry.ts` | API client |
| EDIT | `admin/config/routes.ts` | Register route `/employee-registry` |
| EDIT | `admin/src/locales/vi-VN/menu.ts` | Menu i18n key |
| REF | `backend/pkg/admin/router/workplace.go:11-51` | Route template |
| REF | `backend/pkg/admin/handler/workplace.go` | Handler template |
| REF | `backend/internal/echo/upload_file.go` | Upload middleware |
| REF | `admin/src/pages/user/` | List page template |
| REF | `admin/src/pages/segment/detail/components/tabs/user/components/modal-import.tsx` | Upload modal template |

## Implementation Steps

### B.1 Backend list API (~3h)

1. [20m] Đọc `pkg/admin/router/workplace.go`, `pkg/admin/handler/workplace.go`, `pkg/admin/service/workplace.go` làm template
2. [30m] Tạo `pkg/admin/service/employee_registry.go`:
   ```go
   type EmployeeRegistryService struct{ staffInfo *modelmg.StaffInfo }
   func EmployeeRegistry(staffInfo *modelmg.StaffInfo) EmployeeRegistryService { ... }
   func (s EmployeeRegistryService) GetList(ctx, query GetListQuery) (GetListResponse, error)
   ```
   - Build MongoDB filter từ query (regex search + exact filters)
   - Pagination: `.Skip((page-1)*pageSize).Limit(pageSize)`
   - Total count qua `CountDocuments`
3. [30m] Tạo `pkg/admin/handler/employee_registry.go`:
   ```go
   type EmployeeRegistryHandler struct{}
   func EmployeeRegistries() EmployeeRegistryHandler { return EmployeeRegistryHandler{} }
   func (h EmployeeRegistryHandler) GetList(c echo.Context) error { ... }
   ```
4. [30m] Tạo `pkg/admin/router/employee_registry.go`:
   ```go
   func employeeRegistry(e *echo.Group) {
       h := handler.EmployeeRegistries()
       g := e.Group("/employee-registry", a.RequiredLogin, a.IsRoot)
       g.GET("", h.GetList, v.All)
       // B.3 sẽ thêm POST /import
   }
   ```
5. [15m] Edit `router.go` thêm `employeeRegistry(r)`
6. [30m] Manual test `curl` GET endpoint trả empty list + pagination 0
7. [25m] Define `GetListQuery` + `GetListResponse` types, export cho type safety

### B.2 Admin UI (~3h)

1. [20m] Đọc `admin/src/pages/user/index.tsx` + `components/filter.tsx` + `components/table.tsx` làm template
2. [30m] Tạo `admin/src/services/employeeRegistry.ts`:
   ```ts
   export const getEmployeeRegistryList = (params) => request('/api/v1/admin/employee-registry', { params })
   export const importEmployeeRegistry = (file) => request.post('/api/v1/admin/employee-registry/import', { data: formData })
   ```
3. [45m] Tạo `admin/src/pages/employee-registry/model.ts` (DVA model: `namespace: 'employeeRegistryModel'`, state `{list, pagination, filter, loading}`, effects `*getList({payload}, {call, put})` gọi service client) + `index.tsx` page dùng `connect(({employeeRegistryModel, loading}) => ...)` từ `umi`. Pattern COPY từ `admin/src/pages/user/{model.ts,index.tsx}`.
4. [30m] Tạo `components/filter.tsx` — search input, workplace select, status dropdown, matched toggle
5. [30m] Tạo `components/table.tsx` — antd Table columns: mã NV, họ tên, SĐT, đơn vị, status, matched user
6. [20m] Tạo `components/upload-modal.tsx` **skeleton** — form + antd Upload + button. `onOk` gọi `importEmployeeRegistry`. Hiển thị loading + message.success với `import_id`. **Chưa hiển thị errors** (Phase C).
7. [5m] Edit `admin/config/routes.ts`: `{ path: '/employee-registry', name: 'employeeRegistry', component: './employee-registry' }`
8. [5m] Edit `admin/src/locales/vi-VN/menu.ts`: `'menu.employeeRegistry': 'Danh sách nhân viên'`
9. [15m] Run admin dev, verify page render, filter UI interactive, empty table hiển thị placeholder "Chưa có dữ liệu"

### B.3 Upload handler skeleton (~1h)

1. [10m] Đọc `internal/echo/upload_file.go` để hiểu middleware `UploadSingle`
2. [15m] Thêm route `POST /import` vào `router/employee_registry.go`:
   ```go
   g.POST("/import", h.Import, v.Create, echoupload.UploadSingle("file", []string{".xlsx"}, 10*1024*1024))
   ```
3. [25m] Impl `handler.Import(c echo.Context)`:
   - Get `*modelmg.FileInfo` từ context (middleware đã set)
   - Get staffInfo từ ctx
   - Call `service.CreateImport(ctx, fileInfo, staffInfo)` → return `import_id`
4. [10m] Impl `service.CreateImport(ctx, fileInfo, staffInfo)`:
   - Compute SHA256 checksum của file (lưu vào `fileChecksum`, KHÔNG dedup warn đợt 1)
   - MinIO upload bucket `employee-registry-imports` (private, presigned). Tạo bucket config trong `pkg/file/service/` hoặc config tương ứng nếu chưa có
   - `ImportHistoryDAO.Insert(ImportHistoryRaw{ImportID: uuid, FileName, FileChecksum, FilePath, UploadedBy: staffInfo.ID, Timestamp: now, Status: "preview"})`
   - Return `importID`
5. [10m] Manual test `curl -F file=@sample.xlsx /v1/admin/employee-registry/import` → 200 `{import_id}`. Verify `db["import-histories"].findOne()` có record.

## Todo List

- [x] B.1.1 Service `EmployeeRegistryService.GetList`
- [x] B.1.2 Handler `EmployeeRegistryHandler.GetList`
- [x] B.1.3 Router file + register
- [x] B.1.4 Curl test GET empty list
- [x] B.1.5 Define query/response types
- [x] B.2.1 Service client `employeeRegistry.ts`
- [x] B.2.2 Page `index.tsx`
- [x] B.2.3 Component `filter.tsx`
- [x] B.2.4 Component `table.tsx`
- [x] B.2.5 Component `upload-modal.tsx` skeleton
- [x] B.2.6 Route `/employee-registry`
- [x] B.2.7 Menu i18n key
- [x] B.2.8 Dev server render + empty state
- [x] B.3.1 POST `/import` route với upload middleware
- [x] B.3.2 Handler `Import` + service `CreateImport`
- [x] B.3.3 SHA256 checksum
- [x] B.3.4 Insert `import_history` status=preview
- [x] B.3.5 Curl test upload trả `import_id`

## Success Criteria

- [x] `curl GET /v1/admin/employee-registry` với cookie admin → 200 `{list:[], pagination:{total:0,page:1,pageSize:20}}`
- [x] `curl GET /v1/admin/employee-registry?q=nguyen&page=2` → pagination page=2
- [x] Admin UI `/employee-registry` render không crash, filter input + select hoạt động (local state), empty table hiển thị antd default
- [x] Menu "Danh sách nhân viên" xuất hiện trong sidebar
- [x] `curl -F file=@VP_Mẫu.xlsx POST /import` → 200 `{import_id:"..."}`
- [x] `mongo> db["import-histories"].findOne()` có doc với `status:"preview"`, `uploadedBy`, `fileChecksum`
- [x] Upload `.pdf` → 400 từ middleware (ext validate)
- [x] Upload file 20MB → 400 (size limit)
- [x] GET list endpoint chạy không cần register root account (middleware `a.IsRoot` vẫn enforce)

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| GET list filter với regex gây slow query | MED | Index trên `employeeCode`, `phone`, `workplaceName` (đã có từ Phase A). Regex anchored `^` nếu có thể. |
| Upload middleware chưa support `.xlsx` mime | LOW | Check `internal/echo/upload_file.go` để confirm ext whitelist; nếu chưa có `.xlsx` → thêm ext vào allow list |
| Admin UI theme/antd version mismatch | LOW | Reuse exact component pattern từ `pages/user/` |
| MinIO bucket `employee-registry-imports` chưa tồn tại | MED | Tạo bucket qua admin console MinIO trước khi deploy, hoặc auto-create trong code khi service init. Document trong README dev setup. |
| `staffInfo` ctx key khác giữa module | LOW | Reuse helper `adminauth.GetStaffInfo(c)` (xem workplace handler) |
| Race condition: 2 admin upload cùng lúc cùng checksum | LOW | UUID `import_id` unique. Dedup warn defer đợt 2. |

## Security Considerations

- **Admin auth:** All routes behind `a.RequiredLogin, a.IsRoot` — chỉ root staff truy cập
- **File upload (NFR-003):**
  - Ext whitelist `.xlsx` ONLY (no `.xls`, no `.xlsm` — avoid macro)
  - Size limit 10MB ở middleware
  - MIME check: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - Path traversal: middleware save với sanitized filename (UUID) không dùng `filename` gốc từ client
  - **Macro/script scan:** Phase B chưa scan, document TODO cho Phase C (mở file xem nếu có VBAProject → reject)
- **NoSQL injection:** Query build qua struct + bson tag, search `q` dùng `primitive.Regex` escaped — không interpolate string raw
- **SSRF:** Không fetch URL external; MinIO client internal
- **Rate limit:** Không enforce trong đợt 1 (defer). Document.
- **File retention:** Phase B save file tmp hoặc MinIO. Cleanup job defer đợt 2. Document TODO.

## Next Steps

Phase B unblocks Phase C (wire Excel parser vào upload handler). Xem [phase-C-excel-parser-validator.md](phase-C-excel-parser-validator.md).

Đợt 2 sẽ extend:
- List API thêm filter `action` (khi dry-run table có)
- Upload handler: sau parse + validate → chạy dry-run match → save `import_changes` với `phase=preview`
- Admin UI: preview table + Apply button (FR-004)
