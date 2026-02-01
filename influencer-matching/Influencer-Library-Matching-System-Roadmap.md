# LỘ TRÌNH PHÁT TRIỂN SẢN PHẨM - BÁO CÁO CHO ACCESSTRADE

**Ngày:** 2026-02-01
**Người viết:** Product Manager - Diso
**Dành cho:** Accesstrade Leadership Team
**Mục đích:** Trình bày lộ trình phát triển Influence-Meter và cách tích hợp với hệ thống Accesstrade

---

## TÓM TẮT TỔNG QUAN

**Vendor** đang xây dựng **Influence-Meter** - một nền tảng API scoring và matching influencer. Song song, **Diso** đang phát triển **at-core** cho Accesstrade (AT) - nền tảng quản lý chiến dịch influencer marketing. Hai hệ thống này hoạt động độc lập nhưng tích hợp chặt chẽ để phục vụ khách hàng cuối như Techcombank.

### Mô Hình Kinh Doanh

```
┌─────────────────────────────────────────────────────────────────┐
│                      VENDOR (Third Party)                       │
│                                                                 │
│  ┌──────────────────────┐        ┌──────────────────────┐      │
│  │ Influence-Meter      │        │ Social Crawler       │      │
│  │ (API Service Only)   │        │ (Internal Service)   │      │
│  │                      │        │                      │      │
│  │ • Profile Scoring    │◄───────┤ • TikTok Crawler     │      │
│  │ • Demographics       │        │ • Instagram Crawler  │      │
│  │ • Matching Engine    │        │ • YouTube Crawler    │      │
│  │ • API Endpoints      │        │ • Data Enrichment    │      │
│  └──────────┬───────────┘        └──────────────────────┘      │
│             │ API Calls                                         │
└─────────────┼─────────────────────────────────────────────────┘
              │ REST API Integration
              │ (NO UI components, NO SDK)
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 DISO (Development Partner)                      │
│                                                                 │
│  Phát triển at-core cho:                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ at-core Platform (AT owns source code after delivery)   │  │
│  │                                                          │  │
│  │  • Campaign Management                                   │  │
│  │  • Influencer Discovery UI                               │  │
│  │  • Partner Admin Dashboard                               │  │
│  │  • Matching & Filtering UI                               │  │
│  │  • Analytics Dashboard                                   │  │
│  │  • Techcombank Custom Features                           │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                      │
└─────────────────────────┼───────────────────────────────────────┘
                          │ Source Code Delivery → AT
                          ▼
           ┌──────────────────────────────────────┐
           │      ACCESSTRADE (Client)            │
           │                                      │
           │  Owns 100% source code của at-core  │
           │  Bán source code cho khách hàng     │
           └──────────────┬───────────────────────┘
                          │ Source Code Sale
                          │ (100% ownership transfer)
                          ▼
           ┌──────────────────────────────────────┐
           │  TECHCOMBANK (End Customer)          │
           │                                      │
           │  Owns 100% source code của at-core  │
           │  Calls Influence-Meter API at runtime│
           └──────────────────────────────────────┘
```

**QUAN TRỌNG:**
- **Vendor** chỉ cung cấp API (không có UI, không có SDK embedded)
- **Diso** phát triển at-core platform → giao source code cho AT
- **Accesstrade** sở hữu 100% source code của at-core (sau khi Diso giao)
- **Techcombank** mua source code từ AT, tự host và vận hành
- **Influence-Meter API** là dịch vụ ngoài (như AWS, Stripe) - không ảnh hưởng đến ownership của source code

---

## PHẦN 1: INFLUENCE-METER (Vendor phát triển)

### 1.1. Vai Trò của Influence-Meter

**Influence-Meter là gì?**
- Hệ thống API backend đánh giá và phân tích influencer
- **KHÔNG có UI** - chỉ cung cấp RESTful API endpoints
- Tích hợp với Social Crawler để thu thập dữ liệu từ các nền tảng (TikTok, Instagram, YouTube, Facebook)

**Chức năng chính:**
1. **Profile Scoring** - Đánh giá chất lượng influencer (engagement, followers, brand safety)
2. **Audience Demographics** - Phân tích đối tượng theo dõi (tuổi, giới tính, địa lý)
3. **Matching Engine** - Gợi ý influencer phù hợp với chiến dịch của brand
4. **Campaign Eligibility** - Kiểm tra điều kiện tham gia chiến dịch

### 1.2. Lộ Trình Phát Triển Influence-Meter

#### **Version 1.0: Matching System (Hiện tại - Feb 2026)**

**Mục tiêu:** Hệ thống matching cơ bản giúp brand tìm influencer phù hợp

**Tính năng:**
- ✅ **Advanced Search & Filtering**
  - Filter theo demographics (location, age, gender)
  - Filter theo content quality (posting frequency, content type)
  - Filter theo brand safety (verified accounts, no controversial content)

- ✅ **Multi-Dimensional Scoring**
  - Category Match (influencer content vs campaign category)
  - Budget Tier Match (nano/micro/mid/macro/mega influencer)
  - Engagement Rate (like, comment, share per post)

- ✅ **Matching History & Audit Trail**
  - Lưu lại tất cả matching sessions
  - Export báo cáo để phân tích
  - Theo dõi xu hướng điểm số của influencer theo thời gian

**KPI Mục Tiêu (sau 6 tháng):**
- 85%+ brands hài lòng với kết quả matching (so với manual selection)
- Giảm thời gian tạo campaign từ 3 giờ xuống <30 phút
- API response time <5s cho batch 100 influencers

**API Endpoints:**
```
POST /api/v1/matching/score
GET  /api/v1/matching/history/:campaignId
POST /api/v1/search/advanced
```

---

#### **Version 1.1: Demographics System (Đang triển khai - Feb-Mar 2026)**

**Mục tiêu:** Bổ sung dữ liệu demographics chi tiết để cải thiện matching accuracy

**Vấn đề cần giải quyết:**
- Các nền tảng (TikTok, Instagram, YouTube) yêu cầu influencer cấp quyền OAuth để lấy dữ liệu audience
- Tỷ lệ chấp nhận thấp (10-30%) - influencer lo ngại về privacy
- Không có demographics data → matching kém chính xác (chỉ 40% brands hài lòng)

**Giải pháp v1.1: Rule-Based Inference + Manual Input**

1. **Rule-Based Inference Engine** (100% coverage)
   - Tự động ước tính demographics cho TẤT CẢ profiles
   - Sử dụng:
     - Category mapping (beauty → 82% female, gaming → 70% male)
     - Country/language signals (profile ở VN → 85% audience VN)
     - Hashtag analysis (#genz → young audience, #momlife → 25-44 age)
     - Comment author patterns (tên người comment → gender inference)
   - Accuracy: 60-65%

2. **Manual Input Flow** (cải thiện accuracy lên 75-85%)
   - **Screenshot Upload + OCR**: Influencer upload ảnh chụp TikTok Analytics → Google Cloud Vision API tự động extract data
   - **Manual Form**: Nếu không có screenshot, influencer điền form với percentage sliders
   - **Smart Prompting**: Chỉ yêu cầu manual input khi confidence thấp (<0.65)

3. **Admin Verification System**
   - Admin review submissions trước khi approve
   - Automated checks: fake screenshot detection, percentage validation, duplicate detection
   - Progressive trust scoring: influencer tin cậy → auto-approve (giảm workload 30-40%)

**KPI Mục Tiêu (sau 6 tháng):**
- 50-60% profiles có demographics với confidence >0.65
- Flip rate <15% (ổn định kết quả matching khi data thay đổi)
- Campaign match rate tăng từ 40% lên 65%+

**Timeline:**
- **Sprint 1-2 (2 weeks):** Rule-based inference engine + API
- **Sprint 3-4 (2 weeks):** Manual input flow + OCR integration
- **Sprint 5-6 (2 weeks):** Admin verification system + trust scoring
- **Launch:** End of March 2026

**API Endpoints mới:**
```
GET  /api/v1/demographics/:profileId
POST /api/v1/demographics/manual-submit
GET  /api/v1/demographics/admin/queue
POST /api/v1/demographics/admin/verify
```

---

#### **Version 1.2-2.0: Future Enhancements (Q2-Q3 2026)**

**Dự kiến tính năng:**
- ML-based demographics prediction (sử dụng v1.1 data làm training set)
- Audience overlap detection (tìm influencer có audience tương tự)
- Predictive scoring (dự đoán hiệu suất campaign)
- Real-time demographics updates
- Platform OAuth integration (nếu conversion rate cải thiện)

---

### 1.3. Trách Nhiệm của Vendor

**Vendor cung cấp:**
- ✅ Complete REST API documentation (OpenAPI/Swagger)
- ✅ API rate limits & quota management
- ✅ Authentication guide (API key + JWT patterns)
- ✅ Webhook system (optional - event notifications)
- ✅ SLA: 99.5% uptime
- ✅ Performance: API <5s response time cho batch operations
- ✅ Support: Technical documentation, API troubleshooting

**Vendor KHÔNG cung cấp:**
- ❌ UI components (không có React components, không có widgets)
- ❌ SDK/Library (AT tự implement API client)
- ❌ White-label dashboards
- ❌ Custom UI cho từng khách hàng

**Lý do API-only:**
- Đảm bảo AT sở hữu 100% source code (không có third-party UI embedded)
- AT linh hoạt thiết kế UI theo brand guidelines của từng khách hàng
- Tránh conflict ownership khi AT bán source code cho Techcombank

---

## PHẦN 2: AT-CORE (Diso phát triển cho Accesstrade)

### 2.1. Vai Trò của at-core

**at-core là gì?**
- Nền tảng quản lý chiến dịch influencer marketing đầy đủ
- **Sở hữu 100% source code** - AT có thể bán cho khách hàng (Techcombank, Vinfast)
- Tích hợp với Influence-Meter API để lấy scoring/demographics data

**Chức năng chính:**
1. **Campaign Management**
   - Tạo và quản lý campaigns
   - Set target audience (age, gender, location, interests)
   - Theo dõi campaign performance

2. **Influencer Discovery & Matching**
   - Search influencers với advanced filters
   - Hiển thị matching scores từ Influence-Meter API
   - Review và chọn influencers cho campaign

3. **Admin Dashboard**
   - Tenant management (multi-tenant cho nhiều brands)
   - API key management (để gọi Influence-Meter)
   - Analytics & reporting
   - User & permissions management

4. **Techcombank-Specific Features**
   - Custom TCB brand UI/UX
   - TCB-specific workflows (Creator program, event bonuses)
   - Integration với hệ thống nội bộ TCB (nếu cần)

### 2.2. Lộ Trình Phát Triển at-core

#### **Giai đoạn 1: Tích hợp Matching API (Feb 2026)**

**Mục tiêu:** Kết nối at-core với Influence-Meter Matching API v1.0

**Công việc:**
1. **Backend Integration**
   - Implement HTTP client gọi Influence-Meter API
   - Handle API authentication (API key từ tenant config)
   - Xử lý errors, timeouts, retry logic
   - Cache responses (Redis, TTL 1 hour)

2. **Frontend UI**
   - Advanced search filters UI (demographics, quality, safety)
   - Scored influencer list với badges (score, suitable/not suitable)
   - Score breakdown modal (chi tiết điểm từng dimension)
   - Matching history tab trong Campaign Detail page

3. **Database Changes**
   - Lưu matching sessions vào MongoDB (audit trail)
   - Store API responses để replay/analyze

**Deliverables:**
- Brands có thể filter influencers theo demographics
- Brands thấy matching scores khi browse influencers
- Brands review matching history của campaigns

**Timeline:** 1-2 tuần

---

#### **Giai đoạn 2: Tích hợp Demographics API (Feb-Mar 2026)**

**Mục tiêu:** Kết nối với Influence-Meter Demographics API v1.1

**Công việc:**
1. **Backend Integration**
   - Call Demographics API: `GET /api/v1/demographics/:profileId`
   - Handle reliability tiers (LOW/MEDIUM/HIGH)
   - Filter logic: chỉ show influencers với reliability MEDIUM+ (ẩn LOW tier)

2. **Frontend UI**
   - Display demographics data trong influencer profile
   - Show reliability badges (✓ Verified, ✓✓ Trusted, ~ Estimated)
   - Data source transparency ("Manual verified via Instagram Insights")
   - Warning messages cho LOW reliability profiles

3. **Influencer Onboarding Flow** (nếu AT host influencer portal)
   - Integrate với manual input flow của Influence-Meter
   - Hoặc: AT tự build UI, gọi API `POST /api/v1/demographics/manual-submit`

**Deliverables:**
- Brands filter influencers theo target audience demographics
- Brands thấy confidence/reliability scores
- Campaign match rate tăng từ 40% lên 65%+

**Timeline:** 1-2 tuần

---

#### **Giai đoạn 3: Partner Admin Dashboard (Mar 2026)**

**Mục tiêu:** Admin UI cho AT/TCB manage tenants và API usage

**Công việc:**
1. **Tenant Management**
   - CRUD tenants (Techcombank, Vinfast, etc.)
   - Configure API keys cho từng tenant
   - Set quotas/rate limits per tenant

2. **API Key Management**
   - Generate, rotate, revoke API keys
   - Monitor API usage (requests, quotas)
   - Billing/cost tracking

3. **Analytics Dashboard**
   - Campaign stats (total campaigns, active, completed)
   - Matching performance (avg scores, success rates)
   - Demographics coverage (% profiles with high-confidence data)
   - Top influencers by campaign count

**Deliverables:**
- AT có dashboard quản lý tất cả tenants
- Mỗi tenant (TCB, Vinfast) có API keys riêng
- Tracking usage để billing/cost allocation

**Timeline:** 1-2 tuần

---

### 2.3. Trách Nhiệm của Diso

**Diso phát triển (giao source code cho AT):**
- ✅ Campaign management workflows
- ✅ Influencer discovery UI (search, filters, matching UI)
- ✅ Admin dashboards (tenant, API keys, analytics)
- ✅ Techcombank-specific features (custom branding, workflows)
- ✅ Integration với Influence-Meter API (HTTP client, error handling)
- ✅ User authentication & authorization (JWT, roles)
- ✅ Database design (campaigns, influencers, users, tenants)

**Diso KHÔNG làm:**
- ❌ Scoring algorithm (do Influence-Meter API cung cấp)
- ❌ Demographics inference (do Influence-Meter API cung cấp)
- ❌ Social media crawling (do Vendor Social Crawler)

**Accesstrade nhận:**
- ✅ 100% source code ownership sau khi Diso giao
- ✅ Full deployment package (code + docs + guides)
- ✅ Support trong quá trình triển khai (nếu có contract support)

---

## PHẦN 3: TECHCOMBANK (Khách hàng cuối)

### 3.1. Mô Hình Kinh Doanh với Techcombank

**Accesstrade bán SOURCE CODE cho Techcombank:**
- TCB mua 100% source code của at-core platform
- TCB tự host và vận hành (on-premise hoặc TCB cloud)
- TCB sở hữu code → có thể modify, customize

**Influence-Meter vẫn là external API:**
- TCB's at-core instance gọi Influence-Meter API at runtime
- TCB trả phí API usage cho Vendor (thông qua AT hoặc trực tiếp)
- Model tương tự AWS, Stripe - external service, không conflict ownership

### 3.2. Lợi Ích cho Techcombank

**TCB nhận được:**
1. **Full Platform Source Code**
   - 100% ownership, không có vendor lock-in
   - Tự do customize UI/UX theo brand TCB
   - Tích hợp với hệ thống nội bộ TCB (CRM, ERP, etc.)

2. **Tính năng Matching & Demographics**
   - Filter influencers theo target audience của TCB
   - Matching scores để chọn influencers phù hợp
   - Demographics insights để đánh giá campaign effectiveness

3. **Flexibility**
   - Deploy on-premise (TCB servers) hoặc TCB cloud
   - Control data privacy (campaign data, influencer data)
   - Custom features cho Creator program của TCB

**TCB chi trả:**
- One-time: Source code license fee (cho AT)
- Recurring: Influence-Meter API usage fees (cho Vendor, thông qua AT)
- Recurring: Hosting costs (TCB tự host)

---

## PHẦN 4: TIMELINE & DEPENDENCIES

### 4.1. Timeline Tổng Thể (2 Tháng - Feb-Mar 2026)

**Chiến lược:** Công việc của Vendor và Diso chạy SONG SONG và GỐI ĐẦU để tối ưu timeline.

```
TUẦN   │ VENDOR (API Development)          │ DISO (at-core Integration)          │ DELIVERABLES
═══════╪═══════════════════════════════════╪═════════════════════════════════════╪════════════════════════════
       │                                   │                                     │
T1-T2  │ ✓ Matching API v1.0 (DONE)        │ • Matching API integration          │ • at-core có matching UI
Feb    │ • Demographics Sprint 1           │ • HTTP client, cache, error         │ • Backend gọi được API
Week   │   (Rule-based inference)          │   handling                          │ • Search filters basic
1-2    │ • API docs for Diso               │ • Database schema                   │
       │                                   │                                     │
───────┼───────────────────────────────────┼─────────────────────────────────────┼────────────────────────────
       │                                   │                                     │
T3-T4  │ • Demographics Sprint 2           │ • Advanced search UI complete       │ • Demographics API ready
Feb    │   (Manual input + OCR)            │ • Matching score UI (badges,        │ • Search filters đầy đủ
Week   │ • POST /demographics/manual       │   breakdown modal)                  │ • Matching history UI
3-4    │ • OCR integration test            │ • Demographics integration prep     │
       │                                   │   (mock data, UI skeleton)          │
───────┼───────────────────────────────────┼─────────────────────────────────────┼────────────────────────────
       │                                   │                                     │
T5-T6  │ • Demographics Sprint 3-4         │ • Demographics API integration      │ • Admin verify system
Late   │   (Admin verification)            │ • Reliability badges UI             │ • Full demographics flow
Feb    │ • Trust scoring system            │ • Manual input flow (if AT hosts)   │ • Partner admin started
Week   │ • Admin queue API                 │ • Partner Admin Dashboard start     │
5-6    │                                   │   (tenant CRUD, API keys)           │
───────┼───────────────────────────────────┼─────────────────────────────────────┼────────────────────────────
       │                                   │                                     │
T7-T8  │ • Demographics v1.1 finalize      │ • Partner Admin Dashboard           │ • at-core feature complete
Early  │ • Production deployment prep      │   complete                          │ • All APIs integrated
Mar    │ • API stress testing              │ • Analytics dashboard               │ • Integration testing
Week   │ • Documentation complete          │ • Integration testing với Vendor    │ • Bug fixes
7-8    │                                   │ • Bug fixes & polish                │
───────┼───────────────────────────────────┼─────────────────────────────────────┼────────────────────────────
       │                                   │                                     │
T9     │ • Monitor API stability           │ • Code quality check                │ • Source code to AT
Mid    │ • Support Diso integration        │ • Documentation complete            │ • AT review & acceptance
Mar    │   issues                          │ • SOURCE CODE DELIVERY to AT        │ • Deployment prep for TCB
Week   │                                   │ • Support AT deployment prep        │
9      │                                   │                                     │
───────┼───────────────────────────────────┼─────────────────────────────────────┼────────────────────────────
       │                                   │                                     │
T10+   │ • Production monitoring           │ • Support AT deployment to TCB      │ • TCB production launch
Late   │ • Performance optimization        │ • Monitor & troubleshoot            │ • Post-launch monitoring
Mar    │ • Plan v1.2 features              │ • Gather feedback                   │ • v1.2 planning
Week   │                                   │ • Plan v1.2 integration             │
10+    │                                   │                                     │
```

**GỐI ĐẦU QUAN TRỌNG:**
- **T1-T2**: Diso bắt đầu Matching integration ngay khi Vendor có API docs (không đợi Demographics)
- **T3-T4**: Diso build UI trước, mock demographics data để không block bởi Vendor Sprint 2
- **T5-T6**: Admin Dashboard có thể bắt đầu sớm (không phụ thuộc Demographics API hoàn thiện)
- **T7-T8**: Integration testing overlap với development cuối → phát hiện bugs sớm

**CHÚ Ý:** Timeline 2 tháng aggressive nhưng khả thi nếu:
- ✅ Vendor và Diso work song song (không chờ nhau)
- ✅ Diso mock data để develop UI trước khi API ready
- ✅ Communication liên tục (daily sync, shared Slack/Discord)
- ⚠️ Rủi ro: Buffer time ít, nếu có blocker sẽ delay cả pipeline

### 4.2. Dependencies

**Diso phụ thuộc vào:**
- Influence-Meter API availability (SLA 99.5%)
- Vendor API documentation (OpenAPI specs)
- API credentials (API keys, rate limits) từ Vendor
- Requirements rõ ràng từ AT về features

**Accesstrade phụ thuộc vào:**
- Diso giao source code đúng timeline (mid-Mar 2026)
- Code quality đảm bảo (tests, docs)
- Vendor API hoạt động ổn định

**Techcombank phụ thuộc vào:**
- at-core source code delivery từ AT
- Influence-Meter API uptime
- AT/Diso support cho deployment/integration (nếu có contract)

---

## PHẦN 5: SUCCESS METRICS & KPIs

### 5.1. Influence-Meter Metrics

**Coverage:**
- Target: 50-60% profiles với high-confidence demographics (>0.65)
- Current: TBD (v1.1 launching Mar 2026)

**Accuracy:**
- Rule-based: 60-65% vs ground truth
- Manual verified: 75-85% vs ground truth
- Weighted average: 65-70%

**Performance:**
- API response time: <500ms p95 (single profile)
- Batch scoring: <5s p95 (100 influencers)
- Uptime: 99.5% SLA

**Decision Stability:**
- Eligibility flip rate: <15% (profiles chuyển eligible ↔ not eligible khi data update)

### 5.2. at-core Metrics

**Campaign Efficiency:**
- Time to create campaign: từ 3 giờ → <30 phút (target)
- Campaign match quality: từ 40% → 65%+ brands hài lòng

**User Adoption:**
- % brands sử dụng demographics filters: >70%
- % campaigns sử dụng matching scores: >80%

**Admin Efficiency:**
- Tenant setup time: <2 giờ
- API integration success rate: >95% (no blocking issues)

### 5.3. Techcombank Metrics

**Campaign Performance:**
- Influencer match rate: >65% (vs 40% manual)
- Campaign completion rate: >80%
- Cost per matched influencer: giảm 40% (less manual vetting)

**Platform Adoption:**
- Active users (TCB marketing team): >20 users
- Campaigns created per month: >50 campaigns
- Influencer pool size: 1,000+ influencers với demographics

---

## PHẦN 6: RỦI RO & GIẢM THIỂU

### 6.1. Rủi Ro Kỹ Thuật

| Rủi Ro | Mức Độ | Giảm Thiểu |
|--------|--------|------------|
| **Influence-Meter API downtime** | Cao | - Circuit breaker pattern trong at-core<br>- Serve cached scores khi API down<br>- SLA 99.5% với penalties |
| **Demographics accuracy thấp** | Trung bình | - Start với rule-based (60-65%)<br>- Gradually improve với manual verified data<br>- Monitor flip rate <15% |
| **OCR extraction sai** | Trung bình | - Admin verification trước khi approve<br>- Allow manual corrections<br>- Monitor OCR accuracy >80% |
| **API rate limits** | Thấp | - Implement caching (Redis, TTL 1h)<br>- Batch operations<br>- Rate limit quotas per tenant |

### 6.2. Rủi Ro Kinh Doanh

| Rủi Ro | Mức Độ | Giảm Thiểu |
|--------|--------|------------|
| **TCB không hài lòng với match quality** | Trung bình | - Beta period để gather feedback<br>- Iterative improvements based on TCB input<br>- Clear SLA expectations |
| **Influencer không submit demographics** | Cao | - Smart prompting (only low confidence)<br>- Gamification (profile completeness)<br>- Incentives ("3x more matches") |
| **Vendor API costs quá cao cho TCB** | Trung bình | - Transparent pricing model<br>- Volume discounts<br>- Optimize API calls (caching) |

---

## PHẦN 7: NEXT STEPS & ACTION PLAN

### 7.1. Immediate Actions - TUẦN 1 (1-7 Feb 2026)

#### Vendor (API Provider)
| Action | Owner | Deadline | Dependency |
|--------|-------|----------|------------|
| Finalize Demographics v1.1 API specs | Vendor Tech Lead | Feb 3 | ✅ PRD approved |
| Share OpenAPI docs to Diso | Vendor Tech Lead | Feb 5 | API specs |
| Setup staging API credentials | Vendor DevOps | Feb 5 | - |
| Begin Demographics Sprint 1 (Rule-based) | Vendor Dev Team | Feb 1-14 | - |

#### Diso (at-core Development)
| Action | Owner | Deadline | Dependency |
|--------|-------|----------|------------|
| Setup at-core staging environment | Diso DevOps | Feb 3 | - |
| Review Demographics PRD + API docs | Diso Backend Lead | Feb 5 | Vendor API docs |
| Start Matching API integration | Diso Backend Dev | Feb 1-14 | API credentials |
| Design UI mockups (Search, Matching) | Diso Frontend Lead | Feb 7 | AT requirements |

#### Accesstrade (Client/Requirements)
| Action | Owner | Deadline | Dependency |
|--------|-------|----------|------------|
| Confirm at-core feature requirements | AT Product Manager | Feb 5 | - |
| Provide TCB branding assets | AT Design/TCB | Feb 7 | - |
| Approve 2-month timeline | AT Leadership | Feb 5 | Review roadmap |
| Assign AT liaison for daily sync | AT Project Manager | Feb 3 | - |

#### Techcombank (End Customer - Optional)
| Action | Owner | Deadline | Dependency |
|--------|-------|----------|------------|
| Review roadmap, confirm go/no-go | TCB Product Lead | Feb 10 | AT presentation |
| Share custom feature requirements | TCB Marketing Team | Feb 10 | - |
| Prepare deployment infrastructure | TCB DevOps | Mar 1 | - |

---

### 7.2. Key Milestones (8-10 Tuần)

#### 🎯 Milestone 1: Matching Integration Complete (End of T2 - Feb 14)
**Deliverables:**
- ✅ Diso: Matching API integrated (backend + cache + error handling)
- ✅ Diso: Search filters UI + Matching scores UI
- ✅ Vendor: Demographics Sprint 1 API ready (rule-based inference)

**Success Criteria:**
- at-core staging có thể filter influencers theo demographics
- Matching scores hiển thị đúng trong UI
- API response time <5s

**Risks nếu miss:**
- Delay Demographics integration (dependent on Matching foundation)
- Less time cho bug fixes later

---

#### 🎯 Milestone 2: Demographics Integration Ready (End of T4 - Feb 28)
**Deliverables:**
- ✅ Vendor: Demographics Sprint 2 complete (Manual input + OCR)
- ✅ Diso: Demographics API integration done
- ✅ Diso: Reliability badges UI, data source transparency
- 🧪 Integration testing round 1 (Vendor + Diso)

**Success Criteria:**
- Demographics data hiển thị trong influencer profiles
- Reliability badges (LOW/MEDIUM/HIGH) working
- OCR manual input flow tested (if AT hosts influencer portal)

**Risks nếu miss:**
- Admin Dashboard sẽ thiếu demographics features
- Timeline slip → might miss Mar delivery

---

#### 🎯 Milestone 3: Full Feature Complete (End of T6-7 - Mar 14)
**Deliverables:**
- ✅ Vendor: Demographics Sprint 3-4 complete (Admin verification + Trust)
- ✅ Diso: Partner Admin Dashboard complete
- ✅ Diso: Analytics dashboard + all UI polish
- 🧪 Full integration testing (all APIs)
- 🐛 Bug fixes from testing

**Success Criteria:**
- Admin có thể manage tenants, API keys
- Analytics dashboard shows campaign stats, demographics coverage
- All critical bugs fixed (P0, P1)

**Risks nếu miss:**
- Source code delivery delay
- AT/TCB deployment pushed to April

---

#### 🎯 Milestone 4: Source Code Delivery to AT (T9 - Mar 21)
**Deliverables:**
- 📦 Diso → AT: Complete source code package
- 📄 Full documentation (deployment guide, API integration guide)
- ✅ AT: Code review & acceptance testing
- 🚀 AT + Diso: TCB deployment prep

**Success Criteria:**
- Code passes AT quality standards (tests, docs, security)
- AT can deploy to staging successfully
- No blocking issues for TCB production deployment

**Risks nếu miss:**
- TCB production launch delays
- AT revenue impact (if contract has deadlines)

---

#### 🎯 Milestone 5: TCB Production Launch (T10 - Mar 28+)
**Deliverables:**
- 🚀 AT → TCB: Deploy to production
- 📊 Vendor + Diso + AT: Monitor metrics (API uptime, match quality)
- 📈 Gather user feedback from TCB team
- 🔮 Plan v1.2 enhancements

**Success Criteria:**
- TCB production stable (no critical bugs)
- Campaign creation works end-to-end
- TCB team trained & using platform

**Success Metrics (after 1 month):**
- >20 TCB users active
- >50 campaigns created
- >65% match quality satisfaction

---

### 7.3. Communication & Coordination

#### Daily Sync (T1-T8)
- **Time:** 9:00 AM VN time (15 min standup)
- **Attendees:** Vendor Tech Lead, Diso Backend Lead, AT Project Manager
- **Format:**
  - Yesterday progress
  - Today plan
  - Blockers (API issues, requirement changes)

#### Weekly Review (Every Friday)
- **Time:** 2:00 PM VN time (1 hour)
- **Attendees:** All stakeholders (Vendor, Diso, AT leadership, TCB optional)
- **Format:**
  - Demo progress
  - Review metrics (API performance, development velocity)
  - Adjust timeline if needed

#### Escalation Path
- **Blocker identified** → Daily sync → Resolve in 24h
- **Cannot resolve** → Escalate to leadership → Decision in 48h
- **Critical issue (API down, deployment failure)** → Immediate call (Slack emergency channel)

---

### 7.4. Go/No-Go Decision Points

#### Go/No-Go 1: After Milestone 1 (Feb 14)
**Question:** "Có tiếp tục với Demographics integration không?"
- ✅ GO nếu: Matching API stable, UI works, no major blockers
- ❌ NO-GO nếu: API downtime >5%, critical bugs, Vendor delay Sprint 1

**No-Go action:** Extend timeline 2 weeks, re-negotiate with TCB

---

#### Go/No-Go 2: After Milestone 2 (Feb 28)
**Question:** "Có đủ time cho Admin Dashboard + testing không?"
- ✅ GO nếu: Demographics integration done, <10 open bugs
- ❌ NO-GO nếu: Major bugs, API unstable, UI incomplete

**No-Go action:** Cut Admin Dashboard scope (focus core features only), extend to mid-April

---

#### Go/No-Go 3: After Milestone 3 (Mar 14)
**Question:** "Source code ready để deliver cho AT?"
- ✅ GO nếu: All features done, tests pass, docs complete
- ❌ NO-GO nếu: P0/P1 bugs open, missing docs, performance issues

**No-Go action:** Delay delivery 1 week, AT inform TCB về delay

---

### 7.5. Contingency Plans

**Nếu Vendor delay Demographics API 2 weeks:**
- Diso focus Admin Dashboard + UI polish first
- Demographics integration shift to T7-T8
- Delivery to AT vẫn T9 (trade-off: less testing time)

**Nếu AT requirements change mid-sprint:**
- Assess impact (1 day, 1 week, hoặc >2 weeks?)
- If >2 weeks → Cut scope hoặc extend timeline
- Re-negotiate TCB deployment date

**Nếu TCB infrastructure not ready by Mar 28:**
- AT deploy to AT staging first
- TCB soft launch (limited users) in April
- Full production rollout when infra ready

---

## KẾT LUẬN

### Tóm Tắt Vai Trò

**Vendor (Third-Party API Provider):**
- Phát triển Influence-Meter API (scoring, demographics, matching)
- Không có UI - chỉ cung cấp API service
- SLA 99.5%, performance <5s, documentation đầy đủ

**Diso (Development Partner cho AT):**
- Phát triển at-core platform cho Accesstrade
- Tích hợp Influence-Meter API vào at-core
- Giao 100% source code cho AT sau khi hoàn thành
- Timeline: 2 tháng (Feb-Mar 2026)

**Accesstrade (Client & Reseller):**
- Nhận source code từ Diso (100% ownership)
- Bán source code cho khách hàng cuối (TCB, Vinfast)
- Có thể tùy chỉnh thêm features cho từng khách hàng
- Quản lý API credentials với Vendor

**Techcombank (End Customer):**
- Mua source code at-core từ AT
- Tự host và vận hành platform
- Gọi Influence-Meter API at runtime (như external service)
- Full ownership, customizable, scalable

### Lợi Ích Cho Tất Cả Bên

**Vendor:**
- Recurring revenue từ API usage (nhiều customers: TCB, Vinfast, etc.)
- Focus vào core technology (scoring, demographics)
- Không phải maintain UI cho từng customer
- Scalable business model (API service)

**Diso:**
- Development contract với AT (one-time hoặc project-based)
- Build portfolio (enterprise influencer platform)
- Có thể offer support/maintenance contracts sau delivery
- Experience với complex integrations

**Accesstrade:**
- Bán source code → revenue từ TCB, Vinfast, etc.
- Không tốn nguồn lực phát triển (outsource cho Diso)
- Scalable model (reuse cùng platform cho nhiều customers)
- Control API costs (negotiate với Vendor)

**Techcombank:**
- 100% ownership, no vendor lock-in cho platform code
- Flexible customization (có source code)
- Best-in-class matching/demographics từ Vendor API
- Control data privacy & security (self-hosted)

---

**Tài liệu này được tạo bởi:** Diso Product Team
**Ngày:** 2026-02-01
