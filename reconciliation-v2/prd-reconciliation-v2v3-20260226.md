# PRD: Hệ Thống Đối Soát V2 & V3

**Ngày:** 27/02/2026
**Phiên bản:** 3.0
**Trạng thái:** Implemented

**Tài liệu liên quan:**
- Business Overview: [business-overview.md](./business-overview.md)
- PRD V2 cũ (superseded): [prd-reconciliation-v2-archived.md](./prd-reconciliation-v2-archived.md)

---

## Tóm Tắt

Hệ thống đối soát hiện tại **dừng crawl dữ liệu ngay khi campaign hết hạn**. Operations không có dữ liệu để đối soát — buộc kiểm tra thủ công từng video trên nền tảng.

**V2** giải quyết: có snapshot dữ liệu tại thời điểm đối soát.
**V3** giải quyết: hệ thống tự đánh giá từng item theo checklist, đưa ra **đề xuất** (suggestion), admin xem bằng chứng và xác nhận. Checklist là cổng bắt buộc (validation gate) cho mọi quyết định.

**Nguyên tắc thiết kế:** Tất cả luồng hiện tại giữ nguyên. Chỉ bổ sung — không sửa code cũ.

---

## Mục Tiêu Kinh Doanh

1. **Unblock đối soát Techcombank tháng 2** — yêu cầu khẩn cấp từ khách hàng (V2)
2. **Xóa bỏ kiểm tra thủ công từng video** — BTC có dữ liệu sẵn trong hệ thống (V2)
3. **Giảm thời gian đối soát 80%+** — hệ thống auto approve/reject phần lớn items, BTC chỉ review ngoại lệ (V3)

## Chỉ Số Thành Công

| Chỉ số | Mục tiêu | Version |
|--------|---------|---------|
| Đợt đối soát Techcombank tháng 2 thực hiện được | 100% | V2 |
| Thời gian BTC kiểm tra từng video thủ công | Giảm về 0 | V2 |
| Độ trễ snapshot so với thực tế | ≤ 24 giờ | V2 |
| Tỷ lệ item được auto approve/reject | ≥ 80% | V3 |
| Thời gian BTC hoàn thành 1 đợt đối soát | Giảm ≥ 80% so với thủ công | V3 |

---

## Người Dùng

| Persona | Nhu cầu chính |
|---------|--------------|
| **BTC / Operations** | Có dữ liệu đầy đủ khi đối soát. V3: chỉ review ngoại lệ thay vì từng item |
| **Admin** | Quản lý campaign, đóng đối soát, xử lý warning items |

---

## Phạm Vi

**V2 — Snapshot & Hiển Thị:**
- Crawl snapshot hàng ngày (tách biệt khỏi analytics)
- Hiển thị snapshot trong màn hình đối soát và file export
- Dừng crawl khi admin đóng hoặc hết reward pending

**V3 — Checklist & Đề Xuất Tự Động:**
- Checklist đối soát theo loại reward
- Hệ thống tự evaluate từ snapshot → đề xuất duyệt / đề xuất huỷ / cần xem xét
- Checklist-as-gate: validation bắt buộc trước khi duyệt/từ chối
- Admin đánh thủ công các item chưa xác minh (merge với kết quả tự động)
- ConfirmStatus endpoint: admin xác nhận → hệ thống tự áp dụng trạng thái
- Smart CTA UI: nút hành động thông minh theo ngữ cảnh
- Bộ lọc đề xuất (classification filter)
- Export bổ sung cột checklist + đề xuất
- Override kết quả với audit trail đầy đủ

**Ngoài scope:**
- Lịch đối soát tự động (V4)
- Thông báo influencer, kháng cáo (V4)
- Checklist chi tiết cho `by_milestone` (V5+)

---

## Functional Requirements — V2

---

### FR-001: Crawl Snapshot Hàng Ngày

**Ưu tiên:** Must Have

**Mô tả:**
Hệ thống crawl video và lưu snapshot vào bảng riêng (`reconciliation_snapshots`). Có 2 nguồn:
- Khi event còn active: daily crawl hiện tại đồng thời insert snapshot (phục vụ đối soát giữa kỳ)
- Khi event đã hết hạn (`EndAt < now`): job crawl riêng chạy hàng ngày

**Acceptance Criteria:**
- [ ] Khi event active, daily crawl insert 1 snapshot record song song (không ảnh hưởng logic analytics)
- [ ] Khi event hết hạn, job crawl riêng chạy hàng ngày cho video có reward chưa bị rejected
- [ ] Mỗi lần crawl tạo record mới với timestamp — insert-only, không ghi đè
- [ ] Snapshot record lưu: `event_id`, `content_id`, `view_count`, `hashtags[]`, `crawl_success` (bool), `crawled_at`
- [ ] Snapshot lưu vào bảng riêng, không ảnh hưởng pipeline analytics/reward

**Dependencies:** Không

---

### FR-002: Dừng Crawl Khi Đối Soát Hoàn Tất

**Ưu tiên:** Must Have

**Mô tả:**
Job crawl đối soát phải dừng khi không còn cần thiết, tránh tốn tài nguyên vĩnh viễn.

**Acceptance Criteria:**
- [ ] Admin có thể đóng đối soát cho 1 event (set `reconciliation_closed`)
- [ ] Job crawl tự dừng khi event không còn reward ở trạng thái pending
- [ ] Job crawl không chạy cho video đã có reward bị rejected trước đối soát

**Dependencies:** FR-001

---

### FR-003: Hiển Thị Snapshot Trong Màn Hình Đối Soát

**Ưu tiên:** Must Have

**Mô tả:**
Màn hình đối soát hiển thị dữ liệu snapshot mới nhất bên cạnh thông tin reward.

**Acceptance Criteria:**
- [ ] Hiển thị view count mới nhất từ snapshot (kèm thời điểm crawl)
- [ ] Hiển thị danh sách hashtag hiện tại từ snapshot
- [ ] Hiển thị trạng thái crawl: thành công hoặc "Không lấy được dữ liệu"
- [ ] Nếu chưa có snapshot → hiển thị "Chưa có dữ liệu"
- [ ] Load ≤ 2 giây với 500 records

**Dependencies:** FR-001

---

### FR-004: Export Snapshot + Checklist Ra File Đối Soát

**Ưu tiên:** Must Have

**Mô tả:**
File export bổ sung cột snapshot và checklist để BTC làm việc offline.

**Acceptance Criteria:**
- [x] File export có cột snapshot: `snapshot_view_count`, `snapshot_hashtags`, `Trạng thái snapshot`, `Thời điểm snapshot`
- [x] File export có cột checklist: `Video truy cập được`, `Hashtag đúng`, `View không giảm`, `Admin xác nhận`
- [x] File export có cột `Đề xuất` (Đề xuất duyệt / Đề xuất huỷ / Cần xem xét)
- [x] Không làm vỡ format cũ của file export
- [x] Nếu không có snapshot/checklist → cột để trống (không null gây lỗi Excel)

**Dependencies:** FR-001, FR-101

---

### FR-005: Crawl Bù Khi Downtime

**Ưu tiên:** Should Have

**Mô tả:**
Nếu job crawl bị lỡ, có cơ chế crawl bù.

**Acceptance Criteria:**
- [ ] Phát hiện ngày nào không có snapshot cho event đang cần crawl
- [ ] Admin có thể trigger crawl bù thủ công
- [ ] Crawl bù không ảnh hưởng schedule thông thường

**Dependencies:** FR-001

---

## Functional Requirements — V3

---

### FR-101: Checklist Đối Soát Theo Loại Reward

**Ưu tiên:** Must Have

**Mô tả:**
Mỗi reward item trong đợt đối soát có bộ checklist tương ứng với loại reward. Checklist là điều kiện business mà influencer, admin, brand cùng nhìn thấy.

**Checklist `by_view`:**

| # | Điều kiện | Mô tả |
|---|-----------|-------|
| 1 | Video có thể truy cập công khai | Chưa bị xóa, ẩn, hoặc chuyển private |
| 2 | Video còn đủ hashtag campaign | Influencer chưa gỡ hashtag |
| 3 | Lượt xem không giảm so với đã ghi nhận | Không có dấu hiệu view ảo bị platform gỡ |

**Checklist `by_milestone`:**

| # | Điều kiện | Mô tả |
|---|-----------|-------|
| 1 | Admin xác nhận | Hệ thống không tự xác minh milestone — admin review |

*Ghi chú: `by_milestone` là giải pháp tạm ở V3 — Techcombank chưa sử dụng loại này. V5+ làm rõ thêm.*

**Acceptance Criteria:**
- [x] Mỗi reward item có checklist phù hợp với loại reward
- [x] Checklist items hiển thị rõ ràng cho admin trên màn hình đối soát (Checklist Panel)
- [x] Checklist definition có thể mở rộng (thêm loại reward mới) mà không sửa logic core

**Dependencies:** FR-001 (cần có snapshot)

---

### FR-102: Trạng Thái Checklist Item

**Ưu tiên:** Must Have

**Mô tả:**
Mỗi checklist item có 3 trạng thái. Hệ thống tự đánh khi có snapshot, admin đánh thủ công khi không có.

| Trạng thái | Nghĩa | Ai đánh |
|---|---|---|
| ✅ Pass | Xác nhận đạt | Hệ thống (tự động) hoặc Admin (thủ công) |
| ❌ Fail | Xác nhận vi phạm | Hệ thống (tự động) hoặc Admin (thủ công) |
| ⚠️ Chưa xác minh | Chưa có kết luận | Mặc định khi không có bằng chứng |

**Acceptance Criteria:**
- [x] Khi snapshot có data → hệ thống tự evaluate và đánh pass/fail
- [x] Khi crawl fail → tất cả items ở trạng thái "Chưa xác minh"
- [x] `by_milestone` checklist luôn ở trạng thái "Chưa xác minh" (chờ admin)
- [x] Kết quả evaluate được lưu versioned (re-check tạo bản mới, không ghi đè)
- [x] Mỗi bản ghi kết quả lưu: `snapshot_id` dùng làm bằng chứng, `evaluated_at`

**Dependencies:** FR-101

---

### FR-103: Evaluate Tự Động Checklist `by_view`

**Ưu tiên:** Must Have

**Mô tả:**
Khi có snapshot, hệ thống tự đánh giá 3 điều kiện checklist `by_view`:

| # | Điều kiện | Logic evaluate | Fail → |
|---|-----------|---------------|--------|
| 1 | Video truy cập công khai | `crawl_success == true` | 🔴 Auto reject |
| 2 | Hashtag đủ | `required_hashtags ⊆ snapshot.hashtags` | 🔴 Auto reject |
| 3 | View không giảm | `snapshot.view_count >= reward.recorded_view` | ⚠️ Warning |

**Acceptance Criteria:**
- [x] Điều kiện #1: crawl thành công = pass, crawl fail = chưa xác minh (KHÔNG auto reject)
- [x] Điều kiện #2: so sánh hashtag snapshot vs hashtag yêu cầu trong event (`EventOpts.Hashtags`)
- [x] Điều kiện #3: so sánh view snapshot vs view đã ghi nhận tại thời điểm tạo reward
- [x] Logic evaluate chạy khi admin trigger (bấm nút "Đánh giá")
- [x] Lấy snapshot gần nhất tại thời điểm evaluate
- [x] Evaluate chỉ xử lý items pending (skip items đã completed/rejected), hiển thị số skipped
- [x] Merge kết quả: giữ nguyên manual evaluations, update system evaluations

**Dependencies:** FR-101, FR-102, FR-001

---

### FR-104: Đề Xuất Tự Động Reward Item

**Ưu tiên:** Must Have

**Mô tả:**
Sau khi evaluate checklist, hệ thống tổng hợp kết quả và đưa ra đề xuất cho reward item. Đề xuất là gợi ý — admin xem bằng chứng và xác nhận.

| Đề xuất | Điều kiện |
|---------|-----------|
| **Đề xuất duyệt** (auto_approved) | Tất cả checklist items pass |
| **Đề xuất huỷ** (auto_rejected) | Bất kỳ item nào fail với mức auto reject |
| **Cần xem xét** (needs_review) | Có warning hoặc có item chưa xác minh |

**Acceptance Criteria:**
- [x] Đề xuất duyệt: admin xem checklist → bấm xác nhận → hệ thống tự áp dụng trạng thái completed
- [x] Đề xuất huỷ: admin xem checklist → bấm xác nhận → hệ thống tự áp dụng trạng thái rejected (ghi lý do từ checklist fail)
- [x] Cần xem xét: reward giữ trạng thái pending, admin đánh thủ công → xác nhận
- [x] Admin có thể override bất kỳ kết quả nào (cả đã duyệt lẫn đã từ chối)
- [x] Override ghi nhận: admin nào, từ trạng thái nào sang trạng thái nào, lý do (≥10 ký tự), thời điểm
- [x] Bộ lọc đề xuất (classification filter) trên màn hình đối soát

**Dependencies:** FR-102, FR-103

---

### FR-105: Admin Xử Lý Checklist "Chưa Xác Minh"

**Ưu tiên:** Must Have

**Mô tả:**
Admin đánh tay pass/fail cho từng checklist item ở trạng thái chưa xác minh. Kết quả đánh thủ công được merge với kết quả tự động (không ghi đè toàn bộ).

**Acceptance Criteria:**
- [x] Admin có thể đánh pass hoặc fail cho từng item riêng lẻ
- [x] Thao tác nhanh "Duyệt nhanh": pass tất cả items chưa xác minh cùng lúc
- [x] Thao tác nhanh "Hủy nhanh": fail tất cả items chưa xác minh cùng lúc
- [x] Sau khi admin đánh xong → hệ thống tự tổng hợp lại kết quả (checklist summary + suggested status)
- [x] Khi re-evaluate: merge kết quả đánh thủ công với kết quả tự động mới (giữ nguyên manual, update system)
- [x] Ghi nhận admin nào đánh, lúc nào

**Dependencies:** FR-102, FR-104

---

### FR-106: Override Kết Quả Đề Xuất

**Ưu tiên:** Must Have

**Mô tả:**
BTC/Admin có toàn quyền override kết quả đề xuất tự động. Chỉ override được item đã ở trạng thái cuối (completed/rejected).

**Acceptance Criteria:**
- [x] Có thể override từ completed → rejected (và ngược lại)
- [x] Bắt buộc nhập lý do khi override (tối thiểu 10 ký tự, không chấp nhận whitespace-only)
- [x] Ghi nhận audit trail: ai override, từ trạng thái nào sang trạng thái nào, lý do, thời điểm
- [x] Override không xóa kết quả evaluate gốc — lưu song song trong collection riêng
- [x] Atomic update filter ngăn race condition (TOCTOU prevention)

**Dependencies:** FR-104

---

### FR-107: Checklist-as-Gate Validation

**Ưu tiên:** Must Have

**Mô tả:**
Checklist là cổng bắt buộc (mandatory gate) cho mọi quyết định trạng thái. Hệ thống không cho phép duyệt/từ chối nếu checklist chưa đủ điều kiện.

**Acceptance Criteria:**
- [x] Duyệt chỉ khi: tất cả items đã resolved (AllResolved=true) VÀ không có fail (FailCount=0)
- [x] Từ chối chỉ khi: tất cả items đã resolved VÀ có ít nhất 1 fail (FailCount>0)
- [x] Override chỉ trên item đã ở trạng thái cuối (completed/rejected) + lý do ≥10 ký tự
- [x] Validation logic tách thành pure functions (testable, reusable): `ComputeChecklistSummary()`, `ValidateStatusFromChecklist()`
- [x] Guards áp dụng tại: ApplyClassification, Override, ChangeStatusItem

**Dependencies:** FR-101, FR-102

---

### FR-108: ConfirmStatus — Xác Nhận Trạng Thái

**Ưu tiên:** Must Have

**Mô tả:**
Endpoint cho phép admin xác nhận trạng thái (duyệt/từ chối) cho từng reward item. Hệ thống tự áp dụng trạng thái sau khi admin xác nhận, không cần thao tác "Áp dụng kết quả" riêng.

**Endpoint:** `POST /:id/content/:itemId/confirm-status`

**Acceptance Criteria:**
- [x] Cross-validate itemID thuộc reconciliationID (ngăn unauthorized access)
- [x] Validate qua checklist gate trước khi áp dụng
- [x] Trả về response enriched: checklist summary + suggested status + allResolved
- [x] Reject reason không chấp nhận whitespace-only

**Dependencies:** FR-107

---

### FR-109: Smart CTA — Nút Hành Động Thông Minh

**Ưu tiên:** Should Have

**Mô tả:**
Thay thế các nút hành động rời rạc (reject button + override link) bằng một nút CTA thay đổi theo ngữ cảnh checklist.

**Acceptance Criteria:**
- [x] CTA thay đổi label + màu theo trạng thái checklist (Duyệt/Từ chối/Cần xem xét/Đã duyệt/Đã từ chối)
- [x] Item pending: bấm CTA mở checklist panel (expandable row)
- [x] Item đã quyết định: hiển thị trạng thái, không expandable
- [x] Loại bỏ cột action cũ khỏi table

**Dependencies:** FR-104, FR-107

---

## Non-Functional Requirements

---

### NFR-001: Performance — Crawl Throughput

**Ưu tiên:** Must Have

Job crawl hàng ngày hoàn thành trong ≤ 4 giờ cho tối đa 50,000 video.

- [ ] Rate limit platform được tôn trọng — không bị block
- [ ] Job chạy song song theo batch

---

### NFR-002: Performance — Load Màn Hình Đối Soát

**Ưu tiên:** Must Have

Màn hình đối soát (bao gồm snapshot + checklist results) load trong ≤ 2 giây cho 500 records.

- [ ] P95 load time ≤ 2 giây
- [ ] Query snapshot và checklist results với index tối ưu

---

### NFR-003: Reliability — Insert-Only Snapshot

**Ưu tiên:** Must Have

Snapshot đã lưu không bao giờ bị xóa hoặc ghi đè. Đây là audit trail.

- [ ] Schema insert-only cho `reconciliation_snapshots`
- [ ] Không có update/delete trên bảng snapshot

---

### NFR-004: Reliability — Versioned Check Results

**Ưu tiên:** Must Have

Kết quả evaluate checklist được lưu theo version. Re-check tạo bản mới.

- [ ] Mỗi lần evaluate tạo record mới với timestamp
- [ ] Có thể xem lịch sử evaluate cho 1 reward item

---

### NFR-005: Compatibility — Tách Biệt Analytics

**Ưu tiên:** Must Have

Crawl đối soát không ảnh hưởng pipeline analytics hiện tại.

- [ ] Snapshot lưu bảng riêng (`reconciliation_snapshots`)
- [ ] Job crawl sau hết hạn dùng queue riêng
- [ ] Daily crawl insert snapshot song song — nhưng không thay đổi logic analytics

---

### NFR-006: Scalability

**Ưu tiên:** Should Have

Scale lên 100,000 video bằng cách tăng worker, không cần refactor.

---

### NFR-007: Observability

**Ưu tiên:** Should Have

- [ ] Log mỗi job run: start, end, success count, fail count
- [ ] Alert khi job trễ > 2 giờ
- [ ] Log mỗi evaluate run: bao nhiêu auto approved, auto rejected, needs review

---

## Epics

---

### EPIC-001: Crawl Snapshot (V2)

**Mô tả:** Hạ tầng crawl hàng ngày và lưu snapshot tách biệt.

**FRs:** FR-001, FR-002, FR-005

**Ước tính stories:** 3–5

**Ưu tiên:** Must Have — nền tảng của toàn bộ V2 và V3.

---

### EPIC-002: Hiển Thị Snapshot (V2)

**Mô tả:** Đưa snapshot vào giao diện đối soát và file export.

**FRs:** FR-003, FR-004

**Ước tính stories:** 2–4

**Ưu tiên:** Must Have — BTC trực tiếp sử dụng.

---

### EPIC-003: Checklist Engine (V3)

**Mô tả:** Định nghĩa checklist theo loại reward, evaluate tự động từ snapshot.

**FRs:** FR-101, FR-102, FR-103

**Ước tính stories:** 3–5

**Ưu tiên:** Must Have — logic core của V3.

---

### EPIC-004: Đề Xuất, Validation Gate & Admin Actions (V3)

**Mô tả:** Đề xuất tự động, validation gate, xử lý items chưa xác minh, confirm status, Smart CTA, override.

**FRs:** FR-104, FR-105, FR-106, FR-107, FR-108, FR-109

**Ước tính stories:** 5–8

**Ưu tiên:** Must Have — workflow hoàn chỉnh cho BTC.

---

## Ma Trận Truy Xuất

| Epic | Tên | FRs | Stories | Version | Trạng thái |
|------|-----|-----|---------|---------|-----------|
| EPIC-001 | Crawl Snapshot | FR-001, FR-002, FR-005 | 3–5 | V2 | ✅ Done |
| EPIC-002 | Hiển Thị Snapshot + Export | FR-003, FR-004 | 2–4 | V2 | ✅ Done |
| EPIC-003 | Checklist Engine | FR-101, FR-102, FR-103 | 3–5 | V3 | ✅ Done |
| EPIC-004 | Đề Xuất, Gate & Admin Actions | FR-104–FR-109 | 5–8 | V3 | ✅ Done |
| **Tổng** | | **14 FRs** | **13–22 stories** | | |

---

## Tóm Tắt Ưu Tiên

| Loại | Must Have | Should Have | Trạng thái |
|------|-----------|-------------|-----------|
| FRs V2 | 4 (FR-001–004) | 1 (FR-005) | ✅ Done |
| FRs V3 | 8 (FR-101–108) | 1 (FR-109) | ✅ Done |
| NFRs | 5 (NFR-001–005) | 2 (NFR-006, NFR-007) | — |

---

## Phụ Thuộc

### Internal
- Hệ thống reward/campaign hiện tại (đọc danh sách video, reward type, recorded view)
- `EventOpts.Hashtags` (danh sách hashtag yêu cầu của event)
- Pipeline export file đối soát hiện tại
- Hạ tầng job scheduling (cron/queue) hiện tại

### External
- TikTok API / scraper — rate limit cần tôn trọng
- YouTube API (nếu applicable)

---

## Giả Định

- Hệ thống crawl hiện tại có thể tái sử dụng cho snapshot (không viết lại)
- Techcombank chỉ dùng reward `by_view` — `by_milestone` là placeholder cho V5+
- Số video active ≤ 50,000 tại thời điểm launch
- Crawl fail (404) không phân biệt được deleted vs private → admin đánh thủ công
- View count trên platform có thể dao động tự nhiên (normalization) → view drop là warning, không auto reject

---

## Rủi Ro

| Rủi ro | Khả năng | Tác động | Biện pháp |
|--------|----------|----------|-----------|
| TikTok block crawl | Trung bình | Cao | Rate limiting, rotation |
| Crawl job không xong trước đối soát | Thấp | Cao | Monitor + alert, chạy từ tối hôm trước |
| False positive auto reject (hashtag format khác nhau) | Trung bình | Trung bình | Normalize hashtag trước khi so sánh |
| Admin quên đóng đối soát → crawl chạy mãi | Thấp | Thấp | Auto dừng khi hết reward pending |

---

## Câu Hỏi Còn Mở

1. Rate limit TikTok hiện tại cho phép bao nhiêu request/phút?
2. File export hiện tại là Excel hay CSV?
3. Hashtag comparison: case-sensitive? Có cần normalize (#TechComBank vs #techcombank)?
4. View "đã ghi nhận" cụ thể là field nào trong `EventRewardStatistic`?

---

## Revision History

| Phiên bản | Ngày | Thay đổi |
|-----------|------|---------|
| 1.0 | 25/02/2026 | Khởi tạo PRD V2 |
| 2.0 | 26/02/2026 | Viết lại, bổ sung V3 (checklist, phân loại tự động, admin actions). Cập nhật V2 dựa trên brainstorming (snapshot architecture, crawl_success thay vì video_status enum) |
| 3.0 | 27/02/2026 | Cập nhật dựa trên implementation thực tế (16 commits). Thay đổi chính: (1) "Phân loại" → "Đề xuất" — hệ thống đưa gợi ý, admin quyết định; (2) Bổ sung FR-107 Checklist-as-Gate validation bắt buộc; (3) Bổ sung FR-108 ConfirmStatus endpoint tự áp dụng trạng thái; (4) Bổ sung FR-109 Smart CTA UI; (5) Cập nhật FR-004 export thêm cột checklist + đề xuất; (6) Cập nhật FR-103 merge manual + system evaluations; (7) Cập nhật FR-106 override yêu cầu ≥10 ký tự + TOCTOU prevention; (8) Đánh dấu tất cả V2+V3 FRs đã implement xong |
