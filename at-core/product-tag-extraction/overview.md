# Product Tag Extraction — Project Overview

> Dự án mở rộng khả năng extract link từ profile social — đặc biệt là các link "ẩn" trong product tag / shop card của Facebook, Instagram, TikTok.
>
> Cập nhật: 2026-04-21

---

## 1. Bối cảnh

Hệ thống `influence-meter` + `social-crawler-profile` hiện tại đã extract được link http(s) từ:

- Bio profile
- Caption bài đăng
- Top 5 comments dưới bài

Tuy nhiên khi demo với khách, phát hiện **một lớp link quan trọng bị miss**: các **product tag** / **shop card** mà Facebook (và Instagram, TikTok) render overlay trên bài đăng hoặc reel.

Đây là phần lớn nguồn **affiliate traffic** của creator VN — tức là mục tiêu chính của business.

---

## 2. Vấn đề

### 2.1. Feature khách muốn

Khách paste URL profile social → hệ thống trả về **tất cả link gắn trong profile**, bao gồm:

1. **Link text** trong caption (đã làm được)
2. **Card "Shop now"** trên Facebook Reels (chưa làm được)
3. **Card "Mở Shopee"** trên Facebook post ảnh (chưa làm được)
4. **Product tag** trên Instagram Reels / Shopping post (chưa làm được)

### 2.2. Bằng chứng gặp khi demo

**Case 1 — Reels Shop now card**

URL: `https://www.facebook.com/reel/896664166735293` (page `multitventertainment`)
- Mobile app render card overlay: *"Máy ảnh chụp 1 lần FujiFilm Simpl… Shop now"*
- Tap → mở Shopee checkout
- **Link đích không có trong caption text** → extract-links hiện tại trả về `0 link`

**Case 2 — Photo product tag**

Post: Hằng Túi (Fanpage `hangtui6s`) — ảnh sản phẩm "Quế xịn"
- Dưới ảnh có card: *"Nước rửa chén Power100 Tinh dầu quế 3.5KG · Mở Shopee"*
- **Link Shopee chỉ xuất hiện khi tap vào card** → không có trong caption

**Case 3 — URL trong caption**

Post: Hằng Túi `/watch/?v=1281155200078505`
- Caption có: *"Nào thì review chắc gì đã dùng… https://collshp.com/hangtuichoice?view=storefront"*
- **Actor `apify/facebook-posts-scraper`** (crawler đang dùng) trả `text: ""` — **miss luôn URL** mặc dù nằm trong caption!

---

## 3. Phát hiện chính

Sau khi test 5+ Apify actor và research các solution:

### 3.1. Vấn đề dễ fix (Phase 1)

**Actor `apify/facebook-posts-scraper` không đọc được caption đầy đủ**. Field `text` thường rỗng cho photo/video post.

**Actor `pratikdani/facebook-post-scraper`** đọc được full caption → fix ngay case URL trong text.

→ **Fix được ~60% coverage** chỉ bằng việc đổi actor.

### 3.2. Vấn đề khó hơn (Phase 2-3)

**Photo product tag + Reel Shop now card KHÔNG có trong JSON của bất kỳ Apify actor nào** đã test:
- `apify/facebook-reels-scraper`
- `apify/facebook-posts-scraper`
- `apify/instagram-reel-scraper`

Meta render UI mobile qua GraphQL internal (relay), dữ liệu product tag **chỉ render client-side** + có anti-bot protection.

Các giải pháp khả thi (cost cao hoặc phức tạp):
- **Bright Data FB Dataset** — cần POC, ~$50-100/tháng
- **Playwright headless mobile** — flaky, ~$300-500/tháng, maintenance cao
- **Meta Graph API chính thức** — **không dùng được** với creator khác

### 3.3. Giải pháp không khả thi

- **OCR video frame**: Card "Shop now" do FB app render overlay, KHÔNG có trong file MP4. OCR chỉ đọc được text trong video gốc.
- **Graph API `media_product_tags`**: Chỉ hoạt động với page của chính mình + IG Shop business account.

---

## 4. Roadmap 3 Phase

| Phase | Mục tiêu | Công việc | Coverage | Timing |
|---|---|---|---|---|
| **Phase 1** | Fix caption URL miss | Đổi actor crawler sang `pratikdani` | ~60% | Tuần này |
| **Phase 2** | Photo/Reel product tag | POC Bright Data / Phyllo | +15-25% → ~75-85% | 1-2 tuần |
| **Phase 3** | Last resort cho còn lại | Playwright headless mobile | +5-10% → ~90% | 1-2 tháng |

Chi tiết từng phương pháp đã test + sources → xem [research.md](./research.md).

---

## 5. Impact

### 5.1. Với business

- **Affiliate marketing intel**: Biết được creator gắn sản phẩm gì → phân tích thị phần, so sánh giá, campaign reach
- **Compliance check**: Biết creator link đến ai để kiểm tra khai báo tài trợ
- **Content strategy**: Biết loại sản phẩm nào viral → gợi ý cho brand

### 5.2. Với hệ thống

- **Không ảnh hưởng enrich flow cũ** — chỉ nâng cấp crawler actor + mở rộng pipeline
- **Response shape backward-compatible** — thêm field `resolved[]`, giữ nguyên `bio`, `posts`, `all`
- **Trọng số đầu tư**: Phase 1 chi phí thấp, Phase 2-3 cần budget + infra quyết định từ business

---

## 6. Câu hỏi mở cho stakeholder

1. **Team crawler** có thể đổi actor FB sang `pratikdani/facebook-post-scraper` trong tuần này không? (Hoặc chạy song song để fallback)
2. **Budget Phase 2**: OK $50-100/tháng cho Bright Data POC?
3. **Mức độ ưu tiên** Phase 3 (Playwright mobile) so với các feature khác của sprint?
4. **Partnership trực tiếp với creator**: Có thể offer creator access token đổi lại data chính xác 100%?

---

## 7. Tệp liên quan

- [research.md](./research.md) — chi tiết 7 solution đã test + so sánh
- [../../influence-meter](../../influence-meter) — repo implement extract-links hiện tại
- [../../social-crawler-profile](../../social-crawler-profile) — repo crawler (cần nâng cấp actor)
