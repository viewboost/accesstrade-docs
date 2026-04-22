# PRD: Tạo User với Referral Code (Admin)

**Ngày tạo:** 2026-04-08
**Trạng thái:** Implemented
**Project:** Ambassador (accesstrade-projects/ambassabor)

---

## 1. Executive Summary

Cho phép admin tạo user với referral code tùy ý từ admin panel, phục vụ chiến dịch marketing hoặc tạo mã giới thiệu theo yêu cầu. Admin chỉ cần nhập referral code, hệ thống tự generate toàn bộ thông tin user theo naming convention dễ nhận biết và tìm lại.

---

## 2. Bối cảnh & Vấn đề

### Hiện trạng
- Hệ thống referral yêu cầu mã phải thuộc về 1 user thật (`referral.codes` array + `referral.enabled = true`)
- Không có cách tạo mã referral mới từ admin mà không sửa DB trực tiếp

### Vấn đề
Khi cần tạo mã referral cho chiến dịch marketing (VD: `tcb2024`), phải can thiệp MongoDB trực tiếp — rủi ro, không có audit trail, không scalable.

### Các phương án đã đánh giá

| # | Phương án | Ưu điểm | Nhược điểm | Kết luận |
|---|-----------|---------|------------|----------|
| 1 | `SYSTEM_REFERRAL_CODE` env var | Có sẵn | Vẫn cần user thật sở hữu mã | Loại |
| 2 | Sửa DB trực tiếp (MongoDB) | Nhanh | Rủi ro, không audit trail | Loại |
| 3 | **Tạo tính năng trên admin** | An toàn, có audit, dễ dùng | Cần code mới | **Chọn** |

---

## 3. User Personas

| Persona | Mô tả | Mục tiêu |
|---------|-------|----------|
| **Admin (Root)** | Staff có quyền root trên admin panel | Tạo referral code cho chiến dịch marketing |
| **End User** | Người dùng platform Ambassador | Nhập mã referral khi đăng ký |

---

## 4. Functional Requirements

### FR-001: Tạo User với Referral Code

**Priority:** Must Have

**Description:**
Admin nhập referral code duy nhất → hệ thống tạo user mới với mã referral đó. Tất cả thông tin user khác được tự generate.

**Acceptance Criteria:**
- [x] Admin nhập referral code vào modal form trên trang user list
- [x] Hệ thống validate referral code (required, 2-50 ký tự)
- [x] Hệ thống check referral code chưa user nào dùng
- [x] Hệ thống tạo user với thông tin generate theo naming convention
- [x] User mới có `referral.enabled = true` và `referral.codes` chứa mã đã nhập

---

### FR-002: Naming Convention cho User Generate

**Priority:** Must Have

**Description:**
User được tạo phải có naming convention rõ ràng, dễ nhận biết và tìm lại.

**Acceptance Criteria:**
- [x] Name: `ref-{refCode}` (VD: `ref-tcb2024`)
- [x] Email: `ref-{refCode}@system.local` (VD: `ref-tcb2024@system.local`)
- [x] Password: hash của referral code
- [x] Gender: `male` (default)
- [x] System code: random 7 ký tự (unique)
- [x] `referral.codes`: `[systemCode, refCode]`
- [x] Hashtag: `#{systemCode}`
- [x] Tìm lại bằng search `ref-` trong admin hoặc query `{"name": /^ref-/}`

---

### FR-003: Validate Referral Code Trùng

**Priority:** Must Have

**Description:**
Không cho phép tạo referral code đã tồn tại trong hệ thống.

**Acceptance Criteria:**
- [x] Nếu referral code đã có user khác dùng → trả lỗi "Mã giới thiệu không hợp lệ"
- [x] Check trên field `referral.codes` của tất cả users

---

### FR-004: Audit Log

**Priority:** Must Have

**Description:**
Ghi log mỗi lần admin tạo user referral.

**Acceptance Criteria:**
- [x] Audit log ghi nhận staff ID, user ID, message chứa referral code
- [x] Format: `"Admin created referral user with code: {refCode}"`

---

### FR-005: Phân quyền Root Only

**Priority:** Must Have

**Description:**
Chỉ admin có quyền Root mới được tạo user referral.

**Acceptance Criteria:**
- [x] API yêu cầu `RequiredLogin` + `IsRoot` middleware
- [x] Non-root admin không thấy hoặc không gọi được API

---

## 5. Non-Functional Requirements

### NFR-001: Performance

**Priority:** Must Have

**Description:**
API tạo user phải response nhanh.

**Acceptance Criteria:**
- [x] Response time < 500ms (single MongoDB insert + code generation)
- [x] Audit log chạy async (goroutine) không block response

---

### NFR-002: Security

**Priority:** Must Have

**Description:**
API phải được bảo vệ bằng authentication và authorization.

**Acceptance Criteria:**
- [x] JWT authentication required
- [x] Root-only authorization
- [x] Password được hash bằng bcrypt (cost 12)

---

### NFR-003: Data Integrity

**Priority:** Must Have

**Description:**
Đảm bảo không tạo duplicate referral code.

**Acceptance Criteria:**
- [x] Check `referral.codes` unique trước khi insert
- [x] System code được generate unique (recursive check)

---

## 6. Epics

### EPIC-001: Backend API - Tạo User với Referral Code

**Description:** API endpoint cho admin tạo user referral

**Functional Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005

**Files đã sửa:**
| File | Thay đổi |
|------|----------|
| `backend/pkg/admin/model/request/user.go` | `CreateUserBody` struct (field `ref`) |
| `backend/pkg/admin/model/response/user.go` | `CreateUserResponse` struct |
| `backend/pkg/admin/router/routevalidation/user.go` | `CreateUser` validation middleware |
| `backend/pkg/admin/handler/user.go` | `Create` handler method |
| `backend/pkg/admin/service/user.go` | `Create` service + `generateCode` helper |
| `backend/pkg/admin/router/user.go` | `POST /api/admin/users` route |

**Priority:** Must Have

---

### EPIC-002: Frontend UI - Modal Tạo Referral User

**Description:** UI trên admin panel cho admin nhập referral code và tạo user

**Functional Requirements:** FR-001

**Files đã sửa:**
| File | Thay đổi |
|------|----------|
| `admin/src/configs/api.ts` | `user.create` endpoint config |
| `admin/src/services/user.ts` | `create` service function |
| `admin/src/pages/user/type.d.ts` | `create` effect + `CreateUser` type |
| `admin/src/pages/user/model.ts` | `create` DVA effect |
| `admin/src/pages/user/index.tsx` | Nút "Tạo User" + state management |
| `admin/src/pages/user/components/modal-create.tsx` | **NEW** - Modal form (1 input) |

**Priority:** Must Have

---

## 7. Kiến trúc kỹ thuật

### Backend Flow
```
POST /api/admin/users
  → RequiredLogin middleware (JWT validation)
  → IsRoot middleware (root-only access)
  → CreateUser validation middleware (bind + validate body)
  → Create handler (extract payload, call service)
  → Create service:
      1. Validate referral code unique
      2. Generate 7-char system code (unique)
      3. Build user document (naming convention)
      4. Insert to MongoDB
      5. Audit log (async)
  → Response 200 {_id, name, code}
```

### Frontend Flow
```
User list page → Click "Tạo User"
  → Modal open (1 input: referral code)
  → Submit → form.validateFields()
  → dispatch('userModel/create', {body: {ref}})
  → DVA effect → serviceUser.create(body)
  → API call POST /users
  → Success → notification.success + close modal + refresh list
  → Error → notification.error
```

### Data Model (MongoDB `users` collection)
```json
{
  "_id": ObjectId("..."),
  "name": "ref-tcb2024",
  "email": "ref-tcb2024@system.local",
  "hashedPassword": "$2a$12$...",
  "info": { "email": "ref-tcb2024@system.local", "gender": "male" },
  "code": "abc1234",
  "hashtag": "#abc1234",
  "referral": {
    "enabled": true,
    "enabledAt": ISODate("2026-04-08T..."),
    "codes": ["abc1234", "tcb2024"]
  },
  "status": "active",
  "searchString": "ref-tcb2024 ref-tcb2024@system.local abc1234 tcb2024",
  "createdAt": ISODate("2026-04-08T..."),
  "updatedAt": ISODate("2026-04-08T...")
}
```

---

## 8. Cách tìm lại User Referral

| Cách | Query/Action |
|------|-------------|
| Admin UI | Search keyword `ref-` trong user list |
| MongoDB | `db.users.find({"name": /^ref-/})` |
| MongoDB | `db.users.find({"referral.codes": "tcb2024"})` |
| MongoDB | `db.users.find({"email": /^ref-.*@system\.local$/})` |

---

## 9. Assumptions

- Admin chỉ cần tạo mã referral, không cần quản lý user referral (edit/delete)
- User referral không cần phone number (field phone = null)
- Naming convention `ref-{code}` đủ để phân biệt với user thật
- Email `@system.local` không conflict với email thật

---

## 10. Out of Scope

- Quản lý (edit/delete) user referral từ admin
- Bulk import referral codes
- Expiry date cho referral code
- Dashboard thống kê referral performance
- Tự tạo referral code không cần user (thay đổi core referral logic)

---

## 11. Traceability Matrix

| Epic | FRs | Story Estimate | Priority |
|------|-----|----------------|----------|
| EPIC-001: Backend API | FR-001, FR-002, FR-003, FR-004, FR-005 | 3 stories | Must Have |
| EPIC-002: Frontend UI | FR-001 | 2 stories | Must Have |

### Prioritization Summary
- **Must Have FRs:** 5/5 (100%)
- **Must Have NFRs:** 3/3 (100%)
- **Epics:** 2
- **Estimated Stories:** 5

---

## 12. Open Questions

1. Có cần giới hạn số lượng referral user mà 1 admin có thể tạo không?
2. Có cần thêm field đánh dấu user này là "system/referral user" (không phải user thật) không?
3. Khi referral code hết hiệu lực, có cần mechanism để disable user referral không?
