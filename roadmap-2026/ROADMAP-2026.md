# ROADMAP 2026

**Dự án:** Pub2 Affiliate Integration
**Timeline:** Tháng 3 - Tháng 8, 2026
**Cập nhật:** 2026-02-28

---

## TIMELINE TỔNG HỢP 3 DỰ ÁN

> **Ghi chú:** Timeline hiện tại được fill tạm giống nhau. Cần rà soát và cập nhật deadline riêng cho từng dự án.

| # | Tính năng | Priority | T-Fluencers | VCreator | Ambassador |
|---|-----------|:--------:|-------------|----------|------------|
| 1 | Mở rộng MXH (Threads & Facebook Posts) | P1 | 01/03 → 15/03 | 01/03 → 15/03 | ✅ Done (15/02) |
| 2 | Kiểm tra điều kiện tham gia (Pre-Submission Checklist) | P0 | 15/03 → 31/03 | 15/03 → 31/03 | ✅ Done (15/02) |
| 3 | Thưởng hiệu suất (Bonus Reward) | P1 | 15/03 → 31/03 | 15/03 → 31/03 | ✅ Done |
| 4 | Thư viện Influencer - Xây dựng Database | P0 | 16/03 → 15/04 | 16/03 → 15/04 | 16/03 → 15/04 |
| 5 | Brand Dashboard - Hiện đại hóa | P1 | ✅ Done (28/02) | 15/03 → 31/03 | 15/03 → 31/03 |
| 6 | Kết nối Affiliate Programs với Campaigns | P0 | 01/04 → 30/04 | 01/04 → 30/04 | 01/04 → 30/04 |
| 7 | Trợ lý AI thiết lập chiến dịch | P1 | 01/04 → 15/04 | 01/04 → 15/04 | 01/04 → 15/04 |
| 8 | Thư viện Influencer - Tìm kiếm & Khám phá | P0 | 16/04 → 30/04 | 16/04 → 30/04 | 16/04 → 30/04 |
| 9 | Phát hiện gian lận - Nâng cấp ML | P0 | 16/04 → 15/05 | 16/04 → 15/05 | 16/04 → 15/05 |
| 10 | Thư viện Influencer - Chấm điểm & Matching | P1 | 01/05 → 15/05 | 01/05 → 15/05 | 01/05 → 15/05 |
| 11 | Quản lý vận hành - Task & Chấm điểm hiệu suất | P1 | 01/05 → 30/05 | 01/05 → 30/05 | 01/05 → 30/05 |
| 12 | Thư viện Influencer - Đặt chỗ & Booking | P1 | 15/05 → 30/05 | 15/05 → 30/05 | 15/05 → 30/05 |
| 13 | Tự động hóa vòng đời chiến dịch | P1 | 15/05 → 30/05 | 15/05 → 30/05 | 15/05 → 30/05 |
| 14 | Cổng Influencer - Hiện đại hóa UX/UI | P1 | 15/05 → 30/05 | 15/05 → 30/05 | 15/05 → 30/05 |

---

## CAMPAIGN ENHANCEMENTS

### Social Media Schema Extension - Threads & Facebook Posts Support
**Timeline:** 1/3 → 15/3 | **Priority:** P1

**Lợi ích:**

**Cho Influencer:**
- ⚡ **Tăng cơ hội kiếm tiền 3x:** Post được trên 3 platforms (Threads + Facebook + Instagram) thay vì chỉ 1 → Reach rộng hơn
- 🎯 **Chọn platform phù hợp audience:** Gen Z thích Threads, 35+ thích Facebook → Tối ưu conversion theo từng nhóm
- 📊 **Biết platform nào convert tốt:** Dashboard hiển thị tỷ lệ CTR của Threads và Facebook → Focus vào channel hiệu quả

**Cho Brand:**
- 💰 **Tăng reach 40%:** Threads có 2M+ users VN, Facebook 70M+ → Tổng reach lớn hơn nhiều
- 🎯 **Tracking chính xác theo platform:** Biết được campaign perform tốt trên platform nào để adjust strategy

**Cách hoạt động:**

**1. Bổ sung platforms mới:**
- Thêm **Threads** vào danh sách nền tảng hỗ trợ (hiện tại: Instagram Stories, TikTok)
- Thêm **Facebook Posts** vào danh sách nền tảng hỗ trợ
- Influencer có thể chọn 1 trong 5 platforms: Instagram Stories, TikTok, Threads, Facebook Posts, YouTube

**2. Schema thưởng theo Facebook Page Followers (mới):**
- **Thay vì:** Tính thưởng theo số views (áp dụng cho Instagram, TikTok, YouTube)
- **Facebook Posts:** Tính thưởng theo số followers của Facebook Page
- Công thức thưởng:
  - Page có 1,000-5,000 followers: 100k VND/post
  - Page có 5,000-10,000 followers: 200k VND/post
  - Page có 10,000-50,000 followers: 500k VND/post
  - Page có >50,000 followers: 1,000k VND/post

**Example:**
Influencer A tham gia campaign Brand A:

**Option 1 - Facebook Posts (reward theo followers):**
- Page có 25,000 followers → Reward tier: 500k VND/post
- Post về campaign → Không cần đếm views
- Nhận ngay 500k khi post được approve

**Option 2 - Threads (reward theo views):**
- Post thread → 30k views → Reward: 30k VND

→ Influencer chọn platform phù hợp: Facebook nếu có page lớn, Threads nếu engagement cao

---

### Pre-Submission Checklist System - Campaign Participation Requirements
**Timeline:** 15/3 → 31/3 | **Priority:** P0

**Lợi ích:**

**Cho Influencer:**
- ⚡ **Tiết kiệm thời gian 80%:** Biết ngay thiếu gì, không phải submit rồi bị reject rồi hỏi lại
- 🎯 **Tự đánh giá trước:** Thấy số lượng followers hiện tại so với yêu cầu → Biết cần làm gì để đủ điều kiện
- 💎 **UX tốt hơn:** Không bị "bối rối" vì không biết tại sao không tham gia được

**Cho Admin:**
- 🤖 **Giảm workload 30%:** Ít hồ sơ rác hơn (users tự check trước) → Chỉ review hồ sơ qualified
- 📊 **Giảm support tickets 50%:** Users không hỏi "Tại sao tôi bị reject?" vì đã biết lý do từ đầu

**Cho Brand:**
- 💰 **Quality tăng:** Chỉ có influencers đủ điều kiện mới submit → Ít phải review hồ sơ kém chất lượng

**Cách hoạt động:**

**User Flow:**
1. User click "Tham gia campaign" → System check requirements real-time
2. Hiển thị checklist:
   - ✅ Tài khoản ≥ 3 tháng tuổi (OK: 6 tháng)
   - ✅ Email đã xác thực (OK)
   - ❌ Follower: 800/1000 (thiếu 200)
   - ❌ Chưa link Pub2 account
3. Button "Tham gia" bị disable nếu còn yêu cầu chưa đạt
4. Hiển thị message: "Hoàn thiện 2 yêu cầu còn lại để tham gia"
5. User fix issues → Re-check → Button enable khi pass all

**Example:**
Trước: 100 submissions → 30 rejected → 30 support tickets
Sau: 70 submissions (qualified) → 10 rejected → 5 support tickets

→ Admin tiết kiệm 3h mỗi campaign cho review và support

---

### Bonus Reward System - Performance Incentives
**Timeline:** 15/3 → 31/3 | **Priority:** P1

**Lợi ích:**

**Cho Influencer:**
- 💰 **Tăng thu nhập 10-30%:** Top 3 nhận thêm 30% (VD: 500k → 650k)
- 🎯 **Động lực cạnh tranh:** Leaderboard public → Thấy mình đang top mấy → Cố gắng lên top hơn
- 📊 **Minh bạch tiêu chí:** Biết rõ ranking dựa vào conversions (50%), CTR (30%), quality (20%)

**Cho Brand:**
- 💰 **ROI cao hơn:** Chỉ thưởng khi có results (conversions) → Không tốn tiền cho performance kém
- 🎯 **Top performers gắn bó:** Retention tăng 15% vì influencers muốn giữ streak thắng
- 📊 **Push quality lên:** Influencers tập trung tạo content tốt hơn để lên top

**Cho Admin:**
- 🤖 **Tự động hóa:** System tự tính ranking và bonus → Không cần manual calculation
- 📊 **Clear metrics:** Dashboard hiển thị top performers → Dễ track

**Cách hoạt động:**

**Ranking Logic:**
1. System collect data per campaign:
   - Số conversions (weighted 50%)
   - CTR - Click-through rate (weighted 30%)
   - Content quality score từ admin rating (weighted 20%)

2. Tính composite score dựa trên công thức kết hợp conversions, CTR và quality rating

3. Sort influencers theo score → Rank từ 1 đến N

4. Apply bonus tiers:
   - Top 1-3: +30% reward
   - Top 4-10: +20% reward
   - Top 11-20: +10% reward

5. Payout = base_reward × (1 + bonus_percentage)

**Example:**
Campaign: Brand A Credit Card Review
100 influencers tham gia

Top 1: Influencer A
- 15 conversions (7.5 điểm)
- 12% CTR (3.6 điểm)
- Quality 4.5/5 (1.8 điểm)
- Total: 12.9 điểm → Rank #1 → +30% bonus

→ Base reward: 500k → Final: 650k

---

## INFLUENCER LIBRARY - THƯ VIỆN INFLUENCER

### Influencer Library - Build & Own Your Creator Database
**Timeline:** 16/3 → 15/4 | **Priority:** P0

**Lợi ích:**

**Cho Brand:**
- 💰 **Sở hữu database riêng:** Build thư viện influencers đã làm việc → Tái sử dụng cho campaigns sau, không phải tìm lại từ đầu
- 🎯 **Giảm risk 60%:** Chọn từ pool đã verify (lịch sử campaigns, ratings thực tế) → Tránh "bom xịt"
- ⚡ **Tiết kiệm 80% thời gian casting:** 10h research → 2h (chỉ cần browse library + filter) → Launch campaign nhanh hơn
- 📊 **Data-driven decisions:** Xem track record thực tế (engagement rate, conversion rate, completion rate) thay vì tin lời quảng cáo
- 💎 **Blacklist & Whitelist:** Đánh dấu "Favorite influencers" (perform tốt) hoặc "Never work again" (chất lượng kém)
- 🔄 **Relationship management:** Theo dõi lịch sử hợp tác với từng influencer → Build long-term partnerships

**Cho Influencer:**
- 💎 **Tăng visibility:** Profile xuất hiện trong library của nhiều brands → Nhiều cơ hội được book hơn
- 📊 **Track record minh bạch:** Brands thấy "15 campaigns completed, 4.8/5 rating" → Tăng credibility
- 🎯 **Được ưu tiên cho campaigns tiếp theo:** Brand đã hợp tác tốt sẽ invite lại → Stable income

**Cho Admin:**
- 🤖 **Tự động aggregate data:** System tự thu thập từ 4 sources (onboarding, social crawl, campaign performance, brand feedback) → Không cần manual
- 📊 **360° influencer view:** Tất cả info ở 1 chỗ (social stats + performance + ratings + history)
- 💰 **Monetization opportunity:** Bán "Premium Library Access" cho brands (advanced filters, export data, API access)

**Cách hoạt động:**

**1. Build Library - Aggregate Data từ 4 Sources:**

**Source 1 - Influencer Onboarding (Initial Data):**
- Influencer đăng ký → Điền form: Name, niche, location, social links, bio
- System tạo profile base → Status: "Pending verification"

**Source 2 - Social Media Auto-Crawl (Realtime Stats):**
- Crawler chạy daily (00:00 AM) crawl social APIs:
  - Facebook Graph API → Followers count, page engagement, recent posts performance
  - Instagram API → Followers, avg likes/comments per post
  - TikTok API → Followers, views, engagement rate
- Update profile với fresh data → Timestamp: "Last updated 12 hours ago"

**Source 3 - Campaign Performance History (Track Record):**
- Sau mỗi campaign completed → System tự động aggregate:
  - Completion rate: 15/20 campaigns = 75%
  - Avg views per campaign: 50,000 views
  - Avg CTR: 3.5% | Avg CVR: 1.2%
  - On-time delivery rate: 90%
- Lưu vào performance history → Brands xem được track record thực tế

**Source 4 - Brand Ratings & Reviews (Reputation Score):**
- Brand rate influencer sau campaign:
  - Rating: 1-5 stars
  - Categories: Content Quality, Communication, Professionalism, Results
  - Comments: Text feedback
- System calculate overall score: 4.8/5 (based on 12 reviews)
- Display công khai trong profile → Build credibility

**2. Brand Ownership - Library Management:**

**Whitelist (Favorite Influencers):**
- Brand click "Add to Favorites" → Save to private list
- Use case: "Influencers đã hợp tác tốt, muốn invite lại"
- Feature: Bulk invite favorites to new campaign (1 click)

**Blacklist (Never Work Again):**
- Brand click "Block Influencer" → Không xuất hiện trong search nữa
- Use case: "Influencer chất lượng kém, không muốn thấy lại"
- System log reason: Late delivery, low quality, fraud detected

**Campaign History Tracking:**
- Brand xem: "Đã hợp tác với Influencer A trong 3 campaigns"
- Details per campaign:
  - Campaign name, date, deliverables
  - Performance metrics (views, CTR, conversions)
  - Rating given
- Decision: "Perform tốt → Invite lại | Perform kém → Block"

**3. Monetization - Premium Library Access:**

**Free Tier (Basic Access):**
- View top 50 profiles
- Basic filters (niche, location, followers)
- Limited to 5 profile views/day

**Premium Tier (500k VND/month):**
- Full library access (1000+ profiles)
- Advanced filters (engagement rate, price range, availability, past performance)
- Unlimited profile views
- Export to CSV
- API access để integrate vào internal CRM

**Enterprise Tier (Custom pricing):**
- Dedicated account manager
- Custom crawler để add thêm influencers
- White-label library
- Priority support

**Example:**

**Brand A (Finance Brand) sử dụng Library:**

**Lần đầu - Campaign #1 "Credit Card Review":**
- Browse library → Tìm 20 influencers Finance niche
- Check track record: "Influencer A: 95% completion, 4.8/5 rating"
- Invite 20 → 15 accepted → Campaign runs
- After campaign: Rate influencers
  - A, B, C (excellent) → Add to Favorites
  - D, E (poor quality) → Blacklist

**Lần 2 - Campaign #2 "Savings Account Promo" (3 tháng sau):**
- Click "Invite Favorites" → Bulk invite A, B, C (đã verify tốt)
- Tiết kiệm 8h research time
- Higher success rate vì đã biết quality

**Lần 3 - Scale Up:**
- Brand A thấy ROI tốt → Upgrade to Premium tier
- Access full library 1000+ profiles
- Filter advanced: "Finance niche, >50k followers, engagement >5%, CVR >1%"
- Export 100 profiles → Share với marketing team
- Build internal CRM integration via API

→ **Brand A giờ sở hữu database 100+ verified influencers, tái sử dụng liên tục, không phải tìm lại từ đầu**

---

### Influencer Library - Discovery & Exploration
**Timeline:** 16/4 → 30/4 | **Priority:** P0

**Lợi ích:**

**Cho Brand:**
- ⚡ **Tìm đúng người trong 30s:** Search "Beauty, Hà Nội, 10k-50k followers" → 15 matches thay vì scroll 1000 profiles
- 🎯 **Advanced filters:** Lọc theo engagement >5%, past performance, price range → Chỉ xem qualified candidates
- 💰 **Save time 80%:** 10h research → 2h (faster time-to-launch campaign)

**Cho Influencer:**
- 💎 **Được discover dễ hơn:** Profile match đúng niche → Xuất hiện trong search của brands
- 📊 **Smart suggestions:** AI suggest "Influencers tương tự" → Brands discover thêm options

**Cách hoạt động:**

**Search & Filter Flow:**

1. **Brand vào Influencer Library page:**
   - Search bar: Nhập keyword (VD: "Beauty blogger Hà Nội")
   - Filter sidebar:
     

2. **System execute search query:**
   

3. **Results display:**
   - Grid/List view với influencer cards
   - Each card show:
     - Avatar, Name, Niche
     - Followers, Engagement, Quality Score
     - "View Profile" + "Book Now" buttons

4. **Sort options:**
   - Relevance (default - based on quality score)
   - Price (low → high)
   - Followers (high → low)
   - Recent campaigns (active → not active)

**Smart Suggestions (AI-powered):**
- User click vào influencer A
- AI suggest: "Influencers tương tự" dựa trên:
  - Same niche
  - Similar số lượng followers (±20%)
  - Similar quality score (±10 points)


**Example:**

Brand A (Mỹ phẩm) tìm influencer trong Library:
- **Search:** "Beauty blogger Hà Nội"
- **Filter:** 10k-50k followers, engagement >5%, price <1M VND/post
- **Results:** 15 influencers match
- **Sort by:** Quality Score (cao → thấp)
- **Click vào Influencer B → AI suggest:** "Influencers tương tự"
  - Influencer C (Beauty, 35k followers, score 85)
  - Influencer D (Beauty, 28k followers, score 82)
- **Brand A xem 3 profiles → Book Influencer B + C**

→ Tìm được 2 influencers phù hợp trong 2 phút (thay vì 2 giờ scroll manual)

---

### Influencer Library - Scoring & Matching Engine
**Timeline:** 1/5 → 15/5 | **Priority:** P1

**Lợi ích:**

**Cho Brand:**
- 🎯 **Match tự động 90% accurate:** AI suggest top 10 influencers phù hợp nhất → Không cần manual review 100 profiles
- 💰 **Predict success rate:** "85% chance campaign thành công với influencer A" → Giảm risk
- 📊 **Giảm bias:** Quyết định dựa data, không "thiên vị cá nhân" hoặc "influencer quen"

**Cho Influencer:**
- 💎 **Score minh bạch:** Thấy "Quality Score: 87/100" → Biết mình đứng đâu, cần improve gì
- 🎯 **Được suggest cho đúng campaigns:** AI match đúng niche → Tăng tỷ lệ được chọn

**Cách hoạt động:**

**Scoring System:**

1. **Calculate Quality Score (0-100):**
   

2. **Score Tiers:**
   

**Matching Algorithm:**

1. **Brand tạo campaign với requirements:**
   

2. **System tìm influencers match criteria:**
   

3. **Rank matches theo relevance score:**
   

4. **AI suggest top 10:**
   - Sort by relevance_score DESC
   - Return top 10 với predicted success rate


**Example:**

Campaign Brand A (Thẻ tín dụng) cần 50 influencers Finance niche:
- **System calculate scores:**
  - Influencer A: (85 × 0.3) + (8% × 5 × 0.25) + (4.8 × 10 × 0.25) + (95% × 20 × 0.2) = 25.5 + 10 + 12 + 19 = **66.5/100**
  - Influencer B: (70 × 0.3) + (5% × 5 × 0.25) + (4.2 × 10 × 0.25) + (80% × 20 × 0.2) = 21 + 6.25 + 10.5 + 16 = **53.75/100**
- **Match với requirements:**
  - Niche Finance: Influencer A (match 100%), B (match 80%)
  - Followers >10k: A ✅, B ✅
  - Location Hà Nội: A ✅, B ❌
- **Relevance score:** A = 95%, B = 80%
- **AI suggest top 10:** A, C, D, E, F... (sorted by relevance)
- **Predicted success:** A = 85% chance campaign thành công

→ Brand chọn top 10, invite → 8/10 accept → Campaign chạy tốt

---

### Influencer Library - Booking & Reservation System
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**

**Cho Brand:**
- 🎯 **Commitment rõ ràng:** Book → Influencer confirm → Deal chắc chắn (không lo influencer "biến mất")
- 💰 **Deposit 30% lock deal:** Influencer nhận tiền trước → Có động lực hoàn thành tốt
- 📊 **Avoid conflicts:** Hệ thống check availability → Không book influencer đang busy

**Cho Influencer:**
- ⚡ **Tránh overload:** Không bị book 5 campaigns cùng lúc → Có thời gian tạo content quality
- 💰 **Nhận deposit trước:** 30% upfront → Cash flow tốt hơn
- 📊 **Calendar integration:** Thấy schedule (campaign A: 1-7/5, campaign B: 8-15/5) → Dễ quản lý

**Cho Admin:**
- 🤖 **Tự động check conflicts:** System auto-block calendar khi confirmed
- 📊 **Track bookings:** Dashboard hiển thị "50 bookings pending, 30 confirmed"

**Cách hoạt động:**

**Booking Flow:**

1. **Brand browse Influencer Library → Select influencer:**
   - Click "Book Now" button
   - Popup hiển thị influencer calendar (available/busy dates)

2. **Brand fill booking form:**
   

3. **Submit booking request:**
   - System check influencer availability (not double-booked)
   - If available: Create booking record (status: pending)
   - Charge brand deposit 30% (150k)
   - Send notification to influencer

4. **Influencer review booking:**
   - Notification: "Brand X wants to book you (1-7/5)"
   - View booking details
   - Actions:
     - **Accept:** Status → confirmed, calendar blocked, receive deposit 150k
     - **Decline:** Status → rejected, deposit refund to brand
     - **Counter-offer:** Suggest different dates (8-15/5)

5. **If Accepted:**
   - Status: confirmed
   - Calendar blocked (other brands see "Busy 1-7/5")
   - Influencer receives deposit 150k
   - Both parties receive confirmation email

6. **Campaign execution:**
   - Influencer creates content during 1-7/5
   - Submits final deliverable
   - Brand reviews & approves
   - System release remaining 70% (350k)


**Example:**

Brand A muốn book Influencer B cho campaign "Thẻ tín dụng review":
- **Ngày 1/5:** Brand click "Book Now" → Chọn dates: 1-7/5
- **Check calendar:** Influencer B available ✅
- **Fee:** 500k VND/video, deposit 30% = 150k
- **Submit booking** → Status: Pending
- **Influencer B nhận notification:** Review booking
- **Ngày 2/5:** Influencer B accept → Status: Confirmed
  - Calendar blocked 1-7/5 (brands khác thấy "Busy")
  - Nhận deposit 150k vào wallet
- **1-7/5:** Influencer B tạo video review
- **Ngày 7/5:** Submit video → Brand approve
- **Ngày 8/5:** Nhận 70% remaining = 350k
- **Total earned:** 500k

→ Deal commitment rõ ràng, cả 2 bên yên tâm

---

## AFFILIATE CENTER - UNIFIED CAMPAIGN & DUAL EARNING

### Connect Affiliate Programs to Campaigns - Maximize Revenue per Content
**Timeline:** 1/4 → 30/4 | **Priority:** P0

**Lợi ích:**

**Cho Influencer:**
- 💰 **Tăng thu nhập 2-10x:** 1 video earn view reward (50k) + affiliate commission (up to 2,500k) = 2,550k total
- ⚡ **1 content, 2 income streams:** Không phải tạo 2 videos riêng cho views và affiliate
- 📊 **Dashboard thống nhất:** Xem tất cả earnings (views + affiliate) ở 1 chỗ

**Cho Brand:**
- 🎯 **Tăng conversion:** Influencers motivated tạo content quality cao hơn (vì có affiliate commission)
- 💰 **Win-win:** Brand gets sales, Influencer gets commission → Đôi bên cùng lợi
- 📊 **ROI rõ ràng:** Track được views + clicks + conversions trong 1 dashboard

**Cách hoạt động:**

**⚠️ QUAN TRỌNG:**
Tất cả hoạt động affiliate (tạo link, tracking clicks/conversions, tính thưởng) đều được quản lý bởi **hệ thống Pub2 AccessTrade có sẵn** (pub2.accesstrade.vn). Platform này chỉ tích hợp với Pub2 qua API, KHÔNG tự xây dựng hệ thống affiliate riêng.

**Integration Flow:**

**1. Admin setup campaign với affiliate link (Sử dụng Pub2 Program):**
   - Vào Pub2 AccessTrade → Chọn affiliate program có sẵn (VD: "Brand A Credit Card")
   - Copy Program ID từ Pub2
   - Tạo campaign trong platform: "Review Brand A Credit Card"
   - Link đến Pub2 Program ID
   - Set view reward: 50k VND per video (local reward)
   - Commission: Theo Pub2 program (500k/conversion - do Pub2 quản lý)
   - Publish campaign

**2. Influencer join campaign:**
   - Xem dual earning potential:
     - View reward: 50k VND (platform trả)
     - Affiliate commission: 500k/conversion (Pub2 trả)
   - Click "Generate Link" button

**3. System generate tracking link (Pub2 API):**
   - Platform call Pub2 API: `POST /api/publishers/{publisher_id}/links`
   - Pub2 tạo affiliate link tự động
   - Pub2 append sub_id tracking: `?sub_id=influencerA_campaign123`
   - Platform nhận link từ Pub2 → Lưu mapping (influencer ↔ Pub2 link)
   - Return link cho influencer

**4. Influencer create & post content:**
   - Tạo video review
   - Include affiliate link (từ Pub2) vào description
   - Post lên platform (YouTube/TikTok/Facebook)

**5. Tracking clicks & conversions (Pub2 Webhook):**
   - User clicks link → **Pub2 tracking system** ghi nhận click
   - User applies for card → Approved → **Pub2 tracking system** ghi nhận conversion
   - **Pub2 gửi webhook** về platform của chúng ta:
     - Click event: `POST /webhook/pub2/click`
     - Conversion event: `POST /webhook/pub2/conversion`
   - Platform update dashboard với data từ Pub2

**6. Commission calculation & payout (Pub2 quản lý):**
   - **Pub2** tự động tính commission theo program rules
   - **Pub2** chịu trách nhiệm payout commission cho publisher
   - Platform chỉ hiển thị tổng hợp từ Pub2 API

**7. Dashboard display dual earnings (Tổng hợp):**
   - **View reward:** Platform tự tính & trả (50k)
   - **Affiliate commission:** Lấy data từ Pub2 API (500k × conversions)
   - Dashboard tổng hợp: Total = Platform reward + Pub2 commission
   


**Example:**

Influencer A tạo 1 video review Brand A Credit Card, kiếm được cả 2 income streams:

**Stream 1 - View Reward:**
- Video: 100k views → Reward: 50k VND

**Stream 2 - Affiliate Commission:**
- Generate link: `pub2.vn/brandA?sub_id=influencerA_campaign123`
- Include trong video description
- User clicks → 500 clicks
- User applies for card → 5 approved conversions
- Commission: 5 × 500k = 2,500k VND

**Total earning:**
- View reward: 50k
- Affiliate: 2,500k
- **Total: 2,550k VND** (từ 1 video duy nhất!)

→ Influencer motivated tạo content chất lượng cao hơn vì có affiliate upside

---

## SYSTEM IMPROVE

### Fraud Detection - Enhancement & Optimization
**Timeline:** 16/4 → 15/5 | **Priority:** P0

**Lợi ích:**

**Cho Brand:**
- 💰 **Tiết kiệm 200M+ VND/năm:** Phát hiện 80%+ fake views → Không trả tiền cho fraud
- 🎯 **Bảo vệ ROI:** Chỉ trả tiền cho views thật → Marketing budget hiệu quả hơn
- 📊 **Risk mitigation:** ML model detect fraud patterns (bot views, fake engagement) → Block sớm

**Cho Influencer (Trung thực):**
- 💎 **Fair competition:** Cheaters bị catch → Honest influencers có cơ hội win hơn
- 📊 **Không bị ảnh hưởng:** False positive <5% → Users trung thực không bị block nhầm

**Cho Admin:**
- 🤖 **Automation:** ML model tự detect → Không cần manual review từng submission
- ⚡ **Real-time blocking:** Phát hiện fraud trong 24h → Block trước khi payout

**Cách hoạt động:**

**⚠️ LƯU Ý:**
Hệ thống fraud detection cơ bản **ĐÃ TỒN TẠI** và hoạt động. Feature này là **NÂNG CẤP** để phát hiện fraud tốt hơn bằng ML/AI.

**Phase 1: Basic Fraud Detection (ĐÃ CÓ SẴN - Currently Running):**

1. **View Count Validation:**
   - Cross-check views với platform APIs (TikTok, Instagram, YouTube)
   - If reported views ≠ API data → Flag for review

2. **Engagement Rate Check:**
   - Calculate: Engagement Rate = (Likes + Comments) / Views
   - If ER <1% (abnormally low) → Suspicious (bot views)
   - If ER >20% (abnormally high) → Suspicious (fake engagement)
   - Flag for manual review

3. **Growth Pattern Analysis:**
   - Track views over time: 0 → 10k → 50k (natural curve)
   - If spike: 0 → 100k trong 1 giờ → Bot views
   - Flag for review

4. **Duplicate Content Detection:**
   - Check video hash/fingerprint
   - If same video submitted multiple times → Fraud
   - Auto-reject

**Phase 2: Enhanced ML-Powered Detection (FEATURE MỚI):**

1. **Bot View Detection:**
   - ML model phân tích view patterns:
     - **Timing:** Views đều đặn (VD: 100 views/phút liên tục 10 phút) → Bot
     - **Geographic:** 100% views từ 1 quốc gia lạ (VD: Pakistan) → Suspicious
     - **Retention:** Avg watch time <5s (skip ngay) → Fake views
   - Train model trên labeled data (bot vs organic views)
   - Predict fraud score (0-1)

2. **Fake Engagement Detection:**
   - Phân tích comments:
     - Generic comments ("Nice!", "😍", "👍") → Bot comments
     - Comments không liên quan đến content → Fake
   - Phân tích likes pattern:
     - Likes tăng đột biến không match với views → Bought likes
   - ML model detect fake engagement

3. **Follower Quality Check:**
   - Re-validate followers at payment time (xem feature #13)
   - Analyze follower quality:
     - % followers là bot accounts (no profile pic, 0 posts)
     - If >30% bot followers → Influencer quality kém
   - Adjust fraud score

4. **Cross-Platform Consistency:**
   - Check influencer performance across platforms:
     - TikTok: 100k views, Instagram: 500 views (huge gap) → Suspicious
     - Consistent low performance → Likely bought views on 1 platform
   - Flag inconsistencies

**Fraud Response Actions:**

- **Score 0-0.3:** Legitimate → Auto-approve payment
- **Score 0.3-0.7:** Suspicious → Manual review queue (admin kiểm tra)
- **Score 0.7-1.0:** High fraud → Auto-reject payment + notify influencer


**Example:**

**Influencer A (Fraud Attempt):**
- **Video:** TikTok video về Brand A Credit Card
- **Reported views:** 100,000 views
- **ML Analysis:**
  - Views tăng đột biến: 0 → 100k trong 2 giờ (abnormal spike)
  - Geographic: 95% views từ Indonesia (không match target VN)
  - Avg watch time: 3s (video dài 60s, retention <5%)
  - Engagement: 50 likes, 2 comments (ER = 0.05% - quá thấp)
- **Fraud score:** 0.85 (high risk)
- **System action:** Auto-reject payment, notify admin
- **Admin review:** Confirm fraud (bought views từ bot farm)
- **Result:** Influencer A không nhận payment, bị cảnh cáo

**Influencer B (Legitimate):**
- **Video:** YouTube video review Brand A Credit Card
- **Reported views:** 50,000 views
- **ML Analysis:**
  - Views tăng tự nhiên: 0 → 5k (day 1) → 20k (day 3) → 50k (day 7)
  - Geographic: 90% views từ Vietnam (match target)
  - Avg watch time: 4m30s (video 7 phút, retention 64% - tốt)
  - Engagement: 2,500 likes, 180 comments (ER = 5.4% - healthy)
  - Comments quality: Relevant questions về credit card benefits
- **Fraud score:** 0.05 (low risk)
- **System action:** Auto-approve payment
- **Result:** Influencer B nhận payment 500k

**ML Model Training:**
- **Dataset:** 10,000+ submissions (8,000 legitimate, 2,000 fraud)
- **Features:** View growth rate, geographic distribution, engagement rate, watch time, comment quality
- **Algorithm:** Random Forest + Neural Network ensemble
- **Accuracy:** 95% (5% false positive rate)

→ Brand tiết kiệm 200M VND/năm bằng cách chặn fake views trước khi payout

---

### Setup Editor - AI Agent Assistant
**Timeline:** 1/4 → 15/4 | **Priority:** P1

**Lợi ích:**

**Cho Brand/Admin:**
- ⚡ **Tạo campaign nhanh 5x:** 2 hours → 20 minutes (AI fill sẵn 80% content)
- 🎯 **Consistency:** AI đảm bảo không miss required fields (budget, timeline, T&C)
- 💰 **Learning từ best practices:** AI học từ top-performing campaigns → Suggest winning formula
- 📊 **Smart budget suggestion:** AI calculate "100 influencers × 500k = 50M VND" tự động

**Cách hoạt động:**

**AI-Assisted Campaign Creation Flow:**

1. **Brand nhập brief ngắn gọn:**
   

2. **AI analyze và suggest:**
   - Parse keywords: "thẻ tín dụng" → Finance niche
   - Search similar past campaigns (Finance category)
   - Extract patterns từ top performers

3. **AI generate campaign draft:**
   

4. **Brand review AI suggestions:**
   - Edit nếu cần (adjust budget, timeline, requirements)
   - Click "Approve & Publish"

5. **System create campaign:**
   - Save to database
   - Notify influencers matching criteria
   - Campaign goes live

**AI Training & Learning:**
- **Training data:** 200+ past campaigns
- **Features:**
  - Niche, budget, duration, requirements
  - Performance metrics (CTR, CVR, completion rate)
- **Model:** GPT-4 fine-tuned on campaign data
- **Continuous learning:** Re-train quarterly with new campaigns


**Example:**

Brand A muốn tạo campaign "Review thẻ tín dụng":

**Before AI (Manual - 2 hours):**
- Fill 20 fields: Campaign name, description, niche, requirements, budget...
- Research influencers: Scroll 100 profiles → Pick 50
- Calculate budget manually: 50 × 500k = 25M VND
- Write T&C, timeline, deliverables...

**After AI (20 minutes):**
- **Input brief:** "Campaign review thẻ tín dụng Brand A, target Gen Z, budget 30M"
- **AI generates in 10s:**
  - Title: "Review Thẻ Tín Dụng Brand A - Đặc Quyền Gen Z"
  - Description: "Influencer sẽ tạo video review thẻ tín dụng Brand A..."
  - Niche: Finance
  - Requirements: 10k+ followers, Finance content, 18-35 tuổi
  - Budget: 30M VND (60 influencers × 500k)
  - Timeline: 15 ngày
  - T&C: Auto-generated từ template
- **Brand review:** Edit nếu cần → Approve
- **Campaign published:** Ready to receive applications

→ Tiết kiệm 100 phút, AI fill 80% content

---

### Operations Manager - Task Management & Performance Scoring
**Timeline:** 1/5 → 30/5 | **Priority:** P1

**Lợi ích:**

**Cho Admin:**
- ⚡ **Quản lý task hiệu quả:** Dashboard hiển thị "12 pending tasks" → Prioritize theo SLA
- 📊 **SLA tracking:** System cảnh báo "Task #1234 còn 1h trước deadline" → Không miss deadline
- 💰 **Performance-based bonus:** Admin score 95 → Top performer → +20% bonus
- 🤖 **Workload balancing:** System tự assign tasks đều cho team (mỗi admin ~10 tasks)

**Cho Management:**
- 📊 **Track team productivity:** Dashboard hiển thị "Admin A: 95 score, Admin B: 65 score"
- 🎯 **Identify training needs:** Admin B score thấp → Cần training
- 💰 **Data-driven bonuses:** Top performers nhận reward xứng đáng

**Cách hoạt động:**

**Task Management:**

1. **Task Creation (Auto + Manual):**
   - **Auto tasks:**
     - Influencer submits content → Task: "Review submission #1234"
     - Influencer requests payout → Task: "Approve payout #5678"
   - **Manual tasks:**
     - Manager assigns: "Generate monthly report"

2. **Task Assignment:**
   - **Auto-assign (Round-robin):**
     - System distributes evenly
     - Admin A: 10 tasks, Admin B: 10 tasks
   - **Manual-assign:**
     - Manager picks specific admin

3. **Task Dashboard:**
   

4. **SLA Enforcement:**
   - Each task type has SLA:
     - Review submission: 24h
     - Approve payout: 3 days
     - Generate report: 7 days
   - System sends alerts:
     - 2h before deadline: Email notification
     - Deadline passed: Escalate to manager

**Performance Scoring:**

1. **Score Calculation:**
   

2. **Score Tiers & Rewards:**
   

3. **Leaderboard:**
   - Dashboard hiển thị top performers
   - Public visibility → Healthy competition


**Example:**

**Tuần 1:**
- Admin A: 15 tasks assigned
- Complete 12 (3 missed SLA) → Completion: 80%
- Avg time: 2.5h/task (SLA: 3h) → Speed: 83%
- Quality ratings: 4.5/5 avg → Quality: 90%
- **Score:** (80 × 0.5) + (83 × 0.3) + (90 × 0.2) = 40 + 24.9 + 18 = **82.9/100** → Tier: Good

**Tuần 2:**
- Admin A improve: Complete 14/15 tasks
- 0 missed SLA → Completion: 93%
- Speed: 90%, Quality: 95%
- **Score:** (93 × 0.5) + (90 × 0.3) + (95 × 0.2) = 46.5 + 27 + 19 = **92.5/100** → Tier: Excellent → +20% bonus

**Result:** Admin A earn 10M + 2M bonus = 12M VND tháng đó

---

### Brand Portal - Dashboard Modernization
**Timeline:** 15/3 → 31/3 | **Priority:** P1

**Lợi ích:**

**Cho Brand:**
- ⚡ **Quick insights:** Dashboard auto-refresh khi có data mới (WebSocket push) → Không cần F5, thấy updates trong vài phút
- 📊 **Beautiful UI:** Modern design (shadcn/ui) → Professional, dễ present cho leadership
- 📱 **Mobile-friendly:** Brand managers xem dashboard trên iPhone/Android → Check anywhere
- 🎯 **Custom views:** Brand A quan tâm ROI → Dashboard highlight ROI metrics

**Cách hoạt động:**

**Dashboard Components:**

1. **Campaign Overview Cards (Top Row):**
   

2. **Performance Charts (Middle Section):**
   - **Views Over Time:** Line chart showing daily views
   - **Conversion Funnel:** Bar chart (Views → Clicks → Conversions)
   - **Top Influencers:** Table ranking by performance

3. **Budget Tracking (Bottom Left):**
   

4. **Real-time Feed (Bottom Right):**
   

5. **Quick Actions (Floating Button):**
   - Create Campaign
   - Browse Influencers
   - View Reports
   - Settings

**Real-time Updates:**
- WebSocket connection to backend
- Server pushes updates every 5s:
  - New submissions
  - Campaign status changes
  - Budget updates
- No need to refresh page

**Customization:**
- **Brand A Dashboard:**
  - Highlight: ROI, Conversion rate
  - Charts: Revenue per campaign
- **Brand B Dashboard:**
  - Highlight: Reach, Engagement
  - Charts: Views over time


**Example:**

Brand A campaign "Thẻ tín dụng review" có Dashboard:

**Real-time Update (Live Feed):**
- 9:05 AM: Influencer A submitted video review ✅
- 9:12 AM: Influencer B clicked "Generate Link" 🔗
- 9:28 AM: Campaign reached 50k views milestone 🎉
- 9:35 AM: Influencer C earned 500k commission 💰

**Overview Cards (Top Row):**
- **Total Reach:** 2.5M views (↑12% vs yesterday)
- **Conversions:** 45 signups (↑8 today)
- **Budget Used:** 18M/30M VND (60% spent)
- **ROI:** 3.5x (Every 1M spent = 3.5M revenue)

**Performance Chart (Middle):**
- Line chart: Views tăng đều từ 0 → 2.5M trong 15 ngày
- Conversion funnel: 2.5M views → 125k clicks → 45 signups (1.8% CVR)

→ Brand manager xem dashboard trên iPhone lúc đi coffee, biết ngay campaign perform tốt

---

### Automated Campaign Lifecycle
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**

**Cho Brand/Admin:**
- ⚡ **Tự động hóa 70% workflow:** Manual work từ 10h → 3h per campaign
- 📊 **Không bỏ sót steps:** System enforce trình tự (Brief → Discovery → Budgeting → Approval)
- 🎯 **Audit trail:** Track "Ai làm gì, khi nào" → Transparency, accountability
- 🤖 **Notification tự động:** Stakeholders được notify đúng lúc → Không cần remind manual

**Cho Management:**
- 📊 **Visibility:** Dashboard hiển thị "Campaign X đang ở stage Discovery, còn 1 ngày deadline"
- 💰 **Faster time-to-market:** Launch campaigns nhanh hơn 50% (15 days → 7 days)

**Cách hoạt động:**

**5-Stage Lifecycle:**

**Stage 1: BRIEF (Brand Team)**
- **Input:**
  - Campaign goals (VD: "Increase credit card signups by 20%")
  - Target audience (Age 25-35, Finance-savvy)
  - Budget range (50M-100M VND)

- **Output:**
  - Campaign brief document (PDF/Doc)

- **SLA:** 2 days

- **Auto-actions:**
  - Status: "Brief submitted"
  - Notification → Marketing Manager: "New campaign brief ready for review"
  - Dashboard update: Stage 1/5 completed

**Stage 2: DISCOVERY (Marketing Manager)**
- **Input:**
  - Campaign brief from Stage 1

- **Actions:**
  - Use AI Agent Assistant (Feature #10) để draft campaign
  - Browse Influencer Library (Feature #5) để find candidates
  - Select 20-50 potential influencers

- **Output:**
  - Influencer shortlist
  - Campaign draft (title, description, requirements)

- **SLA:** 3 days

- **Auto-actions:**
  - Status: "Discovery completed"
  - Notification → Finance Team: "Campaign ready for budget approval"

**Stage 3: BUDGETING (Finance Team)**
- **Input:**
  - Influencer shortlist + estimated costs

- **Actions:**
  - Review costs: 50 influencers × 500k = 25M VND
  - Check budget availability
  - Approve / Adjust / Reject

- **Output:**
  - Approved budget (VD: 30M VND approved)

- **SLA:** 1 day

- **Auto-actions:**
  - Status: "Budget approved"
  - Notification → Marketing Manager: "Budget approved, proceed to final approval"

**Stage 4: APPROVAL (Director/VP)**
- **Input:**
  - Full campaign plan (brief + influencers + budget)

- **Actions:**
  - Review complete package
  - Approve / Reject / Request changes

- **Output:**
  - Final approval signature

- **SLA:** 2 days

- **Auto-actions:**
  - Status: "Campaign approved"
  - Notification → Operations Team: "Campaign live, start booking influencers"
  - Campaign published on platform

**Stage 5: EXECUTION (Operations Team)**
- **Actions:**
  - Book influencers (Feature #7: Booking System)
  - Monitor submissions
  - Review content
  - Process payouts
  - Generate performance report

- **Output:**
  - Campaign completion report
  - Performance metrics (Views, CTR, CVR, ROI)

- **SLA:** 30 days (campaign duration)

- **Auto-actions:**
  - Status: "Campaign completed"
  - Notification → All stakeholders: "Campaign complete, view report"

**Timeline Tracking:**

**Example:**

Campaign Brand A "Thẻ tín dụng review" lifecycle:

**Stage 1 - BRIEF (Brand Team - 2 days):**
- **Day 1:** Brand nhập goals: "Increase credit card signups by 20%"
- **System:** Status → "Brief submitted", notify Marketing Manager

**Stage 2 - DISCOVERY (Marketing - 3 days):**
- **Day 3:** Marketing Manager dùng AI Agent, generate campaign draft
- **Day 4:** Browse Influencer Library, select 50 influencers Finance niche
- **Day 5:** Complete, notify Finance Team

**Stage 3 - BUDGETING (Finance - 1 day):**
- **Day 6:** Finance review: 50 × 500k = 25M VND
- Budget check: 30M available ✅
- Approve 25M, notify Director

**Stage 4 - APPROVAL (Director - 2 days):**
- **Day 7-8:** Director review full package → Approve
- System publish campaign, notify Operations

**Stage 5 - EXECUTION (Operations - 30 days):**
- **Day 9:** Book 50 influencers
- **Day 9-30:** Monitor, review, process payouts
- **Day 31:** Generate report → Campaign complete

**Timeline:** 15 days setup + 30 days execution = 45 days total (Fast!)

---

### Influencer Portal - UX/UI Modernization
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**

**Cho Influencer:**
- ⚡ **Navigation nhanh 3x:** Đi từ A → B chỉ 1-2 clicks (thay vì 5-6 clicks)
- 📱 **Mobile-first:** 80% influencers dùng điện thoại → UI perfect trên mobile
- 💎 **Onboarding smooth:** New users hiểu cách dùng trong 2 phút (không cần training)
- 🎨 **Modern design:** Beautiful UI → Cảm thấy professional → Muốn quay lại

**Cho Platform:**
- 📊 **Retention +15%:** UX tốt → Users quay lại nhiều hơn
- ⚡ **Fast loading <1s:** Next js SSR → SEO tốt, user happy
- 💰 **Giảm support tickets:** Intuitive UI → Users tự xử lý được

**Cách hoạt động:**

**UI Improvements:**

**Tech Stack:**
- Next.js 15 (App Router + Server Components)
- TypeScript (type safety)
- Tailwind CSS (utility-first styling)
- shadcn/ui (beautiful, accessible components)
- Framer Motion (smooth animations)

**Performance Optimization:**
- SSR (Server-side rendering)
- Code splitting & lazy loading
- Image optimization (Next.js Image component)
- CDN deployment (Vercel Edge)

**Before (Old UI):**
- 6 clicks để join campaign: Login → Campaigns → Scroll → Click → Join → Form → Submit
- Page load: 3 seconds
- User satisfaction: 3.2/5
- Desktop-first design, mobile experience kém

**After (Modern UI):**
- 2 clicks để join: Open app → Swipe card → Join (1-click)
- Page load: 0.8 seconds (SSR + optimization)
- User satisfaction: 4.7/5
- Mobile-first design, perfect trên mọi devices

**Navigation Structure:**

**Bottom Tab Bar (Mobile):**
- 🏠 **Home:** Dashboard, quick stats, recent activity
- 📱 **Campaigns:** Browse campaigns với swipe cards, AI recommendations
- 📚 **Library:** Influencer library access (nếu có premium)
- 💰 **Earnings:** View/Affiliate revenue tracking, payout history
- 👤 **Profile:** Settings, linked accounts, performance stats

**Sidebar (Desktop):**
- Collapsible menu với same sections như mobile
- Hover để expand/collapse
- Pin favorite sections
- Search bar để quick navigation

**Onboarding Flow (New Users):**

**Step 1: Welcome Screen (5 giây)**
- Giới thiệu platform: "Earn money by promoting brands you love"
- Show benefits: Dual income (Views + Affiliate)
- Button: "Get Started" → Next step

**Step 2: Link Pub2 Account (10 giây)**
- 1-click OAuth integration với Pub2 AccessTrade
- Button: "Connect Pub2 Account"
- Auto-fetch publisher info → No manual input needed
- Success: "✅ Pub2 Connected"

**Step 3: Complete Profile (2 phút)**
- Fill basic info:
  - Display Name
  - Niche selection (Finance, Beauty, Tech, Lifestyle...)
  - Social media links (TikTok, Instagram, YouTube)
  - Bio (optional)
- Auto-validate: Check follower count từ social APIs
- Save → Profile created

**Step 4: Browse First Campaign (30 giây)**
- Guided tour: "Swipe để xem campaigns"
- Show 3-5 recommended campaigns (match niche)
- Highlight: "This campaign matches your Finance niche!"
- User can skip hoặc explore

**Step 5: Generate First Link (10 giây)**
- Demo workflow: Click campaign → Click "Generate Link"
- System generate demo affiliate link
- Toast notification: "✅ Link generated! Copy & share to start earning"
- Show estimated earnings: "Each conversion = 500k VND"

**Step 6: Done! (Ready to Earn)**
- Success screen: "🎉 You're all set!"
- Summary:
  - ✅ Pub2 connected
  - ✅ Profile completed
  - ✅ Know how to generate links
- CTA: "Browse Campaigns" → Start earning
- **Total onboarding time: 3 phút**


**Technical Stack:**

**Frontend:**
- **Framework:** Next js 15 (App Router + Server Components)
- **Language:** TypeScript (type safety)
- **UI Library:** React 19 (latest features)
- **Styling:** Tailwind CSS (utility-first)
- **Components:** shadcn/ui (beautiful, accessible)
- **Animations:** Framer Motion (smooth transitions)
- **Icons:** Lucide React

**Performance:**
- **SSR:** Server-side rendering → Fast initial load
- **Code splitting:** Lazy load routes → Smaller bundles
- **Image optimization:** Next js Image component → Fast images
- **CDN:** Deploy on Vercel Edge → Global fast delivery

**Mobile Optimization:**
- **Touch targets:** Min 44×44px (Apple guidelines)
- **Gestures:** Swipe navigation, pull-to-refresh
- **Viewport:** Responsive breakpoints (mobile/tablet/desktop)

**Example:**

**Before (Old UI - Desktop-first, 6 clicks):**
- User login → Home page
- Click "Campaigns" menu (top nav)
- Scroll long list (no filters)
- Click campaign → New page load
- Click "Join" → Fill form (5 fields)
- Submit → Wait 2-3s loading

**After (Modern UI - Mobile-first, 2 clicks):**
- User open app on iPhone
- Bottom tab "Campaigns" → Instant load (SSR)
- See recommended campaigns (AI-powered)
- Swipe card → Click "Join" → 1-click join
- Success toast: "Joined! Generate link now?"

**Performance:**
- Page load: 3s → 0.8s (SSR + optimization)
- Click to join: 6 clicks → 2 clicks
- User satisfaction: 3.2/5 → 4.7/5

**Onboarding (New user flow):**
- **Step 1:** Welcome screen (5s)
- **Step 2:** Link Pub2 account (1-click OAuth, 10s)
- **Step 3:** Fill profile (2 mins)
- **Step 4:** Browse first campaign (30s)
- **Step 5:** Generate first link (10s)
- **Total:** 3 phút → Start earning!

→ Retention tăng 15% (users quay lại nhiều hơn vì UX tốt)


**Cập nhật:** 2026-02-28
**Version:** 3.1 - Thêm bảng timeline tổng hợp 3 dự án
**Người tạo:** Diso Team
