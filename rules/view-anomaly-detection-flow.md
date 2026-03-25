# Rule: View Anomaly Detection - Phát hiện View bất thường

## Tổng quan

Hệ thống có 4 cơ chế phát hiện view tăng/giảm bất thường trên content, hoạt động ở các tầng khác nhau: real-time alert, daily warning tag, daily audit, và reconciliation checklist.

## Flow tổng thể

```
Mỗi lần Crawl
    │
    ├─[1] View drop to zero (real-time)
    │       View crawl = 0 nhưng trước đó > 0?
    │       └── Gửi cảnh báo Telegram ngay
    │
    ├─[2] ContentFlow (lưu delta view)
    │       └── Tổng hợp → ContentAnalyticDaily
    │               │
    │               └─[3] Audit VIEW_INVALID (cron 4:00 AM)
    │                   So khớp tổng Flow vs Daily
    │                   └── Sai lệch → auditStatus = "in_valid", codeReason = "VIEW_INVALID"
    │
    ├─[4] RateView = totalViewOld / totalDay (baseline trung bình)
    │       └── AddWarningTagForContent (cron 5:30 AM)
    │           ├── View hôm qua < 1000 → bỏ qua
    │           ├── RateView = 0 & view >= 1000 → tag LOW (xám)
    │           ├── Rate > 5x → tag HIGH (đỏ)
    │           └── Rate > 2x → tag MEDIUM (vàng)
    │
    └─[5] Reconciliation (đối soát)
            └── Checklist "view_not_dropped"
                View giảm so với đã ghi nhận?
                └── Có → needs_review (warning)
```

## Cơ chế 1: View Drop to Zero (Real-time)

**Trigger:** Mỗi lần crawl content
**Điều kiện:** Content đang có view > 0 nhưng kết quả crawl trả về view = 0
**Hành động:** Gửi cảnh báo Telegram ngay lập tức (message `MsgRequestStatisticInvalid`)
**Cũng check:** Nếu Like và Comment đều = 0 nhưng trước đó có dữ liệu → cảnh báo tương tự

| Item | Chi tiết |
|---|---|
| File | `techcombank/backend/internal/service/content_flow.go` (hàm `CreateFlow`, dòng 35-138) |
| Telegram templates | `techcombank/backend/internal/module/telegram/telegram.go` |

## Cơ chế 2: Warning Tag - View tăng đột biến (Daily)

**Trigger:** Cron 5:30 AM hàng ngày (`AddWarningTagForContent`)
**Baseline:** `RateView = totalViewOld / totalDay` (tốc độ tăng trung bình view/ngày)

### Điều kiện lọc bài viết

Bài viết phải thỏa **tất cả**:
1. Event đang active, trong thời gian diễn ra
2. Status = `waiting_approved` hoặc `approved`
3. Tuổi bài >= 3 ngày
4. `isRemarkTag = false` (chưa từng được admin review)

### Ngưỡng gắn tag

| Tag | Constant | Điều kiện | Màu | Ý nghĩa |
|---|---|---|---|---|
| **Cảnh báo Thấp** | `CheatingWarningLow` | View hôm qua >= 1000 & `RateView == 0` | Xám `#9E9E9E` | Bài gần như không có view trước đó, đột ngột tăng mạnh |
| **Cảnh báo Cao** | `CheatingWarningHigh` | `Rate > 5` (gấp > 5x trung bình) | Đỏ `#F44336` | Tăng trưởng đột biến mạnh |
| **Cảnh báo Vừa** | `CheatingWarningMedium` | `Rate > 2` (gấp > 2x trung bình) | Vàng `#FFEB3B` | Tăng trưởng đáng ngờ |

**Công thức Rate:**
```
Rate = View tăng trưởng hôm qua / RateView (trung bình quá khứ)
```

### Hành động khi gắn tag

1. Thêm warning tag tương ứng vào `warningTags`
2. Đánh dấu `isRemarkTag = true` (không quét lại)
3. Ghi audit log: "Đã đánh thêm tag [Tên Tag]"
4. Gửi tin nhắn tổng kết qua Telegram

| Item | Chi tiết |
|---|---|
| Cron definition | `techcombank/backend/pkg/admin/schedule/init.go` |
| Job logic | `techcombank/backend/pkg/admin/service/shedule.go` (hàm `AddWarningTagForContent`, dòng 141-259) |
| Core logic | `techcombank/backend/internal/service/content.go` (hàm `WarningTagContent`, dòng 308-372) |
| Tag constants | `techcombank/backend/internal/constants/tag.go` |
| Docs chi tiết | `techcombank/backend/documents/DOCS_WARNING_TAG_RULES.md` |

## Cơ chế 3: Audit VIEW_INVALID (Daily)

**Trigger:** Cron 4:00 AM hàng ngày (`AuditContentAnalytic`)
**Logic:** So sánh tổng view trong `ContentFlow` với `ContentAnalyticDaily.View.Value`
**Hành động:** Nếu không khớp → `auditStatus = "in_valid"`, `codeReason = "VIEW_INVALID"`

| Item | Chi tiết |
|---|---|
| File | `techcombank/backend/internal/service/content_analytic_daily.go` (hàm `Audit`, dòng 268-351) |
| Model | `ContentAnalyticDailyRaw` (field `AuditStatus`, `CodeReason`) |

## Cơ chế 4: Reconciliation Checklist - View Not Dropped

**Trigger:** Khi chạy reconciliation checklist (đối soát)
**Logic:** So sánh `snapshot.ViewCount` (view mới nhất từ crawl) vs `TotalViewEnd` (view đã ghi nhận khi khóa)
**Hành động:** Nếu view giảm → `ChecklistStatusUnverified`, `FailLevel: warning`, classification = `needs_review`

| Item | Chi tiết |
|---|---|
| File | `techcombank/backend/internal/service/reconciliation_checklist.go` (hàm `evaluateByView`, dòng 255-338) |
| Checklist code | `view_not_dropped` |
| Message | "View giam so voi da ghi nhan" |

## Cron Schedule tổng hợp

| Job | Schedule | Cơ chế |
|---|---|---|
| Crawl content | Theo event | View drop to zero → Telegram alert |
| `AuditContentAnalytic` | `0 0 4 * * *` (4:00 AM) | Audit VIEW_INVALID |
| `AddWarningTagForContent` | `0 30 5 * * *` (5:30 AM) | Warning tag cheating |

## Lưu ý

1. **Chỉ detect view TĂNG đột biến:** Warning tag (cơ chế 2) chỉ phát hiện spike tăng. View giảm dần đều (ví dụ bot view hết hạn) không bị flag
2. **Ngưỡng 1000 hardcode:** Content nhỏ tăng gấp 10x nhưng < 1000 view sẽ không bị tag
3. **`isRemarkTag` là escape hatch:** Sau khi admin review, content không bị check lại. Không có audit trail ai đã remark
4. **View drop to zero chỉ alert Telegram:** Không gắn tag hay đổi status, phụ thuộc vào người theo dõi channel
5. **Các ngưỡng 2x, 5x, 1000 đều hardcode** trong code, không có config
