# Phase D — Match Logic Core

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Đợt 1 ref:** [../20260424-2255-employee-registry-import-dot1/phase-A-foundations.md](../20260424-2255-employee-registry-import-dot1/phase-A-foundations.md), [phase-C-excel-parser-validator.md](../20260424-2255-employee-registry-import-dot1/phase-C-excel-parser-validator.md)
- **PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) — FR-008/009/010 (kịch bản A/B/C), §EPIC-003
- **Research:** [research/researcher-01-backend-patterns.md](research/researcher-01-backend-patterns.md), [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q4 test scaffolding

## Overview

- **Date:** 2026-04-25
- **Description:** Core match engine generate `ImportChangeRaw` records từ parsed rows. Hash-map join giữa registry data + user data, output 8 actions (auto_verified, cancelled_mismatch, transferred, missing_from_file, new_record, no_match, unchanged, invalid). Workplace 3-tier derive util.
- **Priority:** Must Have (block E, F, G)
- **Implementation Status:** Not Started
- **Review Status:** Pending

## Key Insights

- **Bulk 2-query strategy** thay vì loop N rows × 2 query: `EmployeeRegistryDAO.Find(employeeCode IN parseRows)` + `UserDAO.Find(phone IN parseRows AND employeeCode IS NOT NULL)`. Build hash maps `code → registry`, `phone → user`. Loop trong memory O(N).
- **3 kịch bản** (PRD §EPIC-003): A = code match + phone match → auto_verified; B = code match + phone MISmatch → cancelled_mismatch; C = code KHÔNG có trong registry → no_match (user rejected manual review)
- **Workplace 3-tier:** unitName → `workplace_units` → `workplace_companies` → `workplace_brands`. Derive `brandCode + brandName` cho `workplaceGroup` field.
- **Phone normalize 2 vế:** registry phone đã normalize ở parse stage (đợt 1 `NormalizePhone`), user.phone DB chưa migrate → must `NormalizePhone(user.phone.local)` runtime trước compare.
- **Test strategy:** Integration với local Mongo, prefix collection `test_employee_registry_*`. Cleanup sau test bằng `defer dropCollection`. Skip CI nếu thiếu Mongo.

## Requirements

### FR-008 Match logic (kịch bản A/B/C)

- Input: `[]ParseRow` (đã validate đợt 1) + `importID string`
- Output: `[]ImportChangeRaw{phase:preview}` (1 record / row, có thể thêm record `missing_from_file` riêng — defer Phase E)
- Action enum: `auto_verified`, `cancelled_mismatch`, `transferred`, `new_record`, `no_match`, `unchanged`, `invalid`

### FR-011 Transferred (within match)

- Nếu user `staffStatus=verified` đã có `workplaceBrandCode` cũ, registry update workplace mới → action `transferred`. `oldValue` = workplace cũ, `newValue` = workplace mới.

### Workplace derivation

- `DeriveWorkplaceGroup(ctx, unitName) (brandCode, brandName, error)`:
  - Query `workplace_units{name: unitName}` → unit
  - `workplace_companies{_id: unit.companyID}` → company
  - `workplace_brands{_id: company.brandID}` → brand
  - Return `brand.code, brand.name` hoặc lỗi nếu không tìm thấy ở bất kỳ tier nào

## Architecture

```
ParseRows (Excel đã validate)
        │
        ▼
┌─────────────────────────────────────────┐
│ MatchEngine.GenerateChanges()           │
│                                          │
│  1. Bulk query 1: registry by codes     │
│     map[code] = *EmployeeRegistryRaw    │
│                                          │
│  2. Bulk query 2: users by phones       │
│     map[phone+code] = *UserRaw          │
│                                          │
│  3. Loop rows:                           │
│     - DeriveWorkplaceGroup(unitName)     │
│     - Lookup in maps → kịch bản A/B/C    │
│     - Build ImportChangeRaw              │
└─────────────────────────────────────────┘
        │
        ▼
   []ImportChangeRaw{phase:preview}
        │
        ▼
   (Phase E persist + counter)
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| CREATE | `backend/pkg/util/workplace.go` | `DeriveWorkplaceGroup` 3-tier query |
| CREATE | `backend/pkg/util/workplace_test.go` | Unit test 3-tier với mock DAO |
| CREATE | `backend/pkg/admin/service/employee_registry_match.go` | `MatchEngine` struct + `GenerateChanges` + `LookupSingle` (helper cho FR-009) |
| CREATE | `backend/pkg/admin/service/employee_registry_match_test.go` | Integration test 3 scenarios A/B/C + transferred + new_record |
| REF | `backend/internal/model/mg/workplace_brand.go`, `workplace_company.go`, `workplace_unit.go` | Models 3-tier |
| REF | `backend/internal/model/mg/employee_registry.go` (đợt 1) | Schema registry |
| REF | `backend/internal/model/mg/import_history.go` (đợt 1) | `ImportChangeRaw` |
| REF | `backend/pkg/util/phone.go` (đợt 1) | `NormalizePhone` |
| REF | `backend/pkg/admin/service/employee_registry_parser.go` (đợt 1) | `ParseRow` struct |

## Implementation Steps

### D.1 Workplace 3-tier util (~1h)

1. [10m] Đọc models `workplace_brand.go`, `workplace_company.go`, `workplace_unit.go` và DAO factories
2. [30m] CREATE `pkg/util/workplace.go`:
   ```go
   func DeriveWorkplaceGroup(ctx context.Context, unitName string) (brandCode, brandName string, err error) {
       unit := new(modelmg.WorkplaceUnitRaw)
       err = daomongodb.WorkplaceUnitDAO().GetShare().FindOne(ctx, unit, bson.M{"name": unitName})
       // ... company, brand chain
   }
   ```
3. [20m] CREATE `pkg/util/workplace_test.go` — table-driven, test 3 cases: full chain match, unit không tìm thấy, company orphan (brand thiếu)

### D.2 Match Engine + 3 kịch bản (~3h)

1. [20m] Thiết kế signature:
   ```go
   type MatchEngine struct {}
   type MatchResult struct {
       Changes []*modelmg.ImportChangeRaw
       Counters MatchCounters
   }
   type MatchCounters struct {
       Total, AutoVerified, CancelledMismatch, Transferred,
       NewRecord, NoMatch, Unchanged, Invalid int
   }
   func (m *MatchEngine) GenerateChanges(ctx context.Context, rows []parser.ParseRow, importID string) (*MatchResult, error)
   func (m *MatchEngine) LookupSingle(ctx context.Context, employeeCode, phone string) (*LookupResult, error) // FR-009 helper
   ```
2. [30m] Bulk query helpers:
   ```go
   func loadRegistryByCodes(ctx, codes []string) (map[string]*modelmg.EmployeeRegistryRaw, error) {
       // Find(bson.M{"employeeCode": bson.M{"$in": codes}})
   }
   func loadUsersByPhones(ctx, phones []string) (map[string]*modelmg.UserRaw, error) {
       // Find(bson.M{"phone.local": bson.M{"$in": phones}, "employeeCode": bson.M{"$ne": ""}})
       // Build map key = phone (sau NormalizePhone)
   }
   ```
3. [90m] Loop rows logic — 3 kịch bản + transferred:
   ```go
   for _, row := range rows {
       // Validate row đã pass (đợt 1). Skip nếu Invalid (mặc dù parser đã reject).
       phone := util.NormalizePhone(row.Phone)
       brandCode, brandName, _ := util.DeriveWorkplaceGroup(ctx, row.UnitName)

       existingRegistry, hasReg := registryMap[row.EmployeeCode]
       existingUser, hasUser := userMap[phone]

       switch {
       case !hasReg && !hasUser:
           // Kịch bản: HR thêm mới mã NV chưa có user signup
           change.Action = "new_record"
       case !hasReg && hasUser:
           // Edge: user có employeeCode nhưng registry chưa có → import sẽ tạo registry. Action `new_record` + link user
           change.Action = "new_record"
           change.UserID = &existingUser.ID
       case hasReg && !hasUser:
           // Registry có sẵn, user chưa signup → unchanged hoặc skip
           change.Action = "unchanged"
       case hasReg && hasUser:
           // Cả 2 có. Kiểm tra phone match
           if existingUser.EmployeeCode == row.EmployeeCode && phone == util.NormalizePhone(existingUser.Phone.Local) {
               // Kịch bản A: code + phone match
               if existingUser.StaffStatus == "pending" {
                   change.Action = "auto_verified"
               } else if existingUser.WorkplaceBrandCode != brandCode {
                   change.Action = "transferred"
                   change.OldValue = existingUser.WorkplaceBrandCode
                   change.NewValue = brandCode
               } else {
                   change.Action = "unchanged"
               }
           } else {
               // Kịch bản B: code match registry nhưng user.phone khác registry.phone
               change.Action = "cancelled_mismatch"
               change.Reason = "Phone không khớp dữ liệu HR"
           }
       }
       changes = append(changes, change)
       counters[change.Action]++
   }
   ```
4. [40m] `LookupSingle(employeeCode, phone)` helper cho FR-009 (Phase G.4) — single-row version:
   - Query `EmployeeRegistryDAO.FindOne(employeeCode)` → `registry`
   - Compare `NormalizePhone(phone) == registry.phone`
   - Return `LookupResult{Match bool, MismatchReason string, Registry *EmployeeRegistryRaw}`

### D.3 Integration test với local Mongo (~1h)

1. [10m] Setup test helper `setupTestDB(t)` — connect local Mongo, prefix collection `test_employee_registry_match_*`, return cleanup func
2. [30m] Fixtures:
   - 2 registry: `EMP001` phone `0901234567`, `EMP002` phone `0907654321`
   - 2 users: user1 employeeCode `EMP001` phone `0901234567` staffStatus=pending, user2 employeeCode `EMP002` phone `0900000000` (mismatch)
3. [20m] Test cases:
   - Row `{EMP001, 0901234567, "Hà Nội"}` → action `auto_verified`
   - Row `{EMP002, 0907654321, "Hà Nội"}` → action `cancelled_mismatch` (DB user phone != registry phone)
   - Row `{EMP003, 0911111111, "Hà Nội"}` → action `new_record` (chưa có registry)
   - Row `{EMP001, 0901234567, "TP HCM"}` (giả sử user1 đã verified với brand Hà Nội) → action `transferred`

## Todo List

- [ ] D.1.1 Đọc models workplace 3-tier + DAO factories
- [ ] D.1.2 Implement `DeriveWorkplaceGroup` 3-tier query
- [ ] D.1.3 Unit test 3 cases (full chain, unit miss, company orphan)
- [ ] D.2.1 Define MatchEngine struct + signatures
- [ ] D.2.2 Implement `loadRegistryByCodes` bulk
- [ ] D.2.3 Implement `loadUsersByPhones` bulk
- [ ] D.2.4 Loop rows + 3 kịch bản A/B/C + transferred
- [ ] D.2.5 Implement `LookupSingle` helper cho FR-009
- [ ] D.2.6 `go build ./...` clean
- [ ] D.3.1 Setup test helper với local Mongo + collection prefix
- [ ] D.3.2 Fixtures (2 registry + 2 users)
- [ ] D.3.3 4 scenarios test pass (A, B, new, transferred)

## Success Criteria

- [ ] `MatchEngine.GenerateChanges(1000 rows)` < 2s (2 bulk queries + memory loop)
- [ ] Counters chính xác: tổng từng action = totalRows (không double-count)
- [ ] `DeriveWorkplaceGroup` return error rõ ở mỗi tier miss (debug log)
- [ ] Integration test 4 scenarios pass với local Mongo, cleanup hoàn tất
- [ ] `LookupSingle` return `MismatchReason` rõ cho frontend (FR-009)

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Bulk query OOM nếu 10k rows | MED | Hash maps O(N) memory ~ 1MB/1k rows. 10k = 10MB acceptable. Document limit. Phase H batch 100/lần cho >1000. |
| Phone normalize 2 vế khác nhau (user.phone DB chưa migrate) | HIGH | Runtime `NormalizePhone(user.phone.local)` trong loop. Test case phone DB có `+84` prefix vs registry `0xxx`. |
| `DeriveWorkplaceGroup` return empty nếu unit name typo | MED | Log warning + fallback `brandCode=""`. Không reject row, để admin xem ở preview action `invalid`. |
| Test data conflict 2 dev chạy song song | MED | Prefix collection theo PID/timestamp. Document `TEST_DB_NAME` env var. |
| User table missing index on `phone.local` | HIGH | Trước Phase D run verify index. Nếu thiếu → add ở Phase D.0 (migration step) |

## Security Considerations

- **Bulk query injection:** `bson.M{"$in": codes}` — codes từ Excel parsed, validated regex/length đợt 1. Không build query từ raw string.
- **Phone normalize consistency:** Mọi compare đều qua `NormalizePhone()` cả 2 vế. Tránh false positive mismatch do format.
- **Test isolation:** Integration test prefix collection để không chạm collection prod data.
- **Audit trail:** Match engine không ghi audit. Audit ghi ở Apply (Phase F.2) khi thực sự apply change.

## Next Steps

→ Phase E [phase-E-dryrun-preview-api.md](phase-E-dryrun-preview-api.md): wire `GenerateChanges` vào `GenerateDryRun`, persist `import_changes{phase:preview}`, expose preview API.
