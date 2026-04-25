# Scout 01 — Codebase Gaps Fill

**Date:** 2026-04-24 | **Project:** `accesstrade-projects/vcreator/`

---

## Q1. Workplace V1 model — ✅ FOUND

**3-tier hierarchy:** Brand → Company → Unit

| Layer | Model file | DAO file | Collection const |
|-------|-----------|----------|------------------|
| Brand | `backend/internal/model/mg/workplace_brand.go:15-24` | `backend/internal/module/database/mongodb/dao/workplace_brand.go:8-22` | `CollectionWorkplaceBrand = "workplace-brands"` (collection.go:61) |
| Company | `backend/internal/model/mg/workplace_company.go:15-26` | `backend/internal/module/database/mongodb/dao/workplace_company.go:8-22` | `CollectionWorkplaceCompany = "workplace-companies"` (collection.go:62) |
| Unit | `backend/internal/model/mg/workplace_unit.go:15-28` | `backend/internal/module/database/mongodb/dao/workplace_unit.go:8-22` | `CollectionWorkplaceUnit = "workplace-units"` (collection.go:63) |

**Fields (inferred):**
- `WorkplaceBrandRaw`: ID, Code, Name, Order, Status, CreatedAt, UpdatedAt
- `WorkplaceCompanyRaw`: Brand fields + BrandCode, BrandName
- `WorkplaceUnitRaw`: Brand+Company fields + CompanyCode, CompanyName

**Code snippet:**
```go
type WorkplaceUnitRaw struct {
    ID          AppID     `bson:"_id"`
    Code        string    `bson:"code"`
    BrandCode   string    `bson:"brandCode"`
    CompanyCode string    `bson:"companyCode,omitempty"`
    Name        string    `bson:"name"`
    // ...
}
```

**CRITICAL derive workplace_group logic:** KHÔNG có sẵn trong V1.
- PRD nói 6 nhóm (VinPalace, Vinpearl, VinWonders, Golf, GreenSM, Khác) — tương ứng `WorkplaceBrand` layer.
- Khi import Excel: "Đơn vị thành viên" (cột D) = workplace `name` → cần **lookup WorkplaceUnit WHERE name = X** → lấy `brandCode` → lookup WorkplaceBrand để có `brandName` (= workplace_group).
- Cần util `DeriveWorkplaceGroup(unitName string) (brandCode, brandName string, error)` trong service layer.

---

## Q2. Asynq — ❌ NOT FOUND, CHUYỂN STRATEGY

**Kết quả grep:**
```bash
grep -r "asynq" backend --include="*.go" -l  # 0 results
grep -i "asynq\|hibiken" backend/go.mod      # 0 results
```

**Vcreator KHÔNG dùng Asynq.** Confirm bằng cả go.mod lẫn source code.

**Alternative đã có trong codebase:**
- Redis client + mutex: `backend/internal/module/redis/redis.go`, `backend/internal/module/redis/mutex.go`
- Goroutine pattern phổ biến:
  - `pkg/admin/service/audit.go:49` — `go func(n, i)` batch notification
  - `pkg/admin/service/article.go:84`
  - `pkg/admin/service/admin_notification.go:143, 269, 370`

**Recommend cho đợt 1:**
- **Strategy A (đơn giản):** File ≤ 1000 rows sync return. File > 1000 rows → goroutine với Redis mutex (`redis.Mutex` lock theo `import_id`) + progress được update vào `import_history.status`. Admin poll status qua GET endpoint.
- **Strategy B (defer):** Đợt 1 chỉ support sync ≤ 1000 rows, reject file lớn hơn với message "File quá lớn, vui lòng chia nhỏ". Async đẩy sang đợt 2.
- Cá nhân recommend **B** cho đợt 1 — giảm scope, giảm risk. Đợt 2 add goroutine+Redis nếu cần.

---

## Q3. Admin handler + route — ✅ FOUND

**Route registration:** `backend/pkg/admin/router/router.go:9-43`
- `Init(e)` gọi các function module: `workplaceBrand(r)`, `workplaceCompany(r)`, etc.
- Khi thêm Employee Registry → thêm dòng `employeeRegistry(r)` + file `backend/pkg/admin/router/employee_registry.go`.

**Route file pattern:** `backend/pkg/admin/router/workplace.go:11-51`
```go
func workplaceBrand(e *echo.Group) {
    h := handler.WorkplaceBrands()
    g := e.Group("/workplace-brands", a.RequiredLogin, a.IsRoot)
    g.GET("", h.GetList, v.All)
    g.POST("", h.Create, v.Create)
    g.PUT("/:id", h.Update, v.Update)
}
```

**Auth middleware:** `a.RequiredLogin, a.IsRoot` (từ `backend/pkg/admin/router/routeauth/`).

**Handler pattern:** `backend/pkg/admin/handler/workplace.go`
```go
type WorkplaceBrandHandler struct{}
func WorkplaceBrands() WorkplaceBrandHandler { return WorkplaceBrandHandler{} }
func (h WorkplaceBrandHandler) GetList(c echo.Context) error {
    s := service.WorkplaceBrand(staffInfo)
    return cc.Response200(s.GetList(ctx, query), "")
}
```

---

## Q4. DAO + Collection + Index registration — ✅ FOUND

**Pattern khi thêm DAO mới (apply cho EmployeeRegistry):**

1. **Model:** `backend/internal/model/mg/employee_registry.go` (struct + DAO interface)
2. **DAO impl:** `backend/internal/module/database/mongodb/dao/employee_registry.go`
   ```go
   func EmployeeRegistryDAO() modelmg.EmployeeRegistryDAO {
       return &employeeRegistryDAO{DbShare: databasemongodb.GetDBShare()}
   }
   ```
3. **Collection const:** `backend/internal/module/database/mongodb/collection.go` — add `CollectionEmployeeRegistry = "employee-registries"`, `CollectionImportHistory = "import-histories"`, `CollectionImportChanges = "import-changes"`
4. **Index creation:** `backend/internal/module/database/mongodb/index.go:34-293` (method `IndexDatabase().Indexes(db)`). Workplace index ở line 260-292 làm template. Add indexes:
   - `employee-registries`: unique on `employeeCode`, index on `phone`, `workplaceName`, `genGreenUserId`
   - `import-histories`: index on `timestamp`, `status`, `uploadedBy`
   - `import-changes`: index on `importId`, `userId`, `employeeCode`

---

## Q5. Admin UI routing + i18n — ✅ FOUND

**Route config:** `admin/config/routes.ts:1-200+`
- Format: `{ path, name, component, icon, access }`
- Example: `{ path: '/departments', name: 'departments', component: './department' }`

**i18n files:**
- Main: `admin/src/locales/vi-VN.ts` (key-value aggregate)
- Menu: `admin/src/locales/vi-VN/menu.ts` — ví dụ `'menu.departments': 'Phòng ban'` (line 22)

**DVA model:** NO explicit DVA registration file. Admin dùng React hooks pattern (không phải DVA như researcher-02 guess). Pages tự manage state, gọi API qua `admin/src/services/`.

**Khi thêm trang Employee Registry:**
1. `admin/src/pages/employee-registry/` — folder mới (mẫu theo `admin/src/pages/user/` hoặc `admin/src/pages/department/`)
2. `admin/config/routes.ts` — thêm route `{ path: '/employee-registry', name: 'employeeRegistry', component: './employee-registry' }`
3. `admin/src/locales/vi-VN/menu.ts` — thêm key `'menu.employeeRegistry': 'Danh sách nhân viên'`
4. `admin/src/services/employeeRegistry.ts` — API client mới

---

## Summary — Files cần tạo/sửa cho đợt 1

### Backend (9 files)
| Action | File | Purpose |
|--------|------|---------|
| CREATE | `backend/internal/model/mg/employee_registry.go` | EmployeeRegistryRaw + DAO interface |
| CREATE | `backend/internal/model/mg/import_history.go` | ImportHistoryRaw + ImportChangeRaw + DAO |
| CREATE | `backend/internal/module/database/mongodb/dao/employee_registry.go` | DAO impl |
| CREATE | `backend/internal/module/database/mongodb/dao/import_history.go` | DAO impl |
| EDIT | `backend/internal/module/database/mongodb/collection.go` | Thêm 3 collection const |
| EDIT | `backend/internal/module/database/mongodb/index.go` | Thêm indexes |
| CREATE | `backend/pkg/util/phone.go` | NormalizePhone util |
| CREATE | `backend/pkg/admin/handler/employee_registry.go` | HTTP handlers |
| CREATE | `backend/pkg/admin/service/employee_registry.go` | Business logic (parse Excel, validate) |
| CREATE | `backend/pkg/admin/router/employee_registry.go` | Route definitions |
| EDIT | `backend/pkg/admin/router/router.go` | Register route |
| EDIT | `backend/pkg/admin/service/user.go:653-709` | Phase 0: VerifyStaff accept actor |
| EDIT | `backend/internal/service/audit.go` | Phase 0: createAudit accept actor (nếu cần) |

### Admin UI (4-5 files)
| Action | File | Purpose |
|--------|------|---------|
| CREATE | `admin/src/pages/employee-registry/index.tsx` | Main page |
| CREATE | `admin/src/pages/employee-registry/components/{filter,table,upload-modal}.tsx` | Components |
| CREATE | `admin/src/services/employeeRegistry.ts` | API client |
| EDIT | `admin/config/routes.ts` | Route |
| EDIT | `admin/src/locales/vi-VN/menu.ts` | Menu i18n |

---

## Unresolved Questions (for user)

1. **Async processing strategy** — Đợt 1 chọn Strategy A (goroutine+Redis mutex) hay B (sync-only, file >1000 reject)? → **Recommend B cho đợt 1**.
2. **Phone DB storage format** — Hiện V1 không normalize, lưu raw `0xxx...`. Import normalize về `0xxxxxxxxx` và lưu về DB. Có cần migration backfill phone user hiện có để đồng nhất format không? → **Recommend: không migrate, chỉ normalize runtime khi match**.
3. **Mã NV 7 vs 8 chữ số** — File mẫu `0011111` 7 chữ số, PRD nói 8. Cần confirm đối tác. → **Recommend: validate 7-8 chữ số cho linh hoạt, log warning nếu 7 chữ số**.
4. **Workplace group derive** — V1 không có logic map unitName → brandName. Đợt 1 implement util mới hay defer? → **Recommend implement luôn trong phase registry model** (cần cho dry-run đợt 2).
