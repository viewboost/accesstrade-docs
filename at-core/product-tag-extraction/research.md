# Product Tag Extraction — Research Results

> Chi tiết các solution đã research & test để extract product tag / shop card từ Facebook, Instagram, TikTok.
>
> Cập nhật: 2026-04-21
>
> Xem [overview.md](./overview.md) để nắm bối cảnh.

---

## Tóm tắt bảng

| Solution | Feasibility | Cost MVP | Maintenance | Khuyến nghị |
|---|---|---|---|---|
| **Apify `pratikdani/facebook-post-scraper`** | ✅ 90% | $0 | Thấp | ✅ Phase 1 — làm ngay |
| **Comments mining** (đã có) | ✅ 80% | $0 | Thấp | ✅ Đã làm trong extract-links |
| **Caption URL extraction** (đã có) | ✅ 100% | $0 | Thấp | ✅ Đã làm trong extract-links |
| **Bright Data FB Dataset** | ? 60-80% | $50-100/th | Thấp | ⚠️ Phase 2 POC |
| **Audio transcript (Gemini/Whisper)** | ~60% | $0-30/th | Thấp | ⚠️ Phase 2 phụ trợ |
| **Phyllo / Modash / HypeAuditor** | ? 40-70% | $100-500/th | Thấp | ⚠️ Phase 2 nếu Bright Data fail |
| **Playwright headless mobile** | 35% | $300-500/th | **RẤT CAO** | ⚠️ Phase 3, last resort |
| **Mobile HTML scraping** | 40% | $100-500/th | **RẤT CAO** | ❌ Không đáng đầu tư |
| **OCR video frames** | 0% | N/A | N/A | ❌ Không khả thi về bản chất |
| **Meta Graph API chính thức** | 0% | $0 | N/A | ❌ Không dùng được cho random reel |

---

## 1. Apify Actors đã test

Token đã dùng: `${APIFY_TOKEN}` (plan FREE, user `vinhnguyen_diso`). Token thật lưu trong `.env` không commit.

### 1.1. `apify/facebook-posts-scraper` (actor crawler team đang dùng)

**Test 1**: Page `multitventertainment` với 3 reels.

**Test 2**: Post URL `https://www.facebook.com/watch/?v=1281155200078505` (Hằng Túi, đã tap được card "Mở Shopee").

**Kết quả chung**:
- Trả về: `text`, `textReferences` (chỉ hashtag URLs), `media`, `likes`, `comments`, `shares`
- **KHÔNG trả**: `product_tags`, `shop_items`, `call_to_action`, `cta`, `external_url`, `attached_products`
- Field `text` **rỗng** với post dạng photo / reel
- Field `attachments` chỉ chứa video metadata, không có product

**Verdict**: ❌ **Không đủ cho feature này**. Đang là nguồn lỗi "profile không có link" khi thực tế caption có URL.

### 1.2. `pratikdani/facebook-post-scraper` ⭐

**Test**: Post URL `https://www.facebook.com/watch/?v=1281155200078505` (Hằng Túi).

**Kết quả**:
```json
{
  "content": "Nào thì review chắc gì đã dùngggg :))) lượn nhà tắm 1 vòng cùng H xem nào\n\nhttps://collshp.com/hangtuichoice?view=storefront",
  "post_external_link": null,
  "post_external_title": null,
  "attachments": [
    {"attachment_url": "https://video.fist2-3.fna.fbcdn.net/.../video.mp4"}
  ],
  "marketplace_price": null,
  "is_sponsored": false,
  "page_followers": 458000,
  "video_view_count": 52095,
  ...
}
```

**Field quan trọng**:

| Field | Ý nghĩa | Hoạt động cho... |
|---|---|---|
| `content` | Full caption text | ✅ Photo, video, text post — **fix được case caption có URL** |
| `post_external_link` | URL của link-share post | ⚠️ Chỉ khi post là kiểu "share 1 link", không phải photo/video product tag |
| `post_external_title` | Title của link-share | ⚠️ Same |
| `attachments` | Video MP4 URL | ❌ Không chứa product tag |
| `marketplace_price` | Price cho FB Marketplace listing | ❌ Không áp dụng cho photo product tag thường |
| `is_sponsored` | Boolean — đúng = ad | ℹ️ Useful để filter |

**Khả năng**:
- ✅ Fix ~60% case (URL text trong caption — trước đây actor cũ miss)
- ❌ Không bắt được photo product tag (card Shopee trên ảnh)
- ❌ Không bắt được reel Shop now card

**Verdict**: ✅ **Nâng cấp actor NGAY** — Phase 1.

### 1.3. `apify/facebook-reels-scraper`

**Test 1**: URL reel đơn lẻ `https://www.facebook.com/reel/896664166735293`.
- Kết quả: `error: no_items, Empty or private data for provided input`
- **Actor không xử lý reel URL đơn lẻ** — input phải là page URL

**Test 2**: Page URL `multitventertainment` với `resultsLimit: 3`.
- Trả về 3 reels với metadata: `text`, `shareable_url`, `playCountRounded`, `attachments`, `video_owner`, `tracking`
- `text` rỗng (reels thường không có caption)
- `attachments[0].media` chỉ có `{__typename, id, duration, owner}`
- **Không có** `product_tags`, `shop`, `affiliate_link`, `cta`, `external_url`

**Verdict**: ❌ **Không lấy được Shop now card**.

### 1.4. `apify/instagram-reel-scraper`

**Test**: Username `gearupvn`.

**Kết quả**:
```json
{
  "caption": "...",
  "hashtags": [...],
  "mentions": [...],
  "latestComments": [...],
  "musicInfo": {...},
  "videoUrl": "...",
  "videoPlayCount": N,
  "productType": "clips",  // LƯU Ý: "clips" = Reels format, KHÔNG PHẢI product tag
  ...
}
```

- `productType: "clips"` chỉ là **content type** (Reels vs Post vs IGTV)
- Không có field `shop`, `product_tag`, `affiliate`, `external_link`, `cta`

**Verdict**: ❌ **IG Reel product tag cũng không scrape được bằng actor này.**

### 1.5. Actor premium chưa test được đầy đủ

| Actor | Lý do không test xong |
|---|---|
| `premiumscraper/facebook-reels-and-page-profile-scraper` | Input schema trống, không biết cách gọi |
| `cleansyntax/facebook-profile-posts-scraper` | Run FAILED trên free tier |
| `powerai/facebook-page-posts-scraper` | Trả về post tiếng Ba Lan (scraping sai target với URL `hangtui6s`) |
| `easyapi/facebook-posts-search-scraper` | Chưa test, description không nhắc shop |

**Verdict**: ⚠️ Có thể POC thêm nếu Phase 1 (`pratikdani`) không đủ.

---

## 2. Meta Graph API chính thức

### 2.1. `GET /{video-id}?fields=product_tags`

- **Yêu cầu**: Page Access Token của chính page sở hữu video
- **Giới hạn**: Không dùng được cho video random của creator khác
- **Use case**: Chỉ phù hợp nếu creator tự đăng ký platform + cấp token

### 2.2. Instagram Product Tagging API (`media_product_tags`)

- Endpoint: `GET /{ig-media-id}/media_product_tags`
- Yêu cầu: Business/Creator account + IG Shopping active + access token owner
- **Không thể dùng cho random IG user**

### 2.3. Branded Content API

- Instagram Branded Content cho sponsored post
- **Vẫn cần creator authorize** cho app của mình

**Verdict tổng**: ❌ **Meta official API không dùng được cho feature này** — target user là random VN creator.

---

## 3. Mobile HTML / Headless Browser

### 3.1. Mobile HTML scraping

**Hypothesis**: `m.facebook.com/reel/{id}` hoặc `www.facebook.com/reel/{id}` với mobile User-Agent có thể expose product_tags trong HTML embedded JSON.

**Thực tế**:
- Meta render UI qua **GraphQL internal** (Relay framework), JSON blob encoded + obfuscated
- Anti-bot: Cloudflare + Meta's fingerprint/token detection
- DOM structure thay đổi thường xuyên (A/B tests)

**Verdict**: ❌ **Maintenance cost quá cao**. Không đầu tư.

### 3.2. Playwright / Puppeteer

**Workflow**:
1. Launch headless mobile Chrome/Safari
2. Mở URL reel với mobile UA
3. Chờ JS render card
4. Scrape DOM (`<a>` in product card) hoặc intercept network (XHR/GraphQL call)

**Feasibility**:
- Technical: 70% khả thi
- **Reliability**: 35% — Meta đổi class selector + anti-bot thường xuyên
- Speed: 15-30 giây/reel
- Cost: $300-500/tháng (browser farm) hoặc self-host infra

**Verdict**: ⚠️ **Chỉ làm cho Phase 3** — khi đã có traction + budget, và Phase 2 không đủ.

---

## 4. Third-party scraping services beyond Apify

### 4.1. Bright Data — Facebook Dataset

- Sản phẩm: Dataset snapshot của FB profile / posts
- **Ưu**: Họ lo anti-bot. Enterprise-grade reliability
- **Chi phí**: $50-100/tháng cho basic tier
- **Cần verify**: Có field `product_tags` không → **POC trước khi commit**

**Khuyến nghị**: ⚠️ Phase 2 POC.

### 4.2. Phyllo

- Platform aggregate influencer data
- Focus vào creator đã onboard qua OAuth
- Có thể có product tag cho business KOL
- **Chi phí**: $100-500/tháng
- **Coverage**: Chỉ KOL đã "claim" trong platform

### 4.3. Modash, HypeAuditor, Creatable, Keyhole

Tương tự Phyllo — influencer analytics, một số có product tag cho business tier.

### 4.4. Oxylabs, Smartproxy, Zyte

Proxy services level thấp hơn. Backend cho tự build scraper, team phải tự viết logic FB.

**Verdict chung**: ⚠️ POC từng cái khi cần Phase 2.

---

## 5. Giải pháp gián tiếp

### 5.1. Comments mining ✅ (đã làm)

**Pattern**: FB affiliate bot auto-post comment với Shopee link dưới reel:
> *"Xem sản phẩm tại: https://shopee.vn/product/..."*

- Crawler đã có field `comments` (top 5 comments/post)
- `extract-links` đã scan comments này
- **Coverage**: 30-50% reel VN có bot comment

**Verdict**: ✅ **Đã implemented** trong extract-links hiện tại.

### 5.2. OCR video frames

**Ý tưởng**: Download MP4 → FFmpeg extract frame → Tesseract/Gemini OCR đọc text.

**Vấn đề cốt lõi**:
- Card "Shop now" do **Facebook app render overlay client-side**
- **KHÔNG có trong video file MP4**
- OCR video chỉ đọc được:
  - Subtitle (nếu có)
  - Text creator đè lên video gốc

Để OCR card "Shop now" → phải screenshot màn hình app → không scale được (mỗi reel phải mở tay trên mobile).

**Verdict**: ❌ **Không khả thi về bản chất**. Lỗi nhầm lẫn phổ biến.

### 5.3. Audio transcript + NLP

**Ý tưởng**: Whisper/Gemini đọc audio → creator nói "link trong bio" / tên sản phẩm → search Shopee → suy ra URL.

**Coverage**: 30-40% (nhiều creator không nói rõ).
**Chi phí**: $0-30/tháng (Gemini có free tier).

**Verdict**: ⚠️ Phụ trợ, không chính. Phase 2 nếu có budget.

### 5.4. Hợp tác creator trực tiếp

**Workflow**: Creator đăng ký platform → cấp FB Page Access Token → dùng Graph API trực tiếp.

- **Ưu**: 100% chính xác, official API
- **Nhược**: Yêu cầu onboarding, không làm được với random creator

**Verdict**: ✅ **Long-term strategy** cho enterprise customer, không MVP.

---

## 6. Timeline testing

Đã thực hiện trong session 2026-04-21 (~3 tiếng):

- Test 5 Apify actor với 6+ URL profile/post/reel
- Verify Meta Graph API docs
- Research Bright Data / Phyllo / Modash
- Verify feasibility Playwright + OCR theo nguyên lý

---

## 7. Test commands reference

### Test `pratikdani` actor

```bash
curl -X POST "https://api.apify.com/v2/acts/pratikdani~facebook-post-scraper/run-sync-get-dataset-items?token=${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.facebook.com/watch/?v=1281155200078505"}'
# → content đầy đủ có "https://collshp.com/hangtuichoice"
```

### Test actor cũ để so sánh

```bash
curl -X POST "https://api.apify.com/v2/acts/apify~facebook-posts-scraper/run-sync-get-dataset-items?token=${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":[{"url":"https://www.facebook.com/multitventertainment"}]}'
# → text rỗng, không có URL shop
```

### Test IG Reel scraper

```bash
curl -X POST "https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items?token=${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"username":["gearupvn"],"resultsLimit":3}'
# → có caption, hashtags. Không có product tag.
```

---

## 8. Sources

- Meta Product Tagging API: https://developers.facebook.com/docs/instagram-platform/shopping/product-tagging/
- Apify Store FB scrapers: https://apify.com/store?search=facebook
- Bright Data FB Dataset: https://brightdata.com/products/datasets/facebook
- Phyllo Instagram Reels API: https://www.getphyllo.com/post/a-complete-guide-to-the-instagram-reels-api
- ScreenApp Video OCR: https://screenapp.io/features/video-ocr
- Elfsight Instagram Graph API Guide: https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2026/
- GitHub Facebook GraphQL Scraper: https://github.com/FaustRen/facebook-graphql-scraper

---

## 9. Câu hỏi mở cho implementation

1. Test thêm: Cho URL cụ thể của **post ảnh Quế** (Hằng Túi) để verify actor `pratikdani` có trả được card product tag không
2. Test: POC Bright Data free trial — thời gian ~1-2 ngày
3. Decision: Phase 2 dùng scraping service (Bright Data) hay partnership API (Phyllo)?
4. Kiến trúc: Product tag extraction chạy **sync trong extract-links** hay **async worker riêng**?
