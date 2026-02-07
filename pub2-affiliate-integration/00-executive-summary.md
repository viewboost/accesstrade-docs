# Executive Summary - Pub2 Affiliate Integration

**Date:** 2026-02-07
**Audience:** Product Owners, Business Stakeholders, Management
**Status:** Planning Phase
**Partners:** Techcombank (TCB_001), Ambassador (AMB_001), Vinfast (VF_001)

## 🎨 Live Mockups (Ambassador)

**Xem trực tiếp UI/UX design mockups:**
- 📋 [Campaign Listing Center](https://ambassador.diso.vn/affiliate-center.html) - Browse campaigns, filter, account linking
- 📊 [Personal Dashboard](https://ambassador.diso.vn/affiliate-dashboard.html) - Stats, links, transactions, earnings
- 🔗 [Campaign Detail](https://ambassador.diso.vn/campaign-detail.html) - Chi tiết campaign với CTA "Generate Link"

**Tính năng:**
- ✅ Fully responsive (mobile → desktop)
- ✅ Vietnamese content với diacritics đầy đủ
- ✅ Interactive elements (search, filter, copy, modal)
- ✅ Production-ready quality

---

## 📋 Tổng quan Dự án

### Mục tiêu Kinh doanh

Tích hợp hệ thống affiliate marketing của Pub2 (AccessTrade) vào 3 platforms riêng biệt để **tăng thu nhập cho influencers** và **gia tăng giá trị platform**.

**Lợi ích chính:**
- 💰 **Dual Revenue Stream:** Influencers kiếm tiền từ cả views LẪN affiliate commissions
- 📈 **Tăng Engagement:** Incentive mạnh hơn để tạo nội dung chất lượng
- 🎯 **Competitive Edge:** Khác biệt so với competitors chỉ có single revenue model
- 🤝 **Win-Win-Win:** Platform, Influencers, Merchants đều có lợi

---

## 🏗️ Business Model

### 3 Partners Độc lập

```
┌─────────────────────────────────────────────────────────┐
│  Pub2 System (AccessTrade)                              │
│  ↓ 3 Separate Partnerships                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🏦 TCB_001: Techcombank                                │
│     • Own API key, billing, influencers                 │
│     • Mua source code từ AT (work-for-hire)             │
│     • Tự vận hành sau delivery                          │
│                                                         │
│  🎯 AMB_001: Ambassador                                 │
│     • Owned by AccessTrade                              │
│     • Own API key, billing, influencers                 │
│     • AT vận hành trực tiếp                             │
│                                                         │
│  🚗 VF_001: Vinfast                                     │
│     • Own API key, billing, influencers                 │
│     • Mua source code từ AT (work-for-hire)             │
│     • Tự vận hành sau delivery                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Quan trọng:**
- ✅ Mỗi partner quản lý **hoàn toàn độc lập**
- ✅ Không chia sẻ data giữa các partners
- ✅ Riêng billing, riêng influencers, riêng campaigns

---

## 💡 Cách Hoạt động (User Journey)

### Cho Influencers

#### Bước 1: Đăng ký & Liên kết Tài khoản
**👉 [Xem mockup: Affiliate Center](https://ambassador.diso.vn/affiliate-center.html)**

```
Alice đã là influencer trên Techcombank Creator Platform
→ Truy cập mục "Affiliate Marketing"
→ Thấy CTA: "Liên kết tài khoản Pub2 để bắt đầu kiếm commission"
→ Đọc policy & hướng dẫn về affiliate program
→ Click "Liên kết tài khoản"
  • Nếu CÓ tài khoản Pub2: Liên kết ngay (OAuth hoặc nhập email)
  • Nếu CHƯA CÓ: Hướng dẫn đăng ký Pub2 trước
→ ✅ Liên kết thành công → Sẵn sàng tạo affiliate links
```

#### Bước 2: Browse & Join Campaigns
**👉 [Xem mockup: Campaign Detail](https://ambassador.diso.vn/campaign-detail.html)**

```
Alice vào "Affiliate Campaigns" tab
→ Thấy 15 campaigns được TCB chọn lọc (credit cards, loans, insurance)
→ Click "Thẻ Tín Dụng Platinum" → Xem details
→ Commission: 8.5% per approval (~$42.50/card)
→ Click "Generate Link" → Nhận tracking link
→ Copy link → Paste vào video description
```

#### Bước 3: Kiếm Tiền
**👉 [Xem mockup: Personal Dashboard](https://ambassador.diso.vn/affiliate-dashboard.html)**

```
Viewer xem video của Alice → Click affiliate link
→ Đăng ký thẻ Techcombank qua link
→ Được duyệt
→ Alice nhận $42.50 commission (bên cạnh view revenue)

Dashboard của Alice:
┌────────────────────────────────────┐
│ Earnings This Month                │
├────────────────────────────────────┤
│ Video Views:      $150             │
│ Affiliate Sales:  $510 (12 cards)  │
│ ────────────────────────────────   │
│ TOTAL:           $660              │
└────────────────────────────────────┘
```

### Cho Admin (TCB/AMB/VF)

#### Campaign Curation
```
TCB Admin workflow:

STEP 1: Browse campaigns trên Pub2 Portal
→ Login vào pub2.vn với TCB_001 account
→ Search "credit card" → Thấy 50 campaigns
→ Note down campaign IDs muốn add:
  • camp_123: TCB Platinum Card (commission 8.5%)
  • camp_456: Travel Insurance (commission 5%)
  • ❌ camp_789: Vietcombank Card (competitor - bỏ qua)

STEP 2: Tạo campaign trên TCB Admin Portal
→ Login TCB Creator Admin
→ "Campaigns" → "Add New Campaign"
→ Form:
  • Title: "Thẻ Tín Dụng Techcombank Platinum" (Vietnamese)
  • Description: Custom content cho TCB influencers
  • Pub2 Campaign ID: camp_123 (link to Pub2)
  • Commission: 8.5% (copy từ Pub2)
  • Banner: Upload TCB-branded image
  • Category: Credit Card
  • Status: Draft
→ Submit for Approval

STEP 3: Approval workflow
→ Manager review campaign trong TCB Admin
→ Manager approve → Status = Active
→ 🎉 Influencers giờ thấy campaign này trong TCB Portal
```

---

## 🎯 Value Propositions

### Cho Influencers
- 💰 **Tăng 2-3x thu nhập:** Views + Affiliates
- 📊 **Dashboard thống nhất:** Tất cả earnings một chỗ
- 🎁 **Quality Campaigns:** Platform đã lọc campaigns phù hợp
- 🔒 **Trust & Safety:** Không lo scam, được platform bảo vệ

### Cho Platform (TCB/AMB/VF)
- 📈 **Tăng Retention:** Influencers ở lại vì thu nhập cao hơn
- 🎯 **Content Quality:** Incentive tạo review/tutorial videos tốt hơn
- 💼 **Revenue Share:** Có thể lấy % từ affiliate commissions
- 🏆 **Market Leadership:** Differentiation so với competitors

### Cho Merchants (Pub2 Partners)
- 👥 **Access Influencers:** Reach audience qua trusted creators
- 📹 **Video Marketing:** Authentic reviews, không phải ads
- 📊 **Performance Tracking:** Rõ ràng ROI từng influencer
- 💰 **Pay for Performance:** Chỉ trả khi có conversion

---

## 🔒 Data Privacy & Security

### Tenant Isolation (Hoàn toàn Tách biệt)

**Scenario:**
```
Alice là influencer của CẢ Techcombank VÀ Ambassador
→ Có 1 tài khoản Pub2 (PUB_12345)
→ Tạo links cho cả 2 platforms

Khi Alice login vào TCB Portal:
✅ Thấy: $120 commission từ TCB campaigns
❌ KHÔNG thấy: $80 từ Ambassador campaigns

Khi Alice login vào Ambassador Portal:
✅ Thấy: $80 commission từ AMB campaigns
❌ KHÔNG thấy: $120 từ TCB campaigns
```

**Lý do:** Bảo mật, competitive intelligence, GDPR compliance

---

## 🚀 Rollout Plan

### Phase 1: Design & Planning (Week 1-2)
- [ ] Tạo Figma mockups cho influencer & admin UIs
- [ ] Align với Pub2 về API requirements
- [ ] Finalize account linking flow
- [ ] UX review với stakeholders

### Phase 2: Development (Week 3-6)
- [ ] Account linking (OAuth + Email matching)
- [ ] Campaign management admin panel
- [ ] Pub2 API integration
- [ ] Webhook & sync jobs

### Phase 3: Testing (Week 7-8)
- [ ] UAT với Pub2 sandbox
- [ ] Security testing (tenant isolation)
- [ ] Performance testing (1000+ users)

### Phase 4: Launch (Week 9+)
- [ ] **Week 9:** Techcombank production launch
- [ ] **Week 10:** Monitor metrics, gather feedback
- [ ] **Week 11+:** Expand to Ambassador & Vinfast

---

## 📊 Success Metrics

### Phase 1 Targets (First 3 Months)

| Metric | Current | Target | Impact |
|--------|---------|--------|--------|
| **Pub2 Link Rate** | 0% | 40% | 40% influencers link Pub2 account |
| **Activation Rate** | 0% | 60% | 60% of linked users generate links |
| **Influencer Revenue** | $150/month | $400/month | +167% avg income |
| **Platform Retention** | 65% | 80% | +15% retention |

### Long-term Goals (6-12 Months)

- 🎯 **50% Link Rate:** Half of active influencers participate
- 💰 **$500 Avg Income:** Dual revenue streams working
- 📈 **2x Content Output:** More incentive = more videos
- 🏆 **#1 Creator Platform:** Market leadership

---

## 💼 Business Questions Answered

### Q1: Tại sao 3 partners riêng biệt thay vì 1 at-core?
**A:**
- ✅ **Clean Handover:** TCB/Vinfast mua code, tự vận hành
- ✅ **Billing Independence:** Mỗi partner tự quản lý revenue
- ✅ **Exit Strategy:** TCB có thể rời AT mà không ảnh hưởng AMB/VF
- ✅ **Data Isolation:** Không chia sẻ competitive data

### Q2: Pub2 có 1000+ campaigns, sao không auto-sync?
**A:**
- ⚠️ **Competitor Risk:** Auto-sync → Vietcombank ads show trên TCB portal
- ⚠️ **Irrelevant Content:** Pizza Hut, fashion brands không phù hợp TCB
- ✅ **Solution:** Admin manually curate, full control

### Q3: Influencers có thấy data từ platform khác không?
**A:**
- ❌ **NO - Complete Isolation**
- TCB influencer KHÔNG thấy Ambassador data
- Ambassador KHÔNG thấy TCB data
- Security + GDPR compliance

### Q4: Làm sao liên kết tài khoản Pub2?
**A:**
- 🔐 **Option 1 (Recommended):** OAuth 2.0 - Secure, explicit consent
- 📧 **Option 2 (Fallback):** Email matching + verification
- ✅ **GDPR Compliant:** User consent required

### Q5: Ambassador không muốn show "AccessTrade" branding?
**A:**
- ✅ **White-label OAuth:** Custom domain (affiliate.ambassador.io)
- ✅ **Silent Linking:** Backend integration, zero branding visible
- ✅ **Full Brand Control:** Ambassador UI, không mention AT

---

## 🎁 Competitive Advantages

### So với Competitors

| Feature | Our Platform | Competitor A | Competitor B |
|---------|--------------|--------------|--------------|
| Revenue Streams | Views + Affiliate | Views only | Affiliate only |
| Campaign Curation | Manual, quality | Auto-sync, spam | Limited selection |
| Data Privacy | Complete isolation | Shared data | N/A |
| Brand Protection | White-label ready | Generic | Generic |
| Metrics Dashboard | Unified | Separate tools | Basic |

---

## ⚠️ Risks & Mitigations

### Risk 1: Low Adoption Rate
**Mitigation:**
- Onboarding tutorial + incentives ($10 bonus first conversion)
- Simplify linking flow (2 clicks max)
- Email campaigns highlighting success stories

### Risk 2: Campaign Quality Issues
**Mitigation:**
- Manual curation (admin approval required)
- Competitor detection algorithm
- Regular Pub2 sync (detect ended campaigns)

### Risk 3: Data Leak Between Tenants
**Mitigation:**
- Technical: Database-level filtering (sub_id_2)
- Security: Audit logging, penetration testing
- Compliance: GDPR consent forms

### Risk 4: Pub2 API Changes
**Mitigation:**
- Versioned API contracts
- Fallback mechanisms (polling if webhooks fail)
- Regular sync with Pub2 team

---

## 📞 Next Steps

### Immediate Actions (This Week)
1. **Pub2 Alignment Call:**
   - Confirm OAuth support
   - Discuss custom branding options
   - Get test accounts for development

2. **Stakeholder Review:**
   - Product Owners approve roadmap
   - Legal review GDPR compliance
   - Finance approve revenue share model

3. **Design Kickoff:**
   - UX designer starts Figma mockups
   - User research with 5-10 influencers
   - Competitive analysis

### Week 2-3
- Finalize technical architecture
- Start development Sprint 1
- Setup Pub2 sandbox environment

---

## 📚 Related Documents

Để hiểu chi tiết technical implementation:

1. **[Brainstorming Session](./01-brainstorming-session.md)** - 85+ ideas, SWOT analysis
2. **[Architecture Decisions](./02-architecture-decisions.md)** - 3 critical decisions với code examples
3. **[Admin Campaign Management](./03-admin-campaign-management.md)** - Workflow chi tiết
4. **[Pub2 Q&A](./04-pub2-questions-response.md)** - Trả lời technical questions

---

**Document Owner:** AccessTrade Integration Team
**Reviewers:** Product Owners (TCB, AMB, VF), Business Development
**Last Updated:** 2026-02-07
**Next Review:** After stakeholder approval
