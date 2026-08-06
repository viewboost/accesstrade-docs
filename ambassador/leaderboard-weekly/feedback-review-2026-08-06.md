# Feedback & Review: Mở rộng BXH sang Weekly / Monthly / Lifetime

**Date:** 2026-08-06
**Author:** Vinh Nguyen
**Version:** 1.0
**Status:** Draft — chờ duyệt trước khi viết spec
**Review đối tượng:** `prd-leaderboard-weekly-2026-08-06.md` + `tech-spec.md` (PR #97 merged `develop`, PR #99 open)
**Đối chiếu:** `pmax-projects/creator-os` (module leaderboard) · `ambassador/prd-partner-leaderboard-config-2026-04-02.md`

> Bối cảnh: cần BXH **weekly / monthly / lifetime** gắn vào **landing campaign** và **landing home của partner**,
> đồng bộ mô hình với creator-os. Tài liệu này ghi lại kết quả đối chiếu code thật của cả hai repo,
> các điều chỉnh thiết kế, và những chỗ PR #97/#99 cần sửa **trước khi lên release**.

---

## 0. Ba kết luận cần đọc trước

**0.1 — Hướng "clone creator-os" chỉ đúng một nửa.** creator-os **không có** weekly/monthly. `period` chỉ là enum khai báo; query thật defer:

> `/** Query rank thô theo subject/metric/scope. ALL_TIME = latest snapshot. period MONTH/WEEK defer. */`
> — `creator-os/apps/api/src/modules/leaderboard/leaderboard.service.ts:252`, và SRS §10 của creator-os tự ghi nhận gap này.

Ambassador (PR #97) là nơi **duy nhất** có logic kỳ chạy thật. Nên đây là **merge hai chiều**:

| | creator-os | ambassador |
|---|---|---|
| Model cấu hình (N bảng/scope, subject, metric, size, eligibility, tieBreak) | ✅ | ❌ 1 bảng cứng/event |
| Pin (bảng riêng, `pinRank` + `reason` + `expiresAt`) | ✅ | ❌ chỉ `content.order` cho content |
| Scope GLOBAL + CAMPAIGN | ✅ | ❌ event-only |
| Gắn vào landing (`/landing/creators`, `/landing/videos`, CMS section) | ✅ | ❌ |
| **Query WEEK / MONTH** | ❌ **defer** | ✅ WEEK (mới ở `develop`) |
| Bảng daily có cột `date` | ✅ `content_analytic_daily`, `creator_analytic_daily` | ✅ `user_event_analytic_daily` |
| Frontend | 1 package dùng chung | **17 app fork** |

→ Lấy từ creator-os: **definition + pin + scope + cách gắn landing**. Trả ngược về creator-os: **logic kỳ**.

**0.2 — Quy tắc ân hạn tới thứ Tư phá thiết kế cache đã ghi trong PR #99.** Xem §2 và §3.

**0.3 — PR #97 đặt cấu hình kỳ ở cấp EVENT, mâu thuẫn với quyết định đã duyệt.**
`prd-partner-leaderboard-config-2026-04-02.md` §Resolved Questions chốt *"Config theo **Partner**, apply cho tất cả event của Partner đó"*, và §Out of Scope ghi rõ *"Config BXH theo từng Event"* là ngoài phạm vi. PR #97 lại đặt `leaderboardPeriod` trên `EventOpts`. Không sai, nhưng phải hợp nhất — xem §5.

---

## 1. Yêu cầu bổ sung (chốt trong buổi review)

| # | Yêu cầu | Ảnh hưởng |
|---|---|---|
| R1 | `metric` phải là **số nhiều**: 1 metric chính (quyết định thứ hạng) + nhiều metric phụ (cột hiển thị) | §2 |
| R2 | **Lifetime** = cái đang chạy trên landing partner: luỹ kế từ đầu, không giới hạn thời gian. Một số partner muốn thu hẹp kỳ để thấy thay đổi rõ hơn | §2 |
| R3 | BXH phải **hiển thị rõ khoảng thời gian** đang tính | §3 |
| R4 | **Không đổi kỳ ngay đầu tuần** — T2, T3 vẫn hiển thị tuần cũ; chỉ sang tuần mới từ **thứ Tư** | §3 |
| R5 | Các action **pin top** của creator-os phải mang theo | §4 |
| R6 | **Frontend chưa thể gộp** (17 app fork) | §6 |

---

## 2. Contract hợp nhất — tách trục, `metrics` số nhiều

```
period      : LIFETIME | WEEK | MONTH
scope       : EVENT | PARTNER              // PARTNER còn treo, xem §8
rankBy      : VIEWS | CASH | ...           // KHOÁ SORT DUY NHẤT
metrics     : [VIEWS, CASH]                // cột hiển thị, có thứ tự
valueBasis  : COMPLETED | COMPLETED_PLUS_PENDING   // áp cho CẢ BA kỳ
size        : int
graceDays   : int (mặc định 2)             // §3
```

### 2.1 Vì sao phải tách `rankBy` khỏi `metrics`

Code hiện tại **đã ngầm làm vậy nhưng hardcode ở hai chỗ khác nhau**, và đó chính là nguồn của sự thiếu nhất quán:

- Pipeline tuần **đã tính sẵn 4 giá trị** (view pending/completed, cash pending/completed) nhưng chỉ `$sort` theo `totalView` — `backend/internal/module/database/mongodb/aggregate_pipeline/user_event_analytic_daily.go`
- FE parasola **đã render 2 cột** Views + "Kiếm được" — `parasola/src/pages/home/components/leaderboard-list/index.tsx:15-19`
- `prd-partner-leaderboard-config-2026-04-02.md` FR-002 (`showLeaderboardAmount`) thực chất là **bật/tắt metric thứ hai** dưới dạng cờ boolean

→ `metrics: []` chỉ là tổng quát hoá đúng của thứ đã tồn tại. `showLeaderboardAmount=false` tương đương `metrics: [VIEWS]`.

### 2.2 `valueBasis` — sửa mâu thuẫn hiện có

| Nhánh | Lọc | Sắp xếp |
|---|---|---|
| `all_time` | `statistic.pointTotal.completed > 0` | `statistic.pointTotal.completed` DESC (`backend/pkg/public/handler/event.go:318`) |
| `week` | `completed + pending > 0` | `completed + pending` DESC (trong pipeline) |

Cùng một bảng, hai định nghĩa. PRD FR-002 cố ý chọn `pending+completed` cho week để khớp con số FE hiển thị — nhưng như vậy **`all_time` vẫn lệch với chính con số bên cạnh nó**, và creator chỉ có view pending sẽ xuất hiện ở BXH tuần rồi biến mất ở BXH lifetime. `valueBasis` áp chung cho cả ba kỳ là chỗ chốt một lần.

### 2.3 Nguồn dữ liệu — CỐ Ý khác nhau, không gom

| period | nguồn |
|---|---|
| `LIFETIME` | `user_event` (luỹ kế) — **giữ nguyên cái đang chạy** |
| `WEEK` / `MONTH` | `user_event_analytic_daily` (có cột `date`) |

> ⚠️ **Bẫy:** nếu vì "cho đồng bộ" mà tính luôn LIFETIME từ bảng daily, con số sẽ **tụt** — bảng daily chỉ có
> dữ liệu từ lúc bật analytics, còn `user_event` luỹ kế từ ngày đầu. Partner đang nhìn quen số cũ sẽ thấy view bốc hơi.
>
> **Việc phải làm trước:** đo `min(date)` của `user_event_analytic_daily` theo từng partner, so với `event.startAt`.
> Nếu chênh thì MONTH của tháng đầu cũng thiếu, không riêng LIFETIME.

### 2.4 Giới hạn đã xác minh — `metrics` per-platform bất khả ở WEEK/MONTH

`UserEventStatistic` có **10 nền tảng** (`backend/internal/model/mg/user_event.go:24-43`), nhưng bảng daily chỉ giữ **số lượng content** theo nền tảng, **không có view/cash theo nền tảng** — `EventAnalyticSource` chỉ có `TotalContent*` (`backend/internal/model/mg/event_analytic_daily.go:50-55`).

Hệ quả cụ thể, nối thẳng với PRD #97 §9 và với PRD 04-02 FR-002:

- `getLeaderBoardWeekly` dựng `Statistic` chỉ với `PointTotal` + `CashTotal` → **mọi field per-platform = 0**.
- Partner đặt `showLeaderboardAmount = false` được PRD 04-02 hứa là *"ẩn cash, **giữ nguyên số view theo platform**"*. Ở chế độ tuần, số view theo platform **toàn số 0** → partner đó bật weekly là bảng trắng.

→ **WEEK/MONTH chỉ bật cho partner dùng UI kiểu bảng tổng (như Parasola).** Muốn per-platform theo kỳ thì phải bổ sung field vào bảng daily — việc riêng, không gộp vào đợt này.

---

## 3. Kỳ hiển thị ≠ kỳ hiện tại (R3 + R4)

### 3.1 Công thức

```
graceDays = 2 (cấu hình)

displayAnchor(now):
   WEEK    : weekday(now) ∈ {T2, T3} → tuần TRƯỚC   ; còn lại → tuần hiện tại
   MONTH   : day(now)     ∈ {1, 2}   → tháng TRƯỚC  ; còn lại → tháng hiện tại
   LIFETIME: không áp dụng
```

Lý do: view phát sinh Chủ nhật được crawl/chốt trong T2–T3, nên tuần cũ chưa xong trước thứ Tư.

**Bắt buộc:** tầng service **không được gọi thẳng** `util.TimeStartOfWeekInHCM(now)` nữa (`backend/pkg/public/service/event.go`, hàm `getLeaderBoardWeekly`) — phải bọc qua hàm kỳ-hiển-thị, nếu không R4 không có hiệu lực.

### 3.2 Sửa PR #99 trước khi merge

PRD FR-004 ghi: *"Cache key embeds period anchor (`week_2026-08-03`) … so Monday 00:00 auto-rotates key"*.
Với R4, key phải xoay lúc **00:00 thứ Tư**, không phải thứ Hai. Merge nguyên trạng rồi mới thêm ân hạn sẽ có **2 ngày phục vụ sai kỳ từ cache**.

Ghi chú trạng thái: `develop` hiện **chưa có** `GetKeyCacheListLeaderBoardEvent` trong `backend/internal/module/redis/key.go` → PR #99 chưa vào. Sửa bây giờ còn kịp, không phải hotfix.

### 3.3 Clamp theo vòng đời event — hai ca hỏng ngay trên landing

`EventRaw` có sẵn `StartAt` / `EndAt` (`backend/internal/model/mg/event.go:33-34`) nên clamp được:

| Ca | Nếu không chặn | Xử lý |
|---|---|---|
| Event khai giảng **đúng thứ Hai** | T2–T3 rơi vào tuần trước → bảng rỗng **và nhãn ghi ngày trước cả khi event tồn tại** | anchor không lùi trước kỳ chứa `StartAt` |
| Event **đã kết thúc** | qua T4 thành "tuần hiện tại" rỗng → landing để bảng trắng vĩnh viễn | freeze anchor ở kỳ chứa `EndAt` |

### 3.4 Response (thêm mới, đều `omitempty`)

```
period, periodStartAt, periodEndAt   // của kỳ ĐANG HIỂN THỊ — không phải kỳ hiện tại
isSettling: true                     // đang trong 2 ngày ân hạn
```

FR-003 của PRD #97 đã đúng hướng (server cấp mốc, FE chỉ format) — chỉ cần **đổi nguồn anchor** sang `displayAnchor`. Như vậy R3 được thoả mà FE không phải tự tính gì.

### 3.5 Hai hệ quả nghiệp vụ cần thống nhất trước khi bật cho campaign có giải

1. **T2–T3 creator đăng bài mà BXH không nhúc nhích** (view mới thuộc kỳ chưa hiển thị). Cần dòng phụ kiểu *"Tuần này bắt đầu lên bảng từ thứ Tư"*, nếu không sẽ thành ticket "BXH hỏng".
2. **Số tuần cũ vẫn còn chạy trong T2–T3** — đó chính là lý do có ân hạn. Nên **thứ hạng chỉ chốt được từ thứ Tư**; partner trao giải tuần phải trao từ T4, không phải T2.

---

## 4. Pin — port từ creator-os, chi phí frontend bằng 0 (R5)

creator-os merge pin **ở tầng service** rồi mới trả mảng (`mergePinnedRanked`), **shape response không đổi** → 17 app FE không phải sửa dòng nào. Chỉ `admin/` (1 app) cần ô ghim.

### 4.1 Mang theo

| Thuộc tính | Vì sao |
|---|---|
| `pinRank` (0 = đầu), upsert theo `(board, subject)` | ghim lại không đẻ bản ghi trùng |
| `expiresAt` → tự loại khi serve | **quan trọng nhất với BXH tuần** — ghim cho tuần X phải tự rụng, không thành pin zombie |
| `reason` + `pinnedBy` + audit | ghim ảnh hưởng thứ hạng và giải thưởng (creator-os FR-AUD-022) |
| dedup rồi **mới** cắt `size` | pin không lòi ra lần hai, và không ăn mất chỗ |
| `source: pinned\|ranked` | thêm `omitempty`, FE dùng sau |

### 4.2 Phải quyết khác creator-os

creator-os trả `value = null` khi pin không có trong ranked. Ở ambassador FE render thẳng `statistic` → sẽ ra **0 view / 0đ** cạnh tên creator được ghim, rất tệ trên landing.

→ **Đề xuất:** ghim vẫn lấy số thật của creator trong kỳ, nhưng **chỉ cho ghim creator có phát sinh trong kỳ** — chặn ở admin lúc ghim, không chặn lúc serve.

### 4.3 KHÔNG port

- `subjectType = CONTENT` và `eligibility` — ambassador đã có pin content riêng qua `content.order` (`backend/pkg/admin/service/content.go:126`).
- Cách dựng SQL của creator-os: `eligibility.contentStatus` nội suy thẳng vào `$queryRawUnsafe` chỉ với `.replace(/'/g,'')` (`leaderboard.service.ts:270`), và `METRIC_COL.FOLLOWERS = 'followers'` trỏ vào cột **không tồn tại** trong `metrics_snapshots` (`leaderboard.service.ts:24`) → def `CONTENT` + `FOLLOWERS` lỗi runtime, không có guard. Hai lỗi này đừng bê sang.

---

## 5. Cấu hình ba tầng — hợp nhất PR #97 với PRD 04-02

| Tầng | Chứa | Ai sửa |
|---|---|---|
| `partner.options.leaderboard` | mặc định partner: `period, rankBy, metrics, valueBasis, size, graceDays` | admin partner |
| `event.options.leaderboard` | ghi đè cho một event | ops |
| hardcode | `LIFETIME / VIEWS / [VIEWS, CASH] / COMPLETED / 2` | — |

Giữ được cả hai: quyết định "config theo Partner" của PRD 04-02 thành **tầng mặc định**, còn `leaderboardPeriod` cấp event của PR #97 thành **tầng ghi đè**. Backward-compatible: trống = LIFETIME = hành vi hiện tại.

> **Đề nghị sửa PR #97 trước khi lên release:** đổi field phẳng `LeaderboardPeriod string` trên `EventOpts`
> (`backend/internal/model/mg/event.go:95`) thành **struct `Leaderboard{}`**. Thêm `rankBy` / `metrics` / `graceDays`
> sau này khỏi migrate lần hai. Đây là thay đổi rẻ nhất trong toàn bộ tài liệu này và là thứ duy nhất **gấp**.

Hai cờ `ShowLeaderboard` / `ShowLeaderboardAmount` hiện có (`backend/internal/model/mg/partner.go:34-35`) giữ nguyên, đọc như lớp phủ lên `metrics` để không phá FE đang chạy.

---

## 6. Lộ trình theo chi phí frontend (R6)

Vì 17 app fork, mọi thứ mới phải theo ba luật:

1. **Không đổi shape `UserEventResponse`** — chỉ thêm field `omitempty`. PR #97 đã đúng, giữ kỷ luật đó.
2. **Không thêm endpoint mới cho tính năng cũ** — thêm BXH = thêm *giá trị* trong config, không phải URL mới. Thêm URL = 17 lần wiring service + model + component.
3. **Mặc định trống = hành vi hiện tại**, để deploy BE không cần đụng FE nào.

| Pha | Nội dung | FE phải sửa |
|---|---|---|
| **1** | PR #97 + #99 về release (anchor + cache key theo T4) · MONTH · struct `Leaderboard{}` ba tầng · `rankBy` / `valueBasis` · **pin (BE + admin)** · clamp start/end · gộp các lỗi §7 | **0 / 17** |
| **2** | Nhãn kỳ + `isSettling` + cột `metrics` động | 17 app, 1–2 file/app, cơ học |
| **3** | Nhiều BXH mỗi event (definition model của creator-os) | 17 app — chỉ khi có nhu cầu thật |

Pha 1 giao được **cả ba kỳ + pin + cấu hình per-partner mà không đụng một dòng FE nào**. Đề nghị dừng ở đó rồi đánh giá lại.

---

## 7. Lỗi và nợ phát hiện khi đối chiếu code — gom vào pha 1

| # | Vấn đề | Vị trí |
|---|---|---|
| 1 | PR #97 mới ở `develop`; `release` chưa có gì. PR #99 **chưa vào develop** (`key.go` không có `GetKeyCacheListLeaderBoardEvent`) → **chưa có gì chạy thật** | — |
| 2 | `all_time` sort theo `completed`, `week` sort theo `completed+pending` — cùng bảng, hai nghĩa | `backend/pkg/public/handler/event.go:318` |
| 3 | `GetListUserNewest` chỉ cộng view **YouTube + TikTok**, bỏ Facebook×3 / Instagram×2 / Threads / YoutubeShort / ShopeeVideo → creator chạy Facebook, Threads hiện `TotalView = 0` ngay trên landing | `backend/pkg/public/service/event.go:73` |
| 4 | `GetListUserNewest` N+1 (20 `FindOne` trong goroutine). PR #99 đã gộp `$in` cho leaderboard nhưng **bỏ sót hàm này — cùng một trang landing** | `backend/pkg/public/service/event.go:63-68` |
| 5 | Nhánh `week` nuốt `SortInterface` do handler truyền → thêm BXH theo tiền phải sửa pipeline. `rankBy` giải được | pipeline |
| 6 | Bảng daily không có view/cash theo nền tảng → `metrics` per-platform bất khả ở WEEK/MONTH (xem §2.4) | `backend/internal/model/mg/event_analytic_daily.go:50-55` |
| 7 | `/missions/leaderboard-by-point` hardcode `wildRift.*` trên `User` — BXH **thứ ba** trong hệ thống, partner-scoped nhưng không tái dùng được cho partner khác | `backend/pkg/public/service/mission.go:597-614` |

Ghi chú xác minh phía FE: cả 14 app (frontend, anker, tpbank, mbbank, lusso, vng, vnpay, vpbank, yody, hdbank, wildrift, turborg, flamingo, parasola) đều gọi `/events/:id/leaderboards` + `/events/user-newest`; riêng wildrift gọi thêm `leaderboard-by-point`. Cổng hiển thị nằm ở `parasola/src/pages/home/components/not-logged-in/index.tsx:562` (`partnerDetail?.showLeaderboard !== false`).

---

## 8. Câu hỏi còn mở

**Q1 — BXH trên landing home của partner: xuyên event hay chỉ event đang chạy?**
Hiện FE truyền `event id` → là bảng của một event. Nếu muốn "top creator toàn partner":

- WEEK / MONTH **rẻ** — `user_event_analytic_daily` đã có field `partner` (`backend/internal/model/mg/user_event_analytic_daily.go:20`), chỉ thiếu index `{partner, date}`.
- LIFETIME theo partner **chưa có nguồn** — `user_event` khoá theo event, phải gom nhiều event hoặc dựng bảng luỹ kế theo partner.

Việc này lớn hơn cả pha 1 cộng lại nên tách riêng, **chưa đưa vào lộ trình trên**.

**Q2 — Hai đề xuất §7 của PRD #97 (empty state thứ Hai; tuần lịch vs 7 ngày trượt) vẫn chưa duyệt.**
Với luật ân hạn T4, đề xuất 1 (*empty state thứ Hai*) **gần như không còn xảy ra** — T2/T3 hiển thị tuần cũ đã có dữ liệu. Đề nghị chốt lại theo hướng đó thay vì giữ nguyên câu hỏi cũ.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-08-06 | Vinh Nguyen | Review PR #97/#99, đối chiếu creator-os + PRD partner-config 04-02; bổ sung R1–R6; đề xuất contract, quy tắc kỳ hiển thị, port pin, lộ trình 3 pha |
