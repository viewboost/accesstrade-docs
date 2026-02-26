# Business Brief: Trang Quản Lý Xuất Dữ Liệu trên Dashboard

**Dự án:** Techcombank — Dashboard (Next.js)
**Ngày:** 2026-02-25
**Đối tượng:** Product, Dev, Operations

---

## Vấn Đề Cốt Lõi — UX Export Bị Đứt Đoạn

**Người dùng Dashboard không thể tự lấy file sau khi xuất dữ liệu.**

Hiện tại, khi nhân viên Techcombank muốn xuất dữ liệu từ Dashboard:

1. Nhấn nút Export → chọn định dạng & nội dung → Submit
2. Hệ thống tạo job export (trạng thái `waiting`)
3. Dialog hiện thông báo thành công **kèm link sang Admin Portal**
4. Người dùng phải tự mở Admin Portal để tìm và tải file

**Vấn đề:** Người dùng Dashboard là nhân viên Techcombank — họ không có hoặc không quen dùng Admin Portal. Việc bắt họ sang một hệ thống khác để hoàn thành một tác vụ đã bắt đầu trên Dashboard là UX bị đứt đoạn, tạo ra ma sát không cần thiết.

> **Người dùng không biết file của mình đã xong chưa, và không biết tải ở đâu nếu không vào Admin.**

---

## Phân Tích Hiện Trạng

### Luồng hiện tại (broken)

```
Dashboard → Export Dialog → POST /data-exports
→ Job created (waiting/running)
→ "Thành công — vui lòng vào Admin Portal để tải"
→ [User tự mở tab mới, đăng nhập Admin, tìm file, tải]
```

### Vấn đề kỹ thuật đã xác định

- `use-export.ts` hardcode link sang Admin portal sau khi tạo job
- Không có cơ chế poll status job trên Dashboard
- Không có trang nào trên Dashboard để xem lịch sử export
- API `GET /data-exports` đã có sẵn ở backend nhưng chưa được gọi từ Dashboard

### Những gì backend đã có

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `POST /data-exports` | POST | Tạo export job — **Dashboard đã dùng** |
| `GET /data-exports` | GET | Danh sách jobs — **chưa dùng từ Dashboard** |
| `GET /data-exports/:id/pre-sign` | GET | Pre-signed URL để download — **chưa dùng từ Dashboard** |

Query params của `GET /data-exports`:
- `page`, `limit` — phân trang
- `type` — filter theo loại export
- `status` — filter theo trạng thái
- `keyword` — tìm kiếm

### Filter cần thêm ở backend

API hiện tại chưa filter theo `createdBy` — tức là nếu Dashboard gọi thẳng, user sẽ thấy **tất cả jobs của partner** (bao gồm cả jobs do người khác tạo). Cần backend thêm logic: nếu call từ context Dashboard user (không phải root/admin), chỉ trả về jobs của chính user đó.

---

## Giải Pháp — Option C: Full-featured

### Phạm vi tính năng

**1. Trang `/exports` trên Dashboard**
- Danh sách export jobs của user hiện tại
- Filter cứng: `type=dashboard_multi` + `createdBy=currentUserId`
- Phân trang
- Hiển thị trạng thái: `waiting` → `running` → `completed` / `failed`
- Download button khi `completed`
- Auto-refresh khi có job đang `running`

**2. Notification khi job hoàn thành**
- Toast/badge thông báo khi job chuyển sang `completed`
- Badge trên menu icon (sidebar sau này sẽ ráp vào)

**3. Route sẵn sàng để ráp sidebar**
- Route `/[locale]/exports` tạo trước
- Sidebar sẽ được ráp ở nhánh khác sau

### Filter rules (như yêu cầu)

1. **Của chính user tạo ra** — chỉ hiện jobs có `createdBy = currentUserId`
2. **Type `dashboard_multi` only** — chỉ hiện jobs loại `dashboard_multi`

---

## Phạm Vi Công Việc

### Backend (Go)

Thêm filter `createdBy` vào `GET /data-exports` cho public package:
- Tạo route mới trong `pkg/public/` (hoặc mở rộng route admin với context user)
- Hoặc thêm param `createdBy` vào `DataExportAll` request và filter trong query
- Pre-sign endpoint cũng cần verify ownership (user chỉ download được file của mình)

### Dashboard Frontend (Next.js)

1. **Route** `src/app/[locale]/exports/page.tsx`
2. **Hook** `src/hooks/use-exports.ts` — fetch list + poll
3. **Component** `src/components/exports/export-list.tsx` — table với status + download
4. **Service** update `src/lib/api.ts` hoặc tương đương để có `getExports` + `getPreSign`
5. **Notification** — polling hook + toast khi status change

---

## Điều Cần Xác Nhận Trước Khi Code

| # | Câu hỏi | Quyết định |
|---|---------|------------|
| 1 | Backend thêm `createdBy` filter vào route admin hiện có hay tạo route mới trong `pkg/public/`? | Cần xác nhận |
| 2 | Pre-sign endpoint: public hay admin route? | Cần xác nhận |
| 3 | Notification: toast only hay kèm badge trên header? | → Badge (để sẵn cho sidebar) |
| 4 | Poll interval khi có job running? | → Đề xuất 5 giây |
| 5 | Số records mỗi trang? | → Đề xuất 20 |

---

## Rủi Ro & Lưu Ý

| Rủi ro | Mức độ | Xử lý |
|--------|--------|-------|
| Backend chưa có filter `createdBy` → user thấy jobs của người khác | Cao (security) | Phải implement trước khi deploy |
| Pre-sign URL expose cho user khác | Cao (security) | Backend verify ownership trong `GetPreSign` |
| Poll quá thường gây tải server | Thấp | Chỉ poll khi có job `running`, dừng khi done |
| Dashboard user không có quyền gọi `/data-exports` | Trung bình | Cần verify auth middleware cho public route |

---

*Phân tích: 2026-02-25*
