# Participation Requirements - Configuration Examples

**Date:** 2026-02-07

---

## Example 1: Techcombank Facebook Post Campaign

### Requirements Definition

```json
{
  "event": {
    "id": "event_techcombank_fb_post_001",
    "name": "Techcombank Facebook Post Campaign",
    "participationRequirements": {
      "enabled": true,
      "requirements": [
        {
          "type": "account_age",
          "title": "Tham gia ≥3 tháng",
          "description": "Tài khoản ViewBoost của bạn phải tồn tại ít nhất 3 tháng",
          "validationLevel": "auto",
          "validation": {
            "minMonths": 3
          },
          "required": true,
          "order": 1,
          "helpLink": "/help/account-age"
        },
        {
          "type": "invitation_code",
          "title": "Nhập mã mời",
          "description": "Mã mời từ Techcombank hoặc partner",
          "validationLevel": "auto",
          "validation": {
            "codeRequired": true,
            "codePattern": "^TCB-EVENT01-[A-Z0-9]{5}$"
          },
          "required": true,
          "order": 2,
          "helpLink": "/help/invitation-code"
        },
        {
          "type": "facebook_profile",
          "title": "Liên kết & xác thực Facebook",
          "description": "Tài khoản Facebook cá nhân hoặc Fanpage",
          "validationLevel": "manual",
          "required": true,
          "order": 3,
          "helpLink": "/help/facebook-verification"
        },
        {
          "type": "facebook_followers",
          "title": "Fanpage ≥1,000 followers",
          "description": "Số lượng bạn bè (tài khoản cá nhân) hoặc followers (fanpage)",
          "validationLevel": "hybrid",
          "validation": {
            "minFollowers": 1000
          },
          "required": true,
          "order": 4,
          "helpLink": "/help/facebook-followers"
        },
        {
          "type": "authentic_posts",
          "title": "Có bài đăng thật",
          "description": "Cấm spam share link không chuẩn mục. Phải có bài đăng chất lượng trên trang cá nhân.",
          "validationLevel": "manual",
          "required": true,
          "order": 5,
          "helpLink": "/help/authentic-posts"
        }
      ]
    }
  }
}
```

---

## Example 2: VinFast TikTok Campaign (Less Strict)

### Requirements Definition

```json
{
  "event": {
    "id": "event_vinfast_tiktok_001",
    "name": "VinFast TikTok Video Campaign",
    "participationRequirements": {
      "enabled": true,
      "requirements": [
        {
          "type": "account_age",
          "title": "Tham gia ≥1 tháng",
          "description": "Tài khoản ViewBoost của bạn phải tồn tại ít nhất 1 tháng",
          "validationLevel": "auto",
          "validation": {
            "minMonths": 1
          },
          "required": true,
          "order": 1
        },
        {
          "type": "tiktok_account",
          "title": "Liên kết TikTok",
          "description": "Kết nối tài khoản TikTok của bạn",
          "validationLevel": "auto",
          "required": true,
          "order": 2
        },
        {
          "type": "tiktok_followers",
          "title": "TikTok ≥500 followers",
          "description": "Tài khoản TikTok cần có ít nhất 500 followers",
          "validationLevel": "hybrid",
          "validation": {
            "minFollowers": 500
          },
          "required": true,
          "order": 3
        },
        {
          "type": "invitation_code",
          "title": "Mã mời (không bắt buộc)",
          "description": "Nếu bạn có mã mời từ VinFast, hãy nhập để được ưu tiên duyệt",
          "validationLevel": "auto",
          "validation": {
            "codeRequired": false
          },
          "required": false,
          "order": 4
        }
      ]
    }
  }
}
```

---

## Example 3: Ambassador General Event (Open)

### Requirements Definition

```json
{
  "event": {
    "id": "event_ambassador_general_001",
    "name": "Ambassador General Campaign",
    "participationRequirements": {
      "enabled": true,
      "requirements": [
        {
          "type": "account_age",
          "title": "Tham gia ≥7 ngày",
          "description": "Tài khoản mới cần có ít nhất 7 ngày để tham gia",
          "validationLevel": "auto",
          "validation": {
            "minDays": 7
          },
          "required": true,
          "order": 1
        },
        {
          "type": "email_verified",
          "title": "Xác thực email",
          "description": "Email của bạn cần được xác thực",
          "validationLevel": "auto",
          "required": true,
          "order": 2
        },
        {
          "type": "social_linked",
          "title": "Liên kết ít nhất 1 mạng xã hội",
          "description": "Facebook, TikTok, Instagram, hoặc YouTube",
          "validationLevel": "auto",
          "validation": {
            "minLinkedAccounts": 1,
            "acceptedPlatforms": ["facebook", "tiktok", "instagram", "youtube"]
          },
          "required": true,
          "order": 3
        }
      ]
    }
  }
}
```

---

## Example 4: VIP Invite-Only Event

### Requirements Definition

```json
{
  "event": {
    "id": "event_vip_exclusive_001",
    "name": "VIP Exclusive Campaign",
    "participationRequirements": {
      "enabled": true,
      "requirements": [
        {
          "type": "invitation_code",
          "title": "Mã mời VIP",
          "description": "Chỉ dành cho influencers được mời riêng",
          "validationLevel": "auto",
          "validation": {
            "codeRequired": true,
            "codePattern": "^VIP-2026-[A-Z0-9]{8}$",
            "oneTimeUse": true
          },
          "required": true,
          "order": 1
        },
        {
          "type": "kyc_verified",
          "title": "Xác thực danh tính (KYC)",
          "description": "CMND/CCCD đã được xác thực",
          "validationLevel": "manual",
          "required": true,
          "order": 2
        },
        {
          "type": "minimum_followers_total",
          "title": "Tổng followers ≥10,000",
          "description": "Tổng followers trên tất cả các nền tảng (FB + TikTok + IG + YT)",
          "validationLevel": "hybrid",
          "validation": {
            "minTotalFollowers": 10000,
            "countPlatforms": ["facebook", "tiktok", "instagram", "youtube"]
          },
          "required": true,
          "order": 3
        },
        {
          "type": "content_quality_score",
          "title": "Điểm chất lượng content ≥4.0/5.0",
          "description": "Đánh giá từ các campaign trước đó",
          "validationLevel": "auto",
          "validation": {
            "minScore": 4.0,
            "basedOnPastCampaigns": 3
          },
          "required": true,
          "order": 4
        }
      ]
    }
  }
}
```

---

## Validation Level Definitions

### Auto-Validated
- System tự động check ngay lập tức
- No human intervention needed
- Examples: Account age, invitation code format, email verified

### Manual-Validated
- Requires admin review
- Human judgment needed
- Examples: Profile quality, authentic posts, KYC verification

### Hybrid-Validated
- Auto-check first (via API call)
- Manual override if API fails or borderline cases
- Examples: Follower count (FB Graph API), content quality score

---

## Admin Configuration UI (Mock)

```
┌────────────────────────────────────────────────────────────┐
│  Campaign: Techcombank Facebook Post                      │
│  Participation Requirements Configuration                  │
└────────────────────────────────────────────────────────────┘

☑ Enable participation requirements

┌────────────────────────────────────────────────────────────┐
│  Requirement #1                                             │
├────────────────────────────────────────────────────────────┤
│  Type: [Account Age ▼]                                     │
│  Title: Tham gia ≥3 tháng                                  │
│  Description: ________________________________             │
│  Validation Level: [Auto ▼]                                │
│                                                             │
│  Validation Rules:                                          │
│  Min Months: [3]                                           │
│                                                             │
│  ☑ Required   Order: [1]                                   │
│  Help Link: /help/account-age                              │
│                                                             │
│  [Remove Requirement]                                       │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Requirement #2                                             │
├────────────────────────────────────────────────────────────┤
│  Type: [Facebook Followers ▼]                              │
│  Title: Fanpage ≥1,000 followers                           │
│  Description: ________________________________             │
│  Validation Level: [Hybrid ▼]                              │
│                                                             │
│  Validation Rules:                                          │
│  Min Followers: [1000]                                     │
│  Grace Period: [-10%] (allow 900 followers)                │
│  Re-check Frequency: [Daily ▼]                             │
│                                                             │
│  ☑ Required   Order: [2]                                   │
│  Help Link: /help/facebook-followers                       │
│                                                             │
│  [Remove Requirement]                                       │
└────────────────────────────────────────────────────────────┘

[+ Add Requirement]

[Save Configuration]  [Cancel]
```

---

## User-Facing Checklist UI (Mock)

```
┌────────────────────────────────────────────────────────────┐
│  Campaign: Techcombank Facebook Post Event                 │
│  Thưởng: 150,000đ/bài (tối đa 3 bài)                      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  📋 Điều kiện tham gia (3/5 đạt)                            │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Tham gia ≥3 tháng                                       │
│     ✓ Tài khoản của bạn: 2 năm                             │
│     Tự động kiểm tra                                        │
│                                                             │
│  ✅ Nhập mã mời                                             │
│     ✓ Mã TCB-EVENT01-A3X9K đã xác thực                     │
│     Tự động kiểm tra                                        │
│                                                             │
│  ⏳ Liên kết & xác thực Facebook                            │
│     ⚠ Đang chờ admin duyệt hồ sơ                           │
│     Thời gian duyệt: 1-2 ngày làm việc                     │
│     [Xem hồ sơ đã gửi]                                     │
│                                                             │
│  ⏸️ Fanpage ≥1,000 followers                                │
│     ⓘ Sẽ kiểm tra sau khi hồ sơ được duyệt                 │
│                                                             │
│  ⏸️ Có bài đăng thật (không spam)                           │
│     ⓘ Admin sẽ kiểm tra trong quá trình duyệt              │
│                                                             │
├────────────────────────────────────────────────────────────┤
│  ⏳ Trạng thái: Đang chờ duyệt hồ sơ                        │
│                                                             │
│  Sau khi hồ sơ được duyệt, bạn có thể bắt đầu              │
│  gửi bài viết để nhận thưởng.                              │
│                                                             │
│  [Hủy đăng ký]                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Database Schema Example (MongoDB)

### Event Collection
```javascript
{
  "_id": ObjectId("..."),
  "name": "Techcombank Facebook Post Campaign",
  "participationRequirements": {
    "enabled": true,
    "version": 1, // Increment when requirements change
    "requirements": [
      {
        "type": "account_age",
        "title": "Tham gia ≥3 tháng",
        "description": "Tài khoản ViewBoost của bạn phải tồn tại ít nhất 3 tháng",
        "validationLevel": "auto",
        "validation": {
          "minMonths": 3
        },
        "required": true,
        "order": 1,
        "helpLink": "/help/account-age"
      },
      {
        "type": "facebook_followers",
        "title": "Fanpage ≥1,000 followers",
        "description": "Số lượng bạn bè (tài khoản cá nhân) hoặc followers (fanpage)",
        "validationLevel": "hybrid",
        "validation": {
          "minFollowers": 1000,
          "gracePeriodPercent": 10, // Allow -10% (900 followers)
          "recheckFrequency": "daily"
        },
        "required": true,
        "order": 4
      }
    ]
  },
  // ... other event fields
}
```

### User-Events Collection
```javascript
{
  "_id": ObjectId("..."),
  "user": ObjectId("..."),
  "event": ObjectId("..."),
  "partner": ObjectId("..."),
  "participationStatus": {
    "status": "approved", // "not_started" | "pending_review" | "approved" | "rejected"
    "requirementsVersion": 1, // Locked version when approved
    "lockedRequirements": [ /* snapshot of requirements */ ],
    "requirements": {
      "account_age": {
        "type": "account_age",
        "status": "passed",
        "checkedAt": ISODate("2026-02-07T10:00:00Z"),
        "autoCheckResult": {
          "success": true,
          "data": {
            "accountAgeMonths": 24,
            "required": 3
          }
        },
        "value": 24,
        "required": 3
      },
      "facebook_followers": {
        "type": "facebook_followers",
        "status": "passed",
        "checkedAt": ISODate("2026-02-07T10:30:00Z"),
        "autoCheckResult": {
          "success": true,
          "data": {
            "followers": 1250,
            "source": "facebook_graph_api"
          }
        },
        "manualCheckAt": null,
        "manualCheckBy": null,
        "value": 1250,
        "required": 1000,
        "notes": ""
      },
      "facebook_profile": {
        "type": "facebook_profile",
        "status": "passed",
        "checkedAt": null,
        "autoCheckResult": null,
        "manualCheckAt": ISODate("2026-02-07T11:00:00Z"),
        "manualCheckBy": ObjectId("admin_id"),
        "notes": "Profile hợp lệ, có bài đăng chất lượng"
      }
    },
    "submittedAt": ISODate("2026-02-07T09:00:00Z"),
    "approvedAt": ISODate("2026-02-07T11:00:00Z"),
    "approvedBy": ObjectId("admin_id"),
    "reviewNotes": "Tất cả điều kiện đạt yêu cầu"
  },
  "canSubmitContent": true,
  "statistic": { /* ... */ },
  "createdAt": ISODate("2026-02-07T09:00:00Z"),
  "updatedAt": ISODate("2026-02-07T11:00:00Z")
}
```

### Participation-Reviews Collection (NEW)
```javascript
{
  "_id": ObjectId("..."),
  "userEvent": ObjectId("..."),
  "user": ObjectId("..."),
  "event": ObjectId("..."),
  "partner": ObjectId("..."),
  "status": "approved", // "pending" | "approved" | "rejected" | "need_more_info"

  // Submission data
  "facebookProfileUrl": "https://facebook.com/username",
  "proofScreenshots": [
    "https://media.viewboost.vn/proof/user123_profile.png",
    "https://media.viewboost.vn/proof/user123_posts.png"
  ],
  "invitationCode": "TCB-EVENT01-A3X9K",

  // Review data
  "reviewedAt": ISODate("2026-02-07T11:00:00Z"),
  "reviewedBy": ObjectId("admin_id"),
  "reviewNotes": "Profile OK, followers: 1,250",

  // Requirements snapshot at submission time
  "requirementsSnapshot": {
    "facebook_followers": {
      "type": "facebook_followers",
      "status": "pending",
      "value": null,
      "required": 1000
    },
    "facebook_profile": {
      "type": "facebook_profile",
      "status": "pending"
    }
  },

  "createdAt": ISODate("2026-02-07T09:00:00Z"),
  "updatedAt": ISODate("2026-02-07T11:00:00Z")
}
```

---

*Last Updated: 2026-02-07*
