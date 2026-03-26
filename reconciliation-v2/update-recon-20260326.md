# Reconciliation V2 — Cập nhật đối soát (26/03/2026)

**Branch:** `fix/recon` · 10 commits (`e2b086b6..fcd013ee`)

---

## 1. Crawl Engine

- **Post-expiry crawl** (`e2b086b6`): Thêm cron `RunPostExpiryCrawl` chạy 2:00 AM, tự động crawl lại snapshot cho event đã hết hạn. Chuyển sang `GetDataCore` dùng đúng `CORE_CONTENT_CATCHER_BASE_URL`.
- **Gộp logic crawl** (`1f1c05dc`): Consolidate code crawl từ 2 file về 1, bỏ code trùng lặp (~20 dòng giảm).
- **Batch size = 5 + force crawl** (`8ecd63e5`): Giảm batch xuống 5 URLs/lần tránh quá tải. Thêm param `force` cho makeup crawl API.
- **Tách CrawlSuccess khỏi StatusCode** (`c2bfcaf7`): Thêm field `CrawlSuccess` riêng. Trước đó content ID khớp nhưng HTTP status ≠ 200 vẫn bị đánh fail — giờ đã sửa.
- **UUID request ID** (`5da4462a`): Gắn UUID mỗi request tới content-catcher để trace/debug. Refine content matching logic.

## 2. Admin Reject Flow

- **Force reject + confirmation** (`f4d484ed`, `5e8acdb7`): Admin reject item bất kể kết quả checklist. Nút "Từ chối" hiển thị ở mọi trạng thái (`has_unverified`, `all_pass`, `has_fail`). Dialog bắt buộc nhập lý do.
- **Auto-fill lý do reject** (`f3408d55`): Tự động điền lý do từ checklist items bị fail (qua `CHECKLIST_FAIL_REASONS` map). Admin chỉnh sửa trước khi submit.

## 3. Filter & Validation

- **Classification filter** (`cc43b0cb`): Thêm bộ lọc phân loại content cho admin API.
- **Fallback hashtag check** (`fcd013ee`): Fix bug checklist `hashtag_present` luôn fail khi content-catcher trả `HashTag = null`. Fallback kiểm tra hashtag từ description text.
