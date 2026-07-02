# Test Cases: Luồng thanh toán/rút tiền qua Communication (CB-MBBank Withdraw)

> Phạm vi: luồng `NewWithdraw` khi `ENABLE_COMMUNICATION=true` — request rút tiền được proxy qua service `communication` (NATS `system.request.http`) tới partner MBBank/AccessTrade.
> Tham chiếu code: `withdraw/app/service/withdraw.go`, `withdraw/app/service/withdraw_communication.go`, `withdraw/app/service/query_beneficiary.go`, `withdraw/external/natsio/communication.go`.
> Tham chiếu PRD: `withdraw/docs/prd/2026-06-23-mbbank-withdraw-communication-toggle.md`.

---

## 1. Tổng quan luồng

```
NewWithdraw
  → lock redis + validate (minCash, banned, đủ tiền, account thuộc user, hạn mức tháng)
  → GetUserByID (gRPC): SourceID, EbankID, ChrgAcctCd
  → Insert Withdraw + trừ user stats (updateUserStats -cash)
  → if ENABLE_COMMUNICATION:
        → tìm BeneficiaryAccount {user, accountNumber} (sort verified desc)
        → nếu không có → QueryBeneficiary (fallback, proxy communication)
              → không tìm thấy → WithdrawErr + trả errReceiverAccountNotExists
        → makeTransferViaCommunication (accesstrade.MakeTransfer qua communication)
        → map status theo atStatusMapping
              → SUCCESS  → update SUCCESS + refNumber + push notification
              → REJECTED → revert cash + update REJECTED + push notification + trả errWithdraw
              → PENDING  → giữ PENDING + push notification + trả errWithdraw
```

### Bảng mapping status (AccessTrade → Withdraw)

| AccessTrade `TransferStatus` | Withdraw status | Revert cash? |
| --- | --- | --- |
| `SUCCESS` | `success` | Không |
| `INIT` / `PENDING` / `PROCESSING` / `VERIFYING` | `pending` | Không |
| `CANCEL` / `FAILED` | `rejected` | Có |
| Code khác `PX00000`/`BC00000` (rejected) | `rejected` | Có |

### Điều kiện tiên quyết chung (Preconditions)

- Env `ENABLE_COMMUNICATION=true`, `NATS_URI/USER/PASSWORD` hợp lệ, `WITHDRAW_BANK_CODE` được set.
- Service `communication` đang chạy và subscribe subject `system.request.http`.
- gRPC user service khả dụng; user tồn tại, chưa banned, đã có đủ `CurrentCash`.
- Redis khả dụng (dùng cho khóa chống double-submit).

---

## 2. Test Cases — Happy path

### TC-01: Rút tiền thành công, có sẵn BeneficiaryAccount (đã verified)
- **Precondition**: User có `BeneficiaryAccount {user, accountNumber, verified=true}`. Partner trả `Code=PX00000`, `TransferStatus=SUCCESS`, `RefTxnID="REF123"`.
- **Input**: `NewWithdraw(ctx, userID, {Cash: 50000, AccountNumber: <acc hợp lệ của user>})`.
- **Expected**:
  - Withdraw được insert, sau đó update `status=success`, `referenceNumber="REF123"`.
  - `TransferBSON.Success=true`; `t.Data/t.Response/t.Header` được điền từ `reqInfo`.
  - Request đi qua communication với `AdditionalInfo{Server:"withdraw", PartnerID, ReqTo:"mbbank", Purpose:"transfer"}`.
  - `PushWithdrawNotification` được gọi.
  - Hàm trả `remainingCash = CurrentCash sau khi trừ`, `err=nil`.
  - Cash KHÔNG bị revert (đã trừ 1 lần lúc insert).

### TC-02: Rút tiền thành công, code trả về `BC00000` (CodeSuccess2)
- **Precondition**: Partner trả `Code=BC00000`, `TransferStatus=SUCCESS`.
- **Expected**: Xử lý y hệt TC-01 (`BC00000` được coi là success). Status `success`.

### TC-03: BeneficiaryAccount chưa có → fallback QueryBeneficiary thành công
- **Precondition**: Không có record BeneficiaryAccount cho `{user, accountNumber}`. `QueryBeneficiary` (proxy communication) trả về `AccountName` hợp lệ. Partner MakeTransfer trả `SUCCESS`.
- **Expected**:
  - `QueryBeneficiary` được gọi, dùng `Name/AccountNumber` trả về để build `MakeTransferReq`.
  - Withdraw `status=success`.
  - (Side-effect) `QueryBeneficiary` upsert BeneficiaryAccount mới `verified=true` (async goroutine).

---

## 3. Test Cases — Mapping trạng thái từ Partner

### TC-04: Partner trả PENDING → withdraw giữ `pending`
- **Precondition**: Partner `Code=PX00000`, `TransferStatus=PENDING`.
- **Expected**:
  - `status=pending`, update DB `status=pending` + `referenceNumber=refNumber`.
  - Cash **KHÔNG** revert.
  - `PushWithdrawNotification` được gọi.
  - Hàm trả `err = errWithdraw` (vì `status != success`), `remainingCash=0`.

### TC-05: Partner trả PROCESSING/VERIFYING/INIT → withdraw `pending`
- **Input**: lặp lại TC-04 với `TransferStatus ∈ {PROCESSING, VERIFYING, INIT}`.
- **Expected**: Giống TC-04 (status `pending`, không revert).

### TC-06: Partner trả FAILED → withdraw `rejected` + revert cash
- **Precondition**: Partner `Code=PX00000`, `TransferStatus=FAILED`.
- **Expected**:
  - `status=rejected`, update DB `status=rejected`.
  - Cash được **revert** (`updateUserStats(w, +w.Cash, true)`).
  - `PushWithdrawNotification` được gọi.
  - Hàm trả `err = errWithdraw`.

### TC-07: Partner trả CANCEL → withdraw `rejected` + revert cash
- **Input**: như TC-06 với `TransferStatus=CANCEL`.
- **Expected**: Giống TC-06.

### TC-08: Partner trả code lỗi (khác PX00000/BC00000) → rejected
- **Precondition**: `makeTransferViaCommunication` nhận `res.Code` không thuộc success → trả `WithdrawStatusRejected` + error `"transfer rejected, code: <code>"`.
- **Expected**:
  - `status=rejected`, revert cash, push notification, trả `errWithdraw`.

---

## 4. Test Cases — Beneficiary Account

### TC-09: Có nhiều BeneficiaryAccount → chọn bản `verified=true` trước
- **Precondition**: Tồn tại 2 record cùng `{user, accountNumber}`: một `verified=false`, một `verified=true`.
- **Expected**: `FindOne` với `sort verified desc` chọn record `verified=true`; `Name/AccountNumber` lấy từ record đó.

### TC-10: Không có bene, QueryBeneficiary thất bại → reject sớm (không gọi transfer)
- **Precondition**: Không có BeneficiaryAccount; `QueryBeneficiary` trả error (partner báo account không tồn tại / status error).
- **Expected**:
  - `makeTransferViaCommunication` **KHÔNG** được gọi.
  - `t.Error="beneficiary account not found"`.
  - `WithdrawErr` được gọi; hàm trả `errReceiverAccountNotExists`, `remainingCash=0`.
  - **Kiểm tra cash**: xác nhận trạng thái stats sau lỗi (đã trừ lúc insert — xác định hành vi mong muốn về revert với reviewer).

---

## 5. Test Cases — Validate đầu vào (chạy trước khi tới nhánh communication)

### TC-11: Double-submit bị chặn bởi redis lock
- **Precondition**: Đã tồn tại key redis `RedisKeyUserWithdraw:<userID>`.
- **Expected**: Trả `errServerProcessing` ngay, không insert withdraw, không gọi partner.

### TC-12: Cash < minCash → `errInvalidAmount`
- **Input**: `Cash` nhỏ hơn min cash hiệu lực (env hoặc ICB event).
- **Expected**: Trả `errInvalidAmount`, không insert, không gọi partner.

### TC-13: User bị banned → `errUserBanned`
- **Expected**: Trả `errUserBanned` sau khi `GetUserByID`, không insert, không gọi partner.

### TC-14: Không đủ tiền → `errUserNotEnoughCash`
- **Precondition**: `u.Stats.CurrentCash < cash`.
- **Expected**: Trả `errUserNotEnoughCash` cùng `remainingCash = CurrentCash`, không gọi partner.

### TC-15: AccountNumber không thuộc user → `errReceiverAccountNotExists`
- **Precondition**: `data.AccountNumber != ""` và khác cả `ChrgAcctCd` lẫn `RasiAccountNumber`.
- **Expected**: Trả `errReceiverAccountNotExists`, không gọi partner (validate xảy ra trước insert).

### TC-16: Vượt hạn mức tháng (1,900,000 VND) → `errExceedWithdrawalAmount`
- **Precondition**: `cash + tổng đã rút trong tháng > maxWithdrawalAmountOfMonth`.
- **Expected**: Trả `errExceedWithdrawalAmount`, không insert, không gọi partner.

---

## 6. Test Cases — Tích hợp Communication / NATS (hạ tầng)

### TC-17: Request được đóng gói đúng CommunicationHTTPReq
- **Expected**: Request gửi qua NATS có đúng `URL/Method/Headers/Queries/Body` từ AccessTrade và `AdditionalInfo{Server:"withdraw", PartnerID:<env.PartnerID>, ReqTo:"mbbank", Purpose:"transfer"}`.

### TC-18: Communication trả lỗi (`data.Error != ""`) → transfer thất bại
- **Precondition**: Service communication reply với field `Error` khác rỗng.
- **Expected**: `RequestHTTP` trả error → `makeTransferViaCommunication` trả `rejected` → revert cash + push notification + `errWithdraw`.

### TC-19: NATS timeout / không có subscriber
- **Precondition**: Service communication không chạy (`system.request.http` không có ai subscribe) → request timeout.
- **Expected**: `RequestHTTP` trả error; withdraw → `rejected` + revert cash. Xác nhận không treo request (timeout hữu hạn).

### TC-20: Communication trả StatusCode >= 400 với body lỗi
- **Precondition**: `res.StatusCode >= 400`, body chứa mã lỗi partner.
- **Expected**: AccessTrade parse ra code không-success → `rejected`; `t.Response` giữ body lỗi để tra soát.

---

## 7. Test Cases — Nhánh cờ TẮT (regression, đảm bảo không đổi hành vi)

### TC-21: `ENABLE_COMMUNICATION=false` → chạy luồng cũ MBBank
- **Precondition**: Cờ tắt (mặc định).
- **Expected**:
  - Gọi `GenerateWithdrawToken` + `RequestTransfer` (HTTP trực tiếp), **KHÔNG** đi qua communication/NATS.
  - Receive account = `data.AccountNumber` nếu có, ngược lại `u.ChrgAcctCd`.
  - Không đọc BeneficiaryAccount, không gọi `makeTransferViaCommunication`.
  - Kết quả success/rejected theo `WithdrawErr` cũ.

### TC-22: Cờ tắt + partner lỗi không revert cash (mbNotRevertCashErrCodes)
- **Precondition**: `RequestTransfer` trả error với `ErrorCode ∈ mbNotRevertCashErrCodes`.
- **Expected**: `WithdrawErr` trả `errWithdraw` mà **không** revert cash, không đổi status sang rejected (theo logic hiện có).

---

## 8. Ma trận bao phủ (Coverage matrix)

| Kịch bản | Status kết quả | Revert cash | Notification | Return err |
| --- | --- | --- | --- | --- |
| TC-01/02 SUCCESS | success | Không | Có | nil |
| TC-04/05 PENDING | pending | Không | Có | errWithdraw |
| TC-06/07/08 REJECTED | rejected | Có | Có | errWithdraw |
| TC-10 Bene not found | (không transfer) | — | (WithdrawErr) | errReceiverAccountNotExists |
| TC-11–16 Validate fail | (không insert/transfer) | — | Không | lỗi tương ứng |
| TC-18/19 Communication fail | rejected | Có | Có | errWithdraw |

---

## 9. Ghi chú & Điểm cần xác nhận với reviewer

1. **TC-10 (bene fallback thất bại)**: cash đã bị trừ lúc insert; cần xác nhận `WithdrawErr` có revert cash trong nhánh này không (kiểm tra `res=nil` path trong `WithdrawErr`).
2. **Idempotency của refNumber/RequestID**: `RequestID = w.ClientMessageID` (ID withdraw). Nên có test partner nhận trùng RequestID (retry) không tạo giao dịch kép — cần partner/mock hỗ trợ.
3. **Async side-effects**: `PushWithdrawNotification`, `TransferInsertOne`, và upsert bene trong `QueryBeneficiary` chạy trong goroutine → test cần chờ/synchronize để assert ổn định.
4. **Đơn vị test đề xuất**: tách phần build `MakeTransferReq` thành hàm thuần để test mapping field (UserID=EbankID, CustomerID=SourceID, CreditBankCode=env.Withdraw.BankCode) mà không cần network.
