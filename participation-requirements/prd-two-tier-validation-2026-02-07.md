# Product Requirements Document: Two-Tier Participation Validation System

**Project:** Ambassador Platform - Participation Requirements
**Date:** 07/02/2026
**Version:** 1.0
**Status:** Draft - Awaiting Approval
**Product Manager:** BMAD Creative Intelligence

**Repositories:**
- Backend: `accesstrade-projects/ambassabor/backend`
- Admin: `accesstrade-projects/ambassabor/admin`
- Frontend: `accesstrade-projects/ambassabor/frontend`

---

## Executive Summary

Hệ thống Two-Tier Participation Validation giải quyết vấn đề fraud rate cao (15%) và admin workload quá tải bằng cách tách validation thành 2 tiers:

1. **Tier 1 - Pre-Registration Eligibility:** Auto-check instant điều kiện cơ bản (account age, email/phone exists)
2. **Tier 2 - Post-Registration Validation:** Admin review chất lượng influencer (profile quality, follower count, authentic posts)

**Expected Business Impact:**
- Fraud rate: 15% → <5%
- Admin workload: Giảm 40%
- Support tickets: Giảm 50-60%
- ROI campaign: 150% → >200%
- Payment success rate: >95%

**Investment:**
- Development: 226M VND (one-time)
- Monthly operational: 10M VND
- Payback period: 4.5 months

---

## Table of Contents

1. [Business Objectives](#business-objectives)
2. [Success Metrics](#success-metrics)
3. [User Personas](#user-personas)
4. [Case Studies: Real-World Problem Scenarios](#case-studies-real-world-problem-scenarios)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Epics](#epics)
8. [High-Level User Stories](#high-level-user-stories)
9. [Key User Flows](#key-user-flows)
10. [Dependencies](#dependencies)
11. [Assumptions](#assumptions)
12. [Out of Scope](#out-of-scope)
13. [Open Questions](#open-questions)
14. [Traceability Matrix](#traceability-matrix)
15. [Prioritization Summary](#prioritization-summary)

---

## Business Objectives

### Primary Objectives

**OBJ-1: Giảm Fraud Rate**
- Current: ~15% fraud rate
- Target: <5% fraud rate
- Impact: Tiết kiệm 50M VND/tháng

**OBJ-2: Tăng Partner Trust**
- Target: Techcombank, VinFast confidence tăng
- Metric: Deal renewal rate >80%, deal size tăng 30%
- Impact: Dễ ký deals lớn hơn

**OBJ-3: Tối Ưu Admin Workload**
- Current: Review tất cả users (bao gồm không đủ điều kiện)
- Target: Chỉ review qualified users
- Impact: Admin workload giảm 40%

### Secondary Objectives

**OBJ-4: Compliance & Legal Protection**
- GDPR compliance (email/phone verified consent)
- Audit trail cho partner requirements

**OBJ-5: Scalability**
- Support growth từ 1,000 → 10,000 users/month
- Admin workload không tăng tỷ lệ thuận

---

## Success Metrics

### Registration Funnel
- **Landing → View Requirements:** >70%
- **View → Submit Application:** >60%
- **Submit → Approved:** >70% (30% reject rate acceptable)

### Quality Metrics
- **Fraud rate:** <5% (from 15%)
- **Support tickets:** <10% of users (from 25%)
- **Payment success rate:** >95%

### Operational Metrics
- **Admin review time:** <5 min/application (avg)
- **Review SLA:** 90% approved within 2 days
- **Queue size:** <100 pending applications at any time

### Business Metrics
- **Cost per qualified user:** <50k VND
- **ROI per campaign:** >200% (from 150%)
- **User retention (2nd campaign):** >30%

---

## Case Studies: Real-World Problem Scenarios

### Case Study 1: Techcombank Facebook Post Campaign (CURRENT PROBLEM)

**Bối cảnh:**
Techcombank muốn chạy campaign Facebook Post với yêu cầu strict về chất lượng influencer. Requirements từ product brief:

```
Facebook: Post trên trang cá nhân, fanpage >1,000 friends/followers
- Ngày tham gia ít nhất 3 tháng trước ngày triển khai chiến dịch
- Có bài đăng thật trên trang cá nhân (cấm spam share link không chuẩn mục)
- Chi phí: 150,000 VND/post (tối đa 3 post/camp)
```

**Vấn đề hiện tại:**
Creators submit bài viết TRƯỚC KHI kiểm tra điều kiện → Admin phải reject nhiều bài không đủ điều kiện → Bad UX + admin workload cao.

---

#### Solution: Two-Tier Validation Setup

**TIER 1: Pre-Registration Checks (Instant - Auto)**

Event Configuration trong Event Admin Panel:
```json
{
  "event": {
    "name": "Techcombank Facebook Post Campaign",
    "participationRequirements": {
      "enabled": true,
      "tier1_preChecks": [
        {
          "id": "pre-001",
          "type": "account_age",
          "title": "Tài khoản ≥ 3 tháng",
          "description": "Tài khoản cần được tạo ít nhất 3 tháng trước ngày bắt đầu campaign",
          "validation": {
            "minMonths": 3,
            "checkFrom": "campaign_start_date"
          },
          "validationLevel": "auto",
          "required": true,
          "order": 1,
          "failureMessage": "Tài khoản của bạn chưa đủ 3 tháng tuổi. Vui lòng quay lại sau {{remaining_days}} ngày."
        },
        {
          "id": "pre-002",
          "type": "email_exists",
          "title": "Có địa chỉ email",
          "description": "Cần có email để nhận thông báo",
          "validation": {
            "checkField": "user.email",
            "notNull": true,
            "notEmpty": true
          },
          "validationLevel": "auto",
          "required": true,
          "order": 2,
          "failureAction": {
            "cta": "Cập nhật email",
            "link": "/profile/edit"
          }
        },
        {
          "id": "pre-003",
          "type": "phone_exists",
          "title": "Có số điện thoại",
          "description": "Cần có SĐT để liên hệ khi cần thiết",
          "validation": {
            "checkField": "user.phone",
            "notNull": true,
            "notEmpty": true
          },
          "validationLevel": "auto",
          "required": true,
          "order": 3,
          "failureAction": {
            "cta": "Cập nhật SĐT",
            "link": "/profile/edit"
          }
        },
        {
          "id": "pre-004",
          "type": "account_status",
          "title": "Tài khoản hoạt động bình thường",
          "description": "Tài khoản không bị khóa hoặc cấm",
          "validation": {
            "checkField": "user.status",
            "mustEqual": "active"
          },
          "validationLevel": "auto",
          "required": true,
          "order": 4,
          "failureMessage": "Tài khoản của bạn đang bị tạm khóa. Vui lòng liên hệ support."
        },
        {
          "id": "pre-005",
          "type": "facebook_linked",
          "title": "Đã liên kết Facebook",
          "description": "Liên kết tài khoản Facebook trước khi đăng ký tham gia",
          "validation": {
            "checkField": "user.socialAccounts.facebook",
            "notNull": true,
            "checkFields": {
              "profileUrl": "required",
              "userId": "required",
              "accessToken": "optional"
            },
            "checkAccessible": {
              "enabled": true,
              "method": "basic_graph_api_call",
              "endpoint": "/{user-id}",
              "fallbackToManual": true
            }
          },
          "validationLevel": "auto",
          "required": true,
          "order": 5,
          "failureMessage": "Bạn cần liên kết tài khoản Facebook để tham gia campaign này.",
          "failureAction": {
            "cta": "Liên kết Facebook",
            "trigger": "facebook_connect_flow",
            "link": "/profile/social-accounts",
            "description": "Chúng tôi sẽ redirect bạn tới trang liên kết Facebook. Sau khi liên kết xong, quay lại trang này để tiếp tục."
          },
          "securityNote": "Chúng tôi chỉ lưu trữ public profile URL, không lưu access token hoặc thông tin nhạy cảm."
        }
      ]
    }
  }
}
```

**UI Display cho User:**
```
╔═══════════════════════════════════════════════════════════╗
║  📋 Điều kiện tham gia - Kiểm tra tự động                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ✅ Tài khoản ≥ 3 tháng                                    ║
║     Tài khoản của bạn: 2 năm 3 tháng                      ║
║     🤖 Đã kiểm tra tự động                                 ║
║                                                            ║
║  ✅ Có địa chỉ email                                       ║
║     user@example.com                                       ║
║     🤖 Đã kiểm tra tự động                                 ║
║                                                            ║
║  ❌ Có số điện thoại                                       ║
║     Bạn chưa cập nhật số điện thoại                       ║
║     [Cập nhật SĐT] ← CTA button                           ║
║                                                            ║
║  ✅ Tài khoản hoạt động bình thường                        ║
║     🤖 Đã kiểm tra tự động                                 ║
║                                                            ║
║  ❌ Đã liên kết Facebook                                   ║
║     Bạn chưa liên kết tài khoản Facebook                  ║
║     [Liên kết Facebook] ← CTA button                      ║
║     💡 Chúng tôi chỉ lưu public profile URL               ║
║                                                            ║
╠═══════════════════════════════════════════════════════════╣
║  ⚠️  Vui lòng hoàn thành tất cả điều kiện trên (0/5)      ║
║      để có thể đăng ký tham gia                           ║
║                                                            ║
║  [Đăng ký tham gia] ← DISABLED                            ║
╚═══════════════════════════════════════════════════════════╝

[Sau khi user click "Liên kết Facebook" và hoàn thành OAuth flow]

╔═══════════════════════════════════════════════════════════╗
║  📋 Điều kiện tham gia - Kiểm tra tự động (5/5 ✅)         ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ✅ Tài khoản ≥ 3 tháng                                    ║
║  ✅ Có địa chỉ email                                       ║
║  ✅ Có số điện thoại                                       ║
║  ✅ Tài khoản hoạt động bình thường                        ║
║  ✅ Đã liên kết Facebook                                   ║
║     facebook.com/nguyenvana                                ║
║     🤖 Đã kiểm tra tự động                                 ║
║                                                            ║
╠═══════════════════════════════════════════════════════════╣
║  ✅ Tất cả điều kiện cơ bản đã đạt!                        ║
║                                                            ║
║  [Đăng ký tham gia] ← ENABLED                             ║
╚═══════════════════════════════════════════════════════════╝
```

---

**TIER 2: Post-Registration Validation (Async - Admin Review)**

Event Configuration:
```json
{
  "event": {
    "participationRequirements": {
      "tier2_postValidation": [
        {
          "id": "post-001",
          "type": "email_verified",
          "title": "Email đã xác thực OTP",
          "description": "Xác thực email để nhận thông báo chính thức",
          "validation": {
            "checkField": "user.email.verified",
            "mustEqual": true,
            "otpRequired": true
          },
          "validationLevel": "user_action",
          "required": true,
          "order": 5,
          "action": {
            "type": "otp_verification",
            "trigger": "button_click",
            "buttonLabel": "Xác thực Email"
          }
        },
        {
          "id": "post-002",
          "type": "phone_verified",
          "title": "SĐT đã xác thực OTP",
          "description": "Xác thực SĐT để liên hệ khi cần",
          "validation": {
            "checkField": "user.phone.verified",
            "mustEqual": true,
            "otpRequired": true
          },
          "validationLevel": "user_action",
          "required": true,
          "order": 6,
          "action": {
            "type": "otp_verification",
            "trigger": "button_click",
            "buttonLabel": "Xác thực SĐT"
          }
        },
        {
          "id": "post-003",
          "type": "facebook_profile_quality",
          "title": "Kiểm tra chất lượng Facebook",
          "description": "Admin review profile legitimacy và post quality",
          "validation": {
            "useFacebookUrlFrom": "user.socialAccounts.facebook.profileUrl",
            "userCanUpload": {
              "optional_screenshots": {
                "description": "User có thể upload thêm screenshots nếu muốn",
                "maxFiles": 5,
                "maxSizeMB": 5
              }
            },
            "adminReviews": ["profile_legitimacy", "post_quality"],
            "criteria": {
              "profile_legitimacy": "Tài khoản Facebook có phải người thật?",
              "post_quality": "Có bài đăng thật hay chỉ spam link?"
            }
          },
          "validationLevel": "manual",
          "required": true,
          "order": 7,
          "note": "Facebook profile URL đã được lấy từ Tier 1 pre-check (user.socialAccounts.facebook). User không cần nhập lại."
        },
        {
          "id": "post-004",
          "type": "facebook_followers",
          "title": "Facebook ≥ 1,000 followers",
          "description": "Fanpage hoặc profile cần có ít nhất 1,000 followers/friends",
          "validation": {
            "minFollowers": 1000,
            "autoFetch": {
              "enabled": true,
              "apiSource": "facebook_graph_api",
              "endpoint": "/{page-id}?fields=followers_count",
              "fallbackToManual": true
            },
            "manualInput": {
              "enabled": true,
              "requireScreenshot": true,
              "adminVerifies": true
            }
          },
          "validationLevel": "hybrid",
          "required": true,
          "order": 8
        },
        {
          "id": "post-005",
          "type": "authentic_posts",
          "title": "Có bài đăng thật (không spam)",
          "description": "Trang cá nhân có bài viết chất lượng, cấm spam share link",
          "validation": {
            "adminChecks": [
              "Có bài viết tự tay (original content)?",
              "Có engagement thật (likes, comments)?",
              "Không phải toàn bài spam link?"
            ],
            "criteria": "Ít nhất 3/5 bài gần nhất là bài viết thật"
          },
          "validationLevel": "manual",
          "required": true,
          "order": 9
        },
        {
          "id": "post-006",
          "type": "invitation_code",
          "title": "Mã mời từ Techcombank",
          "description": "Nhập mã mời nếu bạn được Techcombank giới thiệu",
          "validation": {
            "checkDatabase": true,
            "tableName": "invitation_codes",
            "criteria": {
              "code_exists": true,
              "not_expired": true,
              "quota_not_exceeded": true,
              "partner": "techcombank"
            }
          },
          "validationLevel": "auto",
          "required": false,
          "order": 10,
          "submissionRequirements": {
            "code_input": {
              "type": "text_input",
              "label": "Mã mời (nếu có)",
              "placeholder": "TCB-EVENT01-XXXXX",
              "optional": true
            }
          }
        }
      ]
    }
  }
}
```

**Application Form UI:**
```
╔═══════════════════════════════════════════════════════════╗
║  📝 Đăng ký tham gia Techcombank Campaign                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ✅ Email đã xác thực                                      ║
║     user@example.com                                       ║
║                                                            ║
║  ⏳ SĐT chưa xác thực                                      ║
║     [Xác thực SĐT] ← User clicks                          ║
║                                                            ║
║  ✅ Facebook đã liên kết                                   ║
║     facebook.com/nguyenvana                                ║
║     🔗 Đã lấy từ tài khoản đã liên kết                    ║
║                                                            ║
║     Screenshots bổ sung (không bắt buộc):                  ║
║     [📁 Chọn file] (Tối đa 5 files, 5MB/file)             ║
║     💡 Admin sẽ review trực tiếp profile của bạn          ║
║                                                            ║
║  🎫 Mã mời (không bắt buộc)                                ║
║     ┌─────────────────────────────────────────┐           ║
║     │ TCB-EVENT01-XXXXX                       │           ║
║     └─────────────────────────────────────────┘           ║
║                                                            ║
║  ☑️ Tôi xác nhận thông tin trên là chính xác               ║
║                                                            ║
║  [Gửi hồ sơ]                                              ║
║                                                            ║
╠═══════════════════════════════════════════════════════════╣
║  ℹ️  Sau khi gửi, hồ sơ sẽ được admin duyệt trong 1-2 ngày║
║  💡 Admin sẽ xem trực tiếp Facebook profile của bạn       ║
╚═══════════════════════════════════════════════════════════╝
```

---

**Admin Review Dashboard:**
```
╔═══════════════════════════════════════════════════════════╗
║  👤 Hồ sơ: Nguyễn Văn A                                    ║
║  📅 Nộp lúc: 07/02/2026 14:30                              ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ✅ AUTO-CHECKS (Passed)                                   ║
║     • Account age: 2 years ✅                              ║
║     • Email verified: user@example.com ✅                  ║
║     • Phone verified: 0901234567 ✅                        ║
║     • Facebook linked: facebook.com/nguyenvana ✅          ║
║     • Invitation code: TCB-EVENT01-A3X9K ✅                ║
║                                                            ║
║  ⏳ MANUAL REVIEW (Pending)                                ║
║                                                            ║
║  1. Facebook Profile Quality Check                         ║
║     [🔗 facebook.com/nguyenvana] ← Clickable (new tab)     ║
║     🔗 Đã lấy từ pre-check Tier 1                         ║
║                                                            ║
║     Screenshots bổ sung (optional - user uploaded):        ║
║     [📷 View screenshot1.jpg] [📷 View screenshot2.jpg]    ║
║                                                            ║
║     Admin checklist:                                       ║
║     ☐ Profile legitimacy: Real person?                    ║
║        [ ] Yes - Real profile                             ║
║        [ ] No - Fake/Clone account                        ║
║                                                            ║
║     ☐ Post quality: Authentic content?                    ║
║        [ ] Yes - Has original posts                       ║
║        [ ] No - Mostly spam links                         ║
║                                                            ║
║  2. Follower Count (Hybrid: Auto-fetch first)              ║
║     🤖 Calling Facebook Graph API...                       ║
║     ✅ Auto-fetched: 1,500 followers                       ║
║     Requirement: ≥1,000 → PASS ✅                          ║
║                                                            ║
║     (Nếu API fails:)                                       ║
║     ❌ API failed: Rate limit exceeded                     ║
║     Manual input required:                                 ║
║     Follower count: [_______]                             ║
║     (Check từ screenshots hoặc visit profile trực tiếp)   ║
║                                                            ║
║  3. Authentic Posts Check                                  ║
║     💡 Admin visit profile và scroll timeline              ║
║     ☐ Has 3+ original posts (không phải share)            ║
║     ☐ Has real engagement (likes, comments)               ║
║     ☐ Not majority spam links                             ║
║                                                            ║
║  📝 Admin Notes:                                           ║
║     ┌─────────────────────────────────────────┐           ║
║     │ Profile looks good, 1500 followers,     │           ║
║     │ posts are authentic with good engagement│           ║
║     │ Approved for participation.             │           ║
║     └─────────────────────────────────────────┘           ║
║                                                            ║
║  [✅ Duyệt hồ sơ]  [❌ Từ chối]  [❓ Yêu cầu bổ sung]      ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

---

**Re-Validation at Payment Reconciliation:**
```json
{
  "reconciliation": {
    "revalidation": {
      "enabled": true,
      "checks": [
        {
          "id": "recheck-001",
          "type": "follower_count",
          "description": "Re-check follower count để prevent exploitation",
          "trigger": "before_payment_processing",
          "validation": {
            "refetchFollowerCount": true,
            "compareWith": "originalFollowerCountAtApproval",
            "gracePeriod": {
              "allowedDrop": 10,
              "unit": "percentage"
            },
            "rules": [
              {
                "condition": "drop <= 10%",
                "action": "pass",
                "message": "Natural fluctuation, OK"
              },
              {
                "condition": "drop > 10% AND drop <= 30%",
                "action": "manual_review",
                "message": "Flagged for admin review"
              },
              {
                "condition": "drop > 30%",
                "action": "reject_payment",
                "message": "Suspicious drop, payment rejected"
              }
            ]
          }
        },
        {
          "id": "recheck-002",
          "type": "account_status",
          "description": "Check account không bị banned",
          "validation": {
            "checkField": "user.status",
            "mustEqual": "active"
          }
        }
      ]
    }
  }
}
```

---

#### Outcome: Techcombank Campaign

**Before Two-Tier System:**
- 1,000 users submit bài → 150 không đủ điều kiện → Admin waste 75 giờ review
- Fraud rate: 15%
- User frustration: High (submit rồi mới bị reject)

**After Two-Tier System:**
- 1,000 users view event
- Pre-checks filter: 200 không đủ điều kiện cơ bản (blocked ngay)
- 800 submit applications → Admin review
- Post-validation reject: 40 users (5%)
- 760 users approved → Submit content
- Re-validation catch: 10 fraud cases (1.3%)

**Results:**
- Fraud rate: 15% → 1.3% ✅
- Admin workload: 75 giờ → 45 giờ (40% reduction) ✅
- User satisfaction: Cao hơn (instant feedback) ✅

---

### Case Study 2: HDBANK Campaign - Profile Completion Required (NEW PROBLEM)

**Bối cảnh:**
HDBANK campaign yêu cầu user PHẢI có email/phone verified từ đầu để:
- Hỗ trợ mở thẻ tín dụng
- Đối soát dữ liệu với HDBANK
- Compliance requirements từ ngân hàng

**Yêu cầu từ Product Owner:**
> "Yêu cầu creator nhập thông tin liên hệ (SĐT/email, và các thông tin cần thiết khác) ngay tại lần đầu đăng bài trên nền tảng."

---

#### Solution: Tier 0 + Two-Tier Setup

**TIER 0: Platform-Level Profile Completion (One-Time)**

Trigger khi user lần đầu tiên attempt tham gia BẤT KỲ campaign nào:

```json
{
  "platform": {
    "profileCompletionGate": {
      "enabled": true,
      "trigger": "first_campaign_participation",
      "description": "Hoàn thành hồ sơ cơ bản trước khi tham gia campaign",
      "requirements": [
        {
          "id": "tier0-001",
          "type": "email_verified_otp",
          "title": "Xác thực Email",
          "description": "Nhập email và xác thực bằng mã OTP",
          "required": true,
          "order": 1,
          "validation": {
            "emailFormat": "RFC5322",
            "otpRequired": true,
            "otpExpiry": "5_minutes",
            "maxRetries": 3
          },
          "ui": {
            "inputType": "email",
            "placeholder": "your-email@example.com",
            "ctaButton": "Gửi mã OTP"
          }
        },
        {
          "id": "tier0-002",
          "type": "phone_verified_otp",
          "title": "Xác thực Số điện thoại",
          "description": "Nhập SĐT và xác thực bằng mã OTP SMS",
          "required": true,
          "order": 2,
          "validation": {
            "phoneFormat": "vietnam_mobile",
            "otpRequired": true,
            "otpExpiry": "5_minutes",
            "maxRetries": 3
          },
          "ui": {
            "inputType": "tel",
            "placeholder": "09xxxxxxxx",
            "ctaButton": "Gửi OTP qua SMS"
          }
        },
        {
          "id": "tier0-003",
          "type": "basic_info",
          "title": "Thông tin cơ bản",
          "description": "Họ tên và ảnh đại diện",
          "required": true,
          "order": 3,
          "fields": [
            {
              "name": "fullName",
              "label": "Họ và tên",
              "type": "text",
              "validation": {
                "minLength": 3,
                "maxLength": 100,
                "required": true
              }
            },
            {
              "name": "avatar",
              "label": "Ảnh đại diện",
              "type": "file_upload",
              "validation": {
                "maxSizeMB": 2,
                "acceptedFormats": ["jpg", "png"],
                "required": false
              }
            }
          ]
        },
        {
          "id": "tier0-004",
          "type": "consent",
          "title": "Đồng ý điều khoản",
          "description": "Xác nhận đồng ý lưu trữ và sử dụng dữ liệu",
          "required": true,
          "order": 4,
          "validation": {
            "mustCheck": true
          },
          "ui": {
            "type": "checkbox",
            "label": "Tôi đồng ý cho Ambassador Platform lưu trữ thông tin liên hệ của tôi để:",
            "details": [
              "✓ Liên hệ khi cần thiết (xác minh nội dung, hỗ trợ kỹ thuật)",
              "✓ Gửi thông báo thanh toán",
              "✓ Đáp ứng yêu cầu compliance từ đối tác (HDBANK, Techcombank)",
              "",
              "Dữ liệu được bảo mật theo chính sách GDPR."
            ],
            "linkToPolicyPage": "/privacy-policy"
          }
        }
      ],
      "onComplete": {
        "action": "set_user_flag",
        "flag": "user.profileCompleted",
        "value": true,
        "timestamp": true
      },
      "subsequentCampaigns": {
        "skipTier0": true,
        "reuseVerifiedData": true
      }
    }
  }
}
```

**UI: Profile Completion Modal (First Time)**
```
╔═══════════════════════════════════════════════════════════╗
║  🎉 Chào mừng đến với Ambassador Platform!                 ║
║                                                            ║
║  Trước khi tham gia campaign, vui lòng hoàn thành hồ sơ:  ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  📧 Bước 1/3: Xác thực Email                               ║
║  ┌─────────────────────────────────────────┐              ║
║  │ your-email@example.com                  │              ║
║  └─────────────────────────────────────────┘              ║
║  [Gửi mã OTP]                                             ║
║                                                            ║
║  Nhập mã OTP (đã gửi tới email):                          ║
║  ┌───┬───┬───┬───┬───┬───┐                                ║
║  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │                                ║
║  └───┴───┴───┴───┴───┴───┘                                ║
║  ⏱️  Mã hết hiệu lực sau: 04:32                            ║
║  [Gửi lại mã]                                             ║
║                                                            ║
║  ✅ Email đã xác thực                                      ║
║                                                            ║
╠═══════════════════════════════════════════════════════════╣
║  [Tiếp theo: Xác thực SĐT] →                             ║
╚═══════════════════════════════════════════════════════════╝
```

---

**HDBANK Event Config (Event-Specific Requirements)**

```json
{
  "event": {
    "name": "HDBANK Credit Card Promotion",
    "participationRequirements": {
      "enabled": true,

      "tier0_override": {
        "description": "HDBANK yêu cầu profile completion bắt buộc",
        "enforce": true,
        "blockIfNotCompleted": true,
        "message": "Campaign này yêu cầu hồ sơ đã hoàn thành (email + SĐT verified)"
      },

      "tier1_preChecks": [
        {
          "id": "hdbank-pre-001",
          "type": "profile_completed",
          "title": "Hồ sơ đã hoàn thành",
          "description": "Email và SĐT đã xác thực (Tier 0)",
          "validation": {
            "checkField": "user.profileCompleted",
            "mustEqual": true
          },
          "validationLevel": "auto",
          "required": true,
          "order": 1,
          "failureMessage": "Vui lòng hoàn thành hồ sơ cơ bản trước khi tham gia campaign này.",
          "failureAction": {
            "cta": "Hoàn thành hồ sơ",
            "trigger": "profile_completion_flow"
          }
        },
        {
          "id": "hdbank-pre-002",
          "type": "account_age",
          "title": "Tài khoản ≥ 1 tháng",
          "description": "Tài khoản cần ít nhất 1 tháng tuổi",
          "validation": {
            "minMonths": 1
          },
          "validationLevel": "auto",
          "required": true,
          "order": 2
        }
      ],

      "tier2_postValidation": [
        {
          "id": "hdbank-post-001",
          "type": "facebook_profile",
          "title": "Liên kết Facebook",
          "description": "HDBANK yêu cầu verify Facebook profile",
          "validation": {
            "userSubmits": ["facebook_url", "screenshots"],
            "adminReviews": ["profile_legitimacy"]
          },
          "validationLevel": "manual",
          "required": true,
          "order": 3
        },
        {
          "id": "hdbank-post-002",
          "type": "facebook_followers",
          "title": "Facebook ≥ 500 followers",
          "description": "Yêu cầu thấp hơn Techcombank (HDBANK chấp nhận micro-influencers)",
          "validation": {
            "minFollowers": 500,
            "autoFetch": {
              "enabled": true,
              "fallbackToManual": true
            }
          },
          "validationLevel": "hybrid",
          "required": true,
          "order": 4
        },
        {
          "id": "hdbank-post-003",
          "type": "bank_account_info",
          "title": "Thông tin tài khoản ngân hàng",
          "description": "HDBANK cần để hỗ trợ mở thẻ và chuyển thưởng",
          "validation": {
            "userSubmits": [
              "bank_name",
              "bank_account_number",
              "bank_account_name"
            ],
            "adminVerifies": false,
            "autoValidation": {
              "checkNameMatch": "user.fullName"
            }
          },
          "validationLevel": "user_input",
          "required": true,
          "order": 5,
          "submissionRequirements": {
            "bank_name": {
              "type": "dropdown",
              "label": "Ngân hàng",
              "options": ["HDBANK", "Vietcombank", "Techcombank", "VPBank", "Khác"],
              "default": "HDBANK"
            },
            "bank_account_number": {
              "type": "text_input",
              "label": "Số tài khoản",
              "validation": {
                "numeric": true,
                "minLength": 9,
                "maxLength": 14
              }
            },
            "bank_account_name": {
              "type": "text_input",
              "label": "Tên chủ tài khoản",
              "validation": {
                "mustMatch": "user.fullName",
                "message": "Tên tài khoản phải trùng với họ tên trên hồ sơ"
              }
            }
          },
          "securityNote": "Thông tin ngân hàng được mã hóa và chỉ dùng cho mục đích thanh toán."
        }
      ]
    }
  }
}
```

---

**User Journey: HDBANK Campaign**

**Scenario A: User mới (chưa profileCompleted)**
```
1. User click "Xem campaign HDBANK"
   ↓
2. System check: user.profileCompleted?
   → NO
   ↓
3. Trigger Tier 0 Profile Completion Modal
   ↓
4. User hoàn thành:
   - Verify email OTP ✅
   - Verify phone OTP ✅
   - Nhập họ tên ✅
   - Đồng ý điều khoản ✅
   ↓
5. System set user.profileCompleted = true
   ↓
6. Redirect về HDBANK campaign page
   ↓
7. Pre-checks run:
   ✅ Profile completed
   ✅ Account age ≥1 month
   ↓
8. Button "Đăng ký tham gia" enabled
   ↓
9. User submit application (Facebook + Bank info)
   ↓
10. Admin review → Approve
    ↓
11. User submit content → Payment
```

**Scenario B: User cũ (đã profileCompleted từ campaign trước)**
```
1. User click "Xem campaign HDBANK"
   ↓
2. System check: user.profileCompleted?
   → YES ✅ (Skip Tier 0)
   ↓
3. Pre-checks run instant:
   ✅ Profile completed (already)
   ✅ Account age ≥1 month
   ↓
4. Button "Đăng ký tham gia" enabled
   ↓
5. User submit application (chỉ cần Facebook + Bank info)
   ↓
6. Admin review → Approve
   ↓
7. User submit content → Payment
```

---

**Benefits of Tier 0 Approach:**

1. **User Convenience (Long-term):**
   - First campaign: Verify email/phone một lần
   - Subsequent campaigns: Skip verification, instant participation
   - No repeated OTP flows

2. **Compliance:**
   - Platform-level consent (GDPR)
   - Audit trail (khi nào user verify)
   - Reusable verified data cho mọi partners

3. **Partner Flexibility:**
   - HDBANK: Require profile completion (strict)
   - Techcombank: Require profile completion (strict)
   - Ambassador: Optional (lenient)
   - VinFast: Optional (lenient)

4. **Admin Efficiency:**
   - Email/phone verified một lần → Không check lại
   - Event-specific requirements chỉ focus vào Facebook/content quality

---

#### Comparison: With vs Without Tier 0

**WITHOUT Tier 0 (Current Problem):**
```
Campaign 1 (Techcombank):
  User verify email ✅ → Verify phone ✅ → Approved

Campaign 2 (HDBANK):
  User verify email ✅ (lại) → Verify phone ✅ (lại) → Approved

Campaign 3 (VinFast):
  User verify email ✅ (lại lần 3) → Verify phone ✅ (lại lần 3) → Approved

→ User frustration: Phải verify lại mỗi campaign
→ Drop-off rate: Cao (30-40%)
```

**WITH Tier 0 (Solution):**
```
First Campaign (Any):
  Tier 0: Verify email ✅ → Verify phone ✅ (ONE TIME)
  → user.profileCompleted = true

Campaign 2, 3, 4... (Forever):
  Tier 0: SKIP ✅ (already completed)
  → Go straight to event-specific requirements

→ User satisfaction: Cao (only verify once)
→ Drop-off rate: Thấp (10-15%)
```

---

### Summary: Two Case Studies

| Aspect | Case 1: Techcombank | Case 2: HDBANK |
|--------|---------------------|----------------|
| **Problem** | Fraud rate cao (15%) | Thiếu email/phone verified |
| **Main Focus** | Quality validation (followers, posts) | Profile completion mandatory |
| **Tier 0** | Optional | **Required** (enforce) |
| **Tier 1 Pre-Checks** | 4 checks (account age, email/phone exists, status) | 2 checks (profile completed, account age) |
| **Tier 2 Validation** | 6 checks (OTP, Facebook, followers, posts, code) | 3 checks (Facebook, followers, **bank info**) |
| **Follower Requirement** | ≥1,000 (strict) | ≥500 (lenient, micro-influencers OK) |
| **Admin Workload** | High (manual profile + post review) | Medium (Tier 0 handles email/phone) |
| **Key Differentiator** | Re-validation at reconciliation | Bank account info collection |
| **Business Impact** | Fraud ↓ 15%→1.3% | Compliance + smooth payment |

---

## User Personas

### Persona 1: Influencer/Creator
**Profile:**
- Name: Linh (23 tuổi)
- Facebook: 1,500 followers
- Motivation: Kiếm thêm thu nhập 3-5M/tháng
- Pain points: Không rõ requirements, sợ submit rồi bị reject

**Needs:**
- Biết rõ điều kiện từ đầu
- Instant feedback (pass/fail pre-checks)
- Clear timeline (bao lâu được duyệt)
- Self-service (tự fulfill requirements)

---

### Persona 2: Admin/Content Moderator
**Profile:**
- Name: Hoa (28 tuổi, Content Operations)
- Workload: Review 50-100 applications/day
- Pain points: Nhiều applications không đủ điều kiện cơ bản, mất thời gian

**Needs:**
- Pre-filtered queue (chỉ xem qualified users)
- Batch approval tools
- Clear criteria (không phải subjective judgment)
- Fast review workflow (<5 min/user)

---

### Persona 3: Partner (Techcombank Marketing Team)
**Profile:**
- Name: Mr. Tuấn (35 tuổi, Brand Manager)
- Campaign budget: 100-200M VND
- Pain points: Lo ngại về quality influencers, fraud

**Needs:**
- Quality assurance (tất cả influencers đã verified)
- Transparency (biết được criteria)
- Control (có thể config requirements per campaign)
- Reporting (fraud rate, quality metrics)

---

## Functional Requirements

### TIER 1: Pre-Registration Eligibility System

#### FR-001: Account Age Validation (Auto)

**Priority:** Must Have

**Description:**
System tự động kiểm tra account age khi user load event detail page. Nếu account age < minimum required (e.g., 3 tháng), button "Đăng ký tham gia" bị disable.

**Acceptance Criteria:**
- [ ] System calculates account age: `(Date.now() - user.createdAt)`
- [ ] Compare với event.requirements.minAccountAge
- [ ] Display result trong checklist (✅ Pass hoặc ❌ Fail)
- [ ] Nếu fail: Button disabled + tooltip: "Tài khoản cần ít nhất X tháng tuổi"
- [ ] Check runs instantly (<100ms)

**Dependencies:** Event configuration (minAccountAge setting)

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-002: Email/Phone Existence Check (Auto)

**Priority:** Must Have

**Description:**
System kiểm tra user có email và phone trong profile. Không require verified ở tier này, chỉ check existence.

**Acceptance Criteria:**
- [ ] Check `user.email !== null && user.email !== ''`
- [ ] Check `user.phone !== null && user.phone !== ''`
- [ ] Display status trong checklist
- [ ] Nếu missing: Show CTA "Cập nhật email" hoặc "Cập nhật phone"
- [ ] Link tới profile edit page

**Dependencies:** User profile schema có email/phone fields

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-003: Account Status Check (Auto)

**Priority:** Must Have

**Description:**
System kiểm tra account không bị banned/suspended.

**Acceptance Criteria:**
- [ ] Check `user.status === 'active'`
- [ ] Nếu banned/suspended: Hard block với message rõ ràng
- [ ] Log attempt (audit trail)

**Dependencies:** User.status field

---

#### FR-004: Facebook Account Linked Check (Auto)

**Priority:** Must Have

**Description:**
System kiểm tra user đã liên kết Facebook account trước khi cho phép đăng ký. Facebook profile URL được lưu trong user.socialAccounts.facebook và sẽ được dùng cho admin review ở Tier 2.

**Acceptance Criteria:**
- [ ] Check `user.socialAccounts.facebook !== null`
- [ ] Check `user.socialAccounts.facebook.profileUrl` exists và valid
- [ ] Optional: Basic accessibility check (call Facebook Graph API `/{user-id}` để verify profile exists)
- [ ] Display status trong checklist (✅ Linked hoặc ❌ Not Linked)
- [ ] Nếu not linked: Show CTA "Liên kết Facebook"
- [ ] CTA triggers Facebook OAuth flow → User authorizes → Save profile URL
- [ ] After linking: Refresh checklist, mark as ✅

**Dependencies:**
- User.socialAccounts schema với facebook field
- Facebook OAuth integration
- Facebook Graph API (optional, cho accessibility check)

**Related Insight:** Insight 1 - Two-Tier System

**Rationale:**
- **Critical logic fix:** Admin không thể review nếu không có Facebook profile
- Pre-check này filter sớm users chưa link Facebook
- Facebook URL từ Tier 1 sẽ được reuse ở Tier 2 (admin review)
- User không cần nhập lại URL trong application form

**Security Note:**
Chỉ lưu public profile URL, không lưu access token (hoặc nếu cần token thì expire ngay sau khi lấy được profile URL)

---

#### FR-005: Pre-Check Aggregation & UI Display

**Priority:** Must Have

**Description:**
Aggregate tất cả pre-checks và display trong requirements checklist UI. Enable/disable "Đăng ký tham gia" button dựa trên kết quả.

**Acceptance Criteria:**
- [ ] API endpoint: `GET /events/:id/participation/pre-checks`
- [ ] Return JSON với status từng check (✅/❌)
- [ ] Frontend render checklist với visual indicators
- [ ] Button "Đăng ký tham gia" enabled chỉ khi ALL pre-checks pass
- [ ] Tooltip explain lý do nếu disabled

**Dependencies:** FR-001, FR-002, FR-003

**Related Insight:** Insight 1 - Two-Tier System

---

### TIER 2: Post-Registration Validation System

#### FR-005: Participation Application Submission

**Priority:** Must Have

**Description:**
User submit participation application với Facebook profile URL, screenshots, và invitation code (nếu có).

**Acceptance Criteria:**
- [ ] Modal form mở khi click "Đăng ký tham gia"
- [ ] Required fields:
  - Facebook Profile URL (text input, URL validation)
  - Screenshots (file upload, max 5 files, 5MB each)
  - Invitation Code (optional text input)
- [ ] Checkbox: "Tôi xác nhận thông tin chính xác"
- [ ] Submit tạo ParticipationReview record với status 'pending'
- [ ] User receives confirmation: "Hồ sơ đã nộp, dự kiến duyệt trong 1-2 ngày"

**Dependencies:** FR-004 (pre-checks must pass first)

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-006: Email OTP Verification

**Priority:** Must Have (Phase 1) / Should Have (if Tier 0 implemented)

**Description:**
User verify email bằng OTP code. Có thể là part của Tier 0 (profile completion) hoặc event-specific requirement.

**Acceptance Criteria:**
- [ ] User click "Verify Email"
- [ ] System send OTP (6 digits) tới email
- [ ] OTP expires sau 5 minutes
- [ ] User nhập OTP → Verify success → Mark email as verified
- [ ] Max 3 retries per 15 minutes (rate limiting)
- [ ] Update user.email.verified = true

**Dependencies:** Email service (SMTP/SendGrid)

**Related Insight:** Insight 2 - Profile Completion Gate

---

#### FR-007: Phone OTP Verification

**Priority:** Must Have (Phase 1) / Should Have (if Tier 0 implemented)

**Description:**
Tương tự FR-006 nhưng cho phone verification.

**Acceptance Criteria:**
- [ ] User click "Verify Phone"
- [ ] System send OTP qua SMS
- [ ] OTP expires sau 5 minutes
- [ ] User nhập OTP → Verify success
- [ ] Max 3 retries per 15 minutes
- [ ] Update user.phone.verified = true

**Dependencies:** SMS service (Twilio/local provider)

**Related Insight:** Insight 2 - Profile Completion Gate

---

#### FR-008: Facebook Profile Quality Review (Manual)

**Priority:** Must Have

**Description:**
Admin manually review Facebook profile quality: Có phải tài khoản thật? Có bài đăng spam không?

**Acceptance Criteria:**
- [ ] Admin dashboard hiển thị Facebook profile URL (clickable)
- [ ] Admin mở Facebook profile trong new tab
- [ ] Admin review:
  - Profile legitimacy (real person vs fake)
  - Post history (authentic vs spam)
  - Engagement quality (real comments vs bots)
- [ ] Admin mark pass/fail với notes
- [ ] Notes lưu vào ParticipationReview.reviewData.profileQuality

**Dependencies:** FR-005 (application submitted first)

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-009: Follower Count Validation (Hybrid)

**Priority:** Must Have

**Description:**
Validate follower count ≥ threshold. Try Facebook Graph API first, fallback to manual if API fails.

**Acceptance Criteria:**
- [ ] **Level 1 (Auto):** System call Facebook Graph API
  - Success: Extract follower count, compare với threshold
  - Store result với confidence: 'high'
- [ ] **Level 2 (Manual Fallback):** Nếu API fails
  - Admin view screenshots user uploaded
  - Admin manually input follower count
  - Store result với confidence: 'medium' (manual input)
- [ ] **Level 3 (Request More Info):** Nếu screenshots unclear
  - Admin click "Request more info"
  - User receives notification
  - User upload better screenshots → Re-enter queue
- [ ] Compare follower count với event.requirements.minFollowers
- [ ] Mark pass/fail

**Dependencies:**
- Facebook Graph API integration
- FR-005 (screenshots uploaded)

**Related Insight:** Insight 3 - Hybrid Validation

---

#### FR-010: Authentic Posts Check (Manual)

**Priority:** Must Have

**Description:**
Admin verify user có bài đăng thật (không phải toàn spam link).

**Acceptance Criteria:**
- [ ] Admin view Facebook profile (link từ FR-008)
- [ ] Admin scroll timeline, check recent posts
- [ ] Criteria:
  - ✅ Có bài viết tự tay (original content)
  - ✅ Có engagement (likes, comments từ người thật)
  - ❌ Không phải toàn bài share link spam
- [ ] Admin mark pass/fail với notes

**Dependencies:** FR-005, FR-008

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-011: Invitation Code Validation (Auto/Manual)

**Priority:** Should Have

**Description:**
Validate invitation code nếu event require. Có thể auto-check database hoặc manual verify bởi admin.

**Acceptance Criteria:**
- [ ] User nhập invitation code trong application form
- [ ] **Auto validation:**
  - Query InvitationCode table
  - Check code exists, not expired, quota not exceeded
  - Mark pass/fail instantly
- [ ] **Manual validation (nếu auto fails):**
  - Admin review code
  - Admin có thể override (approve với custom code)
- [ ] Link code với user (for tracking/analytics)

**Dependencies:** InvitationCode management system

---

#### FR-012: Admin Review Queue

**Priority:** Must Have

**Description:**
Admin dashboard hiển thị queue of pending applications, sorted by submission time (FIFO).

**Acceptance Criteria:**
- [ ] Dashboard route: `/admin/participation-reviews`
- [ ] Tab "Chờ duyệt" (Pending)
- [ ] Mỗi row hiển thị:
  - User info (name, avatar, account age)
  - Submission time
  - Auto-check results (✅ passed items)
  - Pending manual checks (⏳ items)
  - Actions: [Xem chi tiết] [Duyệt] [Từ chối]
- [ ] Queue sorted by submittedAt ASC (oldest first)
- [ ] Pagination (20 items/page)

**Dependencies:** FR-005, ParticipationReview model

**Related Insight:** Insight 4 - Clear SLA Communication

---

#### FR-013: Admin Approve Application

**Priority:** Must Have

**Description:**
Admin approve application sau khi verify tất cả manual checks pass.

**Acceptance Criteria:**
- [ ] Admin click "Duyệt hồ sơ"
- [ ] System updates:
  - UserEvent.participationStatus = 'approved'
  - UserEvent.approvedAt = Date.now()
  - UserEvent.approvedBy = admin.id
  - ParticipationReview.status = 'approved'
- [ ] User receives notification:
  - Email: "Hồ sơ đã được duyệt"
  - In-app notification badge
- [ ] User có thể submit content ngay

**Dependencies:** FR-012, notification system

---

#### FR-014: Admin Reject Application

**Priority:** Must Have

**Description:**
Admin reject application với lý do rõ ràng nếu fail manual checks.

**Acceptance Criteria:**
- [ ] Admin click "Từ chối"
- [ ] Modal mở: Textarea nhập lý do (required)
- [ ] Admin chọn failed requirements (checkboxes)
- [ ] System updates:
  - UserEvent.participationStatus = 'rejected'
  - ParticipationReview.status = 'rejected'
  - ParticipationReview.rejectionReason = text
  - ParticipationReview.failedRequirements = array
- [ ] User receives notification với lý do cụ thể
- [ ] User có thể appeal hoặc fix và resubmit (nếu fixable)

**Dependencies:** FR-012

---

#### FR-015: Batch Approval Tool

**Priority:** Should Have

**Description:**
Admin có thể approve nhiều applications cùng lúc (efficiency optimization).

**Acceptance Criteria:**
- [ ] Checkbox ở đầu mỗi row trong queue
- [ ] Checkbox "Select all" ở header
- [ ] Button "Duyệt hàng loạt" enabled khi ≥1 item selected
- [ ] Click button → Confirm modal → Batch approve
- [ ] System process sequentially với progress indicator
- [ ] Notifications sent to all approved users

**Dependencies:** FR-012, FR-013

**Related Insight:** Insight 3 - Hybrid Validation (admin efficiency)

---

### TIER 3: Content Submission Validation

#### FR-016: Content Submission Gate

**Priority:** Must Have

**Description:**
Khi user submit content, system check participationStatus. Chỉ cho phép nếu approved.

**Acceptance Criteria:**
- [ ] Existing Content.Create() API updated
- [ ] Check: event.participationRequirements.enabled?
  - NO: Allow submission (backward compatible)
  - YES: Continue to next check
- [ ] Check: userEvent.participationStatus === 'approved'?
  - YES: Allow content creation
  - NO: Return 403 error với message
    - "Bạn chưa đủ điều kiện tham gia campaign này"
    - Link tới requirements checklist page
- [ ] Log rejected attempts (analytics)

**Dependencies:** FR-013 (approval process)

**Related Insight:** Insight 1 - Two-Tier System

---

### TIER 4: Re-Validation at Reconciliation

#### FR-017: Follower Count Re-Validation

**Priority:** Must Have

**Description:**
Trước khi payment reconciliation, re-check follower count để prevent exploitation (user buy fake followers → submit → remove followers → get paid).

**Acceptance Criteria:**
- [ ] Trigger: Payment reconciliation flow
- [ ] Re-fetch follower count (Facebook API hoặc manual)
- [ ] Compare với originalFollowerCount (lúc approved)
- [ ] Calculate dropPercentage: `(original - current) / original * 100`
- [ ] **Grace period rules:**
  - Drop ≤10%: PASS (natural fluctuation)
  - Drop 10-30%: WARNING → Manual review
  - Drop >30%: FAIL → Reject payment
- [ ] If FAIL:
  - Mark payment as 'requires_review'
  - Admin notification
  - User notification: "Follower count giảm bất thường"

**Dependencies:** FR-009, payment reconciliation system

**Related Insight:** Insight 7 - Re-Validation at Reconciliation

---

#### FR-018: Account Status Re-Check

**Priority:** Should Have

**Description:**
Re-check account status (banned/suspended) trước payment.

**Acceptance Criteria:**
- [ ] Check user.status === 'active'
- [ ] Check userEvent.status !== 'banned'
- [ ] Nếu fail: Block payment với reason

**Dependencies:** FR-017

---

### EVENT CONFIGURATION

#### FR-019: Event-Level Participation Requirements Config

**Priority:** Must Have

**Description:**
Admin có thể config participation requirements per event (flexibility).

**Acceptance Criteria:**
- [ ] Event edit page có section "Điều kiện tham gia"
- [ ] Toggle: Enable/Disable participation requirements
- [ ] Config options:
  - Account age minimum (số tháng)
  - Email verified required? (yes/no)
  - Phone verified required? (yes/no)
  - Facebook profile required? (yes/no)
  - Follower count minimum (số)
  - Authentic posts check? (yes/no)
  - Invitation code required? (yes/no)
- [ ] Save to Event.participationRequirements object
- [ ] Preview: Show example checklist user sẽ thấy

**Dependencies:** Event model schema

**Related Insight:** All insights (foundation for system)

---

#### FR-020: Requirements Template System

**Priority:** Could Have

**Description:**
Admin có thể save requirement configs as templates để reuse cho events sau.

**Acceptance Criteria:**
- [ ] Button "Lưu thành template"
- [ ] Input template name
- [ ] Template stored in RequirementsTemplate table
- [ ] Dropdown "Load từ template" khi tạo event mới
- [ ] Common templates:
  - "Techcombank Standard" (strict: 7 requirements)
  - "Ambassador Basic" (lenient: 3 requirements)
  - "VIP Campaign" (very strict: 10 requirements)

**Dependencies:** FR-019

---

### USER EXPERIENCE & COMMUNICATION

#### FR-021: Requirements Checklist UI

**Priority:** Must Have

**Description:**
Event detail page hiển thị requirements checklist với visual status indicators.

**Acceptance Criteria:**
- [ ] Section "📋 Điều kiện tham gia" trên event page
- [ ] Mỗi requirement hiển thị:
  - Icon: ✅ (passed) / ❌ (failed) / ⏳ (pending) / ⏸️ (not checked yet)
  - Title: Tên requirement
  - Description: Giải thích ngắn
  - Action CTA (nếu failed): [Cập nhật email], [Verify phone], etc.
- [ ] Progress indicator: "3/7 hoàn thành"
- [ ] Button "Đăng ký tham gia" ở cuối, enabled/disabled based on pre-checks

**Dependencies:** FR-004 (pre-checks API)

**Related Insight:** Insight 1 - Two-Tier System

---

#### FR-022: Application Status Tracking UI

**Priority:** Should Have

**Description:**
User có thể track status của participation application với clear SLA communication.

**Acceptance Criteria:**
- [ ] Status card hiển thị:
  - Current status: "Đang chờ duyệt" / "Đã duyệt" / "Từ chối"
  - Submission time
  - Estimated review time: "1-2 ngày làm việc"
  - Queue position: "#47/120"
- [ ] Progress bar visual
- [ ] Timeline:
  - ✅ Nộp hồ sơ - 07/02 14:30
  - ✅ Auto-checks - 07/02 14:31
  - ⏳ Admin review - Đang xử lý
  - ⏸️ Thông báo kết quả
- [ ] Tip: "Check lại vào chiều thứ 5"

**Dependencies:** FR-005, FR-012

**Related Insight:** Insight 4 - Clear SLA Communication

---

#### FR-023: Email Notifications

**Priority:** Must Have

**Description:**
User receives email notifications cho key events trong participation flow.

**Acceptance Criteria:**
- [ ] **Application Submitted:**
  - Subject: "Hồ sơ tham gia đã nhận"
  - Body: Confirmation + estimated review time
- [ ] **Application Approved:**
  - Subject: "Chúc mừng! Hồ sơ đã được duyệt"
  - Body: Next steps (submit content)
  - CTA: [Gửi bài viết ngay]
- [ ] **Application Rejected:**
  - Subject: "Hồ sơ chưa đạt yêu cầu"
  - Body: Lý do cụ thể + failed requirements
  - CTA: [Xem chi tiết] [Appeal]
- [ ] **Request More Info:**
  - Subject: "Cần bổ sung thông tin"
  - Body: Yêu cầu cụ thể từ admin

**Dependencies:** Email service, FR-013, FR-014

---

#### FR-024: In-App Notifications

**Priority:** Should Have

**Description:**
In-app notification badge + notification center cho real-time updates.

**Acceptance Criteria:**
- [ ] Notification icon có badge count (unread)
- [ ] Notification center dropdown
- [ ] Notification types: approved, rejected, more_info_needed
- [ ] Click notification → Navigate to relevant page
- [ ] Mark as read

**Dependencies:** Notification service

---

### ANALYTICS & REPORTING

#### FR-025: Admin Analytics Dashboard

**Priority:** Should Have

**Description:**
Admin dashboard hiển thị metrics về participation system performance.

**Acceptance Criteria:**
- [ ] Metrics displayed:
  - Applications submitted (today, week, month)
  - Approval rate (% approved vs rejected)
  - Average review time (per application)
  - Queue size (current pending count)
  - Top rejection reasons (bar chart)
  - Fraud prevention metrics (re-validation failures)
- [ ] Date range filter
- [ ] Export to CSV

**Dependencies:** FR-012, FR-013, FR-014, FR-017

---

#### FR-026: Partner Reporting

**Priority:** Could Have

**Description:**
Partner (Techcombank, VinFast) có thể view quality metrics cho campaign của họ.

**Acceptance Criteria:**
- [ ] Partner dashboard page
- [ ] Metrics:
  - Total approved influencers
  - Average follower count
  - Fraud detection rate
  - Content quality scores
- [ ] Confidence: Partner yên tâm về quality

**Dependencies:** FR-025, partner authentication

---

### ADVANCED FEATURES (Phase 2)

#### FR-027: Profile Completion Gate (Tier 0)

**Priority:** Should Have (Phase 2)

**Description:**
Platform-level requirement: User verify email/phone MỘT LẦN khi đầu tiên tham gia bất kỳ campaign nào.

**Acceptance Criteria:**
- [ ] Trigger: User's first campaign participation attempt
- [ ] Force profile completion flow:
  - Step 1: Verify email OTP
  - Step 2: Verify phone OTP
  - Step 3: Complete basic info (name, avatar)
- [ ] Mark user.profileCompleted = true
- [ ] Subsequent campaigns skip Tier 0
- [ ] Modal với progress: "Hoàn thành hồ sơ (1/3)"

**Dependencies:** FR-006, FR-007

**Related Insight:** Insight 2 - Profile Completion Gate

---

#### FR-028: Verified Creator Badge System

**Priority:** Could Have (Phase 2)

**Description:**
Users with proven track record receive badges và fast-track approval.

**Acceptance Criteria:**
- [ ] Badge tiers:
  - 🥉 Bronze (1-2 campaigns approved)
  - 🥈 Silver (3-5 campaigns, 0 violations)
  - 🥇 Gold (6+ campaigns, 0 violations)
  - 💎 Diamond (Partner-nominated)
- [ ] Badge displayed on profile
- [ ] **Approval path logic:**
  - Diamond: Instant approval (whitelist)
  - Gold: Instant approval (spot check 10%)
  - Silver: Fast-track (4-8h instead of 1-2 days)
  - Bronze: Standard (1-2 days)
- [ ] Auto-downgrade nếu violations detected

**Dependencies:** User participation history tracking

**Related Insight:** Insight 5 - Verified Creator Badge

---

#### FR-029: Partial Approval Tiers

**Priority:** Could Have (Phase 2 - Pilot First)

**Description:**
Thay vì all-or-nothing, users có thể được approve ở tier thấp hơn nếu 60-80% requirements met.

**Acceptance Criteria:**
- [ ] **Score calculation:**
  - Total requirements: N
  - Passed requirements: P
  - Score: P/N
- [ ] **Tier assignment:**
  - Gold (100%): Max 3 posts, 100% reward
  - Silver (≥80%): Max 2 posts, 85% reward
  - Bronze (≥60%): Max 1 post, 70% reward
  - Rejected (<60%): Cannot participate
- [ ] UserEvent.approvalTier = 'gold' | 'silver' | 'bronze'
- [ ] Content submission limit enforced per tier
- [ ] Payment calculation adjusted by reward multiplier

**Dependencies:** FR-013, FR-016, payment system

**Related Insight:** Insight 6 - Partial Approval

---

#### FR-030: Fast-Track Paid Option

**Priority:** Could Have (Phase 2)

**Description:**
Users có thể pay 50k VND để expedite review (2-4 hours thay vì 1-2 days).

**Acceptance Criteria:**
- [ ] Checkbox khi submit application: "Fast-track review (+50k VND)"
- [ ] Payment integration
- [ ] Fast-track queue riêng (admin review priority)
- [ ] SLA: 90% reviewed within 4 hours

**Dependencies:** Payment system, FR-012

---

---

## Non-Functional Requirements

### Performance

#### NFR-001: Pre-Check Response Time

**Priority:** Must Have

**Description:**
Pre-registration eligibility checks phải instant để không block UI.

**Acceptance Criteria:**
- [ ] API response time: <100ms (p95)
- [ ] Database queries optimized với indexes
- [ ] Cache user profile data (TTL 5 minutes)

**Rationale:** User experience - instant feedback critical cho tier 1

**Related Insight:** Insight 1 - Two-Tier System

---

#### NFR-002: Admin Dashboard Load Time

**Priority:** Should Have

**Description:**
Admin dashboard queue phải load nhanh ngay cả với 100+ pending applications.

**Acceptance Criteria:**
- [ ] Initial page load: <500ms
- [ ] Pagination (20 items/page)
- [ ] Infinite scroll with lazy loading
- [ ] Database indexes on submittedAt, status

**Rationale:** Admin efficiency

---

#### NFR-003: File Upload Performance

**Priority:** Should Have

**Description:**
Screenshot uploads phải handle smoothly up to 5 files × 5MB.

**Acceptance Criteria:**
- [ ] Upload to cloud storage (S3/Cloudinary)
- [ ] Progress indicator during upload
- [ ] Client-side image compression before upload
- [ ] Parallel uploads (5 files simultaneously)
- [ ] Total upload time: <30 seconds for 5×5MB files

**Rationale:** User experience, prevent drop-off

---

### Security

#### NFR-004: OTP Security

**Priority:** Must Have

**Description:**
OTP verification phải secure để prevent brute force attacks.

**Acceptance Criteria:**
- [ ] OTP: 6 digits random
- [ ] Expiration: 5 minutes
- [ ] Rate limiting: Max 3 attempts per 15 minutes per user
- [ ] Bcrypt hash OTP before storing (không store plaintext)
- [ ] IP-based rate limiting (prevent distributed attacks)

**Rationale:** Security, prevent fraud

**Related Insight:** Insight 2 - Profile Completion Gate

---

#### NFR-005: Admin Authorization

**Priority:** Must Have

**Description:**
Chỉ authorized admins có quyền approve/reject applications.

**Acceptance Criteria:**
- [ ] Role-based access control (RBAC)
- [ ] Roles: 'admin', 'moderator', 'viewer'
- [ ] Permissions:
  - admin: approve, reject, override
  - moderator: approve, reject (no override)
  - viewer: view only
- [ ] Audit log: Who approved/rejected what, when

**Rationale:** Security, accountability

---

#### NFR-006: Data Privacy & GDPR Compliance

**Priority:** Must Have

**Description:**
User data (email, phone, Facebook profile) phải comply với GDPR.

**Acceptance Criteria:**
- [ ] Explicit consent: User checkbox "Tôi đồng ý lưu trữ dữ liệu"
- [ ] Consent timestamp logged
- [ ] Right to access: User có thể xem data stored
- [ ] Right to deletion: User có thể request deletion
- [ ] Data encryption at rest (database level)
- [ ] Data encryption in transit (HTTPS only)

**Rationale:** Legal compliance, avoid fines

---

### Scalability

#### NFR-007: Horizontal Scaling

**Priority:** Should Have

**Description:**
System phải scale khi user base tăng từ 1,000 → 10,000 users/month.

**Acceptance Criteria:**
- [ ] Stateless API servers (có thể add more instances)
- [ ] Database read replicas cho heavy read operations (queue, checklist)
- [ ] Queue system (Redis/Bull) cho async tasks (OTP, notifications)
- [ ] CDN cho static assets (images, screenshots)

**Rationale:** Growth support

---

#### NFR-008: Database Design for Scale

**Priority:** Must Have

**Description:**
Database schema phải support large number of records.

**Acceptance Criteria:**
- [ ] Indexes on:
  - UserEvent.participationStatus
  - ParticipationReview.status, submittedAt
  - User.email, User.phone (unique)
  - Event.startDate, Event.endDate
- [ ] Archival strategy: Move completed reviews older than 6 months to archive table
- [ ] Partition large tables (if >10M records)

**Rationale:** Performance, cost optimization

---

### Reliability/Availability

#### NFR-009: API Uptime

**Priority:** Must Have

**Description:**
Participation validation APIs phải highly available.

**Acceptance Criteria:**
- [ ] Uptime target: 99.5% (business hours: 8am-10pm daily)
- [ ] Downtime allowed: ~3.6 hours/month
- [ ] Health check endpoints: `/health`, `/readiness`
- [ ] Monitoring: Alert if 5xx error rate >1%

**Rationale:** User trust, business continuity

---

#### NFR-010: Graceful Degradation

**Priority:** Should Have

**Description:**
Nếu Facebook Graph API down, system vẫn hoạt động với manual fallback.

**Acceptance Criteria:**
- [ ] API call timeout: 10 seconds
- [ ] Nếu timeout/error: Return `{ method: 'manual_required' }`
- [ ] Admin sees indicator: "API unavailable, manual input needed"
- [ ] System không crash, không block approval flow

**Rationale:** Resilience

**Related Insight:** Insight 3 - Hybrid Validation

---

#### NFR-011: Notification Delivery Guarantee

**Priority:** Should Have

**Description:**
Email/SMS notifications phải reliable delivery.

**Acceptance Criteria:**
- [ ] Queue-based delivery (Redis Bull)
- [ ] Retry mechanism: 3 attempts with exponential backoff
- [ ] Dead letter queue for failed deliveries
- [ ] Admin alert if delivery failure rate >5%
- [ ] Delivery success rate: >95%

**Rationale:** User communication critical

---

### Usability

#### NFR-012: Mobile Responsiveness

**Priority:** Must Have

**Description:**
Requirements checklist và application form phải responsive trên mobile (majority users are mobile).

**Acceptance Criteria:**
- [ ] Responsive design: Desktop, tablet, mobile
- [ ] Touch-friendly UI (buttons ≥44px tap target)
- [ ] File upload works on mobile browsers
- [ ] Test on: iOS Safari, Android Chrome
- [ ] Page load <3 seconds on 4G

**Rationale:** User base là mobile-first

---

#### NFR-013: Accessibility (WCAG)

**Priority:** Should Have

**Description:**
UI phải accessible cho users với disabilities.

**Acceptance Criteria:**
- [ ] WCAG 2.1 Level AA compliance
- [ ] Color contrast ratio ≥4.5:1
- [ ] Keyboard navigation support
- [ ] Screen reader compatible (ARIA labels)
- [ ] Focus indicators visible

**Rationale:** Inclusivity, legal compliance

---

#### NFR-014: Browser Compatibility

**Priority:** Must Have

**Description:**
Support các browsers phổ biến ở Vietnam.

**Acceptance Criteria:**
- [ ] Chrome (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Edge (latest 2 versions)
- [ ] No IE11 support (deprecated)

**Rationale:** User coverage >98%

---

### Maintainability

#### NFR-015: Code Quality Standards

**Priority:** Should Have

**Description:**
Codebase phải maintainable và testable.

**Acceptance Criteria:**
- [ ] ESLint + Prettier configured
- [ ] TypeScript strict mode enabled
- [ ] Code review required (≥1 approval)
- [ ] No console.log in production
- [ ] Meaningful variable/function names

**Rationale:** Long-term maintainability

---

#### NFR-016: Testing Coverage

**Priority:** Should Have

**Description:**
Critical flows phải có test coverage.

**Acceptance Criteria:**
- [ ] Unit tests: Coverage ≥70%
- [ ] Integration tests cho critical APIs:
  - Pre-checks API
  - Participation submission
  - Admin approve/reject
  - Re-validation at reconciliation
- [ ] E2E tests cho happy paths (Playwright/Cypress)

**Rationale:** Confidence khi deploy, prevent regressions

---

#### NFR-017: API Documentation

**Priority:** Must Have

**Description:**
APIs phải có clear documentation cho frontend/admin devs.

**Acceptance Criteria:**
- [ ] OpenAPI/Swagger spec generated
- [ ] Request/response examples
- [ ] Error codes documented
- [ ] Postman collection exported
- [ ] Auto-generate docs from code (Swagger UI)

**Rationale:** Developer experience

---

### Compatibility

#### NFR-018: Backward Compatibility

**Priority:** Must Have

**Description:**
Existing events without participation requirements phải vẫn hoạt động bình thường.

**Acceptance Criteria:**
- [ ] Event.participationRequirements.enabled default = false
- [ ] Nếu disabled: Skip all tier 1 & tier 2 checks
- [ ] Content submission flow unchanged cho old events
- [ ] Migration script để add field cho existing events

**Rationale:** Không break production

---

#### NFR-019: Facebook API Integration

**Priority:** Must Have

**Description:**
Integrate với Facebook Graph API version stable.

**Acceptance Criteria:**
- [ ] Use Facebook Graph API v18.0+ (stable version)
- [ ] Endpoints:
  - `GET /{page-id}?fields=followers_count`
  - `GET /{user-id}?fields=friends_count`
- [ ] Handle rate limits gracefully (600 calls/hour)
- [ ] Exponential backoff on 429 errors
- [ ] Token refresh mechanism

**Rationale:** Follower count auto-validation

**Related Insight:** Insight 3 - Hybrid Validation

---

---

## Epics

### EPIC-001: Tier 1 - Pre-Registration Eligibility System

**Description:**
Implement instant auto-checks để filter users không đủ điều kiện cơ bản TRƯỚC khi cho phép submit participation application.

**Functional Requirements:**
- FR-001: Account Age Validation
- FR-002: Email/Phone Existence Check
- FR-003: Account Status Check
- FR-004: Facebook Account Linked Check
- FR-005: Pre-Check Aggregation & UI Display

**Story Count Estimate:** 6-10 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- Admin workload giảm 40% (không review users không đủ điều kiện)
- User experience tốt hơn (instant feedback)

**Related Insights:** Insight 1 - Two-Tier System

---

### EPIC-002: Tier 2 - Post-Registration Validation System

**Description:**
Implement application submission flow + admin review workflow để validate chất lượng influencer.

**Functional Requirements:**
- FR-005: Participation Application Submission
- FR-006: Email OTP Verification
- FR-007: Phone OTP Verification
- FR-008: Facebook Profile Quality Review
- FR-009: Follower Count Validation (Hybrid)
- FR-010: Authentic Posts Check
- FR-011: Invitation Code Validation

**Story Count Estimate:** 10-15 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- Quality assurance (chỉ influencers thật được approved)
- Partner trust tăng

**Related Insights:** Insight 1, 3 (Hybrid Validation)

---

### EPIC-003: Admin Review Dashboard & Tools

**Description:**
Build admin dashboard với review queue, batch tools, và analytics.

**Functional Requirements:**
- FR-012: Admin Review Queue
- FR-013: Admin Approve Application
- FR-014: Admin Reject Application
- FR-015: Batch Approval Tool
- FR-025: Admin Analytics Dashboard

**Story Count Estimate:** 8-12 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- Admin efficiency (fast review workflow)
- Visibility (metrics, SLA monitoring)

**Related Insights:** Insight 3, 4 (Clear SLA)

---

### EPIC-004: Content Submission Gate & Re-Validation

**Description:**
Integrate participation validation vào existing content submission flow + implement re-validation at reconciliation.

**Functional Requirements:**
- FR-016: Content Submission Gate
- FR-017: Follower Count Re-Validation
- FR-018: Account Status Re-Check

**Story Count Estimate:** 4-6 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- Prevent unauthorized content submissions
- Fraud prevention (re-validation prevents exploitation)

**Related Insights:** Insight 7 - Re-Validation

---

### EPIC-005: Event Configuration & Templates

**Description:**
Admin tools để config participation requirements per event với templates.

**Functional Requirements:**
- FR-019: Event-Level Participation Requirements Config
- FR-020: Requirements Template System

**Story Count Estimate:** 3-5 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- Flexibility (mỗi campaign config khác nhau)
- Efficiency (reuse templates)

**Related Insights:** All insights (foundation)

---

### EPIC-006: User Experience & Communication

**Description:**
UI/UX cho requirements checklist + status tracking + notifications.

**Functional Requirements:**
- FR-021: Requirements Checklist UI
- FR-022: Application Status Tracking UI
- FR-023: Email Notifications
- FR-024: In-App Notifications

**Story Count Estimate:** 6-10 stories

**Priority:** Must Have (Phase 1)

**Business Value:**
- User satisfaction (transparency, clear communication)
- Support tickets giảm 50-60%

**Related Insights:** Insight 4 - Clear SLA Communication

---

### EPIC-007: Analytics & Reporting

**Description:**
Dashboards cho admin và partners để monitor system performance.

**Functional Requirements:**
- FR-025: Admin Analytics Dashboard (already in EPIC-003)
- FR-026: Partner Reporting

**Story Count Estimate:** 3-5 stories

**Priority:** Should Have (Phase 1-2)

**Business Value:**
- Data-driven decisions
- Partner confidence

---

### EPIC-008: Advanced Features (Phase 2)

**Description:**
Profile completion gate, creator badges, partial approval tiers.

**Functional Requirements:**
- FR-027: Profile Completion Gate (Tier 0)
- FR-028: Verified Creator Badge System
- FR-029: Partial Approval Tiers
- FR-030: Fast-Track Paid Option

**Story Count Estimate:** 8-12 stories

**Priority:** Could Have (Phase 2)

**Business Value:**
- Long-term UX improvement (Tier 0)
- Retention (badges reward loyal creators)
- Revenue (fast-track option)

**Related Insights:** Insight 2, 5, 6

---

---

## High-Level User Stories

### EPIC-001 Stories (Sample)

**US-001:** Pre-Check Account Age
> As a system, I want to instantly check user account age when they view event requirements, so that I can block ineligible users early.

**US-002:** Display Pre-Check Results
> As a user, I want to see which basic requirements I pass/fail instantly, so that I know if I can proceed with application.

**US-003:** Enable/Disable Application Button
> As a system, I want to enable "Đăng ký tham gia" button only when all pre-checks pass, so that I prevent invalid applications.

---

### EPIC-002 Stories (Sample)

**US-010:** Submit Participation Application
> As a user, I want to submit my Facebook profile and screenshots, so that admin can review my eligibility.

**US-011:** Admin Review Facebook Profile
> As an admin, I want to view user's Facebook profile in review queue, so that I can assess legitimacy and post quality.

**US-012:** Auto-Fetch Follower Count
> As a system, I want to call Facebook Graph API to fetch follower count automatically, so that I reduce manual admin work.

---

### EPIC-003 Stories (Sample)

**US-020:** View Pending Applications Queue
> As an admin, I want to see list of pending applications sorted by submission time, so that I can review in FIFO order.

**US-021:** Approve Application
> As an admin, I want to approve qualified applications with one click, so that users can start submitting content.

**US-022:** Batch Approve Multiple Applications
> As an admin, I want to approve multiple applications at once, so that I can process faster during peak times.

---

### EPIC-004 Stories (Sample)

**US-030:** Block Content Submission if Not Approved
> As a system, I want to check participation approval status before allowing content creation, so that only qualified users can submit.

**US-031:** Re-Validate Follower Count at Payment
> As a system, I want to re-check follower count before payment reconciliation, so that I prevent fake follower exploitation.

---

### EPIC-005 Stories (Sample)

**US-040:** Configure Event Requirements
> As an admin, I want to enable/disable participation requirements per event, so that I have flexibility for different campaigns.

**US-041:** Save Requirements Template
> As an admin, I want to save requirement configs as reusable templates, so that I don't reconfigure for similar events.

---

### EPIC-006 Stories (Sample)

**US-050:** Display Requirements Checklist
> As a user, I want to see visual checklist of requirements with pass/fail indicators, so that I know exactly what I need to do.

**US-051:** Track Application Status
> As a user, I want to see my application status with estimated review time, so that I know when to expect results.

**US-052:** Receive Email Notification on Approval
> As a user, I want to receive email when my application is approved, so that I can start submitting content immediately.

---

---

## Key User Flows

### Flow 1: Happy Path - User Application → Approval → Content Submission

```
1. User navigates to Event Detail page
   ↓
2. System runs Tier 1 pre-checks (instant)
   → Account age: ✅ 2 years
   → Email exists: ✅
   → Phone exists: ✅
   ↓
3. Button "Đăng ký tham gia" enabled
   ↓
4. User clicks button → Modal opens
   ↓
5. User fills form:
   → Facebook URL: https://facebook.com/user123
   → Uploads 3 screenshots
   → Enters invitation code (optional)
   ↓
6. User clicks "Gửi hồ sơ"
   ↓
7. System creates ParticipationReview (status: pending)
   ↓
8. User sees confirmation: "Dự kiến duyệt trong 1-2 ngày"
   ↓
9. Application enters admin review queue
   ↓
10. Admin opens application in dashboard
    ↓
11. System auto-fetches follower count via Facebook API: 1,500 ✅
    ↓
12. Admin manually reviews:
    → Profile legitimacy: ✅ Real person
    → Post quality: ✅ Authentic content
    ↓
13. Admin clicks "Duyệt hồ sơ"
    ↓
14. System updates:
    → UserEvent.participationStatus = 'approved'
    → Sends email notification to user
    ↓
15. User receives email: "Hồ sơ đã được duyệt"
    ↓
16. User navigates back to event page
    ↓
17. User clicks "Gửi bài viết"
    ↓
18. System checks participationStatus === 'approved' → Allow
    ↓
19. User submits Facebook post link
    ↓
20. Content published → Tracked → Payment reconciliation
```

---

### Flow 2: Rejection Path - User Fails Manual Checks

```
1-10. [Same as Flow 1]
    ↓
11. System auto-fetch follower count: 800 (requirement: 1000) ❌
    ↓
12. Admin manually reviews:
    → Profile legitimacy: ✅
    → Post quality: ❌ Most posts are spam links
    ↓
13. Admin clicks "Từ chối"
    ↓
14. Modal opens: Admin enters reason
    → "Follower count không đủ (800/1000)"
    → "Bài đăng chủ yếu là spam link"
    ↓
15. System updates:
    → UserEvent.participationStatus = 'rejected'
    → Sends email notification
    ↓
16. User receives email với lý do cụ thể
    ↓
17. User có thể:
    → Appeal (contact support)
    → Fix issues (tăng followers, improve content) → Resubmit sau 30 days
```

---

### Flow 3: Re-Validation at Payment Reconciliation

```
1. User đã approved, submitted 3 posts, posts approved
   ↓
2. Payment reconciliation trigger (end of campaign)
   ↓
3. System re-checks follower count:
   → Original (lúc approved): 1,500
   → Current: 1,350
   → Drop: 10%
   ↓
4. Drop ≤10% → PASS (within grace period)
   ↓
5. Payment proceeds normally
   ↓

ALTERNATE: Suspicious Drop
3b. System re-checks:
    → Original: 1,500
    → Current: 900
    → Drop: 40% ❌
    ↓
4b. Drop >30% → FAIL
    ↓
5b. System:
    → Marks payment as 'requires_review'
    → Alerts admin
    → Notifies user: "Follower count giảm bất thường, payment pending investigation"
    ↓
6b. Admin investigates:
    → Reviews user history
    → Checks if legitimate reason (e.g., fanpage renamed)
    → Manual decision: Approve or reject payment
```

---

---

## Dependencies

### Internal Dependencies

**DEP-001: User Model**
- Schema có `email`, `phone`, `createdAt`, `status` fields
- Ownership: User Service

**DEP-002: Event Model**
- Schema có `participationRequirements` object field
- Ownership: Event Service

**DEP-003: Content Submission Service**
- Content.Create() API cần update để check participation status
- Ownership: Content Service

**DEP-004: Payment Reconciliation Service**
- Reconciliation flow cần integrate re-validation hooks
- Ownership: Payment Service

**DEP-005: Notification Service**
- Email sending service (SMTP/SendGrid)
- SMS sending service (Twilio)
- In-app notification system
- Ownership: Notification Service

**DEP-006: Authentication & Authorization**
- Admin role-based access control (RBAC)
- JWT token validation
- Ownership: Auth Service

---

### External Dependencies

**DEP-007: Facebook Graph API**
- Endpoint: `GET /{page-id}?fields=followers_count`
- Rate limits: 600 calls/hour
- Cost: Free (within limits)
- Risk: API có thể down/change → Mitigation: Manual fallback

**DEP-008: SMS Provider**
- Twilio hoặc local Vietnamese provider
- Cost: ~500 VND/SMS
- Volume: ~1,000 SMS/month (OTP)

**DEP-009: Email Provider**
- SendGrid hoặc SMTP server
- Cost: Free tier (10k emails/month) or paid
- Deliverability: >95%

**DEP-010: Cloud Storage (File Uploads)**
- AWS S3, Cloudinary, or similar
- Cost: ~$5/month for 100GB storage + bandwidth
- Purpose: Store user-uploaded screenshots

**DEP-011: Frontend Repository**
- Path: `accesstrade-projects/ambassabor/frontend`
- Need coordination để build UI components

**DEP-012: Admin Repository**
- Path: `accesstrade-projects/ambassabor/admin`
- Need coordination để build admin dashboard

---

---

## Assumptions

**ASMP-001: Facebook Profile Requirement**
Assume users có Facebook profile và willing to share. Nếu không có Facebook → Không thể tham gia (acceptable trade-off).

**ASMP-002: Admin Availability**
Assume có admin available để review 1-2 days SLA. Nếu holiday/weekend → Queue có thể tồn đọng (acceptable).

**ASMP-003: Email/Phone Ownership**
Assume users có quyền sở hữu email/phone nhập vào. System không verify ownership ngoài OTP.

**ASMP-004: Facebook API Stability**
Assume Facebook Graph API có uptime >90%. Nếu API down lâu → Manual fallback vẫn functional.

**ASMP-005: User Literacy**
Assume users có thể upload screenshots và nhập Facebook URL. Nếu không biết → Có hướng dẫn (tooltips, help text).

**ASMP-006: Network Connectivity**
Assume users có stable internet để upload files. Nếu mất kết nối giữa chừng → User retry.

**ASMP-007: Browser Support**
Assume users dùng modern browsers (Chrome, Safari, Firefox, Edge). Không support IE11.

**ASMP-008: Existing User Base**
Assume hệ thống đã có users và events. Migration cần backward compatibility (existing events không bị break).

**ASMP-009: Admin Training**
Assume admins sẽ được train về criteria review (profile quality, authentic posts). Documentation cần rõ ràng.

**ASMP-010: Budget Approval**
Assume development budget 226M VND + operational 10M VND/month đã approved. Nếu không → Cần adjust scope.

---

---

## Out of Scope

**OOS-001: Instagram/TikTok Integration**
Phase 1 chỉ support Facebook. Instagram/TikTok validation deferred to Phase 3.

**OOS-002: AI-Powered Auto-Review**
AI model để auto-review profile quality, post spam detection → Phase 3 research.

**OOS-003: Video Verification**
User record video selfie để verify identity → Out of scope (too complex).

**OOS-004: KYC (Know Your Customer)**
Government ID verification (CCCD/Passport) → Out of scope.

**OOS-005: Blockchain/NFT Verification**
Blockchain-based identity or NFT badges → Out of scope (unnecessary complexity).

**OOS-006: Multi-Language Support**
Phase 1 chỉ Vietnamese. English/other languages → Phase 4.

**OOS-007: Mobile App (Native)**
Phase 1 chỉ web responsive. Native iOS/Android apps → Future.

**OOS-008: Influencer Marketplace**
Matching influencers với brands, bidding system → Separate project.

**OOS-009: Advanced Analytics (ML)**
Predictive fraud detection, user churn prediction → Phase 3+.

**OOS-010: White-Label Solution**
Allowing other companies to use this system → Not in roadmap.

---

---

## Open Questions

**Q-001: Re-Validation Frequency?**
- Question: Ngoài payment reconciliation, có cần re-validate định kỳ không? (e.g., mỗi 3 tháng)
- Impact: System complexity, API calls cost
- Decision needed by: Architecture phase
- Owner: Product Manager + Tech Lead

**Q-002: Appeal Process Details?**
- Question: Nếu user bị reject, appeal process như thế nào? Admin nào review appeal? SLA?
- Impact: Support workload, user satisfaction
- Decision needed by: Sprint planning
- Owner: Product Manager

**Q-003: Partner Access Level?**
- Question: Partners (Techcombank, VinFast) có thể tự review applications không? Hay chỉ xem reports?
- Impact: Authorization model, UI complexity
- Decision needed by: Architecture phase
- Owner: Product Manager + Partner stakeholders

**Q-004: Data Retention Policy?**
- Question: Screenshots và application data lưu bao lâu? Delete sau bao lâu? GDPR compliance?
- Impact: Storage cost, legal compliance
- Decision needed by: Before implementation
- Owner: Legal team + Product Manager

**Q-005: Invitation Code Management?**
- Question: Ai tạo invitation codes? Partners tự tạo hay admin tạo? Có expiration date không?
- Impact: Feature scope, admin tools
- Decision needed by: Sprint planning
- Owner: Product Manager

**Q-006: Fast-Track SLA Guarantee?**
- Question: Nếu offer fast-track paid option, có guarantee SLA không? Nếu không meet SLA thì refund?
- Impact: Operational commitment, customer support
- Decision needed by: Phase 2 (nếu implement FR-030)
- Owner: Business Owner + Product Manager

**Q-007: Partial Approval Communication?**
- Question: Với partial approval tiers (bronze/silver/gold), làm sao communicate rõ ràng limitations? User có confused không?
- Impact: UX, user satisfaction
- Decision needed by: Phase 2 (nếu implement FR-029)
- Owner: Product Manager + UX Designer

**Q-008: Spot Check Frequency for Gold Creators?**
- Question: Gold creators có instant approval nhưng spot check 10%. Spot check như thế nào? Random? Frequency?
- Impact: Fraud risk vs efficiency trade-off
- Decision needed by: Phase 2 (nếu implement FR-028)
- Owner: Product Manager + Risk team

---

---

## Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Estimate | Phase | Priority |
|---------|-----------|------------------------|----------------|-------|----------|
| EPIC-001 | Tier 1 Pre-Registration Eligibility | FR-001, FR-002, FR-003, FR-004 | 5-8 stories | 1 | Must Have |
| EPIC-002 | Tier 2 Post-Registration Validation | FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011 | 10-15 stories | 1 | Must Have |
| EPIC-003 | Admin Review Dashboard & Tools | FR-012, FR-013, FR-014, FR-015, FR-025 | 8-12 stories | 1 | Must Have |
| EPIC-004 | Content Submission Gate & Re-Validation | FR-016, FR-017, FR-018 | 4-6 stories | 1 | Must Have |
| EPIC-005 | Event Configuration & Templates | FR-019, FR-020 | 3-5 stories | 1 | Must Have |
| EPIC-006 | User Experience & Communication | FR-021, FR-022, FR-023, FR-024 | 6-10 stories | 1 | Must Have |
| EPIC-007 | Analytics & Reporting | FR-025, FR-026 | 3-5 stories | 1-2 | Should Have |
| EPIC-008 | Advanced Features | FR-027, FR-028, FR-029, FR-030 | 8-12 stories | 2 | Could Have |

**Total Story Estimate:** 47-73 stories

**Phase 1 (Must Have):** 36-56 stories
**Phase 2 (Should/Could Have):** 11-17 stories

---

## Prioritization Summary

### Functional Requirements Breakdown

**Total FRs:** 30

**Priority Distribution:**
- **Must Have:** 22 FRs (73%)
  - EPIC-001: 4 FRs
  - EPIC-002: 7 FRs
  - EPIC-003: 5 FRs
  - EPIC-004: 3 FRs
  - EPIC-005: 2 FRs
  - EPIC-006: 1 FR

- **Should Have:** 5 FRs (17%)
  - EPIC-002: 1 FR (FR-011 Invitation Code)
  - EPIC-003: 1 FR (FR-015 Batch Approval)
  - EPIC-006: 3 FRs (FR-022, FR-023, FR-024)

- **Could Have:** 3 FRs (10%)
  - EPIC-005: 1 FR (FR-020 Templates)
  - EPIC-007: 1 FR (FR-026 Partner Reporting)
  - EPIC-008: 4 FRs (FR-027 to FR-030)

---

### Non-Functional Requirements Breakdown

**Total NFRs:** 19

**Priority Distribution:**
- **Must Have:** 12 NFRs (63%)
  - Performance: NFR-001
  - Security: NFR-004, NFR-005, NFR-006
  - Scalability: NFR-008
  - Reliability: NFR-009
  - Usability: NFR-012, NFR-014
  - Maintainability: NFR-017
  - Compatibility: NFR-018, NFR-019

- **Should Have:** 7 NFRs (37%)
  - Performance: NFR-002, NFR-003
  - Reliability: NFR-010, NFR-011
  - Usability: NFR-013
  - Maintainability: NFR-015, NFR-016

---

### Implementation Phases

**Phase 1: MVP (Must Have) - Week 1-5**
Focus: Core two-tier validation system
- Epics: 1, 2, 3, 4, 5, 6 (partial)
- Stories: ~36-56 stories
- Timeline: 5 weeks
- Team: 1 Backend Dev, 1 Frontend Dev, 0.5 QA

**Phase 2: Enhancement (Should Have) - Week 6-8**
Focus: Advanced features, optimization
- Epics: 6 (complete), 7, 8 (partial)
- Stories: ~11-17 stories
- Timeline: 3 weeks
- Team: Same

**Phase 3: Future (Could Have) - TBD**
Focus: AI/ML, integrations, scale
- Instagram/TikTok support
- AI-powered review
- Advanced analytics

---

---

## Success Criteria Summary

### Phase 1 Success Criteria (MVP Launch)

**Functional Completeness:**
- [ ] All Must-Have FRs implemented (22/22)
- [ ] Core user flow working end-to-end (Flow 1)
- [ ] Admin review workflow functional
- [ ] Re-validation at reconciliation working

**Performance:**
- [ ] Pre-check API response time <100ms
- [ ] Admin dashboard load <500ms
- [ ] File uploads <30s for 5 files

**Quality:**
- [ ] Zero critical bugs
- [ ] Test coverage ≥70%
- [ ] Code review approved

**Business Metrics:**
- [ ] Fraud rate reduced to <8% (target <5% sau 3 months)
- [ ] Admin workload giảm ≥30% (target 40%)
- [ ] Support tickets giảm ≥40% (target 50-60%)

**User Acceptance:**
- [ ] Pilot test với 100 users (Techcombank mini-campaign)
- [ ] User feedback score ≥3.5/5
- [ ] No major UX complaints

---

### Phase 2 Success Criteria (Full Launch)

**Feature Completeness:**
- [ ] All Should-Have FRs implemented
- [ ] Profile completion gate (Tier 0) working
- [ ] Creator badge system functional

**Business Metrics:**
- [ ] Fraud rate <5% sustained
- [ ] Admin workload giảm 40%
- [ ] Support tickets giảm 50-60%
- [ ] ROI campaign >200%
- [ ] Payment success rate >95%

**Scalability:**
- [ ] System handles 5,000 users/month smoothly
- [ ] Admin dashboard responsive với 500+ pending applications

---

---

## Stakeholders

### Primary Stakeholders

**STK-001: Product Owner**
- Name: TBD
- Role: Final approval on requirements, priorities
- Involvement: High (weekly review)

**STK-002: Tech Lead**
- Name: TBD
- Role: Architecture decisions, technical feasibility
- Involvement: High (daily during Phase 1)

**STK-003: Business Owner / CEO**
- Name: TBD
- Role: Budget approval, strategic direction
- Involvement: Medium (milestone reviews)

---

### Secondary Stakeholders

**STK-004: Partner - Techcombank Marketing Team**
- Contact: Mr. Tuấn (Brand Manager)
- Interest: Quality assurance, fraud prevention
- Involvement: Medium (requirements validation, pilot test)

**STK-005: Partner - VinFast**
- Contact: TBD
- Interest: Influencer quality, brand safety
- Involvement: Low-Medium (requirements input)

**STK-006: Content Operations Team (Admins)**
- Size: 3-5 admins
- Interest: Efficient review workflow, clear criteria
- Involvement: High (UAT, training)

**STK-007: Customer Support Team**
- Size: 2-3 agents
- Interest: Reduced support tickets, clear documentation
- Involvement: Medium (documentation review, escalation paths)

---

### Tertiary Stakeholders

**STK-008: Legal/Compliance Team**
- Interest: GDPR compliance, data privacy
- Involvement: Low (review before launch)

**STK-009: Finance Team**
- Interest: Budget, ROI tracking
- Involvement: Low (quarterly reviews)

**STK-010: UX Designer**
- Name: TBD
- Interest: User experience, wireframes
- Involvement: Medium (Phase 1 design)

---

---

## Appendix

### Related Documents

1. **Brainstorming Session:** `.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md`
   - 7 key insights
   - 21 ideas from SCAMPER
   - Root cause analysis (5 Whys)

2. **Executive Summary:** `accesstrade-projects/docs/participation-requirements/00-SUMMARY.md`
   - Business case
   - ROI calculation
   - Timeline

3. **Technical Analysis:** `accesstrade-projects/docs/participation-requirements/02-code-audit.md`
   - Code audit findings
   - Edge cases
   - Implementation recommendations

4. **Configuration Examples:** `accesstrade-projects/docs/participation-requirements/03-requirements-config-examples.md`
   - Database schemas
   - UI mockups
   - Event configs

5. **PM Response:** `accesstrade-projects/docs/participation-requirements/PM-RESPONSE-TO-REQUIREMENTS.md`
   - Detailed analysis
   - Solution architecture
   - User flows

---

### Glossary

**Tier 1:** Pre-registration eligibility checks (auto, instant)

**Tier 2:** Post-registration validation (manual admin review)

**Tier 0:** (Optional) Platform-level profile completion gate

**Pre-checks:** Auto-validation điều kiện cơ bản (account age, email/phone exists)

**Post-validation:** Manual validation chất lượng influencer (profile, posts)

**Hard block:** Requirements không thể bypass (e.g., account too young)

**Soft reject:** Applications bị reject nhưng có thể appeal/resubmit

**Hybrid validation:** Kết hợp auto (API) và manual (admin input) fallback

**Re-validation:** Check lại điều kiện tại payment reconciliation

**Grace period:** Cho phép follower count drop 10% (natural fluctuation)

**FIFO:** First In First Out (review queue strategy)

**SLA:** Service Level Agreement (e.g., 90% reviewed within 2 days)

**MoSCoW:** Must Have, Should Have, Could Have, Won't Have (prioritization framework)

**FR:** Functional Requirement

**NFR:** Non-Functional Requirement

**EPIC:** Large body of work grouping related user stories

---

### Acronyms

- **PRD:** Product Requirements Document
- **FR:** Functional Requirement
- **NFR:** Non-Functional Requirement
- **MVP:** Minimum Viable Product
- **ROI:** Return on Investment
- **SLA:** Service Level Agreement
- **OTP:** One-Time Password
- **GDPR:** General Data Protection Regulation
- **API:** Application Programming Interface
- **UI:** User Interface
- **UX:** User Experience
- **RBAC:** Role-Based Access Control
- **SMS:** Short Message Service
- **SMTP:** Simple Mail Transfer Protocol
- **CDN:** Content Delivery Network
- **WCAG:** Web Content Accessibility Guidelines
- **FIFO:** First In First Out

---

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 07/02/2026 | BMAD Creative Intelligence | Initial PRD creation |

---

## Approval Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | __________ | __________ | ______ |
| Tech Lead | __________ | __________ | ______ |
| Business Owner | __________ | __________ | ______ |
| Partner Representative (Techcombank) | __________ | __________ | ______ |

---

**Next Steps:**

1. ✅ Review PRD với stakeholders (1 week)
2. ⏳ Get approval sign-off from Product Owner, Tech Lead, Business Owner
3. ⏳ Handoff to System Architect → `/bmad:architecture`
4. ⏳ Architecture design (1 week)
5. ⏳ Sprint planning → `/bmad:sprint-planning`
6. ⏳ Development start (Week 1)

---

*Document generated by BMAD Method v6 - Product Manager Agent*
*Last Updated: 07/02/2026*
*Status: Draft - Awaiting Approval*
