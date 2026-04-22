# PRD — API Get Share Link

**Tác giả:** bmad-agent (brainstorm session với owner)
**Ngày:** 2026-04-21 (revised 2026-04-22)
**Trạng thái:** Draft — chờ duyệt implement

**Changelog:**
- **2026-04-22:** (1) Thêm `utm_aff=share_link` cho mọi share-flow URL (aff-link tracking URL + body AT `product_link/create`). (2) Server-brand **luôn truyền `clickId`** ngay cả khi share=true → `utm_term` không rỗng, tiktok `utm_content` có format đầy đủ.
**Reference:**
- Brainstorm session: [_bmad-output/brainstorming/brainstorming-session-2026-04-21.md](../../_bmad-output/brainstorming/brainstorming-session-2026-04-21.md)
- AccessTrade API docs: [API_CREATE_SHARE_LINK.md](./API_CREATE_SHARE_LINK.md)
- Code tham chiếu: [app/service/brand_v2.go:99](../app/service/brand_v2.go#L99), [app/service/brand.go:142](../app/service/brand.go#L142), [internal/util/generate_url.go:221](../internal/util/generate_url.go#L221)

---

## 1. Tổng quan (Overview)

### 1.1. Bối cảnh

Hệ thống atcashback (B2B) hiện cung cấp endpoint `GET /v2/brands/generate-url` để sinh **affiliate link** (aff-link). Aff-link này dùng cho use case **user click vào để mua hàng** — khi user click, click event được track qua `clickID`, sinh trace vào Redis, và user hưởng cashback khi đơn hoàn tất.

Partner B2B hiện muốn mở thêm tính năng **chia sẻ link kiếm tiền**: user copy 1 đường link, gửi cho bạn bè/mạng xã hội; khi người nhận click và mua hàng, **người share nhận commission**.

Để UX tốt (link ngắn, đẹp, copy-paste thuận tiện), cần trả về **shortlink** thay vì aff-link dạng dài `https://tracking.accesstrade.vn/deep_link/...?utm_*=...&sub*=...`. AccessTrade có sẵn API `POST /v1/product_link/create` trả về `short_link` dạng `https://shorten.accesstrade.me/xxxxxxxx`.

### 1.2. Vấn đề cần giải quyết

- App frontend (webview) cần hiển thị **shortlink để user share**.
- App frontend không gọi trực tiếp AccessTrade (không nắm token AT, không duplicate business logic utm/sub).
- Server-brand (BE trung gian) cần 1 endpoint ở system có thể gọi để lấy shortlink cho 1 URL bất kỳ, tương tự cách nó đang gọi `generate-url`.

### 1.3. Giải pháp đề xuất ở tầng cao

**Mở rộng endpoint `GET /v2/brands/generate-url` hiện có** bằng query param `share=true`. Khi flag này bật:

1. Tái dùng 100% pipeline resolve URL hiện có (`getFinalURL` → `preprocessURL` → `getBrandAndNetworkByURL`).
2. Ép nhánh build aff-link đi V2 (logic V2 có `utm_medium = hash(userID)` để tracking user share).
3. Thêm 1 HTTP call ra AccessTrade `POST /v1/product_link/create` để lấy `short_link`.
4. Bỏ mọi PushTrace và Redis `SAdd active_ids` (vì share-link không phải click event).
5. Trả về response cũ + field mới `shortLink`.

---

## 2. Mục tiêu & Phi mục tiêu

### 2.1. Mục tiêu (Goals)

- **G1.** Cho phép partner B2B (qua server-brand) lấy được **shortlink AccessTrade** cho 1 URL sản phẩm bất kỳ (Shopee, Lazada, TikTok Shop).
- **G2.** Tái dùng tối đa code hiện có; không tạo controller/service/route riêng.
- **G3.** Giữ **utm/sub tracking signature nhất quán với click-flow** để BI không phải maintain 2 logic attribution. **Thêm marker `utm_aff=share_link`** để BI có 1 field đơn lẻ filter share-traffic (thay cho trick check `utm_term` rỗng).
- **G4.** Đảm bảo **graceful degrade**: khi AT fail/timeout, vẫn trả HTTP 200 với `shortLink = ""` để webview tự fallback.
- **G5.** Ship được trong **1 sprint** (≤ 150 LOC mới, ≤ 7 file impact).

### 2.2. Phi mục tiêu (Non-goals)

- **N1.** KHÔNG cache shortlink ở system — server-brand tự quản lý unique/dedupe theo policy của nó.
- **N2.** KHÔNG rate-limit anti-abuse ở endpoint share — share-link là public-by-design.
- **N3.** KHÔNG implement signed URL / expiring token cho shortlink.
- **N4.** KHÔNG hỗ trợ batch multi-URL trong 1 request (có thể làm sau).
- **N5.** KHÔNG hỗ trợ network source ngoài AccessTrade family (Shopee direct, Lazada direct, Tiki, Ecomobi, Adpia, Optimise, Cityads, Masoffer…) — trả `shortLink = ""` cho các source này.
- **N6.** KHÔNG thêm `PushTrace` riêng cho AT `product_link/create` call — sẽ có bảng tracking request chuyên dụng (out-of-scope PRD này).
- **N7.** KHÔNG thêm layer security/authorization đặc biệt ngoài RequireLogin hiện có.

---

## 3. Stakeholders

| Vai trò | Tên/Đội | Quan tâm chính |
|---|---|---|
| Product Owner | (đang thu thập) | UX share-link, tỉ lệ convert |
| Backend (system) | Team atcashback | Implementation, ổn định |
| Server-brand | Team server-brand | Contract API, retry/fallback behavior |
| App/Webview | Team app | Hiển thị shortlink, xử lý empty case |
| BI/Analytics | Team data | Tracking attribution, phân biệt click vs share |
| AccessTrade | Đối tác ngoài | Rate limit API `product_link/create` |

---

## 4. User Stories

### 4.1. Primary

**US-01 — Partner user share link kiếm tiền**
> **Là** một người dùng B2B đã login vào app partner,
> **tôi muốn** lấy được 1 shortlink đẹp từ URL sản phẩm bất kỳ,
> **để** tôi copy-paste gửi cho bạn bè qua Zalo/Facebook/SMS,
> **và khi** người nhận click vào shortlink, mua hàng, **tôi nhận được commission** về tài khoản.

**Acceptance criteria:**
- Copy-paste shortlink vào Zalo hiện preview đẹp (shortlink ngắn < 50 ký tự).
- Click vào shortlink → redirect đúng về trang sản phẩm Shopee/Lazada/Tiktok.
- Đơn hàng từ click này được commission về đúng `userID` của người share (không về người click).
- Shortlink active ít nhất 30 ngày (theo AT TTL).

---

**US-02 — Server-brand request shortlink**
> **Là** server-brand (BE trung gian),
> **tôi muốn** gọi 1 endpoint REST đơn giản để lấy shortlink cho URL sản phẩm,
> **để** trả về webview mà không phải implement logic affiliate phức tạp.

**Acceptance criteria:**
- Endpoint trả về response có field `shortLink`.
- Request shape tương tự `generate-url` hiện có — chỉ thêm query param `share=true`.
- Không yêu cầu server-brand phải biết `campaign_id`, utm rules, hay AT token.
- Nếu AT fail, `shortLink` rỗng chứ không HTTP 500 → server-brand fallback về `url` (aff-link dài) dễ dàng.

---

### 4.2. Secondary

**US-03 — BI phân biệt click traffic vs share traffic**
> **Là** BI analyst,
> **tôi muốn** nhìn vào tracking record (conversion, click log) và biết nó đến từ aff-link click hay share-link,
> **để** tính CR riêng, ROI riêng cho feature share.

**Acceptance criteria:**
- Share-flow có marker riêng `utm_aff=share_link` trong mọi aff-link + shortlink.
- Click-flow **không có** `utm_aff`.
- BI filter share-traffic chỉ cần 1 điều kiện: `utm_aff = 'share_link'`.
- Cả click-flow và share-flow đều có `utm_medium = hash(userID)` (attribution user consistent).

---

**US-04 — App handle empty shortlink**
> **Là** app developer maintain webview,
> **tôi muốn** biết shortlink có thể rỗng,
> **để** tôi hiển thị UI fallback phù hợp (ẩn nút "Copy short", giữ nút "Copy link" dài).

**Acceptance criteria:**
- API doc mô tả rõ `shortLink` có thể là empty string.
- Empty không có nghĩa error — vẫn có `url` (aff-link dài) dùng được.

---

## 5. Use Cases

### UC-01 — Happy path: Share Shopee product

**Actor:** User A (logged in, partner X)

**Flow:**
1. User A mở app partner, browse sản phẩm Shopee.
2. User A bấm nút "Share"/"Lấy link kiếm tiền".
3. Webview gọi server-brand: "lấy shortlink cho URL `https://shopee.vn/-i.123.456`".
4. Server-brand gọi `GET /v2/brands/generate-url?url=https://shopee.vn/-i.123.456&share=true` (có header Authorization JWT của User A).
5. System:
   - Resolve URL qua `getFinalURL` → `https://shopee.vn/-i.123.456`.
   - Preprocess → `https://shopee.vn/universal-link/product/123/456`.
   - Lookup brand/network → Shopee/AccessTrade.
   - Build aff-link V2: `https://tracking.accesstrade.vn/deep_link/{campaign}?url=...&utm_campaign={rootID}&utm_medium={hash(userID)}&utm_content=&utm_source={partnerID}&utm_term=`.
   - Call AT `POST /v1/product_link/create` → nhận `short_link = https://shorten.accesstrade.me/abc123`.
6. System trả response:
   ```json
   {
     "url": "https://tracking.accesstrade.vn/deep_link/...",
     "shortLink": "https://shorten.accesstrade.me/abc123",
     "shopId": "123", "productId": "456",
     "brandId": "...", "redirectUrl": "...",
     "openVia": "...", "isRed": false
   }
   ```
7. Server-brand trả webview → user copy `shortLink`, paste vào Zalo.
8. Bạn của user click shortlink → AT redirect về Shopee → mua hàng → commission về User A.

---

### UC-02 — AT `product_link/create` timeout

**Actor:** User B

**Flow:**
1. Bước 1-5 như UC-01.
2. AT `product_link/create` timeout sau 3s.
3. System catch error, **không retry**, trả `shortLink = ""`.
4. Response:
   ```json
   {
     "url": "https://tracking.accesstrade.vn/deep_link/...",
     "shortLink": "",
     ...
   }
   ```
5. Webview detect `shortLink == ""` → ẩn nút "Share link ngắn", hiện nút "Copy link dài" (từ field `url`).

---

### UC-03 — Share URL với source không phải AccessTrade

**Actor:** User C

**Precondition:** User truyền URL của brand có `network.Source = SourceShopeeNew` (gọi Shopee API trực tiếp, không qua AT).

**Flow:**
1. Bước 1-4 như UC-01.
2. System check `isATFamilySource(network.Source)` → false.
3. **Skip hoàn toàn call AT `product_link/create`**.
4. Trả response với `shortLink = ""`.
5. Webview hiển thị nút "Copy link" (từ `url`) bình thường.

---

### UC-04 — Share URL đã là shortlink shopee (`s.shopee.vn/xxx`)

**Actor:** User D

**Flow:**
1. User truyền `url = https://s.shopee.vn/ABC`.
2. System `getFinalURL` resolve → `https://shopee.vn/product/123/456` (qua AT `/get-dest-url` hoặc headless).
3. Preprocess → universal-link.
4. Phần còn lại như UC-01.

→ Transparent với user, không có logic đặc biệt.

---

### UC-05 — Partner không phải OneAT

**Flow:**
- Request body AT gửi: `urls` ở plain text (không Base64), `utm_content` rỗng.

### UC-06 — Partner là OneAT

**Flow:**
- Request body AT gửi: `urls` ở Base64, `url_enc: true`, `utm_content = userID`.

---

## 6. Functional Requirements (Contract)

### 6.1. Endpoint

```
GET /v2/brands/generate-url
```

(Giữ nguyên endpoint hiện có — chỉ mở rộng.)

### 6.2. Request

**Headers:**
- `Authorization: Bearer <JWT>` — RequireLogin (giữ nguyên)
- `X-Partner-Id: <partnerID>` — getPartnerId middleware (giữ nguyên)

**Query Params (new):**

| Param | Type | Required | Default | Mô tả |
|---|---|---|---|---|
| `url` | string | Yes | — | URL sản phẩm (raw hoặc shortened) |
| `share` | bool | No | `false` | **MỚI** — Khi `true`, sinh thêm shortlink và gắn `utm_aff=share_link` |
| `clickId` | string | No | `""` | **Server-brand luôn truyền** (cả click-flow và share-flow). Rỗng chỉ ở legacy client. |
| `platform` | string | No | — | iOS/Android/Web (giữ nguyên) |
| `addInfo` | string | No | — | Format `sub3:xxx,sub4:yyy` (giữ nguyên) |

### 6.3. Response (200)

```json
{
  "url": "string",
  "shopId": "string",
  "shopSlug": "string",
  "productId": "string",
  "brandId": "string",
  "redirectUrl": "string",
  "openVia": "string",
  "isRed": false,
  "shortLink": "string"
}
```

**Field mới:**

| Field | Type | Khi nào có giá trị |
|---|---|---|
| `shortLink` | string | Non-empty **chỉ khi** `share=true` + `network.Source` ∈ AccessTrade family + AT call thành công. Các case khác: `""`. Omit khỏi JSON khi rỗng (`omitempty`). |

### 6.4. Response (400)

Giữ nguyên contract cũ — share=true **không** đổi logic validate URL.

### 6.5. Errors cần handle

| Error case | Behavior khi `share=true` |
|---|---|
| `url` rỗng | 400, giống cũ |
| `url` invalid URI | 400, giống cũ |
| Không resolve được final URL | 400, giống cũ |
| Không lookup được brand | 400, giống cũ |
| AT `product_link/create` timeout | 200, `shortLink: ""` |
| AT `product_link/create` trả `success: false` | 200, `shortLink: ""` |
| AT `product_link/create` trả `success_link: []` rỗng | 200, `shortLink: ""` |
| `network.Source` không phải AT family | 200, `shortLink: ""` |

### 6.6. Request AT `product_link/create` — body

**Non-OneAT partner:**
```json
{
  "campaign_id": "<network.CampaignID>",
  "urls": ["<info.FinalURL>"],
  "utm_source": "<partnerID hoặc affAccountID>",
  "utm_campaign": "<rootID>",
  "utm_medium": "<ASCEncrypt(userID)>",
  "utm_content": "",
  "utm_aff": "share_link"
}
```

**OneAT partner:**
```json
{
  "campaign_id": "<network.CampaignID>",
  "urls": ["<Base64(info.FinalURL)>"],
  "url_enc": true,
  "utm_source": "<partnerID hoặc affAccountID>",
  "utm_campaign": "<rootID>",
  "utm_medium": "<ASCEncrypt(userID)>",
  "utm_content": "<userID>",
  "utm_aff": "share_link"
}
```

**Note:** `sub1`, `sub2` nếu cần thêm clickID cho AT tracking, có thể map `sub1 = clickID` (tương đương `utm_term` trong aff-link). Nhưng AT `product_link/create` không có `utm_term` field → quyết định dùng `sub1` cần confirm BI team (xem Open Question Q4).

**Với `addInfo` có sub3/sub4:**
Thêm vào body `"sub3": "<value>"`, `"sub4": "<value>"` (giới hạn chỉ 2 key này theo logic `assignATAddInfo` hiện có).

---

## 7. Non-functional Requirements

### 7.1. Performance

| Metric | Target |
|---|---|
| Latency p95 (share=true) | ≤ 1500 ms (pipeline cũ p95 ~700ms + AT call ~500ms = 1200ms buffer) |
| Latency p99 (share=true) | ≤ 3000 ms |
| Timeout AT `product_link/create` | 3s (hard) — dùng `context.WithTimeout` |
| Không retry | Fail một lần → trả `shortLink: ""` |

### 7.2. Observability

| Gì | Có? |
|---|---|
| PushTrace cho share-flow | **Không** (skip tất cả) |
| SAdd Redis active_ids | **Không** |
| Log error AT fail | **Có** — `log.Println` là đủ, cho debug local |
| Bảng tracking riêng cho AT call | Out-of-scope — do infra team làm riêng |

### 7.3. Security

- Giữ middleware `RequireLogin` → chỉ user logged-in mới gọi được.
- Giữ middleware `getPartnerId` + `setPartnerIdAndClientId` để scope request.
- Không thêm rate-limit riêng cho `share=true`.

### 7.4. Backward compatibility

- Client cũ không truyền `share` → `share = false` (default) → behavior 100% như trước.
- Field `shortLink` có `omitempty` → không xuất hiện trong response khi `share=false` → struct client cũ không break.

---

## 8. Technical Design (Hướng giải quyết)

### 8.1. Architecture decision

**Quyết định:** Không tách endpoint mới — mở rộng `generate-url` hiện có bằng query param `share=true`.

**Lý do:**
- Toàn bộ pipeline resolve/preprocess/brand-lookup tái dùng được 100%.
- Contract request giống hệt (chỉ thêm 1 param) → server-brand dễ integrate.
- Giảm code duplicate; 1 test suite cover cả 2 flow.

**Alternative đã cân nhắc và loại:**
- Tách endpoint riêng `/v2/brands/get-share-link` — duplicate route wiring, lặp code, khó maintain khi pipeline thay đổi.
- Để server-brand call AT trực tiếp — leak business logic, phải share AT token.

### 8.2. Data flow

```
Client (webview)
   │
   ▼
Server-brand
   │ GET /v2/brands/generate-url?url=...&share=true
   ▼
System (atcashback)
   │
   ├─ Controller: skip PushTrace + SAdd khi share=true
   │
   ├─ Service GenerateURLV2:
   │    ├─ validate URL
   │    ├─ BrandRedirectClickMatchCondition (giữ nguyên)
   │    ├─ getFinalURL (giữ nguyên)
   │    ├─ preprocessURL (giữ nguyên)
   │    ├─ getBrandAndNetworkByURL (giữ nguyên)
   │    ├─ BrandGenerateURL:
   │    │     └─ getFinalURLBySource:
   │    │           └─ if clickID=="" && !share { V1 } else { V2 với Share: p.Share }
   │    │
   │    └─ if p.Share && isATFamilySource:
   │           └─ util.GenerateShareShortLink(ctx, payload)
   │                 └─ POST https://api.accesstrade.vn/v1/product_link/create
   │
   └─ Response: append field shortLink (có thể rỗng)
```

### 8.3. File changes (ordered)

| # | File | Thay đổi | Est LOC |
|---|---|---|---|
| 1 | `app/model/brand_v2.go` | Thêm `Share bool` vào `BrandGenURLParamV2`; `ShortLink string` vào `BrandGenURLResV2` | +2 |
| 2 | `internal/util/generate_url.go` | Thêm `Share bool` vào `GenURLATPayload`; adjust guard V2; adjust tiktok `utm_content` | +8 |
| 3 | `app/service/brand.go` | Đổi điều kiện rẽ nhánh V1/V2: `if clickId == "" && !p.Share` | +2 |
| 4 | `internal/util/generate_share_link.go` | **MỚI** — hàm `GenerateShareShortLink` gọi AT `product_link/create` | ~90 |
| 5 | `app/service/brand_v2.go` | Thêm block gọi share sau `BrandGenerateURL`; tách helper `resolveAffAccountID` | +40 |
| 6 | `app/controller/brand_v2.go` | Wrap mọi `PushTrace` + `SAdd` bằng `if !param.Share` | +6 |
| 7 | `internal/config/*` + Zookeeper | Thêm key `ATProductLinkCreateURL` = `https://api.accesstrade.vn/v1/product_link/create` | +2 |

**Tổng: ~150 LOC mới, 0 file xóa.**

### 8.4. Core logic changes

**8.4.1. V1/V2 branching ([app/service/brand.go:215](../app/service/brand.go#L215))**

```go
// BEFORE
if clickId == "" {
    finalURL = util.GenerateURLForAccessTrade(...)
} else {
    finalURL = util.GenerateURLForAccessTradeVersionII(...)
}

// AFTER
if clickId == "" && !p.Share {
    finalURL = util.GenerateURLForAccessTrade(util.GenURLATPayload{
        // ... existing fields
    })
} else {
    finalURL = util.GenerateURLForAccessTradeVersionII(util.GenURLATPayload{
        // ... existing fields
        Share: p.Share,
    })
}
```

**8.4.2. V2 guard ([internal/util/generate_url.go:278](../internal/util/generate_url.go#L278))**

Vì server-brand luôn truyền `clickId` (cả click-flow lẫn share-flow), `p.ClickID` thường non-empty. Vẫn giữ adjust guard để **defensive** cho legacy client không truyền clickId nhưng vẫn share=true.

```go
// BEFORE
if p.RootID == "" || p.ClickID == "" {
    return p.URL
}

// AFTER
if p.RootID == "" || (p.ClickID == "" && !p.Share) {
    return p.URL
}
```

**Thêm `utm_aff=share_link` khi share=true:**

```go
q.Set("utm_campaign", p.RootID)
q.Set("utm_medium", hash)
q.Set("utm_source", p.getUTMSource())
q.Set("utm_term", p.ClickID)
if p.Share {
    q.Set("utm_aff", UTMAffShareLink)   // ← MỚI
}
assignATAddInfo(q, p.AddInfo)
```

**8.4.3. TikTok utm_content ([internal/util/generate_url.go:370](../internal/util/generate_url.go#L370))**

Vì server-brand luôn truyền clickId, đoạn này **thực tế không cần đổi**. Giữ format cũ `utmContent := p.UserID + "_" + p.ClickID`. Adjust chỉ để defensive:

```go
// DEFENSIVE (optional) — không làm vỡ khi clickID rỗng ở legacy client
utmContent := p.UserID
if p.ClickID != "" {
    utmContent = p.UserID + "_" + p.ClickID
}
```

**Thêm `utm_aff=share_link` vào TikTok request body:**

```go
type RequestPayload struct {
    ProductUrl  string `json:"product_url"`
    UTMSource   string `json:"utm_source"`
    UTMMedium   string `json:"utm_medium"`
    UTMCampaign string `json:"utm_campaign"`
    UTMContent  string `json:"utm_content"`
    UTMAff      string `json:"utm_aff,omitempty"`   // ← MỚI, omit khi không share
}

reqBody := RequestPayload{
    ProductUrl:  p.URL,
    UTMSource:   p.getUTMSource(),
    UTMMedium:   hash,
    UTMCampaign: p.RootID,
    UTMContent:  utmContent,
}
if p.Share {
    reqBody.UTMAff = UTMAffShareLink   // ← MỚI
}
```

**8.4.3a. Constant mới ([internal/util/generate_url.go](../internal/util/generate_url.go) — top-level)**

```go
const UTMAffShareLink = "share_link"
```

**8.4.4. Service gọi shortlink ([app/service/brand_v2.go](../app/service/brand_v2.go))**

Chèn sau `BrandGenerateURL`:

```go
affURL := BrandGenerateURL(network, userID, p, brandInfo.Root, isRedirect)

var shortLink string
if p.Share && isATFamilySource(network.Source) {
    affAccountID := resolveAffAccountID(p, network)
    shortLink = util.GenerateShareShortLink(context.Background(), util.GenURLATPayload{
        AffAccID:   affAccountID,
        PartnerID:  p.PartnerID,
        URL:        info.FinalURL,
        RootID:     network.Root.Hex(),
        UserID:     userID.Hex(),
        CampaignID: network.CampaignID,
        AddInfo:    p.AddInfo,
        ClickID:    "",
        ClientID:   p.ClientID,
        Share:      true,
    })
}

return &appmodel.BrandGenURLResV2{
    // ... existing
    ShortLink: shortLink,
}, nil
```

**8.4.4a. Body AT `product_link/create` — thêm `utm_aff`**

Trong file mới `internal/util/generate_share_link.go`, khi build body gửi AT, **luôn** set `utm_aff`:

```go
body := map[string]interface{}{
    "campaign_id":  p.CampaignID,
    "utm_source":   p.getUTMSource(),
    "utm_campaign": p.RootID,
    "utm_medium":   hash,
    "utm_aff":      UTMAffShareLink,   // ← luôn set (hàm này chỉ gọi khi share=true)
    // ... utm_content, urls, url_enc tùy OneAT/non-OneAT
}
```

**8.4.5. Helper tách từ `getFinalURLBySource`**

```go
func isATFamilySource(src string) bool {
    return src == config.SourceAccessTrade || src == config.SourceAccessTradeCB
}

func resolveAffAccountID(p appmodel.BrandGenURLParamV2, network model.BrandNetworkBSON) string {
    if p.ClientID != "" {
        clientObjID := externalutil.GetObjectIDFromHex(p.ClientID)
        c, _ := dao.ClientFindByID(context.Background(), clientObjID)
        if c.Aff.PubID != "" {
            return c.Aff.PubID
        }
    } else if !network.AffAccountID.IsZero() {
        acc := dao.AffAccountFindByID(context.Background(), network.AffAccountID)
        if acc.AccountID != "" {
            return acc.AccountID
        }
    }
    return ""
}
```

**8.4.6. Controller wrap trace ([app/controller/brand_v2.go](../app/controller/brand_v2.go))**

```go
if !param.Share {
    if err := redisdb.SAdd("trace:active_ids", param.ClickID); err != nil {
        fmt.Println("Rediss add clickIds error: ", err)
    }
}

// Mọi PushTrace đều cần wrap:
if !param.Share {
    appservice.PushTrace(...)
}
```

Cân nhắc refactor thành helper:

```go
func pushTraceIfNotShare(share bool, p appmodel.TraceParams) {
    if !share {
        appservice.PushTrace(p)
    }
}
```

### 8.5. Config mới

**Zookeeper key:**
- `ATProductLinkCreateURL` — default `https://api.accesstrade.vn/v1/product_link/create`

**Load vào `internal/config`:**

```go
type EnvVariable struct {
    // ... existing
    ATProductLinkCreateURL string
}
```

---

## 9. Edge Cases & Behavior

| # | Edge case | Behavior |
|---|---|---|
| E1 | `share=true` + `clickId` có giá trị | **Default case** — server-brand luôn truyền clickId. V2 build aff-link với `utm_term = clickId` + `utm_aff = share_link`. AT `product_link/create` body cũng có `utm_aff = share_link`. |
| E11 | `share=true` + `clickId` rỗng (legacy client) | Defensive: V2 guard `(ClickID == "" && !Share)` cho qua vì Share=true. Build aff-link với `utm_term=` rỗng + `utm_aff = share_link`. Vẫn trả shortLink bình thường. |
| E2 | `share=true` + URL là TikTok Shop | `isATFamilySource` check `network.Source` — TikTok có thể là AT family (`SourceAccessTrade`) → vẫn gọi. Nếu là nhánh AT Tiktokshop v2 riêng (`generateURLForAccessTradeVersionIIForTiktokshop`), aff-link gen OK. `product_link/create` có support TikTok URL không? **→ cần verify với AT docs/team.** |
| E3 | `share=true` + URL không parse được brand | Lỗi ở `getBrandAndNetworkByURL` → HTTP 400 (giống cũ). Không sinh shortlink. |
| E4 | User không login (không có userID) | RequireLogin middleware chặn ở middleware. Không đến service. |
| E5 | `network.CampaignID` rỗng (brand config sai) | `GenerateShareShortLink` early return `""` → response `shortLink: ""`. Không crash. |
| E6 | AT token không có cho partner | Same as E5 — early return `""`. |
| E7 | `url` là URL của brand nước ngoài (không phải Shopee/Lazada/Tiktok VN) | `getBrandAndNetworkByURL` trả 400 "invalid URL" (giống cũ). |
| E8 | `share=true` nhưng `addInfo` có `sub1`, `sub2` | `assignATAddInfo` chỉ allow `sub3`, `sub4` → `sub1`, `sub2` ignored (giống cũ). |
| E9 | AT trả `success_link: [...]` nhiều item | Lấy item đầu: `resp.Data.SuccessLink[0].ShortLink`. |
| E10 | AT trả `error_link` non-empty, `success_link` rỗng | Coi như fail → `shortLink: ""`. |

---

## 10. Out of Scope

Các mục sau **KHÔNG** làm trong PRD này:

1. **Multi-URL batch share** — `urls: ["url1", "url2"]` trong 1 request (có thể mở rộng sau, AT đã support).
2. **Cache shortLink** ở system — để server-brand/client tự cache theo policy.
3. **Admin tool sinh shortlink** cho campaign marketing nội bộ — use case khác, PRD riêng.
4. **Analytics dashboard** "top shared products" — do BI team implement dựa trên bảng tracking AT.
5. **Rate limit/anti-abuse** cho endpoint — trust server-brand; nếu cần, đặt ở API gateway sau.
6. **Source khác AccessTrade** (Shopee direct, Lazada direct, v.v.) — trả `shortLink: ""` cho MVP; mở rộng khi có use-case thật.
7. **Bảng tracking request AT** — infra team xử lý riêng, không block MVP này.

---

## 11. Success Metrics

**Sprint 0 (ship MVP):**
- [ ] Tất cả unit test pass (coverage ≥ 80% cho file mới).
- [ ] Integration test: gọi endpoint với `share=true` trên staging → nhận được shortlink hợp lệ.
- [ ] Latency p95 ≤ 1500ms trên staging (measure qua Grafana/APM hiện có).
- [ ] Không regression ở `share=false` flow (diff-test với response cũ).

**Sprint +1 → +4 (sau launch):**
- [ ] **Adoption:** số request `share=true` / tổng request `generate-url` ≥ 20% sau 2 tuần.
- [ ] **Success rate AT:** tỉ lệ request có `shortLink ≠ ""` ≥ 95%.
- [ ] **Error rate:** ≤ 0.1% endpoint trả HTTP 5xx.
- [ ] **Business:** commission từ share-flow / tổng commission ≥ 5% sau 1 tháng.

---

## 12. Rollout Plan

### 12.1. Phase 1 — Dev & Unit Test (3 ngày)
- Implement 7 file changes theo thứ tự spec.
- Unit test cho `GenerateShareShortLink` (happy + timeout + empty response).
- Regen swagger.

### 12.2. Phase 2 — Staging (2 ngày)
- Deploy lên develop env.
- Smoke test với Postman/curl.
- Server-brand team integrate staging.
- Webview team test hiển thị.

### 12.3. Phase 3 — Canary / Soft launch (1 tuần)
- Deploy production nhưng chỉ enable qua feature flag cho 1 partner (partner X test-pilot).
- Monitor latency, error rate.

### 12.4. Phase 4 — General Availability
- Enable cho mọi partner.
- Announce qua docs.

---

## 13. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| AT `product_link/create` rate limit bất ngờ | Medium | Medium | Timeout 3s hard, không retry; bảng tracking request để debug sau |
| V2 guard adjust làm regression aff-link cũ | Low | High | Unit test cover case `clickID != ""` và `share == false`; diff-test trên staging |
| `utm_term=` (rỗng) làm BI query lệch | Low | Low | Docs cho BI: share-flow có signature `utm_term rỗng` + `utm_medium != ""` |
| TikTok Shop `product_link/create` không support | Medium | Medium | Verify với AT team trước khi dev; nếu không, skip TikTok trong `isATFamilySource` |
| Server-brand không handle `shortLink == ""` → UI rác | Medium | Medium | Docs API rõ ràng; review server-brand code trước khi enable |
| Config `ATProductLinkCreateURL` sai env | Low | High | Test staging trước; config validate ở startup |

---

## 14. Open Questions

| # | Câu hỏi | Cần trả lời bởi | Deadline |
|---|---|---|---|
| Q1 | TikTok Shop URL có dùng được với AT `product_link/create` không? | AT support team / BA | Trước dev Phase 1 |
| Q2 | AT có hard limit (QPS) trên `product_link/create` không? | AT docs / account manager | Trước rollout GA |
| Q3 | Helper `pushTraceIfNotShare` hay inline `if !Share`? | Tech lead team atcashback | Trong PR review |
| Q4 | `sub1 = clickID` trong body AT `product_link/create` có cần không? (vì aff-link V2 đã có `utm_term = clickID`, còn shortlink AT không support utm_term). | BI team | Trước dev Phase 1 |
| Q5 | Shortlink TTL (30d? 90d? forever?) — có cần surface cho webview không? | AT docs | Có thể defer |

---

## 15. Appendix

### 15.1. AT `product_link/create` response schema (từ docs)

```json
{
  "data": {
    "error_link": [],
    "success_link": [
      {
        "aff_link": "https://tracking.dev.accesstrade.me/deep_link/...",
        "first_link": null,
        "short_link": "https://shorten.dev.accesstrade.me/ujrBHxpc",
        "url_origin": "https://shopee.vn"
      }
    ],
    "suspend_url": []
  },
  "success": true
}
```

### 15.2. So sánh V1 vs V2 (ref internal/util/generate_url.go)

| | V1 | V2 (other) |
|---|---|---|
| Guard | `RootID == "" \|\| UserID == ""` | `RootID == "" \|\| ClickID == ""` → adjust thành `RootID == "" \|\| (ClickID == "" && !Share)` |
| `utm_source` | `getUTMSource()` | `getUTMSource()` |
| `utm_campaign` | `RootID` | `RootID` |
| `utm_content` | `UserID` (luôn) | `UserID` (OneAT) / `""` (non-OneAT) |
| `utm_medium` | — | `ASCEncrypt(UserID)` |
| `utm_term` | — | `ClickID` (server-brand luôn truyền → non-empty) |
| `utm_aff` | — | **`share_link`** khi `p.Share = true`, otherwise không set |
| URL encoding | OneAT: `url_enc`; else `url` | Giống V1 |

### 15.3. Ideas từ brainstorm session

16 ideas được capture trong [_bmad-output/brainstorming/brainstorming-session-2026-04-21.md](../../_bmad-output/brainstorming/brainstorming-session-2026-04-21.md).

---

**End of PRD.**
