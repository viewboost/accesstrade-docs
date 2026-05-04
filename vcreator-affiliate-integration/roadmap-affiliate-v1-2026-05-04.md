# Lộ trình Build Affiliate V1 cho VCreator

> **Source:** `accesstrade-projects/vcreator/`
> **Reference V1 (Ambassador):** `docs/pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md`
> **Reference Account Linking (Scalef):** `docs/gen-green/scalef-integration/`
> **Date:** 2026-05-04
> **Author:** vinhnguyen
> **Status:** Draft

---

## 1. Mục tiêu

Port toàn bộ chức năng **Affiliate V1 đã implement ở Ambassador** sang VCreator với điều chỉnh phù hợp:

- VCreator đã có sẵn hạ tầng `pub_be` HMAC client + `opshub` module → tái dùng
- VCreator đã có 2 endpoint Scalef account-linking (`/users/link-account`, `/users/update-phone-number`) → tận dụng làm điểm chạm liên kết AT
- Khái niệm **Event** ở VCreator ≈ **Campaign** ở Ambassador → mapping Affiliate Campaign vào Event

**Phạm vi V1:** Admin quản lý Affiliate Campaign + mapping với Event; Creator browse, join, tạo link affiliate; Frontend UI cho AT linking đã có endpoint backend.

**Out of scope (V2):** Reports (clicks, conversions, sale, commission), Orders list, Webhook từ Pub2.

---

## 2. Tình trạng hiện tại — VCreator

### Đã có (re-usable)

| Thành phần | Vị trí | Ghi chú |
|------------|--------|---------|
| HMAC Pub_BE client | `backend/internal/module/pub_be/client.go` | HMAC-SHA256 giống Pub2 ở Ambassador. Plain text format hơi khác (`clientID|traceNo|epochMs|secret`) — cần align hoặc fork module mới `pub2/` |
| OpsHub client | `backend/internal/module/opshub/` | Riêng, không liên quan affiliate |
| User model + `AT *ATInfo` | `backend/internal/model/mg/user.go:50` | Lưu `sso_id` + `username` sau khi link |
| Account linking BE | `backend/pkg/public/service/user.go:LinkAccountToAt`, `ConfirmUpdatePhoneNumber` | Gọi Pub_BE API `/api/v1/partners/scalef/check-link-account` + `/confirm-phone-update` |
| Account linking routes | `backend/pkg/public/router/user.go:55-56` | `POST /users/link-account`, `POST /users/update-phone-number` |
| Event domain | `backend/internal/model/mg/event.go` + `pkg/admin/handler/event.go` | Sẽ là target cho mapping |

### Chưa có (cần build)

| Thành phần | Mô hình tham chiếu (Ambassador) |
|------------|--------------------------------|
| Affiliate Campaign model + DAO | `internal/model/mg/affiliate.go:AffiliateCampaignRaw` |
| Event ↔ Affiliate Campaign mapping | `CampaignAffiliateMappingRaw` |
| Affiliate Contract + Link models | `AffiliateContractRaw`, `AffiliateLinkRaw` |
| Pub2 API log model | `Pub2ApiLogRaw` |
| Admin CRUD APIs cho affiliate campaign | `pkg/admin/handler/affiliate.go` |
| Public APIs (join, generate link, get contract) | `pkg/public/handler/affiliate.go` |
| Pub2 API client (join + generate link) | `internal/module/pub2/client.go` |
| Admin UI CRUD + mapping | `admin/src/pages/affiliate-campaign/` |
| Frontend affiliate section trong event detail | `frontend/src/pages/home/components/affiliate-campaigns-section/` |
| Frontend affiliate campaign detail page | `frontend/src/pages/affiliate-campaign-detail/` |
| **Frontend AT linking UI** (banner + popup) | Chưa có ở Ambassador, vcreator chưa có FE — cần build mới dù backend có sẵn |

---

## 3. Mapping khái niệm Ambassador → VCreator

| Ambassador | VCreator | Ghi chú |
|-----------|----------|---------|
| Campaign / Event | Event | `EventRaw` |
| Influencer | Creator (User) | Đã có `UserRaw.AT *ATInfo` |
| Pub2 client | Pub_BE client (đã có) hoặc `pub2` module mới | Cần extend client hiện tại để hỗ trợ headers `client-signature` chuẩn Pub2 |
| AccessTrade (AT) account | Scalef account | Cùng concept: link để có `sso_id` |
| AT Linking flow | Đã implement (Scalef account-linking) | Tận dụng — chỉ cần FE banner + popup |

**Lưu ý quan trọng:**
- Module `pub_be` hiện tại có signature format `clientID|traceNo|epochMs|secret` (4 phần ghép vào HMAC), khác với Pub2 chuẩn `clientID|traceNo|epochMs` (3 phần). Cần verify với team Pub2 hoặc tạo module riêng `pub2/` để dùng cho affiliate APIs.
- Endpoint base URL có thể khác giữa account-linking (Pub_BE) và affiliate (Pub2 / `core-aff.dev.accesstrade.me`).

---

## 4. Lộ trình triển khai (4 Phase, ~3.5 tuần)

Mỗi phase go-live độc lập. Phase 0 là prerequisite, Phase 1-3 là core delivery.

### Phase 0 — Foundation (2-3 ngày)

**Mục tiêu:** Hạ tầng module + config + verify Pub2 endpoint.

| ID | Task | Files | Effort |
|----|------|-------|--------|
| F-01 | Verify Pub2 signature format vs hiện tại của `pub_be`. Quyết định: extend `pub_be` hay tạo `internal/module/pub2/` mới | — | 0.5d |
| F-02 | Tạo module `internal/module/pub2/` (client, hmac, models, errors) | `internal/module/pub2/{client,hmac,models,errors}.go` | 1d |
| F-03 | Add config `PubAffiliate` (BaseURL, ClientID, ClientSecret) vào `internal/config/env.go` | `internal/config/env.go` | 0.25d |
| F-04 | Tạo collection names + DAO scaffold: affiliate_campaign, campaign_affiliate_mapping, affiliate_contract, affiliate_link, pub2_api_log | `internal/module/database/mongodb/collection.go` + `dao/*.go` | 1d |

**Done when:** Có thể call mock Pub2 API thành công với HMAC signature đúng spec.

---

### Phase 1 — Admin Affiliate Campaign Management (5-7 ngày)

**Mục tiêu:** Admin tạo/sửa/xóa affiliate campaign + mapping với event.

#### Backend (3-4 ngày)

| ID | Task | Files | Effort | Reference |
|----|------|-------|--------|-----------|
| BE-01 | Model `AffiliateCampaignRaw` (partner, title, desc, banner, commission, pub2_campaign_id, status, dates) | `internal/model/mg/affiliate.go` | 0.5d | `prd-affiliate-v1` FR-001 |
| BE-02 | Model `CampaignAffiliateMappingRaw` (event_id, affiliate_campaign_id) — many-to-many | `internal/model/mg/affiliate.go` | 0.25d | FR-003 |
| BE-03 | Service `internal/service/affiliate.go` (business logic: validate pub2_campaign_id unique, status transitions) | `internal/service/affiliate.go` | 1d | FR-015 |
| BE-04 | Admin handler + service + router cho CRUD: `POST/GET/PUT /admin/affiliate-campaigns`, `PATCH .../status` | `pkg/admin/{handler,service,router}/affiliate.go` | 1d | FR-001/002/015 |
| BE-05 | Admin handler cho mapping: `POST /admin/events/:id/affiliate-campaigns`, `DELETE .../:affId`, `GET .../by-event/:eventId`, `GET .../by-affiliate/:affId` | `pkg/admin/handler/affiliate.go` | 1d | FR-003 |
| BE-06 | Validation rules + request/response models | `pkg/admin/model/{request,response}/affiliate.go` + `pkg/admin/router/routevalidation/affiliate.go` | 0.5d | — |

#### Admin UI (2-3 ngày)

| ID | Task | Files | Effort | Reference |
|----|------|-------|--------|-----------|
| AD-01 | Model + service layer (DVA + API client) | `admin/src/pages/affiliate-campaign/{model.ts,type.d.ts}` + `services/affiliate-campaign.ts` | 0.5d | — |
| AD-02 | List page với filter status, search title, bulk activate/deactivate | `admin/src/pages/affiliate-campaign/{index.tsx,components/{table,filter}.tsx}` | 1d | FR-002 |
| AD-03 | Create/Edit modal (form với partner, title, desc, banner upload, commission, pub2 fields, dates) | `admin/src/pages/affiliate-campaign/components/modal.tsx` | 1d | FR-001 |
| AD-04 | Detail page với tab "Campaigns đã liên kết" + autocomplete để link/unlink event | `admin/src/pages/affiliate-campaign/detail/index.tsx` | 1d | FR-003 |
| AD-05 | Tab "Affiliate Campaigns liên kết" trong Event Detail (existing page) | `admin/src/pages/event/detail/components/` | 0.5d | FR-003 |

**Done when:** Admin có thể tạo, edit, activate/deactivate affiliate campaign và liên kết với event.

---

### Phase 2 — Creator Affiliate Experience (7-9 ngày)

**Mục tiêu:** Creator thấy affiliate campaign trong event, join, tạo link affiliate.

#### Backend (3-4 ngày)

| ID | Task | Files | Effort | Reference |
|----|------|-------|--------|-----------|
| BE-07 | Model `AffiliateContractRaw` (user_id, affiliate_campaign_id, contract_no, contract_status, retry_at) | `internal/model/mg/affiliate.go` | 0.25d | FR-017 |
| BE-08 | Model `AffiliateLinkRaw` (user_id, affiliate_campaign_id, original_url, affiliate_link, short_link, sub params) | `internal/model/mg/affiliate.go` | 0.25d | FR-005 |
| BE-09 | Pub2 client method: `JoinCampaign(partnerCode, ssoId, partnerRefCampaignId)` (API 1.2) | `internal/module/pub2/client.go` | 0.5d | API-1.2 |
| BE-10 | Pub2 client method: `GenerateAffiliateLink(ssoUserId, campaignId, originalUrl, sub1-5)` (API 2) | `internal/module/pub2/client.go` | 0.5d | API-2 |
| BE-11 | Public APIs cho Creator: `GET /events/:id/affiliate-campaigns`, `GET /affiliate-campaigns/:id` | `pkg/public/{handler,service,router}/affiliate.go` | 1d | FR-004 |
| BE-12 | Public APIs: `POST /affiliate-campaigns/:id/join`, `GET .../contract` (với retry logic PENDING/REJECTED) | `pkg/public/handler/affiliate.go` + `internal/service/affiliate.go` | 1d | FR-017 |
| BE-13 | Public APIs: `POST /affiliate-campaigns/:id/generate-link`, `GET /affiliate-links` | `pkg/public/handler/affiliate.go` | 1d | FR-005, FR-016 |
| BE-14 | Middleware/guard: chỉ cho phép join/generate khi `user.AT != nil` (đã link AT/Scalef) | `pkg/public/router/routeauth/` hoặc service-level check | 0.25d | NFR-002 |
| BE-15 | Config retry: `AFFILIATE_RETRY_PENDING_SECONDS` (24h), `AFFILIATE_RETRY_REJECTED_SECONDS` (14d) | `internal/config/env.go` | 0.25d | FR-017 |

#### Frontend (Creator) (4-5 ngày)

> **Lưu ý:** vcreator có 3 frontend (`frontend`, `frontend-vcreator`, `frontend-green`). Cần xác định FE nào là "creator-facing". Mặc định dùng `frontend-vcreator` cho build mới, copy sang nếu cần.

| ID | Task | Files | Effort | Reference |
|----|------|-------|--------|-----------|
| FE-01 | Service layer + interfaces (TypeScript types) | `frontend-vcreator/src/services/affiliate.ts` + `interfaces/affiliate.ts` | 0.5d | — |
| FE-02 | Component `AffiliateCampaignsSection` trong event detail (grid 1-2 cột) | `frontend-vcreator/src/pages/.../affiliate-campaigns-section/` | 1d | FR-004 |
| FE-03 | Component `AffiliateItemCard` (banner, title, badges hoa hồng/thưởng/thời gian, CTA "Khám phá") | `frontend-vcreator/src/pages/.../affiliate-item-card/` | 0.5d | FR-004 |
| FE-04 | Page `affiliate-campaign-detail` (2-col desktop, stack mobile, tabs Thể lệ/Hướng dẫn, accordion từ markdown desc) | `frontend-vcreator/src/pages/affiliate-campaign-detail/` | 1.5d | FR-018 |
| FE-05 | Logic join campaign + states (PENDING banner vàng + countdown, REJECTED banner đỏ + countdown, APPROVED hiển thị nút "Tạo link") | `frontend-vcreator/src/pages/affiliate-campaign-detail/index.tsx` | 1d | FR-017 |
| FE-06 | Logic generate affiliate link + copy + lưu danh sách link đã tạo | Same page | 0.5d | FR-005 |
| FE-07 | Page "Danh sách link affiliate của tôi" | `frontend-vcreator/src/pages/account/.../my-affiliate-links/` | 0.5d | — |

**Done when:** Creator đã link AT có thể vào event detail → thấy affiliate section → vào detail → join → tạo link → copy.

---

### Phase 3 — AT Linking Touchpoints (UI) (3-4 ngày)

**Mục tiêu:** Hoàn thiện UX liên kết Scalef từ phía creator. Backend đã có sẵn, chỉ thiếu UI.

| ID | Task | Files | Effort | Reference |
|----|------|-------|--------|-----------|
| FE-08 | Trang `/account/management/at-linking` (form nhập email + phone, gọi `/users/link-account`, xử lý các response code: success / CONFIRM_REQUIRED / PHONE_DUPLICATE_KYC_DIFFERENT_EMAIL / ACCOUNT_CONFLICT) | `frontend-vcreator/src/pages/account/management/at-linking/` | 1.5d | Service đã có ở `service/user.go:LinkAccountToAt` |
| FE-09 | Flow OTP confirm-phone-update (popup nhập OTP, gọi `/users/update-phone-number`) | Same page | 1d | `service/user.go:ConfirmUpdatePhoneNumber` |
| FE-10 | Banner "Liên kết Scalef" trong `AffiliateCampaignsSection` (chỉ hiển thị khi `user.at == null`) + popup khi user bấm join/generate-link mà chưa link | `frontend-vcreator/src/pages/.../affiliate-campaigns-section/` | 0.5d | FR-013 (Ambassador) |
| FE-11 | Hiển thị trạng thái "Đã liên kết AT (username: xxx)" ở settings/account khi `user.at != null` | `frontend-vcreator/src/pages/account/management/components/` | 0.5d | — |
| FE-12 | Service layer: `linkAccount(email, phone)`, `confirmUpdatePhone(email, phone, isSync)`, `getMe()` returning AT field | `frontend-vcreator/src/services/user.ts` | 0.25d | — |

**Done when:** Creator chưa link AT có thể từ banner / popup → hoàn tất link Scalef → quay lại affiliate campaign join được.

---

## 5. Tổng hợp effort

| Phase | Backend | Frontend/Admin | Total |
|-------|---------|----------------|-------|
| Phase 0: Foundation | 2.75d | — | **2.75d** |
| Phase 1: Admin CRUD + Mapping | 4.25d | 4d (Admin) | **8.25d** |
| Phase 2: Creator Experience | 4.5d | 5d (FE) | **9.5d** |
| Phase 3: AT Linking UI | — | 3.75d (FE) | **3.75d** |
| **Tổng** | **~11.5d** | **~12.75d** | **~24d (~3.5 tuần BE+FE song song)** |

> Effort estimate cho 1 BE + 1 FE làm song song. Phase 0 → Phase 1 BE + Phase 3 FE có thể chạy song song. Phase 2 BE + FE cần phối hợp chặt.

---

## 6. Risk & Open Questions

### Technical risks

| # | Risk | Mitigation |
|---|------|-----------|
| R-1 | Pub_BE signature format khác Pub2 → có thể không reuse được client hiện tại | Phase 0 task F-01 verify trước; nếu khác → tạo `pub2/` module riêng (theo pattern Ambassador) |
| R-2 | `frontend` vs `frontend-vcreator` vs `frontend-green` — chưa rõ creator-facing là cái nào | Cần xác nhận với team; mặc định dùng `frontend-vcreator` |
| R-3 | Account-linking hiện tại không có flow OAuth SSO như Scalef PRD (chỉ có form email+phone) — có cần upgrade lên OAuth không? | Trong scope V1: giữ nguyên flow hiện tại. OAuth là Phase 2 của Scalef integration (out of scope V1) |
| R-4 | Event partner restriction (Ambassador chỉ map affiliate cho cùng partner) — VCreator có cần không? | Check business: nếu VCreator multi-partner thì áp dụng rule như Ambassador |
| R-5 | Generated affiliate link store trong MongoDB — có cần cap số lượng / quota per user? | Thống nhất với product: V1 chưa cần cap |

### Open questions cần product làm rõ

1. **Endpoint Pub2 dev/staging/prod** cho VCreator: dùng chung với Ambassador hay riêng?
2. **`partner_code`** trong API JoinCampaign: VCreator dùng giá trị gì? (Ambassador dùng `PARTNER_1_POINT_5`)
3. **Tax/payment**: hoa hồng affiliate hợp nhất với cashflow vcreator hay tách riêng? (V1 không trong scope, V2 reports mới chạm)
4. **Sub params (sub1-5)** dùng để track gì? Ambassador dùng `sub2 = 'AMBASSADOR'` để identify tenant — VCreator nên dùng `sub2 = 'VCREATOR'`
5. **Notification**: khi contract chuyển từ PENDING → APPROVED, có cần push notification không? (V1 có thể skip)

---

## 7. Out of scope V1 → V2 backlog

| Feature | Reference |
|---------|-----------|
| Báo cáo click (API 3.1) | `prd-affiliate-v2-2026-03-31.md` |
| Báo cáo conversion (API 3.2) | V2 |
| Báo cáo sale amount (API 3.3) | V2 |
| Báo cáo commission (API 3.4) | V2 |
| Danh sách đơn (API 8) | V2 |
| Webhook Pub2 → vcreator | V2 |
| Affiliate dashboard cho creator (clicks, orders, commission, total) | V2 (tham khảo `roadmap-vcreator-2026/dashboard-overview.md`) |
| Withdraw hoa hồng affiliate riêng / hợp nhất với cashflow | V2 |
| OAuth SSO Scalef (thay form link-account hiện tại) | Scalef integration phase 2 |
| Batch migration legacy publishers | Scalef Phase 1c (nếu cần) |

---

## 8. Validation checklist trước khi go-live V1

- [ ] Admin tạo được affiliate campaign + mapping với event
- [ ] Affiliate campaign có status `inactive` mặc định, chỉ active mới hiển thị cho creator
- [ ] Creator chưa link AT → thấy banner liên kết, không join được (popup yêu cầu link)
- [ ] Creator đã link AT → join campaign → contract status PENDING / APPROVED / REJECTED
- [ ] PENDING → countdown 24h → cho retry
- [ ] REJECTED → countdown 14d → cho retry
- [ ] APPROVED → tạo affiliate link thành công, link copy được
- [ ] Affiliate link store trong MongoDB và list được ở trang "Link của tôi"
- [ ] Pub2 API logs ghi đầy đủ request/response cho debug
- [ ] HMAC signature verify được bằng curl/postman với credentials thật
- [ ] Mobile responsive ≥ 320px cho tất cả pages
- [ ] Permission: admin APIs yêu cầu admin role; public APIs yêu cầu login + AT linked

---

## 9. Lệ thuộc & lập lịch

```
Phase 0 (Foundation) → 2.75d
        ↓
Phase 1 BE → 4.25d ────┐
                       ├── Phase 2 BE → 4.5d ──── Phase 2 FE → 5d
Phase 1 Admin UI → 4d ─┘                          
                                                  
Phase 3 FE (3.75d) — có thể chạy song song bất kỳ lúc nào sau Phase 0
```

**Critical path:** Phase 0 → Phase 1 BE → Phase 2 BE → Phase 2 FE = ~16.5 ngày
**Có buffer 20%:** ~20 ngày làm việc thực tế.

---

## 10. Phụ lục — File mapping nhanh (Ambassador → VCreator)

| Ambassador file | VCreator file (cần tạo) |
|-----------------|-------------------------|
| `backend/internal/model/mg/affiliate.go` | `backend/internal/model/mg/affiliate.go` |
| `backend/internal/module/pub2/client.go` | `backend/internal/module/pub2/client.go` |
| `backend/internal/service/affiliate.go` | `backend/internal/service/affiliate.go` |
| `backend/pkg/admin/handler/affiliate.go` | `backend/pkg/admin/handler/affiliate.go` |
| `backend/pkg/public/handler/affiliate.go` | `backend/pkg/public/handler/affiliate.go` |
| `admin/src/pages/affiliate-campaign/` | `admin/src/pages/affiliate-campaign/` |
| `frontend/src/pages/affiliate-campaign-detail/` | `frontend-vcreator/src/pages/affiliate-campaign-detail/` |
| `frontend/src/pages/home/components/affiliate-campaigns-section/` | `frontend-vcreator/src/pages/.../affiliate-campaigns-section/` |
| `frontend/src/services/affiliate.ts` | `frontend-vcreator/src/services/affiliate.ts` |
