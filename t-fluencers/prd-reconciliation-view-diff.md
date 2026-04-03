# Thêm cột "Chênh lệch View" vào file export đối soát

> Thêm cột **"Chênh lệch View"** vào file Excel export đối soát, tính bằng `View (Snapshot) - View cuối kỳ`.

**Ngày:** 03/04/2026  
**Trạng thái:** Đề xuất  
**Đối tượng đọc:** Business, Ops, PM, Dev

---

## 1. Bối cảnh

### File export đối soát hiện tại

**File:** `backend/pkg/admin/service/export_reconciliation.go`

Sheet "Content" hiện có các cột liên quan đến View:

| Cột | Header | Nguồn dữ liệu |
|-----|--------|---------------|
| G | Số view | `rc.Content.TotalViewEnd` |
| L | Số view đầu kỳ | `rc.Content.TotalViewBegin` |
| M | Số view cuối kỳ | `rc.Content.TotalViewEnd` |
| O | Số view chờ đối soát trong kỳ | `rc.Content.TotalViewPending` |
| R | View (Snapshot) | `snapshot.ViewCount` |

### Nhu cầu

Ops cần biết **chênh lệch giữa View snapshot (tại thời điểm đối soát) và View cuối kỳ** để đánh giá:
- View có tăng/giảm bất thường không sau khi kết thúc kỳ đối soát
- Phát hiện các bài đăng có view giảm đáng ngờ (có thể do gian lận view)
- Hỗ trợ quyết định duyệt/từ chối nhanh hơn

### Công thức

```
Chênh lệch View = View (Snapshot) - View cuối kỳ
               = snapshot.ViewCount - rc.Content.TotalViewEnd
```

- **Giá trị dương**: view tăng thêm sau cuối kỳ (bình thường)
- **Giá trị âm**: view giảm so với cuối kỳ (cần kiểm tra)
- **Giá trị 0**: không thay đổi
- **Rỗng**: không có snapshot data

---

## 2. Phạm vi thay đổi

### 2.1. Backend — Export file Excel

**File:** `backend/pkg/admin/service/export_reconciliation.go`

#### Header (line ~80)

Thêm cột **"Chênh lệch View"** ngay sau cột **"View (Snapshot)"** (cột R):

```go
file.SetSheetRow(SheetContent, "A1", &[]interface{}{
    "Mã nội dung",                    // A
    "Mã người dung",                  // B
    "Tên người dung",                 // C
    "Link",                           // D
    "Nguồn nội dung",                 // E
    "Tiêu đề",                        // F
    "Số view",                        // G
    "Số like",                        // H
    "Số comment",                     // I
    "Ngày phát hành",                 // J
    "Ngày gửi",                       // K
    "Số view đầu kỳ",                // L
    "Số view cuối kỳ",               // M
    "Tỉ lệ engagement",              // N
    "Số view chờ đối soát trong kỳ", // O
    "Tổng tiền đối soát trong kỳ",   // P
    "Trạng thái đối soát",           // Q
    "View (Snapshot)",                // R
    "Chênh lệch View",               // S  ← MỚI
    "Hashtags (Snapshot)",            // T  (cũ: S)
    "Trạng thái snapshot",           // U  (cũ: T)
    "Thời điểm snapshot",            // V  (cũ: U)
    "Video truy cập được",           // W  (cũ: V)
    "Hashtag đúng",                  // X  (cũ: W)
    "View không giảm",               // Y  (cũ: X)
    "Admin xác nhận",                // Z  (cũ: Y)
    "Đề xuất",                       // AA (cũ: Z)
})
```

#### Row data (hàm `getRecordReconciliationItemContent`, line ~306)

Thêm giá trị chênh lệch view sau `snapshotView`:

```go
// Tính chênh lệch view
var viewDiff interface{} = ""
if snapshot != nil {
    viewDiff = snapshot.ViewCount - rc.Content.TotalViewEnd
}

return []interface{}{
    content.ID.Hex(),
    user.ID.Hex(),
    user.Name,
    content.Link,
    content.Source,
    content.Title,
    rc.Content.TotalViewEnd,
    rc.Content.TotalLike,
    rc.Content.TotalComment,
    util.TimeOfDayInHCM(content.PublishAt).Format(constants.FormatTimeDDMMYYYYHHmm),
    util.TimeOfDayInHCM(content.CreatedAt).Format(constants.FormatTimeDDMMYYYYHHmm),
    rc.Content.TotalViewBegin,
    rc.Content.TotalViewEnd,
    rc.Content.Engagement,
    rc.Content.TotalViewPending,
    rc.Content.TotalCashPending,
    rc.Status,
    snapshotView,
    viewDiff,           // ← MỚI: chênh lệch view
    snapshotHashtag,
    crawlStatus,
    crawledAt,
    checklistValues[0],
    checklistValues[1],
    checklistValues[2],
    checklistValues[3],
    classification,
}
```

---

## 3. Dữ liệu nguồn

| Thành phần | Nguồn | Type |
|------------|-------|------|
| View (Snapshot) | `ReconciliationSnapshotRaw.ViewCount` | `int64` |
| View cuối kỳ | `ReconciliationItemContent.TotalViewEnd` | `int64` |
| Chênh lệch | `ViewCount - TotalViewEnd` | `int64` |

Cả 2 giá trị đều đã có sẵn trong hàm `getRecordReconciliationItemContent` — không cần query thêm DB.

---

## 4. Ví dụ output

| ... | View cuối kỳ (M) | ... | View (Snapshot) (R) | Chênh lệch View (S) | ... |
|-----|------------------|-----|--------------------|--------------------|-----|
| ... | 10,000 | ... | 12,500 | 2,500 | ... |
| ... | 5,000 | ... | 4,800 | -200 | ... |
| ... | 8,000 | ... | 8,000 | 0 | ... |
| ... | 3,000 | ... | _(không có snapshot)_ | _(rỗng)_ | ... |

---

## 5. Không nằm trong phạm vi

- Không thêm cột này vào giao diện Dashboard (chỉ trong file export)
- Không thêm cảnh báo/highlight tự động cho giá trị âm (có thể bổ sung sau)
- Không thay đổi model DB hay logic đối soát

---

## 6. Lưu ý kỹ thuật

- **Thứ tự cột thay đổi**: các cột sau "View (Snapshot)" đều dịch sang phải 1 vị trí. Nếu có code/script nào đọc file export theo vị trí cột cố định (column index), cần cập nhật theo.
- **Không ảnh hưởng Sheet Milestone**: chỉ thay đổi Sheet Content.

---

## 7. Checklist test

- [ ] File export có cột "Chênh lệch View" đúng vị trí (sau "View (Snapshot)")
- [ ] Giá trị tính đúng: `snapshot.ViewCount - rc.Content.TotalViewEnd`
- [ ] Khi không có snapshot → cột rỗng (không phải 0)
- [ ] Các cột sau dịch đúng, không bị mất data
- [ ] Sheet Milestone không bị ảnh hưởng
- [ ] Header + row data khớp số cột
