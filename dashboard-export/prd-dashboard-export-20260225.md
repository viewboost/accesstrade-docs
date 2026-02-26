# PRD: Quản Lý Xuất Dữ Liệu — Techcombank Dashboard

**Dự án:** Techcombank — Dashboard (Next.js) + Backend (Go)
**Ngày:** 2026-02-25
**Version:** 1.0
**Tác giả:** Product Manager (BMAD)
**Đối tượng:** Dev, QA, Stakeholders

---

## Tóm Tắt

Tính năng xuất dữ liệu hiện tại trên Dashboard bị đứt đoạn ở bước cuối: người dùng tạo được job export nhưng không có cách theo dõi tiến trình hay tải file ngay trên Dashboard — phải sang Admin Portal. PRD này định nghĩa toàn bộ yêu cầu để hoàn thiện luồng xuất dữ liệu end-to-end, bao gồm cả phần backend cần cập nhật.

---

## 1. Mục Tiêu Kinh Doanh

| # | Mục tiêu | Đo lường |
|---|----------|----------|
| B1 | Loại bỏ ma sát trong luồng xuất dữ liệu — người dùng không cần rời Dashboard | Tỉ lệ export thành công (tải được file) tăng |
| B2 | Người dùng Dashboard tự quản lý lịch sử export của mình | Không còn phản hồi "tôi không biết file ở đâu" |
| B3 | Giảm phụ thuộc vào Admin Portal cho người dùng cuối | Số lần user cần support về export giảm |

---

## 2. User Personas

### Nhân viên Techcombank (primary)
- Dùng Dashboard để theo dõi hiệu quả chiến dịch influencer
- Cần xuất báo cáo định kỳ (campaigns, creators, payments)
- **Không có quyền truy cập Admin Portal**
- Mong đợi: làm xong mọi thứ trong Dashboard

### Campaign Owner (secondary)
- Quản lý nhiều chiến dịch, cần export tổng hợp
- Tạo nhiều export jobs, cần xem lịch sử
- Mong đợi: biết job nào đang chạy, job nào xong

---

## 3. Hiện Trạng & Vấn Đề

### Luồng hiện tại (broken)
```
User → Export Dialog → POST /data-exports → Job tạo xong
→ Toast: "Thành công — xem tại Admin Portal"
→ User phải tự sang Admin Portal để tìm file
```

### Vấn đề kỹ thuật đã xác nhận
- `use-export.ts:69` hardcode `window.open(getAdminDataUrl(), '_blank')` sau khi tạo job
- Không có API call `GET /data-exports` từ Dashboard
- Không có trang quản lý export trên Dashboard
- Backend `GET /data-exports` chưa có filter `createdBy` — nếu gọi thẳng, user thấy toàn bộ jobs của partner

---

## 4. Functional Requirements

### FR-001: Trang Danh Sách Export Jobs

**Priority:** Must Have

**Mô tả:**
Hệ thống phải cung cấp trang `/exports` trên Dashboard hiển thị danh sách export jobs của người dùng hiện tại.

**Acceptance Criteria:**
- [ ] Route `/{locale}/exports` tồn tại và accessible với user đã đăng nhập
- [ ] Trang hiển thị danh sách export jobs dạng bảng
- [ ] Chỉ hiển thị jobs của người dùng hiện tại (`createdBy = currentUserId`)
- [ ] Chỉ hiển thị jobs có `type = dashboard_multi`
- [ ] Hiển thị tối thiểu: tên file, trạng thái, thời gian tạo, nút hành động
- [ ] Trang có tiêu đề rõ ràng bằng ngôn ngữ người dùng (i18n)

**Dependencies:** FR-004 (Backend filter)

---

### FR-002: Phân Trang Danh Sách

**Priority:** Must Have

**Mô tả:**
Danh sách export jobs phải hỗ trợ phân trang.

**Acceptance Criteria:**
- [ ] Mặc định hiển thị 20 records/trang
- [ ] Hiển thị tổng số records
- [ ] User có thể chuyển trang
- [ ] URL không bắt buộc phản ánh trang hiện tại (stateful component là đủ)

**Dependencies:** FR-001

---

### FR-003: Hiển Thị Trạng Thái Job

**Priority:** Must Have

**Mô tả:**
Mỗi export job phải hiển thị trạng thái rõ ràng với visual indicator tương ứng.

**Acceptance Criteria:**
- [ ] `waiting` → badge xám + label "Đang chờ"
- [ ] `running` → badge xanh dương + spinner + label "Đang xử lý"
- [ ] `completed` → badge xanh lá + label "Hoàn thành"
- [ ] `failed` → badge đỏ + label "Thất bại" + hiển thị reason nếu có
- [ ] Visual indicator đủ rõ ràng để phân biệt không cần đọc text

**Dependencies:** FR-001

---

### FR-004: Backend Filter `createdBy` cho `GET /data-exports`

**Priority:** Must Have

**Mô tả:**
Backend phải hỗ trợ filter chỉ trả về jobs của người dùng hiện tại khi được yêu cầu.

**Acceptance Criteria:**
- [ ] `GET /data-exports?filterByOwner=true` chỉ trả về jobs có `createdBy = staffId` từ JWT token
- [ ] `staffId` được lấy từ JWT context — client không tự set được
- [ ] `GET /data-exports` không có `filterByOwner` vẫn hoạt động như cũ (backward compatible)
- [ ] `filterByOwner=true` kết hợp được với các filter khác (`type`, `status`, `page`, `limit`)

---

### FR-005: Download File Khi Job Hoàn Thành

**Priority:** Must Have

**Mô tả:**
Người dùng phải có thể tải file export trực tiếp từ Dashboard khi job ở trạng thái `completed`.

**Acceptance Criteria:**
- [ ] Nút "Tải xuống" chỉ xuất hiện/enable khi `status = completed`
- [ ] Click "Tải xuống" → gọi `GET /data-exports/:id/pre-sign` → mở file trong tab mới
- [ ] Nút bị disable hoặc ẩn khi `status ≠ completed`
- [ ] Loading state khi đang lấy pre-signed URL
- [ ] Hiển thị lỗi nếu không lấy được URL

**Dependencies:** FR-004, FR-006

---

### FR-006: Backend Verify Ownership trong `GetPreSign`

**Priority:** Must Have

**Mô tả:**
Backend phải đảm bảo người dùng chỉ có thể lấy pre-signed URL của file do chính họ tạo ra.

**Acceptance Criteria:**
- [ ] `GET /data-exports/:id/pre-sign` trả về 403 nếu `createdBy ≠ staffId` (và không phải root)
- [ ] Root user vẫn có thể lấy pre-sign của mọi job (backward compatible)
- [ ] Error message rõ ràng khi bị từ chối

**Dependencies:** FR-004

---

### FR-007: Auto-Refresh Khi Có Job Đang Chạy

**Priority:** Must Have

**Mô tả:**
Trang export jobs phải tự động cập nhật trạng thái khi có job đang ở trạng thái `waiting` hoặc `running`.

**Acceptance Criteria:**
- [ ] Polling tự động bắt đầu khi trang load và có ít nhất 1 job `waiting` hoặc `running`
- [ ] Interval polling: 5 giây
- [ ] Polling tự động dừng khi không còn job `waiting`/`running`
- [ ] Polling dừng khi user rời khỏi trang (cleanup)
- [ ] Không polling khi tất cả jobs đã `completed` hoặc `failed`

**Dependencies:** FR-001

---

### FR-008: Toast Notification Khi Job Hoàn Thành

**Priority:** Must Have

**Mô tả:**
Người dùng phải nhận được thông báo khi một export job chuyển sang trạng thái `completed`.

**Acceptance Criteria:**
- [ ] Toast xuất hiện khi job chuyển từ `running`/`waiting` → `completed`
- [ ] Toast có action "Tải xuống" cho phép download ngay
- [ ] Toast xuất hiện ngay cả khi user đang ở trang khác (nếu đang trong session)
- [ ] Toast tự động đóng sau 8 giây nếu không có action

**Dependencies:** FR-007

---

### FR-009: Badge Notification Trên Navigation

**Priority:** Should Have

**Mô tả:**
Icon/menu dẫn đến trang Exports phải hiển thị badge khi có job đang chờ/chạy.

**Acceptance Criteria:**
- [ ] Badge hiện số lượng jobs `waiting`/`running` khi > 0
- [ ] Badge biến mất khi không còn job đang xử lý
- [ ] Badge slot sẵn sàng để sidebar component ráp vào (không cần sidebar hoàn chỉnh ngay)

**Dependencies:** FR-001, FR-007

**Lưu ý:** Navigation/sidebar sẽ được thêm link ở nhánh khác — FR này tạo slot trước.

---

### FR-010: Hiển Thị Reason Khi Job Thất Bại

**Priority:** Should Have

**Mô tả:**
Khi một job có trạng thái `failed`, người dùng phải biết lý do thất bại.

**Acceptance Criteria:**
- [ ] Cột `reason` được hiển thị trong bảng hoặc tooltip/modal
- [ ] Nếu `reason` trống: hiển thị "Không xác định"
- [ ] Reason text đủ để user hiểu cần làm gì tiếp theo (hoặc liên hệ support)

**Dependencies:** FR-003

---

### FR-011: Cập Nhật Export Dialog — Bỏ Link Admin Portal

**Priority:** Must Have

**Mô tả:**
Sau khi tạo export job thành công, Dialog phải dẫn user đến trang Exports trong Dashboard thay vì link sang Admin Portal.

**Acceptance Criteria:**
- [ ] Toast/dialog sau khi tạo job có action "Xem lịch sử xuất" → navigate đến `/{locale}/exports`
- [ ] Không còn hardcode link `NEXT_PUBLIC_ADMIN_URL/data`
- [ ] Thông báo thành công vẫn hiển thị rõ ràng
- [ ] Backward compatible: nếu route exports chưa có thì hiển thị message không có action

**Dependencies:** FR-001

---

## 5. Non-Functional Requirements

### NFR-001: Security — Isolation Dữ Liệu Theo User

**Priority:** Must Have

**Mô tả:**
Người dùng chỉ được phép xem và tải file export do chính họ tạo ra.

**Acceptance Criteria:**
- [ ] API `GET /data-exports?filterByOwner=true` enforce tại backend, không tại frontend
- [ ] API `GET /data-exports/:id/pre-sign` trả về 403 nếu user không phải owner
- [ ] Không có cách nào để frontend bypass filter `createdBy`

**Rationale:** Jobs export có thể chứa dữ liệu nhạy cảm của chiến dịch, influencer, và tài chính.

---

### NFR-002: Performance — Polling Không Gây Tải Bất Thường

**Priority:** Must Have

**Mô tả:**
Cơ chế auto-refresh không được gây tải server bất thường.

**Acceptance Criteria:**
- [ ] Polling chỉ xảy ra khi có job `waiting`/`running` (không poll khi không cần thiết)
- [ ] Interval tối thiểu 5 giây giữa các lần poll
- [ ] Cleanup đúng cách khi component unmount
- [ ] Không có memory leak từ polling interval

---

### NFR-003: Performance — Response Time API

**Priority:** Should Have

**Mô tả:**
API `GET /data-exports` với `filterByOwner=true` phải trả về trong thời gian chấp nhận được.

**Acceptance Criteria:**
- [ ] Response time < 500ms cho 95% requests (dataset thực tế: < 1000 records)
- [ ] MongoDB query có index trên `createdBy` + `type` + `createdAt`

---

### NFR-004: Usability — i18n

**Priority:** Must Have

**Mô tả:**
Tất cả text trên trang Exports phải hỗ trợ đa ngôn ngữ (vi/en).

**Acceptance Criteria:**
- [ ] Tất cả label, status text, button text đều dùng i18n keys
- [ ] Hỗ trợ tiếng Việt và tiếng Anh
- [ ] Không có hardcoded text trực tiếp trong component

---

### NFR-005: Compatibility — Backward Compatible

**Priority:** Must Have

**Mô tả:**
Các thay đổi backend không được phá vỡ chức năng Admin hiện tại.

**Acceptance Criteria:**
- [ ] Admin vẫn xem được tất cả jobs (không bị filter khi không truyền `filterByOwner`)
- [ ] Pre-sign endpoint vẫn hoạt động với Admin flow hiện tại
- [ ] Root user vẫn có full access

---

### NFR-006: Maintainability — Code Structure

**Priority:** Should Have

**Mô tả:**
Code mới phải theo đúng pattern và convention của codebase hiện tại.

**Acceptance Criteria:**
- [ ] Hook `use-exports.ts` theo pattern tương tự `use-events.ts`, `use-analytics.ts`
- [ ] API functions thêm vào `lib/api.ts` hoặc file dedicated, không inline trong component
- [ ] Component structure theo pattern của `components/` hiện có

---

## 6. Epics

### EPIC-001: Backend — Data Access Control

**Mô tả:**
Cập nhật backend để hỗ trợ filter và phân quyền theo owner, phục vụ Dashboard call.

**Functional Requirements:**
- FR-004 (filter createdBy)
- FR-006 (verify ownership pre-sign)

**Story Count Estimate:** 2–3 stories

**Priority:** Must Have

**Business Value:** Security foundation — không làm thì không triển khai được frontend

---

### EPIC-002: Dashboard — Trang Quản Lý Export

**Mô tả:**
Xây dựng trang `/exports` với đầy đủ chức năng: danh sách, phân trang, trạng thái, download.

**Functional Requirements:**
- FR-001 (trang danh sách)
- FR-002 (phân trang)
- FR-003 (hiển thị trạng thái)
- FR-005 (download)
- FR-007 (auto-refresh)
- FR-010 (hiển thị reason)

**Story Count Estimate:** 4–6 stories

**Priority:** Must Have

**Business Value:** Core user journey — người dùng tự quản lý export của mình

---

### EPIC-003: Dashboard — Notification & UX Hoàn Thiện

**Mô tả:**
Hoàn thiện UX: notification khi job done, badge trên nav, cập nhật export dialog.

**Functional Requirements:**
- FR-008 (toast notification)
- FR-009 (badge navigation)
- FR-011 (cập nhật export dialog)

**Story Count Estimate:** 3–4 stories

**Priority:** Must Have (FR-011) + Should Have (FR-008, FR-009)

**Business Value:** Đóng vòng lặp UX — người dùng không cần chủ động kiểm tra

---

## 7. User Flows

### Flow chính: Tạo và Tải Export

```
1. User ở trang Dashboard chính
   → Nhấn "Xuất dữ liệu"
   → Chọn định dạng (CSV/XLSX) và nội dung
   → Submit

2. Toast thành công: "Đang xử lý — Xem lịch sử xuất"
   → Click "Xem lịch sử xuất" OR navigate đến /exports

3. Trang /exports:
   → Job mới hiển thị với status "waiting" hoặc "running"
   → Auto-refresh 5 giây

4. Job chuyển sang "completed":
   → Toast notification xuất hiện (nếu user đang ở trang khác)
   → Status badge chuyển xanh lá
   → Nút "Tải xuống" enable

5. Click "Tải xuống"
   → Mở file trong tab mới
```

### Flow phụ: Xem lịch sử cũ

```
1. User navigate đến /exports trực tiếp
   → Xem tất cả jobs cũ của mình (type=dashboard_multi)
   → Paginate nếu nhiều
   → Download lại bất kỳ file completed nào (trong giới hạn pre-sign URL)
```

---

## 8. Dependencies

### Internal
- Backend API `GET /data-exports` — cần cập nhật (EPIC-001)
- Backend API `GET /data-exports/:id/pre-sign` — cần cập nhật (EPIC-001)
- Dashboard auth layer (`lib/auth.ts`) — đã có, reuse
- Dashboard API client (`lib/api.ts`) — đã có, extend
- i18n messages files — cần thêm keys mới

### External
- Không có dependency external mới
- MinIO/S3 pre-signed URL — đã có trong backend

---

## 9. Ngoài Phạm Vi (Out of Scope)

| Hạng mục | Lý do |
|---------|-------|
| Sidebar navigation link | Nhánh khác sẽ ráp sau khi sidebar được xây dựng |
| Export types khác (reconciliation, transfer, v.v.) | Dashboard chỉ xuất `dashboard_multi` |
| Admin Portal export page | Đã có, không thay đổi |
| Email notification khi job done | Không có yêu cầu, không trong scope |
| Scheduled exports | Không trong scope Dashboard |
| Search/filter theo tên trên trang exports | Giai đoạn 1: không cần |

---

## 10. Assumptions

1. Dashboard users dùng cùng JWT token với Admin (đã xác nhận từ `lib/auth.ts`)
2. Backend `GET /data-exports` accessible bằng token admin của Dashboard user
3. `type=dashboard_multi` đủ để identify các export từ Dashboard
4. MongoDB collection `dataExports` đã có index trên `createdBy`
5. Pre-signed URL từ MinIO còn hiệu lực 15 phút (đã xác nhận từ code)

---

## 11. Open Questions

| # | Câu hỏi | Mức độ ưu tiên |
|---|---------|----------------|
| Q1 | MongoDB đã có index compound `{createdBy, type, createdAt}` chưa? Nếu chưa, cần thêm trước khi deploy | High |
| Q2 | Pre-sign URL 15 phút — có đủ không, hay user cần refetch? | Medium |
| Q3 | Số lượng export jobs thực tế mỗi user — có cần pagination aggressive không? | Low |

---

## 12. Traceability Matrix

| Epic | FRs | NFRs | Story Estimate | Priority |
|------|-----|------|----------------|----------|
| EPIC-001: Backend Access Control | FR-004, FR-006 | NFR-001, NFR-003, NFR-005 | 2–3 | Must Have |
| EPIC-002: Trang Quản Lý Export | FR-001, FR-002, FR-003, FR-005, FR-007, FR-010 | NFR-002, NFR-004, NFR-006 | 4–6 | Must Have |
| EPIC-003: Notification & UX | FR-008, FR-009, FR-011 | NFR-004 | 3–4 | Must/Should |
| **Tổng** | **11 FRs** | **6 NFRs** | **9–13 stories** | |

---

## 13. Prioritization Summary

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-011 (9) | NFR-001, NFR-002, NFR-004, NFR-005 (4) |
| Should Have | FR-009, FR-010 (2) | NFR-003, NFR-006 (2) |
| Could Have | — | — |

---

*PRD Generated: 2026-02-25 | BMAD Method — Product Manager workflow*
*Tài liệu tham khảo: business-brief.md, implementation-plan.md*
