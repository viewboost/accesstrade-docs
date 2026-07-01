# PRD tổng thể: RASI + Auto-Withdraw (holding 60 ngày)

- **Ngày**: 2026-07-01
- **Trạng thái**: as-built (tổng hợp từ code thực tế trên branch `feature/rasi`)
- **Service liên quan**: `user`, `transaction`, `withdraw`, submodule dùng chung `external` (proto gRPC)
- **PRD tham khảo (đã lỗi thời một phần)**:
  - [2026-06-23-rasi-account-state-PRD.md](./2026-06-23-rasi-account-state-PRD.md)
  - [2026-06-23-auto-withdraw-60d-holding-PRD.md](./2026-06-23-auto-withdraw-60d-holding-PRD.md)

> **Lưu ý**: Đây là tài liệu **as-built** — mô tả đúng những gì code trên `feature/rasi` đang làm, không phải kế hoạch. Có một số điểm code đã **lệch so với 2 PRD gốc**; các điểm lệch quan trọng được liệt kê ở mục [Những điểm code lệch so với PRD gốc](#những-điểm-code-lệch-so-với-prd-gốc) để team review lại xem có phải là cố ý hay không.

---

## Problem Statement

Từ góc nhìn người dùng và vận hành, hệ thống cần giải quyết đồng thời ba vấn đề gắn với tính năng RASI:

1. **Người dùng không biết mình đã đủ điều kiện rút tiền hay chưa.** Để nhận tiền cashback về ngân hàng, người dùng phải có **tài khoản RASI** và đã **ký điều khoản (TOS)**. Nếu app không phân biệt được các tình huống (app cũ chưa hỗ trợ RASI / chưa đăng ký RASI / có RASI nhưng chưa ký TOS / đủ điều kiện), người dùng bị kẹt mà không biết vì sao.

2. **Người dùng phải tự bấm rút thủ công**, và tiền cashback vào số dư rút được ngay khi giao dịch chuyển sang `cashback`. Nhưng giao dịch gốc vẫn có thể bị hoàn/huỷ (reject/clawback) sau đó — dẫn tới tình huống "đã chi tiền rồi mới bị thu hồi", rất khó xử lý.

3. **Luồng chuyển tiền ra MBBank cần đi qua lớp communication tập trung** (proxy accesstrade), cần đối chiếu tài khoản người nhận (beneficiary), và cần cập nhật trạng thái bất đồng bộ qua webhook thay vì chỉ dựa vào response đồng bộ.

## Solution

Tính năng RASI gồm bốn khối, trải trên ba service:

### A. Trạng thái tài khoản RASI (`accountStats`) — service `user`
Khi SSO Auth, MBBank trả thêm `rasiAccountNumber` (STK RASI) và deeplink đăng ký RASI (`deeplinkRegisterRasiAccount` trong `clientAddInfo`). Service `user` lưu `rasiAccountNumber` vào DB, còn `rasiDeeplink` được nhúng vào **JWT** (sống 6 tháng) và chỉ tồn tại trong bộ nhớ (không lưu DB). Endpoint `/me` trả về một trường `accountStats` là **một trong 4 trạng thái** (`OK` / `REGISTER_RASI` / `SIGN_TOS` / `UPDATE_APP`); client tự switch theo trạng thái để điều hướng.

### B. Holding 60 ngày (age-gate) — service `transaction`
Mỗi giao dịch khi chuyển sang `cashback` được gắn `transferStatus = pending` và `estimateTransferAt = startOfDayHCM(orderTime + 60 ngày)`. Tiền đang trong holding được tính là **cash chờ** (`cashTransferWaiting`) — hiển thị nhưng chưa rút được. Một cronjob **03:00 HCM** hằng ngày "thả" các giao dịch đã đủ tuổi: đổi `transferStatus = success`, ghi audit vào collection `cash-transfer-tracking`, và gọi `UpdateUserStats` để cập nhật stats người dùng. `currentCash` ở service `user` tự co lại vì `transaction` trừ `cashTransferWaiting` khỏi `successCommission` khi trả về qua gRPC.

Nếu giao dịch bị **clawback** khi còn `pending`, hệ thống **ép `transferStatus = success` + `estimateTransferAt = đầu ngày hôm nay`** để executor thu hồi như tiền đã chi; nếu đã `success` thì giữ nguyên (không đụng `estimateTransferAt` cũ).

### C. Auto-withdraw — service `user` (scanner) + `withdraw` (thực thi)
Cronjob **05:00 HCM** (sau job thả tiền 03:00) ở service `user` quét user theo trang, lọc điều kiện đẩy xuống DB (không banned + có `rasiAccountNumber`), so `currentCash` với `minCash` động (lấy từ event service ICB, fallback env), rồi **publish NATS `CreateWithdraw`** với `mode = auto` và tài khoản nhận là `rasiAccountNumber`. Service `withdraw` consume message này và chạy `NewWithdraw` bất đồng bộ. Một user lỗi không chặn cả mẻ; có Redis lock chống chạy trùng và nhịp giãn cách chống spam MBBank.

### D. Luồng chuyển tiền qua communication + webhook — service `withdraw`
Khi bật `ENABLE_COMMUNICATION`, `NewWithdraw` chuyển tiền qua **communication service** (proxy accesstrade qua NATS) thay vì gọi MBBank trực tiếp. Trước khi chuyển, hệ thống tra cứu **beneficiary account** (từ DB, fallback query partner rồi lưu lại). Trạng thái withdraw được cập nhật **bất đồng bộ qua webhook** (NATS `UpdateTrancStatusFromWebhook`) và một **cronjob đồng bộ pending** định kỳ. Notification chỉ push cho mode `manual`/`auto`.

### Sơ đồ tổng thể — Kiến trúc 3 service + luồng dữ liệu

```mermaid
flowchart LR
    subgraph MB[MBBank SSO]
        SSO[/userInfo:<br/>rasiAccountNumber + deeplink/]
    end

    subgraph USER[Service user]
        Auth[SSO Auth<br/>lưu rasiAccountNumber DB<br/>rasiDeeplink → JWT]
        Me[GET /me<br/>ResolveAccountStats → 4 state]
        Scanner[[AutoWithdrawScanner<br/>cron 05:00 HCM]]
    end

    subgraph TXN[Service transaction]
        Hold[transferStatus pending/success<br/>+ estimateTransferAt]
        RelJob[[TransferReleaseRun<br/>cron 03:00 HCM]]
        Agg[AggregateUserStats<br/>trừ cashTransferWaiting]
    end

    subgraph WD[Service withdraw]
        NW[NewWithdraw<br/>manual / auto / batch]
        Comm[Communication branch<br/>proxy accesstrade]
        Bene[(beneficiary-accounts)]
        Webhook[[Webhook + cronjob<br/>sync pending]]
    end

    SSO --> Auth
    Auth --> Me
    RelJob -->|03:00| Hold
    RelJob -->|UpdateUserStats| Agg
    Scanner -->|"gRPC UserAggregateStats"| Agg
    Agg -->|currentCash đã age-gate| Scanner
    Scanner -->|"NATS CreateWithdraw mode=auto<br/>account=rasiAccountNumber"| NW
    NW --> Comm
    Comm -->|"NATS proxy"| PARTNER[MBBank / accesstrade]
    NW --> Bene
    PARTNER -.->|"webhook NATS"| Webhook
    Webhook --> NW
```

**Thứ tự thời gian trong ngày (giờ HCM):** `03:00` transaction thả tiền đủ tuổi → `05:00` user scanner quét & publish auto-withdraw → `08:00 & 14:00` withdraw đồng bộ trạng thái pending với partner.

---

## Chi tiết nghiệp vụ

### A. Trạng thái tài khoản RASI (`accountStats`)

**4 trạng thái** (service `user`, `app/model/user.go`):

| Điều kiện | `accountStats` | Ý nghĩa với client |
|---|---|---|
| Không có `rasiAccountNumber` **và** không có `rasiDeeplink` | `UPDATE_APP` | App cũ chưa hỗ trợ RASI → dẫn ra store cập nhật |
| Không có `rasiAccountNumber` **và** có `rasiDeeplink` | `REGISTER_RASI` | Mở `rasiDeeplink` để đăng ký RASI |
| Có `rasiAccountNumber` **nhưng** chưa ký TOS (`tos.status != completed`) | `SIGN_TOS` | Dẫn tới màn ký điều khoản |
| Có `rasiAccountNumber` **và** đã ký TOS | `OK` | Đủ điều kiện, cho rút bình thường |

Thứ tự ưu tiên: kiểm tra `rasiAccountNumber` trước → rồi tới TOS. Nguồn dữ liệu: `rasiAccountNumber` và `tos.status` đọc từ **DB**; `rasiDeeplink` đọc từ **JWT claims** (set vào context ở auth middleware). Ở `/me`, sau khi lấy `UserInfo` từ DB, controller gọi `SetRasiDeeplink(deeplink từ JWT)` để tính lại `accountStats` (đặc biệt phân biệt `UPDATE_APP` vs `REGISTER_RASI`).

#### Sơ đồ A1 — Cây quyết định `ResolveAccountStats`

```mermaid
flowchart TD
    Start([GET /me]) --> HasRasi{"Có rasiAccountNumber?<br/>(từ DB)"}
    HasRasi -->|Không| HasLink{"Có rasiDeeplink?<br/>(từ JWT)"}
    HasLink -->|Không| UA["UPDATE_APP<br/>→ client mở store cập nhật"]
    HasLink -->|Có| RR["REGISTER_RASI<br/>→ client mở rasiDeeplink đăng ký"]
    HasRasi -->|Có| HasTos{"tos.status == completed?<br/>(từ DB)"}
    HasTos -->|Không| ST["SIGN_TOS<br/>→ client dẫn tới màn ký TOS"]
    HasTos -->|Có| OK["OK<br/>→ cho rút bình thường"]
```

#### Sơ đồ A2 — Luồng RASI trong SSO Auth và `/me`

```mermaid
sequenceDiagram
    participant App as Client app
    participant MB as MBBank SSO
    participant U as Service user
    participant DB as MongoDB
    participant JWT as JWT (6 tháng)

    App->>U: SSO Auth (token MBBank)
    U->>MB: AuthMBBankWithToken
    MB-->>U: rasiAccountNumber + clientAddInfo[deeplinkRegisterRasiAccount]
    U->>DB: lưu rasiAccountNumber (persistent)
    U->>JWT: nhúng rasiAccountNumber + rasiDeeplink
    JWT-->>App: access token

    App->>U: GET /me (Bearer JWT)
    Note over U: middleware: đọc rasiDeeplink từ JWT → context
    U->>DB: đọc rasiAccountNumber, tos.status (tươi)
    Note over U: SetRasiDeeplink(deeplink) → ResolveAccountStats
    U-->>App: { accountStats, rasiDeeplink, rasiAccountNumber, ... }
```

### B. Holding 60 ngày

**HoldingClock** (thuần hàm, timezone `Asia/Ho_Chi_Minh`):
- `HoldingDays()`: đọc env `TRANSACTION_HOLDING_DAYS`, mặc định **60**.
- `EstimateTransferAt(orderTime) = startOfDayHCM(orderTime + HoldingDays)`.
- `IsMatured(estimateAt, now) = estimateAt <= startOfDayHCM(now)`.

**Trạng thái `transferStatus` trên chính document transaction** (không dùng bảng ledger riêng):
- `pending`: đang trong holding → tính vào `cashTransferWaiting`, KHÔNG nằm trong `currentCash`.
- `success`: đã thả (qua job hằng ngày hoặc force-release do clawback) → vào `currentCash`.

**`cashTransferWaiting`** = tổng `commission.cashback` của các giao dịch có `status = cashback` **và** `transferStatus = pending` của một user. Đây là số được aggregate **trực tiếp từ collection transaction** (không phải từ một bảng ledger), trả về qua gRPC field `cash_transfer_waiting` (số 8 trong `AggregateUserStatsResponse`).

**Collection `cash-transfer-tracking`** (audit log, không phải ledger vòng đời): mỗi document = một lần job thả 1 giao dịch. Fields: `user`, `transactionId`, `value` (= `commission.cashback` thực nhận), `orderTime`, `estimateTransferAt`, `releasedAt`, `createdAt`. Index: `transactionId` **unique** (idempotent), `user`. Insert idempotent (`InsertIfNotExists`, bỏ qua duplicate key).

#### Sơ đồ B0 — Luồng tính `currentCash` liên service

```mermaid
sequenceDiagram
    participant U as user.UserAggregateStats
    participant T as transaction.AggregateUserStats
    participant W as withdraw.GetUserStats

    U->>T: AggregateUserStats(userID)
    Note over T: successCommission (như cũ)<br/>cashTransferWaiting = Σ cashback<br/>where status=cashback AND transferStatus=pending
    T-->>U: successCommission (ĐÃ trừ cashTransferWaiting) + cashTransferWaiting

    U->>W: GetUserStats(userID)
    W-->>U: pendingCash, successCash (đã rút)

    Note over U: currentCash = successCommission − withdrawSuccess − withdrawPending (+ nguồn khác)<br/>waitingCommissionCashback = cashTransferWaiting (chỉ để hiển thị)
    U-->>U: currentCash (chỉ tiền đủ 60 ngày) + waitingCommissionCashback
```

**Điểm mấu chốt:** `user` không cần biết về holding — `transaction` đã tự trừ `cashTransferWaiting` khỏi `successCommission` trước khi trả về. `waitingCommissionCashback` chỉ để hiển thị số "tiền đang chờ về".

### Sơ đồ B1 — Vòng đời `transferStatus` của một giao dịch cashback

```mermaid
stateDiagram-v2
    [*] --> pending: Giao dịch chuyển sang status=cashback<br/>set transferStatus=pending,<br/>estimateTransferAt = startOfDayHCM(orderTime + 60d)

    pending --> success: Job thả tiền 03:00 HCM<br/>IsMatured(estimateAt, now) == true<br/>+ ghi audit cash-transfer-tracking + UpdateUserStats
    pending --> success_forced: Clawback khi còn pending<br/>ép transferStatus=success,<br/>estimateTransferAt = đầu ngày hôm nay

    success --> [*]: Vào currentCash (tiền rút được)
    success_forced --> [*]: Coi như đã chi → executor thu hồi
```

### Sơ đồ B2 — Job thả tiền (service `transaction`, 03:00 HCM)

```mermaid
flowchart TD
    Start([Cron 03:00 HCM]) --> Q[Query transaction theo trang lastId, batch 500:<br/>status=cashback AND transferStatus=pending<br/>AND estimateTransferAt <= now]
    Q --> Loop{Còn record?}
    Loop -->|Có| Mature{IsMatured?}
    Mature -->|Không| Loop
    Mature -->|Có| Mark[TransactionMarkTransferSuccess:<br/>transferStatus = success]
    Mark --> Audit[Insert idempotent cash-transfer-tracking<br/>value=commission.cashback, releasedAt=now]
    Audit --> Side[runSideEffects tác vụ phụ]
    Side --> Collect[Gom userId bị ảnh hưởng]
    Collect --> Loop
    Loop -->|Hết trang| Next[Trang kế theo lastId]
    Next --> Q
    Loop -->|Hết tất cả| Upd[Với mỗi user bị ảnh hưởng:<br/>gRPC UpdateUserStats userId]
    Upd --> End([Tiền đủ tuổi đã vào currentCash])
```

### C. Auto-withdraw

**Scanner** (`user`, `app/service/auto_withdraw_scanner.go`, cron 05:00 HCM):
- **Redis lock** `auto_withdraw_scanner:running` TTL 2h; đang chạy thì skip.
- Phân trang theo `_id` tăng dần, batch 500. Điều kiện đẩy xuống DB (có index `tos.status, _id`): `banned != true` **và** `rasiAccountNumber` tồn tại & khác rỗng. *(Filter `tos.status == completed` đã bị comment out — xem mục lệch spec.)*
- Với mỗi user: `UserAggregateStats(user)` lấy `currentCash` (đã trừ `cashTransferWaiting` do transaction trả về). Nếu `currentCash < effectiveMinCash(user)` → skip.
- `effectiveMinCash = max(env WITHDRAW_MIN_CASH, minCash từ event ICB)` — gọi gRPC `event.GetMinWithdrawalConfig(userID)`, lỗi thì fallback env.
- `cash = floor(currentCash)`; nếu `<= 0` → skip.
- Publish NATS `CreateWithdraw{ UserId, Cash, AccountNumber = rasiAccountNumber, Mode = "auto" }`.
- Một user lỗi → log + continue. Nhịp giãn cách: `sleep 2s` sau mỗi **10 user** (`processed % 10 == 0`).
- **Sandbox**: route develop-only `POST /sandbox/trigger-auto-withdraw` để chạy scanner ngay không cần chờ cron.

**Thực thi** (`withdraw`): consumer NATS `CreateWithdraw` build `WithdrawBody{ Cash, AccountNumber, Mode }` rồi chạy `go NewWithdraw(...)` bất đồng bộ, trả `Accepted: true` ngay.

### Sơ đồ C1 — Auto-withdraw end-to-end

```mermaid
flowchart TD
    Start([Cron 05:00 HCM — user service]) --> Lock{Lấy Redis lock?}
    Lock -->|Không| Skip([Skip, đã có instance chạy])
    Lock -->|Có| Page[Quét user theo trang _id, batch 500<br/>filter DB: not banned + có rasiAccountNumber]
    Page --> Next{Còn user?}
    Next -->|Hết| Done([Log processed, nhả lock])
    Next -->|Có| Stats[UserAggregateStats → currentCash]
    Stats --> Min[effectiveMinCash = max env, ICB event]
    Min --> Check{currentCash >= minCash<br/>AND floor > 0?}
    Check -->|Không| Pace
    Check -->|Có| Pub[Publish NATS CreateWithdraw<br/>userId, floor cash, rasiAccountNumber, mode=auto]
    Pub --> Pace[processed++; nếu %10==0 sleep 2s]
    Pace --> Next
    Pub -.NATS.-> WConsume[[withdraw: consumer CreateWithdraw<br/>go NewWithdraw mode=auto, Accepted=true]]
```

### D. Luồng chuyển tiền qua communication + webhook (`withdraw`)

**`NewWithdraw`** (điểm vào chung cho mọi mode: `manual` HTTP, `auto` NATS, `batch_transfer` file):
- Lấy user info qua gRPC (kèm `rasiAccountNumber`, `chrgAcctCd`).
- **Validate tài khoản nhận**: nếu `data.AccountNumber` khác rỗng thì phải là `chrgAcctCd` **hoặc** `rasiAccountNumber` của chính user, ngược lại lỗi `errReceiverAccountNotExists`.
- Kiểm tra `currentCash >= cash`.
- *(Check TOS cho `manual`/`auto` hiện đã comment out — xem mục lệch spec.)*
- **Nhánh `ENABLE_COMMUNICATION = true`**: tra beneficiary từ DB (sort verified desc); không có thì `QueryBeneficiary` từ partner rồi lưu; gọi `makeTransferViaCommunication` (proxy accesstrade qua NATS, remark "MB hoàn tiền mua sắm", map status accesstrade → internal). Thành công thì set `referenceNumber`, `status = success`; lỗi/không success thì set `pending`, revert cash nếu `rejected`, push notification.
- **Nhánh `ENABLE_COMMUNICATION = false`**: giữ luồng cũ (generate token MBBank → `RequestTransfer` trực tiếp).

**Query beneficiary** (`GET /query-beneficiary-account`, RequireLogin): gọi partner qua communication để lấy tên chủ tài khoản; validate (HTTP >= 400 / status fail / tên rỗng → lỗi); **async lưu** vào collection `beneficiary-accounts` nếu chưa có (`status = active`, `verified = true`). Response gồm `beneficiaryAcc { name, accountNumber }` và `fee`.

**Webhook / callback**: `TransferCallback { ref_txn_id, transfer_status, txn_id }`. `WithdrawUpdateStatusFromWebhook` tìm withdraw theo `transactionId`, chỉ xử lý khi đang `pending`, map status accesstrade (`SUCCESS→success`, `CANCEL/FAILED→rejected`, `INIT/PENDING/PROCESSING/VERIFYING→pending`), cập nhật `status/updatedAt/updatedFrom/referenceNumber`, revert cash nếu `rejected`, push notification. Ngoài ra có **cronjob đồng bộ pending** (prod 08:00 & 14:00, dev mỗi phút) quét withdraw `pending` và hỏi lại partner, có Redis lock.

**NATS**: `Init()` **luôn connect** (để publish được); chỉ đăng ký consumer khi `ENABLE_WORKER = true` (tách API-only pod khỏi worker). Hai consumer: `CreateWithdraw` và `UpdateTrancStatusFromWebhook`.

### Collection `beneficiary-accounts` (`withdraw`)
Fields: `user`, `name`, `bankCode`, `customerName`, `customerShortName`, `customerNo`, `accountNumber`, `status`, `verified`, `createdAt`. Index **unique** `(user, accountNumber)`. DAO có `FindOne`, `InsertOne`, `Upsert` (upsert theo `(user, accountNumber)`, insert gắn `_id/user/accountNumber/createdAt`, update chỉ set fields trong `set`). Có gRPC `CreateBeneficiaryAccount(user, accountNumber, name, bankCode)` để service ngoài tạo trước (verified=true).

### Sơ đồ D1 — `NewWithdraw` (nhánh `ENABLE_COMMUNICATION`)

```mermaid
flowchart TD
    Start([NewWithdraw: userID, cash, accountNumber, mode]) --> ValAcc{"accountNumber ∈<br/>{chrgAcctCd, rasiAccountNumber}?"}
    ValAcc -->|Không| ErrAcc[errReceiverAccountNotExists]
    ValAcc -->|Có| ValCash{currentCash >= cash?}
    ValCash -->|Không| ErrCash[lỗi không đủ số dư]
    ValCash -->|Có| Comm{ENABLE_COMMUNICATION?}

    Comm -->|false| Old[Luồng cũ:<br/>generate token MBBank → RequestTransfer trực tiếp]
    Comm -->|true| FindBene[Tra beneficiary từ DB<br/>sort verified desc]
    FindBene --> HasBene{Có beneficiary?}
    HasBene -->|Không| Query[QueryBeneficiary từ partner<br/>→ lưu beneficiary-accounts]
    Query --> Transfer
    HasBene -->|Có| Transfer[makeTransferViaCommunication<br/>proxy accesstrade qua NATS]
    Transfer --> Res{Kết quả}
    Res -->|success| OK[set referenceNumber,<br/>status=success]
    Res -->|rejected| Rev[status=pending → rejected,<br/>revert cash, push notification]
    Res -->|pending/khác| Pend[status=pending,<br/>push notification]
    Old --> End([Kết thúc])
    OK --> End
    Rev --> End
    Pend --> End
```

### Sơ đồ D2 — Cập nhật trạng thái bất đồng bộ (webhook + cronjob sync)

```mermaid
flowchart TD
    subgraph WH[Webhook callback từ partner]
        W1[NATS UpdateTrancStatusFromWebhook<br/>TransferCallback ref_txn_id, transfer_status, txn_id]
        W1 --> W2[Tìm withdraw theo transactionId]
        W2 --> W3{status == pending?}
        W3 -->|Không| W4[bỏ qua ErrStatusNotPending]
        W3 -->|Có| W5[Map status accesstrade → internal<br/>SUCCESS→success / CANCEL,FAILED→rejected /<br/>INIT,PENDING,PROCESSING,VERIFYING→pending]
    end

    subgraph CR[Cronjob sync pending — prod 08:00 & 14:00]
        C1[Redis lock withdraw_sync_status] --> C2[Quét withdraw status=pending<br/>phân trang 100]
        C2 --> C3[QueryTransactionStatus từ partner]
        C3 --> C5{status != pending?}
        C5 -->|Có| W5
    end

    W5 --> Upd[WithdrawUpdateStatus:<br/>status, updatedAt, updatedFrom, referenceNumber]
    Upd --> RevCash{status == rejected?}
    RevCash -->|Có| Revert[revert cash cho user]
    RevCash -->|Không| Notify
    Revert --> Notify[Push notification nếu mode manual/auto]
```

---

## User Stories

### Trạng thái tài khoản RASI (`accountStats`)
1. Là người dùng dùng app cũ chưa hỗ trợ RASI, tôi muốn nhận trạng thái `UPDATE_APP`, để được dẫn ra cửa hàng ứng dụng cập nhật.
2. Là người dùng chưa đăng ký RASI nhưng app đã hỗ trợ, tôi muốn nhận `REGISTER_RASI` kèm `rasiDeeplink`, để mở màn đăng ký RASI.
3. Là người dùng đã có RASI nhưng chưa ký điều khoản, tôi muốn nhận `SIGN_TOS`, để được dẫn tới màn ký TOS.
4. Là người dùng đã có RASI và đã ký TOS, tôi muốn nhận `OK`, để rút tiền bình thường không bị làm phiền.
5. Là client, tôi muốn `/me` trả một `accountStats` rõ ràng kèm `rasiDeeplink`, để tự điều hướng mà không phải suy luận logic nghiệp vụ.
6. Là hệ thống `user`, tôi muốn lưu `rasiAccountNumber` vào DB mỗi lần SSO Auth, để có dữ liệu tin cậy cho auto-withdraw và trạng thái tài khoản.
7. Là hệ thống `user`, tôi muốn nhúng `rasiDeeplink` vào JWT thay vì DB, để lấy được deeplink mà không phải gọi lại SSO.
8. Là người dùng vừa đăng ký RASI xong, tôi muốn lần đăng nhập/SSO tiếp theo cập nhật `rasiAccountNumber` và trạng thái chuyển sang `SIGN_TOS`/`OK`, để phản ánh đúng tình trạng.

### Holding 60 ngày
9. Là người dùng, tôi muốn nhìn thấy số "tiền đang chờ về" (`cashTransferWaiting`) tách biệt số dư rút được, để biết bao nhiêu tiền sắp đủ điều kiện.
10. Là người dùng, tôi muốn số dư rút được (`currentCash`) chỉ gồm tiền đã giữ đủ 60 ngày, để không bị hiểu nhầm về số tiền khả dụng.
11. Là người dùng có giao dịch bị hoàn/huỷ trong thời gian chờ, tôi muốn khoản tương ứng bị xử lý đúng (force-release để executor thu hồi), để không nhận phần tiền không thuộc về mình.
12. Là hệ thống `transaction`, tôi muốn gắn `transferStatus=pending` + `estimateTransferAt` khi giao dịch chuyển sang cashback, để tính holding 60 ngày.
13. Là hệ thống `transaction`, tôi muốn chạy job 03:00 HCM hằng ngày thả các giao dịch đủ tuổi (`transferStatus=success`), ghi audit và cập nhật user stats, để tiền đủ tuổi vào `currentCash` đúng hạn.
14. Là hệ thống `transaction`, tôi muốn trừ `cashTransferWaiting` khỏi `successCommission` khi trả stats qua gRPC, để `currentCash` ở `user` chỉ gồm tiền đủ tuổi mà `user` không cần biết về holding.
15. Là hệ thống `transaction`, tôi muốn audit mỗi lần thả tiền vào `cash-transfer-tracking` idempotent theo `transactionId`, để không ghi trùng khi job chạy lại.
16. Là hệ thống `transaction`, khi clawback một giao dịch còn `pending`, tôi muốn ép `transferStatus=success` + `estimateTransferAt=đầu ngày hôm nay`, để executor thu hồi như tiền đã chi.

### Auto-withdraw
17. Là người dùng đủ điều kiện, tôi muốn tiền hợp lệ được tự động chuyển về STK RASI mỗi ngày, để không phải bấm rút thủ công.
18. Là người dùng, tôi muốn tiền được chuyển về đúng `rasiAccountNumber` của tôi, để không phải nhập lại thông tin nhận tiền.
19. Là người dùng chưa có RASI, tôi muốn bị loại khỏi auto-withdraw, để hệ thống không chuyển tiền khi chưa có tài khoản nhận.
20. Là người dùng bị khoá (banned), tôi muốn không bị auto-chuyển tiền, để tuân thủ quy định.
21. Là người dùng có số dư dưới `minCash`, tôi muốn được giữ tiền lại tới khi đủ ngưỡng, để mỗi lần chuyển đều hợp lệ.
22. Là cronjob auto-withdraw, tôi muốn lấy `minCash` động = max(env, ICB event) theo từng user, để tôn trọng cấu hình ngưỡng của sự kiện.
23. Là cronjob auto-withdraw, tôi muốn quét user theo trang với filter đẩy xuống DB + index, để không full-scan bảng user.
24. Là cronjob auto-withdraw, tôi muốn có Redis lock chống chạy trùng, để không tạo lệnh rút trùng khi nhiều instance.
25. Là cronjob auto-withdraw, tôi muốn giãn cách 2s mỗi 10 user, để không spam MBBank/withdraw service.
26. Là cronjob auto-withdraw, khi một user lỗi tôi muốn bỏ qua và tiếp tục, để một user lỗi không chặn cả mẻ.
27. Là đội vận hành, tôi muốn auto-withdraw chạy 05:00 HCM (sau job thả tiền 03:00), để tiền đủ tuổi đã vào `currentCash` trước khi quét.
28. Là đội phát triển, tôi muốn một route sandbox develop-only để trigger auto-withdraw ngay, để test không phải chờ cron.

### Chuyển tiền qua communication + webhook
29. Là hệ thống `withdraw`, tôi muốn validate tài khoản nhận thuộc chính user (`chrgAcctCd` hoặc `rasiAccountNumber`), để không chuyển nhầm tài khoản người khác.
30. Là hệ thống `withdraw`, khi bật `ENABLE_COMMUNICATION` tôi muốn chuyển tiền qua communication service (proxy accesstrade), để tập trung outbound qua một cổng.
31. Là người dùng, tôi muốn tra cứu tên chủ tài khoản nhận qua `GET /query-beneficiary-account` trước khi chuyển, để xác nhận đúng người nhận.
32. Là hệ thống `withdraw`, tôi muốn lưu beneficiary đã xác thực vào DB (unique theo user+accountNumber), để lần sau không phải query lại partner.
33. Là hệ thống `withdraw`, tôi muốn cập nhật trạng thái withdraw bất đồng bộ qua webhook, để phản ánh đúng kết quả cuối từ partner.
34. Là hệ thống `withdraw`, khi withdraw bị `rejected` tôi muốn revert lại cash cho user, để số dư không bị trừ oan.
35. Là hệ thống `withdraw`, tôi muốn một cronjob định kỳ đồng bộ các withdraw còn `pending` với partner, để không kẹt trạng thái khi lỡ webhook.
36. Là hệ thống `withdraw`, tôi muốn push notification chỉ cho mode `manual`/`auto` (bỏ qua `batch_transfer`), để không gửi thông báo cho luồng nội bộ.
37. Là vận hành, tôi muốn tách API pod và worker pod qua `ENABLE_WORKER` nhưng NATS luôn connect, để pod API vẫn publish được mà không chạy consumer.

### Migration / backfill (service `transaction`)
38. Là đội vận hành, tôi muốn backfill `transferStatus=success` + `estimateTransferAt` cho các đơn cashback cũ (trước go-live), để dữ liệu cũ nhất quán với mô hình holding mới.
39. Là đội vận hành, tôi muốn một endpoint trigger job thả tiền ngay, để chủ động release mà không chờ cron.
40. Là đội vận hành, tôi muốn công cụ đánh dấu và xoá/reject giao dịch trùng, để làm sạch dữ liệu trùng lặp.

---

## Implementation Decisions

### Phân bổ theo service
- **`user`**: RASI fields + `accountStats` (4 state) ở `/me`; `AutoWithdrawScanner` cron 05:00; map `cashTransferWaiting` → `waitingCommissionCashback`; gRPC event `GetMinWithdrawalConfig`; sandbox trigger route.
- **`transaction`**: `HoldingClock`; field `transferStatus` + `estimateTransferAt` trên transaction; job thả tiền 03:00 (`TransferReleaseRun`); collection audit `cash-transfer-tracking`; aggregate `cashTransferWaiting`; xử lý clawback force-release; các migration API.
- **`withdraw`**: `NewWithdraw` với validate tài khoản nhận + mode `auto`; nhánh `ENABLE_COMMUNICATION` (proxy accesstrade qua NATS); query beneficiary + collection `beneficiary-accounts`; webhook cập nhật trạng thái + cronjob sync pending; consumer NATS `CreateWithdraw`/webhook.
- **`external`**: proto bổ sung — `AggregateUserStatsResponse.cash_transfer_waiting` (8), `UserInfo.rasi_account_number` (17), rpc `UpdateUserStats`, `CreateBeneficiaryAccount`.

### Module sâu (deep modules)

**HoldingClock** (`transaction`, thuần hàm, không I/O):
```
HoldingDays() int                          // env TRANSACTION_HOLDING_DAYS, default 60
EstimateTransferAt(orderTime) time         // = startOfDayHCM(orderTime + HoldingDays)
IsMatured(estimateAt, now) bool            // = estimateAt <= startOfDayHCM(now)
```

**ResolveAccountStats** (`user`, thuần hàm):
```
ResolveAccountStats(user, rasiDeeplink) -> "OK" | "REGISTER_RASI" | "SIGN_TOS" | "UPDATE_APP"
// rasiAccountNumber == "" ? (rasiDeeplink == "" ? UPDATE_APP : REGISTER_RASI)
//                        : (tos != completed ? SIGN_TOS : OK)
```

**TransferReleaseRun** (`transaction`, job):
```
Run(now)
// phân trang lastId batch 500 over {status=cashback, transferStatus=pending, estimateTransferAt<=now}
// for tx matured: MarkTransferSuccess(tx) → insert cash-transfer-tracking (idempotent) → runSideEffects
// gom userIds bị ảnh hưởng → gRPC UpdateUserStats(user)
```

**AutoWithdrawScanner** (`user`, quét + publish):
```
Run(now)
// Redis lock 2h; phân trang _id batch 500; filter DB: banned!=true + có rasiAccountNumber
// per user: stats=UserAggregateStats; if currentCash < effectiveMinCash: skip
//           cash=floor(currentCash); publish NATS CreateWithdraw{userId, cash, rasiAccountNumber, auto}
//           pace: sleep 2s mỗi 10 user; lỗi → log + continue
```

**BeneficiaryAccountDAO** (`withdraw`): `FindOne`, `InsertOne`, `Upsert((user, accountNumber))` — encapsulate collection `beneficiary-accounts` (unique index).

### Schema changes
- `transaction` collection `transactions`: thêm `transferStatus` (`pending`|`success`), `estimateTransferAt`. Index `(transferStatus, estimateTransferAt)`.
- `transaction` collection mới `cash-transfer-tracking`: `user`, `transactionId` (unique), `value`, `orderTime`, `estimateTransferAt`, `releasedAt`, `createdAt`.
- `user` `UserStats`: thêm `waitingCommissionCashback` (map từ `cash_transfer_waiting`). Index mới `(tos.status, _id)`.
- `user` `UserBSON`: `rasiAccountNumber` (DB), `rasiDeeplink` (bson:"-", chỉ memory/JWT).
- `withdraw` collection mới `beneficiary-accounts`: unique `(user, accountNumber)`.
- `withdraw` constants mode: `batch_transfer` | `manual` | `auto`.

### API / gRPC contracts
- `user` `GET /me`: response thêm `accountStats` (4 giá trị) + `rasiDeeplink`.
- `withdraw` `GET /query-beneficiary-account` (RequireLogin): trả `beneficiaryAcc{name, accountNumber}` + `fee`; async lưu beneficiary.
- gRPC `transaction.AggregateUserStats`: thêm `cash_transfer_waiting`; `success_commission` trả ra đã trừ `cashTransferWaiting`.
- gRPC `user.UpdateUserStats(userId)`, `user.GetUserInfo` trả `rasi_account_number`; `user` map `SourceID → EbankId`.
- gRPC `event.GetMinWithdrawalConfig(userId) → minWithdrawal`.
- gRPC `withdraw.CreateBeneficiaryAccount(user, accountNumber, name, bankCode)`.
- NATS `withdraw`: `CreateWithdraw{userId, cash, accountNumber, mode}` (async, `Accepted=true`), `UpdateTrancStatusFromWebhook(TransferCallback)`.

### Config / env mới
- `transaction`: `TRANSACTION_HOLDING_DAYS` (default 60); constants `transferStatus` pending/success.
- `user`: `WITHDRAW_MIN_CASH` (default 0, ngưỡng thô); constant context key `rasiDeeplink`.
- `withdraw`: `ENABLE_COMMUNICATION` (default false), `ENABLE_WORKER` (default true), `NATS_URI/USER/PASSWORD`.

### Lịch chạy (đã chốt trong code)
- `transaction` job thả tiền: **03:00 HCM** (`0 0 3 * * *`).
- `user` auto-withdraw scanner: **05:00 HCM** (`0 0 5 * * *`).
- `withdraw` cronjob sync pending: prod **08:00 & 14:00**, dev **mỗi phút**.

### Tái sử dụng ràng buộc rủi ro (`NewWithdraw`)
Lock Redis theo user (chống double-withdraw), check đủ số dư, validate tài khoản nhận thuộc user, hạn mức tháng, gọi partner (trực tiếp hoặc qua communication), cập nhật stats, push notification. Auto-withdraw không nhân bản logic — chỉ publish NATS để gọi lại `NewWithdraw` với `mode=auto`.

---

## Testing Decisions

**Nguyên tắc**: chỉ test **hành vi bên ngoài** (input → output/observable state), không test chi tiết cài đặt nội bộ. Ưu tiên module thuần/lõi nghiệp vụ chạy độc lập với MBBank/gRPC thật.

**Đã có test trong code (prior art tham chiếu):**
- `transaction/internal/holdingclock/holdingclock_test.go`: mốc cơ bản (+60d về đầu ngày HCM), input cuối ngày không off-by-one, input UTC quy đổi HCM.
- `transaction/internal/job/transfer_release_job_test.go`: giao dịch đủ tuổi → `success` + audit; giao dịch chưa tới hạn → skip. (Dùng `RunSideEffectsFunc` override để test side-effect.)
- `withdraw/internal/dao/beneficiary_test.go`: upsert insert-then-update trả về cùng ID, chỉ 1 doc, field được cập nhật.

**Nên bổ sung (nếu tách được DAO/gRPC qua interface):**
- `ResolveAccountStats` (thuần hàm): 4 nhánh trạng thái theo tổ hợp `rasiAccountNumber` / `rasiDeeplink` / TOS.
- `AutoWithdrawScanner`: "một user lỗi không chặn cả mẻ", "lọc banned/có RASI/minCash", "floor cash & skip <= 0" — mock DAO user + NATS client + gRPC stats/event.
- Webhook mapping: map status accesstrade → internal (`SUCCESS/CANCEL/FAILED/PENDING/...`) và revert cash khi `rejected`.

**Prior art**: bám cấu trúc `internal/...` + `_test.go` sẵn có trong từng service Go của repo.

---

## Out of Scope

- **Gamification & event holding**: chưa áp holding — giữ hành vi cũ (tiền vào số dư ngay). Sẽ áp mô hình tương tự ở giai đoạn sau.
- **Migration số dư cũ trước go-live** ngoài phần backfill `transferStatus` đã có: đội sản phẩm tự lo phần còn lại nếu cần.
- **Màn đăng ký RASI trong app** và quy trình đăng ký RASI phía MBBank (client xử lý qua `rasiDeeplink`).
- **Thay đổi cơ chế phát hành/verify JWT** hiện có.
- **Thuật toán thu hồi FIFO/recall-debt** cho tiền đã chi — không có; clawback trước release chỉ force-release để executor xử lý.
- **Chi tiết UI/UX** hiển thị `cashTransferWaiting`/`accountStats` phía client.

---

## Further Notes

### Những điểm code lệch so với PRD gốc

Đây là các điểm code trên `feature/rasi` **khác** so với 2 PRD ngày 2026-06-23. Cần team review lại xem có cố ý không:

1. **Kiểm tra TOS cho auto-withdraw đã bị comment out.**
   - PRD auto-withdraw chốt: mode `auto` **phải** yêu cầu `IsSignedTOS`.
   - Code thực tế: trong `AutoWithdrawScanner`, filter `tos.status == completed` bị comment; trong `NewWithdraw`, check `IsSignedTOS` cho `manual`/`auto` cũng bị comment. → Hiện **không** chặn user chưa ký TOS khỏi auto-withdraw. ⚠️ Cần xác nhận có chủ đích hay không.

2. **Mô hình holding không dùng bảng ledger `user-cash-tracking` (waiting/released/cancelled).**
   - PRD mô tả một bảng ledger per-record với `status waiting|released|cancelled`.
   - Code thực tế: dùng field `transferStatus` (`pending`|`success`) **trực tiếp trên document transaction**; `cash-transfer-tracking` chỉ là **audit log lúc release** (không có trạng thái `cancelled`). `cashTransferWaiting` được aggregate trực tiếp từ transaction, không recompute từ bảng riêng.

3. **Auto-withdraw đi qua NATS, không phải gRPC `AutoWithdraw`.**
   - PRD dự kiến rpc `withdraw.AutoWithdraw(userID, cash)`.
   - Code thực tế: scanner **publish NATS `CreateWithdraw`** (async), `withdraw` consume rồi chạy `go NewWithdraw`. Không có rpc `AutoWithdraw` trong proto.

4. **`accountStats` có 4 trạng thái và nằm ở `user` service (`/me`), không phải API `/api/withdraw/account-state` ở `withdraw`.**
   - PRD RASI dự kiến 3 state (`OK`/`NEED_REGISTER_RASI`/`NEED_UPDATE_APP`) qua endpoint ở `withdraw`.
   - Code thực tế: 4 state (`OK`/`REGISTER_RASI`/`SIGN_TOS`/`UPDATE_APP`, thêm nhánh TOS) resolve ở `user` và trả tại `/me`.

5. **Nhịp giãn cách auto-withdraw = 2s mỗi 10 user** (PRD gợi ý ~5s hoặc mỗi 10 user).

6. **Job thả tiền không có bước "reconcile toàn bộ user cuối ngày"** như PRD mô tả — chỉ recompute qua `UpdateUserStats` cho các user bị ảnh hưởng trong lần chạy job.

### Điểm mới không có trong 2 PRD gốc
- Toàn bộ **khối D** (communication branch, query beneficiary, webhook callback, cronjob sync pending, collection `beneficiary-accounts`, gate `ENABLE_WORKER`/`ENABLE_COMMUNICATION`, NATS luôn connect).
- Xử lý **clawback force-release** khi còn `pending`.
- Các **migration API** (backfill transferStatus, remove/reject transaction duplicate, trigger transfer-release-tick).
- Map `SourceID → EbankId` trong gRPC user info.

### Bất biến an toàn (theo code)
- `currentCash` = `successCommission (đã trừ cashTransferWaiting)` − withdraw success/pending + các nguồn khác → chỉ gồm tiền đủ tuổi.
- `cash-transfer-tracking` idempotent theo `transactionId` (unique) → job chạy lại không ghi trùng.
- Clawback trước release → force `success` + `estimateTransferAt = đầu ngày` để executor thu hồi; clawback sau release → giữ nguyên.
- `beneficiary-accounts` unique `(user, accountNumber)` → không trùng bản ghi người nhận.

### Rủi ro & lưu ý vận hành
| Rủi ro | Ghi chú |
|---|---|
| Auto-withdraw không chặn user chưa ký TOS (do comment out) | ⚠️ Cần xác nhận chủ đích; nếu không, bỏ comment filter TOS ở scanner + `NewWithdraw`. |
| Lỡ webhook → withdraw kẹt `pending` | Cronjob sync pending (08:00 & 14:00 prod) hỏi lại partner. |
| Double-withdraw cùng user | Redis lock trong `NewWithdraw` + lock scanner. |
| Spam MBBank khi quét nhiều user | Pace 2s mỗi 10 user. |
| Sai tài khoản nhận | Validate `accountNumber ∈ {chrgAcctCd, rasiAccountNumber}`; auto-withdraw luôn dùng `rasiAccountNumber`. |
| Lệch `cashTransferWaiting` | Aggregate trực tiếp từ transaction mỗi lần gọi (không cache per-record); `UpdateUserStats` sau job thả tiền. |
