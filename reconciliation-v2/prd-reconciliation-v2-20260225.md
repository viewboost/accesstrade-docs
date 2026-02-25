# PRD: Hệ Thống Đối Soát V2 — Unblock Đối Soát

**Ngày:** 25/02/2026
**Tác giả:** Product Manager
**Phiên bản:** 1.0
**Trạng thái:** Draft
**Deadline:** 28/02/2026

**Tài liệu liên quan:**
- Business Overview: [business-overview.md](./business-overview.md)

---

## Tóm Tắt

Hệ thống đối soát hiện tại **dừng crawl dữ liệu ngay khi campaign hết hạn**. Vì đối soát thường diễn ra vài ngày sau khi campaign kết thúc, operations không có dữ liệu để làm việc — buộc phải kiểm tra thủ công từng video một trên nền tảng. Với campaign có hàng trăm content, đây là điều bất khả thi.

**V2 giải quyết đúng một vấn đề:** tiếp tục crawl sau khi campaign hết hạn để có snapshot dữ liệu tại thời điểm đối soát.

---

## Mục Tiêu Kinh Doanh

1. **Unblock đối soát Techcombank tháng 2** — đáp ứng yêu cầu khẩn cấp từ khách hàng
2. **Xóa bỏ kiểm tra thủ công từng video** — operations không còn phải mở link ra nền tảng
3. **Đảm bảo dữ liệu đối soát có thể tin cậy được** — snapshot phản ánh trạng thái video tại thời điểm đối soát, không phải tại thời điểm campaign kết thúc

## Chỉ Số Thành Công

| Chỉ số | Mục tiêu |
|--------|---------|
| Đợt đối soát Techcombank tháng 2 thực hiện được | 100% |
| Thời gian operations kiểm tra từng video | Giảm về 0 (có dữ liệu sẵn) |
| Số campaign có dữ liệu crawl sau hết hạn | 100% campaign đang active |
| Độ trễ snapshot so với thực tế | ≤ 24 giờ |

---

## Người Dùng

| Persona | Mô tả | Nhu cầu chính |
|---------|-------|--------------|
| **Operations / BTC** | Nhân viên thực hiện đối soát | Có dữ liệu đầy đủ khi tải file đối soát, không phải dò thủ công |
| **Admin** | Người quản lý campaign trên hệ thống | Campaign tiếp tục được theo dõi sau hết hạn |

---

## Phạm Vi V2

**Trong scope:**
- Crawl video sau khi campaign hết hạn
- Lưu snapshot: view count, trạng thái video (còn tồn tại / bị xóa / private), hashtag
- Hiển thị dữ liệu snapshot trong màn hình đối soát và file export

**Ngoài scope (V3+):**
- Tự động hóa lịch đối soát
- Phân loại tự động (duyệt / hủy / cần xem xét)
- Thông báo influencer
- Luồng kháng cáo

---

## Functional Requirements

---

### FR-001: Tiếp Tục Crawl Sau Khi Campaign Hết Hạn

**Ưu tiên:** Must Have

**Mô tả:**
Hệ thống phải tiếp tục crawl toàn bộ video thuộc campaign mỗi ngày sau khi campaign kết thúc, cho đến khi tất cả đợt đối soát của campaign đó được đóng (COMPLETED hoặc REJECTED).

**Acceptance Criteria:**
- [ ] Campaign ở trạng thái hết hạn vẫn có job crawl chạy hàng ngày
- [ ] Job crawl dừng khi campaign được đánh dấu đã đóng hoàn toàn
- [ ] Không ảnh hưởng đến dữ liệu reward hay analytics hiện tại

**Dependencies:** Không có

---

### FR-002: Lưu Snapshot Dữ Liệu Crawl

**Ưu tiên:** Must Have

**Mô tả:**
Mỗi lần crawl phải lưu lại snapshot bao gồm: view count tại thời điểm crawl, trạng thái tồn tại của video, danh sách hashtag hiện tại. Dữ liệu snapshot được gắn timestamp và không bị ghi đè — mỗi lần crawl tạo ra một bản ghi mới.

**Acceptance Criteria:**
- [ ] Mỗi lần crawl tạo record mới với timestamp
- [ ] Record lưu đủ: view_count, video_status (active / deleted / private / unavailable), hashtags
- [ ] Không ghi đè bản ghi cũ — có thể truy vấn lịch sử
- [ ] Dữ liệu snapshot có thể join với reward records theo video_id

**Dependencies:** FR-001

---

### FR-003: Xác Định Trạng Thái Video

**Ưu tiên:** Must Have

**Mô tả:**
Mỗi lần crawl phải xác định và ghi nhận trạng thái hiện tại của video theo 4 loại: `active` (bình thường), `deleted` (bị xóa), `private` (chuyển private), `unavailable` (không thể truy cập vì lý do khác).

**Acceptance Criteria:**
- [ ] Phân biệt được 4 trạng thái trên cho video TikTok
- [ ] Phân biệt được 4 trạng thái trên cho video YouTube (nếu applicable)
- [ ] Khi video không crawl được, ghi nhận lý do thay vì bỏ qua

**Dependencies:** FR-001, FR-002

---

### FR-004: Hiển Thị Dữ Liệu Snapshot Trong Màn Hình Đối Soát

**Ưu tiên:** Must Have

**Mô tả:**
Màn hình đối soát phải hiển thị dữ liệu snapshot crawl gần nhất bên cạnh thông tin phần thưởng: view count tại thời điểm crawl, trạng thái video, và thời điểm crawl gần nhất. BTC có thể thấy ngay video nào còn tồn tại và view như thế nào mà không cần mở link.

**Acceptance Criteria:**
- [ ] Hiển thị view count mới nhất từ snapshot (kèm thời điểm crawl)
- [ ] Hiển thị badge trạng thái video: Active / Đã xóa / Private / Không truy cập được
- [ ] Nếu chưa có snapshot (chưa crawl lần nào) → hiển thị "Chưa có dữ liệu"
- [ ] Dữ liệu load được trong vòng 2 giây

**Dependencies:** FR-002, FR-003

---

### FR-005: Export Dữ Liệu Snapshot Ra File Đối Soát

**Ưu tiên:** Must Have

**Mô tả:**
File export đối soát (Excel/CSV) phải bổ sung các cột từ snapshot: view count tại thời điểm đối soát, trạng thái video, thời điểm crawl gần nhất. BTC tải file về là có đủ dữ liệu để làm việc.

**Acceptance Criteria:**
- [ ] File export có cột `snapshot_view_count`
- [ ] File export có cột `video_status` (giá trị dạng text rõ ràng)
- [ ] File export có cột `last_crawled_at` (timestamp)
- [ ] Các cột mới không làm vỡ format cũ của file export
- [ ] Nếu không có snapshot → các cột để trống, không để null gây lỗi khi mở Excel

**Dependencies:** FR-002, FR-003

---

### FR-006: Crawl Bù Khi Hệ Thống Downtime

**Ưu tiên:** Should Have

**Mô tả:**
Nếu job crawl bị bỏ lỡ (hệ thống downtime, lỗi), hệ thống phải có cơ chế crawl bù cho các ngày bị thiếu trong vòng 3 ngày gần nhất.

**Acceptance Criteria:**
- [ ] Phát hiện được ngày nào không có snapshot
- [ ] Có thể trigger crawl bù thủ công hoặc tự động
- [ ] Crawl bù không ảnh hưởng đến schedule crawl thông thường

**Dependencies:** FR-001, FR-002

---

### FR-007: Cảnh Báo Khi Video Đổi Trạng Thái

**Ưu tiên:** Should Have

**Mô tả:**
Khi phát hiện video chuyển từ `active` sang trạng thái khác (deleted / private / unavailable), hệ thống gắn cờ cảnh báo trên record phần thưởng tương ứng để BTC chú ý khi đối soát.

**Acceptance Criteria:**
- [ ] Record phần thưởng có field `alert_flag` được set khi video đổi trạng thái
- [ ] Màn hình đối soát hiển thị icon cảnh báo trên các record có `alert_flag`
- [ ] Alert không tự động hủy phần thưởng — chỉ gắn cờ để BTC biết

**Dependencies:** FR-002, FR-003, FR-004

---

## Non-Functional Requirements

---

### NFR-001: Performance — Crawl Job Throughput

**Ưu tiên:** Must Have

**Mô tả:**
Job crawl hàng ngày phải hoàn thành trong vòng 4 giờ cho tổng khối lượng ước tính (tối đa 50,000 video đang active trên tất cả campaign chưa đóng).

**Acceptance Criteria:**
- [ ] 50,000 video crawl xong trong ≤ 4 giờ
- [ ] Rate limit của từng nền tảng (TikTok, YouTube) được tôn trọng — không bị block
- [ ] Job có thể chạy song song theo batch

**Lý do:** Nếu crawl chạy quá lâu, snapshot không đủ tươi cho đợt đối soát sáng hôm sau.

---

### NFR-002: Performance — Load Màn Hình Đối Soát

**Ưu tiên:** Must Have

**Mô tả:**
Màn hình đối soát có dữ liệu snapshot phải load trong ≤ 2 giây cho danh sách lên đến 500 phần thưởng.

**Acceptance Criteria:**
- [ ] P95 load time ≤ 2 giây với 500 records
- [ ] Snapshot data được query với index tối ưu (không full scan)

---

### NFR-003: Reliability — Không Mất Dữ Liệu Snapshot

**Ưu tiên:** Must Have

**Mô tả:**
Dữ liệu snapshot đã lưu không bao giờ bị xóa hoặc ghi đè — kể cả khi crawl lại cùng video. Đây là audit trail cho đối soát.

**Acceptance Criteria:**
- [ ] Schema sử dụng insert-only cho snapshot records
- [ ] Không có soft-delete hay update trên bảng snapshot
- [ ] Backup snapshot cùng chu kỳ với các bảng dữ liệu quan trọng khác

---

### NFR-004: Compatibility — Tách Biệt Với Luồng Analytics

**Ưu tiên:** Must Have

**Mô tả:**
Luồng crawl cho đối soát phải hoàn toàn tách biệt với luồng crawl analytics và reward hiện tại — không chia sẻ queue, không ghi vào cùng bảng dữ liệu.

**Acceptance Criteria:**
- [ ] Crawl job cho đối soát dùng queue riêng
- [ ] Dữ liệu snapshot lưu vào bảng riêng (`reconciliation_snapshots`)
- [ ] Lỗi trong crawl đối soát không ảnh hưởng đến pipeline analytics

**Lý do:** Tránh regression — hệ thống analytics đang chạy ổn định, không được làm ảnh hưởng.

---

### NFR-005: Scalability — Số Lượng Campaign Tăng

**Ưu tiên:** Should Have

**Mô tả:**
Kiến trúc crawl phải scale được khi số campaign tăng gấp đôi (100,000 video) mà không cần refactor.

**Acceptance Criteria:**
- [ ] Tăng số worker/thread là đủ để tăng throughput
- [ ] Không có bottleneck single-threaded trong pipeline

---

### NFR-006: Observability — Monitoring Job Crawl

**Ưu tiên:** Should Have

**Mô tả:**
Phải có dashboard/log đủ để biết: job có chạy không, crawl được bao nhiêu video, bao nhiêu lỗi, bao nhiêu video không truy cập được.

**Acceptance Criteria:**
- [ ] Mỗi job run ghi log: start time, end time, success count, error count
- [ ] Alert khi job không chạy đúng lịch (> 2 giờ trễ)
- [ ] Có thể query "video X đã được crawl lần nào, kết quả ra sao"

---

## Epics

---

### EPIC-001: Crawl Engine Sau Hết Hạn

**Mô tả:**
Xây dựng hạ tầng crawl tiếp tục chạy sau khi campaign kết thúc. Bao gồm job scheduling, logic xác định campaign cần crawl, và lưu snapshot.

**Functional Requirements:**
- FR-001 — Tiếp tục crawl sau hết hạn
- FR-002 — Lưu snapshot dữ liệu
- FR-003 — Xác định trạng thái video
- FR-006 — Crawl bù khi downtime

**Ước tính stories:** 4–6

**Ưu tiên:** Must Have

**Giá trị kinh doanh:**
Đây là nền tảng của toàn bộ V2. Không có epic này, không có gì khác hoạt động được.

---

### EPIC-002: Dữ Liệu Snapshot Trong Đối Soát

**Mô tả:**
Đưa dữ liệu snapshot vào giao diện đối soát và file export để BTC có đủ thông tin khi làm việc mà không cần mở link thủ công.

**Functional Requirements:**
- FR-004 — Hiển thị snapshot trong màn hình đối soát
- FR-005 — Export snapshot ra file
- FR-007 — Cảnh báo video đổi trạng thái

**Ước tính stories:** 3–5

**Ưu tiên:** Must Have

**Giá trị kinh doanh:**
Đây là thứ BTC trực tiếp thấy và dùng. Xây crawl engine mà không có epic này thì BTC vẫn không đối soát được.

---

## Ma Trận Truy Xuất

| Epic | Tên | Functional Requirements | Ước tính Stories |
|------|-----|------------------------|-----------------|
| EPIC-001 | Crawl Engine Sau Hết Hạn | FR-001, FR-002, FR-003, FR-006 | 4–6 |
| EPIC-002 | Dữ Liệu Snapshot Trong Đối Soát | FR-004, FR-005, FR-007 | 3–5 |
| **Tổng** | | **7 FRs** | **7–11 stories** |

---

## Tóm Tắt Ưu Tiên

| Loại | Must Have | Should Have | Could Have |
|------|-----------|-------------|------------|
| Functional Requirements | 5 (FR-001–005) | 2 (FR-006, FR-007) | 0 |
| Non-Functional Requirements | 4 (NFR-001–004) | 2 (NFR-005, NFR-006) | 0 |

---

## Phụ Thuộc

### Internal
- Hệ thống reward / campaign hiện tại (đọc danh sách video cần crawl)
- Pipeline export file đối soát hiện tại (bổ sung cột mới)
- Hạ tầng job scheduling (cron / queue) hiện tại

### External
- TikTok API / scraper — rate limit cần được tôn trọng
- YouTube API (nếu có video YouTube trong campaign)

---

## Giả Định

- Campaign Techcombank tháng 2 có thể chờ đến 28/02 để có dữ liệu V2
- Số lượng video active trên tất cả campaign không vượt quá 50,000 tại thời điểm launch
- Hệ thống hiện tại đã có cơ chế crawl video — V2 tái sử dụng, không viết lại từ đầu
- Không cần backward fill snapshot cho các campaign đã kết thúc trước V2 (chỉ apply cho campaign mới từ ngày deploy)

---

## Rủi Ro

| Rủi ro | Khả năng | Tác động | Biện pháp |
|--------|----------|----------|-----------|
| TikTok block crawl | Trung bình | Cao | Implement rate limiting, rotation |
| Crawl job không xong trước đợt đối soát sáng | Thấp | Cao | Monitor + alert, chạy crawl từ tối hôm trước |
| Schema migration ảnh hưởng production | Thấp | Cao | Migration riêng biệt, rollback plan |
| Khối lượng video lớn hơn ước tính | Thấp | Trung bình | Scale worker ngang |

---

## Câu Hỏi Còn Mở

1. Hệ thống crawl hiện tại dùng tool/library gì? (để đánh giá có thể tái sử dụng không)
2. Rate limit TikTok hiện tại cho phép bao nhiêu request/phút?
3. Có campaign nào đã kết thúc trước V2 cần backward fill không?
4. File export hiện tại là Excel hay CSV? Có template cố định không?

---

## Approval

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Operations Lead (BTC)

---

## Revision History

| Phiên bản | Ngày | Thay đổi |
|-----------|------|---------|
| 1.0 | 25/02/2026 | Khởi tạo PRD cho V2 |

---

*Tài liệu này được tạo theo BMAD Method — Phase 2 (Planning)*
*Bước tiếp theo: `/bmad:architecture` để thiết kế kiến trúc kỹ thuật cho V2*
