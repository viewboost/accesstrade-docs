# PRD: Bảng xếp hạng theo tuần

**Project:** Ambassador (Parasola)
**Date:** 2026-08-06
**Author:** Dang Dinh
**Status:** ✅ Đã triển khai — PR #97 (merged 2026-08-05) + PR #99 (open). 3 đề xuất §7: **chờ duyệt**.
**Version:** 1.0
**Tài liệu kỹ thuật:** `tech-spec.md` (spec implement)

---

## 1. Executive Summary

Bảng xếp hạng campaign xếp theo con số **luỹ kế từ ngày campaign bắt đầu**. Với campaign chạy vài tháng, thứ hạng đóng băng: creator vào sau không thể đuổi kịp khoảng cách tích luỹ dù làm tốt, creator cũ ngừng đăng bài vẫn giữ hạng. Bảng không còn phản ánh ai đang hoạt động, và brand mất cột mốc để truyền thông hàng tuần.

**Nguyên nhân:** bảng đọc `statistic.pointTotal.completed` của collection `user_event` — collection này giữ một document cho mỗi cặp user-event, chứa con số hiện tại, **không có field ngày**. Con số hình thành từ ngày nào là thông tin không tồn tại, nên không cắt theo tuần được. Đây là giới hạn hình dạng dữ liệu, không phải lỗi truy vấn.

**Cách fix:** thêm cấu hình `leaderboardPeriod` ở cấp campaign (`all_time` / `week`); khi là `week` thì đọc `user_event_analytic_daily` — collection thống kê theo ngày vốn đã có, mỗi bản ghi là phát sinh của đúng một ngày — rồi cộng theo khoảng thứ Hai đến Chủ nhật giờ Việt Nam. Mặc định `all_time` nên campaign đang chạy không đổi gì. Kèm 1 index và 1 lớp cache. 1 dev ~2 ngày, không migration, không đổi đường dẫn API.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Creator vào giữa campaign vẫn có cơ hội lên top | Thứ hạng đảo lại mỗi tuần, không đóng băng theo tháng |
| 2 | Bảng phản ánh ai đang hoạt động | Creator ngừng đăng bài rời top trong vòng 1 tuần |
| 3 | Brand có nhịp truyền thông hàng tuần | Mỗi campaign dài có N cuộc đua thay vì 1 |
| 4 | Ops tự bật/tắt theo từng campaign | 0 lần cần deploy để đổi cấu hình |
| 5 | Không ảnh hưởng campaign đang chạy | 0 campaign đổi hành vi sau deploy |

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **Creator mới vào** | Thi đua sòng phẳng với người vào trước, biết nỗ lực tuần này được tính |
| **Creator đang hoạt động** | Biết rõ bảng đang tính khung thời gian nào, không nhầm là mất thành tích |
| **Brand** | Bật chế độ thi đua tuần cho riêng campaign của mình |
| **Ops/Admin** | Cấu hình trong form event, không cần nhờ kỹ thuật |

---

## 4. Functional Requirements

### FR-001: Cấu hình kỳ xếp hạng ở cấp campaign — **Must Have**

Thêm field `leaderboardPeriod` vào `EventOpts`, hai giá trị `all_time` / `week`. Ô chọn **"Kỳ xếp hạng"** trong form event admin, tab Tuỳ chọn, nhãn *Toàn thời gian* / *Theo tuần*.

Field khai `omitempty`: event cũ không có field → unmarshal ra chuỗi rỗng → rơi vào nhánh luỹ kế. Không migration.

**AC:**
- [ ] Ô chọn nằm ở tab Tuỳ chọn, cạnh `maxContentPerDay` / `hashtags` / `applyForSources`
- [ ] Tạo event mới mặc định *Toàn thời gian*
- [ ] Chuỗi rỗng, `all_time`, và giá trị lạ (`month`, `abc`) đều cho ra bảng luỹ kế
- [ ] Nhãn lấy từ file locale, không hardcode trong component

### FR-002: Xếp hạng theo phát sinh trong tuần — **Must Have**

Kỳ `week` chỉ tính lượt xem và tiền thưởng phát sinh từ **thứ Hai 00:00:00 đến Chủ nhật 23:59:59 giờ Việt Nam**. Thứ hạng dựa trên tổng `pending + completed` — đúng công thức frontend hiển thị ở cột Views, nếu xếp theo số khác thì thứ hạng mâu thuẫn với con số ngay bên cạnh.

| Case | Cấu hình | Tình huống | Kỳ vọng |
|---|---|---|---|
| 1 | `all_time` | bất kỳ | Bảng y hệt trước khi có tính năng |
| 2 | `week` | Giữa tuần, creator có phát sinh | Chỉ hiện phần phát sinh trong tuần |
| 3 | `week` | Creator ngừng đăng, tuần này 0 view | Không xuất hiện trên bảng |
| 4 | `week` | Chủ nhật 23:00 | Vẫn thuộc tuần hiện tại, không nhảy sang tuần sau |
| 5 | `week` | Thứ Hai 00:05, chưa có bản ghi nào | Bảng rỗng — hiển thị theo kết quả phê duyệt §7 |
| 6 | `week` | Hai creator cùng số view | Thứ tự ổn định giữa các lần gọi (tie-break `_id`) |

**AC:**
- [ ] 6 case trên đúng như bảng (case 5 theo kết quả phê duyệt §7)
- [ ] Tuần vắt qua ranh giới tháng tính đúng
- [ ] Biên hai tuần liền kề khít nhau — không hở giây nào, không chồng lấn
- [ ] Kết quả trả về đúng cấu trúc `UserEventResponse` của nhánh luỹ kế → frontend dùng chung một component

### FR-003: Bảng ghi rõ khung thời gian đang tính — **Must Have**

Kỳ `week` hiện dòng `Tuần này · 03/08 – 09/08` dưới tiêu đề bảng. Kỳ `all_time` không render dòng nào.

Biên tuần do server chốt và trả xuống qua `periodStartAt` / `periodEndAt`; frontend không tự tính. Server trả mốc dạng UTC nên frontend phải ghim offset giờ Việt Nam khi format.

> Thiếu dòng nhãn này thì creator chỉ thấy các con số nhỏ đi mà không hiểu vì sao — toàn bộ mục đích của tính năng biến mất. Đây là khác biệt có chủ đích so với `creator-os`, bên đó không hiển thị kỳ ở trang công khai.

**AC:**
- [ ] Kỳ `all_time` giao diện giữ nguyên từng pixel
- [ ] Kỳ `week` thiếu `periodStartAt`/`periodEndAt` → hiện "Tuần này" không kèm ngày, không vỡ layout
- [ ] Trình duyệt ở múi giờ khác vẫn hiện đúng ngày theo giờ Việt Nam
- [ ] Đúng ở cả desktop và mobile (breakpoint 768px)
- [ ] Frontend không gửi tham số kỳ lên API

### FR-004: Index + cache cho endpoint bảng xếp hạng — **Must Have**

Thêm index `{event, date}` cho `user_event_analytic_daily`, và cache-aside 10 phút cho endpoint.

Sáu index sẵn có của collection đều dẫn đầu bằng `user` hoặc `inviter`, mà truy vấn kỳ tuần lọc `{event, date}` không có `user` → quét toàn collection, mỗi lượt vào trang chủ một lần. Bảng xếp hạng nhiệm vụ đã cache 10 phút từ lâu, bảng event thì chưa.

Khoá cache nhúng **mốc kỳ** (`week_2026-08-03`) chứ không chỉ tên kỳ, để 00:00 thứ Hai là khoá tự đổi.

**AC:**
- [ ] Truy vấn kỳ tuần dùng index, không collection scan
- [ ] Index tạo tự động lúc khởi động, idempotent khi chạy lại
- [ ] Sang tuần mới bảng làm mới ngay, không đợi hết TTL
- [ ] Admin đổi kỳ → người xem thấy ngay
- [ ] Kết quả rỗng hợp lệ **có** cache; truy vấn lỗi **không** cache
- [ ] Redis không khả dụng → tính năng vẫn chạy, chỉ mất cache

### FR-005: Nhân bản event giữ nguyên cấu hình kỳ — **Should Have**

`cloneEventOptions` chép từng field bằng tay, không sao chép cả struct → không bổ sung field mới thì nhân bản event nuốt mất cấu hình, và im lặng vì kết quả vẫn là event hợp lệ.

**AC:**
- [ ] Nhân bản event kỳ `week` → event mới cũng `week`
- [ ] Nhân bản event không cấu hình → event mới cũng không có field, không sinh chuỗi rỗng thừa

## 5. Non-Functional Requirements

- **NFR-001:** Không migration, không đổi đường dẫn API — campaign đã tạo chạy đúng ngay sau deploy. Rollback chỉ cần đổi lại lựa chọn trong admin.
- **NFR-002:** Không N+1 — tra thông tin creator gom 1 truy vấn cho cả trang. Cache hit tốn 1 truy vấn, cache miss tốn 3.
- **NFR-003:** Không regression — nhánh luỹ kế không sửa logic; response kỳ `all_time` không thừa field nào; build BE pass.
- **NFR-004:** Khoá cache không chứa định danh người xem (response giống nhau với mọi người). Thêm dữ liệu riêng người xem thì **bắt buộc** bổ sung định danh vào khoá.

---

## 6. Epics & Prioritization

| Epic | FRs | Priority | Effort |
|------|-----|----------|--------|
| EPIC-001: Kỳ xếp hạng theo tuần | FR-001, FR-002, FR-003, FR-005 | Must | ~1.5 ngày |
| EPIC-002: Index + cache | FR-004 | Must | ~0.5 ngày |
| EPIC-003: Hoàn thiện trải nghiệm (§7) | — | Should (chờ §7) | ~1 ngày |

## 7. Đề xuất cần Sếp phê duyệt

| # | Nội dung cần quyết định | Đề xuất | Nếu không duyệt | Quyết định |
|---|------------------------|---------|-----------------|------------|
| 1 | Sáng thứ Hai bảng chưa có dữ liệu — **ẩn hay hiện trạng thái rỗng?** | **Hiện trạng thái rỗng** "Tuần này chưa có ai ghi điểm" — giữ khối trên trang | Cả khối bảng biến mất khỏi trang cho tới lượt crawl đầu tiên; creator mở trang thấy mục quen thuộc mất hẳn | ☐ |
| 2 | Tuần lịch (T2–CN) hay **7 ngày kể từ ngày mở campaign?** | **Tuần lịch** — creator hiểu ngay không cần giải thích | Campaign mở giữa tuần có "tuần 1" ngắn hơn 7 ngày; nếu brand trao thưởng theo tuần thì tuần đầu không công bằng | ☐ |
| 3 | Khối tiền cá nhân đứng cạnh bảng tuần — **có gắn nhãn "luỹ kế" không?** | **Có** — gắn nhãn, không đổi cách tính (tiền là tiền thật đã kiếm) | Creator có thể hiểu nhầm tiền cũng reset theo tuần | ☐ |

> Cả 3 đề xuất **không chặn** việc bật tính năng, nhưng nên chốt trước khi bật cho campaign có trao thưởng.

## 8. Out of Scope

- **Kỳ theo tháng** — `creator-os` có sẵn 3 kỳ trong model nhưng khách chỉ yêu cầu tuần
- **Xem lại bảng của tuần đã qua** — cần thêm API liệt kê các tuần trong khoảng campaign
- **Hạng của chính người xem khi ngoài top** — hạ tầng đã sẵn (`GetLeaderBoard` nhận định danh nhưng chưa dùng); làm thì **bắt buộc** đưa định danh vào khoá cache
- **Ghim creator lên đầu bảng** — `creator-os` có, ambassador chưa cần
- **Trao thưởng tự động theo tuần**
- **Nhãn kỳ cho giao diện partner ngoài Parasola** — backend đã sẵn sàng

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Bảng rỗng sáng thứ Hai bị ẩn khỏi trang → creator hoang mang | Đề xuất 1 §7; nếu duyệt thì hiện trạng thái rỗng |
| Partner app hiển thị icon từng nền tảng sẽ thấy toàn số 0 nếu bật kỳ tuần (nguồn dữ liệu không tách view theo nền tảng) | Chỉ bật kỳ tuần cho partner dùng giao diện dạng bảng như Parasola |
| Tạo index trên collection lớn làm chậm lượt deploy đầu | Theo dõi lượt deploy đầu tiên; index idempotent nên chạy lại an toàn |
| Người mở rộng sau quên đưa định danh người xem vào khoá cache → rò dữ liệu giữa các user | Cảnh báo đặt ngay tại chỗ dựng khoá trong code + NFR-004 + tech-spec §5 |
| QA test tưởng "chưa fix" vì cache 10 phút | Test bằng event mới hoặc chờ TTL; đổi kỳ trong admin làm đổi khoá nên thấy ngay |

## 10. Nghiệm thu

- [ ] Campaign chưa cấu hình kỳ trả kết quả y hệt trước khi có tính năng
- [ ] 6 case ở FR-002 pass (case 5 theo kết quả phê duyệt §7)
- [ ] Nhãn kỳ hiện đúng ngày trên desktop + mobile, kể cả trình duyệt ở múi giờ khác
- [ ] Sang tuần mới bảng làm mới trong vòng 1 phút
- [ ] Nhân bản event giữ nguyên cấu hình kỳ
- [ ] Regression NFR-003 pass

---

## 11. Trạng thái triển khai

**Đã ship:** FR-001 → FR-005. **PR #97** (merged 2026-08-05, vào `develop`). Phần cache + gom truy vấn creator gom trong **PR #99** (open).

### Sửa kèm trong PR #99 (có lợi cho cả nhánh luỹ kế đang chạy)

| Fix | Vấn đề | Cách xử lý |
|-----|--------|-----------|
| **A** | Mỗi dòng bảng một truy vấn `FindOne` → 20 dòng là 20 truy vấn, trên endpoint public không cache | Gom thành 1 truy vấn `$in` cho cả trang; áp dụng cả hai nhánh |
| **B** | `$limit <= 0` làm Mongo ném lỗi, lỗi bị tầng service nuốt → bảng rỗng không rõ nguyên nhân | Chỉ gắn `$skip`/`$limit` khi giá trị hợp lệ |
| **C** | Truy vấn lỗi vẫn cache → một lần DB trục trặc khoá bảng rỗng suốt 10 phút | Hai nhánh trả `(res, error)`; lỗi thì không cache |

### Test

13 hàm / 22 case, không hàm nào cần cơ sở dữ liệu: biên tuần (5/7), cấu trúc pipeline (4/8), khoá cache (4/7).

**Chưa kiểm chứng:** TypeScript chưa typecheck được (`typescript` không có trong `node_modules` của Parasola lẫn admin); chưa chạy với dữ liệu thật vì chưa campaign nào bật kỳ tuần.

---

## Appendix: Code Impact

| File | Thay đổi | FR | PR |
|------|----------|----|----|
| `backend/internal/model/mg/event.go` | Field `LeaderboardPeriod` trên `EventOpts` | FR-001 | #97 |
| `backend/internal/constants/constants.go` | Hằng kỳ + layout ngày cho khoá cache | FR-001, FR-004 | #97, #99 |
| `backend/internal/util/time.go` | `TimeStartOfWeekInHCM`, `TimeEndOfWeekInHCM` | FR-002 | #97 |
| `.../aggregate_pipeline/user_event_analytic_daily.go` | `GetUserEventLeaderboard` + guard phân trang | FR-002, B | #97, #99 |
| `backend/pkg/public/service/event.go` | Rẽ nhánh kỳ, tách `getLeaderBoardAllTime`, cache, gom truy vấn creator | FR-002, FR-004, A, C | #97, #99 |
| `backend/pkg/public/model/response/event.go` | `period` / `periodStartAt` / `periodEndAt` | FR-003 | #97 |
| `backend/internal/module/database/mongodb/index.go` | Index `{event, date}` | FR-004 | #97 |
| `backend/internal/module/redis/key.go` | `GetKeyCacheListLeaderBoardEvent` | FR-004 | #99 |
| `backend/pkg/admin/service/event.go` | `cloneEventOptions` giữ cấu hình kỳ | FR-005 | #97 |
| `admin/src/pages/event/components/modal.tsx` | Ô chọn "Kỳ xếp hạng" | FR-001 | #97 |
| `admin/src/configs/app.ts` + `locales/` | Bảng ánh xạ + nhãn | FR-001 | #97 |
| `parasola/.../leaderboard-list/index.tsx` + `.scss` | Nhãn kỳ + ghim offset giờ VN | FR-003 | #97 |
| `parasola/src/pages/home/model.ts` + `_desktop.tsx` + `not-logged-in/index.tsx` | Dẫn meta kỳ từ response xuống component | FR-003 | #97 |

*Chi tiết implement, root cause, test matrix: `tech-spec.md`*
