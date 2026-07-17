# Technical Specification: Duyệt/Từ chối content hàng loạt — chạy nền (async)

## Document Overview

**Ngày:** 17/07/2026
**Trạng thái:** Đã implement — PR `Vin-VCreator/vcreator#125` → `develop`
**Branch:** `fix/batch-approve-reject-async` (từ `origin/develop`)
**Project:** vcreator (backend Go + admin frontend)
**Task:** #8 — "Tính năng duyệt hàng loạt → lỗi tính năng không chạy"

Tài liệu mô tả bản đã implement, thay cơ chế `BatchChangeStatus` đồng bộ bằng **job chạy nền** để chống timeout và lưu lỗi từng item. Tái dùng pattern "apply async theo lô" của [import-content-to-reject](../import-content-to-reject/tech-spec.md), lược bỏ upload/preview/parser.

---

## Problem & Solution

### Problem Statement

`PATCH /contents/batch-status` → `service.BatchChangeStatus` chạy **đồng bộ trong HTTP request**, dùng `ctx = c.Request().Context()`. Vòng lặp gọi `ChangeStatus` từng content; mỗi item còn chạy **đồng bộ** `ActionAfterWhenChangeStatus` (revoke `EventReward`, update `ContentAnalyticDaily`, `redis.DelAllKeyByPattern("cache_list_event*")`, recheck event schema, push notification).

Lô lớn ⇒ tổng thời gian ≈ N × chi phí nặng ⇒ vượt timeout proxy/server ⇒ **request context bị hủy** ⇒ các item còn lại fail tại `FindById`/`UpdateOne` (context canceled) ⇒ status **kẹt `waiting_approved`**. Ngoài ra: chỉ 1 item lỗi → trả 400 cả cụm, FE không refresh ⇒ nhìn như "không chạy".

- **Intermittent:** chỉ dính khi lô đủ lớn để chạm timeout.
- **Tần suất tăng:** data nhiều ⇒ chọn nhiều/lần + `DelAllKeyByPattern` chậm dần theo số key.

### Proposed Solution

Endpoint mới **tạo job → trả `jobId` ngay → xử lý trong goroutine `context.Background()`** (không chết theo request). Job lặp gọi `ChangeStatus(isBatch=true)` (giữ nguyên side-effect), lưu tiến độ + **lỗi từng item** vào 1 collection để FE poll và hiển thị. Endpoint cũ giữ nguyên.

---

## Requirements

### What Needs to Be Built

1. **Collection job** `content-batch-actions` (1 doc/job) — lưu action, danh sách content, tiến độ, lỗi từng item, trạng thái.
2. **Service async** — `CreateBatchAction` (validate + tạo job + spawn goroutine), `processAsync` (mutex + heartbeat + idempotent + lưu lỗi), `GetBatchActionStatus` (poll).
3. **API** — `POST /contents/batch-actions` (tạo job), `GET /contents/batch-actions/:jobId/status` (poll tiến độ + lỗi).
4. **Apply** — reuse admin `ChangeStatus(isBatch=true)`; **tuyệt đối không** raw-update status (mất side-effect thưởng/thông báo).
5. **Frontend** — đổi effect batch: tạo job → poll → thanh tiến độ → modal danh sách lỗi → refresh. UI component giữ nguyên.
6. **Concurrency** — Redis mutex per-job, recover panic, cap 2000 item.

### What This Does NOT Include

- **Preview / match engine 6 action** — selection trên bảng đã là preview.
- **Upload file / MinIO / parser** — input là danh sách ID từ UI.
- **Rollback / retry tự động.**
- **"Chọn tất cả theo filter"** — chỉ xử lý danh sách `ids` gửi lên (giữ nguyên hành vi cũ; `isAll`/`filter` bỏ qua).
- **Xoá endpoint cũ** `/contents/batch-status` (giữ để không phá gì đang gọi).

---

## Technical Approach

### Technology Stack

- **Backend:** Go, project `viewboost` (vcreator). Reuse `ChangeStatus`, DAO pattern, Redis mutex (`internal/module/redis`).
- **Database:** MongoDB — collection mới `content-batch-actions`; đọc/ghi `content` qua `ChangeStatus`.
- **Concurrency:** Redis mutex (`NewMutexWithExpiration`).
- **Frontend:** admin (umi/dva + antd) — `message.loading` (tiến độ), `Modal.warning` (danh sách lỗi).

### Architecture Overview

```
[Admin UI: chọn content → Duyệt/Từ chối]
        │ POST /contents/batch-actions { ids, status, reason }
        ▼
[CreateBatchAction]  (đồng bộ, nhanh)
   - validate action ∈ {approved, rejected, waiting_approved}
   - dedupe ids, cap 2000
   - insert job (status=pending)
   - go processAsync(jobId)                          ← spawn goroutine
        │ trả { jobId, status, totalToProcess } NGAY
        ▼
[FE poll GET /contents/batch-actions/:jobId/status mỗi 2.5s]
   → thanh tiến độ X/Y → xong: Modal liệt kê lỗi → refresh list

────────── goroutine (context.Background) ──────────
[processAsync]
   - Redis mutex "content-batch-action:<jobId>" (30')
   - recover() → panic set status=failed
   - chỉ chạy job pending → set running
   - for mỗi content (nghỉ 500ms / 50 item):
        · fetch content; ID lỗi / không tồn tại → failedItems
        · idempotent: content.status == action → skip success
        · else ChangeStatus(ctx, id, createdBy, {status, reason}, isBatch=true)
              lỗi → failedItems (contentId + reason)
        · $inc processedCount + $set updatedAt (heartbeat)
   - done (hoặc failed nếu 100% lỗi) + successCount/failedCount/failedItems
```

### Data Model — `content-batch-actions`

`ContentBatchActionRaw` (`backend/internal/model/mg/content_batch_action.go`):

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `jobId` | string | unique hex — khóa poll |
| `action` | string | target status (`approved`/`rejected`/`waiting_approved`) |
| `reason` | string | lý do (rejected) |
| `partner` | AppID | partner staff (zero = toàn quyền) — scope quyền xem |
| `createdBy` | AppID | staff bấm |
| `contentIds` | []string | snapshot input |
| `totalToProcess` / `processedCount` | int | progress |
| `successCount` / `failedCount` | int | kết quả |
| `failedItems` | []{contentId, reason} | lỗi từng item |
| `status` | string | `pending`→`running`→`done`\|`failed` |
| `createdAt` / `updatedAt` | time | `updatedAt` = heartbeat |

Index: `jobId` unique, `-createdAt`, `(partner, status)`.

### API

| Method | Route | Handler | Validation |
|---|---|---|---|
| POST | `/contents/batch-actions` | `CreateBatchAction` | reuse `v.BatchChangeStatus` (body `ContentBatchChangeStatusBody`) |
| GET | `/contents/batch-actions/:jobId/status` | `GetBatchActionStatus` | check `IsAllowPartner` |

Đặt **TRƯỚC** `/:id` trong router để tránh match nhầm. Lỗi create: `BATCH_ACTION_INVALID_ACTION` / `_EMPTY` / `_TOO_MANY` → 400.

`GET status` trả: `{ jobId, status, processedCount, totalToProcess, successCount, failedCount, percent, failedItems[] }`.

### Apply — điểm bắt buộc

- **Reuse `pkg/admin/service/content.go` `ChangeStatus(..., isBatch=true)`** — giữ nguyên `ActionAfterWhenChangeStatus` (reward/analytics/notification/cache/schema). **Không** raw-update `status`.
- **Idempotent:** trước khi xử lý, nếu `content.status == action` → skip success (tránh re-notification khi double-submit).
- **Nghỉ theo lô** (`50 item / 500ms`) cho side-effect goroutine kịp drain.

### Frontend

- `admin/src/configs/api.ts` — thêm `createBatchAction`, `getBatchActionStatus`.
- `admin/src/services/content.ts` — 2 hàm gọi API.
- `admin/src/pages/content/model.ts` — effect `batchChangeStatus` viết lại: create → poll (2.5s, trần 240 lần ≈ 10') → `message.loading "X/Y"` → xong: `Modal.warning` liệt kê `contentId — reason` (không lỗi → notification success) → `getList`.
- **UI component (index.tsx/table.tsx) không đổi** — cùng effect cho cả duyệt & từ chối.

---

## Implementation Plan

| # | Hạng mục | File |
|---|---|---|
| 1 | Collection const + model + DAO + index | `model/mg/content_batch_action.go`, `dao/content_batch_action.go`, `collection.go`, `index.go` |
| 2 | Response structs | `pkg/admin/model/response/content_batch_action.go` |
| 3 | Service async | `pkg/admin/service/content_batch_action.go` |
| 4 | Handler + router | `pkg/admin/handler/content.go`, `pkg/admin/router/content.go` |
| 5 | Frontend | `api.ts`, `services/content.ts`, `pages/content/model.ts` |

---

## Acceptance Criteria

1. Duyệt/từ chối lô lớn (>50) → **không kẹt "chờ duyệt"**, không phụ thuộc timeout request.
2. FE hiện tiến độ X/Y khi chạy.
3. Có item lỗi → modal liệt kê đúng `contentId + lý do`; item OK vẫn đổi trạng thái.
4. Content cross-partner → vào `failedItems` (lý do no-permission), không chặn cả lô.
5. Double-submit → idempotent, không đổi trạng thái lần 2.
6. Poll mất kết nối liên tục → dừng, báo "tải lại trang".

---

## Non-Functional Requirements

- Job 2000 item chạy nền không OOM (nghỉ theo lô).
- Goroutine dùng `context.Background()` — không chết theo request.
- Redis mutex + heartbeat: job chết (pod restart) không kẹt.
- FE poll nhẹ (mỗi 2.5s, trần 240 lần).

---

## Dependencies

- `pkg/admin/service/content.go` `ChangeStatus(isBatch=true)` (đã có).
- `internal/module/redis` `NewMutexWithExpiration` (đã có).
- MongoDB + Redis.

---

## Risks & Mitigation

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Job chết giữa chừng | TB | Redis mutex + heartbeat `updatedAt`; recover panic → failed |
| Double-click 2 job cùng IDs | Thấp | Idempotent skip theo target status (còn khe hẹp noti trùng — hardening: disable nút / khoá per-partner) |
| Lô quá lớn | Thấp | Cap 2000; nghỉ theo lô |
| Cross-partner | Thấp | Ghi `failedItems`, không chặn cả lô |

---

## Timeline

~1.5–2 ngày công (BE ~1–1.5 ngày, FE ~0.5 ngày). Đã implement.

---

## Approval

- Verify: `go build` ✅, `tsc --noEmit` không lỗi mới ✅.
- **Chưa e2e** (cần Mongo+Redis+server) — chờ QA.

---

## Next Steps

1. QA e2e: lô nhỏ, lô >50, cross-partner, double-click, mất kết nối khi poll.
2. Cân nhắc hardening: disable nút bulk khi job chạy + nút copy ID lỗi.
3. Sau khi ổn: gỡ endpoint cũ `/contents/batch-status`.
4. Quyết định có đưa lên `main` không (stack trên `feat/import-content-to-reject-to-main`).
