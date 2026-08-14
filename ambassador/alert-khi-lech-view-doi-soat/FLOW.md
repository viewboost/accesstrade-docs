# Luồng kiểm tra của job cảnh báo bất thường dữ liệu view

**Ngày:** 2026-08-14
**Nhánh:** `feature/alert` · PR #136 → `develop` · 23 commit · 169 test xanh
**Mã nguồn:** `backend/pkg/admin/service/view_anomaly_*.go`, `backend/pkg/admin/schedule/init.go`
**Liên quan:** [PRD](2026-08-13-view-anomaly-alert-prd.md) · [Tech spec](2026-08-13-view-anomaly-alert-tech-spec.md) · [Việc còn treo](2026-08-13-view-anomaly-alert-followups.md) · [Danh mục 36 case](case.md)

---

## Mục lục

1. [Nguyên tắc chi phối toàn bộ thiết kế](#1-nguyên-tắc-chi-phối-toàn-bộ-thiết-kế)
2. [Điểm vào và khoá chống chạy chồng](#2-điểm-vào-và-khoá-chống-chạy-chồng)
3. [Cửa sổ thời gian](#3-cửa-sổ-thời-gian)
4. [Luồng tổng thể của job](#4-luồng-tổng-thể-của-job)
5. [Tầng scanner — nạp dữ liệu và cổng lỗi](#5-tầng-scanner--nạp-dữ-liệu-và-cổng-lỗi)
6. [Cổng loại trừ nhóm D](#6-cổng-loại-trừ-nhóm-d)
7. [Bảy detector](#7-bảy-detector)
8. [Gom báo cáo](#8-gom-báo-cáo)
9. [Vân tay và khoảng lặng](#9-vân-tay-và-khoảng-lặng)
10. [Gửi email](#10-gửi-email)
11. [Lịch sử chạy job](#11-lịch-sử-chạy-job)
12. [API sandbox](#12-api-sandbox)
13. [Cấu hình](#13-cấu-hình)
14. [Collection đọc và ghi](#14-collection-đọc-và-ghi)
15. [Điểm mù đã biết](#15-điểm-mù-đã-biết)

---

## 1. Nguyên tắc chi phối toàn bộ thiết kế

Ba nguyên tắc dưới đây quyết định hình dạng của mọi luồng trong tài liệu này. Đọc chúng trước, các quyết định phía sau sẽ tự giải thích.

**Bỏ sót thì chấp nhận được, bịa ra thì không.**
Phần lớn chênh lệch giữa view và thưởng là **đúng thiết kế** — nhiệm vụ tắt, hết budget, chạm cap, ngoài hiệu lực, content chưa duyệt. Một alert bắn vào những trường hợp đó sẽ bị Ops tắt trong vòng một tuần, và sau đó nó không bắt được gì, kể cả case thật. Vì vậy mọi nhánh mơ hồ đều chọn phía **im lặng**.

**Truy vấn hỏng không bao giờ được đọc thành "không có dữ liệu".**
Detector coi sự vắng mặt là bằng chứng. Nếu `RewardsFor` lỗi và trả map rỗng, `reward_missing` sẽ bắn vào **mọi** content-ngày vốn dĩ có thưởng. Một sự cố hạ tầng biến thành một trận lũ cảnh báo sai.

**Job chỉ đọc dữ liệu nghiệp vụ.**
Nó chỉ ghi vào hai collection của chính nó. Không sửa trạng thái content, không sinh thưởng bù, không đánh dấu bản ghi nào.

---

## 2. Điểm vào và khoá chống chạy chồng

Có hai đường vào cùng một thân job. Chúng chỉ khác nhau ở giá trị `triggeredBy` ghi vào lịch sử chạy.

```mermaid
flowchart TD
  CRON["cron 04:00 giờ HCM<br/>ScanViewAnomaly()"] --> BODY
  SBX["POST /api/admin/sandbox/view-anomaly/run<br/>TriggerViewAnomalyScan()<br/>chỉ môi trường develop"] --> BODY
  BODY["runViewAnomalyScan(triggeredBy)"]
  BODY --> G{"isRunViewAnomaly<br/>đang true?"}
  G -->|có| SKIP["log 'previous scan still running'<br/>return — KHÔNG tạo bản ghi lượt chạy"]
  G -->|không| SET["isRunViewAnomaly = true<br/>defer đặt lại false"]
  SET --> RUN["chạy thân job"]
```

**Khoá là biến package-level `isRunViewAnomaly`**, theo đúng pattern `isRunAnalyticDaily` đã có sẵn trong `shedule.go`. Job này đọc nặng hơn mọi job hiện có, chạy chồng là nhân đôi tải database.

**Hệ quả cần biết khi test:** nếu tester bấm API sandbox trong lúc cron đang chạy, lượt bấm đó **bị bỏ qua hoàn toàn** — không có bản ghi lượt chạy nào được tạo, chỉ có một dòng log. API vẫn trả `200` kèm `triggered: true`, nên tester không biết. Đây là hạn chế đã ghi nhận.

**Lịch 04:00 trùng khung với `AuditContentAnalytic`** (`0 0 4 * * *`). Job đó **ghi** `auditStatus` lên `content-analytic-daily`, job này **đọc** chính collection đó. Hai job không điều phối với nhau nên sẽ chạy song song và cộng dồn tải.

---

## 3. Cửa sổ thời gian

Đây là phần dễ sai nhất và ảnh hưởng tới mọi detector, nên tách riêng.

```mermaid
flowchart LR
  NOW["time.Now()"] --> TS["util.TimeStartOfDayInHCM(now)<br/>đúng thời điểm đầu ngày HCM<br/>nhưng GẮN NHÃN UTC"]
  TS --> REL[".In(util.TimeLocationHCM)<br/>gắn lại nhãn HCM<br/>CÙNG thời điểm"]
  REL --> TODAY["Today = 00:00 hôm nay giờ HCM"]
  TODAY --> LC["LastClosed = Today - 1 ngày<br/>ngày mới nhất được phép xét"]
  LC --> FROM["from = LastClosed - LookbackDays<br/>mặc định 7 ngày"]
```

### Vì sao `LastClosed` là hôm qua

Dữ liệu của ngày đang chạy **chưa đầy đủ theo định nghĩa**. Mọi alert dựa trên nó đều là báo động giả. Không có ngoại lệ nào cho quy tắc này.

### Vì sao phải gắn lại nhãn múi giờ

`util.TimeStartOfDayInHCM` tính đúng thời điểm đầu ngày HCM rồi gọi `.UTC()` ở cuối, nên giá trị trả về mang **nhãn UTC**. Đọc `Hour()` sẽ ra 17 chứ không phải 0.

`.In(util.TimeLocationHCM)` chỉ **đổi cách hiển thị, không đổi thời điểm**. Nếu bỏ bước này, `Today`/`LastClosed` sẽ đọc sai khi log và khi định dạng ngày trong email.

### Hệ quả với `Format` — bẫy lệch một ngày

`content-analytic-daily.date` được ghi bằng chính `TimeStartOfDayInHCM`, tức là mang nhãn UTC của thời điểm `17:00Z hôm trước`. Nếu format thẳng giá trị đó sẽ ra **lùi một ngày**.

Vì vậy cả `Finding.dateKey()` (dùng trong vân tay) lẫn `formatAnomalyDate()` (dùng trong email) đều gọi `.In(util.TimeLocationHCM)` trước khi format. Không có bước này thì:
- một email mang **hai quy ước ngày lệch nhau một ngày**;
- vân tay lưu **sai ngày vĩnh viễn** trong database.

### Bảng cửa sổ theo từng tầng

| Nơi dùng | Cửa sổ | Ghi chú |
|---|---|---|
| `AnalyticsFor` | `date >= from, <= LastClosed` | 7 ngày |
| `RewardsFor` | `date >= from, <= LastClosed` | 7 ngày |
| `CallbacksFor` | `createdAt >= now - 30 ngày` | hằng cứng `callbackLookbackDays` |
| `RewardedViewByUser` | **không lọc ngày** | luỹ kế cả chiến dịch |
| `MilestoneRewardedUsers` | **không lọc ngày** | luỹ kế cả chiến dịch |
| `reward_missing` | bỏ ngày > `LastClosed - 24h` | thực tế chỉ xét tới D−2 |
| `reward_lag` | cùng cutoff D−2 | |
| `view_duplicated` | bỏ ngày > `LastClosed` | |
| `vendor_outage` | `LastClosed - VendorWindowHours` (24h) | |
| `crawl_not_queued` | `Today - CrawlSilentDays` (3 ngày) | neo vào `Today`, không phải `LastClosed` |
| `callback_empty` | không theo ngày | đếm chuỗi N callback mới nhất |
| `milestone_missing` | không theo ngày | luỹ kế |

**Hai query cấp user cố ý bỏ qua `from`/`to`.** Mốc thưởng là trạng thái luỹ kế cả chiến dịch. Lọc 7 ngày ở đó là đem tổng một tuần so với ngưỡng cả chiến dịch — không bao giờ chạm tới.

---

## 4. Luồng tổng thể của job

```mermaid
flowchart TD
  START["runs.Start()<br/>status = running<br/>ghi NGAY, không đợi kết thúc"]
  START --> CFG["loadAlertConfig()<br/>đọc common-configs<br/>lỗi hoặc thiếu ⇒ dùng mặc định"]
  CFG --> SCAN["runScan()<br/>xem mục 5"]
  SCAN --> RAW["findings thô"]
  RAW --> FP["tính fingerprint cho từng finding"]
  FP --> SEEN["state.LastSeen(fingerprints)<br/>lỗi ⇒ coi như map rỗng, vẫn chạy tiếp"]
  SEEN --> FILT["filterSuppressed()<br/>trả về (kept, blocked, suppressed)"]
  FILT --> BUMP["state.BumpHit(blocked)<br/>CHỈ tập bị chặn"]
  BUMP --> COLL["collectFindings(kept)<br/>xem mục 8"]
  COLL --> SUP["report.Suppressed = suppressed"]
  SUP --> EN{"isViewAnomalyAlertEnabled()"}
  EN -->|tắt| NOTIFY
  EN -->|bật| REC["state.Record(kept)<br/>ghi cooldown"]
  REC --> NOTIFY["notifyViewAnomalies()<br/>xem mục 10"]
  NOTIFY --> FIN["runs.Finish()<br/>thời lượng, số liệu, kết quả gửi mail"]
  PANIC["panic bất kỳ đâu"] -.-> REC2["recover()<br/>runs.Fail(lý do)"]
```

### Bốn điểm dễ hiểu sai

**`BumpHit` chỉ nhận tập bị chặn.**
Tập được báo đã được `Record` tăng `hitCount` bằng `$inc` trong cùng lượt quét. Truyền cả danh sách vào `BumpHit` sẽ **cộng đôi**. Đây từng là một lỗi thật, được vòng review cuối bắt.

**`Record` bị bỏ qua khi tắt gửi mail.**
Khi đang ở giai đoạn hiệu chỉnh ngưỡng, nếu vẫn ghi cooldown thì mọi phát hiện sẽ bị đánh dấu "đã báo". Tới lúc bật mail, hộp thư im lặng một cách khó hiểu.

**Khi bật, `Record` chạy TRƯỚC khi gửi và không phụ thuộc kết quả gửi.**
Đánh đổi có chủ ý: phát hiện sẽ không bắn lại ở lần quét kế tiếp dù admin chưa nhận được email. Phương án ngược lại — chỉ ghi khi gửi thành công — khiến một sự cố mail kéo dài tích tụ thành một email khổng lồ khi mail hồi phục.

**`recover` phải đóng lượt chạy ở trạng thái `failed`.**
Nếu không, bản ghi nằm mãi ở `running` và không phân biệt được với một lượt đang chạy thật.

---

## 5. Tầng scanner — nạp dữ liệu và cổng lỗi

```mermaid
flowchart TD
  A["ActiveEvents()<br/>status=active, startAt<=now, endAt>now"]
  A -->|lỗi| AX["log, trả về rỗng"]
  A -->|ok| LOOP["với mỗi event"]

  LOOP --> E1["SchemasOf(event)"]
  E1 -->|lỗi| SKIPE["log kèm event.ID<br/>BỎ QUA CẢ EVENT"]
  E1 -->|ok| E2["MissionsOf(event)"]
  E2 -->|lỗi| SKIPE
  E2 -->|ok| E3["RewardedViewByUser(event)<br/>luỹ kế cả chiến dịch"]
  E3 -->|lỗi| SKIPE
  E3 -->|ok| E4["MilestoneRewardedUsers(event)<br/>luỹ kế cả chiến dịch"]
  E4 -->|lỗi| SKIPE
  E4 -->|ok| PAGE

  PAGE["ContentsPage()<br/>event + status=approved<br/>_id > lastID, sort _id, limit 200"]
  PAGE -->|lỗi| BRK["log, break vòng phân trang"]
  PAGE -->|rỗng| DONE["xong event này"]
  PAGE -->|có dòng| B1["AnalyticsFor(ids)"]

  B1 -->|lỗi| SKIPB["log<br/>ĐẨY CON TRỎ<br/>bỏ qua lô này VÀ bộ đếm vendor của nó"]
  B1 -->|ok| B2["RewardsFor(ids)"]
  B2 -->|lỗi| SKIPB
  B2 -->|ok| B3["CallbacksFor(ids)"]
  B3 -->|lỗi| SKIPB
  B3 -->|ok| SCOPE["dựng Scope"]

  SCOPE --> RUN["runDetectors(scope, cfg, detectors)<br/>6 detector theo lô"]
  RUN --> TALLY["accumulateVendorStall()"]
  TALLY --> ADV["lastID = content cuối"]
  ADV --> PAGE
  SKIPB --> PAGE

  DONE --> NEXT["event tiếp theo"]
  NEXT --> VEND["sau TẤT CẢ event:<br/>detectVendorOutage() MỘT LẦN<br/>trên bộ đếm toàn cục"]
```

### Mọi nhánh `continue` đều phải đẩy con trỏ

Nếu một nhánh bỏ qua lô mà không gán lại `lastID`, vòng lặp sẽ quay **vô tận** vào database. Đây là điều duy nhất trong tầng này có thể làm sập production, và nó được kiểm chứng bằng test riêng.

### Cô lập lỗi ở tầng detector

```mermaid
flowchart LR
  R["runDetectors"] --> S["sắp tên detector<br/>để log và kết quả ổn định"]
  S --> L["với mỗi kind"]
  L --> EN{"cfg.Enabled[kind]"}
  EN -->|false| NEXT["bỏ qua"]
  EN -->|true| FN["chạy trong closure<br/>có defer recover()"]
  FN -->|panic| LOG["log kèm tên detector<br/>MẤT kết quả của riêng nó"]
  FN -->|ok| APP["gộp findings"]
  LOG --> NEXT
  APP --> NEXT
```

`runDetectors` nhận **registry làm tham số** chứ không đọc thẳng biến package `detectors`. Lý do: test cần thay một detector bằng hàm panic, và một test đổi trạng thái package sẽ rò rỉ sang test khác khi chạy song song. Bên gọi thật luôn truyền `detectors`.

### `vendor_outage` là ngoại lệ có chủ ý

Sáu detector còn lại chạy **mỗi lô một lần**. `vendor_outage` cần dữ liệu vượt phạm vi một lô **và** vượt phạm vi một event, nên scanner tích luỹ bộ đếm `map[source]*vendorStallCount` xuyên suốt lần quét, rồi gọi detector đó **đúng một lần** sau khi mọi event đã quét xong.

### Hai bất biến scanner phải bảo đảm

| Bất biến | Ai phụ thuộc | Hậu quả nếu sai |
|---|---|---|
| `AnalyticsFor` trả chuỗi **sắp theo ngày tăng dần** | `detectViewDuplicated` | cửa sổ trượt tính trung vị sai hoàn toàn |
| `CallbacksFor` trả **mới nhất trước**, rồi mới cắt còn 5 | `detectCallbackEmpty` | đếm chuỗi rỗng từ đầu sai đầu |

### Hai hạn chế đã chấp nhận

**`MissionsOf` nạp toàn bộ mission** vì `MissionRaw` không có trường tham chiếu event. Nếu mô hình dữ liệu về sau có liên kết đó thì sửa đúng chỗ này.

**`CallbacksFor` chạy thêm một truy vấn** đọc lại `contents` để lấy `link`, vì `contents-callback` khoá theo link chứ không theo mã content. Bỏ trống và để hai detector tầng crawl tự nạp sẽ làm chúng mất tính thuần — phương án tệ hơn.

---

## 6. Cổng loại trừ nhóm D

`shouldExpectReward` trả lời một câu duy nhất: **content này, ngày này, có được kỳ vọng sinh bản ghi thưởng không?**

Hai detector gate trên nó: `reward_missing` và `reward_lag`. Đây là module quan trọng nhất của cả tính năng.

```mermaid
flowchart TD
  IN["event, schemas, mission, content, date"] --> N{"event nil<br/>hoặc content nil"}
  N -->|có| X0["condition_not_met"]
  N -->|không| B1{"mission nil<br/>hoặc type ≠ content-with-crawl"}
  B1 -->|có| X1["mission_not_by_view · D5"]
  B1 -->|không| B2{"content.Status"}
  B2 -->|rejected| X2a["content_rejected · D7"]
  B2 -->|khác approved| X2b["content_not_approved · D8"]
  B2 -->|approved| B3{"event.EndAt trước date"}
  B3 -->|có| X3["event_ended · D6"]
  B3 -->|không| B4{"mission.Status ≠ active"}
  B4 -->|có| X4["mission_inactive · D1"]
  B4 -->|không| B5{"date ngoài<br/>[mission.StartAt, EndAt]"}
  B5 -->|có| X5["out_of_mission_window · D4/E5"]
  B5 -->|không| B6{"content.ApprovedAt ngoài<br/>[mission.StartAt, EndAt]"}
  B6 -->|có| X6["approved_out_of_range · D4"]
  B6 -->|không| B7{"Bpe ≠ nil VÀ<br/>Total > 0 VÀ Remain <= 0"}
  B7 -->|có| X7["budget_exhausted · D2"]
  B7 -->|không| B8{"CÓ BẤT KỲ schema nào<br/>Quantity đã cạn"}
  B8 -->|có| X8["cap_reached · D3"]
  B8 -->|không| B9{"content.Source không nằm trong<br/>mission.ApplyForSources"}
  B9 -->|có| X9["condition_not_met · D9"]
  B9 -->|không| OK["expect = true<br/>reason rỗng"]
```

### Thứ tự là load-bearing

Nhánh trước **che** nhánh sau và đổi luôn lý do được báo. Ví dụ: nếu ngày đang xét nằm ngoài cửa sổ nhiệm vụ **và** ngày duyệt cũng ngoài cửa sổ, hàm sẽ báo `out_of_mission_window` chứ không phải `approved_out_of_range`, vì nhánh 5 đứng trước nhánh 6.

### Vì sao trả về lý do chứ không chỉ `bool`

Khi Ops nghi hệ thống bỏ sót, một dòng log ghi `"content X excluded: budget_exhausted"` là **bằng chứng kiểm chứng được**. Thiếu nó, module này là hộp đen không ai tin.

### Ba nhánh có chi tiết cần nhớ

**`Bpe == nil` KHÔNG phải là hết budget.**
Nhiều event không cấu hình budget. Hiểu nhầm sẽ loại trừ sai **toàn bộ** chúng, tức là `reward_missing` im lặng vĩnh viễn trên những event đó.

**Cap loại trừ khi CÓ BẤT KỲ schema nào cạn.**
Một event có thể mang nhiều `EventSchemaRaw` với `Quantity` khác nhau, và **không schema nào tham chiếu mission**. Không có cách nào biết schema nào chi phối content này. Nhận cả danh sách và loại trừ khi bất kỳ cái nào đã cạn — hướng bảo thủ, chấp nhận bỏ sót để không báo động giả.

**Hàm chịu được con trỏ nil ở mọi tham số.**
Nó chạy trong vòng lặp quét hàng chục nghìn content; một bản ghi dữ liệu cũ thiếu tham chiếu không được làm chết cả lần quét.

---

## 7. Bảy detector

Mọi detector đều là **hàm thuần**: không I/O, không `time.Now()`, nhận dữ liệu đã nạp sẵn qua `Scope`, trả `[]Finding` rỗng-không-nil khi không có gì.

### 7.1 `reward_missing` — case C1, mức cao

Có view trong dữ liệu ngày nhưng không sinh bản ghi thưởng tương ứng. Đây là case Nha khoa Parkway.

```mermaid
flowchart TD
  S["mỗi content × mỗi ngày<br/>trong Analytics"] --> V{"View.Value > 0"}
  V -->|không| Q1["im lặng"]
  V -->|có| C{"date > LastClosed - RewardLagCycleHours"}
  C -->|có| Q2["im lặng<br/>chưa đóng hoặc còn trong chu kỳ"]
  C -->|không| G{"shouldExpectReward"}
  G -->|bị loại trừ| Q3["im lặng"]
  G -->|kỳ vọng| R{"hasRewardOnDate<br/>so theo chuỗi yyyy-mm-dd"}
  R -->|có| Q4["im lặng"]
  R -->|không| F["BẮN<br/>Expected = view của ngày<br/>Actual = 0"]
```

`hasRewardOnDate` so **theo ngày** chứ không theo thời điểm, vì reward và analytic-daily đều chốt theo mốc ngày và có thể lệch nhau vài giờ trong cùng một ngày.

### 7.2 `milestone_missing` — case E4, mức trung bình

Creator đã vượt ngưỡng mốc nhưng không có bản ghi thưởng mốc.

```mermaid
flowchart TD
  S["event"] --> M["milestoneSchemas()<br/>schema có Milestone.NumberOfView > 0"]
  M --> C0{"số lượng"}
  C0 -->|0| Q0["im lặng"]
  C0 -->|"> 1"| Q1["im lặng + log<br/>không biết mốc nào áp cho content nào"]
  C0 -->|đúng 1| W{"schema.Status = active VÀ<br/>LastClosed trong [StartAt, EndAt]"}
  W -->|không| Q2["im lặng · case E5"]
  W -->|có| U["mỗi content, mỗi user một lần"]
  U --> T{"RewardedViewByUser[user]<br/>>= Milestone.NumberOfView"}
  T -->|không| Q3["im lặng"]
  T -->|có| P{"MilestoneRewardedUsers[user]"}
  P -->|đã thưởng| Q4["im lặng"]
  P -->|chưa| G{"shouldExpectReward"}
  G -->|bị loại trừ| Q5["im lặng"]
  G -->|kỳ vọng| F["BẮN<br/>Expected = ngưỡng mốc<br/>Actual = view được tính thưởng"]
```

**Then chốt — dùng đúng loại chỉ số.**
Ngưỡng xét trên `RewardedViewByUser`, nguồn là `TotalViewPendingRewarded` của pipeline `GetTotalCashRewardByContent`. **Không phải** `content.Statistic.View.Total`.

Đây chính xác là case Phở Cung Đình: view hiển thị và view được tính thưởng là hai con số khác nhau một cách hợp lệ. So nhầm sẽ tạo báo động giả hàng loạt.

**Vì sao tra `MilestoneRewardedUsers` theo user chứ không theo content.**
Thưởng mốc được tạo với `Options: &EventRewardOpts{}` — **rỗng, không mang ContentID** (xem `internal/service/event_schema.go`). Mà `scope.Rewards` khoá theo `Options.ContentID`. Tra theo content sẽ **luôn** cho kết quả "chưa thưởng" và làm detector bắn vào mọi user vượt mốc. Đây là lỗi đã bị vòng review bắt và sửa.

**Vì sao không gọi `schema.IsValid()`.**
`IsValid()` đọc đồng hồ hệ thống, làm detector mất tính tất định và không test được. Thay bằng so trực tiếp với `scope.LastClosed`.

### 7.3 `reward_lag` — case C4/E3, mức trung bình

Cả một nhiệm vụ có view nhưng không quy đổi thành thưởng quá một chu kỳ.

```mermaid
flowchart TD
  S["mỗi content trong nhiệm vụ"] --> D["mỗi ngày trong Analytics"]
  D --> C{"date > cutoff<br/>(LastClosed - 24h)"}
  C -->|có| SK["không cộng vào tổng"]
  C -->|không| G{"shouldExpectReward"}
  G -->|bị loại trừ| SK
  G -->|kỳ vọng| MARK["đánh dấu ngày này là 'kỳ vọng'<br/>viewTotal += View.Value"]
  MARK --> R["mỗi reward của content"]
  R --> RC{"reward.Date > cutoff<br/>hoặc ngày không nằm trong tập kỳ vọng"}
  RC -->|có| SKR["không cộng"]
  RC -->|không| ACC["rewardedTotal += Statistic.TotalView"]
  ACC --> SUM["tổng theo NHIỆM VỤ"]
  SUM --> Z{"viewTotal > 0"}
  Z -->|không| Q1["im lặng"]
  Z -->|có| TOL{"rewardedTotal >=<br/>viewTotal × RewardLagTolerance (0.9)"}
  TOL -->|có| Q2["im lặng<br/>nằm trong dung sai"]
  TOL -->|không| F["BẮN<br/>một finding cho mỗi nhiệm vụ"]
```

**Hai vế phải cùng tập ngày.**
Nếu chỉ gate vế view mà không gate vế reward, tử số và mẫu số đến từ hai tập ngày khác nhau và alert bắn oan. Vì vậy code dựng một `map[string]bool` các ngày kỳ vọng, rồi chỉ cộng reward của những ngày nằm trong tập đó.

**Vì sao có dung sai thay vì so tuyệt đối.**
Reward và analytic chốt lệch nhau vài giờ, làm tròn và trễ một phần là bình thường. Đòi `rewarded >= view` là đòi hai nguồn số liệu khớp tuyệt đối — điều không bao giờ xảy ra, và sẽ bắn alert mỗi ngày.

**Vì sao vẫn phải qua `shouldExpectReward`.**
Bản đầu tiên của detector này cố ý bỏ cổng loại trừ. Vòng review cuối chỉ ra: một nhiệm vụ đã kết thúc ba ngày trước với 500 view ghi nhận sẽ cho `viewTotal=500, rewardedTotal=0` và bắn alert **mỗi ngày, mãi mãi**. Đã sửa.

### 7.4 `view_duplicated` — case B2, mức cao

View của một ngày nhảy vọt bất thường so với chính content đó.

```mermaid
flowchart TD
  S["chuỗi Analytics của content"] --> L{"độ dài >= 4<br/>(minSeriesForMedian)"}
  L -->|không| Q1["im lặng"]
  L -->|có| I["duyệt từ chỉ số 3 trở đi"]
  I --> D{"day.Date > LastClosed"}
  D -->|có| Q2["im lặng"]
  D -->|không| MIN{"View.Value >= DuplicateMinView<br/>(1000)"}
  MIN -->|không| Q3["im lặng<br/>dưới sàn view"]
  MIN -->|có| BASE["trung vị tối đa 7 ngày liền trước<br/>series[i-7 : i]"]
  BASE --> B0{"trung vị > 0"}
  B0 -->|không| Q4["im lặng"]
  B0 -->|có| R{"View.Value >=<br/>trung vị × DuplicateFactor (1.8)"}
  R -->|không| Q5["im lặng"]
  R -->|có| F["BẮN<br/>Expected = trung vị<br/>Actual = view của ngày"]
```

**Dùng trung vị, không dùng trung bình.**
Một ngày đã nhảy vọt sẽ kéo trung bình lên và **tự che chính nó**. Đây là bất biến có test riêng, được kiểm chứng bằng cách đổi sang trung bình và xác nhận test đỏ.

**Hạn chế đã biết, ghi thẳng trong comment của hàm.**
Detector này **không phân biệt được** content đang lên xu hướng với đếm trùng — tăng gấp đôi view trong một ngày là chuyện hoàn toàn bình thường với content viral. Nó là tín hiệu để người xem, không phải kết luận. Đây là detector nhiều khả năng phải hiệu chỉnh ngưỡng nhất và là **ứng viên số một để tắt riêng** nếu nhiễu.

### 7.5 `vendor_outage` — case A6, mức cao, dạng cụm

Nhiều content của nhiều user khác nhau, cùng nền tảng, cùng đứng view.

```mermaid
flowchart TD
  subgraph TALLY["accumulateVendorStall — chạy mỗi lô"]
    S["mỗi content"] --> SRC{"Source rỗng"}
    SRC -->|có| SK0["không đếm"]
    SRC -->|không| AB{"TotalNotFound >= 3"}
    AB -->|có| SK1["không đếm<br/>hệ thống đã bỏ crawl, ĐÚNG THIẾT KẾ"]
    AB -->|không| HR{"có bản ghi analytic nào<br/>trong cửa sổ VendorWindowHours"}
    HR -->|không| SK2["không đếm<br/>chưa bao giờ được crawl"]
    HR -->|có| MV{"có ngày nào View.Value > 0"}
    MV -->|có| SK3["không đếm — vẫn chạy bình thường"]
    MV -->|không| CNT["đếm vào map[source]<br/>Contents++, Users[user]"]
  end
  CNT --> G["bộ đếm toàn cục<br/>xuyên suốt mọi lô, mọi event"]
  G --> ONE["detectVendorOutage — chạy MỘT LẦN ở cuối"]
  ONE --> C{"Contents >= 50 VÀ<br/>len(Users) >= 10"}
  C -->|không| Q["im lặng"]
  C -->|có| F["BẮN một finding cho cả cụm<br/>Content và User để Zero"]
```

**Yêu cầu vượt CẢ HAI ngưỡng cùng lúc.**
Đây là điều phân biệt với case A4 — token một kênh hết hạn cũng làm nhiều content đứng, nhưng tất cả thuộc **một** user. Nếu chỉ xét số content, alert này sẽ bắn nhầm vào A4.

**Hai điều kiện loại trừ do vòng review cuối bổ sung.**
Ban đầu bộ đếm coi "không có bản ghi analytic nào" là đứng view. Nhưng content **chưa bao giờ được crawl** cũng cho ra map rỗng. Trên một campaign đã chạy lâu, lượng content approved-nhưng-chưa-crawl thường xuyên vượt ngưỡng 50/10, nên `vendor_outage` sẽ bắn ngay ngày đầu và mỗi ngày sau đó. Đã thêm hai điều kiện: phải **có ít nhất một bản ghi** trong cửa sổ, và phải **chưa bị bỏ crawl**.

### 7.6 `callback_empty` — case A2, mức thấp

Hệ thống vẫn crawl đều nhưng callback trả về không mang dữ liệu view.

```mermaid
flowchart TD
  S["Callbacks của content<br/>đã sắp mới nhất trước"] --> N{"số lượng >= CallbackEmptyStreak (3)"}
  N -->|không| Q1["im lặng"]
  N -->|có| ST["đếm chuỗi rỗng liên tiếp<br/>TỪ ĐẦU MỚI NHẤT<br/>gặp cái không rỗng thì dừng"]
  ST --> B{"streak >= 3"}
  B -->|không| Q2["im lặng"]
  B -->|có| F["BẮN<br/>Expected = 3, Actual = streak"]
```

**Định nghĩa "rỗng"** (`isEmptyCallback`): `Information` rỗng, hoặc có `Information` nhưng **không có trường view nào** trong `view` / `views` / `playCount` / `play_count`.

Vòng review cuối đã truy: production chỉ ghi và đọc đúng khoá `view`. Ba khoá còn lại là dự phòng vô hại — chúng chỉ có thể làm hàm trả "không rỗng", tức là làm alert **im lặng hơn**, không thể gây báo động giả.

**Dấu hiệu phân biệt với case A1:** ở đây **vẫn có callback mới**. A1 thì không còn callback nào — đó là việc của `crawl_not_queued`.

### 7.7 `crawl_not_queued` — case A3, mức thấp

Content hợp lệ thuộc campaign đang chạy nhưng không có dấu vết crawl nào.

```mermaid
flowchart TD
  S["content"] --> A{"Status = approved"}
  A -->|không| Q1["im lặng"]
  A -->|có| M{"mission.Type =<br/>content-with-crawl"}
  M -->|không| Q2["im lặng<br/>nhiệm vụ không crawl thì không kỳ vọng callback"]
  M -->|có| AB{"TotalNotFound >= crawlNotFoundLimit (3)"}
  AB -->|có| Q3["im lặng<br/>case A1 — ngừng crawl có chủ đích, thuộc vòng 1"]
  AB -->|không| R{"có callback nào<br/>createdAt > Today - CrawlSilentDays (3)"}
  R -->|có| Q4["im lặng"]
  R -->|không| F["BẮN"]
```

**Nhánh `TotalNotFound >= 3` là bắt buộc.**
Không có nó, **mọi** content đã bị đánh dấu crawl-failed sẽ bắn vào đây mỗi ngày, vĩnh viễn. Bất biến này được kiểm chứng bằng cách xoá nhánh và xác nhận test đỏ.

**Detector này neo vào `Today`, không phải `LastClosed`**, vì nó hỏi "có dấu vết crawl gần đây không", chứ không phải "ngày đó có bất thường không".

---

## 8. Gom báo cáo

```mermaid
flowchart TD
  IN["findings đã qua cooldown"] --> K{"Kind có trong alertLabel"}
  K -->|không| DROP["bỏ — không để một nhóm<br/>không nhãn lọt vào email"]
  K -->|có| FP{"fingerprint đã thấy"}
  FP -->|có| DUP["bỏ — khử trùng"]
  FP -->|chưa| ADD["gom vào byKind[kind]"]
  ADD --> SORT["sắp trong nhóm theo fingerprint<br/>để kết quả ổn định giữa hai lần chạy"]
  SORT --> CAP{"total > MaxRowsPerKind (50)"}
  CAP -->|có| CUT["Rows = 50 đầu<br/>Omitted = total - 50"]
  CAP -->|không| ALL["Rows = tất cả<br/>Omitted = 0"]
  CUT --> ACC["Total += total (TRƯỚC khi cắt)<br/>TotalShown += len(Rows)"]
  ALL --> ACC
  ACC --> GS["sắp nhóm theo severityRank<br/>rồi theo tên kind"]
```

**Bất biến quan trọng nhất:** `Total` và `TotalFound` đếm **trước** khi cắt dòng, còn `TotalShown` và `len(Rows)` đếm **sau**. Khi có sự cố diện rộng, email chỉ hiển thị 50 dòng nhưng **con số thật phải sống sót** — đó mới là thứ nói cho admin biết mức độ nghiêm trọng.

Bất biến này được kiểm chứng bằng cách đổi `TotalFound += total` thành `TotalFound += len(rows)` và xác nhận test đỏ.

**Khử trùng chạy trước khi gom nhóm và đếm**, nên một finding trùng không thể thổi phồng `Total`.

---

## 9. Vân tay và khoảng lặng

Vân tay là **danh tính của một SỰ CỐ**, không phải của một lần phát hiện. Hai lần quét khác nhau thấy cùng một sự cố phải cho ra cùng một chuỗi.

```mermaid
flowchart LR
  F["Finding"] --> K{"Kind"}
  K -->|"reward_missing<br/>view_duplicated"| A["kind + content + date"]
  K -->|milestone_missing| B["kind + event + user + ngưỡng"]
  K -->|vendor_outage| C["kind + source"]
  K -->|reward_lag| D["kind + event + mission"]
  K -->|"callback_empty<br/>crawl_not_queued"| E["kind + content"]
  A --> J["join bằng dấu |"]
  B --> J
  C --> J
  D --> J
  E --> J
  J --> L["LastSeen tra trong<br/>view-anomaly-alerts"]
  L --> S{"now - notifiedAt<br/>< CooldownHours (72h)"}
  S -->|có| BL["blocked<br/>chỉ BumpHit"]
  S -->|không| KP["kept<br/>Record + vào email"]
```

### Cố ý loại trừ `Expected`, `Actual`, `Detail`

Số liệu của một sự cố đang diễn ra vẫn thay đổi mỗi ngày. Nếu chúng lọt vào vân tay thì cooldown **không bao giờ khớp** và alert bắn lại mỗi ngày — đúng thứ cơ chế này sinh ra để chặn.

### Bốn kind không có ngày trong vân tay

| Kind | Có ngày | Vì sao |
|---|---|---|
| `reward_missing` | có | mỗi ngày thiếu thưởng là một sự cố riêng |
| `view_duplicated` | có | cú nhảy vọt thuộc về đúng một ngày |
| `milestone_missing` | **không** | vượt mốc là chuyện xảy ra một lần |
| `vendor_outage` | **không** | sự cố vendor ba ngày là MỘT sự cố |
| `reward_lag` | **không** | job thưởng hỏng là trạng thái kéo dài |
| `callback_empty` | **không** | trạng thái kéo dài |
| `crawl_not_queued` | **không** | trạng thái kéo dài |

`vendor_outage` và `reward_lag` ban đầu **có** ngày trong vân tay. Vòng review cuối chỉ ra: cả hai đặt `Date = scope.LastClosed`, mà giá trị đó tiến một ngày sau mỗi lần quét, nên vân tay đổi mỗi ngày và cooldown không bao giờ chặn được. Một sự cố vendor ba ngày gửi ba email giống hệt nhau. Đã sửa.

### `dateKey()` chuẩn hoá múi giờ

Xem lại [mục 3](#3-cửa-sổ-thời-gian). Nếu bỏ bước `.In(util.TimeLocationHCM)`, vân tay lưu **sai ngày vĩnh viễn** trong database — và sửa sau sẽ làm vô hiệu toàn bộ cooldown đang có.

### `HitCount` tăng cả khi bị chặn

Một sự cố kéo dài vẫn phải để lại dấu vết đếm được trong suốt khoảng lặng, nếu không nó biến mất khỏi dữ liệu. Đây là thứ trả lời được câu "sự cố này tồn tại bao lâu rồi" — câu hỏi mà cảnh báo kỳ đối soát hiện không trả lời được.

---

## 10. Gửi email

```mermaid
flowchart TD
  R["report"] --> Z{"TotalFound == 0"}
  Z -->|có| Q1["return false<br/>không log gì — giữ log sạch"]
  Z -->|không| E{"VIEW_ANOMALY_ALERT_ENABLE"}
  E -->|tắt| Q2["log tổng số VÀ số theo TỪNG loại alert<br/>return false"]
  E -->|bật| P{"VIEW_ANOMALY_ALERT_RECIPIENTS<br/>sau normalizeRecipients"}
  P -->|rỗng| Q3["log, return false"]
  P -->|có| API["core.Client().SmsGatewayAction<br/>POST /v1.0/partner/email/send"]
  API -->|lỗi transport| Q4["log nội dung lỗi, return false"]
  API -->|HTTP 200| ST{"res['status'] == 'success'"}
  ST -->|không| Q5["log NGUYÊN VĂN response<br/>return false"]
  ST -->|có| OK["log, return true<br/>ghi vào lịch sử lượt chạy"]
```

### Bắt buộc đọc status trong thân phản hồi

API AccessTrade trả **HTTP 200 kèm trạng thái thật nằm trong payload**. Tin vào mã transport thôi sẽ dẫn tới việc ghi log "đã gửi thành công" trong khi email chưa hề đi.

### Nhánh tắt phải log số theo từng loại alert

Đó là **toàn bộ đầu vào** của việc hiệu chỉnh ngưỡng. Nếu chỉ log tổng, không ai biết alert nào đang ồn.

### Hàm không bao giờ trả lỗi và không bao giờ panic

Chữ ký trả `bool` (đã gửi được hay chưa), không trả `error`. Mọi nhánh hỏng đều log rồi thoát êm. Lỗi ở tầng gửi không được rò ra ngoài về luồng quét.

### Đường gửi

| | |
|---|---|
| Hàm | `core.Client().SmsGatewayAction` |
| Endpoint | `constants.EmailSendEndpoint` = `/v1.0/partner/email/send` |
| Base URL, khoá | nhóm env `ACCESS_TRADE_SMS_*` |
| Xác thực | HMAC — `client-id`, `client-trace-no`, `client-request-time`, `client-signature` |
| Template | `AMBASSADOR_EMAIL_VIEW_ANOMALY_ALERT` — **chưa được AccessTrade cấp** |

Đây đúng cùng một đường với email OTP và với cảnh báo lệch kỳ đối soát.

### Cấu trúc `template_data` có hai cấp

```
{
  scanned_at, total_found, total_shown, suppressed, company, year,
  groups: [
    { kind, kind_label, severity, total, omitted,
      rows: [ { content_id, user_id, event_id, source, date,
                expected, actual, affected_contents, affected_users, detail } ] }
  ]
}
```

**Cần xác nhận với AccessTrade:** template bên đó có hỗ trợ **vòng lặp lồng nhau** không. Nếu chỉ nhận biến phẳng thì phải dựng sẵn chuỗi HTML — thay đổi gói gọn trong `buildViewAnomalyTemplateData`.

---

## 11. Lịch sử chạy job

Collection `view-anomaly-job-runs`, một bản ghi cho mỗi lượt chạy.

```mermaid
flowchart LR
  A["runs.Start()"] --> ST["status = running<br/>date = LastClosed<br/>triggeredBy = cron | sandbox<br/>startedAt = now"]
  ST --> W["job chạy"]
  W -->|bình thường| B["runs.Finish()"]
  W -->|panic| C["runs.Fail()"]
  B --> BD["status = done<br/>durationMs<br/>totalFound / totalShown / suppressed<br/>countByKind<br/>emailEnabled / emailSent / recipients"]
  C --> CD["status = failed<br/>error = nguyên văn lý do"]
```

### Vì sao ghi ngay lúc bắt đầu

Một lượt chạy bị treo hoặc bị giết giữa chừng vẫn phải để lại dấu vết. Nếu chỉ ghi lúc kết thúc thì "không có bản ghi" vừa có nghĩa là **chưa chạy** vừa có nghĩa là **chạy rồi chết** — hai tình huống cần phân biệt.

### `emailEnabled` khác `emailSent`

- `emailEnabled` — trạng thái cờ env tại lúc chạy.
- `emailSent` — email có thực sự được AccessTrade tiếp nhận không.

Hai giá trị khác nhau khi cờ bật nhưng danh sách người nhận rỗng, hoặc khi API từ chối.

### `countByKind` là dữ liệu hiệu chỉnh ngưỡng

Đếm trên `Total` của nhóm (**trước** khi cắt dòng), vì số dòng hiển thị không nói lên mức độ ồn của một alert.

### Lỗi ghi lịch sử chỉ được bỏ qua

Lịch sử chạy là dữ liệu phụ trợ, không được phép chặn việc quét.

---

## 12. API sandbox

Chỉ tồn tại ở môi trường `develop`.

| Method | Đường dẫn | Việc |
|---|---|---|
| `POST` | `/api/admin/sandbox/view-anomaly/run` | kích hoạt quét, chạy nền, trả ngay |
| `GET` | `/api/admin/sandbox/view-anomaly/runs` | 20 lượt gần nhất, mới nhất trước |

```mermaid
flowchart TD
  REQ["request"] --> RT{"config.IsEnvDevelop()<br/>ở TẦNG ROUTER"}
  RT -->|false| NF["route không được đăng ký<br/>⇒ 404, không lộ ra là API tồn tại"]
  RT -->|true| AUTH["a.RequiredLogin"]
  AUTH --> HD{"config.IsEnvDevelop()<br/>ở TẦNG HANDLER"}
  HD -->|false| B400["400 — chặn lớp thứ hai"]
  HD -->|true| GO["go TriggerViewAnomalyScan()<br/>trả 200 ngay"]
```

**Kiểm tra hai lớp là có chủ ý.** Tầng router không đăng ký route nên trả 404 chứ không phải 403 — không lộ ra rằng API có tồn tại. Tầng handler kiểm tra lại để một sửa nhầm ở router không mở API này ra production.

**Hạn chế đã biết:** nếu khoá chống chạy chồng đang bật, lượt bấm bị bỏ qua nhưng API **vẫn trả `200` kèm `triggered: true`**. Tester không biết là lượt bấm đã bị nuốt.

---

## 13. Cấu hình

### Biến môi trường — quyết định triển khai

```
VIEW_ANOMALY_ALERT_ENABLE=false
VIEW_ANOMALY_ALERT_RECIPIENTS=          # phân tách bằng dấu phẩy
```

Hai biến này **chỉ quyết định có gửi email hay không**. Job luôn quét và luôn ghi log.

Người nhận đi qua `normalizeRecipients` (dùng chung với cảnh báo đối soát): cắt khoảng trắng, hạ chữ thường, bỏ chuỗi rỗng, khử trùng giữ thứ tự.

### `common-configs` — tham số hiệu chỉnh

Bản ghi `name = view_anomaly_alert`, trường `Value` là `map[string]string`.

| Khoá | Mặc định | Dùng ở đâu |
|---|---|---|
| `lookbackDays` | 7 | cửa sổ nạp analytic và reward |
| `cooldownHours` | 72 | khoảng lặng chống bắn lặp |
| `maxRowsPerKind` | 50 | số dòng tối đa mỗi nhóm trong email |
| `vendorWindowHours` | 24 | cửa sổ xét đứng view |
| `vendorMinContents` | 50 | ngưỡng cụm vendor |
| `vendorMinUsers` | 10 | ngưỡng cụm vendor |
| `duplicateFactor` | 1.8 | bội số so với trung vị |
| `duplicateMinView` | 1000 | sàn view tối thiểu |
| `rewardLagCycleHours` | 24 | chu kỳ tính thưởng |
| `rewardLagTolerance` | 0.9 | tỉ lệ quy đổi còn coi là bình thường |
| `callbackEmptyStreak` | 3 | số callback rỗng liên tiếp |
| `crawlSilentDays` | 3 | số ngày im lặng crawl |
| `enabled.<kind>` | true | bật tắt từng alert độc lập |

**Giá trị rác, rỗng hoặc âm đều rơi về mặc định.** Ngưỡng bằng 0 nghĩa là bắt tất cả mọi thứ — tệ hơn nhiều so với chạy bằng mặc định.

**Mọi giá trị mặc định đều suy ra từ tài liệu case, chưa đối chiếu với dữ liệu thật lần nào.** Chúng tồn tại để job chạy được, không phải để tin.

### Quy trình bật gửi mail

1. Giữ `ENABLE=false`, chạy ít nhất 7 ngày.
2. Đếm phát hiện theo từng alert mỗi ngày từ log tiền tố `[ScanViewAnomaly]` hoặc từ `countByKind` trong `view-anomaly-job-runs`.
3. Đối chiếu tay 10 phát hiện của `reward_missing` và `milestone_missing` — đây là bài kiểm tra chất lượng duy nhất của `shouldExpectReward`.
4. Hiệu chỉnh ngưỡng bằng cách sửa `common-configs`, **không sửa mã, không deploy lại**.
5. Điền `RECIPIENTS`, đặt `ENABLE=true`.

Ứng viên tắt riêng đầu tiên nếu nhiễu: `enabled.view_duplicated = false`.

---

## 14. Collection đọc và ghi

| Collection | Quyền | Dùng để |
|---|---|---|
| `view-anomaly-alerts` | **ghi** | fingerprint, notifiedAt, hitCount — điều khiển cooldown |
| `view-anomaly-job-runs` | **ghi** | lịch sử lượt chạy |
| `contents` | đọc | phân trang cursor theo event |
| `content-analytic-daily` | đọc | chuỗi view theo ngày, cửa sổ 7 ngày |
| `event-rewards` | đọc | reward theo ngày + 2 aggregate luỹ kế chiến dịch |
| `contents-callback` | đọc | phản hồi crawl theo link, chặn 30 ngày |
| `events` | đọc | event đang hiệu lực |
| `event-schemas` | đọc | cổng loại trừ, cấu hình mốc |
| `missions` | đọc | cổng loại trừ |
| `common-configs` | đọc | ngưỡng |

### Index đã thêm

| Collection | Index | Vì sao |
|---|---|---|
| `contents` | `{event, status, _id}` | `ContentsPage` lọc `{event, status}` rồi range `_id` và **sort `_id`**. Index cũ `{event, status}` không phục vụ sort → Mongo sort trong bộ nhớ, lặp lại ở **mỗi trang** |
| `contents-callback` | `{link, createdAt}` | collection này trước đó **chỉ có `{createdAt}`**, không có index nào trên `link` — mà `link` mới là vế chọn lọc |
| `view-anomaly-alerts` | `{fingerprint}`, `{-notifiedAt}`, `{kind, -notifiedAt}` | tra cooldown |
| `view-anomaly-job-runs` | `{-startedAt}`, `{date}`, `{status}` | đọc lịch sử |

**Lưu ý triển khai:** `i.process` tạo index lúc service khởi động. Trên `contents` và `contents-callback` cỡ production nên tạo tay trước ở khung thấp điểm:

```js
db.contents.createIndex({ event: 1, status: 1, _id: 1 }, { background: true })
db["contents-callback"].createIndex({ link: 1, createdAt: 1 }, { background: true })
```

### Index chưa thêm — đo trên production rồi quyết

| Collection | Index đề xuất | Truy vấn | Mức |
|---|---|---|---|
| `event-rewards` | `{options.contentId, date}` | `RewardsFor` — index hiện tại đơn trường, mỗi content kéo về toàn bộ reward từ trước tới nay rồi lọc ngày trong bộ nhớ | vừa |
| `event-rewards` | `{event, statistic.totalCashMilestone}` | `MilestoneRewardedUsers` — phải đọc mọi reward của event để lọc ra một nhúm reward mốc | thấp |

---

## 15. Điểm mù đã biết

### Thời điểm hết budget

Hệ thống không có trường ghi lại lúc budget cạn, nên `shouldExpectReward` chỉ biết trạng thái **tại lúc quét**.

Hệ quả: một content không sinh thưởng vì **bug** trong khi budget còn, rồi budget cạn sau đó, sẽ bị loại trừ **sai** và không bao giờ được báo.

Đây là **bỏ sót im lặng**, không phải báo động giả — khó phát hiện hơn nhiều. Chỉ khắc phục được bằng cách bổ sung trường thời điểm hết budget.

### Case B1 — ghi đè dữ liệu trễ

Case **phổ biến nhất** trong toàn bộ danh mục 36 case vẫn không phát hiện được, vì không có lịch sử thay đổi số liệu để so. Đây là khoảng trống lớn nhất còn lại sau vòng 2.

### `callbackLookbackDays` khoá ngầm `CrawlSilentDays`

`CallbacksFor` chặn dưới 30 ngày bằng **hằng số cứng**, trong khi `CrawlSilentDays` chỉnh được qua `common-configs` và mặc định là 3.

Nếu ai đó nâng `CrawlSilentDays` vượt quá 30, `crawl_not_queued` sẽ **báo động giả**: một content có callback mới nhất 40 ngày trước vẫn nằm trong cửa sổ im lặng, nhưng truy vấn đã cắt mất bản ghi đó.

Cách vá: cận dưới lấy theo `max(30, 2 × CrawlSilentDays)`, hoặc chặn ngay lúc nạp cấu hình.

### `view_duplicated` không phân biệt viral với đếm trùng

Đã nêu ở [mục 7.4](#74-view_duplicated--case-b2-mức-cao).

### Cap loại trừ theo "bất kỳ schema nào"

Có thể loại trừ rộng hơn thực tế trên event nhiều schema — nhưng lệch về phía **im lặng**, đúng nguyên tắc thà bỏ sót còn hơn báo sai.

### API sandbox không báo khi bị khoá nuốt

Đã nêu ở [mục 12](#12-api-sandbox).

### Mã template email chưa được cấp

Cho tới khi AccessTrade cấp `AMBASSADOR_EMAIL_VIEW_ANOMALY_ALERT`, cảnh báo chỉ tồn tại dưới dạng dòng log và bản ghi trong `view-anomaly-job-runs`.

Nên bàn giao **cùng lúc** với `reconciliation_mismatch_email.html` — mã template của cảnh báo đối soát (12/08) tới nay cũng chưa có.
