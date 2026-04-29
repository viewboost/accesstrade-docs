# Audit 03: event.go (860 dòng)

**Source:** `vcreator-philippines/backend/pkg/public/service/event.go`

---

## Function inventory (12 functions)

| Function | Line | Body summary | Country issues |
|---|---|---|---|
| `Event()` factory | 38 | Returns `&eventImpl{}` | None |
| `GetListUserNewest` | 45-84 | Fetch users với totalPoints>0 từ UserEventRaw, async load profiles | None |
| `GetStatistic` | 87-143 | 3 goroutines: count active events, aggregate EventAnalyticDaily (views/content/commission), count users | ⚠️ `fmt.Println` line 127 |
| `GetDetailBySlug` | 146-161 | Find event by slug + optional partner filter | None |
| `GetList` | 163-300 | List events trong displayStart/EndAt window, top-4 content per event, user stats | ⚠️ `context.Background()` line 255 (error hiding) |
| `GetAllSchema` | 302-377 | Fetch event schemas (ViewMilestone + ContentMilestone), check user EventReward completion | ⚠️ **Commented time-window filter** lines 314-319 |
| `getSortContent` | 379-402 | Helper: map sort string → MongoDB sort doc | None |
| `GetListContentByEvent` | 405-487 | List approved content cho event | None |
| `GetListContentByMe` | 489-571 | List content của current user trong event | YouTube thumbnail fallback line 563 (generic OK) |
| `GetLeaderBoard` | 574-641 | Rankings by `statistic.pointTotal.completed > 0` | ⚠️ **No sort order** trong query |
| `GetEventCurrent` | 643-665 | Find ViewBoost active event by partner ID | None |
| `getEventDetailResponse` | 667-833 | Build full event detail (covers/tags/videos/articles/related events) | ⚠️ `context.Background()` lines 720, 238 |
| `getArticle` | 836-860 | Fetch article by ID, return nil silently if not found | ⚠️ Inconsistent error handling |

---

## Country-specific issues

### 🟢 Clean — event.go module này SẠCH

- **No `+84/+62/+63`** hardcode trong file này
- **No timezone HCM/Manila** trong logic event.go
- **No VND/IDR/PHP** currency literals
- **No Vietnamese/Bahasa text strings**
- **All user text đã i18n** qua `locale.GetMessageByKey()`

→ Module event.go là **read-only query layer**, business logic complex nhưng **không có country leftover**.

### 🟡 Tham chiếu indirect

- Constants `timezoneHCM` (VN), `RegexPhoneNumber` (ID), `IPCountryCodeID` exist trong codebase, nhưng **không được event.go dùng**. Chỉ là cleanup global.

---

## Business logic insights

### Event lifecycle (multi-stage)

**Display Window** (UI visibility):
- `displayStartAt <= now <= displayEndAt` (lines 168-173, 652-656)
- Independent với actual event runtime
- Used in `GetList`, `GetEventCurrent`
- Purpose: control khi nào event hiển thị (trước/sau active period)

**Active Window** (event execution):
- `startAt <= now <= endAt` (lines 104-109, 799-804)
- Used in `GetStatistic`, related events trong detail

**Status field**:
- Filter `status: "active"` (used khắp nơi)
- 3-level filtering: Display + Execution + Status

### Leaderboard
- Trigger: `GetLeaderBoard()` (line 574)
- Filter: `statistic.pointTotal.completed > 0`
- ⚠️ **Bug:** No sort order trong query → ranking undefined

### Schema & Milestones
- 2 schema types: `ViewMilestone` + `ContentMilestone` (lines 310-311)
- ⚠️ **Commented filter:** lines 314-319 có time-window validation bị comment out → schemas có thể fulfill at wrong time
- Completion tracking: query EventRewardRaw status pending/completed

### Reward calc trigger
- **KHÔNG ở event.go** — calculation ở schedule.go
- Event service chỉ:
  - Fetch schema definitions với CashReward data (line 346)
  - Check user's earned EventReward records
  - Return `IsPass: true` if user has claimed reward

### Content listing per event
- Approved only filter (line 422)
- Sort: Newest/Like/View/Comment via getSortContent
- User profiles lazy-loaded với goroutines

---

## Bug / Red flags

### Critical

| Line | Issue | Impact |
|---|---|---|
| 296-298 | Sort GetList: `return res.Data[i].ID == query.Event` (boolean sort) | Sort algo unstable — không guaranteed move match to front |
| 574-641 | GetLeaderBoard không có SortInterface trong query | Leaderboard ranking undefined |
| 314-319 | Commented time-window filter trong GetAllSchema | Incomplete port — schemas có thể không respect timing |

### Code quality

| Line | Issue |
|---|---|
| 127 | `fmt.Println` cho error logging |
| 238, 255, 720 | `context.Background()` trong nested goroutines (mất error chain) |
| 287 | Dead code: `ptime.TimeResponseInit` set nhưng never used |
| 836-844 | `getArticle` returns nil silently — inconsistent error pattern |

---

## Cleanup tasks

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| EVT-01 | event.go:296-298 | Fix sort bug GetList — dùng explicit swap thay boolean sort | P0 | S |
| EVT-02 | event.go:574 | Add SortInterface cho GetLeaderBoard query | P0 | S |
| EVT-03 | event.go:314-319 | Decide: enable hoặc remove commented time-window filter trong GetAllSchema | P1 | S |
| EVT-04 | event.go:127 | Replace fmt.Println → proper logger | P2 | S |
| EVT-05 | event.go:238,255,720 | Replace context.Background() → propagate ctx | P2 | M |
| EVT-06 | event.go:287 | Remove dead code TimeResponseInit | P2 | S |
| EVT-07 | event.go:836-844 | Standardize getArticle error pattern | P2 | S |
| EVT-08 | event.go:256-290 | Optimize: batch user/userEvent load thay vì per-event loop | P2 | M |

---

## Verdict module event.go

✅ **Đây là module SẠCH NHẤT đã audit cho đến giờ** (so với user.go, schedule.go có VN leftover nặng).

- Không cần PH-specific changes trong event.go
- Chỉ cần fix bugs general (sort, ctx propagation, commented code)
- Total cleanup: ~8h
