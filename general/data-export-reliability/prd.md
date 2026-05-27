# PRD — Độ tin cậy cho chức năng Xuất dữ liệu (Data-Export Reliability)

**Ngày:** 27/05/2026
**Trạng thái:** Đề xuất
**Sản phẩm:** vCreator (admin)
**Module:** `pkg/admin/service/export.go`, `pkg/admin/schedule`, collection `data_export`
**Overview:** [`overview.md`](./overview.md)

> Ngôn ngữ: narrative tiếng Việt, technical terms giữ tiếng Anh. Mỗi FR + acceptance criteria là nguồn sinh test case.

---

## 1. Bối cảnh & mục tiêu

Chức năng data-export dùng MongoDB collection `data_export` làm hàng đợi, với state machine: `waiting → running → completed | failed`. Bộ điều phối (`CheckRun`) giới hạn 2 job `running` đồng thời và được trigger bởi cron (mỗi giờ) + ngay khi user tạo job.

Ba lỗi độ tin cậy đã được xác minh trong mã nguồn:
1. Job kẹt vĩnh viễn ở `running` khi process chết giữa chừng (bước chuyển `completed/failed` nằm trong `defer`, không chạy khi crash).
2. Hai job stuck `running` → bộ đếm khóa ở 2 → mọi job sau kẹt `waiting` vĩnh viễn.
3. Sau migrate reset `running→failed`, cron chỉ đẩy 1 job/lượt → backlog xả 1 job/giờ.
4. (Phụ) Race condition: đếm-rồi-update không atomic giữa cron và đường `go CheckRun()`.

**Mục tiêu:** hệ thống tự phục hồi sau sự cố, không kẹt cứng, không cần can thiệp DB thủ công, và xả backlog kịp thời.

**Success metrics:**
- 0 job kẹt `running` quá ngưỡng phát hiện mà không bị reap.
- Sau sự cố/migrate, chức năng export hoạt động lại tự động trong ≤ 8 phút mà không cần thao tác tay.
- Không còn ticket vận hành "phải sửa DB cho export".

---

## 2. Yêu cầu chức năng (Functional Requirements)

### FR-01 — Đánh dấu thời điểm bắt đầu chạy
Khi một job chuyển từ `waiting` sang `running`, hệ thống phải ghi nhận thời điểm bắt đầu (`startedAt`) và nhịp tim đầu tiên (`heartbeatAt`).

**Acceptance criteria:**
- AC-01.1: Sau khi job chuyển `running`, bản ghi có `startedAt` = thời điểm chuyển, khác zero.
- AC-01.2: Sau khi job chuyển `running`, bản ghi có `heartbeatAt` = `startedAt` (xấp xỉ, cùng thời điểm).

### FR-02 — Nhịp tim định kỳ khi đang chạy
Trong suốt thời gian job ở `running`, hệ thống phải cập nhật `heartbeatAt` định kỳ mỗi `HEARTBEAT_INTERVAL` (mặc định 1 phút) cho tới khi job kết thúc.

**Acceptance criteria:**
- AC-02.1: Với job chạy lâu hơn 1 phút, `heartbeatAt` được cập nhật ít nhất 1 lần sau `startedAt` (giá trị tăng dần).
- AC-02.2: Heartbeat chỉ cập nhật khi job vẫn ở `running`; sau khi job `completed/failed`, không còn cập nhật `heartbeatAt`.
- AC-02.3: Khi process chứa job bị chết (kill/crash), `heartbeatAt` ngừng tăng (không có tiến trình nào đập hộ).

### FR-03 — Tự động phát hiện và đánh thất bại job chết
Trước mỗi lần điều phối, hệ thống phải rà soát các job đang `running` mà `heartbeatAt` cũ hơn `STALE_THRESHOLD` (mặc định 3 phút) và chuyển chúng sang `failed` với lý do rõ ràng.

**Acceptance criteria:**
- AC-03.1: Job `running` có `heartbeatAt < now - STALE_THRESHOLD` được chuyển sang `failed`.
- AC-03.2: Job bị reap có `reason` chứa thông điệp chỉ rõ nguyên nhân tự phục hồi (vd "recovered: job ngừng heartbeat").
- AC-03.3: Job `running` còn đập heartbeat bình thường (`heartbeatAt >= now - STALE_THRESHOLD`) KHÔNG bị reap, dù `startedAt` đã rất lâu (job chạy lâu hợp lệ).
- AC-03.4: Bước reap chạy ở đầu mỗi `CheckRun` (cả từ cron lẫn từ API tạo job).

### FR-04 — Giải phóng ô chạy sau khi reap
Sau khi job chết bị đánh `failed`, "ô chạy" phải được trả lại để job `waiting` kế tiếp được xử lý.

**Acceptance criteria:**
- AC-04.1: Có 2 job kẹt `running` (heartbeat quá hạn) + ≥1 job `waiting`. Sau một lần `CheckRun`: 2 job kẹt → `failed`, và job `waiting` được nhận chạy (chuyển `running`).
- AC-04.2: Số job `running` thực tế tại mọi thời điểm không vượt quá `MAX_CONCURRENT` (mặc định 2).

### FR-05 — Claim job atomic (chống xử lý trùng)
Việc nhận một job từ `waiting` sang `running` phải atomic, để hai luồng điều phối đồng thời không thể cùng nhận một job.

**Acceptance criteria:**
- AC-05.1: Khi gọi `CheckRun` đồng thời từ 2 nguồn (cron + API tạo job) trên cùng tập `waiting`, mỗi job chỉ được claim đúng một lần (không job nào bị xử lý 2 lần).
- AC-05.2: Job được claim theo thứ tự FIFO (`_id` tăng dần) như hành vi hiện tại.

### FR-06 — Xả nhiều job mỗi lượt điều phối
Một lượt `CheckRun` phải xử lý nhiều job liên tiếp cho tới khi đạt `MAX_CONCURRENT` hoặc hết `waiting`, thay vì chỉ một job.

**Acceptance criteria:**
- AC-06.1: Có 0 job `running` và 5 job `waiting`. Sau một lượt `CheckRun`, hệ thống xử lý nhiều hơn 1 job (tới giới hạn slot), không dừng sau job đầu.
- AC-06.2: Vòng lặp dừng đúng khi đạt `MAX_CONCURRENT` (không khởi chạy quá giới hạn) hoặc khi hết job `waiting`.

### FR-07 — Cron chạy thường xuyên hơn
Tác vụ định kỳ trigger điều phối phải chạy mỗi 5 phút thay vì mỗi giờ.

**Acceptance criteria:**
- AC-07.1: Lịch cron của job export là `0 */5 * * * *` (mỗi 5 phút), thay cho `0 0 */1 * * *`.
- AC-07.2: Cron vẫn chỉ chạy trên instance master (`IS_MASTER=true`) như cơ chế hiện tại.

### FR-08 — Bước hoàn tất không "hồi sinh" job đã bị reap
Khi một job (bị reap nhầm rồi process thật vẫn hoàn thành) ghi kết quả cuối, hệ thống không được ghi đè trạng thái nếu job đã không còn ở `running`.

**Acceptance criteria:**
- AC-08.1: Bước cập nhật cuối của `RunExport` chỉ áp dụng khi điều kiện gồm `status == running`; nếu job đã bị reap sang `failed`, cập nhật là no-op.
- AC-08.2: Không tồn tại trạng thái cuối cùng bị "lẫn" (vd `completed` ghi đè lên một job đã bị xác định là chết và bỏ).

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

- **NFR-01 (Tự phục hồi):** Hệ thống phục hồi sau crash mà không cần thao tác thủ công vào DB. Thời gian phát hiện job chết ≤ `STALE_THRESHOLD` + chu kỳ cron (≈ ≤ 8 phút với cấu hình mặc định).
- **NFR-02 (Không hồi quy hiệu năng):** Tải thêm lên Mongo do heartbeat không đáng kể (1 update nhỏ/phút/job đang chạy, tối đa 2 job).
- **NFR-03 (Không thêm hạ tầng):** Chỉ dùng MongoDB hiện có; không yêu cầu Redis lock hay message queue mới. Hợp lệ vì cron chỉ chạy trên 1 instance master.
- **NFR-04 (Tương thích dữ liệu cũ):** Job cũ không có `startedAt`/`heartbeatAt` không gây lỗi; có thể cần xử lý migration một lần cho job `running` tồn đọng.
- **NFR-05 (Quan sát được):** Mỗi lần reap ghi log rõ ràng (job id, type, thời điểm heartbeat cuối) để vận hành truy vết.

---

## 4. Migration & vận hành

- **MIG-01:** Một lần sau deploy, reset job kẹt: chuyển mọi `running` hiện hữu (không có heartbeat hợp lệ) sang `failed`. Sau khi có FR-03, không cần lặp lại thủ công.
- **MIG-02:** Thêm index `{status: 1, _id: 1}` cho collection `data_export` để claim/đếm hiệu quả.
- **CFG-01:** Hằng số: `HEARTBEAT_INTERVAL=1m`, `STALE_THRESHOLD=3m`, `MAX_CONCURRENT=2`. Cron `0 */5 * * * *` hardcode (theo quyết định: không đưa vào env).

---

## 5. Epic & phân rã

**Epic: Data-Export Reliability** — biến cơ chế export từ "kẹt cứng khi sự cố" thành "tự phục hồi".

| Story | FR liên quan | Mô tả |
|---|---|---|
| S1 — Heartbeat & recovery | FR-01, FR-02, FR-03, FR-04, FR-08 | Thêm `startedAt`/`heartbeatAt`, ticker đập nhịp, reaper dọn job chết, hoàn tất có điều kiện |
| S2 — Atomic claim | FR-05 | `FindOneAndUpdate` thay cặp find→update |
| S3 — Drain loop | FR-06 | Vòng lặp xử lý nhiều job tới giới hạn slot |
| S4 — Cron tần suất | FR-07 | Đổi lịch cron sang 5 phút |
| S5 — Migration & index | MIG-01, MIG-02 | Reset job kẹt + thêm index |

---

## 6. Out of scope

- Song song thật nhiều luồng `RunExport` chạy đồng thời trong cùng process (hiện đồng bộ tuần tự — đủ dùng; cân nhắc tương lai).
- Chuyển sang message queue chuyên dụng (Asynq/Redis) — chỉ làm khi export trở thành nút nghẽn hoặc cần retry/dead-letter chuẩn.
- Gửi email thông báo khi export xong (field `emails` đã tồn tại nhưng ngoài phạm vi tài liệu này).
- Các luồng upload/import khác.

---

## 7. Tài liệu liên quan

- [`overview.md`](./overview.md) — bản business-friendly
- [`../../../vcreator/plans/data-export-reliability-fix.md`](../../../vcreator/plans/data-export-reliability-fix.md) — implementation plan gốc (chi tiết kỹ thuật, code flow, schema)
