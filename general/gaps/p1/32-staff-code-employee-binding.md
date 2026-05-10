# Gap #32 — Concept "mã nhân viên + binding partner" — TCB đơn giản, vCreator chi tiết hơn nhiều, Ambassador chưa có

> **Priority**: 🟠 **P1** (reclassified P2→P1 2026-05-07)
> **Source**: Tách từ gap #13 (2026-05-07)
> **Direction port**: vCreator → TCB (extend) + vCreator → Ambassador (port full)
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Trong các campaign B2B (banking partner, brand partner), creator đăng ký nền tảng cần **link với mã nhân viên** của partner để verify "user này là nhân viên thật của bank/company".

**Hiện trạng 3 sản phẩm**:

### TCB — Concept "ManageCode" đơn giản
- Admin pre-create danh sách mã (vd: "EMP001", "EMP002") trong collection `manage_code`
- User đăng ký với mã staff → backend check mã có tồn tại không + chưa được dùng
- Nếu hợp lệ → bind user với partner
- **Đặc điểm**: rất basic — chỉ có code, không có thông tin nhân viên (tên, phone, workplace)

### vCreator — Concept "EmployeeRegistry" rất chi tiết
- Admin import file Excel từ HR Vin với **18 fields** mỗi nhân viên: code, fullName, phone, workplace 3 cấp (Brand → Company → Unit), workplace group, status (active/terminated), import history
- Có **match engine** với 10 actions xử lý mọi case: auto_verified, mismatch_phone, mismatch_code, terminated, transferred, ambiguous, ...
- Có theo dõi import history (mỗi lần HR upload file mới = 1 import batch)
- Có canonicalize workplace name từ master list

→ vCreator **chi tiết hơn TCB rất nhiều** — đây là feature ra đời từ business need thật của Gen-Green/VinFast (HR Vin upload danh sách nhân viên định kỳ).

### Ambassador — Chưa có gì
- Có concept Partner nhưng KHÔNG có mã nhân viên / employee registry
- Creator không có cách link với "tôi là nhân viên Anker" (vd) ở backend layer

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB (`ManageCode`) | vCreator (`EmployeeRegistry`) | Ambassador |
|---|:---:|:---:|:---:|
| **Có khái niệm "mã nhân viên" để bind partner?** | ✅ Có (đơn giản) | ✅ Có (chi tiết) | ❌ Không |
| **Lưu thông tin nhân viên (tên, phone, workplace)?** | ❌ Chỉ có code | ✅ Đầy đủ 18 fields | — |
| **Workplace hierarchy (Brand→Company→Unit)?** | ❌ | ✅ 3 tier | — |
| **Import từ HR (file Excel)?** | ❌ Admin tạo từng code | ✅ Bulk import + tracking | — |
| **Match engine xử lý các case edge?** | ❌ Chỉ check code tồn tại | ✅ 10 actions (mismatch, terminated, transferred, ambiguous...) | — |
| **Theo dõi nhân viên đã rời công ty (terminated)?** | ❌ | ✅ Có status terminated | — |
| **Theo dõi import history (lần nào, ai upload)?** | ❌ | ✅ Có | — |
| **Audit ai duyệt bind (auto vs manual)?** | 🟡 Có audit cơ bản | ✅ Đầy đủ với ActorType (xem gap #5) | — |

## Hệ quả khi không unify

1. **Ambassador không có concept** → khi onboarding partner mới (vd: Anker, Yody, VNPay), không có cách verify creator là nhân viên thật → phải làm manual check ngoài hệ thống
2. **TCB stuck với pattern cũ** → khi banking partner muốn workflow chi tiết hơn (vd: phân quyền theo workplace, track terminated employees), không có support
3. **Maintenance lệch** → vCreator team đang invest vào feature này (đã có 18 fields, match engine, ActorType...). TCB và Ambassador thiếu → khi business request feature mới ở 2 sản phẩm, phải build lại từ đầu

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: vCreator là **source of truth** cho concept này. Direction port:
- **vCreator → Ambassador**: port full (Ambassador hoàn toàn thiếu)
- **vCreator → TCB**: port để unify với pattern chi tiết hơn (TCB hiện chỉ có ManageCode đơn giản, có thể giữ song song hoặc migrate)

**Lý do chọn vCreator làm chuẩn**:
- vCreator đã có **18 fields chi tiết**, đầy đủ flow workplace 3-tier
- Match engine của vCreator đã handle 10 cases edge — production tested
- Pattern này là kết quả của business iteration cho Gen-Green/VinFast (B2B partner phức tạp)
- TCB ManageCode chỉ là subset — chưa đáp ứng các case như "nhân viên đã rời công ty", "nhân viên chuyển workplace"

**Effort dự kiến**:
- **Ambassador port full** (~1-2 tuần): tạo schema mới + admin import + match engine
- **TCB extend** (~1 tuần): thêm fields chi tiết vào ManageCode hoặc tạo song song EmployeeRegistry, cần migration data nếu có records cũ

**Cần product/business confirm trước khi triển khai**:
1. **Ambassador**: có nhu cầu link creator với HR data của partner không? (vd: Anker upload list employees → creator đăng ký = nhân viên thật)
2. **TCB**: có muốn migrate ManageCode → EmployeeRegistry pattern không? Hay giữ song song (ManageCode cho campaign cũ + EmployeeRegistry cho campaign mới)?
3. Ambassador HR file format giống vCreator (Excel với cùng schema) hay format riêng cho mỗi partner?
4. Có nên port luôn ActorType audit (gap #5) cùng với feature này không? (vCreator đã có ActorType vì context HR import — port chung sẽ tự nhiên hơn)
5. Workplace hierarchy 3-tier (Brand→Company→Unit) có phù hợp với Ambassador/TCB không?

→ Nếu **chỉ Ambassador có nhu cầu** → priority có thể tăng lên P1. Nếu cả 2 đều không có demand cụ thể → giữ P2.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

3 sản phẩm có 3 trạng thái:
- **vCreator**: stack đầy đủ — model `EmployeeRegistryRaw` (18 fields), service `registry_match` với 10 ChangeActions, admin import flow với tracking, master `workplace_units` collection, ActorType audit
- **TCB**: minimal — model `ManageCodeRaw` (9 fields), check tồn tại đơn giản trong `pkg/public/service/user.go`, không có match engine
- **Ambassador**: KHÔNG có gì

## Verify code

### vCreator (full implementation)

**Model `internal/model/mg/employee_registry.go`** (18 fields):
```go
type EmployeeRegistryRaw struct {
    ID, EmployeeCode AppID, string  // unique, mọi format
    FullName, Phone string  // phone normalized
    WorkplaceName string  // raw từ Excel, canonicalized
    WorkplaceBrandCode/Name, WorkplaceCompanyCode/Name, WorkplaceUnitCode/Name string
    WorkplaceGroup string  // = BrandCode (rule mặc định, HR custom)
    Status string  // "active" | "terminated"
    GenGreenUserID *AppID  // link đến UserRaw nếu đã match
    ImportedAt time.Time
    ImportID, LastSeenImportID string
    CreatedAt, UpdatedAt time.Time
}
```

**Service `internal/service/registry_match.go`** (445 LOC):
```go
type ChangeAction string  // 10 values
const (
    ActionAutoVerified    // code+phone match → auto verify user
    ActionMismatchCode    // phone match nhưng code không
    ActionMismatchPhone   // code match nhưng phone không
    ActionTerminated      // employee đã terminated
    ActionTransferred     // employee chuyển workplace
    ActionAmbiguous       // nhiều match
    ActionNewEmployee     // chưa có user, chỉ là registry
    ActionDeleted         // remove khỏi registry mới
    ActionUnchanged       // no change
    ActionInvalid         // input invalid
)

// Surface
MatchEngine() // factory
GenerateChanges(ctx, []MatchRow, importID)  // bulk match cho admin import V2
LookupSingle(ctx, code, phone)  // single lookup cho public register hook
```

**Admin import flow**:
- `pkg/admin/handler/employee_registry.go` — POST endpoint nhận file Excel
- `pkg/admin/service/employee_registry.go` — parse Excel → match engine → preview changes → admin confirm → apply

### TCB (minimal)

**Model `internal/model/mg/manage_code.go`** (9 fields):
```go
type ManageCodeRaw struct {
    ID, Partner AppID
    Type, Code string
    IsUsed bool
    UsedBy AppID
    UsedAt, CreatedAt, UpdatedAt time.Time
}
```

**Caller `pkg/public/service/user.go:212-220`**:
```go
if config.GetENV().IsValidateStaffCodeExists {
    var manageCode = new(modelmg.ManageCodeRaw)
    _ = daomongodb.ManageCodeDAO().GetShare().FindOne(ctx, manageCode, bson.M{
        "partner": partner.ID,
        "code":    body.Code,
        "type":    constants.ManageCodeApplyForEmployee,
    })
    if manageCode.ID.IsZero() {
        return errors.New(locale.ReferralKeyCodeInvalid)
    }
}
```

→ Chỉ check tồn tại, không có thông tin nhân viên đi kèm, không có match engine.

### Ambassador (không có gì)

```bash
ls ambassabor/backend/internal/model/mg/ | grep -iE "employee|manage_code|registry" → 0 results
```

→ Chưa có concept này.

## Đề xuất implementation

### Phase 1: Ambassador port full (~1-2 tuần)

1. **Schema migration**: tạo collection `employee_registry` với 18 fields giống vCreator. Optional: tạo master `workplace_units`
2. **Service port**: copy `registry_match` từ vCreator (~445 LOC), adapt với business model Ambassador (không có workplace 3-tier nếu Ambassador partner không cần)
3. **Admin handler**: import Excel + match preview + apply changes
4. **Public service hook**: khi user đăng ký với staff code → lookup registry, auto-verify nếu match
5. **Migration data**: không có data cũ → start fresh

**Question for Ambassador**: workplace 3-tier (Brand→Company→Unit) có phù hợp không? Anker/HDBank/etc có cấu trúc tương đương Vin không, hay cần adapt?

### Phase 2: TCB extend hoặc migrate (~1 tuần)

**Option A — Migrate ManageCode → EmployeeRegistry**:
- Migration data: `manage_code` records → `employee_registry` records (chỉ có `code`, các fields khác để empty)
- Refactor caller `pkg/public/service/user.go:212` để dùng EmployeeRegistry thay vì ManageCode
- Risk: existing admin tools cho ManageCode bị break

**Option B — Giữ song song (recommended)**:
- Giữ `manage_code` collection cho legacy use cases
- Thêm `employee_registry` collection cho campaign mới muốn pattern chi tiết
- Caller check cả 2 collections (manage_code first, fallback employee_registry, hoặc ngược lại)
- Tạo flag config per-campaign: `useEmployeeRegistry: bool`

→ Đề xuất **Option B** cho TCB — giảm risk migration, ops team có thể quyết định dùng pattern nào per campaign.

### Phase 3: Combine với gap #5 ActorType (~tied)

vCreator EmployeeRegistry import flow đã sử dụng ActorType audit (root_account khi import từ Excel). Khi port sang TCB/Ambassador, port luôn ActorType (gap #5) cho consistency.

## Risks + mitigations

1. **Workplace 3-tier có thể không fit Ambassador** → Anker/HDBank có thể không có concept "Brand → Company → Unit" giống Vin
   - **Mitigation**: Ambassador có thể làm flat (không có hierarchy) hoặc 1-tier (chỉ có Workplace name) — tùy partner
2. **TCB Option B duplicate data** → cùng concept tồn tại 2 collections
   - **Mitigation**: chỉ dùng cho campaign mới, không migrate cũ → không tăng data legacy
3. **Match engine vCreator có 10 ChangeActions có thể overkill cho Amb** → simplify nếu không cần
   - **Mitigation**: port subset (5-6 actions cơ bản: AutoVerified, Mismatch, NewEmployee, Unchanged, Invalid)

## Files referenced

**vCreator (source of truth)**:
- `internal/model/mg/employee_registry.go` — 18 fields chi tiết
- `internal/model/mg/workplace_unit.go` (nếu có) — master workplace
- `internal/service/registry_match.go` — engine 10 ChangeActions
- `pkg/admin/handler/employee_registry.go` — import Excel handler
- `pkg/admin/service/employee_registry.go` — preview + apply flow
- `pkg/public/service/user.go` — register hook

**TCB (cần extend hoặc migrate)**:
- `internal/model/mg/manage_code.go` — 9 fields cơ bản
- `pkg/public/service/user.go:212-220` — check ManageCode tồn tại
- KHÔNG có match engine, không có import bulk

**Ambassador (cần port full)**:
- KHÔNG có collection liên quan
- KHÔNG có handler/service liên quan

## Lịch sử phân loại

- **2026-05-07 (gap #13 cũ)**: Thuộc gap #13 "Content moderation tools" — title misleading vì gộp 5 features khác nhau (trong đó có "staff code validate")
- **2026-05-07 (split)**: Tách thành gap #32 riêng. User confirm: *"có, cái này thành gap riêng và vCreator cũng có chức năng tương tự, còn chi tiết hơn cả TCB cơ (có cơ sở làm việc)"*
- **Direction port**: vCreator → Ambassador (port full) + vCreator → TCB (extend hoặc song song)
- **Liên quan gap khác**:
  - Gap #5 (ActorType) — port chung vì vCreator EmployeeRegistry dùng ActorType
  - Gap #22 (vCreator Workplace 3-tier — P3 KHÔNG port) — concept workplace hierarchy có thể dùng riêng cho vCreator hoặc selective port
  - Gap #23 (vCreator registry_match HR engine — P3 KHÔNG port) — **revoke P3 status**: gap #32 thực ra là gap này được rescope với business intent rõ ràng hơn

### Bài học methodology
- Initial gap-analysis có gap #23 mark "vCreator HR registry — KHÔNG port (vCreator-specific)" — **sai**
- Reality: vCreator pattern này quá tốt, **direction đúng là port qua 2 sản phẩm khác** thay vì keep isolated
- Khi gap original mark "X-only feature" cần verify: là **specific feature** (như Affiliate Ambassador) hay là **good pattern chưa được port**
