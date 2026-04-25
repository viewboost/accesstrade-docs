# Researcher 02 — Admin UI + Excel Library Research

**Date:** 2026-04-24  
**Topic:** Admin UI patterns + Backend Excel library cho Employee Registry Import

---

## 1. Admin List Page Pattern

**Files hiện tại:**
- `admin/src/pages/user/index.tsx` (page)
- `admin/src/pages/user/components/filter.tsx`, `table.tsx`
- `admin/src/pages/user/type.d.ts`, `model.ts` (DVA model)
- `admin/src/services/` (API client)

**Pattern hiện tại (DVA):**
- Model + reducer → filter state + table data state
- Filter input → gọi API `/api/user/list` + paging
- Table: columns config, row selection, inline actions
- Pagination: pageSize, current page

**Recommend cho Employee Registry:**
- Copy pattern `admin/pages/segment/` (segment import có sẵn modal)
- DVA model: `{ list, loading, pagination, filters }`
- Table columns: employee_id, name, phone, workplace_id, matched_status (?)
- Filter component: search employee_id/name, workplace select (từ DB), status dropdown
- **Lưu ý:** WorkplaceCascadingSelect KHÔNG có sẵn admin → dùng antd `Select` + API `/api/workplace/list`

---

## 2. Admin Upload UI (Segment Import Modal)

**File reference:**
- `admin/src/pages/segment/detail/components/tabs/user/components/modal-import.tsx`

**Pattern:**
```tsx
<Form.Item label="Upload File">
  <Upload
    beforeUpload={(file) => {
      const isXlsx = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      if (!isXlsx) {
        message.error(intl.formatMessage({ id: 'file.format.xlsx.only' }));
        return Upload.LIST_IGNORE;
      }
      return false;
    }}
    maxCount={1}
  >
    <Button>Click to Upload</Button>
  </Upload>
</Form.Item>
```

**Recommend cho Employee Registry:**
- Reuse pattern này
- Mime type: `.xlsx` only
- Error handling: `message.error()` + intl

---

## 3. Backend Excel Library — tealeg vs excelize/v2

**Tealeg/xlsx:**
- Dùng: `user_segment.go`, `helper.go` (import)
- Pros: simple, ổn định, core team familiar
- Cons: feature hạn chế, không support data validation

**Excelize/v2:**
- Dùng: `export_content_analytic.go`, `export_reconciliation.go` (export)
- Pros: modern, support data validation (validation rule, dropdown), team đã familiar
- Cons: hơi verbose

**Recommend: excelize/v2**  
**Lý do:** 
- Team đã familiar qua export flow
- Support data validation cho cột dropdown (nếu cần)
- Active maintenance, feature-rich
- Import + read Excel cells dễ dàng hơn tealeg

**Code snippet (read):**
```go
f, err := excelize.OpenFile("file.xlsx")
defer f.Close()

rows, _ := f.GetRows("Sheet1")
for _, row := range rows {
  employeeID := row[0] // Column A
  phone := row[1]      // Column B
  // ...
}
```

---

## 4. Frontend-green Phone Validation

**File:** `frontend-green/src/components/profile-completion-popup/form.tsx`

**Phone format hiện tại:**
- Regex: `PHONE_REGEX = /^0\d{9}$/` (10 digits, leading 0)
- Frontend: **KHÔNG normalize** → gửi raw `0xxx...` string

**Recommend cho Employee Registry:**
- Backend accept format: `0\d{9}` (10 digits)
- **Hoặc** normalize server-side (strip spaces, check length)
- Database store: raw format `0xxx...` hoặc normalized `+840xxx...`

---

## Unresolved Questions

1. **Cột J validation list (tính năng gì?):**  
   - Dropdown từ DB? (e.g., list tất cả phone từ HR system)
   - Hardcode list? (e.g., department list)
   - Data validation rule cho Excel?

2. **Employee Registry filter cần:**
   - Status filter (unmatched/matched/error)?
   - Workplace filter (dropdown)?
   - Date range (upload date)?
   - Search by employee_id/name/phone?

3. **Duplicates handling:**
   - Reject nếu phone trùng trong DB?
   - Merge strategy?

4. **File mẫu (.xlsx):**
   - Column order: A=ID, B=Name, C=Phone, D=Workplace, E-J=?
   - Header row bắt buộc hay auto-detect?
