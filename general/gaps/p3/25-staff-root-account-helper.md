# Gap #25 — TCB/Ambassador không có helper `GetRoot()` cho staff root account (vCreator có)

> **Priority**: ⚪ **P3** (reclassified P1→P3 2026-05-07 — không có business impact)
> **Source**: Initial gap-analysis #25
> **Direction port**: vCreator → TCB/Ambassador
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Trong các flow tự động (webhook, cron, batch), hệ thống cần "actor" là **root staff account** để gán vào audit log. vCreator có helper function `Staff().GetRoot()` đóng gói logic này. TCB và Ambassador chưa có → mỗi flow tự động đều phải viết lại raw query inline.

→ Đây là **tech debt cleanup**, không có business impact trực tiếp. User confirm: *"không có ý nghĩa về biz lắm"*.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Helper `Staff().GetRoot()` | ❌ | ✅ | ❌ |
| Cách lấy root staff hiện tại | Raw bson query inline mỗi caller | Helper function | Raw bson query inline |
| Filter `active=true` | ❌ Không | ✅ Có | ❌ Không |
| Cảnh báo nếu multi-root | ❌ | ✅ | ❌ |
| Sort `createdAt asc` (kết quả ổn định) | ❌ | ✅ | ❌ |

## Hệ quả

- Tech debt: code repeat ở mọi caller automation
- Edge case: TCB/Amb có thể lấy nhầm root staff đã bị disable (không filter `active`)
- Silent fail: không có error handling khi root staff không tồn tại

→ Defer P3 vì các issue này hiếm xảy ra, chỉ cleanup khi có resource rảnh.

## Giải pháp

Port `staff.go` (62 LOC) từ vCreator sang TCB/Amb + refactor caller `opshub_webhook.go` dùng helper. Effort: ~4-6 giờ mỗi sản phẩm.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

vCreator có service `staff.go` (62 LOC) với 1 hàm `GetRoot()`. TCB/Ambassador không có — caller dùng raw bson query inline ở `opshub_webhook.go`. Port = copy file + refactor caller.

## Verify code

### vCreator (`internal/service/staff.go` — source of truth)

```go
type StaffInterface interface {
    GetRoot(ctx context.Context) (*modelmg.StaffRaw, error)
}

func (s staffServiceImpl) GetRoot(ctx) (*modelmg.StaffRaw, error) {
    filter := bson.M{"isRoot": true, "active": true}
    count := StaffDAO.CountByCondition(ctx, ..., filter)
    if count == 0 { return nil, errors.New("root staff not found") }
    if count > 1 { fmt.Println("WARNING: multiple root staff, using earliest created") }

    sortOpts := options.FindOne().SetSort(bson.D{{"createdAt", 1}})
    staff := new(modelmg.StaffRaw)
    err := StaffDAO.FindOne(ctx, staff, filter, sortOpts)
    return staff, err
}
```

**vCreator callers**:
- `pkg/admin/service/staff_removal_cron.go`
- `pkg/admin/service/user.go`
- `pkg/admin/service/employee_registry_cancel.go`
- `pkg/public/service/opshub_webhook.go`

### TCB/Ambassador (`pkg/public/service/opshub_webhook.go` — inline raw query)

```go
// Find root staff for system action
rootStaff := new(modelmg.StaffRaw)
_ = daomongodb.StaffDAO().GetShare().FindOne(ctx, rootStaff, bson.M{"isRoot": true})
// ← Không filter active, không error handling, không sort
staff := modelmg.StaffInfo{
    ID:     rootStaff.ID,  // ← có thể là zero nếu không tìm thấy
    Name:   rootStaff.Name,
    IsRoot: true,
}
```

→ Code identical giữa TCB và Ambassador (copy-paste pattern).

## Đề xuất implementation

1. **Copy `internal/service/staff.go`** từ vCreator sang TCB + Ambassador (62 LOC)
2. **Refactor caller** ở `pkg/public/service/opshub_webhook.go`:
   ```go
   rootStaff, err := internalservice.Staff().GetRoot(ctx)
   if err != nil {
       fmt.Println("opshub: cannot find root staff:", err)
       return
   }
   ```
3. **Test**: verify webhook flow vẫn hoạt động với helper

**Total effort**: ~4-6 giờ mỗi sản phẩm.

## Risks + mitigations

1. **TCB/Amb chưa có root staff trong DB** → `GetRoot()` trả error → flow break
   - **Mitigation**: kiểm tra DB production trước khi deploy. Nếu chưa có root staff → seed manual.
2. **Multiple root staff trong DB** → vCreator pattern dùng earliest. TCB/Amb hiện tại random.
   - **Mitigation**: vCreator pattern an toàn hơn. Migration verify chỉ có 1 root.

## Files referenced

**vCreator (source of truth)**: `internal/service/staff.go` (62 LOC)

**TCB/Ambassador (target — chưa có)**:
- KHÔNG có `internal/service/staff.go`
- Caller inline ở `pkg/public/service/opshub_webhook.go`

## Lịch sử phân loại

- **Initial**: P1 (Total 13)
- **Reclassified P3 (2026-05-07)**: User confirm *"cái này thì P3, làm sau cũng được, nó ko có ý nghĩa vì vê biz lắm"* — tech debt cleanup, không có business impact.
