# Architecture Decisions - Pub2 Affiliate Integration

**Date:** 2026-02-07
**Status:** Decision Made
**Related:** [01-brainstorming-session.md](./01-brainstorming-session.md)

---

## Executive Summary

Tài liệu này phân tích 3 băn khoăn quan trọng về kiến trúc tích hợp Pub2 vào at-core platform, sau brainstorming session ban đầu. Các decisions này ảnh hưởng trực tiếp đến:

- **Business model:** Handover source code cho TCB/Vinfast
- **Data architecture:** Multi-tenant isolation
- **User experience:** Influencer portal design

---

## Table of Contents

1. [Decision 1: Pub2 Partner Structure](#decision-1-pub2-partner-structure)
2. [Decision 2: User Balance & Transactions](#decision-2-user-balance--transactions)
3. [Decision 3: Influencer Portal Display](#decision-3-influencer-portal-display)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Appendix: Code Examples](#appendix-code-examples)

---

## Decision 1: Pub2 Partner Structure

### 🎯 Question
**Pub2 nên biết Techcombank, Ambassador, Vinfast là 3 partners riêng biệt, hay chỉ biết 1 mình at-core?**

### Context
- **Business requirement:** AT bán source code cho TCB/Vinfast
- **Ownership:** TCB/Vinfast expect 100% control sau handover
- **Source code model:** Per BUSINESS-CONTEXT.md, AT delivers clean source code
- **Independence:** TCB không muốn dependency vào AT long-term

---

### Option A: 3 Separate Pub2 Partners ⭐ CHOSEN

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Pub2 System                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Partner: Techcombank (ID: TCB_001)                        │
│  ├─ API Key: tcb_prod_xxxxxxxxxxxxx                        │
│  ├─ Publisher Accounts: 1,200 influencers                  │
│  ├─ Commission Balance: $45,000                            │
│  └─ Billing: TCB pays Pub2 directly                        │
│                                                             │
│  Partner: Ambassador (ID: AMB_001)                         │
│  ├─ API Key: amb_prod_xxxxxxxxxxxxx                        │
│  ├─ Publisher Accounts: 3,500 influencers                  │
│  ├─ Commission Balance: $78,000                            │
│  └─ Billing: AT pays Pub2 directly                         │
│                                                             │
│  Partner: Vinfast (ID: VF_001)                             │
│  ├─ API Key: vf_prod_xxxxxxxxxxxxx                         │
│  ├─ Publisher Accounts: 800 influencers                    │
│  ├─ Commission Balance: $12,000                            │
│  └─ Billing: Vinfast pays Pub2 directly                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ▲              ▲              ▲
         │              │              │
         │              │              │
┌────────┴────┐  ┌──────┴──────┐  ┌───┴──────┐
│ at-core     │  │ at-core     │  │ at-core  │
│ (TCB)       │  │ (Ambassador)│  │ (Vinfast)│
│ Source Code │  │ Source Code │  │ Source   │
│ Delivered   │  │ (AT owned)  │  │ Delivered│
└─────────────┘  └─────────────┘  └──────────┘
```

#### Pros & Cons

**✅ Advantages:**

1. **Clean Source Code Handover**
   - TCB nhận source + own Pub2 API key
   - Zero dependency vào AT sau delivery
   - Self-sufficient operation

2. **Billing Independence**
   - TCB pays Pub2 directly (no middleman)
   - AT không involved trong TCB's Pub2 billing
   - Transparent cost structure

3. **Complete Data Isolation**
   - TCB data ≠ Vinfast data (separate Pub2 accounts)
   - Compliance-friendly (GDPR/PDPA)
   - No cross-tenant data leakage risk

4. **Commercial Flexibility**
   - TCB có thể negotiate commission rates riêng với Pub2
   - Custom SLA agreements
   - Independent roadmap priorities

5. **Exit Strategy**
   - Nếu AT ngừng maintain at-core → TCB/Vinfast vẫn hoạt động
   - No vendor lock-in
   - Full control over destiny

**❌ Disadvantages:**

1. **Setup Complexity**
   - Each tenant needs separate Pub2 onboarding
   - AT phải coordinate 3 setups (or more as platform scales)
   - Initial overhead

2. **Network Effect Limitation**
   - Influencer từ TCB có separate balance với Ambassador
   - Không share liquidity pool
   - Cross-tenant collaboration harder

3. **Pub2 Operational Load**
   - Pub2 manage 3 partners thay vì 1
   - More admin overhead for Pub2
   - May impact pricing

---

### Option B: Single Pub2 Partner (at-core)

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Pub2 System                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Partner: AccessTrade (ID: AT_001)                         │
│  ├─ API Key: at_core_prod_xxxxxxxxxxxxx (SHARED)          │
│  ├─ Publisher Accounts: 5,500 influencers (all tenants)   │
│  ├─ Commission Balance: $135,000 (aggregated)             │
│  └─ Billing: AT pays Pub2, invoices tenants               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
                          │
         ┌────────────────┴────────────────┐
         │      at-core Platform           │
         │  (Internal tenant filtering)    │
         └────────────────┬────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    │ Tenant  │     │ Tenant  │     │ Tenant  │
    │ TCB     │     │ AMB     │     │ Vinfast │
    │ Filter: │     │ Filter: │     │ Filter: │
    │ sub_id_2│     │ sub_id_2│     │ sub_id_2│
    │ ="tcb"  │     │ ="amb"  │     │ ="vf"   │
    └─────────┘     └─────────┘     └─────────┘
```

#### Pros & Cons

**✅ Advantages:**

1. **Simple Setup**
   - 1 Pub2 API key for all tenants
   - Centralized management by AT
   - Faster time-to-market

2. **Network Effects**
   - Influencer có thể join multiple tenants với 1 Pub2 account
   - Shared balance = convenience
   - Cross-tenant collaboration easier

3. **Lower Pub2 Overhead**
   - Pub2 chỉ deal với 1 partner
   - May get better pricing

**❌ Disadvantages:**

1. **Source Handover Complexity**
   - TCB nhận source nhưng vẫn dùng AT's API key?
   - TCB phụ thuộc AT's Pub2 account long-term
   - Ownership ambiguity

2. **Billing Dependency**
   - TCB pays AT → AT pays Pub2 (middleman risk)
   - No direct relationship TCB ↔ Pub2
   - Commission transparency issues

3. **Weak Data Isolation**
   - Rely on at-core filtering logic (sub_id_2)
   - Potential data leakage bugs
   - Audit trail complexity

4. **Difficult Exit Strategy**
   - Nếu AT ngừng maintain → TCB/Vinfast stuck
   - Cannot operate independently
   - Vendor lock-in risk

---

### 🎯 Decision: **Option A - 3 Separate Pub2 Partners**

**Rationale:**

1. **Aligns with Business Context**
   - Per BUSINESS-CONTEXT.md: AT bán source code với 100% ownership
   - TCB/Vinfast expect full control post-delivery
   - Clean IP ownership model

2. **Long-term Independence**
   - TCB không muốn depend AT forever
   - Exit strategy essential for enterprise customers
   - Reduces single-point-of-failure risks

3. **Compliance & Legal**
   - TCB, Vinfast = separate legal entities
   - Data privacy regulations require clear boundaries
   - Audit trails must be unambiguous

4. **Commercial Flexibility**
   - TCB có thể negotiate better rates với Pub2 directly
   - Custom SLA requirements
   - Independent roadmap control

**Trade-offs Accepted:**
- ✅ Accept higher setup complexity (one-time cost)
- ✅ Accept weaker network effects (business isolation > convenience)
- ✅ Accept higher Pub2 overhead (scales with success)

---

### Implementation Plan

#### Phase 1: Setup Pub2 Accounts (Week 1-2)

**For each tenant (TCB, Ambassador, Vinfast):**

1. **AT coordinates với Pub2:**
   - Request partner account creation
   - Provide business details (company name, tax ID, billing contact)
   - Sign partnership agreement

2. **Pub2 provisions:**
   - Partner ID (e.g., TCB_001)
   - API credentials (key + secret)
   - Webhook endpoints configuration
   - Sandbox environment for testing

3. **AT configures at-core:**
   ```typescript
   // Database: tenant_pub2_config
   INSERT INTO tenant_pub2_config VALUES (
     'tcb',                              -- tenant_id
     encrypt('TCB_PROD_API_KEY_XXX'),   -- pub2_api_key (KMS encrypted)
     'TCB_001',                          -- pub2_partner_id
     true,                               -- enabled
     '["banking", "finance", "insurance"]', -- campaign_whitelist
     '[]',                               -- campaign_blacklist
     0.0,                                -- commission_share_pct (no platform fee)
     NOW(),
     NOW()
   );
   ```

4. **Testing:**
   - Sandbox API calls
   - Webhook delivery verification
   - Data filtering validation

#### Phase 2: Source Code Handover (Week 3-4)

**For TCB handover:**

1. **AT delivers source code:**
   - Complete at-core codebase
   - Environment config template:
     ```bash
     # .env.tcb
     TENANT_ID=tcb
     PUB2_API_KEY=TCB_PROD_API_KEY_XXX  # TCB's own key
     PUB2_PARTNER_ID=TCB_001
     PUB2_API_URL=https://api.pub2.vn/v1
     ```

2. **Documentation:**
   - Pub2 integration guide
   - API key rotation procedures
   - Monitoring & alerting setup
   - Troubleshooting playbook

3. **Knowledge transfer:**
   - Training sessions for TCB engineers
   - Runbook for common operations
   - Escalation paths (AT support → Pub2 support)

4. **Handoff checklist:**
   - [ ] Source code repository access
   - [ ] Pub2 API credentials transferred
   - [ ] Production deployment guide
   - [ ] Monitoring dashboards configured
   - [ ] Support SLA agreement signed

**Post-handover:**
- TCB operates independently
- AT provides best-effort support (if contracted)
- TCB manages Pub2 relationship directly

---

## Decision 2: User Balance & Transactions

### 🎯 Question
**Influencer có 1 Pub2 account, join cả TCB lẫn Ambassador. Balance & transactions nên riêng hay chung?**

### Context

**Scenario: Alice the Influencer**
- Pub2 Account: `ALICE_789` (single account)
- Activities:
  - TCB portal: Review credit card → Earn $120 commission
  - Ambassador portal: Review coffee brand → Earn $80 commission
- **Question:** Alice thấy gì trong mỗi portal?

---

### Option A: Separate Balance per Tenant ⭐ CHOSEN

#### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Pub2 Backend                             │
│                                                             │
│  Alice's Account (pub2_user_id: ALICE_789)                 │
│  ├─ Total Balance: $200                                    │
│  ├─ Transactions:                                          │
│  │  ├─ Conv #1: campaign_123, sub_id_2="tcb"  → $85       │
│  │  ├─ Conv #2: campaign_456, sub_id_2="tcb"  → $35       │
│  │  ├─ Conv #3: campaign_789, sub_id_2="amb"  → $50       │
│  │  └─ Conv #4: campaign_012, sub_id_2="amb"  → $30       │
│  └─ Payout History: [...]                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
                   API calls with filtering
                          │
         ┌────────────────┴────────────────┐
         │                                 │
┌────────┴─────────┐           ┌──────────┴──────────┐
│  at-core (TCB)   │           │  at-core (AMB)      │
│  Filtering:      │           │  Filtering:         │
│  sub_id_2="tcb"  │           │  sub_id_2="amb"     │
└────────┬─────────┘           └──────────┬──────────┘
         │                                 │
         ▼                                 ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  TCB Influencer Portal  │   │  AMB Influencer Portal  │
│                         │   │                         │
│  Alice's Earnings:      │   │  Alice's Earnings:      │
│  Affiliate: $120        │   │  Affiliate: $80         │
│  - Conv #1: $85         │   │  - Conv #3: $50         │
│  - Conv #2: $35         │   │  - Conv #4: $30         │
│                         │   │                         │
│  [Request Payout: $120] │   │  [Request Payout: $80]  │
└─────────────────────────┘   └─────────────────────────┘
```

#### Filtering Logic

```typescript
// at-core backend service
class AffiliatEarningsService {
  async getEarnings(influencerId: string, tenantId: string): Promise<Earnings> {
    // Step 1: Get influencer's Pub2 account
    const pub2UserId = await this.getPub2UserId(influencerId);

    // Step 2: Fetch tenant's Pub2 API key
    const tenantConfig = await this.getTenantPub2Config(tenantId);

    // Step 3: Fetch ALL transactions from Pub2
    const allTransactions = await this.pub2Client.getTransactions(
      pub2UserId,
      tenantConfig.pub2ApiKey
    );

    // Step 4: Filter by tenant marker (sub_id_2)
    const tenantTransactions = allTransactions.filter(
      tx => tx.sub_id_2 === tenantId
    );

    // Step 5: Calculate balance
    const balance = tenantTransactions.reduce(
      (sum, tx) => sum + tx.commission,
      0
    );

    return {
      balance,
      transactions: tenantTransactions,
      currency: 'USD'
    };
  }
}
```

#### UI Display

**TCB Portal:**
```
┌───────────────────────────────────────┐
│ MY EARNINGS - TECHCOMBANK             │
├───────────────────────────────────────┤
│ Affiliate Commission: $120            │
│                                       │
│ Recent Conversions:                   │
│ • Credit Card Review    $85           │
│ • Savings Account       $35           │
│                                       │
│ Pending Payout: $120                  │
│ [Request Payout]                      │
└───────────────────────────────────────┘
```

**Ambassador Portal:**
```
┌───────────────────────────────────────┐
│ MY EARNINGS - AMBASSADOR              │
├───────────────────────────────────────┤
│ Affiliate Commission: $80             │
│                                       │
│ Recent Conversions:                   │
│ • Coffee Brand Review   $50           │
│ • Fashion Product       $30           │
│                                       │
│ Pending Payout: $80                   │
│ [Request Payout]                      │
└───────────────────────────────────────┘
```

#### Pros & Cons

**✅ Advantages:**

1. **White-label Isolation**
   - TCB portal chỉ show TCB earnings
   - Ambassador portal chỉ show Ambassador earnings
   - No cross-tenant data visibility

2. **Tenant Revenue Isolation**
   - TCB pays for TCB conversions only ($120)
   - Ambassador pays for Ambassador conversions only ($80)
   - Clear billing boundaries

3. **Source Code Handover Friendly**
   - TCB nhận code với filtering logic
   - Self-contained, no external dependencies
   - Testable & auditable

4. **Compliance**
   - Data privacy regulations satisfied
   - Audit trails clear per tenant
   - No data leakage risk

**❌ Disadvantages:**

1. **Payout Complexity**
   - Alice requests payout 2 lần (TCB: $120, AMB: $80)
   - Dual payout workflows
   - Potential user confusion

2. **Pub2 Balance Mismatch**
   - Pub2 sees $200 total balance
   - at-core shows $120 (TCB) + $80 (AMB) separately
   - Reconciliation complexity

---

### Option B: Shared Balance (Consolidated)

#### UI Display

```
┌───────────────────────────────────────┐
│ MY TOTAL AFFILIATE EARNINGS           │
├───────────────────────────────────────┤
│ Total Commission: $200                │
│                                       │
│ Breakdown by Platform:                │
│ • Techcombank:  $120                  │
│ • Ambassador:   $80                   │
│                                       │
│ [Request Payout: $200]                │
└───────────────────────────────────────┘
```

#### Pros & Cons

**✅ Advantages:**
- Unified UX (Alice thấy total earnings)
- Single payout (convenient)
- Pub2 balance alignment (no mismatch)

**❌ Disadvantages:**
- ❌ White-label broken (TCB portal shows AMB data?)
- ❌ Data leak (Vinfast biết TCB earnings)
- ❌ Billing conflict (Who pays for $200? TCB or AMB or split?)
- ❌ Source handover issues (cross-tenant logic embedded)

---

### 🎯 Decision: **Option A - Separate Balance per Tenant**

**Rationale:**

1. **White-label Requirement**
   - TCB brand identity ≠ Ambassador brand
   - TCB portal must NOT show Ambassador data
   - Brand isolation critical for enterprise customers

2. **Business Model Alignment**
   - TCB pays for TCB conversions only
   - No cross-subsidization between tenants
   - Clear cost attribution

3. **Source Code Handover**
   - TCB nhận code với clear tenant filtering
   - No hidden cross-tenant dependencies
   - Auditable & testable isolation

4. **Compliance & Security**
   - Data privacy regulations require boundaries
   - Audit trails must be tenant-specific
   - Zero cross-tenant data leakage

**Trade-offs Accepted:**
- ✅ Accept dual payout complexity (better than data leak)
- ✅ Accept Pub2 balance mismatch (reconciliation is manageable)

---

### Payout Implementation Strategies

#### Strategy 1: Separate Payout per Tenant (MVP) ⭐ RECOMMENDED

**Flow:**
```
Alice requests payout from TCB portal:
  ├─ TCB portal: "Request payout $120"
  ├─ at-core validates: Alice has $120 pending (sub_id_2=tcb)
  ├─ TCB finance team approves
  └─ TCB pays Alice via bank transfer

Alice requests payout from AMB portal:
  ├─ AMB portal: "Request payout $80"
  ├─ at-core validates: Alice has $80 pending (sub_id_2=amb)
  ├─ AMB finance team approves
  └─ AMB pays Alice via bank transfer

Pub2's role:
  └─ Just tracking, no payout handling
```

**Pros:**
- ✅ Simplest implementation
- ✅ Clear tenant ownership
- ✅ No cross-tenant coordination needed

**Cons:**
- ⚠️ Dual requests from influencer perspective
- ⚠️ Separate payment processing

**Recommended for:** MVP, small-scale

---

#### Strategy 2: Consolidated Payout via Pub2 (Future Enhancement)

**Flow:**
```
Alice requests single payout:
  ├─ Portal: "Request payout $200 (all platforms)"
  ├─ at-core aggregates: TCB=$120, AMB=$80
  ├─ at-core triggers Pub2 payout API
  ├─ Pub2 pays Alice: $200
  └─ at-core reconciles:
      ├─ TCB owes AT (or Pub2): $120
      └─ AMB owes AT (or Pub2): $80

Monthly invoicing:
  ├─ TCB receives invoice: $120 for Alice + other influencers
  ├─ AMB receives invoice: $80 for Alice + other influencers
  └─ Pub2 handles actual bank transfers
```

**Pros:**
- ✅ Better UX for influencer (single payout)
- ✅ Pub2 handles payment infrastructure
- ✅ Consolidated payment processing

**Cons:**
- ❌ Complex accounting & reconciliation
- ❌ Cross-tenant financial dependency
- ❌ Requires Pub2 API support for split attribution

**Recommended for:** Scale (1000+ influencers), mature platform

---

### Implementation Code

```typescript
// Service: AffiliatePayout.service.ts

interface PayoutRequest {
  influencerId: string;
  tenantId: string;
  amount: number;
}

class AffiliatePayoutService {

  // Strategy 1: Separate payout per tenant
  async requestPayoutSeparate(request: PayoutRequest): Promise<PayoutResult> {
    const { influencerId, tenantId, amount } = request;

    // Validate available balance
    const earnings = await this.earningsService.getEarnings(
      influencerId,
      tenantId
    );

    if (earnings.balance < amount) {
      throw new Error('Insufficient balance');
    }

    // Create payout record
    const payout = await db.payouts.create({
      influencer_id: influencerId,
      tenant_id: tenantId,
      amount: amount,
      status: 'pending',
      requested_at: new Date()
    });

    // Notify tenant finance team
    await this.notificationService.notifyFinanceTeam(tenantId, payout);

    // Notify influencer
    await this.notificationService.notifyInfluencer(influencerId, {
      message: `Payout request submitted: ${amount} USD`,
      tenant: tenantId
    });

    return {
      payout_id: payout.id,
      status: 'pending',
      estimated_processing: '3-5 business days'
    };
  }

  // Strategy 2: Consolidated payout (future)
  async requestPayoutConsolidated(influencerId: string): Promise<PayoutResult> {
    // Aggregate earnings across all tenants
    const allEarnings = await this.earningsService.getEarningsAllTenants(
      influencerId
    );

    const totalAmount = allEarnings.reduce((sum, e) => sum + e.balance, 0);

    // Trigger Pub2 payout API
    const pub2Payout = await this.pub2Client.createPayout({
      publisher_id: await this.getPub2UserId(influencerId),
      amount: totalAmount
    });

    // Record attribution for reconciliation
    for (const earnings of allEarnings) {
      await db.payout_attributions.create({
        pub2_payout_id: pub2Payout.id,
        tenant_id: earnings.tenantId,
        amount: earnings.balance
      });
    }

    return {
      payout_id: pub2Payout.id,
      total_amount: totalAmount,
      breakdown: allEarnings.map(e => ({
        tenant: e.tenantId,
        amount: e.balance
      }))
    };
  }
}
```

---

## Decision 3: Influencer Portal Display

### 🎯 Question
**Trên TCB Influencer Portal, nên hiển thị gì liên quan affiliate?**

### Design Principles

1. **Tenant Isolation:** TCB portal chỉ show TCB data
2. **Clarity:** Phân biệt rõ view rewards vs affiliate commission
3. **Actionability:** Metrics phải giúp influencer optimize
4. **Transparency:** Earnings breakdown phải chi tiết
5. **White-label:** Branding phải match tenant identity

---

### UI Component Specifications

#### Component 1: Dashboard Overview

**Location:** Homepage sau khi influencer login

**Layout:**
```
┌───────────────────────────────────────────────────────────┐
│  TECHCOMBANK CREATOR DASHBOARD                            │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  MY EARNINGS THIS MONTH                                   │
│  ══════════════════════════════════════════               │
│                                                           │
│  💰 TOTAL: $1,250  ⬆ +15% vs last month                 │
│                                                           │
│  ┌──────────────────────────┐ ┌──────────────────────┐   │
│  │ 📹 Video Views Reward    │ │ 🔗 Affiliate Comm   │   │
│  │ $800 (64%)               │ │ $450 (36%)          │   │
│  │ 10 videos • 45K views    │ │ 5 videos • 23 conv  │   │
│  └──────────────────────────┘ └──────────────────────┘   │
│                                                           │
│  TOP EARNING VIDEO THIS WEEK                              │
│  "TCB Credit Card Review" - $380 total                   │
│  Views: 5.2K → $260  |  Affiliate: 12 sales → $120       │
│                                                           │
├───────────────────────────────────────────────────────────┤
│  QUICK ACTIONS                                            │
│  [Browse Campaigns] [My Affiliate Links] [Analytics]     │
└───────────────────────────────────────────────────────────┘
```

**Data Source:**
```typescript
interface DashboardData {
  totalEarnings: {
    current: number;      // $1,250
    previous: number;     // For comparison
    percentChange: number; // +15%
  };
  viewRewards: {
    amount: number;       // $800
    percentage: number;   // 64%
    videoCount: number;   // 10
    totalViews: number;   // 45,000
  };
  affiliateCommission: {
    amount: number;       // $450
    percentage: number;   // 36%
    videoCount: number;   // 5
    conversions: number;  // 23
  };
  topVideo: {
    title: string;
    totalEarnings: number;
    viewReward: number;
    affiliateCommission: number;
    viewCount: number;
    conversionCount: number;
  };
}
```

**Key Points:**
- ✅ Prominent total earnings (psychological motivation)
- ✅ Clear separation: View rewards vs Affiliate
- ✅ Percentage breakdown (visual understanding)
- ✅ Top performer highlight (actionable insight)
- ❌ NO data from other tenants (Ambassador, Vinfast)

---

#### Component 2: Campaign Browser

**Location:** Navigation → "Affiliate Campaigns"

**Layout:**
```
┌───────────────────────────────────────────────────────────┐
│  AFFILIATE CAMPAIGNS                                      │
├───────────────────────────────────────────────────────────┤
│  Filter: [All] [Banking] [Finance] [Insurance]           │
│  Sort by: [Commission ↓] [Trending] [New] [Ending Soon]  │
│  Search: [________________________] 🔍                    │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🏦 TCB Platinum Credit Card                         │ │
│  │                                                     │ │
│  │ Commission: 8.5% per approved application          │ │
│  │ Average Order Value: $500                           │ │
│  │ Your Estimated Earning: ~$42.50 per conversion     │ │
│  │                                                     │ │
│  │ 📊 Performance:                                     │ │
│  │ • Conversion Rate: 12.3% (excellent!)              │ │
│  │ • Avg Approval Time: 3-5 days                      │ │
│  │ • Active Until: Dec 31, 2026                       │ │
│  │                                                     │ │
│  │ 💡 Pro Tip: Videos showcasing card benefits        │ │
│  │    convert 2x better than generic reviews          │ │
│  │                                                     │ │
│  │ [Generate Affiliate Link] [View Campaign Details]  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 💳 Travel Insurance Bundle                          │ │
│  │ Commission: $15 per sale (fixed)                    │ │
│  │ Conversion Rate: 9.8%                               │ │
│  │ [Generate Link]                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  [Load More Campaigns...]                                 │
└───────────────────────────────────────────────────────────┘
```

**Filtering Logic:**
```typescript
// Only show campaigns matching tenant whitelist
const tcbWhitelist = ['banking', 'finance', 'insurance'];

const campaigns = await pub2Client.getCampaigns(tenantConfig.pub2ApiKey);

const filteredCampaigns = campaigns.filter(campaign => {
  // Whitelist check
  if (!tcbWhitelist.includes(campaign.category)) {
    return false;
  }

  // Blacklist check
  if (tenantConfig.blockedCampaigns.includes(campaign.id)) {
    return false;
  }

  // Min commission rate
  if (campaign.commissionRate < tenantConfig.minCommissionRate) {
    return false;
  }

  // Active status
  if (campaign.status !== 'active') {
    return false;
  }

  return true;
});
```

**Key Features:**
- ✅ Category filtering (banking/finance only for TCB)
- ✅ Estimated earnings calculation
- ✅ Performance metrics (conversion rate)
- ✅ Actionable tips (content suggestions)
- ❌ NO automotive campaigns (Vinfast domain)
- ❌ NO generic lifestyle campaigns (unless whitelisted)

---

#### Component 3: My Affiliate Links

**Location:** Navigation → "My Affiliate Links"

**Layout:**
```
┌───────────────────────────────────────────────────────────┐
│  MY AFFILIATE LINKS                                       │
├───────────────────────────────────────────────────────────┤
│  Filter: [All] [Active] [Top Performing] [Inactive]      │
│  Date Range: [Last 30 Days ▼]                            │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ 📹 TCB Credit Card Review                         │   │
│  │ Published: Feb 3, 2026 • 5,200 views              │   │
│  │                                                   │   │
│  │ Campaign: Platinum Credit Card                    │   │
│  │ Link: https://pub2.vn/track/abc123...             │   │
│  │ [📋 Copy] [📊 View Analytics] [🗑️ Deactivate]    │   │
│  │                                                   │   │
│  │ Performance:                                       │   │
│  │ • Clicks: 234 (4.5% CTR)                          │   │
│  │ • Conversions: 12 (5.1% CVR)                      │   │
│  │ • Commission Earned: $510                         │   │
│  │ • Avg Order Value: $425                           │   │
│  │                                                   │   │
│  │ ⭐ TOP PERFORMER - Best CTR this month            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ 📹 Best Savings Account 2026                      │   │
│  │ Published: Feb 1, 2026 • 3,800 views              │   │
│  │                                                   │   │
│  │ Campaign: High Interest Savings                   │   │
│  │ Performance:                                       │   │
│  │ • Clicks: 189 (5.0% CTR)                          │   │
│  │ • Conversions: 8 (4.2% CVR)                       │   │
│  │ • Commission: $240                                │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ SUMMARY                                           │   │
│  │ Total Links: 12                                   │   │
│  │ Total Clicks: 1,456                               │   │
│  │ Total Conversions: 34                             │   │
│  │ Total Commission: $1,280                          │   │
│  │ Avg CTR: 4.2%  |  Avg CVR: 4.8%                  │   │
│  └───────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

**Data Query:**
```typescript
// Fetch links for current tenant only
const links = await db.pub2_affiliate_links
  .where('influencer_id', influencerId)
  .where('video.tenant_id', tenantId)  // Tenant filter
  .join('videos', 'videos.id', 'pub2_affiliate_links.video_id')
  .leftJoin('pub2_click_events', 'pub2_affiliate_links.id', 'pub2_click_events.link_id')
  .leftJoin('pub2_conversions', 'pub2_affiliate_links.id', 'pub2_conversions.link_id')
  .select('*');

// Aggregate metrics
const summary = {
  totalLinks: links.length,
  totalClicks: sum(links.map(l => l.clickCount)),
  totalConversions: sum(links.map(l => l.conversionCount)),
  totalCommission: sum(links.map(l => l.totalCommission)),
  avgCTR: avg(links.map(l => l.clickCount / l.viewCount)),
  avgCVR: avg(links.map(l => l.conversionCount / l.clickCount))
};
```

**Key Features:**
- ✅ Performance metrics per link (CTR, CVR, commission)
- ✅ Quick actions (copy, analytics, deactivate)
- ✅ Top performer badges
- ✅ Summary statistics
- ❌ NO links from other tenants

---

#### Component 4: Affiliate Analytics

**Location:** Navigation → "Analytics" → "Affiliate Performance"

**Layout:**
```
┌───────────────────────────────────────────────────────────┐
│  AFFILIATE PERFORMANCE ANALYTICS                          │
├───────────────────────────────────────────────────────────┤
│  Date Range: [Last 30 Days ▼]  Compare: [Previous Period]│
│                                                           │
│  KEY METRICS                                              │
│  ══════════════════════════════════════════               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │ Total Clicks│ │ Conversions │ │ Commission  │        │
│  │    490      │ │     23      │ │   $840      │        │
│  │  ⬆ +12%    │ │  ⬆ +8%     │ │  ⬆ +18%    │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │     CTR     │ │     CVR     │ │ Avg Order   │        │
│  │    4.5%     │ │    4.7%     │ │   $520      │        │
│  │  ⬆ +0.3%   │ │  ⬇ -0.5%   │ │  ⬆ +$45     │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                           │
│  📊 COMMISSION TREND                                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │  $                                                │    │
│  │ 400│         ╱╲                                  │    │
│  │ 300│      ╱╲/  ╲╱╲                               │    │
│  │ 200│   ╱╲/          ╲                            │    │
│  │ 100│╱╲/              ╲╱                          │    │
│  │   0└────────────────────────────────────────    │    │
│  │     Week 1  Week 2  Week 3  Week 4              │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  TOP PERFORMING CAMPAIGNS                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Campaign              Conv  Commission  CVR      │    │
│  │ ─────────────────────────────────────────────    │    │
│  │ Platinum Card           12    $510      5.1%     │    │
│  │ Savings Account          8    $240      4.2%     │    │
│  │ Mutual Funds             3     $90      4.5%     │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  📈 INSIGHTS & RECOMMENDATIONS                            │
│  • Your best CTR is 5.1% on banking campaigns            │
│  • Conversions peak on Tuesdays (consider posting then)  │
│  • Videos with product demos convert 2.3x better         │
│  • Platinum Card campaign trending ⬆ - capitalize now!  │
└───────────────────────────────────────────────────────────┘
```

**Analytics Queries:**
```typescript
// Time-series data for charts
const timeSeries = await db.pub2_conversions
  .where('link.video.tenant_id', tenantId)
  .where('purchased_at', '>=', startDate)
  .groupBy('date')
  .select(
    'DATE(purchased_at) as date',
    'SUM(commission) as daily_commission',
    'COUNT(*) as daily_conversions'
  );

// Top campaigns analysis
const topCampaigns = await db.pub2_conversions
  .join('pub2_affiliate_links', ...)
  .where('tenant_id', tenantId)
  .groupBy('campaign_id')
  .select(
    'campaign_id',
    'campaign_name',
    'COUNT(*) as conversion_count',
    'SUM(commission) as total_commission',
    'AVG(order_value) as avg_order_value',
    '(COUNT(*) / SUM(clicks)) as conversion_rate'
  )
  .orderBy('total_commission', 'DESC')
  .limit(10);

// AI-generated insights
const insights = await this.mlService.generateInsights({
  userId: influencerId,
  tenantId: tenantId,
  timeRange: 30,
  metrics: { clicks, conversions, ctr, cvr }
});
```

**Key Features:**
- ✅ Comprehensive metrics dashboard
- ✅ Time-series visualization
- ✅ Top performer analysis
- ✅ AI-generated insights & recommendations
- ✅ Comparison with previous period
- ❌ NO cross-tenant comparisons

---

#### Component 5: Payout History

**Location:** Navigation → "Earnings" → "Payout History"

**Layout:**
```
┌───────────────────────────────────────────────────────────┐
│  PAYOUT HISTORY                                           │
├───────────────────────────────────────────────────────────┤
│  Available Balance: $1,250                                │
│  Minimum Payout: $100                                     │
│  Processing Time: 3-5 business days                       │
│  [Request Payout]                                         │
│                                                           │
│  EARNINGS BREAKDOWN                                       │
│  ┌──────────────────────────────────────────────────┐    │
│  │ 📹 Video View Rewards       $800                 │    │
│  │ 🔗 Affiliate Commissions    $450                 │    │
│  │ ═══════════════════════════════                  │    │
│  │ TOTAL AVAILABLE             $1,250               │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  RECENT PAYOUTS                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Date         Type              Amount    Status   │    │
│  │ ───────────────────────────────────────────────  │    │
│  │ Feb 1, 2026  Video Rewards    $750       Paid ✓  │    │
│  │ Feb 1, 2026  Affiliate Comm   $320       Paid ✓  │    │
│  │ Jan 1, 2026  Combined         $980       Paid ✓  │    │
│  │ Dec 15, 2025 Video Rewards    $650       Paid ✓  │    │
│  │ Dec 15, 2025 Affiliate Comm   $280       Paid ✓  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  PAYOUT DETAILS                                           │
│  Bank Account: **** **** 1234 (TCB Savings)              │
│  Payment Method: Bank Transfer                            │
│  Tax Status: W-9 Submitted ✓                             │
│  [Update Payment Info]                                    │
└───────────────────────────────────────────────────────────┘
```

**Payout Request Flow:**
```typescript
// User clicks "Request Payout"
async function handlePayoutRequest() {
  // Step 1: Validate minimum threshold
  if (availableBalance < MINIMUM_PAYOUT) {
    throw new Error(`Minimum payout is $${MINIMUM_PAYOUT}`);
  }

  // Step 2: Create payout record
  const payout = await db.payouts.create({
    influencer_id: influencerId,
    tenant_id: 'tcb',
    amount: availableBalance,
    breakdown: {
      view_rewards: viewRewardBalance,
      affiliate_commission: affiliateBalance
    },
    status: 'pending',
    requested_at: new Date()
  });

  // Step 3: Notify finance team
  await notificationService.notifyFinanceTeam('tcb', {
    influencer: influencerName,
    amount: availableBalance,
    payout_id: payout.id
  });

  // Step 4: Notify influencer
  await notificationService.notifyInfluencer(influencerId, {
    message: `Payout request submitted: $${availableBalance}`,
    estimated_processing: '3-5 business days'
  });

  return payout;
}
```

**Key Features:**
- ✅ Clear breakdown (view vs affiliate)
- ✅ Combined total for convenience
- ✅ Transparent payout history
- ✅ Payment method management
- ❌ NO payouts from other tenants visible

---

### White-label Branding

#### TCB Portal Theme

**Colors:**
```css
:root {
  --primary-color: #0066CC;      /* TCB Blue */
  --secondary-color: #00AA55;    /* Success Green */
  --accent-color: #FFA500;       /* Highlight Orange */
  --background: #F5F7FA;         /* Clean White */
  --text-primary: #1A1A1A;
  --text-secondary: #666666;
}
```

**Typography:**
```css
--font-heading: 'Inter', sans-serif;  /* Modern, professional */
--font-body: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;  /* For codes/links */
```

**Tone:**
- Professional
- Trustworthy
- Financial authority
- Conservative elegance

---

#### Ambassador Portal Theme

**Colors:**
```css
:root {
  --primary-color: #FF6B6B;      /* Vibrant Red */
  --secondary-color: #4ECDC4;    /* Teal */
  --accent-color: #FFE66D;       /* Yellow */
  --background: #F8F9FA;
  --text-primary: #2D3436;
  --text-secondary: #636E72;
}
```

**Tone:**
- Energetic
- Creative
- Lifestyle-focused
- Fun & engaging

---

#### Vinfast Portal Theme

**Colors:**
```css
:root {
  --primary-color: #1A1A2E;      /* Dark Navy */
  --secondary-color: #E94560;    /* Electric Red */
  --accent-color: #00D9FF;       /* Cyan */
  --background: #EAEAEA;
  --text-primary: #0F0F0F;
  --text-secondary: #555555;
}
```

**Tone:**
- Modern
- Tech-forward
- Automotive precision
- Cutting-edge

---

### 🎯 Decision Summary: Portal Display

**Chosen Approach:**

1. **Tenant-Isolated UI**
   - Each portal shows ONLY that tenant's data
   - No cross-tenant visibility
   - White-label branding per tenant

2. **Comprehensive Metrics**
   - Dashboard overview (total earnings)
   - Campaign browser (filtered)
   - Link management (performance tracking)
   - Analytics (insights & recommendations)
   - Payout history (transparent breakdown)

3. **Dual Revenue Display**
   - Separate cards: View rewards vs Affiliate
   - Combined total (psychological motivation)
   - Clear percentage breakdown

4. **Actionable Insights**
   - CTR, CVR metrics
   - Top performer badges
   - AI-generated recommendations
   - Time-series trends

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-4)

#### Week 1-2: Pub2 Account Setup
- [ ] AT coordinates với Pub2 cho 3 accounts (TCB, AMB, VF)
- [ ] Pub2 provisions API keys & partner IDs
- [ ] AT configures `tenant_pub2_config` table
- [ ] Sandbox testing & validation

#### Week 3-4: Core Backend Services
- [ ] Pub2ApiClient service
- [ ] Tenant filtering logic (sub_id_2)
- [ ] Webhook receiver endpoints
- [ ] Database schema migration
- [ ] Integration tests

**Deliverable:** Backend API functional, tested in sandbox

---

### Phase 2: Frontend UI (Week 5-8)

#### Week 5-6: Core UI Components
- [ ] Dashboard overview component
- [ ] Campaign browser component
- [ ] Affiliate link generator
- [ ] White-label theming system

#### Week 7-8: Analytics & Payout
- [ ] Analytics dashboard
- [ ] Payout request flow
- [ ] Payout history view
- [ ] Notification system

**Deliverable:** Full UI functional, ready for UAT

---

### Phase 3: Testing & Deployment (Week 9-12)

#### Week 9-10: UAT & QA
- [ ] UAT with TCB stakeholders
- [ ] UAT with Ambassador team
- [ ] Bug fixes & refinements
- [ ] Performance optimization

#### Week 11: Production Deployment
- [ ] TCB production deployment
- [ ] Ambassador production deployment
- [ ] Monitoring & alerting setup
- [ ] Runbook documentation

#### Week 12: Handover (TCB)
- [ ] Source code transfer to TCB
- [ ] Pub2 API credentials transfer
- [ ] Training sessions for TCB engineers
- [ ] Support SLA activation

**Deliverable:** TCB operates independently with at-core source

---

### Phase 4: Enhancements (Month 4-6)

- [ ] AI campaign recommendations
- [ ] Advanced fraud detection
- [ ] Consolidated payout (Strategy 2)
- [ ] A/B testing framework
- [ ] Mobile app integration

---

## Appendix: Code Examples

### Database Schema

```sql
-- Tenant Pub2 Configuration
CREATE TABLE tenant_pub2_config (
  tenant_id VARCHAR(50) PRIMARY KEY,
  pub2_api_key VARCHAR(255) NOT NULL,  -- Encrypted via KMS
  pub2_partner_id VARCHAR(100) NOT NULL,
  pub2_account_name VARCHAR(255),
  enabled BOOLEAN DEFAULT false,
  campaign_whitelist JSONB DEFAULT '[]',
  campaign_blacklist JSONB DEFAULT '[]',
  min_commission_rate DECIMAL(5,2) DEFAULT 0.0,
  commission_share_pct DECIMAL(5,2) DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Influencer Pub2 Account Linking
CREATE TABLE influencer_pub2_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  pub2_user_id VARCHAR(100) NOT NULL,
  link_status VARCHAR(20) DEFAULT 'active',  -- 'active' | 'inactive' | 'pending'
  linked_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(influencer_id, pub2_user_id)
);

-- Affiliate Links
CREATE TABLE pub2_affiliate_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  video_id UUID NOT NULL REFERENCES videos(id),
  campaign_id VARCHAR(100) NOT NULL,
  campaign_name VARCHAR(255),
  affiliate_url TEXT NOT NULL,
  sub_id_1 VARCHAR(100),  -- video_id for attribution
  sub_id_2 VARCHAR(100),  -- tenant_id for isolation
  sub_id_3 VARCHAR(100),  -- campaign category
  status VARCHAR(20) DEFAULT 'active',  -- 'active' | 'inactive' | 'flagged'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Click Events
CREATE TABLE pub2_click_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  link_id UUID NOT NULL REFERENCES pub2_affiliate_links(id),
  event_id VARCHAR(100) UNIQUE NOT NULL,  -- Pub2's event ID (idempotency)
  clicked_at TIMESTAMP NOT NULL,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Conversions
CREATE TABLE pub2_conversions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  link_id UUID NOT NULL REFERENCES pub2_affiliate_links(id),
  event_id VARCHAR(100) UNIQUE NOT NULL,  -- Pub2's conversion ID
  order_id VARCHAR(100),
  order_value DECIMAL(10,2),
  commission DECIMAL(10,2),
  commission_status VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'confirmed' | 'paid'
  purchased_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Webhook Logs
CREATE TABLE pub2_webhook_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_type VARCHAR(50) NOT NULL,  -- 'click' | 'conversion' | 'commission_update'
  payload JSONB NOT NULL,
  processed BOOLEAN DEFAULT false,
  error TEXT,
  received_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);

-- Payouts
CREATE TABLE payouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  tenant_id VARCHAR(50) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  breakdown JSONB,  -- { view_rewards: 800, affiliate_commission: 450 }
  status VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'approved' | 'paid' | 'rejected'
  requested_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  payment_reference VARCHAR(255),
  notes TEXT
);

-- Indexes
CREATE INDEX idx_affiliate_links_influencer ON pub2_affiliate_links(influencer_id);
CREATE INDEX idx_affiliate_links_video ON pub2_affiliate_links(video_id);
CREATE INDEX idx_affiliate_links_status ON pub2_affiliate_links(status);
CREATE INDEX idx_click_events_link ON pub2_click_events(link_id);
CREATE INDEX idx_click_events_date ON pub2_click_events(clicked_at);
CREATE INDEX idx_conversions_link ON pub2_conversions(link_id);
CREATE INDEX idx_conversions_status ON pub2_conversions(commission_status);
CREATE INDEX idx_conversions_date ON pub2_conversions(purchased_at);
CREATE INDEX idx_payouts_influencer ON payouts(influencer_id);
CREATE INDEX idx_payouts_tenant ON payouts(tenant_id);
CREATE INDEX idx_payouts_status ON payouts(status);
```

---

### Service Layer Example

```typescript
// services/Pub2Integration.service.ts

import { KMS } from 'aws-sdk';
import axios from 'axios';

interface TenantPub2Config {
  tenantId: string;
  pub2ApiKey: string;
  pub2PartnerId: string;
  campaignWhitelist: string[];
  campaignBlacklist: string[];
  minCommissionRate: number;
}

interface Campaign {
  id: string;
  title: string;
  category: string;
  commissionRate: number;
  commissionType: 'percentage' | 'fixed';
  status: 'active' | 'paused' | 'ended';
}

class Pub2IntegrationService {
  private kms: KMS;

  constructor() {
    this.kms = new KMS({ region: process.env.AWS_REGION });
  }

  // Decrypt tenant API key
  private async decryptApiKey(encryptedKey: string): Promise<string> {
    const result = await this.kms.decrypt({
      CiphertextBlob: Buffer.from(encryptedKey, 'base64')
    }).promise();

    return result.Plaintext!.toString('utf-8');
  }

  // Get tenant Pub2 configuration
  async getTenantConfig(tenantId: string): Promise<TenantPub2Config> {
    const config = await db.tenant_pub2_config.findOne({ tenant_id: tenantId });

    if (!config || !config.enabled) {
      throw new Error(`Pub2 integration not enabled for tenant: ${tenantId}`);
    }

    const decryptedKey = await this.decryptApiKey(config.pub2_api_key);

    return {
      tenantId: config.tenant_id,
      pub2ApiKey: decryptedKey,
      pub2PartnerId: config.pub2_partner_id,
      campaignWhitelist: config.campaign_whitelist || [],
      campaignBlacklist: config.campaign_blacklist || [],
      minCommissionRate: config.min_commission_rate || 0
    };
  }

  // Fetch campaigns from Pub2 with tenant filtering
  async getCampaigns(tenantId: string): Promise<Campaign[]> {
    const config = await this.getTenantConfig(tenantId);

    // Call Pub2 API
    const response = await axios.get('https://api.pub2.vn/v1/campaigns', {
      headers: {
        'Authorization': `Bearer ${config.pub2ApiKey}`,
        'Content-Type': 'application/json'
      },
      params: {
        status: 'active'
      }
    });

    const allCampaigns: Campaign[] = response.data.campaigns;

    // Apply tenant filtering
    const filteredCampaigns = allCampaigns.filter(campaign => {
      // Whitelist check
      if (config.campaignWhitelist.length > 0) {
        if (!config.campaignWhitelist.includes(campaign.category)) {
          return false;
        }
      }

      // Blacklist check
      if (config.campaignBlacklist.includes(campaign.id)) {
        return false;
      }

      // Min commission rate
      if (campaign.commissionRate < config.minCommissionRate) {
        return false;
      }

      return true;
    });

    return filteredCampaigns;
  }

  // Generate affiliate link
  async generateAffiliateLink(params: {
    tenantId: string;
    influencerId: string;
    videoId: string;
    campaignId: string;
  }): Promise<string> {
    const { tenantId, influencerId, videoId, campaignId } = params;

    // Get config
    const config = await this.getTenantConfig(tenantId);

    // Get influencer's Pub2 user ID
    const influencerPub2 = await db.influencer_pub2_accounts.findOne({
      influencer_id: influencerId
    });

    if (!influencerPub2) {
      throw new Error('Influencer not linked to Pub2 account');
    }

    // Call Pub2 API to create link
    const response = await axios.post(
      'https://api.pub2.vn/v1/affiliate-links',
      {
        campaign_id: campaignId,
        publisher_id: influencerPub2.pub2_user_id,
        sub_id_1: videoId,     // For attribution
        sub_id_2: tenantId,    // For tenant isolation
        sub_id_3: campaignId   // For tracking
      },
      {
        headers: {
          'Authorization': `Bearer ${config.pub2ApiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const affiliateUrl = response.data.url;

    // Store in database
    await db.pub2_affiliate_links.create({
      influencer_id: influencerId,
      video_id: videoId,
      campaign_id: campaignId,
      affiliate_url: affiliateUrl,
      sub_id_1: videoId,
      sub_id_2: tenantId,
      sub_id_3: campaignId,
      status: 'active'
    });

    return affiliateUrl;
  }

  // Get affiliate earnings for influencer (filtered by tenant)
  async getAffiliateEarnings(influencerId: string, tenantId: string) {
    const conversions = await db.pub2_conversions
      .join('pub2_affiliate_links', 'pub2_conversions.link_id', 'pub2_affiliate_links.id')
      .join('videos', 'pub2_affiliate_links.video_id', 'videos.id')
      .where('pub2_affiliate_links.influencer_id', influencerId)
      .where('pub2_affiliate_links.sub_id_2', tenantId)  // Tenant filter!
      .select('pub2_conversions.*');

    const totalCommission = conversions.reduce((sum, c) => sum + c.commission, 0);
    const conversionCount = conversions.length;

    return {
      balance: totalCommission,
      conversions: conversionCount,
      transactions: conversions
    };
  }

  // Webhook handler for click events
  async handleClickWebhook(payload: any) {
    const { event_id, link_id, clicked_at, ip_address, user_agent } = payload;

    // Idempotency check
    const existing = await db.pub2_click_events.findOne({ event_id });
    if (existing) {
      return; // Already processed
    }

    // Find link
    const link = await db.pub2_affiliate_links.findOne({
      affiliate_url: { $regex: link_id }
    });

    if (!link) {
      throw new Error(`Link not found: ${link_id}`);
    }

    // Store click event
    await db.pub2_click_events.create({
      link_id: link.id,
      event_id,
      clicked_at: new Date(clicked_at),
      ip_address,
      user_agent
    });

    // Log webhook
    await db.pub2_webhook_logs.create({
      webhook_type: 'click',
      payload,
      processed: true
    });
  }

  // Webhook handler for conversions
  async handleConversionWebhook(payload: any) {
    const {
      event_id,
      link_id,
      order_id,
      order_value,
      commission,
      commission_status,
      purchased_at,
      sub_id_1,  // video_id
      sub_id_2   // tenant_id
    } = payload;

    // Idempotency check
    const existing = await db.pub2_conversions.findOne({ event_id });
    if (existing) {
      // Update if status changed
      if (existing.commission_status !== commission_status) {
        await db.pub2_conversions.update(
          { event_id },
          { commission_status, updated_at: new Date() }
        );
      }
      return;
    }

    // Find link
    const link = await db.pub2_affiliate_links.findOne({
      affiliate_url: { $regex: link_id }
    });

    if (!link) {
      throw new Error(`Link not found: ${link_id}`);
    }

    // Verify tenant match (security check)
    if (link.sub_id_2 !== sub_id_2) {
      throw new Error(`Tenant mismatch: ${link.sub_id_2} !== ${sub_id_2}`);
    }

    // Store conversion
    await db.pub2_conversions.create({
      link_id: link.id,
      event_id,
      order_id,
      order_value,
      commission,
      commission_status,
      purchased_at: new Date(purchased_at)
    });

    // Update video affiliate earnings cache
    await this.updateVideoEarningsCache(link.video_id);

    // Notify influencer
    await this.notifyInfluencerConversion(link.influencer_id, {
      video_id: link.video_id,
      commission,
      order_value
    });

    // Log webhook
    await db.pub2_webhook_logs.create({
      webhook_type: 'conversion',
      payload,
      processed: true
    });
  }

  private async updateVideoEarningsCache(videoId: string) {
    const conversions = await db.pub2_conversions
      .join('pub2_affiliate_links', 'pub2_conversions.link_id', 'pub2_affiliate_links.id')
      .where('pub2_affiliate_links.video_id', videoId)
      .where('pub2_conversions.commission_status', 'confirmed')
      .select('pub2_conversions.*');

    const totalCommission = conversions.reduce((sum, c) => sum + c.commission, 0);

    await db.videos.update(
      { id: videoId },
      { affiliate_earnings: totalCommission }
    );
  }

  private async notifyInfluencerConversion(influencerId: string, data: any) {
    // Send email/push notification
    await notificationService.send({
      user_id: influencerId,
      type: 'affiliate_conversion',
      title: 'New Affiliate Sale! 🎉',
      message: `You earned $${data.commission} from your video!`,
      data
    });
  }
}

export default new Pub2IntegrationService();
```

---

## Summary

### Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Pub2 Partner Structure** | 3 Separate Partners (TCB, AMB, VF) | Clean source handover, billing independence, exit strategy |
| **User Balance** | Separate per Tenant | White-label isolation, clear billing, no data leakage |
| **Portal Display** | Tenant-Isolated UI | Brand identity, compliance, actionable insights |
| **Payout Strategy** | Separate per Tenant (MVP) | Simplicity, clear ownership, can evolve later |

### Implementation Timeline

- **Phase 1 (Week 1-4):** Foundation & Backend
- **Phase 2 (Week 5-8):** Frontend UI
- **Phase 3 (Week 9-12):** Testing & Deployment
- **Phase 4 (Month 4-6):** Enhancements

### Next Steps

1. **Validate with stakeholders:**
   - Present to AccessTrade leadership
   - Review with Techcombank/Vinfast stakeholders
   - Confirm Pub2's capability to support 3 partners

2. **Initiate Phase 1:**
   - AT coordinates Pub2 account setup
   - AT begins backend development
   - Prepare sandbox environment

3. **Documentation:**
   - Update architecture diagrams
   - Write API integration guide
   - Create deployment runbook

---

**Document Owner:** ViewBoost Engineering Team
**Last Updated:** 2026-02-07
**Status:** Architecture Decisions Finalized
**Next Review:** After stakeholder validation
