# V3 Import Test Plan — FR-V3-018 + FR-V3-019

**File:** [sample-import-v3-scenarios.xlsx](sample-import-v3-scenarios.xlsx)
**Date:** 2026-04-30
**Scope:** Verify Workplace Group Derive (FR-V3-018) + Scope Filter Rà soát (FR-V3-019)

---

## ⚠️ Pre-flight check (CRITICAL)

Trước khi test, verify master data có sẵn. Connect MongoDB DB `vcreator-green`:

```javascript
// Phải có ít nhất 2 brands active
db.getCollection("workplace-brands").countDocuments({status: "active"})  // expected: ≥ 2

// Phải có ít nhất các unit names trong file
db.getCollection("workplace-units").find({
  status: "active",
  name: { $in: [
    "Vinpearl Cửa Hội Resort Aff. by Meliá",
    "Sheraton Vinh", "Imperial Club",
    "VinWonders Nha Trang", "VinPalace Cổ Loa",
    "Vinpearl Golf Nha Trang",
    "Khối Công nghệ", "Trung tâm CSKH"
  ]}
}, {name:1, brandCode:1, companyName:1}).toArray()
// expected: 8 units returned, brand cover VINPEARL + GREEN_SM
```

**Nếu thiếu units:** Test sẽ fail ở parser stage (INVALID_WORKPLACE) — không thể test FR-V3-018/019.

---

## Pre-conditions

1. DB `vcreator-green` (hoặc DB BE đang connect — check `.env` `MONGO_DB_NAME`)
2. KHÔNG có pending import (status = preview/processing) — nếu có phải Apply hoặc Cancel trước
3. Login admin với role `IsRoot`
4. Optional: có vài registry records cũ thuộc `GREEN_SM` brand để test scope filter loại trừ Vinpearl

---

## Test scenarios trong file

| Group | Rows Excel | Mã NV | Action expected | Brand · Company | Note |
|---|---|---|---|---|---|
| **A** | 5-9 | V3VP001-005 | `new_record` | VINPEARL · Vinpearl | 5 units cùng company "Vinpearl" |
| **B** | 10-12 | V3VW001-003 | `new_record` | VINPEARL · VinWonders | Cùng brand khác company |
| **C** | 13-14 | V3VPL001-002 | `new_record` | VINPEARL · VinPalace | 3rd company |
| **D** | 15-16 | V3GOLF1-2 | `new_record` | VINPEARL · Vinpearl Golf | 4th company |
| **E** | 17-19 | V3GS001-003 | `new_record` | GREEN_SM · (no company) | Brand thứ 2 — test scope multi-brand |
| **F** | 20-21 | V3TYPO1, V3MISS1 | **invalid** (INVALID_WORKPLACE) | (không match master) | Bị reject ở parser stage |
| **G** | 22-23 | V3DUP1 (×2) | new_record(1) + invalid(1) | VINPEARL · Vinpearl | Row 23 duplicate code |
| **H** | 24-27 | V3INV1-3 | invalid (format) | - | Bad phone / empty name / empty unit / empty code |

**Total: 23 rows** → expected:
- **16 valid rows** chạy MatchEngine: A(5) + B(3) + C(2) + D(2) + E(3) + G row 22(1)
- **7 invalid rows**: F(2) + G(1) + H(4)
- Counter `Thêm mới: 16`, `Lỗi định dạng: 7`

---

## Test cases

### TC-1: FR-V3-018 — Workplace derive cho new_record

**Steps:**
1. Upload `sample-import-v3-scenarios.xlsx`, **KHÔNG tick** "Rà soát nghỉ việc"
2. Mở preview screen
3. Verify counters: `Thêm mới: 16`, `Lỗi định dạng: 7`
4. Cột "Đơn vị" hiển thị **hierarchy** "Vinpearl · Vinpearl · Vinpearl Cửa Hội Resort Aff. by Meliá" (Brand · Company · Unit) cho 16 valid rows
5. Click Apply

**Expected sau Apply:**
- 16 registry records được insert với status = active
- MongoDB query verify 1 record sample:
   ```javascript
   db.getCollection("employee-registries").findOne({ employeeCode: "V3VP001" })
   ```
   - `workplaceBrandCode` = "VINPEARL"
   - `workplaceBrandName` = "Vinpearl"
   - `workplaceCompanyName` = "Vinpearl"
   - `workplaceUnitName` = "Vinpearl Cửa Hội Resort Aff. by Meliá"
   - `workplaceGroup` = "VINPEARL" (mặc định = brandCode)
- Sample GREEN_SM:
   ```javascript
   db.getCollection("employee-registries").findOne({ employeeCode: "V3GS001" })
   ```
   - `workplaceBrandCode` = "GREEN_SM"
   - `workplaceCompanyCode/Name` = empty (units này không có company layer)

---

### TC-2: FR-V3-019 — Scope filter AUTO-DERIVE (default)

**Steps:**
1. Reset DB hoặc skip TC-1 apply (cancel preview thay vì apply)
2. Tạo registry seed cho test missing detection: ví dụ thêm record brand `VINHOMES` thủ công vào DB
   ```javascript
   db.getCollection("employee-registries").insertOne({
     _id: ObjectId(), employeeCode: "VHM_TEST", fullName: "Test Vinhomes NV",
     phone: "0911111000", workplaceName: "X",
     workplaceBrandCode: "VINHOMES", workplaceBrandName: "Vinhomes",
     status: "active", importId: "manual", lastSeenImportId: "manual",
     importedAt: new Date(), createdAt: new Date(), updatedAt: new Date()
   })
   ```
3. Upload file V3, **TICK** "Rà soát nghỉ việc"
4. KHÔNG mở "Phạm vi rà soát (nâng cao)" → để BE auto-derive
5. Mở preview

**Expected:**
- Counters: `Thêm mới: 16`, `Lỗi định dạng: 7`, `Nghi ngờ nghỉ: 0` (vì registry VINHOMES không thuộc scope auto-derive [VINPEARL, GREEN_SM])
- Backend log: scope auto-derive returned `[VINPEARL, GREEN_SM]`
- Record VHM_TEST **KHÔNG** bị flag missing — preserved!

---

### TC-3: FR-V3-019 — Admin OVERRIDE scope (chỉ Vinpearl)

**Steps:**
1. Sau TC-2 apply (16 registry V3 đã insert)
2. Tạo file mới chỉ có 5 rows VINPEARL (rows 5-9 từ file V3)
3. Upload file đó, **TICK** "Rà soát nghỉ việc"
4. Mở "Phạm vi rà soát (nâng cao)" → chọn **chỉ "Vinpearl"**
5. Submit → preview

**Expected:**
- `Nghi ngờ nghỉ: 11` — đó là 11 registry VINPEARL không có trong file mới (16 - 5)
- **KHÔNG flag** 3 record GREEN_SM (V3GS001-003) dù không có trong file
- ImportHistoryRaw lưu `detectMissingScope: ["VINPEARL"]`

---

### TC-4: FR-V3-019 — Safety fallback khi auto-derive fail

**Steps:**
1. Tạo file copy + sửa toàn bộ cột Đơn vị thành "Hilton Saigon" (không có trong master)
2. Upload, tick "Rà soát nghỉ việc", KHÔNG mở advanced

**Expected:**
- Tất cả rows bị reject ở parser stage (INVALID_WORKPLACE) → `ValidRows = 0`
- Hoặc nếu workplace_units có "Hilton Saigon" thì validate pass, nhưng auto-derive trả empty (vì brand chưa setup)
- BE log: `[EmployeeRegistry.GenerateDryRun] scope rỗng — skip detectMissing để tránh false-positive toàn cục`
- **KHÔNG có row nào flag `missing_from_file`**

---

### TC-5: FR-V3-018 — Workplace derive cho transferred (HR đổi cơ sở)

**Steps:**
1. Sau TC-1 apply (V3VP001 thuộc "Vinpearl Cửa Hội Resort Aff. by Meliá", company "Vinpearl")
2. Tạo file mới 1 row: `00001 | V3 NV Vinpearl A1 | 0920100001 | VinWonders Phú Quốc | V3VP001` (cùng mã, đổi unit + company)
3. Upload → preview → apply

**Expected:**
- Action `workplace_updated` (transferred)
- Sau apply, registry V3VP001:
   - `workplaceUnitName` = "VinWonders Phú Quốc"
   - `workplaceCompanyName` = "VinWonders" (đổi từ "Vinpearl")
   - `workplaceBrandCode` = "VINPEARL" (giữ nguyên — vẫn cùng brand)
   - `workplaceGroup` = "VINPEARL"

---

### TC-6: FR-V3-018 — Backfill khi revive registry terminated

**Steps:**
1. Set 1 registry về terminated:
   ```javascript
   db.getCollection("employee-registries").updateOne(
     { employeeCode: "V3VP001" },
     { $set: { status: "terminated", workplaceBrandCode: "", workplaceUnitName: "" }}
   )
   ```
2. Upload file mới chứa V3VP001 với "Vinpearl Beachfront Nha Trang"
3. Apply

**Expected:**
- Action `new_record` (revive path)
- Registry status = "active"
- 7 workplace fields **đầy đủ** (backfill từ derive)

---

### TC-7: Index performance

**Steps:**
```javascript
db.getCollection("employee-registries").find({
  status: "active",
  workplaceBrandCode: { $in: ["VINPEARL"] }
}).explain("executionStats")
```

**Expected:**
- `executionStages.stage` = `IXSCAN` (không phải `COLLSCAN`)
- Index `workplaceBrandCode_1` được sử dụng

---

## Negative tests

| TC | Steps | Expected |
|---|---|---|
| N-1 | Upload V3 file lần 2 mà chưa apply lần 1 | 409 PENDING_IMPORT_EXISTS |
| N-2 | File 0 row valid (toàn bộ INVALID_WORKPLACE) | Preview 0 rows, có thể cancel |
| N-3 | File > 1000 rows | Async path, polling status |

---

## Cleanup sau test

```javascript
// MongoDB shell
db.getCollection("employee-registries").deleteMany({ employeeCode: { $regex: /^V3/ } });
db.getCollection("import-changes").deleteMany({ employeeCode: { $regex: /^V3/ } });
db.getCollection("import-histories").deleteMany({ status: "cancelled" });
// Hoặc dùng API rollback /imports/:id/rollback
```

---

## Common pitfalls

1. **Counter rỗng / 0 changes:** parse stage reject toàn bộ rows do INVALID_WORKPLACE → check master `workplace-units` có units đúng tên không
2. **Cột "Đơn vị" không show hierarchy:** BE chưa restart sau khi merge code mới, hoặc DB connection dùng DB sai (verify `.env` `MONGO_DB_NAME`)
3. **Preview rỗng nhưng counters > 0:** ImportChange records tồn tại nhưng ở status `cancelled` — check filter pagination
