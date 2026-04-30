# Phase 4 Bug-Fix Code Review
**Date:** 2026-04-30  
**Reviewer:** code-reviewer  
**Files read:** `pkg/admin/service/staff.go`, `pkg/admin/service/transfer_processing.go`, `pkg/admin/service/reconciliation_running.go`, `pkg/public/service/user.go`, `pkg/public/service/schedule.go`, `pkg/public/service/event.go`, `pkg/public/service/transcript.go`, `internal/module/reCaptchaV3/reCaptchaV3.go`, `internal/config/env.go`, `internal/config/config.go`, `internal/service/cashflow.go`, `internal/model/mg/user.go`, `internal/module/database/mongodb/index.go`, `.env`

---

## Summary Table

| # | Concern | Status | Severity |
|---|---------|--------|----------|
| 1 | TOTP counter-reset ordering & TTL window semantics | ⚠ caution | Medium |
| 2 | `runCashBack` — `AddCashFlow` idempotency on retry | ❌ issue | High |
| 3 | `isExistedEmail` BSON tags match | ✅ pass | — |
| 4 | `GenerateCode ""` — caller propagation | ❌ issue | High |
| 5 | `UpdateSearchStringContent` pagination — Limit + Sort honored | ✅ pass | — |
| 6 | `UploadContract` defer cleanup ordering | ⚠ caution | Low |
| 7 | reCAPTCHA threshold default=0.5 fires when env absent | ✅ pass | — |
| 8 | Dev env + Google test key + threshold=0.5 | ✅ pass (safe) | — |
| 9 | Hygiene — `BUG-01.2` `IsRoot` partial fix leak | ❌ issue | High |

---

## Detail

### 1. TOTP rate-limit — ⚠ caution
**`pkg/admin/service/staff.go:140-143`**

Counter reset (`Del`) runs at line 147, **before** `staff.GenerateToken()` at line 166. Ordering is correct.

TTL window semantics: Expire is set only when `n == 1` (first failure). Subsequent failures within the window do **not** extend the TTL. This is a **sliding-window-from-first-failure** design, not a rolling window. That is acceptable and intentional (comment at line 138 confirms). No bug.

One real gap: if `Incr` succeeds but `Expire` fails (Redis partial failure on first attempt), the key has no TTL and persists forever — locking the account permanently until manual Redis cleanup. The `_ =` discard on `Expire` means this failure is silent.

**Recommendation:** log or at least `fmt.Println` the `Expire` error so ops can detect it. One-liner: `if expErr := client.Expire(...).Err(); expErr != nil { fmt.Printf("totp: failed to set TTL for key %s: %v\n", failKey, expErr) }`.

---

### 2. `runCashBack` — `AddCashFlow` not idempotent ❌ issue
**`internal/service/cashflow.go:58-83`**

`AddCashFlow` does a blind `InsertOne` per payload (line 79). There is no unique key on the `cashFlow` collection guarding against duplicate `ReconciliationItem` IDs — `CashFlowOptions.ReconciliationItem` is stored in `options` but not indexed as a unique constraint anywhere in `index.go`.

On retry (admin re-runs reconciliation after a previous partial failure), `payloadCashFlow` is rebuilt fresh and `AddCashFlow` will insert duplicate cash-flow rows. The user's `cashRemaining` balance is computed by summing all cash-flow rows (`aggregatepipeline.GetRemaining`), so the duplicate insert **doubles the payout silently**.

The `failed` flag approach in BUG-03.8 reduces the window (reconciliation items stay `Pending` so retry re-enters the loop), but the cash-flow goroutine may have already succeeded before `EventRewardDAO` failed. On retry the item is processed again → second `AddCashFlow` call → duplicate row.

**Recommendation (before shipping):** Add a `$setOnInsert` upsert with a unique filter, e.g. `filter: {"options.reconciliationItem": payload.Options.ReconciliationItem}`, or a unique sparse index on `cashFlow.options.reconciliationItem`. This is the single most dangerous data-integrity gap in the entire Phase 4 diff.

---

### 3. `isExistedEmail` BSON tags — ✅ pass
**`pkg/public/service/user.go:1816-1818`**

Query keys `"info.email"`, `"socialLoginEmail.email"`, `"google.email"` checked against model:
- `UserRaw.Info UserContactInfo bson:"info"` → `UserContactInfo.Email bson:"email"` → path `info.email` ✓
- `UserRaw.SocialLoginEmail *UserSocialLoginEmail bson:"socialLoginEmail"` → `UserSocialLoginEmail.Email bson:"email"` → path `socialLoginEmail.email` ✓
- `UserRaw.Google *UserGoogleData bson:"google"` → `UserGoogleData.Email bson:"email"` → path `google.email` ✓

All three dot-paths match the BSON tags exactly.

---

### 4. `GenerateCode ""` — caller does not propagate failure ❌ issue
**`pkg/public/service/user.go:1644-1646`**

`generateCodeForUser` (line 1644) swallows the empty-string return:
```go
func (u userImpl) generateCodeForUser(ctx context.Context, user *modelmg.UserRaw) {
    code := u.GenerateCode(ctx)
    user.Code = code  // silently sets "" on exhaustion
}
```

Callers (lines 245, 496, 1302, 1407, 1590) never check whether `user.Code == ""` before calling `InsertOne`. Result: a user document is inserted with `Code: ""`. The `users` collection has **no index on `code`** (confirmed: `CollectionUser` does not appear in `index.go` at all — no indexes registered for the `users` collection). There is no `newUniqIndex("code")` call for users. So inserting `""` doesn't fail with a unique violation; it silently stores an empty code.

Downstream consequences: `user.Referral.Codes` is populated from `user.Code` (line 1704), the response field `Code` is `""` (line 1722), and `getUserHashTag` returns `"#"` (line 1876). On second exhaustion-scenario registration, a second user gets `Code = ""` and both users can be found by `bson.M{"code": ""}` — referral lookup becomes ambiguous.

**Recommendation:** change `generateCodeForUser` to return an error and have callers abort `InsertOne` if code generation fails. Minimum acceptable fix: add `if code == "" { return errors.New("code exhausted") }` inside `generateCodeForUser` and propagate. The loop cap of 100 exhausting is astronomically unlikely in practice (7-char alphanumeric space ~78B combos) but correctness matters.

---

### 5. `UpdateSearchStringContent` pagination — ✅ pass
**`pkg/public/service/schedule.go:1435-1440`**

`q.Limit = pageSize (500)` and `q.SortInterface = bson.D{{"_id", 1}}` are both set. `GetFindOptsUsingPage` (confirmed in `mgquery/query.go:228-232`) calls `opts.SetLimit(q.Limit).SetSkip(q.Page * q.Limit)` and `opts.SetSort(q.SortInterface)`. Since `q.Page = 0` (default), skip=0 and limit=500 are applied. The cursor advances via `cond["_id"] = bson.M{"$gt": lastID}`, avoiding skip-based O(n²) scan. Early-exit when `len(contents) < pageSize` is correct. No issue.

---

### 6. `UploadContract` defer cleanup — ⚠ caution
**`pkg/public/service/user.go:684-693`**

`pwd, _ = os.Getwd()` discards the error. If `Getwd` fails (e.g. process CWD deleted), `pwd = ""` → `pathPdf = "/contracts/TOS_...pdf"` (absolute from root). `GeneratePdfFromHtml` will then fail, function returns early before the `defer` is registered, so no cleanup problem. Defer is registered at line 693 only after `GeneratePdfFromHtml` succeeds — correct placement.

The `os.Remove` on a non-existent path returns `*PathError`, which is discarded (`_ =` pattern). No panic risk.

Actual gap: `os.Getwd()` failure is silent. On a broken CWD, `pathPdf` points to `/contracts/...` — write will fail with permission error that surfaces as a `GeneratePdfFromHtml` error → correct error return. Not a production risk but worth a `fmt.Printf("warn: Getwd failed: %v\n", err)`.

---

### 7. reCAPTCHA default=0.5 — ✅ pass
**`internal/config/env.go:78`**

Library is `github.com/sethvargo/go-envconfig v1.1.0`. The `default=0.5` tag is a first-class feature of this library — it populates the field when the env var is absent. Confirmed: `CAPTCHA_SCORE_THRESHOLD` is **not** in `.env`. At boot `ScoreThreshold` will be `0.5`. The check `if threshold > 0 && res.Score < threshold` in `reCaptchaV3.go:51` will therefore evaluate `0.5 > 0 = true` and apply the score gate. Default behavior is correct.

---

### 8. Dev env captcha smoke — ✅ pass (safe)
**`.env` + `internal/module/reCaptchaV3/reCaptchaV3.go`**

`.env` uses Google's public test key `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`. Per Google's documentation, this test key **always returns `success=true, score=1.0`**. With `threshold=0.5`, `1.0 >= 0.5` passes. Dev logins are not broken.

No need for a `IsEnvDevelop()` short-circuit guard. The `IsEnvDevelop()` pattern in the file is used only for debug `fmt.Println` logging (lines 30, 37, 42), not for flow bypass. Existing behavior is safe.

---

### 9. `BUG-01.2` — `IsRoot` partial fix leak ❌ issue
**`pkg/admin/service/staff.go:382-431`**

The BUG-01.2 fix correctly removes `"isRoot": body.IsRoot` from `dataChange` (the `$set` map). However, the in-memory update at line 428 still does:
```go
staff.IsRoot = body.IsRoot
```
This matters because `resetToken(staff)` is called immediately after (line 430) with this mutated `staff` object. `resetToken` only calls `redis.DelAllKeyByPattern` using `staff.ID` — it does not persist `staff` — so the mutation is benign **for the current code**.

But: if the in-memory `staff` object is ever passed to `createAudit` (line 431, it is), the audit log records `body.IsRoot` as the **new** `isRoot` value even though the DB was not updated. Admin audit trail then shows `isRoot=true` for a user that is still `isRoot=false` in the database, creating misleading audit records.

**Recommendation:** remove line 428 (`staff.IsRoot = body.IsRoot`) entirely. The DB value is not changing; the audit should reflect the actual DB state. This is a two-character fix but produces misleading security-relevant audit logs in current form.

---

## Hygiene Notes

- **`pkg/admin/service/reconciliation_running.go:332-335`**: `ContentAnalyticDailyDAO.BulkWrite` runs **synchronously** on the calling goroutine (no `go func`), while `EventRewardDAO.BulkWrite` runs in a goroutine. This is inconsistent: if you're parallelising for speed, both should be goroutines; if content-analytic must complete before the `wg.Wait`, it already does (synchronous call happens before `wg.Wait`). The inconsistency is harmless but confusing to future readers.
- **`pkg/admin/service/reconciliation_running.go:347-356`**: After `wg.Wait()` and `if failed { return }`, a new `wg.Add(1)` is added for `wRcItem` BulkWrite but **`wg.Wait()` is never called again** for this goroutine. The function returns without waiting — meaning the BulkWrite may not complete before the caller's `wg.Done()` in `Running()`. This is an existing pre-Phase-4 pattern but warrants a flag.
- **`pkg/admin/service/staff.go:10`**: `"github.com/kr/pretty"` is used only in `createAudit` error logging. This is a pre-existing import, not introduced by Phase 4. No action needed.
- **`pkg/public/service/user.go`**: `generateCodeForUser` return-type is `void` — cannot propagate error to callers without a signature change. This is a pre-existing design issue made slightly worse by adding the exhaustion comment without fixing the propagation.

---

## If you only have time to fix one thing

**Fix concern #2** (`AddCashFlow` duplicate insert on retry). It is the only Phase 4 change that can silently double-credit a user's cash balance in a retried reconciliation run. All other issues are either low-probability (code exhaustion), audit cosmetics (IsRoot in-memory), or missing log lines. A cash duplication bug in a financial payout flow is the highest business risk.

Minimum fix: add a unique sparse index on `cashFlow.options.reconciliationItem` in `index.go` and change `InsertOne` in `cashflow.go` to an upsert with `filter: {"options.reconciliationItem": payload.Options.ReconciliationItem}`.
