# Gap #1 — Withdraw flow 3 dự án khác nhau hoàn toàn (TCB/vCr cho user rút, Ambassador admin-driven)

> **Priority**: ⚪ **P3** (sau khi verify với business — không phải bug như tưởng ban đầu)
> **Source**: [semantic-diff-financial.md](../semantic-diff-financial.md)
> **Last verified**: 2026-05-07 (sau khi business clarify flow Ambassador)
> **Reclassified**: P1 → P3 (initial misclassification — chi tiết trong section "Lịch sử phân loại")

---

## TL;DR (đã verify lại 2026-05-07 — pattern phức tạp hơn ban đầu nghĩ)

**Cả 3 dự án đều admin-driven trong thực tế**. Endpoint `POST /withdraw` cho user tự rút tiền tồn tại ở TCB/vCr backend nhưng **KHÔNG component frontend nào gọi** (dead code).

### Bảng so sánh thực tế

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Ai thực sự khởi tạo withdraw?** | Admin batch (transfer_processing) | Admin batch (transfer_processing) | Admin batch (transfer_processing) |
| **Backend public API `POST /withdraw`?** | ✅ exists | ✅ exists | ❌ KHÔNG có |
| **Frontend service `withdrawCash()` wrapper?** | ✅ exists | ✅ exists | ✅ exists (orphan!) |
| **Frontend page `/bank` UI** | "Bạn chưa đến kỳ thanh toán" + history (read-only) | Tương tự TCB | Tương tự TCB |
| **Caller của `withdrawCash()` trong pages** | **0** (dead) | **0** (dead) | **0** (dead, lại còn không có endpoint backend) |
| **Bank validation trong service layer** | `pkg/public/service` validate (dead path) | Duplicate cả 2 layer (dead path) | Comment out trong `internal/service` |
| **Bank info lưu trong WithdrawRaw schema** | ❌ đã xóa | ✅ lưu khi admin tạo | 🟡 schema còn nhưng không populate |
| **Tích hợp Accesstrade econtract** | ✅ `service_tos` (TOS 2-way sync) | ✅ `core` (mục đích chưa verify đủ) | ✅ `core` (econtract 1-way pull) |
| **Trigger thực tế xử lý tiền** | Admin batch → external TOS | Admin batch | Admin bấm "Process transfer" → external econtract |

**Gap thực sự (3 layer)**:
1. **Dead code endpoint** ở TCB/vCr — backend `POST /withdraw` + frontend service wrapper tồn tại, không ai gọi → đề xuất xóa hẳn
2. **3 architecture cùng nghiệp vụ "trả tiền"** — admin batch ở 3 dự án vẫn dùng pattern khác nhau (transfer_processing.go là duplicate code chưa unify)
3. **Ambassador legacy code chưa cleanup**: comment-out (không xóa hẳn) + schema `WithdrawRaw` còn 5 fields bank không dùng + frontend `services/withdraw.ts` orphan (gọi endpoint backend không tồn tại)

---

## Bằng chứng 3 dự án đều dead code endpoint

### Verify trên frontend (toàn bộ pages folder)

```bash
# Đếm số nơi GỌI withdrawCash() trong pages — không tính file định nghĩa và interface
grep -r "withdrawCash" techcombank/frontend/src/pages/ → 0 kết quả
grep -r "withdrawCash" vcreator/frontend-green/src/pages/ → 0 kết quả
grep -r "withdrawCash" ambassabor/frontend/src/pages/ → 0 kết quả
```

### `pages/bank/index.tsx` ở 3 dự án

Tất cả render giống nhau:
```tsx
// Chỉ có 2 component được render
<EmptyWithdraw />   // "Bạn chưa đến kỳ thanh toán" — placeholder static
<CashflowList />    // History list (chỉ XEM)
```

→ **Không có nút "Rút tiền"** ở trang bank của bất kỳ sản phẩm nào.

### Component `EmptyWithdraw` ở TCB

```tsx
function EmptyWithdraw({}) {
  return (
    <CommonEmpty icon={<MoneyTimeIcon />} title="Bạn chưa đến kỳ thanh toán" />
  );
}
```

→ Static text. Không có button. Không có form. Không trigger withdraw.

### Backend endpoint `POST /withdraw` ở TCB

```go
// @router /withdraw [post]
func (w withdrawImpl) Create(c echo.Context) error {
    payload := cc.Get(constants.KeyPayload).(request.WithdrawCashBody)
    userId  := cc.GetCurrentUserID()
    s := service.Withdraw()
    requestId, statistic, err := s.Create(ctx, userId, payload)
    // ...
}
```

→ Handler này nhận user-initiated request nhưng **không có ai gọi từ frontend**. Có thể:
- Mobile app gọi (unlikely vì TCB chỉ có web frontend hiện tại)
- Admin tools gọi qua đường khác (cần verify)
- Là legacy từ thời feature "user tự rút" được implement nhưng business yêu cầu disable UI sau đó

→ **Đề xuất xóa endpoint** sau khi verify không có client nào còn gọi.

---

## Business flow thực tế của 3 dự án (đã sửa)

### TCB — Admin batch driven (có dead code endpoint từ feature cũ)

**Flow thực tế**:
```
User → eKYC → link bank card → ký TOS qua tos-ambassador.koc.com.vn (service_tos)
   ↓
[User KHÔNG có nút "Rút tiền" trong UI — chỉ thấy "Bạn chưa đến kỳ thanh toán"]
   ↓
─── Admin side ───
   ↓
Admin tạo Transfer batch → bấm Process → pkg/admin/service/transfer_processing.go
   ↓
Sinh WithdrawRaw cho user đủ điều kiện (cash remaining ≥ threshold + contract SIGNED)
   ↓
tos_sync_helper.UpdateWithdrawSyncStatus() — push withdraw lên TOS, sync 2-way status
```

**Dead code path (tồn tại nhưng không dùng)**:
```
[Frontend service withdrawCash() — exported nhưng 0 caller trong pages]
        ↓
POST /withdraw → pkg/public/handler/withdraw.go (Create)
        ↓
pkg/public/service/withdraw.go.Create():
   - checkUserBankCardValid()
   - validate bank/branch
   - call internalservice.Withdraw().Create()
        ↓
internal/service/withdraw.go (290 LOC engine)
        ↓
Insert WithdrawRaw (schema đã xóa 5 fields bank)
```

→ Code path này **có thể không bao giờ được triệu gọi** trong production. Cần verify có client mobile/external gọi không.

**Đặc điểm TCB**:
- `WithdrawRaw` model **đã xóa hẳn** 5 fields `Bank/CardNumber/Branch...` — bank info chỉ ở UserBankCard collection, lookup khi cần
- Architecture 2 layer rõ ràng (internal engine vs pkg/public với validation)
- Có dead code endpoint cần dọn

### vCreator — Admin batch driven (legacy duplicate code)

**Flow thực tế** (giống TCB):
```
User → eKYC → link bank card
   ↓
[Page /bank chỉ hiển thị "Bạn chưa đến kỳ thanh toán"]
   ↓
Admin tạo Transfer batch → Process → sinh WithdrawRaw cho user đủ điều kiện
```

**Dead code path** giống TCB (có endpoint + frontend service wrapper, 0 caller pages).

**Đặc điểm vCreator**:
- Bank validation **duplicate** ở cả `pkg/public/service` và `internal/service` (336 LOC)
- `WithdrawRaw` model vẫn lưu 5 fields bank info → khác TCB (đã xóa schema)
- Cùng pattern dead code endpoint với TCB

### Ambassador — Admin-initiated transfer batch (no user withdraw)

```
User mở app → eKYC → link bank card
   ↓
User ký contract `B2C_AMBASSADOR` qua hệ thống external (econtract-service)
   ↓
[User KHÔNG có thao tác rút tiền — không có public withdraw endpoint]
   ↓
─── Admin side ───
   ↓
Admin tạo Transfer batch (loại "transfer" thay vì "withdraw")
   ↓
Admin bấm "Process transfer" → pkg/admin/handler/transfer.go
   ↓
pkg/admin/service/transfer_processing.go:
   - Loop tất cả users (banned=false)
   - Với mỗi user: gọi external API
       core.Client() → GET /econtract-service/api/v1.0/pub/contract
       với sso_id = user.Accesstrade.ID, contract_type = "B2C_AMBASSADOR"
   - Check status == "SIGNED" → bỏ qua nếu chưa ký
   - Match condition: cashRemaining ≥ MinValueCashRemaining
   - generateWithdraw(user):
       - cashRemaining = CashFlow.GetPartnerRemaining()
       - call internalservice.Withdraw().Create(user, body) với UserBankCardID="" (rỗng!)
   ↓
internal/service/withdraw.go (336 LOC):
   - check remaining cash
   - bank validation ĐÃ COMMENT OUT (không cần — KYC đã verify trước)
   - insert WithdrawRaw (5 fields bank để trống vì payload không có)
   - insert CashFlow
   ↓
WithdrawRaw status=Pending → admin tool tiếp tục push qua external system
```

**Đặc điểm Ambassador**:
- **KHÔNG có public withdraw API** (không có file `pkg/public/handler/withdraw.go` lẫn `pkg/public/service/withdraw.go`)
- `internal/service/withdraw.go` chỉ được gọi **từ 1 chỗ duy nhất**: `pkg/admin/service/transfer_processing.go` (admin batch)
- Tích hợp external **2 hệ thống**:
  - `econtract-service` để verify contract đã ký
  - `Accesstrade SSO` để link user (`user.Accesstrade.ID`)
- `userBankCardId = ""` được truyền vào withdraw → service không cần validate (admin xử lý sau dùng bank từ KYC user)
- Comment-out trong code = developer **xóa cẩu thả** chứ không phải bug logic

---

## Lưu ý quan trọng: 3 module Accesstrade khác nhau (đừng nhầm)

Cả 3 dự án đều integrate Accesstrade ecosystem, **dùng các microservice khác nhau** cho mục đích khác nhau:

| Module | Sản phẩm dùng | Mục đích | Auth | Liên quan withdraw? |
|---|---|---|---|---|
| **`atcore`** (at-core proxy → influence-meter) | TCB | Enrich influencer profile (followers, engagement rate, avatar) | `X-Partner-ID` + `X-API-Key` | ❌ KHÔNG (chỉ enrichment) |
| **`service_tos`** (Accesstrade TOS / econtract) | TCB | Generate authorize code → user redirect ký TOS qua website ngoài; sync withdraw status với TOS | HMAC-SHA256 | ✅ CÓ (push withdraw + sync 2-way) |
| **`core`** (Accesstrade econtract trực tiếp) | Ambassador | SSO + check contract `SIGNED`; eKYC integration | HMAC-SHA256 | ✅ CÓ (verify contract trước khi tạo withdraw) |

### TCB econtract flow (T-Fluencers)
```
User click "Ký TOS" trong app
   ↓
Backend gọi service_tos.GenerateAuthorizeCode()
   → return RedirectURL = https://tos-ambassador.koc.com.vn/...?code=XXX
   ↓
User mở website ngoài → ký contract → website redirect lại app
   ↓
Backend webhook nhận status update → cập nhật user.ContractTOS.Status = "SIGNED"
   ↓
Sau này khi withdraw process:
   tos_sync_helper.UpdateWithdrawSyncStatus() — push withdraw lên TOS, nhận lại status
```

### Ambassador econtract flow
```
User ký contract qua flow khác (cần verify thêm — có thể cũng redirect)
   ↓
Admin tạo Transfer batch → Process
   → core.Client() pull GET /econtract-service/api/v1.0/pub/contract
   → check contracts có status="SIGNED" và type="B2C_AMBASSADOR"
   → nếu có → generateWithdraw cho user
```

### Khác biệt cốt lõi giữa TCB vs Ambassador econtract integration

| Khía cạnh | TCB `service_tos` | Ambassador `core` |
|---|---|---|
| User trigger ký? | ✅ User click trong app, app gọi backend gen URL → mở website | (chưa verify, có thể tương tự hoặc khác) |
| Sync direction | 2-way (push withdraw + receive status) | 1-way (chỉ pull contract status) |
| Endpoint | `tos-ambassador.koc.com.vn` (TOS service) | `/econtract-service/...` |
| Withdraw push to TOS | ✅ `UpdateWithdrawSyncStatus` | ❌ |
| Status enum | 9 statuses (SUBMIT, WAITING_TO_SIGN, SIGNED, REJECT, ...) | (có status SIGNED, chưa verify đầy đủ) |
| User ký TOS có ảnh hưởng withdraw không? | ✅ User phải có `ContractTOS.Status=SIGNED` mới được rút? (cần verify) | ✅ Admin transfer batch chỉ chọn user có contract `SIGNED` |

→ **TCB integrate Accesstrade econtract SÂU HƠN Ambassador** (2-way sync vs 1-way pull). Đây là gap kiến trúc nhưng CÓ chiều ngược: Ambassador có thể học từ TCB cách push withdraw → TOS để có audit trail đầy đủ hơn.

### Khi đề cập "Accesstrade integration" cần phân biệt rõ:
- ❌ "TCB không có Accesstrade integration" → SAI
- ❌ "TCB không integrate Accesstrade trong withdraw flow" → SAI (có via `service_tos`)
- ❌ "vCreator chưa integrate Accesstrade ở backend" → SAI (có `internal/module/core/` + `UserRaw.AT` field)
- ✅ **Cả 3 sản phẩm đều integrate Accesstrade** nhưng dùng các module/microservice khác nhau:
  - TCB: `atcore` (enrichment) + `service_tos` (TOS 2-way sync)
  - vCreator: `core` (cùng tên module với Ambassador, mục đích cần verify thêm)
  - Ambassador: `core` (econtract + SSO + eKYC)
- ✅ vCreator + Ambassador có cùng module `internal/module/core/` (likely fork chung) nhưng use case có thể khác (vCreator là B2B workplace, dùng SSO Accesstrade cho gì?)

---

## Sự thật về "5 fields bank info bị comment"

**Đây là code legacy chưa cleanup**, không phải bug:

```go
// ambassabor/backend/internal/service/withdraw.go:108-112
// 5. Check bank valid
// userBankCard, bank, branch, _ := w.scheckUserBankCardValid(ctx, body)
// if err != nil {
//     return nil, err
// }
```

**Bằng chứng đây là intentional + cleanup chưa xong**:

1. **TCB đã xóa hẳn** (file 290 LOC vs Ambassador 336 LOC):
   - Comment block bị comment trong Ambassador → TCB **xóa luôn**, thay bằng comment dương `// 5. Data payload transaction (no bank validation needed)`
   - 5 fields trong `WithdrawRaw` model: TCB **xóa khỏi schema**, Ambassador giữ nguyên

2. **`transfer_processing.go:123-129`** cũng có pattern y hệt — comment out fetch UserBankCard:
   ```go
   // _ = daomongodb.UserBankCardDAO().GetShare().FindOne(ctx, userBankCard, bson.M{
   //     "user":      user.ID,
   //     "isDefault": true,
   // })
   // if userBankCard.ID.IsZero() {
   //     return nil
   // }
   ```
   → 2 file độc lập đều comment out cùng pattern → có chủ ý, không phải bug

3. **Typo `scheckUserBankCardValid`** (thừa "s") → cleanup không kỹ, nhưng không gây runtime error (vì code đã được comment)

→ **Conclusion**: Ambassador không có bug. Nhưng có **2 cleanup tasks** hợp lý:
- Xóa hẳn comment block + hàm `checkUserBankCardValid` không dùng (giảm 35 LOC code chết)
- Migrate schema `WithdrawRaw` xóa 5 fields bank info nếu confirm không dùng

---

## Gap thật sự (không phải bug)

### Gap A: Architecture không thống nhất giữa 3 dự án

3 dự án có **3 architecture pattern khác nhau** cho cùng 1 nghiệp vụ "trả tiền cho creator":
- TCB: 2 layer clean (engine + entry-point)
- vCreator: 2 layer nhưng duplicate validation
- Ambassador: chỉ 1 layer (engine), entry-point qua admin batch + external API

→ Hệ quả: không thể có **shared lib withdraw** được. Mỗi product phải maintain riêng.

### Gap B: Ambassador legacy code chưa cleanup

| Item | Hiện tại | Đề xuất |
|---|---|---|
| Comment block trong `internal/service/withdraw.go:108-112` | 5 dòng comment + typo "scheck..." | Xóa hẳn, thay bằng comment giải thích "Ambassador không cần bank validation ở đây — KYC đã verify, transfer batch xử lý sau" |
| Hàm `checkUserBankCardValid` trong file | Còn nguyên 30 LOC, không ai gọi | Xóa nếu confirm không dùng |
| `WithdrawRaw` model 5 fields bank | Còn trong schema, records mới insert toàn null | Verify với business: có còn ý nghĩa cho admin tool tương lai không. Nếu không → migration xóa. |
| Comment block trong `transfer_processing.go:123-129` | Tương tự | Cleanup cùng dịp |

### Gap C: vCreator có duplicate validation

vCreator validate bank **2 lần** (cả `pkg/public/service` lẫn `internal/service`). Performance impact thấp nhưng là code smell.

→ Refactor vCreator giống TCB: chỉ validate ở `pkg/public/service`, `internal/service` thuần engine.

---

## Action items (đã update với picture đúng)

### Verify trước khi xóa dead code (effort: 1 ngày, P3)

1. **Check có client mobile/external nào gọi `POST /withdraw` không** ở TCB và vCr:
   - Grep trong code mobile app (nếu có repo riêng)
   - Check API gateway/CDN logs production xem endpoint có request thật không
   - Nếu = 0 request trong N tháng → confirm dead code

### Cleanup TCB & vCr (effort: 1-2 ngày, P3)

Sau khi confirm dead code:

2. **Xóa endpoint `POST /withdraw`** (TCB + vCr):
   - Backend: xóa `pkg/public/handler/withdraw.go` (Create method) + `pkg/public/service/withdraw.go` Create flow
   - Frontend: xóa `services/withdraw.ts` (`withdrawCash` function) + interface + API const
3. **Loại bỏ duplicate validation** trong vCreator `internal/service/withdraw.go` (sau khi đã xóa user-driven flow, không cần check bank ở engine layer)

### Cleanup Ambassador (effort: <1 ngày, P3)

4. **Xóa orphan frontend service**: `ambassabor/frontend/src/services/withdraw.ts` đang gọi endpoint không tồn tại → xóa hẳn
5. **Xóa hẳn comment block** + hàm `checkUserBankCardValid` không dùng trong `internal/service/withdraw.go`
6. **Xóa comment block** trong `pkg/admin/service/transfer_processing.go:123-129`
7. **Thêm comment giải thích flow** (cho dev tương lai không confuse)

### Schema migration (effort: medium, P3 nhưng cần migration plan)

8. **vCreator + Ambassador**: verify với business `WithdrawRaw.Bank/CardNumber/Branch` có ý nghĩa gì không
   - Nếu admin xử lý batch lookup từ UserBankCard runtime → có thể xóa 5 fields, theo TCB
   - Nếu cần snapshot bank info tại thời điểm withdraw (audit) → giữ nguyên, document lý do

### Strategic decision (P2 — cần PM)

9. **Thống nhất admin batch flow giữa 3 dự án**:
   - 3 dự án có 3 file `transfer_processing.go` riêng biệt nhưng cùng pattern
   - Pro thống nhất: shared lib, dễ maintain
   - Con: TCB tích hợp service_tos, Ambassador tích hợp econtract — không thể merge 100%
   - Đề xuất: extract common skeleton, mỗi dự án inject integration adapter riêng

10. **Có nên expose lại "user tự rút tiền"** trong tương lai không?
    - Nếu có → revive endpoint + build UI nút "Rút tiền"
    - Nếu không → xóa hẳn, đỡ tech debt

---

## Lịch sử phân loại (3 lần update)

### Lần 1 (2026-05-07 sáng): Đánh giá ban đầu — SAI
- Priority: 🟠 P1 (Total 15)
- Claim: "Ambassador thiếu bank validation = bug critical 60%"
- Sai vì: chỉ đọc 1 file, chưa check call graph

### Lần 2 (2026-05-07 chiều): Sau khi business clarify Ambassador admin-driven — VẪN SAI 1 PHẦN
- Priority: ⚪ P3
- Claim: "TCB/vCr cho user tự rút, Ambassador admin-driven"
- Sai vì: chỉ check existence của endpoint, không check **caller** ở frontend

### Lần 3 (2026-05-07 tối): Sau khi user catch "frontend không có UI rút tiền" — ĐÃ ĐÚNG
- Priority: ⚪ P3 (giữ nguyên)
- Insight mới: **Cả 3 dự án đều admin-driven trong thực tế**. TCB/vCr có endpoint + frontend service nhưng **0 caller** trong pages → dead code legacy
- Direction action: chuyển từ "fix Ambassador" sang "**cleanup dead code TCB/vCr + cleanup legacy Ambassador**"

### Bài học methodology (cập nhật mỗi sai lầm)

| Sai | Bài học |
|---|---|
| Đọc 1 file → kết luận bug | Phải check call graph (handler → service → engine) |
| Check existence endpoint → kết luận flow active | Phải check **caller** (grep "withdrawCash" trong pages, không chỉ trong services/) |
| Compare 3 dự án theo file mà không xem **runtime behavior** | Cần xem cả frontend UI có thật sự trigger không |

→ Khi compare cross-product cho mục đích "gap analysis", phải verify ở **3 layer**: code tồn tại / code được gọi / business thực tế dùng.

---

## Files referenced

**TCB** (refactored, 2-layer clean):
- `pkg/public/handler/withdraw.go` — HTTP handler (52 LOC)
- `pkg/public/service/withdraw.go` — public flow + validation (279 LOC)
- `internal/service/withdraw.go` — engine no-bank (290 LOC)
- `internal/model/mg/withdraw.go` — schema **không có** 5 fields bank

**vCreator** (legacy, validation duplicate):
- `pkg/public/handler/withdraw.go` (52 LOC)
- `pkg/public/service/withdraw.go` (279 LOC)
- `internal/service/withdraw.go` (336 LOC, có duplicate validation)
- `internal/model/mg/withdraw.go` — schema **có** 5 fields bank

**Ambassador** (admin-driven, không có public withdraw):
- ❌ KHÔNG có `pkg/public/handler/withdraw.go`
- ❌ KHÔNG có `pkg/public/service/withdraw.go`
- `pkg/admin/service/transfer_processing.go:118-153` — `generateWithdraw()` được gọi từ admin batch
- `internal/service/withdraw.go` (336 LOC, comment out validation, identical skeleton với vCr)
- `internal/model/mg/withdraw.go` — schema **có** 5 fields bank (legacy)
- Integration: `econtract-service` (B2C_AMBASSADOR contract) + Accesstrade SSO
