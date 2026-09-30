# Kỳ đi tiền (Transfer Period) — lộ trình và backlog

> **Trang đầu của bộ tài liệu này.** Đọc file này để nắm kế hoạch triển khai, mở PRD khi cần chi tiết thiết kế.
> **Ngày:** 2026-09-30 · **Trạng thái:** chờ chốt PB-02, PB-03, PB-04 và scope web admin (mục "Đang chặn").
> **Theo dõi trạng thái hằng ngày:** [Google Sheet backlog](https://docs.google.com/spreadsheets/d/16dQ1bMzXZTIUaZPSg8QpvYyi23Fa9ZbhE8BqbmfY8uQ/edit?gid=1159342900#gid=1159342900). File này là bản chốt kế hoạch; sheet là nơi cập nhật trạng thái từng task.

---

## Bộ tài liệu

| File | Dành cho | Nội dung |
| --- | --- | --- |
| [`PRD.md`](./PRD.md) | Tất cả | Bài toán, giải pháp, user stories, module M1–M10, contract API, kịch bản test |
| **`lo-trinh.md`** *(đang đọc)* | Dev · QA · PO | Lịch, effort, việc đang chặn, backlog 43 task chia theo phase |

---

## Tóm tắt

- **Phạm vi:** repo `CB-MBBank/withdraw` (chính), `CB-MBBank/user`, submodule `external`, cộng web admin (FE, chờ PO xác nhận scope).
- **Effort:** 38 ngày công cho 43 task, gồm 2 BE, 1 FE, 1 QA và Lead.
- **Lịch:** bắt đầu thứ Hai 05/10/2026; code complete 20/10; QA trên dev 21–23/10; deploy production 26/10; theo dõi đến 30/10.
- **Sprint 1:** 05/10 – 16/10 · **Sprint 2:** 19/10 – 30/10.
- **Đường găng:** contract `external` → schema → tính số dư có `waiting_process` → tách tạo lệnh / chuyển khoản → Executor → Collector → QA → rollout.

---

## Mốc

| Ngày | Mốc | Điều kiện đạt |
| --- | --- | --- |
| 02/10 | Chốt thiết kế | PB-02, PB-03, PB-04 có quyết định, ghi lại vào PRD |
| 13/10 | Lõi `withdraw` an toàn | Test hồi quy PB-11 pass: luồng tự rút, batch, sandbox không đổi hành vi |
| 20/10 | Code complete | Toàn bộ task BE xong, merge vào nhánh tính năng |
| 23/10 | QA sign-off | Chạy xong 7 kịch bản PRD mục 5.3, không còn bug mức Must |
| 26/10 | Production | Deploy `withdraw` → env → `user`; kỳ đầu chạy mode `manual` |
| 30/10 | Ổn định | Kỳ chạy ổn 2–3 ngày, chuyển mode mặc định về `auto` |

---

## Effort

| Phase | Nội dung | Số task | Ngày công |
| --- | --- | --- | --- |
| P0 | [Chuẩn bị và chốt thiết kế](#p0) | 4 | 1 |
| P1 | [Nền tảng: contract và schema](#p1) | 4 | 3 |
| P2 | [Lõi withdraw: kỳ, tạo lệnh, reject, stats](#p2) | 8 | 7.5 |
| P3 | [Bộ đi tiền (Executor)](#p3) | 4 | 4.5 |
| P4 | [API admin (/admin/withdraw) + Web admin](#p4) | 10 | 10.5 |
| P5 | [Service user: bộ gom lệnh](#p5) | 3 | 2 |
| P6 | [Việc chung](#p6) | 2 | 1.5 |
| P7 | [QA và rollout](#p7) | 8 | 8 |
| | **Tổng** | **43** | **38** |

| Đầu mối | Ngày công |
| --- | --- |
| BE-A | 13 |
| BE-B | 13 |
| FE | 4 |
| QA | 4 |
| Lead | 4 |

*Task có hai đầu mối ("Lead + PO", "Lead + Ops") tính vào Lead.*

---

## Đang chặn

| # | Việc cần chốt | Ai chốt | Hạn | Ảnh hưởng nếu chậm |
| --- | --- | --- | --- | --- |
| 1 | **PB-02** — Kỳ `collecting` quá hạn 2h tính từ đâu. Đề xuất thêm `collectStartedAt` | Lead + PO | 02/10 | Chặn PB-09 (vòng đời kỳ) |
| 2 | **PB-03** — Chỉ pod giữ lock scanner mới gọi `collect.done` | Lead + PO | 02/10 | Chặn PB-32 (collector) |
| 3 | **PB-04** — Timeout gọi AT nhỏ hơn TTL lock 5 phút; giá trị env | Lead + vận hành | 02/10 | Chặn PB-31 và cấu hình rollout |
| 4 | **Scope web admin** — PRD mục 6 đang để FE ngoài phạm vi, backlog đã thêm PB-29, PB-30 | PO | trước 14/10 | Nếu không duyệt thì bỏ 4 ngày FE |

---

## Rủi ro cần theo dõi

- **Chi trùng tiền** nếu PB-07 thiếu hoặc sai. Bắt buộc có test và Lead review trước khi có luồng nào tạo lệnh `waiting_process`.
- **Tách tạo lệnh / chuyển khoản (PB-10)** đụng luồng tiền đang chạy production. PB-11 pass là điều kiện để merge.
- **Thứ tự deploy:** `withdraw` trước, `user` sau. Ngược lại thì `withdraw` cũ bỏ qua cờ chờ và chuyển tiền ngay lúc gom.
- **PB-29 sát lịch:** cần API đi tiền / dừng (PB-27) cũng xong ngày 20/10. FE làm trước theo contract PRD mục 4.4.
- **Chưa có buffer fix bug cho FE:** PB-40 chỉ tính phần BE.

---

## Backlog

Quy ước: **Loại** Feature / Tech / Chore / Bug · **Ưu tiên** Must / Should · **Est** tính bằng ngày công · deadline năm 2026.

### P0

**Chuẩn bị và chốt thiết kế** · 1 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-01 | Tạo nhánh từ release cho withdraw, user, external | Chore | Must | Sprint 1 | Lead | 02/10 | withdraw, user, external | 0.25 | — |
| PB-02 | Chốt cách tính kỳ 'collecting' quá hạn 2h | Tech | Must | Sprint 1 | Lead + PO | 02/10 | withdraw (M1) | 0.25 | — |
| PB-03 | Chốt điều kiện gọi collect.done khi có nhiều pod worker | Tech | Must | Sprint 1 | Lead + PO | 02/10 | user (M8) | 0.25 | — |
| PB-04 | Kiểm tra timeout gọi AT và chốt giá trị env với vận hành | Tech | Must | Sprint 1 | Lead | 02/10 | withdraw, user | 0.25 | — |

**PB-01 · Tạo nhánh từ release cho withdraw, user, external**

- Nhánh mới tạo từ release ở cả 3 repo. Code TransferPeriod cũ (withdraw/develop, user/feature/update-transfer) chỉ đọc tham khảo, không merge.

**PB-02 · Chốt cách tính kỳ 'collecting' quá hạn 2h**

- Vấn đề: lệnh user tự rút lúc 00:30 đã tạo kỳ, đến 04:00 collector chạy thì kỳ đã quá 2h, admin bấm đi tiền sẽ chạy trên kỳ đang gom dở.
- Đề xuất: thêm field collectStartedAt, tính 2h từ đó.
- Kết quả: quyết định được ghi lại vào PRD.

**PB-03 · Chốt điều kiện gọi collect.done khi có nhiều pod worker**

- Vấn đề: pod không lấy được lock scanner vẫn gọi collect.done, kỳ sang waiting khi pod khác còn đang quét.
- Đề xuất: chỉ pod giữ lock scanner mới gọi collect.done.

**PB-04 · Kiểm tra timeout gọi AT và chốt giá trị env với vận hành**

- Timeout HTTP client gọi AT phải nhỏ hơn TTL lock đi tiền (5 phút).
- Chốt: AUTO_WITHDRAW_COLLECT_CRON (sau job thả tiền 01:00 của MBBank), TRANSFER_PERIOD_EXECUTE_CRON, TRANSFER_PERIOD_DEFAULT_MODE, TRANSFER_PERIOD_MAX_CONSECUTIVE_FAIL.

### P1

**Nền tảng: contract và schema** · 3 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-05 | external: thêm status waiting_process và contract NATS mới | Tech | Must | Sprint 1 | BE-A | 05/10 | external (M10) | 0.5 | PB-01 |
| PB-06 | withdraw: collection transfer-periods và field transferPeriodId trên lệnh rút | Tech | Must | Sprint 1 | BE-A | 06/10 | withdraw (4.3) | 1 | PB-05 |
| PB-07 | Số dư user tính cả lệnh waiting_process (chống chi trùng) | Tech | Must | Sprint 1 | BE-A | 07/10 | withdraw (4.3) | 1 | PB-05 |
| PB-08 | Luật trạng thái lệnh: map hiển thị, mở rộng filter, bảng chuyển trạng thái | Tech | Must | Sprint 1 | BE-B | 05/10 | withdraw (M3) | 0.5 | PB-05 |

**PB-05 · external: thêm status waiting_process và contract NATS mới**

- Subject mới: withdrawal:transfer.period.create {date} → {id}; withdrawal:transfer.period.collect.done {id} → {ok}.
- withdrawal:create thêm transferPeriodId (string), waitingProcess (bool, mặc định false).
- Mọi field mới optional, payload cũ vẫn decode được.

**PB-06 · withdraw: collection transfer-periods và field transferPeriodId trên lệnh rút**

- transfer-periods: date (đầu ngày HCM, unique), type, mode, status, stopRequested, stopReason, executedBy, executedAt, finishedAt. Index: date unique, status, -createdAt.
- withdraw: thêm transferPeriodId (ObjectID, có thể rỗng) và index {transferPeriodId: 1, status: 1}.
- Dữ liệu cũ không cần migrate (US 59).

**PB-07 · Số dư user tính cả lệnh waiting_process (chống chi trùng)**

- Hàm tổng hợp lệnh rút theo user cộng waiting_process vào tiền pending.
- gRPC balance-flow trả cả lệnh waiting_process (US 54).
- Test: tạo lệnh waiting_process thì currentCash giảm đúng số tiền. Lead review bắt buộc.

**PB-08 · Luật trạng thái lệnh: map hiển thị, mở rộng filter, bảng chuyển trạng thái**

- Hàm thuần, có unit test:
  - Hiển thị cho app/CRM: waiting_process → pending.
  - Filter pending → {pending, waiting_process}.
  - waiting_process chỉ được sang rejected; pending sang rejected (admin, CRM) hoặc success (chỉ CRM); success, rejected bị khoá.
- Test không import package có init() đọc file (locale).

### P2

**Lõi withdraw: kỳ, tạo lệnh, reject, stats** · 7.5 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-09 | Vòng đời kỳ: lấy/tạo kỳ theo ngày, gom xong, đổi mode, yêu cầu dừng | Feature | Must | Sprint 1 | BE-A | 08/10 | withdraw (M1) | 1.5 | PB-06, PB-02 |
| PB-10 | Tách hàm tạo lệnh và hàm chuyển khoản | Tech | Must | Sprint 1 | BE-A | 12/10 | withdraw (M5) | 2 | PB-07, PB-09 |
| PB-11 | Test hồi quy luồng tự rút, batch xlsx, sandbox sau khi tách | Tech | Must | Sprint 1 | BE-A | 13/10 | withdraw (M5) | 1 | PB-10 |
| PB-12 | NATS handler tạo kỳ, gom xong; withdrawal:create nhận field mới | Feature | Must | Sprint 1 | BE-B | 15/10 | withdraw (M10) | 0.5 | PB-09, PB-10 |
| PB-13 | Reject nguyên tử dùng chung, nối vào CRM đơn lẻ và hàng loạt | Feature | Must | Sprint 1 | BE-B | 06/10 | withdraw (M3) | 1 | PB-08 |
| PB-14 | API danh sách lệnh của app và CRM hiển thị waiting_process là pending | Feature | Must | Sprint 1 | BE-B | 06/10 | withdraw (M3) | 0.5 | PB-08 |
| PB-15 | Stats kỳ bằng một aggregation | Feature | Must | Sprint 1 | BE-B | 07/10 | withdraw (M4) | 0.5 | PB-06 |
| PB-16 | Cron sync lệnh pending phân trang bằng cursor _id | Tech | Must | Sprint 1 | BE-B | 14/10 | withdraw (M9) | 0.5 | — |

**PB-09 · Vòng đời kỳ: lấy/tạo kỳ theo ngày, gom xong, đổi mode, yêu cầu dừng**

- Upsert theo đầu ngày HCM, gặp trùng khoá thì đọc lại.
- IS_AUTO_WITHDRAW=true → scheduled / collecting / mode từ env. false → instant / done / mode rỗng. Kỳ đã tồn tại giữ nguyên type.
- Gom xong: chỉ scheduled collecting → waiting, idempotent. Đổi mode khi collecting/waiting. Dừng khi processing.
- Ma trận 'được đi tiền' theo bảng mục 4.2. Test theo 5.2 M1 (US 1-2, 6, 6a, 8-10, 16-18).

**PB-10 · Tách hàm tạo lệnh và hàm chuyển khoản**

- Tạo lệnh: lock theo user, giữ toàn bộ kiểm tra hiện có, gán kỳ (từ request, không có thì kỳ hôm nay). Có cờ chờ → waiting_process, không gọi bank; không cờ → pending.
- Chuyển khoản: giữ nguyên phần gọi bank (communication/AT và legacy MBBank), là điểm cắm riêng từng bank.
- Hàm cũ = tạo lệnh, rồi chuyển khoản nếu status pending. Lead review bắt buộc.

**PB-11 · Test hồi quy luồng tự rút, batch xlsx, sandbox sau khi tách**

- Fake bank trả success / pending / lỗi có hoàn tiền / lỗi không hoàn: cùng status, cùng biến động số dư, cùng thông báo như trước khi tách.
- Có cờ chờ: lệnh waiting_process, số dư đã trừ, không gọi bank. Không có id kỳ: tự gắn kỳ hôm nay.
- Điều kiện bắt buộc để merge PB-10 (US 11-15).

**PB-12 · NATS handler tạo kỳ, gom xong; withdrawal:create nhận field mới**

- Đăng ký khi ENABLE_WORKER, cùng chỗ với handler tạo lệnh.
- Payload cũ (không có field mới) vẫn chạy như trước (US 57).

**PB-13 · Reject nguyên tử dùng chung, nối vào CRM đơn lẻ và hàng loạt**

- Cập nhật có điều kiện status ∈ {pending, waiting_process} → rejected, kèm người cập nhật và thời điểm. Không khớp → 409. Khớp → hoàn tiền và gửi thông báo như CRM.
- CRM chặn waiting_process → success.
- Test: 2 lần reject song song chỉ hoàn tiền 1 lần (US 45-47, 52).

**PB-14 · API danh sách lệnh của app và CRM hiển thị waiting_process là pending**

- Áp dụng map hiển thị và mở rộng filter pending. App webview và CRM không phải sửa (US 50-51).

**PB-15 · Stats kỳ bằng một aggregation**

- stats(danh sách id kỳ) → map. Lọc transferPeriodId ∈ ids, nhóm theo (kỳ, status), đếm lệnh và cộng tiền.
- Tính lúc đọc, không lưu. Kỳ không có lệnh → toàn 0 (US 37-38).

**PB-16 · Cron sync lệnh pending phân trang bằng cursor _id**

- Đổi skip sang cursor _id; filter vẫn chỉ pending; webhook AT giữ nguyên.
- Test: có lệnh rời filter giữa chừng thì mọi lệnh pending vẫn được duyệt đúng 1 lần (US 53, 55).

### P3

**Bộ đi tiền (Executor)** · 4.5 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-17 | Bộ đi tiền: lock, duyệt cursor, kiểm tra lại user, giành quyền nguyên tử | Feature | Must | Sprint 1 | BE-A | 16/10 | withdraw (M2) | 2.5 | PB-09, PB-10 |
| PB-18 | Circuit breaker dừng sau N lỗi liên tiếp | Feature | Must | Sprint 1 | BE-A | 16/10 | withdraw (M2) | 0.5 | PB-17 |
| PB-19 | Bộ test Executor | Tech | Must | Sprint 2 | BE-A | 19/10 | withdraw (M2) | 1 | PB-18 |
| PB-20 | Cron tự đi tiền các kỳ auto | Feature | Must | Sprint 2 | BE-A | 20/10 | withdraw (M2) | 0.5 | PB-17 |

**PB-17 · Bộ đi tiền: lock, duyệt cursor, kiểm tra lại user, giành quyền nguyên tử**

- Redis SetNX theo id kỳ, TTL 5 phút, heartbeat sau mỗi lệnh. Set processing, executedBy, executedAt.
- Mỗi trang 50 lệnh waiting_process có _id > lastId. Mỗi lệnh: đọc lại stopRequested; user bị ban hoặc currentCash < 0 → bỏ qua, giữ waiting_process; giành quyền waiting_process → pending; gọi chuyển khoản; nghỉ 2s.
- Kết thúc: stopped + stopReason, hoặc done + finishedAt. Chuyển khoản, kiểm tra user, đồng hồ, sleep được inject (US 20-30).

**PB-18 · Circuit breaker dừng sau N lỗi liên tiếp**

- Hàm chuyển khoản phải phân biệt lỗi (mạng, timeout, mã AT lỗi, legacy lỗi) với pending không lỗi (INIT, PENDING, PROCESSING, VERIFYING).
- Lỗi liên tiếp ≥ TRANSFER_PERIOD_MAX_CONSECUTIVE_FAIL → stopped, stopReason = circuit_breaker, log Error (US 32-35).

**PB-19 · Bộ test Executor**

- 11 kịch bản mục 5.2 M2: N lệnh chạy xong done; lock chặn chạy song song; lệnh bị reject trước khi giành quyền không bị chuyển; lệnh bỏ qua không gây lặp vô hạn; dừng giữa chừng; circuit breaker; pending không lỗi không làm dừng; lỗi xen kẽ không dừng; đi tiền lại kỳ stopped/done; lock hết hạn thì chạy tiếp được.

**PB-20 · Cron tự đi tiền các kỳ auto**

- Giờ chạy theo TRANSFER_PERIOD_EXECUTE_CRON.
- Chỉ lấy kỳ scheduled, mode auto, trạng thái waiting / processing / collecting quá hạn, kỳ cũ trước. Kỳ stopped không tự chạy lại (US 19, 34).

### P4

**API admin (/admin/withdraw) + Web admin** · 10.5 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-21 | Khung khu vực admin và middleware RequireAdmin | Tech | Must | Sprint 1 | BE-B | 07/10 | withdraw (M7) | 0.5 | — |
| PB-22 | API danh sách kỳ và chi tiết kỳ kèm stats (#1, #2) | Feature | Must | Sprint 1 | BE-B | 08/10 | withdraw (M7) | 1 | PB-15, PB-21 |
| PB-23 | API danh sách lệnh của kỳ, status thô (#6) | Feature | Must | Sprint 1 | BE-B | 09/10 | withdraw (M7) | 0.5 | PB-21 |
| PB-24 | API xem log request/response AT của một lệnh (#7) | Feature | Must | Sprint 1 | BE-B | 12/10 | withdraw (M6) | 1 | PB-21 |
| PB-25 | API reject lệnh (#8) | Feature | Must | Sprint 1 | BE-B | 12/10 | withdraw (M7) | 0.5 | PB-13, PB-21 |
| PB-26 | API export CSV lệnh của kỳ (#5b) | Feature | Must | Sprint 1 | BE-B | 14/10 | withdraw (M6b) | 1.5 | PB-22 |
| PB-27 | API đổi mode, đi tiền, dừng (#3, #4, #5) | Feature | Must | Sprint 2 | BE-B | 20/10 | withdraw (M7) | 1 | PB-17, PB-22 |
| PB-28 | Locale message, mã lỗi, Postman collection | Chore | Should | Sprint 2 | BE-B | 20/10 | withdraw | 0.5 | PB-22 → PB-27 |
| PB-29 | Web admin: danh sách kỳ, chi tiết kỳ, đổi mode / đi tiền / dừng, export CSV | Feature | Must | Sprint 2 | FE | 20/10 | web admin (FE) | 2.5 | PB-22, PB-27 |
| PB-30 | Web admin: danh sách lệnh của kỳ, xem log AT, reject lệnh | Feature | Must | Sprint 2 | FE | 22/10 | web admin (FE) | 1.5 | PB-23, PB-24, PB-25, PB-29 |

**PB-21 · Khung khu vực admin và middleware RequireAdmin**

- Route, controller, service, model theo khuôn admin của service user; mount /admin/withdraw.
- RequireAdmin giống hệt user/brand (JWT hợp lệ có user id), không dùng xác thực CRM (US 49).

**PB-22 · API danh sách kỳ và chi tiết kỳ kèm stats (#1, #2)**

- Query: page, limit, fromDate, toDate, type, status, mode; sort date giảm dần. 404 khi không có kỳ.
- Trả executedBy, executedAt, finishedAt, stopReason để kiểm toán (US 36-40).

**PB-23 · API danh sách lệnh của kỳ, status thô (#6)**

- Query: transferPeriodId, status, user, page, limit. Không map waiting_process (US 41).

**PB-24 · API xem log request/response AT của một lệnh (#7)**

- Tra communication theo clientMessageId, đúng cặp reqTo/purpose như lúc gửi.
- Trả requestId, url, method, query, body, response, statusCode, createdAt, completedAt, parsed {code, transferStatus, refTxnId}.
- 404 'chưa có log giao dịch' (gồm nhánh legacy); 400 communication chưa cấu hình (US 42-44).

**PB-25 · API reject lệnh (#8)**

- Body chỉ nhận status = rejected. 400 khi status khác hoặc lệnh không ở pending/waiting_process; 409 khi lệnh vừa đổi trạng thái (US 45-48).

**PB-26 · API export CSV lệnh của kỳ (#5b)**

- Stream thẳng vào response, cursor _id, lô 500, mỗi lô gọi gRPC user 1 lần. BOM UTF-8, 16 cột theo PRD, giờ HCM.
- gRPC lỗi → tên và CIF để trống, log Warn. Tên file `transfer-period_<YYYY-MM-DD>_<status|all>.csv`.
- Test theo 5.2 M6b (US 40a, 40b).

**PB-27 · API đổi mode, đi tiền, dừng (#3, #4, #5)**

- Đi tiền: lấy lock và kiểm tra trạng thái đồng bộ, trả 202 rồi chạy nền.
- 400 khi kỳ instant hoặc trạng thái không hợp lệ; 409 khi đang có tiến trình đi tiền (US 17-18, 20-22, 31).

**PB-28 · Locale message, mã lỗi, Postman collection**

- Message theo khuôn response chuẩn của service. Postman collection giao cho FE dùng ở PB-29, PB-30.

**PB-29 · Web admin: danh sách kỳ, chi tiết kỳ, đổi mode / đi tiền / dừng, export CSV**

- Lưu ý: PRD mục 6 đang để giao diện admin ngoài phạm vi, cần PO xác nhận đưa vào scope.
- Danh sách kỳ: lọc ngày, type, status, mode; phân trang; hiện stats theo từng status (số lệnh và tổng tiền).
- Chi tiết kỳ: stats, executedBy / executedAt, finishedAt, stopReason.
- Nút đổi mode, Đi tiền, Dừng: ẩn với kỳ instant; đi tiền trả 202 thì hiện 'đang chạy' và tự refresh; hiện đúng lỗi 400 / 409.
- Nút export CSV: toàn bộ hoặc lọc theo status.
- Làm trước theo contract API ở PRD mục 4.4, nối API thật khi PB-22, PB-27 xong.

**PB-30 · Web admin: danh sách lệnh của kỳ, xem log AT, reject lệnh**

- Danh sách lệnh: lọc status (hiện status thô, có waiting_process) và user; phân trang.
- Xem log AT: request, response và các trường đã parse (code, transferStatus, refTxnId); lỗi 404 thì hiện 'chưa có log giao dịch'.
- Reject: chỉ bật với lệnh pending / waiting_process; lệnh pending phải hiện cảnh báo 'bank có thể đã chuyển tiền, xem log AT trước khi reject' (PRD mục 7); xử lý 409.

### P5

**Service user: bộ gom lệnh** · 2 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-31 | Config env AUTO_WITHDRAW_COLLECT_CRON | Tech | Must | Sprint 1 | BE-B | 15/10 | user (config) | 0.25 | PB-04 |
| PB-32 | Collector thay cron auto withdraw giờ cố định | Feature | Must | Sprint 2 | BE-B | 19/10 | user (M8) | 1.5 | PB-03, PB-12, PB-31 |
| PB-33 | Kiểm tra công cụ sandbox trigger theo danh sách user | Tech | Should | Sprint 2 | BE-B | 19/10 | user | 0.25 | PB-32 |

**PB-31 · Config env AUTO_WITHDRAW_COLLECT_CRON**

- Mặc định 0 0 4 * * *. Có test ở package config.

**PB-32 · Collector thay cron auto withdraw giờ cố định**

- Chỉ chạy khi ENABLE_WORKER. Gọi NATS tạo kỳ; nếu IS_AUTO_WITHDRAW thì chạy scanner hiện có (giữ lock, điều kiện, LIMIT_WITHDRAW, nhịp) và gửi withdrawal:create kèm transferPeriodId, waitingProcess = true.
- Luôn gọi collect.done ở cuối, kể cả khi lỗi (theo quyết định PB-03). Tạo kỳ lỗi → không quét, log lỗi.
- Test với fake NATS (US 3-5, 7).

**PB-33 · Kiểm tra công cụ sandbox trigger theo danh sách user**

- Không gửi cờ chờ, vẫn chuyển tiền ngay và có gắn kỳ hôm nay (US 14).

### P6

**Việc chung** · 1.5 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-34 | Trace id và mức log xuyên suốt gom, tạo lệnh, đi tiền | Tech | Should | Sprint 2 | BE-A | 20/10 | withdraw, user | 0.5 | PB-17, PB-32 |
| PB-35 | Review các PR rủi ro cao | Chore | Must | Sprint 2 | Lead | 20/10 | withdraw | 1 | — |

**PB-34 · Trace id và mức log xuyên suốt gom, tạo lệnh, đi tiền**

- Lỗi từng lệnh trong vòng lặp log ErrorSilent; circuit breaker log Error để bắn cảnh báo (US 58).

**PB-35 · Review các PR rủi ro cao**

- Review bắt buộc PB-07, PB-10, PB-13, PB-17.
- Checklist: cập nhật có điều kiện (nguyên tử), hoàn tiền đúng 1 lần, test thuần không import package có init().

### P7

**QA và rollout** · 8 ngày công

| ID | Task | Loại | Ưu tiên | Sprint | Đầu mối | Deadline | Repo / Module | Est | Phụ thuộc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PB-36 | Viết test case | Chore | Must | Sprint 1 | QA | 14/10 | — | 1 | — |
| PB-37 | Deploy dev và smoke test | Chore | Must | Sprint 2 | Lead | 21/10 | withdraw, user | 0.5 | PB-27, PB-30, PB-32 |
| PB-38 | QA test trên dev | Chore | Must | Sprint 2 | QA | 23/10 | — | 3 | PB-36, PB-37 |
| PB-39 | Fix bug QA phần lõi withdraw | Bug | Must | Sprint 2 | BE-A | 23/10 | withdraw | 1 | PB-38 |
| PB-40 | Fix bug QA phần API admin và collector | Bug | Must | Sprint 2 | BE-B | 23/10 | withdraw, user | 1 | PB-38 |
| PB-41 | Runbook rollout và rollback | Chore | Must | Sprint 2 | Lead | 23/10 | — | 0.5 | — |
| PB-42 | Deploy production, kỳ đầu chạy mode manual | Chore | Must | Sprint 2 | Lead + Ops | 26/10 | withdraw, user | 0.5 | PB-38, PB-41 |
| PB-43 | Theo dõi kỳ đầu, chuyển mode mặc định về auto | Chore | Must | Sprint 2 | Lead | 30/10 | withdraw | 0.5 | PB-42 |

**PB-36 · Viết test case**

- 7 kịch bản thủ công mục 5.3, cộng hồi quy app, CRM (danh sách, reject đơn lẻ, reject hàng loạt), webhook AT, batch xlsx, sandbox.

**PB-37 · Deploy dev và smoke test**

- Deploy withdraw trước, user sau; set env trên dev; trigger collector bằng tay.

**PB-38 · QA test trên dev**

- Chạy toàn bộ test case, log bug. Sign-off khi không còn bug mức Must.

**PB-39 · Fix bug QA phần lõi withdraw**

- Buffer cho bug ở kỳ, tạo lệnh, executor.

**PB-40 · Fix bug QA phần API admin và collector**

- Buffer cho bug ở API admin, export, collector.

**PB-41 · Runbook rollout và rollback**

- Thứ tự bắt buộc: withdraw → env common.env → user.
- Rollback user khi còn lệnh waiting_process: đi tiền tay qua API admin.
- Nhắc vận hành xem log AT trước khi reject lệnh pending.

**PB-42 · Deploy production, kỳ đầu chạy mode manual**

- Ngày đầu set TRANSFER_PERIOD_DEFAULT_MODE = manual.
- Smoke: lệnh user tự rút có transferPeriodId; cron auto withdraw cũ đã tắt.

**PB-43 · Theo dõi kỳ đầu, chuyển mode mặc định về auto**

- Đối chiếu stats kỳ với cách tính cũ, admin bấm đi tiền, theo dõi log và circuit breaker. Chạy ổn 2-3 ngày thì đổi mode mặc định về auto.
