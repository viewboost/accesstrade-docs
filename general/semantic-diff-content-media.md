# Semantic Diff — Content & Media Group

> **Generated**: 2026-05-07
> **Method**: md5 check 13 service files + đọc 5 service file divergent + 12 model file (~5500 LOC) ở 3 dự án.
> **Mục đích**: Hiểu khác biệt nghiệp vụ Content & Media giữa TCB / vCreator / Ambassador.

**Files trong scope**:

| Service | TCB | vCreator | Ambassador | md5 status |
|---|---:|---:|---:|---|
| `service/video.go` | 57 | 57 | 57 | **100% identical** (`ff0bf9be...`) → skip |
| `service/content.go` | 519 | 566 | 693 | 3 md5 khác — divergent |
| `service/content_flow.go` | 244 | 246 | 265 | 3 md5 khác — divergent |
| `service/content_analytic_daily.go` | 466 | 541 | 463 | 3 md5 khác — divergent |
| `service/upload_avatar_social.go` | 251 | ❌ | ❌ | **TCB-only** |

**Models đọc cùng**: `content.go`, `content_flow.go`, `content_analytic_daily.go`, `content_flow_backup.go`, `content_manual_flow.go`, `content_callback.go`, `content_crawl_history.go`, `content_transcript.go`, `video.go`, `article.go`, `cover.go`, `content_import_tracking.go` (TCB-only).

---

## TL;DR

3 dự án có **cùng skeleton xử lý content** (status state machine: WaitingApproved → Approved/Rejected, fan-out side effects: EventReward + ContentAnalyticDaily + ContentFlow + Notification + Audit, status push tới ContentFlowDAO). Khác biệt chính:

1. **TCB ưu tiên reconciliation & content import**: thêm `ReconciliationSnapshot` insertion trong `ContentFlow.CreateFlow` (anti-fraud), có service `upload_avatar_social.go` (auto-download avatar từ social → MinIO), có model `ContentImportTrackingRaw` (admin bulk-import content qua link). Cũng giữ rejection chi tiết hơn (`RejectionTags[]` + `RejectionComment` + `IsLastReward` + `IsEmployee`).
2. **vCreator có "Extended Period" mode**: 1 cờ `IsExtended` lan toả qua `ContentRaw`, `ContentFlowRaw`, `ContentManualFlowRaw`, `ContentAnalyticDailyRaw` để tách analytic của giai đoạn extended (sau khi event end) ra khỏi data chính. `event.IsExtendedPeriod()` + `event.GetRecordingDate()` được áp dụng trong `CreateFlow` để remap date.
3. **Ambassador là dự án duy nhất có Mission**: thêm `Mission *AppID` field trong `ContentRaw`, `ContentFlowRaw`, `ContentAnalyticDailyRaw`. `ChangeStatus` re-track WildRift `point.pending/rejected/completed` từ `mission.Reward`. CheckHashtag check thêm `mission.Hashtag`. ContentFlow có thumbnail update.
4. **Sentiment/transcript divergent**: TCB dùng LLM-based (`LLMSummary`, `LLMResponse`, `OverallScore`, `CriteriaScores[]`, `MatchEventDesc`, `ContainsBlacklist`, `BlacklistMatches`) — chấm điểm theo bộ tiêu chí. vCr/Amb dùng Senlyzer (sentiment provider 3-tier: positive/negative/neutral) — model 12 fields hoàn toàn khác bản chất.
5. **OpsHub đã sync 3 dự án**: cả 3 đều có `IsSendOpsHub` + `OpsHubResult` struct identical → integration với at-core/OpsHub đã port xong cho group này.

**Signal đáng chú ý**: `ContentRaw.Reason` ở TCB có comment `// DEPRECATED - kept for backward compatibility during migration` + thêm `RejectionTags[]` & `RejectionComment` (TCB:`content.go:49-54`). Đây là feature đang migrate, vCr/Amb chưa port theo.

---

## 1. `service/content.go` — Status state machine + Hashtag check + Cheating warning

### Skeleton chung (cả 3 đều có)

| Hàm | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| `ActionAfterWhenChangeStatus` | ✅ | ✅ | ✅ (signature khác: thêm `currentStatus *string`) |
| `ChangeStatus` | ✅ | ✅ | ✅ |
| `RejectListContentByIds` | ✅ | ✅ | ✅ |
| `CheckHashTag` | ✅ (signature có `isCreateByAdmin`) | ✅ | ✅ (signature có `mission *MissionRaw`) |
| `WarningTagContent` (cheating tag low/medium/high) | ✅ | ✅ | ✅ |
| `UpdateRateViewAndOld` | ✅ | ✅ | ✅ |
| `UpdateCashStatistic` | ✅ | ✅ (no `Waiting`) | ✅ (use `TotalCashWaitingApprove`) |
| `GetStatisticContentIsRewardInDay` | ✅ | ✅ (thêm `isExtended ...bool`) | ✅ |
| `UploadImagesFromURLs` | ❌ | ✅ | ✅ |

→ Logic status fan-out (cập nhật EventReward + ContentAnalyticDaily + ContentFlow + Notification.Push + Audit.CreatePayload) **giống ~85%** giữa 3 dự án.

### Khác biệt nghiệp vụ

**TCB** (`techcombank/service/content.go`):
- `ActionAfterWhenChangeStatus` gọi `Event().UpdateStatisticUserEvent` + `Event().UpdateAnalyticEventDailyWhenContentChangeStatus` (TCB-specific, không có ở vCr/Amb).
- `CheckHashTag` có `isCreateByAdmin` flag + skip-list `config.GetENV().ContentIdSkipCheckHashTag` (cho admin import) + cutoff 2025-11-07.
  - **Ý nghĩa**: TCB cho phép admin force-import content bypass hashtag check (liên quan tới `ContentImportTrackingRaw` flow).
- `UploadImagesFromURLs` không có (vì TCB không cần download cover từ URL — content TCB chủ yếu là YouTube link).

**vCreator** (`vcreator/service/content.go`):
- `ActionAfterWhenChangeStatus` có nhánh `if event.EndAt.Before(time.Now()) → UpdateAnalyticOldEventDaily(IsSkipChangeTimeExtended: true)` — đây là tích hợp với **Extended Period feature** (analytic của event đã kết thúc nhưng vẫn track).
- `CheckHashTag` skip nếu `config.IsEnvDevelop()` → tiện cho dev local.
- Có `UploadImagesFromURLs` (download cover image về MinIO bucket).

**Ambassador** (`ambassabor/service/content.go`):
- `ActionAfterWhenChangeStatus` signature **khác biệt**: thêm tham số `currentStatus *string` để track previous status, dùng cho **WildRift point recompensation logic**:
  ```go
  // ambassabor/service/content.go:82-99 (StatusWaitingApproved branch)
  if !mission.ID.IsZero() && currentStatus != nil && *currentStatus == constants.StatusRejected {
      // Reset content.statistic.point: pending = mission.Reward, rejected = 0
      // Update user.wildRift.point: pending += reward, rejected -= reward
  }
  ```
  Tương tự cho `StatusApproved` và `StatusRejected` (mỗi nhánh có block update `wildRift.point.pending/rejected/completed`).
- Trong `ActionAfterWhenChangeStatus` gọi thêm `Event().UpdateBudgetStatistic(ctx, content.User, content.Event, content.ID)` — tích hợp budget tracking trên reward, KHÔNG có ở vCr/TCB.
- `CheckHashTag` nhận thêm `mission *MissionRaw` → check hashtag từ mission template (3rd loop sau user.Hashtag + event.Options.Hashtags).
- Verbose logging với `aurora.BrightMagenta` các step `[ChangeStatus] STEP 1/2/3` — không có ở 2 dự án còn lại.
- `UpdateCashStatistic` có thêm `Waiting: s.TotalCashWaitingApprove` (TCB dùng `Waiting: s.TotalCashWaiting`, vCr không có waiting).

### Bảng quick-diff `ActionAfterWhenChangeStatus` side-effects

| Side-effect | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| `EventReward.UpdateMany` | ✅ | ✅ | ✅ |
| `ContentAnalyticDaily.UpdateMany` | ✅ | ✅ | ✅ |
| `ContentFlow.UpdateMany` (async goroutine) | ✅ | ✅ | ✅ |
| `Event().UpdateStatisticUserEvent` | ✅ | ✅ | ❌ |
| `Event().UpdateBudgetStatistic` | ❌ | ❌ | ✅ |
| `Event().UpdateAnalyticEventDailyWhenContentChangeStatus` | ✅ | ❌ | ❌ |
| `Event().UpdateAnalyticEventDaily` | ❌ | ✅ | ✅ |
| `Event().UpdateAnalyticOldEventDaily` (sau EndAt) | ❌ | ✅ | ✅ |
| `EventSchema().RecheckSchemaWithContentWhenChangeStatus` | ✅ | ✅ | ✅ |
| Mission point recompensation (WildRift) | ❌ | ❌ | ✅ |
| Notification.Push (approved/rejected) | ✅ | ✅ | ✅ |
| Audit.CreatePayload | ✅ | ✅ | ✅ |
| Verbose `[STEP 1/2/3]` logging | ❌ | ❌ | ✅ |

---

## 2. `service/content_flow.go` — Crawl statistic delta tracker

### Skeleton chung

`CreateFlow(event, content, contentInfo, timeUpdate[, mission])` build 3 record `ContentFlowRaw` (View / Like / Comment) chứa delta giữa value cũ và mới. Async insert `ContentCrawlHistoryRaw` (raw snapshot) + telegram alert nếu detect view bất thường (view trước > 0 nhưng crawl mới = 0).

### Khác biệt nghiệp vụ

**TCB** (`techcombank/service/content_flow.go`):
- **Insert reconciliation snapshot** (`ReconciliationSnapshot().InsertSnapshot`) trong goroutine cho mỗi crawl với `Source: SnapshotSourceDailyCrawl` — TCB-only.
  - **Ý nghĩa**: Mỗi crawl đều ghi 1 immutable snapshot vào reconciliation collection để audit/dispute view-fraud sau này.
- KHÔNG có `IsExtended` field.
- KHÔNG nhận `mission` param.

**vCreator** (`vcreator/service/content_flow.go`):
- Đầu hàm `CreateFlow` có override:
  ```go
  // vcreator/service/content_flow.go:36-45
  if event.IsExtendedPeriod() {
      b.IsExtended = true
      mapped := event.GetRecordingDate(src)
      timeUpdate = &mapped
  }
  ```
  → Khi event đang ở **Extended Period** (giai đoạn gia hạn sau EndAt), mọi flow record được mark `IsExtended=true` và date được remap qua `event.GetRecordingDate()`.
- KHÔNG insert reconciliation snapshot.
- KHÔNG có `Reward` field deletion (giống skeleton).

**Ambassador** (`ambassabor/service/content_flow.go`):
- Signature: `CreateFlow(..., mission *MissionRaw)` — extra param.
- Logic phân nhánh dựa trên mission:
  ```go
  // ambassabor/service/content_flow.go:100-102
  if mission == nil || mission.ID.IsZero() {
      update["statistic.point.total"] = contentInfo.View
  }
  ```
  → Nếu có mission, **point KHÔNG nhận từ view count** (vì point = mission.Reward fix).
- Update thumbnail từ `contentInfo.Thumbnail.Default.URL` (TCB/vCr không update thumbnail trong flow).
- Gọi `ContentAnalyticDaily().Update` 2 lần: once cho event, once cho mission (nếu cả 2 cùng tồn tại).
- Mỗi `ContentFlowRaw` insert có thêm `data.Mission = content.Mission` nếu mission có.
- `getContentTotalValue` trừ `TotalManualView` khi tính remaining:
  ```go
  // ambassabor/service/content_flow.go:262
  return data[0].Total - data[0].TotalManualView, nil
  ```
  TCB/vCr chỉ return `data[0].Total`. → Ambassador **tách** manual flow ra khỏi remaining để delta tính chỉ từ crawled view, tránh double-count khi user submit manual view.

### Bảng quick-diff

| Khía cạnh | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Insert ReconciliationSnapshot async | ✅ | ❌ | ❌ |
| `IsExtended` flag override | ❌ | ✅ | ❌ |
| `event.IsExtendedPeriod()` / `GetRecordingDate()` | ❌ | ✅ | ❌ |
| Mission param + thumbnail update | ❌ | ❌ | ✅ |
| Trừ TotalManualView khỏi remaining | ❌ | ❌ | ✅ |
| 2 lần `ContentAnalyticDaily.Update` (event + mission) | ❌ | ❌ | ✅ |

---

## 3. `service/content_analytic_daily.go` — Daily analytic upsert

### Skeleton chung

`UpdateWhenManualFlowHasCreated(content)` + `Update(event, content, timeUpdate[, mission])` + `Audit()` + `DeleteContentFlow()`. Logic:
1. Aggregate `ContentFlowRaw` → daily total view/like/comment
2. Aggregate `ContentManualFlowRaw` → manual view
3. Find/create `ContentAnalyticDailyRaw` cho ngày đó (carry-over Begin/End từ ngày hôm trước)
4. Upsert với delta

### Khác biệt nghiệp vụ

**TCB** (`techcombank/service/content_analytic_daily.go:25-30`):
- Interface `Update(ctx, event, content, timeUpdate)` — 4 params.
- Cond aggregate **KHÔNG có** `isExtended` filter (vì TCB không có concept Extended Period).

**vCreator** (`vcreator/service/content_analytic_daily.go:25-30`):
- Interface giống TCB (4 params).
- Cond aggregate **CÓ** `isExtended: {$ne: true}` filter mặc định, nhưng nếu event đang `ExtendedPeriod.Enabled = true` thì set `cond["isExtended"] = true` và remap `nowHCM = event.GetRecordingDate(time.Now())`.
- → vCr xử lý 2 stream analytic riêng biệt: regular (không extended) và extended.

**Ambassador** (`ambassabor/service/content_analytic_daily.go:24-29`):
- Interface `Update(ctx, event, content, timeUpdate, mission *MissionRaw)` — **5 params** (thêm mission).
- Cond aggregate cơ bản (không có isExtended).
- Khi mission có: pipeline tính analytic theo mission scope, ghi `mission` field trong `ContentAnalyticDailyRaw`.

---

## 4. `service/upload_avatar_social.go` — TCB-only

### Existence
- TCB: 251 LOC (đầy đủ)
- vCr: ❌
- Amb: ❌

### Logic nghiệp vụ
- `UploadAvatarSocial(userId, linkAvatarSocial)`:
  1. Skip nếu user đã có `avatar` (no overwrite).
  2. Parse URL → loại bỏ query/fragment, lấy ext (default `.jpg`).
  3. Download file qua `util.DownloadFile`.
  4. Validate (extension whitelist 10 loại: jpg/jpeg/png/webp/svg/ico/tiff/heic/heif, min 1KB, max `MaxSizePhoto`).
  5. Resize 2 size (sm 150x150, md 300x300) qua `resizeimage.ProcessFillImage`.
  6. Concurrent upload MinIO (3 file: original + sm + md).
  7. Delete avatar cũ trên MinIO nếu có.
  8. Update `UserRaw.avatar` = `FilePhoto{Dimensions: {Small, Medium}}`.

### Ý nghĩa
- TCB tự động pull avatar từ social account khi user link Tiktok/YouTube/etc → cache lên MinIO của TCB. Tránh case URL avatar social bị expired/CDN block.
- vCr/Amb có lẽ dùng URL trực tiếp (không cache) hoặc xử lý ở layer khác (không thấy file tương đương).

---

## 5. Models phát hiện thú vị

### `ContentRaw` — divergent

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Total fields | **48** | 42 | 45 |
| `Images []string` | ❌ | ✅ | ✅ |
| `Category AppID` | ❌ | ❌ | ✅ |
| `OrderType string` | ❌ | ❌ | ✅ |
| `Mission *AppID` + `MissionType *string` | ❌ | ❌ | ✅ |
| `IsExtended bool` | ❌ | ✅ | ❌ |
| `Reason string` (DEPRECATED comment) | ✅ (deprecated) | ✅ (no comment) | ✅ |
| `RejectionTags []string` + `RejectionComment string` | ✅ | ❌ | ❌ |
| `IsHidden bool` | ✅ | ❌ | ❌ |
| `TranscriptStatus string` (pending/processing/completed/failed) | ✅ | ❌ | ❌ |
| `IsLastReward bool` | ✅ | ❌ | ❌ |
| `CreatedBy AppID` | ✅ | ❌ | ❌ |
| `IsCreateByAdmin bool` | ✅ | ❌ | ❌ |
| `IsEmployee bool` | ✅ | ❌ | ❌ |
| `IsTranscript bool` | ✅ | ✅ | ✅ |
| `IsSendOpsHub` + `OpsHubResult` | ✅ | ✅ | ✅ |

→ **TCB hierarchy phong phú nhất ở rejection layer** (RejectionTags + RejectionComment + IsHidden + IsLastReward + IsEmployee + IsCreateByAdmin) — phù hợp với governance khắt khe của ngân hàng + admin import bulk content. Comment line 49: `// DEPRECATED - kept for backward compatibility during migration` cho `Reason` → đang migrate sang `RejectionTags + RejectionComment`.

→ **vCreator** thêm `Images[]` (đa ảnh cho post) và `IsExtended` (extended period).

→ **Ambassador** thêm `Category` (phân loại content), `OrderType` (sort), và quan trọng nhất là `Mission/MissionType` — toàn bộ Mission flow là Amb-specific.

### `ContentFlowRaw`

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Common fields (ID, User, Date, Reward, Event, Content, ContentSource, Type, IsDeleted, Status, Value, NewValue, OldValue, CreatedAt, UpdatedAt) | ✅ | ✅ | ✅ |
| `MigrationHash` | ✅ | ✅ | ❌ |
| `IsExtended` | ❌ | ✅ | ❌ |
| `Mission AppID` | ❌ | ❌ | ✅ |

### `ContentAnalyticDailyRaw`

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Common (ID, Partner, Content, Status, Source, Event, User, Date, Month, Year, View, TotalManualView, AuditStatus, CodeReason, Comment, Like, CreatedAt, UpdatedAt) | ✅ | ✅ | ✅ |
| `IsExtended` | ❌ | ✅ | ❌ |
| `Mission` | ❌ | ❌ | ✅ |

→ Pattern rõ: `IsExtended` là **vCreator's signature**, `Mission` là **Ambassador's signature**, **TCB** giữ skeleton chung.

### `ContentTranscriptRaw` — **fundamentally different**

**TCB** (10 fields, LLM-based scoring):
- `Summary`, `LLMSummary`, `LLMResponse *ContentTranscriptScore`, `Score`
- `ContentTranscriptScore` có: `OverallScore int`, `CriteriaScores []ContentTranscriptCriteriaScore`, `MatchEventDesc bool`, `Issues []string`, `Recommendation string`, `EvaluatedAt time.Time`, `ContainsBlacklist bool`, `BlacklistMatches []string`
- → **AI-driven content review**: chấm điểm theo bộ tiêu chí + check blacklist từ event description. Có vẻ tích hợp với LLM (Vertex AI) để evaluate transcript của video.

**vCreator + Ambassador** (12 fields, Senlyzer-based):
- `SenlyzerID`, `Title`, `Summary`, `Score ContentTranscriptScore`, `Status`, `Srt`
- `ContentTranscriptScore`: `Positive string`, `Negative string`, `Neutral string` (sentiment analysis 3-tier)
- → **Sentiment analysis**: dùng external service Senlyzer để get positive/negative/neutral sentiment từ transcript + lưu Srt subtitle.

→ **Đây là divergence nghiệp vụ lớn**: TCB ưu tiên content quality scoring (AI scoring criteria, blacklist enforcement), vCr/Amb ưu tiên sentiment monitoring. KHÔNG thể chia sẻ transcript service.

### `ContentImportTrackingRaw` — **TCB-only**

```go
type ContentImportTrackingRaw struct {
    ID, User, Event, Partner, Staff   AppID
    TotalItems, SuccessItems, ProcessingItems, FailedItems int
    Status   string  // processing, completed, failed
    Contents []ContentImportTrackingItem
    CreatedAt, UpdatedAt, CompletedAt
}
type ContentImportTrackingItem struct {
    Source, Link, Status, Message string
    ContentID AppID
}
```

→ Track **bulk import job** (admin import nhiều link content cùng lúc, mỗi item có Source + Link + status success/failed). Chỉ TCB có flow này — phù hợp với operational reality TCB có team admin nhập content thay user. vCr/Amb là user-driven (user tự submit link).

### `ContentCallbackRaw`

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| Common (ID, Link, Information, Status, RequestID, ReceivedAt, CreatedAt, UpdatedAt) | ✅ | ✅ | ✅ |
| `Desc` / `Description` | `Desc` | `Desc` | `Description` (different json key) |
| `TrackingHistoryImpportID` (typo) | ✅ | ❌ | ❌ |
| `TrackingId` | ✅ | ❌ | ❌ |

→ TCB extra fields liên quan đến tracking import flow. Có 1 typo trong field name: `TrackingHistoryImpportID` (Impport → Import).

### `ContentManualFlowRaw`

vCr thêm `IsExtended` (15 → 16 fields). TCB/Amb không có.

### Other models 100% identical

- `VideoRaw`: 14 fields, identical → `service/video.go` cũng synced.
- `ContentCrawlHistoryRaw`: 7 fields, identical.
- `ContentFlowBackupRaw`: 15 fields, identical.
- `cover.go`: chỉ chứa DAO interface, identical.

---

## 6. Câu hỏi business mở

(Cần PM/tech lead clarify)

1. **TCB rejection migration**: `ContentRaw.Reason` được mark deprecated, đang migrate sang `RejectionTags[]` + `RejectionComment`. **Đã có UI mới chưa?** Backward compatibility query nào còn dùng `Reason` để vCr/Amb có cần follow theo không?
2. **vCreator Extended Period**: Đây là gia hạn event sau khi `EndAt` đã pass — analytic data sau đó được tag `IsExtended=true` và remap date. **Use-case nghiệp vụ gì?** Có phải để track "content vẫn có view dù event đóng" cho marketing post-mortem? TCB/Amb có cần feature này?
3. **Ambassador Mission point logic**: Khi content chuyển từ rejected → waiting/approved, code reset `wildRift.point.pending = mission.Reward` và `point.rejected -= mission.Reward`. **Đây là feature WildRift gaming** (Riot Vietnam?) hay áp dụng cho mọi mission? Tại sao dùng `user.WildRift.Point` thay vì generic `user.MissionPoint`?
4. **TCB ContentImportTrackingRaw**: Có flow admin import bulk content. **Có UI/API admin nào cho phép upload CSV danh sách link?** Liên quan đến `IsCreateByAdmin` + `CheckHashTag(isCreateByAdmin)` skip-list.
5. **Transcript divergence**: TCB dùng LLM scoring với blacklist enforcement, vCr/Amb dùng Senlyzer (positive/negative/neutral). **2 hệ thống có converge không?** Hay là 2 use-case khác hẳn (TCB = anti-violation, vCr/Amb = mood monitoring)?
6. **TCB ReconciliationSnapshot insert per crawl**: TCB ghi snapshot mỗi lần crawl → high write volume. **Có TTL/archive policy không?** Hay collection sẽ vô hạn lớn?
7. **TCB upload_avatar_social.go**: Avatar được cache vào MinIO của TCB. **vCr/Amb không cache** — có gặp issue avatar URL hết hạn (Facebook CDN signed URL) không?

---

## 7. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Status state machine** | Full + UpdateAnalyticEventDailyWhenContentChangeStatus | Full + Extended period detection | Full + Mission point reset + Budget statistic |
| **Content flow tracking** | + ReconciliationSnapshot per crawl | + IsExtended flag remap | + Mission tagging + Manual view subtraction |
| **Daily analytic** | Standard | + Extended period dual-stream | + Mission scope (5-param signature) |
| **Hashtag check** | + Admin skip-list + cutoff | + Dev-mode skip | + Mission hashtag check |
| **Avatar cache** | ✅ MinIO cache | ❌ | ❌ |
| **Rejection structured** | ✅ RejectionTags + Comment (migrating) | ❌ | ❌ |
| **Bulk import tracking** | ✅ ContentImportTrackingRaw | ❌ | ❌ |
| **Extended period mode** | ❌ | ✅ Full feature | ❌ |
| **Mission feature** | ❌ | ❌ | ✅ Full feature (WildRift point) |
| **Transcript scoring** | LLM (criteria + blacklist) | Senlyzer (sentiment) | Senlyzer (sentiment) |
| **OpsHub integration** | ✅ | ✅ | ✅ (synced) |
| **Telegram alerts khi crawl invalid** | ✅ | ✅ | ✅ (synced) |
| **Video service** | identical | identical | identical |

**Direction port nếu cần**:

- **TCB → vCr/Amb**: ReconciliationSnapshot insert (anti-fraud audit trail) — effort medium (cần ReconciliationSnapshot service + collection). RejectionTags+Comment migration (UX cải tiến) — effort small. ContentImportTracking (admin bulk import) — chỉ phù hợp nếu vCr/Amb có nhu cầu.
- **vCreator → TCB/Amb**: Extended Period mode — effort lớn (cần thêm `event.ExtendedPeriod`, `IsExtendedPeriod()`, `GetRecordingDate()`, plus IsExtended flag toàn bộ schema). Chỉ port khi có nhu cầu rõ ràng từ business.
- **Ambassador → TCB/vCr**: Mission flow — quá tightly-coupled với WildRift gaming, khó port general. Generic mission concept có thể abstract ra (thêm `Mission *AppID` vào ContentRaw + analytic) nếu vCr/TCB có roadmap mission-based campaign.
- **TCB upload_avatar_social.go**: Có thể port sang vCr/Amb — effort medium (~250 LOC + MinIO config + resize module). Solve được issue avatar URL expiry.

**Đặc điểm group**:
- `video.go` đã 100% sync → có thể move sang shared lib.
- `ContentCrawlHistoryRaw`, `ContentFlowBackupRaw`, OpsHub structs đã sync.
- 3 dự án đi 3 hướng nghiệp vụ rõ rệt: TCB = governance/audit, vCreator = time-series flexibility (extended period), Ambassador = gamification (mission/wildRift).

---

## Files referenced

- TCB: `accesstrade-projects/techcombank/backend/internal/service/{content,content_flow,content_analytic_daily,video,upload_avatar_social}.go`
- vCreator: `accesstrade-projects/vcreator/backend/internal/service/{content,content_flow,content_analytic_daily,video}.go`
- Ambassador: `accesstrade-projects/ambassabor/backend/internal/service/{content,content_flow,content_analytic_daily,video}.go`
- Models: `*/backend/internal/model/mg/{content,content_flow,content_analytic_daily,content_flow_backup,content_manual_flow,content_callback,content_crawl_history,content_transcript,video,article,cover}.go`
- TCB-only model: `techcombank/backend/internal/model/mg/content_import_tracking.go`
