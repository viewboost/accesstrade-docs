# Brainstorming Session: Đối Soát Tự Động cho Campaign

**Date:** 2026-02-12
**Objective:** Phân tích và thiết kế hệ thống đối soát tự động thay thế quy trình manual cho campaign payments
**Context:** Ambassador platform hiện có quy trình đối soát manual mất 15-20 ngày với 6 bước thủ công. Cần automation để giảm timeline xuống 5-7 ngày, giảm workload cho BTC team 80%, và cải thiện creator experience.

**Current System:**
- Backend: Go (Echo framework) + MongoDB
- Existing models: `Reconciliation`, `ReconciliationItem`, `ReconciliationHistory`, `CashFlow`
- Support types: Content-based, Milestone, Bonus reconciliation
- Manual timeline: 20 days (Cut-off → Validation → Review → Payment)

---

## Techniques Used

1. **SCAMPER** - Biến đổi quy trình manual thành automated
2. **Mind Mapping** - Cấu trúc hóa components và data flows
3. **Six Thinking Hats** - Phân tích đa chiều (technical, risks, benefits, creative)

---

## Quy Trình Manual Hiện Tại

### Timeline (20 ngày)

| Bước | Mô tả | Team/Note | Timing |
|------|-------|-----------|---------|
| **1. Cut-off Data** | Chốt view/số liệu cho chiến dịch | Xác định theo campaign và ngưỡng KPI | Ngày 30-31 hàng tháng |
| **2. Đối Soát View Hợp Lệ** | Chốt số view hợp lệ (link hoạt động, không private/xóa, số view tại thời điểm đối soát) | Kiểm tra link, confirm tính hợp lệ, ghi nhận số liệu | Ngày 6-10 hàng tháng |
| **3. BTC Chốt số view hợp lệ** | BTC chốt số liệu thanh toán chính thức dựa trên số view hợp lệ | View giảm sau đối soát: vẫn tính theo số chốt. Lưu trữ file đối soát để phục vụ audit (nội bộ) | Ngày 11-15 hàng tháng |
| **4. Công bố số chốt cho Creator** | BTC công bố số liệu thanh toán chính thức cho Creator | Không nhận khiếu nại sau thời điểm công bố, đảm bảo minh bạch | Ngày 15 hàng tháng (màn hình hiển thị như bên dưới) |
| **5. Creator hoàn tất hồ sơ thanh toán** | Creator gửi đầy đủ HD/Hóa đơn/Thông tin nhận tiền | Hướng dẫn hoàn thành đăng ký bên dưới (HD, thông tin nhận tiền, hướng dẫn screenshot) | Timing varies |
| **6. Thanh toán** | Thực hiện chi trả theo số liệu đã chốt | Theo thanh toán tháng, có thể thanh toán sớm hơn nếu hồ sơ hoàn thiện | Ngày thứ 5 cuối cùng của tháng |

### Pain Points

**Creators:**
- ⏰ Phải đợi 20 ngày mới nhận payment
- 😟 Không biết trước số tiền sẽ nhận
- 📉 View giảm sau đối soát (không hiểu lý do)
- 📄 Thu thập hồ sơ phức tạp

**BTC Team:**
- 🥵 Volume lớn phải review manual
- 😓 Human errors trong data entry
- ⏱️ Time-consuming validation
- 🔍 Không có tools để detect fraud

**Business:**
- 📉 Slow payment → creator churn
- 💸 Fraud risk không được detect sớm
- 📊 Thiếu data insights
- ⚖️ Không scale được

---

## Ideas Generated

### Category 1: Core Automation Features ⚙️

**1. Scheduled Cut-off Job**
- Cron job tự động chốt data vào ngày 30-31 hàng tháng
- Lock campaign data snapshot
- Trigger validation workflow

**2. Link Status Validator**
- Service check link alive/dead/private
- Scheduled crawling (daily during validation window)
- Handle các social platforms: FB, YT, TikTok

**3. View Count Aggregator**
- Pull view count từ platform APIs
- Cache và compare với database
- Detect discrepancies

**4. Rule-based Calculation Engine**
- Tính cash theo rules: base + bonus + milestone
- Support multiple reward schemas
- Tax calculation integration

**5. Auto-approval Workflow**
- Auto approve items dưới threshold
- Rule-based approval (creator tier, amount, history)
- Immediate cash flow update

**6. Exception Queue System**
- Queue items cần BTC manual review
- Prioritization: value, risk score, fraud alert
- SLA tracking

**7. Payment Trigger Service**
- Auto trigger payment khi conditions met:
  - Reconciliation closed
  - Documents submitted
  - Approval complete
- Integration với payment gateway

---

### Category 2: External Integrations 🔌

**8. Facebook Graph API Integration**
- OAuth flow cho creator authorization
- Fetch post insights: views, engagement
- Handle rate limits, pagination

**9. YouTube Data API Integration**
- YouTube Analytics API
- Video statistics: views, watch time, engagement
- Channel metrics

**10. TikTok API Integration**
- TikTok Creator API
- Video views, engagement metrics
- Handle regional restrictions

**11. Bank API Integration**
- Auto payment disbursement
- Payment status tracking
- Reconciliation với accounting system

**12. SMS Gateway Integration**
- Twilio/local SMS provider
- Critical notifications (payment sent, action required)
- OTP for sensitive operations

**13. Email Service Integration**
- SendGrid/AWS SES
- Rich email templates
- Delivery tracking

**14. Accounting System Sync**
- Đồng bộ cashflow với hệ thống kế toán
- Tax reporting integration
- Audit trail export

---

### Category 3: Data & Analytics 📊

**15. Real-time Dashboard (BTC Admin)**
- Live reconciliation progress
- Exception queue
- System health monitoring
- Creator distribution charts

**16. Creator Portal**
- Creator self-service dashboard
- View reconciliation status
- Download payment history
- Submit disputes

**17. Reconciliation Reports**
- Auto-generate Excel/PDF reports
- Campaign summary
- Creator breakdown
- Tax reports

**18. Performance Analytics**
- Campaign ROI metrics
- Creator performance scoring
- Engagement analysis
- Trend visualization

**19. Fraud Detection Dashboard**
- Suspicious patterns visualization
- Anomaly timeline
- Creator risk scores
- Action recommendations

**20. Audit Trail Logging**
- Immutable history log
- Who/what/when tracking
- Compliance reporting
- Data export

**21. Data Export Tools**
- CSV/Excel export
- API for external systems
- Scheduled exports
- Custom report builder

---

### Category 4: Validation & Quality Control ✅

**22. Engagement Validator**
- Check likes/comments ratio
- Engagement rate calculation
- Detect fake engagement

**23. Duplicate Content Detector**
- Content fingerprinting
- Cross-platform duplicate detection
- Prevent double-claiming

**24. View Velocity Anomaly Detection**
- Statistical anomaly detection
- Sudden spike alerts
- Bot traffic detection

**25. Cross-platform Validation**
- Verify creator không claim same content multiple times
- Link content across platforms
- Unified content ID

**26. Document Validator**
- OCR for invoice/HD validation
- Required field extraction
- Format validation

**27. Threshold Monitoring**
- Auto alerts when approaching thresholds
- Budget cap enforcement
- Creator limit tracking

**28. Quality Score System**
- Score creators based on:
  - Content quality
  - Engagement rate
  - Compliance history
  - Document submission timeliness

---

### Category 5: UX & Notifications 🔔

**29. Multi-channel Notifications**
- Email + In-app + SMS
- User preference management
- Delivery confirmation

**30. Status Update Webhooks**
- Real-time status push
- Third-party integrations
- Mobile app sync

**31. Chatbot Support**
- FAQ bot cho common queries
- Status lookup via chat
- Document submission guide

**32. Push Notifications**
- Mobile push via Firebase
- Critical updates
- Action reminders

**33. Customizable Alerts**
- Creator configure notification preferences
- Frequency control
- Channel selection

**34. Interactive Timeline**
- Visual timeline cho reconciliation process
- Progress indicators
- Estimated completion dates

**35. Self-serve Dispute System**
- Creator submit disputes với evidence
- Automated triage
- BTC review queue

---

### Category 6: Advanced & Innovative 🚀

**36. ML-based Fraud Detection**
- Train model trên historical fraud patterns
- Real-time scoring
- Continuous learning

**37. Predictive Payment Estimation**
- AI predict payment amount real-time
- Predict payment date
- Confidence intervals

**38. Dynamic Scheduling**
- Adjust cut-off date dựa trên completion rate
- Smart deadline extension
- Resource optimization

**39. Tiered Automation Levels**
- Bronze/Silver/Gold/Diamond tiers
- Different auto-approval thresholds
- Creator incentive program

**40. Real-time Reconciliation Preview**
- Creator see estimated payment khi content live
- Real-time view tracking
- What-if scenarios

**41. Blockchain Audit Trail**
- Immutable reconciliation history
- Smart contract automation
- Transparency for partners

**42. Community Validation**
- Peer review system
- Top creators validate newcomers
- Reputation building

**43. Gamification System**
- Creator leveling system
- Badges, achievements
- Unlock features with level

---

### Category 7: Risk Mitigation 🛡️

**44. Rate Limiter**
- Handle platform API rate limits
- Request queuing
- Exponential backoff

**45. Retry Mechanism**
- Auto retry failed API calls
- Retry strategy configuration
- Dead letter queue

**46. Circuit Breaker**
- Prevent cascade failures
- Fallback mechanisms
- Auto recovery

**47. Data Backup & Recovery**
- Regular MongoDB backups
- Point-in-time recovery
- Disaster recovery plan

**48. Rollback Mechanism**
- Quick rollback for bad deployments
- Data rollback procedures
- Version control

**49. Shadow Mode Testing**
- Run automation parallel với manual
- Compare results
- Validate accuracy

**50. Gradual Rollout Strategy**
- Feature flags
- Phased rollout: 10% → 25% → 50% → 100%
- Quick rollback capability

---

### Category 8: Operations & Support 🛠️

**51. Admin Exception Handling UI**
- BTC review exceptions
- Quick approve/reject
- Add notes/reasons

**52. Manual Override Controls**
- BTC override auto decisions
- Audit log for overrides
- Approval workflows

**53. Bulk Operations**
- Bulk approve/reject
- Batch status updates
- Mass notifications

**54. Template Management**
- Notification template editor
- Email/SMS templates
- Multi-language support

**55. Configuration Dashboard**
- Config rules, thresholds, schedules
- Feature flags management
- Environment-specific configs

**56. System Health Monitoring**
- Job status monitoring
- API health checks
- Alert on failures

**57. Training & Documentation**
- User guides (BTC + Creator)
- Video tutorials
- Change logs

---

## Statistics

- **Total ideas generated:** 57
- **Categories:** 8
- **Techniques applied:** 3 (SCAMPER, Mind Mapping, Six Thinking Hats)
- **Key insights:** 7

---

## Key Insights

### 🎯 Insight 1: Reverse Workflow Architecture - "Validate Early, Chốt Late"

**Mô tả:**
Thay vì chốt data trước rồi validate sau (manual process), áp dụng **continuous validation** ngay từ khi content published, và chỉ chốt khi validation complete.

**Source:** SCAMPER (Reverse), Six Thinking Hats (Green - Creativity)

**Impact:** 🔥 **High** - Giảm timeline từ 20 ngày → 5-7 ngày (65% reduction)

**Effort:** 🟡 **Medium** - Refactor workflow logic, không quá phức tạp

**Tại sao quan trọng:**
- ✅ **Giảm wait time:** Creator không phải chờ đến ngày 6-10 mới biết view có hợp lệ
- ✅ **Real-time feedback:** Creator biết ngay nếu link bị private/xóa và có thể fix
- ✅ **Reduce rework:** Validation sớm giảm việc phải reject và redo sau
- ✅ **Better UX:** Transparency tăng → Creator trust tăng

**Implementation:**
```
❌ Traditional:  Cut-off (Day 30) → Validate (Day 6-10) → Chốt (Day 11-15) = 20 days
✅ Reverse:      Publish → Continuous Validation → Ready to Chốt (Day 5-7) = 7 days
```

**Next Steps:**
1. Design event-driven validation pipeline
2. Implement webhook listeners for content publish events
3. Build validation scheduler (daily checks)
4. Create "ready to reconcile" status indicator

---

### 🎯 Insight 2: Tiered Automation Strategy - "Trust-based Automation Levels"

**Mô tả:**
Không apply 100% automation cho tất cả creators. Phân tầng automation dựa trên **creator history, reputation, và transaction size**.

**Source:** Six Thinking Hats (Green - Creativity, Black - Caution), Mind Mapping (Process Layer)

**Impact:** 🔥 **High** - Balance giữa efficiency và risk mitigation

**Effort:** 🟡 **Medium** - Cần creator scoring system

**Tại sao quan trọng:**
- ✅ **Risk management:** High-value/new creators → more validation, trusted creators → full automation
- ✅ **Fraud prevention:** Reduce risk of large fraud losses
- ✅ **Scalability:** Start automation với low-risk segments trước
- ✅ **Creator incentive:** Gamification - creators có động lực build reputation

**Proposed Tiers:**

| Tier | Criteria | Auto-approval Threshold | Review Level |
|------|----------|------------------------|--------------|
| 🥉 **Bronze** | New creators, <10 campaigns | < $100 | Manual BTC review required |
| 🥈 **Silver** | Established, 10-50 campaigns, good history | < $500 | Exception review only |
| 🥇 **Gold** | >50 campaigns, excellent history | < $2,000 | Spot-check only |
| 💎 **Diamond** | Top 1%, strategic partners | Unlimited | Post-payment audit only |

**Scoring Factors:**
- Number of campaigns completed
- Fraud history (0 = good)
- Document submission timeliness
- View/engagement quality score
- Compliance violations

**Next Steps:**
1. Design creator scoring algorithm
2. Build tier assignment logic
3. Create tier progression system
4. Implement tiered approval workflows

---

### 🎯 Insight 3: Exception-First Architecture - "Auto Everything, Manual Only Exceptions"

**Mô tả:**
Design system với assumption là **90%+ cases sẽ auto-approve** thành công. UI và workflow optimize cho việc **handle 10% exceptions**, không phải review 100% items.

**Source:** SCAMPER (Eliminate, Modify), Six Thinking Hats (Yellow - Benefits)

**Impact:** 🔥 **High** - BTC workload giảm 80%

**Effort:** 🟢 **Low** - Mainly UI/UX redesign, backend logic đơn giản

**Tại sao quan trọng:**
- ✅ **BTC focus shift:** Từ data entry → strategic review và problem-solving
- ✅ **Scalability:** System handle growth mà không cần tăng BTC headcount
- ✅ **Faster processing:** Không bottleneck ở BTC review
- ✅ **Better audit trail:** Focus audit effort on high-risk items

**UI/UX Comparison:**

```
❌ Old UI (Manual-first):
   ├── List all items (100% review needed)
   ├── Review one by one
   └── Approve/Reject each

✅ New UI (Exception-first):
   ├── Dashboard: "🎉 95% auto-approved, ⚠️ 5% need review"
   ├── Exception Queue (filtered, prioritized)
   │   ├── 🔴 High value (>$1000)
   │   ├── 🚨 Fraud alerts
   │   ├── ⚡ Anomaly detected
   │   └── 👤 First-time creator
   └── Quick bulk actions for exceptions
```

**Exception Triggers:**
- Amount > tier threshold
- Fraud score > risk threshold
- First-time creator (no history)
- View velocity anomaly detected
- Link validation failed
- Document missing/invalid
- Cross-platform duplicate detected

**Next Steps:**
1. Design exception queue UI
2. Build prioritization logic
3. Implement bulk approval actions
4. Create exception analytics dashboard

---

### 🎯 Insight 4: Shadow Mode Validation - "Prove Before Replace"

**Mô tả:**
Chạy automation **song song với manual process** trong 1-2 cycles để **validate accuracy** trước khi fully replace manual.

**Source:** Six Thinking Hats (Black - Caution, Blue - Process)

**Impact:** 🔥 **High** - Risk mitigation critical cho financial system

**Effort:** 🟡 **Medium** - Cần infrastructure để run parallel

**Tại sao quan trọng:**
- ✅ **Trust building:** Prove automation accuracy với real data
- ✅ **Bug detection:** Catch logic errors trước khi impact creators
- ✅ **Smooth transition:** BTC team học system mà không áp lực
- ✅ **Rollback safety:** Có manual baseline để compare

**3-Phase Rollout:**

**Phase 1: Shadow Mode (Month 1)**
```
├── Run automation in background (không affect production)
├── BTC still do manual process (business as usual)
├── Compare results: Auto vs Manual
│   ├── Match rate target: >95%
│   ├── Analyze discrepancies
│   └── Fix automation logic
└── Success criteria: 95%+ accuracy, 0 critical bugs
```

**Phase 2: Hybrid Mode (Month 2)**
```
├── Auto-approve low-risk items (Bronze/Silver creators, <$500)
├── Manual review:
│   ├── All exceptions
│   └── Random sample 20% của auto-approved items
├── Monitor error rate
└── Adjust rules/thresholds based on data
```

**Phase 3: Full Auto (Month 3+)**
```
├── 90%+ auto-approved
├── Manual review exceptions only
├── Post-payment random audits (5%)
└── Continuous monitoring & optimization
```

**Success Metrics:**
- Accuracy: >99% (auto vs manual match)
- Creator complaints: <1% of total
- Payment errors: <0.1% of transactions
- BTC workload: <20% of original

**Next Steps:**
1. Set up shadow mode infrastructure
2. Build comparison reporting
3. Define success criteria
4. Plan rollback procedures

---

### 🎯 Insight 5: API-First Data Collection - "Pull, Don't Push"

**Mô tả:**
Thay vì rely on creators tự report view numbers (push model), system **chủ động pull data từ platforms** (Facebook, YouTube, TikTok APIs).

**Source:** SCAMPER (Substitute, Eliminate), Mind Mapping (External Integrations)

**Impact:** 🔥 **High** - Eliminate fraud from fake view reports

**Effort:** 🔴 **High** - Complex API integrations, rate limit handling

**Tại sao quan trọng:**
- ✅ **Data accuracy:** Single source of truth từ platforms
- ✅ **Fraud prevention:** Creators không thể manipulate view counts
- ✅ **Real-time data:** View counts updated real-time
- ✅ **Audit trail:** Verifiable data provenance

**Platform APIs:**

| Platform | API | Metrics Available | Rate Limits |
|----------|-----|-------------------|-------------|
| **Facebook** | Graph API | Post insights: views, reach, engagement | 200 calls/hour/user |
| **YouTube** | YouTube Data API v3 | Video statistics: views, likes, comments | 10,000 quota units/day |
| **TikTok** | Creator API | Video views, shares, engagement | Varies by tier |

**Challenges & Solutions:**

**Challenge 1: API Rate Limits**
```
Problem: Limited API calls per day/hour
Solutions:
├── Smart caching: Cache view counts, refresh only when needed
├── Batch requests: Group multiple content checks
├── Rate limiter: Queue requests, respect limits
└── Incremental updates: Only fetch new/changed content
```

**Challenge 2: Platform API Changes**
```
Problem: APIs change, break integrations
Solutions:
├── Adapter pattern: Abstract platform-specific logic
├── Versioned integrations: Support multiple API versions
├── Monitoring: Alert on API errors
└── Fallback: Manual entry as backup
```

**Challenge 3: Private Content Access**
```
Problem: Cannot access private/deleted content
Solutions:
├── Creator OAuth: Creator authorizes app access
├── Link validation: Pre-check content accessibility
└── Grace period: Allow creator to fix before rejection
```

**Challenge 4: API Costs**
```
Problem: Some APIs charge per call
Solutions:
├── Cache aggressively: 24h cache for view counts
├── Fetch only when needed: During validation window only
├── Batch operations: Reduce API call count
└── Cost monitoring: Alert on budget exceeded
```

**Next Steps:**
1. Register for platform APIs (FB, YT, TikTok)
2. Build OAuth authorization flow
3. Implement API adapters
4. Set up caching layer
5. Build rate limiter

---

### 🎯 Insight 6: Event-Driven Notification System - "Push, Don't Pull"

**Mô tả:**
Thay vì creators phải login check status (pull), system **push notifications** qua multiple channels (email, in-app, SMS) mỗi khi có status change.

**Source:** SCAMPER (Modify), Mind Mapping (Output Layer)

**Impact:** 🟡 **Medium** - Improve creator experience, reduce support load

**Effort:** 🟢 **Low** - Standard notification infrastructure

**Tại sao quan trọng:**
- ✅ **Transparency:** Creator always informed về status
- ✅ **Reduce support load:** Fewer "where's my payment" questions
- ✅ **Trust building:** Proactive communication
- ✅ **Action prompts:** Notify when creator action needed

**Notification Triggers & Templates:**

| Event | Channels | Template | Action Required |
|-------|----------|----------|-----------------|
| 🔒 **Cut-off Complete** | Email + In-app | "Campaign [X] data locked. Validation in progress." | None |
| ✅ **Validation Complete** | Email + In-app + SMS | "Validation complete: [X] views valid, [Y] rejected. Reason: [...]" | Review reasons |
| ⏳ **BTC Review Needed** | Email + In-app | "Your submission needs review. Reason: [high value/anomaly/first-time]" | Wait |
| 💰 **Amount Announced** | Email + In-app + SMS | "Payment approved: $XXX. Breakdown: [base + bonus + milestone]" | None |
| 📄 **Document Needed** | Email + In-app | "Upload invoice/HD by [date] to receive payment" | **Upload docs** |
| 🚀 **Payment Processing** | Email + In-app | "Payment initiated. Expect by [date]" | None |
| ✅ **Payment Complete** | Email + In-app + SMS | "Payment sent: $XXX to [account]. Check your bank." | Confirm receipt |
| ❌ **Rejection** | Email + In-app | "Content rejected. Reason: [...]. Appeal: [link]" | Appeal/Fix |

**Multi-channel Strategy:**

```
High Priority (Payment, Rejection):
└── Email + In-app + SMS

Medium Priority (Validation, Documents):
└── Email + In-app

Low Priority (Status updates):
└── In-app only
```

**User Preferences:**
- Allow creators customize notification channels
- Frequency control (instant, daily digest)
- Quiet hours
- Language preference

**Next Steps:**
1. Set up notification infrastructure (SendGrid, SMS gateway)
2. Build event-driven architecture (event bus)
3. Create notification templates
4. Implement user preference management
5. Build in-app notification center

---

### 🎯 Insight 7: Progressive Rollout Strategy - "Crawl, Walk, Run"

**Mô tả:**
Không launch automation 100% ngay. Rollout theo phases: **10% → 25% → 50% → 100%** traffic qua automation.

**Source:** Six Thinking Hats (Black - Caution, Blue - Process)

**Impact:** 🔥 **High** - Critical risk mitigation, limit blast radius

**Effort:** 🟢 **Low** - Feature flag infrastructure

**Tại sao quan trọng:**
- ✅ **Limit blast radius:** Bugs chỉ affect small % creators
- ✅ **Fast feedback loop:** Detect issues sớm với small sample
- ✅ **Team confidence:** Build confidence incrementally
- ✅ **Easy rollback:** Quick revert nếu có critical issues

**Rollout Plan:**

**Phase 1: Internal Testing (Week 1-2)**
```
Target: Internal test campaigns only
Traffic: 0% production traffic
Goals:
├── Test tất cả features
├── Fix obvious bugs
├── Validate infrastructure
└── Train BTC team

Success Criteria:
├── 0 critical bugs
├── All features functional
└── BTC team trained
```

**Phase 2: Beta Group (Week 3-4)**
```
Target: 10% creators (volunteers, trusted creators)
Traffic: 10% of reconciliations
Goals:
├── Real-world testing
├── Intensive monitoring
├── Collect feedback
└── Validate accuracy vs manual

Monitoring:
├── Error rate < 1%
├── Creator satisfaction > 80%
├── No payment errors
└── System performance OK

Exit Criteria:
├── 95%+ accuracy
├── <5 critical issues
└── Positive creator feedback
```

**Phase 3: Gradual Expansion (Week 5-8)**
```
Week 5: 25% traffic
├── Expand to more creator tiers
├── Monitor error rates
└── Optimize based on data

Week 6: 50% traffic
├── Half of reconciliations automated
├── Reduce BTC review workload
└── Continue monitoring

Week 7: 75% traffic
├── Most reconciliations automated
├── BTC focus on exceptions only
└── Performance optimization

Week 8: Review & Optimize
├── Analyze full funnel metrics
├── Fix remaining issues
└── Prepare for 100% rollout

Success Metrics:
├── Error rate < 0.5%
├── BTC workload reduced 60%+
├── Creator complaints < 2%
└── Payment accuracy 99.9%+
```

**Phase 4: Full Rollout (Week 9+)**
```
Target: 100% traffic
Traffic: All reconciliations automated
Goals:
├── Full automation
├── Manual process as fallback only
├── Continuous optimization
└── Scale to handle growth

Monitoring:
├── Real-time dashboards
├── Alert on anomalies
├── Weekly metrics review
└── Monthly optimization sprints

Manual Fallback:
├── Emergency rollback to manual
├── Specific creator/campaign manual override
└── Hybrid mode if needed
```

**Feature Flag Strategy:**
```yaml
features:
  auto_reconciliation:
    enabled: true
    rollout_percentage: 10  # Start at 10%
    rollout_strategy: "creator_tier"  # Or "random", "campaign_type"
    tiers_enabled: ["gold", "diamond"]  # Start with trusted tiers

  auto_payment:
    enabled: false  # Enable later after reconciliation stable
    rollout_percentage: 0
```

**Rollback Triggers:**
- Error rate > 2%
- Payment accuracy < 99%
- Creator complaints spike
- System downtime
- Critical bug discovered

**Next Steps:**
1. Set up feature flag system (LaunchDarkly or custom)
2. Define rollout criteria
3. Build rollback procedures
4. Create monitoring dashboards
5. Prepare communication plan

---

## Technical Architecture Recommendations

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway / Load Balancer               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐      ┌────────▼────────┐     ┌────────▼────────┐
│   Web Admin    │      │  Creator Portal │     │   Mobile App    │
│   (BTC Team)   │      │   (Creators)    │     │   (Creators)    │
└───────┬────────┘      └────────┬────────┘     └────────┬────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Ambassador Backend    │
                    │   (Go + Echo)           │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐      ┌────────▼────────┐     ┌────────▼────────┐
│   Reconciliation│      │   Notification  │     │   Integration   │
│   Service       │      │   Service       │     │   Layer         │
│                 │      │                 │     │                 │
│ - Schedulers    │      │ - Email         │     │ - FB API        │
│ - Validators    │      │ - SMS           │     │ - YT API        │
│ - Calculators   │      │ - In-app        │     │ - TikTok API    │
│ - Approval      │      │ - Webhooks      │     │ - Payment API   │
└───────┬────────┘      └────────┬────────┘     └────────┬────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      MongoDB            │
                    │   (Primary Database)    │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │   Redis / Job Queue     │
                    │   (Caching + Jobs)      │
                    └─────────────────────────┘
```

### Data Flow: Auto Reconciliation

```
1. Content Published (Creator)
   ↓
2. Event: content.published → Validation Queue
   ↓
3. Scheduler: Daily Validation Job
   ├── Check link status (alive/dead/private)
   ├── Pull view count from platform API
   ├── Calculate engagement metrics
   └── Update validation status
   ↓
4. Cut-off Date Reached (Day 30-31)
   ├── Lock campaign data snapshot
   ├── Trigger reconciliation calculation
   └── Create ReconciliationItem records
   ↓
5. Calculation Engine
   ├── Base cash = valid views × rate
   ├── Milestone bonus (if achieved)
   ├── Event bonus (if applicable)
   ├── Tax calculation (if > threshold)
   └── Total cash
   ↓
6. Approval Workflow
   ├── Check creator tier
   ├── Check amount threshold
   ├── Check fraud score
   └── Decision:
       ├── Auto-approve (90% cases) → Status: Completed
       └── Exception queue (10% cases) → Status: Pending BTC Review
   ↓
7. Notification
   ├── Creator: "Amount announced: $XXX"
   └── BTC: "X items auto-approved, Y need review"
   ↓
8. BTC Review (Exceptions Only)
   ├── Review high-value items
   ├── Investigate fraud alerts
   ├── Approve/Reject with reason
   └── Update status
   ↓
9. Document Collection
   ├── Creator uploads HD/Invoice
   ├── Document validator checks format
   └── Status: Ready for Payment
   ↓
10. Payment Processing (Day 5 of month)
    ├── Trigger payment gateway
    ├── Update CashFlow
    ├── Notification: "Payment sent"
    └── Status: Paid
```

### Database Schema Updates

**New Collections:**

```javascript
// reconciliation_rules
{
  _id: ObjectId,
  name: "auto_approve_gold_tier",
  conditions: {
    creatorTier: "gold",
    maxAmount: 2000,
    minHistoryCount: 50,
    fraudScore: { $lt: 0.1 }
  },
  action: "auto_approve",
  priority: 100,
  enabled: true,
  createdAt: Date,
  updatedAt: Date
}

// creator_scores
{
  _id: ObjectId,
  userId: ObjectId,
  tier: "gold", // bronze, silver, gold, diamond
  scores: {
    fraudScore: 0.05,        // 0-1, lower is better
    qualityScore: 0.92,      // 0-1, higher is better
    complianceScore: 0.98,   // 0-1, higher is better
    engagementScore: 0.85    // 0-1, higher is better
  },
  stats: {
    totalCampaigns: 67,
    totalEarned: 45000,
    avgViewQuality: 0.9,
    documentSubmissionRate: 1.0,
    fraudViolations: 0,
    disputesWon: 2
  },
  history: [...],
  updatedAt: Date
}

// validation_logs
{
  _id: ObjectId,
  contentId: ObjectId,
  reconciliationId: ObjectId,
  validationType: "link_status", // or "view_count", "engagement", "fraud"
  result: "valid", // or "invalid", "warning"
  data: {
    linkStatus: "alive",
    statusCode: 200,
    viewCount: 15234,
    viewSource: "facebook_api",
    checkedAt: Date
  },
  createdAt: Date
}

// exception_queue
{
  _id: ObjectId,
  reconciliationItemId: ObjectId,
  reason: "high_value", // or "fraud_alert", "anomaly", "first_time"
  priority: "high", // high, medium, low
  assignedTo: ObjectId, // BTC user
  status: "pending", // pending, in_review, resolved
  metadata: {...},
  createdAt: Date,
  resolvedAt: Date
}
```

**Updated Collections:**

```javascript
// reconciliation_items (add fields)
{
  ...existing_fields,

  // NEW: Automation fields
  automationStatus: "auto_approved", // or "exception", "manual_review"
  approvalRule: ObjectId, // reference to reconciliation_rules
  fraudScore: 0.05,
  qualityScore: 0.92,

  // NEW: Validation fields
  validationHistory: [
    {
      type: "link_status",
      result: "valid",
      checkedAt: Date
    }
  ],

  // NEW: Notification tracking
  notifications: [
    {
      type: "amount_announced",
      channels: ["email", "in_app"],
      sentAt: Date,
      status: "delivered"
    }
  ]
}
```

### Scheduler Jobs (Cron)

```go
// internal/scheduler/reconciliation_scheduler.go

// Daily validation job (runs every day during validation window)
// Cron: 0 2 * * * (2 AM daily)
func DailyValidationJob() {
  // 1. Get active reconciliations in validation period
  // 2. For each reconciliation item:
  //    - Check link status
  //    - Pull view count from API
  //    - Calculate engagement
  //    - Update validation status
  // 3. Detect anomalies and create alerts
}

// Monthly cut-off job (runs on day 30-31)
// Cron: 0 0 30,31 * * (midnight on day 30 or 31)
func MonthlyCutoffJob() {
  // 1. Get campaigns ending this month
  // 2. Lock data snapshot
  // 3. Create reconciliation records
  // 4. Trigger calculation workflow
  // 5. Send notifications
}

// Payment processing job (runs on 5th last day of month)
// Cron: 0 9 25-31 * * (check if 5th last day)
func MonthlyPaymentJob() {
  // 1. Get reconciliation items ready for payment
  //    - Status: Completed
  //    - Documents: Submitted
  // 2. Trigger payment gateway
  // 3. Update cashflow
  // 4. Send notifications
}

// Fraud detection ML job (runs daily)
// Cron: 0 3 * * * (3 AM daily)
func DailyFraudDetectionJob() {
  // 1. Fetch recent reconciliation items
  // 2. Run ML model inference
  // 3. Update fraud scores
  // 4. Create exception queue items for high-risk
  // 5. Alert BTC team
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2) 🏗️

**Goals:**
- Setup infrastructure
- Build core services
- Database schema updates

**Tasks:**
1. **Scheduler Infrastructure**
   - Set up cron job framework
   - Build job monitoring
   - Error handling & retries

2. **Validation Service**
   - Link status checker
   - Basic rule engine
   - Logging infrastructure

3. **Database Updates**
   - Add new collections
   - Update existing schemas
   - Migration scripts

4. **Feature Flags**
   - Set up feature flag system
   - Define flags for rollout
   - Admin UI for flags

**Deliverables:**
- ✅ Scheduler running daily
- ✅ Link validation working
- ✅ Database schema updated
- ✅ Feature flags operational

---

### Phase 2: Core Automation (Week 3-4) ⚙️

**Goals:**
- Auto cut-off
- Auto validation
- Auto calculation
- Basic approval workflow

**Tasks:**
1. **Cut-off Automation**
   - Monthly cut-off job
   - Data snapshot logic
   - Campaign locking

2. **Validation Engine**
   - Link status validation
   - View count validation
   - Engagement calculation
   - Validation history tracking

3. **Calculation Engine**
   - Base cash calculation
   - Bonus calculation
   - Tax calculation
   - Total aggregation

4. **Approval Workflow v1**
   - Simple rule-based approval
   - Threshold-based auto-approve
   - Exception queue

**Deliverables:**
- ✅ Auto cut-off working
- ✅ Validation automated
- ✅ Calculation accurate
- ✅ Basic auto-approval

---

### Phase 3: External Integration (Week 5-6) 🔌

**Goals:**
- Platform API integrations
- Payment gateway
- Notification system

**Tasks:**
1. **Facebook API Integration**
   - OAuth setup
   - Graph API calls
   - Rate limit handling
   - Caching layer

2. **YouTube API Integration**
   - YouTube Data API v3
   - Video statistics
   - Quota management

3. **TikTok API Integration**
   - Creator API setup
   - Video metrics
   - Error handling

4. **Payment Gateway**
   - Bank API integration
   - Payment disbursement
   - Status tracking

5. **Notification System**
   - SendGrid/AWS SES setup
   - SMS gateway (Twilio)
   - Email templates
   - In-app notifications

**Deliverables:**
- ✅ FB/YT/TikTok data pulling
- ✅ Payment automation working
- ✅ Multi-channel notifications

---

### Phase 4: Advanced Features (Week 7-8) 🚀

**Goals:**
- Creator scoring
- Tiered automation
- Fraud detection
- Admin UI

**Tasks:**
1. **Creator Scoring System**
   - Scoring algorithm
   - Tier assignment
   - History tracking
   - Score updates

2. **Tiered Automation**
   - Bronze/Silver/Gold/Diamond logic
   - Different thresholds per tier
   - Tier progression

3. **Fraud Detection (Basic)**
   - Rule-based anomaly detection
   - View velocity checks
   - Engagement validation
   - Fraud alerts

4. **Admin UI (Exception Handling)**
   - Exception queue dashboard
   - Quick approve/reject
   - Bulk operations
   - Notes & reasons

5. **Creator Portal**
   - Reconciliation status page
   - Payment history
   - Document upload
   - Notifications center

6. **Reporting & Analytics**
   - Real-time dashboard
   - Excel export
   - Performance metrics
   - System health

**Deliverables:**
- ✅ Creator tiers working
- ✅ Fraud detection alerts
- ✅ Admin UI complete
- ✅ Creator portal functional
- ✅ Reports & dashboards

---

### Phase 5: Testing & Rollout (Week 9-10) ✅

**Goals:**
- Shadow mode testing
- Parallel validation
- Gradual rollout
- Training & docs

**Tasks:**
1. **Shadow Mode (Week 9)**
   - Run automation in background
   - Manual process continues
   - Compare results
   - Fix discrepancies
   - Target: 95%+ accuracy

2. **Hybrid Mode (Week 10)**
   - 10% traffic automated
   - Monitor closely
   - Collect feedback
   - Optimize rules

3. **Training & Documentation**
   - BTC team training
   - Creator guides
   - Video tutorials
   - FAQ documentation

4. **Monitoring & Alerting**
   - Set up alerts
   - Dashboard for BTC
   - Error tracking
   - Performance monitoring

**Deliverables:**
- ✅ 95%+ accuracy proven
- ✅ 10% rollout successful
- ✅ Team trained
- ✅ Documentation complete

---

### Phase 6: Scale & Optimize (Week 11+) 📈

**Goals:**
- Scale to 100%
- ML fraud detection
- Performance optimization
- Continuous improvement

**Tasks:**
1. **Gradual Rollout**
   - Week 11: 25%
   - Week 12: 50%
   - Week 13: 75%
   - Week 14: 100%

2. **ML Fraud Detection**
   - Collect training data
   - Train ML model
   - Deploy model
   - Continuous learning

3. **Performance Optimization**
   - Database indexing
   - Query optimization
   - Caching improvements
   - API rate optimization

4. **Advanced Features**
   - Real-time reconciliation preview
   - Predictive payment estimation
   - Blockchain audit trail (if needed)
   - Chatbot support

**Deliverables:**
- ✅ 100% rollout complete
- ✅ ML fraud detection live
- ✅ System optimized
- ✅ Advanced features shipped

---

## Success Metrics & KPIs

### Timeline Efficiency
- ✅ **Target:** Reconciliation timeline < 7 days (vs 20 days manual)
- 📊 **Measure:** Avg days from cut-off to payment

### Automation Rate
- ✅ **Target:** >90% auto-approval rate
- 📊 **Measure:** % of items auto-approved vs exceptions

### Accuracy
- ✅ **Target:** >99% accuracy (auto vs manual)
- 📊 **Measure:** Error rate, payment corrections

### BTC Workload Reduction
- ✅ **Target:** 80% workload reduction
- 📊 **Measure:** Hours spent on reconciliation tasks

### Creator Satisfaction
- ✅ **Target:** NPS > 50
- 📊 **Measure:** Creator surveys, complaint rate

### Financial
- ✅ **Target:** Fraud losses < 0.1% of total payments
- 📊 **Measure:** Fraud detected, losses prevented

### System Performance
- ✅ **Target:** 99.9% uptime
- 📊 **Measure:** System availability, job success rate

---

## Risk Mitigation Plan

### Technical Risks

**Risk 1: API Rate Limits**
- **Probability:** High
- **Impact:** Medium
- **Mitigation:**
  - Implement aggressive caching (24h)
  - Batch API requests
  - Rate limiter with queue
  - Fallback to manual entry

**Risk 2: Data Accuracy Issues**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Shadow mode validation
  - Parallel run for 1-2 cycles
  - Random audit sampling
  - Quick rollback capability

**Risk 3: Payment Errors**
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:**
  - Manual review for high-value items
  - Dual approval for >$5000
  - Pre-payment validation
  - Rollback mechanism

### Business Risks

**Risk 4: Creator Trust Erosion**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Transparent communication
  - Shadow mode to prove accuracy
  - Quick issue resolution
  - Compensation for errors

**Risk 5: Fraud Increase**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Multi-layer fraud detection
  - Tiered automation (trust-based)
  - Post-payment audits
  - ML fraud detection

### Operational Risks

**Risk 6: Team Resistance**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Early training
  - Gradual rollout
  - Show efficiency gains
  - Involve team in design

**Risk 7: System Complexity**
- **Probability:** High
- **Impact:** Medium
- **Mitigation:**
  - Comprehensive documentation
  - Monitoring & alerting
  - Runbooks for common issues
  - Dedicated support team

---

## Recommended Next Steps

### Immediate Actions (This Week)

1. **Stakeholder Alignment**
   - Present brainstorming results to leadership
   - Get buy-in on approach
   - Secure budget & resources

2. **Technical Validation**
   - Validate API access (FB, YT, TikTok)
   - Check API quotas & costs
   - Assess infrastructure needs

3. **Team Formation**
   - Assign backend developers (2-3)
   - Assign frontend developer (1)
   - Identify BTC champion for requirements

### Short-term (Next 2 Weeks)

4. **Detailed Planning**
   - Create detailed PRD (Product Requirements Document)
   - Technical architecture design
   - Database schema finalization

5. **Prototype**
   - Build POC for link validation
   - Test platform API integrations
   - Validate calculation logic

### Medium-term (Next Month)

6. **Phase 1 Execution**
   - Build foundation (scheduler, validators)
   - Database migration
   - Basic automation

7. **Shadow Mode Setup**
   - Parallel run infrastructure
   - Comparison reporting
   - Monitoring setup

### Long-term (Next Quarter)

8. **Full Rollout**
   - Gradual rollout 10% → 100%
   - Training & documentation
   - Optimization & scaling

---

## Conclusion

**Đối soát tự động** là một chuyển đổi quan trọng từ manual operations sang automated, data-driven process. Với chiến lược **Reverse Workflow** (validate sớm), **Tiered Automation** (trust-based), và **Exception-First Architecture** (focus on 10% exceptions), hệ thống sẽ:

✅ **Giảm timeline từ 20 ngày → 5-7 ngày** (65% faster)
✅ **Giảm BTC workload 80%** (focus on strategic work)
✅ **Tăng accuracy >99%** (API-driven data)
✅ **Ngăn chặn fraud** (ML detection)
✅ **Cải thiện creator experience** (real-time transparency)

**Keys to Success:**
1. 🎯 **Shadow mode validation** - Prove accuracy trước khi replace manual
2. 🎯 **Progressive rollout** - Limit risk, fast feedback
3. 🎯 **Exception-first UI** - Optimize for 90% auto-approve
4. 🎯 **API-first data** - Single source of truth
5. 🎯 **Event-driven notifications** - Proactive communication

**Next Workflow Recommendation:**
👉 **/bmad:tech-spec** - Create technical specification document với:
- Detailed API contracts
- Database schemas
- Service architectures
- Integration specs
- Security & compliance requirements

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: ~45 minutes*
*Document: accesstrade-projects/docs/operation-optimize/brainstorming-auto-reconciliation-20260212.md*
