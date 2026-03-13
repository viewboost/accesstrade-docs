# Nâng Cấp CMS v1.1 — Tổng Quan & Giải Pháp

**Ngày cập nhật:** 13/03/2026
**Đối tượng:** Ban Thương Hiệu (BTC), Vận hành, Quản lý cấp cao

---

Bản nâng cấp CMS v1.1 gồm 3 cải tiến, xếp theo mức độ ưu tiên:

| # | Cải tiến | Mức độ | Ước lượng |
|---|---------|--------|-----------|
| # | Cải tiến | Mức độ | Ước lượng | Trạng thái |
|---|---------|--------|-----------|-----------|
| **1** | [Chuẩn hóa lý do từ chối content](#1-chuẩn-hóa-lý-do-từ-chối-content) | Nghiêm trọng — block analytics | 4-5 ngày | Chưa bắt đầu |
| **2** | [Hiển thị Event Code trên Dashboard](#2-hiển-thị-event-code-trên-dashboard) | Cao — gây friction vận hành | 0.5-1 ngày | ✅ Done |
| **3** | [Tag phân loại cho Thử thách](#3-tag-phân-loại-cho-thử-thách) | Trung bình — nâng cao UX filter | 2-3 ngày | ✅ Done |

**Tổng ước lượng: ~7-9 ngày** (nhiều phần chạy song song)

**Nguyên tắc chung:** Giữ nguyên mọi luồng hiện tại. v1.1 chỉ bổ sung — không sửa code cũ.

---

# 1. Chuẩn Hóa Lý Do Từ Chối Content

## Vấn Đề — Dashboard Không Đọc Được Lý Do Từ Chối

**Hệ thống cho admin nhập lý do từ chối dưới dạng free text — dashboard không thể tổng hợp, phân tích, hay hiển thị đúng.**

Cùng một lý do "thiếu hashtag" có thể được gõ thành "thiếu #", "ko có hashtag", "missing hashtag", "thiếu # TechcomAgent" — hệ thống coi là **4 lý do khác nhau**.

Widget "Lý do từ chối (Top 5)" gần như **vô dụng**. BTC không thể nhìn dashboard để biết content đang bị reject vì lý do gì.

## Hệ Quả — Block 3 Luồng

**Block phân tích campaign (Nghiêm trọng):**
- Thiếu hashtag chiếm bao nhiêu %? → Không biết
- Campaign nào rejection rate cao nhất? → Không biết
- BTC phải mở từng bài đăng rồi tổng hợp Excel — bất khả thi khi hàng trăm content

**Block cải thiện quy trình:** Không có data chuẩn hóa → không xác định được lỗi phổ biến, không so sánh được giữa các campaign.

**Block trải nghiệm Creator:** Creator chỉ thấy 1 dòng text nhỏ hoặc message mặc định → không hiểu rõ lý do → sửa sai → bị reject tiếp.

## Vì Sao Cần Giải Quyết Ngay

| Yếu tố | Chi tiết |
|---------|---------|
| **Volume tăng** | Content tăng theo campaign mới — free text nghiêm trọng hơn khi scale |
| **Campaign mới** | Campaign tháng 3 cần analytics dashboard hoạt động đúng |
| **Data xấu tích lũy** | Mỗi ngày thêm free text → migration càng phức tạp |
| **Effort nhỏ, impact lớn** | Cốt lõi chỉ tách 1 field → 2 fields |

## Giải Pháp — Tag + Comment

Tách field `reason` (free text) thành 2 field:

| Field | Loại | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| **Rejection Tags** | Chọn từ danh sách | Ít nhất 1 tag | Lý do chính, chuẩn hóa |
| **Rejection Comment** | Nhập tự do | Không (trừ khi chọn "Khác") | Ghi chú bổ sung |

### Danh sách Tag v1

| Tag | Tiếng Việt | Tiếng Anh |
|-----|-----------|-----------|
| `missing_hashtag` | Thiếu hashtag | Missing hashtag |
| `wrong_content` | Nội dung không đúng brief | Content doesn't match brief |
| `poor_quality` | Chất lượng kém | Poor quality |
| `policy_violation` | Vi phạm chính sách | Policy violation |
| `wrong_platform` | Sai nền tảng | Wrong platform |
| `missing_mention` | Thiếu mention/tag | Missing mention/tag |
| `wrong_timing` | Sai thời gian đăng | Wrong posting time |
| `duplicate` | Bài trùng lặp | Duplicate content |
| `other` | Khác (bắt buộc nhập comment) | Other |

### Thay đổi theo từng bên

**Admin Dashboard — Khi reject:**
- Trước: Ô nhập text tự do
- Sau: Dropdown chọn tag (bắt buộc) + ô comment (tùy chọn). Batch reject: chọn tag chung cho nhiều bài

**Admin Dashboard — Khi xem:**
- Trước: Badge "Từ chối" đỏ, mở detail mới thấy text nhỏ
- Sau: Tag badges ngay trong bảng, detail card đầy đủ, filter theo rejection tag

**Admin Dashboard — Analytics:**
- Trước: Widget "Top 5" hiện free text trùng lặp
- Sau: Chart theo tags — dữ liệu chính xác, click vào tag để xem content

**Creator/KOL:**
- Trước: Dòng text nhỏ hoặc message mặc định
- Sau: Tag badges có màu + comment bổ sung

### Backward Compatibility

- Field `reason` cũ giữ nguyên, API chấp nhận request cũ
- Dữ liệu cũ hiển thị fallback bằng text `reason`
- Migration script: map text cũ → tag + giữ text cũ làm comment

### Không làm trong v1.1

Severity level, resubmit flow, appeal/khiếu nại, rejection history, auto-check, custom tags.

### Lộ trình

| Phase | Nội dung | Ước lượng | Song song |
|-------|---------|-----------|-----------|
| 1. Backend | Model, API, validation | 1-2 ngày | — |
| 2. Analytics + Migration | Aggregate pipeline, migration script | 0.5-1 ngày | Sau Phase 1 |
| 3. Dashboard UI | Reject dialog, table badges, widget, filter, i18n | 2-3 ngày | Song song Phase 4 |
| 4. Frontend Creator | Tag badges + comment cho KOL | 1 ngày | Song song Phase 3 |

---

# 2. Hiển Thị Event Code Trên Dashboard

## Vấn Đề — Ops Không Tìm Được Event

Event có 2 tên:
- **`name`** — Tên hiển thị cho user, ngắn (VD: "Chi tiêu cùng thẻ Techcombank")
- **`code`** — Mã vận hành (VD: "2025 - T12 - TCMERS - PYC4 - Usage")

Code encode thông tin quan trọng: năm, tháng, đối tượng, payment cycle, tên ngắn gọn. **Ops team làm việc theo code, không theo name.**

```
2025 - T12 - TCMERS - PYC4 - Usage
 │      │      │       │      └── Tên ngắn gọn
 │      │      │       └── Payment cycle
 │      │      └── Đối tượng
 │      └── Tháng
 └── Năm
```

**Vấn đề: Dashboard hoàn toàn KHÔNG hiển thị code.** Type definition `ApiEvent` chỉ có `name` + `slug`, không có `code`. Ops phải nhớ mapping hoặc mở Admin Panel tra cứu.

## Hiện Trạng

| Vị trí | App | Hiện tại | Ai xem |
|--------|-----|----------|--------|
| CampaignSelect (filter) | Dashboard | `name` only | Ops |
| ContentFilter (event dropdown) | Dashboard | `name` only | Ops |
| PortfolioTable | Dashboard | `name` only | Ops |
| Export CSV | Dashboard | `name` only | Ops |
| EventTable | Admin | `name` + `code` ✅ | Admin |
| Event Form | Admin | `name` + `code` ✅ | Admin |
| EventCard | Frontend | `name` only ✅ | Creator |

## Giải Pháp — Hiện Code Ở Đúng Chỗ

### Nguyên tắc

| Đối tượng | Hiển thị |
|-----------|----------|
| **Creator/KOL** | `name` only — code là nội bộ |
| **Ops (Dashboard)** | `code` + `name` — ops làm việc theo code |
| **Admin** | Cả 2 — đã có hầu hết |

### Thay đổi cụ thể

| Vị trí | Trước | Sau |
|--------|-------|-----|
| **CampaignSelect** | Hiện name, search by name | Hiện `code — name`, search cả code + name |
| **ContentFilter** | Hiện name | Hiện `code — name` |
| **PortfolioTable** | Cột name | Name (bold) + code (muted, nhỏ bên dưới) |
| **Export CSV** | Cột name | Thêm cột code riêng |
| **Admin Detail** heading | Name only | Name + badge code |
| **Frontend** | Không thay đổi | Không thay đổi |

### Effort

~0.5-1 ngày. Root cause chỉ là thêm `code` vào type definition → các component tự có thể access.

---

# 3. Tag Phân Loại Cho Thử Thách (Event Tags)

## Vấn Đề — Không Có Cách Nhóm Events

Khi số lượng events nhiều, CampaignSelect là flat list dài. Không có cách nhóm events theo mục đích/tính chất → không thể:
- Lọc nhanh "tất cả events nhận diện thương hiệu"
- So sánh analytics giữa các nhóm event
- Tìm event mà không nhớ tên cụ thể

**Hiện tại:** Event model có `Categories []AppID` (tham chiếu) và `Tags` (chỉ là ảnh) — **KHÔNG có text tags phân loại.**

## Giải Pháp — Gắn Tags Cho Event + Filter Trên Dashboard

### Reuse hệ thống TagRaw hiện có

Hệ thống đã có model `TagRaw` (name, color, type, active) dùng cho content labeling. Thêm type `"event"` → reuse toàn bộ CRUD, color system, UI pattern đã có.

### Tags đề xuất v1

| Tag | Màu | Mô tả |
|-----|-----|-------|
| `brand_awareness` | Xanh dương | Nhận diện thương hiệu |
| `product_launch` | Cam | Ra mắt sản phẩm |
| `seasonal` | Đỏ | Theo mùa/dịp lễ |
| `always_on` | Xanh lá | Chạy liên tục |
| `internal` | Xám | Nội bộ nhân viên |
| `engagement` | Tím | Tăng tương tác |
| `conversion` | Hồng | Chuyển đổi/bán hàng |

Admin có thể tạo thêm tags tùy ý (reuse TagRaw CRUD).

### Thay đổi cụ thể

**Backend:**
- Thêm type `"event"` vào tag system
- Thêm field `EventTags []AppID` vào Event model
- API: GET /tags?type=event

**Admin Panel (Event setup):**
- Form tạo/sửa Event: thêm multi-select Tags field
- Autocomplete/search tags

**Dashboard (Analytics):**
- Tag chips **nằm bên trong** CampaignSelect dropdown (không phải filter riêng)
- Chọn tag → lọc danh sách events hiển thị trong dropdown (OR logic)
- Event code hiện 2 màu: code (muted) + name (thường)
- URL sync: `?tags=id1,id2`

**Content Page (`/contents`):**
- Tag chips tương tự nằm trong Event dropdown filter
- Chọn tag → lọc events hiển thị (OR logic)
- URL sync: `?eventTag=id1,id2`

### Architecture — Client-side filtering

```
Tag chips (trong dropdown) → lọc events client-side → event list (đã filter) → analytics API (không đổi)
```

Không cần thay đổi analytics backend. Tag filter chỉ thu hẹp danh sách events hiển thị trong dropdown.

### Trạng thái triển khai

| Phần | Trạng thái |
|------|-----------|
| Backend: type `"event"` + EventTags field | ✅ Done |
| Backend: seed 7 tags | ✅ Done |
| Admin: multi-select Tags trong Event form | ✅ Done |
| Dashboard: tag filter trong CampaignSelect | ✅ Done |
| Content page: tag filter trong Event dropdown | ✅ Done |
| Event code 2 màu (muted code + name) | ✅ Done |

### Effort

~2-3 ngày (backend + admin panel + dashboard).

---

## Tổng Kết Lộ Trình

```
Tuần 1:
  ├── [1-2 ngày] Rejection Reason: Backend model + API
  ├── [0.5-1 ngày] Event Code: Dashboard type + components
  └── [0.5 ngày] Event Tags: Backend model + tag type

Tuần 2:
  ├── [2-3 ngày] Rejection Reason: Dashboard UI + Frontend (song song)
  ├── [0.5 ngày] Rejection Reason: Analytics + Migration
  └── [1-2 ngày] Event Tags: Admin form + Dashboard filter
```

**Tổng: ~7-9 ngày làm việc**, nhiều phần chạy song song.

---

## Câu Hỏi Thường Gặp

**Hỏi: 3 cải tiến này có phụ thuộc nhau không?**
→ Không. Mỗi cải tiến độc lập, có thể triển khai riêng. Chỉ Event Code (nhỏ nhất) nên làm trước vì effort thấp, impact nhanh.

**Hỏi: Rejection tags — admin có thể thêm tag mới không?**
→ v1.1 chưa hỗ trợ custom tags. Danh sách 9 tags cố định. Xem xét cho admin tạo tags ở phiên bản sau.

**Hỏi: Dữ liệu reject cũ (free text) có bị mất không?**
→ Không. Field `reason` giữ nguyên. Migration map text cũ → tag + giữ text gốc làm comment.

**Hỏi: Event tags — có ảnh hưởng analytics API không?**
→ Không. Tag filter lọc events client-side, analytics API nhận eventIds như cũ.

**Hỏi: Event code — frontend creator có thấy code không?**
→ Không. Code chỉ hiện cho ops/admin. Creator vẫn chỉ thấy name.

**Hỏi: Batch reject có hỗ trợ tag không?**
→ Có. Admin chọn tag chung + optional comment cho tất cả content được chọn.
