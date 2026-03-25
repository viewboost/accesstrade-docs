# Rule: Content Not Found - Crawl Fail Flow

## Tổng quan

Khi hệ thống crawl content (TikTok/Facebook/YouTube) mà không lấy được dữ liệu, hệ thống sẽ đánh dấu và xử lý theo cơ chế tăng dần: tiếp tục crawl → ngừng crawl → recheck → gắn warning tag.

## Field chính

- **`totalNotFound`** (int) - Số lần crawl không tìm thấy content, lưu trong collection `Content`

## Flow xử lý

```
Crawl content (cron)
    ├── Thành công → totalNotFound = 0 (reset)
    └── Fail (data nil / statusCode = 90) → totalNotFound += 1
                │
                ├── totalNotFound < 3 → Vẫn được crawl bình thường
                │
                ├── totalNotFound >= 3 → Loại khỏi vòng crawl chính
                │       │
                │       └── RecheckVideoNotFound (cron mỗi 3h)
                │           │   Query: totalNotFound >= 3 AND <= 5
                │           │   Dùng TikTok oembed API kiểm tra
                │           ├── Video public → totalNotFound = 0 (reset)
                │           └── Video vẫn mất → totalNotFound += 1
                │
                └── totalNotFound = 6
                        └── AutoRejectContentNotFound (cron 4:30 AM daily)
                            └── Gắn warning tag "không quét được video"
```

## Ngưỡng xử lý

| `totalNotFound` | Hành động |
|---|---|
| 0 | Bình thường |
| 1-2 | Vẫn được crawl, chờ retry |
| 3-5 | Loại khỏi crawl chính. `RecheckVideoNotFound` kiểm tra lại mỗi 3 giờ bằng TikTok oembed API |
| 6 | `AutoRejectContentNotFound` gắn warning tag "không quét được video" (chạy 4:30 AM hàng ngày) |

## Cron Jobs

| Job | Schedule | Mô tả |
|---|---|---|
| Crawl content | Theo cấu hình event | Crawl data từ social platform, tăng `totalNotFound` nếu fail |
| `RecheckVideoNotFound` | `0 0 */3 * * *` (mỗi 3h) | Recheck content có `totalNotFound` 3-5 bằng TikTok oembed |
| `AutoRejectContentNotFound` | `0 30 4 * * *` (4:30 AM) | Gắn warning tag cho content có `totalNotFound = 6` |

## Logic tag

- Khi gắn tag "không quét được video" → `totalNotFound` giữ nguyên = 6
- Khi admin **xoá** tag "không quét được video" → `totalNotFound` reset về 0 (content sẽ được crawl lại)

## Source code

| Chức năng | File |
|---|---|
| Crawl chính (tăng `totalNotFound`) | `techcombank/backend/pkg/public/service/schedule.go` |
| Callback crawl (statusCode 90) | `techcombank/backend/pkg/public/service/schedule.go` |
| `RecheckVideoNotFound` | `techcombank/backend/pkg/admin/service/shedule.go` |
| `AutoRejectContentNotFound` | `techcombank/backend/pkg/admin/service/shedule.go` |
| Logic gắn/xoá tag → reset `totalNotFound` | `techcombank/backend/pkg/admin/service/content.go` |
| Tag constants | `techcombank/backend/internal/constants/tag.go` |
| Model `Content` (`totalNotFound` field) | `techcombank/backend/internal/model/mg/content.go` |

## Lưu ý

1. **Tên hàm gây hiểu lầm:** `AutoRejectContentNotFound` thực tế **không reject** (không đổi status sang `rejected`), chỉ gắn warning tag
2. **Chỉ recheck TikTok:** `RecheckVideoNotFound` và `AutoRejectContentNotFound` chỉ xử lý source TikTok. Facebook/YouTube chỉ có bước tăng `totalNotFound` nhưng không có recheck hay auto tag
3. **Ngưỡng hardcode:** Các ngưỡng 3, 5, 6 được hardcode trực tiếp trong code, không dùng config
