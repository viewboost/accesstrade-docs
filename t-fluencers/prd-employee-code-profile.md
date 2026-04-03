# Thêm thông tin nhân viên vào hồ sơ Influencer

> Thêm 2 trường mới vào trang Hồ sơ trên Dashboard: **"Có phải nhân viên"** và **"Mã nhân viên"**, đồng thời hỗ trợ xuất ra file export.

**Ngày:** 03/04/2026  
**Trạng thái:** Đề xuất  
**Đối tượng đọc:** Business, Ops, PM, Dev

---

## 1. Bối cảnh

### Dữ liệu hiện tại

Model `UserRaw` trong backend (Go) **đã có sẵn** 2 trường liên quan:

```go
// file: backend/internal/model/mg/user.go (line 56-57)
StaffCode   string `bson:"staffCode,omitempty" json:"staffCode,omitempty"`
CompanyCode string `bson:"companyCode,omitempty" json:"companyCode,omitempty"`
```

- `StaffCode`: mã nhân viên (nếu có)
- `CompanyCode`: mã công ty (nếu có)

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
- `staffCode` có giá trị (non-empty) → hiển thị **"Có"** / **"Yes"**
- `staffCode` rỗng/không có → hiển thị **"Không"** / **"No"**

### 2.2. Dashboard — Trang chi tiết Hồ sơ

**File:** `dashboard/src/components/profiles/profile-info-card.tsx`

Thêm section "Thông tin nhân viên" (Employee Info) vào card thông tin, sau section Personal Info:

```
── Thông tin nhân viên ──
Nhân viên:    Có / Không
Mã nhân viên: ABC123
```

Chỉ hiển thị section này khi `staffCode` có giá trị.

### 2.3. Dashboard — Types

**File:** `dashboard/src/types/profiles.ts`

Thêm vào interface `BrandProfile`:

```typescript
staffCode?: string;    // Mã nhân viên (từ UserRaw.staffCode)
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

Đảm bảo response API trả về `staffCode` và `companyCode` từ `UserRaw` khi trả dữ liệu profile. **Kiểm tra xem API hiện tại đã include các trường này chưa** — nếu chưa thì cần bổ sung.

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
isEmployee := "Không"
if user.StaffCode != "" {
    isEmployee = "Có"
}
// ...
return []interface{}{
    // ... (giữ nguyên 17 giá trị cũ)
    isEmployee,
    user.StaffCode,
}
```

**Áp dụng tương tự cho hàm CSV `getUserSocialRowFromPartner` (line ~451).**

---

## 3. Luồng dữ liệu

```
MongoDB (users collection)
  └── staffCode, companyCode
       ↓
Backend API (profile list/detail)
  └── Response JSON bao gồm staffCode
       ↓
Dashboard (profile-columns.tsx + profile-info-card.tsx)
  └── Hiển thị cột "Nhân viên" + "Mã nhân viên"

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
