# PRD: Bảng xếp hạng theo kỳ — Lifetime / Week / Month

**Project:** Ambassador (Parasola + 16 partner app)
**Date:** 2026-08-06
**Author:** Dang Dinh
**Version:** 2.3 (đóng pha 1 + `frontend` ngang `parasola` — 2026-08-11)
**Status:** ✅ **Pha 1 code xong toàn bộ FR-001→FR-008**, đã lên `feat/leaderboard-weekly` (PR #127 đã merge vào `develop`, PR #128 chờ merge) và `feat/leaderboard-weekly-release` (PR #122 chờ merge vào `release`). Xem §6.1.
⚠️ **Chưa nghiệm thu trên giao diện thật** — chưa ai chạy admin để bấm thử, xem §6.5.
⚠️ **1 vấn đề chờ quyết định** (empty state, §6.4b). §6.4a đã bị bác bỏ. 3 đề xuất §7 vẫn chờ duyệt.
**Kế hoạch đóng phần còn thiếu:** `ambassador/plans/260810-1716-leaderboard-pha1-con-lai/plan.md` — ~5.2 ngày, branch `feat/leaderboard-weekly`
**Kế thừa:** `prd-leaderboard-weekly-2026-08-06.md` (v1.0 — chỉ Week, cấu hình phẳng ở cấp event). v1 giữ lại làm bản ghi phạm vi đã ship ở PR #97; **tài liệu này là bản có hiệu lực**.
**Review:** `feedback-review-2026-08-06.md` (Vinh Nguyen) — R1–R6 đã chốt, đã hợp nhất vào tài liệu này
**Tài liệu kỹ thuật:** `tech-spec.md` (spec implement) — **chưa cập nhật theo v2**, xem §6 pha 1

---

## 1. Executive Summary

Bảng xếp hạng campaign xếp theo con số **luỹ kế từ ngày campaign bắt đầu**. Với campaign chạy vài tháng, thứ hạng đóng băng: creator vào sau không thể đuổi kịp khoảng cách tích luỹ dù làm tốt, creator cũ ngừng đăng bài vẫn giữ hạng. Bảng không còn phản ánh ai đang hoạt động, và brand mất cột mốc để truyền thông hàng tuần.

**Nguyên nhân:** bảng đọc `statistic.pointTotal.completed` của `user_event` — collection giữ một document cho mỗi cặp user-event, chứa con số hiện tại, **không có field ngày**. Con số hình thành từ ngày nào là thông tin không tồn tại, nên không cắt theo kỳ được. Đây là giới hạn hình dạng dữ liệu, không phải lỗi truy vấn.

**Cách fix:** kỳ trở thành **cấu hình ba tầng** (mặc định ở partner, ghi đè ở event) với ba giá trị `LIFETIME` / `WEEK` / `MONTH`. Kỳ khác lifetime đọc `user_event_analytic_daily` — bảng thống kê theo ngày vốn đã có. Mặc định `LIFETIME` nên mọi thứ đang chạy không đổi.

**Phạm vi v2.0 rộng hơn v1.0** sau review 2026-08-06: thêm `MONTH`, tách `rankBy` khỏi `metrics`, quy tắc kỳ-hiển-thị có ân hạn, port pin từ creator-os, và hợp nhất với quyết định "config theo partner" của PRD 04-02.

**Đối chiếu creator-os — merge hai chiều.** creator-os **không có** weekly/monthly: `period` chỉ là enum khai báo, query thật bị defer (`leaderboard.service.ts:252` + SRS §10 của họ tự ghi nhận). Ambassador là nơi duy nhất có logic kỳ chạy thật. Lấy từ họ *definition + pin + scope + cách gắn landing*; trả ngược *logic kỳ*.

**Ràng buộc chi phối mọi quyết định: 17 app frontend fork.** Pha 1 giao được cả ba kỳ + pin + cấu hình per-partner mà **không đụng một dòng FE nào**.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Creator vào giữa campaign vẫn có cơ hội lên top | Thứ hạng đảo lại mỗi kỳ, không đóng băng theo tháng |
| 2 | Bảng phản ánh ai đang hoạt động | Creator ngừng đăng bài rời top trong vòng 1 kỳ |
| 3 | Brand có nhịp truyền thông theo kỳ | Mỗi campaign dài có N cuộc đua thay vì 1 |
| 4 | Partner tự chọn kỳ phù hợp với mình | Ops đổi cấu hình không cần deploy |
| 5 | Không ảnh hưởng thứ đang chạy | 0 partner đổi hành vi sau deploy; 0 app FE phải sửa ở pha 1 |
| 6 | Admin ghim được creator lên đầu bảng | Ghim có hạn dùng, tự rụng hết kỳ, có audit |

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **Creator mới vào** | Thi đua sòng phẳng với người vào trước, biết nỗ lực kỳ này được tính |
| **Creator đang hoạt động** | Biết rõ bảng đang tính khoảng thời gian nào, không nhầm là mất thành tích |
| **Brand / partner** | Chọn kỳ cho campaign của mình; một số muốn thu hẹp kỳ để thấy thay đổi rõ hơn |
| **Ops/Admin** | Cấu hình mặc định ở partner, ghi đè ở event; ghim creator lên đầu khi cần |
| **Kỹ sư 17 app FE** | Không phải sửa gì khi backend thêm kỳ mới |

---

## 4. Functional Requirements

### FR-001: Contract cấu hình — tách trục, `metrics` số nhiều — **Must Have**

```
period      : LIFETIME | WEEK | MONTH
scope       : EVENT | PARTNER              // PARTNER còn treo, xem §7.3
rankBy      : VIEWS | CASH | ...           // KHOÁ SORT DUY NHẤT
metrics     : [VIEWS, CASH]                // cột hiển thị, có thứ tự
valueBasis  : COMPLETED | COMPLETED_PLUS_PENDING   // áp cho CẢ BA kỳ
size        : int
graceDays   : int (mặc định 2)             // xem FR-004
```

`rankBy` tách khỏi `metrics` vì code **đã ngầm làm vậy nhưng hardcode ở hai chỗ**: pipeline tuần tính sẵn 4 giá trị nhưng chỉ `$sort` theo `totalView`; FE parasola đã render 2 cột. `showLeaderboardAmount = false` của PRD 04-02 tương đương `metrics: [VIEWS]`.

**AC:**
- [ ] Cấu hình trống → `LIFETIME / VIEWS / [VIEWS, CASH] / COMPLETED / 2`, tức hành vi hiện tại
- [ ] `rankBy` đổi được mà không phải sửa pipeline
- [ ] `metrics` quyết định cột nào có mặt và theo thứ tự nào
- [ ] Hai cờ `ShowLeaderboard` / `ShowLeaderboardAmount` hiện có vẫn hoạt động, đọc như lớp phủ lên `metrics`

### FR-002: Cấu hình ba tầng — hợp nhất partner và event — **Must Have**

| Tầng | Chứa | Ai sửa |
|------|------|--------|
| `partner.options.leaderboard` | mặc định cho partner | admin partner |
| `event.options.leaderboard` | ghi đè cho một event | ops |
| hardcode | `LIFETIME / VIEWS / [VIEWS, CASH] / COMPLETED / 2` | — |

> PRD 04-02 §Resolved Questions chốt *"Config theo **Partner**, apply cho tất cả event của Partner đó"* và liệt kê *"Config BXH theo từng Event"* vào Out of Scope. **Lưu ý phạm vi:** quyết định 04-02 nói về **cờ hiển thị** (`showLeaderboard` / `showLeaderboardAmount`), không nói về `period` — `period` khi đó chưa tồn tại. PR #97 đặt `leaderboardPeriod` phẳng trên `EventOpts` nên **không vi phạm 04-02**; đánh giá của review 2026-08-06 là *"Không sai, nhưng phải hợp nhất"*. Ba tầng giữ được cả hai: quyết định 04-02 thành tầng mặc định, cấp event thành tầng ghi đè.
>
> *Đính chính 2026-08-10: bản 2.0 viết PR #97 "đi ngược quyết định đã duyệt" — nặng hơn thực tế và hiểu sai phạm vi PRD 04-02. Đã sửa.*

**AC:**
- [ ] Field trên `EventOpts` là **struct `Leaderboard{}`**, không phải string phẳng — thêm `rankBy`/`metrics`/`graceDays` sau khỏi migrate lần hai
- [ ] Event không cấu hình → kế thừa partner; partner không cấu hình → hardcode
- [ ] **Merge theo từng field, không theo cả struct** — event chỉ đặt `period` thì `graceDays` của partner phải còn nguyên, không rơi về mặc định hệ thống
- [ ] Nhân bản event giữ nguyên cấu hình kỳ (`cloneEventOptions` chép từng field bằng tay)
- [ ] Không migration dữ liệu; rollback = đổi lại lựa chọn trong admin

### FR-003: Ba kỳ, hai nguồn dữ liệu — **Must Have**

| period | Nguồn | Lý do |
|--------|-------|-------|
| `LIFETIME` | `user_event` | **giữ nguyên cái đang chạy** |
| `WEEK` / `MONTH` | `user_event_analytic_daily` | có cột `date` |

> ⚠️ **Không được** tính `LIFETIME` từ bảng daily cho "đồng bộ". Bảng daily chỉ có dữ liệu từ lúc bật analytics, `user_event` luỹ kế từ ngày đầu → con số sẽ **tụt**, partner đang nhìn quen số cũ sẽ thấy view bốc hơi.

**AC:**
- [ ] Ba kỳ trả **cùng cấu trúc** `UserEventResponse` → FE dùng chung một component
- [ ] `valueBasis` áp chung cả ba kỳ, chấm dứt tình trạng `all_time` lọc/sort theo `completed` còn `week` theo `completed+pending`
- [ ] Tuần: T2 00:00:00 → CN 23:59:59 giờ VN. Tháng: ngày 1 → ngày cuối tháng, giờ VN
- [ ] Chủ nhật thuộc tuần hiện tại, không bị đẩy sang tuần sau
- [ ] Biên hai kỳ liền kề khít nhau — không hở giây nào, không chồng lấn
- [ ] Creator không phát sinh gì trong kỳ không xuất hiện trên bảng
- [ ] Hai creator cùng điểm có thứ tự ổn định giữa các lần gọi (tie-break `_id`)
- [ ] **Trước khi bật:** đo `min(date)` của bảng daily theo từng partner so với `event.startAt`; chênh thì MONTH của tháng đầu cũng thiếu

### FR-004: Kỳ hiển thị ≠ kỳ hiện tại — **Must Have**

```
graceDays = 2 (cấu hình)

displayAnchor(now):
   WEEK    : weekday(now) ∈ {T2, T3} → tuần TRƯỚC   ; còn lại → tuần hiện tại
   MONTH   : day(now)     ∈ {1, 2}   → tháng TRƯỚC  ; còn lại → tháng hiện tại
   LIFETIME: không áp dụng
```

View phát sinh Chủ nhật được crawl/chốt trong T2–T3, nên kỳ cũ chưa xong trước thứ Tư.

Clamp theo vòng đời event — hai ca hỏng ngay trên landing nếu không chặn:

| Ca | Nếu không chặn | Xử lý |
|---|---|---|
| Event khai giảng **đúng thứ Hai** | T2–T3 rơi vào tuần trước → bảng rỗng **và nhãn ghi ngày trước cả khi event tồn tại** | anchor không lùi trước kỳ chứa `StartAt` |
| Event **đã kết thúc** | qua T4 thành "kỳ hiện tại" rỗng → landing để bảng trắng vĩnh viễn | freeze anchor ở kỳ chứa `EndAt` |

**AC:**
- [ ] Tầng service **không gọi thẳng** `util.TimeStartOfWeekInHCM(now)` — phải bọc qua hàm kỳ-hiển-thị, nếu không quy tắc không có hiệu lực
- [ ] T2, T3 hiển thị kỳ trước; từ T4 hiển thị kỳ hiện tại
- [ ] Anchor không lùi trước kỳ chứa `event.StartAt`, không tiến sau kỳ chứa `event.EndAt`
- [ ] `graceDays` cấu hình được, không hardcode — **và ops đặt được từ form admin, không phải sửa DB tay**
- [ ] Bỏ trống ô `graceDays` → dùng mặc định, **không ghi `0` xuống DB** (con trỏ phải giữ nghĩa "chưa đặt", `0` là "tắt ân hạn")

> *2026-08-10: AC "cấu hình được" của bản 2.0 quá lỏng — backend có `GraceDays *int` là coi như đạt, trong khi form admin không có ô nhập nên thực tế giá trị vĩnh viễn là 2. Đã tách thành hai AC kiểm được từ giao diện.*

### FR-005: Bảng ghi rõ khoảng thời gian đang tính — **Must Have**

Response bổ sung, đều `omitempty`:

```
period, periodStartAt, periodEndAt   // của kỳ ĐANG HIỂN THỊ — không phải kỳ hiện tại
isSettling: true                     // đang trong ân hạn
```

Server cấp mốc, FE chỉ format. Server trả mốc dạng UTC nên FE phải ghim offset giờ VN.

> Thiếu nhãn thì creator chỉ thấy các con số nhỏ đi mà không hiểu vì sao. Đây là khác biệt có chủ đích so với creator-os — bên đó không hiển thị kỳ ở trang công khai.

**AC:**
- [ ] `LIFETIME` không trả ba field kỳ; giao diện giữ nguyên từng pixel
- [ ] Nhãn hiện mốc của **kỳ đang hiển thị**, không phải kỳ hiện tại
- [ ] Trình duyệt ở múi giờ khác vẫn hiện đúng ngày theo giờ VN
- [ ] `isSettling = true` trong T2–T3; FE pha 2 dùng để hiện dòng phụ *"Tuần này bắt đầu lên bảng từ thứ Tư"*
- [ ] FE không gửi tham số kỳ lên API

### FR-006: Ghim creator lên đầu bảng — **Must Have**

Port từ creator-os, merge ở **tầng service** rồi mới trả mảng → shape response không đổi, **17 app FE không phải sửa dòng nào**. Chỉ `admin/` cần ô ghim.

| Thuộc tính | Vì sao |
|---|---|
| `pinRank` (0 = đầu), upsert theo `(board, subject)` | ghim lại không đẻ bản ghi trùng |
| `expiresAt` → tự loại khi serve | **quan trọng nhất với kỳ tuần** — ghim cho tuần X phải tự rụng |
| `reason` + `pinnedBy` + audit | ghim ảnh hưởng thứ hạng và giải thưởng |
| dedup rồi **mới** cắt `size` | pin không lòi ra lần hai, không ăn mất chỗ |
| `source: pinned\|ranked` | thêm `omitempty`, FE dùng sau |

**AC:**
- [ ] Ghim lại cùng creator → update, không tạo bản ghi trùng
- [ ] Pin hết hạn tự loại khi serve, không thành pin zombie
- [ ] Pin lên đầu theo `pinRank`, dedup khỏi ranked, cắt `size` **sau** dedup
- [ ] **Chỉ cho ghim creator có phát sinh trong kỳ** — chặn ở admin lúc ghim, không chặn lúc serve
- [ ] Shape `UserEventResponse` không đổi

> Khác creator-os: họ trả `value = null` khi pin không có trong ranked. Ambassador FE render thẳng `statistic` → sẽ ra **0 view / 0đ** cạnh tên creator được ghim, rất tệ trên landing.

### FR-007: Index + cache — **Must Have**

Index `{event, date}` cho `user_event_analytic_daily`; cache-aside 10 phút.

Sáu index sẵn có đều dẫn đầu bằng `user`/`inviter`, mà truy vấn kỳ lọc `{event, date}` không có `user` → quét toàn collection.

**AC:**
- [ ] Truy vấn theo kỳ dùng index, không collection scan
- [ ] Khoá cache nhúng **mốc kỳ đang hiển thị** — xoay lúc **00:00 thứ Tư**, không phải thứ Hai
- [ ] Admin đổi kỳ → người xem thấy ngay
- [ ] Kết quả rỗng hợp lệ **có** cache; truy vấn lỗi **không** cache
- [ ] Redis không khả dụng → tính năng vẫn chạy, chỉ mất cache

> ⚠️ Merge PR #99 nguyên trạng (xoay khoá thứ Hai) rồi mới thêm ân hạn sẽ có **2 ngày phục vụ sai kỳ từ cache**. Sửa trước khi merge — hiện `develop` chưa có `GetKeyCacheListLeaderBoardEvent` nên còn kịp, không phải hotfix.

### FR-008: Giới hạn per-platform ở WEEK/MONTH — **Must Have (ràng buộc)**

`UserEventStatistic` có 10 nền tảng, nhưng bảng daily chỉ giữ **số lượng content** theo nền tảng — `EventAnalyticSource` không có view/cash theo nền tảng.

Hệ quả nối thẳng với PRD 04-02 FR-002: partner đặt `showLeaderboardAmount = false` được hứa là *"ẩn cash, **giữ nguyên số view theo platform**"*. Ở kỳ tuần/tháng, số view theo platform **toàn 0** → partner đó bật weekly là **bảng trắng**.

**AC:**
- [ ] Admin **chặn** bật WEEK/MONTH cho partner đang dùng UI per-platform, kèm thông báo rõ lý do
- [ ] Hoặc tối thiểu: cảnh báo trong form trước khi lưu

---

## 5. Non-Functional Requirements

- **NFR-001:** Không migration, không đổi đường dẫn API. Rollback = đổi lại lựa chọn trong admin.
- **NFR-002:** **Không đổi shape `UserEventResponse`** — chỉ thêm field `omitempty`. Đổi shape = 17 app phải sửa.
- **NFR-003:** **Không thêm endpoint mới cho tính năng cũ** — thêm BXH là thêm *giá trị* trong config, không phải URL mới. Thêm URL = 17 lần wiring service + model + component.
- **NFR-004:** **Mặc định trống = hành vi hiện tại**, để deploy BE không cần đụng FE nào.
- **NFR-005:** Không N+1 — tra thông tin creator gom 1 truy vấn cho cả trang, áp dụng cho **mọi** endpoint của landing (gồm `GetListUserNewest`, hiện còn N+1).
- **NFR-006:** Khoá cache không chứa định danh người xem. Thêm dữ liệu riêng người xem thì **bắt buộc** bổ sung định danh vào khoá.

---

## 6. Epics & Prioritization

Chia theo **chi phí frontend**, không theo tính năng.

| Pha | Nội dung | FRs | FE phải sửa | Effort |
|-----|----------|-----|-------------|--------|
| **1** | Ba kỳ + contract + ba tầng cấu hình + pin + anchor/clamp + index/cache + gộp lỗi §11 | FR-001→FR-008 | **0 / 17** | ~5 ngày |
| **2** | Nhãn kỳ + `isSettling` + cột `metrics` động | — | 17 app, 1–2 file/app, cơ học | ~3 ngày |
| **3** | Nhiều BXH mỗi event (definition model của creator-os) | — | 17 app — chỉ khi có nhu cầu thật | chưa ước |

Pha 1 giao được cả ba kỳ + pin + cấu hình per-partner **mà không đụng một dòng FE nào**. Đề nghị dừng ở đó rồi đánh giá lại.

### 6.1 Trạng thái thật của pha 1 — cập nhật 2026-08-10

Bản 2.0 chỉ ghi một dòng *"Pha 1 | FR-001→FR-008 | ~5 ngày"*, không có ô tick từng FR. Hệ quả: pha 1 được ship từng phần, phần bị cắt không có chỗ nào bắt buộc phải khai báo, nên nhìn tài liệu vẫn thấy trọn vẹn. QA đọc PRD đi test rồi báo thiếu — đúng, và là lỗi tài liệu. Từ đây trạng thái ghi theo FR:

| FR | Nội dung | Trạng thái | Bằng chứng |
|---|---|---|---|
| FR-001 | Ba kỳ LIFETIME / WEEK / MONTH | ✅ | `constants.LeaderboardPeriod*` |
| FR-002a | Cấu hình ba tầng | ✅ | `internal/service/leaderboard_config.go` — `ResolveLeaderBoardConfig`; `LeaderboardOpts.MergeOver` trộn **từng field**; form partner có 4 ô + `graceDays` |
| FR-002b | `rankBy` / `metrics` / `valueBasis` | ✅ | `LeaderboardRankFields` + `LeaderboardRankValueExpr` dùng chung cho cả hai pipeline; `EffectiveMetrics()` áp lớp phủ `showLeaderboardAmount` |
| FR-003 | Biên kỳ theo giờ VN | ✅ | PR #108 sửa lệch 1 ngày ở kỳ tháng |
| FR-004 | Ân hạn + clamp | ✅ | ô "Số ngày ân hạn đầu kỳ" ở tab BXH + form partner; chỉ hiện với kỳ tuần/tháng |
| FR-005 | `isSettling` trong response | ✅ | parasola + frontend đều dùng, có dòng ghi chú "Tuần này bắt đầu lên bảng từ thứ Tư" |
| FR-006 | Pin creator | ✅ | `pin` nằm trên `user_event` (không tách collection); tab BXH có tìm theo tên, ghim/bỏ ghim, lý do, ngày hết hạn; cắt theo `size` sau khi ghép pin |
| FR-007 | Index + cache | ✅ | index `{event, date}` + `{event, pin.rank}`; khoá cache nhúng mốc kỳ + `rankBy` + `valueBasis`; xoá theo pattern khi đổi ghim/cấu hình |
| FR-008 | Chặn per-platform ở admin | ✅ | chặn cứng khi `showLeaderboardAmount = false` + kỳ tuần/tháng |

Lỗi §11: #1 ✅ · #2 ✅ · #3 ✅ · #4 ✅ · #5 ✅ · #7 ⚠️ chỉ gom hằng số · #6 không sửa được (thiếu field ở bảng daily), đã ở Out of Scope.

**§11.2 đã đóng:** `LeaderboardRankValueExpr` là chỗ duy nhất định nghĩa "giá trị xếp hạng", cả hai pipeline gọi chung. Trước đây `all_time` lọc/sắp theo `completed` còn `week`/`month` theo `completed + pending` — cùng một event, đổi kỳ thì thứ hạng đổi vì khác công thức chứ không vì khác khung thời gian.

**§11.7 (`wildRift` hardcode) mới gom hằng số, chưa sửa gốc.** Sửa thật phải đổi mô hình dữ liệu sang bản ghi `(user, partner)` + migration — chưa ước lượng, chưa nằm trong pha nào.

### Ngoài phạm vi FR — sửa thêm trong pha 1

| Vấn đề | Vì sao phải sửa ngay |
|---|---|
| 5 endpoint BXH ở admin không kiểm partner | Staff của partner A biết id event của partner B là ghim được trên bảng của B — đổi cả thứ hạng lẫn giải thưởng của đối tác khác |
| Đổi cấu hình BXH ở partner không xoá cache | Ops sửa xong nhìn từng event vẫn thấy bảng cũ suốt 10 phút TTL, không có lỗi nào báo |
| `defer cursor.Close()` đặt trước khi kiểm lỗi | `Aggregate`/`Find` lỗi trả cursor nil → panic |
| Ghim creator chưa tham gia sự kiện | `UpdateOne` khớp 0 document vẫn trả `nil` → admin báo "Thành công" mà không ghim gì |

### 6.2 Điều chỉnh phạm vi FE — 2026-08-10

Pha 2 rút từ **17 app xuống chỉ `parasola`** theo chốt của chủ sản phẩm. `frontend` đã port ở PR #111 (giữ nguyên, không revert). 15 app còn lại **không port**.

Hệ quả: **FR-008 quan trọng hơn chứ không nhẹ đi.** Cấu hình kỳ nằm ở tầng partner/event dùng chung, nên bật kỳ tuần cho partner đang chạy trên app chưa port sẽ ra một hàng số 0 theo nền tảng. Chặn ở admin là thứ duy nhất ngăn việc đó.

**Cập nhật 2026-08-11 — `frontend` đưa lên ngang `parasola` theo yêu cầu.** Bản port PR #111 mới có nhãn kỳ, thiếu `valueBasis` và `metrics`; để nguyên thì đó là bản sửa nửa vời, hại hơn không sửa. Hiện trạng hai app:

| Trục | parasola | frontend | 15 app còn lại |
|---|---|---|---|
| `period` / mốc kỳ / `isSettling` | ✅ | ✅ | ❌ |
| `valueBasis` | ✅ | ✅ | ❌ |
| `metrics` | ✅ | ✅ | ❌ |
| Ô view = đúng giá trị đem xếp hạng | ✅ | ✅ | ❌ |
| Format số rút gọn Tỷ/Tr/N + CountUp | ✅ | ✅ | ❌ |
| `source: pinned\|ranked` | ❌ pha 2 | ❌ pha 2 | ❌ |

**`frontend` bỏ dãy icon theo nền tảng, chuyển sang một tổng view như `parasola`.** Cách cũ lọc theo `applyForSources` nên event giới hạn nguồn thì tổng bày ra **không bằng** giá trị đem đi xếp hạng (xếp hạng tính mọi nền tảng); thêm nữa kỳ tuần/tháng không tách được view theo nền tảng nên phải rẽ nhánh riêng. Gộp về một tổng là hết cả hai. Bố cục card giữ nguyên — chỉ đồng bộ tính năng, không port layout bảng của `parasola`.

Ba thay đổi **nhìn thấy được** trên landing chạy `frontend`, cần báo trước cho partner:

1. **Không còn dãy icon theo nền tảng**, thay bằng một tổng lượt xem. Lý do ở đoạn trên — số cũ có thể không bằng giá trị đem đi xếp hạng.
2. Cấu hình mặc định `metrics = [view, cash]` → **cột tiền xuất hiện** (app này trước đây chưa bao giờ render tiền). Tắt bằng `showLeaderboardAmount = false` ở partner, hoặc `metrics = [view]` ở event.
3. `showLeaderboardAmount = false` trước đây ẩn **cả khối số**; nay chỉ ẩn cột tiền, **số view hiện trở lại** — đúng lời hứa *"ẩn cash, giữ nguyên số view"* của PRD 04-02 FR-002.

Mục 2 và 3 là về đúng spec PRD 04-02. Mục 1 là quyết định trong đợt này, ghi ở đoạn trên.

Khi thiếu `metrics` (FE lên trước BE), `frontend` rơi về `[view]` chứ không phải `[view, cash]` như parasola — để deploy lệch không đổi gì trên trang.

### 6.3 Kỷ luật ship — bổ sung sau sự cố 2026-08-10

- Mỗi PR ghi rõ trong body **FR nào được đóng lại**; FR chưa đóng thì §6.1 giữ nguyên ❌.
- Cắt phạm vi giữa chừng phải cập nhật §6.1 **trong cùng PR đó**, không để sang lần sau.
- Không dùng comment trong code để định nghĩa lại phạm vi pha. Bản 2.0 để lọt việc này: `leaderboard_opts.go:10` tự ghi `RankBy / Metrics / ValueBasis` *"CHƯA có hiệu lực ở pha 1"*, trong khi review §6 xếp `rankBy`/`valueBasis` **vào** pha 1 — code tự khai mình đủ nên không ai soát ra.

### 6.4 Phát hiện mới khi rà soát — cần quyết định — 2026-08-11

#### (a) ~~`rankBy = view` đếm hai chỉ số khác nhau ở hai kỳ~~ — ĐÃ BÁC BỎ

> Bản đầu của mục này (2026-08-11) kết luận `all_time` xếp theo "point" còn `week`/`month` xếp theo "view", và event có mission thì hai kỳ đổi bản chất tiêu chí. **Kết luận đó SAI**, đã kiểm lại và bác bỏ trong cùng ngày. Giữ lại mục này để không ai đi lại vào cùng một chỗ.

Tên field gây hiểu nhầm: `all_time` xếp theo `statistic.pointTotal`, `week`/`month` xếp theo `statistic.view`. Nhưng trên `user_event`, **`point` là bản sao nguyên văn của `view`**:

```go
// user_event.go — UserContentStatistic.GetPoint()
return CommonStatisticContent{
    Total: u.View.Total, Pending: u.View.Pending,
    Rejected: u.View.Rejected, Completed: u.View.Completed,
}
```

`buildSourceStatistic` gán `s.Point = s.GetPoint()` và dựng `s.View` từ các field `totalView*` của pipeline trên collection `content` (`$sum: "$statistic.view.total"`…). `PointTotal = GetPointTotal()` chỉ là tổng `Point` của các nền tảng.

⇒ **`user_event.pointTotal` chính là tổng lượt xem.** Cả ba kỳ đều xếp theo view. Không có mâu thuẫn.

Chỗ `statistic.point = mission.Reward` (`content.go`) nằm trên collection **`content`**, không phải `user_event`, và không có đường nào chảy vào `pointTotal` — `user_event` được dựng lại từ các pipeline tổng hợp **view**. Xếp hạng theo điểm nhiệm vụ đi qua endpoint riêng (`leaderboard-by-point`, chỉ wildRift dùng).

**Không cần quyết định gì. Không có việc phải làm.**

#### (b) Bảng rỗng — ẩn hay hiện trạng thái rỗng

v1.0 §7 đề xuất **hiện trạng thái rỗng**, chưa tick. v2.0 đóng đề xuất đó với lý do ân hạn T4 làm ca này *"gần như không còn xảy ra"*, nhưng vẫn ghi *"vẫn nên có empty state như lưới an toàn cho ca event vừa khai giảng"*.

**Code đang ẩn hoàn toàn** — cả `parasola` lẫn `frontend` đều `return null` khi danh sách rỗng. Backend thì đã chuẩn bị sẵn: `emptyLeaderBoard` cố ý giữ nguyên `period` / `periodStartAt` / `periodEndAt` / `isSettling` / `valueBasis` / `metrics` đúng để FE render được nhãn kỳ trên khối rỗng — FE hiện không dùng tới.

Ân hạn không cứu được ca **event vừa khai giảng**: FR-004 chốt anchor không lùi trước kỳ chứa `StartAt`, nên event mở hôm nay thì kỳ hiển thị là kỳ hiện tại, rỗng thật. Kỳ luỹ kế cũng rỗng cho tới content đầu tiên được duyệt.

Đây là **khuyến nghị trong ghi chú, không phải FR có acceptance criteria** → chưa làm. Chốt xong thì hoặc làm empty state cho parasola + frontend, hoặc sửa mục này ghi rõ đã cân nhắc và chọn ẩn.

### 6.5 Chưa nghiệm thu + nợ còn lại — 2026-08-11

**Chưa ai chạy admin để bấm thử.** Kiểm tra tự động đã qua: `go build` sạch, 19 test BXH pass, `tsc --noEmit` 0 lỗi ở `admin` / `parasola` / `frontend`. Những thứ chỉ máy thật mới xác nhận được:

- 4 dropdown cấu hình hiện đúng chữ tiếng Việt (Toàn thời gian / Theo tuần / Theo tháng)
- Lưu cấu hình → chuyển tab → quay lại thấy giá trị mới
- Ghim lỗi thì modal ở nguyên, không mất ngày + lý do vừa gõ
- Ô `graceDays` ẩn/hiện theo kỳ
- Staff partner khác bị chặn đúng
- Đổi cấu hình ở partner phản ánh ngay trên event

**Nợ đã báo, chưa sửa:**

| Nợ | Ảnh hưởng |
|---|---|
| Landing chưa đọc `source: pinned\|ranked` | Dòng được ghim không phân biệt được với dòng lên bằng hạng thật — PRD xếp vào pha 2 |
| Mỗi request landing tốn thêm 1 truy vấn partner | `ResolveLeaderBoardConfig` chạy **trước** khi tra cache |
| `GetList` ghim nuốt lỗi phân quyền | Staff partner khác nhận `[]` + HTTP 200 thay vì 403; `Upsert`/`Delete` trả lỗi đúng. Không rò dữ liệu |
| Ghim hết hạn nán lại tối đa 10 phút | `expiresAt` chỉ lọc lúc dựng bảng, không có gì xoá cache đúng lúc hết hạn |
| `MergeOver` không cho event đặt `size` về 0 | Chưa chạm tới được — admin không có ô nhập `size` ở cả hai cấp |

## 7. Đề xuất cần Sếp phê duyệt

| # | Nội dung cần quyết định | Đề xuất | Nếu không duyệt | Quyết định |
|---|------------------------|---------|-----------------|------------|
| 1 | Tuần lịch (T2–CN) hay **7 ngày kể từ ngày mở campaign?** | **Tuần lịch** — creator hiểu ngay không cần giải thích | Campaign mở giữa tuần có "tuần 1" ngắn hơn 7 ngày; nếu brand trao thưởng theo tuần thì tuần đầu không công bằng | ☐ |
| 2 | `graceDays = 2` đang lấy theo cảm tính vận hành — **đo thực tế rồi chốt?** | **Đo trước** `max(date)` của bảng daily so với hiện tại trên vài event thật, rồi chốt con số | Giữ 2 ngày. Nếu độ trễ crawl thật ngắn hơn thì T2–T3 creator đăng bài mà bảng không nhúc nhích một cách không cần thiết | ☐ |
| 3 | **Scope PARTNER** (BXH xuyên event trên landing home) có vào lộ trình này không? | **Tách riêng** — WEEK/MONTH thì rẻ (bảng daily đã có field `partner`, chỉ thiếu index), nhưng **LIFETIME theo partner chưa có nguồn**, phải gom nhiều event hoặc dựng bảng luỹ kế mới | Gộp vào pha 1 → việc lớn hơn cả pha 1 cộng lại | ☐ |

**Đã giải quyết:** đề xuất *"empty state sáng thứ Hai"* của v1.0 — với luật ân hạn T4 (FR-004), T2/T3 hiển thị kỳ cũ đã có dữ liệu nên **gần như không còn xảy ra**. Vẫn nên có empty state như lưới an toàn cho ca event vừa khai giảng.

## 8. Out of Scope

- **Nhiều BXH mỗi event** (definition model đầy đủ của creator-os) — pha 3, chỉ khi có nhu cầu thật
- **Scope PARTNER / BXH xuyên event** — chờ §7.3
- **`metrics` per-platform ở WEEK/MONTH** — cần bổ sung field vào bảng daily, việc riêng
- **Ghim content** — ambassador đã có qua `content.order`
- **Port `subjectType = CONTENT` và `eligibility` của creator-os** — xem §9
- **Trao thưởng tự động theo kỳ**
- **Gộp 17 app FE thành package chung**

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Tính LIFETIME từ bảng daily → con số tụt, partner thấy view bốc hơi | FR-003: LIFETIME **chỉ** đọc `user_event`. Đo `min(date)` trước khi bật |
| Partner dùng UI per-platform bật WEEK → bảng trắng | FR-008: chặn ở admin |
| Merge PR #99 trước khi có ân hạn → 2 ngày phục vụ sai kỳ từ cache | FR-007: sửa khoá xoay theo T4 **trước** khi merge |
| Để `LeaderboardPeriod` phẳng lên release → migrate lần hai khi thêm `rankBy`/`metrics` | FR-002: đổi thành struct **ngay**, `release` chưa có gì nên đang rẻ |
| T2–T3 creator đăng bài mà bảng không nhúc nhích → ticket "BXH hỏng" | Pha 2: dòng phụ từ `isSettling`. Trước đó: thông báo Ops |
| Partner trao giải tuần vào T2 khi số chưa chốt | Thứ hạng **chỉ chốt được từ T4**; thông báo partner |
| Bê nguyên cách dựng SQL của creator-os | **Không port**: `eligibility.contentStatus` nội suy thẳng vào `$queryRawUnsafe` chỉ với `.replace(/'/g,'')`; `METRIC_COL.FOLLOWERS` trỏ cột **không tồn tại** trong `metrics_snapshots` → lỗi runtime không guard |
| Người mở rộng sau quên đưa định danh người xem vào khoá cache | NFR-006 + cảnh báo tại chỗ dựng khoá trong code |

## 10. Nghiệm thu

- [ ] Partner/event chưa cấu hình → kết quả y hệt trước khi có tính năng
- [ ] Ba kỳ trả cùng shape; 0 app FE phải sửa khi hoàn thành pha 1
- [ ] T2, T3 hiển thị kỳ trước; từ T4 hiển thị kỳ hiện tại; khoá cache xoay đúng T4
- [ ] Anchor clamp đúng ở event vừa khai giảng và event đã kết thúc
- [ ] Nhãn kỳ hiện đúng ngày kể cả trình duyệt ở múi giờ khác
- [ ] Pin: hết hạn tự rụng, dedup đúng, không tạo bản ghi trùng
- [ ] `valueBasis` áp chung — không còn tình trạng creator có mặt ở BXH tuần rồi biến mất ở BXH lifetime
- [ ] Bảy lỗi §11 đã xử lý
- [ ] Regression NFR-001→NFR-004 pass

---

## 11. Lỗi và nợ phát hiện khi đối chiếu code — gom vào pha 1

| # | Vấn đề | Vị trí | Đã xác minh |
|---|--------|--------|:-----------:|
| 1 | PR #97 mới ở `develop`; `release` chưa có gì. PR #99 **chưa vào develop** → **chưa có gì chạy thật** | — | ✅ |
| 2 | `all_time` sort theo `completed`, `week` theo `completed+pending` — cùng bảng, hai nghĩa | `pkg/public/handler/event.go:318` | ✅ |
| 3 | `GetListUserNewest` chỉ cộng view **YouTube + TikTok**, bỏ 8 nền tảng → creator chạy Facebook/Threads hiện `TotalView = 0` ngay trên landing | `pkg/public/service/event.go:73` | ✅ |
| 4 | `GetListUserNewest` còn N+1. PR #99 đã gộp `$in` cho leaderboard nhưng **bỏ sót hàm này — cùng một trang landing** | `pkg/public/service/event.go:63-68` | ✅ |
| 5 | Nhánh `week` nuốt `SortInterface` do handler truyền → thêm BXH theo tiền phải sửa pipeline. `rankBy` giải được | pipeline | ✅ |
| 6 | Bảng daily không có view/cash theo nền tảng → per-platform bất khả ở WEEK/MONTH | `model/mg/event_analytic_daily.go:50-55` | ✅ |
| 7 | `/missions/leaderboard-by-point` hardcode `wildRift.*` — BXH **thứ ba** trong hệ thống, partner-scoped nhưng không tái dùng được | `pkg/public/service/mission.go:597-614` | ✅ |

Cả 14 app đều gọi `/events/:id/leaderboards` + `/events/user-newest`; riêng wildrift gọi thêm `leaderboard-by-point`. Cổng hiển thị ở `parasola/.../not-logged-in/index.tsx:562`.

---

## Appendix: Code Impact (pha 1)

| File | Thay đổi | FR |
|------|----------|----|
| `internal/model/mg/event.go` | `LeaderboardPeriod string` → struct `Leaderboard{}` | FR-002 |
| `internal/model/mg/partner.go` | Thêm `options.leaderboard` tầng mặc định | FR-002 |
| `internal/util/time.go` | Biên tuần (đã có) + biên tháng + hàm kỳ-hiển-thị có ân hạn/clamp | FR-003, FR-004 |
| `.../aggregate_pipeline/user_event_analytic_daily.go` | `rankBy` / `valueBasis` thay vì hardcode `totalView` | FR-001, FR-003 |
| `pkg/public/service/event.go` | Phân giải cấu hình ba tầng, ba nhánh kỳ, merge pin, cache; sửa lỗi §11.3 và §11.4 | FR-002→FR-007 |
| `pkg/public/model/response/event.go` | `isSettling` + `source` (đều `omitempty`) | FR-005, FR-006 |
| `internal/module/database/mongodb/index.go` | Index `{event, date}` (đã có), cân nhắc `{partner, date}` cho §7.3 | FR-007 |
| `internal/module/redis/key.go` | Khoá nhúng mốc **kỳ hiển thị** | FR-007 |
| `internal/model/mg/leaderboard_pin.go` *(mới)* | Model pin | FR-006 |
| `pkg/admin/...` | Form cấu hình ba tầng + ô ghim + chặn per-platform | FR-002, FR-006, FR-008 |
| `pkg/public/service/mission.go` | Gỡ hardcode `wildRift.*` (nếu gom §11.7) | — |

*Chi tiết implement, root cause, test matrix: `tech-spec.md`. Kết quả đối chiếu creator-os: `feedback-review-2026-08-06.md`.*

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-08-06 | Dang Dinh | Bản đầu — chỉ WEEK, cấu hình phẳng ở cấp event |
| 2.0 | 2026-08-06 | Dang Dinh | Hợp nhất `feedback-review-2026-08-06.md`: thêm MONTH + LIFETIME tường minh; tách `rankBy`/`metrics`/`valueBasis`; cấu hình ba tầng hoà giải với PRD 04-02; quy tắc kỳ-hiển-thị có ân hạn + clamp vòng đời event; port pin từ creator-os; ràng buộc per-platform; lộ trình 3 pha theo chi phí FE; 7 lỗi đối chiếu code. §7 thay bằng 3 đề xuất mới |
