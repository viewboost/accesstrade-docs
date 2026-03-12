# PRD: Blacklist Keyword & Auto-Approve Rule

## 1. Blacklist Keyword Management

### 1.1 Tổng quan

Quản lý danh sách từ khóa bị cấm (blacklist) áp dụng **toàn cục** cho tất cả thử thách. Khi nội dung của influencer chứa từ khóa blacklist, hệ thống sẽ tự động phát hiện và gắn tag cảnh báo.

### 1.2 Data Model

| Field | Type | Mô tả |
|-------|------|-------|
| `keyword` | string | Từ khóa gốc (giữ nguyên dấu, khoảng trắng) |
| `searchString` | string | Bỏ dấu, giữ khoảng trắng → dùng để search |
| `compareString` | string | Bỏ dấu + bỏ khoảng trắng → dùng để phát hiện trùng lặp (UNIQUE) |
| `active` | boolean | Trạng thái kích hoạt |
| `createdBy` / `updatedBy` | ObjectID → Staff | Người tạo / cập nhật |
| `createdAt` / `updatedAt` | datetime | Thời gian |

**Database indexes:**
- `searchString` — hỗ trợ regex search
- `compareString` (UNIQUE) — chống trùng lặp
- `active` — lọc theo trạng thái
- `createdAt` — sắp xếp

### 1.3 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/blacklist-keywords` | Danh sách (phân trang, lọc keyword + active) |
| POST | `/blacklist-keywords` | Tạo mới |
| PUT | `/blacklist-keywords/:id` | Cập nhật |
| DELETE | `/blacklist-keywords/:id` | Xóa |
| PATCH | `/blacklist-keywords/:id/status` | Bật/tắt trạng thái |
| POST | `/blacklist-keywords/import-excel` | Import từ file Excel |

Tất cả endpoints yêu cầu đăng nhập + quyền Admin.

### 1.4 Business Logic

**Tạo / Cập nhật:**
1. Nhận `keyword` từ request
2. Generate `searchString` = bỏ dấu tiếng Việt, giữ khoảng trắng
3. Generate `compareString` = bỏ dấu + bỏ tất cả khoảng trắng
4. Kiểm tra trùng lặp qua `compareString` → nếu trùng, trả lỗi
5. Lưu vào DB

**Import Excel:**
1. Parse file `.xlsx` / `.xls` (cột A = keyword)
2. Bỏ qua dòng header (dòng 1)
3. Với mỗi dòng:
   - Bỏ qua nếu keyword rỗng
   - Generate `compareString`
   - Kiểm tra trùng trong batch hiện tại (map `seen`)
   - Kiểm tra trùng trong DB
   - Nếu mới → thêm vào batch
4. Bulk insert tất cả keyword mới
5. Trả kết quả: `total`, `created`, `skipped`, `skippedKeywords[]`

### 1.5 Tích hợp với Content Moderation

Khi hệ thống đánh giá nội dung qua LLM (Vertex AI / Gemini):

1. **Truyền blacklist vào prompt:** Danh sách keyword active được đưa vào system instruction của LLM
2. **LLM kiểm tra:** So khớp linh hoạt (không phân biệt hoa/thường, có/không dấu, biến thể từ)
3. **Kết quả trả về:**
   - `containsBlacklist`: true/false
   - `blacklistMatches`: danh sách keyword bị phát hiện
4. **Trừ điểm:**
   - Nhẹ (1-2 keyword, ngữ cảnh trung lập): -15 đến -25 điểm
   - Trung bình (3-5 keyword hoặc keyword nhạy cảm): -30 đến -50 điểm
   - Nặng (5+ keyword hoặc tập trung vào chủ đề cấm): tối đa 20 điểm
5. **Gắn tag:** Nội dung chứa blacklist được gắn tag `content_blacklist`

### 1.6 Giao diện Admin

**Trang chính** (`/blacklist-keyword`):
- Menu sidebar: "Blacklist"
- Nút "Tạo mới" + "Import Excel"
- Bộ lọc: ô search keyword + dropdown trạng thái

**Bảng danh sách:**
| Cột | Mô tả |
|-----|-------|
| Từ khóa | Hiển thị in đậm |
| Trạng thái | Tag Active/Inactive, click để đổi |
| Người tạo | Tên staff |
| Ngày tạo | Formatted date |
| Ngày cập nhật | Formatted date |
| Hành động | Sửa (icon) + Xóa (icon, có xác nhận) |

**Modal tạo/sửa:**
- 1 field: "Từ khóa" (bắt buộc)

**Modal import Excel:**
- Upload file kéo thả (.xlsx / .xls)
- Hiển thị kết quả import

---

## 2. Auto-Approve Rule (Quy tắc gợi ý duyệt)

### 2.1 Tổng quan

Quản lý các quy tắc tự động gợi ý duyệt nội dung, áp dụng **theo từng thử thách**. Khi nội dung thỏa tất cả điều kiện của ít nhất 1 rule → hệ thống gắn tag gợi ý duyệt để admin xem xét.

### 2.2 Data Model

| Field | Type | Mô tả |
|-------|------|-------|
| `eventId` | ObjectID → Event | Thử thách áp dụng (bắt buộc) |
| `name` | string | Tên rule (bắt buộc) |
| `minOverallScore` | number | Điểm LLM tối thiểu (0 = bỏ qua) |
| `requireMatchEvent` | boolean \| null | Yêu cầu nội dung phù hợp thử thách (null = bỏ qua) |
| `requireNoBlacklist` | boolean \| null | Yêu cầu không chứa blacklist (null = bỏ qua) |
| `minCriteriaScore` | number | Điểm tối thiểu cho MỌI tiêu chí (0 = bỏ qua) |
| `minView` | number | Lượt xem tối thiểu (0 = bỏ qua, kiểm tra sau qua job) |
| `minEngagement` | number | Engagement % tối thiểu (0 = bỏ qua, kiểm tra sau qua job) |
| `applyForSources` | string[] | Nền tảng áp dụng (rỗng = tất cả) |
| `active` | boolean | Trạng thái kích hoạt |
| `createdBy` / `updatedBy` | ObjectID → Staff | Người tạo / cập nhật |
| `createdAt` / `updatedAt` | datetime | Thời gian |

**Nền tảng hỗ trợ:** `tiktok`, `youtube`, `youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`

### 2.3 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/auto-approve-rules?eventId=xxx` | Danh sách rules theo thử thách |
| POST | `/auto-approve-rules` | Tạo rule mới |
| PUT | `/auto-approve-rules/:id` | Cập nhật rule |
| DELETE | `/auto-approve-rules/:id` | Xóa rule |
| PATCH | `/auto-approve-rules/:id/status` | Bật/tắt trạng thái |

Tất cả endpoints yêu cầu đăng nhập + quyền Admin.

### 2.4 Business Logic — Đánh giá nội dung

Sau khi LLM đánh giá xong nội dung, hệ thống chạy logic auto-approve:

1. **Lấy rules:** Query tất cả rule active của thử thách
2. **Đánh giá từng rule** (logic AND trong rule, OR giữa các rules):

   ```
   Với mỗi rule:
     ├── applyForSources không rỗng → nguồn nội dung phải nằm trong danh sách
     ├── minOverallScore > 0 → điểm LLM tổng >= ngưỡng
     ├── requireMatchEvent = true → LLM xác nhận nội dung phù hợp thử thách
     ├── requireNoBlacklist = true → LLM xác nhận không chứa blacklist
     ├── minCriteriaScore > 0 → TẤT CẢ điểm tiêu chí >= ngưỡng
     └── minView / minEngagement → kiểm tra sau qua scheduled job
   ```

3. **Kết quả:**
   - Nếu nội dung thỏa TẤT CẢ điều kiện của BẤT KỲ rule nào → gắn tag `content_suggest_approved`
   - Đây là **gợi ý**, admin vẫn cần review và duyệt thủ công

### 2.5 Giao diện Admin

Auto-approve rules nằm trong **tab "Quy tắc gợi ý duyệt"** trong trang chi tiết thử thách.

**Bảng danh sách:**
| Cột | Mô tả |
|-----|-------|
| Tên | Tên rule |
| Điểm LLM tối thiểu | Số hoặc "-" nếu 0 |
| Phù hợp thử thách | Tag "Bắt buộc" hoặc "-" |
| Không Blacklist | Tag "Bắt buộc" hoặc "-" |
| Điểm tiêu chí | Số hoặc "-" nếu 0 |
| Nền tảng | Tag màu theo platform hoặc "Tất cả" |
| Trạng thái | Switch bật/tắt |
| Hành động | Sửa + Xóa (có xác nhận) |

**Modal tạo/sửa:**
- Tên rule (text, bắt buộc)
- Điểm LLM tối thiểu (number, 0-100)
- Điểm tiêu chí tối thiểu (number, 0-100)
- View tối thiểu (number)
- Engagement tối thiểu (%, number)
- Nền tảng áp dụng (multi-select, rỗng = tất cả)
- Checkbox: Phù hợp thử thách, Không chứa Blacklist, Kích hoạt

---

## 3. Luồng tích hợp tổng thể

```
Influencer đăng bài
       │
       ▼
Hệ thống thu thập nội dung + transcript
       │
       ▼
LLM đánh giá (Vertex AI / Gemini)
  ├── Chấm điểm tổng (overallScore)
  ├── Chấm điểm từng tiêu chí (criteriaScores)
  ├── Kiểm tra phù hợp thử thách (matchEventDesc)
  └── Kiểm tra blacklist keywords (containsBlacklist + blacklistMatches)
       │
       ▼
Xử lý kết quả
  ├── Nếu containsBlacklist = true → gắn tag "content_blacklist"
  └── Chạy auto-approve rules
       │
       ▼
Auto-approve evaluation
  ├── Lấy tất cả rules active của thử thách
  ├── Đánh giá từng rule (AND logic)
  └── Nếu pass bất kỳ rule nào → gắn tag "content_suggest_approved"
       │
       ▼
Admin review trên web
  ├── Thấy tag "content_blacklist" → cần kiểm tra kỹ
  ├── Thấy tag "content_suggest_approved" → có thể duyệt nhanh
  └── Quyết định cuối cùng: Duyệt / Từ chối
```

---

## 4. Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Go + Echo framework |
| Database | MongoDB |
| LLM | Vertex AI (Gemini) |
| Admin Frontend | UmiJS + Dva.js + Ant Design Pro |
| Excel parsing | github.com/tealeg/xlsx |
| Authentication | JWT + IsAdmin middleware |

