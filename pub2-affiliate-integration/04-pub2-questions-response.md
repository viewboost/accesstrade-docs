# Trả lời Câu hỏi Pub2 - Integration Details

**Date:** 2026-02-07
**Người nhận:** Pub2 Team (AccessTrade)
**Người gửi:** AccessTrade Team (cho Ambassador, TCB, Vinfast partners)
**Related Documents:**
- [01-brainstorming-session.md](./01-brainstorming-session.md)
- [02-architecture-decisions.md](./02-architecture-decisions.md)
- [03-admin-campaign-management.md](./03-admin-campaign-management.md)

---

## Tóm tắt Executive

Tài liệu này trả lời chi tiết các câu hỏi của Pub2 về integration với 3 partners riêng biệt: **Techcombank, Ambassador, Vinfast**.

**⚠️ QUAN TRỌNG - Business Model:**
- **Pub2 có 3 separate partners:** TCB_001, AMB_001, VF_001
- **Mỗi partner tự quản lý:** Own API key, billing, influencers
- **AccessTrade (AT):**
  - Sở hữu Ambassador platform (AMB_001)
  - Phát triển source code bán cho TCB/Vinfast (work-for-hire)
  - KHÔNG involved trong operations sau delivery
- **ViewBoost:** Chỉ là outsource developer cho AT, KHÔNG tham gia operations

**Câu hỏi tập trung vào:**
1. **Account Linking:** Cơ chế liên kết influencer ↔ Pub2 publisher (per partner)
2. **Campaign Distribution:** Cách mỗi partner tổ chức campaigns riêng

Tất cả giải pháp đã được phân tích trong các documents trước, tài liệu này dẫn chứng cụ thể.

---

## Phần I: UI/UX & Action Flows

### ⚠️ TODO: Cần bổ sung Mockups

**Câu hỏi từ Pub2:**
> "Cần bổ sung chi tiết giao diện? => Yêu cầu bổ sung"
> "Action flow từng bước thế nào? => Yêu cầu bổ sung"

**Trạng thái:**
- ✅ **Đã có:** Wireframes dạng ASCII trong các documents (xem bên dưới)
- ⏳ **Cần bổ sung:** High-fidelity mockups (Figma/Sketch)

**References hiện có:**

1. **Influencer Portal UI**
   - Document: [02-architecture-decisions.md - Section: Decision 3](./02-architecture-decisions.md#decision-3-influencer-portal-display)
   - Nội dung:
     - Dashboard Overview (Total earnings, View vs Affiliate breakdown)
     - Campaign Browser (Filtered campaigns, Generate link UI)
     - My Affiliate Links (Performance table)
     - Affiliate Analytics (Charts, metrics)
     - Payout History (Transaction breakdown)

2. **Admin Campaign Management UI**
   - Document: [03-admin-campaign-management.md - Section: UI/UX Design](./03-admin-campaign-management.md#uiux-design)
   - Nội dung:
     - Campaign List Dashboard
     - Browse Pub2 Campaigns (Search, filter, competitor warnings)
     - Campaign Form (Add/Edit with approval workflow)
     - Approval Dashboard (Pending approvals queue)

**Action Items:**
- [ ] Tạo Figma mockups cho Influencer Portal (5 pages)
- [ ] Tạo Figma mockups cho Admin Panel (4 pages)
- [ ] Bổ sung vào document sau khi complete

**Tạm thời:** Pub2 có thể refer wireframes trong documents hiện tại để hiểu flow.

---

## Phần II: Account Linking (Matching Tài khoản)

### Câu hỏi 1.1: Cơ chế liên kết tài khoản giữa 2 hệ thống

**Reference:** [02-architecture-decisions.md - Decision 2: User Balance](./02-architecture-decisions.md#decision-2-user-balance--transactions)

#### Kiến trúc Tổng quan

```
┌─────────────────────────────────────────────────────────┐
│  Partner Platform (Techcombank/Ambassador/Vinfast)     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Influencer Account:                                    │
│  - influencer_id: UUID (Platform primary key)           │
│  - email: alice@example.com                             │
│  - phone: +84912345678                                  │
│  - identity_number: CCCD (optional)                     │
│  - tenant_id: 'tcb' | 'ambassador' | 'vinfast'          │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ LINKING TABLE
                 ▼
┌─────────────────────────────────────────────────────────┐
│  influencer_pub2_accounts (Mapping Table)               │
├─────────────────────────────────────────────────────────┤
│  - id: UUID                                             │
│  - influencer_id: UUID (FK to influencers)              │
│  - pub2_user_id: VARCHAR(100) (Pub2's publisher ID)     │
│  - link_status: 'active' | 'inactive' | 'pending'       │
│  - link_method: 'oauth' | 'email_match' | 'manual'      │
│  - linked_at: TIMESTAMP                                 │
│  - consent_given: BOOLEAN (GDPR/PDPA compliance)        │
│  - consent_at: TIMESTAMP                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Pub2's publisher_id
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Pub2 System (AccessTrade)                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Publisher Account:                                     │
│  - publisher_id: "PUB_12345" (Pub2's ID)                │
│  - email: alice@example.com (matching key)              │
│  - account_status: 'active'                             │
│  - partner_id: 'TCB_001' | 'AMB_001' | 'VF_001'         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Matching Criteria (Tiêu chí liên kết)

**Priority Order:**

1. **OAuth Flow** (Recommended, most secure)
   ```
   Influencer clicks "Link Pub2 Account"
   → Redirect to Pub2 OAuth
   → Influencer authorizes (TCB/AMB/VF platform)
   → Pub2 returns publisher_id + email
   → Platform stores mapping
   ```
   - **Pros:** Explicit consent, secure, no manual matching
   - **Cons:** Requires Pub2 OAuth support

2. **Email Matching** (Fallback)
   ```
   Platform queries Pub2 API: GET /publishers?email={influencer.email}
   → If match found: Store publisher_id
   → If no match: Prompt influencer to create Pub2 account
   ```
   - **Pros:** Simple, works if emails match
   - **Cons:** Risk false positives nếu email khác nhau

3. **Phone Matching** (Additional layer)
   ```
   If email không match, try phone:
   GET /publishers?phone={influencer.phone}
   ```

4. **CCCD Matching** (Vietnam-specific, for compliance)
   ```
   GET /publishers?identity_number={influencer.cccd}
   ```
   - **Note:** Requires Pub2 stores CCCD (may not exist)

5. **Manual Linking** (Admin override)
   ```
   Admin panel: Enter Pub2 publisher_id manually
   → Store in influencer_pub2_accounts
   → Require admin approval
   ```

#### Database Schema

```sql
CREATE TABLE influencer_pub2_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- at-core side
  influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
  tenant_id VARCHAR(50) NOT NULL,  -- Which tenant this linking belongs to

  -- Pub2 side
  pub2_user_id VARCHAR(100) NOT NULL,  -- Pub2's publisher_id
  pub2_email VARCHAR(255),  -- Cached from Pub2
  pub2_account_status VARCHAR(20),  -- 'active' | 'suspended' | 'inactive'

  -- Linking metadata
  link_status VARCHAR(20) DEFAULT 'active' CHECK (link_status IN ('active', 'inactive', 'pending', 'failed')),
  link_method VARCHAR(20) CHECK (link_method IN ('oauth', 'email_match', 'phone_match', 'cccd_match', 'manual')),

  -- Compliance (GDPR/PDPA)
  consent_given BOOLEAN DEFAULT false,
  consent_text TEXT,  -- What user agreed to
  consent_at TIMESTAMP,

  -- Audit trail
  linked_at TIMESTAMP DEFAULT NOW(),
  linked_by UUID,  -- Admin user if manual linking
  unlinked_at TIMESTAMP,
  unlinked_reason TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(influencer_id, pub2_user_id)
);

CREATE INDEX idx_pub2_accounts_influencer ON influencer_pub2_accounts(influencer_id);
CREATE INDEX idx_pub2_accounts_pub2_user ON influencer_pub2_accounts(pub2_user_id);
CREATE INDEX idx_pub2_accounts_status ON influencer_pub2_accounts(link_status);
```

---

### Câu hỏi 1.2: Tính hợp pháp & Căn cứ pháp lý (Login bằng tài khoản AT)

**Reference:** [02-architecture-decisions.md - Security & Compliance](./02-architecture-decisions.md#security--compliance)

#### Căn cứ Pháp lý

**1. GDPR/PDPA Compliance**

```
Quy trình:
┌─────────────────────────────────────────────────────────┐
│  STEP 1: User Consent (Mandatory)                       │
├─────────────────────────────────────────────────────────┤
│  Before linking Pub2 account, influencer must see:      │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ 📋 Consent Form                               │     │
│  │                                               │     │
│  │ Bạn đồng ý cho phép:                          │     │
│  │                                               │     │
│  │ ☑ Techcombank Creator Platform liên kết với  │     │
│  │   tài khoản AccessTrade (Pub2) của bạn       │     │
│  │                                               │     │
│  │ ☑ Chia sẻ thông tin: Email, Họ tên           │     │
│  │                                               │     │
│  │ ☑ Đồng bộ dữ liệu: Clicks, Conversions,      │     │
│  │   Commission từ Pub2 để hiển thị trong       │     │
│  │   Techcombank Creator Dashboard              │     │
│  │                                               │     │
│  │ ⓘ Bạn có thể hủy liên kết bất cứ lúc nào     │     │
│  │                                               │     │
│  │ [Đồng ý] [Hủy]                                │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  Stored in: influencer_pub2_accounts.consent_given     │
│             influencer_pub2_accounts.consent_text      │
│             influencer_pub2_accounts.consent_at        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  STEP 2: Data Processing Agreement                     │
├─────────────────────────────────────────────────────────┤
│  Legal doc giữa:                                        │
│  - AccessTrade/Pub2 (data controller)                   │
│  - Techcombank/Ambassador/Vinfast (data controller)    │
│                                                         │
│  Quy định:                                              │
│  - Pub2 data ONLY used for affiliate tracking          │
│  - No sharing to third parties                         │
│  - User can request deletion (GDPR right to be forgot) │
│  - Data retention: 2 years (configurable)              │
└─────────────────────────────────────────────────────────┘
```

**2. OAuth 2.0 Standard (Industry best practice)**

```
Login bằng AccessTrade (OAuth Flow):

┌─────────────────────────────────────────────────────────┐
│  Influencer clicks "Liên kết tài khoản AccessTrade"    │
│                                                         │
│  ↓                                                      │
│  Redirect to Pub2 OAuth:                               │
│  https://pub2.vn/oauth/authorize                       │
│    ?client_id=tcb_app_12345                            │
│    &redirect_uri=https://tcb.creator.vn/oauth/callback │
│    &response_type=code                                 │
│    &scope=publisher.read,affiliate.manage              │
│    &state=random_csrf_token                            │
│                                                         │
│  ↓                                                      │
│  Pub2 shows login page:                                │
│  ┌───────────────────────────────────────────────┐     │
│  │ 🔐 AccessTrade Login                          │     │
│  │                                               │     │
│  │ Email: [alice@example.com______________]      │     │
│  │ Password: [********************]              │     │
│  │                                               │     │
│  │ [Đăng nhập]                                   │     │
│  │                                               │     │
│  │ ⓘ Techcombank Creator muốn truy cập:         │     │
│  │ • Thông tin tài khoản Publisher              │     │
│  │ • Tạo affiliate links                         │     │
│  │ • Xem clicks và conversions                   │     │
│  │                                               │     │
│  │ [Cho phép] [Từ chối]                          │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  ↓ (User clicks "Cho phép")                            │
│                                                         │
│  Redirect back to at-core:                             │
│  https://tcb.creator.vn/oauth/callback                 │
│    ?code=AUTH_CODE_123                                 │
│    &state=random_csrf_token                            │
│                                                         │
│  ↓                                                      │
│  TCB Platform exchanges code for access_token:         │
│  POST https://pub2.vn/oauth/token                      │
│    code=AUTH_CODE_123                                  │
│    client_id=tcb_app_12345                             │
│    client_secret=SECRET                                │
│                                                         │
│  ↓                                                      │
│  Pub2 returns:                                         │
│  {                                                     │
│    "access_token": "ACCESS_TOKEN_XYZ",                 │
│    "publisher_id": "PUB_12345",                        │
│    "email": "alice@example.com",                       │
│    "expires_in": 3600                                  │
│  }                                                     │
│                                                         │
│  ↓                                                      │
│  TCB Platform stores in influencer_pub2_accounts:      │
│  - influencer_id: [current influencer]                 │
│  - pub2_user_id: "PUB_12345"                           │
│  - link_method: 'oauth'                                │
│  - consent_given: true                                 │
│                                                         │
│  ✓ Liên kết thành công!                                │
└─────────────────────────────────────────────────────────┘
```

**Tính hợp pháp:**
- ✅ OAuth 2.0 = Industry standard, secure
- ✅ Explicit user consent (GDPR Article 6)
- ✅ Transparent về data usage
- ✅ User có quyền revoke bất cứ lúc nào

**3. Alternative: Email-based Linking (if OAuth not available)**

```
┌─────────────────────────────────────────────────────────┐
│  Email Matching Flow                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STEP 1: User enters email                             │
│  ┌───────────────────────────────────────────────┐     │
│  │ Liên kết tài khoản AccessTrade                │     │
│  │                                               │     │
│  │ Email AccessTrade của bạn:                    │     │
│  │ [alice@example.com______________]             │     │
│  │                                               │     │
│  │ [Tiếp tục]                                    │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 2: Platform queries Pub2 API                     │
│  GET /api/publishers?email=alice@example.com           │
│                                                         │
│  IF FOUND:                                              │
│  Response: { "publisher_id": "PUB_12345", ... }        │
│  → Send verification email to alice@example.com        │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ 📧 Email Verification                         │     │
│  │                                               │     │
│  │ To: alice@example.com                         │     │
│  │ From: noreply@tcb.creator.vn                  │     │
│  │                                               │     │
│  │ Subject: Xác nhận liên kết AccessTrade        │     │
│  │                                               │     │
│  │ Xin chào Alice,                               │     │
│  │                                               │     │
│  │ Bạn đã yêu cầu liên kết tài khoản             │     │
│  │ AccessTrade với Techcombank Creator.          │     │
│  │                                               │     │
│  │ Mã xác nhận: 123456                           │     │
│  │                                               │     │
│  │ Hoặc click: [Xác nhận liên kết]               │     │
│  │                                               │     │
│  │ Mã có hiệu lực trong 15 phút.                 │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 3: User enters verification code                 │
│  → Link confirmed → Store in DB                        │
│                                                         │
│  IF NOT FOUND:                                          │
│  → Prompt: "Không tìm thấy tài khoản AccessTrade.      │
│     Vui lòng đăng ký tại pub2.vn"                      │
└─────────────────────────────────────────────────────────┘
```

**Tính hợp pháp:**
- ✅ Email verification = Proof of ownership
- ✅ 2-factor confirmation (email + code)
- ⚠️ Less secure than OAuth (phishing risk)
- ✅ GDPR compliant nếu có consent form

---

### Câu hỏi 1.3: Auto Onboarding & Matching Logic (CCCD, Email, Phone)

**Reference:** [02-architecture-decisions.md - Implementation Code](./02-architecture-decisions.md#implementation-code)

#### Matching Algorithm

```typescript
// services/AccountLinking.service.ts

interface MatchingResult {
  matched: boolean;
  pub2UserId?: string;
  matchMethod: 'oauth' | 'email' | 'phone' | 'cccd' | 'manual' | 'none';
  confidence: number;  // 0-100
}

class AccountLinkingService {

  /**
   * Auto-match influencer với Pub2 account
   */
  async autoMatchPub2Account(
    influencerId: string,
    tenantId: string
  ): Promise<MatchingResult> {
    const influencer = await db.influencers.findOne({ id: influencerId });
    const tenantConfig = await getTenantPub2Config(tenantId);

    // Priority 1: Check if already linked
    const existing = await db.influencer_pub2_accounts.findOne({
      influencer_id: influencerId,
      link_status: 'active'
    });

    if (existing) {
      return {
        matched: true,
        pub2UserId: existing.pub2_user_id,
        matchMethod: existing.link_method,
        confidence: 100
      };
    }

    // Priority 2: Email matching
    if (influencer.email) {
      const emailMatch = await this.matchByEmail(
        influencer.email,
        tenantConfig.pub2ApiKey
      );

      if (emailMatch.found) {
        return {
          matched: true,
          pub2UserId: emailMatch.pub2UserId,
          matchMethod: 'email',
          confidence: 90  // High confidence if email exact match
        };
      }
    }

    // Priority 3: Phone matching
    if (influencer.phone) {
      const phoneMatch = await this.matchByPhone(
        influencer.phone,
        tenantConfig.pub2ApiKey
      );

      if (phoneMatch.found) {
        return {
          matched: true,
          pub2UserId: phoneMatch.pub2UserId,
          matchMethod: 'phone',
          confidence: 80  // Medium-high confidence
        };
      }
    }

    // Priority 4: CCCD matching (Vietnam-specific)
    if (influencer.identity_number) {
      const cccdMatch = await this.matchByCCCD(
        influencer.identity_number,
        tenantConfig.pub2ApiKey
      );

      if (cccdMatch.found) {
        return {
          matched: true,
          pub2UserId: cccdMatch.pub2UserId,
          matchMethod: 'cccd',
          confidence: 95  // Very high confidence for CCCD
        };
      }
    }

    // No match found
    return {
      matched: false,
      matchMethod: 'none',
      confidence: 0
    };
  }

  /**
   * Match by email
   */
  private async matchByEmail(email: string, apiKey: string) {
    try {
      const response = await pub2Client.searchPublishers(apiKey, {
        email: email
      });

      if (response.publishers.length === 1) {
        return {
          found: true,
          pub2UserId: response.publishers[0].id
        };
      } else if (response.publishers.length > 1) {
        // Multiple matches - ambiguous, require manual resolution
        console.warn(`Multiple Pub2 accounts found for email: ${email}`);
        return { found: false };
      } else {
        return { found: false };
      }
    } catch (error) {
      console.error('Email matching failed:', error);
      return { found: false };
    }
  }

  /**
   * Match by phone
   */
  private async matchByPhone(phone: string, apiKey: string) {
    // Normalize phone number (remove +84, spaces, etc.)
    const normalizedPhone = this.normalizePhoneNumber(phone);

    try {
      const response = await pub2Client.searchPublishers(apiKey, {
        phone: normalizedPhone
      });

      if (response.publishers.length === 1) {
        return {
          found: true,
          pub2UserId: response.publishers[0].id
        };
      } else {
        return { found: false };
      }
    } catch (error) {
      console.error('Phone matching failed:', error);
      return { found: false };
    }
  }

  /**
   * Match by CCCD (Vietnam Identity Number)
   */
  private async matchByCCCD(cccd: string, apiKey: string) {
    try {
      const response = await pub2Client.searchPublishers(apiKey, {
        identity_number: cccd
      });

      if (response.publishers.length === 1) {
        return {
          found: true,
          pub2UserId: response.publishers[0].id
        };
      } else {
        return { found: false };
      }
    } catch (error) {
      console.error('CCCD matching failed:', error);
      return { found: false };
    }
  }

  /**
   * Normalize phone number for matching
   */
  private normalizePhoneNumber(phone: string): string {
    // Remove country code, spaces, dashes
    // +84 912 345 678 → 0912345678
    let normalized = phone.replace(/\s+/g, '').replace(/-/g, '');

    if (normalized.startsWith('+84')) {
      normalized = '0' + normalized.substring(3);
    } else if (normalized.startsWith('84')) {
      normalized = '0' + normalized.substring(2);
    }

    return normalized;
  }

  /**
   * Store matched account (after verification)
   */
  async storeLinking(
    influencerId: string,
    pub2UserId: string,
    method: string,
    consentGiven: boolean = false
  ) {
    await db.influencer_pub2_accounts.create({
      influencer_id: influencerId,
      pub2_user_id: pub2UserId,
      link_method: method,
      link_status: consentGiven ? 'active' : 'pending',
      consent_given: consentGiven,
      consent_at: consentGiven ? new Date() : null
    });
  }
}
```

#### Auto-Onboarding Flow

```
┌─────────────────────────────────────────────────────────┐
│  Scenario: New Influencer Signs Up on Techcombank       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STEP 1: Influencer registers                          │
│  - Email: alice@example.com                             │
│  - Phone: +84 912 345 678                               │
│  - CCCD: 001234567890 (optional)                        │
│                                                         │
│  STEP 2: Platform runs auto-match                       │
│  → Call autoMatchPub2Account(influencerId, 'tcb')      │
│                                                         │
│  STEP 3a: IF MATCH FOUND (email/phone/cccd)            │
│  ┌───────────────────────────────────────────────┐     │
│  │ 🎉 Tìm thấy tài khoản AccessTrade!            │     │
│  │                                               │     │
│  │ Email: alice@example.com                      │     │
│  │ Publisher ID: PUB_12345                       │     │
│  │                                               │     │
│  │ Bạn có muốn liên kết để nhận commission      │     │
│  │ từ affiliate marketing không?                 │     │
│  │                                               │     │
│  │ [Có, liên kết ngay] [Để sau]                  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  → If "Có":                                             │
│    - Send verification email/SMS                       │
│    - User confirms → Link active                       │
│    - Update influencer_pub2_accounts table             │
│                                                         │
│  STEP 3b: IF NO MATCH                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │ ⓘ Chưa có tài khoản AccessTrade                │     │
│  │                                               │     │
│  │ Để sử dụng affiliate marketing, bạn cần      │     │
│  │ đăng ký tài khoản Publisher tại AccessTrade.  │     │
│  │                                               │     │
│  │ [Đăng ký AccessTrade] [Bỏ qua]               │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  → If "Đăng ký":                                        │
│    Option A: Redirect to Pub2 signup                   │
│    Option B: Embedded signup (iframe/API)              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Edge Cases:**

1. **Multiple Matches:**
   ```
   Email matches 2+ Pub2 accounts
   → Manual resolution required
   → Admin panel: Select correct publisher_id
   ```

2. **Partial Matches:**
   ```
   Email matches, but phone different
   → Confidence 70% → Require email verification
   ```

3. **No Match, but user claims has account:**
   ```
   → Manual linking flow
   → User enters Pub2 publisher_id
   → Verification email sent to both sides
   ```

---

### Câu hỏi 1.4: SSO và Brand Protection (Ambassador không muốn show "Login AT")

**Reference:** [02-architecture-decisions.md - Decision 1: Partner Structure](./02-architecture-decisions.md#decision-1-pub2-partner-structure)

#### Vấn đề Brand Identity

```
Scenario: Ambassador không muốn influencers thấy "Login bằng AccessTrade"
Lý do: Ảnh hưởng white-label branding
```

#### Giải pháp: Multi-Tenant OAuth với Custom Branding

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  Option 1: Tenant-Branded OAuth (RECOMMENDED)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Techcombank Portal:                                    │
│  ┌───────────────────────────────────────────────┐     │
│  │ 🔐 Liên kết tài khoản Affiliate               │     │
│  │                                               │     │
│  │ Để sử dụng tính năng affiliate marketing,    │     │
│  │ vui lòng liên kết tài khoản.                  │     │
│  │                                               │     │
│  │ [Liên kết tài khoản] ← Generic wording       │     │
│  └───────────────────────────────────────────────┘     │
│  → Redirect to: https://affiliate.techcombank.vn/oauth │
│     (Subdomain của TCB, NOT pub2.vn)                   │
│                                                         │
│  Ambassador Portal:                                     │
│  ┌───────────────────────────────────────────────┐     │
│  │ 🔗 Connect Affiliate Account                  │     │
│  │                                               │     │
│  │ Enable affiliate commissions by connecting    │     │
│  │ your account.                                 │     │
│  │                                               │     │
│  │ [Connect Account] ← No "AccessTrade" mention │     │
│  └───────────────────────────────────────────────┘     │
│  → Redirect to: https://affiliate.ambassador.io/oauth  │
│                                                         │
└─────────────────────────────────────────────────────────┘

Technical Implementation:
┌─────────────────────────────────────────────────────────┐
│  1. Pub2 configures custom OAuth domains per tenant:   │
│     - TCB: affiliate.techcombank.vn → CNAME to Pub2    │
│     - AMB: affiliate.ambassador.io → CNAME to Pub2     │
│                                                         │
│  2. Pub2 OAuth page shows tenant branding:              │
│     - TCB tenant: Blue theme, TCB logo                  │
│     - AMB tenant: Red theme, AMB logo                   │
│     - NO "AccessTrade" branding visible                 │
│                                                         │
│  3. OAuth callback returns to tenant domain:            │
│     - tcb.creator.vn/oauth/callback                     │
│     - ambassador.io/oauth/callback                      │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```typescript
// OAuth configuration per tenant
const oauthConfig = {
  'tcb': {
    authUrl: 'https://affiliate.techcombank.vn/oauth/authorize',
    tokenUrl: 'https://affiliate.techcombank.vn/oauth/token',
    clientId: 'tcb_app_12345',
    clientSecret: process.env.TCB_OAUTH_SECRET,
    redirectUri: 'https://tcb.creator.vn/oauth/callback',
    branding: {
      buttonText: 'Liên kết tài khoản Affiliate',
      logoUrl: 'https://tcb.creator.vn/logo.png',
      primaryColor: '#0066CC'
    }
  },
  'ambassador': {
    authUrl: 'https://affiliate.ambassador.io/oauth/authorize',
    tokenUrl: 'https://affiliate.ambassador.io/oauth/token',
    clientId: 'amb_app_67890',
    clientSecret: process.env.AMB_OAUTH_SECRET,
    redirectUri: 'https://ambassador.io/oauth/callback',
    branding: {
      buttonText: 'Connect Affiliate Account',
      logoUrl: 'https://ambassador.io/logo.png',
      primaryColor: '#FF6B6B'
    }
  }
};

// Frontend: Dynamic button text
function OAuthButton({ tenantId }: { tenantId: string }) {
  const config = oauthConfig[tenantId];

  return (
    <button
      onClick={() => window.location.href = config.authUrl}
      style={{ backgroundColor: config.branding.primaryColor }}
    >
      {config.branding.buttonText}
    </button>
  );
}
```

---

**Option 2: Backend-Only Integration (No User-Facing OAuth)**

```
┌─────────────────────────────────────────────────────────┐
│  Alternative: Silent Linking (No OAuth UI)             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Flow:                                                  │
│  1. Influencer registers on Ambassador                  │
│     → Email: alice@example.com                          │
│                                                         │
│  2. at-core backend auto-queries Pub2:                  │
│     GET /publishers?email=alice@example.com            │
│                                                         │
│  3a. IF FOUND:                                          │
│     → Send verification email (branded as Ambassador)   │
│     → User clicks confirm link                          │
│     → Backend stores linking silently                   │
│     → No "AccessTrade" ever shown to user              │
│                                                         │
│  3b. IF NOT FOUND:                                      │
│     Option A: Auto-create Pub2 account via API         │
│       POST /publishers (if Pub2 supports)              │
│       → Link automatically                              │
│                                                         │
│     Option B: Prompt user (generic wording)            │
│       "Enable affiliate features? [Yes/No]"            │
│       → Redirect to white-labeled signup               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Zero "AccessTrade" branding visible
- ✅ Seamless UX (user không biết backend là Pub2)
- ✅ Full white-label

**Cons:**
- ⚠️ Requires Pub2 API support auto account creation
- ⚠️ Less explicit consent (GDPR concern) → Need clear terms

---

#### Decision Matrix

| Aspect | Branded OAuth | Silent Linking |
|--------|---------------|----------------|
| White-label | ✅ Good (custom domain) | ✅✅ Excellent (invisible) |
| GDPR Compliance | ✅✅ Explicit consent | ⚠️ Requires clear terms |
| Implementation | Medium (Pub2 config needed) | High (API support needed) |
| Security | ✅✅ OAuth 2.0 standard | ✅ Secure if done right |
| User Trust | ✅ Transparent | ⚠️ "Magic" linking may confuse |

**Recommendation cho Ambassador:**
- **Phase 1 (MVP):** Branded OAuth với custom domain
- **Phase 2:** Silent linking nếu Pub2 hỗ trợ API account creation

---

## Phần III: Campaign Distribution (Phân phối Campaign)

### Câu hỏi 2.1: Tổ chức và quản lý campaigns cho từng đối tượng

**Reference:** [03-admin-campaign-management.md - Full Document](./03-admin-campaign-management.md)

#### Architecture Tổng quan

```
┌─────────────────────────────────────────────────────────┐
│  Pub2 System: 1000+ campaigns (All partners)           │
│  - Banking: 200+                                        │
│  - Automotive: 150+                                     │
│  - Insurance: 100+                                      │
│  - E-commerce: 300+                                     │
│  - Food & Beverage: 150+                                │
│  - Others: 100+                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Manual Curation (NOT auto-sync)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  TENANT-SPECIFIC CAMPAIGN CURATION                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Techcombank (TCB):                                     │
│  Admin browses Pub2 → Adds 15 curated campaigns         │
│  ┌───────────────────────────────────────────────┐     │
│  │ ✓ TCB Platinum Credit Card (pub2: camp_123)  │     │
│  │ ✓ Travel Insurance (pub2: camp_456)          │     │
│  │ ✓ Personal Loan (pub2: camp_789)             │     │
│  │ ... 12 more                                   │     │
│  │                                               │     │
│  │ ❌ Vietcombank Card (competitor, blocked)    │     │
│  │ ❌ Pizza Hut (irrelevant category)           │     │
│  └───────────────────────────────────────────────┘     │
│  → TCB influencers chỉ thấy 15 campaigns này            │
│                                                         │
│  Ambassador (AMB):                                      │
│  Admin adds 30 curated campaigns (broader scope)        │
│  ┌───────────────────────────────────────────────┐     │
│  │ ✓ Fashion Brand X (pub2: camp_111)           │     │
│  │ ✓ Beauty Product Y (pub2: camp_222)          │     │
│  │ ✓ Tech Gadget Z (pub2: camp_333)             │     │
│  │ ... 27 more                                   │     │
│  │                                               │     │
│  │ ❌ No competitor blocking (general platform) │     │
│  └───────────────────────────────────────────────┘     │
│  → AMB influencers see 30 diverse campaigns             │
│                                                         │
│  Vinfast (VF):                                          │
│  Admin adds 10 automotive-focused campaigns             │
│  ┌───────────────────────────────────────────────┐     │
│  │ ✓ Vinfast VF8 Accessories (pub2: camp_999)   │     │
│  │ ✓ Car Insurance (pub2: camp_888)             │     │
│  │ ✓ EV Charging Stations (pub2: camp_777)      │     │
│  │ ... 7 more                                    │     │
│  │                                               │     │
│  │ ❌ Toyota/Honda (competitors, blocked)       │     │
│  └───────────────────────────────────────────────┘     │
│  → VF influencers see 10 auto campaigns                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Admin Campaign Management Flow

**Reference:** [03-admin-campaign-management.md - Workflow 1](./03-admin-campaign-management.md#workflow-1-add-new-campaign)

```
TCB Admin adds campaign:
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Browse Pub2                                    │
│  Admin searches: "credit card"                          │
│  → Pub2 API returns 50 campaigns                        │
│  → at-core filters:                                     │
│    ✓ Show: Techcombank campaigns                       │
│    ⚠️ Warn: Vietcombank (competitor)                   │
│    ❌ Hide: Food campaigns (irrelevant)                │
│                                                         │
│  STEP 2: Select & Customize                             │
│  Admin clicks "Add" on "TCB Platinum Card"             │
│  → Form pre-filled from Pub2:                           │
│    - pub2_campaign_id: "camp_123"                       │
│    - Commission: 8.5%                                   │
│  → Admin customizes:                                    │
│    - Title: "Thẻ Tín Dụng Techcombank Platinum"        │
│    - Description: Vietnamese localized content          │
│    - Image: TCB-branded banner                          │
│    - Category: "Credit Card"                            │
│    - Featured: Yes (show on homepage)                   │
│                                                         │
│  STEP 3: Approval                                       │
│  Admin submits → Manager reviews → Approves             │
│  → Status = 'active'                                    │
│                                                         │
│  STEP 4: Publish                                        │
│  → TCB influencers now see this campaign                │
│  → Can generate affiliate links                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**

1. **Tenant Filtering Table:**
```sql
-- Automatic filtering based on tenant
SELECT * FROM campaigns
WHERE tenant_id = 'tcb'
  AND status = 'active'
ORDER BY display_order ASC, created_at DESC;

-- Result: Only TCB's curated campaigns
```

2. **Campaign Approval Workflow:**
```sql
campaign_approvals:
  - status: 'pending' → 'approved' → campaign.status = 'active'
  - status: 'rejected' → campaign.status = 'inactive'
  - status: 'changes_requested' → Editor re-submits
```

3. **Competitor Detection:**
```typescript
// Auto-warn admin if competitor
const competitorKeywords = {
  'tcb': ['vietcombank', 'bidv', 'vietinbank'],
  'vinfast': ['toyota', 'honda', 'hyundai']
};

function isCompetitor(merchantName: string, tenantId: string): boolean {
  const keywords = competitorKeywords[tenantId] || [];
  return keywords.some(k => merchantName.toLowerCase().includes(k));
}
```

---

### Câu hỏi 2.2: Cơ chế join campaign của người dùng

**Reference:** [02-architecture-decisions.md - Component 2: Campaign Browser](./02-architecture-decisions.md#component-2-campaign-browser)

#### Influencer Flow: Browse → Join → Generate Link

```
┌─────────────────────────────────────────────────────────┐
│  Influencer Portal: Campaign Browser                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STEP 1: Browse Available Campaigns                     │
│  ┌───────────────────────────────────────────────┐     │
│  │ 🔍 Search: [credit card__________] 🔍        │     │
│  │ Category: [All ▼] [Banking] [Insurance]      │     │
│  │ Sort: [Highest Commission ▼]                 │     │
│  │                                               │     │
│  │ Showing 15 campaigns (TCB approved)           │     │
│  │                                               │     │
│  │ ┌─────────────────────────────────────────┐  │     │
│  │ │ 🏦 Thẻ Tín Dụng Techcombank Platinum   │  │     │
│  │ │                                         │  │     │
│  │ │ [Banner Image]                          │  │     │
│  │ │                                         │  │     │
│  │ │ Lãi suất 0% trong 12 tháng đầu         │  │     │
│  │ │                                         │  │     │
│  │ │ Commission: 8.5% per approval           │  │     │
│  │ │ Your estimated earning: ~$42.50         │  │     │
│  │ │                                         │  │     │
│  │ │ Status: Active until Dec 31, 2026      │  │     │
│  │ │ Conversion Rate: 12.3% (High!)          │  │     │
│  │ │                                         │  │     │
│  │ │ [View Details] [Generate Link]          │  │     │
│  │ └─────────────────────────────────────────┘  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 2: Generate Affiliate Link (= "Join Campaign")   │
│  Influencer clicks "Generate Link"                      │
│                                                         │
│  → Backend flow:                                        │
│    1. Check influencer linked to Pub2 (pub2_user_id)   │
│    2. Call Pub2 API:                                    │
│       POST /affiliate-links                             │
│       {                                                 │
│         campaign_id: "camp_123",                        │
│         publisher_id: "PUB_12345",                      │
│         sub_id_1: "vid_abc123",  // video_id           │
│         sub_id_2: "tcb",         // tenant_id          │
│       }                                                 │
│    3. Pub2 returns:                                     │
│       { url: "https://pub2.vn/track/xyz?..." }         │
│    4. Store in Platform DB:                             │
│       pub2_affiliate_links table                        │
│    5. Return to influencer                              │
│                                                         │
│  → UI shows:                                            │
│  ┌───────────────────────────────────────────────┐     │
│  │ ✅ Link Generated!                            │     │
│  │                                               │     │
│  │ Your affiliate link:                          │     │
│  │ https://pub2.vn/track/xyz?camp=123&pub=...   │     │
│  │                                               │     │
│  │ [📋 Copy Link] [Add to Video]                │     │
│  │                                               │     │
│  │ ⓘ Paste this link in your video description  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 3: Track Performance                             │
│  Influencer navigates to "My Affiliate Links"           │
│  → See all generated links with stats:                  │
│    - Clicks: 234                                        │
│    - Conversions: 12                                    │
│    - Commission: $510                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key Points:**

- **"Join Campaign" = Generate Affiliate Link**
  - Không có explicit "Join" button
  - Action = Generate tracking link
  - Link creation = Participation

- **One Influencer, Multiple Links:**
  ```
  Influencer có thể generate nhiều links cho cùng campaign
  → Video 1: link_123 (for credit card review)
  → Video 2: link_456 (for comparison video)
  → Video 3: link_789 (for tutorial)
  ```

- **Campaign Visibility = Per-Partner Filtered:**
  ```typescript
  // Query campaigns for influencer
  // Each partner (TCB/AMB/VF) queries their own campaigns table
  const campaigns = await db.campaigns
    .where('tenant_id', influencer.tenant_id)
    .where('status', 'active')
    .where('start_date', '<=', new Date())
    .where('end_date', '>=', new Date())
    .orderBy('featured', 'desc')
    .orderBy('display_order', 'asc');

  // TCB influencer chỉ thấy TCB campaigns
  // AMB influencer chỉ thấy AMB campaigns
  // VF influencer chỉ thấy VF campaigns
  ```

---

### Câu hỏi 2.3: Hiển thị link, đơn hàng, report - Data isolation

**Reference:** [02-architecture-decisions.md - Decision 2: Separate Balance](./02-architecture-decisions.md#option-a-separate-balance-per-tenant)

#### Vấn đề: Ví dụ "hệ thống affiliate hiển thị trên dữ liệu của Ambassador"

**Scenario:**
```
Alice là influencer join cả TCB lẫn Ambassador
→ Alice có 1 Pub2 account (PUB_12345)
→ Alice generate links cho cả 2 tenants

Question:
- TCB portal có hiển thị Ambassador data không?
- Ambassador portal có thấy TCB data không?
```

**Answer: KHÔNG - Complete Tenant Isolation**

#### Data Isolation Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Alice's Pub2 Account (Backend - Single Account)       │
├─────────────────────────────────────────────────────────┤
│  pub2_user_id: PUB_12345                                │
│  Total Commission: $200                                 │
│                                                         │
│  Transactions:                                          │
│  1. Video vid_001 (sub_id_2='tcb')  → $85              │
│  2. Video vid_002 (sub_id_2='tcb')  → $35              │
│  3. Video vid_003 (sub_id_2='amb')  → $50              │
│  4. Video vid_004 (sub_id_2='amb')  → $30              │
└─────────────────────────────────────────────────────────┘
           │                           │
           │ Filtered by sub_id_2      │
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  TCB Portal          │    │  AMB Portal          │
│  (Alice logged in)   │    │  (Alice logged in)   │
├──────────────────────┤    ├──────────────────────┤
│  MY EARNINGS         │    │  MY EARNINGS         │
│  ────────────────    │    │  ────────────────    │
│  Affiliate: $120     │    │  Affiliate: $80      │
│  - Transaction 1: $85│    │  - Transaction 3: $50│
│  - Transaction 2: $35│    │  - Transaction 4: $30│
│                      │    │                      │
│  ❌ NO AMB data      │    │  ❌ NO TCB data      │
└──────────────────────┘    └──────────────────────┘
```

#### Implementation: Filtering Query

```typescript
// services/AffiliateEarnings.service.ts

/**
 * Get affiliate earnings for influencer
 * CRITICAL: Filter by tenant_id (sub_id_2)
 */
async function getAffiliateEarnings(
  influencerId: string,
  tenantId: string  // MUST pass tenant context
): Promise<EarningsData> {

  // Get all conversions for this influencer
  const conversions = await db.pub2_conversions
    .join('pub2_affiliate_links', 'pub2_conversions.link_id', 'pub2_affiliate_links.id')
    .join('videos', 'pub2_affiliate_links.video_id', 'videos.id')
    .where('pub2_affiliate_links.influencer_id', influencerId)
    .where('pub2_affiliate_links.sub_id_2', tenantId)  // ← CRITICAL FILTER
    .select('pub2_conversions.*');

  const totalCommission = conversions.reduce((sum, c) => sum + c.commission, 0);

  return {
    balance: totalCommission,
    conversions: conversions,
    tenant: tenantId  // Include for transparency
  };
}

/**
 * Get all affiliate links for influencer
 * Also filtered by tenant
 */
async function getAffiliateLinks(
  influencerId: string,
  tenantId: string
): Promise<AffiliateLink[]> {

  const links = await db.pub2_affiliate_links
    .join('videos', 'pub2_affiliate_links.video_id', 'videos.id')
    .where('pub2_affiliate_links.influencer_id', influencerId)
    .where('videos.tenant_id', tenantId)  // ← Videos belong to tenant
    .select('pub2_affiliate_links.*');

  return links;
}
```

#### UI: Tenant-Specific Dashboards

**TCB Portal (alice@example.com logged in):**
```
┌───────────────────────────────────────────────────────────┐
│  MY AFFILIATE PERFORMANCE - TECHCOMBANK                   │
├───────────────────────────────────────────────────────────┤
│  Commission Earned: $120                                  │
│                                                           │
│  Links Generated: 5                                       │
│  Total Clicks: 234                                        │
│  Conversions: 12                                          │
│                                                           │
│  Top Videos:                                              │
│  1. TCB Credit Card Review - $85 (12 conversions)         │
│  2. Savings Account Guide - $35 (3 conversions)           │
│                                                           │
│  ❌ Ambassador data KHÔNG hiển thị                        │
│  ❌ Không có info về $80 từ Ambassador                    │
└───────────────────────────────────────────────────────────┘
```

**Ambassador Portal (cùng alice@example.com logged in):**
```
┌───────────────────────────────────────────────────────────┐
│  MY AFFILIATE PERFORMANCE - AMBASSADOR                    │
├───────────────────────────────────────────────────────────┤
│  Commission Earned: $80                                   │
│                                                           │
│  Links Generated: 3                                       │
│  Total Clicks: 156                                        │
│  Conversions: 8                                           │
│                                                           │
│  Top Videos:                                              │
│  1. Fashion Brand Review - $50 (5 conversions)            │
│  2. Beauty Product Unboxing - $30 (3 conversions)         │
│                                                           │
│  ❌ Techcombank data KHÔNG hiển thị                       │
│  ❌ Không có info về $120 từ TCB                          │
└───────────────────────────────────────────────────────────┘
```

#### Warning System: Cross-Tenant Data Leak Prevention

```typescript
// Middleware: Enforce tenant context
app.use('/api/affiliate/*', async (req, res, next) => {
  const userId = req.user.id;
  const tenantId = req.user.tenant_id;  // From JWT or session

  // Inject tenant context into all queries
  req.tenantContext = tenantId;

  next();
});

// Controller: Always check tenant match
async function getAffiliateData(req, res) {
  const { influencerId } = req.params;
  const tenantId = req.tenantContext;

  // Verify influencer belongs to this tenant
  const influencer = await db.influencers.findOne({
    id: influencerId,
    tenant_id: tenantId  // Security check
  });

  if (!influencer) {
    return res.status(403).json({
      error: 'Forbidden: Cross-tenant access denied'
    });
  }

  // Proceed with tenant-filtered query
  const data = await getAffiliateEarnings(influencerId, tenantId);
  res.json(data);
}
```

#### Audit Logging: Detect Unauthorized Access Attempts

```typescript
// Log all affiliate data queries
async function logDataAccess(req) {
  await db.audit_logs.create({
    user_id: req.user.id,
    tenant_id: req.tenantContext,
    action: 'view_affiliate_data',
    resource: req.path,
    timestamp: new Date(),
    ip_address: req.ip
  });
}

// Alert if cross-tenant access attempted
if (influencer.tenant_id !== req.tenantContext) {
  await securityAlerts.send({
    type: 'cross_tenant_access_attempt',
    user_id: req.user.id,
    attempted_tenant: influencer.tenant_id,
    actual_tenant: req.tenantContext,
    severity: 'high'
  });
}
```

---

### Câu hỏi 2.4: Scenarios & Warnings

**Kịch bản có thể xảy ra:**

#### Scenario 1: Influencer Chuyển Tenant

```
Alice ban đầu là TCB influencer
→ Có 10 affiliate links, earn $500 từ TCB campaigns

Alice chuyển sang làm Ambassador influencer
→ TCB account inactive

Question: Alice có còn thấy $500 từ TCB không?

Answer:
Option A (Strict isolation):
  - Alice login Ambassador portal → KHÔNG thấy TCB data
  - $500 still exists in Pub2, but not visible in AMB portal
  - If Alice wants to see historical TCB data → Must contact TCB admin

Option B (Historical view):
  - Alice có "View Historical Earnings" page
  - Shows all tenants she ever belonged to (read-only)
  - TCB: $500 (archived)
  - AMB: $80 (current)
```

**Recommendation:** Option A (Strict) cho security, Option B nếu UX prioritized

---

#### Scenario 2: Campaign Ends on Pub2 but TCB Still Shows

```
TCB Admin adds campaign "camp_123" from Pub2
→ Status: Active

Pub2 campaign "camp_123" ends
→ pub2_campaign_status = 'ended'

TCB influencers vẫn thấy campaign trong browser

Question: Có hiển thị warning không?

Answer: YES - Auto-sync background job
┌───────────────────────────────────────────────┐
│  ⚠️ Campaign Ended on Pub2                   │
│                                               │
│  "TCB Platinum Card" campaign ended           │
│  on AccessTrade system.                       │
│                                               │
│  Existing links will still track, but new     │
│  sign-ups may not be accepted.                │
│                                               │
│  Contact admin for more info.                 │
└───────────────────────────────────────────────┘

Background job:
- Hourly check: Pub2 campaign status
- If ended → Update pub2_campaign_status
- Notify admin → Admin decides: Hide or Archive
```

---

#### Scenario 3: Influencer Generates Link for Competitor Campaign (Edge Case)

```
Scenario:
- Alice is TCB influencer
- Somehow gets access to Pub2 campaign "camp_999" (Vietcombank)
- Tries to generate link directly via Pub2 website

Question: TCB portal có track conversion không?

Answer: NO - TCB không thấy conversion

Reason:
- Campaign "camp_999" KHÔNG exist trong TCB's campaigns table
- Link generated outside TCB platform
- Conversion webhook từ Pub2:
  {
    "link_id": "link_abc",
    "sub_id_2": "???"  // No tenant marker
  }
- TCB platform receives webhook → Cannot map to campaign → Ignore

Prevention:
- Educate influencers: Only generate links via TCB portal
- TCB portal shows ONLY TCB-approved campaigns
- No way to access competitor campaigns via UI
```

---

### Câu hỏi 2.5: Khảo sát số lượng & Tỉ lệ convert

**Business Question từ Pub2:**
> "Cần khảo sát về số lượng ambassador user & mục tiêu tỉ lệ convert của ambassador sang pub"

#### Data Collection Plan

**Metrics to Track:**

```sql
-- Ambassador user statistics
CREATE TABLE tenant_user_stats (
  id UUID PRIMARY KEY,
  tenant_id VARCHAR(50),
  date DATE,

  -- User counts
  total_influencers INT,
  active_influencers INT,  -- Posted video in last 30 days

  -- Pub2 linking stats
  pub2_linked_count INT,
  pub2_pending_count INT,
  pub2_failed_count INT,

  -- Conversion funnel
  viewed_affiliate_page INT,  -- Visited campaign browser
  generated_link_count INT,   -- Created at least 1 link
  first_click_count INT,      -- Got at least 1 click
  first_conversion_count INT, -- Got at least 1 sale

  -- Calculated rates
  link_conversion_rate DECIMAL(5,2),  -- linked / total
  activation_rate DECIMAL(5,2),       -- generated_link / linked

  created_at TIMESTAMP DEFAULT NOW()
);
```

**Tracking Implementation:**

```typescript
// Daily aggregation job
async function calculateTenantStats(tenantId: string, date: Date) {
  const stats = {
    total_influencers: await db.influencers
      .where('tenant_id', tenantId)
      .count(),

    active_influencers: await db.influencers
      .where('tenant_id', tenantId)
      .whereExists(function() {
        this.select('*')
          .from('videos')
          .whereRaw('videos.influencer_id = influencers.id')
          .where('created_at', '>=', new Date(Date.now() - 30 * 86400000));
      })
      .count(),

    pub2_linked_count: await db.influencer_pub2_accounts
      .join('influencers', 'influencer_pub2_accounts.influencer_id', 'influencers.id')
      .where('influencers.tenant_id', tenantId)
      .where('link_status', 'active')
      .count(),

    generated_link_count: await db.influencers
      .where('tenant_id', tenantId)
      .whereExists(function() {
        this.select('*')
          .from('pub2_affiliate_links')
          .whereRaw('pub2_affiliate_links.influencer_id = influencers.id');
      })
      .count(),

    first_conversion_count: await db.influencers
      .where('tenant_id', tenantId)
      .whereExists(function() {
        this.select('*')
          .from('pub2_conversions')
          .join('pub2_affiliate_links', 'pub2_conversions.link_id', 'pub2_affiliate_links.id')
          .whereRaw('pub2_affiliate_links.influencer_id = influencers.id');
      })
      .count()
  };

  // Calculate rates
  stats.link_conversion_rate = stats.total_influencers > 0
    ? (stats.pub2_linked_count / stats.total_influencers) * 100
    : 0;

  stats.activation_rate = stats.pub2_linked_count > 0
    ? (stats.generated_link_count / stats.pub2_linked_count) * 100
    : 0;

  await db.tenant_user_stats.create({
    tenant_id: tenantId,
    date: date,
    ...stats
  });
}
```

**Dashboard for Pub2:**

```
┌───────────────────────────────────────────────────────────┐
│  PUB2 INTEGRATION METRICS - AMBASSADOR                    │
├───────────────────────────────────────────────────────────┤
│  Date Range: Last 30 Days                                 │
│                                                           │
│  FUNNEL METRICS                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Total Influencers:           3,500               │    │
│  │   ↓ Viewed Affiliate Page:   2,100 (60%)        │    │
│  │   ↓ Linked Pub2 Account:     1,400 (40% of 3.5K)│    │
│  │   ↓ Generated Links:           980 (70% of linked)│   │
│  │   ↓ Got First Click:           735 (75% of gen) │    │
│  │   ↓ Got First Conversion:      490 (67% of click)│   │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  KEY RATES                                                │
│  • Pub2 Link Rate: 40% (Target: 50%)                     │
│  • Activation Rate: 70% (Target: 80%)                    │
│  • Conversion Rate: 67% (Target: 60%) ✓ Exceeding       │
│                                                           │
│  TRENDS                                                   │
│  📊 [Line chart: Link rate over time]                    │
│                                                           │
│  RECOMMENDATIONS                                          │
│  • Increase Pub2 awareness: Add onboarding tutorial      │
│  • Simplify linking flow: Reduce to 2 clicks            │
│  • Incentivize first link: Bonus for first conversion    │
└───────────────────────────────────────────────────────────┘
```

**Conversion Targets (Example):**

```
Ambassador Platform Goals (Q1 2026):
┌─────────────────────────────────────────────────────┐
│  Metric              Current   Target   Status     │
├─────────────────────────────────────────────────────┤
│  Pub2 Link Rate      40%       50%      ⚠️ Gap    │
│  Activation Rate     70%       80%      ⚠️ Gap    │
│  First Conv Rate     67%       60%      ✓ Good    │
│  Monthly Active      980       1,200    ⚠️ Gap    │
└─────────────────────────────────────────────────────┘

Action Items:
1. A/B test: Simplified linking flow
2. Email campaign: "Earn extra with affiliate"
3. In-app tutorial: How to generate links
4. Incentive: $10 bonus for first conversion
```

---

## Phần IV: Summary & Next Steps

### Tóm tắt Trả lời

| Câu hỏi | Trả lời | Reference |
|---------|---------|-----------|
| **UI/UX Mockups** | ⏳ Cần bổ sung Figma designs | [02-architecture-decisions.md](./02-architecture-decisions.md), [03-admin-campaign-management.md](./03-admin-campaign-management.md) |
| **Action Flows** | ✅ Đã detail trong docs (wireframes) | Same as above |
| **Account Linking** | OAuth hoặc Email matching, GDPR compliant | [Section II.1](#câu-hỏi-11-cơ-chế-liên-kết-tài-khoản) |
| **Tính hợp pháp** | OAuth 2.0 standard + Explicit consent | [Section II.2](#câu-hỏi-12-tính-hợp-pháp--căn-cứ-pháp-lý) |
| **Auto Onboarding** | Email/Phone/CCCD matching + Verification | [Section II.3](#câu-hỏi-13-auto-onboarding--matching-logic) |
| **SSO Brand Protection** | Branded OAuth hoặc Silent linking | [Section II.4](#câu-hỏi-14-sso-và-brand-protection) |
| **Campaign Management** | Manual curation, tenant filtering | [Section III.1](#câu-hỏi-21-tổ-chức-và-quản-lý-campaigns) |
| **Join Campaign** | Generate affiliate link = participation | [Section III.2](#câu-hỏi-22-cơ-chế-join-campaign) |
| **Data Isolation** | Complete tenant separation via sub_id_2 | [Section III.3](#câu-hỏi-23-hiển-thị-link-đơn-hàng-report) |
| **Metrics & Targets** | Tracking funnel + conversion goals | [Section III.5](#câu-hỏi-25-khảo-sát-số-lượng--tỉ-lệ-convert) |

---

### Action Items cho Pub2

**Cần từ Pub2:**

1. **OAuth Support:**
   - [ ] Xác nhận Pub2 có hỗ trợ OAuth 2.0 không?
   - [ ] Nếu có: Cung cấp OAuth endpoints & scopes
   - [ ] Nếu chưa: Timeline để implement?

2. **API Endpoints Required:**
   - [ ] GET /publishers?email={email} (search by email)
   - [ ] GET /publishers?phone={phone} (search by phone)
   - [ ] GET /publishers?identity_number={cccd} (optional)
   - [ ] POST /affiliate-links (with sub_id_1, sub_id_2, sub_id_3)
   - [ ] Webhooks: clicks, conversions, commission_updates

3. **Custom Branding:**
   - [ ] Có support custom OAuth domain không?
     (e.g., affiliate.techcombank.vn → CNAME to Pub2)
   - [ ] Có cho phép white-label OAuth page không?

4. **Data & Metrics:**
   - [ ] Cung cấp test accounts để test matching logic
   - [ ] Confirm webhook payload format
   - [ ] Metrics dashboard access cho từng partner (TCB_001, AMB_001, VF_001)?

---

### Action Items cho Từng Partner

**Phase 1 (Design):**
- [ ] Tạo Figma mockups (Influencer Portal: 5 pages, Admin Panel: 4 pages)
- [ ] UX review với stakeholders
- [ ] Finalize account linking flow (OAuth vs Email)

**Phase 2 (Development):**
- [ ] Implement account linking service (OAuth + Email matching)
- [ ] Build campaign management admin panel
- [ ] Integrate Pub2 API (sandbox testing first)
- [ ] Setup webhook receivers + reconciliation jobs

**Phase 3 (Testing):**
- [ ] UAT với Pub2 test environment
- [ ] Test tenant isolation (ensure no data leak between partners)
- [ ] Load testing (1000+ influencers, 10K+ links)

**Phase 4 (Deployment):**
- [ ] Production deployment
  - TCB_001: Techcombank deployment
  - AMB_001: Ambassador deployment (AT-owned)
  - VF_001: Vinfast deployment
- [ ] Monitor metrics dashboard per partner
- [ ] Iterate based on conversion rates

---

### Timeline Estimate

```
Week 1-2:  Figma mockups + Pub2 API alignment
Week 3-4:  Account linking implementation
Week 5-6:  Campaign management implementation
Week 7-8:  Testing & UAT
Week 9:    TCB production deployment
Week 10+:  Monitor, optimize, expand to AMB/VF
```

---

**Document Owner:** AccessTrade Integration Team
**Date:** 2026-02-07
**Status:** Awaiting Pub2 Feedback
**Partners:** Techcombank (TCB_001), Ambassador (AMB_001), Vinfast (VF_001)
**Next Review:** After Pub2 confirms technical feasibility
