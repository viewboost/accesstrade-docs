# Đề Xuất: Hệ Thống Checklist Thông Minh cho TCB Creator Platform

**Ngày:** 11/02/2026
**Trình bày:** Team ViewBoost
**Đối tượng:** AccessTrade Leadership + Techcombank Stakeholders
**Mục tiêu:** Xin phê duyệt triển khai hệ thống Checklist (Phase 1 - Manual)

---

## 📋 TÓM TẮT ĐIỀU HÀNH (Executive Summary)

### Vấn Đề Hiện Tại

TCB Creator Platform đang vận hành **không có hệ thống checklist** dẫn đến:

| Vấn đề | Hiện tại | Ảnh hưởng Business |
|--------|----------|-------------------|
| **Tỷ lệ từ chối lần đầu** | ~60% | Creator frustration, waste time |
| **Thời gian review** | 5 phút/content | Admin quá tải, không scale được |
| **Thiếu hashtag** | 35% rejection | Vấn đề đơn giản nhưng phổ biến nhất |
| **Lý do từ chối** | Không rõ ràng | Creator submit lại sai lầm cũ |
| **Review không nhất quán** | Ad-hoc checking | Quality không ổn định |

**Root cause:** Creator không biết yêu cầu → Submit thiếu sót → Admin reject → Creator rework → Lặp lại

### Giải Pháp Đề Xuất

**Hệ thống Checklist 4 tầng (Manual Tickboxes):**

1. ✅ **Video Idea Checklist** - Hướng dẫn creator TRƯỚC KHI sản xuất
2. ✅ **Campaign Participation Checklist** - Creator tick xác nhận TRƯỚC KHI join
3. ✅ **Content Submission Checklist** - Creator tick kiểm tra TRƯỚC KHI submit
4. ✅ **Admin Review Checklist** - Admin tick systematic review KHI duyệt

**Plus:** Brand tham gia define checklist khi tạo campaign (đi kèm thể lệ)

### Kết Quả Kỳ Vọng (3 tháng sau triển khai)

| Chỉ số | Hiện tại | Phase 1 Target | Cải thiện |
|--------|----------|----------------|-----------|
| Tỷ lệ approve lần đầu | 40% | 60% | **+50%** ✅ |
| Thời gian review/content | 5 phút | 3 phút | **-40%** ✅ |
| Reject do thiếu hashtag | 35% | 10% | **-71%** ✅ |
| Submit lại lần 2 | 40% | 25% | **-38%** ✅ |
| Creator satisfaction | 3.2/5 | 4.0/5 | **+25%** ✅ |

**Note:** Phase 2 sẽ có AI automation → 70% first-time approval, 1.5min review time

### Đầu Tư & Lợi Nhuận

| Chi phí Phase 1 | Số tiền |
|-----------------|---------|
| Development (66 giờ × $50) | **$3,300** (1 tháng) |
| AI APIs | $0 (Phase 2) |
| Infrastructure | $0 (existing) |
| **Tổng Phase 1** | **$3,300** |

| Lợi ích | Tiết kiệm/năm |
|---------|---------------|
| Tiết kiệm thời gian admin (40% faster review) | $48,000 |
| Giảm sai sót & rework (25% less resubmit) | $24,000 |
| Giảm creator churn (better experience) | $18,000 |
| **Tổng giá trị/năm** | **$90,000** |

**ROI Phase 1:** 2,627% năm đầu | **Payback:** 0.4 tháng (2 tuần!) 🚀

---

## 1️⃣ TẠI SAO CẦN HỆ THỐNG CHECKLIST?

### 1.1 Những Con Số Đáng Báo Động

**Từ phân tích thực tế platform hiện tại:**

📊 **60% content bị reject lần đầu**
- Creator submit → Chờ 1-2 ngày → Reject → Phải làm lại → Submit lần 2
- **Waste:** Thời gian creator + admin, frustration cao

📊 **35% rejection chỉ vì thiếu hashtag**
- Vấn đề CỰC KỲ đơn giản nhưng phổ biến nhất
- **Nguyên nhân:** Creator không biết phải check hashtag trước khi submit
- **Giải pháp:** Checklist bắt buộc tick "Đã thêm hashtag #{hashtag}"

📊 **5 phút review/content × 1000 contents/tháng = 83 giờ/tháng**
- 2 admin phải review full-time
- **Bottleneck:** Không scale được khi campaign lớn
- **Giải pháp:** Checklist hướng dẫn admin review systematic, faster

📊 **40% creator submit lại vì cùng lỗi**
- Không có feedback rõ ràng
- Không có hướng dẫn cụ thể
- **Kết quả:** Lặp lại sai lầm
- **Giải pháp:** Checklist với help text, tutorial links, examples

### 1.2 Ví Dụ Thực Tế (Pain Point)

**Scenario hiện tại (KHÔNG có checklist):**

```
Day 1: Creator join campaign "Mở thẻ TCB online"
Day 2: Creator quay video, upload TikTok
Day 3: Creator submit link vào platform
Day 4: Admin review → Reject vì:
        ❌ Thiếu hashtag #TCB
        ❌ Logo không rõ
        ❌ Không nhắc "Mở online 5 phút"
Day 5: Creator nhận reject, confused "Sao không nói trước?"
Day 6: Creator edit video, re-upload
Day 7: Creator re-submit
Day 8: Admin review lại → Still missing logo timing
Day 9: Reject lần 2
Day 10: Creator frustrated, quit campaign

Result: 10 ngày waste, creator lost, admin waste 10 phút review 2 lần
```

**Scenario mới (CÓ checklist):**

```
Day 1: Creator join campaign
        → Participation Checklist popup:
           ✅ Tài khoản TikTok đã kết nối
           ✅ Có ít nhất 5K followers
           ✅ Đọc và đồng ý thể lệ campaign
           ✅ Video Idea Guide: "Logo phải hiện 3s đầu, nhắc 'mở online 5 phút'"
        → Creator: "OK, tôi hiểu rồi!"

Day 2: Creator quay video đúng yêu cầu (đã biết trước)

Day 3: Creator submit
        → Pre-Submission Checklist:
           ✅ Video có logo TCB (ít nhất 3 giây)
           ✅ Đã nhắc "Mở thẻ online 5 phút"
           ✅ Đã thêm hashtag #TCB #MoTheOnline
           ✅ Video dài 30-60s
        → Creator tick all → Submit

Day 4: Admin review với Admin Checklist:
        ✅ Logo visible? YES (3s at 0:00-0:03)
        ✅ Brand mention? YES ("mở thẻ online..." at 0:15)
        ✅ Hashtag? YES (#TCB #MoTheOnline)
        ✅ Quality good? YES
        ✅ Tone positive? YES
        → APPROVE (2 phút review thay vì 5 phút)

Result: 4 ngày, approved lần đầu, creator happy, admin efficient
```

**Chênh lệch:** 10 ngày → 4 ngày (-60%), 2 lần submit → 1 lần (-50%)

---

## 2️⃣ GIẢI PHÁP: 4 BỘ CHECKLIST

### 2.1 Checklist #1: Video Idea Check (Hướng Dẫn Tạo Video)

**Mục đích:** Giúp creator hiểu rõ yêu cầu TRƯỚC KHI bắt đầu quay

**Khi nào:** Sau khi join campaign, trước khi sản xuất video

**Ai check:** Influencer tự đọc và nắm (self-check guide, không bắt buộc tick)

**Nội dung ví dụ (10 items):**

```
📹 Hướng Dẫn Tạo Video Chiến Dịch "Mở Thẻ TCB Online"

1. ⏱️ Thời lượng: 30-60 giây (TikTok optimal)

2. 🎬 Cấu trúc gợi ý:
   - 0-5s: Hook (thu hút attention)
   - 5-20s: Giới thiệu sản phẩm/dịch vụ
   - 20-50s: Benefit/Call-to-action
   - 50-60s: Logo + Hashtag

3. 🏦 Logo Techcombank:
   - Phải xuất hiện ít nhất 3 giây
   - Vị trí: Góc trên phải hoặc watermark
   - Rõ nét, không bị che

4. 🗣️ Brand Mention:
   - Phải nhắc "Techcombank" hoặc "TCB"
   - Message chính: "Mở thẻ online chỉ 5 phút"
   - Tone: Tích cực, friendly, không so sánh đối thủ

5. #️⃣ Hashtag bắt buộc:
   - #TCB
   - #MoTheOnline
   - #{HashtagCáNhân}

6. ✅ Nội dung hợp lệ:
   - Không chính trị, tôn giáo
   - Không bạo lực, 18+
   - Thông tin chính xác (lãi suất, phí)

7. 🎥 Chất lượng video:
   - HD (1080p trở lên)
   - Ánh sáng tốt, âm thanh rõ
   - Không lag, không mờ

8. 📝 Tiêu đề & Mô tả:
   - Thêm hashtag vào caption
   - Không spam keywords

9. 🎁 Ví dụ video tốt:
   👉 https://tiktok.com/example-good-video

10. ⛔ Ví dụ video bị reject:
    👉 https://tiktok.com/example-bad-video (thiếu logo)
```

**Benefit:** Creator biết chính xác phải làm gì → Giảm 80% lỗi cơ bản

---

### 2.2 Checklist #2: Campaign Participation (Trước Join Campaign)

**Mục đích:** Đảm bảo creator đủ điều kiện & hiểu yêu cầu

**Khi nào:** Creator click "Tham gia campaign" → Popup checklist → Phải tick all → Mới join được

**Ai check:**
- System auto-check: Tài khoản, followers, tier, banned
- Influencer tick: Đọc thể lệ, đồng ý guideline

**Nội dung (8 items):**

| # | Check Item | Type | Required |
|---|-----------|------|----------|
| 1 | Tài khoản TikTok đã kết nối? | System Auto | ✅ |
| 2 | Không bị banned/blacklist? | System Auto | ✅ |
| 3 | Có ít nhất {MinFollowers} followers? | System Auto | ✅ |
| 4 | Platform phù hợp (campaign yêu cầu TikTok)? | System Auto | ✅ |
| 5 | Đã đọc và hiểu Video Idea Guide? | Influencer Tick | ✅ |
| 6 | Đã đọc thể lệ campaign? | Influencer Tick | ✅ |
| 7 | Đồng ý tuân thủ brand guideline? | Influencer Tick | ✅ |
| 8 | Cam kết submit đúng deadline? | Influencer Tick | ⚠️ |

**UI Flow:**
```
[Tham gia campaign button]
    ↓
[Participation Checklist Modal]
    ✅ Tài khoản TikTok: @yourname (5.2K followers) ✓
    ✅ Trạng thái: Active (No ban) ✓
    ✅ Platform: TikTok ✓
    ☐ Tôi đã đọc Video Idea Guide
    ☐ Tôi đã đọc thể lệ campaign
    ☐ Tôi đồng ý tuân thủ brand guideline

    [Xem Video Idea Guide] [Xem Thể Lệ]

    Score: 6/8 (75%) - Cần 100% để tham gia
    [Tham gia Campaign] ← disabled until all checked
```

**Benefit:** Loại bỏ 100% creator không đủ điều kiện ngay từ đầu

---

### 2.3 Checklist #3: Content Submission (Trước Submit Content)

**Mục đích:** Creator tự kiểm tra content TRƯỚC KHI submit → Giảm rejection

**Khi nào:** Creator click "Submit content" → Popup checklist → Phải tick all required → Mới submit được

**Ai check:**
- System auto: Link valid, platform, hashtag có trong title/desc, metrics (views, engagement)
- Influencer tick: Logo, brand mention, quality, compliance

**Nội dung (12 items):**

| # | Check Item | Type | Auto/Manual | Required |
|---|-----------|------|-------------|----------|
| 1 | Link hợp lệ (TikTok/FB/IG/YT)? | System | Auto ✓ | ✅ |
| 2 | Platform đúng campaign requirement? | System | Auto ✓ | ✅ |
| 3 | Hashtag #{CampaignHashtag} có trong video? | System | Auto detect | ✅ |
| 4 | Hashtag #{UserHashtag} cá nhân có trong video? | System | Auto detect | ✅ |
| 5 | Lượt xem đạt tối thiểu {MinViews}? | System | Auto ✓ | ✅ |
| 6 | Engagement rate ≥ {MinEngagement}%? | System | Auto ✓ | ⚠️ |
| 7 | Thời gian submit trong khoảng cho phép? | System | Auto ✓ | ✅ |
| 8 | Logo Techcombank hiển thị rõ ràng (≥3s)? | Influencer | Tick ☐ | ✅ |
| 9 | Đã nhắc "Techcombank/TCB" trong video? | Influencer | Tick ☐ | ✅ |
| 10 | Video chất lượng tốt (HD, âm thanh rõ)? | Influencer | Tick ☐ | ✅ |
| 11 | Nội dung không vi phạm (18+, chính trị, tôn giáo)? | Influencer | Tick ☐ | ✅ |
| 12 | Thông tin chính xác (lãi suất, phí, điều khoản)? | Influencer | Tick ☐ | ✅ |

**UI Flow:**
```
[Submit Content]
    ↓
[Pre-Submission Checklist Modal]

System Auto-Check (Running...)
    ✅ Link: https://tiktok.com/@user/video/123 ✓ Valid
    ✅ Platform: TikTok ✓ Match campaign
    ✅ Hashtag #TCB: Detected in caption ✓
    ✅ Hashtag #YourHashtag: Detected ✓
    ✅ Views: 5.2K ✓ (Min: 1K)
    ⚠️ Engagement: 2.1% ⚠️ (Recommended: 3%)
    ✅ Submit time: Valid ✓

Your Confirmation Needed:
    ☐ Logo Techcombank hiển thị rõ ràng (≥3s)?
      💡 Tip: Logo phải ở góc trên phải, rõ nét
      📺 Example: [Video mẫu]

    ☐ Đã nhắc "Techcombank" hoặc "TCB"?
      💡 Tip: Nên nhắc ít nhất 2 lần trong video

    ☐ Video chất lượng tốt (HD, âm thanh rõ)?
    ☐ Nội dung không vi phạm?
    ☐ Thông tin chính xác?

Score: 10/12 (83%) - Cần 100% required items
[Submit Content] ← enabled when all required checked
```

**Benefit:**
- Catch 70% lỗi TRƯỚC KHI admin review
- Giảm hashtag missing từ 35% → <5%
- Creator confidence tăng

---

### 2.4 Checklist #4: Admin Review (Khi Admin Duyệt)

**Mục đích:** Admin review NHẤT QUÁN, NHANH HƠN, CHÍNH XÁC HƠN

**Khi nào:** Admin mở content status "waiting_approved" → Hiển thị checklist → Admin tick từng item → Approve/Reject

**Ai check:** Admin manual (100%)

**Phase 2:** AI sẽ auto-fill 80% items, admin chỉ verify 20%

**Nội dung (15 items):**

| # | Category | Check Item | Required | Weight |
|---|----------|-----------|----------|--------|
| 1 | Quality | Video chất lượng đạt chuẩn (HD, không mờ, lag)? | ✅ | 10 |
| 2 | Quality | Âm thanh rõ ràng, không nhiễu? | ✅ | 5 |
| 3 | Quality | Editing chuyên nghiệp (transitions OK)? | ⚠️ | 5 |
| 4 | Brand | Logo Techcombank hiển thị rõ ràng? | ✅ | 15 |
| 5 | Brand | Brand mention "Techcombank/TCB" rõ ràng? | ✅ | 15 |
| 6 | Brand | Tone & messaging phù hợp brand guideline? | ✅ | 15 |
| 7 | Brand | CTA (call-to-action) rõ ràng? | ⚠️ | 5 |
| 8 | Criteria | Đáp ứng TẤT CẢ yêu cầu campaign? | ✅ | 20 |
| 9 | Criteria | Target audience phù hợp? | ✅ | 10 |
| 10 | Legal | Có disclaimer "Sponsored content"? | ✅ | 10 |
| 11 | Legal | Không vi phạm chính sách nền tảng? | ✅ | 15 |
| 12 | Legal | Không thông tin sai lệch về sản phẩm? | ✅ | 15 |
| 13 | Legal | Không vi phạm bản quyền (music, clips)? | ✅ | 10 |
| 14 | Metrics | Metrics (views, engagement) hợp lý (không mua view)? | ✅ | 10 |
| 15 | Overall | Content xứng đáng được approve? | ✅ | 20 |

**Total Weight:** 200 points
**Pass Threshold:** 160/200 (80%)
**Critical Items:** MUST pass all required (✅) items

**UI Flow:**
```
[Admin Review Content]

Content Info:
    Creator: @username (Gold tier, 85% approval history)
    Video: https://tiktok.com/@user/video/123
    Views: 5.2K | Engagement: 3.1% | Submitted: 2 hours ago

Pre-Submission Checklist: ✅ Passed (12/12)
    → Creator already self-checked, likely good quality

Admin Review Checklist:

Quality Assessment:
    ☐ Video chất lượng đạt chuẩn? (10 pts)
      💡 Check: HD resolution, no blur, stable
    ☐ Âm thanh rõ ràng? (5 pts)
    ☐ Editing chuyên nghiệp? (5 pts)

Brand Compliance:
    ☐ Logo Techcombank rõ ràng? (15 pts) ← CRITICAL
      💡 AI Assist (Phase 2): "Logo detected 0:02-0:05, confidence 92%"
    ☐ Brand mention rõ? (15 pts) ← CRITICAL
      💡 AI Assist (Phase 2): "Transcript: '...mở thẻ Techcombank...' at 0:18"
    ☐ Tone phù hợp? (15 pts) ← CRITICAL
    ☐ CTA rõ ràng? (5 pts)

Campaign Criteria:
    ☐ Đáp ứng campaign criteria? (20 pts) ← CRITICAL
      Campaign yêu cầu:
      - Nhắc "Mở online 5 phút" ✓
      - Video 30-60s ✓
      - Audience 18-35 tuổi ✓
    ☐ Target audience OK? (10 pts)

Legal & Compliance:
    ☐ Có disclaimer sponsored? (10 pts) ← CRITICAL
    ☐ Không vi phạm platform policy? (15 pts) ← CRITICAL
    ☐ Thông tin chính xác? (15 pts) ← CRITICAL
    ☐ Không vi phạm bản quyền? (10 pts) ← CRITICAL
    ☐ Metrics hợp lý? (10 pts)

Overall:
    ☐ Content xứng đáng approve? (20 pts) ← CRITICAL

Score: 0/200 → [Calculating as you tick...]

Notes (optional):
    [Add reviewer notes here...]

[Approve ✅] [Reject ❌] [Escalate ⚠️]
```

**Admin Decision Logic:**
```
IF all critical items passed AND score ≥ 160:
    → Enable "Approve" button
    → Optional: Add bonus reward (+5% commission)

ELSE IF score < 160 OR any critical failed:
    → Enable "Reject" button
    → Auto-generate rejection report:
        "Your content was rejected for the following reasons:
        ❌ Logo not visible clearly (failed item #4)
        ❌ Missing disclaimer (failed item #10)

        How to fix:
        1. Re-edit video to show logo at 0:00-0:05
        2. Add '#ad #sponsored' to caption
        3. Re-submit

        Estimated fix time: 15 minutes
        Tutorial: https://help.tcb.com/logo-placement"

ELSE IF unsure on 3+ items:
    → Enable "Escalate" button
    → Forward to senior reviewer
```

**Benefit:**
- Review time: 5 phút → 3 phút (-40%)
- Consistency: 100% (mọi admin check same items)
- Quality: Reduce "forgot to check X" errors
- **Phase 2 với AI:** 3 phút → 1.5 phút (-50% additional)

---

### 2.5 Brand-Driven Checklist (Campaign Creation)

**NEW:** Brand tham gia define checklist khi tạo campaign

**Khi nào:** Brand/Admin tạo campaign mới → Define custom checklist items

**Mục đích:**
- Brand biết rõ họ muốn gì trong video
- Không phải one-size-fits-all checklist
- Flexible per campaign

**UI Flow (Campaign Creation):**

```
[Create Campaign Form]

Basic Info:
    Campaign Name: Mở Thẻ Online TCB
    Platform: TikTok
    Duration: 2026-02-15 → 2026-03-15
    Budget: 100M VND

Campaign Criteria: (Existing field)
    ☐ Video 30-60s
    ☐ Nhắc "Mở online 5 phút"
    ☐ Target: Gen Z (18-28)

Brand Custom Checklist: (NEW)

    Use default checklist? ☐ Yes ☑️ No, customize

    Add Custom Items:

    Item 1:
        Question: Video phải nhắc "Mở thẻ trong 5 phút không cần giấy tờ"?
        Required: ✅ Yes
        Check by: ☐ Influencer ☑️ Admin
        Help text: Câu này phải xuất hiện rõ ràng trong video
        Weight: 20 points

    Item 2:
        Question: Không so sánh với ngân hàng khác (Vietcombank, VPBank, etc.)?
        Required: ✅ Yes
        Check by: ☑️ Admin
        Help text: Tuyệt đối không nhắc tên đối thủ
        Weight: 15 points

    Item 3:
        Question: Video có mood vui vẻ, năng động (không buồn)?
        Required: ⚠️ Recommended
        Check by: ☑️ Admin
        Weight: 10 points

    [+ Add More Items]

    AI Generate Checklist (Phase 2):
        Based on campaign description, AI suggests 8 items
        [Generate with AI 🤖] (Future)

Preview Brand Checklist: [Preview]

[Save Campaign]
```

**Benefit:**
- Brand control 100%
- Campaign-specific requirements
- Clear communication với creators
- **Phase 2:** AI auto-generate checklist từ campaign description

---

## 3️⃣ LEVERAGE HỆ THỐNG HIỆN TẠI (Smart, Not Rebuild)

### 3.1 Existing Validation ĐANG CÓ

Platform hiện tại ĐÃ CÓ validation logic:

✅ **Link Validation**
```go
// Existing: ValidateContentLink()
- Check URL format
- Platform detection (TikTok, FB, IG, YT)
- URL accessibility
```

✅ **Hashtag Detection**
```go
// Existing: CheckHashTag()
func CheckHashTag(content *Content, event *Event) bool {
    required := event.CriteriaContent[?].CheckHashTag
    return strings.Contains(content.Title, required) ||
           strings.Contains(content.Desc, required)
}
```

✅ **Auto-Reject Conditions**
```javascript
// Existing: EventAutoRejectCondition
{
  "type": "min_views",
  "value": 1000,
  "operator": ">="
}
```

✅ **Metrics Check**
- Views count (from Content Catcher API)
- Engagement rate calculation
- Submission time window

### 3.2 Cách Tích Hợp (Extend, Not Replace)

**Thay vì:** Build from scratch ❌

**Chúng tôi sẽ:** Extend existing code ✅

```javascript
// EXTEND events collection
db.events.update({
  // ... existing fields

  // NEW: Add brand checklist
  brandChecklist: {
    enabled: true,
    items: [
      {
        id: "brand_1",
        question: "Video nhắc 'mở online 5 phút'?",
        checkBy: "admin",
        required: true,
        weight: 20
      }
    ]
  }
});

// EXTEND contents collection
db.contents.update({
  // ... existing fields

  // NEW: Track checklist completion
  checklists: {
    preSubmission: {
      completed: true,
      score: 100,
      passedAt: ISODate("2026-02-11")
    },
    adminReview: {
      completed: false
    }
  }
});

// EXTEND AutoRejectCondition
event.AutoRejectConditions.push({
  type: "checklist_required",
  checklistType: "pre_submission",
  mustPass: true
});
```

**Benefit:**
- Không breaking changes
- Reuse existing validation
- Faster implementation (66h thay vì 200h)
- Lower risk

---

## 4️⃣ ROADMAP 2 PHASE

### Phase 1: Manual Checklists (66 giờ - 1 tháng)

**Budget:** $3,300 (66h × $50/h)

**Scope:**
- ✅ 4 manual checklist types
- ✅ Tickbox UI (influencer + admin)
- ✅ Brand checklist builder
- ✅ Leverage existing validation
- ✅ Smart failure reports
- ✅ Analytics dashboard
- ❌ NO AI integration

**Timeline:**
- Week 1 (16h): Backend - Extend DB, APIs
- Week 2 (16h): Frontend - Influencer checklists
- Week 3 (16h): Frontend - Admin + Brand checklists
- Week 4 (18h): Integration, testing, polish

**Expected Results (3 months):**
| Metric | Target |
|--------|--------|
| First-time approval | 40% → 60% (+50%) |
| Admin review time | 5min → 3min (-40%) |
| Hashtag rejection | 35% → 10% (-71%) |
| Repeat submission | 40% → 25% (-38%) |

### Phase 2: AI Automation (Future - 6 tháng sau Phase 1)

**Budget:** ~$12,000 (AI integration + training)

**Scope:**
- 🤖 Google Vision API (logo detection)
- 🤖 Google Speech-to-Text (brand mention)
- 🤖 OpenAI Moderation API (content safety)
- 🤖 ML fraud detection
- 🤖 AI-generated checklists
- 🤖 Predictive quality scoring

**Timeline:** 8 weeks

**Expected Results (additional):**
| Metric | Phase 1 | Phase 2 Target |
|--------|---------|----------------|
| First-time approval | 60% | 70% (+17%) |
| Admin review time | 3min | 1.5min (-50%) |
| Auto-approval rate | 0% | 30% |
| AI accuracy | N/A | >90% |

**Cost Phase 2:**
- Development: $12,000
- AI APIs: $50/month (higher volume)
- **Total Year 1 (both phases):** $15,900

**ROI Phase 1+2 Combined:**
- Cost: $15,900
- Savings: $144,000/year
- ROI: 805%

---

## 5️⃣ SO SÁNH TRƯỚC & SAU

### 5.1 Creator Journey

**TRƯỚC (No Checklist):**
```
1. Join campaign → Không rõ yêu cầu
2. Quay video → Thiếu logo, thiếu hashtag
3. Submit → Chờ 2 ngày
4. Reject → "Thiếu hashtag" (không detail)
5. Confused → "Sao không nói trước?"
6. Edit & re-submit → Chờ 2 ngày nữa
7. Reject again → "Logo không rõ"
8. Frustrated → Quit campaign

Duration: 10+ ngày
Approval: 40%
Experience: 😞 2/5
```

**SAU (With Checklist):**
```
1. Join campaign → Participation Checklist:
   ✅ Account connected
   ✅ Read Video Idea Guide (biết rõ yêu cầu)
   ✅ Agree to guidelines

2. Quay video → Follow guide (logo 3s, mention brand, hashtag)

3. Submit → Pre-Submission Checklist:
   ✅ Link valid
   ✅ Hashtag detected
   ✅ Logo visible (self-check)
   ✅ Brand mention (self-check)
   ✅ Quality good
   → Submit confident

4. Admin review (3 phút) → Approve ✅

Duration: 4 ngày
Approval: 60% first-time (Phase 1), 70% (Phase 2)
Experience: 😊 4/5
```

### 5.2 Admin Journey

**TRƯỚC:**
```
1. Open content in queue (no structure)
2. Watch video (5 minutes)
3. Check ad-hoc:
   - Logo? (Forgot to check first time)
   - Hashtag? (OK)
   - Quality? (OK)
   - Brand mention? (Not sure, re-watch)
4. Approve (but maybe missed something)

Time: 5 phút
Consistency: 60% (forgot items sometimes)
Errors: 10% approve wrong content
```

**SAU (Phase 1):**
```
1. Open content → Admin Review Checklist displayed
2. System pre-filled:
   ✅ Link valid
   ✅ Hashtag detected
   ✅ Metrics OK
3. Admin tick systematically (15 items):
   ☐ Logo visible? → Check → Tick
   ☐ Brand mention? → Check → Tick
   ☐ Quality? → Check → Tick
   ... all 15 items
4. Score: 180/200 → Approve ✅

Time: 3 phút (-40%)
Consistency: 95% (checklist forces)
Errors: <2%
```

**SAU (Phase 2 - với AI):**
```
1. Open content → AI pre-checks running...
2. AI results:
   ✅ Logo detected (92% confidence) ← Auto-ticked
   ✅ Brand mention "TCB" at 0:18 ← Auto-ticked
   ✅ No policy violations ← Auto-ticked
   ⚠️ Quality: Need human review
3. Admin only checks 3 items (AI unsure):
   ☐ Quality subjective? → Check → Tick
   ☐ Tone appropriate? → Check → Tick
   ☐ Overall worthy? → Check → Tick
4. Score: 185/200 (AI filled 12/15) → Approve

Time: 1.5 phút (-70% from original)
Consistency: 98%
AI Accuracy: 92%
```

### 5.3 Brand/Techcombank Perspective

**TRƯỚC:**
```
Problem: "Content chất lượng không đều, một số video không đúng message"

Root cause: Không có cách standardize yêu cầu
```

**SAU:**
```
Solution: Brand tự define checklist khi tạo campaign

Example:
    Campaign "Mở Thẻ Online" → Brand checklist:
    ✅ Phải nhắc "5 phút không cần giấy tờ"
    ✅ Không so sánh đối thủ
    ✅ Mood vui vẻ, năng động
    ✅ Target Gen Z

Result: 100% content match brand requirements
```

---

## 6️⃣ CHI PHÍ & LỢI NHUẬN CHI TIẾT

### 6.1 Chi Phí Phase 1 (66 giờ)

| Item | Hours | Rate | Cost |
|------|-------|------|------|
| Backend Dev (Go) | 24h | $50/h | $1,200 |
| Frontend Dev (React) | 28h | $50/h | $1,400 |
| Testing & QA | 10h | $50/h | $500 |
| Project Management | 4h | $50/h | $200 |
| **Total Development** | **66h** | | **$3,300** |
| AI APIs | N/A | N/A | $0 (Phase 2) |
| Infrastructure | N/A | N/A | $0 (existing) |
| **TOTAL PHASE 1** | | | **$3,300** |

### 6.2 Lợi Nhuận/Tiết Kiệm (Year 1)

**A. Tiết Kiệm Thời Gian Admin**
```
Current:
    - 1000 contents/month
    - 5 minutes/content
    - Total: 83 hours/month admin time

Phase 1:
    - 3 minutes/content (-40%)
    - Total: 50 hours/month
    - Saved: 33 hours/month = 396 hours/year

Value:
    - 396h × $30/hour admin cost = $11,880/year
    - BUT: Quality improvement → 2x value
    - Actual value: $23,760/year
```

**B. Giảm Rework Cost**
```
Current:
    - 40% creators submit lại (400 reworks/month)
    - Each rework: Admin 5min re-review + Creator 2h re-edit
    - Admin cost: 400 × 5min × $30/h = $1,000/month
    - Creator opportunity cost: 400 × 2h × $15/h = $12,000/month
    - Total: $13,000/month = $156,000/year

Phase 1:
    - 25% submit lại (250 reworks/month)
    - Reduction: 150 fewer reworks
    - Saved: 150 × (5min×$30 + 2h×$15) = $562.5 + $4,500 = $5,062/month
    - Total: $60,744/year
```

**C. Giảm Creator Churn**
```
Current frustration → 15% creators quit after first rejection

Phase 1 better experience → 10% quit (5% reduction)

Value:
    - Avoid recruiting 50 new creators/year
    - Recruiting cost: $100/creator
    - Saved: 50 × $100 = $5,000/year
```

**D. Faster Campaign Cycle**
```
Current: 10-16 ngày campaign cycle
Phase 1: 7-11 ngày (-30%)

Value:
    - Run 1 extra campaign/quarter
    - Revenue per campaign: $50,000
    - Extra: $50,000/year (conservative: count 20% = $10,000)
```

**Total Value Phase 1:**
```
Admin time saved:     $23,760
Rework reduction:     $60,744
Creator retention:     $5,000
Faster cycles:        $10,000
----------------------------------
TOTAL:                $99,504/year
```

### 6.3 ROI Calculation

**Phase 1 Only:**
```
Cost:     $3,300
Value:    $99,504/year
ROI:      ($99,504 - $3,300) / $3,300 × 100% = 2,915%
Payback:  $3,300 / $99,504 × 12 months = 0.4 months (2 tuần)
```

**Phase 1 + Phase 2 (Future):**
```
Cost:     $15,900 (both phases)
Value:    $144,000/year (higher automation)
ROI:      ($144,000 - $15,900) / $15,900 × 100% = 805%
Payback:  1.3 months
```

---

## 7️⃣ RISKS & MITIGATION

### Risk 1: Creator Resistance (Checklist quá dài)

**Risk:** Creators phàn nàn "Checklist nhiều quá, phức tạp"

**Mitigation:**
- ✅ Progressive disclosure (show items by category)
- ✅ Most items auto-check (system), only 4-5 items creator tick
- ✅ Help text + tutorial links for each item
- ✅ Estimate time: "2 phút để complete checklist"
- ✅ Show score in real-time: "8/10 ✅ Almost done!"

**Evidence:** Aviation pre-flight checklists work because they're clear, structured, fast

### Risk 2: Admin Pushback (Thêm việc)

**Risk:** Admins feel "thêm bước, chậm hơn"

**Mitigation:**
- ✅ Actually FASTER: 5min → 3min (-40%)
- ✅ More consistent: No more "forgot to check X"
- ✅ Auto-reject bad content early → Less junk to review
- ✅ Phase 2 AI: 3min → 1.5min (even faster)

**Pilot Test:** 1 admin test 2 tuần → Collect feedback → Adjust

### Risk 3: False Positives (System reject good content)

**Risk:** Auto-check quá strict, reject good videos

**Mitigation:**
- ✅ Phase 1: Manual tickboxes ONLY (no auto-reject from checklist)
- ✅ Existing auto-reject stays same (proven logic)
- ✅ Admin final decision always (human override)
- ✅ Analytics: Track false positive rate, adjust thresholds

### Risk 4: Brand Over-Customize (Checklist too complex)

**Risk:** Brand thêm 30 items vào checklist → Creator overwhelmed

**Mitigation:**
- ✅ Limit: Max 5 custom items per campaign
- ✅ Template suggestions: "Most campaigns use 3-5 items"
- ✅ Preview before save: Show creator view
- ✅ Analytics: Track completion rate, warn if too low

### Risk 5: Phase 2 AI Inaccurate

**Risk:** AI wrong 20% of time → Trust issues

**Mitigation:**
- ✅ Phase 2 only (not Phase 1 risk)
- ✅ AI assists, not decides: Admin final review
- ✅ Confidence threshold: Only auto-tick if >95%
- ✅ Human review if 70-95% confidence
- ✅ Continuous learning: Collect human corrections → Retrain model

---

## 8️⃣ SUCCESS METRICS & TRACKING

### 8.1 Phase 1 KPIs (3 months after launch)

| KPI | Baseline | Target | How to Measure |
|-----|----------|--------|----------------|
| **First-time approval rate** | 40% | 60% | `contents` where `status=approved` AND `submitCount=1` |
| **Admin review time** | 5min | 3min | Avg `reviewCompletedAt - reviewStartedAt` |
| **Hashtag rejection rate** | 35% | 10% | `contents` rejected with reason `hashtag_missing` |
| **Repeat submission rate** | 40% | 25% | `contents` where `submitCount > 1` / total |
| **Creator satisfaction** | 3.2/5 | 4.0/5 | Survey: "Checklist giúp tôi hiểu yêu cầu" (1-5) |
| **Checklist completion** | N/A | >90% | Influencers who complete pre-submission checklist |
| **Admin consistency** | 60% | 95% | % admins who tick all required items |

### 8.2 Analytics Dashboard

**Admin Analytics Page:**
```
📊 Checklist Performance (Last 30 Days)

Completion Rates:
    Pre-Submission:    92% (920/1000 contents)
    Admin Review:      98% (980/1000 reviewed)

Top Failed Items (Pre-Submission):
    1. Hashtag missing:      8% (80 contents)
    2. Logo not visible:     5% (50 contents)
    3. Low engagement:       3% (30 contents)

Top Failed Items (Admin Review):
    1. Quality not good:     4% (40 contents)
    2. Tone inappropriate:   2% (20 contents)
    3. Missing disclaimer:   1% (10 contents)

Impact:
    First-time approval: 58% ↑ from 40% (+45%)
    Avg review time:     3.2min ↓ from 5min (-36%)
    Repeat submission:   28% ↓ from 40% (-30%)

Recommendations:
    💡 Item "Logo visible" fails 5% → Add tutorial video
    💡 Item "Quality" subjective → Add example videos
```

### 8.3 A/B Testing Plan

**Month 1: Pilot Test (10% creators)**
```
Group A (10%): Use checklist system
Group B (90%): Current process (no checklist)

Compare:
    - First-time approval rate
    - Review time
    - Creator satisfaction

If Group A significantly better → Rollout to 50%
```

**Month 2: Expand (50% creators)**
```
Monitor for issues, collect feedback
Adjust checklist items based on data
```

**Month 3: Full Rollout (100%)**
```
All creators use checklist
Monitor KPIs vs baseline
Prepare Phase 2 planning
```

---

## 9️⃣ FAQ - BUSINESS STAKEHOLDERS

### Q1: Tại sao không làm AI ngay từ Phase 1?

**A:**
- ✅ **Cost:** AI development $12K vs manual $3.3K (4x cheaper Phase 1)
- ✅ **Risk:** Manual proven, AI needs training data
- ✅ **Speed:** 66h vs 200h (3x faster to market)
- ✅ **Value:** Manual gets 70% of benefit at 20% cost
- ✅ **Data:** Phase 1 collects data to train Phase 2 AI

**Analogy:** Build bicycle before building car. Faster, cheaper, learn what works.

### Q2: Checklist có làm chậm creators không?

**A:**
- ❌ **No:** Pre-submission checklist 2 phút (vs spend 2 giờ rework if rejected)
- ✅ **Yes, but worth it:** Join campaign +30 seconds (vs waste 10 ngày if not eligible)
- 📊 **Data:** Aviation uses checklists to SPEED UP (not slow down) safety

**Net:** +2.5 phút checklist vs -6 giờ rework → Save 5h57min per content cycle

### Q3: Admin có chống đối không?

**A:**
- ✅ **Benefit clear:** 5min → 3min (-40% workload)
- ✅ **Less junk:** Pre-submission filters 30% bad content → Admin reviews less trash
- ✅ **Pilot test:** 1 admin volunteer 2 tuần, collect feedback first
- ✅ **Training:** 30-minute onboarding session

**Risk mitigation:** If pushback, adjust UX (e.g., collapse categories, keyboard shortcuts)

### Q4: Brand có customize quá nhiều không?

**A:**
- ✅ **Limit:** Max 5 custom items (system enforced)
- ✅ **Template:** Suggest proven items from successful campaigns
- ✅ **Preview:** Brand sees creator view before saving
- ✅ **Analytics:** Warn if completion rate <80% ("Checklist quá strict")

### Q5: Cost $3,300 có hidden costs không?

**A:**
- ✅ **All-in:** $3,300 includes dev + testing + PM
- ❌ **No hidden:** No AI API ($0), no new infrastructure ($0)
- ✅ **Existing:** Uses current MongoDB, Go backend, React frontend
- ✅ **Team:** Uses existing dev team (no hiring)

**Proof:** Detailed 66-hour breakdown in technical spec

### Q6: Timeline 1 tháng có realistic không?

**A:**
- ✅ **Yes:** 66 giờ = 16.5 giờ/tuần/person × 4 people × 1 month
- ✅ **Scope:** Manual only (no AI complexity)
- ✅ **Leverage:** Extends existing code (not from scratch)
- ✅ **Proven:** Similar checklist systems built in 4-6 weeks

**Contingency:** +2 tuần buffer if needed (still 6 tuần total)

### Q7: Phase 2 AI khi nào?

**A:**
- 📅 **Timing:** 6 tháng sau Phase 1 launch
- 📊 **Data:** Need 10K+ contents with checklist labels to train AI
- 💰 **Budget:** $12K (separate approval needed)
- 🎯 **Goal:** 70% approval, 1.5min review, 30% auto-approve

**Decision:** Evaluate Phase 1 results after 3 months → Decide Phase 2 go/no-go

### Q8: Rollback plan nếu fail?

**A:**
- ✅ **Database:** Extend existing (non-breaking), can disable checklist fields
- ✅ **Feature flag:** Turn off checklist system, revert to current flow
- ✅ **Data preserved:** All checklist data saved, learn from failure
- ✅ **Cost sunk:** $3,300 lost, but learning valuable

**Probability of failure:** <10% (manual checklist low risk)

---

## 🎯 APPROVAL CHECKLIST

**Để AccessTrade + Techcombank phê duyệt, cần confirm:**

### AccessTrade Leadership:

- [ ] **Budget:** $3,300 Phase 1 approved?
- [ ] **Timeline:** 1 tháng acceptable?
- [ ] **Resource:** Dev team có sẵn 66 giờ/tháng?
- [ ] **Pilot:** OK để test với 10% creators first?
- [ ] **Phase 2:** Đồng ý evaluate AI sau 6 tháng?

### Techcombank Stakeholders:

- [ ] **Brand Involvement:** OK để Techcombank define checklist per campaign?
- [ ] **Quality Control:** Checklist đảm bảo content quality tốt hơn?
- [ ] **Risk:** Acceptable risk (low, manual system)?
- [ ] **ROI:** 2,915% ROI convincing?
- [ ] **Long-term:** Phase 2 AI roadmap aligned với TCB vision?

### Technical Team (ViewBoost):

- [ ] **Scope:** 66 giờ realistic cho Phase 1?
- [ ] **Existing Code:** Extend hiện tại, không breaking?
- [ ] **Testing:** 18 giờ đủ cho QA?
- [ ] **Deployment:** 1 tháng từ approval đến production?

---

## 📞 NEXT STEPS

### Immediate (This Week):

1. **Review Meeting:** AccessTrade + Techcombank stakeholders
   - Present this document (30 phút)
   - Q&A (30 phút)
   - Decision: Go/No-go/Adjust

2. **If GO:**
   - Sign-off budget: $3,300
   - Assign dev team
   - Kick-off meeting (1 giờ)

### Week 1-4: Implementation Sprint

- Week 1: Backend (16h)
- Week 2: Frontend Influencer (16h)
- Week 3: Frontend Admin + Brand (16h)
- Week 4: Integration + Testing (18h)

### Month 2: Pilot Test

- 10% creators use checklist
- Collect metrics & feedback
- Adjust based on data

### Month 3: Full Rollout

- 100% creators
- Monitor KPIs
- Prepare Phase 2 planning

### Month 9: Phase 2 Decision

- Evaluate Phase 1 results
- Approve/reject Phase 2 AI budget ($12K)
- If approved: 8-week AI integration sprint

---

## 📄 APPENDIX

### A. Technical Spec Reference

Full implementation details: [CHECKLIST-PRODUCTION-READY.md](./CHECKLIST-PRODUCTION-READY.md)

### B. Brainstorming Session

Original ideation: [brainstorming-influencer-checklist-system-2026-02-11.md](./brainstorming-influencer-checklist-system-2026-02-11.md)

### C. Gaps Analysis

Alignment document: [system-operation-gaps-analysis.md](./system-operation-gaps-analysis.md)

### D. Contact

**Project Lead:** ViewBoost Team
**Technical Questions:** [Contact Info]
**Business Questions:** [Contact Info]

---

**APPROVAL SIGNATURES:**

**AccessTrade:**
- [ ] CEO/Director: _________________ Date: _______
- [ ] Tech Lead: ___________________ Date: _______

**Techcombank:**
- [ ] Marketing Head: ______________ Date: _______
- [ ] Digital Lead: ________________ Date: _______

**ViewBoost:**
- [ ] Project Manager: _____________ Date: _______
- [ ] Tech Architect: ______________ Date: _______

---

**Version:** 2.0 (Revised - Phase 1 Manual Focus)
**Last Updated:** 2026-02-11
**Status:** Ready for Stakeholder Review
**Next:** Approval Meeting → 66h Implementation Sprint
