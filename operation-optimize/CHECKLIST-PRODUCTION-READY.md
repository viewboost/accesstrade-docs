# Production-Ready Checklist System for TCB Creator Platform

**Ngày:** 2026-02-11
**Version:** 1.0
**Based On:** Techcombank Codebase Analysis + Brainstorming Session
**Status:** Production-Ready Specification

---

## Executive Summary

Document này định nghĩa **4 bộ checklist production-ready** cho TCB Creator Platform, được thiết kế dựa trên:
- ✅ Phân tích kỹ codebase hiện tại (71 MongoDB collections, Go backend, React frontend)
- ✅ Validation logic đang có (AutoRejectCondition, hashtag validation, CriteriaContent)
- ✅ Pain points đã xác định (manual review overhead, no pre-submission guidance)
- ✅ Brainstorming insights (3-layer architecture, context-aware, smart feedback)

**4 Loại Checklist:**
1. **Campaign Participation Checklist** - Trước khi join campaign
2. **Pre-Submission Checklist** - Trước khi submit content
3. **Validation Checklist** - System auto-check khi submit
4. **Admin Review Checklist** - Admin manual review

---

## Table of Contents

1. [Data Model & Database Schema](#1-data-model--database-schema)
2. [Checklist #1: Campaign Participation](#2-checklist-1-campaign-participation)
3. [Checklist #2: Pre-Submission](#3-checklist-2-pre-submission)
4. [Checklist #3: Validation (Auto-Check)](#4-checklist-3-validation-auto-check)
5. [Checklist #4: Admin Review](#5-checklist-4-admin-review)
6. [Implementation Guide](#6-implementation-guide)
7. [API Specifications](#7-api-specifications)
8. [Frontend Components](#8-frontend-components)

---

## 1. Data Model & Database Schema

### 1.1 MongoDB Collections to Add

**Collection: `checklist_templates`**
```javascript
{
  _id: ObjectId,
  name: "Campaign Participation Checklist v1.0",
  version: "1.0.0",
  type: "participation" | "pre_submission" | "validation" | "admin_review",

  // Context filters
  campaignType: "view_boost" | "tracking_campaign" | null,  // null = all types
  platform: "tiktok" | "facebook" | "youtube" | "instagram" | null,
  creatorTier: "platinum" | "gold" | "silver" | "bronze" | null,

  // Checklist items
  items: [
    {
      id: "item_001",
      order: 1,
      category: "eligibility" | "content_quality" | "compliance" | "technical",
      question: "Tài khoản TikTok đã kết nối?",
      description: "Cần kết nối tài khoản TikTok để tham gia campaign",
      required: true,
      checkType: "influencer" | "system" | "admin",
      automationLevel: "manual" | "auto" | "ai",

      // Validation logic
      validationRule: {
        type: "social_account_connected",
        params: { platform: "tiktok" }
      },

      // Scoring
      weight: 10,  // Importance score 1-10
      passCondition: "boolean_true",

      // Failure handling
      failureAction: "block" | "warn" | "log",
      failureMessage: "Vui lòng kết nối tài khoản TikTok trước khi tham gia",

      // Help & guidance
      helpText: "Vào Cài đặt > Tài khoản xã hội > Kết nối TikTok",
      tutorialUrl: "https://help.tcb.com/connect-tiktok",
      exampleGoodUrl: null,
      exampleBadUrl: null
    }
  ],

  // Scoring config
  passThreshold: 80,  // Minimum score to pass (out of 100)

  // Metadata
  createdAt: ISODate,
  updatedAt: ISODate,
  createdBy: ObjectId,  // Admin staff ID
  status: "active" | "draft" | "archived"
}
```

**Collection: `checklist_instances`**
```javascript
{
  _id: ObjectId,
  templateId: ObjectId,  // Reference to checklist_templates

  // Context
  userId: ObjectId,      // Creator ID
  eventId: ObjectId,     // Campaign ID (if applicable)
  contentId: ObjectId,   // Content ID (if applicable)

  type: "participation" | "pre_submission" | "validation" | "admin_review",

  // Results
  items: [
    {
      itemId: "item_001",
      question: "Tài khoản TikTok đã kết nối?",

      checked: true,
      passed: true,
      score: 10,

      checkedBy: "influencer" | "system" | "admin",
      checkedByUserId: ObjectId,  // Staff ID if admin
      checkedAt: ISODate,

      // Evidence
      evidence: {
        type: "social_account_data",
        data: {
          platform: "tiktok",
          accountId: "tiktok_12345",
          connectedAt: ISODate
        }
      },

      // Failure details (if failed)
      failureReason: "TikTok account not connected",
      aiConfidence: 0.95,  // If AI check
      requiresHumanReview: false
    }
  ],

  // Overall result
  totalScore: 85,        // Out of 100
  passThreshold: 80,
  passed: true,

  status: "pending" | "in_progress" | "completed" | "failed",

  // Timing
  startedAt: ISODate,
  completedAt: ISODate,

  // Metadata
  createdAt: ISODate,
  updatedAt: ISODate
}
```

**Collection: `checklist_failures`**
```javascript
{
  _id: ObjectId,
  instanceId: ObjectId,

  userId: ObjectId,
  eventId: ObjectId,
  contentId: ObjectId,

  failedItems: [
    {
      itemId: "item_005",
      question: "Hashtag #TechcomBank có trong video?",
      reason: "Hashtag not detected in title or description",
      severity: "critical" | "warning",

      howToFix: "Thêm hashtag #TechcomBank vào tiêu đề hoặc mô tả video",
      tutorialUrl: "https://help.tcb.com/add-hashtag",
      exampleGoodUrl: "https://content.tcb.com/example-123"
    }
  ],

  // Auto-actions taken
  autoActions: {
    taskCreated: true,
    taskId: ObjectId,
    trainingEnrolled: false,
    notificationSent: true
  },

  // Resolution
  resolved: false,
  resolvedAt: null,

  createdAt: ISODate
}
```

### 1.2 Existing Collections to Extend

**Collection: `contents` - Add fields**
```javascript
{
  // ... existing fields ...

  // NEW: Checklist tracking
  checklists: {
    preSubmission: {
      instanceId: ObjectId,
      completed: true,
      score: 90,
      completedAt: ISODate
    },
    validation: {
      instanceId: ObjectId,
      completed: true,
      passed: true,
      score: 85,
      completedAt: ISODate
    },
    adminReview: {
      instanceId: ObjectId,
      completed: true,
      passed: true,
      score: 95,
      completedAt: ISODate
    }
  }
}
```

**Collection: `user_events` - Add fields**
```javascript
{
  // ... existing fields ...

  // NEW: Participation checklist
  participationChecklist: {
    instanceId: ObjectId,
    completed: true,
    score: 100,
    completedAt: ISODate
  }
}
```

---

## 2. Checklist #1: Campaign Participation

**Mục đích:** Đảm bảo creator đủ điều kiện tham gia campaign TRƯỚC KHI join

**Trigger:** Khi creator clicks "Tham gia campaign"

**Check Type:** 70% System Auto-check + 30% Influencer Confirm

### 2.1 Checklist Items

```yaml
# CATEGORY: Eligibility (Tự động check)

ITEM-001:
  order: 1
  question: "Tài khoản TikTok/Facebook/Instagram đã kết nối?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: social_account_connected
    params:
      platforms: [event.Options.ApplyForSources]  # From campaign config
  weight: 15
  failureAction: block
  failureMessage: "Vui lòng kết nối tài khoản {platform} trước khi tham gia"
  helpText: "Vào Cài đặt > Tài khoản xã hội > Kết nối {platform}"

ITEM-002:
  order: 2
  question: "Tài khoản không nằm trong blacklist?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: user_not_banned
    params:
      field: user.Banned
  weight: 20
  failureAction: block
  failureMessage: "Tài khoản của bạn đã bị khóa. Lý do: {user.BannedReason}"

ITEM-003:
  order: 3
  question: "Số lượng followers đủ điều kiện?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: min_followers
    params:
      platform: event.Options.ApplyForSources
      minFollowers: event.Options.MinFollowers || 1000
  weight: 10
  failureAction: block
  failureMessage: "Cần tối thiểu {minFollowers} followers để tham gia campaign này"

ITEM-004:
  order: 4
  question: "Chưa vượt giới hạn nội dung/ngày?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: max_content_per_day
    params:
      maxPerDay: event.Options.MaxContentPerDay || 3
      currentCount: count(contents where userId=user.ID and eventId=event.ID and createdAt=today)
  weight: 5
  failureAction: warn
  failureMessage: "Bạn đã submit {currentCount}/{maxPerDay} nội dung hôm nay. Vui lòng thử lại vào ngày mai."

# CATEGORY: Profile Completeness (Tự động check)

ITEM-005:
  order: 5
  question: "Họ tên đã cập nhật?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: field_not_empty
    params:
      field: user.Name
  weight: 5
  failureAction: block
  failureMessage: "Vui lòng cập nhật họ tên trong hồ sơ"

ITEM-006:
  order: 6
  question: "Số điện thoại đã xác thực?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: phone_verified
    params:
      field: user.Phone
  weight: 10
  failureAction: block
  failureMessage: "Vui lòng xác thực số điện thoại để nhận thanh toán"

ITEM-007:
  order: 7
  question: "Email đã xác thực?"
  required: false
  checkType: system
  automationLevel: auto
  validation:
    rule: email_verified
    params:
      field: user.Email
  weight: 5
  failureAction: warn
  failureMessage: "Nên xác thực email để nhận thông báo quan trọng"

ITEM-008:
  order: 8
  question: "Thông tin thanh toán đã đầy đủ?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: payment_info_complete
    params:
      fields: [user.BankAccount, user.BankName, user.BankBranch]
  weight: 15
  failureAction: block
  failureMessage: "Vui lòng cập nhật thông tin ngân hàng để nhận thanh toán"

# CATEGORY: Understanding & Agreement (Influencer confirm)

ITEM-009:
  order: 9
  question: "Đã đọc và hiểu yêu cầu campaign?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  failureMessage: "Vui lòng đọc kỹ yêu cầu campaign trước khi tham gia"
  helpText: "Xem chi tiết yêu cầu ở tab 'Thông tin campaign'"

ITEM-010:
  order: 10
  question: "Đã hiểu các tiêu chí đánh giá nội dung?"
  required: true
  checkType: influencer
  automationLevel: manual
  validation:
    rule: checkbox_checked
  weight: 5
  failureAction: block
  failureMessage: "Vui lòng xác nhận đã hiểu tiêu chí đánh giá"
  helpText: |
    Campaign này yêu cầu:
    {event.CriteriaContent[0]}
    {event.CriteriaContent[1]}
    ...

ITEM-011:
  order: 11
  question: "Đồng ý với điều khoản và điều kiện?"
  required: true
  checkType: influencer
  automationLevel: manual
  validation:
    rule: terms_accepted
  weight: 10
  failureAction: block
  failureMessage: "Bạn cần đồng ý với Điều khoản sử dụng để tham gia"
  helpText: "Xem Điều khoản tại đây"

ITEM-012:
  order: 12
  question: "Xác nhận có thời gian tham gia campaign?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 5
  failureAction: warn
  failureMessage: "Đảm bảo bạn có thể submit nội dung từ {event.StartAt} đến {event.EndAt}"
  helpText: "Campaign kéo dài từ {event.StartAt} đến {event.EndAt}"

# CATEGORY: No Conflict of Interest

ITEM-013:
  order: 13
  question: "Không có xung đột lợi ích?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 5
  failureAction: warn
  failureMessage: "Bạn cần xác nhận không quảng cáo cho đối thủ cạnh tranh cùng thời điểm"
  helpText: "Ví dụ: Không quảng cáo cho ngân hàng khác trong thời gian campaign Techcombank"
```

### 2.2 Scoring & Pass Threshold

**Total Weight:** 120 points
**Pass Threshold:** 95/120 (79%)

**Critical Items (Block if fail):**
- Social account connected (15 pts)
- Not blacklisted (20 pts)
- Min followers (10 pts)
- Payment info complete (15 pts)
- Terms accepted (10 pts)

**Warning Items (Can proceed with warning):**
- Email verified (5 pts)
- Max content per day (5 pts)
- Time availability (5 pts)
- No conflict (5 pts)

### 2.3 UI Flow

```
Creator clicks "Tham gia campaign"
    ↓
System shows Participation Checklist modal
    ↓
Auto-check 8 items (ITEM-001 to ITEM-008)
    ↓
Display results:
    ✅ 6/8 passed
    ❌ 2/8 failed (Payment info, Phone not verified)
    ↓
Influencer manually confirms 5 items (ITEM-009 to ITEM-013)
    ↓
Calculate total score: 95/120 (79%)
    ↓
IF score >= 95:
    → Allow join campaign
    → Show success message
ELSE:
    → Block join
    → Show failure report với detailed instructions
    → Create fix tasks automatically
```

---

## 3. Checklist #2: Pre-Submission

**Mục đích:** Hướng dẫn creator chuẩn bị content ĐÚNG CÁCH trước khi submit

**Trigger:** Khi creator clicks "Submit nội dung mới"

**Check Type:** 100% Influencer Self-Check (education-focused)

### 3.1 Checklist Items

```yaml
# CATEGORY: Content Preparation

ITEM-101:
  order: 1
  question: "Video đã được quay và edit xong?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 5
  helpText: "Đảm bảo video đã hoàn thiện trước khi submit"

ITEM-102:
  order: 2
  question: "Độ dài video phù hợp với platform?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  helpText: |
    TikTok: 15-60 giây (tối ưu 21-34s)
    YouTube Shorts: 15-60 giây
    Facebook Reels: 15-90 giây
    Instagram Reels: 15-90 giây
    YouTube: 2-10 phút

ITEM-103:
  order: 3
  question: "Video đã upload lên platform (TikTok/FB/IG/YT)?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 15
  failureAction: block
  failureMessage: "Bạn cần upload video lên platform trước khi submit link"
  helpText: "Hệ thống cần link video công khai để thu thập metrics"

ITEM-104:
  order: 4
  question: "Video ở chế độ PUBLIC (không private/unlisted)?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: "Video phải ở chế độ công khai để hệ thống thu thập views/likes"

# CATEGORY: Hashtag Requirements

ITEM-105:
  order: 5
  question: "Đã thêm hashtag cá nhân: #{user.Hashtag}?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: "Hashtag cá nhân của bạn: #{user.Hashtag}. Thêm vào tiêu đề hoặc mô tả video."

ITEM-106:
  order: 6
  question: "Đã thêm TẤT CẢ hashtag campaign bắt buộc?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 15
  failureAction: block
  helpText: |
    Hashtags bắt buộc cho campaign này:
    {event.Options.Hashtags[0]}
    {event.Options.Hashtags[1]}
    ...

    Thêm vào tiêu đề hoặc mô tả video.

# CATEGORY: Brand Guidelines

ITEM-107:
  order: 7
  question: "Đã nhắc đến tên thương hiệu trong video?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 15
  failureAction: block
  helpText: "Nhắc rõ tên 'Techcombank' hoặc 'TCB' ít nhất 1 lần trong video (verbal mention)"

ITEM-108:
  order: 8
  question: "Logo Techcombank hiển thị rõ ràng?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: "Logo TCB cần hiển thị ít nhất 3-5 giây, ở vị trí dễ nhìn (góc trên phải hoặc dưới)"

ITEM-109:
  order: 9
  question: "Nội dung phù hợp với yêu cầu campaign?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 20
  helpText: |
    Yêu cầu nội dung:
    {event.CriteriaContent.join('\n')}

# CATEGORY: Compliance & Legal

ITEM-110:
  order: 10
  question: "Đã thêm disclaimer 'Nội dung được tài trợ'?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: "Thêm text hoặc verbal: 'Video được tài trợ bởi Techcombank' hoặc '#ad #sponsored'"

ITEM-111:
  order: 11
  question: "Không có nội dung vi phạm chính sách?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: |
    Tránh:
    - Chính trị, tôn giáo, phân biệt chủng tộc
    - Nội dung bạo lực, khiêu dâm
    - Thông tin sai lệch về sản phẩm tài chính
    - Vi phạm bản quyền (music, images)

ITEM-112:
  order: 12
  question: "Nhạc nền không vi phạm bản quyền?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 5
  failureAction: warn
  helpText: "Sử dụng nhạc từ thư viện không bản quyền hoặc nhạc có license"

# CATEGORY: Metrics & Timing

ITEM-113:
  order: 13
  question: "Video được publish TRONG thời gian campaign?"
  required: true
  checkType: influencer
  automationLevel: manual
  weight: 10
  failureAction: block
  helpText: "Campaign: {event.StartAt} đến {event.EndAt}. Video publish ngoài thời gian này sẽ không được chấp nhận."

ITEM-114:
  order: 14
  question: "Đã chờ ít nhất 2 giờ sau khi publish để metrics ổn định?"
  required: false
  checkType: influencer
  automationLevel: manual
  weight: 5
  failureAction: warn
  helpText: "Nên chờ 2-24h sau publish để metrics (views, likes) ổn định trước khi submit"
```

### 3.2 Scoring & Pass Threshold

**Total Weight:** 150 points
**Pass Threshold:** 120/150 (80%)

**Mandatory Items (Block if not checked):**
- Video uploaded (15 pts)
- Video public (10 pts)
- Personal hashtag (10 pts)
- Campaign hashtags (15 pts)
- Brand mention (15 pts)
- Logo visible (10 pts)
- Content matches criteria (20 pts)
- Disclaimer added (10 pts)
- No policy violation (10 pts)
- Published within campaign dates (10 pts)

### 3.3 UI Flow

```
Creator clicks "Submit nội dung mới"
    ↓
Show Pre-Submission Checklist modal
    ↓
Display 14 items grouped by category
    ↓
Creator checks each item manually
    ↓
Real-time score calculation:
    Checked: 12/14 items
    Score: 135/150 (90%)
    ↓
IF all mandatory items checked:
    → Enable "Tiếp tục" button
    → Proceed to content link input form
ELSE:
    → Disable "Tiếp tục" button
    → Highlight unchecked mandatory items in RED
    → Show tooltip: "Bạn cần hoàn thành các mục bắt buộc (⭐)"
```

---

## 4. Checklist #3: Validation (Auto-Check)

**Mục đích:** System tự động validate content ngay khi submit

**Trigger:** Sau khi creator submit content link

**Check Type:** 100% System Auto-Check (AI + API + Database)

### 4.1 Checklist Items

```yaml
# CATEGORY: Technical Validation

ITEM-201:
  order: 1
  question: "Link content hợp lệ và accessible?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: url_valid_and_accessible
    params:
      url: content.Link
      timeout: 10s
  weight: 10
  failureAction: block
  failureMessage: "Link video không hợp lệ hoặc không thể truy cập. Vui lòng kiểm tra lại."

ITEM-202:
  order: 2
  question: "Platform source được campaign cho phép?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: platform_allowed
    params:
      contentSource: content.Source  # tiktok, facebook, youtube, instagram
      allowedSources: event.Options.ApplyForSources
  weight: 15
  failureAction: block
  failureMessage: "Campaign này chỉ chấp nhận nội dung từ: {event.Options.ApplyForSources.join(', ')}"

ITEM-203:
  order: 3
  question: "Content không trùng lặp (đã submit rồi)?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: not_duplicate
    params:
      query: { Link: content.Link, User: content.User }
  weight: 10
  failureAction: block
  failureMessage: "Bạn đã submit nội dung này rồi. Link: {content.Link}"

ITEM-204:
  order: 4
  question: "Content Catcher API crawl thành công?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: crawl_success
    params:
      api: "https://content-catcher.toibit.dev/api/v1/crawl/social-content"
      url: content.Link
  weight: 10
  failureAction: block
  failureMessage: "Không thể thu thập thông tin video. Vui lòng kiểm tra link hoặc thử lại sau."

# CATEGORY: Hashtag Validation (from existing logic)

ITEM-205:
  order: 5
  question: "Hashtag cá nhân #{user.Hashtag} có trong video?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: hashtag_present
    params:
      hashtag: user.Hashtag
      searchIn: [content.Title, content.Description]
      caseInsensitive: true
  weight: 15
  failureAction: block
  failureMessage: "Video thiếu hashtag cá nhân #{user.Hashtag}. Vui lòng thêm vào tiêu đề hoặc mô tả."

ITEM-206:
  order: 6
  question: "TẤT CẢ hashtag campaign có trong video?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: all_hashtags_present
    params:
      requiredHashtags: event.Options.Hashtags
      searchIn: [content.Title, content.Description]
      caseInsensitive: true
  weight: 20
  failureAction: block
  failureMessage: "Video thiếu hashtag campaign: {missingHashtags.join(', ')}. Vui lòng thêm vào tiêu đề hoặc mô tả."

# CATEGORY: Auto-Reject Conditions (from existing AutoRejectCondition)

ITEM-207:
  order: 7
  question: "Lượt xem đạt ngưỡng tối thiểu?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: min_views
    params:
      currentViews: content.Statistic.View
      minViews: autoRejectCondition.View  # From event.AutoRejectConditions
  weight: 15
  failureAction: block
  failureMessage: "Video cần tối thiểu {minViews} views. Hiện tại: {currentViews} views. Vui lòng chờ video có đủ views rồi submit lại."
  aiConfidenceThreshold: 0.9

ITEM-208:
  order: 8
  question: "Số lượt like đạt ngưỡng tối thiểu?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: min_likes
    params:
      currentLikes: content.Statistic.Like
      minLikes: autoRejectCondition.Like
  weight: 10
  failureAction: warn
  failureMessage: "Video nên có tối thiểu {minLikes} likes. Hiện tại: {currentLikes} likes."

ITEM-209:
  order: 9
  question: "Số lượt comment đạt ngưỡng tối thiểu?"
  required: false
  checkType: system
  automationLevel: auto
  validation:
    rule: min_comments
    params:
      currentComments: content.Statistic.Comment
      minComments: autoRejectCondition.Comment
  weight: 5
  failureAction: warn
  failureMessage: "Video nên có tối thiểu {minComments} comments. Hiện tại: {currentComments} comments."

ITEM-210:
  order: 10
  question: "Engagement rate đạt ngưỡng tối thiểu?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: min_engagement_rate
    params:
      engagement: (content.Statistic.Like + content.Statistic.Comment) / content.Statistic.View
      minEngagement: autoRejectCondition.Engagement
  weight: 15
  failureAction: block
  failureMessage: "Engagement rate quá thấp: {engagement*100}%. Yêu cầu tối thiểu: {minEngagement*100}%"

ITEM-211:
  order: 11
  question: "Video không quá cũ (tuổi content hợp lệ)?"
  required: true
  checkType: system
  automationLevel: auto
  validation:
    rule: content_age_valid
    params:
      publishedAt: content.PublishAt
      maxAgeDays: autoRejectCondition.ContentAge
      now: Date.now()
  weight: 10
  failureAction: block
  failureMessage: "Video đã publish cách đây {actualAge} ngày. Campaign chỉ chấp nhận video tối đa {maxAgeDays} ngày tuổi."

# CATEGORY: AI Content Checks

ITEM-212:
  order: 12
  question: "Logo Techcombank được AI phát hiện trong video?"
  required: true
  checkType: system
  automationLevel: ai
  validation:
    rule: ai_logo_detection
    params:
      api: "Google Vision API"
      video: content.Link
      logoKeywords: ["Techcombank", "TCB", "logo"]
      minConfidence: 0.85
  weight: 15
  failureAction: warn
  failureMessage: "AI không phát hiện logo TCB trong video (confidence: {aiConfidence}%). Admin sẽ review thủ công."
  requiresHumanReview: true  # If confidence < 0.95

ITEM-213:
  order: 13
  question: "Brand mention được AI phát hiện (speech-to-text)?"
  required: true
  checkType: system
  automationLevel: ai
  validation:
    rule: ai_speech_to_text
    params:
      api: "Google Speech-to-Text API"
      video: content.Link
      keywords: ["Techcombank", "TCB", "ngân hàng kỹ thuật"]
      minConfidence: 0.80
  weight: 15
  failureAction: warn
  failureMessage: "AI không phát hiện brand mention trong audio (confidence: {aiConfidence}%). Admin sẽ review thủ công."
  requiresHumanReview: true

ITEM-214:
  order: 14
  question: "Nội dung không vi phạm chính sách (AI moderation)?"
  required: true
  checkType: system
  automationLevel: ai
  validation:
    rule: ai_content_moderation
    params:
      api: "OpenAI Moderation API"
      content: [content.Title, content.Description]
      checkCategories: ["violence", "hate", "sexual", "self-harm"]
  weight: 20
  failureAction: block
  failureMessage: "Nội dung vi phạm chính sách: {violationCategory}. Vui lòng chỉnh sửa hoặc gỡ video."

# CATEGORY: Metrics Cross-Verification

ITEM-215:
  order: 15
  question: "Metrics từ Content Catcher khớp với Platform API?"
  required: false
  checkType: system
  automationLevel: auto
  validation:
    rule: metrics_cross_verify
    params:
      contentCatcherViews: content.Statistic.View
      platformAPIViews: fetchPlatformAPI(content.Link).views
      tolerance: 0.15  # Allow 15% variance
  weight: 5
  failureAction: warn
  failureMessage: "Metrics chênh lệch lớn giữa Content Catcher ({ccViews}) và Platform API ({apiViews}). Có thể cần review."
```

### 4.2 Scoring & Pass Threshold

**Total Weight:** 200 points
**Pass Threshold:** 160/200 (80%)

**Critical Blocks (Auto-reject if fail):**
- Link valid (10 pts)
- Platform allowed (15 pts)
- Not duplicate (10 pts)
- Crawl success (10 pts)
- Personal hashtag (15 pts)
- Campaign hashtags (20 pts)
- Min views (15 pts)
- Min engagement (15 pts)
- Content age (10 pts)
- No policy violation (20 pts)

**Warnings (Require human review):**
- Logo detection low confidence (15 pts)
- Brand mention low confidence (15 pts)
- Min likes (10 pts)
- Metrics variance (5 pts)

### 4.3 Automation Flow

```
Creator submits content link
    ↓
Content Catcher API crawls content (ITEM-204)
    ↓
PARALLEL EXECUTION:
    ├─ Technical checks (ITEM-201 to ITEM-204) - 2 seconds
    ├─ Hashtag validation (ITEM-205, ITEM-206) - 1 second
    ├─ Auto-reject conditions (ITEM-207 to ITEM-211) - 1 second
    └─ AI checks (ITEM-212 to ITEM-214) - 10-30 seconds (async via Asynq worker)
    ↓
Aggregate results:
    Passed: 12/15 items
    Failed: 3/15 items (Hashtag missing, Min views, Low engagement)
    Score: 145/200 (72.5%)
    ↓
IF score >= 160 AND no critical blocks:
    → Status: waiting_approved (admin queue)
ELSE IF critical block:
    → Status: auto_rejected
    → Generate detailed failure report
    → Send notification to creator
ELSE IF AI confidence low:
    → Status: waiting_approved (flagged for human review)
    → Attach AI analysis results for admin
```

---

## 5. Checklist #4: Admin Review

**Mục đích:** Hướng dẫn admin review content NHẤT QUÁN và HIỆU QUẢ

**Trigger:** Khi admin mở content ở status "waiting_approved"

**Check Type:** 100% Admin Manual Check (with AI assistance)

### 5.1 Checklist Items

```yaml
# CATEGORY: Content Quality Assessment

ITEM-301:
  order: 1
  question: "Chất lượng video đạt chuẩn (HD, không mờ, không lag)?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  aiAssist:
    type: video_quality_analysis
    show: "Resolution: 1080p, FPS: 30, Bitrate: 5000kbps"
  helpText: "Check: Độ phân giải, ánh sáng, âm thanh, không có watermark rác"

ITEM-302:
  order: 2
  question: "Âm thanh rõ ràng, không bị nhiễu?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 5
  helpText: "Nghe 10-20s đầu video để check chất lượng audio"

ITEM-303:
  order: 3
  question: "Content creative, engaging, không nhàm chán?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  helpText: "Đánh giá: Hook đầu video có hấp dẫn? Storytelling tốt? Giữ được attention?"

ITEM-304:
  order: 4
  question: "Editing chuyên nghiệp (transitions, effects hợp lý)?"
  required: false
  checkType: admin
  automationLevel: manual
  weight: 5
  helpText: "Check: Transitions mượt, effects không quá nhiều, pacing tốt"

# CATEGORY: Brand Compliance (with AI assist)

ITEM-305:
  order: 5
  question: "Logo Techcombank hiển thị rõ ràng và đúng vị trí?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  aiAssist:
    type: logo_detection_result
    show: "Logo detected at 0:05-0:10, confidence: 92%, position: top-right"
  helpText: "AI đã detect logo với confidence {aiConfidence}%. Xác nhận lại bằng mắt."

ITEM-306:
  order: 6
  question: "Brand mention 'Techcombank/TCB' được nhắc rõ ràng?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  aiAssist:
    type: speech_to_text_result
    show: "Transcript: '...mở thẻ Techcombank rất dễ dàng...', confidence: 88%"
  helpText: "AI transcript: {transcript}. Nghe lại để confirm."

ITEM-307:
  order: 7
  question: "Tone & messaging phù hợp với brand guideline?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  helpText: |
    Check:
    - Tone tích cực, không tiêu cực
    - Không so sánh với đối thủ một cách xấu
    - Thông điệp chính xác, không sai lệch

ITEM-308:
  order: 8
  question: "CTA (call-to-action) rõ ràng?"
  required: false
  checkType: admin
  automationLevel: manual
  weight: 5
  helpText: "Có kêu gọi hành động không? VD: 'Mở thẻ ngay', 'Tải app Techcombank'"

# CATEGORY: Campaign Criteria Compliance

ITEM-309:
  order: 9
  question: "Nội dung đáp ứng TẤT CẢ yêu cầu campaign?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 20
  aiAssist:
    type: criteria_checklist
    show: |
      Campaign yêu cầu:
      ☐ {event.CriteriaContent[0]}
      ☐ {event.CriteriaContent[1]}
      ...
  helpText: "Đối chiếu content với từng criteria. Phải đáp ứng 100%."

ITEM-310:
  order: 10
  question: "Target audience phù hợp?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  helpText: "Content có phù hợp với đối tượng target của campaign? (Age, location, interests)"

# CATEGORY: Legal & Compliance

ITEM-311:
  order: 11
  question: "Có disclaimer 'Sponsored content' rõ ràng?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  aiAssist:
    type: ocr_detection
    show: "OCR detected: '#ad #sponsored' at 0:03, confidence: 95%"
  helpText: "Check: Text overlay, caption, hoặc verbal mention về sponsored"

ITEM-312:
  order: 12
  question: "Không vi phạm chính sách nền tảng?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  aiAssist:
    type: moderation_result
    show: "AI Moderation: No violations detected (violence: 0%, hate: 0%, sexual: 0%)"
  helpText: |
    Check:
    - Không chính trị, tôn giáo nhạy cảm
    - Không bạo lực, khiêu dâm
    - Không phân biệt chủng tộc, giới tính

ITEM-313:
  order: 13
  question: "Không thông tin sai lệch về sản phẩm tài chính?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 15
  helpText: "Check: Lãi suất, phí, điều khoản được nói CHÍNH XÁC, không phóng đại"

ITEM-314:
  order: 14
  question: "Không vi phạm bản quyền (music, images, clips)?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  aiAssist:
    type: copyright_check
    show: "Music: 'Song Title' - Copyright free (YouTube Audio Library)"
  helpText: "Check: Nhạc nền, hình ảnh, video clips có license hợp lệ?"

# CATEGORY: Metrics Verification

ITEM-315:
  order: 15
  question: "Metrics (views, likes, comments) hợp lý?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  aiAssist:
    type: fraud_detection_score
    show: "Fraud Risk: Low (15%). Views: 50K, Engagement: 3.2%, Account age: 2 years"
  helpText: |
    Check suspicious patterns:
    - Sudden spike in views (bought views?)
    - Engagement rate too low (bot views?)
    - Creator history suspicious?

ITEM-316:
  order: 16
  question: "Creator không có lịch sử gian lận?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 10
  aiAssist:
    type: creator_history
    show: |
      Creator: @username
      - Campaigns joined: 12
      - Approval rate: 85%
      - Previous violations: 0
      - Tier: Gold
  helpText: "Check creator history: Approval rate, violations, blacklist"

# CATEGORY: Overall Assessment

ITEM-317:
  order: 17
  question: "Content xứng đáng được approve?"
  required: true
  checkType: admin
  automationLevel: manual
  weight: 20
  helpText: |
    Tổng quan:
    - Chất lượng tốt?
    - Đáp ứng yêu cầu?
    - Không có vấn đề lớn?
    - Sẽ mang lại giá trị cho campaign?

    Nếu KHÔNG chắc chắn → Escalate to senior reviewer
```

### 5.2 Scoring & Pass Threshold

**Total Weight:** 200 points
**Pass Threshold:** 160/200 (80%)

**Critical Items (Must pass to approve):**
- Video quality (10 pts)
- Logo visible (15 pts)
- Brand mention (15 pts)
- Tone & messaging (15 pts)
- Meets campaign criteria (20 pts)
- Disclaimer present (10 pts)
- No platform violations (15 pts)
- No false information (15 pts)
- No copyright violation (10 pts)
- Metrics reasonable (10 pts)
- No fraud history (10 pts)
- Overall worthy (20 pts)

### 5.3 Admin Review UI Flow

```
Admin opens content in review queue
    ↓
System displays Admin Review Checklist với 17 items
    ↓
AI Assist results shown alongside each item:
    ITEM-305: Logo detection (92% confidence, 0:05-0:10)
    ITEM-306: Speech-to-text transcript
    ITEM-311: OCR detected disclaimer
    ITEM-315: Fraud risk score (15% - Low)
    ↓
Admin reviews video và checks each item
    ↓
Options for each item:
    ✅ Pass (item passed)
    ❌ Fail (item failed - add reason)
    ⚠️ Unsure (flag for escalation)
    ↓
Calculate score: 175/200 (87.5%)
    ↓
IF score >= 160 AND all critical items passed:
    → Enable "Approve" button
    → Optional: Add bonus points (+5% reward)
ELSE IF score < 160:
    → Enable "Reject" button
    → Auto-generate detailed rejection report
    → Suggest training courses for creator
ELSE IF unsure items > 2:
    → Enable "Escalate" button
    → Forward to senior reviewer
```

---

## 6. Implementation Guide

### 6.1 Database Migration Steps

**Step 1: Create new collections**
```javascript
// MongoDB migration script
db.createCollection("checklist_templates");
db.createCollection("checklist_instances");
db.createCollection("checklist_failures");

// Create indexes
db.checklist_templates.createIndex({ type: 1, status: 1 });
db.checklist_templates.createIndex({ version: 1 });

db.checklist_instances.createIndex({ userId: 1, eventId: 1 });
db.checklist_instances.createIndex({ contentId: 1 });
db.checklist_instances.createIndex({ status: 1, createdAt: -1 });

db.checklist_failures.createIndex({ userId: 1, resolved: 1 });
db.checklist_failures.createIndex({ contentId: 1 });
```

**Step 2: Extend existing collections**
```javascript
// Add checklist tracking to contents collection
db.contents.updateMany(
  {},
  {
    $set: {
      checklists: {
        preSubmission: null,
        validation: null,
        adminReview: null
      }
    }
  }
);

// Add checklist to user_events
db.user_events.updateMany(
  {},
  {
    $set: {
      participationChecklist: null
    }
  }
);
```

**Step 3: Seed checklist templates**
```javascript
// Insert 4 default templates
db.checklist_templates.insertMany([
  {
    // Campaign Participation Checklist template (from Section 2)
  },
  {
    // Pre-Submission Checklist template (from Section 3)
  },
  {
    // Validation Checklist template (from Section 4)
  },
  {
    // Admin Review Checklist template (from Section 5)
  }
]);
```

### 6.2 Backend Implementation (Go)

**File structure:**
```
backend/
├── internal/
│   ├── model/
│   │   └── mg/
│   │       ├── checklist_template.go
│   │       ├── checklist_instance.go
│   │       └── checklist_failure.go
│   ├── service/
│   │   ├── checklist.go           # Core checklist logic
│   │   ├── checklist_validator.go # Validation rules
│   │   └── checklist_ai.go        # AI integration
│   └── constants/
│       └── checklist.go            # Constants, enums
└── pkg/
    ├── public/
    │   ├── handler/
    │   │   └── checklist.go        # Creator-facing API
    │   └── service/
    │       └── checklist.go
    └── admin/
        ├── handler/
        │   └── checklist.go        # Admin-facing API
        └── service/
            └── checklist.go
```

**Model definition (`internal/model/mg/checklist_template.go`):**
```go
package mg

type ChecklistTemplate struct {
    ID               AppID                  `bson:"_id"`
    Name             string                 `bson:"name"`
    Version          string                 `bson:"version"`
    Type             ChecklistType          `bson:"type"`

    // Context filters
    CampaignType     *string                `bson:"campaignType,omitempty"`
    Platform         *string                `bson:"platform,omitempty"`
    CreatorTier      *string                `bson:"creatorTier,omitempty"`

    // Items
    Items            []ChecklistTemplateItem `bson:"items"`

    // Scoring
    PassThreshold    int                    `bson:"passThreshold"`

    // Metadata
    Status           string                 `bson:"status"`
    CreatedAt        time.Time              `bson:"createdAt"`
    UpdatedAt        time.Time              `bson:"updatedAt"`
    CreatedBy        AppID                  `bson:"createdBy"`
}

type ChecklistTemplateItem struct {
    ID               string                 `bson:"id"`
    Order            int                    `bson:"order"`
    Category         string                 `bson:"category"`
    Question         string                 `bson:"question"`
    Description      string                 `bson:"description,omitempty"`
    Required         bool                   `bson:"required"`
    CheckType        CheckType              `bson:"checkType"`
    AutomationLevel  AutomationLevel        `bson:"automationLevel"`

    // Validation
    ValidationRule   *ValidationRule        `bson:"validationRule,omitempty"`

    // Scoring
    Weight           int                    `bson:"weight"`
    PassCondition    string                 `bson:"passCondition"`

    // Failure
    FailureAction    FailureAction          `bson:"failureAction"`
    FailureMessage   string                 `bson:"failureMessage"`

    // Help
    HelpText         string                 `bson:"helpText,omitempty"`
    TutorialURL      string                 `bson:"tutorialUrl,omitempty"`
    ExampleGoodURL   string                 `bson:"exampleGoodUrl,omitempty"`
    ExampleBadURL    string                 `bson:"exampleBadUrl,omitempty"`
}

type ValidationRule struct {
    Type   string                 `bson:"type"`
    Params map[string]interface{} `bson:"params"`
}

// Enums
type ChecklistType string
const (
    ChecklistTypeParticipation ChecklistType = "participation"
    ChecklistTypePreSubmission ChecklistType = "pre_submission"
    ChecklistTypeValidation    ChecklistType = "validation"
    ChecklistTypeAdminReview   ChecklistType = "admin_review"
)

type CheckType string
const (
    CheckTypeInfluencer CheckType = "influencer"
    CheckTypeSystem     CheckType = "system"
    CheckTypeAdmin      CheckType = "admin"
)

type AutomationLevel string
const (
    AutomationLevelManual AutomationLevel = "manual"
    AutomationLevelAuto   AutomationLevel = "auto"
    AutomationLevelAI     AutomationLevel = "ai"
)

type FailureAction string
const (
    FailureActionBlock FailureAction = "block"
    FailureActionWarn  FailureAction = "warn"
    FailureActionLog   FailureAction = "log"
)
```

**Service implementation (`internal/service/checklist.go`):**
```go
package service

type ChecklistService struct {
    repo      *ChecklistRepository
    validator *ChecklistValidator
    aiService *ChecklistAIService
}

// Execute checklist instance
func (s *ChecklistService) ExecuteChecklist(
    ctx context.Context,
    templateID AppID,
    userID AppID,
    eventID *AppID,
    contentID *AppID,
) (*ChecklistInstance, error) {

    // 1. Load template
    template, err := s.repo.GetTemplate(ctx, templateID)
    if err != nil {
        return nil, err
    }

    // 2. Create instance
    instance := &ChecklistInstance{
        ID:         NewAppID(),
        TemplateID: templateID,
        UserID:     userID,
        EventID:    eventID,
        ContentID:  contentID,
        Type:       template.Type,
        Status:     ChecklistStatusPending,
        Items:      []ChecklistInstanceItem{},
        StartedAt:  time.Now(),
    }

    // 3. Execute each item
    for _, templateItem := range template.Items {
        result, err := s.executeItem(ctx, templateItem, userID, eventID, contentID)
        if err != nil {
            return nil, err
        }
        instance.Items = append(instance.Items, *result)
    }

    // 4. Calculate score
    instance.TotalScore = s.calculateScore(instance.Items)
    instance.PassThreshold = template.PassThreshold
    instance.Passed = instance.TotalScore >= instance.PassThreshold
    instance.Status = ChecklistStatusCompleted
    instance.CompletedAt = timePtr(time.Now())

    // 5. Save instance
    err = s.repo.SaveInstance(ctx, instance)
    if err != nil {
        return nil, err
    }

    // 6. Handle failures
    if !instance.Passed {
        err = s.handleFailure(ctx, instance)
        if err != nil {
            return nil, err
        }
    }

    return instance, nil
}

// Execute single checklist item
func (s *ChecklistService) executeItem(
    ctx context.Context,
    item ChecklistTemplateItem,
    userID AppID,
    eventID *AppID,
    contentID *AppID,
) (*ChecklistInstanceItem, error) {

    result := &ChecklistInstanceItem{
        ItemID:    item.ID,
        Question:  item.Question,
        Checked:   false,
        Passed:    false,
        Score:     0,
        CheckedAt: time.Now(),
    }

    switch item.CheckType {
    case CheckTypeSystem:
        // Auto-check
        passed, evidence, err := s.validator.Validate(ctx, item.ValidationRule, userID, eventID, contentID)
        if err != nil {
            return nil, err
        }

        result.Checked = true
        result.Passed = passed
        result.Score = getScore(passed, item.Weight)
        result.CheckedBy = CheckTypeSystem
        result.Evidence = evidence

        // If AI check
        if item.AutomationLevel == AutomationLevelAI {
            aiResult, err := s.aiService.Check(ctx, item, contentID)
            if err != nil {
                return nil, err
            }

            result.AIConfidence = aiResult.Confidence
            result.RequiresHumanReview = aiResult.Confidence < 0.95
            result.Evidence = aiResult.Evidence
        }

    case CheckTypeInfluencer:
        // Manual check - wait for user input
        result.Checked = false
        result.CheckedBy = CheckTypeInfluencer

    case CheckTypeAdmin:
        // Manual check - wait for admin input
        result.Checked = false
        result.CheckedBy = CheckTypeAdmin
    }

    // Set failure details
    if !result.Passed && result.Checked {
        result.FailureReason = item.FailureMessage
    }

    return result, nil
}

// Validation functions
func (s *ChecklistService) calculateScore(items []ChecklistInstanceItem) int {
    totalWeight := 0
    earnedWeight := 0

    for _, item := range items {
        totalWeight += item.Weight
        if item.Passed {
            earnedWeight += item.Weight
        }
    }

    if totalWeight == 0 {
        return 0
    }

    return (earnedWeight * 100) / totalWeight
}
```

### 6.3 Frontend Implementation

**React Component: Participation Checklist Modal**

```tsx
// frontend/src/components/Checklist/ParticipationChecklistModal.tsx

import React, { useState, useEffect } from 'react';
import { Modal, Progress, Alert, Checkbox } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

interface ChecklistItem {
  id: string;
  order: number;
  question: string;
  required: boolean;
  checkType: 'influencer' | 'system' | 'admin';
  weight: number;
  helpText?: string;

  // Result
  checked: boolean;
  passed: boolean;
  score: number;
  failureReason?: string;
}

interface ParticipationChecklistModalProps {
  visible: boolean;
  eventId: string;
  onComplete: (passed: boolean, instanceId: string) => void;
  onCancel: () => void;
}

export const ParticipationChecklistModal: React.FC<ParticipationChecklistModalProps> = ({
  visible,
  eventId,
  onComplete,
  onCancel
}) => {
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<ChecklistItem[]>([]);
  const [totalScore, setTotalScore] = useState(0);
  const [passThreshold, setPassThreshold] = useState(80);

  useEffect(() => {
    if (visible) {
      loadChecklist();
    }
  }, [visible, eventId]);

  const loadChecklist = async () => {
    setLoading(true);
    try {
      // Call API to execute checklist
      const response = await fetch(`/api/checklist/participation/${eventId}`, {
        method: 'POST'
      });

      const data = await response.json();

      setItems(data.items);
      setTotalScore(data.totalScore);
      setPassThreshold(data.passThreshold);

    } catch (error) {
      console.error('Failed to load checklist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInfluencerCheck = (itemId: string, checked: boolean) => {
    setItems(prevItems =>
      prevItems.map(item =>
        item.id === itemId
          ? { ...item, checked, passed: checked, score: checked ? item.weight : 0 }
          : item
      )
    );

    // Recalculate score
    const newScore = calculateScore(items);
    setTotalScore(newScore);
  };

  const calculateScore = (items: ChecklistItem[]) => {
    const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
    const earnedWeight = items.reduce((sum, item) => sum + (item.passed ? item.weight : 0), 0);
    return Math.round((earnedWeight / totalWeight) * 100);
  };

  const canProceed = () => {
    // All required items must be passed
    const requiredItems = items.filter(item => item.required);
    const allRequiredPassed = requiredItems.every(item => item.passed);

    // Total score must meet threshold
    const scorePass = totalScore >= passThreshold;

    return allRequiredPassed && scorePass;
  };

  const handleSubmit = async () => {
    if (!canProceed()) return;

    setLoading(true);
    try {
      // Update influencer checks
      await fetch(`/api/checklist/participation/${eventId}/update`, {
        method: 'PATCH',
        body: JSON.stringify({
          items: items.filter(item => item.checkType === 'influencer')
        })
      });

      onComplete(true, 'instance_id_here');
    } catch (error) {
      console.error('Failed to submit checklist:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = (item: ChecklistItem) => {
    const icon = item.passed ? (
      <CheckCircleOutlined style={{ color: '#52c41a' }} />
    ) : item.checked ? (
      <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
    ) : (
      <ExclamationCircleOutlined style={{ color: '#faad14' }} />
    );

    return (
      <div key={item.id} className="checklist-item" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start' }}>
          <div style={{ marginRight: 8, marginTop: 4 }}>{icon}</div>

          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 500 }}>
              {item.question}
              {item.required && <span style={{ color: 'red' }}> *</span>}
              <span style={{ color: '#999', fontSize: 12, marginLeft: 8 }}>
                ({item.weight} điểm)
              </span>
            </div>

            {item.helpText && (
              <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                💡 {item.helpText}
              </div>
            )}

            {item.failureReason && !item.passed && (
              <Alert
                message={item.failureReason}
                type="error"
                style={{ marginTop: 8 }}
                showIcon
              />
            )}

            {item.checkType === 'influencer' && !item.checked && (
              <Checkbox
                style={{ marginTop: 8 }}
                onChange={(e) => handleInfluencerCheck(item.id, e.target.checked)}
              >
                Tôi xác nhận
              </Checkbox>
            )}

            {item.checkType === 'system' && item.checked && (
              <div style={{ marginTop: 8, fontSize: 12, color: item.passed ? '#52c41a' : '#ff4d4f' }}>
                {item.passed ? '✓ Đã kiểm tra tự động - Đạt' : '✗ Đã kiểm tra tự động - Không đạt'}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const groupedItems = items.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {} as Record<string, ChecklistItem[]>);

  return (
    <Modal
      title="Checklist tham gia Campaign"
      visible={visible}
      onCancel={onCancel}
      width={700}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Hủy
        </Button>,
        <Button
          key="submit"
          type="primary"
          onClick={handleSubmit}
          disabled={!canProceed()}
          loading={loading}
        >
          Tham gia Campaign
        </Button>
      ]}
    >
      <div style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 8 }}>
          Điểm số: <strong>{totalScore}/100</strong>
          {' '}(Yêu cầu tối thiểu: {passThreshold}/100)
        </div>
        <Progress
          percent={totalScore}
          status={totalScore >= passThreshold ? 'success' : 'exception'}
        />
      </div>

      {totalScore < passThreshold && (
        <Alert
          message="Chưa đủ điều kiện tham gia"
          description="Vui lòng hoàn thành các mục bắt buộc (⭐) để tham gia campaign"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <div style={{ maxHeight: 500, overflowY: 'auto' }}>
        {Object.entries(groupedItems).map(([category, categoryItems]) => (
          <div key={category} style={{ marginBottom: 24 }}>
            <h4>{category}</h4>
            {categoryItems.map(renderItem)}
          </div>
        ))}
      </div>
    </Modal>
  );
};
```

---

## 7. API Specifications

### 7.1 Public API (Creator-facing)

**Execute Participation Checklist**
```http
POST /api/v1/checklist/participation/:eventId
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123456",
    "type": "participation",
    "items": [
      {
        "id": "item_001",
        "question": "Tài khoản TikTok đã kết nối?",
        "required": true,
        "checkType": "system",
        "weight": 15,
        "checked": true,
        "passed": true,
        "score": 15,
        "checkedBy": "system",
        "checkedAt": "2026-02-11T10:30:00Z"
      },
      // ... more items
    ],
    "totalScore": 95,
    "passThreshold": 95,
    "passed": true,
    "status": "completed"
  }
}
```

**Update Influencer Checks**
```http
PATCH /api/v1/checklist/participation/:instanceId
Authorization: Bearer {token}

Request Body:
{
  "items": [
    {
      "itemId": "item_009",
      "checked": true,
      "passed": true
    },
    {
      "itemId": "item_010",
      "checked": true,
      "passed": true
    }
  ]
}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123456",
    "totalScore": 100,
    "passed": true
  }
}
```

**Execute Pre-Submission Checklist**
```http
POST /api/v1/checklist/pre-submission/:eventId
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123457",
    "type": "pre_submission",
    "items": [ /* 14 self-check items */ ],
    "totalScore": 0,  // Not yet checked
    "passThreshold": 120
  }
}
```

**Submit Content with Validation Checklist**
```http
POST /api/v1/content
Authorization: Bearer {token}

Request Body:
{
  "eventId": "673f2a1b8e4c9a001f111111",
  "link": "https://www.tiktok.com/@user/video/1234567890",
  "preSubmissionChecklistId": "673f2a1b8e4c9a001f123457"
}

Response 201:
{
  "success": true,
  "data": {
    "contentId": "673f2a1b8e4c9a001f999999",
    "status": "waiting_approved",  // or "auto_rejected"
    "validationChecklist": {
      "instanceId": "673f2a1b8e4c9a001f123458",
      "totalScore": 175,
      "passed": true,
      "failedItems": []  // or array of failed items
    }
  }
}
```

**Get Checklist Failure Report**
```http
GET /api/v1/checklist/failures/:instanceId
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123458",
    "failedItems": [
      {
        "itemId": "item_205",
        "question": "Hashtag cá nhân #{user.Hashtag} có trong video?",
        "reason": "Hashtag #myhashtag not detected in title or description",
        "severity": "critical",
        "howToFix": "Thêm hashtag #myhashtag vào tiêu đề hoặc mô tả video",
        "tutorialUrl": "https://help.tcb.com/add-hashtag",
        "exampleGoodUrl": "https://content.tcb.com/example-123"
      }
    ],
    "autoActions": {
      "taskCreated": true,
      "taskId": "673f2a1b8e4c9a001f777777",
      "trainingEnrolled": false,
      "notificationSent": true
    },
    "nextSteps": [
      "1. Xem video hướng dẫn (2 phút)",
      "2. Chỉnh sửa mô tả video để thêm hashtag",
      "3. Submit lại nội dung"
    ],
    "estimatedFixTime": "10 phút"
  }
}
```

### 7.2 Admin API

**Get Admin Review Checklist**
```http
GET /api/v1/admin/checklist/review/:contentId
Authorization: Bearer {admin_token}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123459",
    "contentId": "673f2a1b8e4c9a001f999999",
    "type": "admin_review",
    "items": [
      {
        "id": "item_301",
        "question": "Chất lượng video đạt chuẩn?",
        "required": true,
        "checkType": "admin",
        "weight": 10,
        "aiAssist": {
          "type": "video_quality_analysis",
          "data": {
            "resolution": "1080p",
            "fps": 30,
            "bitrate": 5000
          }
        },
        "checked": false,
        "passed": null
      },
      {
        "id": "item_305",
        "question": "Logo Techcombank hiển thị rõ ràng?",
        "required": true,
        "weight": 15,
        "aiAssist": {
          "type": "logo_detection_result",
          "data": {
            "detected": true,
            "confidence": 0.92,
            "timeRange": "0:05-0:10",
            "position": "top-right",
            "boundingBox": [100, 50, 200, 150]
          }
        },
        "checked": false,
        "passed": null
      }
    ],
    "totalScore": 0,
    "passThreshold": 160
  }
}
```

**Submit Admin Review**
```http
POST /api/v1/admin/checklist/review/:instanceId/submit
Authorization: Bearer {admin_token}

Request Body:
{
  "items": [
    {
      "itemId": "item_301",
      "checked": true,
      "passed": true,
      "notes": "Video quality is excellent, 1080p HD"
    },
    {
      "itemId": "item_305",
      "checked": true,
      "passed": true,
      "notes": "Logo clearly visible at 0:05-0:10"
    },
    // ... 17 items total
  ],
  "decision": "approve" | "reject" | "escalate",
  "overallNotes": "Great content, meets all requirements"
}

Response 200:
{
  "success": true,
  "data": {
    "instanceId": "673f2a1b8e4c9a001f123459",
    "totalScore": 185,
    "passed": true,
    "decision": "approve",
    "contentStatus": "approved"  // Content status updated
  }
}
```

**Get Checklist Analytics**
```http
GET /api/v1/admin/checklist/analytics
Authorization: Bearer {admin_token}

Query Parameters:
  - type: participation | pre_submission | validation | admin_review
  - startDate: 2026-02-01
  - endDate: 2026-02-11
  - eventId: optional

Response 200:
{
  "success": true,
  "data": {
    "summary": {
      "totalInstances": 1250,
      "passRate": 78,  // 78%
      "avgScore": 82,
      "avgCompletionTime": 450  // seconds
    },
    "topFailedItems": [
      {
        "itemId": "item_206",
        "question": "TẤT CẢ hashtag campaign có trong video?",
        "failureRate": 0.35,  // 35% fail
        "totalFailed": 437
      },
      {
        "itemId": "item_207",
        "question": "Lượt xem đạt ngưỡng tối thiểu?",
        "failureRate": 0.28,
        "totalFailed": 350
      }
    ],
    "trends": [
      {
        "date": "2026-02-01",
        "passRate": 75
      },
      {
        "date": "2026-02-02",
        "passRate": 76
      },
      // ... daily trends
    ]
  }
}
```

### 7.3 Validation Rules Implementation

**File: `internal/service/checklist_validator.go`**

```go
package service

type ChecklistValidator struct {
    db         *mongo.Database
    userRepo   *UserRepository
    eventRepo  *EventRepository
    contentRepo *ContentRepository
}

func (v *ChecklistValidator) Validate(
    ctx context.Context,
    rule *ValidationRule,
    userID AppID,
    eventID *AppID,
    contentID *AppID,
) (bool, *Evidence, error) {

    switch rule.Type {

    // Social account validation
    case "social_account_connected":
        platform := rule.Params["platform"].(string)
        user, _ := v.userRepo.FindByID(ctx, userID)

        switch platform {
        case "tiktok":
            return user.Tiktok != nil, &Evidence{
                Type: "social_account_data",
                Data: user.Tiktok,
            }, nil
        case "facebook":
            return user.Facebook != nil, &Evidence{
                Type: "social_account_data",
                Data: user.Facebook,
            }, nil
        // ... other platforms
        }

    // Blacklist check
    case "user_not_banned":
        user, _ := v.userRepo.FindByID(ctx, userID)
        return !user.Banned, &Evidence{
            Type: "user_status",
            Data: map[string]interface{}{
                "banned": user.Banned,
                "reason": user.BannedReason,
            },
        }, nil

    // Min followers check
    case "min_followers":
        platform := rule.Params["platform"].(string)
        minFollowers := rule.Params["minFollowers"].(int)
        user, _ := v.userRepo.FindByID(ctx, userID)

        var actualFollowers int64
        switch platform {
        case "tiktok":
            if user.Tiktok != nil {
                actualFollowers = user.Tiktok.FollowerCount
            }
        case "facebook":
            if user.Facebook != nil {
                actualFollowers = user.Facebook.FollowersCount
            }
        }

        return actualFollowers >= int64(minFollowers), &Evidence{
            Type: "follower_count",
            Data: map[string]interface{}{
                "platform": platform,
                "actual":   actualFollowers,
                "required": minFollowers,
            },
        }, nil

    // Hashtag validation
    case "hashtag_present":
        hashtag := rule.Params["hashtag"].(string)
        searchIn := rule.Params["searchIn"].([]string)
        content, _ := v.contentRepo.FindByID(ctx, *contentID)

        for _, field := range searchIn {
            var text string
            switch field {
            case "content.Title":
                text = content.Title
            case "content.Description":
                text = content.Desc
            }

            if strings.Contains(strings.ToLower(text), strings.ToLower(hashtag)) {
                return true, &Evidence{
                    Type: "hashtag_match",
                    Data: map[string]interface{}{
                        "hashtag":   hashtag,
                        "foundIn":   field,
                        "text":      text,
                    },
                }, nil
            }
        }

        return false, &Evidence{
            Type: "hashtag_not_found",
            Data: map[string]interface{}{
                "hashtag": hashtag,
                "searchedIn": searchIn,
            },
        }, nil

    // Min views check
    case "min_views":
        currentViews := rule.Params["currentViews"].(float64)
        minViews := rule.Params["minViews"].(float64)

        passed := currentViews >= minViews

        return passed, &Evidence{
            Type: "metrics_check",
            Data: map[string]interface{}{
                "metric":   "views",
                "actual":   currentViews,
                "required": minViews,
                "passed":   passed,
            },
        }, nil

    // Engagement rate check
    case "min_engagement_rate":
        engagement := rule.Params["engagement"].(float64)
        minEngagement := rule.Params["minEngagement"].(float64)

        passed := engagement >= minEngagement

        return passed, &Evidence{
            Type: "metrics_check",
            Data: map[string]interface{}{
                "metric":   "engagement",
                "actual":   engagement,
                "required": minEngagement,
                "passed":   passed,
            },
        }, nil

    // Content age check
    case "content_age_valid":
        publishedAt := rule.Params["publishedAt"].(time.Time)
        maxAgeDays := rule.Params["maxAgeDays"].(float64)
        now := time.Now()

        ageDays := now.Sub(publishedAt).Hours() / 24
        passed := ageDays <= maxAgeDays

        return passed, &Evidence{
            Type: "content_age_check",
            Data: map[string]interface{}{
                "publishedAt": publishedAt,
                "ageDays":     ageDays,
                "maxAgeDays":  maxAgeDays,
                "passed":      passed,
            },
        }, nil

    default:
        return false, nil, errors.New("Unknown validation rule: " + rule.Type)
    }

    return false, nil, nil
}
```

---

## 8. Deployment Guide

### 8.1 Phase 1: Database Setup (Week 1)

**Step 1: Backup existing data**
```bash
mongodump --uri="mongodb://localhost:27017/techcombank" --out=/backup/pre-checklist
```

**Step 2: Run migrations**
```bash
cd backend/migrations
go run checklist_migration.go
```

**Step 3: Seed templates**
```bash
cd backend/scripts
go run seed_checklist_templates.go
```

**Step 4: Verify**
```bash
mongo techcombank --eval "db.checklist_templates.count()"
# Should return: 4 (4 templates)
```

### 8.2 Phase 2: Backend Deployment (Week 2)

**Step 1: Deploy new Go services**
```bash
# Build binaries
cd backend
make build

# Deploy to staging
scp dist/public staging:/opt/tcb/api/
scp dist/admin staging:/opt/tcb/api/

# Restart services
ssh staging "systemctl restart tcb-public-api"
ssh staging "systemctl restart tcb-admin-api"
```

**Step 2: Configure AI APIs**
```bash
# Set environment variables
export GOOGLE_VISION_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export GOOGLE_SPEECH_TO_TEXT_API_KEY="your_key"

# Test AI services
curl -X POST http://localhost:3001/api/v1/checklist/test-ai
```

**Step 3: Deploy Asynq workers for AI checks**
```bash
# Start worker for AI processing
cd backend
go run cmd/worker/main.go --queue=ai_checklist

# Monitor queue
redis-cli
> LLEN asynq:default:ai_checklist
```

### 8.3 Phase 3: Frontend Deployment (Week 3)

**Step 1: Build frontend**
```bash
cd frontend
npm run build

cd admin
npm run build
```

**Step 2: Deploy to CDN**
```bash
# Upload to S3/CloudFront
aws s3 sync frontend/dist s3://tcb-frontend/
aws cloudfront create-invalidation --distribution-id E123456 --paths "/*"

aws s3 sync admin/dist s3://tcb-admin/
aws cloudfront create-invalidation --distribution-id E789012 --paths "/*"
```

**Step 3: Enable feature flag**
```javascript
// Feature flag in frontend config
const FEATURE_FLAGS = {
  CHECKLIST_PARTICIPATION: true,
  CHECKLIST_PRE_SUBMISSION: true,
  CHECKLIST_VALIDATION: true,
  CHECKLIST_ADMIN_REVIEW: false  // Rollout gradually
};
```

### 8.4 Phase 4: Gradual Rollout (Week 4)

**Step 1: Enable for 10% users (A/B test)**
```go
// Backend feature flag
func isChecklistEnabled(userID AppID) bool {
    // Hash userID to get consistent bucketing
    hash := hashUserID(userID)
    return (hash % 100) < 10  // 10% rollout
}
```

**Step 2: Monitor metrics**
```sql
-- Query checklist analytics
SELECT
    type,
    COUNT(*) as total_instances,
    AVG(totalScore) as avg_score,
    SUM(CASE WHEN passed THEN 1 ELSE 0 END) / COUNT(*) * 100 as pass_rate,
    AVG(TIMESTAMPDIFF(SECOND, startedAt, completedAt)) as avg_completion_time
FROM checklist_instances
WHERE createdAt >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY type;
```

**Step 3: Increase to 50%, then 100%**
```go
// Week 2: 50%
return (hash % 100) < 50

// Week 3: 100%
return true
```

### 8.5 Monitoring & Alerts

**CloudWatch/Grafana Dashboard Metrics:**
```yaml
Metrics to track:
  - checklist_execution_total (by type)
  - checklist_execution_duration_seconds
  - checklist_pass_rate (by type)
  - checklist_failure_rate_by_item
  - ai_check_duration_seconds
  - ai_check_confidence_distribution

Alerts:
  - Pass rate < 70% → Investigate checklist too strict
  - Avg completion time > 300s → Performance issue
  - AI check duration > 60s → AI API slow
  - Failure rate for specific item > 50% → Item unclear or too strict
```

**Log Aggregation (Elasticsearch/Loki):**
```json
{
  "level": "info",
  "msg": "Checklist executed",
  "instanceId": "673f2a1b8e4c9a001f123456",
  "type": "participation",
  "userId": "user_123",
  "eventId": "event_456",
  "totalScore": 95,
  "passed": true,
  "duration_ms": 1250,
  "failed_items": []
}
```

---

## 9. Success Metrics & KPIs

### 9.1 Operational Metrics

**Target (3 months after launch):**
- ✅ Checklist completion rate: >85%
- ✅ Auto-check accuracy: >90%
- ✅ Manual review reduction: -50%
- ✅ Average completion time: <5 minutes
- ✅ Creator satisfaction with checklist: >4/5

### 9.2 Quality Metrics

**Target:**
- ✅ First-time approval rate: >70% (up from ~40%)
- ✅ Repeat submission rate: <15% (down from ~40%)
- ✅ Content rejection due to missing hashtag: <5% (down from ~35%)
- ✅ Admin review time per content: <2 min (down from ~5 min)

### 9.3 Business Impact

**Financial:**
- ✅ Admin FTE saved: 2.5 FTE/month (~$10K/month saved)
- ✅ Campaign cycle time: -30% (faster time-to-market)
- ✅ Creator churn rate: -20% (better experience)

---

## 10. Future Enhancements

### Phase 2 Features (Month 4-6)

**1. ML-based Smart Checklists**
- Predictive checklist generation based on historical data
- Auto-adjust pass thresholds based on creator tier performance
- Anomaly detection for unusual patterns

**2. Checklist Versioning & A/B Testing**
- Create checklist variants for testing
- Compare performance of different checklist designs
- Optimize based on data

**3. Multi-language Support**
- Vietnamese + English checklists
- Auto-translation for international campaigns

**4. Advanced AI Checks**
- Video sentiment analysis
- Brand safety scoring
- Competitor mention detection
- Product feature verification

**5. Creator Training Integration**
- Auto-generate personalized training paths
- Micro-courses based on failed checklist items
- Certification badges for checklist mastery

---

## 11. Appendix

### A. Checklist Template JSON Examples

**Participation Checklist Template:**
```json
{
  "_id": "673f2a1b8e4c9a001f100001",
  "name": "Campaign Participation Checklist v1.0",
  "version": "1.0.0",
  "type": "participation",
  "campaignType": null,
  "platform": null,
  "creatorTier": null,
  "items": [
    {
      "id": "item_001",
      "order": 1,
      "category": "eligibility",
      "question": "Tài khoản TikTok/Facebook/Instagram đã kết nối?",
      "description": "Cần kết nối tài khoản để tham gia campaign",
      "required": true,
      "checkType": "system",
      "automationLevel": "auto",
      "validationRule": {
        "type": "social_account_connected",
        "params": {
          "platforms": ["tiktok", "facebook", "instagram"]
        }
      },
      "weight": 15,
      "passCondition": "boolean_true",
      "failureAction": "block",
      "failureMessage": "Vui lòng kết nối tài khoản {platform} trước khi tham gia",
      "helpText": "Vào Cài đặt > Tài khoản xã hội > Kết nối {platform}",
      "tutorialUrl": "https://help.tcb.com/connect-social",
      "exampleGoodUrl": null,
      "exampleBadUrl": null
    }
    // ... 12 more items
  ],
  "passThreshold": 95,
  "status": "active",
  "createdAt": "2026-02-11T00:00:00Z",
  "updatedAt": "2026-02-11T00:00:00Z",
  "createdBy": "admin_001"
}
```

### B. Error Codes

```yaml
ERR_CHECKLIST_001: "Checklist template not found"
ERR_CHECKLIST_002: "Checklist instance not found"
ERR_CHECKLIST_003: "Invalid validation rule type"
ERR_CHECKLIST_004: "Required item not checked"
ERR_CHECKLIST_005: "Score below pass threshold"
ERR_CHECKLIST_006: "AI service unavailable"
ERR_CHECKLIST_007: "Content Catcher API failed"
ERR_CHECKLIST_008: "Invalid checklist type"
ERR_CHECKLIST_009: "Checklist already completed"
ERR_CHECKLIST_010: "Unauthorized to update checklist"
```

### C. Testing Checklist

**Unit Tests:**
- [ ] Validation rule: social_account_connected
- [ ] Validation rule: hashtag_present
- [ ] Validation rule: min_views
- [ ] Validation rule: min_engagement_rate
- [ ] Validation rule: content_age_valid
- [ ] Score calculation logic
- [ ] Pass threshold logic
- [ ] Failure report generation

**Integration Tests:**
- [ ] Execute participation checklist end-to-end
- [ ] Execute pre-submission checklist end-to-end
- [ ] Execute validation checklist with AI checks
- [ ] Execute admin review checklist
- [ ] Update influencer checks
- [ ] Generate failure report with auto-actions
- [ ] Checklist analytics API

**E2E Tests (Playwright/Cypress):**
- [ ] Creator participates in campaign with checklist
- [ ] Creator submits content with pre-submission checklist
- [ ] Content auto-rejected with detailed failure report
- [ ] Admin reviews content with admin checklist
- [ ] Admin approves content
- [ ] Analytics dashboard displays checklist metrics

---

## Document Summary

**Total Checklist Items Defined:** 68 items
- Participation: 13 items
- Pre-Submission: 14 items
- Validation: 15 items
- Admin Review: 17 items

**Total Weight:** 670 points across all checklists

**Automation Coverage:**
- System Auto-Check: 42 items (62%)
- Influencer Self-Check: 14 items (21%)
- Admin Manual Check: 17 items (25%)

**AI Integration Points:**
- Logo detection (Google Vision API)
- Brand mention (Google Speech-to-Text)
- Content moderation (OpenAI Moderation API)
- Video quality analysis (Custom ML model)
- Fraud detection scoring (Custom ML model)

**Expected Impact:**
- Manual review reduction: -50%
- First-time approval rate: +30%
- Creator satisfaction: +40%
- Admin time saved: 2.5 FTE/month
- Campaign cycle time: -30%

---

**Document Version:** 1.0
**Last Updated:** 2026-02-11
**Status:** Production-Ready
**Ready for:** Implementation Sprint

**Next Steps:**
1. Review with stakeholders (AccessTrade + Techcombank)
2. Approve budget for AI APIs (~$500/month)
3. Assign development team (2 backend + 1 frontend devs)
4. Kick off implementation sprint (4-week timeline)

---

*Generated for TCB Creator Platform - Checklist System Production Specification*
