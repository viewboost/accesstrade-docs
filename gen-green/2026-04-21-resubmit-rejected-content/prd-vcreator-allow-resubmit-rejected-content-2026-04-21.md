# PRD: Cho phép submit lại content đã bị reject ở campaign khác

- **Project**: vcreator
- **Owner**: TBD
- **Date**: 2026-04-21
- **Status**: Draft
- **Related code**: [backend/pkg/public/service/content.go:264-273](../../../vcreator/backend/pkg/public/service/content.go#L264-L273)
- **Related**: [tech-spec-resubmit-rejected-content-2026-04-21.md](./tech-spec-resubmit-rejected-content-2026-04-21.md)

---

## 1. Bối cảnh & Vấn đề

Hệ thống vcreator hiện tại chặn **toàn cục** việc submit một link đã tồn tại trong DB (check theo `contentId` — ID bài post trên nền tảng, không phải URL). Check không phân biệt:
- Trạng thái (`waiting_approved` / `approved` / `rejected`)
- Event / campaign nào

**Hệ quả nghiệp vụ**: Nếu creator submit nhầm link vào event A, bị admin reject → **không thể** submit lại link đó vào event B (dù event B hoàn toàn phù hợp). Creator bị mất cơ hội nhận thưởng cho content hợp lệ.

## 2. Mục tiêu

Cho phép creator submit lại một link ở event khác **nếu**:
1. Partner sở hữu event đó có **bật** feature `allowResubmitRejectedContent`, VÀ
2. Tất cả bản ghi trước đó của link này đều đã bị reject.

Partner không bật flag → giữ nguyên behavior cũ (chặn toàn cục).

## 3. Non-goals

- Không thay đổi logic khi link còn `waiting_approved` hoặc `approved` ở bất kỳ event nào → vẫn chặn.
- Không thay đổi flow duyệt/reject của admin.
- Không xây dựng UI cảnh báo lịch sử submit của link (phase sau).
- Không bật flag mặc định cho partner hiện tại — **opt-in** từng partner.

## 4. User Story

**Là** một creator, **tôi muốn** submit một link vào event B ngay cả khi link đó đã từng bị admin reject ở event A, **để** tôi không bị mất cơ hội nhận thưởng cho content hợp lệ của mình.

## 5. Yêu cầu chức năng (Functional Requirements)

### FR-1: Partner-level feature flag
Thêm cấu hình **per-partner** `allowResubmitRejectedContent` (boolean, default `false`):
- Quản lý ở level `Partner` (mỗi partner 1 giá trị riêng).
- Chỉnh sửa được qua admin UI (admin panel của partner).
- Mặc định `false` → giữ behavior hiện tại.
- Chỉ partner được enable mới áp dụng logic mới.

### FR-2: Relax duplicate check (conditional by partner)
Khi creator submit content với `contentId = X` vào `event = E` (thuộc `partner = P`):

**Nếu `P.allowResubmitRejectedContent = false`** (default):

| Trường hợp bản ghi hiện có của `contentId = X` (cùng partner P) | Kết quả |
|---|---|
| Có bất kỳ bản ghi nào (mọi status) | **REJECT** (behavior hiện tại) |
| Không có bản ghi nào | **ALLOW** |

**Nếu `P.allowResubmitRejectedContent = true`**:

| Trường hợp bản ghi hiện có của `contentId = X` (cùng partner P) | Kết quả |
|---|---|
| Tồn tại ít nhất 1 bản ghi có `status ∈ {waiting_approved, approved}` | **REJECT** |
| Tất cả bản ghi đều có `status = rejected` VÀ thuộc event khác E | **ALLOW** (behavior mới) |
| Có bản ghi `status = rejected` thuộc cùng event E | **REJECT** (chống spam submit-reject cùng event) |
| Không có bản ghi nào | **ALLOW** |

**Scope mặc định**: query duplicate check chỉ scan trong cùng `partner`. Cross-partner không check (mỗi partner là 1 tenant độc lập). Xem Open Question #2.

### FR-3: Guard ở admin un-reject flow
Khi admin chuyển 1 content từ `rejected` → `approved` / `waiting_approved`: nếu đã tồn tại bản ghi active khác cùng `contentId` (cùng partner, đã được creator resubmit thành công ở event khác), **phải chặn** hoặc cảnh báo admin. Guard này **áp dụng bất kể partner flag** (vì rủi ro double-count vẫn có dù flag off — admin vẫn có thể vô tình tạo duplicate active qua thao tác thủ công).

### FR-4: Error message
Giữ nguyên message `locale.ContentKeyLinkUsed` ("Nội dung này đã được sử dụng") cho các case vẫn bị reject.

## 6. Yêu cầu phi chức năng (Non-Functional)

### NFR-1: Performance
Query duplicate check phải dùng được index. Cần thêm compound index `(contentId, status)` trên collection `contents`.

### NFR-2: Concurrency safety
Không có unique index trên `contentId`. Hai request song song cùng `contentId` có thể cùng pass check → insert 2 bản ghi active. Cần:
- Option A: Thêm partial unique index `{contentId: 1}` where `status ≠ rejected` (MongoDB hỗ trợ partial index)
- Option B: Dùng optimistic pattern (insert xong check lại, rollback nếu conflict)

**Recommendation**: Option A.

### NFR-3: Backward compatibility
Bản ghi rejected cũ không cần migrate. Logic mới hoạt động trên dữ liệu hiện tại.

## 7. Rủi ro & Mitigation

| # | Rủi ro | Severity | Mitigation |
|---|---|---|---|
| R1 | Gian lận reward: admin un-reject content cũ sau khi creator đã submit lại ở event khác → double-count | **HIGH** | FR-3 (guard un-reject) |
| R2 | Race condition 2 request song song | MEDIUM-HIGH | NFR-2 (partial unique index) |
| R3 | Cross-partner leak: content bị reject ở partner A lại được submit ở partner B | MEDIUM-LOW | Query scope theo `partner` (FR-2). Không quan trọng vì mỗi partner là tenant độc lập. |
| R7 | Partner bật flag nhầm → loose check → content gian lận lọt qua | MEDIUM | Admin UI có confirm dialog; log audit mỗi lần đổi flag; default = false |
| R8 | Logic phân nhánh theo flag gây maintenance burden (2 code path) | LOW | Viết test case cover cả 2 nhánh flag on/off |
| R4 | Double-counting analytics/reports group theo `contentId` | LOW-MEDIUM | Review báo cáo/report queries sau khi launch |
| R5 | Notification rối cho user (noti "đã hủy" rồi "đã duyệt" cho cùng link) | LOW | Chấp nhận — UX acceptable |
| R6 | `publishAt` của content cũ có thể không phù hợp event mới | LOW | Check `publishAt ∈ [event.StartAt, event.EndAt]` đã có sẵn ở [content.go:252-256](../../../vcreator/backend/pkg/public/service/content.go#L252-L256) → safeguard tự động |

## 8. Decisions & Open Questions

### Confirmed decisions
- **D1**: Cùng event, đã reject → **KHÔNG** cho submit lại (chống spam).
- **D2**: Scope query **theo partner** (không check cross-partner).
- **D3**: Frontend admin **cần làm** (tích hợp vào trang partner settings có sẵn, hoặc tạo mới nếu chưa có).
- **D4**: Quyền toggle flag = **bất kỳ ai có role edit partner** (dùng lại permission có sẵn, không thêm permission riêng).
- **D5**: **Chỉ áp dụng lúc check tại thời điểm submit** — bản ghi rejected cũ hay mới đều được tính như nhau. Không migrate, không phân biệt timestamp.

### Open
- **Q1**: Có cần log audit riêng khi creator resubmit một link đã reject (để admin event mới biết lịch sử)?
- **Q2**: Có hiển thị cảnh báo cho creator trước khi submit link đã từng reject (UX transparency)?

## 9. Success Metrics

- **Primary**: Tỉ lệ submit bị block bởi `ContentKeyLinkUsed` giảm (đo qua log/analytics)
- **Secondary**: Số case support ticket "không submit được content" giảm
- **Guardrail**: Không có incident reward double-count (đo qua reconciliation report)

## 10. Technical Scope (tham chiếu, không phải thiết kế chi tiết)

- **Sửa**: [backend/pkg/public/service/content.go:264-273](../../../vcreator/backend/pkg/public/service/content.go#L264-L273) — relax query
- **Sửa**: [backend/pkg/admin/service/content.go:176-249](../../../vcreator/backend/pkg/admin/service/content.go#L176-L249) — thêm guard un-reject
- **Thêm**: Compound/partial index trong [backend/internal/module/database/mongodb/index.go](../../../vcreator/backend/internal/module/database/mongodb/index.go)
- **Test**: Unit test 4 case chính (xem FR-1)

## 11. Rollout Plan

- **Phase 1**: Deploy logic + index (behind feature flag nếu có hạ tầng flag)
- **Phase 2**: Monitor log duplicate check trong 1-2 tuần
- **Phase 3**: Review reconciliation để đảm bảo không double-count

---

## Appendix: Phân tích kỹ thuật chi tiết

Xem conversation history hoặc [brainstorming doc liên quan] cho:
- Chi tiết call flow submit content
- Model `ContentRaw` và các status value
- Index hiện tại trên collection `contents`
- Side effects của `ActionAfterWhenChangeStatus`
