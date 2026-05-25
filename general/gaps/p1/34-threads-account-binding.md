# Gap #34 — Liên kết tài khoản Threads cho creator: TCB chưa có, vCreator chỉ partial, Ambassador đầy đủ

> **Priority**: 🟠 **P1** (initial 2026-05-10)
> **Source**: User self-listed gap
> **Direction port**: Ambassador → vCreator (bổ sung) + Ambassador → TCB (port đầy đủ)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

**Threads** (Meta — sister product của Instagram) là social platform đang lên, creator dùng để post bài text + image. Để track content đăng trên Threads → creator cần "liên kết tài khoản Threads" với platform AccessTrade.

3 sản phẩm hỗ trợ Threads ở mức độ khác nhau:

| | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Constant `SourceThreads` | ❌ | ✅ `"threads"` | ✅ `"threads"` |
| Module `social/threads/` (URL validation) | ❌ | 🟡 10 LOC (chỉ regex post URL) | ✅ ~263 LOC (client + model + 2 regex profile/post) |
| User struct `UserThreadsData` (lưu profile binding) | ❌ | ❌ | ✅ 8 fields (ID, Username, FullName, Bio, Pic, Followers, IsVerified, LinkSocial) |
| Content tracking source `threads` | ❌ | ✅ (event_schema.go dùng `Statistic.Threads.View`) | ✅ |
| API client gọi Threads (fetch profile/post info) | ❌ | ❌ | ✅ |
| Field trong content_analytic_daily | ❌ | ✅ | ✅ |

## Hệ quả

- **TCB**: creator đăng bài Threads → không track được. Khách hàng TCB không thể chạy campaign Threads → mất market share platform mới
- **vCreator**: track được view của Threads (statistic) nhưng KHÔNG có binding flow đầy đủ — creator không bind được account Threads vào profile của mình → InfluencerProfile thiếu dữ liệu Threads
- **Ambassador**: đầy đủ nhất — bind account, fetch profile metadata, validate URL profile + post, track view/engagement

## Liên quan các gap khác

- **Gap #2 (InfluencerProfile)**: gap #2 đã note "Ambassador có special channels facebook_post, threads" — gap #34 này là phần **scope con** cho riêng Threads
- **Gap #17 (Avatar cache)**: nếu port Threads sang TCB/vCr, avatar Threads cũng cần cache MinIO (cùng pattern các social khác)

## Giải pháp

### Phase 1: vCreator (~3-5 ngày)
- Bổ sung struct `UserThreadsData` vào `user.go` (copy từ Ambassador 8 fields)
- Mở rộng module `social/threads/` thêm regex validate profile URL + API client fetch profile
- Public service: thêm flow `LinkThreadsAccount` cho creator bind

### Phase 2: TCB (~1-2 tuần)
- Thêm `SourceThreads = "threads"` constant
- Tạo folder `internal/module/social/threads/` với client + model + URL validation
- Bổ sung struct `UserThreadsData` vào `user.go`
- Public service: link Threads + fetch profile
- Content tracking: thêm Threads vào `content_analytic_daily` schema
- Avatar cache (gap #17): áp dụng cho Threads

**Total**: ~3 tuần (tương đương vCr 3-5 ngày + TCB 1-2 tuần).

## Tại sao P1

- **Threads đang growth nhanh**: Meta đang push Threads — creator/influencer Việt Nam ngày càng nhiều dùng
- **Cross-product impact lớn**: cả 2 sản phẩm còn lại đều cần (vCr partial → cần bổ sung, TCB chưa có → cần port full)
- **Pattern rõ ràng**: Ambassador đã có production-ready pattern, copy không tốn nhiều effort
- **Liên quan #2** (InfluencerProfile P0): Threads binding là dependency cho InfluencerProfile có dữ liệu Threads complete

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Ambassador có Threads binding đầy đủ (~263 LOC module + struct user.go + content tracking). vCreator chỉ có partial (10 LOC URL validation + content statistics, KHÔNG có user struct binding). TCB không có gì (chỉ vài reference legacy ở social_profile + reconciliation_snapshot).

## Verify code

### Ambassador (source of truth)

**Constants** — `internal/constants/constants.go:197`:
```go
SourceThreads = "threads"
```

**Module** — `internal/module/social/threads/`:
- `threads.go` (36 LOC) — 2 regex constants + 3 validation functions
  ```go
  RegexThreadsProfile = `^https:\/\/(www\.)?(threads\.net|threads\.com)\/@[\w._-]+\/?...`
  RegexThreadsPost    = `^https:\/\/(www\.)?(threads\.net|threads\.com)\/(t\/[\w_-]+|@[\w._-]+\/post\/[\w_-]+)\/?...`
  ```
- `client.go` (154 LOC) — API client fetch profile/post metadata
- `model.go` (73 LOC) — response models

**User struct** — `internal/model/mg/user.go:168-177`:
```go
type UserThreadsData struct {
    ID         string
    Username   string
    FullName   string
    Bio        string
    ProfilePic string
    Followers  int64
    IsVerified bool
    LinkSocial string
}
// User.Threads field: bson:"threads,omitempty"
```

**Content tracking**: `event_analytic_daily.go`, `user_event.go`, `content.go` đều có Threads source.

### vCreator (partial)

**Constants** — `internal/constants/constants.go:188`:
```go
SourceThreads = "threads"
```

**Module** — `internal/module/social/threads/threads.go` (10 LOC):
```go
package threads

func IsValidURL(url string) bool {
    re := regexp.MustCompile(`^https:\/\/(www\.)?threads\.com\/@[\w._-]+\/post\/[\w_-]+(\?.*)?$`)
    return re.MatchString(url)
}
```
→ Chỉ validate post URL, **không có profile URL regex**, **không có client**, **không có model response**.

**User struct**: ❌ KHÔNG có `UserThreadsData` field trong `user.go`. Creator không bind được Threads account.

**Content tracking**: ✅ có (event_schema.go dùng `userEvent.Statistic.Threads.View.Completed`) — nhưng creator phải dán URL post manually mỗi lần (không có profile binding).

### TCB

**Constants**: ❌ KHÔNG có `SourceThreads`.

**Module**: ❌ KHÔNG có folder `internal/module/social/threads/`.

**User struct**: ❌ KHÔNG có `UserThreadsData`.

**Reference legacy**:
- `internal/module/social/social_profile/client.go` — chỉ có comment legacy reference
- `internal/service/reconciliation_snapshot.go` — vài reference legacy
- `internal/constants/content.go` — có thể đã prepare nhưng chưa wire

→ TCB hoàn toàn chưa support Threads.

## Đề xuất implementation

### Phase 1: vCreator (3-5 ngày)
1. Mở rộng `internal/module/social/threads/threads.go` từ 10 → ~36 LOC:
   - Thêm `RegexThreadsProfile`
   - Thêm `IsValidProfileURL()`, `IsValidPostURL()` (giữ `IsValidURL()` cho backward compat)
2. Tạo `internal/module/social/threads/client.go` (~154 LOC) — copy từ Amb
3. Tạo `internal/module/social/threads/model.go` (~73 LOC) — response models
4. Thêm `UserThreadsData` struct vào `internal/model/mg/user.go` + field `Threads *UserThreadsData` trong `UserRaw`
5. Public service: thêm `LinkThreadsAccount` flow

### Phase 2: TCB (1-2 tuần)
1. Thêm `SourceThreads = "threads"` vào `internal/constants/constants.go`
2. Tạo folder `internal/module/social/threads/` (~263 LOC, copy từ Amb)
3. Thêm `UserThreadsData` struct + field `Threads` vào `user.go`
4. Public service: link Threads flow + fetch profile API
5. Content tracking: schema migration cho `event_analytic_daily`, `user_event`, `content`
6. Tích hợp avatar cache (gap #17) cho Threads

**Total**: ~3 tuần effort (3-5 ngày vCr + 1-2 tuần TCB).

## Risks + mitigations

1. **Threads API thay đổi**: Meta có thể update Graph API → break client
   - **Mitigation**: dùng pattern Ambassador (đã production-tested), monitor Meta changelogs
2. **Migration data**: TCB cần data migration cho `event_analytic_daily` thêm field Threads
   - **Mitigation**: nullable field, không break creator/event cũ
3. **Inconsistent regex**: vCreator regex hiện tại chỉ accept `threads.com`, không accept `threads.net` (Amb accept cả 2)
   - **Mitigation**: vCr migrate regex về pattern Ambassador

## Files referenced

**Ambassador (source of truth)**:
- `internal/constants/constants.go:197` (SourceThreads)
- `internal/module/social/threads/threads.go` (36 LOC)
- `internal/module/social/threads/client.go` (154 LOC)
- `internal/module/social/threads/model.go` (73 LOC)
- `internal/model/mg/user.go:168-177` (UserThreadsData)
- `internal/model/mg/event_analytic_daily.go`, `user_event.go`, `content.go`

**vCreator (partial)**:
- `internal/constants/constants.go:188` (SourceThreads)
- `internal/module/social/threads/threads.go` (10 LOC — only URL regex)
- KHÔNG có UserThreadsData struct

**TCB (chưa có)**:
- KHÔNG có SourceThreads constant
- KHÔNG có folder `internal/module/social/threads/`
- KHÔNG có UserThreadsData struct
- Vài reference legacy ở `social_profile/client.go` + `reconciliation_snapshot.go`

## Lịch sử phân loại

- **2026-05-10 (initial)**: Tạo gap mới P1 sau khi user tự liệt kê. User confirm tách riêng cho Threads (không bundle các Facebook variants vào). Lý do P1: Threads đang growth, cross-product impact (cả vCr lẫn TCB cần), liên quan dependency #2 InfluencerProfile.
