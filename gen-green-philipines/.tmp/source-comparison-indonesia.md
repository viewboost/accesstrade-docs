# Đánh giá source vCreator-Indonesia vs yêu cầu vCreator-Philippines

**Date:** 2026-04-27
**Source clone:** `accesstrade-projects/vcreator-philippines/` (clone từ `viewboost/vcreator-philippines.git`, branch main, commit `9e2b817 init philippines`)
**Đối chiếu:** `accesstrade-projects/vcreator/` (vCreator VN) + tasks.csv (yêu cầu PH)

---

## TL;DR

✅ **Source này tiết kiệm RẤT NHIỀU effort cho dự án PH** — đã có sẵn:
- i18n proper với 3 ngôn ngữ (en-US, id-ID, vi-VN) ở 3 locale folders (admin/client/server)
- Currency formatter generic `ToCurrencyIDR` (chỉ cần thêm `ToCurrencyPHP`)
- Phone regex Indonesia (chỉ cần đổi sang PH regex)
- Contract template Indonesia (Bahasa, luật ID) — **template tham chiếu, NHƯNG cần rewrite cho PH**
- FE routes đã English (`/account`, `/payment-info`, `/e-contract`)

⚠️ **Nhưng source này là sub-set của vCreator VN** — thiếu nhiều module mà PH có thể cần

❓ **Không có Filipino (fil-PH) sẵn** — phải add từ đầu

---

## 1. Cấu trúc + Locales

### Source structure
```
vcreator-philippines/
├── backend/        (Go)
├── frontend/       (UmiJS - Creator)
├── admin/          (UmiJS - Admin)
└── locales/        ← MỚI! Top-level shared locales
    ├── admin/      (en-US.json, id-ID.json, vi-VN.json)
    ├── client/     (en-US.json, id-ID.json, vi-VN.json)
    └── server/     (en.json, id.json, vi.json)
```

### Locale coverage (số keys)

| Layer | Files | Keys |
|---|---|---:|
| Client (creator FE) | en-US/id-ID/vi-VN | 295/295/293 |
| Admin | en-US/id-ID/vi-VN | 409/408/408 |
| Server (backend errors) | en/id/vi | 345/345/346 |
| FE creator local | en-US/id-ID/vi-VN | 229/231/226 |
| FE admin local | en-US/id-ID/vi-VN | 409/408/173 (vi thiếu) |
| **Total** | | **~3,800 keys |

→ **i18n đã proper rồi, không phải hardcode** như vCreator VN.

---

## 2. So sánh modules với vCreator VN

### Backend public routers

| Module | vCreator VN | vCreator-ID (PH source) |
|---|:---:|:---:|
| user | ✅ | ✅ (subset) |
| event | ✅ | ✅ |
| article | ✅ | ✅ |
| common | ✅ | ✅ |
| content_callback | ✅ | ✅ |
| news | ✅ | ✅ |
| notification | ✅ | ✅ |
| partner | ✅ | ✅ |
| quick_action | ✅ | ✅ |
| schedule | ✅ | ✅ (thiếu Threads + update-contract-status) |
| transcript | ✅ | ✅ |
| user_statistic | ✅ | ✅ |
| **migration** | ✅ | ❌ |
| **opshub_webhook** | ✅ | ❌ |
| **workplace** | ✅ | ❌ |

### Backend admin routers

| Module | VN | ID |
|---|:---:|:---:|
| admin_notification | ✅ | ✅ |
| article | ✅ | ✅ |
| audit | ✅ | ✅ |
| common | ✅ | ✅ |
| content | ✅ | ✅ |
| content_manual_flow | ✅ | ✅ |
| event | ✅ | ✅ |
| event_schema | ✅ | ✅ |
| export | ✅ | ✅ |
| identification | ✅ | ✅ |
| migration | ✅ | ✅ |
| news | ✅ | ✅ |
| partner | ✅ | ✅ |
| quick_action | ✅ | ✅ |
| reconciliation | ✅ | ✅ |
| role | ✅ | ✅ |
| segment | ✅ | ✅ |
| staff | ✅ | ✅ |
| tag | ✅ | ✅ |
| transfer | ✅ | ✅ |
| user | ✅ | ✅ |
| user_segment | ✅ | ✅ |
| **employee_registry** | ✅ | ❌ |
| **event_bonus** | ✅ | ❌ |
| **event_reward** | ✅ | ❌ |
| **workplace** | ✅ | ❌ |

### Public user routes diff (chi tiết)

vCreator-ID **THIẾU** so với VN:
- `/identification/image` (OCR ảnh ID)
- `/ekyc/check-condition`, `/ekyc/sdk`, `/ekyc/save` — **toàn bộ eKYC SDK**
- `/link-account`, `/update-phone-number`
- `/econtract/create`, `/econtract/:id`, `/econtract/list` — **flow econtract**
- `/check-bank-account` — verify tên chủ tài khoản
- `/bank/list`
- `/complete-profile`, `/check-unique`, `/dismiss-profile-popup`
- `/profile/request-otp`, `/profile/verify-otp` (separate OTP cho update profile)

vCreator-ID **THÊM MỚI**:
- `POST /users/contract/agree` (UserAgreeContract — flow ký contract đơn giản hơn?)

---

## 3. Config Indonesia hardcode (cần đổi sang PH)

| Hạng mục | Indonesia | Cần đổi cho PH |
|---|---|---|
| Phone regex | `^(?:\+62\|62\|0)[2-9][1-9][0-9]{6,11}$` | `^(09\|\+639\|639)\d{9}$` |
| Currency | `ToCurrencyIDR` (`IDR` symbol, no decimal, dot thousands) | Thêm `ToCurrencyPHP` (`₱`, 2 decimals, comma thousands) |
| Tax % | `PercentTaxIndonesia = 12` (constants.go:226) | Bỏ tax (theo decision partner) |
| Contract template | `internal/constants/contract.go` Bahasa Indonesia + luật ID + "PT. Interspace Indonesia" | Rewrite EN + luật PH + "GreenSM Philippines" |
| Withdraw tax calc | `service/withdraw.go:137`: `payload.CashTax = math.Round(payload.Body.Cash * constants.PercentTaxIndonesia / 100)` | Bỏ logic tax (do bỏ tax + bỏ withdraw scope) |
| Locale code | `IPCountryCodeID = "ID"` (locale.go:29) | Add `IPCountryCodeID_PH = "PH"` |

---

## 4. Đánh giá lại tasks.csv (sau khi có source mới)

### Effort GIẢM ĐÁNG KỂ

| Task | Trước (tasks.csv với source VN) | Sau (source ID) | Giảm |
|---|---:|---:|---:|
| **I18N-FE-02** Replace tiếng Việt → key + add EN locale | 57h | ~10h (chỉ swap locale paths + add config PH) | -47h |
| **I18N-ADMIN-02** Replace tiếng Việt → EN admin | 44h | ~8h (đã có en-US.json, chỉ verify) | -36h |
| **I18N-BE-02** Replace error messages → EN | 23h | ~4h (đã có en.json, chỉ audit + fix gaps) | -19h |
| **I18N-FE-01/I18N-ADMIN-01/I18N-BE-01** Audit tiếng Việt | 16h | ~4h (audit gap thay vì full scan) | -12h |
| **CONFIG-03** Currency formatter | 3h | ~2h (đã có pattern ToCurrencyIDR, chỉ thêm ToCurrencyPHP) | -1h |
| **CONFIG-01/02** Phone regex + util | 5h | ~3h (chỉ swap regex) | -2h |
| **CONTRACT-01** Rewrite contract template | 30h | ~25h (đã có template Bahasa làm reference structure) | -5h |
| **BRAND-15** Audit & xóa VinFast legacy | 6h | ~3h (source đã không có VinFast — verify lại) | -3h |
| **DISABLE-***  Bỏ Bank/Tax/Withdraw module | 21h | ~25h (cần verify thêm vì routes structure khác) | +4h |

**Total saving estimate: ~120h** (~15 person-days)

### Tasks MỚI / CẦN CẬP NHẬT

| Task mới | Description | Effort |
|---|---|---|
| **I18N-PH-01** Add Filipino (fil-PH) locale files | Tạo `locales/{admin,client,server}/fil-PH.json` (3 files) + translate ~3,800 keys | M (16h dev + translator) |
| **I18N-PH-02** Add fil-PH support trong code | Update i18n config + language toggle để load fil-PH | S (4h) |
| **REVIEW-ID** Review module thiếu so với VN | Verify employee_registry / workplace / event_bonus / event_reward có cần cho PH không | S (4h) |
| **PORT-VN** Port modules từ VN sang PH (nếu cần) | Nếu PH cần workplace/employee_registry → port từ vCreator VN | M-L (30-50h) |

### ⚠️ Cảnh báo: source thiếu modules

Source vCreator-ID **THIẾU** các module sau (so với VN):
- ❌ **Workplace** (brands/companies/units = cơ sở làm việc)
- ❌ **Employee Registry** (import nhân viên + match staff verification)
- ❌ **Event Bonus + Event Reward** (admin)
- ❌ **eKYC SDK flow** (toàn bộ SDK eKYC)
- ❌ **Econtract flow** (create/get/list)
- ❌ **Update phone number flow**
- ❌ **Profile OTP separate**

**Hệ quả với scope PH:**
- Nếu partner GreenSM PH **cần workplace/staff verification** → phải PORT từ VN (~30-50h)
- Nếu **không cần** → OK, source ID đủ
- eKYC SDK + econtract create — nếu PH cần thì phải PORT

---

## 5. Khuyến nghị

### Option A: Dùng source vCreator-ID làm baseline ⭐ (recommend)
**Pros:**
- i18n proper sẵn → tiết kiệm ~80% effort i18n (saving ~115h)
- FE routes đã English
- Currency/phone đã có pattern multi-region
- Contract template ID làm reference

**Cons:**
- Thiếu Workplace + Employee Registry → nếu PH cần phải port
- Thiếu eKYC SDK + econtract flow advanced

**Total estimate:** **~580h** (giảm từ 695h xuống)

### Option B: Dùng vCreator VN, manual port
**Pros:**
- Có đầy đủ workplace + employee_registry + eKYC

**Cons:**
- Effort i18n cực lớn (174h)
- Tổng vẫn 695h

→ **Source ID rõ ràng tốt hơn nếu scope PH không bắt buộc workplace/employee_registry full.**

---

## 6. Câu hỏi cần partner clarify (URGENT)

Trước khi quyết định baseline, cần trả lời:

1. **Workplace + Cơ sở làm việc:** GreenSM PH có dùng feature này không (giống Vin VN với 57 cơ sở)?
   - Nếu YES → port từ VN (~30h)
   - Nếu NO → dùng source ID sạch
2. **Employee Registry:** Có cần import nhân viên GreenSM PH bằng Excel không?
   - Nếu YES → port từ VN (~20h)
   - Nếu NO → skip
3. **eKYC tự động:** Có dùng eKYC SDK không hay manual KYC?
   - Nếu manual → source ID đủ
   - Nếu auto → port eKYC + tích hợp provider PH (~30h)
4. **Econtract flow:** Source ID có endpoint `/contract/agree` đơn giản. VN có `/econtract/create` + `/econtract/:id` + `/econtract/list` phức tạp hơn. PH dùng flow nào?

---

## 7. Action items

1. ✅ Document so sánh (file này)
2. ⏳ Trả lời 4 câu hỏi §6 với partner
3. ⏳ Update tasks.csv dựa trên baseline mới (effort giảm ~120h nếu dùng source ID)
4. ⏳ Update overview.md ghi rõ source baseline = vCreator-Indonesia (không phải vCreator VN)
5. ⏳ Update estimate cost: 580h × $13.45 ≈ **\$7,800** (giảm từ \$9,500)
