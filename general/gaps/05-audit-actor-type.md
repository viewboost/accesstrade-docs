# Gap #5 — TCB/Ambassador thiếu Audit ActorType (đã có ở vCreator)

> **Priority**: 🟡 **P2** (reclassified 2026-05-07 sau khi user clarify business context)
> **Source**: [semantic-diff-reconciliation-audit.md](../semantic-diff-reconciliation-audit.md)
> **Direction port**: vCreator → TCB + Ambassador
> **Last verified**: 2026-05-07 (3-layer verification: model + service + caller)

---

## TL;DR

Cả 3 dự án đều **CÓ flow tự động dùng root account** để lưu audit (webhook, batch, cron). Khác biệt:
- **vCreator** đã thêm field `ActorType` (`human_admin` / `root_account`) → audit log phân biệt được tự động vs thủ công khi query
- **TCB và Ambassador** vẫn dùng root account làm `actionBy` nhưng **không có field phân biệt** → mọi audit log nhìn giống nhau, query log không filter được "tự động vs thủ công"

→ **Gap thật** (không phải cargo-cult): root account đã được dùng ở 3 dự án, chỉ là TCB/Amb thiếu field metadata. Backport là logical step.

**Direction port**: vCreator → TCB + Ambassador. Effort thấp (~20-30 LOC backend) nhưng không cấp bách → **P2**.

---

## Tại sao cần ActorType (business value)

### Use case thực tế ở vCreator

```
HR upload CSV → batch import 1000 employees
   ↓
Engine match registry (registry_match.go) → tự động verify user, update workplace
   ↓
Mỗi user update sinh 1 audit log:
   - actionBy = (root account ID, hardcoded)
   - actorType = "root_account"  ← biết đây là automation
   - message = "Auto-verified via HR import batch #123"
```

→ Khi admin xem audit log của 1 user, có thể **filter**:
- "Hành động do staff thật" (actorType=human_admin) — ai approve, ai reject
- "Hành động do system" (actorType=root_account) — auto-verify, auto-import, webhook callback

### Risk khi không có ActorType (TCB + Ambassador hiện tại)

1. **Compliance issue**: kiểm toán hỏi "Ai đã verify user X?" → audit trả "staff Y" nhưng thực ra là system tự verify dùng staff Y làm fallback actor → **gây hiểu lầm**, có thể vi phạm SOC/SOX/ISO audit requirements
2. **Debug khó**: nếu action sai (vd: 500 user bị reject nhầm), không biết là **staff bấm sai** hay **bug automation** → mất thời gian investigate
3. **Permission/RBAC sai**: nếu sau này muốn rule "chỉ staff cấp manager mới được approve" → không phân biệt được là root_account đang fake permission

---

## Verify 3-layer (theo methodology học từ gap #1)

### Layer 1: Code tồn tại — vCreator có, TCB/Amb không

| Component | TCB | vCreator | Ambassador |
|---|---|---|---|
| Model `AuditRaw.ActorType` field | ❌ | ✅ `actorType,omitempty` | ❌ |
| Service constants `ActorTypeHumanAdmin`, `ActorTypeRootAccount` | ❌ | ✅ | ❌ |
| Service `PayloadAudit.ActorType` field | ❌ | ✅ | ❌ |
| Service fn `CreatePayloadWithActorType` | ❌ | ✅ | ❌ |
| Default fallback ("human_admin" nếu không truyền) | ❌ | ✅ ở `CreateAudits` | ❌ |

**File LOC**:
- TCB `internal/service/audit.go`: 56 LOC
- Ambassador `internal/service/audit.go`: 56 LOC (md5 identical với TCB)
- vCreator `internal/service/audit.go`: 80 LOC (thêm ~24 LOC)

### Layer 2: Code được gọi — vCreator có caller dùng thật

```bash
# vCreator: tìm caller dùng ActorTypeRootAccount
grep -rn "ActorTypeRootAccount" vcreator/backend/pkg/
```

Kết quả:
- `pkg/admin/service/employee_registry.go:579` — ghi audit khi auto-verify user qua HR import
- `pkg/admin/service/employee_registry.go:630` — ghi audit khi update registry (HR đính chính phone/workplace)
- `pkg/admin/service/employee_registry_match_test.go:216` — assertion trong test
- `pkg/admin/service/user.go:554,564,574,585` — helper `getActorContext` quyết định actor type theo context (request có staff session → human_admin; không có → root_account)

→ **Có caller thực sự dùng**, không phải code chết.

### Layer 3: Runtime DB — vCreator ghi field, TCB/Amb không

`AuditRaw` schema (đã verify):
```go
// vCreator (có ActorType)
type AuditRaw struct {
    ID, TargetId, Data, Message, ActionBy
    ActorType string `bson:"actorType,omitempty"`  ← chỉ vCreator có
    CreatedAt, BatchID
}

// TCB + Ambassador (giống nhau, không có ActorType)
type AuditRaw struct {
    ID, TargetId, Data, Message, ActionBy
    CreatedAt, BatchID
}
```

→ TCB + Ambassador md5 audit.go service file **identical** (`b672c9cb0067777d547f735ea0f479cf`). Schema cũng identical.

---

## Tại sao TCB lại không có (giải đáp "có vẻ kỳ cục")

User comment: *"TCB là fork từ vCreator mà sao nó khác được thì quá vô lý"*

**Đúng là TCB fork từ vCreator**, nhưng timeline cho thấy hợp lý:

```bash
# Git log thực tế
vCreator first commit:           2024-10-16  "source code handover"
                                              (chưa có ActorType lúc này)
TCB first commit:                 2025-10-07  "Sure PI!"
                                              (fork tại đây — vCreator vẫn chưa có ActorType)
vCreator added ActorType:         2026-04-24  "feat(employee-registry): scaffold import pipeline"
                                              (innovation MỚI sau khi TCB đã fork)
                                              ↑
                                              Chính là feature HR import batch — context tự nhiên cần phân biệt actor
TCB hiện tại (2026-05-07):                   Chưa backport
```

→ **TCB lag behind vCreator** vì feature ActorType được phát triển **sau** thời điểm fork. Đây là pattern điển hình "downstream lag behind upstream innovations" — không có gì kỳ cục.

**Ambassador**: lịch sử git bị wipe (`5ff00f83 remove git history`) — không trace được. Nhưng size + structure giống TCB → likely fork cùng thời điểm hoặc trước.

---

## Đề xuất implementation

### Phase 1: Port code vCreator → TCB + Ambassador (~1-2 ngày)

#### Step 1: Update `internal/model/mg/audit.go`
Thêm 1 field vào `AuditRaw` struct ở cả TCB và Ambassador:
```go
// ActorType phân loại actor: "human_admin" (staff từ request) | "root_account" (fallback tự động)
ActorType string `bson:"actorType,omitempty"`
```

#### Step 2: Update `internal/service/audit.go`
Copy y nguyên từ vCreator:
- 2 constants `ActorTypeHumanAdmin`, `ActorTypeRootAccount`
- Field `ActorType` trong `PayloadAudit`
- Method `CreatePayloadWithActorType`
- Update `CreateAudits` để map field + default fallback

→ Backward compatible: `CreatePayload` cũ không truyền actorType → fallback "human_admin" → mọi audit log cũ vẫn hoạt động.

#### Step 3: Update các caller cần ghi root_account
Identify chỗ nào trong TCB và Ambassador là **automation flow** (webhook, cron, batch import). Candidates:
- TCB: `reconciliation_snapshot_job.go` (cron snapshot), `tracking_request_crawl.go` (webhook crawl), `transfer_processing.go` (admin batch)
- Ambassador: `transfer_processing.go` (admin batch), bất cứ webhook econtract callback

→ Ở những chỗ này, đổi từ `Audit().CreatePayload()` sang `Audit().CreatePayloadWithActorType(... ActorTypeRootAccount)`.

### Phase 2: Migration data cũ (optional, ~0.5 ngày)

Decision: backfill audit log cũ với actorType nào?

**Option A — Không migrate**:
- Records cũ: actorType empty → khi query default "human_admin"
- Records mới: có actorType chính xác
- Pro: zero risk, không cần migration
- Con: log cũ không phân biệt được automation vs human

**Option B — Best-effort backfill**:
- Heuristic: nếu `ActionBy` = root staff ID → set `actorType = root_account`
- Dùng cho compliance audit lookback
- Pro: data history correct
- Con: cần biết root staff ID từng dự án (vCreator có concept staff.go GetRoot, TCB/Amb có thể chưa)

→ Đề xuất **Option A** trước (đơn giản, zero risk). Nếu compliance team yêu cầu lookback → mới làm B.

### Phase 3: Test + verify (~0.5 ngày)

- Unit test: copy `audit_test.go` từ vCreator nếu có
- Integration test: trigger webhook/cron flow → verify audit log có actorType=root_account
- Manual verify: admin xem audit log → filter được theo actorType

---

## Effort estimate

| Task | Effort |
|---|---|
| Backend changes (model + service) — TCB | 0.5 ngày |
| Backend changes — Ambassador (giống TCB, dễ copy) | 0.25 ngày |
| Update callers (identify automation flows + đổi sang CreatePayloadWithActorType) | 0.5 ngày × 2 dự án = 1 ngày |
| Test + verify | 0.5 ngày |
| **Tổng** | **~2-3 ngày dev** |

→ Easy win đúng nghĩa: backend changes ≤ 30 LOC mỗi dự án, business value cao (compliance + debug clarity).

---

## Action items

1. ✅ **Verify với vCreator team**: ActorType pattern hoạt động OK trong production không? Có pain point gì lúc rollout không?
2. **Port vCreator → TCB**: tạo PR backport (model + service + identify ~3-5 callers automation)
3. **Port vCreator → Ambassador**: tương tự (transfer_processing.go là caller chính)
4. **Update CLAUDE.md hoặc docs/handbook**: ghi rõ convention "khi nào dùng human_admin vs root_account" cho dev tương lai
5. **Optional**: backfill data cũ nếu compliance yêu cầu

---

## Câu hỏi business mở

1. **Compliance team có chuẩn audit cụ thể không?** SOX/SOC/ISO 27001 thường yêu cầu phân biệt actor → cần verify với compliance team TCB.
2. **Ambassador automation flows nào cần root_account?** Hiện đã thấy `transfer_processing.go` (batch + webhook econtract callback). Còn `core.Client()` callback flow nào khác không?
3. **TCB có concept "root staff account" như vCreator chưa?** vCreator có `staff.go` service `GetRoot()` để fetch root account. TCB có thể chưa có → cần seed root staff trước khi triển khai.
4. **Migration data cũ**: có cần lookback audit log không? (gap #25 vCreator staff root account port có thể tied với gap này)

---

## Liên quan tới gap khác

- **Gap #25** (vCreator staff root account → TCB/Amb): tied với gap này. Nếu port ActorType thì TCB/Amb cần `GetRoot()` để có root staff ID làm `ActionBy`.
- **Gap #6, #15** (Reconciliation engine, ReconciliationSnapshot): nếu port reconciliation từ TCB → vCr/Amb thì các automation flow như `RunPostExpiryCrawl` cần ghi audit với `root_account`.

→ Đề xuất combo: làm gap #5 + #25 cùng nhau (đều là vCreator → TCB/Amb, đều liên quan automation actor).

---

## Files referenced

**vCreator (source of truth)**:
- `internal/service/audit.go` (80 LOC, có 4 fns + 2 constants)
- `internal/model/mg/audit.go` (30 LOC, có field ActorType)
- `pkg/admin/service/employee_registry.go:579,630` — caller chính dùng `ActorTypeRootAccount`
- `pkg/admin/service/user.go:554-585` — helper `getActorContext` quyết định actor type theo context

**TCB (cần backport)**:
- `internal/service/audit.go` (56 LOC, md5 = `b672c9cb0067777d547f735ea0f479cf`)
- `internal/model/mg/audit.go` (28 LOC)

**Ambassador (cần backport, giống TCB)**:
- `internal/service/audit.go` (56 LOC, md5 identical với TCB)
- `internal/model/mg/audit.go` (28 LOC, identical với TCB)

---

## Lịch sử phân loại

### Lần 1 — Initial (2026-05-07): SAI
- Priority: 🔴 P0 (Total 17)
- Đánh giá: "TCB/Amb thiếu ActorType = audit log không phân biệt automation"

### Lần 2 — User catch fork timeline (2026-05-07): VẪN SAI
- Verify với git log: TCB fork 2025-10, vCreator thêm ActorType 2026-04 (sau fork) → "downstream lag" pattern
- Vẫn giữ P0

### Lần 3 — User clarify business context (2026-05-07): reclassify P0 → 🟡 P2

User question: *"actor type ý bạn là chức năng gì? Import danh sách nhân viên để auto duyệt á hả"*

→ Đúng context vCreator. Commit `0d3ec3bf` thêm ActorType là cho:
1. **Employee Registry import** (HR upload Excel → engine `registry_match` auto-verify user)
2. **OpsHub webhook callback** (refactor để dùng `Staff.GetRoot()` thay vì raw bson query)

User clarify thêm: *"thực ra là có đó. Rất nhiều luồng sử dụng root account để lưu vào audit. Chỉ là tôi ko nghĩ code lại sinh ra field đó"*

→ TCB/Ambassador **CŨNG có nhiều flow dùng root account** (webhook, cron, batch...) — chỉ là chưa có field `ActorType` để metadata phân biệt khi query audit log.

→ Vẫn là **gap thật** (TCB/Amb thiếu cải tiến field), nhưng:
- Không cấp bách như P0 ban đầu nghĩ
- Bug hiện tại chưa gây compliance issue (audit log vẫn ghi `actionBy` đúng, chỉ là không phân biệt được khi query)
- Reclassify **P2**: nice-to-have, làm khi có resource

### Bài học methodology (sai 2 lần liên tiếp ở gap này)

**Sai lần 1**: Mark P0 mà không hỏi business context của vCreator (commit message nói rõ feature gì).

**Sai lần 2**: Sau khi biết context vCreator (HR import), vội vàng kết luận TCB/Amb không có business need → suggest P3/remove. Nhưng thực ra **TCB/Amb cũng có flow root account** (webhook, cron) đã tồn tại, chỉ chưa được categorize trong audit.

**Pattern sai chung**: Tôi đoán business context dựa trên **commit message của 1 feature**, không hỏi user về flow rộng hơn của target project. User ngồi cùng codebase nhiều năm → biết rõ root account được dùng nhiều chỗ.

**Cần thêm layer trước khi classify priority**:
1. Code tồn tại ở source
2. Code được gọi ở source
3. Runtime business dùng ở source
4. **Hỏi user về flow tương đương ở target project** ← thay vì đoán
5. Mới classify priority

### Khi nào revisit?

Upgrade P2 → P0/P1 nếu:
- Compliance team yêu cầu audit log phân biệt actor (SOX/SOC/ISO)
- Có incident query audit log không trace được automation flow
- Build feature mới ở TCB/Amb cần audit trace strict (vd: budget approval workflow)
