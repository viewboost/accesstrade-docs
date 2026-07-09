# PRD: Cập nhật trạng thái content hàng loạt bằng file Excel (Preview + Apply + History)

**Ngày:** 01/07/2026
**Author:** vinhnguyen
**Project:** Gen-Green (vcreator)
**Project Level:** 1 (1–10 stories)
**Trạng thái:** Draft
**Related:** [`overview.md`](./overview.md) · [`tech-spec.md`](./tech-spec.md)

> Narrative tiếng Việt, technical terms tiếng Anh. Mỗi FR có acceptance criteria (AC) testable — nguồn để sinh test case.

---

## Problem Statement

Admin Gen-Green hiện chỉ hủy (reject) content lẻ từng cái trên UI. Mỗi đợt rà soát 50–500 content tốn 1–2 giờ thao tác, dễ sai sót, không có audit trail dễ tra cứu. Ops thường đã xuất file Excel từ Data Export, mark thủ công content cần hủy, rồi vào admin hủy từng cái — một vòng lặp dư thừa.

## Solution

Bổ sung chức năng **Cập nhật trạng thái content hàng loạt từ file Excel** theo luồng có kiểm soát: **upload → preview (dry-run, phân loại từng dòng) → apply**, kèm trang **lịch sử import**. Tái dùng pattern preview/apply, model `import_history`/`import_changes`, cơ chế async + concurrency lock của feature **employee-registry** đã chạy production, và dịch vụ hủy content hàng loạt (`RejectListContentByIds`) đã có sẵn.

**Scope phase 1 (đã chốt):**
- Entity: **content** (bài đăng).
- File Excel cột: **ID content (required)**, **Trạng thái mới (required)**, **Lý do (optional)**.
- Trạng thái đích duy nhất được apply: **`rejected`** (Hủy). Dòng ghi trạng thái khác → `invalid`, không apply.
- **Không rollback** — thao tác 1 chiều. Preview + checkbox xác nhận là phòng tuyến.
- Async theo pattern employee-registry: **sync ≤1000 dòng, async >1000 dòng** (goroutine + Redsync mutex + poll `/status`).

---

## User Stories

1. Là Ops, tôi muốn mở trang **Danh sách content** và thấy nút "Cập nhật trạng thái hàng loạt", để bắt đầu đổi trạng thái nhiều content thay vì làm từng cái.
2. Là Ops, tôi muốn một modal upload hướng dẫn rõ định dạng file (`.xlsx`, cột ID content / Trạng thái mới / Lý do) kèm nút "Tải file mẫu", để chuẩn bị file đúng ngay từ đầu.
3. Là Ops, tôi muốn hệ thống từ chối file không phải `.xlsx`, file hỏng, file vượt giới hạn dòng/kích thước với thông báo rõ ràng.
4. Là Ops, sau khi upload tôi muốn được chuyển sang trang **preview** của lô đó, để rà soát trước khi ghi dữ liệu.
5. Là Ops, tôi muốn thấy counter tổng hợp đầu trang preview (tổng dòng, sẽ hủy, đã hủy rồi, không tìm thấy, lỗi), để nắm nhanh chất lượng lô.
6. Là Ops, tôi muốn mỗi dòng preview hiển thị phân loại rõ ràng bằng badge màu (Sẽ hủy / Đã hủy rồi / Không tìm thấy / Lỗi), kèm lý do lỗi cụ thể.
7. Là Ops, tôi muốn preview hiển thị tiêu đề content, người đăng, sự kiện (khi resolve được) thay vì chỉ ID, để kiểm tra trực quan.
8. Là Ops, tôi muốn lọc danh sách preview theo phân loại và phân trang, để xử lý lô lớn không treo trình duyệt.
9. Là Ops, tôi muốn bấm "Áp dụng" với checkbox xác nhận số lượng content sẽ bị hủy, để chủ động trước khi ghi.
10. Là Ops, tôi muốn nút "Áp dụng" bị vô hiệu khi không có dòng "Sẽ hủy" nào, để tránh thao tác vô nghĩa.
11. Là Ops, với lô lớn xử lý nền, tôi muốn UI hiển thị tiến độ (poll) và tự cập nhật cho tới khi xong.
12. Là Ops, tôi muốn bấm "Hủy bỏ" (có xác nhận) một lô đang preview mà chưa apply, để dọn lô nhập nhầm.
13. Là Ops, tôi muốn hệ thống chặn tạo lô mới khi đang có lô chưa hoàn tất (409), để buộc xử lý dứt điểm lô cũ.
14. Là Ops, tôi muốn vào trang **Lịch sử import** để xem lại tất cả các lô đã upload, kèm trạng thái + counter + người upload + thời gian.
15. Là Ops, tôi muốn click 1 dòng lịch sử để mở lại trang preview (snapshot) của lô đó, kể cả khi đã apply.
16. Là người quản lý, tôi muốn mỗi content bị hủy từ import được set `rejectReason`/`rejectedBy`/`rejectedAt` và gửi thông báo cho creator, nhất quán với hủy content tay.

---

## Functional Requirements

### FR-1 — Nút mở modal trên trang Danh sách content
Trang Danh sách content admin Gen-Green có nút "Cập nhật trạng thái hàng loạt" mở modal upload; có link "Lịch sử import".

**AC:**
- [ ] Nút xuất hiện trên trang Danh sách content, cạnh các action hiện có.
- [ ] Click nút → mở `UploadModal`.
- [ ] Có entry vào trang Lịch sử import.

### FR-2 — Upload file Excel + validate định dạng
Modal cho chọn 1 file `.xlsx`, có nút tải file mẫu; validate extension, kích thước, số dòng trước khi parse.

**AC:**
- [ ] Chỉ chấp nhận `.xlsx` (MIME `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`). File khác → lỗi rõ ràng, không upload.
- [ ] File > `maxFileSize` (10MB) → lỗi `FILE_TOO_LARGE`.
- [ ] File > `maxDataRows` (5000) → lỗi `FILE_TOO_LARGE` (theo số dòng), không parse tiếp.
- [ ] File hỏng / sheet trống → lỗi `INVALID_FILE_FORMAT`.
- [ ] Có nút "Tải file mẫu" → tải về `.xlsx` đúng cột.

### FR-3 — Parse Excel theo cột chuẩn
Parser đọc file `.xlsx` (excelize, RawCellValue giữ leading zero), bỏ header + dòng trống, đọc 3 cột: ID content, Trạng thái mới, Lý do (optional).

**AC:**
- [ ] Đọc đúng 3 cột theo template mẫu; dòng trống hoàn toàn bị bỏ qua (không tính tổng dòng, không báo lỗi).
- [ ] ID content đọc ở dạng thô (không bị Excel ép sang số / mất ký tự).
- [ ] Trả về `TotalRows`, danh sách dòng hợp lệ, danh sách lỗi (mỗi lỗi có `Row`, `Column`, `Code`, `Message`).
- [ ] Mã lỗi parse tối thiểu: `EMPTY_CONTENT_ID`, `INVALID_CONTENT_ID` (sai format ID), `EMPTY_TARGET_STATUS`, `UNSUPPORTED_TARGET_STATUS` (khác `rejected`), `INVALID_FILE_FORMAT`, `FILE_TOO_LARGE`.

### FR-4 — Match engine phân loại từng dòng (dry-run)
Đối chiếu từng dòng với collection `content` (bulk query theo ID), sinh 4 action.

**AC:**
- [ ] `will_reject` — content tồn tại + status ∈ {`waiting`, `waiting_approved`, `approved`, `pending`, `reviewing`} (status có thể hủy) + target = `rejected`.
- [ ] `already_rejected` — content tồn tại + status = `rejected` → no-op.
- [ ] `not_found` — ID không tồn tại trong DB → skip + warning.
- [ ] `invalid` — thiếu ID / ID sai format / target status khác `rejected` / status hiện tại không cho hủy (vd `deleted`) → skip + lý do.
- [ ] Match dùng **bulk query** (không loop 1-by-1 query DB).
- [ ] Preview resolve snapshot tiêu đề / người đăng / sự kiện để hiển thị (best-effort, resolve được thì hiện tên).

### FR-5 — Tạo lô import + lưu preview
Upload thành công → tạo `import_history` (status `preview`, type `content_status`) + `import_changes` (phase `preview`) + upload file gốc lên MinIO. Sync nếu ≤1000 dòng, async nếu >1000 dòng.

**AC:**
- [ ] `import_history` có `type = "content_status"` để phân biệt với `employee_registry`.
- [ ] Counter được tính đúng: total, willReject, alreadyRejected, notFound, invalid.
- [ ] File Excel gốc upload MinIO, lưu `filePath` + `fileChecksum` (SHA256).
- [ ] ≤1000 dòng → trả `status=preview` ngay; >1000 dòng → trả `status=processing`, xử lý goroutine + Redsync mutex, cập nhật `processedRows`.

### FR-6 — Trang preview
Hiển thị counter + filter + table + footer xác nhận. Snapshot mode khi lô đã completed/cancelled/failed.

**AC:**
- [ ] Counter pills đúng 4 phân loại + tổng.
- [ ] Filter theo action; phân trang server-side (pageSize ≤ 100).
- [ ] Table: ID, tiêu đề, người đăng, sự kiện, badge action, lý do sẽ áp dụng.
- [ ] Footer: checkbox "Xác nhận hủy N content" (bắt buộc tick) + nút Áp dụng (đỏ) + nút Hủy bỏ.
- [ ] Nút Áp dụng disabled khi `willReject = 0` hoặc chưa tick checkbox.
- [ ] Lô lớn đang `processing` → hiển thị progress bar, poll `/status` mỗi 3s, tự reload preview khi xong.
- [ ] Lô đã ở trạng thái cuối (completed/cancelled/failed) → disable Áp dụng/Hủy bỏ (snapshot mode).

### FR-7 — Apply (bulk reject, 1 chiều, atomic, idempotent)
Tick xác nhận → apply: bulk update content sang `rejected`. Atomic lock chống double-apply.

**AC:**
- [ ] Atomic lock: `FindOneAndUpdate({importId, status: "preview"}, {status: "processing"})`. Apply lần 2 (double-click / multi-pod) → 409 `IMPORT_ALREADY_PROCESSED`.
- [ ] Với mỗi `will_reject`: update content `status=rejected`, `rejectReason` (từ file hoặc default), `rejectedBy`, `rejectedAt`, `bulkImportId`. Update chỉ khớp khi `status != rejected` (concurrent safety) — reuse `RejectListContentByIds` hoặc tương đương.
- [ ] Lý do mặc định khi cột Lý do trống: `"Hủy hàng loạt từ import <fileName> ngày <DD-MM-YYYY>"`.
- [ ] 1 dòng lỗi khi apply không chặn các dòng còn lại (partial success); trả `{applied, skipped, failed, errors[]}`.
- [ ] Sau apply: `import_history` status → `completed`, `import_changes` phase → `applied`, ghi counter applied/failed.
- [ ] Content đã hủy được gửi thông báo cho creator (reuse notification `NotificationTypeContentRejected`).
- [ ] Ghi audit action bulk (uploadedBy, rejectedBy).
- [ ] **KHÔNG có rollback** — không cung cấp endpoint/nút hoàn tác ở phase 1.

### FR-8 — Cancel preview
Bấm Hủy bỏ (khi status `preview`) → set lô `cancelled`, không đổi content nào.

**AC:**
- [ ] Chỉ cancel được khi status = `preview`.
- [ ] `import_history` status → `cancelled`, `import_changes` phase → `cancelled`.
- [ ] Không content nào bị đổi trạng thái.

### FR-9 — Concurrency guard (chặn trùng lô)
Chặn tạo lô mới khi còn lô chưa hoàn tất.

**AC:**
- [ ] Có lô `preview` hoặc `processing` → upload lô mới trả 409 `PENDING_IMPORT_EXISTS`.
- [ ] Sau khi lô cũ `completed`/`cancelled`/`failed` → cho phép tạo lô mới.

### FR-10 — Lịch sử import
Trang list các lô import + status + counter + người upload + thời gian; click mở preview snapshot.

**AC:**
- [ ] Chỉ list lô `type = content_status` (không lẫn employee_registry).
- [ ] Cột: thời gian, file, người upload, trạng thái (tag màu), tổng dòng, counter compact.
- [ ] Phân trang; (optional) filter theo status.
- [ ] Click row → mở trang preview snapshot của lô đó (kể cả đã apply/cancel).

---

## Non-Functional Requirements

### NFR-1 — Performance
- File ≤1000 dòng: upload+preview xong < **10s** (P95, sync).
- File >1000 dòng: xử lý nền, UI poll tiến độ; không block request.
- Apply dùng bulk update, không loop query DB từng dòng.

### NFR-2 — Security
- API chỉ cho admin (reuse middleware `RequiredLogin` + `IsRoot` như employee-registry).
- Validate extension + size ở service (không tin content-type client).
- MinIO key có importId → không guessable; audit trail đầy đủ (`uploadedBy`, `rejectedBy`).
- Sanitize giá trị ô khi render preview (chống CSV/formula injection: prefix `=`,`+`,`-`,`@` bằng `'`).

### NFR-3 — Reliability & Concurrency
- Atomic lock chống double-apply; Redsync mutex (TTL 30 phút) chống xử lý trùng lô async cross-pod.
- Recover panic trong goroutine → set lô `failed` thay vì kẹt `processing`.
- Apply idempotent: chạy lại an toàn, content đã `rejected` không bị đụng.

### NFR-4 — i18n / UX
- UI tiếng Việt (admin Gen-Green chỉ tiếng Việt).
- Badge màu nhất quán qua `action-config` (single source of truth: counter + filter + table).

### NFR-5 — Logging
- Log INFO cho upload/apply success, ERROR cho parse/apply fail. Mọi log line kèm `importId` để trace.

---

## Data Model (tóm tắt — chi tiết ở tech-spec)

- Reuse `import_history` (thêm `type = "content_status"`, counter riêng cho content) + `import_changes` (thêm field snapshot content: contentId, title, link, author, eventCode; action `will_reject|already_rejected|not_found|invalid`).
- Reuse collection `content`: khi apply set `status=rejected`, `rejectReason`, `rejectedBy`, `rejectedAt`, `bulkImportId` (field mới optional, audit).
- Migration: backfill `type` cho record `import_history` cũ = `employee_registry`.

## API (group `/content-status-import`, auth admin — chi tiết ở tech-spec)

| Method | Path | Mô tả |
|---|---|---|
| POST | `/import` | Upload `.xlsx`, parse, dry-run, tạo lô preview |
| GET | `/imports` | List lịch sử import (filter status, pagination) |
| GET | `/imports/:importId/status` | Poll tiến độ async |
| GET | `/imports/:importId/preview` | Preview counters + list (filter action, pagination) |
| POST | `/imports/:importId/apply` | Apply (bulk reject) — atomic, idempotent |
| POST | `/imports/:importId/cancel` | Hủy bỏ preview |

> **Không có** endpoint `rollback` ở phase 1.

## State Machine của một lô import

```
preview ──apply (atomic lock)──▶ processing ──(job xong)──▶ completed
   │                                 │
   │                                 └─(panic/lỗi hạ tầng)─▶ failed
   └──cancel──▶ cancelled
```
- Chỉ `preview` mới apply/cancel. Apply là **1 chiều** — không có đường về từ `completed`.
- Content do apply chuyển `→ rejected` (không hoàn tác qua hệ thống).

---

## Testing Decisions

**Module có test tự động: Excel Parser + hàm thuần build filter/match.**
- `content_status_import_parser_test.go`: dòng hợp lệ; các ca lỗi (thiếu ID, ID sai format, thiếu target status, target status khác `rejected`); dòng trống bị bỏ qua; đếm đúng counter.
- Test match engine phân loại thuần (fixture content map) → khẳng định 4 action đúng.
- Parser + match là deep module thuần, không cần DB/MinIO → test nhanh, ổn định.

**Các module còn lại (service async, handler/route, FE): verify E2E thủ công** — upload → preview (filter action) → apply (lô lớn `processing` → poll → `completed`, content `rejected`) → cancel (`cancelled`, không đổi content) → chặn lô mới khi còn lô chưa hoàn tất (409) → double-apply chỉ apply 1 lần.

**Prior art:** style test parser/filter theo `backend/pkg/admin/service/employee_registry_parser_test.go`. Pattern preview/apply của employee-registry là tham chiếu hành vi khi test thủ công.

---

## Out of Scope (phase 1)

- **Rollback** cả lô (revert status). → hướng mở rộng.
- **Trạng thái đích khác `rejected`** (approve / reset về chờ / ...). → hướng mở rộng, kiến trúc đã tách cột "Trạng thái mới".
- **Nhận diện cột theo label header linh hoạt** (upload thẳng file Data Export không chỉnh cột) → hướng mở rộng.
- Dùng chung collection lịch sử với employee-registry — phân biệt bằng field `type` (không tách collection).
- Chỉnh sửa từng dòng trực tiếp trong preview (sửa lỗi phải sửa file rồi upload lại).
- Định dạng ngoài `.xlsx` (CSV).
- Partner scoping per-partner (employee-registry là root-only; feature này cũng root/admin — không cần scope partner ở phase 1).

---

## Further Notes

- **Reuse hạ tầng:** parser pattern + `ParseExcel` style của employee-registry; `import_history`/`import_changes` DAO; `RejectListContentByIds`/reject service của content; `echoupload.UploadSingle()`, `minioclient.PutObject`, `redisclient.NewMutexWithExpiration`, `internalservice.Audit()`; `NewAppID().Hex()` làm importId. FE reuse component `UploadModal` + preview components + `action-config` + 3 DVA model của employee-registry.
- **Coupling cần test regression:** migration thêm `type` vào `import_history` touch record employee-registry → phải test employee-registry import vẫn chạy đúng.
- **Rủi ro review:** thao tác 1 chiều không rollback — preview + checkbox là phòng tuyến duy nhất; UI phải cảnh báo rõ khi `willReject` lớn.
