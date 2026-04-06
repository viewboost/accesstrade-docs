# Thêm thông tin nhân viên vào hồ sơ Influencer

> Thêm 2 trường mới vào trang Hồ sơ trên Dashboard: **"Có phải nhân viên"** và **"Mã nhân viên"**, đồng thời hỗ trợ xuất ra file export.

**Ngày:** 03/04/2026  
**Trạng thái:** Đề xuất  
**Đối tượng đọc:** Business, Ops, PM, Dev

---

## 1. Bối cảnh

### Dữ liệu hiện tại

Mã nhân viên được lưu ở **2 nguồn khác nhau** tùy theo flow:

#### Nguồn 1: `UserPartnerRaw.Code` + `StatusStaff` (nguồn chính)

```go
// file: backend/internal/model/mg/user_partner.go (line 19-20)
StatusStaff string `json:"statusStaff" bson:"statusStaff"` // "employee" | "not_employee" | "not_verify"
Code        string `json:"code" bson:"code"`                // mã nhân viên do user nhập khi confirm
```

- Được set khi **user tự xác nhận** qua API `POST /users/confirm-is-staff` (`pkg/public/service/user.go:177`)
- Request body: `{ partner, isStaff, code }`
- Nếu ENV `IS_VALIDATE_STAFF_CODE_EXISTS=true` → validate `code` có tồn tại trong bảng `manage-codes` (collection `manage-codes`, model `ManageCodeRaw`)
- Lưu `code` vào `UserPartnerRaw.Code`, set `statusStaff` = `"employee"` hoặc `"not_employee"`

#### Nguồn 2: `UserRaw.StaffCode` (chỉ khi admin tạo user)

```go
// file: backend/internal/model/mg/user.go (line 56-57)
StaffCode   string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`
CompanyCode string `bson:"companyCode,omitempty" json:"companyCode,omitempty"`
```

- Chỉ được set khi **admin tạo user thủ công** (`pkg/admin/service/user.go:124-138`)
- Phần lớn user tự đăng ký → `UserRaw.StaffCode` sẽ **rỗng**

#### Bảng lookup: `manage-codes`

```go
// file: backend/internal/model/mg/manage_code.go
type ManageCodeRaw struct {
    Partner   AppID     // partner nào
    Type      string    // "employee" (ManageCodeApplyForEmployee)
    Code      string    // mã nhân viên hợp lệ
    IsUsed    bool
    UsedBy    AppID
}
```

Danh sách mã nhân viên hợp lệ do admin import sẵn, dùng để validate khi user confirm staff.

#### Kết luận

**Nguồn dữ liệu chính để xác định nhân viên là `UserPartnerRaw`** (bảng `user-partners`), không phải `UserRaw.StaffCode`.

**Hiện tại các trường này chưa được hiển thị trên Dashboard** — chỉ lưu trong DB.

### Nhu cầu

Ops/Admin cần:
- Biết influencer nào là nhân viên (nội bộ) để phân biệt với influencer bên ngoài
- Xem mã nhân viên trực tiếp trên Dashboard (trang danh sách + chi tiết hồ sơ)
- Xuất thông tin nhân viên ra file Excel khi export hồ sơ

---

## 2. Phạm vi thay đổi

### 2.1. Dashboard — Trang danh sách Hồ sơ

**File:** `dashboard/src/components/profiles/profile-columns.tsx`

Thêm 2 cột mới vào bảng danh sách (sau cột Status, trước cột Action):

| Cột | Tên hiển thị (VI) | Tên hiển thị (EN) | Giá trị |
|-----|-------------------|-------------------|---------|
| `isEmployee` | Nhân viên | Employee | "Có" / "Không" (có/không có `staffCode`) |
| `staffCode` | Mã nhân viên | Staff Code | Giá trị `staffCode` hoặc "—" |

**Logic xác định "Nhân viên":**
- `UserPartnerRaw.StatusStaff == "employee"` → hiển thị **"Có"** / **"Yes"**
- Ngược lại (`"not_employee"`, `"not_verify"`, hoặc rỗng) → hiển thị **"Không"** / **"No"**

**Logic hiển thị "Mã nhân viên":**
- Ưu tiên `UserPartnerRaw.Code` (nguồn chính — user tự nhập khi confirm staff)
- Fallback `UserRaw.StaffCode` (trường hợp admin tạo user thủ công)
- Cả hai rỗng → hiển thị "—"

### 2.2. Dashboard — Trang chi tiết Hồ sơ

**File:** `dashboard/src/components/profiles/profile-info-card.tsx`

Thêm section "Thông tin nhân viên" (Employee Info) vào card thông tin, sau section Personal Info:

```
── Thông tin nhân viên ──
Nhân viên:    Có / Không
Mã nhân viên: ABC123
```

Chỉ hiển thị section này khi `statusStaff == "employee"` hoặc có `code`/`staffCode`.

### 2.3. Dashboard — Types

**File:** `dashboard/src/types/profiles.ts`

Thêm vào interface `BrandProfile`:

```typescript
statusStaff?: string;  // Trạng thái nhân viên (từ UserPartnerRaw.statusStaff: "employee" | "not_employee" | "not_verify")
code?: string;         // Mã nhân viên do user nhập (từ UserPartnerRaw.code)
staffCode?: string;    // Mã nhân viên do admin set (từ UserRaw.staffCode, fallback)
companyCode?: string;  // Mã công ty (từ UserRaw.companyCode)
```

### 2.4. Dashboard — Translations

**Files:** `dashboard/src/messages/vi/profiles.json` + `en/profiles.json`

Thêm keys:

```json
// vi
{
  "columns": {
    "isEmployee": "Nhân viên",
    "staffCode": "Mã nhân viên"
  },
  "profileDetail": {
    "employeeInfo": {
      "title": "Thông tin nhân viên",
      "isEmployee": "Nhân viên",
      "staffCode": "Mã nhân viên",
      "yes": "Có",
      "no": "Không"
    }
  }
}

// en
{
  "columns": {
    "isEmployee": "Employee",
    "staffCode": "Staff Code"
  },
  "profileDetail": {
    "employeeInfo": {
      "title": "Employee Info",
      "isEmployee": "Employee",
      "staffCode": "Staff Code",
      "yes": "Yes",
      "no": "No"
    }
  }
}
```

### 2.5. Backend — API response

**File:** `backend/pkg/admin/model/response/` (response cho profile list/detail)

Đảm bảo response API trả về:
- `statusStaff` và `code` từ `UserPartnerRaw` (nguồn chính)
- `staffCode` và `companyCode` từ `UserRaw` (fallback cho trường hợp admin tạo user)

**Kiểm tra xem API hiện tại đã include các trường này chưa** — nếu chưa thì cần bổ sung.

### 2.6. Backend — Export hồ sơ

**File:** `backend/pkg/admin/service/export_user_social.go`

Thêm 2 cột mới vào header Excel (sau cột "Ngày tạo"):

| Cột | Header |
|-----|--------|
| R | Nhân viên (Có/Không) |
| S | Mã nhân viên |

**Header mới (line ~333):**

```go
title := []interface{}{
    // ... (giữ nguyên 17 cột cũ)
    "Nhân viên",      // cột mới
    "Mã nhân viên",   // cột mới
}
```

**Row data (hàm `getUserSocialExcelRowFromPartner`, line ~492):**

```go
// Thêm vào cuối slice return
// Xác định nhân viên dựa trên UserPartnerRaw.StatusStaff (nguồn chính)
isEmployee := "Không"
if raw.StatusStaff == constants.StatusStaffIsEmployee {
    isEmployee = "Có"
}
// Mã nhân viên: ưu tiên UserPartnerRaw.Code, fallback UserRaw.StaffCode
employeeCode := raw.Code
if employeeCode == "" {
    employeeCode = user.StaffCode
}
// ...
return []interface{}{
    // ... (giữ nguyên 17 giá trị cũ)
    isEmployee,
    employeeCode,
}
```

**Áp dụng tương tự cho hàm CSV `getUserSocialRowFromPartner` (line ~451).**

---

## 3. Luồng dữ liệu

```
MongoDB (user-partners collection) ← NGUỒN CHÍNH
  └── statusStaff ("employee" | "not_employee" | "not_verify")
  └── code (mã nhân viên do user nhập khi confirm staff)
       ↓
MongoDB (users collection) ← FALLBACK (chỉ khi admin tạo user)
  └── staffCode, companyCode
       ↓
MongoDB (manage-codes collection) ← LOOKUP (validate khi user confirm)
  └── partner, type, code, isUsed
       ↓
Backend API (profile list/detail)
  └── Response JSON bao gồm statusStaff, code, staffCode
       ↓
Dashboard (profile-columns.tsx + profile-info-card.tsx)
  └── Hiển thị cột "Nhân viên" (dựa trên statusStaff) + "Mã nhân viên" (code || staffCode)

Backend Export (export_user_social.go)
  └── Excel/CSV bao gồm 2 cột mới
```

---

## 4. Không nằm trong phạm vi

- Không thêm chức năng nhập/sửa mã nhân viên từ Dashboard (nếu cần sẽ là PRD riêng)
- Không thêm filter "Chỉ nhân viên" / "Chỉ bên ngoài" (có thể bổ sung sau)
- Không thay đổi model DB (đã có sẵn trường)

---

## 5. Checklist test

- [ ] Trang danh sách Hồ sơ hiển thị 2 cột mới (Nhân viên, Mã nhân viên)
- [ ] Trang chi tiết Hồ sơ hiển thị section "Thông tin nhân viên" khi có staffCode
- [ ] Trang chi tiết Hồ sơ ẩn section khi không có staffCode
- [ ] Export Excel có 2 cột mới với dữ liệu đúng
- [ ] Export CSV có 2 cột mới với dữ liệu đúng
- [ ] Translations hoạt động đúng ở cả tiếng Việt và tiếng Anh
- [ ] Build + type-check pass
